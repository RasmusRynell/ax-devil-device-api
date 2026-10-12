# GENERATED from specs/apis/radar/radar-control2.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure radar motion detection event rules: channels and profiles with include areas, cross lines and filters. Also enables or disables the radar and sends test alarms.

Docs: https://developer.axis.com/vapix/radar/radar-configuration/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Point = list[Annotated[float, Field(ge=-1, le=1)]]


class Channel(Model):
    active: bool | None = None
    """Active profiles for the channel are set to true; inactive to false. Default: True."""
    id: int = Field(ge=1)
    """Channel value applied when requesting video with ``media.amp``. Starts at 1. Default: 1."""


class ObjectTypeFilter(Model):
    """Which kinds of objects generate events. For example, setting ``vehicle`` to false lets vehicles enter the alarm area without an event."""

    type: Literal["objectType"]
    active: bool | None = None
    """Whether the filter is active."""
    small: bool | None = None
    """Whether small objects (small animals such as rodents, small dogs and birds) generate events. Default: True."""
    human: bool | None = None
    """Whether humans generate events. Default: True."""
    vehicle: bool | None = None
    """Whether vehicles generate events. Default: True."""
    unknown: bool | None = None
    """Whether unknown objects (everything not covered by the other types) generate events. Default: True."""


class TimeShortLivedLimitFilter(Model):
    """Suppresses alarms for objects that are tracked for less than the set time."""

    type: Literal["timeShortLivedLimit"]
    active: bool | None = None
    """Whether the filter is active."""
    data: int | None = Field(default=None, ge=1)
    """Seconds an object is tracked before an alarm is raised."""


class ExcludeAreaFilter(Model):
    """An area where objects do not generate events."""

    type: Literal["excludeArea"]
    data: list[Point] | None = None
    """The exclude area polygon."""
    track_passing_objects: bool | None = Field(
        default=None, validation_alias="trackPassingObjects", serialization_alias="trackPassingObjects"
    )
    """Enable passing objects tracking."""


class MinimumSpeedLimitFilter(Model):
    """The minimum speed an object must travel at to generate an event."""

    type: Literal["minimumSpeedLimit"]
    active: bool | None = None
    """Whether the filter is active."""
    data: float | None = Field(default=None, ge=0)
    """The minimum speed in meters per second. The maximum comes from ``get_configuration_capabilities``."""


class MaximumSpeedLimitFilter(Model):
    """The maximum speed an object may travel at to generate an event."""

    type: Literal["maximumSpeedLimit"]
    active: bool | None = None
    """Whether the filter is active."""
    data: float | None = Field(default=None, ge=0)
    """The maximum speed in meters per second. The maximum comes from ``get_configuration_capabilities``."""


Filter = (
    ObjectTypeFilter | TimeShortLivedLimitFilter | ExcludeAreaFilter | MinimumSpeedLimitFilter | MaximumSpeedLimitFilter
)
AlarmDirection = Literal["leftToRight", "rightToLeft"]


class IncludeAreaTrigger(Model):
    type: Literal["includeArea"]
    data: list[Point] | None = None
    """The include area polygon."""


class CrossLineTrigger(Model):
    type: Literal["crossLine"]
    alarm_direction: AlarmDirection | None = Field(
        default=None, validation_alias="alarmDirection", serialization_alias="alarmDirection"
    )
    """The direction in which an object must cross the line to generate an event."""
    data: list[Point] | None = None
    """The cross line as a polyline."""


class MultipleLineCrossLineTrigger(Model):
    type: Literal["multipleLineCrossLine"]
    alarm_direction: AlarmDirection | None = Field(
        default=None, validation_alias="alarmDirection", serialization_alias="alarmDirection"
    )
    """The direction in which an object must cross the lines to generate an event."""
    data: list[list[Point]] | None = None
    """An array of lines, each ``[[x0, y0], ..., [xn, yn]]``."""
    crossing_time_limit: float | None = Field(
        default=None, validation_alias="crossingTimeLimit", serialization_alias="crossingTimeLimit"
    )
    """The maximum time in seconds an object may take to cross the two lines before an alarm is raised. 0 disables the time limit. Default: 0."""


Trigger = IncludeAreaTrigger | CrossLineTrigger | MultipleLineCrossLineTrigger


class Profile(Model):
    name: str | None = None
    """Unicode string used in the event's nice name, visible in the action rule list. Defaults to ``Profile <uid>``."""
    channel: int | None = None
    """The ``id`` of the corresponding channel. Default: 1."""
    uid: int
    """A unique profile id. Default: 1."""
    filters: list[Filter] | None = None
    """Exclusion filters."""
    triggers: list[Trigger] | None = None
    """The triggers; at most one."""
    minimum_trigger_duration: float | None = Field(
        default=None, validation_alias="minimumTriggerDuration", serialization_alias="minimumTriggerDuration", ge=0
    )
    """The minimum time in seconds that the profile remains active after it has been triggered."""


class Configuration(Model):
    """The radar event configuration as reported by the device."""

    channels: list[Channel]
    """One entry per VAPIX channel."""
    profiles: list[Profile]
    """The event profiles."""
    configuration_status: int | None = Field(
        default=None, validation_alias="configurationStatus", serialization_alias="configurationStatus"
    )
    """Read-only. 0 for the default configuration, then increased by 1 on every set up to 2147483647, after which it restarts at 1."""


class SetConfigurationRequest(Model):
    """Arguments of ``set_configuration``. A complete event configuration; remove a profile from ``profiles`` to delete it."""

    channels: list[Channel]
    """One entry per VAPIX channel."""
    profiles: list[Profile]
    """The event profiles. Profiles that are left out are removed."""

    @classmethod
    def from_current(cls, configuration: Configuration) -> SetConfigurationRequest:
        """A request that rewrites ``configuration`` unchanged: copy it, edit fields, send it back."""
        data = configuration.request_data(exclude={"configuration_status"})
        return cls(**data)


Bound = float | list[float]


class FilterCapability(Model):
    """Limits and defaults of one filter type. Which fields are present depends on ``type``."""

    type: Literal["excludeArea", "objectType", "timeShortLivedLimit", "minimumSpeedLimit", "maximumSpeedLimit"]
    min: Bound | None = None
    """The minimum allowed value."""
    max: Bound | None = None
    """The maximum allowed value."""
    default: float | list[str] | None = None
    """The default value; for ``objectType``, the object types that generate an alarm."""
    default_active: bool | None = Field(
        default=None, validation_alias="defaultActive", serialization_alias="defaultActive"
    )
    """Whether the filter is active by default."""
    min_nbr_vertices: int | None = Field(
        default=None, validation_alias="minNbrVertices", serialization_alias="minNbrVertices"
    )
    """The minimum number of vertices of the area."""
    max_nbr_vertices: int | None = Field(
        default=None, validation_alias="maxNbrVertices", serialization_alias="maxNbrVertices"
    )
    """The maximum number of vertices of the area."""
    default_instance: list[Point] | None = Field(
        default=None, validation_alias="defaultInstance", serialization_alias="defaultInstance"
    )
    """The default area vertices."""
    default_track_passing_objects: bool | None = Field(
        default=None, validation_alias="defaultTrackPassingObjects", serialization_alias="defaultTrackPassingObjects"
    )
    """The default value of ``trackPassingObjects``."""


class TriggerCapability(Model):
    """Limits and defaults of one trigger type. Which fields are present depends on ``type``."""

    type: Literal["crossLine", "multipleLineCrossLine", "includeArea"]
    min: list[float] | None = None
    """``[x, y]`` minimum allowed values."""
    max: list[float] | None = None
    """``[x, y]`` maximum allowed values."""
    min_nbr_vertices: int | None = Field(
        default=None, validation_alias="minNbrVertices", serialization_alias="minNbrVertices"
    )
    max_nbr_vertices: int | None = Field(
        default=None, validation_alias="maxNbrVertices", serialization_alias="maxNbrVertices"
    )
    min_nbr_lines: int | None = Field(default=None, validation_alias="minNbrLines", serialization_alias="minNbrLines")
    """The minimum number of lines of a multiple line crossing."""
    max_nbr_lines: int | None = Field(default=None, validation_alias="maxNbrLines", serialization_alias="maxNbrLines")
    """The maximum number of lines of a multiple line crossing."""
    min_nbr_instances: int | None = Field(
        default=None, validation_alias="minNbrInstances", serialization_alias="minNbrInstances"
    )
    max_nbr_instances: int | None = Field(
        default=None, validation_alias="maxNbrInstances", serialization_alias="maxNbrInstances"
    )
    valid_alarm_directions: list[str] | None = Field(
        default=None, validation_alias="validAlarmDirections", serialization_alias="validAlarmDirections"
    )
    """The possible alarm directions."""
    default_instance: list[Point | list[Point]] | None = Field(
        default=None, validation_alias="defaultInstance", serialization_alias="defaultInstance"
    )
    """The default vertices: a list of points, or for ``multipleLineCrossLine`` a list of lines."""
    default_alarm_direction: str | None = Field(
        default=None, validation_alias="defaultAlarmDirection", serialization_alias="defaultAlarmDirection"
    )
    default_alarm_directions: str | None = Field(
        default=None, validation_alias="defaultAlarmDirections", serialization_alias="defaultAlarmDirections"
    )
    """The default alarm direction of a multiple line crossing."""
    default_crossing_time_limit: float | None = Field(
        default=None, validation_alias="defaultCrossingTimeLimit", serialization_alias="defaultCrossingTimeLimit"
    )
    min_crossing_time_limit: float | None = Field(
        default=None, validation_alias="minCrossingTimeLimit", serialization_alias="minCrossingTimeLimit"
    )
    max_crossing_time_limit: float | None = Field(
        default=None, validation_alias="maxCrossingTimeLimit", serialization_alias="maxCrossingTimeLimit"
    )


class ProfileCapabilities(Model):
    min_nbr_profiles_per_channel: float | None = Field(
        default=None, validation_alias="minNbrProfilesPerChannel", serialization_alias="minNbrProfilesPerChannel"
    )
    max_nbr_profiles_per_channel: float | None = Field(
        default=None, validation_alias="maxNbrProfilesPerChannel", serialization_alias="maxNbrProfilesPerChannel"
    )
    min_length_name: float | None = Field(
        default=None, validation_alias="minLengthName", serialization_alias="minLengthName"
    )
    """The minimum number of characters of a profile name."""
    max_length_name: float | None = Field(
        default=None, validation_alias="maxLengthName", serialization_alias="maxLengthName"
    )
    """The maximum number of characters of a profile name."""
    min_minimum_trigger_duration: float | None = Field(
        default=None, validation_alias="minMinimumTriggerDuration", serialization_alias="minMinimumTriggerDuration"
    )
    max_minimum_trigger_duration: float | None = Field(
        default=None, validation_alias="maxMinimumTriggerDuration", serialization_alias="maxMinimumTriggerDuration"
    )
    default_minimum_trigger_duration: float | None = Field(
        default=None,
        validation_alias="defaultMinimumTriggerDuration",
        serialization_alias="defaultMinimumTriggerDuration",
    )
    """The default of ``minimumTriggerDuration`` when omitted."""


class RadarProfileCapabilities(Model):
    values: list[str] | None = None
    """The radar profiles, for example area and road."""
    default: str | None = None


class ConfigurationCapabilities(Model):
    filters: list[FilterCapability] | None = None
    triggers: list[TriggerCapability] | None = None
    profiles: ProfileCapabilities | None = None
    radar_profile: RadarProfileCapabilities | None = Field(
        default=None, validation_alias="radarProfile", serialization_alias="radarProfile"
    )


class Enabled(Model):
    enabled: bool
    """Whether the radar is enabled."""


class SetEnabledRequest(Model):
    enabled: bool
    """True to enable the radar, false to disable it."""


class SendAlarmEventRequest(Model):
    profile: int
    """The uid of the profile that should raise an alarm."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/radar/control.cgi"

INFO = ApiInfo(
    id="radar-control2",
    name="Radar configuration - Control API",
    family=Family.JSONRPC,
    major=2,
    known_versions=(ApiVersion(2, 2),),
    discovery=(ApiDiscovery("radar-control2"),),
    docs=("https://developer.axis.com/vapix/radar/radar-configuration/",),
    errors={
        1000: ErrorCode("Internal error., kind: internal"),
        2000: ErrorCode("The requested API version is not supported by this implementation.", "unsupported"),
        2001: ErrorCode("The format of a provided JSON parameter was incorrect.", "invalid_argument"),
        2002: ErrorCode("Conflicting input parameters, e.g. two profiles with the same uid.", "invalid_argument"),
        2003: ErrorCode("A mandatory input parameter was not found in the input., kind: invalid_argument"),
        2004: ErrorCode("An input parameter has an incorrect type., kind: invalid_argument"),
        2005: ErrorCode("An unexpected parameter was passed., kind: invalid_argument"),
        8000: ErrorCode("The requested method is not supported by this implementation.", "unsupported"),
        8003: ErrorCode("The provided input was not well-formed JSON., kind: invalid_argument"),
    },
)


class OPS:
    get_configuration = Operation(
        INFO,
        "get_configuration",
        JsonRpcBinding("getConfiguration", PATH),
        result=Configuration,
        access="admin",
        effect="read",
    )
    set_configuration = Operation(
        INFO,
        "set_configuration",
        JsonRpcBinding("setConfiguration", PATH),
        params=SetConfigurationRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    get_configuration_capabilities = Operation(
        INFO,
        "get_configuration_capabilities",
        JsonRpcBinding("getConfigurationCapabilities", PATH),
        result=ConfigurationCapabilities,
        access="admin",
        effect="read",
    )
    get_enabled = Operation(
        INFO, "get_enabled", JsonRpcBinding("getEnabled", PATH), result=Enabled, access="admin", effect="read"
    )
    set_enabled = Operation(
        INFO,
        "set_enabled",
        JsonRpcBinding("setEnabled", PATH),
        params=SetEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    send_alarm_event = Operation(
        INFO,
        "send_alarm_event",
        JsonRpcBinding("sendAlarmEvent", PATH),
        params=SendAlarmEventRequest,
        access="operator",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class RadarControlApi(SyncApi):
    """Radar configuration - Control API (``radar-control2``, version 2)."""

    INFO = INFO

    def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Get the current radar event configuration. Access: admin."""
        return self._run(OPS.get_configuration, None, {}, request_options)

    @overload
    def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_configuration(
        self, /, *, channels: list[Channel], profiles: list[Profile], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Apply a new, complete event configuration.

        The configuration replaces the stored one; remove a profile from ``profiles`` to delete it. Remove
        an exclude area filter when it is not in use.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_configuration, request, kwargs, request_options)

    def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Get the boundaries and default values of the Control API configuration. Access: admin."""
        return self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    def get_enabled(self, *, request_options: RequestOptions | None = None) -> Enabled:
        """Determine whether the radar is enabled. Access: admin."""
        return self._run(OPS.get_enabled, None, {}, request_options)

    def set_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the radar. Changes only the fields given. Access: admin."""
        self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    def send_alarm_event(self, profile: int, *, request_options: RequestOptions | None = None) -> None:
        """Send a stateful alarm event for a profile uid, to test a configuration.

        The event stays active for a few seconds and the response returns immediately. Profile events are
        sent regardless of their current state.

        Access: operator.
        """
        self._run(OPS.send_alarm_event, None, {"profile": profile}, request_options)


class AsyncRadarControlApi(AsyncApi):
    """Radar configuration - Control API (``radar-control2``, version 2)."""

    INFO = INFO

    async def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Get the current radar event configuration. Access: admin."""
        return await self._run(OPS.get_configuration, None, {}, request_options)

    @overload
    async def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_configuration(
        self, /, *, channels: list[Channel], profiles: list[Profile], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Apply a new, complete event configuration.

        The configuration replaces the stored one; remove a profile from ``profiles`` to delete it. Remove
        an exclude area filter when it is not in use.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_configuration, request, kwargs, request_options)

    async def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Get the boundaries and default values of the Control API configuration. Access: admin."""
        return await self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    async def get_enabled(self, *, request_options: RequestOptions | None = None) -> Enabled:
        """Determine whether the radar is enabled. Access: admin."""
        return await self._run(OPS.get_enabled, None, {}, request_options)

    async def set_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the radar. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    async def send_alarm_event(self, profile: int, *, request_options: RequestOptions | None = None) -> None:
        """Send a stateful alarm event for a profile uid, to test a configuration.

        The event stays active for a few seconds and the response returns immediately. Profile events are
        sent regardless of their current state.

        Access: operator.
        """
        await self._run(OPS.send_alarm_event, None, {"profile": profile}, request_options)
