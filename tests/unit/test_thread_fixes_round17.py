"""A JSON null message is delivered; a known firmware below the minimum is NO even when discovery failed."""

from __future__ import annotations

import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device, Support
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.apis.scene_profile import SceneProfileApi
from ax_devil_device_api.errors import ReadTimeout
from ax_devil_device_api.testing import MockCamera

QUICK = Heartbeat(None)


def test_json_null_message_is_delivered_not_dropped() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].push(None)
            camera.sockets[0].push({"after": 1})
            assert session.receive(timeout=3) is None  # a delivered None, not a ReadTimeout
            assert session.receive(timeout=3) == {"after": 1}
            with pytest.raises(ReadTimeout):
                session.receive(timeout=0.1)  # nothing left: that is the only timeout


@pytest.mark.anyio
async def test_async_json_null_message_is_delivered_not_dropped() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].push(None)
            assert await session.receive(timeout=3) is None
            with pytest.raises(ReadTimeout):
                await session.receive(timeout=0.1)


def test_old_firmware_is_no_even_when_discovery_failed() -> None:
    camera = MockCamera()  # discovery endpoints answer 404: the probes fail
    camera.identity(firmware="5.50.1")
    with camera.device() as dev:
        result = dev.supports(SceneProfileApi)  # requires 6.25
    assert result.status is Support.NO and "5.50.1" in result.reason


def test_failed_discovery_with_enough_firmware_stays_unknown() -> None:
    camera = MockCamera()
    camera.identity(firmware="11.0.0")
    with camera.device() as dev:
        assert dev.supports(SceneProfileApi).status is Support.UNKNOWN
