# GENERATED from specs/apis/network-video/rate-control.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read and change the default bitrate control (VBR, MBR, ABR) of the video streams of an image view through param.cgi.

Docs: https://developer.axis.com/vapix/network-video/rate-control/
"""

from __future__ import annotations

from collections.abc import Mapping

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListRateControlRequest(Model):
    group: str
    """The parameter group, Image.I<n>.RateControl."""


class UpdateRateControlRequest(Model):
    parameters: dict[str, str]


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
            PATH, fixed_query=(("action", "list"),), args=(CgiArg("group"),), reply=TextKv(strip_prefix="root.")
        ),
        params=ListRateControlRequest,
        result=dict[str, str],
        access="admin",
        effect="read",
    )
    update_rate_control = Operation(
        INFO,
        "update_rate_control",
        CgiBinding(
            "/axis-cgi/admin/param.cgi",
            fixed_query=(("action", "update"),),
            args=(CgiArg("parameters", style="spread"),),
            reply=TextOk(),
        ),
        params=UpdateRateControlRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class RateControlApi(SyncApi):
    """Rate control (``rate-control``)."""

    INFO = INFO

    def list_rate_control(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Get the default rate control parameters of an image view as ``{"Image.I0.RateControl.Mode": "vbr"}`` (``root.`` removed).

        Pass the parameter group of the image view, for example ``Image.I0.RateControl``; the number ranges
        from 0 to Properties.Image.NbrOfViews minus one. The values are Mode (vbr, mbr or abr), Priority
        (none, quality, framerate or fullframerate), MaxBitrate, ABR.TargetBitrate, ABR.MaxBitrate (all in
        kbit/s, 0 means the product default of at least 50000) and ABR.RetentionTime (days, 1 to 3652).

        Access: admin.
        """
        return self._run(OPS.list_rate_control, None, {"group": group}, request_options)

    def update_rate_control(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set default rate control parameters, e.g. ``{"root.Image.I0.RateControl.Mode": "mbr"}``.

        The keys are parameters of Image.I<n>.RateControl, written with the ``root.`` prefix as in the docs.
        Mode is vbr, mbr or abr (default vbr). In MBR mode MaxBitrate and Priority apply. In ABR mode
        ABR.TargetBitrate, ABR.MaxBitrate and ABR.RetentionTime apply and MaxBitrate and Priority are
        ignored. Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_rate_control, None, {"parameters": dict(parameters)}, request_options)


class AsyncRateControlApi(AsyncApi):
    """Rate control (``rate-control``)."""

    INFO = INFO

    async def list_rate_control(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Get the default rate control parameters of an image view as ``{"Image.I0.RateControl.Mode": "vbr"}`` (``root.`` removed).

        Pass the parameter group of the image view, for example ``Image.I0.RateControl``; the number ranges
        from 0 to Properties.Image.NbrOfViews minus one. The values are Mode (vbr, mbr or abr), Priority
        (none, quality, framerate or fullframerate), MaxBitrate, ABR.TargetBitrate, ABR.MaxBitrate (all in
        kbit/s, 0 means the product default of at least 50000) and ABR.RetentionTime (days, 1 to 3652).

        Access: admin.
        """
        return await self._run(OPS.list_rate_control, None, {"group": group}, request_options)

    async def update_rate_control(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set default rate control parameters, e.g. ``{"root.Image.I0.RateControl.Mode": "mbr"}``.

        The keys are parameters of Image.I<n>.RateControl, written with the ``root.`` prefix as in the docs.
        Mode is vbr, mbr or abr (default vbr). In MBR mode MaxBitrate and Priority apply. In ABR mode
        ABR.TargetBitrate, ABR.MaxBitrate and ABR.RetentionTime apply and MaxBitrate and Priority are
        ignored. Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_rate_control, None, {"parameters": dict(parameters)}, request_options)
