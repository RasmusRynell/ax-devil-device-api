# GENERATED from specs/apis/network-video/groupview.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Get, list available and set the channel layout of a group view (for example quad or dual).

Docs: https://developer.axis.com/vapix/network-video/group-view/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Channel(Model):
    """A channel placed at one location of the group view."""

    id: int
    """Channel placed at this location."""


Layout = list[list[Channel]]


class AllowedChannels(Model):
    """The channels that may be placed at one location of an available layout."""

    id: list[int]
    """Channel IDs allowed at this location."""


LayoutOption = list[list[AllowedChannels]]


class AvailableLayout(Model):
    id: int
    """Group view ID."""
    layout: list[LayoutOption]
    """List of possible layouts."""


class GroupViewLayout(Model):
    id: int
    """Group view ID."""
    layout: Layout


class GetLayoutRequest(Model):
    id: int
    """The ID of the group view to check."""


class GetAvailableLayoutRequest(Model):
    id: int | None = None
    """Group view ID. Omit to get possible layouts for every ID supporting group view. The request fails if the ID does not support group view."""


class SetLayoutRequest(Model):
    id: int
    """The group view ID to set the layout for."""
    layout: Layout
    """New channel layout: list of rows, each a list of {id} channel elements from left to right."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/groupview.cgi"

INFO = ApiInfo(
    id="groupview",
    name="Group View",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("groupview"),),
    docs=("https://developer.axis.com/vapix/network-video/group-view/",),
    errors={
        1100: ErrorCode("Internal error (also out-of-memory).", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
        2106: ErrorCode("Authentication failed.", "access_denied"),
        2107: ErrorCode("Transport-level error (HTTP 4XX, 5XX)."),
    },
)


class OPS:
    get_layout = Operation(
        INFO,
        "get_layout",
        JsonRpcBinding("getLayout", PATH),
        params=GetLayoutRequest,
        result=GroupViewLayout,
        access="operator",
        effect="read",
    )
    get_available_layout = Operation(
        INFO,
        "get_available_layout",
        JsonRpcBinding("getAvailableLayout", PATH),
        params=GetAvailableLayoutRequest,
        result=list[AvailableLayout],
        access="operator",
        effect="read",
    )
    set_layout = Operation(
        INFO,
        "set_layout",
        JsonRpcBinding("setLayout", PATH),
        params=SetLayoutRequest,
        result=GroupViewLayout,
        access="admin",
        effect="write",
        write="patch",
        errors={
            1200: ErrorCode("List does not match an allowed layout.", "invalid_argument"),
            2200: ErrorCode("Invalid value for ID in parameter layout.", "invalid_argument"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class GroupViewApi(SyncApi):
    """Group View (``groupview``, version 1)."""

    INFO = INFO

    def get_layout(self, *, id: int, request_options: RequestOptions | None = None) -> GroupViewLayout:
        """Request the current channel layout of a group view. Access: operator."""
        return self._run(OPS.get_layout, None, {"id": id}, request_options)

    def get_available_layout(
        self, *, id: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[AvailableLayout]:
        """Request possible layouts available to the group view(s). Access: operator."""
        return self._run(OPS.get_available_layout, None, {"id": id}, request_options)

    @overload
    def set_layout(
        self, request: SetLayoutRequest, /, *, request_options: RequestOptions | None = None
    ) -> GroupViewLayout: ...
    @overload
    def set_layout(
        self, /, *, id: int, layout: Layout, request_options: RequestOptions | None = None
    ) -> GroupViewLayout: ...
    def set_layout(
        self,
        request: SetLayoutRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> GroupViewLayout:
        """Set the channel layout of a group view. Changes only the fields given. Access: admin."""
        return self._run(OPS.set_layout, request, kwargs, request_options)


class AsyncGroupViewApi(AsyncApi):
    """Group View (``groupview``, version 1)."""

    INFO = INFO

    async def get_layout(self, *, id: int, request_options: RequestOptions | None = None) -> GroupViewLayout:
        """Request the current channel layout of a group view. Access: operator."""
        return await self._run(OPS.get_layout, None, {"id": id}, request_options)

    async def get_available_layout(
        self, *, id: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[AvailableLayout]:
        """Request possible layouts available to the group view(s). Access: operator."""
        return await self._run(OPS.get_available_layout, None, {"id": id}, request_options)

    @overload
    async def set_layout(
        self, request: SetLayoutRequest, /, *, request_options: RequestOptions | None = None
    ) -> GroupViewLayout: ...
    @overload
    async def set_layout(
        self, /, *, id: int, layout: Layout, request_options: RequestOptions | None = None
    ) -> GroupViewLayout: ...
    async def set_layout(
        self,
        request: SetLayoutRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> GroupViewLayout:
        """Set the channel layout of a group view. Changes only the fields given. Access: admin."""
        return await self._run(OPS.set_layout, request, kwargs, request_options)
