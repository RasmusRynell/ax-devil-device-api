# GENERATED from specs/apis/network-video/time-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Get and set date, time and time zone (IANA or POSIX) via /axis-cgi/time.cgi.

Docs: https://developer.axis.com/vapix/network-video/time-api/
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import CONST, ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class DateTimeInfo(Model):
    """System date, time and time zone information."""

    date_time: str = Field(validation_alias="dateTime", serialization_alias="dateTime")
    """System date and time in UTC, ISO 8601. (format=date-time)"""
    local_date_time: str = Field(validation_alias="localDateTime", serialization_alias="localDateTime")
    """Local date and time, ISO 8601. (format=date-time)"""
    max_year_supported: int = Field(validation_alias="maxYearSupported", serialization_alias="maxYearSupported")
    """The latest year that the date can be set to."""
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone")
    """System time zone in IANA format, e.g. Europe/Stockholm. Omitted if not available."""
    posix_time_zone: str | None = Field(
        default=None, validation_alias="posixTimeZone", serialization_alias="posixTimeZone"
    )
    """System time zone in POSIX format, e.g. EST5EDT,M3.2.0,M11.1.0. Omitted if not available."""
    dst_enabled: bool | None = Field(default=None, validation_alias="dstEnabled", serialization_alias="dstEnabled")
    """DST flag controlling the POSIX string. Always true if the IANA format is present. Omitted if POSIX time zone isn't available."""
    dhcp_time_zone: str | None = Field(
        default=None, validation_alias="dhcpTimeZone", serialization_alias="dhcpTimeZone"
    )
    """DHCP time zone (IANA or POSIX). Omitted if not available. Introduced in API version 1.1."""
    dhcp_time_zone_utilized: bool | None = Field(
        default=None, validation_alias="dhcpTimeZoneUtilized", serialization_alias="dhcpTimeZoneUtilized"
    )
    """Whether the DHCP time zone is used by the system. Omitted if DHCP time zone isn't available. Introduced in API version 1.1."""


class AllDateTimeInfo(Model):
    """The date and time information plus the available IANA time zones."""

    date_time: str = Field(validation_alias="dateTime", serialization_alias="dateTime")
    """System date and time in UTC, ISO 8601. (format=date-time)"""
    local_date_time: str = Field(validation_alias="localDateTime", serialization_alias="localDateTime")
    """Local date and time, ISO 8601. (format=date-time)"""
    max_year_supported: int = Field(validation_alias="maxYearSupported", serialization_alias="maxYearSupported")
    """The latest year that the date can be set to."""
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone")
    """System time zone in IANA format, e.g. Europe/Stockholm. Omitted if not available."""
    posix_time_zone: str | None = Field(
        default=None, validation_alias="posixTimeZone", serialization_alias="posixTimeZone"
    )
    """System time zone in POSIX format, e.g. EST5EDT,M3.2.0,M11.1.0. Omitted if not available."""
    dst_enabled: bool | None = Field(default=None, validation_alias="dstEnabled", serialization_alias="dstEnabled")
    """DST flag controlling the POSIX string. Always true if the IANA format is present. Omitted if POSIX time zone isn't available."""
    dhcp_time_zone: str | None = Field(
        default=None, validation_alias="dhcpTimeZone", serialization_alias="dhcpTimeZone"
    )
    """DHCP time zone (IANA or POSIX). Omitted if not available. Introduced in API version 1.1."""
    dhcp_time_zone_utilized: bool | None = Field(
        default=None, validation_alias="dhcpTimeZoneUtilized", serialization_alias="dhcpTimeZoneUtilized"
    )
    """Whether the DHCP time zone is used by the system. Omitted if DHCP time zone isn't available. Introduced in API version 1.1."""
    time_zones: list[str] | None = Field(default=None, validation_alias="timeZones", serialization_alias="timeZones")
    """Supported time zones in the IANA format."""


class SetDateTimeRequest(Model):
    date_time: str = Field(
        validation_alias="dateTime", serialization_alias="dateTime", pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    )
    """Date and time in UTC formatted as [YYYY]-[MM]-[DD]T[hh]:[mm]:[ss]Z (e.g. 2018-12-24T20:30:45Z)."""


class SetDateTimeResult(Model):
    date_time: str = Field(validation_alias="dateTime", serialization_alias="dateTime")
    """Echoes the date and time that was set."""


class SetTimeZoneRequest(Model):
    time_zone: str = Field(validation_alias="timeZone", serialization_alias="timeZone")
    """Which IANA time zone that should be set (see getAll timeZones)."""


class SetTimeZoneResult(Model):
    time_zone: str = Field(validation_alias="timeZone", serialization_alias="timeZone")
    """Echoes the time zone that was set."""


class SetPosixTimeZoneRequest(Model):
    posix_time_zone: str = Field(validation_alias="posixTimeZone", serialization_alias="posixTimeZone")
    """POSIX time zone, e.g. EST5EDT,M3.2.0,M11.1.0."""
    enable_dst: bool = Field(validation_alias="enableDst", serialization_alias="enableDst")
    """true activates the DST settings of the POSIX time zone string; false ignores them."""


class SetPosixTimeZoneResult(Model):
    posix_time_zone: str = Field(validation_alias="posixTimeZone", serialization_alias="posixTimeZone")
    dst_enabled: bool = Field(validation_alias="dstEnabled", serialization_alias="dstEnabled")


class ResetTimeZoneResult(Model):
    status: Annotated[Literal["success"], CONST]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/time.cgi"

INFO = ApiInfo(
    id="time-service",
    name="Time API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1)),
    discovery=(ApiDiscovery("time-service"),),
    docs=("https://developer.axis.com/vapix/network-video/time-api/",),
    errors={
        1000: ErrorCode("Internal error. Refer to message field or logs.", "internal"),
        2000: ErrorCode("Invalid request. Only HTTP request type POST is supported.", "invalid_argument"),
        2001: ErrorCode("Request body too large.", "invalid_argument"),
        3000: ErrorCode("Invalid JSON data.", "invalid_argument"),
        4000: ErrorCode("Method does not exist.", "not_found"),
        4001: ErrorCode("The specified version is not supported.", "unsupported"),
        4002: ErrorCode("Authorization failed.", "access_denied"),
        4003: ErrorCode("Missing parameter(s).", "invalid_argument"),
        4004: ErrorCode("Invalid parameter(s).", "invalid_argument"),
    },
)


class OPS:
    get_date_time_info = Operation(
        INFO,
        "get_date_time_info",
        JsonRpcBinding("getDateTimeInfo", PATH),
        result=DateTimeInfo,
        access="viewer",
        effect="read",
    )
    get_all = Operation(
        INFO, "get_all", JsonRpcBinding("getAll", PATH), result=AllDateTimeInfo, access="viewer", effect="read"
    )
    set_date_time = Operation(
        INFO,
        "set_date_time",
        JsonRpcBinding("setDateTime", PATH),
        params=SetDateTimeRequest,
        result=SetDateTimeResult,
        access="operator",
        effect="write",
        write="patch",
    )
    set_time_zone = Operation(
        INFO,
        "set_time_zone",
        JsonRpcBinding("setTimeZone", PATH),
        params=SetTimeZoneRequest,
        result=SetTimeZoneResult,
        access="operator",
        effect="write",
        write="patch",
    )
    set_posix_time_zone = Operation(
        INFO,
        "set_posix_time_zone",
        JsonRpcBinding("setPosixTimeZone", PATH),
        params=SetPosixTimeZoneRequest,
        result=SetPosixTimeZoneResult,
        access="operator",
        effect="write",
        write="patch",
    )
    reset_time_zone = Operation(
        INFO,
        "reset_time_zone",
        JsonRpcBinding("resetTimeZone", PATH),
        result=ResetTimeZoneResult,
        access="operator",
        effect="action",
        since=ApiVersion(1, 1),
    )


# ---------------------------------------------------------------------------
# API classes


class TimeServiceApi(SyncApi):
    """Time API (``time-service``, version 1)."""

    INFO = INFO

    def get_date_time_info(self, *, request_options: RequestOptions | None = None) -> DateTimeInfo:
        """Get system date, time, time zone and local time. Access: viewer."""
        return self._run(OPS.get_date_time_info, None, {}, request_options)

    def get_all(self, *, request_options: RequestOptions | None = None) -> AllDateTimeInfo:
        """Get all properties of get_date_time_info plus a list of available IANA time zones.

        Access: viewer.
        """
        return self._run(OPS.get_all, None, {}, request_options)

    def set_date_time(self, *, date_time: str, request_options: RequestOptions | None = None) -> SetDateTimeResult:
        """Set system date and time in UTC. Changes only the fields given. Access: operator."""
        return self._run(OPS.set_date_time, None, {"date_time": date_time}, request_options)

    def set_time_zone(self, *, time_zone: str, request_options: RequestOptions | None = None) -> SetTimeZoneResult:
        """Set system time zone in IANA format (preferred).

        Changes only the fields given. Access: operator.
        """
        return self._run(OPS.set_time_zone, None, {"time_zone": time_zone}, request_options)

    def set_posix_time_zone(
        self, *, posix_time_zone: str, enable_dst: bool, request_options: RequestOptions | None = None
    ) -> SetPosixTimeZoneResult:
        """Set system time zone in POSIX format and the DST flag (not recommended).

        Changes only the fields given. Access: operator.
        """
        return self._run(
            OPS.set_posix_time_zone,
            None,
            {"posix_time_zone": posix_time_zone, "enable_dst": enable_dst},
            request_options,
        )

    def reset_time_zone(self, *, request_options: RequestOptions | None = None) -> ResetTimeZoneResult:
        """Reset time zones back to the device default; DHCP time zone will be used when available.

        Access: operator.
        """
        return self._run(OPS.reset_time_zone, None, {}, request_options)


class AsyncTimeServiceApi(AsyncApi):
    """Time API (``time-service``, version 1)."""

    INFO = INFO

    async def get_date_time_info(self, *, request_options: RequestOptions | None = None) -> DateTimeInfo:
        """Get system date, time, time zone and local time. Access: viewer."""
        return await self._run(OPS.get_date_time_info, None, {}, request_options)

    async def get_all(self, *, request_options: RequestOptions | None = None) -> AllDateTimeInfo:
        """Get all properties of get_date_time_info plus a list of available IANA time zones.

        Access: viewer.
        """
        return await self._run(OPS.get_all, None, {}, request_options)

    async def set_date_time(
        self, *, date_time: str, request_options: RequestOptions | None = None
    ) -> SetDateTimeResult:
        """Set system date and time in UTC. Changes only the fields given. Access: operator."""
        return await self._run(OPS.set_date_time, None, {"date_time": date_time}, request_options)

    async def set_time_zone(
        self, *, time_zone: str, request_options: RequestOptions | None = None
    ) -> SetTimeZoneResult:
        """Set system time zone in IANA format (preferred).

        Changes only the fields given. Access: operator.
        """
        return await self._run(OPS.set_time_zone, None, {"time_zone": time_zone}, request_options)

    async def set_posix_time_zone(
        self, *, posix_time_zone: str, enable_dst: bool, request_options: RequestOptions | None = None
    ) -> SetPosixTimeZoneResult:
        """Set system time zone in POSIX format and the DST flag (not recommended).

        Changes only the fields given. Access: operator.
        """
        return await self._run(
            OPS.set_posix_time_zone,
            None,
            {"posix_time_zone": posix_time_zone, "enable_dst": enable_dst},
            request_options,
        )

    async def reset_time_zone(self, *, request_options: RequestOptions | None = None) -> ResetTimeZoneResult:
        """Reset time zones back to the device default; DHCP time zone will be used when available.

        Access: operator.
        """
        return await self._run(OPS.reset_time_zone, None, {}, request_options)
