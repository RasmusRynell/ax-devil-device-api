"""Run sans-IO call flows over a sync or async transport.

These two drivers are the only code that connects protocol flows to I/O.
Everything they do is mechanical: send what the flow yields, hand back what
the transport returns, and wrap streamed bodies in a managed result.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import AsyncExitStack, ExitStack
from dataclasses import dataclass, replace
from typing import Any, Generic, Protocol, TypeVar

from .._http.config import ResponseHook
from .._http.options import RetryPolicy
from .._http.types import Request, Response
from .._protocols.base import CallFlow, Operation, StreamDecoder
from ..errors import ConnectionFailed, ReadTimeout, TransportError

logger = logging.getLogger("ax_devil_device_api")

T = TypeVar("T")


class SyncTransportLike(Protocol):
    def send(self, request: Request) -> Response: ...

    def open_stream(self, request: Request) -> Any:
        """Context manager yielding ``(Response, Iterator[bytes])``.

        For a non-2xx status the response carries the full body and the
        iterator is empty.
        """
        ...


class AsyncTransportLike(Protocol):
    async def send(self, request: Request) -> Response: ...

    def open_stream(self, request: Request) -> Any:
        """Async context manager yielding ``(Response, AsyncIterator[bytes])``."""
        ...


class StreamResult(Generic[T]):
    """A streamed response body; iterate it inside ``with``.

    Leaving the ``with`` block (or calling ``close``) releases the connection,
    whether or not the body was fully read.
    """

    def __init__(self, response: Response, chunks: Iterator[bytes], decoder: StreamDecoder[T], stack: ExitStack) -> None:
        self.response = response
        self._chunks = chunks
        self._decoder = decoder
        self._stack = stack
        self._closed = False

    def __enter__(self) -> StreamResult[T]:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def __iter__(self) -> Iterator[T]:
        try:
            for chunk in self._chunks:
                yield from self._decoder.feed(chunk)
            yield from self._decoder.close()
        finally:
            self.close()

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self._stack.close()


class AsyncStreamResult(Generic[T]):
    """Async counterpart of ``StreamResult``; use ``async with`` and ``async for``."""

    def __init__(
        self, response: Response, chunks: AsyncIterator[bytes], decoder: StreamDecoder[T], stack: AsyncExitStack
    ) -> None:
        self.response = response
        self._chunks = chunks
        self._decoder = decoder
        self._stack = stack
        self._closed = False

    async def __aenter__(self) -> AsyncStreamResult[T]:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def __aiter__(self) -> AsyncIterator[T]:
        try:
            async for chunk in self._chunks:
                for item in self._decoder.feed(chunk):
                    yield item
            for item in self._decoder.close():
                yield item
        finally:
            await self.aclose()

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            await self._stack.aclose()


@dataclass(frozen=True)
class Call:
    """Per-call settings the driver applies to every request of a flow."""

    op: Operation[Any] | None = None
    label: tuple[str, str] | None = None
    """(api, operation) for logging when there is no ``op`` (internal probes)."""
    timeout: float | None = None
    retry: RetryPolicy = RetryPolicy()
    on_response: ResponseHook | None = None

    def prepare(self, request: Request) -> Request:
        return replace(request, timeout=self.timeout) if self.timeout is not None else request

    def should_retry(self, request: Request, error: TransportError, attempt: int) -> bool:
        policy = self.retry
        if attempt >= policy.attempts or not request.replayable:
            # A streamed body may be partly consumed even if nothing reached the device.
            return False
        if not error.request_sent:
            return policy.retry_unsent
        effect = self.op.effect if self.op is not None else "unknown"
        return (
            policy.retry_reads
            and effect == "read"
            and not request.stream
            and isinstance(error, (ReadTimeout, ConnectionFailed))
        )

    def observe(self, request: Request, response: Response | None, error: Exception | None, started: float, attempt: int) -> None:
        duration_ms = round((time.monotonic() - started) * 1000, 1)
        if self.op is not None:
            api, operation = self.op.api.id, self.op.id
        else:
            api, operation = self.label or (None, None)
        status = response.status if response is not None else None
        if logger.isEnabledFor(logging.DEBUG):
            outcome = status if error is None else type(error).__name__
            logger.debug(
                "%s %s -> %s in %.1f ms (attempt %d, %s.%s)",
                request.method, request.path, outcome, duration_ms, attempt, api, operation,
            )
        if self.on_response is not None:
            self.on_response(
                {
                    "api": api,
                    "operation": operation,
                    "method": request.method,
                    "path": request.path,
                    "status": status,
                    "error": type(error).__name__ if error is not None else None,
                    "duration_ms": duration_ms,
                    "attempt": attempt,
                }
            )


DEFAULT_CALL = Call()


def _send_sync(transport: SyncTransportLike, request: Request, call: Call) -> Response:
    attempt = 1
    while True:
        started = time.monotonic()
        try:
            response = transport.send(request)
        except TransportError as error:
            call.observe(request, None, error, started, attempt)
            if not call.should_retry(request, error, attempt):
                raise
            time.sleep(call.retry.delay(attempt))
            attempt += 1
            continue
        call.observe(request, response, None, started, attempt)
        return response


async def _send_async(transport: AsyncTransportLike, request: Request, call: Call) -> Response:
    attempt = 1
    while True:
        started = time.monotonic()
        try:
            response = await transport.send(request)
        except TransportError as error:
            call.observe(request, None, error, started, attempt)
            if not call.should_retry(request, error, attempt):
                raise
            await asyncio.sleep(call.retry.delay(attempt))
            attempt += 1
            continue
        call.observe(request, response, None, started, attempt)
        return response


def run_sync(transport: SyncTransportLike, flow: CallFlow[Any], call: Call = DEFAULT_CALL) -> Any:
    """Drive ``flow`` to completion with blocking I/O."""
    try:
        request = next(flow)
    except StopIteration as done:
        return done.value
    while True:
        request = call.prepare(request)
        if request.stream:
            return _finish_stream_sync(transport, flow, request, call)
        response = _send_sync(transport, request, call)
        try:
            request = flow.send(response)
        except StopIteration as done:
            return done.value


def _finish_stream_sync(transport: SyncTransportLike, flow: CallFlow[Any], request: Request, call: Call) -> Any:
    stack = ExitStack()
    started = time.monotonic()
    try:
        response, chunks = stack.enter_context(transport.open_stream(request))
        call.observe(request, response, None, started, 1)
        try:
            flow.send(response)
        except StopIteration as done:
            decoder = done.value
        else:
            raise RuntimeError("A flow must not yield after a stream request")
        if decoder is None:
            stack.close()
            return None
        return StreamResult(response, iter(chunks), decoder, stack)
    except BaseException:
        stack.close()
        raise


async def run_async(transport: AsyncTransportLike, flow: CallFlow[Any], call: Call = DEFAULT_CALL) -> Any:
    """Drive ``flow`` to completion with async I/O."""
    try:
        request = next(flow)
    except StopIteration as done:
        return done.value
    while True:
        request = call.prepare(request)
        if request.stream:
            return await _finish_stream_async(transport, flow, request, call)
        response = await _send_async(transport, request, call)
        try:
            request = flow.send(response)
        except StopIteration as done:
            return done.value


async def _finish_stream_async(transport: AsyncTransportLike, flow: CallFlow[Any], request: Request, call: Call) -> Any:
    stack = AsyncExitStack()
    started = time.monotonic()
    try:
        response, chunks = await stack.enter_async_context(transport.open_stream(request))
        call.observe(request, response, None, started, 1)
        try:
            flow.send(response)
        except StopIteration as done:
            decoder = done.value
        else:
            raise RuntimeError("A flow must not yield after a stream request")
        if decoder is None:
            await stack.aclose()
            return None
        return AsyncStreamResult(response, chunks, decoder, stack)
    except BaseException:
        await stack.aclose()
        raise
