"""The unread-message buffer is bounded; multipart line limits are byte-accurate and split on LF only."""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

import anyio
import pytest
from ws_fake import FakeSocket, FakeWsCamera, notify

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._http.transport import WS_QUEUE_SIZE
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api._streams import MixedReplaceDecoder, MultipartLinesDecoder
from ax_devil_device_api.errors import ConnectionFailed, ResponseFormatError

QUICK = Heartbeat(None)
FLOOD = WS_QUEUE_SIZE * 3 + 100  # notifications sent before the reply
DROPPED = FLOOD - WS_QUEUE_SIZE


def _flood_then_reply(socket: FakeSocket, message: Any) -> None:
    if message["method"] == "flood":
        for n in range(FLOOD):
            socket.push(notify(f"t/{n}", seq=str(n)))
        socket.push({"apiVersion": "1.0", "context": message["context"], "method": "flood", "data": {"done": True}})


# -- bounded buffer -------------------------------------------------------------------------------------


def test_sync_request_during_a_flood_keeps_the_buffer_bounded_and_gets_its_reply(caplog: pytest.LogCaptureFixture) -> None:
    camera = FakeWsCamera(handler=_flood_then_reply)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session, caplog.at_level(logging.WARNING):
            assert session.request("flood", {}, timeout=20) == {"done": True}
            assert len(session._core.pending) == WS_QUEUE_SIZE  # noqa: SLF001
            assert session.dropped_notifications == DROPPED
            first = session.receive(timeout=1)  # the oldest ones are gone, the newest are kept in order
            assert first["params"]["notification"]["topic"] == f"t/{DROPPED}"
    assert len([r for r in caplog.records if "dropping the oldest" in r.message]) == 1  # one warning per episode


@pytest.mark.anyio
async def test_async_request_during_a_flood_keeps_the_buffer_bounded_and_gets_its_reply(
    caplog: pytest.LogCaptureFixture,
) -> None:
    camera = FakeWsCamera(handler=_flood_then_reply)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            with caplog.at_level(logging.WARNING):
                assert await session.request("flood", {}, timeout=20) == {"done": True}
            assert len(session._core.pending) == WS_QUEUE_SIZE  # noqa: SLF001
            assert session.dropped_notifications == DROPPED
            first = await session.receive(timeout=1)
            assert first["params"]["notification"]["topic"] == f"t/{DROPPED}"
    assert len([r for r in caplog.records if "dropping the oldest" in r.message]) == 1


def test_sync_normal_consumption_drops_nothing() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            for n in range(WS_QUEUE_SIZE * 2):
                camera.sockets[0].push(notify(f"t/{n}", seq=str(n)))
            topics = [session.receive(timeout=5)["params"]["notification"]["topic"] for _ in range(WS_QUEUE_SIZE * 2)]
            assert topics == [f"t/{n}" for n in range(WS_QUEUE_SIZE * 2)]
            assert session.dropped_notifications == 0


@pytest.mark.anyio
async def test_async_normal_consumption_drops_nothing() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            for n in range(WS_QUEUE_SIZE * 2):
                camera.sockets[0].push(notify(f"t/{n}", seq=str(n)))
            seen = [(await session.receive(timeout=5))["params"]["notification"]["topic"] for _ in range(WS_QUEUE_SIZE * 2)]
            assert seen == [f"t/{n}" for n in range(WS_QUEUE_SIZE * 2)]
            assert session.dropped_notifications == 0


def test_sync_failure_still_wakes_pending_requests_with_a_full_buffer() -> None:
    camera = FakeWsCamera(handler=_flood_then_reply)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            assert session.request("flood", {}, timeout=20) == {"done": True}  # the buffer is full now
            outcomes: list[BaseException] = []

            def call() -> None:
                try:
                    session.request("silent", {}, timeout=10)
                except BaseException as error:  # noqa: BLE001
                    outcomes.append(error)

            threads = [threading.Thread(target=call) for _ in range(2)]
            for thread in threads:
                thread.start()
            time.sleep(0.3)
            camera.sockets[0].close(1011)
            for thread in threads:
                thread.join(10)
                assert not thread.is_alive()
            assert len(outcomes) == 2 and all(isinstance(e, ConnectionFailed) for e in outcomes)


@pytest.mark.anyio
async def test_async_failure_still_wakes_pending_requests_with_a_full_buffer() -> None:
    camera = FakeWsCamera(handler=_flood_then_reply)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            assert await session.request("flood", {}, timeout=20) == {"done": True}
            outcomes: list[BaseException] = []

            async def call() -> None:
                try:
                    await session.request("silent", {}, timeout=10)
                except BaseException as error:  # noqa: BLE001
                    outcomes.append(error)

            async with anyio.create_task_group() as tg:
                tg.start_soon(call)
                tg.start_soon(call)
                await anyio.sleep(0.3)
                camera.sockets[0].close(1011)
            assert len(outcomes) == 2 and all(isinstance(e, ConnectionFailed) for e in outcomes)


# -- multipart lines: bytes, LF only ---------------------------------------------------------------------------


def _decode(body: bytes, max_line_bytes: int = 1000) -> list[str]:
    data = b"--b\r\nContent-Type: text/plain\r\n\r\n" + body + b"\r\n--b--\r\n"
    return MultipartLinesDecoder(MixedReplaceDecoder("b"), max_line_bytes=max_line_bytes).feed(data)


def test_unicode_line_separators_do_not_split_a_line() -> None:
    assert _decode("one two\u0085three\nnext\r\nlast".encode()) == ["one two\u0085three", "next", "last"]


def test_line_limit_counts_bytes_not_characters() -> None:
    line = "€" * 4  # 4 characters, 12 bytes
    with pytest.raises(ResponseFormatError, match="exceeds"):
        _decode(line.encode(), max_line_bytes=10)
    assert _decode(b"a" * 10, max_line_bytes=10) == ["a" * 10]
    assert _decode(line.encode(), max_line_bytes=12) == [line]
