# GENERATED from specs/apis/network-video/rtsp-adjustable-live-stream.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Change a subset of an ongoing RTSP stream's settings (compression, fps, keyframe interval, max bitrate, zipstream strength) without restarting it.

Docs: https://developer.axis.com/vapix/network-video/rtsp-adjustable-live-stream/
"""

from __future__ import annotations

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiBinding, TextKv
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class OpenAdjustableStreamUrlRequest(Model):
    videozprofile: str | None = None
    """videozprofile=storage is incompatible with this API; 400 Bad Request is returned if used."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="rtsp-adjustable-live-stream",
    name="RTSP Adjustable Live Stream",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.RTSP.AdjustableStreamSettings"),),
    docs=("https://developer.axis.com/vapix/network-video/rtsp-adjustable-live-stream/",),
)


class OPS:
    get_adjustable_stream_settings_property = Operation(
        INFO,
        "get_adjustable_stream_settings_property",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "root.Properties.API.RTSP.AdjustableStreamSettings")),
            reply=TextKv(strip_prefix="root."),
        ),
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    open_adjustable_stream_url = Operation(
        INFO,
        "open_adjustable_stream_url",
        RtspBinding(fixed_query=(("adjustablelivestream", "1"),)),
        params=OpenAdjustableStreamUrlRequest,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RtspAdjustableLiveStreamApi(SyncApi):
    """RTSP Adjustable Live Stream (``rtsp-adjustable-live-stream``)."""

    INFO = INFO

    def get_adjustable_stream_settings_property(
        self, *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Retrieve the supported adjustable stream settings via param.cgi.

        The feature is supported if the property exists and lists one or more settings.

        Access: viewer.
        """
        return self._run(OPS.get_adjustable_stream_settings_property, None, {}, request_options)

    def open_adjustable_stream_url(
        self, *, videozprofile: str | MISSING = MISSING, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Build the RTSP URL of a live stream with adjustable live stream enabled.

        Open the URL with an RTSP client. While the stream runs, the client can send GET_PARAMETER
        Adjustable-Stream-Settings to list the settings it may change and SET_PARAMETER Adjustable-Stream-
        Configuration (for example "fps=30,compression=30,videomaxbitrate=100000") to apply them; supported
        settings are compression, fps, videokeyframeinterval, videomaxbitrate and videozstrength, and they
        behave like the URL options of the Video streaming API. Both RTSP methods must be driven by the RTSP
        client; they are not operations of this library. Values above those used when the stream was started
        are not recommended, as some players cannot handle them.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.open_adjustable_stream_url,
            {"videozprofile": videozprofile},
            port=port,
            include_credentials=include_credentials,
        )


class AsyncRtspAdjustableLiveStreamApi(AsyncApi):
    """RTSP Adjustable Live Stream (``rtsp-adjustable-live-stream``)."""

    INFO = INFO

    async def get_adjustable_stream_settings_property(
        self, *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Retrieve the supported adjustable stream settings via param.cgi.

        The feature is supported if the property exists and lists one or more settings.

        Access: viewer.
        """
        return await self._run(OPS.get_adjustable_stream_settings_property, None, {}, request_options)

    def open_adjustable_stream_url(
        self, *, videozprofile: str | MISSING = MISSING, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Build the RTSP URL of a live stream with adjustable live stream enabled.

        Open the URL with an RTSP client. While the stream runs, the client can send GET_PARAMETER
        Adjustable-Stream-Settings to list the settings it may change and SET_PARAMETER Adjustable-Stream-
        Configuration (for example "fps=30,compression=30,videomaxbitrate=100000") to apply them; supported
        settings are compression, fps, videokeyframeinterval, videomaxbitrate and videozstrength, and they
        behave like the URL options of the Video streaming API. Both RTSP methods must be driven by the RTSP
        client; they are not operations of this library. Values above those used when the stream was started
        are not recommended, as some players cannot handle them.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.open_adjustable_stream_url,
            {"videozprofile": videozprofile},
            port=port,
            include_credentials=include_credentials,
        )
