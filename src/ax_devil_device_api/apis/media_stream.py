# GENERATED from specs/apis/network-video/media-cgi.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Fetch a live media stream (video and/or audio) packaged in a Matroska or MP4 container over HTTP via /axis-cgi/media.cgi.

Docs: https://developer.axis.com/vapix/network-video/media-stream-over-http/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, Stream
from .._runtime.driver import AsyncStreamResult, StreamResult
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class GetMediaStreamRequest(Model):
    audio: Literal[0, 1] | None = None
    """Specifies whether the audio should be included in the stream. Please note that you also need to enable audio support for the audio source with `AudioSource.A#.AudioSupport=yes`. Default: Audio.A#.Enabled."""
    audiobitrate: int | None = None
    """The audio bit rate. Default: AudioSource.A#.BitRate."""
    audiochannel: Literal[1] | None = None
    """The audio source. Please note that it can not be used together with `audiodeviceid` and `audioinputid`. Default: Audio.A#.Source."""
    audiocodec: Literal["aac", "opus"] | None = None
    """The audio codec. Default: aac. Default: 'aac'."""
    audiodeviceid: int | None = Field(default=None, ge=0)
    """The audio device ID. Please note that it can not be used together with `audiochannel`. Default: Audio.A#.Source."""
    audioinputid: int | None = Field(default=None, ge=0)
    """The audio input ID. Please note that it can not be used together with `audiochannel`. Default: Audio.A#.Source."""
    audionbrofchannels: Literal[1, 2] | None = None
    """Can be either mono or stereo sound. Default: Audio.A#.NbrOfChannels."""
    audiosamplerate: int | None = None
    """The audio sample rate. Default: AudioSource.A#.SampleRate."""
    camera: str | None = None
    """Selects the video source. Please note that this argument is only valid on Axis products with more than one video source, i.e. cameras with multiple view areas or video encoders with multiple video channels. Default: 1. Default: '1'."""
    container: Literal["matroska", "mp4"] | None = None
    """The container format. Default: matroska. Default: 'matroska'."""
    compression: int | None = Field(default=None, ge=0, le=100)
    """Adjusts the compression level of the image. Using a higher value corresponds to a higher compression, i.e. a lower quality and smaller image size. Default: Image.I#.Appearance.Compression."""
    fps: int | None = None
    """Selects the frame rate. `0` means unlimited. Default: Image.I#.Stream.FPS."""
    h264profile: Literal["high", "main", "baseline"] | None = None
    """The H.264 profile that should be used. Default: Image.I#.MPEG.H264.Profile. baseline is not available on all products; see Properties.Image.H264.Profiles for available values."""
    mirror: Literal[0, 1] | None = None
    """Specifies whether the image should be mirrored. Default: Image.I#.Appearance.MirrorEnabled."""
    color: Literal[0, 1] | None = None
    """Specifies whether the image should be in color or monochrome. Default: Image.I#.Appearance.ColorEnabled."""
    resolution: str | None = None
    """The resolution of the retrieved image. Use the parameter `Properties.Image.Resolutions` for a list of supported resolutions. Default: Image.I#.Appearance.Resolution."""
    rotation: Literal[0, 90, 180, 270] | None = None
    """Rotates the image clockwise."""
    streamprofile: str | None = None
    """The name of a saved stream profile."""
    squarepixel: Literal[0, 1] | None = None
    """Enable/disable square pixel (aspect ratio) correction. The device will adjust the aspect ratio to make it appear as intended if the parameter is set to 1. Default: Image.I#.Appearance SquarePixelEnabled."""
    video: Literal[0, 1] | None = None
    """Specify if video should be included in the stream. Default: 1. Default: 1."""
    videoabrmaxbitrate: int | None = None
    """The maximum bitrate when bitrate mode is ABR. Default: Image.I#.RateControl ABR.MaxBitrate."""
    videoabrretentiontime: int | None = None
    """Retention time when bitrate mode is ABR. Default: Image.I#.RateControl ABR.RetentionTime."""
    videoabrtargetbitrate: int | None = None
    """Target bitrate when bitrate mode is ABR. Default: Image.I#.RateControl ABR.TargetBitrate."""
    videobitratemode: Literal["abr", "mbr", "vbr"] | None = None
    """The bitrate mode. Default: Image.I#.RateControl Mode."""
    videobitratepriority: Literal["none", "framerate", "quality", "fullframerate"] | None = None
    """The bitrate priority. Default: Image.I#.RateControl Priority."""
    videocodec: Literal["h264", "h265"] | None = None
    """The video codec. Default: h264. Default: 'h264'."""
    videoframeskipmode: Literal["drop", "empty"] | None = None
    """Determines what should happen when either the rate controller or Zipstream skips a frame."""
    videomaxbitrate: int | None = None
    """The maximum bitrate when bitrate mode is MBR. Default: Image.I#.RateControl MaxBitrate."""
    videozfpsmode: Literal["fixed", "dynamic"] | None = None
    """The Zipstream fps mode."""
    videozgopmode: Literal["fixed", "dynamic"] | None = None
    """The Zipstream GOP mode."""
    videozmaxgoplength: int | None = None
    """The Zipstream maximum GOP length. Default: Image.I#.MPEG.ZMaxGopLength."""
    videozstrength: str | None = None
    """The Zipstream strength. Default: Image.I#.MPEG.ZStrength."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/media.cgi"

INFO = ApiInfo(
    id="media-cgi",
    name="Media stream over HTTP",
    family=Family.CGI,
    discovery=(ApiDiscovery("media-cgi"),),
    docs=("https://developer.axis.com/vapix/network-video/media-stream-over-http/",),
)


class OPS:
    get_media_stream = Operation(
        INFO,
        "get_media_stream",
        CgiBinding(
            PATH,
            args=(
                CgiArg("audio"),
                CgiArg("audiobitrate"),
                CgiArg("audiochannel"),
                CgiArg("audiocodec"),
                CgiArg("audiodeviceid"),
                CgiArg("audioinputid"),
                CgiArg("audionbrofchannels"),
                CgiArg("audiosamplerate"),
                CgiArg("camera"),
                CgiArg("container"),
                CgiArg("compression"),
                CgiArg("fps"),
                CgiArg("h264profile"),
                CgiArg("mirror"),
                CgiArg("color"),
                CgiArg("resolution"),
                CgiArg("rotation"),
                CgiArg("streamprofile"),
                CgiArg("squarepixel"),
                CgiArg("video"),
                CgiArg("videoabrmaxbitrate"),
                CgiArg("videoabrretentiontime"),
                CgiArg("videoabrtargetbitrate"),
                CgiArg("videobitratemode"),
                CgiArg("videobitratepriority"),
                CgiArg("videocodec"),
                CgiArg("videoframeskipmode"),
                CgiArg("videomaxbitrate"),
                CgiArg("videozfpsmode"),
                CgiArg("videozgopmode"),
                CgiArg("videozmaxgoplength"),
                CgiArg("videozstrength"),
            ),
            reply=Stream(),
            stream=True,
        ),
        params=GetMediaStreamRequest,
        access="viewer",
        effect="read",
        errors={
            400: ErrorCode("Bad Request"),
            401: ErrorCode("Unauthorized", "access_denied"),
            403: ErrorCode("Forbidden"),
            404: ErrorCode("Not Found", "not_found"),
            500: ErrorCode("Server Error"),
            503: ErrorCode("Service Unavailable", "unavailable"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class MediaStreamApi(SyncApi):
    """Media stream over HTTP (``media-cgi``)."""

    INFO = INFO

    @overload
    def get_media_stream(
        self, request: GetMediaStreamRequest, /, *, request_options: RequestOptions | None = None
    ) -> StreamResult[bytes]: ...
    @overload
    def get_media_stream(
        self,
        /,
        *,
        audio: Literal[0, 1] | MISSING = MISSING,
        audiobitrate: int | MISSING = MISSING,
        audiochannel: Literal[1] | MISSING = MISSING,
        audiocodec: Literal["aac", "opus"] | MISSING = MISSING,
        audiodeviceid: int | MISSING = MISSING,
        audioinputid: int | MISSING = MISSING,
        audionbrofchannels: Literal[1, 2] | MISSING = MISSING,
        audiosamplerate: int | MISSING = MISSING,
        camera: str | MISSING = MISSING,
        container: Literal["matroska", "mp4"] | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        fps: int | MISSING = MISSING,
        h264profile: Literal["high", "main", "baseline"] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        resolution: str | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        streamprofile: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        video: Literal[0, 1] | MISSING = MISSING,
        videoabrmaxbitrate: int | MISSING = MISSING,
        videoabrretentiontime: int | MISSING = MISSING,
        videoabrtargetbitrate: int | MISSING = MISSING,
        videobitratemode: Literal["abr", "mbr", "vbr"] | MISSING = MISSING,
        videobitratepriority: Literal["none", "framerate", "quality", "fullframerate"] | MISSING = MISSING,
        videocodec: Literal["h264", "h265"] | MISSING = MISSING,
        videoframeskipmode: Literal["drop", "empty"] | MISSING = MISSING,
        videomaxbitrate: int | MISSING = MISSING,
        videozfpsmode: Literal["fixed", "dynamic"] | MISSING = MISSING,
        videozgopmode: Literal["fixed", "dynamic"] | MISSING = MISSING,
        videozmaxgoplength: int | MISSING = MISSING,
        videozstrength: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StreamResult[bytes]: ...
    def get_media_stream(
        self,
        request: GetMediaStreamRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> StreamResult[bytes]:
        """Fetch a media stream packaged in a specific container format.

        Returns the media as a stream of byte chunks (Matroska by default, or MP4 with container=mp4);
        iterate the result inside a with block and write the chunks to a file or hand them to a player. The
        content type is video/x-matroska, video/mp4, audio/x-matroska or audio/mp4 followed by
        codecs=<codecs> (RFC 6381); the response also carries the Video-Metadata-Transform and Video-Sensor-
        Transform headers.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return self._run(OPS.get_media_stream, request, kwargs, request_options)


class AsyncMediaStreamApi(AsyncApi):
    """Media stream over HTTP (``media-cgi``)."""

    INFO = INFO

    @overload
    async def get_media_stream(
        self, request: GetMediaStreamRequest, /, *, request_options: RequestOptions | None = None
    ) -> AsyncStreamResult[bytes]: ...
    @overload
    async def get_media_stream(
        self,
        /,
        *,
        audio: Literal[0, 1] | MISSING = MISSING,
        audiobitrate: int | MISSING = MISSING,
        audiochannel: Literal[1] | MISSING = MISSING,
        audiocodec: Literal["aac", "opus"] | MISSING = MISSING,
        audiodeviceid: int | MISSING = MISSING,
        audioinputid: int | MISSING = MISSING,
        audionbrofchannels: Literal[1, 2] | MISSING = MISSING,
        audiosamplerate: int | MISSING = MISSING,
        camera: str | MISSING = MISSING,
        container: Literal["matroska", "mp4"] | MISSING = MISSING,
        compression: int | MISSING = MISSING,
        fps: int | MISSING = MISSING,
        h264profile: Literal["high", "main", "baseline"] | MISSING = MISSING,
        mirror: Literal[0, 1] | MISSING = MISSING,
        color: Literal[0, 1] | MISSING = MISSING,
        resolution: str | MISSING = MISSING,
        rotation: Literal[0, 90, 180, 270] | MISSING = MISSING,
        streamprofile: str | MISSING = MISSING,
        squarepixel: Literal[0, 1] | MISSING = MISSING,
        video: Literal[0, 1] | MISSING = MISSING,
        videoabrmaxbitrate: int | MISSING = MISSING,
        videoabrretentiontime: int | MISSING = MISSING,
        videoabrtargetbitrate: int | MISSING = MISSING,
        videobitratemode: Literal["abr", "mbr", "vbr"] | MISSING = MISSING,
        videobitratepriority: Literal["none", "framerate", "quality", "fullframerate"] | MISSING = MISSING,
        videocodec: Literal["h264", "h265"] | MISSING = MISSING,
        videoframeskipmode: Literal["drop", "empty"] | MISSING = MISSING,
        videomaxbitrate: int | MISSING = MISSING,
        videozfpsmode: Literal["fixed", "dynamic"] | MISSING = MISSING,
        videozgopmode: Literal["fixed", "dynamic"] | MISSING = MISSING,
        videozmaxgoplength: int | MISSING = MISSING,
        videozstrength: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AsyncStreamResult[bytes]: ...
    async def get_media_stream(
        self,
        request: GetMediaStreamRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AsyncStreamResult[bytes]:
        """Fetch a media stream packaged in a specific container format.

        Returns the media as a stream of byte chunks (Matroska by default, or MP4 with container=mp4);
        iterate the result inside a with block and write the chunks to a file or hand them to a player. The
        content type is video/x-matroska, video/mp4, audio/x-matroska or audio/mp4 followed by
        codecs=<codecs> (RFC 6381); the response also carries the Video-Metadata-Transform and Video-Sensor-
        Transform headers.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return await self._run(OPS.get_media_stream, request, kwargs, request_options)
