"""on_request records and the public request copy redact body metadata identically (names, file names, content types, boundary)."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.debug import _body, emit_request, redact_request
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import FilePart, FormBody, JsonBody, MultipartBody, RawBody, Request
from ax_devil_device_api._protocols.base import BytesDecoder
from ax_devil_device_api._runtime.driver import Call, run_async, run_sync

FORBIDDEN = ["hunter2", "u:p@"]


def bodies() -> dict[str, Any]:
    return {
        "multipart filename": MultipartBody((), (FilePart("file", "password=hunter2", b"x"),)),
        "multipart part name": MultipartBody((), (FilePart("token=hunter2", "n.bin", b"x"),)),
        "multipart part content type": MultipartBody((), (FilePart("f", "n.bin", b"x", content_type="token=hunter2"),)),
        "multipart boundary": MultipartBody((), (FilePart("f", "n.bin", b"x"),), boundary="password=hunter2"),
        "multipart url in filename": MultipartBody((), (FilePart("f", "rtsp://u:p@h/x", b"x"),)),
        "multipart field": MultipartBody((("password=hunter2", "v"),), (FilePart("f", "n.bin", b"x"),)),
        "raw bytes content type": RawBody(b"abc", "token=hunter2"),
        "raw stream content type": RawBody(iter([b"abc"]), "token=hunter2", size=3),
        "form": FormBody((("password=hunter2", "v"),)),
        "json": JsonBody({"password=hunter2": "v"}),
    }


def _record(request: Request) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    emit_request(events.append, request, "https://cam/x", 5.0, True)
    return events[0]["request"]["body"]


@pytest.mark.parametrize("name", sorted(bodies()))
def test_record_and_public_copy_hide_the_same_secrets(name: str) -> None:
    request = Request("POST", "/x", body=bodies()[name])
    record = _record(request)
    public = redact_request(request)
    assert not any(bad in json.dumps(record) for bad in FORBIDDEN), record
    assert not any(bad in repr(public) for bad in FORBIDDEN), repr(public)
    assert _body(public.body) == record  # the record is a description of the same scrubbed body


def test_ordinary_metadata_is_left_alone() -> None:
    request = Request("POST", "/x", body=MultipartBody((), (FilePart("file", "firmware.bin", b"x", content_type="application/octet-stream"),), boundary="axdevil-1"))
    public = redact_request(request)
    assert isinstance(public.body, MultipartBody)
    assert public.body.files[0].filename == "firmware.bin" and public.body.files[0].content_type == "application/octet-stream"
    assert public.body.boundary == "axdevil-1"
    assert _record(request)["files"] == [{"name": "file", "filename": "firmware.bin", "size": 1}]


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=b"data")


def _flow(body: Any) -> Any:
    yield Request("POST", "/x", body=body, stream=True)
    return BytesDecoder()


@pytest.mark.parametrize("name", ["multipart filename", "multipart part content type", "multipart boundary", "raw bytes content type"])
def test_sync_stream_response_request_and_on_request_agree(name: str) -> None:
    records: list[dict[str, Any]] = []
    config = ConnectionConfig("cam", on_request=records.append)
    with SyncTransport(config, transport=httpx.MockTransport(_ok)) as transport:
        with run_sync(transport, _flow(bodies()[name]), Call(label=("a", "b"))) as result:
            assert not any(bad in repr(result.response) + repr(result.response.request) for bad in FORBIDDEN)
    assert not any(bad in json.dumps(records) for bad in FORBIDDEN)
    assert _body(result.response.request.body) == records[0]["request"]["body"]


@pytest.mark.anyio
@pytest.mark.parametrize("name", ["multipart filename", "multipart part content type", "raw bytes content type"])
async def test_async_stream_response_request_and_on_request_agree(name: str) -> None:
    records: list[dict[str, Any]] = []
    config = ConnectionConfig("cam", on_request=records.append)
    async with AsyncTransport(config, transport=httpx.MockTransport(_ok)) as transport:
        async with await run_async(transport, _flow(bodies()[name]), Call(label=("a", "b"))) as result:
            assert not any(bad in repr(result.response) + repr(result.response.request) for bad in FORBIDDEN)
    assert not any(bad in json.dumps(records) for bad in FORBIDDEN)
    assert _body(result.response.request.body) == records[0]["request"]["body"]
