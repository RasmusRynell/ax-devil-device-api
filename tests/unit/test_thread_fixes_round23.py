"""One read path for receive, notifications and request: replies reach their request, notifications stay in order."""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any

import anyio
import pytest
from ws_fake import FakeSocket, FakeWsCamera, notify

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime import ws
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ConnectionFailed, ResponseFormatError, SessionClosed

QUICK = Heartbeat(None)
DELAYS = {"m1": 0.30, "m2": 0.10, "m3": 0.20, "m4": 0.05}  # replies come back as m4, m2, m3, m1
EXPECTED_TOPICS = ["t/m4", "t/m2", "t/m3", "t/m1"]


def _reply(message: Any) -> dict[str, Any]:
    return {"apiVersion": "1.0", "context": message["context"], "method": message["method"], "data": {"m": message["method"]}}


def _answer(socket: FakeSocket, message: Any) -> None:
    """A notification right before the reply, so the two are interleaved on the wire."""
    socket.push(notify(f"t/{message['method']}", seq=message["method"]))
    socket.push(_reply(message))


def _sync_handler(socket: FakeSocket, message: Any) -> None:
    if message["method"] in DELAYS:
        threading.Timer(DELAYS[message["method"]], _answer, args=(socket, message)).start()


def _async_handler(socket: FakeSocket, message: Any) -> None:
    if message["method"] in DELAYS:
        asyncio.get_running_loop().call_later(DELAYS[message["method"]], _answer, socket, message)


# -- a notification iterator plus concurrent requests ------------------------------------------------------


@pytest.mark.anyio
async def test_async_notification_iterator_and_concurrent_requests_all_complete() -> None:
    camera = FakeWsCamera(handler=_async_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            topics: list[str] = []
            results: dict[str, Any] = {}

            async def iterate() -> None:
                async for event in session.notifications():
                    topics.append(event.topic)
                    if len(topics) == len(DELAYS):
                        return

            async def call(method: str) -> None:
                results[method] = await session.request(method, {}, timeout=5)

            async with anyio.create_task_group() as tg:
                tg.start_soon(iterate)
                await anyio.sleep(0.05)
                for method in DELAYS:
                    tg.start_soon(call, method)
            assert results == {m: {"m": m} for m in DELAYS}
            assert topics == EXPECTED_TOPICS  # every notification, in the order the device sent them


def test_threaded_notification_iterator_and_concurrent_requests_all_complete() -> None:
    camera = FakeWsCamera(handler=_sync_handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            topics: list[str] = []
            results: dict[str, Any] = {}

            def iterate() -> None:
                for event in session.notifications():
                    topics.append(event.topic)
                    if len(topics) == len(DELAYS):
                        return

            def call(method: str) -> None:
                results[method] = session.request(method, {}, timeout=5)

            reader = threading.Thread(target=iterate)
            reader.start()
            time.sleep(0.05)
            callers = [threading.Thread(target=call, args=(m,)) for m in DELAYS]
            for thread in callers:
                thread.start()
            for thread in [*callers, reader]:
                thread.join(15)
                assert not thread.is_alive()
            assert results == {m: {"m": m} for m in DELAYS}
            assert topics == EXPECTED_TOPICS


@pytest.mark.anyio
async def test_async_receive_and_requests_share_the_read_path() -> None:
    camera = FakeWsCamera(handler=_async_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            raw: list[Any] = []

            async def drain() -> None:
                while len(raw) < 1:  # the notification of m1; its reply goes to the request, not here
                    raw.append(await session.receive(timeout=5))

            async with anyio.create_task_group() as tg:
                tg.start_soon(drain)
                await anyio.sleep(0.05)
                assert await session.request("m1", {}, timeout=5) == {"m": "m1"}  
            assert len(raw) == 1 and raw[0]["method"] == "events:notify"


# -- a close or failure wakes every pending request ---------------------------------------------------------


@pytest.mark.anyio
@pytest.mark.parametrize(("code", "expected"), [(1011, ConnectionFailed), (1000, SessionClosed)])
async def test_async_close_wakes_every_pending_request(code: int, expected: type[Exception]) -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            outcomes: list[BaseException] = []

            async def call(method: str) -> None:
                try:
                    await session.request(method, {}, timeout=10)
                except BaseException as error:  # noqa: BLE001
                    outcomes.append(error)

            started = time.monotonic()
            async with anyio.create_task_group() as tg:
                for method in ("a", "b", "c"):
                    tg.start_soon(call, method)
                await anyio.sleep(0.2)
                camera.sockets[0].close(code)
            assert len(outcomes) == 3 and all(isinstance(e, expected) for e in outcomes)
            assert time.monotonic() - started < 3


@pytest.mark.parametrize(("code", "expected"), [(1011, ConnectionFailed), (1000, SessionClosed)])
def test_threaded_close_wakes_every_pending_request(code: int, expected: type[Exception]) -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            outcomes: list[BaseException] = []

            def call(method: str) -> None:
                try:
                    session.request(method, {}, timeout=10)
                except BaseException as error:  # noqa: BLE001
                    outcomes.append(error)

            started = time.monotonic()
            threads = [threading.Thread(target=call, args=(m,)) for m in ("a", "b", "c")]
            for thread in threads:
                thread.start()
            time.sleep(0.3)
            camera.sockets[0].close(code)
            for thread in threads:
                thread.join(10)
                assert not thread.is_alive()
            assert len(outcomes) == 3 and all(isinstance(e, expected) for e in outcomes)
            assert time.monotonic() - started < 5


# -- token status, empty path segments ---------------------------------------------------------------------


@pytest.mark.parametrize("status", [401, 403, 404])
def test_token_fetch_judges_the_status_before_decoding_the_body(status: int) -> None:
    from ax_devil_device_api import errors

    camera = FakeWsCamera()
    original = camera._answer  # noqa: SLF001
    import httpx

    def answer(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/axis-cgi/wssession.cgi":
            return httpx.Response(status, content=b"\xff\xfe<html>nope</html>")
        return original(request)

    camera._answer = answer  # type: ignore[method-assign]  # noqa: SLF001
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with pytest.raises(errors.DeviceError) as caught:
            with dev.connect_session(EVENTS, heartbeat=QUICK, use_token=True):
                pass
    assert not isinstance(caught.value, ResponseFormatError)


@pytest.mark.parametrize("value", ["", ".", ".."])
def test_empty_or_dot_path_parameters_are_rejected_locally(value: str) -> None:
    spec = ws.SessionSpec("audio", "/audio/{audio_session_id}")
    with pytest.raises(ValueError, match="is not a valid path segment"):
        spec.bind({"audio_session_id": value})
    assert spec.bind({"audio_session_id": "ok id"}).path == "/audio/ok%20id"
