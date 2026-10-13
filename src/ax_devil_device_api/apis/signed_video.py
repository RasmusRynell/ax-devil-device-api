# GENERATED from specs/apis/network-video/signed-video.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Enable or disable video signing per video channel with ``Image.I#.MPEG.SignedVideo.Enabled`` (param.cgi).

Docs: https://developer.axis.com/vapix/network-video/signed-video/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SignedVideo(Model):
    """The signed video setting of one channel."""

    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """Whether signed video is enabled by default (``yes`` or ``no`` on the wire)."""


class GetSignedVideoRequest(Model):
    n: int = Field(ge=0)
    """The channel index."""


class SetSignedVideoRequest(Model):
    parameters: dict[str, Literal["yes", "no"]]


class StreamSignedVideoRequest(Model):
    videosigned: bool
    """Enable (1) or disable (0) signed video for this stream."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="signed-video",
    name="Signed Video",
    family=Family.CGI,
    discovery=(ApiDiscovery("signed-video"),),
    docs=("https://developer.axis.com/vapix/network-video/signed-video/",),
)


class OPS:
    get_signed_video = Operation(
        INFO,
        "get_signed_video",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "Image.I{n}.MPEG.SignedVideo.Enabled")),
            reply=TextKv(strip_prefix="root.Image.I{n}.MPEG.SignedVideo."),
            accept="text/plain",
        ),
        params=GetSignedVideoRequest,
        result=SignedVideo,
        access="viewer",
        effect="read",
    )
    set_signed_video = Operation(
        INFO,
        "set_signed_video",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=SetSignedVideoRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    stream_signed_video = Operation(
        INFO, "stream_signed_video", RtspBinding(), params=StreamSignedVideoRequest, access="viewer", effect="read"
    )


# ---------------------------------------------------------------------------
# API classes


class SignedVideoApi(SyncApi):
    """Signed Video (``signed-video``)."""

    INFO = INFO

    def get_signed_video(self, n: int, *, request_options: RequestOptions | None = None) -> SignedVideo:
        """Read whether signed video is enabled by default for a channel.

        ``n`` is the channel index, from 0 up to the number of channels of the product minus 1. The device
        answers ``root.Image.I<n>.MPEG.SignedVideo.Enabled=yes`` or ``no``.

        Access: viewer.
        """
        return self._run(OPS.get_signed_video, None, {"n": n}, request_options)

    def set_signed_video(
        self, parameters: Mapping[str, Literal["yes", "no"]], *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable signed video by default for a channel, e.g. ``{"Image.I0.MPEG.SignedVideo.Enabled": "yes"}``.

        Keys are ``Image.I#.MPEG.SignedVideo.Enabled`` where ``#`` is the channel index (0 up to the number
        of channels minus 1); values are ``yes`` or ``no`` (the default is ``no``). Only the given
        parameters change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_signed_video, None, {"parameters": dict(parameters)}, request_options)

    def stream_signed_video(
        self, *, videosigned: bool, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with video signing enabled or disabled for that stream.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.stream_signed_video, {"videosigned": videosigned}, port=port, include_credentials=include_credentials
        )


class AsyncSignedVideoApi(AsyncApi):
    """Signed Video (``signed-video``)."""

    INFO = INFO

    async def get_signed_video(self, n: int, *, request_options: RequestOptions | None = None) -> SignedVideo:
        """Read whether signed video is enabled by default for a channel.

        ``n`` is the channel index, from 0 up to the number of channels of the product minus 1. The device
        answers ``root.Image.I<n>.MPEG.SignedVideo.Enabled=yes`` or ``no``.

        Access: viewer.
        """
        return await self._run(OPS.get_signed_video, None, {"n": n}, request_options)

    async def set_signed_video(
        self, parameters: Mapping[str, Literal["yes", "no"]], *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable signed video by default for a channel, e.g. ``{"Image.I0.MPEG.SignedVideo.Enabled": "yes"}``.

        Keys are ``Image.I#.MPEG.SignedVideo.Enabled`` where ``#`` is the channel index (0 up to the number
        of channels minus 1); values are ``yes`` or ``no`` (the default is ``no``). Only the given
        parameters change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_signed_video, None, {"parameters": dict(parameters)}, request_options)

    def stream_signed_video(
        self, *, videosigned: bool, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with video signing enabled or disabled for that stream.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.stream_signed_video, {"videosigned": videosigned}, port=port, include_credentials=include_credentials
        )
