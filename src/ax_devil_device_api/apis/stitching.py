# GENERATED from specs/apis/network-video/stitching.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Tune multi-sensor panoramic stitching: blending, parallax compensation, sensor rotation, horizon straightening and field of view.

Docs: https://developer.axis.com/vapix/network-video/stitching/
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


class Capabilities(Model):
    """Whether each method is supported by the device."""

    get_blending_amount: bool | None = Field(
        default=None, validation_alias="getBlendingAmount", serialization_alias="getBlendingAmount"
    )
    set_blending_amount: bool | None = Field(
        default=None, validation_alias="setBlendingAmount", serialization_alias="setBlendingAmount"
    )
    get_parallax_compensation_distance: bool | None = Field(
        default=None,
        validation_alias="getParallaxCompensationDistance",
        serialization_alias="getParallaxCompensationDistance",
    )
    set_parallax_compensation_distance: bool | None = Field(
        default=None,
        validation_alias="setParallaxCompensationDistance",
        serialization_alias="setParallaxCompensationDistance",
    )
    rotate_angle: bool | None = Field(default=None, validation_alias="rotateAngle", serialization_alias="rotateAngle")
    restore: bool | None = None
    set_horizon_straightening_enabled: bool | None = Field(
        default=None,
        validation_alias="setHorizonStraighteningEnabled",
        serialization_alias="setHorizonStraighteningEnabled",
    )
    get_horizon_straightening_enabled: bool | None = Field(
        default=None,
        validation_alias="getHorizonStraighteningEnabled",
        serialization_alias="getHorizonStraighteningEnabled",
    )
    get_horizon_straightening_properties: bool | None = Field(
        default=None,
        validation_alias="getHorizonStraighteningProperties",
        serialization_alias="getHorizonStraighteningProperties",
    )
    set_horizon_straightening_tilt: bool | None = Field(
        default=None, validation_alias="setHorizonStraighteningTilt", serialization_alias="setHorizonStraighteningTilt"
    )
    set_horizon_straightening_stretch_enabled: bool | None = Field(
        default=None,
        validation_alias="setHorizonStraighteningStretchEnabled",
        serialization_alias="setHorizonStraighteningStretchEnabled",
    )
    set_horizon_straightening_stretch_amount: bool | None = Field(
        default=None,
        validation_alias="setHorizonStraighteningStretchAmount",
        serialization_alias="setHorizonStraighteningStretchAmount",
    )
    get_field_of_view: bool | None = Field(
        default=None, validation_alias="getFieldOfView", serialization_alias="getFieldOfView"
    )
    set_stitching_enabled: bool | None = Field(
        default=None, validation_alias="setStitchingEnabled", serialization_alias="setStitchingEnabled"
    )
    get_stitching_enabled: bool | None = Field(
        default=None, validation_alias="getStitchingEnabled", serialization_alias="getStitchingEnabled"
    )


class Limits(Model):
    """Parameter limits of the setter methods."""

    blending_amount_min: float | None = Field(
        default=None, validation_alias="blendingAmountMin", serialization_alias="blendingAmountMin"
    )
    """Minimum blending amount for setBlendingAmount."""
    blending_amount_max: float | None = Field(
        default=None, validation_alias="blendingAmountMax", serialization_alias="blendingAmountMax"
    )
    """Maximum blending amount for setBlendingAmount."""
    parallax_compensation_distance_min: float | None = Field(
        default=None,
        validation_alias="parallaxCompensationDistanceMin",
        serialization_alias="parallaxCompensationDistanceMin",
    )
    """Minimum parallax compensation distance."""
    parallax_compensation_distance_max: float | None = Field(
        default=None,
        validation_alias="parallaxCompensationDistanceMax",
        serialization_alias="parallaxCompensationDistanceMax",
    )
    """Maximum parallax compensation distance."""
    id_min: float | None = Field(default=None, validation_alias="idMin", serialization_alias="idMin")
    """Minimum id for rotateAngle and restore."""
    id_max: float | None = Field(default=None, validation_alias="idMax", serialization_alias="idMax")
    """Maximum id for rotateAngle and restore."""
    angle_min: float | None = Field(default=None, validation_alias="angleMin", serialization_alias="angleMin")
    """Minimum angle for rotateAngle."""
    angle_max: float | None = Field(default=None, validation_alias="angleMax", serialization_alias="angleMax")
    """Maximum angle for rotateAngle."""
    horizon_straightening_tilt_min: float | None = Field(
        default=None, validation_alias="horizonStraighteningTiltMin", serialization_alias="horizonStraighteningTiltMin"
    )
    """Minimum for setHorizonStraighteningTilt."""
    horizon_straightening_tilt_max: float | None = Field(
        default=None, validation_alias="horizonStraighteningTiltMax", serialization_alias="horizonStraighteningTiltMax"
    )
    """Maximum for setHorizonStraighteningTilt."""
    horizon_straightening_stretch_min: float | None = Field(
        default=None,
        validation_alias="horizonStraighteningStretchMin",
        serialization_alias="horizonStraighteningStretchMin",
    )
    """Minimum for setHorizonStraighteningStretchAmount."""
    horizon_straightening_stretch_max: float | None = Field(
        default=None,
        validation_alias="horizonStraighteningStretchMax",
        serialization_alias="horizonStraighteningStretchMax",
    )
    """Maximum for setHorizonStraighteningStretchAmount."""


class StitchingCapabilities(Model):
    capabilities: Capabilities
    limits: Limits


class GetBlendingAmountResult(Model):
    blending_amount: float = Field(validation_alias="blendingAmount", serialization_alias="blendingAmount")
    """Current amount of blurriness around the image seams."""


class SetBlendingAmountRequest(Model):
    blending_amount: float = Field(
        validation_alias="blendingAmount", serialization_alias="blendingAmount", ge=0, le=100
    )
    """0-100; 0 = sharp edges with no blurriness, 100 = maximum blurriness. Only the first 15 decimals are used."""


class GetParallaxCompensationDistanceResult(Model):
    parallax_compensation_distance: float = Field(
        validation_alias="parallaxCompensationDistance", serialization_alias="parallaxCompensationDistance"
    )
    """Distance where alignment is currently calculated, in meters."""


class SetParallaxCompensationDistanceRequest(Model):
    parallax_compensation_distance: float = Field(
        validation_alias="parallaxCompensationDistance", serialization_alias="parallaxCompensationDistance", ge=1, le=50
    )
    """Distance in meters, 1-50. Only the first 15 decimals are used. (unit=m)"""


class RotateAngleRequest(Model):
    id: int = Field(ge=0)
    """Sensor image to rotate; 0 to number of sensors - 1 (see limits idMin/idMax)."""
    axis: Literal["pan", "tilt", "roll"]
    """Axis to rotate."""
    angle: float = Field(ge=-180, le=180)
    """Degrees to rotate, -180..+180. Only the first 15 decimals are used. (unit=degrees)"""


class RestoreRequest(Model):
    id: int = Field(ge=0)
    """Sensor image to restore; 0 to number of sensors - 1."""


class SetHorizonStraighteningEnabledRequest(Model):
    horizon_straightening_enabled: bool = Field(
        validation_alias="horizonStraighteningEnabled", serialization_alias="horizonStraighteningEnabled"
    )
    """true: enable; false: disable."""


class GetHorizonStraighteningEnabledResult(Model):
    enabled: bool


class GetHorizonStraighteningPropertiesResult(Model):
    horizon_straightening_tilt: float = Field(
        validation_alias="horizonStraighteningTilt", serialization_alias="horizonStraighteningTilt"
    )
    """Current straight horizon position."""
    horizon_straightening_stretch_enabled: bool = Field(
        validation_alias="horizonStraighteningStretchEnabled", serialization_alias="horizonStraighteningStretchEnabled"
    )
    """Whether the image is stretched over the black areas."""
    horizon_straightening_stretch_amount: float = Field(
        validation_alias="horizonStraighteningStretchAmount", serialization_alias="horizonStraighteningStretchAmount"
    )
    """How the stretching is performed."""


class SetHorizonStraighteningTiltRequest(Model):
    horizon_straightening_tilt: float = Field(
        validation_alias="horizonStraighteningTilt", serialization_alias="horizonStraighteningTilt"
    )
    """Position of the straight horizon in angles relative to the middle of the image (limits horizonStraighteningTiltMin/Max). Only the first 15 decimals are used. (unit=degrees)"""


class SetHorizonStraighteningStretchEnabledRequest(Model):
    horizon_straightening_stretch_enabled: bool = Field(
        validation_alias="horizonStraighteningStretchEnabled", serialization_alias="horizonStraighteningStretchEnabled"
    )
    """true: enable stretch; false: disable."""


class SetHorizonStraighteningStretchAmountRequest(Model):
    horizon_straightening_stretch_amount: float = Field(
        validation_alias="horizonStraighteningStretchAmount",
        serialization_alias="horizonStraighteningStretchAmount",
        ge=0,
        le=100,
    )
    """0-100; 0 = stretch images non-linearly, 100 = linearly."""


class GetFieldOfViewResult(Model):
    h_fo_v: float = Field(validation_alias="hFoV", serialization_alias="hFoV")
    """Supported horizontal field of view."""
    v_fo_v: float = Field(validation_alias="vFoV", serialization_alias="vFoV")
    """Supported vertical field of view."""


class GetStitchingEnabledResult(Model):
    stitching_enabled: bool = Field(validation_alias="stitchingEnabled", serialization_alias="stitchingEnabled")


class SetStitchingEnabledRequest(Model):
    stitching_enabled: bool = Field(validation_alias="stitchingEnabled", serialization_alias="stitchingEnabled")
    """Whether stitching should be enabled."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/stitching.cgi"

INFO = ApiInfo(
    id="stitching",
    name="Stitching",
    family=Family.JSONRPC,
    major=3,
    known_versions=(ApiVersion(3, 0), ApiVersion(3, 2), ApiVersion(3, 4)),
    discovery=(ApiDiscovery("stitching"),),
    docs=("https://developer.axis.com/vapix/network-video/stitching/",),
    errors={
        1000: ErrorCode("Invalid parameter value", "invalid_argument"),
        2000: ErrorCode("Failed to allocate memory", "internal"),
        2004: ErrorCode("Method not supported", "unsupported"),
        2200: ErrorCode("Unknown error has occurred", "internal"),
        2201: ErrorCode("Failed to init transformation tables", "internal"),
        2202: ErrorCode("Failed to generate table with given parameters", "invalid_argument"),
        2203: ErrorCode("Failed to apply table with given parameters", "invalid_argument"),
        2205: ErrorCode("Failed read calibration file", "internal"),
        2206: ErrorCode("Calibration file is missing", "unavailable"),
        2207: ErrorCode("Failed to unlink calibration file", "internal"),
        2208: ErrorCode("Unsupported stitching mode", "unsupported"),
        2209: ErrorCode("Failed to read configuration file", "internal"),
        2210: ErrorCode("Failed to save configuration file", "internal"),
        2211: ErrorCode("Failed to parse configuration file", "internal"),
        2212: ErrorCode("Method is not allowed in disabled mode", "unavailable"),
        2213: ErrorCode("Operation is not supported", "unsupported"),
        2300: ErrorCode("Internal vipd error, could not complete request", "internal"),
        4001: ErrorCode("Mandatory input parameters was not found in the input", "invalid_argument"),
        4002: ErrorCode("The type of a provided JSON parameter was incorrect", "invalid_argument"),
        8000: ErrorCode("Internal error, could not complete request", "internal"),
        8002: ErrorCode("Generic error", "internal"),
    },
)


class OPS:
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        result=StitchingCapabilities,
        access="admin",
        effect="read",
    )
    get_blending_amount = Operation(
        INFO,
        "get_blending_amount",
        JsonRpcBinding("getBlendingAmount", PATH),
        result=GetBlendingAmountResult,
        access="admin",
        effect="read",
    )
    set_blending_amount = Operation(
        INFO,
        "set_blending_amount",
        JsonRpcBinding("setBlendingAmount", PATH),
        params=SetBlendingAmountRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            2204: ErrorCode("Failed to apply blending", "internal"),
            2214: ErrorCode("Blending is disabled", "unavailable"),
        },
    )
    get_parallax_compensation_distance = Operation(
        INFO,
        "get_parallax_compensation_distance",
        JsonRpcBinding("getParallaxCompensationDistance", PATH),
        result=GetParallaxCompensationDistanceResult,
        access="admin",
        effect="read",
    )
    set_parallax_compensation_distance = Operation(
        INFO,
        "set_parallax_compensation_distance",
        JsonRpcBinding("setParallaxCompensationDistance", PATH),
        params=SetParallaxCompensationDistanceRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    rotate_angle = Operation(
        INFO,
        "rotate_angle",
        JsonRpcBinding("rotateAngle", PATH),
        params=RotateAngleRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    restore = Operation(
        INFO, "restore", JsonRpcBinding("restore", PATH), params=RestoreRequest, access="admin", effect="action"
    )
    set_horizon_straightening_enabled = Operation(
        INFO,
        "set_horizon_straightening_enabled",
        JsonRpcBinding("setHorizonStraighteningEnabled", PATH),
        params=SetHorizonStraighteningEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_horizon_straightening_enabled = Operation(
        INFO,
        "get_horizon_straightening_enabled",
        JsonRpcBinding("getHorizonStraighteningEnabled", PATH),
        result=GetHorizonStraighteningEnabledResult,
        access="admin",
        effect="read",
    )
    get_horizon_straightening_properties = Operation(
        INFO,
        "get_horizon_straightening_properties",
        JsonRpcBinding("getHorizonStraighteningProperties", PATH),
        result=GetHorizonStraighteningPropertiesResult,
        access="admin",
        effect="read",
        errors={2215: ErrorCode("Horizon straightening is not enabled", "unavailable")},
    )
    set_horizon_straightening_tilt = Operation(
        INFO,
        "set_horizon_straightening_tilt",
        JsonRpcBinding("setHorizonStraighteningTilt", PATH),
        params=SetHorizonStraighteningTiltRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={2215: ErrorCode("Horizon straightening is not enabled", "unavailable")},
    )
    set_horizon_straightening_stretch_enabled = Operation(
        INFO,
        "set_horizon_straightening_stretch_enabled",
        JsonRpcBinding("setHorizonStraighteningStretchEnabled", PATH),
        params=SetHorizonStraighteningStretchEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={2215: ErrorCode("Horizon straightening is not enabled", "unavailable")},
    )
    set_horizon_straightening_stretch_amount = Operation(
        INFO,
        "set_horizon_straightening_stretch_amount",
        JsonRpcBinding("setHorizonStraighteningStretchAmount", PATH),
        params=SetHorizonStraighteningStretchAmountRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            2215: ErrorCode("Horizon straightening is not enabled", "unavailable"),
            2216: ErrorCode("Horizon straightening stretch is disabled", "unavailable"),
        },
    )
    get_field_of_view = Operation(
        INFO,
        "get_field_of_view",
        JsonRpcBinding("getFieldOfView", PATH),
        result=GetFieldOfViewResult,
        access="admin",
        effect="read",
    )
    get_stitching_enabled = Operation(
        INFO,
        "get_stitching_enabled",
        JsonRpcBinding("getStitchingEnabled", PATH),
        result=GetStitchingEnabledResult,
        access="admin",
        effect="read",
    )
    set_stitching_enabled = Operation(
        INFO,
        "set_stitching_enabled",
        JsonRpcBinding("setStitchingEnabled", PATH),
        params=SetStitchingEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class StitchingApi(SyncApi):
    """Stitching (``stitching``, version 3)."""

    INFO = INFO

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> StitchingCapabilities:
        """Retrieve which stitching.cgi methods the device supports, and the parameter limits.

        Access: admin.
        """
        return self._run(OPS.get_capabilities, None, {}, request_options)

    def get_blending_amount(self, *, request_options: RequestOptions | None = None) -> GetBlendingAmountResult:
        """Retrieve the current blending amount. Access: admin."""
        return self._run(OPS.get_blending_amount, None, {}, request_options)

    def set_blending_amount(self, *, blending_amount: float, request_options: RequestOptions | None = None) -> None:
        """Set the blending amount.

        Useful when white balance differs between sensors. 0 when there is only one object at the parallax
        compensation distance around the seams (sharp transition); increase when many objects at different
        distances (blurs skewed alignments).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_blending_amount, None, {"blending_amount": blending_amount}, request_options)

    def get_parallax_compensation_distance(
        self, *, request_options: RequestOptions | None = None
    ) -> GetParallaxCompensationDistanceResult:
        """Retrieve the current parallax compensation distance (meters). Access: admin."""
        return self._run(OPS.get_parallax_compensation_distance, None, {}, request_options)

    def set_parallax_compensation_distance(
        self, *, parallax_compensation_distance: float, request_options: RequestOptions | None = None
    ) -> None:
        """Set the distance (meters) to the objects where seam alignment is calculated.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_parallax_compensation_distance,
            None,
            {"parallax_compensation_distance": parallax_compensation_distance},
            request_options,
        )

    def rotate_angle(
        self,
        *,
        id: int,
        axis: Literal["pan", "tilt", "roll"],
        angle: float,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Rotate a sensor image on pan, tilt or roll to align the panoramic view.

        Hard limits -180..+180 degrees; lower product/sensor dependent soft limits exist (e.g. AXIS
        Q3819-PVE ±1.4 degrees pan). Exceeding them can cause unknown image behavior.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.rotate_angle, None, {"id": id, "axis": axis, "angle": angle}, request_options)

    def restore(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Restore a sensor to factory default (removes changes from setBlendingAmount, setParallaxCompensationDistance and rotateAngle).

        Access: admin.
        """
        self._run(OPS.restore, None, {"id": id}, request_options)

    def set_horizon_straightening_enabled(
        self, *, horizon_straightening_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable horizon straightening. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_horizon_straightening_enabled,
            None,
            {"horizon_straightening_enabled": horizon_straightening_enabled},
            request_options,
        )

    def get_horizon_straightening_enabled(
        self, *, request_options: RequestOptions | None = None
    ) -> GetHorizonStraighteningEnabledResult:
        """Retrieve if horizon straightening is enabled. Access: admin."""
        return self._run(OPS.get_horizon_straightening_enabled, None, {}, request_options)

    def get_horizon_straightening_properties(
        self, *, request_options: RequestOptions | None = None
    ) -> GetHorizonStraighteningPropertiesResult:
        """Retrieve horizon straightening tilt, stretch enabled and stretch amount. Access: admin."""
        return self._run(OPS.get_horizon_straightening_properties, None, {}, request_options)

    def set_horizon_straightening_tilt(
        self, *, horizon_straightening_tilt: float, request_options: RequestOptions | None = None
    ) -> None:
        """Set the position of the straight horizon (so it is not in the middle of the image).

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_horizon_straightening_tilt,
            None,
            {"horizon_straightening_tilt": horizon_straightening_tilt},
            request_options,
        )

    def set_horizon_straightening_stretch_enabled(
        self, *, horizon_straightening_stretch_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable horizon straightening stretch.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_horizon_straightening_stretch_enabled,
            None,
            {"horizon_straightening_stretch_enabled": horizon_straightening_stretch_enabled},
            request_options,
        )

    def set_horizon_straightening_stretch_amount(
        self, *, horizon_straightening_stretch_amount: float, request_options: RequestOptions | None = None
    ) -> None:
        """Set the horizon straightening stretch amount.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_horizon_straightening_stretch_amount,
            None,
            {"horizon_straightening_stretch_amount": horizon_straightening_stretch_amount},
            request_options,
        )

    def get_field_of_view(self, *, request_options: RequestOptions | None = None) -> GetFieldOfViewResult:
        """Retrieve the supported horizontal and vertical field of view. Access: admin."""
        return self._run(OPS.get_field_of_view, None, {}, request_options)

    def get_stitching_enabled(self, *, request_options: RequestOptions | None = None) -> GetStitchingEnabledResult:
        """Retrieve the most recent stitching status set by set_stitching_enabled. Product dependent.

        Access: admin.
        """
        return self._run(OPS.get_stitching_enabled, None, {}, request_options)

    def set_stitching_enabled(self, *, stitching_enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Enable or disable stitching. This method is product dependent.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_stitching_enabled, None, {"stitching_enabled": stitching_enabled}, request_options)


class AsyncStitchingApi(AsyncApi):
    """Stitching (``stitching``, version 3)."""

    INFO = INFO

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> StitchingCapabilities:
        """Retrieve which stitching.cgi methods the device supports, and the parameter limits.

        Access: admin.
        """
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    async def get_blending_amount(self, *, request_options: RequestOptions | None = None) -> GetBlendingAmountResult:
        """Retrieve the current blending amount. Access: admin."""
        return await self._run(OPS.get_blending_amount, None, {}, request_options)

    async def set_blending_amount(
        self, *, blending_amount: float, request_options: RequestOptions | None = None
    ) -> None:
        """Set the blending amount.

        Useful when white balance differs between sensors. 0 when there is only one object at the parallax
        compensation distance around the seams (sharp transition); increase when many objects at different
        distances (blurs skewed alignments).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_blending_amount, None, {"blending_amount": blending_amount}, request_options)

    async def get_parallax_compensation_distance(
        self, *, request_options: RequestOptions | None = None
    ) -> GetParallaxCompensationDistanceResult:
        """Retrieve the current parallax compensation distance (meters). Access: admin."""
        return await self._run(OPS.get_parallax_compensation_distance, None, {}, request_options)

    async def set_parallax_compensation_distance(
        self, *, parallax_compensation_distance: float, request_options: RequestOptions | None = None
    ) -> None:
        """Set the distance (meters) to the objects where seam alignment is calculated.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_parallax_compensation_distance,
            None,
            {"parallax_compensation_distance": parallax_compensation_distance},
            request_options,
        )

    async def rotate_angle(
        self,
        *,
        id: int,
        axis: Literal["pan", "tilt", "roll"],
        angle: float,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Rotate a sensor image on pan, tilt or roll to align the panoramic view.

        Hard limits -180..+180 degrees; lower product/sensor dependent soft limits exist (e.g. AXIS
        Q3819-PVE ±1.4 degrees pan). Exceeding them can cause unknown image behavior.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.rotate_angle, None, {"id": id, "axis": axis, "angle": angle}, request_options)

    async def restore(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Restore a sensor to factory default (removes changes from setBlendingAmount, setParallaxCompensationDistance and rotateAngle).

        Access: admin.
        """
        await self._run(OPS.restore, None, {"id": id}, request_options)

    async def set_horizon_straightening_enabled(
        self, *, horizon_straightening_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable horizon straightening. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_horizon_straightening_enabled,
            None,
            {"horizon_straightening_enabled": horizon_straightening_enabled},
            request_options,
        )

    async def get_horizon_straightening_enabled(
        self, *, request_options: RequestOptions | None = None
    ) -> GetHorizonStraighteningEnabledResult:
        """Retrieve if horizon straightening is enabled. Access: admin."""
        return await self._run(OPS.get_horizon_straightening_enabled, None, {}, request_options)

    async def get_horizon_straightening_properties(
        self, *, request_options: RequestOptions | None = None
    ) -> GetHorizonStraighteningPropertiesResult:
        """Retrieve horizon straightening tilt, stretch enabled and stretch amount. Access: admin."""
        return await self._run(OPS.get_horizon_straightening_properties, None, {}, request_options)

    async def set_horizon_straightening_tilt(
        self, *, horizon_straightening_tilt: float, request_options: RequestOptions | None = None
    ) -> None:
        """Set the position of the straight horizon (so it is not in the middle of the image).

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_horizon_straightening_tilt,
            None,
            {"horizon_straightening_tilt": horizon_straightening_tilt},
            request_options,
        )

    async def set_horizon_straightening_stretch_enabled(
        self, *, horizon_straightening_stretch_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable horizon straightening stretch.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_horizon_straightening_stretch_enabled,
            None,
            {"horizon_straightening_stretch_enabled": horizon_straightening_stretch_enabled},
            request_options,
        )

    async def set_horizon_straightening_stretch_amount(
        self, *, horizon_straightening_stretch_amount: float, request_options: RequestOptions | None = None
    ) -> None:
        """Set the horizon straightening stretch amount.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_horizon_straightening_stretch_amount,
            None,
            {"horizon_straightening_stretch_amount": horizon_straightening_stretch_amount},
            request_options,
        )

    async def get_field_of_view(self, *, request_options: RequestOptions | None = None) -> GetFieldOfViewResult:
        """Retrieve the supported horizontal and vertical field of view. Access: admin."""
        return await self._run(OPS.get_field_of_view, None, {}, request_options)

    async def get_stitching_enabled(
        self, *, request_options: RequestOptions | None = None
    ) -> GetStitchingEnabledResult:
        """Retrieve the most recent stitching status set by set_stitching_enabled. Product dependent.

        Access: admin.
        """
        return await self._run(OPS.get_stitching_enabled, None, {}, request_options)

    async def set_stitching_enabled(
        self, *, stitching_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable stitching. This method is product dependent.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_stitching_enabled, None, {"stitching_enabled": stitching_enabled}, request_options)
