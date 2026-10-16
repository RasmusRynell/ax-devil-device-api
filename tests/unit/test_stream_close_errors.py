"""A transport error raised while closing a stream is mapped when closing is the primary operation, and never replaces the
error that caused the teardown."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Iterator

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import Request
from ax_devil_device_api._runtime.driver import Call, run_async, run_sync
from ax_devil_device_api.errors import ConnectionFailed

SECRET = "close-secret-123"


class BadCloseStream(httpx.SyncByteStream):
    def __iter__(self) -> Iterator[bytes]:
        yield b"one"
        yield b"two"

    def close(self) -> None:
        raise httpx.ReadError(f"connection reset while closing {SECRET}")


class ABadCloseStream(httpx.AsyncByteStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"one"
        yield b"two"

    async def aclose(self) -> None:
        raise httpx.ReadError(f"connection reset while closing {SECRET}")


def _sync_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, stream=BadCloseStream())


def _async_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, stream=ABadCloseStream())


class Exploding:
    """A decoder whose failure is the error that causes the teardown."""

    def feed(self, chunk: bytes) -> list[bytes]:
        raise RuntimeError("decoder boom")

    def close(self) -> list[bytes]:
        return []


def _flow(decoder: object):  # type: ignore[no-untyped-def]
    yield Request("GET", "/x", stream=True)
    return decoder


class Passthrough:
    def feed(self, chunk: bytes) -> list[bytes]:
        return [chunk]

    def close(self) -> list[bytes]:
        return []


def test_sync_close_failure_is_mapped_when_closing_is_the_primary_operation() -> None:
    config = ConnectionConfig("cam")
    with SyncTransport(config, transport=httpx.MockTransport(_sync_handler)) as transport:
        result = run_sync(transport, _flow(Passthrough()), Call(label=("a", "b")))
        with pytest.raises(ConnectionFailed) as info:
            result.close()  # the caller closes without having read: the close is the operation
    assert info.value.__cause__ is None and info.value.__context__ is None
    assert "ReadError" in str(info.value)


def test_sync_close_failure_does_not_replace_the_decoder_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG, logger="ax_devil_device_api")
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_sync_handler)) as transport:
        result = run_sync(transport, _flow(Exploding()), Call(label=("a", "b")))
        with pytest.raises(RuntimeError, match="decoder boom"):
            for _ in result:
                pass
    assert any("closing the" in r.getMessage() and "failed while another error" in r.getMessage() for r in caplog.records)


def test_sync_close_failure_does_not_replace_an_exception_in_the_with_block() -> None:
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_sync_handler)) as transport:
        with pytest.raises(ValueError, match="body error"):
            with run_sync(transport, _flow(Passthrough()), Call(label=("a", "b"))):
                raise ValueError("body error")


@pytest.mark.anyio
async def test_async_close_failure_is_mapped_when_closing_is_the_primary_operation() -> None:
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_async_handler)) as transport:
        result = await run_async(transport, _flow(Passthrough()), Call(label=("a", "b")))
        with pytest.raises(ConnectionFailed) as info:
            await result.aclose()
    assert info.value.__cause__ is None and info.value.__context__ is None


@pytest.mark.anyio
async def test_async_close_failure_does_not_replace_the_decoder_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG, logger="ax_devil_device_api")
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_async_handler)) as transport:
        result = await run_async(transport, _flow(Exploding()), Call(label=("a", "b")))
        with pytest.raises(RuntimeError, match="decoder boom"):
            async for _ in result:
                pass
    assert any("closing the" in r.getMessage() and "failed while another error" in r.getMessage() for r in caplog.records)


@pytest.mark.anyio
async def test_async_close_failure_does_not_replace_an_exception_in_the_with_block() -> None:
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_async_handler)) as transport:
        with pytest.raises(ValueError, match="body error"):
            async with await run_async(transport, _flow(Passthrough()), Call(label=("a", "b"))):
                raise ValueError("body error")
