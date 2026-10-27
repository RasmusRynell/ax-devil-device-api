# GENERATED from specs/apis/audio-systems/audio-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Receive (receive.cgi) and transmit (transmit.cgi) audio over HTTP, and build RTSP URLs with audio. Audio settings are the Audio and AudioSource parameter groups (Parameter management API).

Docs: https://developer.axis.com/vapix/audio-systems/audio-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._http.upload import UploadSource, UploadSpec
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Stream, Text
from .._runtime.driver import AsyncStreamResult, StreamResult
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

AudioMimeType = Literal[
    "audio/basic",
    "audio/axis-mulaw-128",
    "audio/G726-32",
    "audio/G726-24",
    "audio/mpeg4-generic",
    "audio/opus",
    "audio/L24",
]


class ReceiveAudioRequest(Model):
    audio: Literal[0, 1] | None = None
    """Enable (1) or disable (0) audio."""
    audiobitrate: int | None = Field(default=None, ge=8000)
    """The audio bit rate in bps. (unit=bps)"""
    audiocodec: Literal["g711", "g726", "aac", "opus", "lpcm"] | None = None
    """The audio codec type."""
    audiosamplerate: int | None = Field(default=None, ge=8000)
    """The audio sample rate in Hz. (unit=Hz)"""
    camera: int | None = Field(default=None, ge=1)
    """Select the audio configuration in Audio.A#. camera=1 -> Audio.A0. Number of configurations is product-dependent."""
    httptype: Literal["singlepart", "multipart"] | None = None
    """Choose streaming method. Some proxies require multipart. Default: parameter Audio.A#.HTTPMessageType."""
    audiochannel: int | None = Field(default=None, ge=1)
    """Select the audio source in AudioSource.A#. audiochannel=2 -> AudioSource.A1. Mutually exclusive with audiodeviceid+audioinputid."""
    audiodeviceid: str | None = None
    """The audio device ID (id from Audio Device Control API). Supported only if audio-device-control status is official in API discovery. Mutually exclusive with audiochannel."""
    audioinputid: str | None = None
    """The audio device input ID (id from Audio Device Control API). Same support condition as audiodeviceid."""
    audionbrofchannels: int | None = Field(default=None, ge=1)
    """The number of audio channels."""


class TransmitAudioRequest(Model):
    audio: UploadSource = Field(exclude=True, repr=False)
    """The audio data."""
    content_type: AudioMimeType | None = None
    """The audio format of the data (the Content-Type of the request). Default: the content type of an Upload, else audio/basic."""
    audiodeviceid: str | None = None
    """The audio device ID (id from Audio Device Control API). Supported only if audio-device-control status is official in API discovery."""
    audiooutputid: str | None = None
    """The audio device output ID. Same support condition as audiodeviceid."""


class RtspAudioStreamUrlRequest(Model):
    videocodec: str | None = None
    """The video codec of the media stream, for example h264 (the docs example requests video and audio)."""
    audio: Literal[0, 1] | None = None
    """1 includes audio, 0 excludes it even when the parameters enable it."""
    camera: int | None = Field(default=None, ge=1)
    """Video source and audio configuration (Audio.A#; camera=1 is Audio.A0)."""
    audiochannel: int | None = Field(default=None, ge=1)
    """The audio source (AudioSource.A#; audiochannel=2 is AudioSource.A1). Only when AudioSource.A#.AudioSupport is enabled."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/audio/receive.cgi"

INFO = ApiInfo(
    id="audio-api",
    name="Audio API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.Audio.Audio", "yes"), ApiDiscovery("audio-device-control")),
    requires_firmware="5.00",
    docs=("https://developer.axis.com/vapix/audio-systems/audio-api/",),
    errors={
        400: ErrorCode(
            "Bad request. The request had a bad syntax, or could not be implemented (an invalid parameter value).",
            "invalid_argument",
        ),
        405: ErrorCode("Method not allowed. The GET/POST is not allowed in the current (duplex) mode.", "unsupported"),
        415: ErrorCode(
            "Unsupported media type. The request is not in an acceptable format and can not be processed.",
            "invalid_argument",
        ),
        503: ErrorCode("Service unavailable. The maximum number of clients are already connected.", "unavailable"),
    },
)


class OPS:
    receive_audio = Operation(
        INFO,
        "receive_audio",
        CgiBinding(
            PATH,
            args=(
                CgiArg("audio"),
                CgiArg("audiobitrate"),
                CgiArg("audiocodec"),
                CgiArg("audiosamplerate"),
                CgiArg("camera"),
                CgiArg("httptype"),
                CgiArg("audiochannel"),
                CgiArg("audiodeviceid"),
                CgiArg("audioinputid"),
                CgiArg("audionbrofchannels"),
            ),
            reply=Stream(),
            stream=True,
        ),
        params=ReceiveAudioRequest,
        access="viewer",
        effect="read",
    )
    transmit_audio = Operation(
        INFO,
        "transmit_audio",
        CgiBinding(
            "/axis-cgi/audio/transmit.cgi",
            method="POST",
            encoding="body",
            args=(CgiArg("audiodeviceid"), CgiArg("audiooutputid")),
            body_field="audio",
            content_type_field="content_type",
            uploads=(UploadSpec("audio", content_type="audio/basic"),),
            reply=Text(),
        ),
        params=TransmitAudioRequest,
        result=str,
        access="viewer",
        effect="action",
    )
    rtsp_audio_stream_url = Operation(
        INFO, "rtsp_audio_stream_url", RtspBinding(), params=RtspAudioStreamUrlRequest, access="viewer", effect="read"
    )


# ---------------------------------------------------------------------------
# API classes


class AudioApi(SyncApi):
    """Audio API (``audio-api``)."""

    INFO = INFO

    @overload
    def receive_audio(
        self, request: ReceiveAudioRequest, /, *, request_options: RequestOptions | None = None
    ) -> StreamResult[bytes]: ...
    @overload
    def receive_audio(
        self,
        /,
        *,
        audio: Literal[0, 1] | MISSING = MISSING,
        audiobitrate: int | MISSING = MISSING,
        audiocodec: Literal["g711", "g726", "aac", "opus", "lpcm"] | MISSING = MISSING,
        audiosamplerate: int | MISSING = MISSING,
        camera: int | MISSING = MISSING,
        httptype: Literal["singlepart", "multipart"] | MISSING = MISSING,
        audiochannel: int | MISSING = MISSING,
        audiodeviceid: str | MISSING = MISSING,
        audioinputid: str | MISSING = MISSING,
        audionbrofchannels: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StreamResult[bytes]: ...
    def receive_audio(
        self,
        request: ReceiveAudioRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> StreamResult[bytes]:
        """Request and configure an audio stream from the device (singlepart or multipart).

        Singlepart (default) streams a continuous flow of audio packets in the codec's MIME type, with the
        content type only set at the start of the connection; multipart (`httptype=multipart`) answers
        `multipart/x-mixed-replace` with one audio block per part (G.711 512 bytes, G.726 32 kbit/s 256
        bytes, G.726 24 kbit/s 192 bytes; AAC is not supported). The stream is returned as raw bytes, also
        for multipart, so split the parts yourself.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return self._run(OPS.receive_audio, request, kwargs, request_options)

    def transmit_audio(
        self,
        *,
        audio: UploadSource,
        content_type: AudioMimeType | MISSING = MISSING,
        audiodeviceid: str | MISSING = MISSING,
        audiooutputid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Transmit an audio stream to the device (POST audio data to transmit.cgi).

        Sends the audio as the request body. The content type is set once at the start of the connection and
        defaults to `audio/basic` (G.711 mu-law); pass `content_type` for another format (for example
        `audio/axis-mulaw-128`, `audio/G726-32`, `audio/opus`). A content type on an `Upload` is used when
        `content_type` is not given. Check the supported decoders in `Properties.Audio.Decoder.Format`. The
        server answers every successful playback; if playback fails, the connection is closed without a
        response.

        Access: viewer.
        """
        return self._run(
            OPS.transmit_audio,
            None,
            {
                "audio": audio,
                "content_type": content_type,
                "audiodeviceid": audiodeviceid,
                "audiooutputid": audiooutputid,
            },
            request_options,
        )

    def rtsp_audio_stream_url(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        audio: Literal[0, 1] | MISSING = MISSING,
        camera: int | MISSING = MISSING,
        audiochannel: int | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Request an RTSP stream including audio.

        RTSP streams include audio if the request contains audio=1 or if Audio.A#.Enabled and
        AudioSource.A#.AudioSupport are enabled; audio=0 excludes audio. When AudioSource.A#.AudioSupport is
        enabled, the camera and audiochannel arguments of receive.cgi can be used; camera specifies both
        video source and audio configuration.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.rtsp_audio_stream_url,
            {"videocodec": videocodec, "audio": audio, "camera": camera, "audiochannel": audiochannel},
            port=port,
            include_credentials=include_credentials,
        )


class AsyncAudioApi(AsyncApi):
    """Audio API (``audio-api``)."""

    INFO = INFO

    @overload
    async def receive_audio(
        self, request: ReceiveAudioRequest, /, *, request_options: RequestOptions | None = None
    ) -> AsyncStreamResult[bytes]: ...
    @overload
    async def receive_audio(
        self,
        /,
        *,
        audio: Literal[0, 1] | MISSING = MISSING,
        audiobitrate: int | MISSING = MISSING,
        audiocodec: Literal["g711", "g726", "aac", "opus", "lpcm"] | MISSING = MISSING,
        audiosamplerate: int | MISSING = MISSING,
        camera: int | MISSING = MISSING,
        httptype: Literal["singlepart", "multipart"] | MISSING = MISSING,
        audiochannel: int | MISSING = MISSING,
        audiodeviceid: str | MISSING = MISSING,
        audioinputid: str | MISSING = MISSING,
        audionbrofchannels: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AsyncStreamResult[bytes]: ...
    async def receive_audio(
        self,
        request: ReceiveAudioRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AsyncStreamResult[bytes]:
        """Request and configure an audio stream from the device (singlepart or multipart).

        Singlepart (default) streams a continuous flow of audio packets in the codec's MIME type, with the
        content type only set at the start of the connection; multipart (`httptype=multipart`) answers
        `multipart/x-mixed-replace` with one audio block per part (G.711 512 bytes, G.726 32 kbit/s 256
        bytes, G.726 24 kbit/s 192 bytes; AAC is not supported). The stream is returned as raw bytes, also
        for multipart, so split the parts yourself.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return await self._run(OPS.receive_audio, request, kwargs, request_options)

    async def transmit_audio(
        self,
        *,
        audio: UploadSource,
        content_type: AudioMimeType | MISSING = MISSING,
        audiodeviceid: str | MISSING = MISSING,
        audiooutputid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Transmit an audio stream to the device (POST audio data to transmit.cgi).

        Sends the audio as the request body. The content type is set once at the start of the connection and
        defaults to `audio/basic` (G.711 mu-law); pass `content_type` for another format (for example
        `audio/axis-mulaw-128`, `audio/G726-32`, `audio/opus`). A content type on an `Upload` is used when
        `content_type` is not given. Check the supported decoders in `Properties.Audio.Decoder.Format`. The
        server answers every successful playback; if playback fails, the connection is closed without a
        response.

        Access: viewer.
        """
        return await self._run(
            OPS.transmit_audio,
            None,
            {
                "audio": audio,
                "content_type": content_type,
                "audiodeviceid": audiodeviceid,
                "audiooutputid": audiooutputid,
            },
            request_options,
        )

    def rtsp_audio_stream_url(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        audio: Literal[0, 1] | MISSING = MISSING,
        camera: int | MISSING = MISSING,
        audiochannel: int | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Request an RTSP stream including audio.

        RTSP streams include audio if the request contains audio=1 or if Audio.A#.Enabled and
        AudioSource.A#.AudioSupport are enabled; audio=0 excludes audio. When AudioSource.A#.AudioSupport is
        enabled, the camera and audiochannel arguments of receive.cgi can be used; camera specifies both
        video source and audio configuration.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.rtsp_audio_stream_url,
            {"videocodec": videocodec, "audio": audio, "camera": camera, "audiochannel": audiochannel},
            port=port,
            include_credentials=include_credentials,
        )
