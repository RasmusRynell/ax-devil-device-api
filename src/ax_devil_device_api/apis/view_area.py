# GENERATED from specs/apis/network-video/view-area.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List view areas (virtual channels covering subsections of the full camera view) and set/reset their geometry.

Docs: https://developer.axis.com/vapix/network-video/view-area-api/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class RectangularGeometry(Model):
    """Rectangle related to the canvas. Only listed if the geometry can be configured."""

    horizontal_offset: int | None = Field(
        default=None, validation_alias="horizontalOffset", serialization_alias="horizontalOffset", ge=0
    )
    """Offset of the rectangle's left edge relative to the left edge of the canvas."""
    horizontal_size: int | None = Field(
        default=None, validation_alias="horizontalSize", serialization_alias="horizontalSize", ge=0
    )
    """Width of the rectangle."""
    vertical_offset: int | None = Field(
        default=None, validation_alias="verticalOffset", serialization_alias="verticalOffset", ge=0
    )
    """Offset of the top edge of the rectangle relative to the top edge of the canvas."""
    vertical_size: int | None = Field(
        default=None, validation_alias="verticalSize", serialization_alias="verticalSize", ge=0
    )
    """Height of the rectangle."""


class Size(Model):
    horizontal: int | None = Field(default=None, ge=0)
    vertical: int | None = Field(default=None, ge=0)


class Grid(Model):
    """Grid that a geometry is applied to on the canvas due to device limitations."""

    horizontal_offset: int | None = Field(
        default=None, validation_alias="horizontalOffset", serialization_alias="horizontalOffset", ge=0
    )
    """Offset of the first vertical grid line relative to the left edge of the canvas."""
    horizontal_size: int | None = Field(
        default=None, validation_alias="horizontalSize", serialization_alias="horizontalSize", ge=0
    )
    """Distance between vertical grid lines."""
    vertical_offset: int | None = Field(
        default=None, validation_alias="verticalOffset", serialization_alias="verticalOffset", ge=0
    )
    """Offset of the first horizontal grid line relative to the top edge of the canvas."""
    vertical_size: int | None = Field(
        default=None, validation_alias="verticalSize", serialization_alias="verticalSize", ge=0
    )
    """Distance between horizontal grid lines."""


class ViewAreaInfo(Model):
    """A view area (virtual channel). Geometry fields are only listed for configurable view areas."""

    id: int = Field(ge=0)
    """Identifies the view area."""
    source: int = Field(ge=0)
    """Identifies the image source that created the view areas."""
    camera: int = Field(ge=0)
    """Identifies the view area used by streaming, PTZ and other APIs."""
    configurable: bool
    """Defines if a view can be configured. Some view areas can not be configured."""
    rectangular_geometry: RectangularGeometry | None = Field(
        default=None, validation_alias="rectangularGeometry", serialization_alias="rectangularGeometry"
    )
    canvas_size: Size | None = Field(default=None, validation_alias="canvasSize", serialization_alias="canvasSize")
    """Size of the overview image the geometry is defined on. Only listed if configurable."""
    min_size: Size | None = Field(default=None, validation_alias="minSize", serialization_alias="minSize")
    """Minimum size a view area can have. Only listed if configurable."""
    max_size: Size | None = Field(default=None, validation_alias="maxSize", serialization_alias="maxSize")
    """Maximum size a view area can have. Only listed if configurable."""
    grid: Grid | None = None
    """Only listed if configurable."""


class ViewAreaGeometry(Model):
    id: int = Field(ge=0)
    """Identifies the area that should be configured."""
    rectangular_geometry: RectangularGeometry = Field(
        validation_alias="rectangularGeometry", serialization_alias="rectangularGeometry"
    )
    """Geometry for the view area as a rectangle related to the canvas."""


class ViewAreaRef(Model):
    id: int = Field(ge=0)
    """Identifies the area that should be configured."""


class ViewAreaListData(Model):
    view_areas: list[ViewAreaInfo] = Field(validation_alias="viewAreas", serialization_alias="viewAreas")


class SetGeometryRequest(Model):
    view_area: ViewAreaGeometry = Field(validation_alias="viewArea", serialization_alias="viewArea")


class ResetGeometryRequest(Model):
    view_area: ViewAreaRef = Field(validation_alias="viewArea", serialization_alias="viewArea")


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/viewarea/configure.cgi"

INFO = ApiInfo(
    id="view-area",
    name="View Area API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("view-area"),),
    docs=("https://developer.axis.com/vapix/network-video/view-area-api/",),
    errors={
        101: ErrorCode("The requested API version is not supported", "unsupported"),
        102: ErrorCode("Method unsupported", "unsupported"),
        103: ErrorCode("Internal error", "internal"),
    },
)


class OPS:
    list = Operation(
        INFO,
        "list",
        JsonRpcBinding("list", "/axis-cgi/viewarea/info.cgi"),
        result=ViewAreaListData,
        access="viewer",
        effect="read",
    )
    set_geometry = Operation(
        INFO,
        "set_geometry",
        JsonRpcBinding("setGeometry", PATH),
        params=SetGeometryRequest,
        result=ViewAreaListData,
        access="admin",
        effect="write",
        write="patch",
        errors={
            200: ErrorCode("Invalid view area ID", "invalid_argument"),
            201: ErrorCode("View area is not configurable", "unsupported"),
            202: ErrorCode("Invalid geometry", "invalid_argument"),
        },
    )
    reset_geometry = Operation(
        INFO,
        "reset_geometry",
        JsonRpcBinding("resetGeometry", PATH),
        params=ResetGeometryRequest,
        result=ViewAreaListData,
        access="admin",
        effect="action",
        errors={
            200: ErrorCode("Invalid view area ID", "invalid_argument"),
            201: ErrorCode("View area is not configurable", "unsupported"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class ViewAreaApi(SyncApi):
    """View Area API (``view-area``, version 1)."""

    INFO = INFO

    def list(self, *, request_options: RequestOptions | None = None) -> ViewAreaListData:
        """Retrieve a complete listing of available view areas and how they have been configured.

        Access: viewer.
        """
        return self._run(OPS.list, None, {}, request_options)

    @overload
    def set_geometry(
        self, request: SetGeometryRequest, /, *, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    @overload
    def set_geometry(
        self, /, *, view_area: ViewAreaGeometry, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    def set_geometry(
        self,
        request: SetGeometryRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ViewAreaListData:
        """Set the geometry of a view area.

        The geometry is not always aligned with the canvas grid and the video aspect ratio might make it
        impossible to align on all sides; the geometry will align to the best possible fit. It is
        recommended to update the local view area geometry to what is provided by the response, as it may
        differ from the request.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.set_geometry, request, kwargs, request_options)

    @overload
    def reset_geometry(
        self, request: ResetGeometryRequest, /, *, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    @overload
    def reset_geometry(
        self, /, *, view_area: ViewAreaRef, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    def reset_geometry(
        self,
        request: ResetGeometryRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ViewAreaListData:
        """Restore the geometry of a view area back to its default values. Access: admin."""
        return self._run(OPS.reset_geometry, request, kwargs, request_options)


class AsyncViewAreaApi(AsyncApi):
    """View Area API (``view-area``, version 1)."""

    INFO = INFO

    async def list(self, *, request_options: RequestOptions | None = None) -> ViewAreaListData:
        """Retrieve a complete listing of available view areas and how they have been configured.

        Access: viewer.
        """
        return await self._run(OPS.list, None, {}, request_options)

    @overload
    async def set_geometry(
        self, request: SetGeometryRequest, /, *, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    @overload
    async def set_geometry(
        self, /, *, view_area: ViewAreaGeometry, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    async def set_geometry(
        self,
        request: SetGeometryRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ViewAreaListData:
        """Set the geometry of a view area.

        The geometry is not always aligned with the canvas grid and the video aspect ratio might make it
        impossible to align on all sides; the geometry will align to the best possible fit. It is
        recommended to update the local view area geometry to what is provided by the response, as it may
        differ from the request.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.set_geometry, request, kwargs, request_options)

    @overload
    async def reset_geometry(
        self, request: ResetGeometryRequest, /, *, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    @overload
    async def reset_geometry(
        self, /, *, view_area: ViewAreaRef, request_options: RequestOptions | None = None
    ) -> ViewAreaListData: ...
    async def reset_geometry(
        self,
        request: ResetGeometryRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ViewAreaListData:
        """Restore the geometry of a view area back to its default values. Access: admin."""
        return await self._run(OPS.reset_geometry, request, kwargs, request_options)
