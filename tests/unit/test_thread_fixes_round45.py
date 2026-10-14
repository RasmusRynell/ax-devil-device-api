"""Correlated WebSocket messages always resolve their waiter; capability values are plain data; identity values are text."""

from __future__ import annotations

from typing import Any

import anyio
import pytest
from ws_fake import FakeSocket, FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import DATA_HUB, EVENTS
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventsCodec
from ax_devil_device_api.errors import ResponseFormatError

QUICK = Heartbeat(None)
DISCOVERY = "/axis-cgi/apidiscovery.cgi"


# -- 1: a correlated message with neither result nor error ---------------------------------------------------------------


def test_the_codecs_raise_for_a_correlated_message_with_neither_result_nor_error() -> None:
    with pytest.raises(ResponseFormatError):
        EventsCodec().classify({"apiVersion": "1.0", "context": "ax-1"})
    with pytest.raises(ResponseFormatError):
        DataHubCodec().classify({"jsonrpc": "2.0", "id": "ax-1"})
    assert EventsCodec().classify({"apiVersion": "1.0"}) is None  # not correlated: still ignorable
    assert DataHubCodec().classify({"jsonrpc": "2.0"}) is None


def _empty_events(socket: FakeSocket, message: Any) -> None:
    socket.push({"apiVersion": "1.0", "context": message["context"], "method": message["method"]})


def _empty_hub(socket: FakeSocket, message: Any) -> None:
    socket.push({"jsonrpc": "2.0", "id": message["id"]})


@pytest.mark.parametrize(("spec", "handler"), [(EVENTS, _empty_events), (DATA_HUB, _empty_hub)], ids=["events", "datahub"])
def test_sync_request_completes_at_once_for_an_empty_reply(spec: Any, handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(spec, heartbeat=QUICK) as session:
            with pytest.raises(ResponseFormatError):  # not a ReadTimeout after the full timeout
                session.request("m", {}, timeout=5)


@pytest.mark.anyio
@pytest.mark.parametrize(("spec", "handler"), [(EVENTS, _empty_events), (DATA_HUB, _empty_hub)], ids=["events", "datahub"])
async def test_async_request_completes_at_once_for_an_empty_reply(spec: Any, handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(spec, heartbeat=QUICK) as session:
            with anyio.fail_after(4), pytest.raises(ResponseFormatError):
                await session.request("m", {}, timeout=5)
