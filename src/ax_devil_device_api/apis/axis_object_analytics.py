# GENERATED from specs/apis/applications/axis-object-analytics.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure object-detection scenarios (motion, fence, crossline counting, occupancy in area) of the AXIS Object Analytics (AOA) ACAP.

Docs: https://developer.axis.com/vapix/applications/axis-object-analytics-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import AcapDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Point = list[float]


class Device(Model):
    id: int
    """The device id that should correspond to the id in data.devices in getConfigurationCapabilities."""
    type: Literal["camera"]
    """The device type (can only be camera)."""
    rotation: Literal[0, 90, 180, 270]
    """The camera rotation, measured in degrees."""
    is_active: bool | None = Field(default=None, validation_alias="isActive", serialization_alias="isActive")
    """True if omitted. Excludes the device from being used if set to false; scenarios, perspectives or metadata overlays referring to it are ignored. Default: True."""


class MetadataOverlay(Model):
    id: int = Field(ge=1)
    """The metadata overlay ID in the range [1... n]. Corresponds to the device ID."""
    draw_on_all_resolutions: bool | None = Field(
        default=None, validation_alias="drawOnAllResolutions", serialization_alias="drawOnAllResolutions"
    )
    """Whether the overlay should be drawn on all available resolutions. Not mandatory if resolutions is specified."""
    resolutions: list[Annotated[str, Field(pattern="^[0-9]+x[0-9]+$")]] | None = None
    """Supported resolutions <width>x<height>. Should be empty or not specified if drawOnAllResolutions is true."""


class PerspectiveBar(Model):
    height: int
    """Virtual height (in centimeters) of an object appearing at the same location and perceived height as the bar."""
    points: list[Point]
    """Start (pos 0, touches the ground plane) and end (pos 1) points in ONVIF coordinates. (minItems=2, maxItems=2)"""


class Perspective(Model):
    id: int
    """A unique ID identifying the perspective."""
    bars: list[PerspectiveBar]
    """Bars contributing to the perspective calculation, limited by getConfigurationCapabilities."""


Direction = Literal["leftToRight", "rightToLeft"]


class Trigger(Model):
    """Scenario trigger; the fields used depend on the type. At least one trigger is needed per scenario. includeArea uses vertices (polygon); fence uses vertices (polyline) and alarmDirection; countingLine uses vertices (polyline) and countingDirection."""

    type: Literal["includeArea", "fence", "countingLine"]
    vertices: list[Point] | None = None
    """Polygon (includeArea) or polyline (fence, countingLine) vertices."""
    alarm_direction: Direction | None = Field(
        default=None, validation_alias="alarmDirection", serialization_alias="alarmDirection"
    )
    """Fence only. Direction in which a crossing object raises the alarm (valid values from getConfigurationCapabilities)."""
    counting_direction: Direction | None = Field(
        default=None, validation_alias="countingDirection", serialization_alias="countingDirection"
    )
    """countingLine only. Direction in which a crossing object is counted."""


class Filter(Model):
    """Scenario filter (optional rules excluding objects); the fields used depend on the type. sizePercentage and sizePerspective use width and height (only one of the two may be used); timeShortLivedLimit uses time; distanceSwayingObject uses distance; speed uses minSpeed and maxSpeed (several allowed, only with a secondary radar device); excludeArea uses vertices (several allowed)."""

    type: Literal[
        "sizePercentage", "sizePerspective", "timeShortLivedLimit", "distanceSwayingObject", "speed", "excludeArea"
    ]
    width: int | None = None
    """Horizontal upper limit; ONVIF coordinates for sizePercentage, centimeters for sizePerspective."""
    height: int | None = None
    """Vertical upper limit; ONVIF coordinates for sizePercentage, centimeters for sizePerspective."""
    time: float | None = None
    """Waiting time in seconds until a detected object raises an alarm (timeShortLivedLimit)."""
    distance: int | None = None
    """Distance an object may travel before raising an alarm, percent of the image (distanceSwayingObject)."""
    min_speed: float | None = Field(default=None, validation_alias="minSpeed", serialization_alias="minSpeed")
    """Ground speed (m/s) from which moving objects won't raise an alarm."""
    max_speed: float | None = Field(default=None, validation_alias="maxSpeed", serialization_alias="maxSpeed")
    """Ground speed (m/s) up to which moving objects won't raise an alarm."""
    vertices: list[Point] | None = None
    """Exclude area polygon (excludeArea)."""


class ObjectClassification(Model):
    type: str
    """Identifies the object type."""
    sub_types: list[ObjectClassification] | None = Field(
        default=None, validation_alias="subTypes", serialization_alias="subTypes"
    )
    """Optional list of sub classifiers (two-level depth currently supported; only if the camera supports subtypes)."""


class ScenarioDevice(Model):
    id: int
    """Device ID defined in the root devices list."""


class AccumulatedCountsConfig(Model):
    """Crossline counting only."""

    timed_reset_enabled: bool | None = Field(
        default=None, validation_alias="timedResetEnabled", serialization_alias="timedResetEnabled"
    )
    """Timed reset (at midnight) of accumulated counts enabled."""


class PassthroughConfig(Model):
    """Crossline counting only."""

    enabled: bool | None = None
    period: int | None = None
    """Trigger an event for every <period> count."""


class Threshold(Model):
    level: int | None = None
    """The number of threshold objects."""
    type: Literal["moreThan", "lessThan"] | None = None
    """Triggers if the number of objects in the area is more or less than the level."""


class ThresholdConfig(Model):
    """Occupancy in area only."""

    enabled: bool | None = None
    trigger_delay: int | None = Field(default=None, validation_alias="triggerDelay", serialization_alias="triggerDelay")
    """Seconds to wait after the threshold is reached before the alarm is triggered."""
    thresholds: list[Threshold] | None = None


class Scenario(Model):
    id: int
    """A unique scenario ID."""
    name: str
    """A user friendly scenario name."""
    type: Literal["motion", "fence", "crosslinecounting", "occupancyInArea"]
    metadata_overlay: int | None = Field(
        default=None, validation_alias="metadataOverlay", serialization_alias="metadataOverlay"
    )
    """Must point to a valid id in the metadataOverlay array; omitting disables the overlay."""
    alarm_rate: str | None = Field(default=None, validation_alias="alarmRate", serialization_alias="alarmRate")
    """Valid rates are listed in getConfigurationCapabilities.data.scenarios.alarmRates."""
    devices: list[ScenarioDevice]
    triggers: list[Trigger]
    """At least one trigger is required."""
    filters: list[Filter] | None = None
    object_classifications: list[ObjectClassification] | None = Field(
        default=None, validation_alias="objectClassifications", serialization_alias="objectClassifications"
    )
    """An empty array means an alarm can be triggered on any detected motion."""
    perspectives: list[int] | None = None
    """Perspective IDs (from data.perspectives); mandatory if a perspective filter is configured."""
    presets: list[int] | None = None
    """PTZ presets tracked: -2 always (except when moving), -1 all presets, 1 home, 2... specific presets. Not valid on non-PTZ devices."""
    accumulated_counts: AccumulatedCountsConfig | None = Field(
        default=None, validation_alias="accumulatedCounts", serialization_alias="accumulatedCounts"
    )
    passthrough_configuration: PassthroughConfig | None = Field(
        default=None, validation_alias="passthroughConfiguration", serialization_alias="passthroughConfiguration"
    )
    threshold_configuration: ThresholdConfig | None = Field(
        default=None, validation_alias="thresholdConfiguration", serialization_alias="thresholdConfiguration"
    )


class Configuration(Model):
    """The complete application configuration, as read by get_configuration and written by set_configuration."""

    devices: list[Device] | None = None
    metadata_overlay: list[MetadataOverlay] | None = Field(
        default=None, validation_alias="metadataOverlay", serialization_alias="metadataOverlay"
    )
    """Size limited by capabilities metadataOverlay.minNbrActiveCameras/maxNbrActiveCameras."""
    perspectives: list[Perspective] | None = None
    scenarios: list[Scenario] | None = None

    @classmethod
    def from_current(cls, configuration: Configuration) -> Configuration:
        """A request that rewrites ``configuration`` unchanged: copy it, edit fields, send it back."""
        data = configuration.request_data()
        return cls(**data)


class TriggerCapability(Model):
    """Limits of one trigger type (includeArea, fence or countingLine)."""

    type: str | None = None
    min_pos_x: float | None = Field(default=None, validation_alias="minPosX", serialization_alias="minPosX")
    max_pos_x: float | None = Field(default=None, validation_alias="maxPosX", serialization_alias="maxPosX")
    min_pos_y: float | None = Field(default=None, validation_alias="minPosY", serialization_alias="minPosY")
    max_pos_y: float | None = Field(default=None, validation_alias="maxPosY", serialization_alias="maxPosY")
    min_nbr_vertices: int | None = Field(
        default=None, validation_alias="minNbrVertices", serialization_alias="minNbrVertices"
    )
    max_nbr_vertices: int | None = Field(
        default=None, validation_alias="maxNbrVertices", serialization_alias="maxNbrVertices"
    )
    min_nbr_instances: int | None = Field(
        default=None, validation_alias="minNbrInstances", serialization_alias="minNbrInstances"
    )
    max_nbr_instances: int | None = Field(
        default=None, validation_alias="maxNbrInstances", serialization_alias="maxNbrInstances"
    )
    default_instance: list[Point] | None = Field(
        default=None, validation_alias="defaultInstance", serialization_alias="defaultInstance"
    )
    valid_alarm_directions: list[str] | None = Field(
        default=None, validation_alias="validAlarmDirections", serialization_alias="validAlarmDirections"
    )
    """Fence (and, per the docs table, counting line) only."""
    default_alarm_direction: str | None = Field(
        default=None, validation_alias="defaultAlarmDirection", serialization_alias="defaultAlarmDirection"
    )
    """Fence (and, per the docs table, counting line) only."""
    valid_counting_directions: list[str] | None = Field(
        default=None, validation_alias="validCountingDirections", serialization_alias="validCountingDirections"
    )
    """Counting line only."""
    default_counting_direction: str | None = Field(
        default=None, validation_alias="defaultCountingDirection", serialization_alias="defaultCountingDirection"
    )
    """Counting line only."""


class FilterCapability(Model):
    """Limits and defaults of one filter type; the fields present depend on the type."""

    type: str | None = None
    min_width: int | None = Field(default=None, validation_alias="minWidth", serialization_alias="minWidth")
    max_width: int | None = Field(default=None, validation_alias="maxWidth", serialization_alias="maxWidth")
    min_height: int | None = Field(default=None, validation_alias="minHeight", serialization_alias="minHeight")
    max_height: int | None = Field(default=None, validation_alias="maxHeight", serialization_alias="maxHeight")
    default_width: int | None = Field(default=None, validation_alias="defaultWidth", serialization_alias="defaultWidth")
    default_height: int | None = Field(
        default=None, validation_alias="defaultHeight", serialization_alias="defaultHeight"
    )
    min_time: int | None = Field(default=None, validation_alias="minTime", serialization_alias="minTime")
    """timeShortLivedLimit (docs table; see open questions)."""
    max_time: int | None = Field(default=None, validation_alias="maxTime", serialization_alias="maxTime")
    default_time: int | None = Field(default=None, validation_alias="defaultTime", serialization_alias="defaultTime")
    min_distance: int | None = Field(default=None, validation_alias="minDistance", serialization_alias="minDistance")
    """distanceSwayingObject (also used by the timeShortLivedLimit example block)."""
    max_distance: int | None = Field(default=None, validation_alias="maxDistance", serialization_alias="maxDistance")
    default_distance: int | None = Field(
        default=None, validation_alias="defaultDistance", serialization_alias="defaultDistance"
    )
    min_speed: float | None = Field(default=None, validation_alias="minSpeed", serialization_alias="minSpeed")
    max_speed: float | None = Field(default=None, validation_alias="maxSpeed", serialization_alias="maxSpeed")
    default_min_speed: float | None = Field(
        default=None, validation_alias="defaultMinSpeed", serialization_alias="defaultMinSpeed"
    )
    default_max_speed: float | None = Field(
        default=None, validation_alias="defaultMaxSpeed", serialization_alias="defaultMaxSpeed"
    )
    min_pos_x: float | None = Field(default=None, validation_alias="minPosX", serialization_alias="minPosX")
    max_pos_x: float | None = Field(default=None, validation_alias="maxPosX", serialization_alias="maxPosX")
    min_pos_y: float | None = Field(default=None, validation_alias="minPosY", serialization_alias="minPosY")
    max_pos_y: float | None = Field(default=None, validation_alias="maxPosY", serialization_alias="maxPosY")
    min_nbr_vertices: int | None = Field(
        default=None, validation_alias="minNbrVertices", serialization_alias="minNbrVertices"
    )
    max_nbr_vertices: int | None = Field(
        default=None, validation_alias="maxNbrVertices", serialization_alias="maxNbrVertices"
    )
    min_nbr_instances: int | None = Field(
        default=None, validation_alias="minNbrInstances", serialization_alias="minNbrInstances"
    )
    max_nbr_instances: int | None = Field(
        default=None, validation_alias="maxNbrInstances", serialization_alias="maxNbrInstances"
    )
    min_nbr_areas: int | None = Field(default=None, validation_alias="minNbrAreas", serialization_alias="minNbrAreas")
    max_nbr_areas: int | None = Field(default=None, validation_alias="maxNbrAreas", serialization_alias="maxNbrAreas")
    default_instance: list[Point] | None = Field(
        default=None, validation_alias="defaultInstance", serialization_alias="defaultInstance"
    )


class DeviceCapability(Model):
    id: int | None = None
    type: str | None = None
    image_index: int | None = Field(default=None, validation_alias="imageIndex", serialization_alias="imageIndex")
    """The image source index."""
    name: str | None = None
    rotation: Literal[0, 90, 180, 270] | None = None
    resolutions: list[str] | None = None
    tags: list[Literal["primary", "secondary", "fisheye"]] | None = None
    """primary is the device to use when a secondary exists; secondary can only be used together with a primary; fisheye has a fisheye lens."""


class MetadataOverlayCamera(Model):
    id: int | None = None
    """Camera value used with media.amp, starting at 1."""
    can_draw_in_specified_resolutions: bool | None = Field(
        default=None,
        validation_alias="canDrawInSpecifiedResolutions",
        serialization_alias="canDrawInSpecifiedResolutions",
    )
    """False means only drawing on all resolutions at once is supported."""
    resolutions: list[str] | None = None


class MetadataOverlayCapabilities(Model):
    min_nbr_active_cameras: int | None = Field(
        default=None, validation_alias="minNbrActiveCameras", serialization_alias="minNbrActiveCameras"
    )
    """If 0 cameras are referenced, the overlay is disabled."""
    max_nbr_active_cameras: int | None = Field(
        default=None, validation_alias="maxNbrActiveCameras", serialization_alias="maxNbrActiveCameras"
    )
    """If 0, the feature is not supported."""
    cameras: list[MetadataOverlayCamera] | None = None


class PerspectiveCapabilities(Model):
    min_nbr_bars: int | None = Field(default=None, validation_alias="minNbrBars", serialization_alias="minNbrBars")
    max_nbr_bars: int | None = Field(default=None, validation_alias="maxNbrBars", serialization_alias="maxNbrBars")
    min_nbr_perspectives_per_scenario: int | None = Field(
        default=None,
        validation_alias="minNbrPerspectivesPerScenario",
        serialization_alias="minNbrPerspectivesPerScenario",
    )
    max_nbr_perspectives_per_scenario: int | None = Field(
        default=None,
        validation_alias="maxNbrPerspectivesPerScenario",
        serialization_alias="maxNbrPerspectivesPerScenario",
    )
    min_height: int | None = Field(default=None, validation_alias="minHeight", serialization_alias="minHeight")
    max_height: int | None = Field(default=None, validation_alias="maxHeight", serialization_alias="maxHeight")
    default_height: int | None = Field(
        default=None, validation_alias="defaultHeight", serialization_alias="defaultHeight"
    )
    min_nbr_perspectives: int | None = Field(
        default=None, validation_alias="minNbrPerspectives", serialization_alias="minNbrPerspectives"
    )
    max_nbr_perspectives: int | None = Field(
        default=None, validation_alias="maxNbrPerspectives", serialization_alias="maxNbrPerspectives"
    )


class AccumulatedCountsCapabilities(Model):
    default_timed_reset_enabled: bool | None = Field(
        default=None, validation_alias="defaultTimedResetEnabled", serialization_alias="defaultTimedResetEnabled"
    )


class PassthroughCapabilities(Model):
    default_enabled: bool | None = Field(
        default=None, validation_alias="defaultEnabled", serialization_alias="defaultEnabled"
    )
    min_period: int | None = Field(default=None, validation_alias="minPeriod", serialization_alias="minPeriod")
    max_period: int | None = Field(default=None, validation_alias="maxPeriod", serialization_alias="maxPeriod")


class ThresholdCapabilities(Model):
    default_enabled: bool | None = Field(
        default=None, validation_alias="defaultEnabled", serialization_alias="defaultEnabled"
    )
    min_level_with_more_than_type: int | None = Field(
        default=None, validation_alias="minLevelWithMoreThanType", serialization_alias="minLevelWithMoreThanType"
    )
    min_level_with_less_than_type: int | None = Field(
        default=None, validation_alias="minLevelWithLessThanType", serialization_alias="minLevelWithLessThanType"
    )
    min_trigger_delay: int | None = Field(
        default=None, validation_alias="minTriggerDelay", serialization_alias="minTriggerDelay"
    )
    max_trigger_delay: int | None = Field(
        default=None, validation_alias="maxTriggerDelay", serialization_alias="maxTriggerDelay"
    )
    default_level: int | None = Field(default=None, validation_alias="defaultLevel", serialization_alias="defaultLevel")
    default_type: str | None = Field(default=None, validation_alias="defaultType", serialization_alias="defaultType")
    default_trigger_delay: int | None = Field(
        default=None, validation_alias="defaultTriggerDelay", serialization_alias="defaultTriggerDelay"
    )
    max_level: int | None = Field(default=None, validation_alias="maxLevel", serialization_alias="maxLevel")


class ScenarioCapabilities(Model):
    min_nbr_scenarios_per_camera: int | None = Field(
        default=None, validation_alias="minNbrScenariosPerCamera", serialization_alias="minNbrScenariosPerCamera"
    )
    max_nbr_scenarios_per_camera: int | None = Field(
        default=None, validation_alias="maxNbrScenariosPerCamera", serialization_alias="maxNbrScenariosPerCamera"
    )
    min_nbr_active_devices: int | None = Field(
        default=None, validation_alias="minNbrActiveDevices", serialization_alias="minNbrActiveDevices"
    )
    max_nbr_active_devices: int | None = Field(
        default=None, validation_alias="maxNbrActiveDevices", serialization_alias="maxNbrActiveDevices"
    )
    min_nbr_devices: int | None = Field(
        default=None, validation_alias="minNbrDevices", serialization_alias="minNbrDevices"
    )
    max_nbr_devices: int | None = Field(
        default=None, validation_alias="maxNbrDevices", serialization_alias="maxNbrDevices"
    )
    min_length_name: int | None = Field(
        default=None, validation_alias="minLengthName", serialization_alias="minLengthName"
    )
    max_length_name: int | None = Field(
        default=None, validation_alias="maxLengthName", serialization_alias="maxLengthName"
    )
    default_scenario: str | None = Field(
        default=None, validation_alias="defaultScenario", serialization_alias="defaultScenario"
    )
    default_device_id: str | None = Field(
        default=None, validation_alias="defaultDeviceId", serialization_alias="defaultDeviceId"
    )
    supported_scenarios: list[str] | None = Field(
        default=None, validation_alias="supportedScenarios", serialization_alias="supportedScenarios"
    )
    alarm_rates: list[str] | None = Field(default=None, validation_alias="alarmRates", serialization_alias="alarmRates")
    default_alarm_rate: str | None = Field(
        default=None, validation_alias="defaultAlarmRate", serialization_alias="defaultAlarmRate"
    )
    accumulated_counts: AccumulatedCountsCapabilities | None = Field(
        default=None, validation_alias="accumulatedCounts", serialization_alias="accumulatedCounts"
    )
    passthrough_configuration: PassthroughCapabilities | None = Field(
        default=None, validation_alias="passthroughConfiguration", serialization_alias="passthroughConfiguration"
    )
    threshold_configuration: ThresholdCapabilities | None = Field(
        default=None, validation_alias="thresholdConfiguration", serialization_alias="thresholdConfiguration"
    )


class PresetCapabilities(Model):
    """Only included if the camera supports PTZ presets."""

    min_nbr_presets_per_scenario: int | None = Field(
        default=None, validation_alias="minNbrPresetsPerScenario", serialization_alias="minNbrPresetsPerScenario"
    )
    max_nbr_presets_per_scenario: int | None = Field(
        default=None, validation_alias="maxNbrPresetsPerScenario", serialization_alias="maxNbrPresetsPerScenario"
    )
    default_preset: int | None = Field(
        default=None, validation_alias="defaultPreset", serialization_alias="defaultPreset"
    )


class ConfigurationCapabilities(Model):
    devices: list[DeviceCapability] | None = None
    filters: list[FilterCapability] | None = None
    metadata_overlay: MetadataOverlayCapabilities | None = Field(
        default=None, validation_alias="metadataOverlay", serialization_alias="metadataOverlay"
    )
    object_classifications: list[ObjectClassification] | None = Field(
        default=None, validation_alias="objectClassifications", serialization_alias="objectClassifications"
    )
    perspective: PerspectiveCapabilities | None = None
    scenarios: ScenarioCapabilities | None = None
    triggers: list[TriggerCapability] | None = None
    presets: PresetCapabilities | None = None


class ScenarioRequest(Model):
    scenario: int
    """The unique scenario ID."""


class Counts(Model):
    """Object counts. Besides the named fields there is one entry per configured category."""

    reset_time: str | None = Field(default=None, validation_alias="resetTime", serialization_alias="resetTime")
    """Time when counting started or was last reset (ISO 8601 YYYY-MM-DDTHH:MM:SSZ). Only in accumulated counts."""
    time_stamp: str | None = Field(default=None, validation_alias="timeStamp", serialization_alias="timeStamp")
    """Time when the count was read (ISO 8601)."""
    total: int
    """Total number of counted objects of any category."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/objectanalytics/control.cgi"

INFO = ApiInfo(
    id="axis-object-analytics",
    name="AXIS Object Analytics API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 2),),
    discovery=(AcapDiscovery("objectanalytics"),),
    docs=("https://developer.axis.com/vapix/applications/axis-object-analytics-api/",),
    errors={
        1000: ErrorCode("An error occurred inside the application.", "internal"),
        2000: ErrorCode("The requested version of the application is not supported.", "unsupported"),
        2002: ErrorCode("Incoherent configuration (such as mismatched ID).", "invalid_argument"),
        2003: ErrorCode("A mandatory parameter is missing.", "invalid_argument"),
        2004: ErrorCode("Invalid parameter.", "invalid_argument"),
        2005: ErrorCode("The requested CGI method is not supported.", "unsupported"),
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
    get_configuration = Operation(
        INFO,
        "get_configuration",
        JsonRpcBinding("getConfiguration", PATH),
        result=Configuration,
        access="operator",
        effect="read",
    )
    set_configuration = Operation(
        INFO,
        "set_configuration",
        JsonRpcBinding("setConfiguration", PATH),
        params=Configuration,
        access="operator",
        effect="write",
        write="replace",
        errors={2002: ErrorCode("Incoherent configuration (such as mismatched ID).", "invalid_argument")},
    )
    send_alarm_event = Operation(
        INFO,
        "send_alarm_event",
        JsonRpcBinding("sendAlarmEvent", PATH),
        params=ScenarioRequest,
        access="operator",
        effect="action",
    )
    get_accumulated_counts = Operation(
        INFO,
        "get_accumulated_counts",
        JsonRpcBinding("getAccumulatedCounts", PATH),
        params=ScenarioRequest,
        result=Counts,
        access="operator",
        effect="read",
    )
    reset_accumulated_counts = Operation(
        INFO,
        "reset_accumulated_counts",
        JsonRpcBinding("resetAccumulatedCounts", PATH),
        params=ScenarioRequest,
        access="operator",
        effect="action",
    )
    reset_passthrough = Operation(
        INFO,
        "reset_passthrough",
        JsonRpcBinding("resetPassthrough", PATH),
        params=ScenarioRequest,
        access="operator",
        effect="action",
    )
    get_occupancy = Operation(
        INFO,
        "get_occupancy",
        JsonRpcBinding("getOccupancy", PATH),
        params=ScenarioRequest,
        result=Counts,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class AxisObjectAnalyticsApi(SyncApi):
    """AXIS Object Analytics API (``axis-object-analytics``, version 1)."""

    INFO = INFO

    def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Retrieve the configuration limits, capabilities and default/reference values of all configurable parameters.

        Access: admin.
        """
        return self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Retrieve the complete current application configuration. Access: operator."""
        return self._run(OPS.get_configuration, None, {}, request_options)

    @overload
    def set_configuration(
        self, request: Configuration, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_configuration(
        self,
        /,
        *,
        devices: list[Device] | MISSING = MISSING,
        metadata_overlay: list[MetadataOverlay] | MISSING = MISSING,
        perspectives: list[Perspective] | MISSING = MISSING,
        scenarios: list[Scenario] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_configuration(
        self, request: Configuration | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Apply a complete application configuration immediately.

        Replaces the whole configuration. Any ongoing event is set inactive when a new configuration is
        applied, stopping ongoing recordings (all channels on multichannel cameras). Exception: if there is
        movement in the include area after the configuration is set and no exclusion filter hinders the
        alarm, the event is set active directly after the new configuration is applied. Values outside the
        camera capabilities result in an error.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        self._run(OPS.set_configuration, request, kwargs, request_options)

    def send_alarm_event(self, scenario: int, *, request_options: RequestOptions | None = None) -> None:
        """Force a scenario to enter its alarm state for a 3 second duration (emits Axis and ONVIF events while high).

        Access: operator.
        """
        self._run(OPS.send_alarm_event, None, {"scenario": scenario}, request_options)

    def get_accumulated_counts(self, scenario: int, *, request_options: RequestOptions | None = None) -> Counts:
        """Retrieve the accumulated counts (per configured class and total) for a Crossline Counting scenario.

        Access: operator.
        """
        return self._run(OPS.get_accumulated_counts, None, {"scenario": scenario}, request_options)

    def reset_accumulated_counts(self, scenario: int, *, request_options: RequestOptions | None = None) -> None:
        """Reset the object counts for a Crossline Counting scenario. Access: operator."""
        self._run(OPS.reset_accumulated_counts, None, {"scenario": scenario}, request_options)

    def reset_passthrough(self, scenario: int, *, request_options: RequestOptions | None = None) -> None:
        """Reset the passthrough counter (event every N counts) for a Crossline Counting scenario.

        Access: operator.
        """
        self._run(OPS.reset_passthrough, None, {"scenario": scenario}, request_options)

    def get_occupancy(self, scenario: int, *, request_options: RequestOptions | None = None) -> Counts:
        """Retrieve the current object counts for an Occupancy in Area scenario. Access: operator."""
        return self._run(OPS.get_occupancy, None, {"scenario": scenario}, request_options)


class AsyncAxisObjectAnalyticsApi(AsyncApi):
    """AXIS Object Analytics API (``axis-object-analytics``, version 1)."""

    INFO = INFO

    async def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Retrieve the configuration limits, capabilities and default/reference values of all configurable parameters.

        Access: admin.
        """
        return await self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    async def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Retrieve the complete current application configuration. Access: operator."""
        return await self._run(OPS.get_configuration, None, {}, request_options)

    @overload
    async def set_configuration(
        self, request: Configuration, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_configuration(
        self,
        /,
        *,
        devices: list[Device] | MISSING = MISSING,
        metadata_overlay: list[MetadataOverlay] | MISSING = MISSING,
        perspectives: list[Perspective] | MISSING = MISSING,
        scenarios: list[Scenario] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_configuration(
        self, request: Configuration | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Apply a complete application configuration immediately.

        Replaces the whole configuration. Any ongoing event is set inactive when a new configuration is
        applied, stopping ongoing recordings (all channels on multichannel cameras). Exception: if there is
        movement in the include area after the configuration is set and no exclusion filter hinders the
        alarm, the event is set active directly after the new configuration is applied. Values outside the
        camera capabilities result in an error.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        await self._run(OPS.set_configuration, request, kwargs, request_options)

    async def send_alarm_event(self, scenario: int, *, request_options: RequestOptions | None = None) -> None:
        """Force a scenario to enter its alarm state for a 3 second duration (emits Axis and ONVIF events while high).

        Access: operator.
        """
        await self._run(OPS.send_alarm_event, None, {"scenario": scenario}, request_options)

    async def get_accumulated_counts(self, scenario: int, *, request_options: RequestOptions | None = None) -> Counts:
        """Retrieve the accumulated counts (per configured class and total) for a Crossline Counting scenario.

        Access: operator.
        """
        return await self._run(OPS.get_accumulated_counts, None, {"scenario": scenario}, request_options)

    async def reset_accumulated_counts(self, scenario: int, *, request_options: RequestOptions | None = None) -> None:
        """Reset the object counts for a Crossline Counting scenario. Access: operator."""
        await self._run(OPS.reset_accumulated_counts, None, {"scenario": scenario}, request_options)

    async def reset_passthrough(self, scenario: int, *, request_options: RequestOptions | None = None) -> None:
        """Reset the passthrough counter (event every N counts) for a Crossline Counting scenario.

        Access: operator.
        """
        await self._run(OPS.reset_passthrough, None, {"scenario": scenario}, request_options)

    async def get_occupancy(self, scenario: int, *, request_options: RequestOptions | None = None) -> Counts:
        """Retrieve the current object counts for an Occupancy in Area scenario. Access: operator."""
        return await self._run(OPS.get_occupancy, None, {"scenario": scenario}, request_options)
