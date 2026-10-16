"""The Response an application can reach (``StreamResult.response``) carries a redacted copy of its request.

A masked argument such as export_recording's ``password`` is a long-lived credential: it must not be readable from the
public response, its repr or the result's repr. The original request stays internal (retries, authentication).
"""

from __future__ import annotations

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.debug import public_response, redact_request
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import (
    FilePart,
    FormBody,
    Headers,
    JsonBody,
    MultipartBody,
    RawBody,
    Request,
    Response,
)
from ax_devil_device_api._protocols.base import BytesDecoder
from ax_devil_device_api._runtime.driver import Call, run_async, run_sync
from ax_devil_device_api.testing import MockCamera

SENTINEL = "S3NT1N3L-PASSWORD"
EXPORT = "/axis-cgi/record/export/exportrecording.cgi"


def _shown(result: object) -> str:
    response = result.response  # type: ignore[attr-defined]
    return repr(response) + repr(response.request) + repr(response.request.query) + repr(result) + str(response.request.path)


def test_export_recording_hides_its_password_sync() -> None:
    cam = MockCamera()
    cam.cgi(EXPORT, text=b"MKV", content_type="video/x-matroska")
    with cam.device() as dev:
        with dev.apis.export_recording.export_recording(
            "rec", "disk", "matroska", password=SENTINEL, encryption_format="zip-aes256"
        ) as result:
            assert SENTINEL not in _shown(result)
            assert dict(result.response.request.query)["password"] == "<redacted>"
            assert dict(result.response.request.query)["recordingid"] == "rec"  # ordinary values stay
            assert b"".join(result) == b"MKV"
    # the wire request still carried the real password
    assert any(SENTINEL in str(r.query) for r in cam.requests)


@pytest.mark.anyio
async def test_export_recording_hides_its_password_async() -> None:
    cam = MockCamera()
    cam.cgi(EXPORT, text=b"MKV", content_type="video/x-matroska")
    dev = cam.async_device()
    async with dev:
        async with await dev.apis.export_recording.export_recording(
            "rec", "disk", "matroska", password=SENTINEL, encryption_format="zip-aes256"
        ) as result:
            assert SENTINEL not in _shown(result)


def _flow(request: Request):  # type: ignore[no-untyped-def]
    response = yield request
    if request.stream:
        return BytesDecoder()
    return response.status


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=b"data")


MASKED_REQUEST = Request("GET", "/x", query=(("token_like", SENTINEL), ("plain", "visible")), masked=frozenset({"token_like"}), stream=True)


def test_generic_masked_param_sync_streamed_and_buffered() -> None:
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_ok)) as transport:
        with run_sync(transport, _flow(MASKED_REQUEST), Call(label=("a", "b"))) as result:
            assert SENTINEL not in _shown(result) and "visible" in _shown(result)
        buffered = run_sync(transport, _flow(Request("GET", "/x", query=MASKED_REQUEST.query, masked=MASKED_REQUEST.masked)), Call(label=("a", "b")))
        assert SENTINEL not in repr(buffered)


@pytest.mark.anyio
async def test_generic_masked_param_async_streamed() -> None:
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_ok)) as transport:
        async with await run_async(transport, _flow(MASKED_REQUEST), Call(label=("a", "b"))) as result:
            assert SENTINEL not in _shown(result) and "visible" in _shown(result)


def test_the_internal_request_still_has_the_real_values() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, content=b"data")

    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        with run_sync(transport, _flow(MASKED_REQUEST), Call(label=("a", "b"))):
            pass
    assert SENTINEL in str(seen[0].url)  # what was sent is unchanged


def test_redact_request_covers_path_headers_and_every_body_kind() -> None:
    secret_named = Request("POST", f"/p/password={SENTINEL}/x", headers=(("X-Api-Token", SENTINEL),), masked=frozenset({"mine"}))
    shown = redact_request(secret_named)
    assert SENTINEL not in repr(shown)
    bodies = [
        JsonBody({"mine": SENTINEL, "ok": "1"}),
        JsonBody({"anything": SENTINEL}, sensitive=True),
        FormBody((("mine", SENTINEL), ("ok", "1"))),
        MultipartBody((("mine", SENTINEL),), (FilePart("f", "n.bin", SENTINEL.encode()),)),
        RawBody(SENTINEL.encode(), "application/octet-stream"),
    ]
    for body in bodies:
        request = Request("POST", "/x", body=body, masked=frozenset({"mine"}))
        assert SENTINEL not in repr(redact_request(request)), body


def test_public_response_leaves_status_headers_and_content_alone() -> None:
    request = Request("GET", "/x", query=(("mine", SENTINEL),), masked=frozenset({"mine"}))
    response = Response(200, Headers([("Content-Type", "text/plain")]), b"body", request)
    shown = public_response(response)
    assert shown.status == 200 and shown.content == b"body" and shown.headers["content-type"] == "text/plain"
    assert response.request.query[0][1] == SENTINEL  # the original is untouched
