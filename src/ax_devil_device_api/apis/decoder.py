# GENERATED from specs/apis/network-video/decoder.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure what a network video decoder displays (views made of panes + streams, sequences) and query its capabilities.

Docs: https://developer.axis.com/vapix/network-video/decoder-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Resolution = Literal["1920x1080", "1280x720", "720x480", "640x480"]


class Capabilities(Model):
    """What the decoder supports."""

    resolution: Resolution
    """One of the supported decoder resolutions; the one currently in use."""
    max_streams: int = Field(validation_alias="maxStreams", serialization_alias="maxStreams", ge=1)
    """The maximum supported number of open video streams."""
    video_codecs: list[str] = Field(validation_alias="videoCodecs", serialization_alias="videoCodecs")
    """Video codecs supported by the decoder (documented values: H264, MPEG4, MJPEG; the example shows ``H.264``)."""
    audio_codecs: list[str] = Field(validation_alias="audioCodecs", serialization_alias="audioCodecs")
    """Audio codecs supported by the decoder (documented values: AAC, G711, G726)."""
    overlapping_panes: bool = Field(validation_alias="overlappingPanes", serialization_alias="overlappingPanes")
    """Whether the decoder supports overlapping panes (picture in picture)."""


class ConfigurationId(Model):
    configuration_id: str = Field(validation_alias="configurationId", serialization_alias="configurationId")
    """The ID of the configuration."""


class Pane(Model):
    """A canvas on which a video stream is drawn, given as position and size within the view. The origin (0, 0) is the upper left corner of the view and (1, 1) the lower right. The stream keeps its own aspect ratio."""

    pane_id: int = Field(validation_alias="paneId", serialization_alias="paneId", ge=0)
    """Unique pane ID."""
    left: float = Field(ge=0, le=1)
    top: float = Field(ge=0, le=1)
    right: float = Field(ge=0, le=1)
    bottom: float = Field(ge=0, le=1)


class Stream(Model):
    """A video stream. The camera credentials are sent unencrypted; consider HTTPS."""

    stream_id: int = Field(validation_alias="streamId", serialization_alias="streamId", ge=0)
    """Unique stream ID."""
    url: str
    """Where the decoder can reach the video, for example ``rtsp://192.168.0.90/axis-media/media.amp?resolution=1920x1080``."""
    video_codec: str = Field(validation_alias="videoCodec", serialization_alias="videoCodec")
    """The video codec the decoder should use, for example ``H264``."""
    audio_codec: str | None = Field(default=None, validation_alias="audioCodec", serialization_alias="audioCodec")
    """The audio codec, for example ``AAC``. Only one stream may set it, if the decoder supports audio. Empty by default."""
    username: str | None = None
    """Camera user name, if a login is required."""
    password: str | None = None
    """Camera password, if a login is required."""


class Segment(Model):
    """One pane and one stream that together form a part of a view."""

    stream: int = Field(ge=0)
    """The ``streamId`` of the stream."""
    pane: int = Field(ge=0)
    """The ``paneId`` of the pane."""


class View(Model):
    """The whole screen area, divided into segments."""

    view_id: int = Field(validation_alias="viewId", serialization_alias="viewId", ge=0)
    """Unique view ID."""
    duration: int | None = Field(default=None, ge=0)
    """Seconds the view is shown when several views run in a sequence. 0 shows the view continuously."""
    segments: list[Segment]


class Event(Model):
    """An event as returned in ``errors``. Stream events also carry ``viewId`` and ``streamId``. Code ranges: 1xx information, 2xx error, 3xx reserved for stream information, 4xx stream error."""

    code: int = Field(ge=0)
    message: str
    view_id: int | None = Field(default=None, validation_alias="viewId", serialization_alias="viewId", ge=0)
    stream_id: int | None = Field(default=None, validation_alias="streamId", serialization_alias="streamId", ge=0)


class SetViewConfigurationRequest(Model):
    """Arguments of ``set_view_configuration``. Replaces the running configuration."""

    panes: list[Pane]
    streams: list[Stream]
    views: list[View]
    """The views. If there are several, the decoder loops through them in a sequence, each shown for its ``duration``."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/decoder.cgi"

INFO = ApiInfo(
    id="decoder",
    name="Decoder API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ParamDiscovery("Properties.API.Decoder.Decoder", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/decoder-api/",),
    errors={
        100: ErrorCode("Configuration changed. The ID of the new configuration is provided in the message field."),
        200: ErrorCode("Internal error. Generic error.", "internal"),
        201: ErrorCode(
            "Unsupported API version. The decoder does not support the API version provided in the request.",
            "unsupported",
        ),
        202: ErrorCode("Invalid JSON. The decoder could not parse the provided JSON object.", "invalid_argument"),
        210: ErrorCode("Illegal view ID. ID is either a duplicate or not a positive integer.", "invalid_argument"),
        211: ErrorCode("Illegal pane ID. ID is either a duplicate or not a positive integer.", "invalid_argument"),
        212: ErrorCode(
            "Pane out of bound. Parts of the pane are outside of the view. The message holds the pane ID.",
            "invalid_argument",
        ),
        213: ErrorCode(
            "Overlapping pane. The pane overlaps another pane and the decoder does not support picture-in-picture (overlappingPanes is false). The message holds the pane ID.",
            "invalid_argument",
        ),
        400: ErrorCode("Failed to connect. The decoder could not connect to the streaming device.", "unavailable"),
        401: ErrorCode("Not authenticated. The provided credentials were not accepted.", "invalid_argument"),
        402: ErrorCode(
            "Out of resources. The decoder does not have enough resources to render the provided configuration.",
            "unavailable",
        ),
        403: ErrorCode(
            "Unsupported protocol. The decoder is not able to play the video or audio provided in the configuration.",
            "unsupported",
        ),
        410: ErrorCode("Illegal stream ID. ID is either a duplicate or not a positive integer.", "invalid_argument"),
    },
)


class OPS:
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        result=Capabilities,
        access="operator",
        effect="read",
    )
    get_view_configuration = Operation(
        INFO,
        "get_view_configuration",
        JsonRpcBinding("getViewConfiguration", PATH),
        result=ConfigurationId,
        access="operator",
        effect="read",
    )
    set_view_configuration = Operation(
        INFO,
        "set_view_configuration",
        JsonRpcBinding("setViewConfiguration", PATH),
        params=SetViewConfigurationRequest,
        result=ConfigurationId,
        access="operator",
        effect="write",
        write="replace",
    )


# ---------------------------------------------------------------------------
# API classes


class DecoderApi(SyncApi):
    """Decoder API (``decoder``, version 1)."""

    INFO = INFO

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """List the capabilities of the decoder. Access: operator."""
        return self._run(OPS.get_capabilities, None, {}, request_options)

    def get_view_configuration(self, *, request_options: RequestOptions | None = None) -> ConfigurationId:
        """Return the ID of the currently running configuration. Access: operator."""
        return self._run(OPS.get_view_configuration, None, {}, request_options)

    @overload
    def set_view_configuration(
        self, request: SetViewConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> ConfigurationId: ...
    @overload
    def set_view_configuration(
        self,
        /,
        *,
        panes: list[Pane],
        streams: list[Stream],
        views: list[View],
        request_options: RequestOptions | None = None,
    ) -> ConfigurationId: ...
    def set_view_configuration(
        self,
        request: SetViewConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ConfigurationId:
        """Configure what the decoder displays; returns the ID of the new configuration.

        The decoder has one running configuration, which the next successful call replaces; it is saved so
        the decoder recovers after a restart. Sequences are not supported in a split view. If the errors are
        not serious (for example the decoder cannot connect to some streams) the decoder may still use the
        configuration; the reply then carries the errors, including a 100 event with the new configuration
        ID, and the decoder keeps trying to reconnect.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        return self._run(OPS.set_view_configuration, request, kwargs, request_options)


class AsyncDecoderApi(AsyncApi):
    """Decoder API (``decoder``, version 1)."""

    INFO = INFO

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """List the capabilities of the decoder. Access: operator."""
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    async def get_view_configuration(self, *, request_options: RequestOptions | None = None) -> ConfigurationId:
        """Return the ID of the currently running configuration. Access: operator."""
        return await self._run(OPS.get_view_configuration, None, {}, request_options)

    @overload
    async def set_view_configuration(
        self, request: SetViewConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> ConfigurationId: ...
    @overload
    async def set_view_configuration(
        self,
        /,
        *,
        panes: list[Pane],
        streams: list[Stream],
        views: list[View],
        request_options: RequestOptions | None = None,
    ) -> ConfigurationId: ...
    async def set_view_configuration(
        self,
        request: SetViewConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ConfigurationId:
        """Configure what the decoder displays; returns the ID of the new configuration.

        The decoder has one running configuration, which the next successful call replaces; it is saved so
        the decoder recovers after a restart. Sequences are not supported in a split view. If the errors are
        not serious (for example the decoder cannot connect to some streams) the decoder may still use the
        configuration; the reply then carries the errors, including a 100 event with the new configuration
        ID, and the decoder keeps trying to reconnect.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        return await self._run(OPS.set_view_configuration, request, kwargs, request_options)
