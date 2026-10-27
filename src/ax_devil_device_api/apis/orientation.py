# GENERATED from specs/apis/network-video/orientation-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve camera lens orientation (longitudinal and lateral angles) from built-in gyroscopes/accelerometers.

Docs: https://developer.axis.com/vapix/network-video/orientation-api/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version, major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class LongitudinalAngle(Model):
    """The lens rotation around its longitudinal axis."""

    value: int = Field(validation_alias="Value", serialization_alias="Value", ge=0, le=359)
    """The angle in degrees (0 to 359)."""


class LateralAngle(Model):
    """The angle between the lens longitudinal axis and a line perpendicular to the ground; 0 is straight down, 180 straight up."""

    value: int = Field(validation_alias="Value", serialization_alias="Value", ge=0, le=180)
    """The angle in degrees (0 to 180)."""


class GetLongitudinalValueRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class GetLateralValueRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/orientation/getschemaversions.cgi"

INFO = ApiInfo(
    id="orientation-api",
    name="Orientation API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.Orientation.Reporting", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/orientation-api/",),
    errors={
        10: ErrorCode("Error while processing the request."),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
    },
)


class OPS:
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            PATH,
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "SchemaVersion",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("VersionNumber", source="child"),
                                    XmlField("Deprecated", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetSchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="operator",
        effect="read",
    )
    get_longitudinal_value = Operation(
        INFO,
        "get_longitudinal_value",
        CgiBinding(
            "/axis-cgi/orientation/getlongitudinalvalue.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("Value", source="child"),),
                    root="Success/GetLongitudinalValueSuccess/LongitudinalValue",
                )
            ),
        ),
        params=GetLongitudinalValueRequest,
        result=LongitudinalAngle,
        access="operator",
        effect="read",
    )
    get_lateral_value = Operation(
        INFO,
        "get_lateral_value",
        CgiBinding(
            "/axis-cgi/orientation/getlateralvalue.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("Value", source="child"),), root="Success/GetLateralValueSuccess/LateralValue"
                )
            ),
        ),
        params=GetLateralValueRequest,
        result=LateralAngle,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class OrientationApi(SyncApi):
    """Orientation API (``orientation-api``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve supported XML schema versions. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def get_longitudinal_value(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> LongitudinalAngle:
        """Get the longitudinal angle. Access: operator."""
        return self._run(OPS.get_longitudinal_value, None, {"schemaversion": schemaversion}, request_options)

    def get_lateral_value(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> LateralAngle:
        """Get the lateral angle. Access: operator."""
        return self._run(OPS.get_lateral_value, None, {"schemaversion": schemaversion}, request_options)


class AsyncOrientationApi(AsyncApi):
    """Orientation API (``orientation-api``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve supported XML schema versions. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def get_longitudinal_value(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> LongitudinalAngle:
        """Get the longitudinal angle. Access: operator."""
        return await self._run(OPS.get_longitudinal_value, None, {"schemaversion": schemaversion}, request_options)

    async def get_lateral_value(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> LateralAngle:
        """Get the lateral angle. Access: operator."""
        return await self._run(OPS.get_lateral_value, None, {"schemaversion": schemaversion}, request_options)
