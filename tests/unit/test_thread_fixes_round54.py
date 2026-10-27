"""Discovery alternatives are all evaluated; identity refresh invalidates on a different device; the token is fetched
after a stream slot is held."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from ax_devil_device_api import Support
from ax_devil_device_api._protocols.base import AcapDiscovery, ApiDiscovery, ApiInfo, Family, ParamDiscovery
from ax_devil_device_api._runtime.capabilities import Advertised, Capabilities, decide_support
from ax_devil_device_api.testing import MockCamera


def _caps(**kw: Any) -> Capabilities:
    base: dict[str, Any] = {"classic_apis": None, "dca_apis": None, "properties": None, "errors": {}, "observed_at": datetime.now(UTC)}
    return Capabilities(**{**base, **kw})


def _info(*discovery: Any, major: int | None = 1) -> ApiInfo:
    return ApiInfo(id="basic-device-info", name="b", family=Family.JSONRPC, major=major, discovery=discovery)


MARKERS = (ApiDiscovery("basic-device-info"), ParamDiscovery("Properties.API.Basic.Info", "yes"))
GROUP = frozenset({"Properties.API"})


# -- B2 ---------------------------------------------------------------------------------------------------------------------


def test_an_incompatible_classic_version_plus_a_satisfied_property_is_yes() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties={"Properties.API.Basic.Info": "yes"}, property_groups=GROUP)
    result = decide_support(_info(*MARKERS), caps)
    assert result.status is Support.YES and "parameter" in result.reason


def test_the_order_of_the_alternatives_does_not_matter() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties={"Properties.API.Basic.Info": "yes"}, property_groups=GROUP)
    assert decide_support(_info(*reversed(MARKERS)), caps).status is Support.YES


def test_an_incompatible_version_and_every_other_alternative_saying_no_is_no_with_the_version_reason() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties={"Properties.API.Other": "x"}, property_groups=GROUP)
    result = decide_support(_info(*MARKERS), caps)
    assert result.status is Support.NO and "version 2.0" in result.reason


def test_an_incompatible_version_and_an_alternative_that_could_not_be_evaluated_is_unknown() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 properties=None, errors={"properties": "ReadTimeout: slow"})
    result = decide_support(_info(*MARKERS), caps)
    assert result.status is Support.UNKNOWN and any("slow" in error for error in result.errors)


def test_an_incompatible_version_then_an_installed_application_is_yes() -> None:
    caps = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))},
                 applications={"Thing": "1.0"})
    assert decide_support(_info(ApiDiscovery("basic-device-info"), AcapDiscovery("thing")), caps).status is Support.YES


def test_a_fitting_version_is_still_yes_and_a_lone_incompatible_version_is_still_no() -> None:
    fits = _caps(classic_apis={"basic-device-info": "1.0"}, classic_versions={"basic-device-info": Advertised(("1.0",))})
    assert decide_support(_info(ApiDiscovery("basic-device-info")), fits).status is Support.YES
    lone = _caps(classic_apis={"basic-device-info": "2.0"}, classic_versions={"basic-device-info": Advertised(("2.0",))})
    assert decide_support(_info(ApiDiscovery("basic-device-info")), lone).status is Support.NO


# -- B3 ---------------------------------------------------------------------------------------------------------------------

MQTT = "/axis-cgi/mqtt/client.cgi"


def _warm(camera: MockCamera) -> None:
    camera.identity(firmware="11.9.0", serial="AAA", ProdNbr="Q1656")
    camera.api_list({"mqtt-client": "1.0"})


@pytest.mark.parametrize(
    ("changed", "cleared"),
    [
        ({}, False),
        ({"serial": "BBB"}, True),
        ({"ProdNbr": "Q1659"}, True),
        ({"firmware": "12.0.0"}, True),
    ],
    ids=["same device", "other serial, same firmware", "other product number", "other firmware"],
)
def test_identity_refresh_drops_the_caches_when_the_unit_changes(changed: dict[str, str], cleared: bool) -> None:
    camera = MockCamera()
    _warm(camera)
    with camera.device() as dev:
        dev.identity()
        dev.capabilities()
        assert dev._state.get("classic_apis") is not None  # noqa: SLF001
        camera.identity(**{"firmware": "11.9.0", "serial": "AAA", "ProdNbr": "Q1656", **changed})
        dev.identity(refresh=True)
        assert (dev._state.get("classic_apis") is None) is cleared  # noqa: SLF001
        assert dev.identity().serial_number == changed.get("serial", "AAA")  # the new identity itself is kept


@pytest.mark.anyio
@pytest.mark.parametrize("changed", [{}, {"serial": "BBB"}, {"ProdNbr": "Q1659"}], ids=["same", "serial", "product number"])
async def test_async_identity_refresh_drops_the_caches_when_the_unit_changes(changed: dict[str, str]) -> None:
    camera = MockCamera()
    _warm(camera)
    async with camera.async_device() as dev:
        await dev.identity()
        await dev.capabilities()
        assert dev._state.get("classic_apis") is not None  # noqa: SLF001
        camera.identity(**{"firmware": "11.9.0", "serial": "AAA", "ProdNbr": "Q1656", **changed})
        await dev.identity(refresh=True)
        assert (dev._state.get("classic_apis") is None) is bool(changed)  # noqa: SLF001


# -- C1: the wssession token is fetched after the stream slot is held --------------------------------------------------------

import asyncio  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402

import httpx  # noqa: E402
from ws_fake import FakeWsCamera  # noqa: E402

from ax_devil_device_api import AsyncDevice, Device, errors  # noqa: E402
from ax_devil_device_api._http.options import Heartbeat  # noqa: E402
from ax_devil_device_api._runtime.ws import EVENTS  # noqa: E402

TOKEN_PATH = "/axis-cgi/wssession.cgi"
TOKEN_LIFETIME = 15.0


class _Clock:
    """The camera's notion of time; the test moves it, nothing sleeps for the token's lifetime."""

    def __init__(self) -> None:
        self.now = 0.0


def _expiring_camera(clock: _Clock) -> FakeWsCamera:
    """A camera whose wssession tokens are valid for 15 (injected) seconds; a handshake with an old token is refused."""
    camera = FakeWsCamera()
    issued: dict[str, float] = {}
    original = camera._answer  # noqa: SLF001

    def answer(request: httpx.Request) -> httpx.Response:
        if request.url.path == TOKEN_PATH:
            token = f"token-{len(issued)}"
            issued[token] = clock.now
            camera.token = token
        elif request.headers.get("upgrade") == "websocket" and "wssession" in request.url.params:
            if clock.now - issued[request.url.params["wssession"]] > TOKEN_LIFETIME:
                camera.requests.append(request)
                return httpx.Response(401, text="token expired")
        return original(request)

    camera._answer = answer  # type: ignore[method-assign]  # noqa: SLF001
    return camera


def test_sync_the_token_is_fetched_after_a_busy_slot_frees_up() -> None:
    clock = _Clock()
    camera = _expiring_camera(clock)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=1) as dev:
        holder = dev.connect_session(EVENTS, heartbeat=Heartbeat(None))
        first = holder.__enter__()
        slots = dev._transport._stream_slots  # noqa: SLF001

        def release_late() -> None:
            deadline = time.monotonic() + 10
            while not slots._cond._waiters and time.monotonic() < deadline:  # type: ignore[attr-defined]  # noqa: SLF001
                time.sleep(0.01)  # until the second connect is waiting for the slot
            clock.now += 20  # longer than the token lives
            holder.__exit__(None, None, None)

        thread = threading.Thread(target=release_late)
        thread.start()
        try:
            with dev.connect_session(EVENTS, heartbeat=Heartbeat(None), use_token=True):
                pass
        finally:
            thread.join(timeout=10)
        assert first is not None
    assert len([r for r in camera.requests if r.url.path == TOKEN_PATH]) == 1
    assert len(camera.sockets) == 2, "the second handshake was accepted with a token fetched after the wait"


@pytest.mark.anyio
async def test_async_the_token_is_fetched_after_a_busy_slot_frees_up() -> None:
    clock = _Clock()
    camera = _expiring_camera(clock)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport(), max_streams=1) as dev:
        ready, release = asyncio.Event(), asyncio.Event()

        async def hold() -> None:  # a session is entered and left by the same task
            async with dev.connect_session(EVENTS, heartbeat=Heartbeat(None)):
                ready.set()
                await release.wait()

        holder = asyncio.create_task(hold())
        await ready.wait()
        _, slots = dev._transport._semaphores()  # noqa: SLF001

        async def release_late() -> None:
            for _ in range(1000):
                if slots._waiters:  # type: ignore[attr-defined]  # noqa: SLF001
                    break
                await asyncio.sleep(0.01)  # until the second connect is waiting for the slot
            clock.now += 20  # longer than the token lives
            release.set()

        task = asyncio.create_task(release_late())
        try:
            async with dev.connect_session(EVENTS, heartbeat=Heartbeat(None), use_token=True):
                pass
        finally:
            await task
            await holder
    assert len([r for r in camera.requests if r.url.path == TOKEN_PATH]) == 1
    assert len(camera.sockets) == 2


def test_a_failed_token_fetch_is_raised_as_it_was_not_as_a_handshake_failure() -> None:
    camera = FakeWsCamera()
    original = camera._answer  # noqa: SLF001

    def answer(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="no token") if request.url.path == TOKEN_PATH else original(request)

    camera._answer = answer  # type: ignore[method-assign]  # noqa: SLF001
    events: list[dict[str, Any]] = []
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), on_response=events.append) as dev:
        with pytest.raises(errors.DeviceError):
            with dev.connect_session(EVENTS, heartbeat=Heartbeat(None), use_token=True):
                pass
    assert not camera.ws_requests, "no handshake was attempted"
    assert len(events) == 1, "the failed token request is recorded once, not again as a handshake attempt"
