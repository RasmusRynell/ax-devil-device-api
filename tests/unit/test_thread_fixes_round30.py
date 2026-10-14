"""A refused send is stored as the terminal outcome; sends are bounded (async by the request deadline, sync by the
transport write timeout)."""

from __future__ import annotations

import threading
import time
from typing import Any

import anyio
import httpcore
import pytest
import wsproto.utilities
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ConnectionFailed, ReadTimeout, SessionClosed

QUICK = Heartbeat(None)


def _refuse(*args: Any, **kwargs: Any) -> None:
    raise wsproto.utilities.LocalProtocolError("connection is closed")


async def _arefuse(*args: Any, **kwargs: Any) -> None:
    raise wsproto.utilities.LocalProtocolError("connection is closed")


def _run(results: list[Any], fn: Any) -> threading.Thread:
    def target() -> None:
        try:
            results.append(("value", fn()))
        except BaseException as error:  # noqa: BLE001
            results.append(("error", error))

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread


# -- E: LocalProtocolError on send ------------------------------------------------------------------------------------


def test_sync_refused_send_is_stored_and_wakes_the_pending_request_and_reader() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            owner: list[Any] = []
            pending: list[Any] = []
            threads = [_run(owner, lambda: session.receive(None))]
            time.sleep(0.2)
            threads.append(_run(pending, lambda: session.request("silent", {}, timeout=10)))
            time.sleep(0.2)
            session._raw.send_bytes = _refuse  # type: ignore[method-assign]  # noqa: SLF001
            started = time.monotonic()
            with pytest.raises(SessionClosed):
                session.send(b"x")
            for thread in threads:
                thread.join(5)
                assert not thread.is_alive()
            assert time.monotonic() - started < 3
            assert isinstance(owner[0][1], SessionClosed) and isinstance(pending[0][1], SessionClosed)
            with pytest.raises(SessionClosed):  # every later read raises it too
                session.receive(timeout=0.1)


@pytest.mark.anyio
async def test_async_refused_send_is_stored_and_wakes_the_pending_request_and_reader() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            outcomes: list[BaseException] = []

            async def run(fn: Any) -> None:
                try:
                    await fn()
                except BaseException as error:  # noqa: BLE001
                    outcomes.append(error)

            started = time.monotonic()
            async with anyio.create_task_group() as tg:
                tg.start_soon(run, lambda: session.receive(None))
                await anyio.sleep(0.2)
                tg.start_soon(run, lambda: session.request("silent", {}, timeout=10))
                await anyio.sleep(0.2)
                session._raw.send_bytes = _arefuse  # type: ignore[method-assign]  # noqa: SLF001
                with pytest.raises(SessionClosed):
                    await session.send(b"x")
            assert time.monotonic() - started < 3
            assert len(outcomes) == 2 and all(isinstance(e, SessionClosed) for e in outcomes)
            with pytest.raises(SessionClosed):
                await session.receive(timeout=0.1)


# -- F: bounded sends ---------------------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_async_request_bounds_a_stalled_send_by_its_deadline() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:

            async def stalled(buffer: bytes, timeout: float | None = None) -> None:
                await anyio.sleep(30)

            camera.streams[0].write = stalled  # type: ignore[method-assign]
            started = time.monotonic()
            with pytest.raises(ReadTimeout):
                await session.request("m", {}, timeout=0.3)
            assert time.monotonic() - started < 2
            termination = session._core.record.termination  # type: ignore[union-attr]  # noqa: SLF001
            assert termination is not None and termination[0] == "network"  # a half-written frame ends the session
            with pytest.raises(ReadTimeout):  # and every later read raises the stored outcome
                await session.receive(timeout=0.1)


def test_sync_sends_get_the_transport_write_timeout() -> None:
    camera = FakeWsCamera()
    seen: list[float | None] = []
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), timeout=0.25) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            real = camera.streams[0].write

            def stalled(buffer: bytes, timeout: float | None = None) -> None:
                seen.append(timeout)
                if timeout is not None and timeout < 1:
                    raise httpcore.WriteTimeout("stalled")  # what the real socket does when the peer does not read
                real(buffer, timeout)

            camera.streams[0].write = stalled  # type: ignore[method-assign]
            with pytest.raises(ConnectionFailed):
                session.send(b"x")
            assert seen[0] == 0.25  # httpx-ws writes without a timeout; the transport supplies the device timeout
            termination = session._core.record.termination  # type: ignore[union-attr]  # noqa: SLF001
            assert termination is not None and termination[0] == "network"
