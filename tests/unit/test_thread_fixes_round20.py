"""request(timeout=) is validated before anything is sent; every handshake attempt gets a fresh wssession token."""

from __future__ import annotations

import math

import httpx
import pytest
from ws_fake import FakeWsCamera, events_handler

from ax_devil_device_api import AsyncDevice, Device, RetryPolicy
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS

QUICK = Heartbeat(None)
TOKEN_PATH = "/axis-cgi/wssession.cgi"


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


@pytest.mark.parametrize("bad", [math.inf, -math.inf, math.nan, 0, -1, 0.0])
def test_request_timeout_is_validated_before_sending(bad: float) -> None:
    camera = FakeWsCamera(handler=events_handler)
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        with pytest.raises(ValueError, match="timeout must be a positive, finite"):
            session.request("events:configure", {}, timeout=bad)
        assert camera.sockets[0].received == []  # nothing was sent
        assert session.request("events:configure", {}, timeout=5) == {}  # still usable


@pytest.mark.anyio
@pytest.mark.parametrize("bad", [math.inf, math.nan, 0, -1])
async def test_async_request_timeout_is_validated_before_sending(bad: float) -> None:
    camera = FakeWsCamera(handler=events_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            with pytest.raises(ValueError, match="timeout must be a positive, finite"):
                await session.request("events:configure", {}, timeout=bad)
            assert camera.sockets[0].received == []
            assert await session.request("events:configure", {}, timeout=5) == {}


def _flaky(camera: FakeWsCamera) -> httpx.MockTransport:
    """The first WebSocket upgrade fails before it is sent (a retryable connect error)."""
    failures = [1]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.headers.get("upgrade") == "websocket" and failures[0]:
            failures[0] -= 1
            raise httpx.ConnectError("refused", request=request)
        return camera._answer(request)  # noqa: SLF001

    return httpx.MockTransport(handler)


def _tokens(camera: FakeWsCamera) -> list[str]:
    return [r.url.params.get("wssession", "") for r in camera.requests if r.headers.get("upgrade") == "websocket"]


def test_each_handshake_attempt_fetches_a_fresh_token() -> None:
    camera = FakeWsCamera()
    issued = iter(f"token-{n}" for n in range(10))
    camera.token = next(issued)
    original = camera._answer  # noqa: SLF001

    def answer(request: httpx.Request) -> httpx.Response:
        if request.url.path == TOKEN_PATH:
            camera.token = next(issued)
        return original(request)

    camera._answer = answer  # type: ignore[method-assign]  # noqa: SLF001
    with Device(
        "cam.test", credentials=("root", "pass"), transport=_flaky(camera), retry=RetryPolicy(attempts=2, backoff=0)
    ) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK, use_token=True):
            pass
    fetches = [r for r in camera.requests if r.url.path == TOKEN_PATH]
    assert len(fetches) == 2  # two handshake attempts, two token fetches
    assert _tokens(camera) == ["token-2"]  # the attempt that got through used the second fetch, not the first


@pytest.mark.anyio
async def test_async_each_handshake_attempt_fetches_a_fresh_token() -> None:
    camera = FakeWsCamera()
    issued = iter(f"token-{n}" for n in range(10))
    camera.token = next(issued)
    original = camera._answer  # noqa: SLF001

    def answer(request: httpx.Request) -> httpx.Response:
        if request.url.path == TOKEN_PATH:
            camera.token = next(issued)
        return original(request)

    camera._answer = answer  # type: ignore[method-assign]  # noqa: SLF001
    camera._async = True  # noqa: SLF001
    async with AsyncDevice(
        "cam.test", credentials=("root", "pass"), transport=_flaky(camera), retry=RetryPolicy(attempts=2, backoff=0)
    ) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK, use_token=True):
            pass
    assert len([r for r in camera.requests if r.url.path == TOKEN_PATH]) == 2
    assert _tokens(camera) == ["token-2"]
