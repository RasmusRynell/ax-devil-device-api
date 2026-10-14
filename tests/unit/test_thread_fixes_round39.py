"""Required fields of a topicSample / events:notify raise ResponseFormatError; nothing known is silently dropped."""

from __future__ import annotations

from typing import Any

import pytest
from ws_fake import notify

from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventNotification, EventsCodec, TopicSample
from ax_devil_device_api.errors import ResponseFormatError


def _sample(**override: Any) -> dict[str, Any]:
    params: dict[str, Any] = {
        "topic": "t", "subscriptionId": "s", "instance": {"k": "v"}, "data": {"x": 1}, "timestamp": "2024-01-01T00:00:00Z",
    }
    params.update(override)
    return {"jsonrpc": "2.0", "method": "data-hub_v1:topicSample", "params": {k: v for k, v in params.items() if v is not _MISSING}}


_MISSING = object()


@pytest.mark.parametrize("field", ["topic", "subscriptionId", "instance", "data", "timestamp"])
@pytest.mark.parametrize("bad", [_MISSING, None, 5, ["x"], True])
def test_a_missing_or_wrongly_typed_required_field_raises(field: str, bad: Any) -> None:
    with pytest.raises(ResponseFormatError, match=field):
        DataHubCodec().classify(_sample(**{field: bad}))


def test_a_valid_sample_and_the_is_historical_semantics_are_unchanged() -> None:
    note = DataHubCodec().classify(_sample())
    assert note is not None and isinstance(note.item, TopicSample)  # type: ignore[union-attr]
    assert note.item.topic == "t" and note.item.subscription_id == "s" and note.item.is_historical is False  # type: ignore[union-attr]
    assert note.item.timestamp is not None  # type: ignore[union-attr]
    flagged = DataHubCodec().classify(_sample(isHistorical=True))
    assert flagged is not None and flagged.item.is_historical is True  # type: ignore[union-attr]
    with pytest.raises(ResponseFormatError, match="isHistorical"):
        DataHubCodec().classify(_sample(isHistorical="false"))


def test_extra_fields_in_a_sample_are_ignored() -> None:
    assert DataHubCodec().classify({**_sample(), "params": {**_sample()["params"], "futureField": [1]}}) is not None


def test_unparsable_timestamp_text_leaves_the_timestamp_unset() -> None:
    note = DataHubCodec().classify(_sample(timestamp="not a time"))
    assert note is not None and note.item.timestamp is None  # type: ignore[union-attr]


@pytest.mark.parametrize(
    "message",
    [
        {"method": "events:notify"},
        {"method": "events:notify", "params": {}},
        {"method": "events:notify", "params": {"notification": "x"}},
        {"method": "events:notify", "params": {"notification": {"message": {}}}},
        {"method": "events:notify", "params": {"notification": {"topic": 5}}},
    ],
)
def test_events_notify_without_a_topic_raises(message: dict[str, Any]) -> None:
    with pytest.raises(ResponseFormatError):
        EventsCodec().classify(message)


def test_a_valid_event_still_parses() -> None:
    note = EventsCodec().classify(notify(state="0"))
    assert note is not None and isinstance(note.item, EventNotification)  # type: ignore[union-attr]
