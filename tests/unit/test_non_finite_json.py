"""NaN, Infinity and -Infinity are not JSON: every JSON decoder refuses them as a malformed response."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from ax_devil_device_api._http.types import Headers, Request, Response, loads_json
from ax_devil_device_api._protocols import cgi, dca, jsonrpc, rest, service_json
from ax_devil_device_api._protocols.state import DeviceState
from ax_devil_device_api._runtime.capabilities import dca_apis_flow
from ax_devil_device_api.apis import audio_relay_service, decoder, demographic_identifier, mqtt_client
from ax_devil_device_api.errors import ResponseFormatError

CONSTANTS = ["NaN", "Infinity", "-Infinity"]


def response(body: str) -> Response:
    return Response(200, Headers([("Content-Type", "application/json")]), body.encode(), Request("POST", "/x"))


@pytest.mark.parametrize("constant", CONSTANTS)
def test_loads_json_rejects_non_finite_constants(constant: str) -> None:
    with pytest.raises(ValueError, match="non-finite"):
        loads_json(f'{{"v": {constant}}}')
    with pytest.raises(ValueError):
        loads_json(f"[{constant}]".encode())
    assert loads_json('{"v": 1.5, "w": [true, null]}') == {"v": 1.5, "w": [True, None]}


def _dca(body: str) -> Any:
    return dca._decode(mqtt_client.OPS.get_client_status, response(body))  # type: ignore[arg-type]


def _jsonrpc(body: str) -> Any:
    return jsonrpc._decode(decoder.OPS.get_capabilities, response(body))


def _rest(body: str) -> Any:
    from ax_devil_device_api.apis import intercom_configuration

    return rest._decode(intercom_configuration.OPS.get_configuration, response(body))


def _service_json(body: str) -> Any:
    return service_json._decode(audio_relay_service.OPS.get_service_capabilities, response(body))


def _cgi(body: str) -> Any:
    return cgi._decode(demographic_identifier.OPS.get_live_tracks, response(body))


def _discover(body: str) -> Any:
    flow = dca_apis_flow(DeviceState())
    next(flow)
    try:
        flow.send(response(body))
    except StopIteration as done:
        return done.value


DECODERS: dict[str, Callable[[str], Any]] = {
    "dca": _dca,
    "jsonrpc": _jsonrpc,
    "rest": _rest,
    "service_json": _service_json,
    "cgi": _cgi,
    "discover": _discover,
}


@pytest.mark.parametrize("constant", CONSTANTS)
@pytest.mark.parametrize("name", sorted(DECODERS))
def test_decoders_refuse_non_finite_constants(name: str, constant: str) -> None:
    body = f'{{"apiVersion": "1.0", "method": "m", "data": {{"value": {constant}}}, "apis": {{"x": [{constant}]}}}}'
    with pytest.raises(ResponseFormatError):
        DECODERS[name](body)


@pytest.mark.parametrize("constant", CONSTANTS)
def test_websocket_messages_refuse_non_finite_constants(constant: str) -> None:
    from ws_fake import FakeWsCamera

    from ax_devil_device_api import Device
    from ax_devil_device_api._http.options import Heartbeat
    from ax_devil_device_api._runtime.ws import EVENTS

    camera = FakeWsCamera()
    dev = Device("cam.test", credentials=("root", "pass"), transport=camera.transport())
    with dev.connect_session(EVENTS, heartbeat=Heartbeat(None)) as session:
        camera.sockets[0].push({"v": float(constant.lower().replace("infinity", "inf"))})  # json.dumps writes NaN/Infinity
        with pytest.raises(ResponseFormatError):
            session.receive(timeout=2)
