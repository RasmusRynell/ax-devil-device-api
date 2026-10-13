"""Line streams are bounded; leaving a session whose close fails still releases the socket, the reader and the slot."""

from __future__ import annotations

import time
from typing import Any

import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime import ws
from ax_devil_device_api._streams import LinesDecoder, MixedReplaceDecoder, MultipartLinesDecoder
from ax_devil_device_api.errors import ResponseFormatError

QUICK = Heartbeat(None)
RAW = ws.SessionSpec("audio", "/audio")


# -- bounded lines ---------------------------------------------------------------------------


def test_unterminated_line_stream_is_bounded() -> None:
    decoder = LinesDecoder(max_line_bytes=1000)
    assert decoder.feed(b"ok\nsecond\npartial") == ["ok", "second"]
    with pytest.raises(ResponseFormatError, match="exceeds"):
        for _ in range(100):
            decoder.feed(b"x" * 100)


def test_a_single_long_line_in_one_chunk_is_rejected() -> None:
    with pytest.raises(ResponseFormatError):
        LinesDecoder(max_line_bytes=10).feed(b"short\n" + b"y" * 11 + b"\n")


def test_default_limit_is_one_mebibyte() -> None:
    decoder = LinesDecoder()
    assert decoder.feed(b"a" * (1024 * 1024)) == []
    with pytest.raises(ResponseFormatError):
        decoder.feed(b"a")


def test_multipart_lines_are_bounded_too() -> None:
    body = b"--b\r\nContent-Type: text/plain\r\n\r\n" + b"z" * 50 + b"\r\n--b\r\n"
    decoder = MultipartLinesDecoder(MixedReplaceDecoder("b"), max_line_bytes=10)
    with pytest.raises(ResponseFormatError, match="exceeds"):
        decoder.feed(body)
    ok = MultipartLinesDecoder(MixedReplaceDecoder("b"), max_line_bytes=100)
    assert ok.feed(body) == ["z" * 50]


# -- a close whose write fails records a network end (the real close() is kept; the failure is injected at stream.write) --

import anyio  # noqa: E402
import httpcore  # noqa: E402

from ax_devil_device_api._http import transport as transport_module  # noqa: E402
from ax_devil_device_api._streams import decoder_for  # noqa: E402


def _failing_write(error: Exception) -> Any:
    def write(*args: Any, **kwargs: Any) -> None:
        raise error

    return write


def _async_failing_write(error: Exception) -> Any:
    async def write(*args: Any, **kwargs: Any) -> None:
        raise error

    return write


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    now = [1000.0]
    monkeypatch.setattr(transport_module, "_clock", lambda: now[0])
    return now


@pytest.mark.parametrize("error", [httpcore.WriteError("swallowed by httpx-ws"), httpcore.ReadError("raised by close")])
def test_close_whose_write_fails_is_a_network_end_at_the_last_frame(clock: list[float], error: Exception) -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=4) as dev:
        dev._ledger.now = lambda: clock[0]  # noqa: SLF001
        with dev.connect_session(RAW, heartbeat=QUICK) as session:
            clock[0] = 1010.0
            camera.sockets[0].push_bytes(b"d")
            assert session.receive(timeout=5) == b"d"
            camera.streams[0].write = _failing_write(error)  # type: ignore[method-assign,assignment]
            clock[0] = 1100.0
            session.close()  # the real close
            termination = session._core.record.termination  # type: ignore[union-attr]  # noqa: SLF001
            assert termination is not None and termination[0] == "network"
        clock[0] = 1200.0
        with dev.connect_session(RAW, heartbeat=QUICK) as again:
            assert again.gap is not None and again.gap.start.timestamp() == 1010.0


def test_context_exit_whose_close_write_fails_is_a_network_end_and_releases_the_slot(clock: list[float]) -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=1) as dev:
        dev._ledger.now = lambda: clock[0]  # noqa: SLF001
        for _ in range(3):  # more than max_streams: a leaked slot would time out
            clock[0] = 1000.0
            with dev.connect_session(RAW, heartbeat=QUICK):
                clock[0] = 1010.0
                camera.sockets[-1].push_bytes(b"d")
                time.sleep(0.2)
                camera.streams[-1].write = _failing_write(httpcore.WriteError("gone"))  # type: ignore[method-assign,assignment]
                clock[0] = 1100.0
        clock[0] = 1200.0
        with dev.connect_session(RAW, heartbeat=QUICK) as again:
            assert again.gap is not None and again.gap.start.timestamp() < 1100.0  # not stamped as a clean local close


@pytest.mark.anyio
@pytest.mark.parametrize("error", [httpcore.WriteError("swallowed by httpx-ws"), httpcore.ReadError("raised by close")])
async def test_async_close_whose_write_fails_is_a_network_end(clock: list[float], error: Exception) -> None:
    camera = FakeWsCamera()
    async with AsyncDevice(
        "cam.test", credentials=("root", "pass"), transport=camera.async_transport(), max_streams=4
    ) as dev:
        dev._ledger.now = lambda: clock[0]  # noqa: SLF001
        async with dev.connect_session(RAW, heartbeat=QUICK) as session:
            clock[0] = 1010.0
            camera.sockets[0].push_bytes(b"d")
            assert await session.receive(timeout=5) == b"d"
            camera.streams[0].write = _async_failing_write(error)  # type: ignore[method-assign,assignment]
            clock[0] = 1100.0
            await session.close()
            termination = session._core.record.termination  # type: ignore[union-attr]  # noqa: SLF001
            assert termination is not None and termination[0] == "network"
        clock[0] = 1200.0
        async with dev.connect_session(RAW, heartbeat=QUICK) as again:
            assert again.gap is not None and again.gap.start.timestamp() == 1010.0
    with anyio.fail_after(1):
        pass


# -- the multipart decoder is chosen by media type --------------------------------------------


class _Lines:
    decoder = "lines"
    encoding = "utf-8"


@pytest.mark.parametrize(
    "content_type", ['multipart/x-mixed-replace; boundary=""', "multipart/x-mixed-replace", "multipart/mixed; boundary="]
)
def test_multipart_lines_stream_without_a_boundary_is_rejected_not_read_as_lines(content_type: str) -> None:
    from ax_devil_device_api._http.types import Headers, Request, Response

    response = Response(200, Headers([("content-type", content_type)]), b"", Request("GET", "/x"))
    with pytest.raises(ResponseFormatError):
        decoder_for(_Lines(), response)


@pytest.mark.anyio
async def test_cancelled_heartbeat_write_on_a_normal_exit_is_not_a_write_failure(clock: list[float]) -> None:
    camera = FakeWsCamera()
    async with AsyncDevice(
        "cam.test", credentials=("root", "pass"), transport=camera.async_transport(), max_streams=4
    ) as dev:
        dev._ledger.now = lambda: clock[0]  # noqa: SLF001
        async with dev.connect_session(RAW, heartbeat=Heartbeat(0.05, 5)) as session:
            clock[0] = 1010.0
            camera.sockets[0].push_bytes(b"d")
            assert await session.receive(timeout=5) == b"d"
            stream = camera.streams[0]
            real_write = stream.write

            async def slow_write(buffer: bytes, timeout: float | None = None) -> None:
                await anyio.sleep(0.1)  # a heartbeat ping write is in flight when the session is left
                await real_write(buffer, timeout)

            stream.write = slow_write  # type: ignore[method-assign]
            await anyio.sleep(0.07)
            clock[0] = 1100.0
        assert camera.sockets[0].closed_by_client == 1000  # the peer saw a normal close
        clock[0] = 1200.0
        async with dev.connect_session(RAW, heartbeat=QUICK) as again:
            assert again.gap is not None and again.gap.start.timestamp() == 1100.0
