"""Leaving the context after the device closed abnormally publishes that close, not SessionClosed(1000)."""

from __future__ import annotations

import time

import anyio
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ConnectionFailed

QUICK = Heartbeat(None)


def test_sync_context_exit_after_a_1011_publishes_the_failure() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1011)
            time.sleep(0.3)  # the reader has stamped it; the app has not read it
        record = session._core.record  # noqa: SLF001
        assert record is not None and record.termination is not None and record.termination[0] == "abnormal_remote"
        with pytest.raises(ConnectionFailed, match="1011"):  # not SessionClosed(1000)
            session.receive(timeout=0.2)
        with pytest.raises(ConnectionFailed):
            session.request("m", {}, timeout=0.2)


@pytest.mark.anyio
async def test_async_context_exit_after_a_1011_publishes_the_failure() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1011)
            await anyio.sleep(0.3)
        record = session._core.record  # noqa: SLF001
        assert record is not None and record.termination is not None and record.termination[0] == "abnormal_remote"
        with pytest.raises(ConnectionFailed, match="1011"):
            await session.receive(timeout=0.2)
        with pytest.raises(ConnectionFailed):
            await session.request("m", {}, timeout=0.2)
