# GENERATED from specs/apis/radar/radar-analytics2.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure radar analytics: detection sensitivity, coexistence, frequency channel, global filters, mounting height and tilt, lanes and radar profile.

Docs: https://developer.axis.com/vapix/radar/radar-configuration/
"""

from __future__ import annotations

from typing import Annotated, Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Point = list[Annotated[float, Field(ge=-1, le=1)]]
FrequencyChannel = int | str


class IntegerChoices(Model):
    """Allowed integer values and the default."""

    values: list[int] | None = None
    """The allowed values."""
    default: int | None = None
    """The default value."""


class CoexistenceCapabilities(Model):
    """Present only if the device supports coexistence."""

    max_neighboring_radars: IntegerChoices | None = Field(
        default=None, validation_alias="maxNeighboringRadars", serialization_alias="maxNeighboringRadars"
    )
    """Allowed values and default of the coexistence mode."""
    group: IntegerChoices | None = None
    """Allowed values and default of the coexistence group."""


class FrequencyChannelCapabilities(Model):
    """Present only if the device supports multiple frequency channels."""

    automatic: bool | None = None
    """Whether automatic frequency channel selection is supported."""
    values: list[FrequencyChannel] | None = None
    """The allowed frequency channels."""
    default: FrequencyChannel | None = None
    """The default frequency channel."""


class MountingHeightCapabilities(Model):
    min_value: float | None = Field(default=None, validation_alias="minValue", serialization_alias="minValue")
    """The smallest allowed mounting height."""
    max_value: float | None = Field(default=None, validation_alias="maxValue", serialization_alias="maxValue")
    """The largest allowed mounting height."""
    default: float | None = None
    """The default mounting height."""


class MountingTiltCapabilities(Model):
    min_value: float | None = Field(default=None, validation_alias="minValue", serialization_alias="minValue")
    """The smallest allowed mounting tilt angle."""
    max_value: float | None = Field(default=None, validation_alias="maxValue", serialization_alias="maxValue")
    """The largest allowed mounting tilt angle."""
    automatic: bool | None = None
    """Whether automatic mounting tilt measurement is supported."""
    default: float | None = None
    """The default mounting tilt angle."""


class DetectionSensitivityCapabilities(Model):
    values: list[str] | None = None
    """The allowed sensitivities, for example low, medium and high."""
    default: str | None = None


class LaneCapabilities(Model):
    """Present only if the device supports lanes."""

    max_name_length: float | None = Field(
        default=None, validation_alias="maxNameLength", serialization_alias="maxNameLength"
    )
    """The maximum length of a lane name."""
    max_nodes: float | None = Field(default=None, validation_alias="maxNodes", serialization_alias="maxNodes")
    """The maximum number of nodes of a lane polygon."""


class ConfigurationCapabilities(Model):
    coexistence: CoexistenceCapabilities | None = None
    frequency_channel: FrequencyChannelCapabilities | None = Field(
        default=None, validation_alias="frequencyChannel", serialization_alias="frequencyChannel"
    )
    mounting_height: MountingHeightCapabilities | None = Field(
        default=None, validation_alias="mountingHeight", serialization_alias="mountingHeight"
    )
    mounting_tilt: MountingTiltCapabilities | None = Field(
        default=None, validation_alias="mountingTilt", serialization_alias="mountingTilt"
    )
    detection_sensitivity: DetectionSensitivityCapabilities | None = Field(
        default=None, validation_alias="detectionSensitivity", serialization_alias="detectionSensitivity"
    )
    lanes: LaneCapabilities | None = None


class ChannelRequest(Model):
    """Selects a radar channel; channel 1 is used when omitted."""

    channel: int | None = None
    """Radar channel. Channel 1 if omitted."""


class DetectionSensitivity(Model):
    value: str
    """The current detection sensitivity."""


class SetDetectionSensitivityRequest(Model):
    value: str
    """The detection sensitivity; allowed values come from ``get_configuration_capabilities``."""
    channel: int | None = None
    """Radar channel to set. If omitted, all radar channels use their default detection sensitivity."""


class SetCoexistenceRequest(Model):
    max_neighboring_radars: int = Field(
        validation_alias="maxNeighboringRadars", serialization_alias="maxNeighboringRadars"
    )
    """The maximum number of neighboring radars."""
    channel: int | None = None
    """Radar channel. All radar channels are set if omitted."""
    group: int | None = None
    """Coexistence group the radar belongs to. Optional if ``maxNeighboringRadars`` is 2 or fewer. Group 1 if omitted."""


class NeighboringRadars(Model):
    value: int | None = None
    """The maximum number of neighboring radars."""


class Coexistence(Model):
    """The current coexistence mode. Only available if the device supports coexistence."""

    max_neighboring_radars: NeighboringRadars | None = Field(
        default=None, validation_alias="maxNeighboringRadars", serialization_alias="maxNeighboringRadars"
    )
    group: NeighboringRadars | None = None
    """The coexistence group; not shown in the documented response."""


class SetFrequencyChannelRequest(Model):
    automatic: bool | None = None
    """Use automatic frequency channel selection. Only allowed if ``frequencyChannel.automatic`` is true in the capabilities; otherwise the device returns an error."""
    value: FrequencyChannel | None = None
    """The frequency channel to use; allowed values come from ``get_configuration_capabilities``."""
    channel: int | None = None
    """Radar channel. All radar channels are set if omitted."""


class CurrentFrequencyChannel(Model):
    automatic: bool | None = None
    """Whether the device selects the frequency channel automatically."""
    value: FrequencyChannel
    """The current frequency channel of the requested radar channel."""


class GlobalFilter(Model):
    type: str
    """Name of the filter; supported names come from ``get_global_filters``."""
    active: bool
    """Whether the filter is enabled."""


class SetGlobalFiltersRequest(Model):
    filters: list[GlobalFilter]
    """The filters to configure and their state."""


class GlobalFilters(Model):
    filters: list[GlobalFilter]
    """The global filters of the device and their state."""


class SetMountingHeightRequest(Model):
    value: float
    """Vertical mounting height in meters; the range comes from ``get_configuration_capabilities``."""
    channel: int | None = None
    """Radar channel. All radar channels are set if omitted."""


class MountingHeight(Model):
    value: float
    """The current mounting height in meters."""


class SetMountingTiltRequest(Model):
    automatic: bool | None = None
    """Use automatic tilt measurement. Only allowed if ``mountingTilt.automatic`` is true in the capabilities; otherwise the device returns an error."""
    value: float | None = None
    """Mounting tilt in degrees; positive values are tilted downwards, 0 is level with the surface. Ignored if ``automatic`` is true."""
    channel: int | None = None
    """Radar channel. All radar channels are set if omitted."""


class MountingTilt(Model):
    automatic: bool | None = None
    """Whether automatic mounting tilt measurement is used."""
    value: float
    """The mounting tilt in degrees. Updated on each request if ``automatic`` is true and the physical tilt changes."""


class RadarDataStatus(Model):
    value: bool
    """True if data is received from the radar sensor; false if not (the sensor may be malfunctioning)."""


class Lane(Model):
    name: str
    """The lane name."""
    enabled: bool
    """Whether the lane is enabled."""
    nodes: list[Point]
    """Polygon that describes the lane outline."""


class Lanes(Model):
    lanes: list[Lane]
    """The lanes. Limits come from ``get_configuration_capabilities`` (lanes)."""


class SetLanesRequest(Model):
    """Arguments of ``set_lanes``. Replaces the stored lanes."""

    lanes: list[Lane]
    """The lanes. Limits come from ``get_configuration_capabilities`` (lanes)."""

    @classmethod
    def from_current(cls, lanes: Lanes) -> SetLanesRequest:
        """A request that rewrites ``lanes`` unchanged: copy it, edit fields, send it back."""
        data = lanes.request_data()
        return cls(**data)


class SetRadarProfileRequest(Model):
    value: str
    """The radar profile; allowed values come from ``get_radar_profile``."""
    channel: int | None = None
    """Radar channel whose profile is set."""


class RadarProfile(Model):
    value: str
    """The profile in use."""
    allowed_values: list[str] | None = Field(
        default=None, validation_alias="allowedValues", serialization_alias="allowedValues"
    )
    """The available profiles."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/radar/radaranalytics.cgi"

INFO = ApiInfo(
    id="radar-analytics2",
    name="Radar configuration - Analytics API",
    family=Family.JSONRPC,
    major=2,
    known_versions=(ApiVersion(2, 2), ApiVersion(2, 4)),
    discovery=(ApiDiscovery("radar-analytics2"),),
    docs=("https://developer.axis.com/vapix/radar/radar-configuration/",),
    errors={
        1000: ErrorCode("Invalid parameter value., kind: invalid_argument"),
        4000: ErrorCode("The provided input was not well-formed JSON., kind: invalid_argument"),
        4001: ErrorCode("A mandatory input parameter was not found in the input., kind: invalid_argument"),
        4002: ErrorCode("The type of value of a provided JSON parameter was incorrect.", "invalid_argument"),
        4004: ErrorCode("The format of a provided JSON parameter was incorrect.", "invalid_argument"),
        7000: ErrorCode("The requested API version is not supported by this implementation.", "unsupported"),
        8000: ErrorCode("Internal error., kind: internal"),
    },
)


class OPS:
    get_configuration_capabilities = Operation(
        INFO,
        "get_configuration_capabilities",
        JsonRpcBinding("getConfigurationCapabilities", PATH),
        result=ConfigurationCapabilities,
        access="admin",
        effect="read",
    )
    set_detection_sensitivity = Operation(
        INFO,
        "set_detection_sensitivity",
        JsonRpcBinding("setDetectionSensitivity", PATH),
        params=SetDetectionSensitivityRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_detection_sensitivity = Operation(
        INFO,
        "get_detection_sensitivity",
        JsonRpcBinding("getDetectionSensitivity", PATH),
        params=ChannelRequest,
        result=DetectionSensitivity,
        access="operator",
        effect="read",
    )
    set_coexistence = Operation(
        INFO,
        "set_coexistence",
        JsonRpcBinding("setCoexistence", PATH),
        params=SetCoexistenceRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_coexistence = Operation(
        INFO,
        "get_coexistence",
        JsonRpcBinding("getCoexistence", PATH),
        params=ChannelRequest,
        result=Coexistence,
        access="operator",
        effect="read",
    )
    set_frequency_channel = Operation(
        INFO,
        "set_frequency_channel",
        JsonRpcBinding("setFrequencyChannel", PATH),
        params=SetFrequencyChannelRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_frequency_channel = Operation(
        INFO,
        "get_frequency_channel",
        JsonRpcBinding("getFrequencyChannel", PATH),
        params=ChannelRequest,
        result=CurrentFrequencyChannel,
        access="operator",
        effect="read",
    )
    set_global_filters = Operation(
        INFO,
        "set_global_filters",
        JsonRpcBinding("setGlobalFilters", PATH),
        params=SetGlobalFiltersRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_global_filters = Operation(
        INFO,
        "get_global_filters",
        JsonRpcBinding("getGlobalFilters", PATH),
        result=GlobalFilters,
        access="admin",
        effect="read",
    )
    set_mounting_height = Operation(
        INFO,
        "set_mounting_height",
        JsonRpcBinding("setMountingHeight", PATH),
        params=SetMountingHeightRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_mounting_height = Operation(
        INFO,
        "get_mounting_height",
        JsonRpcBinding("getMountingHeight", PATH),
        params=ChannelRequest,
        result=MountingHeight,
        access="operator",
        effect="read",
    )
    set_mounting_tilt = Operation(
        INFO,
        "set_mounting_tilt",
        JsonRpcBinding("setMountingTilt", PATH),
        params=SetMountingTiltRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_mounting_tilt = Operation(
        INFO,
        "get_mounting_tilt",
        JsonRpcBinding("getMountingTilt", PATH),
        params=ChannelRequest,
        result=MountingTilt,
        access="operator",
        effect="read",
    )
    get_radar_data_status = Operation(
        INFO,
        "get_radar_data_status",
        JsonRpcBinding("getRadarDataStatus", PATH),
        result=RadarDataStatus,
        access="operator",
        effect="read",
    )
    set_lanes = Operation(
        INFO,
        "set_lanes",
        JsonRpcBinding("setLanes", PATH),
        params=SetLanesRequest,
        access="operator",
        effect="write",
        since=ApiVersion(2, 4),
        write="replace",
    )
    get_lanes = Operation(
        INFO,
        "get_lanes",
        JsonRpcBinding("getLanes", PATH),
        result=Lanes,
        access="operator",
        effect="read",
        since=ApiVersion(2, 4),
    )
    set_radar_profile = Operation(
        INFO,
        "set_radar_profile",
        JsonRpcBinding("setRadarProfile", PATH),
        params=SetRadarProfileRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_radar_profile = Operation(
        INFO,
        "get_radar_profile",
        JsonRpcBinding("getRadarProfile", PATH),
        result=RadarProfile,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RadarAnalyticsApi(SyncApi):
    """Radar configuration - Analytics API (``radar-analytics2``, version 2)."""

    INFO = INFO

    def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Request capabilities information from the Analytics API. Access: admin."""
        return self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    def set_detection_sensitivity(
        self, *, value: str, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Set the detection sensitivity. A higher sensitivity raises the detection probability, and possibly the false alarms.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_detection_sensitivity, None, {"value": value, "channel": channel}, request_options)

    def get_detection_sensitivity(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> DetectionSensitivity:
        """Get the current detection sensitivity. Access: operator."""
        return self._run(OPS.get_detection_sensitivity, None, {"channel": channel}, request_options)

    def set_coexistence(
        self,
        *,
        max_neighboring_radars: int,
        channel: int | MISSING = MISSING,
        group: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the coexistence mode to reduce interference between radars within each others' active area.

        Only available if the capabilities contain a ``coexistence`` key.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_coexistence,
            None,
            {"max_neighboring_radars": max_neighboring_radars, "channel": channel, "group": group},
            request_options,
        )

    def get_coexistence(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Coexistence:
        """Get the current coexistence mode.

        Only available if the capabilities contain a ``coexistence`` key.

        Access: operator.
        """
        return self._run(OPS.get_coexistence, None, {"channel": channel}, request_options)

    def set_frequency_channel(
        self,
        *,
        automatic: bool | MISSING = MISSING,
        value: FrequencyChannel | MISSING = MISSING,
        channel: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the frequency channel to avoid interference between nearby radars.

        Only available if the capabilities contain a ``frequencyChannel`` key.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_frequency_channel,
            None,
            {"automatic": automatic, "value": value, "channel": channel},
            request_options,
        )

    def get_frequency_channel(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> CurrentFrequencyChannel:
        """Get the current frequency channel.

        Only available if the capabilities contain a ``frequencyChannel`` key.

        Access: operator.
        """
        return self._run(OPS.get_frequency_channel, None, {"channel": channel}, request_options)

    @overload
    def set_global_filters(
        self, request: SetGlobalFiltersRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_global_filters(
        self, /, *, filters: list[GlobalFilter], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_global_filters(
        self,
        request: SetGlobalFiltersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Enable or disable global filters, for example the swaying object filter.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        self._run(OPS.set_global_filters, request, kwargs, request_options)

    def get_global_filters(self, *, request_options: RequestOptions | None = None) -> GlobalFilters:
        """Get the current global filter configuration. Access: admin."""
        return self._run(OPS.get_global_filters, None, {}, request_options)

    def set_mounting_height(
        self, *, value: float, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Set the mounting height (affects the analytics algorithm; default 3.5 m).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_mounting_height, None, {"value": value, "channel": channel}, request_options)

    def get_mounting_height(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MountingHeight:
        """Get the current mounting height. Access: operator."""
        return self._run(OPS.get_mounting_height, None, {"channel": channel}, request_options)

    def set_mounting_tilt(
        self,
        *,
        automatic: bool | MISSING = MISSING,
        value: float | MISSING = MISSING,
        channel: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the mounting tilt (degrees, positive = tilted downwards; 0 = level with the surface; default 0).

        Overrides the automatic tilt measurement that some products have.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_mounting_tilt, None, {"automatic": automatic, "value": value, "channel": channel}, request_options
        )

    def get_mounting_tilt(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MountingTilt:
        """Get the current mounting tilt and whether automatic tilt measurement is used.

        Access: operator.
        """
        return self._run(OPS.get_mounting_tilt, None, {"channel": channel}, request_options)

    def get_radar_data_status(self, *, request_options: RequestOptions | None = None) -> RadarDataStatus:
        """Check data reception status from the radar sensor. Access: operator."""
        return self._run(OPS.get_radar_data_status, None, {}, request_options)

    @overload
    def set_lanes(self, request: SetLanesRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_lanes(self, /, *, lanes: list[Lane], request_options: RequestOptions | None = None) -> None: ...
    def set_lanes(
        self, request: SetLanesRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set the lane configuration (name, enabled, nodes) for road monitoring.

        Sends the whole lane array, which replaces the stored lanes.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        self._run(OPS.set_lanes, request, kwargs, request_options)

    def get_lanes(self, *, request_options: RequestOptions | None = None) -> Lanes:
        """Get the current lane setup while the radar is in road mode. Access: operator."""
        return self._run(OPS.get_lanes, None, {}, request_options)

    def set_radar_profile(
        self, *, value: str, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Set the radar profile (for example area or road) of a radar channel.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_radar_profile, None, {"value": value, "channel": channel}, request_options)

    def get_radar_profile(self, *, request_options: RequestOptions | None = None) -> RadarProfile:
        """Get the radar profile in use and the allowed values. Access: operator."""
        return self._run(OPS.get_radar_profile, None, {}, request_options)


class AsyncRadarAnalyticsApi(AsyncApi):
    """Radar configuration - Analytics API (``radar-analytics2``, version 2)."""

    INFO = INFO

    async def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Request capabilities information from the Analytics API. Access: admin."""
        return await self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    async def set_detection_sensitivity(
        self, *, value: str, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Set the detection sensitivity. A higher sensitivity raises the detection probability, and possibly the false alarms.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_detection_sensitivity, None, {"value": value, "channel": channel}, request_options)

    async def get_detection_sensitivity(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> DetectionSensitivity:
        """Get the current detection sensitivity. Access: operator."""
        return await self._run(OPS.get_detection_sensitivity, None, {"channel": channel}, request_options)

    async def set_coexistence(
        self,
        *,
        max_neighboring_radars: int,
        channel: int | MISSING = MISSING,
        group: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the coexistence mode to reduce interference between radars within each others' active area.

        Only available if the capabilities contain a ``coexistence`` key.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_coexistence,
            None,
            {"max_neighboring_radars": max_neighboring_radars, "channel": channel, "group": group},
            request_options,
        )

    async def get_coexistence(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Coexistence:
        """Get the current coexistence mode.

        Only available if the capabilities contain a ``coexistence`` key.

        Access: operator.
        """
        return await self._run(OPS.get_coexistence, None, {"channel": channel}, request_options)

    async def set_frequency_channel(
        self,
        *,
        automatic: bool | MISSING = MISSING,
        value: FrequencyChannel | MISSING = MISSING,
        channel: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the frequency channel to avoid interference between nearby radars.

        Only available if the capabilities contain a ``frequencyChannel`` key.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_frequency_channel,
            None,
            {"automatic": automatic, "value": value, "channel": channel},
            request_options,
        )

    async def get_frequency_channel(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> CurrentFrequencyChannel:
        """Get the current frequency channel.

        Only available if the capabilities contain a ``frequencyChannel`` key.

        Access: operator.
        """
        return await self._run(OPS.get_frequency_channel, None, {"channel": channel}, request_options)

    @overload
    async def set_global_filters(
        self, request: SetGlobalFiltersRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_global_filters(
        self, /, *, filters: list[GlobalFilter], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_global_filters(
        self,
        request: SetGlobalFiltersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Enable or disable global filters, for example the swaying object filter.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        await self._run(OPS.set_global_filters, request, kwargs, request_options)

    async def get_global_filters(self, *, request_options: RequestOptions | None = None) -> GlobalFilters:
        """Get the current global filter configuration. Access: admin."""
        return await self._run(OPS.get_global_filters, None, {}, request_options)

    async def set_mounting_height(
        self, *, value: float, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Set the mounting height (affects the analytics algorithm; default 3.5 m).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_mounting_height, None, {"value": value, "channel": channel}, request_options)

    async def get_mounting_height(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MountingHeight:
        """Get the current mounting height. Access: operator."""
        return await self._run(OPS.get_mounting_height, None, {"channel": channel}, request_options)

    async def set_mounting_tilt(
        self,
        *,
        automatic: bool | MISSING = MISSING,
        value: float | MISSING = MISSING,
        channel: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the mounting tilt (degrees, positive = tilted downwards; 0 = level with the surface; default 0).

        Overrides the automatic tilt measurement that some products have.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_mounting_tilt, None, {"automatic": automatic, "value": value, "channel": channel}, request_options
        )

    async def get_mounting_tilt(
        self, *, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> MountingTilt:
        """Get the current mounting tilt and whether automatic tilt measurement is used.

        Access: operator.
        """
        return await self._run(OPS.get_mounting_tilt, None, {"channel": channel}, request_options)

    async def get_radar_data_status(self, *, request_options: RequestOptions | None = None) -> RadarDataStatus:
        """Check data reception status from the radar sensor. Access: operator."""
        return await self._run(OPS.get_radar_data_status, None, {}, request_options)

    @overload
    async def set_lanes(
        self, request: SetLanesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_lanes(self, /, *, lanes: list[Lane], request_options: RequestOptions | None = None) -> None: ...
    async def set_lanes(
        self, request: SetLanesRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set the lane configuration (name, enabled, nodes) for road monitoring.

        Sends the whole lane array, which replaces the stored lanes.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        await self._run(OPS.set_lanes, request, kwargs, request_options)

    async def get_lanes(self, *, request_options: RequestOptions | None = None) -> Lanes:
        """Get the current lane setup while the radar is in road mode. Access: operator."""
        return await self._run(OPS.get_lanes, None, {}, request_options)

    async def set_radar_profile(
        self, *, value: str, channel: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Set the radar profile (for example area or road) of a radar channel.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_radar_profile, None, {"value": value, "channel": channel}, request_options)

    async def get_radar_profile(self, *, request_options: RequestOptions | None = None) -> RadarProfile:
        """Get the radar profile in use and the allowed values. Access: operator."""
        return await self._run(OPS.get_radar_profile, None, {}, request_options)
