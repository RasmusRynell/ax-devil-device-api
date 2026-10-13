"""A normal close ends the session at the recorded arrival time on every path; the close is recorded before the reader starts."""

from __future__ import annotations

import time
from typing import Any

import anyio
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http import transport as transport_module
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import SessionClosed

QUICK = Heartbeat(None)
CLOSE_AT = 5000.0


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


def _adevice(camera: FakeWsCamera) -> AsyncDevice:
    return AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport())


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """The transport stamps the close frame with this clock; the test sets it to CLOSE_AT when the frame arrives."""
    monkeypatch.setattr(transport_module, "_clock", lambda: CLOSE_AT)


def _last_seen(dev: Device | AsyncDevice) -> float:
    return dev._ledger._tracks[EVENTS.key].last_seen  # noqa: SLF001


def test_receive_after_a_delay_stamps_the_close_time(clock: None) -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1000)
            time.sleep(0.3)  # the app reads the close late
            with pytest.raises(SessionClosed):
                session.receive(timeout=3)
            assert _last_seen(dev) == CLOSE_AT


def test_close_and_context_exit_after_a_delay_stamp_the_close_time(clock: None) -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1001)
            time.sleep(0.3)
            session.close()
            assert _last_seen(dev) == CLOSE_AT
    camera = FakeWsCamera()
    with _device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK):
            camera.sockets[0].close(1000)
            time.sleep(0.3)
        assert _last_seen(dev) == CLOSE_AT  # context cleanup, close never read


def test_reaping_stamps_the_close_time(clock: None) -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK):
            camera.sockets[0].close(1000)
            time.sleep(0.3)
            with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None and again.gap.start.timestamp() == CLOSE_AT


@pytest.mark.anyio
async def test_async_receive_close_and_cleanup_stamp_the_close_time(clock: None) -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1000)
            await anyio.sleep(0.3)
            with pytest.raises(SessionClosed):
                await session.receive(timeout=3)
            assert _last_seen(dev) == CLOSE_AT
    camera = FakeWsCamera()
    async with _adevice(camera) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1001)
            await anyio.sleep(0.3)
            await session.close()
            assert _last_seen(dev) == CLOSE_AT
    camera = FakeWsCamera()
    async with _adevice(camera) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK):
            camera.sockets[0].close(1000)
            await anyio.sleep(0.3)
        assert _last_seen(dev) == CLOSE_AT


@pytest.mark.anyio
async def test_async_reaping_stamps_the_close_time(clock: None) -> None:
    camera = FakeWsCamera()
    async with _adevice(camera) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK):
            camera.sockets[0].close(1000)
            await anyio.sleep(0.3)
            async with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None and again.gap.start.timestamp() == CLOSE_AT


# -- the close is recorded before the reader starts ------------------------------------------


def test_close_during_a_slow_hook_is_still_recorded() -> None:
    camera = FakeWsCamera()

    def hook(record: Any) -> None:
        camera.sockets[-1].close(1000)  # the device closes while on_response runs
        time.sleep(0.3)

    with Device(
        "cam.test", credentials=("root", "pass"), transport=camera.transport(), on_response=hook
    ) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            recorded = session._core.remote_close  # noqa: SLF001
            assert recorded is not None and recorded[0] == 1000


@pytest.mark.anyio
async def test_async_close_during_a_slow_hook_is_still_recorded() -> None:
    camera = FakeWsCamera()

    def hook(record: Any) -> None:
        camera.sockets[-1].close(1000)
        time.sleep(0.3)

    async with AsyncDevice(
        "cam.test", credentials=("root", "pass"), transport=camera.async_transport(), on_response=hook
    ) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            await anyio.sleep(0.3)  # the reader task runs once the blocking hook is over; it saw the close frame
            recorded = session._core.remote_close  # noqa: SLF001
            assert recorded is not None and recorded[0] == 1000
