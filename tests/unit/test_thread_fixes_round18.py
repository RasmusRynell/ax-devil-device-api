"""send() after the reader already processed a close frame raises the same error receive() would."""

from __future__ import annotations

import time
from typing import Any

import anyio
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime import ws
from ax_devil_device_api.errors import ConnectionFailed, SessionClosed, TransportError

QUICK = Heartbeat(None)
RAW = ws.SessionSpec("audio", "/audio")


def _cause(session: Any) -> str:
    termination = session._core.record.termination  # noqa: SLF001
    return termination[0] if termination else ""


def test_send_after_a_processed_1011_raises_a_transport_error() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(RAW, heartbeat=QUICK) as session:
            camera.sockets[0].close(1011)
            time.sleep(0.3)  # the reader has processed it; the app has not read it
            with pytest.raises(TransportError) as caught:
                session.send(b"x")
            assert isinstance(caught.value, ConnectionFailed) and "1011" in str(caught.value)
            assert _cause(session) == "abnormal_remote"


def test_send_after_a_normal_close_is_still_session_closed() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(RAW, heartbeat=QUICK) as session:
            camera.sockets[0].close(1000)
            time.sleep(0.3)
            with pytest.raises(SessionClosed):
                session.send(b"x")
            assert _cause(session) == "normal_remote"


@pytest.mark.anyio
async def test_async_send_after_a_processed_1011_raises_a_transport_error() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(RAW, heartbeat=QUICK) as session:
            camera.sockets[0].close(1011)
            await anyio.sleep(0.3)
            with pytest.raises(TransportError) as caught:
                await session.send(b"x")
            assert isinstance(caught.value, ConnectionFailed) and "1011" in str(caught.value)
            assert _cause(session) == "abnormal_remote"


@pytest.mark.anyio
async def test_async_send_after_a_normal_close_is_still_session_closed() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(RAW, heartbeat=QUICK) as session:
            camera.sockets[0].close(1000)
            await anyio.sleep(0.3)
            with pytest.raises(SessionClosed):
                await session.send(b"x")
            assert _cause(session) == "normal_remote"
