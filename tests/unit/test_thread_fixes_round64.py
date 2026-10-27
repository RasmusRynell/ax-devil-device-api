"""Frames are built and written under one session lock: concurrent senders never have two frames built and unwritten."""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any

import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import DATA_HUB, EVENTS

QUICK = Heartbeat(None)
THREADS = 8
PER_THREAD = 25


class _Watch:
    """Counts frames that are built but not yet written; a serialized sender never has more than one."""

    def __init__(self) -> None:
        self.pending = 0
        self.most = 0
        self.guard = threading.Lock()

    def built(self) -> None:
        with self.guard:
            self.pending += 1
            self.most = max(self.most, self.pending)

    def written(self) -> None:
        with self.guard:
            self.pending -= 1


def _instrument(raw: Any, watch: _Watch) -> None:
    build, write = raw.connection.send, raw.stream.write

    def slow_build(event: Any) -> bytes:
        data = build(event)
        watch.built()
        time.sleep(0.0005)  # widens the window between building a frame and writing it
        return data

    def counted_write(*args: Any, **kwargs: Any) -> None:
        write(*args, **kwargs)
        watch.written()

    raw.connection.send = slow_build
    raw.stream.write = counted_write


def test_sync_concurrent_senders_never_interleave_build_and_write() -> None:
    camera = FakeWsCamera()
    watch = _Watch()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(DATA_HUB, heartbeat=QUICK) as session:
            _instrument(session._raw, watch)  # noqa: SLF001
            errors: list[BaseException] = []

            def sender(number: int) -> None:
                try:
                    for index in range(PER_THREAD):
                        session.send({"t": number, "m": index})
                except BaseException as error:  # noqa: BLE001
                    errors.append(error)

            threads = [threading.Thread(target=sender, args=(n,)) for n in range(THREADS)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=30)
    assert not errors and watch.most == 1, (watch.most, errors[:1])
    received = camera.sockets[0].received
    assert sorted((m["t"], m["m"]) for m in received) == sorted((n, i) for n in range(THREADS) for i in range(PER_THREAD))


def test_sync_requests_from_several_threads_are_serialized_too() -> None:
    camera = FakeWsCamera(handler=lambda socket, message: socket.push({"jsonrpc": "2.0", "id": message["id"], "result": {}}))
    watch = _Watch()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(DATA_HUB, heartbeat=QUICK) as session:
            _instrument(session._raw, watch)  # noqa: SLF001
            results: list[Any] = []
            failures: list[BaseException] = []

            def ask(number: int) -> None:
                try:
                    for _ in range(5):
                        results.append(session.request("data-hub_v1:listTopics", {"n": number}, timeout=10))
                except BaseException as error:  # noqa: BLE001
                    failures.append(error)

            threads = [threading.Thread(target=ask, args=(n,)) for n in range(THREADS)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=30)
    assert not failures and len(results) == THREADS * 5 and watch.most == 1


@pytest.mark.anyio
async def test_async_concurrent_senders_never_interleave_build_and_write() -> None:
    camera = FakeWsCamera()
    watch = _Watch()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            raw = session._raw  # noqa: SLF001
            build, write = raw.connection.send, raw.stream.write

            def slow_build(event: Any) -> bytes:
                data = build(event)
                watch.built()
                return data

            async def counted_write(buffer: bytes, timeout: float | None = None) -> None:
                await asyncio.sleep(0.0005)  # lets other senders run between building a frame and writing it
                await write(buffer, timeout)
                watch.written()

            raw.connection.send = slow_build
            raw.stream.write = counted_write

            async def sender(number: int) -> None:
                for index in range(PER_THREAD):
                    await session.send({"t": number, "m": index})

            await asyncio.gather(*(sender(n) for n in range(THREADS)))
    assert watch.most == 1
    assert sorted((m["t"], m["m"]) for m in camera.sockets[0].received) == sorted((n, i) for n in range(THREADS) for i in range(PER_THREAD))
