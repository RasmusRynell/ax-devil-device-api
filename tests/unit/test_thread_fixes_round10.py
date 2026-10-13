"""Bad event timestamps stay inside the codec; a raising on_response hook does not leak WebSocket slots."""

from __future__ import annotations

import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventNotification, EventsCodec

QUICK = Heartbeat(None)


def _event(millis: object) -> dict[str, object]:
    return {
        "method": "events:notify",
        "params": {"notification": {"topic": "t", "timestamp": millis, "message": {"data": {}}}},
    }


@pytest.mark.parametrize("millis", [1e300, float("inf"), float("-inf"), float("nan"), 10**30, -(10**30), True])
def test_bad_event_timestamps_leave_the_timestamp_unset(millis: object) -> None:
    note = EventsCodec().classify(_event(millis))
    assert note is not None
    event = note.item  # type: ignore[union-attr]
    assert isinstance(event, EventNotification) and event.timestamp is None and event.topic == "t"


def test_good_event_timestamp_still_parses() -> None:
    note = EventsCodec().classify(_event(1_600_000_000_000))
    assert note.item.timestamp.year == 2020  # type: ignore[union-attr]


@pytest.mark.parametrize("text", ["9999-12-31T23:59:59-23:59", "not a time", "0000-00-00T00:00:00Z"])
def test_bad_data_hub_timestamps_leave_the_timestamp_unset(text: str) -> None:
    message = {"method": "data-hub_v1:topicSample", "params": {"topic": "t", "subscriptionId": "s", "timestamp": text}}
    note = DataHubCodec().classify(message)
    assert note is not None  # classified without raising


def test_raising_on_response_hook_does_not_leak_stream_slots() -> None:
    camera = FakeWsCamera()

    def hook(record: object) -> None:
        raise RuntimeError("hook failed")

    with Device(
        "cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=1, on_response=hook
    ) as dev:
        for _ in range(4):  # more than max_streams
            with pytest.raises(RuntimeError, match="hook failed"):
                with dev.connect_session(EVENTS, heartbeat=QUICK):
                    pass
    assert camera.streams and all(s.closed for s in camera.streams)


@pytest.mark.anyio
async def test_async_raising_on_response_hook_does_not_leak_stream_slots() -> None:
    camera = FakeWsCamera()

    def hook(record: object) -> None:
        raise RuntimeError("hook failed")

    async with AsyncDevice(
        "cam.test", credentials=("root", "pass"), transport=camera.async_transport(), max_streams=1, on_response=hook
    ) as dev:
        for _ in range(4):
            with pytest.raises(RuntimeError, match="hook failed"):
                async with dev.connect_session(EVENTS, heartbeat=QUICK):
                    pass
    assert camera.streams and all(s.closed for s in camera.streams)
