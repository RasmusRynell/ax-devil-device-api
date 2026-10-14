"""Required parts of events/Data Hub messages raise instead of defaulting; unread messages are bounded by bytes too."""

from __future__ import annotations

from typing import Any

import pytest
from ws_fake import FakeSocket, FakeWsCamera, notify

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventsCodec
from ax_devil_device_api.errors import ConfigurationError, ResponseFormatError

QUICK = Heartbeat(None)


def _events(notification: Any = None, params: Any = None, **override: Any) -> dict[str, Any]:
    body = {"notification": {"topic": "t", "timestamp": 1639385866198, "message": {"source": {}, "key": {}, "data": {}}}}
    message: dict[str, Any] = {"method": "events:notify", "params": body}
    if notification is not None:
        body["notification"] = notification
    if params is not None:
        message["params"] = params
    message.update(override)
    return message


@pytest.mark.parametrize(
    "message",
    [
        _events(params="x"),
        _events(params={}),
        _events(notification="x"),
        _events(notification={"topic": "t"}),  # no message
        _events(notification={"topic": "t", "message": []}),
        _events(notification={"topic": "t", "message": "x"}),
        _events(notification={"topic": "t", "message": {"data": []}}),
        _events(notification={"topic": "t", "message": {"source": "x"}}),
        _events(notification={"topic": 5, "message": {}}),
    ],
)
def test_events_notify_with_a_missing_or_wrongly_typed_required_part_raises(message: dict[str, Any]) -> None:
    with pytest.raises(ResponseFormatError):
        EventsCodec().classify(message)


def test_events_optional_parts_keep_their_defaults() -> None:
    note = EventsCodec().classify(_events(notification={"topic": "t", "message": {}}))
    assert note is not None
    event = note.item  # type: ignore[union-attr]
    assert event.topic == "t" and event.timestamp is None and event.source == {} and event.key == {} and event.data == {}


@pytest.mark.parametrize("bad", [None, "x", [], 5, {"code": 1}, {"message": "m"}, {"code": True, "message": "m"}, {"code": 1, "message": 5}])
def test_a_reply_error_needs_a_code_and_a_message(bad: Any) -> None:
    with pytest.raises(ResponseFormatError):
        EventsCodec().classify({"context": "c1", "error": bad})
    with pytest.raises(ResponseFormatError):
        DataHubCodec().classify({"jsonrpc": "2.0", "id": "1", "error": bad})


def test_a_well_formed_reply_error_still_parses() -> None:
    reply = EventsCodec().classify({"context": "c1", "error": {"code": 2104, "message": "bad"}})
    assert reply is not None and reply.error.code == 2104  # type: ignore[union-attr]


@pytest.mark.parametrize("params", [None, "x", [], 5])
def test_data_hub_sample_params_must_be_an_object(params: Any) -> None:
    with pytest.raises(ResponseFormatError):
        DataHubCodec().classify({"jsonrpc": "2.0", "method": "data-hub_v1:topicSample", "params": params})


# -- the unread-bytes budget -------------------------------------------------------------------------------------------

BUDGET = 4 * 1024 * 1024
BLOB = "x" * (1024 * 1024)
FRAMES = 12


def _flood_then_reply(socket: FakeSocket, message: Any) -> None:
    if message["method"] == "flood":
        for n in range(FRAMES):
            socket.push(notify(f"t/{n}", blob=BLOB))
        socket.push({"apiVersion": "1.0", "context": message["context"], "method": "flood", "data": {"done": True}})


def test_sync_large_frames_without_a_consumer_stay_within_the_byte_budget_and_the_reply_arrives() -> None:
    camera = FakeWsCamera(handler=_flood_then_reply)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            session._core.max_unread_bytes = BUDGET  # noqa: SLF001
            assert session.request("flood", {}, timeout=30) == {"done": True}
            core = session._core  # noqa: SLF001
            assert core.pending_bytes <= BUDGET and len(core.pending) <= 4
            assert session.dropped_notifications >= FRAMES - 4
            kept = len(core.pending)
            assert session.receive(timeout=1)["params"]["notification"]["topic"] == f"t/{FRAMES - kept}"  # the newest are kept


@pytest.mark.anyio
async def test_async_large_frames_without_a_consumer_stay_within_the_byte_budget_and_the_reply_arrives() -> None:
    camera = FakeWsCamera(handler=_flood_then_reply)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            session._core.max_unread_bytes = BUDGET  # noqa: SLF001
            assert await session.request("flood", {}, timeout=30) == {"done": True}
            core = session._core  # noqa: SLF001
            assert core.pending_bytes <= BUDGET and len(core.pending) <= 4
            assert session.dropped_notifications >= FRAMES - 4


def test_the_byte_budget_default_is_validated_and_generous() -> None:
    from ax_devil_device_api._runtime.ws import MAX_UNREAD_BYTES
    from ax_devil_device_api._validate import positive_int

    assert MAX_UNREAD_BYTES == 64 * 1024 * 1024
    with pytest.raises(ConfigurationError):
        positive_int("max_unread_bytes", 1.5)
