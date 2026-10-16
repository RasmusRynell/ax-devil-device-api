# GENERATED from specs/apis/radar/radar-properties.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Inspect radar properties — detection range and angle limits, maximum number of radar objects, maximum object speed and network pairing status.

Docs: https://developer.axis.com/vapix/radar/radar-properties/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import FixedVersion, JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class RadarProperties(Model):
    device: str | None = None
    """The product number of the radar device (e.g. D2210-VE)."""
    min_detection_range: int | None = Field(
        default=None, validation_alias="minDetectionRange", serialization_alias="minDetectionRange"
    )
    """The minimum detection range."""
    max_detection_range: int | None = Field(
        default=None, validation_alias="maxDetectionRange", serialization_alias="maxDetectionRange"
    )
    """The maximum detection range."""
    min_horizontal_angle: int | None = Field(
        default=None, validation_alias="minHorizontalAngle", serialization_alias="minHorizontalAngle"
    )
    """The minimum horizontal angle."""
    max_horizontal_angle: int | None = Field(
        default=None, validation_alias="maxHorizontalAngle", serialization_alias="maxHorizontalAngle"
    )
    """The maximum horizontal angle."""
    min_vertical_angle: int | None = Field(
        default=None, validation_alias="minVerticalAngle", serialization_alias="minVerticalAngle"
    )
    """The minimum vertical angle."""
    max_vertical_angle: int | None = Field(
        default=None, validation_alias="maxVerticalAngle", serialization_alias="maxVerticalAngle"
    )
    """The maximum vertical angle."""
    max_radar_objects: int | None = Field(
        default=None, validation_alias="maxRadarObjects", serialization_alias="maxRadarObjects"
    )
    """The maximum number of radar objects."""
    max_object_speed: float | None = Field(
        default=None, validation_alias="maxObjectSpeed", serialization_alias="maxObjectSpeed"
    )
    """The maximum object speed."""
    network_paired: bool | None = Field(
        default=None, validation_alias="networkPaired", serialization_alias="networkPaired"
    )
    """Whether the radar device is paired with another device."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/properties.cgi"

INFO = ApiInfo(
    id="radar-properties",
    name="Radar Properties",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("radar-properties"),),
    docs=("https://developer.axis.com/vapix/radar/radar-properties/",),
    errors={
        1100: ErrorCode("Internal error.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
        2106: ErrorCode("Authentication failed.", "access_denied"),
        2107: ErrorCode("Transport level error.", "unavailable"),
    },
)


class OPS:
    get_radar_properties = Operation(
        INFO,
        "get_radar_properties",
        JsonRpcBinding("getRadarProperties", PATH, negotiation=FixedVersion(ApiVersion(1, 0))),
        result=RadarProperties,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RadarPropertiesApi(SyncApi):
    """Radar Properties (``radar-properties``, version 1)."""

    INFO = INFO

    def get_radar_properties(self, *, request_options: RequestOptions | None = None) -> RadarProperties:
        """Retrieve all radar properties. Access: admin."""
        return self._run(OPS.get_radar_properties, None, {}, request_options)


class AsyncRadarPropertiesApi(AsyncApi):
    """Radar Properties (``radar-properties``, version 1)."""

    INFO = INFO

    async def get_radar_properties(self, *, request_options: RequestOptions | None = None) -> RadarProperties:
        """Retrieve all radar properties. Access: admin."""
        return await self._run(OPS.get_radar_properties, None, {}, request_options)
