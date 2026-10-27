# GENERATED from specs/apis/network-video/overlay-image.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage the overlay images on the camera and the default image (listing, validating, deleting).

Docs: https://developer.axis.com/vapix/network-video/overlay-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ImageFormat = Literal["bmp", "jpeg", "png", "svg"]


class SupportedFormats(Model):
    formats: list[ImageFormat]
    """List of supported image formats."""


class ValidateImageHeaderRequest(Model):
    type: ImageFormat
    """The image type. One of the formats returned by ``supported_formats``."""
    width: int
    """The width of the image."""
    height: int
    """The height of the image."""


class ImageSupport(Model):
    supports_alpha: bool = Field(validation_alias="supportsAlpha", serialization_alias="supportsAlpha")
    """Whether an alpha value may be specified for this image."""
    supports_scaling: bool = Field(validation_alias="supportsScaling", serialization_alias="supportsScaling")
    """Whether scale-to-resolution is supported for this image."""


class OverlayImageFile(Model):
    path: str
    """The path identifying the image."""
    scale_with_resolution: bool = Field(
        validation_alias="scaleWithResolution", serialization_alias="scaleWithResolution"
    )
    """Whether the image is scaled with the stream resolution."""


class ImageList(Model):
    files: list[OverlayImageFile]
    """The available images."""


class ImagePathRequest(Model):
    path: str
    """The path identifying the image."""


class ImagePath(Model):
    path: str
    """The path that should be used when referring to the image."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/manageoverlayimages.cgi"

INFO = ApiInfo(
    id="overlay-image",
    name="Overlay image API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("overlayimage"),),
    docs=("https://developer.axis.com/vapix/network-video/overlay-api/",),
    errors={
        1000: ErrorCode("Internal error.", "internal"),
        1001: ErrorCode("The requested API version is not supported.", "unsupported"),
        1002: ErrorCode("Invalid method.", "invalid_argument"),
        1003: ErrorCode("Invalid parameter.", "invalid_argument"),
        1004: ErrorCode("The provided input was invalid.", "invalid_argument"),
        1005: ErrorCode("Image size is too big.", "invalid_argument"),
        1006: ErrorCode("Unsupported image format.", "unsupported"),
        1007: ErrorCode("Not enough space left on the device.", "unavailable"),
        1008: ErrorCode("Alpha is not supported.", "unsupported"),
        1009: ErrorCode("Scale-to-resolution is not supported.", "unsupported"),
        1010: ErrorCode("Image already exists."),
        1011: ErrorCode("Image is being used by a dynamic overlay."),
        1012: ErrorCode("Image is being used by a legacy overlay."),
        1013: ErrorCode("Image is being used as default image."),
        1014: ErrorCode("Image is being used by an overlay."),
    },
)


class OPS:
    supported_formats = Operation(
        INFO,
        "supported_formats",
        JsonRpcBinding("supportedFormats", PATH),
        result=SupportedFormats,
        access="operator",
        effect="read",
    )
    validate_image_header = Operation(
        INFO,
        "validate_image_header",
        JsonRpcBinding("validateImageHeader", PATH),
        params=ValidateImageHeaderRequest,
        result=ImageSupport,
        access="operator",
        effect="read",
    )
    list_images = Operation(
        INFO, "list_images", JsonRpcBinding("listImages", PATH), result=ImageList, access="operator", effect="read"
    )
    delete_image = Operation(
        INFO,
        "delete_image",
        JsonRpcBinding("deleteImage", PATH),
        params=ImagePathRequest,
        access="operator",
        effect="write",
        write="delete",
        errors={
            1011: ErrorCode("Image is being used by a dynamic overlay."),
            1012: ErrorCode("Image is being used by a legacy overlay."),
            1013: ErrorCode("Image is being used as default image."),
            1014: ErrorCode("Image is being used by an overlay."),
        },
    )
    get_default_image = Operation(
        INFO,
        "get_default_image",
        JsonRpcBinding("getDefaultImage", PATH),
        result=ImagePath,
        access="operator",
        effect="read",
    )
    set_default_image = Operation(
        INFO,
        "set_default_image",
        JsonRpcBinding("setDefaultImage", PATH),
        params=ImagePathRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class OverlayImageApi(SyncApi):
    """Overlay image API (``overlay-image``, version 1)."""

    INFO = INFO

    def supported_formats(self, *, request_options: RequestOptions | None = None) -> SupportedFormats:
        """Get the image formats the camera supports. Access: operator."""
        return self._run(OPS.supported_formats, None, {}, request_options)

    def validate_image_header(
        self, *, type: ImageFormat, width: int, height: int, request_options: RequestOptions | None = None
    ) -> ImageSupport:
        """Check whether an image is supported, based on its header data.

        Checks that an image with these properties is supported, has an acceptable size and fits in the
        device memory. Invalid parameters give an error response whose code tells what is wrong.

        Access: operator.
        """
        return self._run(
            OPS.validate_image_header, None, {"type": type, "width": width, "height": height}, request_options
        )

    def list_images(self, *, request_options: RequestOptions | None = None) -> ImageList:
        """List all overlay images on the camera. Access: operator."""
        return self._run(OPS.list_images, None, {}, request_options)

    def delete_image(self, path: str, *, request_options: RequestOptions | None = None) -> None:
        """Delete an overlay image. Access: operator."""
        self._run(OPS.delete_image, None, {"path": path}, request_options)

    def get_default_image(self, *, request_options: RequestOptions | None = None) -> ImagePath:
        """Get the currently configured default image. Access: operator."""
        return self._run(OPS.get_default_image, None, {}, request_options)

    def set_default_image(self, path: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the default overlay image. Changes only the fields given. Access: operator."""
        self._run(OPS.set_default_image, None, {"path": path}, request_options)


class AsyncOverlayImageApi(AsyncApi):
    """Overlay image API (``overlay-image``, version 1)."""

    INFO = INFO

    async def supported_formats(self, *, request_options: RequestOptions | None = None) -> SupportedFormats:
        """Get the image formats the camera supports. Access: operator."""
        return await self._run(OPS.supported_formats, None, {}, request_options)

    async def validate_image_header(
        self, *, type: ImageFormat, width: int, height: int, request_options: RequestOptions | None = None
    ) -> ImageSupport:
        """Check whether an image is supported, based on its header data.

        Checks that an image with these properties is supported, has an acceptable size and fits in the
        device memory. Invalid parameters give an error response whose code tells what is wrong.

        Access: operator.
        """
        return await self._run(
            OPS.validate_image_header, None, {"type": type, "width": width, "height": height}, request_options
        )

    async def list_images(self, *, request_options: RequestOptions | None = None) -> ImageList:
        """List all overlay images on the camera. Access: operator."""
        return await self._run(OPS.list_images, None, {}, request_options)

    async def delete_image(self, path: str, *, request_options: RequestOptions | None = None) -> None:
        """Delete an overlay image. Access: operator."""
        await self._run(OPS.delete_image, None, {"path": path}, request_options)

    async def get_default_image(self, *, request_options: RequestOptions | None = None) -> ImagePath:
        """Get the currently configured default image. Access: operator."""
        return await self._run(OPS.get_default_image, None, {}, request_options)

    async def set_default_image(self, path: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the default overlay image. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_default_image, None, {"path": path}, request_options)
