# GENERATED from specs/apis/network-video/shock-detection.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Enable/disable shock detection and control its sensitivity on products with built-in orientation devices; emits tns1:Device/tnsaxis:Tampering/ShockDetected.

Docs: https://developer.axis.com/vapix/network-video/shock-detection-api/
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


class ShockDetectionStatus(Model):
    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """True if shock detection is enabled, false if it is disabled."""


class SensitivityLevel(Model):
    level: int = Field(validation_alias="Level", serialization_alias="Level", ge=0, le=100)
    """The sensitivity level: 0 is low sensitivity and 100 is high."""


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version in the form major.minor."""
    deprecated: str | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """"true" if this version of the XML schema is deprecated and should not be used, otherwise "false". The device may send an empty element, which means false."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class GetEnabledRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetEnabledRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    enabled: bool
    """true enables shock detection, false disables it."""


class GetSensitivityLevelRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetSensitivityLevelRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    level: int = Field(ge=0, le=100)
    """The shock detection sensitivity level: 0 is low sensitivity and 100 is high."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/shockdetection/getenabled.cgi"

INFO = ApiInfo(
    id="shock-detection",
    name="Shock detection API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.Tampering.ShockDetection", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/shock-detection-api/",),
    errors={
        10: ErrorCode("Error while processing the request."),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
    },
)


class OPS:
    get_enabled = Operation(
        INFO,
        "get_enabled",
        CgiBinding(
            PATH,
            args=(CgiArg("schemaversion"),),
            reply=Xml(map=XmlMap(fields=(XmlField("Enabled", source="child"),), root="Success/GetEnabledSuccess")),
        ),
        params=GetEnabledRequest,
        result=ShockDetectionStatus,
        access="operator",
        effect="read",
    )
    set_enabled = Operation(
        INFO,
        "set_enabled",
        CgiBinding(
            "/axis-cgi/shockdetection/setenabled.cgi", args=(CgiArg("schemaversion"), CgiArg("enabled")), reply=Xml()
        ),
        params=SetEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_sensitivity_level = Operation(
        INFO,
        "get_sensitivity_level",
        CgiBinding(
            "/axis-cgi/shockdetection/getsensitivitylevel.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("Level", source="child"),),
                    root="Success/GetSensitivityLevelSuccess/SensitivityLevel",
                )
            ),
        ),
        params=GetSensitivityLevelRequest,
        result=SensitivityLevel,
        access="operator",
        effect="read",
    )
    set_sensitivity_level = Operation(
        INFO,
        "set_sensitivity_level",
        CgiBinding(
            "/axis-cgi/shockdetection/setsensitivitylevel.cgi",
            args=(CgiArg("schemaversion"), CgiArg("level")),
            reply=Xml(),
        ),
        params=SetSensitivityLevelRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            30: ErrorCode(
                "Unable to set shock detection sensitivity. Specified value is out of range.", "invalid_argument"
            )
        },
    )
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            "/axis-cgi/shockdetection/getschemaversion.cgi",
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


# ---------------------------------------------------------------------------
# API classes


class ShockDetectionApi(SyncApi):
    """Shock detection API (``shock-detection``)."""

    INFO = INFO

    def get_enabled(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> ShockDetectionStatus:
        """Check if shock detection is enabled. Access: operator."""
        return self._run(OPS.get_enabled, None, {"schemaversion": schemaversion}, request_options)

    def set_enabled(self, *, schemaversion: int, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Enable or disable shock detection. Changes only the fields given. Access: operator."""
        self._run(OPS.set_enabled, None, {"schemaversion": schemaversion, "enabled": enabled}, request_options)

    def get_sensitivity_level(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> SensitivityLevel:
        """Retrieve the current sensitivity level. Access: operator."""
        return self._run(OPS.get_sensitivity_level, None, {"schemaversion": schemaversion}, request_options)

    def set_sensitivity_level(
        self, *, schemaversion: int, level: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the shock detection sensitivity level (0 low to 100 high).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_sensitivity_level, None, {"schemaversion": schemaversion, "level": level}, request_options)

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)


class AsyncShockDetectionApi(AsyncApi):
    """Shock detection API (``shock-detection``)."""

    INFO = INFO

    async def get_enabled(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> ShockDetectionStatus:
        """Check if shock detection is enabled. Access: operator."""
        return await self._run(OPS.get_enabled, None, {"schemaversion": schemaversion}, request_options)

    async def set_enabled(
        self, *, schemaversion: int, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable shock detection. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_enabled, None, {"schemaversion": schemaversion, "enabled": enabled}, request_options)

    async def get_sensitivity_level(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> SensitivityLevel:
        """Retrieve the current sensitivity level. Access: operator."""
        return await self._run(OPS.get_sensitivity_level, None, {"schemaversion": schemaversion}, request_options)

    async def set_sensitivity_level(
        self, *, schemaversion: int, level: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the shock detection sensitivity level (0 low to 100 high).

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_sensitivity_level, None, {"schemaversion": schemaversion, "level": level}, request_options
        )

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)
