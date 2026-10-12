"""JSON-RPC protocol: negotiation, envelopes, error mapping, and request bodies.

Exercised end to end through the public API (``Device`` / ``AsyncDevice``)
over ``httpx.MockTransport``, plus a few direct flows for binding options.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from ax_devil_device_api.device import AsyncDevice, Device
from ax_devil_device_api._protocols.base import ApiInfo, ApiVersion, Family, Model, Operation, flow_for
from ax_devil_device_api._protocols.jsonrpc import FixedVersion, JsonRpcBinding, NoVersion
from ax_devil_device_api._runtime.driver import run_sync
from ax_devil_device_api.apis.mqtt_client import Server
from ax_devil_device_api.errors import ApiError, HttpError, NotSupported, ResponseFormatError

PATH = "/axis-cgi/mqtt/client.cgi"
MQTT_ERROR_2104 = "Invalid parameter value specified"


def envelope(method: str, data: Any = None, *, error: Any = None, version: str = "1.0") -> dict[str, Any]:
    body: dict[str, Any] = {"apiVersion": version, "method": method}
    if error is not None:
        body["error"] = error
    else:
        body["data"] = {} if data is None else data
    return body


class Camera:
    """Scriptable JSON-RPC device. Records every request body in ``bodies``."""

    def __init__(
        self,
        advertised: tuple[str, ...] = ("1.0",),
        replies: dict[str, Callable[[dict[str, Any]], httpx.Response] | httpx.Response] | None = None,
    ) -> None:
        self.advertised = list(advertised)
        self.replies = dict(replies or {})
        self.bodies: list[dict[str, Any]] = []
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        body = json.loads(request.content)
        self.bodies.append(body)
        method = body["method"]
        if method == "getSupportedVersions":
            return httpx.Response(200, json=envelope(method, {"apiVersions": self.advertised}, version="1.0"))
        reply = self.replies.get(method)
        if callable(reply):
            return reply(body)
        if reply is not None:
            return reply
        return httpx.Response(200, json=envelope(method))

    def calls(self, method: str) -> list[dict[str, Any]]:
        return [b for b in self.bodies if b.get("method") == method]


def connect(camera: Camera) -> Device:
    return Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(camera))


def connect_async(camera: Camera) -> AsyncDevice:
    return AsyncDevice("cam", credentials=("u", "p"), transport=httpx.MockTransport(camera))


# ---------------------------------------------------------------------------
# Negotiation


def test_negotiation_runs_once_per_device_across_calls() -> None:
    camera = Camera(
        replies={
            "getClientStatus": httpx.Response(
                200,
                json=envelope("getClientStatus", {"status": {"state": "active", "connectionStatus": "connected"}}),
            ),
        }
    )
    with connect(camera) as dev:
        mqtt = dev.apis.mqtt_client
        mqtt.activate_client()
        mqtt.deactivate_client()
        status = mqtt.get_client_status()

    assert status.status.state == "active"
    assert len(camera.calls("getSupportedVersions")) == 1
    assert [b["apiVersion"] for b in camera.calls("activateClient")] == ["1.0"]
    assert [b["apiVersion"] for b in camera.calls("deactivateClient")] == ["1.0"]


@pytest.mark.parametrize("advertised", [("1.0",), ("1.0", "1.5"), ("1.0", "2.0")])
def test_sent_version_is_lower_of_device_and_client_maximum(advertised: tuple[str, ...]) -> None:
    # The client knows only 1.0, so it must speak 1.0 whatever the device offers
    # above that; a device offering nothing newer than 1.0 also yields 1.0.
    camera = Camera(advertised=advertised)
    with connect(camera) as dev:
        dev.apis.mqtt_client.activate_client()

    assert camera.calls("activateClient")[0]["apiVersion"] == "1.0"


def test_device_offering_only_newer_major_is_not_supported() -> None:
    camera = Camera(advertised=("2.0",))
    with connect(camera) as dev, pytest.raises(NotSupported, match="device offers API versions 2.0"):
        dev.apis.mqtt_client.activate_client()

    assert camera.calls("activateClient") == []


def test_refresh_forces_renegotiation() -> None:
    camera = Camera()
    with connect(camera) as dev:
        dev.apis.mqtt_client.activate_client()
        dev.refresh()
        dev.apis.mqtt_client.activate_client()

    assert len(camera.calls("getSupportedVersions")) == 2


# ---------------------------------------------------------------------------
# Response envelopes and error mapping


def test_error_envelope_with_http_200_is_api_error() -> None:
    camera = Camera(
        replies={
            "activateClient": httpx.Response(
                200,
                json=envelope("activateClient", error={"code": 2104, "message": "bad value"}),
            ),
        }
    )
    with connect(camera) as dev, pytest.raises(ApiError) as caught:
        dev.apis.mqtt_client.activate_client()

    error = caught.value
    assert error.code == 2104
    assert error.message == "bad value"
    assert error.description == MQTT_ERROR_2104
    assert error.http_status == 200
    assert error.api == "mqtt-client"
    assert error.operation == "activate_client"


def test_error_body_wins_over_http_400() -> None:
    camera = Camera(
        replies={
            "activateClient": httpx.Response(
                400,
                json=envelope("activateClient", error={"code": 2104, "message": "bad value"}),
            ),
        }
    )
    with connect(camera) as dev, pytest.raises(ApiError) as caught:
        dev.apis.mqtt_client.activate_client()

    assert caught.value.code == 2104
    assert caught.value.http_status == 400


def test_http_500_non_json_is_http_error() -> None:
    camera = Camera(replies={"activateClient": httpx.Response(500, text="internal failure")})
    with connect(camera) as dev, pytest.raises(HttpError) as caught:
        dev.apis.mqtt_client.activate_client()

    assert caught.value.status == 500


def test_http_404_is_not_supported() -> None:
    camera = Camera(replies={"activateClient": httpx.Response(404, text="Not Found")})
    with connect(camera) as dev, pytest.raises(NotSupported, match="not found"):
        dev.apis.mqtt_client.activate_client()


def test_http_200_non_json_is_response_format_error() -> None:
    camera = Camera(replies={"activateClient": httpx.Response(200, text="<html>login</html>")})
    with connect(camera) as dev, pytest.raises(ResponseFormatError):
        dev.apis.mqtt_client.activate_client()


def test_response_method_mismatch_is_response_format_error() -> None:
    camera = Camera(replies={"activateClient": httpx.Response(200, json=envelope("deactivateClient"))})
    with connect(camera) as dev, pytest.raises(ResponseFormatError, match="deactivateClient"):
        dev.apis.mqtt_client.activate_client()


# ---------------------------------------------------------------------------
# Request shape


def test_activate_client_sends_no_params_key() -> None:
    camera = Camera()
    with connect(camera) as dev:
        dev.apis.mqtt_client.activate_client()

    assert camera.calls("activateClient") == [{"apiVersion": "1.0", "method": "activateClient"}]


def test_unset_optional_arguments_are_absent_from_params() -> None:
    camera = Camera()
    with connect(camera) as dev:
        dev.apis.mqtt_client.configure_client(server=Server(host="broker"), client_id="cam1")

    [body] = camera.calls("configureClient")
    assert body["params"] == {"server": {"host": "broker"}, "clientId": "cam1"}


def test_set_optional_argument_is_sent_with_alias() -> None:
    camera = Camera()
    with connect(camera) as dev:
        dev.apis.mqtt_client.configure_client(
            server=Server(host="broker", port=1883),
            client_id="cam1",
            keep_alive_interval=30,
        )

    [body] = camera.calls("configureClient")
    assert body["params"] == {"server": {"host": "broker", "port": 1883}, "clientId": "cam1", "keepAliveInterval": 30}


def test_request_has_json_content_type_and_accept() -> None:
    camera = Camera()
    with connect(camera) as dev:
        dev.apis.mqtt_client.activate_client()

    request = next(r for r in camera.requests if json.loads(r.content)["method"] == "activateClient")
    assert request.headers["content-type"] == "application/json"
    assert request.headers["accept"] == "application/json"
    assert request.url.path == PATH


# ---------------------------------------------------------------------------
# Binding options, driven through flow_for directly


class Args(Model):
    name: str
    count: int | None = None


INFO = ApiInfo(
    id="test-jsonrpc",
    name="Test JSON-RPC API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
)


def run_op(device: Device, binding: JsonRpcBinding, params: Model | None) -> Any:
    op = Operation(INFO, "ping", binding=binding, params=Args)
    return run_sync(device._transport, flow_for(op, params, device._state))


def test_top_level_placement_merges_args_into_envelope() -> None:
    camera = Camera()
    binding = JsonRpcBinding("ping", PATH, params_placement="top_level", negotiation=FixedVersion(ApiVersion(1, 0)))
    with connect(camera) as dev:
        run_op(dev, binding, Args(name="cam1", count=3))

    [body] = camera.calls("ping")
    assert body == {"apiVersion": "1.0", "method": "ping", "name": "cam1", "count": 3}
    assert "params" not in body


def test_fixed_version_sends_version_without_negotiating() -> None:
    camera = Camera()
    binding = JsonRpcBinding("ping", PATH, negotiation=FixedVersion(ApiVersion(1, 0)))
    with connect(camera) as dev:
        run_op(dev, binding, Args(name="cam1"))

    assert camera.calls("getSupportedVersions") == []
    assert camera.calls("ping") == [{"apiVersion": "1.0", "method": "ping", "params": {"name": "cam1"}}]


def test_no_version_omits_api_version_without_negotiating() -> None:
    camera = Camera()
    binding = JsonRpcBinding("ping", PATH, negotiation=NoVersion())
    with connect(camera) as dev:
        run_op(dev, binding, None)

    assert camera.calls("getSupportedVersions") == []
    assert camera.calls("ping") == [{"method": "ping"}]


# ---------------------------------------------------------------------------
# AsyncDevice


@pytest.mark.anyio
async def test_async_negotiation_runs_once_across_calls() -> None:
    camera = Camera()
    async with connect_async(camera) as dev:
        await dev.apis.mqtt_client.activate_client()
        await dev.apis.mqtt_client.deactivate_client()

    assert len(camera.calls("getSupportedVersions")) == 1
    assert [b["apiVersion"] for b in camera.calls("activateClient")] == ["1.0"]
    assert [b["apiVersion"] for b in camera.calls("deactivateClient")] == ["1.0"]


@pytest.mark.anyio
async def test_async_error_envelope_with_http_200_is_api_error() -> None:
    camera = Camera(
        replies={
            "activateClient": httpx.Response(
                200,
                json=envelope("activateClient", error={"code": 2104, "message": "bad value"}),
            ),
        }
    )
    async with connect_async(camera) as dev:
        with pytest.raises(ApiError) as caught:
            await dev.apis.mqtt_client.activate_client()

    assert caught.value.code == 2104
    assert caught.value.description == MQTT_ERROR_2104
    assert caught.value.http_status == 200


@pytest.mark.anyio
async def test_async_device_offering_only_newer_major_is_not_supported() -> None:
    camera = Camera(advertised=("2.0",))
    async with connect_async(camera) as dev:
        with pytest.raises(NotSupported):
            await dev.apis.mqtt_client.activate_client()

    assert camera.calls("activateClient") == []


# ---------------------------------------------------------------------------
# Error envelope variants


def _failure(body: dict[str, Any]) -> ApiError:
    camera = Camera(replies={"activateClient": httpx.Response(200, json=body)})
    with connect(camera) as dev, pytest.raises(ApiError) as caught:
        dev.apis.mqtt_client.activate_client()
    return caught.value


def test_error_member_names_error_code_and_error_msg() -> None:
    error = _failure(envelope("activateClient", error={"errorCode": 2002, "errorMsg": "locale not supported"}))
    assert (error.code, error.message) == (2002, "locale not supported")


def test_top_level_errors_array_is_api_error_with_first_entry() -> None:
    body = {
        "apiVersion": "1.0",
        "method": "activateClient",
        "errors": [{"code": 400, "message": "Failed to connect", "viewId": 0}, {"code": 100, "message": "15"}],
    }
    error = _failure(body)
    assert error.code == 400
    assert error.message == "Failed to connect (and 1 more error)"
    assert error.details == body["errors"]


def test_errors_array_next_to_data_is_not_a_failure() -> None:
    camera = Camera(
        replies={"activateClient": httpx.Response(200, json={**envelope("activateClient"), "errors": [{"code": 400, "message": "x"}]})}
    )
    with connect(camera) as dev:
        dev.apis.mqtt_client.activate_client()
