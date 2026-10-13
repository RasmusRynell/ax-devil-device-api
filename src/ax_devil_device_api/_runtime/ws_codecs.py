"""Message codecs for the WebSocket APIs (sans-IO).

A codec builds request messages and classifies incoming ones. It never
touches a socket. These belong with the planned ``_protocols/ws`` family and
can move there unchanged; they live in ``_runtime`` until that module exists.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

from ..errors import ApiAccessDenied, ApiError, ApiUnavailable, ErrorKind

JsonObject = Mapping[str, Any]


@dataclass(frozen=True)
class WsError:
    code: int | str | None
    message: str
    data: Any = None


@dataclass(frozen=True)
class Reply:
    """The answer to a request sent with ``request_id``."""

    request_id: str | None
    result: Any = None
    error: WsError | None = None


@dataclass(frozen=True)
class Notification:
    """A parsed server-initiated message (event, data sample)."""

    item: Any


class WsCodec(Protocol):
    api_id: str
    """API Discovery id; used in error messages."""

    def encode_request(self, method: str, params: JsonObject | None, request_id: str) -> dict[str, Any]: ...

    def classify(self, message: Any) -> Reply | Notification | None:
        """``None`` for anything that is neither a reply nor a known notification."""
        ...

    def error_kind(self, code: int | str | None) -> ErrorKind | None: ...


def api_error(codec: WsCodec, method: str, error: WsError) -> ApiError:
    kind = codec.error_kind(error.code)
    cls = {"access_denied": ApiAccessDenied, "unavailable": ApiUnavailable}.get(kind or "", ApiError)
    return cls(codec.api_id, method, error.code, error.message, kind=kind, details=error.data)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _error(value: Any) -> WsError:
    err = _mapping(value)
    return WsError(err.get("code"), str(err.get("message", "")), err.get("data"))


# ---------------------------------------------------------------------------
# Event streaming over WebSocket (``/vapix/ws-data-stream?sources=events``)


@dataclass(frozen=True)
class EventFilter:
    """One subscription. Give a topic filter, a content filter, or both."""

    topic_filter: str | None = None
    content_filter: str | None = None

    def __post_init__(self) -> None:
        if self.topic_filter is None and self.content_filter is None:
            raise ValueError("EventFilter needs a topic_filter or a content_filter")

    def to_wire(self) -> dict[str, str]:
        wire: dict[str, str] = {}
        if self.topic_filter is not None:
            wire["topicFilter"] = self.topic_filter
        if self.content_filter is not None:
            wire["contentFilter"] = self.content_filter
        return wire


@dataclass(frozen=True)
class EventNotification:
    topic: str
    timestamp: datetime | None
    """UTC; the device sends epoch milliseconds."""
    source: Mapping[str, Any] = field(default_factory=dict)
    key: Mapping[str, Any] = field(default_factory=dict)
    data: Mapping[str, Any] = field(default_factory=dict)
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)


class EventsCodec:
    """JSON-RPC style messages of the event stream: ``context`` correlates, ``events:notify`` delivers."""

    api_id = "event-streaming-over-websocket"
    api_version = "1.0"
    notify_method = "events:notify"

    def encode_request(self, method: str, params: JsonObject | None, request_id: str) -> dict[str, Any]:
        message: dict[str, Any] = {"apiVersion": self.api_version, "context": request_id, "method": method}
        if params is not None:
            message["params"] = dict(params)
        return message

    def classify(self, message: Any) -> Reply | Notification | None:
        if not isinstance(message, Mapping):
            return None
        method = message.get("method")
        if method == self.notify_method:
            return self._notification(message)
        if "error" in message:
            return Reply(_ctx(message), error=_error(message["error"]))
        if "data" in message:
            return Reply(_ctx(message), result=message["data"])
        return None

    @staticmethod
    def _notification(message: Mapping[str, Any]) -> Notification | None:
        raw = _mapping(_mapping(message.get("params")).get("notification"))
        topic = raw.get("topic")
        if not isinstance(topic, str):
            return None
        body = _mapping(raw.get("message"))
        millis = raw.get("timestamp")
        stamp = datetime.fromtimestamp(millis / 1000, tz=UTC) if isinstance(millis, (int, float)) else None
        return Notification(EventNotification(topic, stamp, _mapping(body.get("source")), _mapping(body.get("key")), _mapping(body.get("data")), raw))

    def error_kind(self, code: int | str | None) -> ErrorKind | None:
        return None


def _ctx(message: Mapping[str, Any]) -> str | None:
    value = message.get("context")
    return None if value is None else str(value)


def events_setup(options: Mapping[str, Any]) -> list[tuple[str, JsonObject | None]]:
    """Requests to send right after connecting: ``events:configure`` when filters are given."""
    unknown = set(options) - {"event_filter_list"}
    if unknown:
        raise TypeError(f"unexpected arguments for the event session: {sorted(unknown)}")
    filters = options.get("event_filter_list")
    if filters is None:
        return []
    wire = [f.to_wire() if isinstance(f, EventFilter) else dict(f) for f in filters]
    return [("events:configure", {"eventFilterList": wire})]


# ---------------------------------------------------------------------------
# Device Data Hub (``/vapix/ws/v1?apis=data-hub``)


@dataclass(frozen=True)
class TopicSample:
    subscription_id: str
    topic: str
    instance: Mapping[str, Any]
    data: Mapping[str, Any]
    timestamp: datetime | None
    is_historical: bool
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)


_DATAHUB_KINDS: dict[int | str, ErrorKind] = {
    -32700: "invalid_argument",
    -32600: "invalid_argument",
    -32601: "unsupported",
    -32602: "invalid_argument",
    -32603: "internal",
    2100: "unsupported",
    2105: "access_denied",
    1200: "not_found",
}


class DataHubCodec:
    """JSON-RPC 2.0 messages of Device Data Hub: ``id`` correlates, ``data-hub_v1:topicSample`` delivers."""

    api_id = "datahub-streaming-over-websocket"
    sample_method = "data-hub_v1:topicSample"

    def encode_request(self, method: str, params: JsonObject | None, request_id: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": dict(params or {})}

    def classify(self, message: Any) -> Reply | Notification | None:
        if not isinstance(message, Mapping):
            return None
        if message.get("method") == self.sample_method:
            return self._sample(_mapping(message.get("params")))
        identifier = message.get("id")
        rid = None if identifier is None else str(identifier)
        if "error" in message:
            return Reply(rid, error=_error(message["error"]))
        if "result" in message:
            return Reply(rid, result=message["result"])
        return None

    @staticmethod
    def _sample(params: Mapping[str, Any]) -> Notification | None:
        topic, subscription = params.get("topic"), params.get("subscriptionId")
        if not isinstance(topic, str) or not isinstance(subscription, str):
            return None
        stamp: datetime | None = None
        text = params.get("timestamp")
        if isinstance(text, str):
            try:
                stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                stamp = None
        return Notification(
            TopicSample(
                subscription, topic, _mapping(params.get("instance")), _mapping(params.get("data")), stamp,
                bool(params.get("isHistorical", False)), params,
            )
        )

    def error_kind(self, code: int | str | None) -> ErrorKind | None:
        return None if code is None else _DATAHUB_KINDS.get(code)


def datahub_setup(options: Mapping[str, Any]) -> list[tuple[str, JsonObject | None]]:
    """``subscriptions``: a sequence of ``{"subscriptionId": ..., "filters": [...], ...}`` objects sent as ``data-hub_v1:subscribe``."""
    unknown = set(options) - {"subscriptions"}
    if unknown:
        raise TypeError(f"unexpected arguments for the data hub session: {sorted(unknown)}")
    subscriptions: Sequence[JsonObject] = options.get("subscriptions") or ()
    return [("data-hub_v1:subscribe", dict(sub)) for sub in subscriptions]
