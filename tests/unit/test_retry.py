"""Retry policy, per-call options, timeouts, and observability hooks."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx
import pytest

from ax_devil_device_api import NO_RETRY, RequestOptions, RetryPolicy
from ax_devil_device_api.apis.mqtt_client import Server
from ax_devil_device_api.errors import ConnectionFailed, ReadTimeout
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"
STATUS = {"status": {"state": "active", "connectionStatus": "connected"}}
FAST = RetryPolicy(backoff=0)


def camera_with_mqtt() -> MockCamera:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=STATUS)
    camera.jsonrpc(MQTT, "configureClient")
    camera.jsonrpc(MQTT, "activateClient")
    return camera


def configure(dev: Any, **kwargs: Any) -> None:
    dev.apis.mqtt_client.configure_client(server=Server(host="b"), client_id="c", **kwargs)


# -- Retrying -----------------------------------------------------------------


def test_unsent_connect_error_is_retried_for_write_operation() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ConnectError, times=1)

    with camera.device(retry=FAST) as dev:
        configure(dev)

    assert len(camera.calls("configureClient")) == 1
    assert len(camera.requests) == 3  # failed negotiation, negotiation, configure


def test_read_timeout_is_not_retried_by_default() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ReadTimeout, times=1)

    with camera.device(retry=FAST) as dev, pytest.raises(ReadTimeout) as caught:
        dev.apis.mqtt_client.get_client_status()

    assert caught.value.request_sent is True
    assert len(camera.requests) == 1


def test_read_timeout_is_retried_for_read_operation_with_retry_reads() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ReadTimeout, times=1)

    with camera.device(retry=RetryPolicy(retry_reads=True, backoff=0)) as dev:
        status = dev.apis.mqtt_client.get_client_status()

    assert status.status.state == "active"
    assert len(camera.requests) == 3


def test_read_timeout_is_not_retried_for_write_even_with_retry_reads() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ReadTimeout, times=1)

    with camera.device(retry=RetryPolicy(retry_reads=True, backoff=0)) as dev, pytest.raises(ReadTimeout):
        configure(dev)

    assert len(camera.requests) == 1


def test_read_timeout_is_not_retried_for_action_even_with_retry_reads() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ReadTimeout, times=1)

    with camera.device(retry=RetryPolicy(retry_reads=True, backoff=0)) as dev, pytest.raises(ReadTimeout):
        dev.apis.mqtt_client.activate_client()

    assert len(camera.requests) == 1


def test_attempts_limit_total_requests() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ConnectError)

    with camera.device(retry=RetryPolicy(attempts=3, backoff=0)) as dev, pytest.raises(ConnectionFailed):
        configure(dev)

    assert len(camera.requests) == 3


def test_no_retry_in_request_options_disables_retry() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ConnectError, times=1)

    with camera.device(retry=FAST) as dev, pytest.raises(ConnectionFailed):
        configure(dev, request_options=RequestOptions(retry=NO_RETRY))

    assert len(camera.requests) == 1


def test_request_options_retry_overrides_device_policy() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ConnectError, times=2)

    with camera.device(retry=NO_RETRY) as dev:
        configure(dev, request_options=RequestOptions(retry=RetryPolicy(attempts=3, backoff=0)))

    assert len(camera.calls("configureClient")) == 1


def test_unsent_retry_can_be_disabled() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ConnectError, times=1)

    with camera.device(retry=RetryPolicy(retry_unsent=False, backoff=0)) as dev, pytest.raises(ConnectionFailed):
        configure(dev)

    assert len(camera.requests) == 1


def test_backoff_delay_doubles_and_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    delays: list[float] = []
    monkeypatch.setattr("ax_devil_device_api._runtime.driver.time.sleep", delays.append)
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ConnectError)

    with camera.device(retry=RetryPolicy(attempts=4, backoff=0.5, max_backoff=1.0)) as dev, pytest.raises(ConnectionFailed):
        configure(dev)

    assert delays == [0.5, 1.0, 1.0]


def test_policy_delay_and_validation() -> None:
    policy = RetryPolicy(backoff=0.1, max_backoff=0.3)
    assert [policy.delay(n) for n in (1, 2, 3, 4)] == [0.1, 0.2, 0.3, 0.3]
    with pytest.raises(ValueError):
        RetryPolicy(attempts=0)


@pytest.mark.anyio
async def test_async_unsent_retry_and_read_timeout_rules() -> None:
    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ConnectError, times=1)
    async with camera.async_device(retry=FAST) as dev:
        await dev.apis.mqtt_client.configure_client(server=Server(host="b"), client_id="c")
    assert len(camera.calls("configureClient")) == 1

    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ReadTimeout, times=1)
    async with camera.async_device(retry=FAST) as dev:
        with pytest.raises(ReadTimeout):
            await dev.apis.mqtt_client.get_client_status()

    camera = camera_with_mqtt()
    camera.fail(MQTT, httpx.ReadTimeout, times=1)
    async with camera.async_device(retry=RetryPolicy(retry_reads=True, backoff=0)) as dev:
        assert (await dev.apis.mqtt_client.get_client_status()).status.state == "active"


# -- Timeouts -----------------------------------------------------------------


def timeout_recorder(camera: MockCamera, seen: list[dict[str, Any]]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.extensions["timeout"]))
        method = json.loads(request.content)["method"]
        data = {"apiVersions": ["1.0"]} if method == "getSupportedVersions" else STATUS
        return httpx.Response(200, json={"method": method, "data": data})

    camera.route("POST", MQTT, handler)


def test_device_timeout_reaches_transport() -> None:
    camera, seen = MockCamera(), []
    timeout_recorder(camera, seen)

    with camera.device(timeout=7.0) as dev:
        dev.apis.mqtt_client.get_client_status()

    assert seen and all(t["read"] == 7.0 and t["connect"] == 7.0 for t in seen)


def test_request_options_timeout_reaches_transport_for_every_request_of_the_call() -> None:
    camera, seen = MockCamera(), []
    timeout_recorder(camera, seen)

    with camera.device(timeout=7.0) as dev:
        dev.apis.mqtt_client.get_client_status(request_options=RequestOptions(timeout=42.0))

    assert len(seen) == 2  # negotiation and the call itself
    assert all(t == {"connect": 42.0, "read": 42.0, "write": 42.0, "pool": 42.0} for t in seen)


# -- Hooks and logging --------------------------------------------------------


def test_on_response_hook_records_api_operation_status_attempt() -> None:
    camera, events = camera_with_mqtt(), []

    with camera.device(on_response=events.append) as dev:
        dev.apis.mqtt_client.get_client_status()

    last = events[-1]
    assert (last["api"], last["operation"], last["method"], last["path"]) == (
        "mqtt-client", "get_client_status", "POST", MQTT,
    )
    assert (last["status"], last["error"], last["attempt"]) == (200, None, 1)
    assert last["duration_ms"] >= 0
    assert len(events) == 2


def test_on_response_hook_sees_failed_attempt_then_retry() -> None:
    camera, events = camera_with_mqtt(), []
    camera.fail(MQTT, httpx.ConnectError, times=1)

    with camera.device(retry=FAST, on_response=events.append) as dev:
        dev.apis.mqtt_client.get_client_status()

    assert [(e["attempt"], e["status"], e["error"]) for e in events] == [
        (1, None, "ConnectionFailed"),
        (2, 200, None),
        (1, 200, None),
    ]


def test_debug_logging_on_library_logger(caplog: pytest.LogCaptureFixture) -> None:
    camera = camera_with_mqtt()
    caplog.set_level(logging.DEBUG, logger="ax_devil_device_api")

    with camera.device() as dev:
        dev.apis.mqtt_client.get_client_status()

    messages = [r.getMessage() for r in caplog.records if r.name == "ax_devil_device_api"]
    assert any(f"POST {MQTT} -> 200" in m and "mqtt-client.get_client_status" in m and "attempt 1" in m for m in messages)


def test_no_debug_logging_by_default(caplog: pytest.LogCaptureFixture) -> None:
    camera = camera_with_mqtt()
    caplog.set_level(logging.INFO, logger="ax_devil_device_api")

    with camera.device() as dev:
        dev.apis.mqtt_client.get_client_status()

    assert not [r for r in caplog.records if r.name == "ax_devil_device_api"]
