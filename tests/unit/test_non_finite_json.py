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


# --- absurdly deep nesting is a malformed response, never a RecursionError ------------------------------------------------------

DEEP = 100_000


def test_loads_json_turns_a_recursion_error_into_a_value_error() -> None:
    with pytest.raises(ValueError, match="nested too deeply"):
        loads_json("[" * DEEP + "]" * DEEP)
    assert loads_json("[" * 50 + "]" * 50) is not None


@pytest.mark.parametrize("name", sorted(DECODERS))
def test_decoders_refuse_deeply_nested_json(name: str) -> None:
    with pytest.raises(ResponseFormatError):
        DECODERS[name]("[" * DEEP + "]" * DEEP)


def test_websocket_messages_refuse_deeply_nested_json() -> None:
    import wsproto.events
    from ws_fake import FakeWsCamera

    from ax_devil_device_api import Device
    from ax_devil_device_api._http.options import Heartbeat
    from ax_devil_device_api._runtime.ws import EVENTS

    camera = FakeWsCamera()
    dev = Device("cam.test", credentials=("root", "pass"), transport=camera.transport())
    with dev.connect_session(EVENTS, heartbeat=Heartbeat(None)) as session:
        sock = camera.sockets[0]
        sock._emit(sock.conn.send(wsproto.events.TextMessage("[" * DEEP + "]" * DEEP)))
        with pytest.raises(ResponseFormatError):
            session.receive(timeout=2)


def test_error_details_of_deeply_nested_xml_do_not_overflow_the_stack() -> None:
    from ax_devil_device_api._protocols import soap
    from ax_devil_device_api.apis import certificate_management, export_recording
    from ax_devil_device_api.errors import ApiError

    deep = "<a>" * DEEP + "</a>" * DEEP
    envelope = (
        '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Body><s:Fault><s:Code><s:Value>x</s:Value></s:Code>'
        "<s:Reason><s:Text>t</s:Text></s:Reason><s:Detail>" + deep + "</s:Detail></s:Fault></s:Body></s:Envelope>"
    )
    fault = Response(500, Headers([("Content-Type", "application/soap+xml")]), envelope.encode(), Request("POST", "/x"))
    with pytest.raises(ApiError):
        soap._decode(certificate_management.OPS.load_pkcs12, fault)
    body = "<GeneralError><ErrorCode>1</ErrorCode><ErrorDescription>x</ErrorDescription>" + deep + "</GeneralError>"
    with pytest.raises(ApiError):
        cgi._decode(export_recording.OPS.get_properties, response(body))


# --- numbers that overflow to infinity (1e999) are refused like NaN and Infinity -----------------------------------------------

OVERFLOWS = ["1e999", "-1e999", "1E400", "-2.5e+9999", "123456789e999999"]


@pytest.mark.parametrize("number", OVERFLOWS)
def test_loads_json_refuses_numbers_that_overflow_to_infinity(number: str) -> None:
    for text in (number, f'{{"value": {number}}}', f"[1, {number}]"):
        with pytest.raises(ValueError, match="out of range"):
            loads_json(text)


def test_ordinary_and_tiny_numbers_still_parse() -> None:
    assert loads_json('{"a": 1.5, "b": -2e3, "c": 1e-999, "d": 1.7976931348623157e308, "e": 12}') == {
        "a": 1.5, "b": -2000.0, "c": 0.0, "d": 1.7976931348623157e308, "e": 12,
    }


@pytest.mark.parametrize("number", OVERFLOWS)
@pytest.mark.parametrize("name", sorted(DECODERS))
def test_decoders_refuse_overflowing_numbers(name: str, number: str) -> None:
    body = f'{{"apiVersion": "1.0", "method": "m", "data": {{"value": {number}}}, "apis": {{"x": [{number}]}}}}'
    with pytest.raises(ResponseFormatError):
        DECODERS[name](body)


@pytest.mark.parametrize("number", OVERFLOWS)
def test_websocket_receive_refuses_overflowing_numbers(number: str) -> None:
    import wsproto.events
    from ws_fake import FakeWsCamera

    from ax_devil_device_api import Device
    from ax_devil_device_api._http.options import Heartbeat
    from ax_devil_device_api._runtime.ws import EVENTS

    camera = FakeWsCamera()
    dev = Device("cam.test", credentials=("root", "pass"), transport=camera.transport())
    with dev.connect_session(EVENTS, heartbeat=Heartbeat(None)) as session:
        sock = camera.sockets[0]
        sock._emit(sock.conn.send(wsproto.events.TextMessage(f'{{"value": {number}}}')))
        with pytest.raises(ResponseFormatError):
            session.receive(timeout=2)
