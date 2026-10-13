# GENERATED from specs/apis/network-video/ptz-focus-recall.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage PTZ memory zones, areas of pan, tilt and zoom with a saved focus that give instant focus.

Docs: https://developer.axis.com/vapix/network-video/pantiltzoom-api/
"""

from __future__ import annotations

from typing import Annotated, Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, JsonReply, Text
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models

CameraSource = Annotated[int, Field(ge=1)]


class MemoryZoneRef(Model):
    name: str
    """The name of the memory zone."""
    index: int
    """The unique index of the memory zone. -1 means that there is no zone."""


class MemoryZone(Model):
    name: str
    """The name of the memory zone."""
    index: int
    """The unique index of the memory zone."""
    polygon: str | None = None
    """Image coordinates of the zone corners, "x,y:x,y:x,y:x,y". Only returned when listing the zones in view."""
    ptpolygon: str | None = None
    """Pan and tilt coordinates of the zone corners, "x,y:x,y:x,y:x,y"."""
    zoomrange: str | None = None
    """The zoom range of the zone, "min:max"."""
    focus: int | None = None
    """The saved focus position."""


class AddMemoryZoneRequest(Model):
    name: str | None = Field(default=None, max_length=32)
    """Name of the memory zone (UTF-8), at most 32 characters."""
    polygon: str | None = None
    """Image coordinates of the zone corners, floats in "<x1>,<y1>:<x2>,<y2>:<x3>,<y3>:<x4>,<y4>". The origin (0.0, 0.0) is the image centre, x grows to the right and y upwards. The image corners are (-1.0, -1.0) to (1.0, 1.0); values outside that range are accepted. The coordinates relate to the default rotation and mirroring of the channel."""
    zoomrange: str | None = Field(default=None, pattern="^[0-9]+:[0-9]+$")
    """The zoom range where the zone is valid, "<zoom_min>:<zoom_max>" in the VAPIX scale 1-19999. Default: '1:19999'."""
    camera: CameraSource | None = None
    focus: str = Field(pattern="^(current|[0-9]{1,4})$")
    """The focus to save, 1-9999 in the VAPIX scale, or "current" to save the current focus position."""


class RemoveMemoryZoneRequest(Model):
    index: int | None = None
    """The index of the zone to remove. The zone at the current coordinate is removed if omitted."""
    camera: CameraSource | None = None


class RemoveAllMemoryZonesRequest(Model):
    camera: CameraSource | None = None


class ListMemoryZonesRequest(Model):
    camera: CameraSource | None = None


class ListMemoryZonesInViewRequest(Model):
    camera: CameraSource | None = None


class GetCurrentMemoryZoneRequest(Model):
    camera: CameraSource | None = None


class GotoMemoryZoneRequest(Model):
    camera: CameraSource | None = None
    index: int
    """The index of the memory zone."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/memoryzones/add.cgi"

INFO = ApiInfo(
    id="ptz-focus-recall",
    name="Focus recall API",
    family=Family.CGI,
    discovery=(
        ApiDiscovery("ptz-focus-recall"),
        ParamDiscovery("Properties.MemoryZones.MemoryZones", "yes"),
        ParamDiscovery("Properties.MemoryZones.Version", "0.1"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/pantiltzoom-api/",),
    errors={
        501: ErrorCode("Other error.", "internal"),
        502: ErrorCode("Unknown memory zone command.", "invalid_argument"),
        503: ErrorCode("Unknown index.", "not_found"),
        504: ErrorCode("List full.", "unavailable"),
        505: ErrorCode("Name already defined.", "invalid_argument"),
        506: ErrorCode("Name too long.", "invalid_argument"),
    },
)


class OPS:
    add_memory_zone = Operation(
        INFO,
        "add_memory_zone",
        CgiBinding(
            PATH,
            args=(CgiArg("name"), CgiArg("polygon"), CgiArg("zoomrange"), CgiArg("camera"), CgiArg("focus")),
            reply=JsonReply(),
        ),
        params=AddMemoryZoneRequest,
        result=MemoryZoneRef,
        access="viewer",
        effect="write",
        write="create",
    )
    remove_memory_zone = Operation(
        INFO,
        "remove_memory_zone",
        CgiBinding("/axis-cgi/memoryzones/remove.cgi", args=(CgiArg("index"), CgiArg("camera")), reply=Text()),
        params=RemoveMemoryZoneRequest,
        access="viewer",
        effect="write",
        write="delete",
    )
    remove_all_memory_zones = Operation(
        INFO,
        "remove_all_memory_zones",
        CgiBinding(
            "/axis-cgi/memoryzones/remove.cgi",
            fixed_query=(("removeall", "1"),),
            args=(CgiArg("camera"),),
            reply=Text(),
        ),
        params=RemoveAllMemoryZonesRequest,
        access="viewer",
        effect="write",
        write="delete",
    )
    list_memory_zones = Operation(
        INFO,
        "list_memory_zones",
        CgiBinding(
            "/axis-cgi/memoryzones/list.cgi",
            fixed_query=(("query", "list"),),
            args=(CgiArg("camera"),),
            reply=JsonReply(),
        ),
        params=ListMemoryZonesRequest,
        result=list[MemoryZone],
        access="viewer",
        effect="read",
    )
    list_memory_zones_in_view = Operation(
        INFO,
        "list_memory_zones_in_view",
        CgiBinding(
            "/axis-cgi/memoryzones/list.cgi",
            fixed_query=(("query", "view"),),
            args=(CgiArg("camera"),),
            reply=JsonReply(),
        ),
        params=ListMemoryZonesInViewRequest,
        result=list[MemoryZone],
        access="viewer",
        effect="read",
    )
    get_current_memory_zone = Operation(
        INFO,
        "get_current_memory_zone",
        CgiBinding(
            "/axis-cgi/memoryzones/list.cgi",
            fixed_query=(("query", "current"),),
            args=(CgiArg("camera"),),
            reply=JsonReply(),
        ),
        params=GetCurrentMemoryZoneRequest,
        result=MemoryZoneRef,
        access="viewer",
        effect="read",
    )
    goto_memory_zone = Operation(
        INFO,
        "goto_memory_zone",
        CgiBinding("/axis-cgi/memoryzones/goto.cgi", args=(CgiArg("camera"), CgiArg("index")), reply=Text()),
        params=GotoMemoryZoneRequest,
        access="viewer",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class FocusRecallApi(SyncApi):
    """Focus recall API (``ptz-focus-recall``)."""

    INFO = INFO

    @overload
    def add_memory_zone(
        self, request: AddMemoryZoneRequest, /, *, request_options: RequestOptions | None = None
    ) -> MemoryZoneRef: ...
    @overload
    def add_memory_zone(
        self,
        focus: str,
        /,
        *,
        name: str | MISSING = MISSING,
        polygon: str | MISSING = MISSING,
        zoomrange: str | MISSING = MISSING,
        camera: CameraSource | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> MemoryZoneRef: ...
    def add_memory_zone(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> MemoryZoneRef:
        """Add a memory zone that saves a focus position for a pan, tilt and zoom area.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, AddMemoryZoneRequest):
            kwargs = bind_positional(OPS.add_memory_zone, ("focus",), (request, *args), kwargs)
            request = None
        return self._run(OPS.add_memory_zone, request, kwargs, request_options)

    def remove_memory_zone(
        self,
        index: int | MISSING = MISSING,
        *,
        camera: CameraSource | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Remove a memory zone, by default the one at the current coordinate. Access: viewer."""
        self._run(OPS.remove_memory_zone, None, {"index": index, "camera": camera}, request_options)

    def remove_all_memory_zones(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove all configured memory zones. Access: viewer."""
        self._run(OPS.remove_all_memory_zones, None, {"camera": camera}, request_options)

    def list_memory_zones(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[MemoryZone]:
        """List all memory zones. Access: viewer."""
        return self._run(OPS.list_memory_zones, None, {"camera": camera}, request_options)

    def list_memory_zones_in_view(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[MemoryZone]:
        """List the memory zones inside the current view, including their image polygon.

        Access: viewer.
        """
        return self._run(OPS.list_memory_zones_in_view, None, {"camera": camera}, request_options)

    def get_current_memory_zone(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MemoryZoneRef:
        """Get the memory zone at the current coordinate.

        The index is -1 and the name empty when no zone is at the current coordinate.

        Access: viewer.
        """
        return self._run(OPS.get_current_memory_zone, None, {"camera": camera}, request_options)

    def goto_memory_zone(
        self, index: int, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Go to and focus on the coordinates of a memory zone. Access: viewer."""
        self._run(OPS.goto_memory_zone, None, {"camera": camera, "index": index}, request_options)


class AsyncFocusRecallApi(AsyncApi):
    """Focus recall API (``ptz-focus-recall``)."""

    INFO = INFO

    @overload
    async def add_memory_zone(
        self, request: AddMemoryZoneRequest, /, *, request_options: RequestOptions | None = None
    ) -> MemoryZoneRef: ...
    @overload
    async def add_memory_zone(
        self,
        focus: str,
        /,
        *,
        name: str | MISSING = MISSING,
        polygon: str | MISSING = MISSING,
        zoomrange: str | MISSING = MISSING,
        camera: CameraSource | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> MemoryZoneRef: ...
    async def add_memory_zone(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> MemoryZoneRef:
        """Add a memory zone that saves a focus position for a pan, tilt and zoom area.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, AddMemoryZoneRequest):
            kwargs = bind_positional(OPS.add_memory_zone, ("focus",), (request, *args), kwargs)
            request = None
        return await self._run(OPS.add_memory_zone, request, kwargs, request_options)

    async def remove_memory_zone(
        self,
        index: int | MISSING = MISSING,
        *,
        camera: CameraSource | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Remove a memory zone, by default the one at the current coordinate. Access: viewer."""
        await self._run(OPS.remove_memory_zone, None, {"index": index, "camera": camera}, request_options)

    async def remove_all_memory_zones(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove all configured memory zones. Access: viewer."""
        await self._run(OPS.remove_all_memory_zones, None, {"camera": camera}, request_options)

    async def list_memory_zones(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[MemoryZone]:
        """List all memory zones. Access: viewer."""
        return await self._run(OPS.list_memory_zones, None, {"camera": camera}, request_options)

    async def list_memory_zones_in_view(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[MemoryZone]:
        """List the memory zones inside the current view, including their image polygon.

        Access: viewer.
        """
        return await self._run(OPS.list_memory_zones_in_view, None, {"camera": camera}, request_options)

    async def get_current_memory_zone(
        self, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MemoryZoneRef:
        """Get the memory zone at the current coordinate.

        The index is -1 and the name empty when no zone is at the current coordinate.

        Access: viewer.
        """
        return await self._run(OPS.get_current_memory_zone, None, {"camera": camera}, request_options)

    async def goto_memory_zone(
        self, index: int, *, camera: CameraSource | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Go to and focus on the coordinates of a memory zone. Access: viewer."""
        await self._run(OPS.goto_memory_zone, None, {"camera": camera, "index": index}, request_options)
