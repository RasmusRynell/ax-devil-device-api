# GENERATED from specs/apis/network-video/imaging-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""``param.cgi`` parameters for CCD/CMOS image sources (``ImageSource.I#.Sensor``, ``ImageSource.I#``, ``ImageSource.I#.Appearance``).

Docs: https://developer.axis.com/vapix/network-video/imaging-api/
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListParametersRequest(Model):
    group: list[str] = Field(min_length=1)
    """Groups to list, e.g. ``ImageSource.I0.Sensor``."""


class UpdateParametersRequest(Model):
    parameters: dict[str, str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="imaging-api",
    name="Imaging API",
    family=Family.CGI,
    requires_firmware="5.00",
    docs=("https://developer.axis.com/vapix/network-video/imaging-api/",),
)


class OPS:
    list_parameters = Operation(
        INFO,
        "list_parameters",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListParametersRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    update_parameters = Operation(
        INFO,
        "update_parameters",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=UpdateParametersRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class ImagingApi(SyncApi):
    """Imaging API (``imaging-api``)."""

    INFO = INFO

    def list_parameters(self, group: list[str], *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Image source parameters as ``{"ImageSource.I0.Sensor.Brightness": "50"}`` (``root.`` removed).

        Groups: ``ImageSource.I0.Sensor`` (BacklightCompensation, Brightness, ColorLevel, Contrast,
        Exposure, ExposureWindow, MaxGain, Sharpness, WDR, WhiteBalance, Stabilizer, Defog, SensorProtector,
        ...), ``ImageSource.I0`` (AutoRotation, CameraTiltOrientation, ShockTriggeredLensCalibration) and
        ``ImageSource.I0.Appearance`` (AutoRotationEnabled). The sensor group is product dependent and only
        available in network cameras, so check which parameters the device has and their valid values first.
        Modular cameras extend the sensor group to other channels.

        Access: viewer.
        """
        return self._run(OPS.list_parameters, None, {"group": group}, request_options)

    def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set image source parameters, e.g. ``{"ImageSource.I0.Sensor.Brightness": "60"}``.

        Only the given parameters change. Operators can read and write the sensor parameters; the stabilizer
        parameters are readable by viewers, and operators can only read ``ShockTriggeredLensCalibration``.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)


class AsyncImagingApi(AsyncApi):
    """Imaging API (``imaging-api``)."""

    INFO = INFO

    async def list_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Image source parameters as ``{"ImageSource.I0.Sensor.Brightness": "50"}`` (``root.`` removed).

        Groups: ``ImageSource.I0.Sensor`` (BacklightCompensation, Brightness, ColorLevel, Contrast,
        Exposure, ExposureWindow, MaxGain, Sharpness, WDR, WhiteBalance, Stabilizer, Defog, SensorProtector,
        ...), ``ImageSource.I0`` (AutoRotation, CameraTiltOrientation, ShockTriggeredLensCalibration) and
        ``ImageSource.I0.Appearance`` (AutoRotationEnabled). The sensor group is product dependent and only
        available in network cameras, so check which parameters the device has and their valid values first.
        Modular cameras extend the sensor group to other channels.

        Access: viewer.
        """
        return await self._run(OPS.list_parameters, None, {"group": group}, request_options)

    async def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set image source parameters, e.g. ``{"ImageSource.I0.Sensor.Brightness": "60"}``.

        Only the given parameters change. Operators can read and write the sensor parameters; the stabilizer
        parameters are readable by viewers, and operators can only read ``ShockTriggeredLensCalibration``.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)
