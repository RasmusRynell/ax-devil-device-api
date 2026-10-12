# GENERATED from specs/apis/network-video/isotherm.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Enable isothermal imaging and set the isotherm palette temperature ranges (lower, middle, upper limits).

Docs: https://developer.axis.com/vapix/network-video/thermal-imaging/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """major.minor"""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


IsothermMode = Literal["enabled", "disabled"]


class ModeStatus(Model):
    mode: IsothermMode = Field(validation_alias="Mode", serialization_alias="Mode")


class Limits(Model):
    """Temperature limits in the unit set by the temperature alarm API (Celsius or Fahrenheit)."""

    upper: int = Field(validation_alias="Upper", serialization_alias="Upper")
    """The upper temperature limit."""
    middle: int = Field(validation_alias="Middle", serialization_alias="Middle")
    """The middle temperature limit."""
    lower: int = Field(validation_alias="Lower", serialization_alias="Lower")
    """The lower temperature limit."""


class SetModeRequest(Model):
    mode: IsothermMode


class SetLimitsRequest(Model):
    upper: int | None = None
    """The upper temperature limit, in the unit set by temperature_alarm/settemperaturescale.cgi."""
    middle: int | None = None
    """The middle temperature limit, in the unit set by temperature_alarm/settemperaturescale.cgi."""
    lower: int | None = None
    """The lower temperature limit, in the unit set by temperature_alarm/settemperaturescale.cgi."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/isotherm/schemaversions.cgi"

INFO = ApiInfo(
    id="isotherm",
    name="Isotherm API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.Isotherm.Isotherm", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/thermal-imaging/",),
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
                    root="SchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="viewer",
        effect="read",
        errors={
            10: ErrorCode("Error while processing the request."),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )
    set_mode = Operation(
        INFO,
        "set_mode",
        CgiBinding("/axis-cgi/isotherm/setmode.cgi", args=(CgiArg("mode"),), reply=Xml()),
        params=SetModeRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request."),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )
    get_mode = Operation(
        INFO,
        "get_mode",
        CgiBinding(
            "/axis-cgi/isotherm/getmode.cgi",
            reply=Xml(map=XmlMap(fields=(XmlField("Mode", source="child"),), root="Success/GetModeSuccess")),
        ),
        result=ModeStatus,
        access="viewer",
        effect="read",
        errors={
            10: ErrorCode("Error while processing the request."),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )
    set_limits = Operation(
        INFO,
        "set_limits",
        CgiBinding(
            "/axis-cgi/isotherm/setlimits.cgi", args=(CgiArg("upper"), CgiArg("middle"), CgiArg("lower")), reply=Xml()
        ),
        params=SetLimitsRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request."),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )
    get_limits = Operation(
        INFO,
        "get_limits",
        CgiBinding(
            "/axis-cgi/isotherm/getlimits.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("Upper", source="child"),
                        XmlField("Middle", source="child"),
                        XmlField("Lower", source="child"),
                    ),
                    root="Success/GetLimitsSuccess",
                )
            ),
        ),
        result=Limits,
        access="viewer",
        effect="read",
        errors={
            10: ErrorCode("Error while processing the request."),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class IsothermApi(SyncApi):
    """Isotherm API (``isotherm``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: viewer."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def set_mode(self, *, mode: IsothermMode, request_options: RequestOptions | None = None) -> None:
        """Enable or disable isothermal imaging. Changes only the fields given. Access: operator."""
        self._run(OPS.set_mode, None, {"mode": mode}, request_options)

    def get_mode(self, *, request_options: RequestOptions | None = None) -> ModeStatus:
        """Check if isothermal imaging is enabled. Access: viewer."""
        return self._run(OPS.get_mode, None, {}, request_options)

    def set_limits(
        self,
        *,
        upper: int | MISSING = MISSING,
        middle: int | MISSING = MISSING,
        lower: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the upper, middle and lower limits of the isotherm palette temperature ranges.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_limits, None, {"upper": upper, "middle": middle, "lower": lower}, request_options)

    def get_limits(self, *, request_options: RequestOptions | None = None) -> Limits:
        """Retrieve the current isotherm temperature limits. Access: viewer."""
        return self._run(OPS.get_limits, None, {}, request_options)


class AsyncIsothermApi(AsyncApi):
    """Isotherm API (``isotherm``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: viewer."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def set_mode(self, *, mode: IsothermMode, request_options: RequestOptions | None = None) -> None:
        """Enable or disable isothermal imaging. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_mode, None, {"mode": mode}, request_options)

    async def get_mode(self, *, request_options: RequestOptions | None = None) -> ModeStatus:
        """Check if isothermal imaging is enabled. Access: viewer."""
        return await self._run(OPS.get_mode, None, {}, request_options)

    async def set_limits(
        self,
        *,
        upper: int | MISSING = MISSING,
        middle: int | MISSING = MISSING,
        lower: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the upper, middle and lower limits of the isotherm palette temperature ranges.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_limits, None, {"upper": upper, "middle": middle, "lower": lower}, request_options)

    async def get_limits(self, *, request_options: RequestOptions | None = None) -> Limits:
        """Retrieve the current isotherm temperature limits. Access: viewer."""
        return await self._run(OPS.get_limits, None, {}, request_options)
