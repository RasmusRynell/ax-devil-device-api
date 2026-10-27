"""Format errors (not only device error messages) never carry device text for an operation that handles secrets:
the version list and the echoed method of a JSON-RPC reply, content types, a bad XML declaration. Nothing of it is in
str, repr, args, the formatted traceback, ``__cause__`` or ``__context__``; other operations get a redacted, bounded form."""

from __future__ import annotations

import traceback
from typing import Any

import httpx
import pytest

from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, has_secret_fields
from ax_devil_device_api._protocols.cgi import Binary, CgiBinding, Xml
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventsCodec
from ax_devil_device_api.apis.basic_device_info import PATH as BASIC_PATH
from ax_devil_device_api.apis.mqtt_client import OPS, PATH
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import DeviceError, ResponseFormatError
from ax_devil_device_api.testing import MockCamera

SENTINEL = "SENTINEL-SECRET-VALUE"


def _clean(error: BaseException) -> None:
    rendered = "".join(traceback.format_exception(error))
    assert SENTINEL not in str(error) and SENTINEL not in repr(error) and SENTINEL not in rendered
    assert not any(SENTINEL in repr(arg) for arg in error.args)
    assert error.__cause__ is None and error.__context__ is None


def _reply(**fields: Any) -> httpx.Response:
    return httpx.Response(200, json={"apiVersion": "1.0", **fields})


def _versions(camera: MockCamera, path: str, versions: list[Any]) -> None:
    camera.route("POST", path, lambda request: _reply(method="getSupportedVersions", data={"apiVersions": versions}) if b"getSupportedVersions" in request.content else _reply(data={}))


def test_the_operation_is_secret_bearing() -> None:
    assert has_secret_fields(OPS.get_client_status)


# -- JSON-RPC: the advertised versions ----------------------------------------------------------------------------------


def test_an_unreadable_advertised_version_of_a_secret_operation_leaks_nothing() -> None:
    camera = MockCamera()
    _versions(camera, PATH, [SENTINEL])
    with camera.device() as dev, pytest.raises(ResponseFormatError) as caught:
        dev.apis.mqtt_client.get_client_status()
    _clean(caught.value)
    assert "getSupportedVersions" in str(caught.value) and "omitted" in str(caught.value)


@pytest.mark.anyio
async def test_the_same_through_the_async_path() -> None:
    camera = MockCamera()
    _versions(camera, PATH, [SENTINEL])
    async with camera.async_device() as dev:
        with pytest.raises(ResponseFormatError) as caught:
            await dev.apis.mqtt_client.get_client_status()
    _clean(caught.value)


def test_an_unreadable_advertised_version_of_another_operation_is_shown_redacted_and_bounded() -> None:
    camera = MockCamera()
    _versions(camera, BASIC_PATH, ["password=hunter2 " + "x" * 5000])
    with camera.device() as dev, pytest.raises(ResponseFormatError) as caught:
        dev.apis.basic_device_info.get_all_properties()
    text = str(caught.value)
    assert "not a major.minor version" in text and "password" in text and "hunter2" not in text and len(text) < 1500
    assert caught.value.__cause__ is None


# -- JSON-RPC: the echoed method ----------------------------------------------------------------------------------------


def test_an_echoed_method_of_a_secret_operation_leaks_nothing() -> None:
    camera = MockCamera()
    camera.route(
        "POST",
        PATH,
        lambda request: _reply(method="getSupportedVersions", data={"apiVersions": ["1.0"]})
        if b"getSupportedVersions" in request.content
        else _reply(method=SENTINEL, data={}),
    )
    with camera.device() as dev, pytest.raises(ResponseFormatError) as caught:
        dev.apis.mqtt_client.get_client_status()
    _clean(caught.value)
    assert "getClientStatus" in str(caught.value)


@pytest.mark.anyio
async def test_an_echoed_method_through_the_async_path() -> None:
    camera = MockCamera()
    camera.route(
        "POST",
        PATH,
        lambda request: _reply(method="getSupportedVersions", data={"apiVersions": ["1.0"]})
        if b"getSupportedVersions" in request.content
        else _reply(method={"x": SENTINEL}, data={}),
    )
    async with camera.async_device() as dev:
        with pytest.raises(ResponseFormatError) as caught:
            await dev.apis.mqtt_client.get_client_status()
    _clean(caught.value)


def test_an_echoed_method_of_another_operation_is_shown_redacted() -> None:
    camera = MockCamera()
    camera.route(
        "POST",
        BASIC_PATH,
        lambda request: _reply(method="getSupportedVersions", data={"apiVersions": ["1.0"]})
        if b"getSupportedVersions" in request.content
        else _reply(method="token=abc123 other", data={}),
    )
    with camera.device() as dev, pytest.raises(ResponseFormatError) as caught:
        dev.apis.basic_device_info.get_all_properties()
    assert "response is for method" in str(caught.value) and "other" in str(caught.value) and "abc123" not in str(caught.value)


# -- content types and XML declarations ---------------------------------------------------------------------------------


class Secret(Model):
    __masked__ = frozenset({"key"})  # type: ignore[assignment]
    key: str | None = None


def _info() -> ApiInfo:
    return ApiInfo(id="t", name="T", family=Family.CGI)


def _invoke(op: Operation[Any], response: httpx.Response) -> DeviceError:
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(lambda request: response)) as dev:
        with pytest.raises(DeviceError) as caught:
            dev.invoke(op)
    return caught.value


def test_a_content_type_of_a_secret_operation_leaks_nothing() -> None:
    op = Operation(_info(), "get", CgiBinding("/x.cgi", reply=Binary(media_types=("image/jpeg",))), result=Secret)
    error = _invoke(op, httpx.Response(200, content=b"x", headers={"content-type": f"application/{SENTINEL}"}))
    assert isinstance(error, ResponseFormatError)
    lowered = SENTINEL.lower()  # the media type is normalized to lower case
    assert lowered not in str(error).lower() and lowered not in repr(error).lower() and "unexpected content type" in str(error)


def test_an_unknown_xml_encoding_of_a_secret_operation_leaks_nothing() -> None:
    op = Operation(_info(), "get", CgiBinding("/x.cgi", reply=Xml()), result=Secret)
    error = _invoke(op, httpx.Response(200, content=f'<?xml version="1.0" encoding="{SENTINEL}"?><a/>'.encode(), headers={"content-type": "text/xml"}))
    assert isinstance(error, ResponseFormatError)
    rendered = "".join(traceback.format_exception(error))
    assert SENTINEL not in str(error) and SENTINEL not in repr(error) and SENTINEL not in rendered


# -- the WebSocket codecs carry no operation: they never repeat a malformed value ----------------------------------------


def _no_text(error: BaseException) -> None:
    assert SENTINEL not in str(error) and SENTINEL not in repr(error) and SENTINEL not in "".join(traceback.format_exception(error))


def test_ws_codec_errors_name_the_json_type_not_the_value() -> None:
    events, hub = EventsCodec(), DataHubCodec()
    messages: list[tuple[Any, dict[str, Any]]] = [
        (events, {"method": "events:notify", "params": SENTINEL}),
        (events, {"method": "events:notify", "params": {"notification": [SENTINEL]}}),
        (events, {"method": "events:notify", "params": {"notification": {"topic": {"x": SENTINEL}, "message": {}}}}),
        (events, {"context": "1", "error": {"code": [SENTINEL], "message": SENTINEL}}),
        (events, {"context": "1", "error": SENTINEL}),
        (hub, {"id": 1, "error": {"code": 1, "message": {"x": SENTINEL}}}),
        (hub, {"method": "data-hub_v1:topicSample", "params": SENTINEL}),
    ]
    for codec, message in messages:
        with pytest.raises(ResponseFormatError) as caught:
            codec.classify(message)
        _no_text(caught.value)


def test_a_topic_sample_with_an_unexpected_key_does_not_repeat_it() -> None:
    sample = {"subscriptionId": 5, "topic": "t", "instance": {}, "data": {}, "timestamp": "2020-01-01T00:00:00Z", SENTINEL: 1}
    with pytest.raises(ResponseFormatError) as caught:
        DataHubCodec().classify({"method": "data-hub_v1:topicSample", "params": sample})
    _no_text(caught.value)
    assert "subscriptionId" in str(caught.value)
