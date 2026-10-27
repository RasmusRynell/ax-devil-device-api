"""Non-finite floats are never sent over a WebSocket; a failed session keeps raising its failure."""

from __future__ import annotations

import time

import anyio
import pytest
from ws_fake import FakeWsCamera, events_handler

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ConnectionFailed

QUICK = Heartbeat(None)
BAD = [float("nan"), float("inf"), float("-inf")]


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


@pytest.mark.parametrize("value", BAD)
def test_non_finite_floats_are_rejected_before_anything_is_sent(value: float) -> None:
    camera = FakeWsCamera(handler=events_handler)
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        with pytest.raises(ValueError, match="NaN and infinity"):
            session.send({"x": [1, {"y": value}]})
        with pytest.raises(ValueError, match="NaN and infinity"):
            session.request("events:configure", {"v": value})
        assert camera.sockets[0].received == []  # nothing reached the wire
        session.send({"ok": 1})  # the session is still usable
        time.sleep(0.2)
        assert camera.sockets[0].received == [{"ok": 1}]


@pytest.mark.anyio
@pytest.mark.parametrize("value", BAD)
async def test_async_non_finite_floats_are_rejected_before_anything_is_sent(value: float) -> None:
    camera = FakeWsCamera(handler=events_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            with pytest.raises(ValueError, match="NaN and infinity"):
                await session.send({"x": value})
            with pytest.raises(ValueError, match="NaN and infinity"):
                await session.request("events:configure", {"v": value})
            assert camera.sockets[0].received == []
            await session.send({"ok": 1})
            await anyio.sleep(0.2)
            assert camera.sockets[0].received == [{"ok": 1}]


@pytest.mark.parametrize("how", ["close_1011", "network_error"])
def test_second_receive_after_a_failure_raises_the_same_error_at_once(how: str) -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        getattr(camera.sockets[0], "close" if how == "close_1011" else "network_error")(*([1011] if how == "close_1011" else []))
        with pytest.raises(ConnectionFailed) as first:
            session.receive(timeout=3)
        started = time.monotonic()
        with pytest.raises(ConnectionFailed) as second:
            session.receive(timeout=3)
        assert second.value is first.value and time.monotonic() - started < 0.5
        with pytest.raises(ConnectionFailed):
            session.request("events:configure", {})
        assert session._core.record.termination[0] in ("abnormal_remote", "network")  # type: ignore[index]  # noqa: SLF001


@pytest.mark.anyio
@pytest.mark.parametrize("how", ["close_1011", "network_error"])
async def test_async_second_receive_after_a_failure_raises_the_same_error_at_once(how: str) -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            getattr(camera.sockets[0], "close" if how == "close_1011" else "network_error")(*([1011] if how == "close_1011" else []))
            with pytest.raises(ConnectionFailed) as first:
                await session.receive(timeout=3)
            started = time.monotonic()
            with pytest.raises(ConnectionFailed) as second:
                await session.receive(timeout=3)
            assert second.value is first.value and time.monotonic() - started < 0.5
            with pytest.raises(ConnectionFailed):
                await session.request("events:configure", {})
