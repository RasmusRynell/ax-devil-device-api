"""A peer that answers the upgrade with a bare 101 and then is not a WebSocket fails cleanly with a library error."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from ws_fake import FakeSocket, FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device, errors
from ax_devil_device_api._http.options import Heartbeat, RequestOptions
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api._runtime.ws_codecs import EventFilter

FILTERS = [EventFilter(topic_filter="tns1:PTZController/tnsaxis:PTZReady")]
QUICK = Heartbeat(None)
OPTIONS = RequestOptions(timeout=2)


def _garbage(socket: FakeSocket, message: Any) -> None:
    socket._emit(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html>not a websocket</html>")  # noqa: SLF001


def _drop(socket: FakeSocket, message: Any) -> None:
    socket.drop()


@pytest.mark.parametrize("handler", [_garbage, _drop], ids=["non-websocket bytes", "closed"])
def test_sync_bare_101_fails_at_the_first_exchange_with_a_library_error(handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    dev = Device("cam.test", credentials=("root", "pass"), transport=camera.transport())
    with pytest.raises(errors.DeviceError):
        with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS, request_options=OPTIONS):
            pass


@pytest.mark.anyio
@pytest.mark.parametrize("handler", [_garbage, _drop], ids=["non-websocket bytes", "closed"])
async def test_async_bare_101_fails_at_the_first_exchange_with_a_library_error(handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    dev = AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport())
    async with dev:
        with pytest.raises(errors.DeviceError):
            async with asyncio.timeout(5):
                async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS, request_options=OPTIONS):
                    pass
