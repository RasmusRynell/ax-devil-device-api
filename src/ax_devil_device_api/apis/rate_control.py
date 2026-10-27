# GENERATED from specs/apis/network-video/rate-control.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read and change the default bitrate control (VBR, MBR, ABR) of the video streams of an image view through param.cgi.

Docs: https://developer.axis.com/vapix/network-video/rate-control/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models

Mode = Literal["vbr", "mbr", "abr"]
Priority = Literal["none", "quality", "framerate", "fullframerate"]


class RateControl(Model):
    """The default rate control parameters of one image view (the names are those below ``root.Image.I<n>.RateControl.``)."""

    mode: Mode | None = Field(default=None, validation_alias="Mode", serialization_alias="Mode")
    priority: Priority | None = Field(default=None, validation_alias="Priority", serialization_alias="Priority")
    max_bitrate: int | None = Field(default=None, validation_alias="MaxBitrate", serialization_alias="MaxBitrate", ge=0)
    """The maximum bitrate in kbit/s in MBR mode."""
    abr_target_bitrate: int | None = Field(
        default=None, validation_alias="ABR.TargetBitrate", serialization_alias="ABR.TargetBitrate", ge=0
    )
    """The maximum average bitrate in kbit/s in ABR mode."""
    abr_max_bitrate: int | None = Field(
        default=None, validation_alias="ABR.MaxBitrate", serialization_alias="ABR.MaxBitrate", ge=0
    )
    """The maximum instantaneous bitrate in kbit/s in ABR mode."""
    abr_retention_time: int | None = Field(
        default=None, validation_alias="ABR.RetentionTime", serialization_alias="ABR.RetentionTime", ge=1, le=3652
    )
    """The desired retention in days in ABR mode."""


class ListRateControlRequest(Model):
    n: int = Field(ge=0)
    """The image view index."""


class SetRateControlRequest(Model):
    n: int = Field(ge=0)
    """The image view index."""
    mode: Mode | None = Field(
        default=None,
        validation_alias="root.Image.I{n}.RateControl.Mode",
        serialization_alias="root.Image.I{n}.RateControl.Mode",
    )
    priority: Priority | None = Field(
        default=None,
        validation_alias="root.Image.I{n}.RateControl.Priority",
        serialization_alias="root.Image.I{n}.RateControl.Priority",
    )
    max_bitrate: int | None = Field(
        default=None,
        validation_alias="root.Image.I{n}.RateControl.MaxBitrate",
        serialization_alias="root.Image.I{n}.RateControl.MaxBitrate",
        ge=0,
    )
    """The maximum bitrate in kbit/s in MBR mode."""
    abr_target_bitrate: int | None = Field(
        default=None,
        validation_alias="root.Image.I{n}.RateControl.ABR.TargetBitrate",
        serialization_alias="root.Image.I{n}.RateControl.ABR.TargetBitrate",
        ge=0,
    )
    """The maximum average bitrate in kbit/s in ABR mode."""
    abr_max_bitrate: int | None = Field(
        default=None,
        validation_alias="root.Image.I{n}.RateControl.ABR.MaxBitrate",
        serialization_alias="root.Image.I{n}.RateControl.ABR.MaxBitrate",
        ge=0,
    )
    """The maximum instantaneous bitrate in kbit/s in ABR mode."""
    abr_retention_time: int | None = Field(
        default=None,
        validation_alias="root.Image.I{n}.RateControl.ABR.RetentionTime",
        serialization_alias="root.Image.I{n}.RateControl.ABR.RetentionTime",
        ge=1,
        le=3652,
    )
    """The desired retention in days in ABR mode."""


class GetRtspStreamWithRateControlRequest(Model):
    videobitratemode: Mode | None = None
    videobitratepriority: Priority | None = None
    videomaxbitrate: int | None = Field(default=None, ge=0)
    """The maximum bitrate in kbit/s (MBR)."""
    videoabrtargetbitrate: int | None = Field(default=None, ge=0)
    """The target average bitrate in kbit/s (ABR)."""
    videoabrmaxbitrate: int | None = Field(default=None, ge=0)
    """The maximum instantaneous bitrate in kbit/s (ABR)."""
    videoabrretentiontime: int | None = Field(default=None, ge=1, le=3652)
    """The retention time in days (ABR)."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="rate-control",
    name="Rate control",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.Image.RateControl.ABR.ABR", "yes"),
        ParamDiscovery("Properties.Image.RateControl.Version", "1.1", ">="),
    ),
    docs=("https://developer.axis.com/vapix/network-video/rate-control/",),
)


class OPS:
    list_rate_control = Operation(
        INFO,
        "list_rate_control",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "Image.I{n}.RateControl")),
            reply=TextKv(strip_prefix="root.Image.I{n}.RateControl."),
        ),
        params=ListRateControlRequest,
        result=RateControl,
        access="admin",
        effect="read",
    )
    set_rate_control = Operation(
        INFO,
        "set_rate_control",
        CgiBinding(
            "/axis-cgi/admin/param.cgi",
            fixed_query=(("action", "update"),),
            args=(
                CgiArg("mode", wire="root.Image.I{n}.RateControl.Mode"),
                CgiArg("priority", wire="root.Image.I{n}.RateControl.Priority"),
                CgiArg("max_bitrate", wire="root.Image.I{n}.RateControl.MaxBitrate"),
                CgiArg("abr_target_bitrate", wire="root.Image.I{n}.RateControl.ABR.TargetBitrate"),
                CgiArg("abr_max_bitrate", wire="root.Image.I{n}.RateControl.ABR.MaxBitrate"),
                CgiArg("abr_retention_time", wire="root.Image.I{n}.RateControl.ABR.RetentionTime"),
            ),
            reply=TextOk(),
        ),
        params=SetRateControlRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_rtsp_stream_with_rate_control = Operation(
        INFO,
        "get_rtsp_stream_with_rate_control",
        RtspBinding(),
        params=GetRtspStreamWithRateControlRequest,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RateControlApi(SyncApi):
    """Rate control (``rate-control``)."""

    INFO = INFO

    def list_rate_control(self, n: int, *, request_options: RequestOptions | None = None) -> RateControl:
        """Get the default rate control parameters of an image view.

        ``n`` is the image view index, from 0 to Properties.Image.NbrOfViews minus one. The values are Mode
        (vbr, mbr or abr), Priority (none, quality, framerate or fullframerate), MaxBitrate,
        ABR.TargetBitrate, ABR.MaxBitrate (all in kbit/s, 0 means the product default of at least 50000) and
        ABR.RetentionTime (days, 1 to 3652). A product returns only the parameters it supports.

        Access: admin.
        """
        return self._run(OPS.list_rate_control, None, {"n": n}, request_options)

    @overload
    def set_rate_control(
        self, request: SetRateControlRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_rate_control(
        self,
        n: int,
        /,
        *,
        mode: Mode | MISSING = MISSING,
        priority: Priority | MISSING = MISSING,
        max_bitrate: int | MISSING = MISSING,
        abr_target_bitrate: int | MISSING = MISSING,
        abr_max_bitrate: int | MISSING = MISSING,
        abr_retention_time: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_rate_control(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set default rate control parameters of an image view.

        In MBR mode MaxBitrate and Priority apply. In ABR mode ABR.TargetBitrate, ABR.MaxBitrate and
        ABR.RetentionTime apply and MaxBitrate and Priority are ignored. Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRateControlRequest):
            kwargs = bind_positional(OPS.set_rate_control, ("n",), (request, *args), kwargs)
            request = None
        self._run(OPS.set_rate_control, request, kwargs, request_options)

    def get_rtsp_stream_with_rate_control(
        self,
        *,
        videobitratemode: Mode | MISSING = MISSING,
        videobitratepriority: Priority | MISSING = MISSING,
        videomaxbitrate: int | MISSING = MISSING,
        videoabrtargetbitrate: int | MISSING = MISSING,
        videoabrmaxbitrate: int | MISSING = MISSING,
        videoabrretentiontime: int | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with rate control settings that apply to that stream only.

        The settings override the defaults of ``list_rate_control``. If any rate control option is given,
        ``videobitratemode`` must be given as well, otherwise the device answers 400 Bad Request. Settings
        that do not apply to the mode are ignored. If both ``videoabrmaxbitrate`` and
        ``videoabrtargetbitrate`` are given, the maximum must not be smaller than the target.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_rate_control,
            {
                "videobitratemode": videobitratemode,
                "videobitratepriority": videobitratepriority,
                "videomaxbitrate": videomaxbitrate,
                "videoabrtargetbitrate": videoabrtargetbitrate,
                "videoabrmaxbitrate": videoabrmaxbitrate,
                "videoabrretentiontime": videoabrretentiontime,
            },
            port=port,
            include_credentials=include_credentials,
        )


class AsyncRateControlApi(AsyncApi):
    """Rate control (``rate-control``)."""

    INFO = INFO

    async def list_rate_control(self, n: int, *, request_options: RequestOptions | None = None) -> RateControl:
        """Get the default rate control parameters of an image view.

        ``n`` is the image view index, from 0 to Properties.Image.NbrOfViews minus one. The values are Mode
        (vbr, mbr or abr), Priority (none, quality, framerate or fullframerate), MaxBitrate,
        ABR.TargetBitrate, ABR.MaxBitrate (all in kbit/s, 0 means the product default of at least 50000) and
        ABR.RetentionTime (days, 1 to 3652). A product returns only the parameters it supports.

        Access: admin.
        """
        return await self._run(OPS.list_rate_control, None, {"n": n}, request_options)

    @overload
    async def set_rate_control(
        self, request: SetRateControlRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_rate_control(
        self,
        n: int,
        /,
        *,
        mode: Mode | MISSING = MISSING,
        priority: Priority | MISSING = MISSING,
        max_bitrate: int | MISSING = MISSING,
        abr_target_bitrate: int | MISSING = MISSING,
        abr_max_bitrate: int | MISSING = MISSING,
        abr_retention_time: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_rate_control(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set default rate control parameters of an image view.

        In MBR mode MaxBitrate and Priority apply. In ABR mode ABR.TargetBitrate, ABR.MaxBitrate and
        ABR.RetentionTime apply and MaxBitrate and Priority are ignored. Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRateControlRequest):
            kwargs = bind_positional(OPS.set_rate_control, ("n",), (request, *args), kwargs)
            request = None
        await self._run(OPS.set_rate_control, request, kwargs, request_options)

    def get_rtsp_stream_with_rate_control(
        self,
        *,
        videobitratemode: Mode | MISSING = MISSING,
        videobitratepriority: Priority | MISSING = MISSING,
        videomaxbitrate: int | MISSING = MISSING,
        videoabrtargetbitrate: int | MISSING = MISSING,
        videoabrmaxbitrate: int | MISSING = MISSING,
        videoabrretentiontime: int | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with rate control settings that apply to that stream only.

        The settings override the defaults of ``list_rate_control``. If any rate control option is given,
        ``videobitratemode`` must be given as well, otherwise the device answers 400 Bad Request. Settings
        that do not apply to the mode are ignored. If both ``videoabrmaxbitrate`` and
        ``videoabrtargetbitrate`` are given, the maximum must not be smaller than the target.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_rate_control,
            {
                "videobitratemode": videobitratemode,
                "videobitratepriority": videobitratepriority,
                "videomaxbitrate": videomaxbitrate,
                "videoabrtargetbitrate": videoabrtargetbitrate,
                "videoabrmaxbitrate": videoabrmaxbitrate,
                "videoabrretentiontime": videoabrretentiontime,
            },
            port=port,
            include_credentials=include_credentials,
        )
