# GENERATED from specs/apis/network-video/privacy-mask.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Create, update, remove, locate and toggle privacy masks through ``privacymask.cgi`` (follows pan/tilt/zoom) and the ``Image.I#.Overlay.MaskWindows`` parameters.

Docs: https://developer.axis.com/vapix/network-video/overlay-api/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, JsonReply, Text, TextKv, TextOk
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models


class PixelPoint(Model):
    x: int
    """Horizontal pixel coordinate. Outside the current view it may be negative or larger than the image width."""
    y: int
    """Vertical pixel coordinate. Outside the current view it may be negative or larger than the image height."""


class MaskPixels(Model):
    """A privacy mask with pixel coordinates in the camera's maximum resolution at rotation 0."""

    id: int
    name: str
    enabled: bool
    zoomlowlimit: int
    """Zoom position below which the mask is hidden."""
    zoom_visible: bool | None = None
    """Whether the position polygon is visible given the ``zoomlowlimit`` setting. Not always present."""
    position: list[PixelPoint]
    """External corners (set by the user), up to ``Properties.PrivacyMask.MaxNbrOfCorners``. Empty if the mask is not visible at the current camera position."""
    all_position: list[PixelPoint] | None = None
    """The corners in ``position`` plus any helper corners added by the service. Not always present."""


class MaskList(Model):
    masks: list[MaskPixels] = Field(validation_alias="listpx", serialization_alias="listpx")


class MaskPosition(Model):
    position: list[PixelPoint]
    """Corners of the mask. Empty if the mask is not visible at the current camera position."""


class AddMaskRequest(Model):
    name: str = Field(max_length=128)
    """Unique name that identifies the mask."""
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""
    width: float | None = Field(default=None, ge=0.0, le=100.0)
    """Width of the mask in percent of the image width."""
    height: float | None = Field(default=None, ge=0.0, le=100.0)
    """Height of the mask in percent of the image height."""
    center: str | None = Field(default=None, pattern=r"^[0-9]+(\.[0-9]+)?,[0-9]+(\.[0-9]+)?$")
    """Center of the mask as ``<x>,<y>`` in percent of the image width and height (0.0 to 100.0), used with ``width`` and ``height``. The mask is placed in the center of the picture when omitted."""
    pxpolygon: str | None = Field(default=None, pattern="^-?[0-9]+,-?[0-9]+(:-?[0-9]+,-?[0-9]+)*$")
    """Pixel coordinates of the corners as ``<x1>,<y1>:<x2>,<y2>:...`` in the camera's maximum resolution at rotation 0. The number of corners and the shape follow ``Properties.PrivacyMask.MaxNbrOfCorners`` and ``Properties.PrivacyMask.Polygon``."""
    zoomlowlimit: int | None = Field(default=None, ge=0, le=19999)
    """Minimum VAPIX zoom position for the mask to be rendered; at wider zoom values the mask is not rendered. 0 when omitted. Up to 19999 when digital zoom is supported."""


class UpdateMaskRequest(Model):
    name: str = Field(max_length=128)
    """Unique name that identifies the mask."""
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""
    width: float | None = Field(default=None, ge=0.0, le=100.0)
    """Width of the mask in percent of the image width."""
    height: float | None = Field(default=None, ge=0.0, le=100.0)
    """Height of the mask in percent of the image height."""
    center: str | None = Field(default=None, pattern=r"^[0-9]+(\.[0-9]+)?,[0-9]+(\.[0-9]+)?$")
    """Center of the mask as ``<x>,<y>`` in percent of the image width and height (0.0 to 100.0), used with ``width`` and ``height``. The mask is placed in the center of the picture when omitted."""
    pxpolygon: str | None = Field(default=None, pattern="^-?[0-9]+,-?[0-9]+(:-?[0-9]+,-?[0-9]+)*$")
    """Pixel coordinates of the corners as ``<x1>,<y1>:<x2>,<y2>:...`` in the camera's maximum resolution at rotation 0. The number of corners and the shape follow ``Properties.PrivacyMask.MaxNbrOfCorners`` and ``Properties.PrivacyMask.Polygon``."""
    zoomlowlimit: int | None = Field(default=None, ge=0, le=19999)
    """Minimum VAPIX zoom position for the mask to be rendered; at wider zoom values the mask is not rendered. 0 when omitted. Up to 19999 when digital zoom is supported."""


class RemoveMaskRequest(Model):
    name: str = Field(max_length=128)
    """Unique name that identifies the mask."""
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""


class GotoMaskRequest(Model):
    name: str = Field(max_length=128)
    """Unique name that identifies the mask."""
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""


class EnableAllMasksRequest(Model):
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""


class DisableAllMasksRequest(Model):
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""


class ListMasksRequest(Model):
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""


class GetMaskPositionRequest(Model):
    name: str = Field(max_length=128)
    """Unique name that identifies the mask."""
    imagesource: int | None = Field(default=None, ge=0)
    """Image source index, 0 to the number of image sources - 1. The device uses 0 when omitted."""


class ListMaskWindowParametersRequest(Model):
    group: list[str] = Field(min_length=1)


class AddMaskWindowRequest(Model):
    group: str
    """Parent group, e.g. ``Image.I0.Overlay.MaskWindows``."""
    parameters: dict[str, str]


class UpdateMaskWindowParametersRequest(Model):
    parameters: dict[str, str]


class RemoveMaskWindowsRequest(Model):
    group: list[str] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/privacymask.cgi"

INFO = ApiInfo(
    id="privacy-mask",
    name="Privacy mask API",
    family=Family.CGI,
    discovery=(ApiDiscovery("privacy-mask"), ParamDiscovery("Properties.PrivacyMask.PrivacyMask", "yes")),
    docs=("https://developer.axis.com/vapix/network-video/overlay-api/",),
)


class OPS:
    add_mask = Operation(
        INFO,
        "add_mask",
        CgiBinding(
            PATH,
            fixed_query=(("action", "add"),),
            args=(
                CgiArg("name"),
                CgiArg("imagesource"),
                CgiArg("width"),
                CgiArg("height"),
                CgiArg("center"),
                CgiArg("pxpolygon"),
                CgiArg("zoomlowlimit"),
            ),
            reply=Text(),
        ),
        params=AddMaskRequest,
        access="admin",
        effect="write",
        write="create",
    )
    update_mask = Operation(
        INFO,
        "update_mask",
        CgiBinding(
            PATH,
            fixed_query=(("action", "update"),),
            args=(
                CgiArg("name"),
                CgiArg("imagesource"),
                CgiArg("width"),
                CgiArg("height"),
                CgiArg("center"),
                CgiArg("pxpolygon"),
                CgiArg("zoomlowlimit"),
            ),
            reply=Text(),
        ),
        params=UpdateMaskRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_mask = Operation(
        INFO,
        "remove_mask",
        CgiBinding(
            PATH, fixed_query=(("action", "remove"),), args=(CgiArg("name"), CgiArg("imagesource")), reply=Text()
        ),
        params=RemoveMaskRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    goto_mask = Operation(
        INFO,
        "goto_mask",
        CgiBinding(PATH, fixed_query=(("action", "goto"),), args=(CgiArg("name"), CgiArg("imagesource")), reply=Text()),
        params=GotoMaskRequest,
        access="admin",
        effect="action",
    )
    enable_all_masks = Operation(
        INFO,
        "enable_all_masks",
        CgiBinding(PATH, fixed_query=(("action", "enable_all"),), args=(CgiArg("imagesource"),), reply=Text()),
        params=EnableAllMasksRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    disable_all_masks = Operation(
        INFO,
        "disable_all_masks",
        CgiBinding(PATH, fixed_query=(("action", "disable_all"),), args=(CgiArg("imagesource"),), reply=Text()),
        params=DisableAllMasksRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_masks = Operation(
        INFO,
        "list_masks",
        CgiBinding(PATH, fixed_query=(("query", "listpxjson"),), args=(CgiArg("imagesource"),), reply=JsonReply()),
        params=ListMasksRequest,
        result=MaskList,
        access="operator",
        effect="read",
    )
    get_mask_position = Operation(
        INFO,
        "get_mask_position",
        CgiBinding(
            PATH,
            fixed_query=(("query", "positionpxjson"),),
            args=(CgiArg("name"), CgiArg("imagesource")),
            reply=JsonReply(),
        ),
        params=GetMaskPositionRequest,
        result=MaskPosition,
        access="operator",
        effect="read",
    )
    list_mask_window_parameters = Operation(
        INFO,
        "list_mask_window_parameters",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListMaskWindowParametersRequest,
        result=dict[str, str],
        access="operator",
        effect="read",
    )
    add_mask_window = Operation(
        INFO,
        "add_mask_window",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "add"), ("template", "0_maskwindows")),
            args=(CgiArg("group"), CgiArg("parameters", style="spread")),
            reply=Text(),
        ),
        params=AddMaskWindowRequest,
        result=str,
        access="admin",
        effect="write",
        write="create",
    )
    update_mask_window_parameters = Operation(
        INFO,
        "update_mask_window_parameters",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "update"),),
            args=(CgiArg("parameters", style="spread"),),
            reply=TextOk(),
        ),
        params=UpdateMaskWindowParametersRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_mask_windows = Operation(
        INFO,
        "remove_mask_windows",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "remove"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextOk(),
        ),
        params=RemoveMaskWindowsRequest,
        access="admin",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class PrivacyMaskApi(SyncApi):
    """Privacy mask API (``privacy-mask``)."""

    INFO = INFO

    @overload
    def add_mask(self, request: AddMaskRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def add_mask(
        self,
        name: str,
        /,
        *,
        imagesource: int | MISSING = MISSING,
        width: float | MISSING = MISSING,
        height: float | MISSING = MISSING,
        center: str | MISSING = MISSING,
        pxpolygon: str | MISSING = MISSING,
        zoomlowlimit: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_mask(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Add a new mask with a unique name.

        Give either ``width`` and ``height`` (percent of the image, optionally with ``center``), or
        ``pxpolygon``. The device replies 204 No content.

        Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, AddMaskRequest):
            kwargs = bind_positional(OPS.add_mask, ("name",), (request, *args), kwargs)
            request = None
        self._run(OPS.add_mask, request, kwargs, request_options)

    @overload
    def update_mask(self, request: UpdateMaskRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_mask(
        self,
        name: str,
        /,
        *,
        imagesource: int | MISSING = MISSING,
        width: float | MISSING = MISSING,
        height: float | MISSING = MISSING,
        center: str | MISSING = MISSING,
        pxpolygon: str | MISSING = MISSING,
        zoomlowlimit: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_mask(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the position and/or size of an existing mask.

        Give either ``width`` and ``height`` (optionally with ``center``), or ``pxpolygon``.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, UpdateMaskRequest):
            kwargs = bind_positional(OPS.update_mask, ("name",), (request, *args), kwargs)
            request = None
        self._run(OPS.update_mask, request, kwargs, request_options)

    def remove_mask(
        self, name: str, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an existing mask. Access: admin."""
        self._run(OPS.remove_mask, None, {"name": name, "imagesource": imagesource}, request_options)

    def goto_mask(
        self, name: str, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Center the camera on an existing mask. Access: admin."""
        self._run(OPS.goto_mask, None, {"name": name, "imagesource": imagesource}, request_options)

    def enable_all_masks(
        self, imagesource: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable all masks.

        Sets ``Image.I#.Overlay.MaskWindows.M#.Enabled`` to yes for all configured masks. Needs
        ``Properties.PrivacyMask.MainSwitch=yes``.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.enable_all_masks, None, {"imagesource": imagesource}, request_options)

    def disable_all_masks(
        self, imagesource: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> None:
        """Disable all masks, for example in an emergency when nothing vital should be hidden.

        Sets ``Image.I#.Overlay.MaskWindows.M#.Enabled`` to no for all configured masks. Needs
        ``Properties.PrivacyMask.MainSwitch=yes``.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.disable_all_masks, None, {"imagesource": imagesource}, request_options)

    def list_masks(
        self, imagesource: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> MaskList:
        """List all masks with pixel coordinates.

        Coordinates are in the camera's maximum resolution at rotation 0. Supported if ``listpxjson`` is
        listed in ``Properties.PrivacyMask.Query``.

        Access: operator.
        """
        return self._run(OPS.list_masks, None, {"imagesource": imagesource}, request_options)

    def get_mask_position(
        self, name: str, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MaskPosition:
        """Pixel coordinates of a named mask.

        Coordinates are in the camera's maximum resolution at rotation 0. Supported if ``positionpxjson`` is
        listed in ``Properties.PrivacyMask.Query``.

        Access: operator.
        """
        return self._run(OPS.get_mask_position, None, {"name": name, "imagesource": imagesource}, request_options)

    def list_mask_window_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Parameter values as ``{"Image.I0.Overlay.MaskWindows.M0.Name": "..."}`` (``root.`` removed).

        List groups such as ``Image.I0.Overlay.MaskWindows``. Per image source: ``Color`` (black, grey,
        white, red, blurred, or hardware dependent mosaic, chameleon) and ``MosaicScale`` (3-16); per mask
        ``M#``: ``Enabled``, ``Name``, ``XPos``, ``YPos``, ``Width``, ``Height`` (pixels) and
        ``ZoomLowLimit``.

        Access: operator.
        """
        return self._run(OPS.list_mask_window_parameters, None, {"group": group}, request_options)

    def add_mask_window(
        self, group: str, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> str:
        """Create a mask ``M0``, ``M1``, ... from the ``0_maskwindows`` template with ``param.cgi``.

        ``group`` is e.g. ``Image.I0.Overlay.MaskWindows``. Pass initial values as full parameter names with
        a bare ``M`` for the new mask, e.g. ``{"Image.I0.Overlay.MaskWindows.M.Enabled": "yes",
        "Image.I0.Overlay.MaskWindows.M.Width": "250", "Image.I0.Overlay.MaskWindows.M.Name": "mask1"}``.
        Masks made this way do not follow pan/tilt/zoom changes.

        Access: admin.
        """
        return self._run(OPS.add_mask_window, None, {"group": group, "parameters": dict(parameters)}, request_options)

    def update_mask_window_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Update mask parameters, e.g. ``{"Image.I0.Overlay.MaskWindows.M1.Name": "mask2_old"}``.

        Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_mask_window_parameters, None, {"parameters": dict(parameters)}, request_options)

    def remove_mask_windows(self, group: list[str], *, request_options: RequestOptions | None = None) -> None:
        """Remove masks with ``param.cgi``, e.g. ``["Image.I0.Overlay.MaskWindows.M0"]``.

        Access: admin.
        """
        self._run(OPS.remove_mask_windows, None, {"group": group}, request_options)


class AsyncPrivacyMaskApi(AsyncApi):
    """Privacy mask API (``privacy-mask``)."""

    INFO = INFO

    @overload
    async def add_mask(self, request: AddMaskRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def add_mask(
        self,
        name: str,
        /,
        *,
        imagesource: int | MISSING = MISSING,
        width: float | MISSING = MISSING,
        height: float | MISSING = MISSING,
        center: str | MISSING = MISSING,
        pxpolygon: str | MISSING = MISSING,
        zoomlowlimit: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_mask(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Add a new mask with a unique name.

        Give either ``width`` and ``height`` (percent of the image, optionally with ``center``), or
        ``pxpolygon``. The device replies 204 No content.

        Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, AddMaskRequest):
            kwargs = bind_positional(OPS.add_mask, ("name",), (request, *args), kwargs)
            request = None
        await self._run(OPS.add_mask, request, kwargs, request_options)

    @overload
    async def update_mask(
        self, request: UpdateMaskRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_mask(
        self,
        name: str,
        /,
        *,
        imagesource: int | MISSING = MISSING,
        width: float | MISSING = MISSING,
        height: float | MISSING = MISSING,
        center: str | MISSING = MISSING,
        pxpolygon: str | MISSING = MISSING,
        zoomlowlimit: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_mask(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the position and/or size of an existing mask.

        Give either ``width`` and ``height`` (optionally with ``center``), or ``pxpolygon``.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, UpdateMaskRequest):
            kwargs = bind_positional(OPS.update_mask, ("name",), (request, *args), kwargs)
            request = None
        await self._run(OPS.update_mask, request, kwargs, request_options)

    async def remove_mask(
        self, name: str, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an existing mask. Access: admin."""
        await self._run(OPS.remove_mask, None, {"name": name, "imagesource": imagesource}, request_options)

    async def goto_mask(
        self, name: str, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Center the camera on an existing mask. Access: admin."""
        await self._run(OPS.goto_mask, None, {"name": name, "imagesource": imagesource}, request_options)

    async def enable_all_masks(
        self, imagesource: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable all masks.

        Sets ``Image.I#.Overlay.MaskWindows.M#.Enabled`` to yes for all configured masks. Needs
        ``Properties.PrivacyMask.MainSwitch=yes``.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.enable_all_masks, None, {"imagesource": imagesource}, request_options)

    async def disable_all_masks(
        self, imagesource: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> None:
        """Disable all masks, for example in an emergency when nothing vital should be hidden.

        Sets ``Image.I#.Overlay.MaskWindows.M#.Enabled`` to no for all configured masks. Needs
        ``Properties.PrivacyMask.MainSwitch=yes``.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.disable_all_masks, None, {"imagesource": imagesource}, request_options)

    async def list_masks(
        self, imagesource: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> MaskList:
        """List all masks with pixel coordinates.

        Coordinates are in the camera's maximum resolution at rotation 0. Supported if ``listpxjson`` is
        listed in ``Properties.PrivacyMask.Query``.

        Access: operator.
        """
        return await self._run(OPS.list_masks, None, {"imagesource": imagesource}, request_options)

    async def get_mask_position(
        self, name: str, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MaskPosition:
        """Pixel coordinates of a named mask.

        Coordinates are in the camera's maximum resolution at rotation 0. Supported if ``positionpxjson`` is
        listed in ``Properties.PrivacyMask.Query``.

        Access: operator.
        """
        return await self._run(OPS.get_mask_position, None, {"name": name, "imagesource": imagesource}, request_options)

    async def list_mask_window_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Parameter values as ``{"Image.I0.Overlay.MaskWindows.M0.Name": "..."}`` (``root.`` removed).

        List groups such as ``Image.I0.Overlay.MaskWindows``. Per image source: ``Color`` (black, grey,
        white, red, blurred, or hardware dependent mosaic, chameleon) and ``MosaicScale`` (3-16); per mask
        ``M#``: ``Enabled``, ``Name``, ``XPos``, ``YPos``, ``Width``, ``Height`` (pixels) and
        ``ZoomLowLimit``.

        Access: operator.
        """
        return await self._run(OPS.list_mask_window_parameters, None, {"group": group}, request_options)

    async def add_mask_window(
        self, group: str, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> str:
        """Create a mask ``M0``, ``M1``, ... from the ``0_maskwindows`` template with ``param.cgi``.

        ``group`` is e.g. ``Image.I0.Overlay.MaskWindows``. Pass initial values as full parameter names with
        a bare ``M`` for the new mask, e.g. ``{"Image.I0.Overlay.MaskWindows.M.Enabled": "yes",
        "Image.I0.Overlay.MaskWindows.M.Width": "250", "Image.I0.Overlay.MaskWindows.M.Name": "mask1"}``.
        Masks made this way do not follow pan/tilt/zoom changes.

        Access: admin.
        """
        return await self._run(
            OPS.add_mask_window, None, {"group": group, "parameters": dict(parameters)}, request_options
        )

    async def update_mask_window_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Update mask parameters, e.g. ``{"Image.I0.Overlay.MaskWindows.M1.Name": "mask2_old"}``.

        Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_mask_window_parameters, None, {"parameters": dict(parameters)}, request_options)

    async def remove_mask_windows(self, group: list[str], *, request_options: RequestOptions | None = None) -> None:
        """Remove masks with ``param.cgi``, e.g. ``["Image.I0.Overlay.MaskWindows.M0"]``.

        Access: admin.
        """
        await self._run(OPS.remove_mask_windows, None, {"group": group}, request_options)
