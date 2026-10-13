"""Streamed bodies: multipart/x-mixed-replace decoding and stream results with cleanup."""

from __future__ import annotations

import random
from collections.abc import AsyncIterator, Iterator

import httpx
import pytest

from ax_devil_device_api import errors
from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import Headers, Request, Response
from ax_devil_device_api._runtime.driver import AsyncStreamResult, Call, StreamResult, run_async, run_sync
from ax_devil_device_api._streams import LinesDecoder, MixedReplaceDecoder, Part, boundary_of, decoder_for, mjpeg_decoder, stream_flow

JPEG_A = b"\xff\xd8AAAA\r\n--not-a-boundary\xff\xd9"
JPEG_B = b"\xff\xd8" + bytes(range(256)) * 4 + b"\xff\xd9"


def frame(body: bytes, *, length: bool = True, boundary: str = "myboundary") -> bytes:
    head = f"--{boundary}\r\nContent-Type: image/jpeg\r\n" + (f"Content-Length: {len(body)}\r\n" if length else "") + "\r\n"
    return head.encode() + body + b"\r\n"


def decode(data: bytes, *, boundary: str = "myboundary", chunk: int | None = None) -> list[Part]:
    decoder = MixedReplaceDecoder(boundary)
    parts: list[Part] = []
    pieces = [data] if chunk is None else [data[i : i + chunk] for i in range(0, len(data), chunk)]
    for piece in pieces:
        parts += decoder.feed(piece)
    parts += decoder.close()
    return parts


@pytest.mark.parametrize("chunk", [None, 1, 3, 7, 64, 1000])
@pytest.mark.parametrize("length", [True, False])
def test_mjpeg_parts_any_chunking(chunk: int | None, length: bool) -> None:
    stream = b"".join(frame(b, length=length) for b in (JPEG_A, JPEG_B, JPEG_A)) + b"--myboundary--\r\n"
    parts = decode(stream, chunk=chunk)
    assert [p.body for p in parts] == [JPEG_A, JPEG_B, JPEG_A]
    assert parts[0].content_type == "image/jpeg" and parts[0].headers["content-length"] == str(len(JPEG_A)) if length else True


def test_unknown_length_part_is_released_when_next_boundary_arrives() -> None:
    decoder = MixedReplaceDecoder("b")
    assert decoder.feed(frame(b"one", length=False, boundary="b")) == []  # next boundary not seen yet
    parts = decoder.feed(b"--b\r\nContent-Type: image/jpeg\r\n\r\ntwo")
    assert [p.body for p in parts] == [b"one"]  # "two" waits for its closing boundary


def test_tolerates_preamble_bare_newlines_and_dashed_boundary() -> None:
    data = b"preamble\r\n--b\nContent-Type: text/plain\n\nhello\n--b\nContent-Type: text/plain\n\nbye\n--b--"
    assert [p.body for p in decode(data, boundary="b")] == [b"hello", b"bye"]
    dashed = frame(JPEG_B, boundary="xx")
    assert [p.body for p in decode(dashed, boundary="--xx")] == [JPEG_B]


def test_truncated_part_raises_on_close() -> None:
    data = frame(JPEG_B)[:-100]
    with pytest.raises(errors.ConnectionFailed):
        decode(data)
    with pytest.raises(errors.ConnectionFailed):
        decode(b"--myboundary\r\nContent-Type: image/jpeg\r\n")
    assert decode(b"") == []


def test_limits() -> None:
    with pytest.raises(errors.ResponseFormatError):
        MixedReplaceDecoder("b", max_part_bytes=10).feed(frame(b"x" * 11, boundary="b"))
    with pytest.raises(errors.ResponseFormatError):
        MixedReplaceDecoder("b", max_part_bytes=10).feed(b"--b\r\n\r\n" + b"y" * 50)


def test_random_chunking_property() -> None:
    rng = random.Random(7)
    bodies = [bytes(rng.randrange(256) for _ in range(rng.randrange(0, 3000))) for _ in range(20)]
    stream = b"".join(frame(b, length=rng.random() < 0.5) for b in bodies)
    for _ in range(20):
        decoder = MixedReplaceDecoder("myboundary")
        parts: list[Part] = []
        i = 0
        while i < len(stream):
            n = rng.randrange(1, 500)
            parts += decoder.feed(stream[i : i + n])
            i += n
        assert [p.body for p in parts] == bodies[: len(parts)] and len(parts) >= len(bodies) - 1


def test_boundary_and_response_helpers() -> None:
    assert boundary_of('multipart/x-mixed-replace; boundary="my b"') == "my b"
    assert boundary_of("multipart/x-mixed-replace;boundary=--x") == "--x"
    assert boundary_of("image/jpeg") is None
    request = Request("GET", "/axis-cgi/mjpg/video.cgi")
    ok = Response(200, Headers([("Content-Type", "multipart/x-mixed-replace; boundary=myboundary")]), b"", request)
    assert isinstance(mjpeg_decoder(ok), MixedReplaceDecoder)
    with pytest.raises(errors.ResponseFormatError):
        mjpeg_decoder(Response(200, Headers([("Content-Type", "image/jpeg")]), b"", request))


def test_lines_decoder() -> None:
    d = LinesDecoder()
    assert d.feed(b"a\r\nb") == ["a"] and d.feed(b"c\nd") == ["bc"] and d.close() == ["d"]


# -- end to end through the transports --------------------------------------

STREAM = b"".join(frame(b) for b in (JPEG_A, JPEG_B, JPEG_A))
HEADERS = {"Content-Type": "multipart/x-mixed-replace; boundary=myboundary"}


class Chunks(httpx.SyncByteStream, httpx.AsyncByteStream):
    def __init__(self, data: bytes, size: int = 100) -> None:
        self.data, self.size = data, size
        self.closed = False
        self.sent = 0

    def __iter__(self) -> Iterator[bytes]:
        for i in range(0, len(self.data), self.size):
            self.sent += 1
            yield self.data[i : i + self.size]

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for i in range(0, len(self.data), self.size):
            self.sent += 1
            yield self.data[i : i + self.size]

    def close(self) -> None:
        self.closed = True

    async def aclose(self) -> None:
        self.closed = True


def mjpeg_flow(path: str = "/axis-cgi/mjpg/video.cgi"):
    return stream_flow(
        Request("GET", path),
        mjpeg_decoder,
        lambda response: errors.HttpError(response.status, response.excerpt(), api="video", operation="mjpeg"),
    )


def test_stream_result_sync_reads_all_parts_and_releases_slot() -> None:
    body = Chunks(STREAM)
    handler = lambda request: httpx.Response(200, headers=HEADERS, stream=body)  # noqa: E731
    with SyncTransport(ConnectionConfig("cam", max_streams=1), transport=httpx.MockTransport(handler)) as transport:
        for _ in range(2):  # the single stream slot must be free again
            body.closed = False
            result = run_sync(transport, mjpeg_flow(), Call())
            assert isinstance(result, StreamResult)
            with result as parts:
                assert [p.body for p in parts] == [JPEG_A, JPEG_B, JPEG_A]
            assert body.closed


def test_stream_result_sync_early_exit_closes_connection() -> None:
    body = Chunks(STREAM * 50, size=50)
    handler = lambda request: httpx.Response(200, headers=HEADERS, stream=body)  # noqa: E731
    with SyncTransport(ConnectionConfig("cam", max_streams=1), transport=httpx.MockTransport(handler)) as transport:
        with run_sync(transport, mjpeg_flow(), Call()) as parts:
            first = next(iter(parts))
            assert first.body == JPEG_A
        assert body.closed and body.sent < len(STREAM * 50) // 50
        with run_sync(transport, mjpeg_flow(), Call()):
            pass  # slot was released


def test_stream_error_status_raises_with_body() -> None:
    handler = lambda request: httpx.Response(503, text="busy")  # noqa: E731
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        with pytest.raises(errors.HttpError) as raised:
            run_sync(transport, mjpeg_flow(), Call())
        assert raised.value.status == 503 and "busy" in raised.value.body_excerpt


def test_wrong_content_type_closes_stream() -> None:
    body = Chunks(b"x" * 10)
    handler = lambda request: httpx.Response(200, headers={"Content-Type": "image/jpeg"}, stream=body)  # noqa: E731
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        with pytest.raises(errors.ResponseFormatError):
            run_sync(transport, mjpeg_flow(), Call())
    assert body.closed


@pytest.mark.anyio
async def test_stream_result_async() -> None:
    body = Chunks(STREAM * 20, size=50)
    handler = lambda request: httpx.Response(200, headers=HEADERS, stream=body)  # noqa: E731
    async with AsyncTransport(ConnectionConfig("cam", max_streams=1), transport=httpx.MockTransport(handler)) as transport:
        result = await run_async(transport, mjpeg_flow(), Call())
        assert isinstance(result, AsyncStreamResult)
        async with result as parts:
            got = [p async for p in parts]
        assert len(got) == 60 and body.closed
        body.closed = False
        async with await run_async(transport, mjpeg_flow(), Call()) as parts:
            async for part in parts:
                assert part.body == JPEG_A
                break
        assert body.closed
        with pytest.raises(errors.HttpError):
            await run_async(AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(lambda r: httpx.Response(500))), mjpeg_flow(), Call())


# -- the lines decoder on multipart answers (port.cgi?monitor=...) ------------------

PORT_MONITOR = (
    b"--x\r\nContent-Type: text/plain\r\n\r\n1I:/\r\n\r\n"
    b"--x\r\nContent-Type: text/plain\r\n\r\n\r\n"  # keep-alive: an empty part
    b"--x\r\nContent-Type: text/plain\r\n\r\n1I:H\r\n2I:\\\r\n\r\n"
    b"--x--\r\n"
)
PORT_HEADERS = {"Content-Type": "multipart/x-mixed-replace; boundary=x"}


def lines_flow():
    from ax_devil_device_api._protocols.cgi import Stream

    return stream_flow(
        Request("GET", "/axis-cgi/io/port.cgi"),
        lambda response: decoder_for(Stream("lines"), response),
        lambda response: errors.HttpError(response.status, response.excerpt(), api="io", operation="monitor"),
    )


@pytest.mark.parametrize("size", [1, 7, 10_000])
def test_lines_stream_on_multipart_returns_part_text_only(size: int) -> None:
    body = Chunks(PORT_MONITOR, size=size)
    handler = lambda request: httpx.Response(200, headers=PORT_HEADERS, stream=body)  # noqa: E731
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        with run_sync(transport, lines_flow(), Call()) as lines:
            assert list(lines) == ["1I:/", "1I:H", "2I:\\"]


def test_lines_stream_on_plain_text_is_unchanged() -> None:
    handler = lambda request: httpx.Response(200, headers={"Content-Type": "text/plain"}, content=b"a\r\n\r\nb\n")  # noqa: E731
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        with run_sync(transport, lines_flow(), Call()) as lines:
            assert list(lines) == ["a", "", "b"]


@pytest.mark.anyio
async def test_lines_stream_on_multipart_async() -> None:
    handler = lambda request: httpx.Response(200, headers=PORT_HEADERS, stream=Chunks(PORT_MONITOR, size=13))  # noqa: E731
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        async with await run_async(transport, lines_flow(), Call()) as lines:
            assert [line async for line in lines] == ["1I:/", "1I:H", "2I:\\"]


def test_lines_stream_cut_inside_a_part_fails() -> None:
    handler = lambda request: httpx.Response(200, headers=PORT_HEADERS, content=b"--x\r\nContent-Type: text/plain\r\n\r\n1I:")  # noqa: E731
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(handler)) as transport:
        with pytest.raises(errors.ConnectionFailed):
            with run_sync(transport, lines_flow(), Call()) as lines:
                list(lines)
