"""receive(timeout=) is validated; concurrent requests on one session are serialized and cannot steal each other's reply."""

from __future__ import annotations

import asyncio
import math
import threading
import time
from typing import Any

import anyio
import pytest
from ws_fake import FakeSocket, FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ReadTimeout

QUICK = Heartbeat(None)


def _reply(message: dict[str, Any]) -> dict[str, Any]:
    return {"apiVersion": "1.0", "context": message["context"], "method": message["method"], "data": {"m": message["method"]}}


def _sync_handler(socket: FakeSocket, message: Any) -> None:
    if message["method"] == "slow":
        threading.Timer(0.3, socket.push, args=(_reply(message),)).start()
    elif message["method"] != "silent":
        socket.push(_reply(message))


def _async_handler(socket: FakeSocket, message: Any) -> None:
    if message["method"] == "slow":
        asyncio.get_running_loop().call_later(0.3, socket.push, _reply(message))
    elif message["method"] != "silent":
        socket.push(_reply(message))


# -- receive(timeout=) ------------------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [math.inf, -math.inf, math.nan, -1, -0.5])
def test_receive_timeout_is_validated(bad: float) -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            with pytest.raises(ValueError, match="timeout must be a finite"):
                session.receive(timeout=bad)
            with pytest.raises(ReadTimeout):
                session.receive(timeout=0)  # 0 polls
            camera.sockets[0].push({"x": 1})
            assert session.receive(timeout=3) == {"x": 1}


@pytest.mark.anyio
@pytest.mark.parametrize("bad", [math.inf, math.nan, -1])
async def test_async_receive_timeout_is_validated(bad: float) -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            with pytest.raises(ValueError, match="timeout must be a finite"):
                await session.receive(timeout=bad)
            with pytest.raises(ReadTimeout):
                await session.receive(timeout=0)


# -- concurrent requests ----------------------------------------------------------------------------------


def test_threaded_requests_with_out_of_order_replies_both_complete() -> None:
    camera = FakeWsCamera(handler=_sync_handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            results: dict[str, Any] = {}

            def call(method: str) -> None:
                results[method] = session.request(method, {}, timeout=5)

            slow = threading.Thread(target=call, args=("slow",))
            slow.start()
            time.sleep(0.05)  # "slow" is out first, its reply comes late; "fast" would be answered at once
            fast = threading.Thread(target=call, args=("fast",))
            fast.start()
            slow.join(10)
            fast.join(10)
            assert results == {"slow": {"m": "slow"}, "fast": {"m": "fast"}}


@pytest.mark.anyio
async def test_async_concurrent_requests_with_out_of_order_replies_both_complete() -> None:
    camera = FakeWsCamera(handler=_async_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            results: dict[str, Any] = {}

            async def call(method: str) -> None:
                results[method] = await session.request(method, {}, timeout=5)

            async with anyio.create_task_group() as tg:
                tg.start_soon(call, "slow")
                await anyio.sleep(0.05)
                tg.start_soon(call, "fast")
            assert results == {"slow": {"m": "slow"}, "fast": {"m": "fast"}}


@pytest.mark.anyio
async def test_async_notifications_during_requests_are_still_queued() -> None:
    camera = FakeWsCamera(handler=_async_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].push({"note": 1})
            assert await session.request("fast", {}, timeout=5) == {"m": "fast"}
            assert await session.receive(timeout=3) == {"note": 1}


@pytest.mark.anyio
async def test_async_timed_out_or_cancelled_request_releases_the_lock() -> None:
    camera = FakeWsCamera(handler=_async_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            with pytest.raises(ReadTimeout):
                await session.request("silent", {}, timeout=0.2)
            assert await session.request("fast", {}, timeout=3) == {"m": "fast"}
            async with anyio.create_task_group() as tg:
                tg.start_soon(lambda: session.request("silent", {}, timeout=5))
                await anyio.sleep(0.1)
                tg.cancel_scope.cancel()
            assert await session.request("fast", {}, timeout=3) == {"m": "fast"}


@pytest.mark.anyio
async def test_async_an_outstanding_request_does_not_block_another() -> None:
    # Replaces the earlier "waiting for the turn" test: requests are multiplexed now (see test_thread_fixes_round23).
    camera = FakeWsCamera(handler=_async_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:

            async def hold() -> None:
                with pytest.raises(ReadTimeout):
                    await session.request("silent", {}, timeout=1)

            async with anyio.create_task_group() as tg:
                tg.start_soon(hold)
                await anyio.sleep(0.05)
                started = time.monotonic()
                assert await session.request("fast", {}, timeout=0.5) == {"m": "fast"}
                assert time.monotonic() - started < 0.4


def test_sync_timed_out_request_releases_the_lock() -> None:
    camera = FakeWsCamera(handler=_sync_handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            with pytest.raises(ReadTimeout):
                session.request("silent", {}, timeout=0.2)
            assert session.request("fast", {}, timeout=3) == {"m": "fast"}
