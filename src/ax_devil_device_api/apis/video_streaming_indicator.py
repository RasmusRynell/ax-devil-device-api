# GENERATED from specs/apis/network-video/video-streaming-indicator.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Superimpose an animation over the video stream to show that the stream is live even without scene motion.

Docs: https://developer.axis.com/vapix/network-video/video-streaming-indicator/
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import FixedVersion, JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

IndicatorSize = Literal["small", "medium", "large", "H1", "H2", "H3", "H4", "H5"]
Position = Literal["topLeft", "topRight", "bottomLeft", "bottomRight"] | list[Annotated[float, Field(ge=-1.0, le=1.0)]]


class IndicatorConfig(Model):
    """Current configuration and state of the indicator."""

    indicator_size: IndicatorSize = Field(validation_alias="indicatorSize", serialization_alias="indicatorSize")
    position: Position
    color: Literal["black", "white", "red", "semiTransparent"]
    bg_color: Literal["black", "white", "transparent", "semiTransparent"] = Field(
        validation_alias="bgColor", serialization_alias="bgColor"
    )
    """Background color. The tables list black, white and transparent; the set response syntax also shows semiTransparent."""
    size: list[int]
    """The size of the indicator's bounding box. (minItems=2, maxItems=2)"""
    is_active: bool = Field(validation_alias="isActive", serialization_alias="isActive")
    """Flag showing if the indicator is currently active or not."""


class SetRequest(Model):
    indicator_size: Literal["small", "medium", "large", "H1", "H2", "H3", "H4", "H5"] | None = Field(
        default=None, validation_alias="indicatorSize", serialization_alias="indicatorSize"
    )
    """Specifies the size of the indicator."""
    position: Position | None = None
    """Predefined value (topLeft, topRight, bottomLeft, bottomRight) or an array with x and y coordinates normalized in [-1.0, 1.0]."""
    color: Literal["black", "white", "red", "semiTransparent"] | None = None
    """Specifies the color of the indicator."""
    bg_color: Literal["black", "white", "transparent"] | None = Field(
        default=None, validation_alias="bgColor", serialization_alias="bgColor"
    )
    """Specifies the background color of the indicator."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/videostreamingindicator.cgi"

INFO = ApiInfo(
    id="video-streaming-indicator",
    name="Video streaming indicator",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(
        ApiDiscovery("video-streaming-indicator"),
        ParamDiscovery("Properties.VideoStreamingIndicator.VideoStreamingIndicator", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/video-streaming-indicator/",),
    errors={
        1000: ErrorCode("Internal error.", "internal"),
        1001: ErrorCode("The requested API version is not supported.", "unsupported"),
        1002: ErrorCode("Invalid method.", "unsupported"),
        1003: ErrorCode("Invalid parameter.", "invalid_argument"),
        1004: ErrorCode("The provided input was invalid.", "invalid_argument"),
    },
)


class OPS:
    get = Operation(
        INFO,
        "get",
        JsonRpcBinding("get", PATH, negotiation=FixedVersion(ApiVersion(1, 0))),
        result=IndicatorConfig,
        access="operator",
        effect="read",
    )
    set = Operation(
        INFO,
        "set",
        JsonRpcBinding("set", PATH, negotiation=FixedVersion(ApiVersion(1, 0))),
        params=SetRequest,
        result=IndicatorConfig,
        access="operator",
        effect="write",
        write="patch",
    )
    on = Operation(
        INFO,
        "on",
        JsonRpcBinding("on", PATH, negotiation=FixedVersion(ApiVersion(1, 0))),
        access="operator",
        effect="write",
        write="patch",
    )
    off = Operation(
        INFO,
        "off",
        JsonRpcBinding("off", PATH, negotiation=FixedVersion(ApiVersion(1, 0))),
        access="operator",
        effect="write",
        write="patch",
    )
    show = Operation(
        INFO,
        "show",
        JsonRpcBinding("show", PATH, negotiation=FixedVersion(ApiVersion(1, 0))),
        access="operator",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class VideoStreamingIndicatorApi(SyncApi):
    """Video streaming indicator (``video-streaming-indicator``, version 1)."""

    INFO = INFO

    def get(self, *, request_options: RequestOptions | None = None) -> IndicatorConfig:
        """Get the current configuration of the indicator. Access: operator."""
        return self._run(OPS.get, None, {}, request_options)

    def set(
        self,
        *,
        indicator_size: Literal["small", "medium", "large", "H1", "H2", "H3", "H4", "H5"] | MISSING = MISSING,
        position: Position | MISSING = MISSING,
        color: Literal["black", "white", "red", "semiTransparent"] | MISSING = MISSING,
        bg_color: Literal["black", "white", "transparent"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IndicatorConfig:
        """Update the configuration of the indicator.

        Changes only the fields given. Access: operator.
        """
        return self._run(
            OPS.set,
            None,
            {"indicator_size": indicator_size, "position": position, "color": color, "bg_color": bg_color},
            request_options,
        )

    def on(self, *, request_options: RequestOptions | None = None) -> None:
        """Enable the indicator. Changes only the fields given. Access: operator."""
        self._run(OPS.on, None, {}, request_options)

    def off(self, *, request_options: RequestOptions | None = None) -> None:
        """Disable the indicator. Changes only the fields given. Access: operator."""
        self._run(OPS.off, None, {}, request_options)

    def show(self, *, request_options: RequestOptions | None = None) -> None:
        """Show the indicator for 5 seconds (non-adjustable). Access: operator."""
        self._run(OPS.show, None, {}, request_options)


class AsyncVideoStreamingIndicatorApi(AsyncApi):
    """Video streaming indicator (``video-streaming-indicator``, version 1)."""

    INFO = INFO

    async def get(self, *, request_options: RequestOptions | None = None) -> IndicatorConfig:
        """Get the current configuration of the indicator. Access: operator."""
        return await self._run(OPS.get, None, {}, request_options)

    async def set(
        self,
        *,
        indicator_size: Literal["small", "medium", "large", "H1", "H2", "H3", "H4", "H5"] | MISSING = MISSING,
        position: Position | MISSING = MISSING,
        color: Literal["black", "white", "red", "semiTransparent"] | MISSING = MISSING,
        bg_color: Literal["black", "white", "transparent"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IndicatorConfig:
        """Update the configuration of the indicator.

        Changes only the fields given. Access: operator.
        """
        return await self._run(
            OPS.set,
            None,
            {"indicator_size": indicator_size, "position": position, "color": color, "bg_color": bg_color},
            request_options,
        )

    async def on(self, *, request_options: RequestOptions | None = None) -> None:
        """Enable the indicator. Changes only the fields given. Access: operator."""
        await self._run(OPS.on, None, {}, request_options)

    async def off(self, *, request_options: RequestOptions | None = None) -> None:
        """Disable the indicator. Changes only the fields given. Access: operator."""
        await self._run(OPS.off, None, {}, request_options)

    async def show(self, *, request_options: RequestOptions | None = None) -> None:
        """Show the indicator for 5 seconds (non-adjustable). Access: operator."""
        await self._run(OPS.show, None, {}, request_options)
