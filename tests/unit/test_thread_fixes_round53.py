"""D19: the DeviceError base class owns how an error is shown. Every text field of every subclass goes through
``display_text`` (secret-name pairs and URL credentials redacted, control characters escaped, length bounded)."""

from __future__ import annotations

import inspect
import io
import json
import traceback
import types
import typing
from typing import Any, Literal, Union, get_args, get_origin

import httpx
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device, cli, errors
from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, parse_result
from ax_devil_device_api._protocols.cgi import CgiBinding, Text
from ax_devil_device_api._runtime.capabilities import Capabilities, Support, SupportResult, malformed_reason
from ax_devil_device_api._runtime.ws_codecs import EventsCodec, WsError, api_error
from ax_devil_device_api.errors import ApiError, DeviceError, SessionClosed, display_text, sanitize_details
from ax_devil_device_api.testing import MockCamera

NASTY = ["password=hunter2", "rtsp://u:p@h/x", "\r\nINJECTED-LINE"]
FORBIDDEN = ["hunter2", "u:p@", "\r", "\nINJECTED-LINE"]


def _all_subclasses(cls: type) -> list[type]:
    found: list[type] = []
    for sub in cls.__subclasses__():
        for item in (sub, *_all_subclasses(sub)):
            if item not in found:  # diamonds (HttpAccessDenied) are reachable twice
                found.append(item)
    return found


def _kinds(hint: Any) -> set[Any]:
    if get_origin(hint) in (Union, types.UnionType):
        return {kind for arg in get_args(hint) for kind in _kinds(arg)}
    if get_origin(hint) is Literal:
        return {Literal}
    return {hint}


def _build(cls: type, nasty: str) -> BaseException:
    """An instance with ``nasty`` in every string-capable parameter; a class taking only ``*args`` gets it as its message."""
    arguments = _arguments(cls, nasty)
    return cls(nasty) if not arguments else cls(**arguments)


def _arguments(cls: type, nasty: str) -> dict[str, Any]:
    """Keyword arguments that put ``nasty`` into every string-capable parameter (and a nested structure into ``Any``)."""
    signature = inspect.signature(cls.__init__)
    hints = typing.get_type_hints(cls.__init__, vars(__import__("ax_devil_device_api.errors", fromlist=["x"])))
    arguments: dict[str, Any] = {}
    for name, parameter in signature.parameters.items():
        if name in ("self", "args") or parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            continue
        kinds = _kinds(hints.get(name, str))
        if str in kinds:
            arguments[name] = nasty
        elif Any in kinds:
            arguments[name] = {"k": nasty, nasty: [nasty], "n": 1}
        elif int in kinds:
            arguments[name] = 7
        elif parameter.default is inspect.Parameter.empty:
            arguments[name] = nasty
    return arguments


def _shown(error: BaseException) -> list[str]:
    try:
        raise error
    except BaseException as caught:  # noqa: BLE001
        rendered = "".join(traceback.format_exception(caught))
    return [str(error), repr(error), rendered]


def test_the_enumeration_finds_the_whole_hierarchy() -> None:
    names = {cls.__name__ for cls in _all_subclasses(DeviceError)}
    assert {"ApiError", "ApiAccessDenied", "HttpError", "SessionClosed", "ConnectionFailed", "ResponseFormatError", "NotSupported", "ConfigurationError"} <= names


@pytest.mark.parametrize("nasty", NASTY)
@pytest.mark.parametrize("cls", [DeviceError, *_all_subclasses(DeviceError)], ids=lambda cls: cls.__name__)
def test_no_device_error_shows_a_secret_a_credential_or_a_control_character(cls: type, nasty: str) -> None:
    error = _build(cls, nasty)
    for text in _shown(error):
        for forbidden in FORBIDDEN:
            if forbidden in nasty or forbidden == "\r" and "\r" in nasty:
                assert forbidden not in text, (cls.__name__, forbidden, text)


# Matching uses raw values BEFORE an error is built, so every attribute an exception carries is in its shown form.
RAW_MATCHING_ATTRIBUTES: set[str] = set()  # none: matching uses the raw code before an error is built; .code is the shown form


def _strings(value: Any, seen: set[int]) -> list[str]:
    """Every string reachable from ``value``: dict keys and values, sequences, and the ``__dict__`` of other objects."""
    if id(value) in seen:
        return []
    seen.add(id(value))
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for key, item in value.items() for text in (*_strings(key, seen), *_strings(item, seen))]
    if isinstance(value, (list, tuple, set, frozenset)):
        return [text for item in value for text in _strings(item, seen)]
    if hasattr(value, "__dict__") and not isinstance(value, type):
        return _strings(vars(value), seen)
    return []


@pytest.mark.parametrize("nasty", NASTY)
@pytest.mark.parametrize("cls", [DeviceError, *_all_subclasses(DeviceError)], ids=lambda cls: cls.__name__)
def test_no_public_attribute_of_a_device_error_holds_a_secret_a_credential_or_a_control_character(cls: type, nasty: str) -> None:
    error = _build(cls, nasty)
    for name, value in vars(error).items():
        if name in RAW_MATCHING_ATTRIBUTES:
            continue
        for text in [*_strings(value, set()), name]:
            for forbidden in FORBIDDEN:
                if forbidden in nasty:
                    assert forbidden not in text, (cls.__name__, name, forbidden, text)


def test_the_charset_error_carries_a_label_not_the_request_path() -> None:
    from ax_devil_device_api._http.types import Headers, Request, Response

    request = Request("GET", "/axis-cgi/x.cgi/user%3Dpassword%3Dhunter2")
    response = Response(200, Headers([("content-type", "text/plain; charset=nonsense-charset")]), b"x", request)
    with pytest.raises(errors.ResponseFormatError) as caught:
        response.text  # noqa: B018
    assert (caught.value.api, caught.value.operation) == ("http", "response_text")
    assert "hunter2" not in json.dumps(vars(caught.value)) and "hunter2" not in str(caught.value)


def test_a_subclass_that_bypasses_the_base_init_is_still_shown_safely() -> None:
    class Sloppy(DeviceError):
        def __init__(self, text: str) -> None:  # never calls super().__init__
            self.text = text

        def __new__(cls, text: str) -> Sloppy:
            instance = super().__new__(cls, text)
            return instance

    error = Sloppy("password=hunter2\r\nINJECTED-LINE")
    for text in _shown(error):
        assert "hunter2" not in text and "\nINJECTED-LINE" not in text and "\r" not in text


# -- display_text -----------------------------------------------------------------------------------------------------


def test_display_text_redacts_escapes_and_bounds_and_is_idempotent() -> None:
    text = display_text("login password=hunter2 at rtsp://u:p@h/x\r\nnext\x1b[31m", 200)
    assert "hunter2" not in text and "u:p@" not in text and "\\r\\n" in text and "\x1b" not in text
    assert display_text(text, 200) == text
    long = display_text("x" * 5000, 100)
    assert len(long) == 100 and display_text(long, 100) == long


def test_sanitize_details_keeps_the_structure() -> None:
    details = sanitize_details({"password": "hunter2", "list": ["rtsp://u:p@h", {"n": 1}], "a\r\nb": "x\ny", "ok": True, "none": None})
    assert details["password"] != "hunter2" and "u:p@" not in json.dumps(details)
    assert details["ok"] is True and details["none"] is None and details["list"][1] == {"n": 1}
    assert "a\\r\\nb" in details and details["a\\r\\nb"] == "x\\ny"
    assert sanitize_details(sanitize_details(details)) == details
    assert len(sanitize_details(list(range(1000)))) == 101


# -- the six cases of the review ----------------------------------------------------------------------------------------


def test_the_string_code_is_not_shown_raw_and_the_public_code_is_the_shown_form() -> None:
    error = ApiError("api", "op", "password=hunter2\r\nINJECTED-LINE", "failed")
    assert error.code == "password=<redacted>\\r\\nINJECTED-LINE"
    for text in _shown(error):
        assert "hunter2" not in text and "\r" not in text and "\nINJECTED-LINE" not in text
    assert "failed" in str(error) and "error " in str(error)


def test_ws_error_data_is_sanitized_like_http_details() -> None:
    data = {"password": "hunter2", "url": "rtsp://u:p@h/x", "multi\r\nline": "a\r\nb"}
    error = api_error(EventsCodec(), "events:configure", WsError(7, "bad", data))
    assert isinstance(error.details, dict) and "hunter2" not in json.dumps(error.details) and "u:p@" not in json.dumps(error.details)
    assert all("\r" not in key and "\n" not in key for key in error.details)
    for text in _shown(error):
        assert "hunter2" not in text and "u:p@" not in text


def test_a_mapping_key_in_a_validation_location_is_sanitized() -> None:
    op = Operation(ApiInfo(id="t", name="T", family=Family.CGI), "get", CgiBinding("/x.cgi", reply=Text()), result=dict[str, bool])
    key = "password=hunter2 rtsp://u:p@h/\r\nINJECTED-LINE"
    with pytest.raises(errors.ResponseFormatError) as caught:
        parse_result(op, {key: "not a bool"})
    for text in _shown(caught.value):
        assert "hunter2" not in text and "u:p@" not in text and "\r" not in text and "\nINJECTED-LINE" not in text
    assert "result" in str(caught.value) or "bool" in str(caught.value)


class _Secret(Model):
    __masked__ = frozenset({"key"})  # type: ignore[assignment]
    key: str | None = None
    items: dict[str, bool] | None = None


def test_a_secret_operation_shows_a_mapping_key_as_a_wildcard() -> None:
    op = Operation(ApiInfo(id="t", name="T", family=Family.CGI), "get", CgiBinding("/x.cgi", reply=Text()), result=_Secret)
    with pytest.raises(errors.ResponseFormatError) as caught:
        parse_result(op, {"items": {"SENTINEL-KEY": "not a bool"}})
    assert "SENTINEL-KEY" not in str(caught.value) and "items.*" in str(caught.value)


def test_a_multipart_content_type_is_sanitized() -> None:
    from ax_devil_device_api._streams import MixedReplaceDecoder

    response = httpx.Response(200, headers={"content-type": "text/plain; x=password=hunter2 rtsp://u:p@h/"}, content=b"")
    from ax_devil_device_api._http.types import Response as LibResponse  # noqa: F401

    camera = MockCamera()
    camera.route("GET", "/stream", lambda _: response)
    with camera.device() as dev:
        with pytest.raises(errors.ResponseFormatError) as caught:
            dev.invoke(_stream_op())
    for text in _shown(caught.value):
        assert "hunter2" not in text and "u:p@" not in text
    assert MixedReplaceDecoder is not None


def _stream_op() -> Operation[Any]:
    from ax_devil_device_api._protocols.cgi import Stream

    return Operation(ApiInfo(id="t", name="T", family=Family.CGI), "stream", CgiBinding("/stream", reply=Stream(media_types=("multipart/x-mixed-replace",)), stream=True), result=None)


def test_a_close_reason_is_sanitized_in_session_closed_and_connection_failed() -> None:
    reason = "bye password=hunter2 rtsp://u:p@h/\r\nINJECTED-LINE"
    closed = SessionClosed(1000, reason)
    assert "hunter2" not in closed.reason and "\r" not in closed.reason
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(_events(), heartbeat=_quick()) as session:
            camera.sockets[0].close(1001, reason)
            with pytest.raises(errors.SessionClosed) as normal:
                session.receive(timeout=2)
        with dev.connect_session(_events(), heartbeat=_quick()) as session:
            camera.sockets[1].close(1011, reason)
            with pytest.raises(errors.ConnectionFailed) as abnormal:
                list(session)
    for error in (normal.value, abnormal.value):
        for text in _shown(error):
            assert "hunter2" not in text and "u:p@" not in text and "\r" not in text and "\nINJECTED-LINE" not in text
    assert "bye" in str(normal.value) and "bye" in str(abnormal.value)


@pytest.mark.anyio
async def test_the_same_close_reasons_through_the_async_path() -> None:
    reason = "bye password=hunter2 rtsp://u:p@h/\r\nINJECTED-LINE"
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(_events(), heartbeat=_quick()) as session:
            camera.sockets[0].close(1011, reason)
            with pytest.raises(errors.ConnectionFailed) as abnormal:
                [m async for m in session]
    for text in _shown(abnormal.value):
        assert "hunter2" not in text and "u:p@" not in text and "\nINJECTED-LINE" not in text


def _events() -> Any:
    from ax_devil_device_api._runtime.ws import EVENTS

    return EVENTS


def _quick() -> Any:
    from ax_devil_device_api._http.options import Heartbeat

    return Heartbeat(None)


# -- discovery diagnostics ------------------------------------------------------------------------------------------------

DISCOVERY = "/axis-cgi/apidiscovery.cgi"
BAD_ID = "password=hunter2 rtsp://u:p@h/\r\nINJECTED-LINE"


def _listing() -> MockCamera:
    camera = MockCamera()
    camera.identity(model="AXIS X", firmware="11.0.0")
    camera.jsonrpc(DISCOVERY, "getApiList", data={"apiList": [{"id": BAD_ID, "version": "garbage"}, {"id": "mqtt-client", "version": "1.0"}, 5]})
    return camera


def _clean(text: str) -> None:
    assert "hunter2" not in text and "u:p@" not in text and "\r" not in text and "\nINJECTED-LINE" not in text


def test_discovery_errors_in_capabilities_are_sanitized() -> None:
    with _listing().device() as dev:
        caps = dev.capabilities()
    assert caps.errors, "the malformed entries are reported"
    for key, text in caps.errors.items():
        _clean(key)
        _clean(text)


def test_malformed_reason_and_the_dataclasses_sanitize_on_construction() -> None:
    _clean(malformed_reason("apiList", BAD_ID, {"password": "hunter2", "u": BAD_ID}, "an object"))
    support = SupportResult(Support.UNKNOWN, f"unreadable firmware {BAD_ID!r}", (BAD_ID,))
    _clean(support.reason)
    _clean(" ".join(support.errors))
    caps = Capabilities(None, None, None, {BAD_ID: BAD_ID}, support.observed_at, applications_problems=(BAD_ID,), dca_malformed={"a": BAD_ID})
    _clean(" ".join([*caps.errors, *caps.errors.values(), *caps.applications_problems, *caps.dca_malformed.values()]))


def test_the_cli_output_of_supported_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    camera = _listing()
    monkeypatch.setattr(cli, "make_device", lambda args: camera.device())
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(["supported"], out=out, err=err)
    assert code == 0
    payload = json.loads(out.getvalue())
    assert payload["errors"]
    _clean(out.getvalue())
    _clean(err.getvalue())
