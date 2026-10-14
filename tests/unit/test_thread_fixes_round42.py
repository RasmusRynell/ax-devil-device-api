"""A malformed correlated reply completes its request; a malformed /config/discover entry makes only that API unknown."""

from __future__ import annotations

from typing import Any

import anyio
import pytest
from ws_fake import FakeSocket, FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import DATA_HUB, EVENTS
from ax_devil_device_api.errors import ResponseFormatError

QUICK = Heartbeat(None)


def _events_handler(socket: FakeSocket, message: Any) -> None:
    socket.push({"apiVersion": "1.0", "context": message["context"], "method": message["method"], "error": "not an object"})


def _hub_handler(socket: FakeSocket, message: Any) -> None:
    socket.push({"jsonrpc": "2.0", "id": message["id"], "error": {"code": "7"}})  # no message, wrong code type... malformed


# -- N ---------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(("spec", "handler"), [(EVENTS, _events_handler), (DATA_HUB, _hub_handler)], ids=["events", "datahub"])
def test_sync_malformed_reply_completes_the_pending_request(spec: Any, handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(spec, heartbeat=QUICK) as session:
            with pytest.raises(ResponseFormatError):  # not a ReadTimeout after the full timeout
                session.request("m", {}, timeout=5)


@pytest.mark.anyio
@pytest.mark.parametrize(("spec", "handler"), [(EVENTS, _events_handler), (DATA_HUB, _hub_handler)], ids=["events", "datahub"])
async def test_async_malformed_reply_completes_the_pending_request(spec: Any, handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(spec, heartbeat=QUICK) as session:
            with anyio.fail_after(4), pytest.raises(ResponseFormatError):
                await session.request("m", {}, timeout=5)


def test_an_unmatched_malformed_reply_is_still_queued_as_before() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].push({"context": "someone-else", "error": "bad"})
            assert session.receive(timeout=3)["context"] == "someone-else"
