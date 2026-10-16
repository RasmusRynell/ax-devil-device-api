"""Failed uploads close the files they opened, even while the exception is retained."""

from __future__ import annotations

import asyncio
import os

import httpx
import pytest

from ax_devil_device_api import errors
from ax_devil_device_api._http import upload
from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import MultipartBody, RawBody, Request, resolve_deferred


def _open_fds() -> int:
    return len(os.listdir("/proc/self/fd"))


def _request(path: str, kind: str) -> Request:
    part = upload.file_part("file", __import__("pathlib").Path(path))
    if kind == "raw":
        request = Request("POST", "/up", body=RawBody(part.content, "application/octet-stream", size=part.size))
    else:
        request = Request("POST", "/up", body=MultipartBody(files=(part,)))
    return resolve_deferred(request)  # what the driver does before the transport sees it


@pytest.fixture
def big_file(tmp_path, monkeypatch):
    monkeypatch.setattr(upload, "INLINE_LIMIT", 10)
    monkeypatch.setattr(upload, "CHUNK_SIZE", 8)
    path = tmp_path / "fw.bin"
    path.write_bytes(b"x" * 100)
    return str(path)


@pytest.mark.parametrize("kind", ["raw", "multipart"])
def test_sync_failed_upload_closes_file(big_file, kind):
    class Failing(httpx.BaseTransport):
        def handle_request(self, request: httpx.Request) -> httpx.Response:
            chunks = iter(request.stream)  # type: ignore[arg-type]  # stays referenced by the retained traceback
            next(chunks)
            next(chunks)
            raise httpx.WriteError("boom")

    before = _open_fds()
    kept = []
    with SyncTransport(ConnectionConfig("cam"), transport=Failing()) as transport:
        for _ in range(3):
            with pytest.raises(errors.ConnectionFailed) as info:
                transport.send(_request(big_file, kind))
            kept.append(info.value)
        assert _open_fds() == before


@pytest.mark.parametrize("kind", ["raw", "multipart"])
def test_async_failed_upload_closes_file(big_file, kind):
    asyncio.run(_async_case(big_file, kind))


async def _async_case(big_file, kind):
    class Failing(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            chunks = request.stream.__aiter__()  # type: ignore[union-attr]
            await chunks.__anext__()
            await chunks.__anext__()
            raise httpx.WriteError("boom")

    before = _open_fds()
    kept = []
    async with AsyncTransport(ConnectionConfig("cam"), transport=Failing()) as transport:
        for _ in range(3):
            with pytest.raises(errors.ConnectionFailed) as info:
                await transport.send(_request(big_file, kind))
            kept.append(info.value)
        assert _open_fds() == before
