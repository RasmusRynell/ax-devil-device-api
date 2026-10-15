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

from pydantic import ValidationError

from ..errors import ApiAccessDenied, ApiError, ApiUnavailable, ErrorKind, ResponseFormatError

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

    def correlation_id(self, message: Any) -> str | None:
        """The id a reply carries, read without any strict parsing (``None`` if it is not a reply)."""
        ...

    def error_kind(self, code: int | str | None) -> ErrorKind | None: ...


def api_error(codec: WsCodec, method: str, error: WsError) -> ApiError:
    kind = codec.error_kind(error.code)
    cls = {"access_denied": ApiAccessDenied, "unavailable": ApiUnavailable}.get(kind or "", ApiError)
    return cls(codec.api_id, method, error.code, error.message, kind=kind, details=error.data)


def _object(api: str, where: str, value: Any) -> Mapping[str, Any]:
    """A REQUIRED JSON object: missing or of another type is a malformed message, never an empty default."""
    if not isinstance(value, Mapping):
        raise ResponseFormatError(api, "receive", f"{where} must be an object, got {value!r}")
    return value


def _optional_object(api: str, where: str, value: Any) -> Mapping[str, Any]:
    """An optional JSON object: absent (or null) is empty, but a value of another type is malformed."""
    return {} if value is None else _object(api, where, value)


def _error(api: str, value: Any) -> WsError:
    """The error object of a failed reply: JSON-RPC requires an integer or text ``code`` and a text ``message``."""
    err = _object(api, "the error of a reply", value)
    code, message = err.get("code"), err.get("message")
    if isinstance(code, bool) or not isinstance(code, (int, str)) or not isinstance(message, str):
        raise ResponseFormatError(api, "receive", f"a reply error needs a code and a message, got {dict(err)!r}")
    return WsError(code, message, err.get("data"))


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
        for name in ("topic_filter", "content_filter"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"EventFilter.{name} must be a string, got {type(value).__name__}")

    @classmethod
    def from_wire(cls, data: Mapping[str, Any]) -> EventFilter:
        """Validate a plain ``{"topicFilter": ..., "contentFilter": ...}`` mapping."""
        unknown = sorted(str(k) for k in data if k not in ("topicFilter", "contentFilter"))
        if unknown:
            raise ValueError(f"unexpected event filter field(s): {', '.join(unknown)}")
        return cls(data.get("topicFilter"), data.get("contentFilter"))

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


_EVENTS_KINDS: dict[int | str, ErrorKind] = {
    1100: "internal",
    2100: "unsupported",
    2101: "invalid_argument",
    2102: "unsupported",
    2103: "invalid_argument",
    2104: "invalid_argument",
    2105: "access_denied",
    2106: "access_denied",
    2107: "invalid_argument",
}


class EventsCodec:
    """JSON-RPC style messages of the event stream: ``context`` correlates, ``events:notify`` delivers."""

    api_id = "event-streaming-over-websocket"
    api_version = "1.0"
    notify_method = "events:notify"

    def encode_request(self, method: str, params: JsonObject | None, request_id: str) -> dict[str, Any]:
        message: dict[str, Any] = {"apiVersion": self.api_version, "context": request_id, "method": method}
        if params is not None:
            message["params"] = _params(params)
        return message

    def correlation_id(self, message: Any) -> str | None:
        if not isinstance(message, Mapping) or message.get("method") == self.notify_method:
            return None
        return _ctx(message)

    def classify(self, message: Any) -> Reply | Notification | None:
        if not isinstance(message, Mapping):
            return None
        method = message.get("method")
        if method == self.notify_method:
            return self._notification(message)
        if "error" in message:
            return Reply(_ctx(message), error=_error(self.api_id, message["error"]))
        if "data" in message:
            return Reply(_ctx(message), result=message["data"])
        if _ctx(message) is not None:  # a correlated message must always resolve its waiter, never vanish
            raise ResponseFormatError(self.api_id, "receive", "a reply with neither data nor error")
        return None

    @staticmethod
    def _notification(message: Mapping[str, Any]) -> Notification | None:
        api = "event-streaming-over-websocket"
        params = _object(api, "events:notify params", message.get("params"))
        raw = _object(api, "events:notify notification", params.get("notification"))
        topic = raw.get("topic")
        if not isinstance(topic, str):
            raise ResponseFormatError(api, "receive", f"events:notify notification.topic must be text, got {topic!r}")
        body = _object(api, "events:notify notification.message", raw.get("message"))
        source, key, data = (_optional_object(api, f"notification.message.{name}", body.get(name)) for name in ("source", "key", "data"))
        return Notification(EventNotification(topic, _epoch_millis(raw.get("timestamp")), source, key, data, raw))

    def error_kind(self, code: int | str | None) -> ErrorKind | None:
        return None if code is None else _EVENTS_KINDS.get(code)


def _epoch_millis(value: Any) -> datetime | None:
    """UTC time of an epoch-milliseconds number; ``None`` (unset) if it is not a number or not a representable time."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(value / 1000, tz=UTC)
    except (OverflowError, ValueError, OSError):  # inf, nan, 1e300: a bad timestamp must not break the stream
        return None


def _params(params: Any) -> dict[str, Any]:
    """Request params: ``None`` is empty; anything else must be a mapping (``""`` or ``0`` are not silently dropped)."""
    if params is None:
        return {}
    if not isinstance(params, Mapping):
        raise TypeError(f"request params must be a mapping or None, got {type(params).__name__}")
    return dict(params)


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
    if isinstance(filters, (str, bytes, Mapping)) or not isinstance(filters, Sequence):
        raise TypeError("event_filter_list must be a sequence of EventFilter objects or {'topicFilter': ...} mappings")
    # Every entry is checked here, so a malformed filter fails locally instead of being rejected by the device.
    wire = [(f if isinstance(f, EventFilter) else EventFilter.from_wire(f)).to_wire() for f in filters]
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
        return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": _params(params)}

    def correlation_id(self, message: Any) -> str | None:
        if not isinstance(message, Mapping) or message.get("method") == self.sample_method:
            return None
        identifier = message.get("id")
        return None if identifier is None else str(identifier)

    def classify(self, message: Any) -> Reply | Notification | None:
        if not isinstance(message, Mapping):
            return None
        if message.get("method") == self.sample_method:
            return self._sample(_object(self.api_id, "topicSample params", message.get("params")))
        identifier = message.get("id")
        rid = None if identifier is None else str(identifier)
        if "error" in message:
            return Reply(rid, error=_error(self.api_id, message["error"]))
        if "result" in message:
            return Reply(rid, result=message["result"])
        if rid is not None and message.get("method") is None:  # a response (no method, or an explicit null) with neither result nor error
            raise ResponseFormatError(self.api_id, "receive", "a reply with neither result nor error")
        return None

    @staticmethod
    def _sample(params: Mapping[str, Any]) -> Notification | None:
        """A ``topicSample``, validated as a whole against the generated ``TopicSampleParams`` (strict types: a required
        field that is missing or of the wrong type is a malformed message, never a silent drop or a default).
        ``isHistorical`` keeps its semantics: a real bool, and absent means ``False``."""
        # The generated schema, imported late because that module imports this one.
        from .._protocols.base import RESPONSE_CONTEXT
        from ..apis.device_data_hub_ws import TopicSampleParams

        checked: TopicSampleParams | None = None
        fields = ""
        try:
            checked = TopicSampleParams.model_validate(
                {"isHistorical": False, **params}, strict=True, context={RESPONSE_CONTEXT: True}
            )
        except ValidationError as error:
            fields = ", ".join(sorted({".".join(str(part) for part in item["loc"]) for item in error.errors(include_input=False)}))
        if checked is None:  # raised outside the handler: the validation error would carry the sample (instance and data)
            raise ResponseFormatError(
                "datahub-streaming-over-websocket", "receive", f"malformed topicSample: invalid or missing {fields}"
            )
        stamp: datetime | None = None
        try:
            stamp = datetime.fromisoformat(checked.timestamp.replace("Z", "+00:00"))
        except (ValueError, OverflowError):
            stamp = None  # the text is required, but an unparsable time leaves the timestamp unset
        return Notification(
            TopicSample(checked.subscription_id, checked.topic, checked.instance, checked.data, stamp, checked.is_historical, params)
        )

    def error_kind(self, code: int | str | None) -> ErrorKind | None:
        return None if code is None else _DATAHUB_KINDS.get(code)


def datahub_setup(options: Mapping[str, Any]) -> list[tuple[str, JsonObject | None]]:
    """``subscriptions``: a sequence of ``{"subscriptionId": ..., "filters": [...], ...}`` objects sent as ``data-hub_v1:subscribe``."""
    unknown = set(options) - {"subscriptions"}
    if unknown:
        raise TypeError(f"unexpected arguments for the data hub session: {sorted(unknown)}")
    # The generated schema, imported late because that module imports this one.
    from ..apis.device_data_hub_ws import Subscription

    subscriptions: Any = options.get("subscriptions")
    if subscriptions is None:
        subscriptions = ()
    # Only None means "no subscriptions": {}, "", 0 and False are wrong types and must not open a silent session.
    if isinstance(subscriptions, (str, bytes, Mapping)) or not isinstance(subscriptions, Sequence):
        raise TypeError("subscriptions must be a sequence of Subscription objects or mappings")
    requests: list[tuple[str, JsonObject | None]] = []
    for sub in subscriptions:
        # Validated against the schema (strict request rules) and serialized with the wire names; a bad
        # mapping raises a ValidationError here instead of reaching the device.
        model = sub.revalidated() if isinstance(sub, Subscription) else Subscription.model_validate(dict(sub)).revalidated()
        requests.append(("data-hub_v1:subscribe", model.to_wire()))
    return requests
