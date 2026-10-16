"""Sync and async drivers: run hand-written flows over fake transports.

No HTTP here. The fake transports record what was sent and when streams are
closed, so the tests check the driver's own contract.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import pytest

from ax_devil_device_api._http.options import RetryPolicy
from ax_devil_device_api._http.types import Headers, Request, Response
from ax_devil_device_api._protocols.base import BytesDecoder, CallFlow
from ax_devil_device_api._runtime.driver import AsyncStreamResult, Call, StreamResult, run_async, run_sync
from ax_devil_device_api.errors import ConnectionFailed, HttpError


def make_response(request: Request, status: int = 200, content: bytes = b"") -> Response:
    return Response(status, Headers(()), content, request)


class FakeTransport:
    """Sync transport double. Answers ``send`` in order and tracks stream closes."""

    def __init__(self, *, send_contents: list[bytes] | None = None, status: int = 200, chunks: list[bytes] | None = None) -> None:
        self._send_contents = list(send_contents or [])
        self.status = status
        self.chunks = list(chunks or [])
        self.sent: list[Request] = []
        self.opened: list[Request] = []
        self.closed: list[str] = []

    def send(self, request: Request) -> Response:
        self.sent.append(request)
        return make_response(request, content=self._send_contents.pop(0))

    @contextmanager
    def open_stream(self, request: Request) -> Iterator[tuple[Response, Iterator[bytes]]]:
        self.opened.append(request)
        try:
            if 200 <= self.status < 300:
                yield make_response(request, self.status), iter(self.chunks)
            else:
                yield make_response(request, self.status, b"".join(self.chunks)), iter(())
        finally:
            self.closed.append(request.path)


class FakeAsyncTransport:
    """Async transport double with the same contract as ``FakeTransport``."""

    def __init__(self, *, send_contents: list[bytes] | None = None, status: int = 200, chunks: list[bytes] | None = None) -> None:
        self._send_contents = list(send_contents or [])
        self.status = status
        self.chunks = list(chunks or [])
        self.sent: list[Request] = []
        self.opened: list[Request] = []
        self.closed: list[str] = []

    async def send(self, request: Request) -> Response:
        self.sent.append(request)
        return make_response(request, content=self._send_contents.pop(0))

    @asynccontextmanager
    async def open_stream(self, request: Request) -> AsyncIterator[tuple[Response, AsyncIterator[bytes]]]:
        self.opened.append(request)
        try:
            if 200 <= self.status < 300:
                yield make_response(request, self.status), _achunks(self.chunks)
            else:
                yield make_response(request, self.status, b"".join(self.chunks)), _achunks([])
        finally:
            self.closed.append(request.path)


async def _achunks(chunks: list[bytes]) -> AsyncIterator[bytes]:
    for chunk in chunks:
        yield chunk


# ---------------------------------------------------------------------------
# Hand-written flows (shared by sync and async tests)


def two_requests() -> CallFlow[tuple[bytes, bytes]]:
    first = yield Request("GET", "/a")
    second = yield Request("POST", "/b")
    return first.content, second.content


def no_io() -> CallFlow[str]:
    return "value"
    yield  # pragma: no cover - makes this a generator


def stream_flow() -> CallFlow[BytesDecoder]:
    yield Request("GET", "/stream", stream=True)
    return BytesDecoder()


def stream_then_raise() -> CallFlow[BytesDecoder]:
    yield Request("GET", "/stream", stream=True)
    raise RuntimeError("boom after stream open")


def stream_flow_checks_status() -> CallFlow[BytesDecoder]:
    response = yield Request("GET", "/stream", stream=True)
    if response.status != 200:
        raise HttpError(response.status, response.content.decode(), api="test", operation="stream")
    return BytesDecoder()


def stream_then_more_requests() -> CallFlow[BytesDecoder]:
    yield Request("GET", "/stream", stream=True)
    yield Request("GET", "/after")  # not allowed after a stream request
    return BytesDecoder()


# ---------------------------------------------------------------------------
# Sync driver


def test_multi_yield_flow_receives_responses_in_order() -> None:
    transport = FakeTransport(send_contents=[b"first", b"second"])

    result = run_sync(transport, two_requests())

    assert result == (b"first", b"second")
    assert [(r.method, r.path) for r in transport.sent] == [("GET", "/a"), ("POST", "/b")]


def test_flow_returning_without_yielding_returns_its_value() -> None:
    transport = FakeTransport()

    assert run_sync(transport, no_io()) == "value"
    assert transport.sent == []


def test_sync_stream_result_iterates_chunks() -> None:
    transport = FakeTransport(chunks=[b"ab", b"", b"cd"])

    result = run_sync(transport, stream_flow())

    assert isinstance(result, StreamResult)
    assert result.response.status == 200
    with result:
        assert list(result) == [b"ab", b"cd"]


def test_sync_stream_closed_on_leaving_with_block() -> None:
    transport = FakeTransport(chunks=[b"ab"])

    with run_sync(transport, stream_flow()) as result:
        assert transport.closed == []
        assert result.response.status == 200

    assert transport.closed == ["/stream"]


def test_sync_stream_closed_when_iteration_finishes() -> None:
    transport = FakeTransport(chunks=[b"ab"])

    with run_sync(transport, stream_flow()) as result:
        list(result)
        assert transport.closed == ["/stream"]


def test_sync_exception_after_stream_open_closes_stream() -> None:
    transport = FakeTransport(chunks=[b"ab"])

    with pytest.raises(RuntimeError, match="boom after stream open"):
        run_sync(transport, stream_then_raise())

    assert transport.opened[0].path == "/stream"
    assert transport.closed == ["/stream"]


def test_sync_non_2xx_stream_gives_full_content_to_flow_and_closes() -> None:
    transport = FakeTransport(status=503, chunks=[b"busy", b" later"])

    with pytest.raises(HttpError) as caught:
        run_sync(transport, stream_flow_checks_status())

    assert caught.value.status == 503
    assert caught.value.body_excerpt == "busy later"
    assert transport.closed == ["/stream"]


def test_sync_yield_after_stream_request_is_runtime_error_and_closes() -> None:
    transport = FakeTransport(chunks=[b"ab"])

    with pytest.raises(RuntimeError, match="must not yield after a stream request"):
        run_sync(transport, stream_then_more_requests())

    assert transport.closed == ["/stream"]
    assert transport.sent == []


# ---------------------------------------------------------------------------
# Async driver


@pytest.mark.anyio
async def test_async_multi_yield_flow_receives_responses_in_order() -> None:
    transport = FakeAsyncTransport(send_contents=[b"first", b"second"])

    result = await run_async(transport, two_requests())

    assert result == (b"first", b"second")
    assert [(r.method, r.path) for r in transport.sent] == [("GET", "/a"), ("POST", "/b")]


@pytest.mark.anyio
async def test_async_flow_returning_without_yielding_returns_its_value() -> None:
    transport = FakeAsyncTransport()

    assert await run_async(transport, no_io()) == "value"
    assert transport.sent == []


@pytest.mark.anyio
async def test_async_stream_result_iterates_chunks() -> None:
    transport = FakeAsyncTransport(chunks=[b"ab", b"", b"cd"])

    result: Any = await run_async(transport, stream_flow())

    assert isinstance(result, AsyncStreamResult)
    assert result.response.status == 200
    async with result:
        assert [chunk async for chunk in result] == [b"ab", b"cd"]


@pytest.mark.anyio
async def test_async_stream_closed_on_leaving_async_with_block() -> None:
    transport = FakeAsyncTransport(chunks=[b"ab"])

    async with await run_async(transport, stream_flow()) as result:
        assert transport.closed == []
        assert result.response.status == 200

    assert transport.closed == ["/stream"]


@pytest.mark.anyio
async def test_async_exception_after_stream_open_closes_stream() -> None:
    transport = FakeAsyncTransport(chunks=[b"ab"])

    with pytest.raises(RuntimeError, match="boom after stream open"):
        await run_async(transport, stream_then_raise())

    assert transport.closed == ["/stream"]


@pytest.mark.anyio
async def test_async_non_2xx_stream_gives_full_content_to_flow_and_closes() -> None:
    transport = FakeAsyncTransport(status=503, chunks=[b"busy", b" later"])

    with pytest.raises(HttpError) as caught:
        await run_async(transport, stream_flow_checks_status())

    assert caught.value.status == 503
    assert caught.value.body_excerpt == "busy later"
    assert transport.closed == ["/stream"]


@pytest.mark.anyio
async def test_async_yield_after_stream_request_is_runtime_error_and_closes() -> None:
    transport = FakeAsyncTransport(chunks=[b"ab"])

    with pytest.raises(RuntimeError, match="must not yield after a stream request"):
        await run_async(transport, stream_then_more_requests())

    assert transport.closed == ["/stream"]
    assert transport.sent == []


# ---------------------------------------------------------------------------
# Call: per-call timeout, retry, and response hook


class FlakyTransport(FakeTransport):
    """Fails the first ``failures`` sends with an unsent transport error."""

    def __init__(self, failures: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.failures = failures

    def send(self, request: Request) -> Response:
        if self.failures:
            self.failures -= 1
            self.sent.append(request)
            raise ConnectionFailed("refused", request_sent=False)
        return super().send(request)


def test_call_timeout_is_applied_to_every_request() -> None:
    transport = FakeTransport(send_contents=[b"a", b"b"])

    run_sync(transport, two_requests(), Call(timeout=3.5))

    assert [r.timeout for r in transport.sent] == [3.5, 3.5]


def test_default_call_leaves_request_timeout_alone() -> None:
    transport = FakeTransport(send_contents=[b"a", b"b"])

    run_sync(transport, two_requests())

    assert [r.timeout for r in transport.sent] == [None, None]


def test_call_retries_unsent_failure_and_reports_each_attempt() -> None:
    transport = FlakyTransport(1, send_contents=[b"first", b"second"])
    events: list[dict[str, Any]] = []

    result = run_sync(transport, two_requests(), Call(retry=RetryPolicy(backoff=0), on_response=events.append))

    assert result == (b"first", b"second")
    assert [(e["attempt"], e["status"], e["error"]) for e in events] == [
        (1, None, "ConnectionFailed"),
        (2, 200, None),
        (1, 200, None),
    ]


def test_call_without_retry_budget_raises_transport_error() -> None:
    transport = FlakyTransport(5, send_contents=[b"x", b"y"])

    with pytest.raises(ConnectionFailed):
        run_sync(transport, two_requests(), Call(retry=RetryPolicy(attempts=2, backoff=0)))

    assert len(transport.sent) == 2


@pytest.mark.anyio
async def test_async_call_timeout_and_retry() -> None:
    transport = FakeAsyncTransport(send_contents=[b"a", b"b"])
    await run_async(transport, two_requests(), Call(timeout=1.5))
    assert [r.timeout for r in transport.sent] == [1.5, 1.5]

    class Flaky(FakeAsyncTransport):
        failed = False

        async def send(self, request: Request) -> Response:
            if not self.failed:
                self.failed = True
                raise ConnectionFailed("refused", request_sent=False)
            return await super().send(request)

    flaky = Flaky(send_contents=[b"a", b"b"])
    assert await run_async(flaky, two_requests(), Call(retry=RetryPolicy(backoff=0))) == (b"a", b"b")
