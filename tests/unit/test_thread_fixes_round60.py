"""A library error never chains the transport exception: through __cause__ and __context__ no httpx Request, Response,
Headers or URL (with its Authorization header and masked query parameters) is reachable, and no secret is in any
reachable repr. The class name and message of the underlying error stay in the library error's text."""

from __future__ import annotations

import ssl
from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any

import httpx
import pytest

from ax_devil_device_api import AsyncDevice, BearerToken, Device, errors
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS

PASSWORD = "SENTINEL-EXPORT-PASSWORD"
BEARER = "SENTINEL-BEARER-TOKEN"
FORBIDDEN_TYPES = (httpx.Request, httpx.Response, httpx.Headers, httpx.URL)


def _chain(error: BaseException) -> list[BaseException]:
    found: list[BaseException] = []
    pending: list[BaseException] = [error]
    while pending:
        current = pending.pop()
        if any(current is seen for seen in found):
            continue
        found.append(current)
        pending += [link for link in (current.__cause__, current.__context__) if link is not None]
    return found


def _reachable_values(error: BaseException) -> list[Any]:
    values: list[Any] = []
    for link in _chain(error):
        values += [link, *link.args, *vars(link).values()]
    return values


def assert_no_transport_state(error: BaseException) -> None:
    for link in _chain(error):
        assert not link.__class__.__module__.startswith("httpx"), f"{link.__class__.__module__}.{link.__class__.__name__} is chained"
    for value in _reachable_values(error):
        assert not isinstance(value, FORBIDDEN_TYPES), type(value)
    for value in _reachable_values(error):
        for secret in (PASSWORD, BEARER):
            assert secret not in repr(value), (secret, repr(value)[:200])


def _failures() -> dict[str, Callable[[httpx.Request], httpx.Response]]:
    def raising(exception: Callable[[], Exception]) -> Callable[[httpx.Request], httpx.Response]:
        def handler(request: httpx.Request) -> httpx.Response:
            raise exception()

        return handler

    return {
        "read error": raising(lambda: httpx.ReadError("connection reset by peer")),
        "connect timeout": raising(lambda: httpx.ConnectTimeout("timed out")),
        "read timeout": raising(lambda: httpx.ReadTimeout("slow")),
        "tls": raising(lambda: httpx.ConnectError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed")),
        "remote protocol": raising(lambda: httpx.RemoteProtocolError("server disconnected")),
    }


FAILURES = list(_failures())
CREDENTIALS: dict[str, Any] = {"password": ("root", "pw"), "bearer": BearerToken(BEARER)}


def _export(dev: Any) -> Any:
    return dev.apis.export_recording.export_recording("rec", "disk", "matroska", password=PASSWORD, encryption_format="zip-aes256")


@pytest.mark.parametrize("credentials", list(CREDENTIALS))
@pytest.mark.parametrize("failure", FAILURES)
def test_sync_a_streamed_call_failing_in_transport_chains_no_httpx_object(failure: str, credentials: str) -> None:
    with Device("cam", credentials=CREDENTIALS[credentials], transport=httpx.MockTransport(_failures()[failure])) as dev:
        with pytest.raises(errors.TransportError) as caught:
            with _export(dev) as stream:
                list(stream)
    assert_no_transport_state(caught.value)
    assert type(caught.value).__name__ in str(type(caught.value).__mro__) and str(caught.value)


@pytest.mark.anyio
@pytest.mark.parametrize("credentials", list(CREDENTIALS))
@pytest.mark.parametrize("failure", FAILURES)
async def test_async_a_streamed_call_failing_in_transport_chains_no_httpx_object(failure: str, credentials: str) -> None:
    async with AsyncDevice("cam", credentials=CREDENTIALS[credentials], transport=httpx.MockTransport(_failures()[failure])) as dev:
        with pytest.raises(errors.TransportError) as caught:
            async with await _export(dev) as stream:
                [chunk async for chunk in stream]
    assert_no_transport_state(caught.value)


@pytest.mark.parametrize("failure", FAILURES)
def test_sync_and_async_plain_calls_chain_no_httpx_object(failure: str) -> None:
    with Device("cam", credentials=("root", "pw"), transport=httpx.MockTransport(_failures()[failure])) as dev:
        with pytest.raises(errors.TransportError) as caught:
            dev.apis.export_recording.get_capabilities()
    assert_no_transport_state(caught.value)


@pytest.mark.anyio
@pytest.mark.parametrize("failure", FAILURES)
async def test_async_plain_calls_chain_no_httpx_object(failure: str) -> None:
    async with AsyncDevice("cam", credentials=("root", "pw"), transport=httpx.MockTransport(_failures()[failure])) as dev:
        with pytest.raises(errors.TransportError) as caught:
            await dev.apis.export_recording.get_capabilities()
    assert_no_transport_state(caught.value)


class _BrokenBody(httpx.SyncByteStream):
    def __iter__(self) -> Iterator[bytes]:
        yield b"partial"
        raise httpx.ReadError("connection lost mid-body")


class _AsyncBrokenBody(httpx.AsyncByteStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"partial"
        raise httpx.ReadError("connection lost mid-body")


def _mid_body(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, headers={"content-type": "video/x-matroska"}, stream=_BrokenBody())


def _async_mid_body(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, headers={"content-type": "video/x-matroska"}, stream=_AsyncBrokenBody())


def test_sync_a_body_failing_while_streaming_chains_no_httpx_object() -> None:
    with Device("cam", credentials=("root", "pw"), transport=httpx.MockTransport(_mid_body)) as dev:
        with pytest.raises(errors.TransportError) as caught:
            with _export(dev) as stream:
                list(stream)
    assert_no_transport_state(caught.value)
    assert "ReadError" in str(caught.value) and "connection lost mid-body" in str(caught.value)


@pytest.mark.anyio
async def test_async_a_body_failing_while_streaming_chains_no_httpx_object() -> None:
    async with AsyncDevice("cam", credentials=("root", "pw"), transport=httpx.MockTransport(_async_mid_body)) as dev:
        with pytest.raises(errors.TransportError) as caught:
            async with await _export(dev) as stream:
                [chunk async for chunk in stream]
    assert_no_transport_state(caught.value)


def test_the_underlying_class_name_and_message_stay_in_the_text() -> None:
    handler = _failures()["tls"]
    with Device("cam", credentials=("root", "pw"), transport=httpx.MockTransport(handler)) as dev:
        with pytest.raises(errors.TlsError) as caught:
            dev.apis.export_recording.get_capabilities()
    assert "ConnectError" in str(caught.value) and "CERTIFICATE_VERIFY_FAILED" in str(caught.value)
    assert ssl is not None


def test_sync_a_websocket_handshake_failure_chains_no_httpx_object() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadError("handshake reset")

    with Device("cam", credentials=BearerToken(BEARER), transport=httpx.MockTransport(handler)) as dev:
        with pytest.raises(errors.TransportError) as caught:
            with dev.connect_session(EVENTS, heartbeat=Heartbeat(None)):
                pass
    assert_no_transport_state(caught.value)
    assert "ReadError" in str(caught.value)


@pytest.mark.anyio
async def test_async_a_websocket_handshake_failure_chains_no_httpx_object() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("handshake timed out")

    async with AsyncDevice("cam", credentials=BearerToken(BEARER), transport=httpx.MockTransport(handler)) as dev:
        with pytest.raises(errors.TransportError) as caught:
            async with dev.connect_session(EVENTS, heartbeat=Heartbeat(None), use_token=True):
                pass
    assert_no_transport_state(caught.value)
