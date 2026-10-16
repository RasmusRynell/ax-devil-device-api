# GENERATED from specs/apis/network-video/video-streaming-rtsp.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""RTSP media streaming from rtsp://<servername>/axis-media/media.amp: commands, URL parameters (incl.

Docs: https://developer.axis.com/vapix/network-video/video-streaming/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class GetAlwaysMulticastSdpRequest(Model):
    camera: str | None = None
    """Desired video source."""


class DescribeUrlRequest(Model):
    streamprofile: str | None = None
    """Name of a saved stream profile (StreamProfile.S#.Name). Values can be overridden by parameters after it."""
    videocodec: Literal["av1", "h264", "h265", "jpeg"] | None = None
    """Video format (Image API URL option); av1 is platform dependent, h265 product dependent. Default: h264 for RTSP."""
    resolution: str | None = None
    """Resolution of the stream (Image API URL option), for example 640x480."""
    recordingid: str | None = None
    """Name of a saved recording."""
    audio: Literal[0, 1] | None = None
    """Whether audio shall be available in the stream. 0 = No audio, 1 = Audio. (Metadata table: default configurable, see Audio.A0.Enabled.) Default: 1."""
    pull: Literal[0, 1] | None = None
    """For PLAY when downloading a recording: 1 = stream as fast as possible (only useful with RTSP over HTTP); 0 = default, pull disabled, real-time playback. Default: 0."""
    video: Literal[0, 1] | None = None
    """Whether video should be made available in the stream. Default: 1."""
    event: Literal["off", "on"] | None = None
    """Whether event metadata should be made available in the stream. Default: 'off'."""
    eventtopic: str | None = None
    """Event topic filter: <filter1>[,<filter2>...], Topic Expression of the ConcreteSet dialect with prefixes onvif (http://www.onvif.org/ver10/topics) and axis (http://www.axis.com/2009/event/topics)."""
    eventcontent: str | None = None
    """MessageContent filter expression in the ItemFilter dialect (ONVIF); may be URL encoded. Only useful when event=on."""
    ptz: Literal["none", "all", "status", "position"] | None = None
    """PTZ metadata. Values: none: No PTZ status or position information; all: Both PTZ status and position; status: PTZ status; position: PTZ position"""
    analytics: Literal["off", "box", "polygon"] | None = None
    """Scene (analytics) metadata. Values: off: No scene data; box: Bounding box and object classification (if supported/configured); polygon: Polygon and bounding box and object classification (if supported/configured)"""
    ptz_pantilt_coordinate_space: Literal["generic", "degrees", "digital"] | None = None
    """Coordinate space for pan/tilt positions; only with ptz=all|position. Values: generic: http://www.onvif.org/ver10/tptz/PantiltSpaces/PositionGenericSpace; degrees: http://www.onvif.org/ver10/tptz/PantiltSpaces/SphericalPositionSpaceDegrees; digital: http://www.onvif.org/ver10/tptz/PantiltSpaces/DigitalPositionSpace"""
    ptz_zoom_coordinate_space: Literal["generic", "digital"] | None = None
    """Coordinate space for zoom positions; only with ptz=all|position. Values: generic: http://www.onvif.org/ver10/tptz/ZoomSpaces/PositionGenericSpace; digital: http://www.onvif.org/ver10/tptz/ZoomSpaces/NormalizedDigitalPosition"""


class SsmDescribeUrlRequest(Model):
    audio: Literal[0, 1] | None = None


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/alwaysmulti.sdp"

INFO = ApiInfo(
    id="video-streaming-rtsp",
    name="Video streaming over RTSP",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.API.RTSP.Version", "2.01"),
        ParamDiscovery("Properties.API.RTSP.RTSPAuth", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/video-streaming/",),
)


class OPS:
    get_always_multicast_sdp = Operation(
        INFO,
        "get_always_multicast_sdp",
        CgiBinding(PATH, args=(CgiArg("camera"),), reply=Text()),
        params=GetAlwaysMulticastSdpRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    describe_url = Operation(
        INFO, "describe_url", RtspBinding(), params=DescribeUrlRequest, access="viewer", effect="read"
    )
    ssm_describe_url = Operation(
        INFO,
        "ssm_describe_url",
        RtspBinding(path="/axis-media/ssm/media.amp"),
        params=SsmDescribeUrlRequest,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RtspHelperApi(SyncApi):
    """Video streaming over RTSP (``video-streaming-rtsp``)."""

    INFO = INFO

    def get_always_multicast_sdp(
        self, *, camera: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Get the SDP of an always-multicast stream (continuously running multicast; reduces connect latency).

        Requires Network.RTP.R0.AlwaysMulticastVideo=yes. Protected by HTTP authentication; viewer, operator
        and admin can request. Identification: Properties.API.HTTP.Version=3, AXIS OS 5.40 and later. Since
        AXIS OS 5.40.

        Access: viewer.
        """
        return self._run(OPS.get_always_multicast_sdp, None, {"camera": camera}, request_options)

    def describe_url(
        self,
        *,
        streamprofile: str | MISSING = MISSING,
        videocodec: Literal["av1", "h264", "h265", "jpeg"] | MISSING = MISSING,
        resolution: str | MISSING = MISSING,
        recordingid: str | MISSING = MISSING,
        audio: Literal[0, 1] | MISSING = MISSING,
        pull: Literal[0, 1] | MISSING = MISSING,
        video: Literal[0, 1] | MISSING = MISSING,
        event: Literal["off", "on"] | MISSING = MISSING,
        eventtopic: str | MISSING = MISSING,
        eventcontent: str | MISSING = MISSING,
        ptz: Literal["none", "all", "status", "position"] | MISSING = MISSING,
        analytics: Literal["off", "box", "polygon"] | MISSING = MISSING,
        ptz_pantilt_coordinate_space: Literal["generic", "degrees", "digital"] | MISSING = MISSING,
        ptz_zoom_coordinate_space: Literal["generic", "digital"] | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a media stream (the URL of DESCRIBE, SETUP and PLAY).

        The same URL is used by the RTSP commands DESCRIBE, SETUP (with /trackID=n) and PLAY; sending them,
        and the other commands (OPTIONS, PAUSE, TEARDOWN, SET_PARAMETER Renew-Stream, GET_PARAMETER) and
        tunnelling RTSP over HTTP, is the job of an RTSP client. Parameters are sent in field order, so the
        video options after streamprofile override the values saved in the stream profile. The video URL
        options of the Image API (camera, fps, compression, ...) are also accepted by the device but are not
        listed here.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.describe_url,
            {
                "streamprofile": streamprofile,
                "videocodec": videocodec,
                "resolution": resolution,
                "recordingid": recordingid,
                "audio": audio,
                "pull": pull,
                "video": video,
                "event": event,
                "eventtopic": eventtopic,
                "eventcontent": eventcontent,
                "ptz": ptz,
                "analytics": analytics,
                "ptz_pantilt_coordinate_space": ptz_pantilt_coordinate_space,
                "ptz_zoom_coordinate_space": ptz_zoom_coordinate_space,
            },
            port=port,
            include_credentials=include_credentials,
        )

    def ssm_describe_url(
        self, *, audio: Literal[0, 1] | MISSING = MISSING, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Source-specific multicast (SSM): SDP includes a=source-filter; SETUP with Transport: RTP/AVP;multicast; tracks addressed as /stream=<n>.

        Requires Network.RTP.R0.VideoAddress, Network.RTP.R0.VideoPort (0 = dynamically allocated by the
        RTSP server; otherwise static), Network.RTP.R0.TTL (and AudioAddress/AudioPort for audio, with
        ?audio=1). The SSM implementation does not support RTCP receiver feedback.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.ssm_describe_url, {"audio": audio}, port=port, include_credentials=include_credentials
        )


class AsyncRtspHelperApi(AsyncApi):
    """Video streaming over RTSP (``video-streaming-rtsp``)."""

    INFO = INFO

    async def get_always_multicast_sdp(
        self, *, camera: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Get the SDP of an always-multicast stream (continuously running multicast; reduces connect latency).

        Requires Network.RTP.R0.AlwaysMulticastVideo=yes. Protected by HTTP authentication; viewer, operator
        and admin can request. Identification: Properties.API.HTTP.Version=3, AXIS OS 5.40 and later. Since
        AXIS OS 5.40.

        Access: viewer.
        """
        return await self._run(OPS.get_always_multicast_sdp, None, {"camera": camera}, request_options)

    def describe_url(
        self,
        *,
        streamprofile: str | MISSING = MISSING,
        videocodec: Literal["av1", "h264", "h265", "jpeg"] | MISSING = MISSING,
        resolution: str | MISSING = MISSING,
        recordingid: str | MISSING = MISSING,
        audio: Literal[0, 1] | MISSING = MISSING,
        pull: Literal[0, 1] | MISSING = MISSING,
        video: Literal[0, 1] | MISSING = MISSING,
        event: Literal["off", "on"] | MISSING = MISSING,
        eventtopic: str | MISSING = MISSING,
        eventcontent: str | MISSING = MISSING,
        ptz: Literal["none", "all", "status", "position"] | MISSING = MISSING,
        analytics: Literal["off", "box", "polygon"] | MISSING = MISSING,
        ptz_pantilt_coordinate_space: Literal["generic", "degrees", "digital"] | MISSING = MISSING,
        ptz_zoom_coordinate_space: Literal["generic", "digital"] | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a media stream (the URL of DESCRIBE, SETUP and PLAY).

        The same URL is used by the RTSP commands DESCRIBE, SETUP (with /trackID=n) and PLAY; sending them,
        and the other commands (OPTIONS, PAUSE, TEARDOWN, SET_PARAMETER Renew-Stream, GET_PARAMETER) and
        tunnelling RTSP over HTTP, is the job of an RTSP client. Parameters are sent in field order, so the
        video options after streamprofile override the values saved in the stream profile. The video URL
        options of the Image API (camera, fps, compression, ...) are also accepted by the device but are not
        listed here.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.describe_url,
            {
                "streamprofile": streamprofile,
                "videocodec": videocodec,
                "resolution": resolution,
                "recordingid": recordingid,
                "audio": audio,
                "pull": pull,
                "video": video,
                "event": event,
                "eventtopic": eventtopic,
                "eventcontent": eventcontent,
                "ptz": ptz,
                "analytics": analytics,
                "ptz_pantilt_coordinate_space": ptz_pantilt_coordinate_space,
                "ptz_zoom_coordinate_space": ptz_zoom_coordinate_space,
            },
            port=port,
            include_credentials=include_credentials,
        )

    def ssm_describe_url(
        self, *, audio: Literal[0, 1] | MISSING = MISSING, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Source-specific multicast (SSM): SDP includes a=source-filter; SETUP with Transport: RTP/AVP;multicast; tracks addressed as /stream=<n>.

        Requires Network.RTP.R0.VideoAddress, Network.RTP.R0.VideoPort (0 = dynamically allocated by the
        RTSP server; otherwise static), Network.RTP.R0.TTL (and AudioAddress/AudioPort for audio, with
        ?audio=1). The SSM implementation does not support RTCP receiver feedback.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.ssm_describe_url, {"audio": audio}, port=port, include_credentials=include_credentials
        )
