# GENERATED from specs/apis/network-video/video-streaming.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""HTTP image requests: JPEG, AVIF and bitmap snapshots, the image size, video status and the always-multicast SDP.

Docs: https://developer.axis.com/vapix/network-video/video-streaming/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import Binary, CgiArg, CgiBinding, Stream, Text, TextKv
from .._runtime.driver import AsyncStreamResult, StreamResult
from .._streams import Part
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Camera = Annotated[str, Field(pattern="^([0-9]+|quad)$")]
Overlays = Literal["all", "text", "image", "application", "off", "all-sync", "application-sync"]


class ImageRequest(Model):
    """The image request arguments; unless given, the defaults configured on the device apply."""

    resolution: str | None = None
    """Resolution of the returned image, for example ``320x240`` or ``QCIF``. Product and release dependent; see ``Properties.Image.Resolution``."""
    camera: Camera | None = None
    compression: int | None = Field(default=None, ge=0, le=100)
    """Compression level; higher values mean higher compression (lower quality, smaller image). Internally mapped and product dependent."""
    color: Literal[0, 1] | None = None
    """``0`` black and white, ``1`` color."""
    rotation: Literal[0, 90, 180, 270] | None = None
    """Rotate the image clockwise. The alternatives are defined by ``Properties.Image.Rotation``; 90, 180 and 270 are product and release dependent. Not applicable to AVIF."""
    mirror: Literal[0, 1] | None = None
    """``0`` no horizontal mirroring, ``1`` mirror the image horizontally."""
    palette: str | None = None
    """Thermal cameras only. The color palette to use, applicable if ``Properties.Image.Palette.StreamPalette`` is ``yes`` or does not exist. See thermal-color-palettes."""
    squarepixel: Literal[0, 1] | None = None
    """``1`` adjusts the aspect ratio to appear as intended (square pixel correction). Not applicable to AVIF."""
    overlays: Overlays | None = None


class JpegRequest(Model):
    """The image request arguments plus the text overlay options shown in the JPEG examples."""

    resolution: str | None = None
    """Resolution of the returned image, for example ``320x240`` or ``QCIF``. Product and release dependent; see ``Properties.Image.Resolution``."""
    camera: Camera | None = None
    compression: int | None = Field(default=None, ge=0, le=100)
    """Compression level; higher values mean higher compression (lower quality, smaller image). Internally mapped and product dependent."""
    color: Literal[0, 1] | None = None
    """``0`` black and white, ``1`` color."""
    rotation: Literal[0, 90, 180, 270] | None = None
    """Rotate the image clockwise. The alternatives are defined by ``Properties.Image.Rotation``; 90, 180 and 270 are product and release dependent. Not applicable to AVIF."""
    mirror: Literal[0, 1] | None = None
    """``0`` no horizontal mirroring, ``1`` mirror the image horizontally."""
    palette: str | None = None
    """Thermal cameras only. The color palette to use, applicable if ``Properties.Image.Palette.StreamPalette`` is ``yes`` or does not exist. See thermal-color-palettes."""
    squarepixel: Literal[0, 1] | None = None
    """``1`` adjusts the aspect ratio to appear as intended (square pixel correction). Not applicable to AVIF."""
    overlays: Overlays | None = None
    text: int | None = Field(default=None, ge=0, le=1)
    """Set to ``1`` to display text on the image. Defined in the Image API URL options."""
    textstring: str | None = None
    """The text to display, for example ``My Camera``. Defined in the Image API URL options."""


class MjpegRequest(Model):
    """The image request arguments plus the stream profile and the stream length. A value given after ``streamprofile`` overrides the saved one."""

    resolution: str | None = None
    """Resolution of the returned image, for example ``320x240`` or ``QCIF``. Product and release dependent; see ``Properties.Image.Resolution``."""
    camera: Camera | None = None
    compression: int | None = Field(default=None, ge=0, le=100)
    """Compression level; higher values mean higher compression (lower quality, smaller image). Internally mapped and product dependent."""
    color: Literal[0, 1] | None = None
    """``0`` black and white, ``1`` color."""
    rotation: Literal[0, 90, 180, 270] | None = None
    """Rotate the image clockwise. The alternatives are defined by ``Properties.Image.Rotation``; 90, 180 and 270 are product and release dependent. Not applicable to AVIF."""
    mirror: Literal[0, 1] | None = None
    """``0`` no horizontal mirroring, ``1`` mirror the image horizontally."""
    palette: str | None = None
    """Thermal cameras only. The color palette to use, applicable if ``Properties.Image.Palette.StreamPalette`` is ``yes`` or does not exist. See thermal-color-palettes."""
    squarepixel: Literal[0, 1] | None = None
    """``1`` adjusts the aspect ratio to appear as intended (square pixel correction). Not applicable to AVIF."""
    overlays: Overlays | None = None
    streamprofile: str | None = None
    """Name of a saved stream profile (``StreamProfile.S#.Name``)."""
    duration: int | None = Field(default=None, ge=0)
    """For how many seconds the video is generated and pushed to the client. ``0`` is unlimited."""
    nbrofframes: int | None = Field(default=None, ge=0)
    """How many frames the device generates and pushes. ``0`` is unlimited."""
    fps: int | None = Field(default=None, ge=0)
    """The frame rate. ``0`` is unlimited."""


class ImageSize(Model):
    width: int = Field(validation_alias="image width", serialization_alias="image width")
    """Image width in pixels."""
    height: int = Field(validation_alias="image height", serialization_alias="image height")
    """Image height in pixels."""


class VideoStatusRequest(Model):
    status: list[Annotated[int, Field(ge=1)]]
    """The video sources to check, 1 and up. The number of video sources is given by ``ImageSource.NbrOfSources``."""


class SdpRequest(Model):
    camera: Camera | None = None


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/imagesize.cgi"

INFO = ApiInfo(
    id="video-streaming",
    name="Video streaming over HTTP",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    requires_firmware="5.00",
    docs=("https://developer.axis.com/vapix/network-video/video-streaming/",),
)


class OPS:
    get_image_size = Operation(
        INFO,
        "get_image_size",
        CgiBinding(
            PATH,
            args=(
                CgiArg("resolution"),
                CgiArg("camera"),
                CgiArg("compression"),
                CgiArg("color"),
                CgiArg("rotation"),
                CgiArg("mirror"),
                CgiArg("palette"),
                CgiArg("squarepixel"),
                CgiArg("overlays"),
            ),
            reply=TextKv(),
            accept="text/plain",
        ),
        params=ImageRequest,
        result=ImageSize,
        access="viewer",
        effect="read",
    )
    get_video_status = Operation(
        INFO,
        "get_video_status",
        CgiBinding(
            "/axis-cgi/videostatus.cgi", args=(CgiArg("status", style="csv"),), reply=TextKv(), accept="text/plain"
        ),
        params=VideoStatusRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    get_bitmap = Operation(
        INFO,
        "get_bitmap",
        CgiBinding(
            "/axis-cgi/bitmap/image.bmp",
            args=(
                CgiArg("resolution"),
                CgiArg("camera"),
                CgiArg("compression"),
                CgiArg("color"),
                CgiArg("rotation"),
                CgiArg("mirror"),
                CgiArg("palette"),
                CgiArg("squarepixel"),
                CgiArg("overlays"),
            ),
            reply=Binary(media_types=("image/bitmap",)),
        ),
        params=ImageRequest,
        result=bytes,
        access="viewer",
        effect="read",
    )
    get_avif = Operation(
        INFO,
        "get_avif",
        CgiBinding(
            "/axis-cgi/avif/image.cgi",
            args=(
                CgiArg("resolution"),
                CgiArg("camera"),
                CgiArg("compression"),
                CgiArg("color"),
                CgiArg("rotation"),
                CgiArg("mirror"),
                CgiArg("palette"),
                CgiArg("squarepixel"),
                CgiArg("overlays"),
            ),
            reply=Binary(media_types=("image/avif",)),
        ),
        params=ImageRequest,
        result=bytes,
        access="viewer",
        effect="read",
    )
    get_jpeg = Operation(
        INFO,
        "get_jpeg",
        CgiBinding(
            "/axis-cgi/jpg/image.cgi",
            args=(
                CgiArg("resolution"),
                CgiArg("camera"),
                CgiArg("compression"),
                CgiArg("color"),
                CgiArg("rotation"),
                CgiArg("mirror"),
                CgiArg("palette"),
                CgiArg("squarepixel"),
                CgiArg("overlays"),
                CgiArg("text"),
                CgiArg("textstring"),
            ),
            reply=Binary(media_types=("image/jpeg",)),
        ),
        params=JpegRequest,
        result=bytes,
        access="viewer",
        effect="read",
    )
    get_mjpeg_stream = Operation(
        INFO,
        "get_mjpeg_stream",
        CgiBinding(
            "/axis-cgi/mjpg/video.cgi",
            args=(
                CgiArg("resolution"),
                CgiArg("camera"),
                CgiArg("compression"),
                CgiArg("color"),
                CgiArg("rotation"),
                CgiArg("mirror"),
                CgiArg("palette"),
                CgiArg("squarepixel"),
                CgiArg("overlays"),
                CgiArg("streamprofile"),
                CgiArg("duration"),
                CgiArg("nbrofframes"),
                CgiArg("fps"),
            ),
            reply=Stream("mjpeg"),
            stream=True,
        ),
        params=MjpegRequest,
        access="viewer",
        effect="read",
    )
    get_always_multicast_sdp = Operation(
        INFO,
        "get_always_multicast_sdp",
        CgiBinding("/axis-cgi/alwaysmulti.sdp", args=(CgiArg("camera"),), reply=Text()),
        params=SdpRequest,
        result=str,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class VideoStreamingApi(SyncApi):
    """Video streaming over HTTP (``video-streaming``)."""

    INFO = INFO

    @overload
    def get_image_size(
        self, request: ImageRequest, /, *, request_options: RequestOptions | None = None
    ) -> ImageSize: ...
    @overload
    def get_image_size(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ImageSize: ...
    def get_image_size(
        self, request: ImageRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ImageSize:
        """Retrieve the real image resolution, for example to verify the resolution after rotation.

        Accepts the image request arguments. A product that does not support the requested resolution
        replies with an error message in the body (``<!-- Camera 1 not available. -->`` when ``camera`` is
        given), with HTTP 200. The device also accepts POST.

        Access: viewer.
        """
        return self._run(OPS.get_image_size, request, kwargs, request_options)

    def get_video_status(
        self, status: list[Annotated[int, Field(ge=1)]], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Retrieve whether there is an analog video signal on a video encoder's video sources, as ``{"Video 1": "video"}``.

        Each value is ``video`` or ``no video`` (no analog video signal), with a leading space.

        Access: viewer.
        """
        return self._run(OPS.get_video_status, None, {"status": status}, request_options)

    @overload
    def get_bitmap(self, request: ImageRequest, /, *, request_options: RequestOptions | None = None) -> bytes: ...
    @overload
    def get_bitmap(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes: ...
    def get_bitmap(
        self, request: ImageRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> bytes:
        """Request a bitmap image (deprecated; not supported on AXIS OS 11.0 and later).

        Deprecated. Supported if ``Properties.Image.Format`` lists ``bitmap``.

        Access: viewer.
        """
        return self._run(OPS.get_bitmap, request, kwargs, request_options)

    @overload
    def get_avif(self, request: ImageRequest, /, *, request_options: RequestOptions | None = None) -> bytes: ...
    @overload
    def get_avif(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes: ...
    def get_avif(
        self, request: ImageRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> bytes:
        """Retrieve an AVIF image (snapshot).

        Extensive use can affect product performance. ``rotation`` and ``squarepixel`` do not apply to AVIF.

        Access: viewer.
        """
        return self._run(OPS.get_avif, request, kwargs, request_options)

    @overload
    def get_jpeg(self, request: JpegRequest, /, *, request_options: RequestOptions | None = None) -> bytes: ...
    @overload
    def get_jpeg(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        text: int | MISSING = MISSING,
        textstring: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes: ...
    def get_jpeg(
        self, request: JpegRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> bytes:
        """Retrieve a JPEG image (snapshot).

        Extensive use can affect product performance.

        Access: viewer.
        """
        return self._run(OPS.get_jpeg, request, kwargs, request_options)

    @overload
    def get_mjpeg_stream(
        self, request: MjpegRequest, /, *, request_options: RequestOptions | None = None
    ) -> StreamResult[Part]: ...
    @overload
    def get_mjpeg_stream(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        streamprofile: str | MISSING = MISSING,
        duration: int | MISSING = MISSING,
        nbrofframes: int | MISSING = MISSING,
        fps: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StreamResult[Part]: ...
    def get_mjpeg_stream(
        self, request: MjpegRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> StreamResult[Part]:
        """Open a Motion JPEG stream.

        Returns a stream of ``multipart/x-mixed-replace`` parts, one JPEG per part. Arguments such as
        resolution and compression are given in the request, or taken from a saved stream profile. Use the
        result as a context manager.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return self._run(OPS.get_mjpeg_stream, request, kwargs, request_options)

    def get_always_multicast_sdp(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Retrieve the Session Description Protocol (SDP) of the always-multicast stream of a video source.

        Requires ``Network.RTP.R0.AlwaysMulticastVideo=yes`` and AXIS OS 5.40 or later. Viewer, operator and
        admin can make the request. The SDP tells a client which multicast address and port to join.

        Access: viewer.
        """
        return self._run(OPS.get_always_multicast_sdp, None, {"camera": camera}, request_options)


class AsyncVideoStreamingApi(AsyncApi):
    """Video streaming over HTTP (``video-streaming``)."""

    INFO = INFO

    @overload
    async def get_image_size(
        self, request: ImageRequest, /, *, request_options: RequestOptions | None = None
    ) -> ImageSize: ...
    @overload
    async def get_image_size(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ImageSize: ...
    async def get_image_size(
        self, request: ImageRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ImageSize:
        """Retrieve the real image resolution, for example to verify the resolution after rotation.

        Accepts the image request arguments. A product that does not support the requested resolution
        replies with an error message in the body (``<!-- Camera 1 not available. -->`` when ``camera`` is
        given), with HTTP 200. The device also accepts POST.

        Access: viewer.
        """
        return await self._run(OPS.get_image_size, request, kwargs, request_options)

    async def get_video_status(
        self, status: list[Annotated[int, Field(ge=1)]], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Retrieve whether there is an analog video signal on a video encoder's video sources, as ``{"Video 1": "video"}``.

        Each value is ``video`` or ``no video`` (no analog video signal), with a leading space.

        Access: viewer.
        """
        return await self._run(OPS.get_video_status, None, {"status": status}, request_options)

    @overload
    async def get_bitmap(self, request: ImageRequest, /, *, request_options: RequestOptions | None = None) -> bytes: ...
    @overload
    async def get_bitmap(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes: ...
    async def get_bitmap(
        self, request: ImageRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> bytes:
        """Request a bitmap image (deprecated; not supported on AXIS OS 11.0 and later).

        Deprecated. Supported if ``Properties.Image.Format`` lists ``bitmap``.

        Access: viewer.
        """
        return await self._run(OPS.get_bitmap, request, kwargs, request_options)

    @overload
    async def get_avif(self, request: ImageRequest, /, *, request_options: RequestOptions | None = None) -> bytes: ...
    @overload
    async def get_avif(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes: ...
    async def get_avif(
        self, request: ImageRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> bytes:
        """Retrieve an AVIF image (snapshot).

        Extensive use can affect product performance. ``rotation`` and ``squarepixel`` do not apply to AVIF.

        Access: viewer.
        """
        return await self._run(OPS.get_avif, request, kwargs, request_options)

    @overload
    async def get_jpeg(self, request: JpegRequest, /, *, request_options: RequestOptions | None = None) -> bytes: ...
    @overload
    async def get_jpeg(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        text: int | MISSING = MISSING,
        textstring: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes: ...
    async def get_jpeg(
        self, request: JpegRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> bytes:
        """Retrieve a JPEG image (snapshot).

        Extensive use can affect product performance.

        Access: viewer.
        """
        return await self._run(OPS.get_jpeg, request, kwargs, request_options)

    @overload
    async def get_mjpeg_stream(
        self, request: MjpegRequest, /, *, request_options: RequestOptions | None = None
    ) -> AsyncStreamResult[Part]: ...
    @overload
    async def get_mjpeg_stream(
        self,
        /,
        *,
        resolution: str | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        overlays: Overlays | MISSING = MISSING,
        streamprofile: str | MISSING = MISSING,
        duration: int | MISSING = MISSING,
        nbrofframes: int | MISSING = MISSING,
        fps: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AsyncStreamResult[Part]: ...
    async def get_mjpeg_stream(
        self, request: MjpegRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AsyncStreamResult[Part]:
        """Open a Motion JPEG stream.

        Returns a stream of ``multipart/x-mixed-replace`` parts, one JPEG per part. Arguments such as
        resolution and compression are given in the request, or taken from a saved stream profile. Use the
        result as a context manager.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return await self._run(OPS.get_mjpeg_stream, request, kwargs, request_options)

    async def get_always_multicast_sdp(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Retrieve the Session Description Protocol (SDP) of the always-multicast stream of a video source.

        Requires ``Network.RTP.R0.AlwaysMulticastVideo=yes`` and AXIS OS 5.40 or later. Viewer, operator and
        admin can make the request. The SDP tells a client which multicast address and port to join.

        Access: viewer.
        """
        return await self._run(OPS.get_always_multicast_sdp, None, {"camera": camera}, request_options)
