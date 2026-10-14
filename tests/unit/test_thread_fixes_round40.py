"""Required parts of events/Data Hub messages raise instead of defaulting; unread messages are bounded by bytes too."""

from __future__ import annotations

from typing import Any

import pytest

from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventsCodec
from ax_devil_device_api.errors import ResponseFormatError

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
