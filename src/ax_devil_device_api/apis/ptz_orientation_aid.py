# GENERATED from specs/apis/network-video/ptz-orientationaid.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Add a compass overlay to the video, set north, and show/hide preset position tags.

Docs: https://developer.axis.com/vapix/network-video/ptz-orientation-aid/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models


class Tag(Model):
    """Tag of a PTZ preset position."""

    id: str | None = None
    """The ID of the preset position."""
    text: str | None = None
    """The name of the preset position."""
    display: bool | None = None
    """Whether the preset position is displayed in the device web interface."""


class CompassState(Model):
    enabled: bool
    """Whether the compass is enabled."""


class SetCompassStateRequest(Model):
    enabled: bool
    """Whether the compass should be enabled."""


class TagVisibility(Model):
    id: str
    """The ID of the preset position."""
    display: bool
    """Whether the preset position is displayed in the device web interface."""


class SetTagStateRequest(Model):
    tag_list: list[TagVisibility] = Field(validation_alias="tagList", serialization_alias="tagList")
    """The tags to show or hide."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/ptz-orientationaid.cgi"

INFO = ApiInfo(
    id="ptz-orientationaid",
    name="PTZ Orientation Aid API",
    family=Family.JSONRPC,
    major=2,
    known_versions=(ApiVersion(2, 0),),
    discovery=(ApiDiscovery("ptz-orientationaid"),),
    docs=("https://developer.axis.com/vapix/network-video/ptz-orientation-aid/",),
    errors={
        1000: ErrorCode("Invalid parameter value.", "invalid_argument"),
        2003: ErrorCode("The requested API version is not supported.", "unsupported"),
        2004: ErrorCode("Method not supported.", "unsupported"),
        4000: ErrorCode("The provided JSON input was invalid.", "invalid_argument"),
        4001: ErrorCode("A mandatory input parameter was not found in the input.", "invalid_argument"),
        4002: ErrorCode("The type of a provided JSON parameter was incorrect.", "invalid_argument"),
        8000: ErrorCode("Internal error, could not complete the request.", "internal"),
        8002: ErrorCode("Generic Error.", "internal"),
    },
)


class OPS:
    set_north = Operation(INFO, "set_north", JsonRpcBinding("setNorth", PATH), access="operator", effect="action")
    get_compass_state = Operation(
        INFO,
        "get_compass_state",
        JsonRpcBinding("getCompassState", PATH),
        result=CompassState,
        access="operator",
        effect="read",
    )
    set_compass_state = Operation(
        INFO,
        "set_compass_state",
        JsonRpcBinding("setCompassState", PATH),
        params=SetCompassStateRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    list_tags = Operation(
        INFO, "list_tags", JsonRpcBinding("listTags", PATH), result=Tag, access="operator", effect="read"
    )
    set_tag_state = Operation(
        INFO,
        "set_tag_state",
        JsonRpcBinding("setTagState", PATH),
        params=SetTagStateRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class PtzOrientationAidApi(SyncApi):
    """PTZ Orientation Aid API (``ptz-orientationaid``, version 2)."""

    INFO = INFO

    def set_north(self, *, request_options: RequestOptions | None = None) -> None:
        """Set the direction the camera currently points to as north.

        Call it again whenever the camera position changes.

        Access: operator.
        """
        self._run(OPS.set_north, None, {}, request_options)

    def get_compass_state(self, *, request_options: RequestOptions | None = None) -> CompassState:
        """Check whether the compass is enabled. Access: operator."""
        return self._run(OPS.get_compass_state, None, {}, request_options)

    def set_compass_state(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the compass overlay. Changes only the fields given. Access: operator."""
        self._run(OPS.set_compass_state, None, {"enabled": enabled}, request_options)

    def list_tags(self, *, request_options: RequestOptions | None = None) -> Tag:
        """List the available tags for the preset positions. Access: operator."""
        return self._run(OPS.list_tags, None, {}, request_options)

    @overload
    def set_tag_state(
        self, request: SetTagStateRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_tag_state(
        self, tag_list: list[TagVisibility], /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_tag_state(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Show or hide the preset position tags in the device web interface.

        Changes only the entries given; entries that do not exist yet may be created. Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetTagStateRequest):
            kwargs = bind_positional(OPS.set_tag_state, ("tag_list",), (request, *args), kwargs)
            request = None
        self._run(OPS.set_tag_state, request, kwargs, request_options)


class AsyncPtzOrientationAidApi(AsyncApi):
    """PTZ Orientation Aid API (``ptz-orientationaid``, version 2)."""

    INFO = INFO

    async def set_north(self, *, request_options: RequestOptions | None = None) -> None:
        """Set the direction the camera currently points to as north.

        Call it again whenever the camera position changes.

        Access: operator.
        """
        await self._run(OPS.set_north, None, {}, request_options)

    async def get_compass_state(self, *, request_options: RequestOptions | None = None) -> CompassState:
        """Check whether the compass is enabled. Access: operator."""
        return await self._run(OPS.get_compass_state, None, {}, request_options)

    async def set_compass_state(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the compass overlay. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_compass_state, None, {"enabled": enabled}, request_options)

    async def list_tags(self, *, request_options: RequestOptions | None = None) -> Tag:
        """List the available tags for the preset positions. Access: operator."""
        return await self._run(OPS.list_tags, None, {}, request_options)

    @overload
    async def set_tag_state(
        self, request: SetTagStateRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_tag_state(
        self, tag_list: list[TagVisibility], /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_tag_state(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Show or hide the preset position tags in the device web interface.

        Changes only the entries given; entries that do not exist yet may be created. Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetTagStateRequest):
            kwargs = bind_positional(OPS.set_tag_state, ("tag_list",), (request, *args), kwargs)
            request = None
        await self._run(OPS.set_tag_state, request, kwargs, request_options)
