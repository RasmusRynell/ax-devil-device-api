# GENERATED from specs/apis/network-video/daynight.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage day/night switching (shift levels, dwell times, autotune) when the IR-cut filter is Auto, and the night filter (clear glass / IR-pass) when Off.

Docs: https://developer.axis.com/vapix/network-video/daynight-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

NightFilter = Literal["irpass", "clear"]


class Capabilities(Model):
    """Day and night capabilities of one channel."""

    channel: int
    autotune_support: bool = Field(validation_alias="AutotuneSupport", serialization_alias="AutotuneSupport")
    """True if the channel supports autotune."""
    ir_pass_support: bool = Field(validation_alias="IrPassSupport", serialization_alias="IrPassSupport")
    """True if the channel supports the IR-pass filter."""
    night_day_shift_level_support: bool = Field(
        validation_alias="NightDayShiftLevelSupport", serialization_alias="NightDayShiftLevelSupport"
    )
    """True if the channel supports night to day shift levels."""


class Configuration(Model):
    """Day and night configuration of one channel. Fields the channel does not support are absent."""

    channel: int
    day_night_dwell_time: float | None = Field(
        default=None, validation_alias="DayNightDwellTime", serialization_alias="DayNightDwellTime", ge=1, le=600
    )
    """Seconds that pass, once the ``DayNightShiftLevel`` threshold is reached, before the channel switches from day to night mode."""
    day_night_shift_level: int | None = Field(
        default=None, validation_alias="DayNightShiftLevel", serialization_alias="DayNightShiftLevel", ge=0, le=100
    )
    """Day to night switch threshold. A higher value switches when the image is darker. Equivalent to the param.cgi parameter ``root.ImageSource.IX.DayNight.ShiftLevel``."""
    night_day_dwell_time: float | None = Field(
        default=None, validation_alias="NightDayDwellTime", serialization_alias="NightDayDwellTime", ge=1, le=600
    )
    """Seconds that pass, once the ``NightDayShiftLevel`` threshold is reached, before the channel switches from night to day mode."""
    night_day_shift_level: int | None = Field(
        default=None, validation_alias="NightDayShiftLevel", serialization_alias="NightDayShiftLevel"
    )
    """Night to day threshold; only if ``NightDayShiftLevelSupport`` is true. A higher value switches when the image is darker; too high a value may cause day and night oscillation. Cannot be set while ``Autotune`` is true."""
    autotune: bool | None = Field(default=None, validation_alias="Autotune", serialization_alias="Autotune")
    """Only if ``AutotuneSupport`` is true. True lets an algorithm control ``NightDayShiftLevel``; false lets the operator set it."""
    night_filter: NightFilter | None = Field(
        default=None, validation_alias="NightFilter", serialization_alias="NightFilter"
    )
    """Only if ``IrPassSupport`` is true. ``irpass`` uses the IR-pass filter and ``clear`` uses clear glass when the IR-cut filter is Off."""


class SetConfigurationRequest(Model):
    """Arguments of ``set_configuration``. Only the given fields are changed."""

    channel: int
    """The channel that should be used for the operation."""
    day_night_dwell_time: float | None = Field(
        default=None, validation_alias="DayNightDwellTime", serialization_alias="DayNightDwellTime", ge=1, le=600
    )
    """Seconds before switching from day to night mode."""
    day_night_shift_level: int | None = Field(
        default=None, validation_alias="DayNightShiftLevel", serialization_alias="DayNightShiftLevel", ge=0, le=100
    )
    """Day to night switch threshold. A higher value switches when the image is darker."""
    night_day_dwell_time: float | None = Field(
        default=None, validation_alias="NightDayDwellTime", serialization_alias="NightDayDwellTime", ge=1, le=600
    )
    """Seconds before switching from night to day mode."""
    night_day_shift_level: int | None = Field(
        default=None, validation_alias="NightDayShiftLevel", serialization_alias="NightDayShiftLevel"
    )
    """Only if ``NightDayShiftLevelSupport`` is true and ``Autotune`` is false."""
    autotune: bool | None = Field(default=None, validation_alias="Autotune", serialization_alias="Autotune")
    """Only if ``AutotuneSupport`` is true."""
    night_filter: NightFilter | None = Field(
        default=None, validation_alias="NightFilter", serialization_alias="NightFilter"
    )
    """Only if ``IrPassSupport`` is true."""


class ChannelRequest(Model):
    channel: int
    """The channel that should be used for the operation."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/daynight.cgi"

INFO = ApiInfo(
    id="daynight",
    name="DayNight API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 2)),
    discovery=(ApiDiscovery("daynight"),),
    docs=("https://developer.axis.com/vapix/network-video/daynight-api/",),
    errors={
        1100: ErrorCode("Internal error. The details field may list the parameters that could not be set.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Bad request. Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Missing parameter. Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
        2106: ErrorCode("Authentication failed.", "access_denied"),
        2107: ErrorCode("Method not allowed. Transport level error.", "unsupported"),
    },
)


class OPS:
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        params=ChannelRequest,
        result=list[Capabilities],
        access="operator",
        effect="read",
    )
    get_configuration = Operation(
        INFO,
        "get_configuration",
        JsonRpcBinding("getConfiguration", PATH),
        params=ChannelRequest,
        result=list[Configuration],
        access="operator",
        effect="read",
    )
    set_configuration = Operation(
        INFO,
        "set_configuration",
        JsonRpcBinding("setConfiguration", PATH),
        params=SetConfigurationRequest,
        result=list[Configuration],
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class DayNightApi(SyncApi):
    """DayNight API (``daynight``, version 1)."""

    INFO = INFO

    def get_capabilities(self, *, channel: int, request_options: RequestOptions | None = None) -> list[Capabilities]:
        """List all day and night capabilities for a specific channel. Access: operator."""
        return self._run(OPS.get_capabilities, None, {"channel": channel}, request_options)

    def get_configuration(self, *, channel: int, request_options: RequestOptions | None = None) -> list[Configuration]:
        """Request configuration information for a channel. Access: operator."""
        return self._run(OPS.get_configuration, None, {"channel": channel}, request_options)

    @overload
    def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> list[Configuration]: ...
    @overload
    def set_configuration(
        self,
        /,
        *,
        channel: int,
        day_night_dwell_time: float | MISSING = MISSING,
        day_night_shift_level: int | MISSING = MISSING,
        night_day_dwell_time: float | MISSING = MISSING,
        night_day_shift_level: int | MISSING = MISSING,
        autotune: bool | MISSING = MISSING,
        night_filter: NightFilter | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> list[Configuration]: ...
    def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> list[Configuration]:
        """Apply day/night configuration to a channel.

        Returns the resulting configuration of the channel.

        Changes only the fields given. Access: operator.
        """
        return self._run(OPS.set_configuration, request, kwargs, request_options)


class AsyncDayNightApi(AsyncApi):
    """DayNight API (``daynight``, version 1)."""

    INFO = INFO

    async def get_capabilities(
        self, *, channel: int, request_options: RequestOptions | None = None
    ) -> list[Capabilities]:
        """List all day and night capabilities for a specific channel. Access: operator."""
        return await self._run(OPS.get_capabilities, None, {"channel": channel}, request_options)

    async def get_configuration(
        self, *, channel: int, request_options: RequestOptions | None = None
    ) -> list[Configuration]:
        """Request configuration information for a channel. Access: operator."""
        return await self._run(OPS.get_configuration, None, {"channel": channel}, request_options)

    @overload
    async def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> list[Configuration]: ...
    @overload
    async def set_configuration(
        self,
        /,
        *,
        channel: int,
        day_night_dwell_time: float | MISSING = MISSING,
        day_night_shift_level: int | MISSING = MISSING,
        night_day_dwell_time: float | MISSING = MISSING,
        night_day_shift_level: int | MISSING = MISSING,
        autotune: bool | MISSING = MISSING,
        night_filter: NightFilter | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> list[Configuration]: ...
    async def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> list[Configuration]:
        """Apply day/night configuration to a channel.

        Returns the resulting configuration of the channel.

        Changes only the fields given. Access: operator.
        """
        return await self._run(OPS.set_configuration, request, kwargs, request_options)
