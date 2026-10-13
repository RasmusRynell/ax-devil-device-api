"""A JSON null WebSocket message is delivered; a known-old firmware beats an incomplete discovery."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from ws_fake import FakeWsCamera, events_handler

from ax_devil_device_api import AsyncDevice, Device, errors
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.capabilities import Capabilities, Support, decide_support
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.apis.scene_profile import AsyncSceneProfileApi, SceneProfileApi
from ax_devil_device_api.testing import MockCamera

QUICK = Heartbeat(None)


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


def _adevice(camera: FakeWsCamera) -> AsyncDevice:
    return AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport())


def test_json_null_message_is_delivered() -> None:
    camera = FakeWsCamera(handler=events_handler)
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        camera.sockets[0].push(None)
        assert session.receive(timeout=1) is None


def test_json_null_in_fragments_is_delivered_once() -> None:
    camera = FakeWsCamera(handler=events_handler)
    with _device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        camera.sockets[0].push_fragments("nu", "ll")
        assert session.receive(timeout=1) is None
        with pytest.raises(errors.ReadTimeout):
            session.receive(timeout=0.05)


@pytest.mark.anyio
async def test_async_json_null_message_is_delivered() -> None:
    camera = FakeWsCamera(handler=events_handler)
    async with _adevice(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        camera.sockets[0].push(None)
        assert await session.receive(timeout=1) is None


# -- firmware minimum with an incomplete discovery ---------------------------------


def _caps(firmware: str | None, **kw: Any) -> Capabilities:
    base: dict[str, Any] = dict(
        classic_apis=None, dca_apis=None, properties=None, firmware=firmware,
        errors={"classic_apis": "boom"}, observed_at=datetime.now(UTC),
    )
    return Capabilities(**{**base, **kw})


def test_old_firmware_is_no_even_when_discovery_failed() -> None:
    result = decide_support(SceneProfileApi.INFO, _caps("5.50"))
    assert result.status is Support.NO and "6.25" in result.reason


def test_failed_discovery_stays_unknown_when_firmware_is_new_or_unknown() -> None:
    assert decide_support(SceneProfileApi.INFO, _caps("6.25")).status is Support.UNKNOWN
    assert decide_support(SceneProfileApi.INFO, _caps(None)).status is Support.UNKNOWN
    assert decide_support(SceneProfileApi.INFO, _caps("garbage")).status is Support.UNKNOWN


def _failing_discovery(firmware: str) -> MockCamera:
    camera = MockCamera()
    camera.identity(firmware=firmware)  # no api list / param routes: every discovery probe fails
    return camera


def test_supports_is_no_on_old_firmware_when_probes_fail() -> None:
    with _failing_discovery("5.50").device() as dev:
        assert dev.supports(SceneProfileApi).status is Support.NO


@pytest.mark.anyio
async def test_async_supports_is_no_on_old_firmware_when_probes_fail() -> None:
    async with _failing_discovery("5.50").async_device() as dev:
        assert (await dev.supports(AsyncSceneProfileApi)).status is Support.NO
