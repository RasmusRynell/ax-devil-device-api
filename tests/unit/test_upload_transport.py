"""Transport details behind the upload and bare-query bindings."""

from __future__ import annotations

import httpx

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.multipart import encode_multipart
from ax_devil_device_api._http.transport import SyncTransport
from ax_devil_device_api._http.types import FilePart, MultipartBody, RawBody, Request


def send(request: Request) -> httpx.Request:
    seen: list[httpx.Request] = []

    def handler(r: httpx.Request) -> httpx.Response:
        seen.append(r)
        return httpx.Response(200)

    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        transport.send(request)
    return seen[0]


def test_streamed_raw_body_declares_its_size() -> None:
    request = send(Request("POST", "/up", body=RawBody(iter([b"ab", b"cde"]), "application/octet-stream", size=5)))
    assert request.headers["content-length"] == "5" and request.read() == b"abcde"


def test_bare_query_keys_keep_their_order() -> None:
    request = send(Request("GET", "/a.json", query=(("setparams", None), ("date", "a b"), ("flag", None))))
    assert request.url.query == b"setparams&date=a+b&flag"
    assert send(Request("GET", "/a", query=(("k", "v"),))).url.query == b"k=v"


def test_file_part_without_filename_is_a_typed_field() -> None:
    encoded = encode_multipart(MultipartBody((), (FilePart("json", None, b"{}", "application/json"),), boundary="B"))
    assert encoded.content == (
        b'--B\r\nContent-Disposition: form-data; name="json"\r\nContent-Type: application/json\r\n\r\n{}\r\n--B--\r\n'
    )
