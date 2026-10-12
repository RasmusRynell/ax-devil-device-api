"""Documented plain-text CGI error replies (HTTP 200 with ``Error: ...`` bodies)."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ax_devil_device_api._protocols.base import ApiInfo, ErrorCode, Family, Operation
from ax_devil_device_api._protocols.cgi import CgiBinding, Text, TextKv, TextOk
from ax_devil_device_api.device import AsyncDevice, Device
from ax_devil_device_api.errors import ApiError, ApiUnavailable

INFO = ApiInfo(
    id="t", name="T", family=Family.CGI,
    errors={4: ErrorCode("Application not found", "not_found"), 6: ErrorCode("Busy", "unavailable")},
)


def make(codec: Any) -> Operation[CgiBinding]:
    return Operation(INFO, "op", binding=CgiBinding("/axis-cgi/t.cgi", reply=codec))


def handler(body: str, status: int = 200) -> Any:
    return lambda request: httpx.Response(status, text=body)


CASES = [
    ("Error: 4\n", 4, "4"),
    ("Error: 6", 6, "6"),
    ("Error: 99", 99, "99"),
    ("Error:\nquery: unknown value: x\n", None, "query: unknown value: x"),
    ("Error:\n4\n", 4, "4"),
    ("Error:  invalid password.", None, "invalid password."),
    ("\n# Error: Error setting 'a' to 'b'!\n", None, "Error: Error setting 'a' to 'b'!"),
]


@pytest.mark.parametrize("codec", [TextOk(), Text(), TextKv()])
@pytest.mark.parametrize(("body", "code", "message"), CASES)
def test_sync(codec: Any, body: str, code: int | None, message: str) -> None:
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler(body))) as dev:
        with pytest.raises(ApiError) as caught:
            dev.invoke(make(codec))
    assert caught.value.code == code
    assert message in caught.value.message


@pytest.mark.anyio
@pytest.mark.parametrize("codec", [TextOk(), Text(), TextKv()])
@pytest.mark.parametrize(("body", "code", "message"), CASES)
async def test_async(codec: Any, body: str, code: int | None, message: str) -> None:
    async with AsyncDevice("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler(body))) as dev:
        with pytest.raises(ApiError) as caught:
            await dev.invoke(make(codec))
    assert caught.value.code == code
    assert message in caught.value.message


def test_documented_code_selects_kind() -> None:
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler("Error: 6"))) as dev:
        with pytest.raises(ApiUnavailable) as caught:
            dev.invoke(make(TextOk()))
    assert caught.value.kind == "unavailable"
    assert caught.value.description == "Busy"


def test_error_reply_with_failure_status() -> None:
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler("Error: 4", 400))) as dev:
        with pytest.raises(ApiError) as caught:
            dev.invoke(make(Text()))
    assert (caught.value.code, caught.value.http_status) == (4, 400)


@pytest.mark.parametrize("body", ["OK", "OK\n"])
def test_ok_still_succeeds(body: str) -> None:
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler(body))) as dev:
        assert dev.invoke(make(TextOk())) is None


def test_non_error_text_is_untouched() -> None:
    from ax_devil_device_api._http.types import Headers, Request, Response
    from ax_devil_device_api._protocols.cgi import _decode

    kv = "root.Foo=Error: not at the start\nroot.Bar=1\n"
    response = Response(200, Headers(), kv.encode(), Request("GET", "/x"))
    assert _decode(make(TextKv()), response) == {"root.Foo": "Error: not at the start", "root.Bar": "1"}
    response = Response(200, Headers(), b"Errors: none\n", Request("GET", "/x"))
    assert _decode(make(Text()), response) == "Errors: none\n"
