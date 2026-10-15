"""A large one-shot Upload that was already read from cannot be sent again from its current position."""

from __future__ import annotations

import io
from pathlib import Path

import httpx
import pytest

from ax_devil_device_api._http import upload
from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import MultipartBody, Request, resolve_deferred
from ax_devil_device_api._http.upload import Upload, file_part
from ax_devil_device_api._runtime.driver import Call
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


def test_a_large_upload_that_was_never_read_is_still_usable() -> None:
    source = Upload(io.BytesIO(DATA), len(DATA))
    resolve_deferred(_request(source))  # prepared (e.g. a hook then raised or no slot was free) but never iterated
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
