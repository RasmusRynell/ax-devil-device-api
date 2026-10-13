"""Review fixes for the HTTP layer and driver: bearer if_challenged, config validation,
slot waits bound by the timeout, off-loop upload reads, and stream-open retries."""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import httpx
import pytest

from ax_devil_device_api._http.config import BearerToken, ConnectionConfig
from ax_devil_device_api._http.options import RetryPolicy
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import Headers, RawBody, Request, Response
from ax_devil_device_api._protocols.base import BytesDecoder, CallFlow
from ax_devil_device_api._runtime.driver import Call, run_async, run_sync
from ax_devil_device_api.errors import ConfigurationError, ConnectTimeout, PoolTimeout, ReadTimeout

# -- Thread 1: bearer + if_challenged ------------------------------------------


def _bearer_cfg() -> ConnectionConfig:
    return ConnectionConfig("cam", credentials=BearerToken("tok"))


def test_bearer_if_challenged_is_anonymous_first_and_succeeds_without_token() -> None:
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("authorization"))
        return httpx.Response(200)

    with SyncTransport(_bearer_cfg(), transport=httpx.MockTransport(handler)) as t:
        assert t.send(Request("GET", "/x", auth="if_challenged")).status == 200
    assert seen == [None]


def test_bearer_if_challenged_sends_token_after_a_challenge() -> None:
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("authorization")
        seen.append(auth)
        if auth is None:
            return httpx.Response(401, headers={"WWW-Authenticate": "Bearer realm=x"})
        return httpx.Response(200)

    with SyncTransport(_bearer_cfg(), transport=httpx.MockTransport(handler)) as t:
        assert t.send(Request("GET", "/x", auth="if_challenged")).status == 200
    assert seen == [None, "Bearer tok"]


def test_bearer_required_stays_preemptive() -> None:
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("authorization"))
        return httpx.Response(200)

    with SyncTransport(_bearer_cfg(), transport=httpx.MockTransport(handler)) as t:
        t.send(Request("GET", "/x"))
    assert seen == ["Bearer tok"]


# -- Threads 2, 3, 7: configuration validation ---------------------------------


def test_proxy_password_is_not_in_the_config_repr() -> None:
    config = ConnectionConfig("cam", proxy="https://user:hunter2@proxy.example:3128")
    text = repr(config)
    assert "hunter2" not in text and "user:" not in text
    assert "proxy.example:3128" in text
    assert config.proxy == "https://user:hunter2@proxy.example:3128"


def test_config_repr_without_proxy_userinfo_is_unchanged() -> None:
    assert "proxy='http://p:3128'" in repr(ConnectionConfig("cam", proxy="http://p:3128", allow_http=True))
    assert "proxy=None" in repr(ConnectionConfig("cam"))


@pytest.mark.parametrize("base_path", ["/camera#admin", "/camera?x=1", "camera", "/camera/"])
def test_invalid_base_path_is_rejected(base_path: str) -> None:
    with pytest.raises(ConfigurationError):
        ConnectionConfig("cam", base_path=base_path)


@pytest.mark.parametrize("kwargs", [{"backoff": -1}, {"max_backoff": -0.5}, {"backoff": float("nan")}])
def test_negative_retry_delays_are_rejected(kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        RetryPolicy(attempts=2, **kwargs)


def test_zero_backoff_is_allowed() -> None:
    assert RetryPolicy(backoff=0, max_backoff=0).delay(3) == 0


# -- Thread 10: slot waits are bounded by the request timeout ------------------


def test_sync_slot_wait_times_out_with_pool_timeout() -> None:
    release = threading.Event()
    entered = threading.Event()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/slow":
            entered.set()
            release.wait(5)
        return httpx.Response(200)

    config = ConnectionConfig("cam", max_concurrency=1)
    with SyncTransport(config, transport=httpx.MockTransport(handler)) as t:
        worker = threading.Thread(target=lambda: t.send(Request("GET", "/slow")))
        worker.start()
        assert entered.wait(2)
        started = time.monotonic()
        with pytest.raises(PoolTimeout) as info:
            t.send(Request("GET", "/fast", timeout=0.2))
        assert time.monotonic() - started < 2
        assert info.value.request_sent is False
        release.set()
        worker.join()
        assert t.send(Request("GET", "/after")).status == 200  # slot was not leaked


@pytest.mark.anyio
async def test_async_slot_wait_times_out_with_pool_timeout() -> None:
    release = asyncio.Event()

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/slow":
            await release.wait()
        return httpx.Response(200)

    config = ConnectionConfig("cam", max_concurrency=1)
    async with AsyncTransport(config, transport=httpx.MockTransport(handler)) as t:
        slow = asyncio.create_task(t.send(Request("GET", "/slow")))
        await asyncio.sleep(0.05)
        with pytest.raises(PoolTimeout):
            await t.send(Request("GET", "/fast", timeout=0.2))
        release.set()
        await slow
        assert (await t.send(Request("GET", "/after"))).status == 200


# -- Thread 8: blocking upload reads stay off the event loop -------------------


@pytest.mark.anyio
async def test_async_upload_chunks_are_read_in_a_worker_thread() -> None:
    main = threading.get_ident()
    threads: list[int] = []

    def chunks() -> Iterator[bytes]:
        for part in (b"ab", b"cd"):
            threads.append(threading.get_ident())
            yield part

    received: list[bytes] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        received.append(request.content)
        return httpx.Response(200)

    request = Request("POST", "/up", body=RawBody(chunks(), "application/octet-stream", size=4))
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as t:
        assert (await t.send(request)).status == 200
    assert received == [b"abcd"]
    assert threads and main not in threads


@pytest.mark.anyio
async def test_slow_upload_read_does_not_block_other_tasks() -> None:
    def chunks() -> Iterator[bytes]:
        for _ in range(3):
            time.sleep(0.1)
            yield b"x"

    ticks = 0

    async def ticker() -> None:
        nonlocal ticks
        while True:
            await asyncio.sleep(0.01)
            ticks += 1

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    request = Request("POST", "/up", body=RawBody(chunks(), "application/octet-stream", size=3))
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as t:
        task = asyncio.create_task(ticker())
        await t.send(request)
        task.cancel()
    assert ticks >= 10


# -- Threads 25, 26: retry policy applies when opening streams -----------------


def _response(request: Request) -> Response:
    return Response(200, Headers(()), b"", request)


class FlakyStreams:
    """Fails the first ``failures`` opens with ``error``, then serves one chunk."""

    def __init__(self, failures: int, error: Exception) -> None:
        self.failures, self.error = failures, error
        self.opens = 0

    def send(self, request: Request) -> Response:  # pragma: no cover - unused
        raise AssertionError

    @contextmanager
    def open_stream(self, request: Request) -> Iterator[tuple[Response, Iterator[bytes]]]:
        self.opens += 1
        if self.opens <= self.failures:
            raise self.error
        yield _response(request), iter([b"data"])


class FlakyAsyncStreams:
    def __init__(self, failures: int, error: Exception) -> None:
        self.failures, self.error = failures, error
        self.opens = 0

    async def send(self, request: Request) -> Response:  # pragma: no cover - unused
        raise AssertionError

    @asynccontextmanager
    async def open_stream(self, request: Request) -> AsyncIterator[tuple[Response, AsyncIterator[bytes]]]:
        self.opens += 1
        if self.opens <= self.failures:
            raise self.error

        async def one() -> AsyncIterator[bytes]:
            yield b"data"

        yield _response(request), one()


def stream_flow() -> CallFlow[BytesDecoder]:
    yield Request("GET", "/stream", stream=True)
    return BytesDecoder()


FAST = RetryPolicy(attempts=3, backoff=0)


def test_sync_stream_open_is_retried_when_unsent() -> None:
    transport = FlakyStreams(2, ConnectTimeout("t"))
    observed: list[dict[str, Any]] = []
    call = Call(retry=FAST, on_response=observed.append)
    with run_sync(transport, stream_flow(), call) as result:
        assert list(result) == [b"data"]
    assert transport.opens == 3
    assert [o["attempt"] for o in observed] == [1, 2, 3]
    assert [o["error"] for o in observed] == ["ConnectTimeout", "ConnectTimeout", None]


def test_sync_stream_open_gives_up_after_the_attempts() -> None:
    transport = FlakyStreams(5, ConnectTimeout("t"))
    with pytest.raises(ConnectTimeout):
        run_sync(transport, stream_flow(), Call(retry=FAST))
    assert transport.opens == 3


def test_sync_stream_open_respects_retry_unsent_false() -> None:
    transport = FlakyStreams(1, ConnectTimeout("t"))
    with pytest.raises(ConnectTimeout):
        run_sync(transport, stream_flow(), Call(retry=RetryPolicy(attempts=3, backoff=0, retry_unsent=False)))
    assert transport.opens == 1


def test_sync_stream_open_is_not_retried_after_the_request_was_sent() -> None:
    transport = FlakyStreams(1, ReadTimeout("t"))
    with pytest.raises(ReadTimeout):
        run_sync(transport, stream_flow(), Call(retry=RetryPolicy(attempts=3, backoff=0, retry_reads=True)))
    assert transport.opens == 1


@pytest.mark.anyio
async def test_async_stream_open_is_retried_when_unsent() -> None:
    transport = FlakyAsyncStreams(2, ConnectTimeout("t"))
    result = await run_async(transport, stream_flow(), Call(retry=FAST))
    async with result:
        assert [item async for item in result] == [b"data"]
    assert transport.opens == 3


@pytest.mark.anyio
async def test_async_stream_open_gives_up_after_the_attempts() -> None:
    transport = FlakyAsyncStreams(5, ConnectTimeout("t"))
    with pytest.raises(ConnectTimeout):
        await run_async(transport, stream_flow(), Call(retry=FAST))
    assert transport.opens == 3


def test_sync_failed_stream_open_emits_an_on_response_record() -> None:
    observed: list[dict[str, Any]] = []
    transport = FlakyStreams(5, ConnectTimeout("t"))
    with pytest.raises(ConnectTimeout):
        run_sync(transport, stream_flow(), Call(retry=FAST, on_response=observed.append))
    assert [o["error"] for o in observed] == ["ConnectTimeout"] * 3
    assert [o["attempt"] for o in observed] == [1, 2, 3]


@pytest.mark.anyio
async def test_async_failed_stream_open_emits_an_on_response_record() -> None:
    observed: list[dict[str, Any]] = []
    transport = FlakyAsyncStreams(5, ConnectTimeout("t"))
    with pytest.raises(ConnectTimeout):
        await run_async(transport, stream_flow(), Call(retry=FAST, on_response=observed.append))
    assert [o["error"] for o in observed] == ["ConnectTimeout"] * 3
