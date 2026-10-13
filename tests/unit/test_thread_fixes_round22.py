"""receive(timeout=0) returns a buffered frame; a boundary-looking sequence inside a part without Content-Length stays content."""

from __future__ import annotations

import time

import anyio
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime import ws
from ax_devil_device_api._streams import MixedReplaceDecoder, Part
from ax_devil_device_api.errors import ReadTimeout

QUICK = Heartbeat(None)
RAW = ws.SessionSpec("audio", "/audio")


# -- receive(timeout=0) -----------------------------------------------------------------------------------


def test_sync_receive_zero_returns_a_buffered_frame_and_times_out_when_empty() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(RAW, heartbeat=QUICK) as session:
            with pytest.raises(ReadTimeout):
                session.receive(timeout=0)
            camera.sockets[0].push_bytes(b"frame")
            time.sleep(0.2)  # buffered by the reader
            assert session.receive(timeout=0) == b"frame"
            with pytest.raises(ReadTimeout):
                session.receive(timeout=0)


@pytest.mark.anyio
async def test_async_receive_zero_returns_a_buffered_frame_and_times_out_when_empty() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(RAW, heartbeat=QUICK) as session:
            with pytest.raises(ReadTimeout):
                await session.receive(timeout=0)
            camera.sockets[0].push_bytes(b"frame")
            await anyio.sleep(0.2)
            assert await session.receive(timeout=0) == b"frame"
            with pytest.raises(ReadTimeout):
                await session.receive(timeout=0)


@pytest.mark.anyio
async def test_async_receive_zero_surfaces_a_buffered_close() -> None:
    from ax_devil_device_api.errors import SessionClosed

    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(RAW, heartbeat=QUICK) as session:
            camera.sockets[0].close(1000)
            await anyio.sleep(0.2)
            with pytest.raises(SessionClosed):
                await session.receive(timeout=0)


# -- boundary lookalikes inside a part without Content-Length ----------------------------------------------


def _parts(data: bytes, chunk: int | None) -> list[Part]:
    decoder = MixedReplaceDecoder("b")
    pieces = [data] if chunk is None else [data[i : i + chunk] for i in range(0, len(data), chunk)]
    parts: list[Part] = []
    for piece in pieces:
        parts += decoder.feed(piece)
    decoder.close()
    return parts


@pytest.mark.parametrize("chunk", [None, 1, 2, 3, 7])
def test_a_lookalike_boundary_inside_the_content_does_not_truncate_the_part(chunk: int | None) -> None:
    content = b"line one\r\n--bextra and more\r\n--b not a boundary\r\n--b-x tail"
    data = b"--b\r\nContent-Type: text/plain\r\n\r\n" + content + b"\r\n--b\r\nContent-Type: text/plain\r\n\r\nnext\r\n--b--\r\n"
    parts = _parts(data, chunk)
    assert [p.body for p in parts] == [content, b"next"]


@pytest.mark.parametrize("chunk", [None, 1, 2, 5])
def test_real_boundary_forms_still_end_a_part(chunk: int | None) -> None:
    data = (
        b"--b\r\n\r\none\r\n--b\r\n\r\ntwo\n--b  \t\r\n\r\nthree\r\n--b\n\nfour\r\n--b--"
    )
    assert [p.body for p in _parts(data, chunk)] == [b"one", b"two", b"three", b"four"]


def test_endless_blanks_after_a_candidate_do_not_buffer_without_bound() -> None:
    decoder = MixedReplaceDecoder("b", max_part_bytes=5000)
    decoder.feed(b"--b\r\n\r\nbody\r\n--b" + b" " * 4000)
    assert decoder.feed(b"more") == []  # judged not a boundary after a bounded wait; scanning goes on
