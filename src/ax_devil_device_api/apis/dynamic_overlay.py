# GENERATED from specs/apis/network-video/dynamic-overlay.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Add, change, list and remove text and image overlays, and query overlay capabilities.

Docs: https://developer.axis.com/vapix/network-video/overlay-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Color = Literal["black", "white", "red", "transparent", "semiTransparent"]
NamedPosition = Literal["top", "topRight", "bottomRight", "bottom", "bottomLeft", "topLeft"]
Position = NamedPosition | Annotated[list[Annotated[float, Field(ge=-1.0, le=1.0)]], Field(min_length=2, max_length=2)]
Reference = Literal["channel", "source", "sensor", "scene"]
PtPosition = Annotated[int, Field(ge=-180, le=180)] | list[Annotated[int, Field(ge=-180, le=180)]]
ZoomInterval = Annotated[int, Field(ge=1, le=19999)] | list[Annotated[int, Field(ge=1, le=19999)]]


class AddTextRequest(Model):
    """Arguments of add_text."""

    camera: int = Field(ge=1)
    """The view area on which the overlay is displayed, from 1 to the number of view areas of the product (Plain Config / Image / Nbr of configs)."""
    text: str = Field(max_length=512)
    """The text to display. %0A is a new line. At most 512 characters."""
    position: Position | None = None
    text_color: Color | None = Field(default=None, validation_alias="textColor", serialization_alias="textColor")
    """Text color. Default is black. Default: 'black'."""
    text_bg_color: Color | None = Field(default=None, validation_alias="textBGColor", serialization_alias="textBGColor")
    """Background color. Default is transparent. Default: 'transparent'."""
    text_ol_color: Color | None = Field(default=None, validation_alias="textOLColor", serialization_alias="textOLColor")
    """Outline color. Default is transparent. Default: 'transparent'."""
    font_size: int | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize")
    """Size of the text. The default depends on the maximal camera resolution; use list to read it. The range is minFontSize to maxFontSize of get_overlay_capabilities."""
    rotation: int | None = Field(default=None, ge=-180, le=180)
    """Rotation in degrees around the center point. Default is 0. Default: 0."""
    reference: Reference | None = None
    """How the position coordinates are expressed. Deprecated; to be removed in API version 13.0. source and sensor are deprecated too. Default: 'channel'."""
    pt_position: PtPosition | None = Field(
        default=None, validation_alias="ptPosition", serialization_alias="ptPosition"
    )
    """Pan and tilt of the PTZ at which the overlay is visible. Defaults to the camera position when the overlay was created."""
    zoom_interval: ZoomInterval | None = Field(
        default=None, validation_alias="zoomInterval", serialization_alias="zoomInterval"
    )
    scroll_speed: int | None = Field(
        default=None, validation_alias="scrollSpeed", serialization_alias="scrollSpeed", ge=-20, le=20
    )
    """Slides the text across the stream: positive left to right, negative right to left. With textBGColor set the background covers the full stream width. Default: 0."""
    indicator: str | None = None
    """Documented only in the request syntax template."""
    indicator_size: int | None = Field(
        default=None, validation_alias="indicatorSize", serialization_alias="indicatorSize", ge=0, le=200
    )
    """Documented only in the request syntax template."""
    indicator_color: Color | None = Field(
        default=None, validation_alias="indicatorColor", serialization_alias="indicatorColor"
    )
    """Documented only in the request syntax template."""
    indicator_bg: Color | None = Field(default=None, validation_alias="indicatorBG", serialization_alias="indicatorBG")
    """Documented only in the request syntax template."""
    indicator_ol: Color | None = Field(default=None, validation_alias="indicatorOL", serialization_alias="indicatorOL")
    """Documented only in the request syntax template."""


class OverlayCreated(Model):
    camera: int
    """The view area on which the overlay was created."""
    identity: int
    """The identity of the overlay created."""


class AddImageRequest(Model):
    """Arguments of add_image."""

    camera: int = Field(ge=1)
    """The view area on which the overlay is displayed, from 1 to the number of view areas of the product (Plain Config / Image / Nbr of configs)."""
    overlay_path: str = Field(validation_alias="overlayPath", serialization_alias="overlayPath")
    """Path to the image to display (uploaded with the Overlay image API)."""
    position: Position | None = None


class SetTextRequest(Model):
    """Arguments of set_text. Only the given fields change."""

    identity: int
    """The overlay to change."""
    text: str | None = Field(default=None, max_length=512)
    """The text to display."""
    position: Position | None = None
    text_color: Color | None = Field(default=None, validation_alias="textColor", serialization_alias="textColor")
    text_bg_color: Color | None = Field(default=None, validation_alias="textBGColor", serialization_alias="textBGColor")
    text_ol_color: Color | None = Field(default=None, validation_alias="textOLColor", serialization_alias="textOLColor")
    font_size: int | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize")
    """Size of the text; the range is minFontSize to maxFontSize of get_overlay_capabilities."""
    rotation: int | None = Field(default=None, ge=-180, le=180)
    """Rotation in degrees around the center point."""
    scroll_speed: int | None = Field(
        default=None, validation_alias="scrollSpeed", serialization_alias="scrollSpeed", ge=-20, le=20
    )
    """Speed at which the text slides across the stream."""


class SetImageRequest(Model):
    """Arguments of set_image. Only the given fields change."""

    identity: int
    """The overlay to change."""
    overlay_path: str | None = Field(default=None, validation_alias="overlayPath", serialization_alias="overlayPath")
    """Path to the image to display."""
    position: Position | None = None


class ListOverlaysRequest(Model):
    camera: int | None = Field(default=None, ge=1)
    """List only the overlays of this view area. All view areas if omitted."""
    identity: int | None = None
    """List only this overlay."""


class ImageOverlay(Model):
    camera: int
    """The view area."""
    identity: int
    """The overlay identity."""
    overlay_path: str | None = Field(default=None, validation_alias="overlayPath", serialization_alias="overlayPath")
    """The path to the image used for the overlay."""
    position: Position | None = None
    z_index: int | None = Field(default=None, validation_alias="zIndex", serialization_alias="zIndex")
    visible: bool | None = None
    """If the overlay is visible."""
    scalable: bool | None = None
    """If the overlay is scaled, based on the resolution."""


class TextOverlay(Model):
    camera: int
    """The view area."""
    identity: int
    """The overlay identity."""
    position: Position | None = None
    text: str | None = None
    """The overlay text."""
    text_color: str | None = Field(default=None, validation_alias="textColor", serialization_alias="textColor")
    """The text color."""
    text_bg_color: str | None = Field(default=None, validation_alias="textBGColor", serialization_alias="textBGColor")
    """The background color."""
    text_ol_color: str | None = Field(default=None, validation_alias="textOLColor", serialization_alias="textOLColor")
    """The outline color."""
    font_size: int | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize")
    """The font size (the docs repeat the outline color description)."""
    rotation: int | None = None
    """The rotation of the overlay."""
    reference: str | None = None
    """The coordinate system of the position of the overlay."""
    scroll_speed: int | None = Field(default=None, validation_alias="scrollSpeed", serialization_alias="scrollSpeed")
    """The scroll speed."""
    size: list[int] | None = None
    """The actual size in pixels of the text overlay."""
    z_index: int | None = Field(default=None, validation_alias="zIndex", serialization_alias="zIndex")
    visible: bool | None = None
    """If the overlay is visible."""
    scalable: bool | None = None
    """If the overlay is scaled, based on the resolution."""
    text_length: int | None = Field(default=None, validation_alias="textLength", serialization_alias="textLength")
    """The length of the text in bytes after modifiers have been expanded with default values."""
    pt_position: list[float] | None = Field(
        default=None, validation_alias="ptPosition", serialization_alias="ptPosition"
    )
    """Pan and tilt of the PTZ at which the overlay is visible, in degrees."""
    zoom_interval: list[float] | None = Field(
        default=None, validation_alias="zoomInterval", serialization_alias="zoomInterval"
    )
    """The zoom interval in which the overlay is visible."""
    indicator: str | None = None
    """The overlay indicator text."""
    indicator_size: int | None = Field(
        default=None, validation_alias="indicatorSize", serialization_alias="indicatorSize"
    )
    """The font size of the indicator."""
    indicator_color: str | None = Field(
        default=None, validation_alias="indicatorColor", serialization_alias="indicatorColor"
    )
    """The text color of the indicator."""
    indicator_bg: str | None = Field(default=None, validation_alias="indicatorBG", serialization_alias="indicatorBG")
    """The background color of the indicator."""
    indicator_ol: str | None = Field(default=None, validation_alias="indicatorOL", serialization_alias="indicatorOL")
    """The outline color of the indicator."""


class OverlayList(Model):
    image_files: list[str] | None = Field(default=None, validation_alias="imageFiles", serialization_alias="imageFiles")
    """File names available as image overlays, for example /etc/overlays/image1.ovl."""
    image_overlays: list[ImageOverlay] | None = Field(
        default=None, validation_alias="imageOverlays", serialization_alias="imageOverlays"
    )
    text_overlays: list[TextOverlay] | None = Field(
        default=None, validation_alias="textOverlays", serialization_alias="textOverlays"
    )


class OverlayIdentity(Model):
    identity: int
    """The overlay, as returned by the add or list methods."""


class OverlayCapabilities(Model):
    max_font_size: int | None = Field(default=None, validation_alias="maxFontSize", serialization_alias="maxFontSize")
    """The maximum font size for a text overlay."""
    min_font_size: int | None = Field(default=None, validation_alias="minFontSize", serialization_alias="minFontSize")
    """The minimum font size for a text overlay."""
    max_image_height: int | None = Field(
        default=None, validation_alias="maxImageHeight", serialization_alias="maxImageHeight"
    )
    """The maximum height in pixels of an image overlay."""
    max_image_size: int | None = Field(
        default=None, validation_alias="maxImageSize", serialization_alias="maxImageSize"
    )
    """The maximum number of pixels of an image overlay."""
    max_image_width: int | None = Field(
        default=None, validation_alias="maxImageWidth", serialization_alias="maxImageWidth"
    )
    """The maximum width in pixels of an image overlay."""
    max_text_length: int | None = Field(
        default=None, validation_alias="maxTextLength", serialization_alias="maxTextLength"
    )
    """The maximum length of the text of a text overlay."""
    num_available_slots: int | None = Field(
        default=None, validation_alias="numAvailableSlots", serialization_alias="numAvailableSlots"
    )
    """The number of slots available to overlays."""
    rotation_supported: bool | None = Field(
        default=None, validation_alias="rotationSupported", serialization_alias="rotationSupported"
    )
    """If rotation is supported."""
    slots_per_image_overlay: int | None = Field(
        default=None, validation_alias="slotsPerImageOverlay", serialization_alias="slotsPerImageOverlay"
    )
    """The number of slots an image overlay occupies."""
    slots_per_overlay: int | None = Field(
        default=None, validation_alias="slotsPerOverlay", serialization_alias="slotsPerOverlay"
    )
    """The number of slots an overlay uses."""
    slots_per_text_overlay: int | None = Field(
        default=None, validation_alias="slotsPerTextOverlay", serialization_alias="slotsPerTextOverlay"
    )
    """The number of slots a text overlay occupies."""
    supported_references: list[str] | None = Field(
        default=None, validation_alias="supportedReferences", serialization_alias="supportedReferences"
    )
    """Supported overlay references."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/dynamicoverlay/dynamicoverlay.cgi"

INFO = ApiInfo(
    id="dynamic-overlay",
    name="Dynamic overlay API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 8)),
    discovery=(
        ParamDiscovery("Properties.DynamicOverlay.DynamicOverlay", "yes"),
        ParamDiscovery("Properties.DynamicOverlay.Version", "1.00"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/overlay-api/",),
    errors={
        100: ErrorCode("The requested API version is not supported.", "unsupported"),
        101: ErrorCode("Internal error.", "internal"),
        102: ErrorCode("A mandatory input parameter was not found in the input.", "invalid_argument"),
        103: ErrorCode("Invalid parameter.", "invalid_argument"),
        200: ErrorCode("The provided input was invalid.", "invalid_argument"),
        201: ErrorCode("Unexpected error.", "internal"),
        202: ErrorCode("Generic error.", "internal"),
        203: ErrorCode("Invalid method.", "unsupported"),
    },
)


class OPS:
    add_text = Operation(
        INFO,
        "add_text",
        JsonRpcBinding("addText", PATH),
        params=AddTextRequest,
        result=OverlayCreated,
        access="operator",
        effect="write",
        write="create",
        errors={
            300: ErrorCode("Unable to create overlays (limit reached).", "unavailable"),
            301: ErrorCode("Invalid value for parameter camera.", "invalid_argument"),
            303: ErrorCode("Invalid value for parameter position.", "invalid_argument"),
            304: ErrorCode("Invalid value for parameter text.", "invalid_argument"),
            306: ErrorCode("Invalid value for parameter textColor.", "invalid_argument"),
            307: ErrorCode("Invalid value for parameter textBGColor.", "invalid_argument"),
            308: ErrorCode("Invalid value for parameter textOLColor.", "invalid_argument"),
            309: ErrorCode("Invalid value for parameter fontSize.", "invalid_argument"),
            310: ErrorCode("Invalid value for parameter scrollSpeed.", "invalid_argument"),
            311: ErrorCode("Invalid value for parameter visible", "invalid_argument"),
            312: ErrorCode("Invalid value for parameter zIndex.", "invalid_argument"),
            313: ErrorCode("Invalid value for parameter reference. (Deprecated)", "invalid_argument"),
            314: ErrorCode("Invalid value for parameter ptPosition.", "invalid_argument"),
            315: ErrorCode("Invalid value for parameter zoomInterval.", "invalid_argument"),
            316: ErrorCode("Invalid value for parameter indicator.", "invalid_argument"),
            317: ErrorCode("Invalid value for parameter indicatorSize.", "invalid_argument"),
            318: ErrorCode("Invalid value for parameter indicatorColor.", "invalid_argument"),
            319: ErrorCode("Invalid value for parameter indicatorBG.", "invalid_argument"),
            320: ErrorCode("Invalid value for parameter indicatorOL.", "invalid_argument"),
            321: ErrorCode("Invalid value for parameter rotation.", "invalid_argument"),
        },
    )
    add_image = Operation(
        INFO,
        "add_image",
        JsonRpcBinding("addImage", PATH),
        params=AddImageRequest,
        result=OverlayCreated,
        access="operator",
        effect="write",
        write="create",
        errors={
            300: ErrorCode("Unable to create overlays (limit reached).", "unavailable"),
            301: ErrorCode("Invalid value for parameter camera.", "invalid_argument"),
            303: ErrorCode("Invalid value for parameter position.", "invalid_argument"),
            305: ErrorCode("Invalid value for parameter overlayPath", "invalid_argument"),
        },
    )
    set_text = Operation(
        INFO,
        "set_text",
        JsonRpcBinding("setText", PATH),
        params=SetTextRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            302: ErrorCode("Invalid value for parameter identity.", "invalid_argument"),
            303: ErrorCode("Invalid value for parameter position.", "invalid_argument"),
            304: ErrorCode("Invalid value for parameter text.", "invalid_argument"),
            306: ErrorCode("Invalid value for parameter textColor.", "invalid_argument"),
            307: ErrorCode("Invalid value for parameter textBGColor.", "invalid_argument"),
            308: ErrorCode("Invalid value for parameter textOLColor.", "invalid_argument"),
            309: ErrorCode("Invalid value for parameter fontSize.", "invalid_argument"),
            310: ErrorCode("Invalid value for parameter scrollSpeed.", "invalid_argument"),
            311: ErrorCode("Invalid value for parameter visible.", "invalid_argument"),
            312: ErrorCode("Invalid value for parameter zIndex.", "invalid_argument"),
            313: ErrorCode("Invalid value for parameter reference. (Deprecated)", "invalid_argument"),
            314: ErrorCode("Invalid value for parameter ptPosition.", "invalid_argument"),
            315: ErrorCode("Invalid value for parameter zoomInterval.", "invalid_argument"),
            316: ErrorCode("Invalid value for parameter indicator.", "invalid_argument"),
            317: ErrorCode("Invalid value for parameter indicatorSize.", "invalid_argument"),
            318: ErrorCode("Invalid value for parameter indicatorColor.", "invalid_argument"),
            319: ErrorCode("Invalid value for parameter indicatorBG.", "invalid_argument"),
            320: ErrorCode("Invalid value for parameter indicatorOL.", "invalid_argument"),
            321: ErrorCode("Invalid value for parameter rotation.", "invalid_argument"),
        },
    )
    set_image = Operation(
        INFO,
        "set_image",
        JsonRpcBinding("setImage", PATH),
        params=SetImageRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            302: ErrorCode("Invalid value for parameter identity.", "invalid_argument"),
            303: ErrorCode("Invalid value for parameter position.", "invalid_argument"),
            305: ErrorCode("Invalid value for parameter overlayPath.", "invalid_argument"),
        },
    )
    list_overlays = Operation(
        INFO,
        "list_overlays",
        JsonRpcBinding("list", PATH),
        params=ListOverlaysRequest,
        result=OverlayList,
        access="operator",
        effect="read",
        errors={
            301: ErrorCode("Invalid value for parameter camera.", "invalid_argument"),
            302: ErrorCode("Invalid value for parameter identity.", "invalid_argument"),
        },
    )
    remove_overlay = Operation(
        INFO,
        "remove_overlay",
        JsonRpcBinding("remove", PATH),
        params=OverlayIdentity,
        access="operator",
        effect="write",
        write="delete",
        errors={
            301: ErrorCode("Invalid value for parameter camera.", "invalid_argument"),
            302: ErrorCode("Invalid value for parameter identity.", "invalid_argument"),
        },
    )
    get_overlay_capabilities = Operation(
        INFO,
        "get_overlay_capabilities",
        JsonRpcBinding("getOverlayCapabilities", PATH),
        result=OverlayCapabilities,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class DynamicOverlayApi(SyncApi):
    """Dynamic overlay API (``dynamic-overlay``, version 1)."""

    INFO = INFO

    @overload
    def add_text(
        self, request: AddTextRequest, /, *, request_options: RequestOptions | None = None
    ) -> OverlayCreated: ...
    @overload
    def add_text(
        self,
        /,
        *,
        camera: int,
        text: str,
        position: Position | MISSING = MISSING,
        text_color: Color | MISSING = MISSING,
        text_bg_color: Color | MISSING = MISSING,
        text_ol_color: Color | MISSING = MISSING,
        font_size: int | MISSING = MISSING,
        rotation: int | MISSING = MISSING,
        reference: Reference | MISSING = MISSING,
        pt_position: PtPosition | MISSING = MISSING,
        zoom_interval: ZoomInterval | MISSING = MISSING,
        scroll_speed: int | MISSING = MISSING,
        indicator: str | MISSING = MISSING,
        indicator_size: int | MISSING = MISSING,
        indicator_color: Color | MISSING = MISSING,
        indicator_bg: Color | MISSING = MISSING,
        indicator_ol: Color | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> OverlayCreated: ...
    def add_text(
        self, request: AddTextRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> OverlayCreated:
        """Create a text overlay and return its identity.

        Creates a text overlay. Properties can be given at the same time.

        Access: operator.
        """
        return self._run(OPS.add_text, request, kwargs, request_options)

    def add_image(
        self,
        *,
        camera: int,
        overlay_path: str,
        position: Position | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> OverlayCreated:
        """Create an image overlay and return its identity.

        Properties can be given at the same time. Upload new images with the Overlay image API.

        Access: operator.
        """
        return self._run(
            OPS.add_image, None, {"camera": camera, "overlay_path": overlay_path, "position": position}, request_options
        )

    @overload
    def set_text(self, request: SetTextRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_text(
        self,
        /,
        *,
        identity: int,
        text: str | MISSING = MISSING,
        position: Position | MISSING = MISSING,
        text_color: Color | MISSING = MISSING,
        text_bg_color: Color | MISSING = MISSING,
        text_ol_color: Color | MISSING = MISSING,
        font_size: int | MISSING = MISSING,
        rotation: int | MISSING = MISSING,
        scroll_speed: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_text(
        self, request: SetTextRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change properties of a text overlay.

        Fields that are not given are not changed.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_text, request, kwargs, request_options)

    def set_image(
        self,
        *,
        identity: int,
        overlay_path: str | MISSING = MISSING,
        position: Position | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Change properties of an image overlay.

        Fields that are not given are not changed.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_image,
            None,
            {"identity": identity, "overlay_path": overlay_path, "position": position},
            request_options,
        )

    def list_overlays(
        self,
        *,
        camera: int | MISSING = MISSING,
        identity: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> OverlayList:
        """List the overlays that were created, with their properties, and the available image files.

        Overlay identities can change after a reboot, so check the identity with this method before updating
        or removing an overlay.

        Access: operator.
        """
        return self._run(OPS.list_overlays, None, {"camera": camera, "identity": identity}, request_options)

    def remove_overlay(self, *, identity: int, request_options: RequestOptions | None = None) -> None:
        """Remove an overlay.

        Removes the overlay identified by the given identity.

        Access: operator.
        """
        self._run(OPS.remove_overlay, None, {"identity": identity}, request_options)

    def get_overlay_capabilities(self, *, request_options: RequestOptions | None = None) -> OverlayCapabilities:
        """Get the number of overlay slots, slots per text and image overlay, and size limits.

        Access: operator.
        """
        return self._run(OPS.get_overlay_capabilities, None, {}, request_options)


class AsyncDynamicOverlayApi(AsyncApi):
    """Dynamic overlay API (``dynamic-overlay``, version 1)."""

    INFO = INFO

    @overload
    async def add_text(
        self, request: AddTextRequest, /, *, request_options: RequestOptions | None = None
    ) -> OverlayCreated: ...
    @overload
    async def add_text(
        self,
        /,
        *,
        camera: int,
        text: str,
        position: Position | MISSING = MISSING,
        text_color: Color | MISSING = MISSING,
        text_bg_color: Color | MISSING = MISSING,
        text_ol_color: Color | MISSING = MISSING,
        font_size: int | MISSING = MISSING,
        rotation: int | MISSING = MISSING,
        reference: Reference | MISSING = MISSING,
        pt_position: PtPosition | MISSING = MISSING,
        zoom_interval: ZoomInterval | MISSING = MISSING,
        scroll_speed: int | MISSING = MISSING,
        indicator: str | MISSING = MISSING,
        indicator_size: int | MISSING = MISSING,
        indicator_color: Color | MISSING = MISSING,
        indicator_bg: Color | MISSING = MISSING,
        indicator_ol: Color | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> OverlayCreated: ...
    async def add_text(
        self, request: AddTextRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> OverlayCreated:
        """Create a text overlay and return its identity.

        Creates a text overlay. Properties can be given at the same time.

        Access: operator.
        """
        return await self._run(OPS.add_text, request, kwargs, request_options)

    async def add_image(
        self,
        *,
        camera: int,
        overlay_path: str,
        position: Position | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> OverlayCreated:
        """Create an image overlay and return its identity.

        Properties can be given at the same time. Upload new images with the Overlay image API.

        Access: operator.
        """
        return await self._run(
            OPS.add_image, None, {"camera": camera, "overlay_path": overlay_path, "position": position}, request_options
        )

    @overload
    async def set_text(self, request: SetTextRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def set_text(
        self,
        /,
        *,
        identity: int,
        text: str | MISSING = MISSING,
        position: Position | MISSING = MISSING,
        text_color: Color | MISSING = MISSING,
        text_bg_color: Color | MISSING = MISSING,
        text_ol_color: Color | MISSING = MISSING,
        font_size: int | MISSING = MISSING,
        rotation: int | MISSING = MISSING,
        scroll_speed: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_text(
        self, request: SetTextRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change properties of a text overlay.

        Fields that are not given are not changed.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_text, request, kwargs, request_options)

    async def set_image(
        self,
        *,
        identity: int,
        overlay_path: str | MISSING = MISSING,
        position: Position | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Change properties of an image overlay.

        Fields that are not given are not changed.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_image,
            None,
            {"identity": identity, "overlay_path": overlay_path, "position": position},
            request_options,
        )

    async def list_overlays(
        self,
        *,
        camera: int | MISSING = MISSING,
        identity: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> OverlayList:
        """List the overlays that were created, with their properties, and the available image files.

        Overlay identities can change after a reboot, so check the identity with this method before updating
        or removing an overlay.

        Access: operator.
        """
        return await self._run(OPS.list_overlays, None, {"camera": camera, "identity": identity}, request_options)

    async def remove_overlay(self, *, identity: int, request_options: RequestOptions | None = None) -> None:
        """Remove an overlay.

        Removes the overlay identified by the given identity.

        Access: operator.
        """
        await self._run(OPS.remove_overlay, None, {"identity": identity}, request_options)

    async def get_overlay_capabilities(self, *, request_options: RequestOptions | None = None) -> OverlayCapabilities:
        """Get the number of overlay slots, slots per text and image overlay, and size limits.

        Access: operator.
        """
        return await self._run(OPS.get_overlay_capabilities, None, {}, request_options)
