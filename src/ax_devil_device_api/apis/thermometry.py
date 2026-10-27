# GENERATED from specs/apis/network-video/thermometry.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure temperature monitoring on temperature-calibrated thermal cameras: isotherm levels, detection areas, spot meter, area groups, guard tour and overlays.

Docs: https://developer.axis.com/vapix/network-video/thermometry/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, Applicability, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

TemperatureScale = Literal["celsius", "fahrenheit"]
DetectionType = Literal["above", "below", "increase", "decrease"]
AreaMeasurement = Literal["maximum", "minimum", "average"]
GroupMeasurement = Literal["maximum", "minimum", "average", "inherit"]
AreaOverlay = Literal["none", "always", "if_triggered"]
CoordinateSystem = Literal["coord_neg1_1", "coord_0_1"]
Vertex = list[Annotated[float, Field(ge=-1, le=1)]]


class Capabilities(Model):
    """Thermometric limits and configuration values."""

    current_temperature_scale: TemperatureScale = Field(
        validation_alias="currentTemperatureScale", serialization_alias="currentTemperatureScale"
    )
    """The current temperature scale."""
    min_temperature: int = Field(validation_alias="minTemperature", serialization_alias="minTemperature")
    """Minimum measurable temperature in the current scale."""
    max_temperature: int = Field(validation_alias="maxTemperature", serialization_alias="maxTemperature")
    """Maximum measurable temperature in the current scale."""
    max_number_of_areas: int = Field(validation_alias="maxNumberOfAreas", serialization_alias="maxNumberOfAreas")
    """Maximum number of areas that can be defined (per preset on PTZ cameras)."""
    max_number_of_vertices: int = Field(
        validation_alias="maxNumberOfVertices", serialization_alias="maxNumberOfVertices"
    )
    """Maximum number of vertices of an alarm area."""
    max_delay_time: int = Field(validation_alias="maxDelayTime", serialization_alias="maxDelayTime")
    """Maximum delay time in seconds."""
    default_delay_time: int = Field(validation_alias="defaultDelayTime", serialization_alias="defaultDelayTime")
    """Default delay time in seconds."""
    max_name_length: int = Field(validation_alias="maxNameLength", serialization_alias="maxNameLength")
    """Maximum number of characters of an area name."""
    max_groups: int | None = Field(default=None, validation_alias="maxGroups", serialization_alias="maxGroups")
    """Maximum number of area groups per preset. Added in API 1.2."""
    imagesources: list[int] | None = None
    """Valid image sources that are active as thermal input channels. Added in API 1.3."""
    overlay_channels: list[int] | None = Field(
        default=None, validation_alias="overlayChannels", serialization_alias="overlayChannels"
    )
    """Channels that can have area overlays enabled. Added in API 1.3."""


class IsothermLevels(Model):
    """The isotherm levels of the temperature color scale. Only meaningful with isothermal palettes (names starting with ``Iso-``)."""

    high: int
    """The highest temperature level."""
    middle: int
    """The middle temperature level."""
    low: int
    """The lowest temperature colored by the palette. Temperatures between low and min appear in grayscale."""
    min: int | None = None
    """The lowest temperature that can be shown in the image. Available from API 1.2."""
    render_overlay: bool | None = Field(
        default=None, validation_alias="renderOverlay", serialization_alias="renderOverlay"
    )
    """True if the palette, with the three levels marked, is included in the video stream."""


class Area(Model):
    """A temperature detection area as listed by the device."""

    id: int
    """The area ID."""
    imagesource: int | None = None
    """The image source for the area. Added in API 1.3."""
    enabled: bool
    """True if area monitoring is enabled."""
    name: str
    detection_type: DetectionType = Field(validation_alias="detectionType", serialization_alias="detectionType")
    measurement: AreaMeasurement
    threshold: int
    delay: int
    """Seconds the trigger condition must be true before an alarm."""
    vertices: list[Vertex]
    area_overlay: AreaOverlay | None = Field(
        default=None, validation_alias="areaOverlay", serialization_alias="areaOverlay"
    )
    temperature_overlay: bool | None = Field(
        default=None, validation_alias="temperatureOverlay", serialization_alias="temperatureOverlay"
    )
    """Show the chosen measurement value while the area overlay is visible."""
    preset_nbr: int | None = Field(default=None, validation_alias="presetNbr", serialization_alias="presetNbr")
    """Preset number of the area."""


class AreaList(Model):
    area_list: list[Area] = Field(validation_alias="areaList", serialization_alias="areaList")


class AreaStatus(Model):
    id: int
    """The area ID."""
    avg: int
    """Average temperature of the area."""
    min: int
    """Minimum temperature of the area."""
    max: int
    """Maximum temperature of the area."""
    min_coordinates: list[float] | None = Field(
        default=None, validation_alias="minCoordinates", serialization_alias="minCoordinates"
    )
    """Coordinates of the first pixel found with the minimum temperature."""
    max_coordinates: list[float] | None = Field(
        default=None, validation_alias="maxCoordinates", serialization_alias="maxCoordinates"
    )
    """Coordinates of the first pixel found with the maximum temperature."""
    triggered: bool
    """True if the area alarm has been triggered."""
    imagesource: int | None = None
    """The image source of the area. Added in API 1.3."""


class AreaStatusList(Model):
    area_list: list[AreaStatus] = Field(validation_alias="areaList", serialization_alias="areaList")


class AddedArea(Model):
    id: int
    """The ID of the new area."""


class AddAreaRequest(Model):
    """Arguments of ``add_area``. The docs do not say which fields are required; the fields that define the alarm are required here."""

    imagesource: int | None = None
    """The image source for the area. Area overlays default to the image source they were created on."""
    enabled: bool | None = None
    """Enables area monitoring if true."""
    name: str
    """The area name; must be unique. Maximum length is given by ``get_configuration_capabilities``."""
    detection_type: DetectionType = Field(validation_alias="detectionType", serialization_alias="detectionType")
    measurement: AreaMeasurement
    threshold: int
    """The temperature value that activates the trigger; for increase/decrease the temperature change during the delay time, which must be positive. The allowed range is given by ``get_configuration_capabilities``."""
    delay: int | None = Field(default=None, ge=0)
    """Seconds the trigger condition must be true before an alarm (0 triggers immediately). For increase/decrease, the time during which the temperature must change by the threshold. Maximum and default are given by ``get_configuration_capabilities``."""
    vertices: list[Vertex]
    """Polygon vertices; at least 3, at most ``maxNumberOfVertices``. All vertices must be unique and edges may not cross."""
    area_overlay: AreaOverlay | None = Field(
        default=None, validation_alias="areaOverlay", serialization_alias="areaOverlay"
    )
    temperature_overlay: bool | None = Field(
        default=None, validation_alias="temperatureOverlay", serialization_alias="temperatureOverlay"
    )
    """Show the chosen measurement value while the area overlay is visible."""
    preset_nbr: int | None = Field(default=None, validation_alias="presetNbr", serialization_alias="presetNbr")
    """Preset number of the area. Ignored on non-PTZ cameras; must be an existing preset on PTZ cameras."""


class UpdateAreaRequest(Model):
    """Arguments of ``update_area``. Only the given fields change."""

    id: int
    """The ID of the area to update."""
    imagesource: int | None = None
    """The image source for the area."""
    enabled: bool | None = None
    name: str | None = None
    """The area name; must be unique. Maximum length is given by ``get_configuration_capabilities``."""
    detection_type: DetectionType | None = Field(
        default=None, validation_alias="detectionType", serialization_alias="detectionType"
    )
    measurement: AreaMeasurement | None = None
    threshold: int | None = None
    delay: int | None = Field(default=None, ge=0)
    """Seconds the trigger condition must be true before an alarm."""
    vertices: list[Vertex] | None = None
    area_overlay: AreaOverlay | None = Field(
        default=None, validation_alias="areaOverlay", serialization_alias="areaOverlay"
    )
    temperature_overlay: bool | None = Field(
        default=None, validation_alias="temperatureOverlay", serialization_alias="temperatureOverlay"
    )
    preset_nbr: int | None = Field(default=None, validation_alias="presetNbr", serialization_alias="presetNbr")
    """Preset number of the area. Ignored on non-PTZ cameras; must be an existing preset on PTZ cameras."""


class SpotTemperature(Model):
    spot_temperature: float = Field(validation_alias="spotTemperature", serialization_alias="spotTemperature")
    """The current temperature at the spot."""
    spot_coordinates: list[float] = Field(validation_alias="spotCoordinates", serialization_alias="spotCoordinates")
    """The x and y coordinates of the spot."""
    render_overlay: bool | None = Field(
        default=None, validation_alias="renderOverlay", serialization_alias="renderOverlay"
    )
    """Whether the spot meter overlay is activated."""


class TgtConfiguration(Model):
    """Thermometric guard tour configuration (PTZ cameras)."""

    pause_on_alarm: bool | None = Field(
        default=None, validation_alias="pauseOnAlarm", serialization_alias="pauseOnAlarm"
    )
    """The guard tour pauses on the preset while an event is active."""
    auto_resume: bool | None = Field(default=None, validation_alias="autoResume", serialization_alias="autoResume")
    """Only valid if ``pauseOnAlarm`` is true. The tour resumes automatically when the event becomes inactive; otherwise it must be restarted manually."""


class Group(Model):
    """An area group that monitors temperature deviation across areas."""

    id: int
    """The group ID."""
    enabled: bool
    name: str
    measurement: GroupMeasurement
    threshold: int
    """The allowed temperature difference in the group before an alarm."""
    delay: int
    """Seconds the trigger condition must be true before an alarm."""
    area_ids: list[int] = Field(validation_alias="areaIds", serialization_alias="areaIds")
    group_overlay: bool | None = Field(
        default=None, validation_alias="groupOverlay", serialization_alias="groupOverlay"
    )
    """Whether an area overlay is displayed when the group is triggered."""
    preset_nbr: int | None = Field(default=None, validation_alias="presetNbr", serialization_alias="presetNbr")


class GroupList(Model):
    grouplist: list[Group]


class AddGroupRequest(Model):
    """Arguments of ``add_group``. The docs do not say which fields are required; name, measurement and threshold are required here."""

    enabled: bool | None = None
    """Enables group monitoring if true. The real value is returned in the response (locked to false until the group has at least 2 areas)."""
    name: str
    """The group name; must be unique. Maximum length is given by ``get_configuration_capabilities`` (too long gives 2104, not unique gives 1200)."""
    measurement: GroupMeasurement
    threshold: int = Field(ge=1)
    """The allowed temperature difference in the group before an alarm. A positive value of at least 1."""
    delay: int | None = Field(default=None, ge=0)
    """Seconds the trigger condition must be true before an alarm (0 triggers immediately). Maximum is given by ``get_configuration_capabilities``."""
    area_ids: list[int] | None = Field(default=None, validation_alias="areaIds", serialization_alias="areaIds")
    """IDs of the areas in the group. At least 2 are needed to start analysis; fewer (or none) are allowed but lock ``enabled`` to false."""
    group_overlay: bool | None = Field(
        default=None, validation_alias="groupOverlay", serialization_alias="groupOverlay"
    )
    """Whether to display an area overlay when the group is triggered."""
    preset_nbr: int | None = Field(default=None, validation_alias="presetNbr", serialization_alias="presetNbr")
    """Preset number of the group. Cannot be changed by ``update_group``. Ignored on non-PTZ cameras."""


class AddedGroup(Model):
    id: int
    """The new group ID, starting at 1."""
    enabled: bool
    """The status of the new group; false if its configuration is incomplete."""


class UpdateGroupRequest(Model):
    """Arguments of ``update_group``. Only the given fields change; ``areaIds`` replaces the whole list."""

    id: int
    """The ID of the group to update."""
    enabled: bool | None = None
    """The requested enabled state; the actual state is returned."""
    name: str | None = None
    measurement: GroupMeasurement | None = None
    threshold: int | None = Field(default=None, ge=1)
    delay: int | None = Field(default=None, ge=0)
    area_ids: list[int] | None = Field(default=None, validation_alias="areaIds", serialization_alias="areaIds")
    """Fully replaces the area IDs in the group. May be empty."""
    group_overlay: bool | None = Field(
        default=None, validation_alias="groupOverlay", serialization_alias="groupOverlay"
    )


class UpdatedGroup(Model):
    enabled: bool
    """The actual enabled state after the update. A group may become disabled without being asked to."""


class MemberArea(Model):
    area_id: int | None = Field(default=None, validation_alias="areaId", serialization_alias="areaId")
    area_name: str | None = Field(default=None, validation_alias="areaName", serialization_alias="areaName")


class DeviationArea(Model):
    """The most or least deviating area. The device returns two entries, one with the max* fields and one with the min* fields."""

    max_area_id: int | None = Field(default=None, validation_alias="maxAreaId", serialization_alias="maxAreaId")
    """ID of the most deviating area."""
    max_area_temp: float | None = Field(default=None, validation_alias="maxAreaTemp", serialization_alias="maxAreaTemp")
    """Temperature of the most deviating area."""
    min_area_id: int | None = Field(default=None, validation_alias="minAreaId", serialization_alias="minAreaId")
    """ID of the least deviating area."""
    min_area_temp: float | None = Field(default=None, validation_alias="minAreaTemp", serialization_alias="minAreaTemp")
    """Temperature of the least deviating area."""


class GroupStatusDetails(Model):
    """Current status data of a group. The contents may change in the future and may be empty."""

    name: str | None = None
    current_deviation: float | None = Field(
        default=None, validation_alias="currentDeviation", serialization_alias="currentDeviation"
    )
    """The current maximum deviation within the group."""
    threshold: int | None = None
    """The maximum total deviation to monitor."""
    member_areas: list[MemberArea] | None = Field(
        default=None, validation_alias="memberAreas", serialization_alias="memberAreas"
    )
    max_deviation_areas: list[DeviationArea] | None = Field(
        default=None, validation_alias="maxDeviationAreas", serialization_alias="maxDeviationAreas"
    )


class GroupStatus(Model):
    id: int
    """The group ID."""
    triggered: bool
    """True if the group alarm has been triggered."""
    details: GroupStatusDetails | None = None


class GroupStatusList(Model):
    grouplist: list[GroupStatus]


class OverlayChannelEntry(Model):
    imagesource: int
    """A channel a thermal image can originate from. Product dependent."""
    overlay_channels: list[int] = Field(validation_alias="overlayChannels", serialization_alias="overlayChannels")
    """Channels where overlays, such as area and spot meter overlays, can appear. Different from the image source."""


class OverlayChannelList(Model):
    overlay_list: list[OverlayChannelEntry] = Field(validation_alias="overlayList", serialization_alias="overlayList")


class OverlayChannelRequest(Model):
    imagesource: int
    """The image source whose area overlays are shown."""
    overlay_channel: int = Field(validation_alias="overlayChannel", serialization_alias="overlayChannel")
    """The channel that displays (or, when removing, stops displaying) area overlays."""


class SpotMeterEntry(Model):
    imagesource: int
    """A channel where the spot meter can be enabled."""
    active: bool
    """True if the spot meter is enabled."""


class SpotMeterList(Model):
    spotmeters: list[SpotMeterEntry]


class SetTemperatureScaleRequest(Model):
    unit: TemperatureScale
    """The temperature scale to use."""


class SetIsothermLevelsRequest(Model):
    high: int
    """Range [minTemperature + 3, maxTemperature] from ``get_configuration_capabilities``."""
    middle: int
    """Range [minTemperature + 2, maxTemperature - 1]."""
    low: int
    """Range [minTemperature + 1, maxTemperature - 2]."""
    min: int | None = None
    """Optional, API 1.2 and later. Defaults to the lowest possible temperature. Range [minTemperature, maxTemperature - 3]."""
    render_overlay: bool | None = Field(
        default=None, validation_alias="renderOverlay", serialization_alias="renderOverlay"
    )
    """Include the color palette, with the levels marked, in the video stream."""


class RemoveAreasRequest(Model):
    areas: list[int]
    """IDs of the areas to remove. The maximum per request is given by ``get_configuration_capabilities``."""


class ListAreasRequest(Model):
    preset_nbr: int | None = Field(default=None, validation_alias="presetNbr", serialization_alias="presetNbr")
    """The preset number; 0 returns the areas of all presets."""
    imagesource: int | None = None
    """Only return areas created on this image source. Added in API 1.3."""


class AddSpotTemperatureRequest(Model):
    spot_coordinates: list[float] = Field(validation_alias="spotCoordinates", serialization_alias="spotCoordinates")
    """The [x, y] coordinates of the pixel of interest."""
    coordinate_system: CoordinateSystem = Field(
        validation_alias="coordinateSystem", serialization_alias="coordinateSystem"
    )
    imagesource: int | None = None
    """The image source channel that shows the spot meter. Added in API 1.3."""


class GetSpotTemperatureRequest(Model):
    coordinate_system: CoordinateSystem | None = Field(
        default=None, validation_alias="coordinateSystem", serialization_alias="coordinateSystem"
    )
    """The coordinate system for the returned spot coordinates. It need not match the one used in add_spot_temperature."""
    imagesource: int | None = None
    """The image source channel that shows the spot meter. Added in API 1.3."""


class RemoveSpotTemperatureRequest(Model):
    imagesource: int | None = None
    """The image source channel to remove the spot meter from. Added in API 1.3."""


class RemoveGroupRequest(Model):
    id: int = Field(ge=0)
    """The group ID. 0 removes all groups for all presets. A group that does not exist gives an error."""


class ListGroupsRequest(Model):
    preset_nbr: int | None = Field(default=None, validation_alias="presetNbr", serialization_alias="presetNbr")
    """The preset number. 0 or omitted returns the groups of all presets; a preset that does not exist gives an error."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/thermometry.cgi"

INFO = ApiInfo(
    id="thermometry",
    name="Thermometry",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1), ApiVersion(1, 2), ApiVersion(1, 3)),
    discovery=(ApiDiscovery("thermometry"),),
    docs=("https://developer.axis.com/vapix/network-video/thermometry/",),
    errors={
        1100: ErrorCode("Internal error (also out of memory)", "internal"),
        1101: ErrorCode("Request is denied - not a thermal camera", "unsupported"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON format", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        2105: ErrorCode("Invalid arguments", "invalid_argument"),
        2106: ErrorCode("Invalid request method", "invalid_argument"),
        2107: ErrorCode("Invalid content length", "invalid_argument"),
        2108: ErrorCode("Invalid content type", "invalid_argument"),
        2109: ErrorCode("Authorization failed", "access_denied"),
        2110: ErrorCode("Authentication failed", "access_denied"),
    },
)


class OPS:
    get_configuration_capabilities = Operation(
        INFO,
        "get_configuration_capabilities",
        JsonRpcBinding("getConfigurationCapabilities", PATH),
        result=Capabilities,
        access="operator",
        effect="read",
    )
    set_temperature_scale = Operation(
        INFO,
        "set_temperature_scale",
        JsonRpcBinding("setTemperatureScale", PATH),
        params=SetTemperatureScaleRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_isotherm_levels = Operation(
        INFO,
        "get_isotherm_levels",
        JsonRpcBinding("getIsothermLevels", PATH),
        result=IsothermLevels,
        access="operator",
        effect="read",
    )
    set_isotherm_levels = Operation(
        INFO,
        "set_isotherm_levels",
        JsonRpcBinding("setIsothermLevels", PATH),
        params=SetIsothermLevelsRequest,
        access="operator",
        effect="write",
        write="patch",
        applicability=(Applicability("min", ApiVersion(1, 2)),),
    )
    add_area = Operation(
        INFO,
        "add_area",
        JsonRpcBinding("addArea", PATH),
        params=AddAreaRequest,
        result=AddedArea,
        access="admin",
        effect="write",
        write="create",
        errors={
            1200: ErrorCode(
                "Maximum number of areas in the preset reached, or the preset does not exist", "invalid_argument"
            ),
            2104: ErrorCode("The specified name is already in use", "invalid_argument"),
        },
    )
    update_area = Operation(
        INFO,
        "update_area",
        JsonRpcBinding("updateArea", PATH),
        params=UpdateAreaRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            1200: ErrorCode(
                "Maximum number of areas in the preset reached, or the preset does not exist", "invalid_argument"
            ),
            2104: ErrorCode("The specified name is already in use", "invalid_argument"),
        },
    )
    remove_areas = Operation(
        INFO,
        "remove_areas",
        JsonRpcBinding("removeAreas", PATH),
        params=RemoveAreasRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={1200: ErrorCode("Area [x] could not be found", "not_found")},
    )
    list_areas = Operation(
        INFO,
        "list_areas",
        JsonRpcBinding("listAreas", PATH),
        params=ListAreasRequest,
        result=AreaList,
        access="operator",
        effect="read",
        applicability=(Applicability("imagesource", ApiVersion(1, 3)),),
    )
    get_area_status = Operation(
        INFO,
        "get_area_status",
        JsonRpcBinding("getAreaStatus", PATH),
        result=AreaStatusList,
        access="operator",
        effect="read",
        errors={1200: ErrorCode("Could not get status for areas", "internal")},
    )
    add_spot_temperature = Operation(
        INFO,
        "add_spot_temperature",
        JsonRpcBinding("addSpotTemperature", PATH),
        params=AddSpotTemperatureRequest,
        access="operator",
        effect="write",
        write="replace",
        applicability=(Applicability("imagesource", ApiVersion(1, 3)),),
        errors={2104: ErrorCode("Invalid channel number specified", "invalid_argument")},
    )
    get_spot_temperature = Operation(
        INFO,
        "get_spot_temperature",
        JsonRpcBinding("getSpotTemperature", PATH),
        params=GetSpotTemperatureRequest,
        result=SpotTemperature,
        access="operator",
        effect="read",
        applicability=(Applicability("imagesource", ApiVersion(1, 3)),),
        errors={2104: ErrorCode("Invalid channel number specified", "invalid_argument")},
    )
    remove_spot_temperature = Operation(
        INFO,
        "remove_spot_temperature",
        JsonRpcBinding("removeSpotTemperature", PATH),
        params=RemoveSpotTemperatureRequest,
        access="operator",
        effect="write",
        write="delete",
        applicability=(Applicability("imagesource", ApiVersion(1, 3)),),
        errors={2104: ErrorCode("Invalid channel number specified", "invalid_argument")},
    )
    get_tgt_configuration = Operation(
        INFO,
        "get_tgt_configuration",
        JsonRpcBinding("getTgtConfiguration", PATH),
        result=TgtConfiguration,
        access="admin",
        effect="read",
        since=ApiVersion(1, 1),
        errors={
            1202: ErrorCode(
                "Method not supported: no guard tour settings available since the camera is fixed", "unsupported"
            )
        },
    )
    set_tgt_configuration = Operation(
        INFO,
        "set_tgt_configuration",
        JsonRpcBinding("setTgtConfiguration", PATH),
        params=TgtConfiguration,
        access="admin",
        effect="write",
        since=ApiVersion(1, 1),
        write="patch",
        errors={
            1202: ErrorCode(
                "Method not supported: no guard tour settings available since the camera is fixed", "unsupported"
            )
        },
    )
    add_group = Operation(
        INFO,
        "add_group",
        JsonRpcBinding("addGroup", PATH),
        params=AddGroupRequest,
        result=AddedGroup,
        access="operator",
        effect="write",
        since=ApiVersion(1, 2),
        write="create",
        errors={
            1200: ErrorCode(
                "Group name not unique, maximum number of groups for the preset reached, preset does not exist, or invalid group area configuration (areas disabled, missing, not in the preset, or area limit reached)",
                "invalid_argument",
            )
        },
    )
    update_group = Operation(
        INFO,
        "update_group",
        JsonRpcBinding("updateGroup", PATH),
        params=UpdateGroupRequest,
        result=UpdatedGroup,
        access="admin",
        effect="write",
        since=ApiVersion(1, 2),
        write="patch",
        errors={
            1200: ErrorCode(
                "Group ID invalid, group name not unique, or invalid group area configuration", "invalid_argument"
            )
        },
    )
    remove_group = Operation(
        INFO,
        "remove_group",
        JsonRpcBinding("removeGroup", PATH),
        params=RemoveGroupRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 2),
        write="delete",
        errors={1200: ErrorCode("Group ID is invalid", "not_found")},
    )
    list_groups = Operation(
        INFO,
        "list_groups",
        JsonRpcBinding("listGroups", PATH),
        params=ListGroupsRequest,
        result=GroupList,
        access="operator",
        effect="read",
        since=ApiVersion(1, 2),
        errors={1200: ErrorCode("Preset does not exist", "not_found")},
    )
    get_group_status = Operation(
        INFO,
        "get_group_status",
        JsonRpcBinding("getGroupStatus", PATH),
        result=GroupStatusList,
        access="operator",
        effect="read",
        since=ApiVersion(1, 2),
    )
    add_overlay_channel = Operation(
        INFO,
        "add_overlay_channel",
        JsonRpcBinding("addOverlayChannel", PATH),
        params=OverlayChannelRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 3),
        write="create",
    )
    remove_overlay_channel = Operation(
        INFO,
        "remove_overlay_channel",
        JsonRpcBinding("removeOverlayChannel", PATH),
        params=OverlayChannelRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 3),
        write="delete",
    )
    list_overlay_channels = Operation(
        INFO,
        "list_overlay_channels",
        JsonRpcBinding("listOverlayChannels", PATH),
        result=OverlayChannelList,
        access="admin",
        effect="read",
        since=ApiVersion(1, 3),
    )
    list_spot_meters = Operation(
        INFO,
        "list_spot_meters",
        JsonRpcBinding("listSpotMeters", PATH),
        result=SpotMeterList,
        access="admin",
        effect="read",
        since=ApiVersion(1, 3),
    )


# ---------------------------------------------------------------------------
# API classes


class ThermometryApi(SyncApi):
    """Thermometry (``thermometry``, version 1)."""

    INFO = INFO

    def get_configuration_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Retrieve the thermometric limits and configuration values. Access: operator."""
        return self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    def set_temperature_scale(self, *, unit: TemperatureScale, request_options: RequestOptions | None = None) -> None:
        """Set the temperature scale (Celsius is the default).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_temperature_scale, None, {"unit": unit}, request_options)

    def get_isotherm_levels(self, *, request_options: RequestOptions | None = None) -> IsothermLevels:
        """Retrieve the isotherm levels and whether the palette overlay is rendered.

        Only meaningful with isothermal palettes (names beginning with ``Iso-``), selected with the
        ``Image.I0.Appearance.Palette`` parameter.

        Access: operator.
        """
        return self._run(OPS.get_isotherm_levels, None, {}, request_options)

    @overload
    def set_isotherm_levels(
        self, request: SetIsothermLevelsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_isotherm_levels(
        self,
        /,
        *,
        high: int,
        middle: int,
        low: int,
        min: int | MISSING = MISSING,
        render_overlay: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_isotherm_levels(
        self,
        request: SetIsothermLevelsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the isotherm levels and whether the palette overlay is rendered.

        The levels must be unique and in rising order from low to high.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_isotherm_levels, request, kwargs, request_options)

    @overload
    def add_area(self, request: AddAreaRequest, /, *, request_options: RequestOptions | None = None) -> AddedArea: ...
    @overload
    def add_area(
        self,
        /,
        *,
        imagesource: int | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        name: str,
        detection_type: DetectionType,
        measurement: AreaMeasurement,
        threshold: int,
        delay: int | MISSING = MISSING,
        vertices: list[Vertex],
        area_overlay: AreaOverlay | MISSING = MISSING,
        temperature_overlay: bool | MISSING = MISSING,
        preset_nbr: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedArea: ...
    def add_area(
        self, request: AddAreaRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AddedArea:
        """Add a temperature detection area (a polygon) with alarm conditions. Access: admin."""
        return self._run(OPS.add_area, request, kwargs, request_options)

    @overload
    def update_area(self, request: UpdateAreaRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_area(
        self,
        /,
        *,
        id: int,
        imagesource: int | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        name: str | MISSING = MISSING,
        detection_type: DetectionType | MISSING = MISSING,
        measurement: AreaMeasurement | MISSING = MISSING,
        threshold: int | MISSING = MISSING,
        delay: int | MISSING = MISSING,
        vertices: list[Vertex] | MISSING = MISSING,
        area_overlay: AreaOverlay | MISSING = MISSING,
        temperature_overlay: bool | MISSING = MISSING,
        preset_nbr: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_area(
        self,
        request: UpdateAreaRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update an existing temperature detection area.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_area, request, kwargs, request_options)

    def remove_areas(self, *, areas: list[int], request_options: RequestOptions | None = None) -> None:
        """Remove one or several areas. Access: admin."""
        self._run(OPS.remove_areas, None, {"areas": areas}, request_options)

    def list_areas(
        self,
        *,
        preset_nbr: int | MISSING = MISSING,
        imagesource: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AreaList:
        """List temperature detection areas for a preset (0 lists all presets), optionally for one image source.

        Access: operator.
        """
        return self._run(OPS.list_areas, None, {"preset_nbr": preset_nbr, "imagesource": imagesource}, request_options)

    def get_area_status(self, *, request_options: RequestOptions | None = None) -> AreaStatusList:
        """Current temperature and trigger status of the active areas.

        PTZ cameras return the status of the areas on the current preset, or an empty list when not on a
        preset.

        Access: operator.
        """
        return self._run(OPS.get_area_status, None, {}, request_options)

    def add_spot_temperature(
        self,
        *,
        spot_coordinates: list[float],
        coordinate_system: CoordinateSystem,
        imagesource: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Activate the spot meter at the given coordinates, replacing any existing one.

        When the spot meter is activated on a specific image source, an overlay is enabled on that channel.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        self._run(
            OPS.add_spot_temperature,
            None,
            {"spot_coordinates": spot_coordinates, "coordinate_system": coordinate_system, "imagesource": imagesource},
            request_options,
        )

    def get_spot_temperature(
        self,
        *,
        coordinate_system: CoordinateSystem | MISSING = MISSING,
        imagesource: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SpotTemperature:
        """Get the temperature at the spot set by ``add_spot_temperature``. Access: operator."""
        return self._run(
            OPS.get_spot_temperature,
            None,
            {"coordinate_system": coordinate_system, "imagesource": imagesource},
            request_options,
        )

    def remove_spot_temperature(
        self, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the rendering of the spot meter. Access: operator."""
        self._run(OPS.remove_spot_temperature, None, {"imagesource": imagesource}, request_options)

    def get_tgt_configuration(self, *, request_options: RequestOptions | None = None) -> TgtConfiguration:
        """Retrieve the thermometric guard tour configuration (PTZ cameras). Access: admin."""
        return self._run(OPS.get_tgt_configuration, None, {}, request_options)

    def set_tgt_configuration(
        self,
        *,
        pause_on_alarm: bool | MISSING = MISSING,
        auto_resume: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the thermometric guard tour configuration (PTZ cameras).

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_tgt_configuration,
            None,
            {"pause_on_alarm": pause_on_alarm, "auto_resume": auto_resume},
            request_options,
        )

    @overload
    def add_group(
        self, request: AddGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddedGroup: ...
    @overload
    def add_group(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        name: str,
        measurement: GroupMeasurement,
        threshold: int,
        delay: int | MISSING = MISSING,
        area_ids: list[int] | MISSING = MISSING,
        group_overlay: bool | MISSING = MISSING,
        preset_nbr: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedGroup: ...
    def add_group(
        self, request: AddGroupRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AddedGroup:
        """Add an area group that monitors temperature deviation across areas. Access: operator."""
        return self._run(OPS.add_group, request, kwargs, request_options)

    @overload
    def update_group(
        self, request: UpdateGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> UpdatedGroup: ...
    @overload
    def update_group(
        self,
        /,
        *,
        id: int,
        enabled: bool | MISSING = MISSING,
        name: str | MISSING = MISSING,
        measurement: GroupMeasurement | MISSING = MISSING,
        threshold: int | MISSING = MISSING,
        delay: int | MISSING = MISSING,
        area_ids: list[int] | MISSING = MISSING,
        group_overlay: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UpdatedGroup: ...
    def update_group(
        self,
        request: UpdateGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> UpdatedGroup:
        """Update an existing group (presetNbr cannot be changed).

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.update_group, request, kwargs, request_options)

    def remove_group(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Remove one group, or all groups with ID 0. Access: admin."""
        self._run(OPS.remove_group, None, {"id": id}, request_options)

    def list_groups(
        self, *, preset_nbr: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GroupList:
        """List groups for a preset (0 or omitted lists all presets). Access: operator."""
        return self._run(OPS.list_groups, None, {"preset_nbr": preset_nbr}, request_options)

    def get_group_status(self, *, request_options: RequestOptions | None = None) -> GroupStatusList:
        """Current trigger status of the active groups.

        PTZ cameras return the status of the groups on the current preset, or an empty list when not on a
        preset.

        Access: operator.
        """
        return self._run(OPS.get_group_status, None, {}, request_options)

    def add_overlay_channel(
        self, *, imagesource: int, overlay_channel: int, request_options: RequestOptions | None = None
    ) -> None:
        """Add a channel that displays the area overlays created on an image source. Access: admin."""
        self._run(
            OPS.add_overlay_channel,
            None,
            {"imagesource": imagesource, "overlay_channel": overlay_channel},
            request_options,
        )

    def remove_overlay_channel(
        self, *, imagesource: int, overlay_channel: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an overlay channel so it no longer shows the area overlays of an image source.

        Access: admin.
        """
        self._run(
            OPS.remove_overlay_channel,
            None,
            {"imagesource": imagesource, "overlay_channel": overlay_channel},
            request_options,
        )

    def list_overlay_channels(self, *, request_options: RequestOptions | None = None) -> OverlayChannelList:
        """List the active overlay channels and their image sources. Access: admin."""
        return self._run(OPS.list_overlay_channels, None, {}, request_options)

    def list_spot_meters(self, *, request_options: RequestOptions | None = None) -> SpotMeterList:
        """List the channels that have a spot meter, and whether it is active. Access: admin."""
        return self._run(OPS.list_spot_meters, None, {}, request_options)


class AsyncThermometryApi(AsyncApi):
    """Thermometry (``thermometry``, version 1)."""

    INFO = INFO

    async def get_configuration_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Retrieve the thermometric limits and configuration values. Access: operator."""
        return await self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    async def set_temperature_scale(
        self, *, unit: TemperatureScale, request_options: RequestOptions | None = None
    ) -> None:
        """Set the temperature scale (Celsius is the default).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_temperature_scale, None, {"unit": unit}, request_options)

    async def get_isotherm_levels(self, *, request_options: RequestOptions | None = None) -> IsothermLevels:
        """Retrieve the isotherm levels and whether the palette overlay is rendered.

        Only meaningful with isothermal palettes (names beginning with ``Iso-``), selected with the
        ``Image.I0.Appearance.Palette`` parameter.

        Access: operator.
        """
        return await self._run(OPS.get_isotherm_levels, None, {}, request_options)

    @overload
    async def set_isotherm_levels(
        self, request: SetIsothermLevelsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_isotherm_levels(
        self,
        /,
        *,
        high: int,
        middle: int,
        low: int,
        min: int | MISSING = MISSING,
        render_overlay: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_isotherm_levels(
        self,
        request: SetIsothermLevelsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the isotherm levels and whether the palette overlay is rendered.

        The levels must be unique and in rising order from low to high.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_isotherm_levels, request, kwargs, request_options)

    @overload
    async def add_area(
        self, request: AddAreaRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddedArea: ...
    @overload
    async def add_area(
        self,
        /,
        *,
        imagesource: int | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        name: str,
        detection_type: DetectionType,
        measurement: AreaMeasurement,
        threshold: int,
        delay: int | MISSING = MISSING,
        vertices: list[Vertex],
        area_overlay: AreaOverlay | MISSING = MISSING,
        temperature_overlay: bool | MISSING = MISSING,
        preset_nbr: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedArea: ...
    async def add_area(
        self, request: AddAreaRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AddedArea:
        """Add a temperature detection area (a polygon) with alarm conditions. Access: admin."""
        return await self._run(OPS.add_area, request, kwargs, request_options)

    @overload
    async def update_area(
        self, request: UpdateAreaRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_area(
        self,
        /,
        *,
        id: int,
        imagesource: int | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        name: str | MISSING = MISSING,
        detection_type: DetectionType | MISSING = MISSING,
        measurement: AreaMeasurement | MISSING = MISSING,
        threshold: int | MISSING = MISSING,
        delay: int | MISSING = MISSING,
        vertices: list[Vertex] | MISSING = MISSING,
        area_overlay: AreaOverlay | MISSING = MISSING,
        temperature_overlay: bool | MISSING = MISSING,
        preset_nbr: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_area(
        self,
        request: UpdateAreaRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update an existing temperature detection area.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_area, request, kwargs, request_options)

    async def remove_areas(self, *, areas: list[int], request_options: RequestOptions | None = None) -> None:
        """Remove one or several areas. Access: admin."""
        await self._run(OPS.remove_areas, None, {"areas": areas}, request_options)

    async def list_areas(
        self,
        *,
        preset_nbr: int | MISSING = MISSING,
        imagesource: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AreaList:
        """List temperature detection areas for a preset (0 lists all presets), optionally for one image source.

        Access: operator.
        """
        return await self._run(
            OPS.list_areas, None, {"preset_nbr": preset_nbr, "imagesource": imagesource}, request_options
        )

    async def get_area_status(self, *, request_options: RequestOptions | None = None) -> AreaStatusList:
        """Current temperature and trigger status of the active areas.

        PTZ cameras return the status of the areas on the current preset, or an empty list when not on a
        preset.

        Access: operator.
        """
        return await self._run(OPS.get_area_status, None, {}, request_options)

    async def add_spot_temperature(
        self,
        *,
        spot_coordinates: list[float],
        coordinate_system: CoordinateSystem,
        imagesource: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Activate the spot meter at the given coordinates, replacing any existing one.

        When the spot meter is activated on a specific image source, an overlay is enabled on that channel.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        await self._run(
            OPS.add_spot_temperature,
            None,
            {"spot_coordinates": spot_coordinates, "coordinate_system": coordinate_system, "imagesource": imagesource},
            request_options,
        )

    async def get_spot_temperature(
        self,
        *,
        coordinate_system: CoordinateSystem | MISSING = MISSING,
        imagesource: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SpotTemperature:
        """Get the temperature at the spot set by ``add_spot_temperature``. Access: operator."""
        return await self._run(
            OPS.get_spot_temperature,
            None,
            {"coordinate_system": coordinate_system, "imagesource": imagesource},
            request_options,
        )

    async def remove_spot_temperature(
        self, *, imagesource: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the rendering of the spot meter. Access: operator."""
        await self._run(OPS.remove_spot_temperature, None, {"imagesource": imagesource}, request_options)

    async def get_tgt_configuration(self, *, request_options: RequestOptions | None = None) -> TgtConfiguration:
        """Retrieve the thermometric guard tour configuration (PTZ cameras). Access: admin."""
        return await self._run(OPS.get_tgt_configuration, None, {}, request_options)

    async def set_tgt_configuration(
        self,
        *,
        pause_on_alarm: bool | MISSING = MISSING,
        auto_resume: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the thermometric guard tour configuration (PTZ cameras).

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_tgt_configuration,
            None,
            {"pause_on_alarm": pause_on_alarm, "auto_resume": auto_resume},
            request_options,
        )

    @overload
    async def add_group(
        self, request: AddGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddedGroup: ...
    @overload
    async def add_group(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        name: str,
        measurement: GroupMeasurement,
        threshold: int,
        delay: int | MISSING = MISSING,
        area_ids: list[int] | MISSING = MISSING,
        group_overlay: bool | MISSING = MISSING,
        preset_nbr: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedGroup: ...
    async def add_group(
        self, request: AddGroupRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AddedGroup:
        """Add an area group that monitors temperature deviation across areas. Access: operator."""
        return await self._run(OPS.add_group, request, kwargs, request_options)

    @overload
    async def update_group(
        self, request: UpdateGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> UpdatedGroup: ...
    @overload
    async def update_group(
        self,
        /,
        *,
        id: int,
        enabled: bool | MISSING = MISSING,
        name: str | MISSING = MISSING,
        measurement: GroupMeasurement | MISSING = MISSING,
        threshold: int | MISSING = MISSING,
        delay: int | MISSING = MISSING,
        area_ids: list[int] | MISSING = MISSING,
        group_overlay: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UpdatedGroup: ...
    async def update_group(
        self,
        request: UpdateGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> UpdatedGroup:
        """Update an existing group (presetNbr cannot be changed).

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.update_group, request, kwargs, request_options)

    async def remove_group(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Remove one group, or all groups with ID 0. Access: admin."""
        await self._run(OPS.remove_group, None, {"id": id}, request_options)

    async def list_groups(
        self, *, preset_nbr: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GroupList:
        """List groups for a preset (0 or omitted lists all presets). Access: operator."""
        return await self._run(OPS.list_groups, None, {"preset_nbr": preset_nbr}, request_options)

    async def get_group_status(self, *, request_options: RequestOptions | None = None) -> GroupStatusList:
        """Current trigger status of the active groups.

        PTZ cameras return the status of the groups on the current preset, or an empty list when not on a
        preset.

        Access: operator.
        """
        return await self._run(OPS.get_group_status, None, {}, request_options)

    async def add_overlay_channel(
        self, *, imagesource: int, overlay_channel: int, request_options: RequestOptions | None = None
    ) -> None:
        """Add a channel that displays the area overlays created on an image source. Access: admin."""
        await self._run(
            OPS.add_overlay_channel,
            None,
            {"imagesource": imagesource, "overlay_channel": overlay_channel},
            request_options,
        )

    async def remove_overlay_channel(
        self, *, imagesource: int, overlay_channel: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an overlay channel so it no longer shows the area overlays of an image source.

        Access: admin.
        """
        await self._run(
            OPS.remove_overlay_channel,
            None,
            {"imagesource": imagesource, "overlay_channel": overlay_channel},
            request_options,
        )

    async def list_overlay_channels(self, *, request_options: RequestOptions | None = None) -> OverlayChannelList:
        """List the active overlay channels and their image sources. Access: admin."""
        return await self._run(OPS.list_overlay_channels, None, {}, request_options)

    async def list_spot_meters(self, *, request_options: RequestOptions | None = None) -> SpotMeterList:
        """List the channels that have a spot meter, and whether it is active. Access: admin."""
        return await self._run(OPS.list_spot_meters, None, {}, request_options)
