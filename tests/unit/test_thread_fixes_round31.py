"""Cancelled/timed-out sends end the session; context exit publishes SessionClosed; the terminal outcome is set-once."""

from __future__ import annotations

import time

import anyio
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ConnectionFailed, ReadTimeout

QUICK = Heartbeat(None)


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


def _adevice(camera: FakeWsCamera) -> AsyncDevice:
    return AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport())


def _stall(camera: FakeWsCamera) -> list[bytes]:
    writes: list[bytes] = []

    async def stalled(buffer: bytes, timeout: float | None = None) -> None:
        writes.append(buffer)
        await anyio.sleep(30)

    camera.streams[0].write = stalled  # type: ignore[method-assign]
    return writes


# -- I: an interrupted async send ----------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_cancelled_send_ends_the_session_for_waiters_and_reraises_the_cancellation() -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        waiter: list[BaseException] = []
        cancelled = {"seen": False}

        async def wait_for_a_message() -> None:
            try:
                await session.receive(None)
            except BaseException as error:  # noqa: BLE001
                waiter.append(error)

        async def send_then_get_cancelled() -> None:
            try:
                await session.send(b"x")
            except anyio.get_cancelled_exc_class():
                cancelled["seen"] = True
                raise

        writes = _stall(camera)
        async with anyio.create_task_group() as tg:
            tg.start_soon(wait_for_a_message)
            await anyio.sleep(0.2)
            with anyio.move_on_after(0.3):
                await send_then_get_cancelled()
            await anyio.sleep(0.3)
        assert cancelled["seen"]  # the cancelled task saw the cancellation unchanged
        assert len(waiter) == 1 and isinstance(waiter[0], ConnectionFailed)  # the concurrent waiter got the failure
        sent = len(writes)
        with pytest.raises(ConnectionFailed):  # later sends and requests raise before writing anything
            await session.send(b"y")
        with pytest.raises(ConnectionFailed):
            await session.request("m", {}, timeout=1)
        assert len(writes) == sent
        assert camera.streams[0].closed  # the connection was dropped, no graceful close frame was attempted


@pytest.mark.anyio
async def test_send_timeout_stores_the_failure_and_later_sends_raise_immediately() -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        writes = _stall(camera)
        with pytest.raises(ReadTimeout):
            await session.request("m", {}, timeout=0.3)
        started = time.monotonic()
        with pytest.raises(ReadTimeout):
            await session.send(b"y")
        with pytest.raises(ReadTimeout):
            await session.request("m", {}, timeout=5)
        assert time.monotonic() - started < 0.5 and len(writes) == 1  # nothing more reached the peer
        assert camera.streams[0].closed and not camera.sockets[0].received


@pytest.mark.anyio
async def test_async_terminal_outcome_is_set_once_a_later_network_error_does_not_replace_it() -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        _stall(camera)
        with pytest.raises(ReadTimeout) as first:
            await session.request("m", {}, timeout=0.3)
        camera.sockets[0].network_error()
        await anyio.sleep(0.2)
        with pytest.raises(ReadTimeout) as later:
            await session.receive(timeout=1)
        assert later.value is first.value


def test_sync_terminal_outcome_is_set_once_a_later_network_error_does_not_replace_it() -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        stored = session._core.fail_with(ReadTimeout("send stalled"))  # noqa: SLF001
        camera.sockets[0].network_error()
        time.sleep(0.2)
        with pytest.raises(ReadTimeout) as caught:
            session.receive(timeout=1)
        assert caught.value is stored
        assert session._core.on_network_error() is stored  # noqa: SLF001
