"""Regression tests for review findings: one test group per finding.

Each section names the code path it protects. The tests drive the public
surface or the narrowest internal seam that exposes the bug.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from ax_devil_device_api._http.auth import AxisAuth, _BasicState
from ax_devil_device_api._http.options import RetryPolicy
from ax_devil_device_api._http.types import Headers, RawBody, Request, Response
from ax_devil_device_api._protocols.base import parse_result
from ax_devil_device_api._protocols.state import DeviceState
from ax_devil_device_api._runtime.driver import Call, run_sync
from ax_devil_device_api.apis import mqtt_client
from ax_devil_device_api.apis.mqtt_client import ClientConfig, ClientStatus, ConfigureClientRequest
from ax_devil_device_api.errors import ConnectionFailed, ResponseFormatError
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"
VERSIONS_KEY = f"jsonrpc:{MQTT}"
PUBLISHERS = "/config/rest/analytics-mqtt/v1/publishers"


# -- a. driver: non-replayable bodies are not retried -------------------------


class _FailingTransport:
    """Sync transport whose ``send`` fails before the request is sent, and counts calls."""

    def __init__(self, fail_times: int) -> None:
        self.fail_times = fail_times
        self.calls = 0

    def send(self, request: Request) -> Response:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ConnectionFailed("x", request_sent=False)
        return Response(200, Headers(()), b"ok", request)

    def open_stream(self, request: Request) -> Any:  # pragma: no cover - not used here
        raise AssertionError("no stream expected")


def _upload_flow(body: RawBody) -> Any:
    response = yield Request("POST", "/upload", body=body)
    return response.status


def test_non_replayable_body_is_not_retried_after_unsent_failure() -> None:
    transport = _FailingTransport(fail_times=1)
    body = RawBody(iter([b"x"]), "application/octet-stream")

    with pytest.raises(ConnectionFailed):
        run_sync(transport, _upload_flow(body), Call(retry=RetryPolicy(backoff=0)))

    assert transport.calls == 1


def test_replayable_body_is_retried_after_unsent_failure() -> None:
    transport = _FailingTransport(fail_times=1)
    body = RawBody(b"x", "application/octet-stream")

    assert run_sync(transport, _upload_flow(body), Call(retry=RetryPolicy(backoff=0))) == 200
    assert transport.calls == 2


# -- b. auth: demote does not clear a newer verified state --------------------


def test_demote_does_not_clear_a_newer_verified_state() -> None:
    owner = AxisAuth(None)
    state_a = _BasicState()
    state_b = _BasicState()
    owner._verified = state_a

    owner._promote(state_b)  # another request verified a newer state
    owner._demote(state_a)  # the stale request now reports its old state as invalid

    assert owner._verified is state_b


def test_demote_clears_the_expected_verified_state() -> None:
    owner = AxisAuth(None)
    state_a = _BasicState()
    owner._promote(state_a)

    owner._demote(state_a)

    assert owner._verified is None


# -- c. DCA: dot path segments are rejected before any request ----------------


@pytest.mark.parametrize("bad_id", [".", ".."])
def test_get_publisher_rejects_dot_segments_without_sending(bad_id: str) -> None:
    camera = MockCamera()
    with camera.device() as dev:
        with pytest.raises(ValueError):
            dev.apis.analytics_mqtt.get_publisher(bad_id)

    assert camera.requests == []


def test_remove_publisher_rejects_dotdot_without_sending() -> None:
    camera = MockCamera()
    with camera.device() as dev:
        with pytest.raises(ValueError):
            dev.apis.analytics_mqtt.remove_publisher("..")

    assert camera.requests == []


# -- d. state: forget and set_or_clear semantics ------------------------------


def test_forget_invalidates_outstanding_token_for_that_key_only() -> None:
    state = DeviceState()
    token_a = state.token("a")
    token_b = state.token("b")

    state.forget("a")

    assert state.set("a", 1, token_a) is False
    assert state.get("a") is None
    assert state.set("b", 2, token_b) is True
    assert state.get("b") == 2


def test_set_or_clear_stale_clears_other_facts_and_stores_new_value() -> None:
    state = DeviceState()
    state.set("other", "kept?", state.token("other"))
    state.set("identity", "old", state.token("identity"))
    other_token = state.token("other")
    identity_token = state.token("identity")

    state.set_or_clear("identity", "new", identity_token, stale=lambda old, new: old != new)

    assert state.get("other") is None  # everything else was cleared
    assert state.get("identity") == "new"
    assert state.set("other", "late", other_token) is False  # the clear invalidated other tokens


def test_set_or_clear_not_stale_keeps_other_facts() -> None:
    state = DeviceState()
    state.set("other", "kept", state.token("other"))
    identity_token = state.token("identity")

    state.set_or_clear("identity", "new", identity_token, stale=lambda old, new: old != new)

    assert state.get("other") == "kept"
    assert state.get("identity") == "new"


# -- e. JSON-RPC: a 404 with an error envelope forgets cached versions --------


def test_404_with_jsonrpc_error_envelope_forgets_cached_versions() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", error=(2102, "x"), status=404)

    with camera.device() as dev:
        with pytest.raises(Exception):
            dev.apis.mqtt_client.get_client_status()
        assert dev._state.advertised_versions(VERSIONS_KEY) is None

        camera.jsonrpc(MQTT, "getClientStatus", data={"status": {"state": "active", "connectionStatus": "connected"}})
        dev.apis.mqtt_client.get_client_status()

    assert len(camera.calls("getSupportedVersions")) == 2  # renegotiated after the 404


# -- f. models: ClientStatus.status.state shape validation --------------------


@pytest.mark.parametrize("bad_state", [None, 123, {}, ["abc"]])
def test_client_status_rejects_non_string_state(bad_state: Any) -> None:
    data = {"status": {"state": bad_state, "connectionStatus": "connected"}}

    with pytest.raises(ResponseFormatError):
        parse_result(mqtt_client.OPS.get_client_status, data)


def test_client_status_accepts_and_keeps_new_string_state() -> None:
    data = {"status": {"state": "standby", "connectionStatus": "connected"}}

    result = parse_result(mqtt_client.OPS.get_client_status, data)

    assert isinstance(result, ClientStatus)
    assert result.status.state == "standby"


# -- g. ConfigureClientRequest.from_current with null username and port -------


def test_from_current_with_null_username_and_port_omits_them_and_keeps_password() -> None:
    data = {
        "status": {"state": "active", "connectionStatus": "connected"},
        "config": {
            "clientId": "cam-1",
            "server": {"host": "broker.test", "port": None, "protocol": "tcp"},
            "username": None,
            "password": "*****",
        },
    }
    current = parse_result(mqtt_client.OPS.get_client_status, data).config
    assert isinstance(current, ClientConfig)

    wire = ConfigureClientRequest.from_current(current).to_wire()

    assert "username" not in wire
    assert "password" not in wire
    assert "port" not in wire["server"]
    assert wire["server"]["host"] == "broker.test"
    assert wire["clientId"] == "cam-1"
    assert wire["keepExistingPassword"] is True


# -- h. identity coalescing: concurrent cold calls fetch once -----------------


@pytest.mark.anyio
async def test_concurrent_cold_identity_calls_issue_one_request() -> None:
    camera = MockCamera()
    camera.identity(firmware="11.9.0")

    async with camera.async_device() as dev:
        first, second = await asyncio.gather(dev.identity(), dev.identity())

    assert first.firmware_version == "11.9.0" and second.firmware_version == "11.9.0"
    assert len(camera.calls("getAllProperties")) == 1
