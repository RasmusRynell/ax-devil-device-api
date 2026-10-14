"""Terminal outcomes reach every reader; a request's timeout is its total budget."""

from __future__ import annotations

import threading
import time
from typing import Any

import anyio
import httpcore
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ConnectionFailed, ReadTimeout, SessionClosed

QUICK = Heartbeat(None)


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


def _adevice(camera: FakeWsCamera) -> AsyncDevice:
    return AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport())


def _in_thread(results: list[Any], fn: Any) -> threading.Thread:
    def run() -> None:
        try:
            results.append(("value", fn()))
        except BaseException as error:  # noqa: BLE001
            results.append(("error", error))

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread


def _failing(error: Exception) -> Any:
    def write(*args: Any, **kwargs: Any) -> None:
        raise error

    return write


# -- (a) a failed send ends the reader owner's wait and the pending request ----------------------------------------


def test_sync_send_failure_wakes_the_reader_owner_and_the_pending_request() -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        owner: list[Any] = []
        pending: list[Any] = []
        owner_thread = _in_thread(owner, lambda: session.receive(None))  # owns the reader, blocked
        time.sleep(0.2)
        pending_thread = _in_thread(pending, lambda: session.request("silent", {}, timeout=10))
        time.sleep(0.2)
        camera.streams[0].write = _failing(httpcore.WriteError("broken pipe"))  # type: ignore[method-assign,assignment]
        started = time.monotonic()
        with pytest.raises(ConnectionFailed):
            session.send(b"x")
        for thread in (owner_thread, pending_thread):
            thread.join(5)
            assert not thread.is_alive()
        assert time.monotonic() - started < 3  # not the 10 s request timeout
        assert isinstance(owner[0][1], ConnectionFailed) and isinstance(pending[0][1], ConnectionFailed)


@pytest.mark.anyio
async def test_async_send_failure_wakes_the_reader_owner_and_the_pending_request() -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        outcomes: list[BaseException] = []
        started = time.monotonic()

        async def run(fn: Any) -> None:
            try:
                await fn()
            except BaseException as error:  # noqa: BLE001
                outcomes.append(error)

        async with anyio.create_task_group() as tg:
            tg.start_soon(run, lambda: session.receive(None))
            await anyio.sleep(0.2)
            tg.start_soon(run, lambda: session.request("silent", {}, timeout=10))
            await anyio.sleep(0.2)

            async def broken(*args: Any, **kwargs: Any) -> None:
                raise httpcore.WriteError("broken pipe")

            camera.streams[0].write = broken  # type: ignore[method-assign,assignment]
            with pytest.raises(ConnectionFailed):
                await session.send(b"x")
        assert time.monotonic() - started < 3
        assert len(outcomes) == 2 and all(isinstance(e, ConnectionFailed) for e in outcomes)


# -- (b) / (c) a local close() ends every wait with SessionClosed, even without the peer's acknowledgement ----------


@pytest.mark.parametrize("acknowledged", [True, False])
def test_sync_local_close_wakes_everyone_with_session_closed(acknowledged: bool) -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        owner: list[Any] = []
        pending: list[Any] = []
        owner_thread = _in_thread(owner, lambda: session.receive(None))
        time.sleep(0.2)
        pending_thread = _in_thread(pending, lambda: session.request("silent", {}, timeout=10))
        time.sleep(0.2)
        if not acknowledged:
            camera.sockets[0].feed = lambda data: None  # type: ignore[method-assign]  # the device never answers
        started = time.monotonic()
        session.close()
        for thread in (owner_thread, pending_thread):
            thread.join(5)
            assert not thread.is_alive()
        assert time.monotonic() - started < 3
        assert isinstance(owner[0][1], SessionClosed) and isinstance(pending[0][1], SessionClosed)


@pytest.mark.anyio
@pytest.mark.parametrize("acknowledged", [True, False])
async def test_async_local_close_makes_pending_requests_raise_session_closed(acknowledged: bool) -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        outcomes: list[BaseException] = []

        async def run(method: str) -> None:
            try:
                await session.request(method, {}, timeout=10)
            except BaseException as error:  # noqa: BLE001
                outcomes.append(error)

        async with anyio.create_task_group() as tg:
            tg.start_soon(run, "a")
            tg.start_soon(run, "b")
            await anyio.sleep(0.3)
            if not acknowledged:
                camera.sockets[0].feed = lambda data: None  # type: ignore[method-assign]
            await session.close()
        assert len(outcomes) == 2 and all(isinstance(e, SessionClosed) for e in outcomes)  # not ConnectionFailed


# -- the request timeout is the total budget --------------------------------------------------------------------------


def test_sync_request_timeout_includes_a_slow_send() -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        real = camera.streams[0].write

        def slow(buffer: bytes, timeout: float | None = None) -> None:
            time.sleep(0.4)
            real(buffer, timeout)

        camera.streams[0].write = slow  # type: ignore[method-assign]
        started = time.monotonic()
        with pytest.raises(ReadTimeout):
            session.request("silent", {}, timeout=0.1)
        assert time.monotonic() - started < 0.47  # the write took 0.4; waiting for a reply did not start another 0.1


@pytest.mark.anyio
async def test_async_request_timeout_includes_a_slow_send() -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        real: Any = camera.streams[0].write

        async def slow(buffer: bytes, timeout: float | None = None) -> None:
            await anyio.sleep(0.4)
            await real(buffer, timeout)

        camera.streams[0].write = slow  # type: ignore[method-assign]
        started = time.monotonic()
        with pytest.raises(ReadTimeout):
            await session.request("silent", {}, timeout=0.1)
        assert time.monotonic() - started < 0.47
