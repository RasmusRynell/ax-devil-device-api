"""A non-text error message or code from the device is never stringified (no repr of a mapping for the redactor to miss):
the result is a ResponseFormatError that names only the types, in every protocol that reads an error object."""

from __future__ import annotations

import json
import traceback
from typing import Any

import httpx
import pytest
from test_invariants_garbage import _ops

from ax_devil_device_api import Device
from ax_devil_device_api._protocols.base import kind_of
from ax_devil_device_api.errors import DeviceError, ResponseFormatError

SECRET = "SENTINEL-HUNTER2"
NON_TEXT = [{"password": SECRET}, [SECRET], {"a": {"token": SECRET}}, 5, 1.5, True, None]

# (operation, envelope with @ where the raw message goes)
ENVELOPES = {
    "jsonrpc": ['{"error":{"code":1,"message":@}}', '{"error":{"errorCode":1,"errorMsg":@}}', '{"errors":[{"code":1,"message":@}]}', '{"error":@}'],
    "dca": ['{"status":"error","error":{"code":1,"message":@}}', '{"status":"error","error":@}'],
    "service-json": ['{"Fault":"f","FaultCode":"c","FaultMsg":@}', '{"Fault":@,"FaultCode":"c"}'],
    "cgi-json": ['{"error":{"id":1,"message":@}}'],
}


def _drive(name: str, body: str, status: int) -> BaseException:
    op = _ops()[name]
    transport = httpx.MockTransport(lambda request: httpx.Response(status, content=body.encode()))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev:
        try:
            dev.invoke(op)
        except DeviceError as error:
            return error
    raise AssertionError("the call did not fail")


def _clean(error: BaseException) -> None:
    rendered = "".join(traceback.format_exception(error))
    for text in (str(error), repr(error), rendered, json.dumps(getattr(error, "details", None), default=str)):
        assert SECRET not in text, text


@pytest.mark.parametrize("value", NON_TEXT, ids=lambda v: kind_of(v))
@pytest.mark.parametrize(("name", "envelope"), [(name, e) for name, envelopes in ENVELOPES.items() for e in envelopes])
def test_a_non_text_message_is_a_format_error_that_names_only_the_type(name: str, envelope: str, value: Any) -> None:
    if value is None and name == "service-json" and "FaultMsg" in envelope:
        pytest.skip("a null FaultMsg falls back to the next member")
    if value is None and name == "cgi-json":
        pytest.skip("a null message falls back to the default text")
    body = envelope.replace("@", json.dumps(value))
    error = _drive(name, body, 200)
    _clean(error)
    if isinstance(value, dict) and envelope.endswith('"error":@}'):
        return  # the whole error member is an object: an error object without a message, not a malformed one
    assert isinstance(error, ResponseFormatError), type(error).__name__
    assert "malformed error object" in str(error) or "not a JSON object" in str(error)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 500, 503])
@pytest.mark.parametrize(("name", "envelope"), [(name, e) for name, envelopes in ENVELOPES.items() for e in envelopes])
def test_no_status_turns_a_non_text_message_into_text(name: str, envelope: str, status: int) -> None:
    error = _drive(name, envelope.replace("@", json.dumps({"password": SECRET})), status)
    _clean(error)


@pytest.mark.parametrize("code", [{"password": SECRET}, [SECRET], 1.5, True, None])
@pytest.mark.parametrize("name", ["jsonrpc", "dca", "service-json"])
def test_a_non_scalar_code_is_never_shown(name: str, code: Any) -> None:
    body = {
        "jsonrpc": '{"error":{"code":@,"message":"m"}}',
        "dca": '{"status":"error","error":{"code":@,"message":"m"}}',
        "service-json": '{"Fault":"f","FaultCode":@,"FaultMsg":"m"}',
    }[name].replace("@", json.dumps(code))
    for status in (200, 500):
        _clean(_drive(name, body, status))


def test_the_message_of_a_malformed_error_object_is_the_type_only() -> None:
    error = _drive("jsonrpc", '{"error":{"code":1,"message":{"password":"' + SECRET + '"}}}', 200)
    assert isinstance(error, ResponseFormatError)
    assert "message is an object" in str(error) and SECRET not in str(error)


RAW = [{"password": SECRET}, [SECRET], 5, 1.5, True, None]


@pytest.mark.parametrize("status", [None, 200, 401, 403, 500, 503])
@pytest.mark.parametrize("code", [*RAW, 7, "7", "text"], ids=lambda v: kind_of(v) + str(v)[:6])
@pytest.mark.parametrize("message", [*RAW, "m"], ids=lambda v: kind_of(v) + str(v)[:6])
def test_api_error_shows_no_repr_of_any_raw_code_or_message(code: Any, message: Any, status: int | None) -> None:
    from ax_devil_device_api._protocols.base import api_error

    error = api_error(_ops()["jsonrpc"], code, message, http_status=status, details=None)
    _clean(error)
    valid = isinstance(message, str) and (code is None or (isinstance(code, (int, str)) and not isinstance(code, bool)))
    if not valid and status not in (401, 403, 503):
        assert isinstance(error, ResponseFormatError)


# -- internationalised host names are sent as IDNA ----------------------------------------------------------------------


def test_an_internationalised_host_is_idna_encoded_in_the_rtsp_url_and_the_base_url() -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api.rtsp import build_rtsp_url

    url = build_rtsp_url("bücher.example", path="/axis-media/media.amp")
    assert url.url.startswith("rtsp://xn--bcher-kva.example:554/") and "ü" not in url.url and "ü" not in url.safe
    config = ConnectionConfig("bücher.example")
    assert "xn--bcher-kva.example" in config.base_url and "ü" not in config.base_url
    assert build_rtsp_url("camera.local").url.startswith("rtsp://camera.local:554/")
    assert build_rtsp_url("::1").url.startswith("rtsp://[::1]:554/")


@pytest.mark.parametrize("host", ["bücher..example", "ü" * 70 + ".example", "bü cher.example"])
def test_an_invalid_internationalised_host_is_a_configuration_error(host: str) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api.errors import ConfigurationError
    from ax_devil_device_api.rtsp import build_rtsp_url

    with pytest.raises(ConfigurationError):
        build_rtsp_url(host)
    with pytest.raises(ConfigurationError):
        ConnectionConfig(host)
