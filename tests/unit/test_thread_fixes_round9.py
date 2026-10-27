"""Codex round 9: no placeholder after a failed tolerant pass, session tracking ends when the reader dies,
mutated nested models in Data Hub subscription mappings are revalidated."""

from __future__ import annotations

import time
from typing import Any, Literal

import anyio
import pytest
from pydantic import ValidationError
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._protocols.base import ApiInfo, Family, Operation, parse_result
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api._runtime.ws_codecs import datahub_setup
from ax_devil_device_api.errors import ResponseFormatError, SessionClosed

QUICK = Heartbeat(None)
INFO = ApiInfo(id="t", name="T", family=Family.CGI)


def _op(result: Any) -> Operation[Any]:
    return Operation(INFO, "get", binding=object(), result=result)


def test_failed_tolerant_pass_raises_instead_of_returning_a_placeholder() -> None:
    with pytest.raises(ResponseFormatError):
        parse_result(_op(list[Literal["A", "B"]]), ["NEW_SERVICE", 7])
    with pytest.raises(ResponseFormatError):
        parse_result(_op(dict[str, Literal["a"]]), {"x": "new", "y": 7})
    assert parse_result(_op(list[Literal["A", "B"]]), ["NEW_SERVICE", "A"]) == ["NEW_SERVICE", "A"]


def test_mutated_nested_models_in_subscription_mappings_are_revalidated() -> None:
    from ax_devil_device_api.apis.device_data_hub_ws import Filter, StartFrom

    flt = Filter(topics=["t"])
    flt.topics.clear()
    with pytest.raises(ValidationError):
        datahub_setup({"subscriptions": [{"filters": [flt]}]})
    start = StartFrom(position="new")
    start.position = "sideways"  # type: ignore[assignment]
    with pytest.raises(ValidationError):
        datahub_setup({"subscriptions": [{"filters": [{"topics": ["t"]}], "startFrom": start}]})


def _device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


def test_device_close_ends_tracking_before_anyone_reads_it() -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK):
            camera.sockets[0].close()
            time.sleep(0.3)  # the background reader sees the close frame
            with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None  # the dead session is not an open one


def test_send_after_device_close_ends_tracking() -> None:
    camera = FakeWsCamera()
    with _device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close()
            with pytest.raises(SessionClosed):
                for _ in range(300):
                    session.send({"x": 1})
                    time.sleep(0.01)
            assert dev._ledger.live(EVENTS.key) == 0  # noqa: SLF001


@pytest.mark.anyio
async def test_async_device_close_ends_tracking_before_anyone_reads_it() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK):
            camera.sockets[0].close()
            await anyio.sleep(0.3)
            async with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
                assert again.gap is not None


@pytest.mark.anyio
async def test_async_send_after_device_close_ends_tracking() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close()
            with pytest.raises(SessionClosed):
                for _ in range(300):
                    await session.send({"x": 1})
                    await anyio.sleep(0.01)
            assert dev._ledger.live(EVENTS.key) == 0  # noqa: SLF001
