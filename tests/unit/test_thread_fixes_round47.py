"""An operation that returns secret fields puts no part of a body into an error; others get a redacted excerpt."""

from __future__ import annotations

from typing import Annotated, Any

import httpx
import pytest
from pydantic import Field

from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, has_masked_fields
from ax_devil_device_api._protocols.cgi import CgiBinding, JsonReply, TextKv
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import ApiError, ResponseFormatError
from ax_devil_device_api.testing import MockCamera

KEY = "TOPSECRETSRTPKEYVALUE0123456789"
INFO = ApiInfo(id="t", name="T", family=Family.CGI)


def test_audio_multicast_source_with_a_bad_port_never_puts_the_srtp_key_in_the_error() -> None:
    camera = MockCamera()
    body = {"data": {"id": "s1", "label": "l", "port": 5, "srtpKey": KEY}}  # port out of range, key right next to it
    camera.rest("GET", "/config/rest/audio-multicast-ctrl/v1beta/sources/s1", data=body["data"])
    with camera.device() as dev, pytest.raises(ResponseFormatError) as caught:
        dev.apis.audio_multicast_ctrl.get_source("s1")
    error = caught.value
    for rendered in (str(error), repr(error), error.reason, repr(error.args)):
        assert KEY not in rendered
    assert "body omitted" in str(error) and "port" in str(error)  # the reason is still reported


class Plain(Model):
    value: int
    name: str | None = None


class Secret(Model):
    __masked__ = frozenset({"key"})  # type: ignore[assignment]
    key: str | None = None
    port: Annotated[int, Field(ge=1024)] = 2000


class Holder(Model):
    items: list[Secret] | None = None
    by_name: dict[str, Secret] | None = None
    maybe: Secret | None = None


@pytest.mark.parametrize(
    ("tp", "expected"),
    [
        (Plain, False), (Secret, True), (Holder, True), (list[Secret], True), (dict[str, Secret], True),
        (Secret | None, True), (Annotated[Secret, "x"], True), (list[Plain], False), (dict[str, list[Plain]], False),
        (int, False), (None, False), (Plain | None, False),
    ],
)
def test_masked_fields_are_found_at_any_depth(tp: Any, expected: bool) -> None:
    assert has_masked_fields(tp) is expected


def _json_op(result: Any) -> Operation[Any]:
    return Operation(INFO, "get", CgiBinding("/x.cgi", reply=JsonReply()), result=result)


def _invoke(op: Operation[Any], body: Any) -> Exception:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev:
        with pytest.raises(ResponseFormatError) as caught:
            dev.invoke(op)
    return caught.value


def test_a_non_masked_operation_still_gets_an_excerpt_and_a_password_in_it_is_redacted() -> None:
    error = _invoke(_json_op(Plain), {"value": "not a number", "name": "n", "password": "hunter2", "url": "https://u:pw@h/x"})
    message = str(error)
    assert "not a number" in message and '"name": "n"' in message  # an excerpt of what the device sent
    assert "hunter2" not in message and "pw@" not in message  # redacted by the hook rules
    assert len(message) < 900


@pytest.mark.parametrize("result", [Holder, list[Secret], dict[str, Secret]])
def test_nested_masked_fields_omit_the_excerpt_entirely(result: Any) -> None:
    body: Any = [{"key": KEY, "port": 1}] if result is list[Secret] else {"a": {"key": KEY, "port": 1}}
    if result is Holder:
        body = {"items": [{"key": KEY, "port": 1}]}
    error = _invoke(_json_op(result), body)
    assert KEY not in str(error) and "body omitted" in str(error)


def test_the_text_error_paths_of_a_masked_operation_leak_nothing() -> None:
    op = Operation(INFO, "get", CgiBinding("/x.cgi", reply=TextKv()), result=Secret)
    for text in (f"No such thing {KEY}", f"key={KEY}\nnot a pair {KEY}"):
        transport = httpx.MockTransport(lambda request, text=text: httpx.Response(200, text=text))
        with Device("cam", credentials=("u", "p"), transport=transport) as dev:
            with pytest.raises((ApiError, ResponseFormatError)) as caught:
                dev.invoke(op)
        error = caught.value
        assert KEY not in str(error) and KEY not in repr(error) and KEY not in str(getattr(error, "details", ""))


def test_a_non_masked_text_reply_still_carries_the_device_text() -> None:
    op = Operation(INFO, "get", CgiBinding("/x.cgi", reply=TextKv()), result=Plain)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="No camera specified (ex. camera=1)"))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev:
        with pytest.raises(ApiError) as caught:
            dev.invoke(op)
    assert "No camera specified" in caught.value.message
