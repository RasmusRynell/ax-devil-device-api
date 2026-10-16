"""Whitespace in credentials is refused at construction; a transport diagnostic never repeats a configured credential."""

from __future__ import annotations

import httpx
import pytest

from ax_devil_device_api._http.config import BearerToken, ConnectionConfig, Credentials
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import Request
from ax_devil_device_api.errors import ConfigurationError, ConnectionFailed

SECRET = "LONG-LIVED-SECRET"


# --- (a) construction ---------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("token", [SECRET + " ", " " + SECRET, "LONG-LIVED SECRET", SECRET + "\t", SECRET + " "])
def test_bearer_tokens_with_whitespace_are_refused_without_echoing_them(token: str) -> None:
    with pytest.raises(ConfigurationError, match="whitespace|control character") as info:
        BearerToken(token)
    assert SECRET not in str(info.value) and SECRET not in repr(info.value) and "LONG" not in str(info.value.args)


def test_a_callable_provider_is_checked_when_used() -> None:
    with pytest.raises(ConfigurationError, match="whitespace|control character") as info:
        BearerToken(lambda: SECRET + " ").current()
    assert SECRET not in str(info.value)


@pytest.mark.parametrize(("username", "password"), [("root ", "pw"), (" root", "pw"), ("ro ot", "pw"), ("root", SECRET + " "), ("root", " " + SECRET)])
def test_credentials_with_stray_whitespace_are_refused(username: str, password: str) -> None:
    with pytest.raises(ConfigurationError) as info:
        Credentials(username, password)
    assert SECRET not in str(info.value) and SECRET not in repr(info.value)


def test_a_password_may_contain_inner_spaces_and_a_clean_token_passes() -> None:
    assert Credentials("root", "pass phrase").password == "pass phrase"
    assert BearerToken(SECRET).current() == SECRET


# --- (b) transport diagnostics ---------------------------------------------------------------------------------------------------


def _leaky(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadError(f"invalid header value b'Bearer {SECRET}' / password {SECRET}", request=request)


def _assert_clean(error: ConnectionFailed) -> None:
    assert SECRET not in str(error) and SECRET not in repr(error) and SECRET not in str(error.args)
    assert error.__cause__ is None and error.__context__ is None
    assert "ReadError" in str(error)  # the useful part of the diagnostic stays


@pytest.mark.parametrize(
    "credentials", [Credentials("root", SECRET), BearerToken(SECRET)], ids=["password", "bearer"]
)
def test_sync_diagnostics_do_not_repeat_the_credential(credentials: Credentials | BearerToken) -> None:
    config = ConnectionConfig("cam", credentials=credentials)
    with SyncTransport(config, transport=httpx.MockTransport(_leaky)) as transport:
        with pytest.raises(ConnectionFailed) as info:
            transport.send(Request("GET", "/x"))
    _assert_clean(info.value)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "credentials", [Credentials("root", SECRET), BearerToken(SECRET)], ids=["password", "bearer"]
)
async def test_async_diagnostics_do_not_repeat_the_credential(credentials: Credentials | BearerToken) -> None:
    config = ConnectionConfig("cam", credentials=credentials)
    async with AsyncTransport(config, transport=httpx.MockTransport(_leaky)) as transport:
        with pytest.raises(ConnectionFailed) as info:
            await transport.send(Request("GET", "/x"))
    _assert_clean(info.value)


def test_a_rotating_token_provider_is_scrubbed_with_the_value_last_sent() -> None:
    config = ConnectionConfig("cam", credentials=BearerToken(lambda: SECRET))
    with SyncTransport(config, transport=httpx.MockTransport(_leaky)) as transport:
        with pytest.raises(ConnectionFailed) as info:
            transport.send(Request("GET", "/x"))
    _assert_clean(info.value)


def test_secret_named_and_masked_query_values_are_scrubbed_too() -> None:
    def leaky(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadError("bad request line: GET /ws?wssession=WS-TOKEN-1234&other=ZZZ-masked-9999", request=request)

    request = Request("GET", "/ws", query=(("wssession", "WS-TOKEN-1234"), ("other", "ZZZ-masked-9999")), masked=frozenset({"other"}))
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(leaky)) as transport:
        with pytest.raises(ConnectionFailed) as info:
            transport.send(request)
    assert "WS-TOKEN-1234" not in str(info.value) and "ZZZ-masked-9999" not in repr(info.value)


def test_streamed_body_errors_are_scrubbed() -> None:
    class Leaky(httpx.SyncByteStream):
        def __iter__(self):  # type: ignore[no-untyped-def]
            yield b"x"
            raise httpx.ReadError(f"connection lost after {SECRET}")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, stream=Leaky())

    config = ConnectionConfig("cam", credentials=Credentials("root", SECRET))
    with SyncTransport(config, transport=httpx.MockTransport(handler)) as transport:
        with transport.open_stream(Request("GET", "/x", stream=True)) as (_, chunks):
            with pytest.raises(ConnectionFailed) as info:
                list(chunks)
    _assert_clean(info.value)
