"""A normal close ends the session at the recorded arrival time on every path; the close is recorded before the reader starts."""

from __future__ import annotations

import time
from typing import Any

import anyio
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS

QUICK = Heartbeat(None)


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


def _adevice(camera: FakeWsCamera) -> AsyncDevice:
    return AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport())


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
