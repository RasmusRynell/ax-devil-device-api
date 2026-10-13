# GENERATED from specs/apis/device-data-hub/datahub-streaming-over-websocket.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Consume data from Device Data Hub (on-device pub/sub) over a JSON-RPC 2.0 WebSocket API.

Docs: https://developer.axis.com/vapix/device-data-hub/websocket/
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, ClassVar, Literal

from pydantic import Field

from .._http.options import DEFAULT_HEARTBEAT, Heartbeat, RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model
from .._runtime.ws import AsyncSession, Session, SessionSpec
from .._runtime.ws_codecs import DataHubCodec, datahub_setup
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PtzOpticalZoomStateV1(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"hfov_deg", "vfov_deg", "zoom_mag", "zoom_moving"})
    channel_id: str = Field(validation_alias="channelId", serialization_alias="channelId")
    hfov_deg: float | None = Field(default=None, ge=0, le=360.0)
    vfov_deg: float | None = Field(default=None, ge=0, le=360.0)
    zoom_mag: float | None = Field(default=None, ge=1.0, le=100.0)
    zoom_moving: bool | None = None


class PtzPanTiltStateV1(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"pan_deg", "pan_moving", "pan_speed_deg_s", "tilt_deg", "tilt_moving", "tilt_speed_deg_s"}
    )
    channel_id: str = Field(validation_alias="channelId", serialization_alias="channelId")
    pan_deg: float | None = Field(default=None, ge=-360, le=360.0)
    pan_moving: bool | None = None
    pan_speed_deg_s: float | None = Field(default=None, ge=-400, le=400.0)
    tilt_deg: float | None = Field(default=None, ge=-360, le=360.0)
    tilt_moving: bool | None = None
    tilt_speed_deg_s: float | None = Field(default=None, ge=-400, le=400.0)


class Filter(Model):
    """Subscription filter. The filters array currently supports one filter object."""

    topics: list[str] = Field(min_length=1)
    """Lists of topics to subscribe to. Minimum one topic is required."""
    instance_filter: list[dict[str, str]] | None = Field(
        default=None, validation_alias="instanceFilter", serialization_alias="instanceFilter"
    )
    """Filters samples by instance key-value pairs."""
    data_filter: list[str] | None = Field(default=None, validation_alias="dataFilter", serialization_alias="dataFilter")
    """Filters samples using jq-style expressions."""


class StartFrom(Model):
    position: Literal["oldest", "new"] | None = None
    """oldest includes historical samples, new receives only new samples. Default: 'new'."""


class Subscription(Model):
    """Same structure as the data-hub_v1:subscribe params. Each WebSocket session supports up to 10 subscriptions, and up to 10 WebSocket sessions can be active concurrently."""

    subscription_id: str | None = Field(
        default=None, validation_alias="subscriptionId", serialization_alias="subscriptionId"
    )
    """Identifies the subscription. If omitted, the device assigns a unique ID."""
    filters: list[Filter] = Field(min_length=1)
    """The filter used to select the topics and data samples. The array currently supports one filter object."""
    start_from: StartFrom | None = Field(default=None, validation_alias="startFrom", serialization_alias="startFrom")


class TopicSampleParams(Model):
    subscription_id: str = Field(validation_alias="subscriptionId", serialization_alias="subscriptionId")
    """Identifies the subscription that the sample matches."""
    topic: str
    """Identifies the topic from which the sample was received."""
    instance: dict[str, Any]
    """Instance key-value pairs associated with the sample."""
    data: dict[str, Any]
    """The topic sample data (see the topic data schemas)."""
    timestamp: str
    """When the sample was produced, ISO 8601. (format=date-time)"""
    is_historical: bool = Field(validation_alias="isHistorical", serialization_alias="isHistorical")
    """Whether the sample was cached before the subscription started."""


# ---------------------------------------------------------------------------
# Descriptors

# No shared path: every operation names its own endpoint.

INFO = ApiInfo(
    id="datahub-streaming-over-websocket",
    name="Device Data Hub WebSocket API",
    family=Family.WS,
    discovery=(ApiDiscovery("datahub-streaming-over-websocket"),),
    requires_firmware="12.11",
    docs=(
        "https://developer.axis.com/vapix/device-data-hub/websocket/",
        "https://developer.axis.com/vapix/device-data-hub/topics/",
        "https://developer.axis.com/vapix/device-data-hub/",
    ),
    errors={
        -32700: ErrorCode("Invalid JSON", "invalid_argument"),
        -32600: ErrorCode("Invalid request", "invalid_argument"),
        -32601: ErrorCode("Method not found", "unsupported"),
        -32602: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        -32603: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2105: ErrorCode("Authorization failed", "access_denied"),
        2107: ErrorCode("Transport level error"),
        1200: ErrorCode("No such subscription. Data Hub specific error code.", "not_found"),
    },
)


class OPS:
    pass


class SESSIONS:
    connect = SessionSpec(
        INFO.id, "/vapix/ws/v1", query=(("apis", "data-hub"),), codec=DataHubCodec(), setup=datahub_setup
    )


# ---------------------------------------------------------------------------
# API classes


class DeviceDataHubWebSocketApi(SyncApi):
    """Device Data Hub WebSocket API (``datahub-streaming-over-websocket``)."""

    INFO = INFO

    def connect(
        self,
        subscriptions: Sequence[Mapping[str, Any]] | None = None,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractContextManager[Session]:
        """Open the WebSocket session with Device Data Hub and optionally subscribe to topics.

        Each entry of `subscriptions` (a `Subscription`: `subscriptionId`, `filters`, `startFrom`) is sent
        as a `data-hub_v1:subscribe` request right after the handshake. Matching samples arrive as `data-
        hub_v1:topicSample` notifications (`session.notifications()` yields `TopicSample`). The other
        methods are in-session requests: `session.request("data-hub_v1:listTopics", {})`, `data-
        hub_v1:unsubscribe` (`subscriptionId`), `data-hub_v1:unsubscribeAll` and `data-
        hub_v1:listSubscriptions`. The handshake uses Basic or Digest authentication, or a session token
        from `wssession.cgi` (`use_token=True`; valid for 15 seconds).

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.connect,
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
            subscriptions=subscriptions,
        )


class AsyncDeviceDataHubWebSocketApi(AsyncApi):
    """Device Data Hub WebSocket API (``datahub-streaming-over-websocket``)."""

    INFO = INFO

    def connect(
        self,
        subscriptions: Sequence[Mapping[str, Any]] | None = None,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Open the WebSocket session with Device Data Hub and optionally subscribe to topics.

        Each entry of `subscriptions` (a `Subscription`: `subscriptionId`, `filters`, `startFrom`) is sent
        as a `data-hub_v1:subscribe` request right after the handshake. Matching samples arrive as `data-
        hub_v1:topicSample` notifications (`session.notifications()` yields `TopicSample`). The other
        methods are in-session requests: `session.request("data-hub_v1:listTopics", {})`, `data-
        hub_v1:unsubscribe` (`subscriptionId`), `data-hub_v1:unsubscribeAll` and `data-
        hub_v1:listSubscriptions`. The handshake uses Basic or Digest authentication, or a session token
        from `wssession.cgi` (`use_token=True`; valid for 15 seconds).

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.connect,
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
            subscriptions=subscriptions,
        )
