# GENERATED from specs/apis/network-video/event-streaming-over-websocket.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Receive Event System events over a WebSocket (ws(s)://<device>/vapix/ws-data-stream?sources=events) using JSON-RPC style configure/notify messages.

Docs: https://developer.axis.com/vapix/network-video/event-streaming-over-websocket/
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import AbstractAsyncContextManager, AbstractContextManager

from .._http.options import DEFAULT_HEARTBEAT, Heartbeat, RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family
from .._runtime.ws import AsyncSession, Session, SessionSpec
from .._runtime.ws_codecs import EventFilter, EventsCodec, events_setup
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


# ---------------------------------------------------------------------------
# Descriptors

# No shared path: every operation names its own endpoint.

INFO = ApiInfo(
    id="event-streaming-over-websocket",
    name="Event streaming over WebSocket",
    family=Family.WS,
    discovery=(ApiDiscovery("event-streaming-over-websocket"),),
    docs=("https://developer.axis.com/vapix/network-video/event-streaming-over-websocket/",),
    errors={
        1100: ErrorCode("Internal error.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
        2106: ErrorCode("Authentication failed.", "access_denied"),
        2107: ErrorCode("Request too large.", "invalid_argument"),
    },
)


class OPS:
    pass


class SESSIONS:
    connect = SessionSpec(
        INFO.id, "/vapix/ws-data-stream", query=(("sources", "events"),), codec=EventsCodec(), setup=events_setup
    )


# ---------------------------------------------------------------------------
# API classes


class EventStreamingWebSocketApi(SyncApi):
    """Event streaming over WebSocket (``event-streaming-over-websocket``)."""

    INFO = INFO

    def connect(
        self,
        event_filter_list: Sequence[EventFilter | Mapping[str, str]] | None = None,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractContextManager[Session]:
        """Open the data-stream WebSocket for events (HTTP Upgrade handshake) and optionally select the events.

        Each connection is a separate, stateless session. `event_filter_list` sends `events:configure` right
        after the handshake (each filter is a separate subscription, so an event that matches several
        filters is delivered several times; use one filter with a logical topic expression to avoid it);
        send `session.request("events:configure", ...)` to replace the filter later, only the latest
        applies. Events arrive as `events:notify` notifications (`session.notifications()` yields
        `EventNotification`). The handshake uses Digest authentication, or a session token from
        `wssession.cgi` (`use_token=True`; valid for 15 seconds).

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.connect,
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
            event_filter_list=event_filter_list,
        )


class AsyncEventStreamingWebSocketApi(AsyncApi):
    """Event streaming over WebSocket (``event-streaming-over-websocket``)."""

    INFO = INFO

    def connect(
        self,
        event_filter_list: Sequence[EventFilter | Mapping[str, str]] | None = None,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Open the data-stream WebSocket for events (HTTP Upgrade handshake) and optionally select the events.

        Each connection is a separate, stateless session. `event_filter_list` sends `events:configure` right
        after the handshake (each filter is a separate subscription, so an event that matches several
        filters is delivered several times; use one filter with a logical topic expression to avoid it);
        send `session.request("events:configure", ...)` to replace the filter later, only the latest
        applies. Events arrive as `events:notify` notifications (`session.notifications()` yields
        `EventNotification`). The handshake uses Digest authentication, or a session token from
        `wssession.cgi` (`use_token=True`; valid for 15 seconds).

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.connect,
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
            event_filter_list=event_filter_list,
        )
