"""A large one-shot Upload that was already read from cannot be sent again from its current position."""

from __future__ import annotations

import io
import threading
from pathlib import Path

import httpx
import pytest

from ax_devil_device_api._http import upload
from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.options import RetryPolicy
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import MultipartBody, Request, release_deferred, resolve_deferred
from ax_devil_device_api._http.upload import Upload, file_part
from ax_devil_device_api._runtime.driver import Call, run_sync
from ax_devil_device_api.errors import ConfigurationError, ConnectionFailed

DATA = bytes(range(100))


@pytest.fixture(autouse=True)
def small_limits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(upload, "INLINE_LIMIT", 10)
    monkeypatch.setattr(upload, "CHUNK_SIZE", 8)


def _request(source: Upload | Path) -> Request:
    return Request("POST", "/up", body=MultipartBody(files=(file_part("file", source),)))


class Failing(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        chunks = iter(request.stream)  # type: ignore[arg-type]
        next(chunks)
        next(chunks)
        raise httpx.WriteError("boom")


class AFailing(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        chunks = request.stream.__aiter__()  # type: ignore[union-attr]
        await chunks.__anext__()
        await chunks.__anext__()
        raise httpx.WriteError("boom")


def test_sync_reusing_a_partly_consumed_large_upload_fails_locally() -> None:
    source = Upload(io.BytesIO(DATA), len(DATA))
    with SyncTransport(ConnectionConfig("cam"), transport=Failing()) as transport:
        with pytest.raises(ConnectionFailed):
            transport.send(resolve_deferred(_request(source)))
    with pytest.raises(ConfigurationError, match="already consumed; create a new Upload"):
        resolve_deferred(_request(source))  # raised while the request is prepared: nothing is sent


@pytest.mark.anyio
async def test_async_reusing_a_partly_consumed_large_upload_fails_locally() -> None:
    source = Upload(io.BytesIO(DATA), len(DATA))
    async with AsyncTransport(ConnectionConfig("cam"), transport=AFailing()) as transport:
        with pytest.raises(ConnectionFailed):
            await transport.send(await Call().aprepare(_request(source)))
    with pytest.raises(ConfigurationError, match="already consumed"):
        await Call().aprepare(_request(source))


def test_a_large_upload_prepared_but_released_without_a_read_is_still_usable() -> None:
    source = Upload(io.BytesIO(DATA), len(DATA))
    first = resolve_deferred(_request(source))  # prepared (a hook raised, or no slot was free) but never iterated
    release_deferred(first)  # what the driver does when the call ends
    resolve_deferred(_request(source))


def test_small_buffered_uploads_and_file_paths_stay_reusable(tmp_path: Path) -> None:
    small = Upload(io.BytesIO(b"abc"), 3)
    for _ in range(2):
        body = resolve_deferred(_request(small)).body
        assert isinstance(body, MultipartBody) and body.files[0].content == b"abc"
    path = tmp_path / "big.bin"
    path.write_bytes(DATA)
    for _ in range(2):
        body = resolve_deferred(_request(path)).body
        assert isinstance(body, MultipartBody) and b"".join(body.files[0].content) == DATA  # type: ignore[arg-type]


class Refusing(httpx.BaseTransport):
    """Fails to connect: the body is never touched."""

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)


def _upload_flow(source: Upload):  # type: ignore[no-untyped-def]
    response = yield _request(source)
    return response.status


def test_a_connect_failure_before_any_read_leaves_the_source_reusable() -> None:
    source = Upload(io.BytesIO(DATA), len(DATA))
    retry = RetryPolicy(attempts=1)
    with SyncTransport(ConnectionConfig("cam"), transport=Refusing()) as transport:
        with pytest.raises(ConnectionFailed):
            run_sync(transport, _upload_flow(source), Call(label=("a", "b"), retry=retry))
    seen: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.read())
        return httpx.Response(200)

    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        assert run_sync(transport, _upload_flow(source), Call(label=("a", "b"))) == 200
    assert DATA in seen[0]  # the full body, from the start of the stream


def test_two_calls_sharing_one_large_source_cannot_both_send() -> None:
    source = Upload(io.BytesIO(DATA), len(DATA))
    first = resolve_deferred(_request(source))  # the first call holds the lease
    with pytest.raises(ConfigurationError, match="in use by another call"):
        resolve_deferred(_request(source))  # the second fails locally, before anything is sent
    seen: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.read())
        return httpx.Response(200)

    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        assert transport.send(first).status == 200
    assert len(seen) == 1 and DATA in seen[0]
    release_deferred(first)
    with pytest.raises(ConfigurationError, match="already consumed"):
        resolve_deferred(_request(source))  # after a read the source is consumed for good


def test_concurrent_threads_on_one_source_exactly_one_sends_the_full_body() -> None:
    source = Upload(io.BytesIO(DATA), len(DATA))
    barrier = threading.Barrier(2)
    bodies: list[bytes] = []
    outcomes: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(request.read())
        return httpx.Response(200)

    def worker() -> None:
        with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
            barrier.wait()
            try:
                run_sync(transport, _upload_flow(source), Call(label=("a", "b")))
                outcomes.append("sent")
            except ConfigurationError:
                outcomes.append("refused")

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(outcomes) == ["refused", "sent"]
    assert len(bodies) == 1 and DATA in bodies[0]  # no second, partial request reached the device
