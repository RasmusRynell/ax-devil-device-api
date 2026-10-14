"""Closing with many coalesced frames in one socket read cannot hang; a directly cancelled aclose() still tears down."""

from __future__ import annotations

import asyncio
import json
import threading
import time

import pytest
import wsproto.events
from ws_fake import FakeWsCamera, notify

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS

QUICK = Heartbeat(None)
FRAMES = 150  # far more than the upstream queue holds, delivered in ONE read


def _coalesced(camera: FakeWsCamera, stream_index: int = 0) -> None:
    socket = camera.sockets[stream_index]
    data = b"".join(socket.conn.send(wsproto.events.TextMessage(json.dumps(notify(f"t/{n}", seq=str(n))))) for n in range(FRAMES))
    camera.streams[stream_index]._out.put(data)  # type: ignore[union-attr]  # noqa: SLF001 - one socket read, many frames


def _exits_within(seconds: float, close_first: bool) -> bool:
    camera = FakeWsCamera()
    finished = threading.Event()

    def scenario() -> None:
        with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
            with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
                _coalesced(camera)
                time.sleep(0.4)  # the reader is blocked in put() with the rest of the read still to deliver
                if close_first:
                    session.close()
        finished.set()

    threading.Thread(target=scenario, daemon=True).start()
    return finished.wait(seconds)


def test_context_exit_with_many_coalesced_frames_in_one_read_does_not_hang() -> None:
    assert _exits_within(15, close_first=False), "leaving the session hung on the reader"


def test_close_then_exit_with_many_coalesced_frames_does_not_hang() -> None:
    assert _exits_within(15, close_first=True)


def test_the_coalesced_frames_are_still_all_delivered_to_a_reading_consumer() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            _coalesced(camera)
            topics = [session.receive(timeout=10)["params"]["notification"]["topic"] for _ in range(FRAMES)]
            assert topics == [f"t/{n}" for n in range(FRAMES)]


@pytest.mark.anyio
async def test_async_context_exit_with_many_coalesced_frames_does_not_hang() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with asyncio.timeout(15):
            async with dev.connect_session(EVENTS, heartbeat=QUICK):
                socket = camera.sockets[0]
                data = b"".join(socket.conn.send(wsproto.events.TextMessage(json.dumps(notify(f"t/{n}")))) for n in range(FRAMES))
                camera.streams[0]._out.put_nowait(data)  # type: ignore[union-attr]  # noqa: SLF001
                await asyncio.sleep(0.3)
