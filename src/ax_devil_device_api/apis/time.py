# GENERATED from specs/apis/device-configuration/time-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the date, time and time zone (IANA, POSIX or DHCP) of the device.

Docs: https://developer.axis.com/vapix/device-configuration/time-api/
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class TimeZoneEntry(Model):
    """An object containing time zone information."""

    time_zone: str = Field(validation_alias="timeZone", serialization_alias="timeZone")
    """The time zone string."""


TimeZonesArray = list[TimeZoneEntry]


class TimeSettings(Model):
    """Handle date and time configuration."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"local_date_time", "max_supported_year"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"local_date_time", "max_supported_year"})
    date_time: str = Field(validation_alias="dateTime", serialization_alias="dateTime")
    """The system date and time in UTC. The format is in ISO 8601. The date should be between Unix time (`UTC 1970-01-01T00:00:00`) and the last second of the year declared in `maxSupportedYear`."""
    local_date_time: str = Field(
        default_factory=not_sent, validation_alias="localDateTime", serialization_alias="localDateTime"
    )
    """The local date and time. The format is in ISO 8601."""
    max_supported_year: int = Field(
        default_factory=not_sent, validation_alias="maxSupportedYear", serialization_alias="maxSupportedYear"
    )
    """Latest year that the date can be set to."""


class Dhcp(Model):
    """Handle DHCP time zone configuration."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"time_zone"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"time_zone"})
    enabled: bool
    """Flag which enables the device to use DHCP time zone from the network."""
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone")
    """The DHCP time zone supplied by the network. Can be in either the IANA or POSIX format. Is set to `null` if the DHCP time zone isn't available."""


class Iana(Model):
    """Handle IANA time zone configuration."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"posix_time_zone", "time_zone"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"posix_time_zone"})
    posix_time_zone: str | None = Field(
        default=None, validation_alias="posixTimeZone", serialization_alias="posixTimeZone"
    )
    """The time zone in POSIX format corresponding to the time of the last transition."""
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone")
    """The system time zone in the IANA format. Example `Europe/Prague`. If set to a valid value, `dhcp.enabled` will be set to `false` and `posix.timeZone` will be set to `null`."""


class Posix(Model):
    """Handle POSIX time zone configuration."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"time_zone"})
    dst_enabled: bool = Field(validation_alias="dstEnabled", serialization_alias="dstEnabled")
    """The DST flag for controlling the POSIX time zone string."""
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone")
    """The system time zone in the POSIX format. Example `EST5EDT,M3.2.0,M11.1.0`. If set to a valid value, `dhcp.enabled` will be set to `false` and `iana.timeZone` will be set to `null`."""


class TimeZone(Model):
    """Handle all settings related to time zones."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"active_time_zone"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"active_time_zone"})
    active_time_zone: str = Field(
        default_factory=not_sent, validation_alias="activeTimeZone", serialization_alias="activeTimeZone"
    )
    """The currently active system time zone, in IANA or POSIX format. The IANA or POSIX time zone if one has been set; with DHCP enabled, the DHCP time zone if the network supplies one, otherwise the factory default time zone."""
    dhcp: Dhcp
    iana: Iana
    posix: Posix


class Time(Model):
    """The whole API tree."""

    time: TimeSettings
    time_zone: TimeZone = Field(validation_alias="timeZone", serialization_alias="timeZone")


class UpdatePosixRequest(Model):
    """Arguments of ``update_posix``."""

    dst_enabled: bool | None = Field(default=None, validation_alias="dstEnabled", serialization_alias="dstEnabled")
    """The DST flag for controlling the POSIX time zone string."""
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone")
    """The system time zone in the POSIX format. Example `EST5EDT,M3.2.0,M11.1.0`. If set to a valid value, `dhcp.enabled` will be set to `false` and `iana.timeZone` will be set to `null`."""


class SetDateTimeRequest(Model):
    date_time: str = Field(validation_alias="dateTime", serialization_alias="dateTime")
    """The system date and time in UTC. The format is in ISO 8601. The date should be between Unix time (`UTC 1970-01-01T00:00:00`) and the last second of the year declared in `maxSupportedYear`."""


class SetDhcpEnabledRequest(Model):
    enabled: bool
    """Flag which enables the device to use DHCP time zone from the network."""


class SetIanaTimeZoneRequest(Model):
    time_zone: str = Field(validation_alias="timeZone", serialization_alias="timeZone")
    """The system time zone in the IANA format. Example `Europe/Prague`. If set to a valid value, `dhcp.enabled` will be set to `false` and `posix.timeZone` will be set to `null`."""


class SetPosixDstEnabledRequest(Model):
    dst_enabled: bool = Field(validation_alias="dstEnabled", serialization_alias="dstEnabled")
    """The DST flag for controlling the POSIX time zone string."""


class SetPosixTimeZoneRequest(Model):
    time_zone: str = Field(validation_alias="timeZone", serialization_alias="timeZone")
    """The system time zone in the POSIX format. Example `EST5EDT,M3.2.0,M11.1.0`. If set to a valid value, `dhcp.enabled` will be set to `false` and `iana.timeZone` will be set to `null`."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/time/v2"

INFO = ApiInfo(
    id="time-config",
    name="Time API",
    family=Family.DCA,
    discovery=(DcaDiscovery("time", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/time-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Time, access="admin", effect="read")
    get_time = Operation(
        INFO, "get_time", DcaBinding("GET", f"{ROOT}/time"), result=TimeSettings, access="admin", effect="read"
    )
    set_date_time = Operation(
        INFO,
        "set_date_time",
        DcaBinding("PATCH", f"{ROOT}/time/dateTime", body="value", body_field="dateTime"),
        params=SetDateTimeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_active_time_zone = Operation(
        INFO,
        "get_active_time_zone",
        DcaBinding("GET", f"{ROOT}/timeZone/activeTimeZone"),
        result=str,
        access="viewer",
        effect="read",
    )
    get_time_zone = Operation(
        INFO, "get_time_zone", DcaBinding("GET", f"{ROOT}/timeZone"), result=TimeZone, access="admin", effect="read"
    )
    get_dhcp = Operation(
        INFO, "get_dhcp", DcaBinding("GET", f"{ROOT}/timeZone/dhcp"), result=Dhcp, access="admin", effect="read"
    )
    set_dhcp_enabled = Operation(
        INFO,
        "set_dhcp_enabled",
        DcaBinding("PATCH", f"{ROOT}/timeZone/dhcp/enabled", body="value", body_field="enabled"),
        params=SetDhcpEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_iana = Operation(
        INFO, "get_iana", DcaBinding("GET", f"{ROOT}/timeZone/iana"), result=Iana, access="admin", effect="read"
    )
    set_iana_time_zone = Operation(
        INFO,
        "set_iana_time_zone",
        DcaBinding("PATCH", f"{ROOT}/timeZone/iana/timeZone", body="value", body_field="timeZone"),
        params=SetIanaTimeZoneRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_time_zone_list = Operation(
        INFO,
        "get_time_zone_list",
        DcaBinding("POST", f"{ROOT}/timeZone/iana/getTimeZoneList", body="object"),
        result=TimeZonesArray,
        access="operator",
        effect="read",
    )
    get_posix = Operation(
        INFO, "get_posix", DcaBinding("GET", f"{ROOT}/timeZone/posix"), result=Posix, access="admin", effect="read"
    )
    update_posix = Operation(
        INFO,
        "update_posix",
        DcaBinding("PATCH", f"{ROOT}/timeZone/posix", body="object"),
        params=UpdatePosixRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_posix_dst_enabled = Operation(
        INFO,
        "set_posix_dst_enabled",
        DcaBinding("PATCH", f"{ROOT}/timeZone/posix/dstEnabled", body="value", body_field="dstEnabled"),
        params=SetPosixDstEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_posix_time_zone = Operation(
        INFO,
        "set_posix_time_zone",
        DcaBinding("PATCH", f"{ROOT}/timeZone/posix/timeZone", body="value", body_field="timeZone"),
        params=SetPosixTimeZoneRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class TimeApi(SyncApi):
    """Time API (``time-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Time:
        """All time and time zone settings. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_time(self, *, request_options: RequestOptions | None = None) -> TimeSettings:
        """Get the date and time settings. Access: admin."""
        return self._run(OPS.get_time, None, {}, request_options)

    def set_date_time(self, *, date_time: str, request_options: RequestOptions | None = None) -> None:
        """Set the system date and time (UTC, ISO 8601).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_date_time, None, {"date_time": date_time}, request_options)

    def get_active_time_zone(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the currently active time zone (IANA or POSIX format). Access: viewer."""
        return self._run(OPS.get_active_time_zone, None, {}, request_options)

    def get_time_zone(self, *, request_options: RequestOptions | None = None) -> TimeZone:
        """Get the time zone settings. Access: admin."""
        return self._run(OPS.get_time_zone, None, {}, request_options)

    def get_dhcp(self, *, request_options: RequestOptions | None = None) -> Dhcp:
        """Get the DHCP time zone settings. Access: admin."""
        return self._run(OPS.get_dhcp, None, {}, request_options)

    def set_dhcp_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the DHCP time zone. Enabling resets the IANA and POSIX time zones to null.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_dhcp_enabled, None, {"enabled": enabled}, request_options)

    def get_iana(self, *, request_options: RequestOptions | None = None) -> Iana:
        """Get the IANA time zone settings. Access: admin."""
        return self._run(OPS.get_iana, None, {}, request_options)

    def set_iana_time_zone(self, *, time_zone: str, request_options: RequestOptions | None = None) -> None:
        """Set the IANA time zone. Clears the POSIX time zone and disables the DHCP time zone.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_iana_time_zone, None, {"time_zone": time_zone}, request_options)

    def get_time_zone_list(self, *, request_options: RequestOptions | None = None) -> TimeZonesArray:
        """List the IANA time zones available on the device. Access: operator."""
        return self._run(OPS.get_time_zone_list, None, {}, request_options)

    def get_posix(self, *, request_options: RequestOptions | None = None) -> Posix:
        """Get the POSIX time zone settings. Access: admin."""
        return self._run(OPS.get_posix, None, {}, request_options)

    def update_posix(
        self,
        *,
        dst_enabled: bool | MISSING = MISSING,
        time_zone: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the POSIX time zone and DST flag. A valid time zone clears the IANA time zone and disables the DHCP time zone.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_posix, None, {"dst_enabled": dst_enabled, "time_zone": time_zone}, request_options)

    def set_posix_dst_enabled(self, *, dst_enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the DST flag of the POSIX time zone. Changes only the fields given. Access: admin."""
        self._run(OPS.set_posix_dst_enabled, None, {"dst_enabled": dst_enabled}, request_options)

    def set_posix_time_zone(self, *, time_zone: str, request_options: RequestOptions | None = None) -> None:
        """Set the POSIX time zone. Clears the IANA time zone and disables the DHCP time zone.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_posix_time_zone, None, {"time_zone": time_zone}, request_options)


class AsyncTimeApi(AsyncApi):
    """Time API (``time-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Time:
        """All time and time zone settings. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_time(self, *, request_options: RequestOptions | None = None) -> TimeSettings:
        """Get the date and time settings. Access: admin."""
        return await self._run(OPS.get_time, None, {}, request_options)

    async def set_date_time(self, *, date_time: str, request_options: RequestOptions | None = None) -> None:
        """Set the system date and time (UTC, ISO 8601).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_date_time, None, {"date_time": date_time}, request_options)

    async def get_active_time_zone(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the currently active time zone (IANA or POSIX format). Access: viewer."""
        return await self._run(OPS.get_active_time_zone, None, {}, request_options)

    async def get_time_zone(self, *, request_options: RequestOptions | None = None) -> TimeZone:
        """Get the time zone settings. Access: admin."""
        return await self._run(OPS.get_time_zone, None, {}, request_options)

    async def get_dhcp(self, *, request_options: RequestOptions | None = None) -> Dhcp:
        """Get the DHCP time zone settings. Access: admin."""
        return await self._run(OPS.get_dhcp, None, {}, request_options)

    async def set_dhcp_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the DHCP time zone. Enabling resets the IANA and POSIX time zones to null.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_dhcp_enabled, None, {"enabled": enabled}, request_options)

    async def get_iana(self, *, request_options: RequestOptions | None = None) -> Iana:
        """Get the IANA time zone settings. Access: admin."""
        return await self._run(OPS.get_iana, None, {}, request_options)

    async def set_iana_time_zone(self, *, time_zone: str, request_options: RequestOptions | None = None) -> None:
        """Set the IANA time zone. Clears the POSIX time zone and disables the DHCP time zone.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_iana_time_zone, None, {"time_zone": time_zone}, request_options)

    async def get_time_zone_list(self, *, request_options: RequestOptions | None = None) -> TimeZonesArray:
        """List the IANA time zones available on the device. Access: operator."""
        return await self._run(OPS.get_time_zone_list, None, {}, request_options)

    async def get_posix(self, *, request_options: RequestOptions | None = None) -> Posix:
        """Get the POSIX time zone settings. Access: admin."""
        return await self._run(OPS.get_posix, None, {}, request_options)

    async def update_posix(
        self,
        *,
        dst_enabled: bool | MISSING = MISSING,
        time_zone: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the POSIX time zone and DST flag. A valid time zone clears the IANA time zone and disables the DHCP time zone.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_posix, None, {"dst_enabled": dst_enabled, "time_zone": time_zone}, request_options)

    async def set_posix_dst_enabled(self, *, dst_enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the DST flag of the POSIX time zone. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_posix_dst_enabled, None, {"dst_enabled": dst_enabled}, request_options)

    async def set_posix_time_zone(self, *, time_zone: str, request_options: RequestOptions | None = None) -> None:
        """Set the POSIX time zone. Clears the IANA time zone and disables the DHCP time zone.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_posix_time_zone, None, {"time_zone": time_zone}, request_options)
