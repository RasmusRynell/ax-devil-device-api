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
from .._http.debug import public_response, redact_path
from .._http.options import RetryPolicy
from .._http.types import Request, Response, has_deferred, release_deferred, resolve_deferred
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
        self.response = public_response(response) if isinstance(response, Response) else response  # the original request stays internal: it holds masked values
        self._chunks = chunks
        self._decoder = decoder
        self._stack = stack
        self._closed = False
        self._items: Iterator[T] | None = None

    def __enter__(self) -> StreamResult[T]:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def __iter__(self) -> StreamResult[T]:
        return self  # one iterator per result: `next(stream)` followed by more iteration continues, it does not restart

    def __next__(self) -> T:
        if self._closed:
            raise StopIteration  # exhausted, or closed by the caller
        if self._items is None:
            self._items = self._generate()
        return next(self._items)

    def _generate(self) -> Iterator[T]:
        try:
            for chunk in self._chunks:
                yield from self._decoder.feed(chunk)
            yield from self._decoder.close()
        finally:
            self.close()  # on exhaustion or an error; an abandoned iteration is released by close() / leaving ``with``

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self._stack.close()


class AsyncStreamResult(Generic[T]):
    """Async counterpart of ``StreamResult``; use ``async with`` and ``async for``."""

    def __init__(
        self, response: Response, chunks: AsyncIterator[bytes], decoder: StreamDecoder[T], stack: AsyncExitStack
    ) -> None:
        self.response = public_response(response) if isinstance(response, Response) else response  # the original request stays internal: it holds masked values
        self._chunks = chunks
        self._decoder = decoder
        self._stack = stack
        self._closed = False
        self._teardown: asyncio.Future[None] | None = None
        self._items: AsyncIterator[T] | None = None

    async def __aenter__(self) -> AsyncStreamResult[T]:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    def __aiter__(self) -> AsyncStreamResult[T]:
        return self  # one iterator per result (see StreamResult)

    async def __anext__(self) -> T:
        if self._closed:
            raise StopAsyncIteration
        if self._items is None:
            self._items = self._generate()
        return await self._items.__anext__()

    async def _generate(self) -> AsyncIterator[T]:
        try:
            async for chunk in self._chunks:
                for item in self._decoder.feed(chunk):
                    yield item
            for item in self._decoder.close():
                yield item
        finally:
            await self.aclose()

    async def aclose(self) -> None:
        if self._closed:
            return
        # The teardown is a task of its own: cancelling the caller (even with a direct ``Task.cancel()``, which an
        # AnyIO shield does not stop) cannot interrupt it half way. A second aclose() awaits the same task. The
        # result is marked closed only after the teardown finished; the cancellation is re-raised after that.
        if self._teardown is None:
            self._teardown = asyncio.ensure_future(self._stack.aclose())
        task = self._teardown
        cancelled: asyncio.CancelledError | None = None
        while not task.done():
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError as error:
                if not task.cancelled():
                    cancelled = error  # the caller was cancelled (again): keep waiting for the teardown
        self._closed = True
        if not task.cancelled():
            task.result()
        if cancelled is not None:
            raise cancelled


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
        """Apply the call timeout and read deferred upload content (blocking)."""
        return resolve_deferred(self._timed(request))

    async def aprepare(self, request: Request) -> Request:
        """``prepare`` for async calls: deferred upload content is read in a worker thread."""
        request = self._timed(request)
        return await asyncio.to_thread(resolve_deferred, request) if has_deferred(request) else request

    def _timed(self, request: Request) -> Request:
        if self.timeout is not None:
            request = replace(request, timeout=self.timeout)
        params = self.op.params if self.op is not None else None
        if params is not None and not request.masked:
            masked = params.masked_wire_names()
            if masked:
                request = replace(request, masked=masked)
        return request

    def should_retry(self, request: Request, error: TransportError, attempt: int) -> bool:
        policy = self.retry
        # A failed credentials preflight is its own replayable read-only GET; the one-shot body behind it was
        # never touched, so it is judged as such, not by the outer request.
        preflight = error.during_preflight
        if attempt < policy.attempts and error.body_untouched and not error.request_sent:
            return policy.retry_unsent  # nothing was built or sent yet, whatever the body is
        if attempt >= policy.attempts or not (request.replayable or preflight):
            # A streamed body may be partly consumed even if nothing reached the device.
            return False
        if not error.request_sent:
            return policy.retry_unsent
        effect = "read" if preflight else (self.op.effect if self.op is not None else "unknown")
        return (
            policy.retry_reads
            and effect == "read"
            and (preflight or not request.stream)
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
                request.method, redact_path(request.path, request.masked), outcome, duration_ms, attempt, api, operation,
            )
        if self.on_response is not None:
            self.on_response(
                {
                    "api": api,
                    "operation": operation,
                    "method": request.method,
                    "path": redact_path(request.path, request.masked),
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
        except Exception as error:
            # Not a transport failure (e.g. AuthError from the credentials check): never retried,
            # but the attempt still gets its record.
            call.observe(request, None, error, started, attempt)
            raise
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
        except Exception as error:
            call.observe(request, None, error, started, attempt)
            raise
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
        try:
            if request.stream:
                return _finish_stream_sync(transport, flow, request, call)
            response = _send_sync(transport, request, call)
        finally:
            release_deferred(request)  # a one-shot upload source leased for this call but never read is free again
        try:
            request = flow.send(response)
        except StopIteration as done:
            return done.value


def _finish_stream_sync(transport: SyncTransportLike, flow: CallFlow[Any], request: Request, call: Call) -> Any:
    stack = ExitStack()
    try:
        attempt = 1
        while True:
            started = time.monotonic()
            try:
                response, chunks = stack.enter_context(transport.open_stream(request))
            except TransportError as error:
                # Opening failed before a response: same retry rules as any request.
                call.observe(request, None, error, started, attempt)
                if not call.should_retry(request, error, attempt):
                    raise
                time.sleep(call.retry.delay(attempt))
                attempt += 1
                continue
            except Exception as error:
                call.observe(request, None, error, started, attempt)
                raise
            break
        call.observe(request, response, None, started, attempt)
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
        request = await call.aprepare(request)
        try:
            if request.stream:
                return await _finish_stream_async(transport, flow, request, call)
            response = await _send_async(transport, request, call)
        finally:
            release_deferred(request)
        try:
            request = flow.send(response)
        except StopIteration as done:
            return done.value


async def _finish_stream_async(transport: AsyncTransportLike, flow: CallFlow[Any], request: Request, call: Call) -> Any:
    stack = AsyncExitStack()
    try:
        attempt = 1
        while True:
            started = time.monotonic()
            try:
                response, chunks = await stack.enter_async_context(transport.open_stream(request))
            except TransportError as error:
                call.observe(request, None, error, started, attempt)
                if not call.should_retry(request, error, attempt):
                    raise
                await asyncio.sleep(call.retry.delay(attempt))
                attempt += 1
                continue
            except Exception as error:
                call.observe(request, None, error, started, attempt)
                raise
            break
        call.observe(request, response, None, started, attempt)
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
