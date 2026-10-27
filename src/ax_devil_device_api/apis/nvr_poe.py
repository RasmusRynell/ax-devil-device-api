# GENERATED from specs/apis/network-video/nvr-poe.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Recorder PoE PSE control: port statuses, enable/disable port power, total power limit, keep-power-during-reboot (/axis-cgi/nvr/poe/*.cgi, XML responses).

Docs: https://developer.axis.com/vapix/network-video/nvr-poe-switch-configuration/
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """The supported XML schema version, major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """The deprecation status. Defaults to false."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class PortMode(Model):
    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the specified port is enabled."""


PortStatusCode = Literal[0, 1, 2, 3, 4, 5]


class PortStatus(Model):
    port: int = Field(validation_alias="Port", serialization_alias="Port")
    """The port number."""
    status_code: PortStatusCode = Field(validation_alias="StatusCode", serialization_alias="StatusCode")
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """A human-readable status description."""
    extra: str | None = Field(default=None, validation_alias="Extra", serialization_alias="Extra")
    """Container for additional status information."""
    class_power_limit: float | None = Field(
        default=None, validation_alias="ClassPowerLimit", serialization_alias="ClassPowerLimit"
    )
    """The maximum power delivered by the PSE for the detected PD class, in watts."""
    poe_class: int | None = Field(default=None, validation_alias="PoeClass", serialization_alias="PoeClass")
    """The detected PoE class of the PD. Absent when the device sends an empty element (no class detected)."""
    allocated_power: float | None = Field(
        default=None, validation_alias="AllocatedPower", serialization_alias="AllocatedPower"
    )
    """The allocated power for the PoE, in watts."""
    power_consumption: float | None = Field(
        default=None, validation_alias="PowerConsumption", serialization_alias="PowerConsumption"
    )
    """A snapshot of the power consumed by the PD."""
    pse_class_limit: int | None = Field(
        default=None, validation_alias="PseClassLimit", serialization_alias="PseClassLimit"
    )
    """The maximum PoE class supported by the port."""
    requested_power: float | None = Field(
        default=None, validation_alias="RequestedPower", serialization_alias="RequestedPower"
    )
    """The power requested by the PD in watts. Absent when the device sends an empty element (no LLDPDU received from the PD)."""


class PortStatuses(Model):
    port_status: list[PortStatus] = Field(validation_alias="PortStatus", serialization_alias="PortStatus")


class TotalPowerLimit(Model):
    limit: float = Field(validation_alias="Limit", serialization_alias="Limit")
    """The total power limit, in watts."""


class KeepPower(Model):
    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the keep power function is active."""


class GetPortModeRequest(Model):
    schemaversion: int
    """The major XML version that should be used along with its highest minor version."""
    port: int
    """The port number."""


class SetPortModeRequest(Model):
    schemaversion: int
    """The major XML version that should be used along with its highest minor version."""
    port: int
    """The port number."""
    enabled: bool
    """Enables (yes) or disables (no) the specified port."""


class GetPortStatusesRequest(Model):
    schemaversion: int
    """The major XML version that should be used along with its highest minor version."""


class GetTotalPowerLimitRequest(Model):
    schemaversion: int
    """The major XML version that should be used along with its highest minor version."""


class GetKeepPowerRequest(Model):
    schemaversion: int
    """The major XML version that should be used along with its highest minor version."""


class SetKeepPowerRequest(Model):
    schemaversion: int
    """The major XML version that should be used along with its highest minor version."""
    enabled: bool
    """yes: power is kept when the recorder is rebooting; no: power is cut."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/nvr/poe/schemaversions.cgi"

INFO = ApiInfo(
    id="nvr-poe",
    name="NVR PoE switch configuration",
    family=Family.CGI,
    discovery=(ApiDiscovery("nvr-poe"),),
    docs=("https://developer.axis.com/vapix/network-video/nvr-poe-switch-configuration/",),
    errors={
        10: ErrorCode("An error occurred while processing the request."),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        30: ErrorCode("Unauthorized request.", "access_denied"),
        40: ErrorCode("Specified version not supported.", "unsupported"),
        50: ErrorCode("Not supported.", "unsupported"),
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
                    root="SchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="operator",
        effect="read",
    )
    get_port_mode = Operation(
        INFO,
        "get_port_mode",
        CgiBinding(
            "/axis-cgi/nvr/poe/getportmode.cgi",
            args=(CgiArg("schemaversion"), CgiArg("port")),
            reply=Xml(map=XmlMap(fields=(XmlField("Enabled", source="child"),), root="GetPortModeSuccess")),
        ),
        params=GetPortModeRequest,
        result=PortMode,
        access="operator",
        effect="read",
    )
    set_port_mode = Operation(
        INFO,
        "set_port_mode",
        CgiBinding(
            "/axis-cgi/nvr/poe/setportmode.cgi",
            args=(CgiArg("schemaversion"), CgiArg("port"), CgiArg("enabled", style="axis_bool")),
            reply=Xml(),
        ),
        params=SetPortModeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_port_statuses = Operation(
        INFO,
        "get_port_statuses",
        CgiBinding(
            "/axis-cgi/nvr/poe/getportstatuses.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "PortStatus",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("Port", source="child"),
                                    XmlField("StatusCode", source="child"),
                                    XmlField("Description", source="child"),
                                    XmlField("Extra", source="child"),
                                    XmlField("ClassPowerLimit", source="child"),
                                    XmlField("PoeClass", source="child"),
                                    XmlField("AllocatedPower", source="child"),
                                    XmlField("PowerConsumption", source="child"),
                                    XmlField("PseClassLimit", source="child"),
                                    XmlField("RequestedPower", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="GetPortStatusesSuccess",
                )
            ),
        ),
        params=GetPortStatusesRequest,
        result=PortStatuses,
        access="operator",
        effect="read",
    )
    get_total_power_limit = Operation(
        INFO,
        "get_total_power_limit",
        CgiBinding(
            "/axis-cgi/nvr/poe/gettotalpowerlimit.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(map=XmlMap(fields=(XmlField("Limit", source="child"),), root="GetTotalPowerLimitSuccess")),
        ),
        params=GetTotalPowerLimitRequest,
        result=TotalPowerLimit,
        access="operator",
        effect="read",
    )
    get_keep_power = Operation(
        INFO,
        "get_keep_power",
        CgiBinding(
            "/axis-cgi/nvr/poe/getkeeppower.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(map=XmlMap(fields=(XmlField("Enabled", source="child"),), root="GetKeepPowerSuccess")),
        ),
        params=GetKeepPowerRequest,
        result=KeepPower,
        access="operator",
        effect="read",
    )
    set_keep_power = Operation(
        INFO,
        "set_keep_power",
        CgiBinding(
            "/axis-cgi/nvr/poe/setkeeppower.cgi",
            args=(CgiArg("schemaversion"), CgiArg("enabled", style="axis_bool")),
            reply=Xml(),
        ),
        params=SetKeepPowerRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class NvrPoeApi(SyncApi):
    """NVR PoE switch configuration (``nvr-poe``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve a listing of all supported XML schema versions. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def get_port_mode(
        self, *, schemaversion: int, port: int, request_options: RequestOptions | None = None
    ) -> PortMode:
        """Check the status of the PoE port mode. Access: operator."""
        return self._run(OPS.get_port_mode, None, {"schemaversion": schemaversion, "port": port}, request_options)

    def set_port_mode(
        self, *, schemaversion: int, port: int, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the specified PoE port. Changes only the fields given. Access: operator."""
        self._run(
            OPS.set_port_mode, None, {"schemaversion": schemaversion, "port": port, "enabled": enabled}, request_options
        )

    def get_port_statuses(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> PortStatuses:
        """Retrieve status information for all available PoE ports. Access: operator."""
        return self._run(OPS.get_port_statuses, None, {"schemaversion": schemaversion}, request_options)

    def get_total_power_limit(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> TotalPowerLimit:
        """Get the total power limit of the PSE (watts). Access: operator."""
        return self._run(OPS.get_total_power_limit, None, {"schemaversion": schemaversion}, request_options)

    def get_keep_power(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> KeepPower:
        """Check whether the keep power function (keep PoE power during recorder reboot) is active.

        Returns error 50 (Not supported) on devices where the CGI is not supported.

        Access: operator.
        """
        return self._run(OPS.get_keep_power, None, {"schemaversion": schemaversion}, request_options)

    def set_keep_power(
        self, *, schemaversion: int, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Control whether PoE power should be kept active when the recorder is rebooting.

        Returns error 50 (Not supported) on devices where the CGI is not supported.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_keep_power, None, {"schemaversion": schemaversion, "enabled": enabled}, request_options)


class AsyncNvrPoeApi(AsyncApi):
    """NVR PoE switch configuration (``nvr-poe``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve a listing of all supported XML schema versions. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def get_port_mode(
        self, *, schemaversion: int, port: int, request_options: RequestOptions | None = None
    ) -> PortMode:
        """Check the status of the PoE port mode. Access: operator."""
        return await self._run(OPS.get_port_mode, None, {"schemaversion": schemaversion, "port": port}, request_options)

    async def set_port_mode(
        self, *, schemaversion: int, port: int, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the specified PoE port. Changes only the fields given. Access: operator."""
        await self._run(
            OPS.set_port_mode, None, {"schemaversion": schemaversion, "port": port, "enabled": enabled}, request_options
        )

    async def get_port_statuses(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> PortStatuses:
        """Retrieve status information for all available PoE ports. Access: operator."""
        return await self._run(OPS.get_port_statuses, None, {"schemaversion": schemaversion}, request_options)

    async def get_total_power_limit(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> TotalPowerLimit:
        """Get the total power limit of the PSE (watts). Access: operator."""
        return await self._run(OPS.get_total_power_limit, None, {"schemaversion": schemaversion}, request_options)

    async def get_keep_power(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> KeepPower:
        """Check whether the keep power function (keep PoE power during recorder reboot) is active.

        Returns error 50 (Not supported) on devices where the CGI is not supported.

        Access: operator.
        """
        return await self._run(OPS.get_keep_power, None, {"schemaversion": schemaversion}, request_options)

    async def set_keep_power(
        self, *, schemaversion: int, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Control whether PoE power should be kept active when the recorder is rebooting.

        Returns error 50 (Not supported) on devices where the CGI is not supported.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_keep_power, None, {"schemaversion": schemaversion, "enabled": enabled}, request_options)
