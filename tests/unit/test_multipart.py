"""multipart/form-data request bodies."""

from __future__ import annotations

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.multipart import encode_multipart
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import FilePart, MultipartBody, Request


def parse(content: bytes, content_type: str):
    """Parse with the standard library so the encoder is checked against an independent reader."""
    from email.parser import BytesParser
    from email.policy import HTTP

    message = BytesParser(policy=HTTP).parsebytes(b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + content)
    return [(p.get_param("name", header="content-disposition"), p.get_filename(), p.get_content_type(), p.get_payload(decode=True)) for p in message.iter_parts()]


def test_bytes_body_layout_and_order() -> None:
    body = MultipartBody(
        (("kind", "firmware"), ("note", "ünï")),
        (FilePart("file", "fw.bin", b"\x00\r\n--x\xff", "application/octet-stream"), FilePart("meta", "m.json", b"{}", "application/json")),
        boundary="BOUND",
    )
    encoded = encode_multipart(body)
    assert encoded.content_type == "multipart/form-data; boundary=BOUND" and encoded.replayable
    assert isinstance(encoded.content, bytes) and encoded.length == len(encoded.content)
    assert encoded.content.endswith(b"--BOUND--\r\n")
    parts = parse(encoded.content, encoded.content_type)
    assert [(p[0], p[1], p[2]) for p in parts] == [
        ("kind", None, "text/plain"), ("note", None, "text/plain"), ("file", "fw.bin", "application/octet-stream"), ("meta", "m.json", "application/json"),
    ]
    assert parts[1][3] == "ünï".encode() and parts[2][3] == b"\x00\r\n--x\xff"


def test_names_are_escaped() -> None:
    body = MultipartBody((), (FilePart('we"ird', 'a"b\\c.bin', b"x"),), boundary="B")
    encoded = encode_multipart(body)
    assert isinstance(encoded.content, bytes)
    assert b'name="we%22ird"' in encoded.content and b'filename="a%22b\\\\c.bin"' in encoded.content


def test_generated_boundary_is_unique_and_valid() -> None:
    a, b = encode_multipart(MultipartBody()), encode_multipart(MultipartBody())
    assert a.content_type != b.content_type
    with pytest.raises(ValueError):
        encode_multipart(MultipartBody(boundary="bad boundary"))
    with pytest.raises(ValueError):
        encode_multipart(MultipartBody(boundary="x" * 71))


def test_streamed_file_with_known_size() -> None:
    chunks = [b"a" * 10, b"b" * 5]
    body = MultipartBody((("k", "v"),), (FilePart("file", "fw.bin", iter(chunks), size=15),), boundary="B")
    assert not body.replayable and not Request("POST", "/u", body=body).replayable
    encoded = encode_multipart(body)
    assert not isinstance(encoded.content, bytes) and not encoded.replayable
    data = b"".join(encoded.content)
    assert encoded.length == len(data)
    assert parse(data, encoded.content_type)[1][3] == b"a" * 10 + b"b" * 5


def test_streamed_file_without_size_has_unknown_length() -> None:
    encoded = encode_multipart(MultipartBody((), (FilePart("f", "f.bin", iter([b"x"])),), boundary="B"))
    assert encoded.length is None


def capture(headers_out: list[httpx.Request]):
    def handler(request: httpx.Request) -> httpx.Response:
        request.read()
        headers_out.append(request)
        return httpx.Response(200, text="OK")

    return handler


def test_sync_transport_sends_streamed_multipart_with_content_length() -> None:
    seen: list[httpx.Request] = []
    body = MultipartBody((("k", "v"),), (FilePart("file", "fw.bin", iter([b"12345", b"67890"]), size=10),), boundary="B")
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(capture(seen))) as transport:
        transport.send(Request("POST", "/upload", body=body))
    request = seen[0]
    assert request.headers["content-type"] == "multipart/form-data; boundary=B"
    assert int(request.headers["content-length"]) == len(request.content) and "transfer-encoding" not in request.headers
    assert b"1234567890" in request.content


@pytest.mark.anyio
async def test_async_transport_sends_streamed_multipart() -> None:
    seen: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        await request.aread()
        seen.append(request)
        return httpx.Response(200)

    body = MultipartBody((), (FilePart("file", "fw.bin", iter([b"12345", b"67890"]), size=10),), boundary="B")
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        await transport.send(Request("POST", "/upload", body=body))
        await transport.send(Request("POST", "/upload", body=MultipartBody((("a", "b"),), (), boundary="B")))
    assert b"1234567890" in seen[0].content and int(seen[0].headers["content-length"]) == len(seen[0].content)
    assert seen[1].content.startswith(b"--B\r\n")


def test_streamed_multipart_is_never_replayed_after_a_challenge() -> None:
    from ax_devil_device_api import errors
    from ax_devil_device_api._http.config import Credentials

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, headers={"WWW-Authenticate": 'Digest realm="r", nonce="n", qop="auth"'})

    body = MultipartBody((), (FilePart("file", "fw.bin", iter([b"x"]), size=1),))
    with SyncTransport(ConnectionConfig("cam", credentials=Credentials("u", "p")), transport=httpx.MockTransport(handler)) as transport:
        with pytest.raises(errors.AuthError):
            transport.send(Request("POST", "/upload", body=body))
