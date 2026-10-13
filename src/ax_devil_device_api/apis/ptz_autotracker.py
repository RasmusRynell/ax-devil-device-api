# GENERATED from specs/apis/network-video/autotracking-2.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Track moving objects with an Axis PTZ camera: application/tracker settings, viewport rotation, manual target, automatic zone triggers, profiles (zones)...

Docs: https://developer.axis.com/vapix/network-video/ptz-autotracker-api/
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


class MinObjectSize(Model):
    width: float | None = None
    """Min width in percent of the screen."""
    height: float | None = None
    """Min height in percent of the screen."""
    enabled: bool | None = None
    """Whether the filter is enabled."""


class MinObjectLifespan(Model):
    time: float | None = None
    """Minimum lifespan in seconds."""
    enabled: bool | None = None
    """Whether the filter is enabled."""


class TrackingParams(Model):
    timeout_to_home: float | None = Field(
        default=None, validation_alias="timeoutToHome", serialization_alias="timeoutToHome"
    )
    """Seconds the tracker waits after losing an object before returning to preset (global; profiles may override)."""
    zoom_limit_high: float | None = Field(
        default=None, validation_alias="zoomLimitHigh", serialization_alias="zoomLimitHigh"
    )
    """Maximum zoom magnification (>= 1.0)."""
    zoom_limit_low: float | None = Field(
        default=None, validation_alias="zoomLimitLow", serialization_alias="zoomLimitLow"
    )
    """Minimum zoom magnification (>= 1.0)."""
    max_profile_number: int | None = Field(
        default=None, validation_alias="maxProfileNumber", serialization_alias="maxProfileNumber"
    )
    """Maximum number of profiles you can create."""
    tracker_type: int | None = Field(default=None, validation_alias="trackerType", serialization_alias="trackerType")
    """Data source: 0 MOTE, 5 VOD++, 6 Radar."""
    return_to_preset: int | None = Field(
        default=None, validation_alias="returnToPreset", serialization_alias="returnToPreset"
    )
    """Preset to return to after click-to-track; -1 = home preset."""
    max_tracking_time: int | None = Field(
        default=None, validation_alias="maxTrackingTime", serialization_alias="maxTrackingTime"
    )
    """Max seconds an object is tracked before returning; 0 = indefinitely."""


class TrackerInfo(Model):
    tracker_id: int | None = Field(default=None, validation_alias="trackerId", serialization_alias="trackerId")
    """Tracker id."""
    tracker_name: str | None = Field(default=None, validation_alias="trackerName", serialization_alias="trackerName")
    """e.g. MOTE, VOD2, RadarFusion."""


class TrackerSupport(Model):
    supported: list[TrackerInfo] | None = None
    """Read-only list of supported trackers."""
    active_tracker_id: int | None = Field(
        default=None, validation_alias="activeTrackerId", serialization_alias="activeTrackerId"
    )
    """Currently active trackerId."""


class Profile(Model):
    id: int
    """Profile ID."""
    name: str
    """Profile name."""
    preset: int
    """Connected preset number; -1 if none."""
    enabled: bool
    """Profile/zone enabled."""
    zone_type: int | None = Field(default=None, validation_alias="zoneType", serialization_alias="zoneType")
    """Zone type."""
    timeout_to_home: int | None = Field(
        default=None, validation_alias="timeoutToHome", serialization_alias="timeoutToHome"
    )
    """Local timeout override in seconds; -1 = use global."""
    aoa_id: str | None = Field(default=None, validation_alias="aoaId", serialization_alias="aoaId")
    """ID of an AOA scenario used for triggering (either aoaId or px_polygon)."""
    px_polygon: list[float] | None = None
    """Flat [x0,y0,x1,y1,...] polygon in the current viewport; 3-10 points."""


class ProfileSummary(Model):
    id: int | None = None
    """ID of the profile."""
    name: str | None = None
    """Name of the profile."""
    preset: int | None = None
    """Connected preset number; -1 if none."""


TrackingRequirement = Literal["requireRadarTrigger", "requireRadarTrack", "requireAny"]
VideoObjectClassification = Literal["human", "bus", "car", "truck", "motorcycle_bicycle", "vehicle_other"]


class RadarProfile(Model):
    id: int
    """Profile ID."""
    radar_scenario_uuid: str = Field(validation_alias="radarScenarioUuid", serialization_alias="radarScenarioUuid")
    """Unique ID of the radar scenario (Radar Configuration CGI)."""
    name: str
    """Profile name."""
    enabled: bool
    """Profile enabled."""
    priority: int
    """Profile priority (capabilities: 1-20)."""
    video_object_classifications: list[VideoObjectClassification] = Field(
        validation_alias="videoObjectClassifications", serialization_alias="videoObjectClassifications"
    )
    tracking_requirement: TrackingRequirement = Field(
        validation_alias="trackingRequirement", serialization_alias="trackingRequirement"
    )
    vod_confirmation_time: float | None = Field(
        default=None, validation_alias="vodConfirmationTime", serialization_alias="vodConfirmationTime"
    )
    """Seconds allowed for VOD confirmation of a radar track before blocking (5-15, default 5)."""


class RadarProfileSettings(Model):
    id: int | None = None
    """Profile ID."""
    radar_scenario_uuid: str | None = Field(
        default=None, validation_alias="radarScenarioUuid", serialization_alias="radarScenarioUuid"
    )
    """Unique ID of the radar scenario (Radar Configuration CGI)."""
    name: str | None = None
    """Profile name."""
    enabled: bool | None = None
    """Profile enabled."""
    priority: int | None = None
    """Profile priority (capabilities: 1-20)."""
    video_object_classifications: list[VideoObjectClassification] | None = Field(
        default=None, validation_alias="videoObjectClassifications", serialization_alias="videoObjectClassifications"
    )
    tracking_requirement: TrackingRequirement | None = Field(
        default=None, validation_alias="trackingRequirement", serialization_alias="trackingRequirement"
    )
    vod_confirmation_time: float | None = Field(
        default=None, validation_alias="vodConfirmationTime", serialization_alias="vodConfirmationTime"
    )
    """Seconds allowed for VOD confirmation of a radar track before blocking (5-15, default 5)."""


class RadarPtzAlignment(Model):
    radar_pan_offset: float | None = Field(
        default=None, validation_alias="radarPanOffset", serialization_alias="radarPanOffset"
    )
    """Pan offset in degrees aligning radar and PTZ."""


class NumberRange(Model):
    min: float | None = None
    max: float | None = None


class IntegerRange(Model):
    min: int | None = None
    max: int | None = None


class ObjectPriority(Model):
    used_priority: Literal["first", "last", "periodic", "closest", "furthest", "slowest", "fastest"] | None = Field(
        default=None, validation_alias="usedPriority", serialization_alias="usedPriority"
    )
    """Object priority when multiple objects."""
    periodic_time_seconds: float | None = Field(
        default=None, validation_alias="periodicTimeSeconds", serialization_alias="periodicTimeSeconds", ge=0.1
    )
    """Period for "periodic" (min 0.1)."""


class ServiceState(Model):
    active: bool
    """Whether the autotracking service is active."""
    version: str | None = None
    """Optional service version."""


class ApiSupport(Model):
    aoa: bool | None = None
    """Optional. AOA API supported."""
    radar: bool | None = None
    """Optional. Radar API supported."""


class GetApplicationSettingsResult(Model):
    service: ServiceState
    api_support: ApiSupport | None = Field(
        default=None, validation_alias="apiSupport", serialization_alias="apiSupport"
    )


class ServiceUpdate(Model):
    """Container for active state."""

    active: bool | None = None
    """Whether the application subscribes to data sources and stays active."""


class SetApplicationSettingsRequest(Model):
    service: ServiceUpdate
    """Container for active state."""


class GetAutotrackingSettingsResult(Model):
    min_object_size: MinObjectSize = Field(validation_alias="minObjectSize", serialization_alias="minObjectSize")
    min_object_lifespan: MinObjectLifespan = Field(
        validation_alias="minObjectLifespan", serialization_alias="minObjectLifespan"
    )
    tracker_support: TrackerSupport | None = Field(
        default=None, validation_alias="trackerSupport", serialization_alias="trackerSupport"
    )
    tracking_params: TrackingParams | None = Field(
        default=None, validation_alias="trackingParams", serialization_alias="trackingParams"
    )
    profiles: list[Profile]


class ActiveTrackerUpdate(Model):
    """Optional. Change activeTrackerId (supported list is read-only)."""

    active_tracker_id: int | None = Field(
        default=None, validation_alias="activeTrackerId", serialization_alias="activeTrackerId"
    )


class SetAutotrackingSettingsRequest(Model):
    min_object_size: MinObjectSize | None = Field(
        default=None, validation_alias="minObjectSize", serialization_alias="minObjectSize"
    )
    """Optional. Min object size filter."""
    min_object_lifespan: MinObjectLifespan | None = Field(
        default=None, validation_alias="minObjectLifespan", serialization_alias="minObjectLifespan"
    )
    """Optional. Min lifespan filter."""
    tracker_support: ActiveTrackerUpdate | None = Field(
        default=None, validation_alias="trackerSupport", serialization_alias="trackerSupport"
    )
    """Optional. Change activeTrackerId (supported list is read-only)."""
    tracking_params: TrackingParams | None = Field(
        default=None, validation_alias="trackingParams", serialization_alias="trackingParams"
    )
    """Optional. Tracker-related settings."""


class GetViewportConfigResult(Model):
    rotation: int
    """-1 if not initialized; 0 or 180 otherwise."""


class SetViewportConfigRequest(Model):
    rotation: Literal[0, 180]
    """Camera rotation; only 0 and 180 supported."""
    metadata: bool | None = None
    """Whether metadata should be enabled (default true). Default: True."""


class GetAutotrackingTargetResult(Model):
    target_id: int = Field(validation_alias="targetId", serialization_alias="targetId")
    """Tracked object ID; -1 when not tracking."""


class SetAutotrackingTargetRequest(Model):
    target_id: int = Field(validation_alias="targetId", serialization_alias="targetId")
    """Object ID to follow; -1 to stop tracking."""


class GetAutotrackingStateResult(Model):
    enabled: bool
    """Automatic triggering in zones enabled."""


class SetAutotrackingStateRequest(Model):
    enabled: bool
    """Whether tracking (automatic triggering) is enabled."""


class AddProfileRequest(Model):
    name: str | None = None
    """Name of the profile."""
    preset: int
    """Connected preset number; -1 if none."""
    enabled: bool | None = None
    """Profile/zone enabled (default true). Default: True."""
    timeout_to_home: int | None = Field(
        default=None, validation_alias="timeoutToHome", serialization_alias="timeoutToHome"
    )
    """Local timeout in seconds overriding global timeoutToHome; -1 = global (default -1). Default: -1."""
    aoa_id: str | None = Field(default=None, validation_alias="aoaId", serialization_alias="aoaId")
    """Conditional: either aoaId or px_polygon is required. AOA scenario ID."""
    px_polygon: list[float] | None = None
    """Conditional: either aoaId or px_polygon. Flat [x0,y0,...] floats; max ten points."""


class AddProfileResult(Model):
    id: int
    """ID of the new profile."""
    name: str | None = None
    """Optional profile name."""


class GetProfileRequest(Model):
    id: int
    """ID of the requested profile."""


class UpdateProfileRequest(Model):
    id: int
    """ID of the profile."""
    name: str | None = None
    """Name of the profile."""
    preset: int | None = None
    """Connected preset number; -1 if none."""
    enabled: bool | None = None
    """Profile/zone enabled."""
    timeout_to_home: int | None = Field(
        default=None, validation_alias="timeoutToHome", serialization_alias="timeoutToHome"
    )
    """Local timeout in seconds overriding global timeoutToHome; -1 = global."""
    aoa_id: str | None = Field(default=None, validation_alias="aoaId", serialization_alias="aoaId")
    """Conditional: either aoaId or px_polygon is required. AOA scenario ID."""
    px_polygon: list[float] | None = None
    """Conditional: either aoaId or px_polygon. Flat [x0,y0,...] floats; max ten points."""


class DeleteProfileRequest(Model):
    id: int
    """ID of profile to delete."""


class SetTempZoneRequest(Model):
    zone_type: str | None = Field(default=None, validation_alias="zoneType", serialization_alias="zoneType")
    """Zone type (default "fullscreen"). Default: 'fullscreen'."""
    timeout: int | None = Field(default=None, ge=5, le=120)
    """Zone lifetime 5..120 s (default 30). (unit=s) Default: 30."""


class GetRadarAutotrackingSettingsResult(Model):
    radar_ptz_alignment: RadarPtzAlignment | None = Field(
        default=None, validation_alias="radarPTZAlignment", serialization_alias="radarPTZAlignment"
    )
    radar_profiles: list[RadarProfile] | None = Field(
        default=None, validation_alias="radarProfiles", serialization_alias="radarProfiles"
    )
    object_priority: ObjectPriority | None = Field(
        default=None, validation_alias="objectPriority", serialization_alias="objectPriority"
    )


class SetRadarAutotrackingSettingsRequest(Model):
    radar_ptz_alignment: RadarPtzAlignment | None = Field(
        default=None, validation_alias="radarPTZAlignment", serialization_alias="radarPTZAlignment"
    )
    """Optional. Degrees to align radar and PTZ."""
    radar_profiles: list[RadarProfileSettings] | None = Field(
        default=None, validation_alias="radarProfiles", serialization_alias="radarProfiles"
    )
    """Optional. Radar profile options."""
    object_priority: ObjectPriority | None = Field(
        default=None, validation_alias="objectPriority", serialization_alias="objectPriority"
    )
    """Optional. Object priority for multiple objects."""


class RadarPtzAlignmentCapabilities(Model):
    radar_pan_offset: NumberRange | None = Field(
        default=None, validation_alias="radarPanOffset", serialization_alias="radarPanOffset"
    )


class MinimumNumber(Model):
    min: float | None = None


class ObjectPriorityCapabilities(Model):
    object_priorities: list[str] | None = Field(
        default=None, validation_alias="objectPriorities", serialization_alias="objectPriorities"
    )
    periodic_time_seconds: MinimumNumber | None = Field(
        default=None, validation_alias="periodicTimeSeconds", serialization_alias="periodicTimeSeconds"
    )


class NumberRangeWithDefault(Model):
    min: float | None = None
    default: float | None = None
    max: float | None = None


class RadarProfileCapabilities(Model):
    priority: IntegerRange | None = None
    video_object_classifications: list[str] | None = Field(
        default=None, validation_alias="videoObjectClassifications", serialization_alias="videoObjectClassifications"
    )
    tracking_requirements: list[str] | None = Field(
        default=None, validation_alias="trackingRequirements", serialization_alias="trackingRequirements"
    )
    vod_confirmation_time: NumberRangeWithDefault | None = Field(
        default=None, validation_alias="vodConfirmationTime", serialization_alias="vodConfirmationTime"
    )


class GetRadarAutotrackingCapabilitiesResult(Model):
    radar_ptz_alignment: RadarPtzAlignmentCapabilities | None = Field(
        default=None, validation_alias="radarPTZAlignment", serialization_alias="radarPTZAlignment"
    )
    object_priority: ObjectPriorityCapabilities | None = Field(
        default=None, validation_alias="objectPriority", serialization_alias="objectPriority"
    )
    radar_profiles: RadarProfileCapabilities | None = Field(
        default=None, validation_alias="radarProfiles", serialization_alias="radarProfiles"
    )


class AddRadarProfileRequest(Model):
    radar_scenario_uuid: str = Field(validation_alias="radarScenarioUuid", serialization_alias="radarScenarioUuid")
    """unique ID of the radar scenario."""
    name: str
    """profile name."""
    enabled: bool
    """whether the profile is enabled."""
    priority: int
    """profile priority."""
    video_object_classifications: list[VideoObjectClassification] = Field(
        validation_alias="videoObjectClassifications", serialization_alias="videoObjectClassifications"
    )
    """object types to track."""
    tracking_requirement: TrackingRequirement = Field(
        validation_alias="trackingRequirement", serialization_alias="trackingRequirement"
    )
    vod_confirmation_time: float | None = Field(
        default=None, validation_alias="vodConfirmationTime", serialization_alias="vodConfirmationTime"
    )
    """seconds allowed for VOD confirmation of a radar track."""


class GetRadarProfileRequest(Model):
    id: int
    """ID of the requested profile."""


class UpdateRadarProfileRequest(Model):
    id: int
    """ID of the profile to update."""
    radar_scenario_uuid: str | None = Field(
        default=None, validation_alias="radarScenarioUuid", serialization_alias="radarScenarioUuid"
    )
    """New unique ID of the radar scenario."""
    name: str | None = None
    """New profile name."""
    enabled: bool | None = None
    """New whether the profile is enabled."""
    priority: int | None = None
    """New profile priority."""
    video_object_classifications: list[VideoObjectClassification] | None = Field(
        default=None, validation_alias="videoObjectClassifications", serialization_alias="videoObjectClassifications"
    )
    """New object types to track."""
    tracking_requirement: TrackingRequirement | None = Field(
        default=None, validation_alias="trackingRequirement", serialization_alias="trackingRequirement"
    )
    vod_confirmation_time: float | None = Field(
        default=None, validation_alias="vodConfirmationTime", serialization_alias="vodConfirmationTime"
    )
    """New seconds allowed for VOD confirmation of a radar track."""


class DeleteRadarProfileRequest(Model):
    id: int
    """ID of the profile to delete."""


class SendTestAutotrackingEventRequest(Model):
    event_type: Literal[0, 1] = Field(validation_alias="eventType", serialization_alias="eventType")
    """0: global autotracking state event; 1: autotracking profile event."""
    profile_id: int | None = Field(default=None, validation_alias="profileId", serialization_alias="profileId")
    """Active profile ID; required if eventType > 0."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/ptz-autotracking/operator.cgi"

INFO = ApiInfo(
    id="autotracking-2",
    name="PTZ Autotracker API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("autotracking-2"),),
    docs=("https://developer.axis.com/vapix/network-video/ptz-autotracker-api/",),
    errors={
        1001: ErrorCode("The provided JSON input was invalid.", "invalid_argument"),
        1002: ErrorCode("No Method name tag found in request.", "invalid_argument"),
        1003: ErrorCode("Method not supported.", "unsupported"),
        1004: ErrorCode('Parameter tag ("params") required, but missing.', "invalid_argument"),
        1005: ErrorCode("Required parameter missing.", "invalid_argument"),
        1006: ErrorCode("Invalid value of parameter.", "invalid_argument"),
        1007: ErrorCode("Internal error.", "internal"),
    },
)


class OPS:
    get_application_settings = Operation(
        INFO,
        "get_application_settings",
        JsonRpcBinding("getApplicationSettings", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        result=GetApplicationSettingsResult,
        access="viewer",
        effect="read",
    )
    set_application_settings = Operation(
        INFO,
        "set_application_settings",
        JsonRpcBinding("setApplicationSettings", PATH),
        params=SetApplicationSettingsRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_autotracking_settings = Operation(
        INFO,
        "get_autotracking_settings",
        JsonRpcBinding("getAutotrackingSettings", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        result=GetAutotrackingSettingsResult,
        access="viewer",
        effect="read",
    )
    set_autotracking_settings = Operation(
        INFO,
        "set_autotracking_settings",
        JsonRpcBinding("setAutotrackingSettings", PATH),
        params=SetAutotrackingSettingsRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1101: ErrorCode("Invalid profile ID", "invalid_argument"),
            1102: ErrorCode("Max number of profiles reached", "unavailable"),
            1103: ErrorCode("Invalid number of coordinates in zone (not equal x/y for example)", "invalid_argument"),
            1104: ErrorCode("Too many coordinates in zone", "invalid_argument"),
            1105: ErrorCode("Too few coordinates in zone", "invalid_argument"),
            1106: ErrorCode("Profile name empty", "invalid_argument"),
            1107: ErrorCode("Invalid preset", "invalid_argument"),
            1108: ErrorCode("Could not update zone"),
            1109: ErrorCode("No zone included", "invalid_argument"),
            1110: ErrorCode("Tracker not active", "unavailable"),
            1201: ErrorCode("Invalid color ID", "invalid_argument"),
            1202: ErrorCode("No colors configured", "unavailable"),
            1301: ErrorCode("Invalid min object size width", "invalid_argument"),
            1302: ErrorCode("Invalid min object size height", "invalid_argument"),
            1401: ErrorCode("Invalid lifespan time", "invalid_argument"),
            1801: ErrorCode("Invalid value for timeout to home", "invalid_argument"),
            1802: ErrorCode("Invalid value for zoom limit", "invalid_argument"),
            1803: ErrorCode("Invalid value for max profile number", "invalid_argument"),
        },
    )
    get_viewport_config = Operation(
        INFO,
        "get_viewport_config",
        JsonRpcBinding("getViewportConfig", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        result=GetViewportConfigResult,
        access="viewer",
        effect="read",
    )
    set_viewport_config = Operation(
        INFO,
        "set_viewport_config",
        JsonRpcBinding("setViewportConfig", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        params=SetViewportConfigRequest,
        access="viewer",
        effect="write",
        write="patch",
        errors={1101: ErrorCode("Unsupported rotation value", "invalid_argument")},
    )
    get_autotracking_target = Operation(
        INFO,
        "get_autotracking_target",
        JsonRpcBinding("getAutotrackingTarget", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        result=GetAutotrackingTargetResult,
        access="viewer",
        effect="read",
    )
    set_autotracking_target = Operation(
        INFO,
        "set_autotracking_target",
        JsonRpcBinding("setAutotrackingTarget", PATH),
        params=SetAutotrackingTargetRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={1101: ErrorCode("Invalid object ID", "invalid_argument")},
    )
    get_autotracking_state = Operation(
        INFO,
        "get_autotracking_state",
        JsonRpcBinding("getAutotrackingState", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        result=GetAutotrackingStateResult,
        access="viewer",
        effect="read",
    )
    set_autotracking_state = Operation(
        INFO,
        "set_autotracking_state",
        JsonRpcBinding("setAutotrackingState", PATH),
        params=SetAutotrackingStateRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    add_profile = Operation(
        INFO,
        "add_profile",
        JsonRpcBinding("addProfile", PATH),
        params=AddProfileRequest,
        result=AddProfileResult,
        access="operator",
        effect="write",
        write="create",
        errors={
            1102: ErrorCode("Max number of profiles reached", "unavailable"),
            1103: ErrorCode("Invalid number of coordinates in zone (not equal x/y for example)", "invalid_argument"),
            1104: ErrorCode("Too many coordinates in zone", "invalid_argument"),
            1105: ErrorCode("Too few coordinates in zone", "invalid_argument"),
        },
    )
    get_profile = Operation(
        INFO,
        "get_profile",
        JsonRpcBinding("getProfile", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        params=GetProfileRequest,
        result=Profile,
        access="viewer",
        effect="read",
    )
    update_profile = Operation(
        INFO,
        "update_profile",
        JsonRpcBinding("updateProfile", PATH),
        params=UpdateProfileRequest,
        result=ProfileSummary,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1101: ErrorCode("Invalid profile ID", "invalid_argument"),
            1103: ErrorCode("Invalid number of coordinates in zone (not equal x/y for example)", "invalid_argument"),
            1104: ErrorCode("Too many coordinates in zone", "invalid_argument"),
            1105: ErrorCode("Too few coordinates in zone", "invalid_argument"),
            1109: ErrorCode("No zone included", "invalid_argument"),
        },
    )
    delete_profile = Operation(
        INFO,
        "delete_profile",
        JsonRpcBinding("deleteProfile", PATH),
        params=DeleteProfileRequest,
        access="operator",
        effect="write",
        write="delete",
        errors={1101: ErrorCode("Invalid profile ID", "invalid_argument")},
    )
    set_temp_zone = Operation(
        INFO,
        "set_temp_zone",
        JsonRpcBinding("setTempZone", PATH),
        params=SetTempZoneRequest,
        access="operator",
        effect="action",
    )
    get_radar_autotracking_settings = Operation(
        INFO,
        "get_radar_autotracking_settings",
        JsonRpcBinding("getRadarAutotrackingSettings", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        result=GetRadarAutotrackingSettingsResult,
        access="viewer",
        effect="read",
    )
    set_radar_autotracking_settings = Operation(
        INFO,
        "set_radar_autotracking_settings",
        JsonRpcBinding("setRadarAutotrackingSettings", PATH),
        params=SetRadarAutotrackingSettingsRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_radar_autotracking_capabilities = Operation(
        INFO,
        "get_radar_autotracking_capabilities",
        JsonRpcBinding("getRadarAutotrackingCapabilities", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        result=GetRadarAutotrackingCapabilitiesResult,
        access="viewer",
        effect="read",
    )
    add_radar_profile = Operation(
        INFO,
        "add_radar_profile",
        JsonRpcBinding("addRadarProfile", PATH),
        params=AddRadarProfileRequest,
        access="operator",
        effect="write",
        write="create",
    )
    get_radar_profile = Operation(
        INFO,
        "get_radar_profile",
        JsonRpcBinding("getRadarProfile", "/axis-cgi/ptz-autotracking/viewer.cgi"),
        params=GetRadarProfileRequest,
        result=RadarProfile,
        access="viewer",
        effect="read",
    )
    update_radar_profile = Operation(
        INFO,
        "update_radar_profile",
        JsonRpcBinding("updateRadarProfile", PATH),
        params=UpdateRadarProfileRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    delete_radar_profile = Operation(
        INFO,
        "delete_radar_profile",
        JsonRpcBinding("deleteRadarProfile", PATH),
        params=DeleteRadarProfileRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    send_test_autotracking_event = Operation(
        INFO,
        "send_test_autotracking_event",
        JsonRpcBinding("sendTestAutotrackingEvent", PATH),
        params=SendTestAutotrackingEventRequest,
        access="operator",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class PtzAutotrackerApi(SyncApi):
    """PTZ Autotracker API (``autotracking-2``, version 1)."""

    INFO = INFO

    def get_application_settings(
        self, *, request_options: RequestOptions | None = None
    ) -> GetApplicationSettingsResult:
        """Return the general application settings (service active, version, API support).

        Access: viewer.
        """
        return self._run(OPS.get_application_settings, None, {}, request_options)

    @overload
    def set_application_settings(
        self, request: SetApplicationSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_application_settings(
        self, /, *, service: ServiceUpdate, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_application_settings(
        self,
        request: SetApplicationSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set whether the Autotracking service is running (subscribes to data sources).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_application_settings, request, kwargs, request_options)

    def get_autotracking_settings(
        self, *, request_options: RequestOptions | None = None
    ) -> GetAutotrackingSettingsResult:
        """List the general autotracking settings (filters, trackers, tracking params, profiles).

        Access: viewer.
        """
        return self._run(OPS.get_autotracking_settings, None, {}, request_options)

    @overload
    def set_autotracking_settings(
        self, request: SetAutotrackingSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_autotracking_settings(
        self,
        /,
        *,
        min_object_size: MinObjectSize | MISSING = MISSING,
        min_object_lifespan: MinObjectLifespan | MISSING = MISSING,
        tracker_support: ActiveTrackerUpdate | MISSING = MISSING,
        tracking_params: TrackingParams | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_autotracking_settings(
        self,
        request: SetAutotrackingSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change the general autotracking settings (not profile settings).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_autotracking_settings, request, kwargs, request_options)

    def get_viewport_config(self, *, request_options: RequestOptions | None = None) -> GetViewportConfigResult:
        """Return the rotation set by setViewportConfig (-1 if not initialized). Access: viewer."""
        return self._run(OPS.get_viewport_config, None, {}, request_options)

    def set_viewport_config(
        self,
        *,
        rotation: Literal[0, 180],
        metadata: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the viewport rotation (0 or 180) used by the backend; object data is not streamed until this is called.

        If two different frontends set different rotation settings, backend behaviour is unspecified.

        Changes only the fields given. Access: viewer.
        """
        self._run(OPS.set_viewport_config, None, {"rotation": rotation, "metadata": metadata}, request_options)

    def get_autotracking_target(self, *, request_options: RequestOptions | None = None) -> GetAutotrackingTargetResult:
        """Return the ID of the currently tracked object (-1 if not tracking). Access: viewer."""
        return self._run(OPS.get_autotracking_target, None, {}, request_options)

    def set_autotracking_target(self, *, target_id: int, request_options: RequestOptions | None = None) -> None:
        """Start following an object (positive ID from the object stream) or stop with -1.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_autotracking_target, None, {"target_id": target_id}, request_options)

    def get_autotracking_state(self, *, request_options: RequestOptions | None = None) -> GetAutotrackingStateResult:
        """Return whether automatic triggering in zones is enabled (automatic mode). Access: viewer."""
        return self._run(OPS.get_autotracking_state, None, {}, request_options)

    def set_autotracking_state(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Enable (automatic mode: first object entering a visible zone triggers tracking) or disable (manual: client calls setAutotrackingTarget).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_autotracking_state, None, {"enabled": enabled}, request_options)

    @overload
    def add_profile(
        self, request: AddProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddProfileResult: ...
    @overload
    def add_profile(
        self,
        /,
        *,
        name: str | MISSING = MISSING,
        preset: int,
        enabled: bool | MISSING = MISSING,
        timeout_to_home: int | MISSING = MISSING,
        aoa_id: str | MISSING = MISSING,
        px_polygon: list[float] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddProfileResult: ...
    def add_profile(
        self,
        request: AddProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AddProfileResult:
        """Create a new profile (zone). Access: operator."""
        return self._run(OPS.add_profile, request, kwargs, request_options)

    def get_profile(self, *, id: int, request_options: RequestOptions | None = None) -> Profile:
        """Return all settings of a profile. Access: viewer."""
        return self._run(OPS.get_profile, None, {"id": id}, request_options)

    @overload
    def update_profile(
        self, request: UpdateProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> ProfileSummary: ...
    @overload
    def update_profile(
        self,
        /,
        *,
        id: int,
        name: str | MISSING = MISSING,
        preset: int | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        timeout_to_home: int | MISSING = MISSING,
        aoa_id: str | MISSING = MISSING,
        px_polygon: list[float] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ProfileSummary: ...
    def update_profile(
        self,
        request: UpdateProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ProfileSummary:
        """Change settings of an existing profile; only included fields are updated.

        Changes only the fields given. Access: operator.
        """
        return self._run(OPS.update_profile, request, kwargs, request_options)

    def delete_profile(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Remove a profile. Access: operator."""
        self._run(OPS.delete_profile, None, {"id": id}, request_options)

    def set_temp_zone(
        self,
        *,
        zone_type: str | MISSING = MISSING,
        timeout: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Create a temporary zone for automatic detection and tracking. Access: operator."""
        self._run(OPS.set_temp_zone, None, {"zone_type": zone_type, "timeout": timeout}, request_options)

    def get_radar_autotracking_settings(
        self, *, request_options: RequestOptions | None = None
    ) -> GetRadarAutotrackingSettingsResult:
        """Get the radar autotracker settings (alignment, radar profiles, object priority).

        Access: viewer.
        """
        return self._run(OPS.get_radar_autotracking_settings, None, {}, request_options)

    @overload
    def set_radar_autotracking_settings(
        self, request: SetRadarAutotrackingSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_radar_autotracking_settings(
        self,
        /,
        *,
        radar_ptz_alignment: RadarPtzAlignment | MISSING = MISSING,
        radar_profiles: list[RadarProfileSettings] | MISSING = MISSING,
        object_priority: ObjectPriority | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_radar_autotracking_settings(
        self,
        request: SetRadarAutotrackingSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change radar autotracker settings; omitted objects keep previous settings.

        Changes only the entries given; entries that do not exist yet may be created. Access: operator.
        """
        self._run(OPS.set_radar_autotracking_settings, request, kwargs, request_options)

    def get_radar_autotracking_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetRadarAutotrackingCapabilitiesResult:
        """Get radar autotracker capabilities (valid ranges and allowed values). Access: viewer."""
        return self._run(OPS.get_radar_autotracking_capabilities, None, {}, request_options)

    @overload
    def add_radar_profile(
        self, request: AddRadarProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_radar_profile(
        self,
        /,
        *,
        radar_scenario_uuid: str,
        name: str,
        enabled: bool,
        priority: int,
        video_object_classifications: list[VideoObjectClassification],
        tracking_requirement: TrackingRequirement,
        vod_confirmation_time: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_radar_profile(
        self,
        request: AddRadarProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a radar profile (service must be active; fails if radarScenarioUuid already exists).

        radarScenarioUuid identifies a scenario in the Radar Configuration CGI; you must keep radar profiles
        updated if UUIDs change or are removed.

        Access: operator.
        """
        self._run(OPS.add_radar_profile, request, kwargs, request_options)

    def get_radar_profile(self, *, id: int, request_options: RequestOptions | None = None) -> RadarProfile:
        """Get the settings of a radar profile. Access: viewer."""
        return self._run(OPS.get_radar_profile, None, {"id": id}, request_options)

    @overload
    def update_radar_profile(
        self, request: UpdateRadarProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_radar_profile(
        self,
        /,
        *,
        id: int,
        radar_scenario_uuid: str | MISSING = MISSING,
        name: str | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        priority: int | MISSING = MISSING,
        video_object_classifications: list[VideoObjectClassification] | MISSING = MISSING,
        tracking_requirement: TrackingRequirement | MISSING = MISSING,
        vod_confirmation_time: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_radar_profile(
        self,
        request: UpdateRadarProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a radar profile; only included fields are updated.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_radar_profile, request, kwargs, request_options)

    def delete_radar_profile(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Delete a radar profile. Access: operator."""
        self._run(OPS.delete_radar_profile, None, {"id": id}, request_options)

    def send_test_autotracking_event(
        self,
        *,
        event_type: Literal[0, 1],
        profile_id: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Temporarily trigger an autotracking event (service must be active). Access: operator."""
        self._run(
            OPS.send_test_autotracking_event,
            None,
            {"event_type": event_type, "profile_id": profile_id},
            request_options,
        )


class AsyncPtzAutotrackerApi(AsyncApi):
    """PTZ Autotracker API (``autotracking-2``, version 1)."""

    INFO = INFO

    async def get_application_settings(
        self, *, request_options: RequestOptions | None = None
    ) -> GetApplicationSettingsResult:
        """Return the general application settings (service active, version, API support).

        Access: viewer.
        """
        return await self._run(OPS.get_application_settings, None, {}, request_options)

    @overload
    async def set_application_settings(
        self, request: SetApplicationSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_application_settings(
        self, /, *, service: ServiceUpdate, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_application_settings(
        self,
        request: SetApplicationSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set whether the Autotracking service is running (subscribes to data sources).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_application_settings, request, kwargs, request_options)

    async def get_autotracking_settings(
        self, *, request_options: RequestOptions | None = None
    ) -> GetAutotrackingSettingsResult:
        """List the general autotracking settings (filters, trackers, tracking params, profiles).

        Access: viewer.
        """
        return await self._run(OPS.get_autotracking_settings, None, {}, request_options)

    @overload
    async def set_autotracking_settings(
        self, request: SetAutotrackingSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_autotracking_settings(
        self,
        /,
        *,
        min_object_size: MinObjectSize | MISSING = MISSING,
        min_object_lifespan: MinObjectLifespan | MISSING = MISSING,
        tracker_support: ActiveTrackerUpdate | MISSING = MISSING,
        tracking_params: TrackingParams | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_autotracking_settings(
        self,
        request: SetAutotrackingSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change the general autotracking settings (not profile settings).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_autotracking_settings, request, kwargs, request_options)

    async def get_viewport_config(self, *, request_options: RequestOptions | None = None) -> GetViewportConfigResult:
        """Return the rotation set by setViewportConfig (-1 if not initialized). Access: viewer."""
        return await self._run(OPS.get_viewport_config, None, {}, request_options)

    async def set_viewport_config(
        self,
        *,
        rotation: Literal[0, 180],
        metadata: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the viewport rotation (0 or 180) used by the backend; object data is not streamed until this is called.

        If two different frontends set different rotation settings, backend behaviour is unspecified.

        Changes only the fields given. Access: viewer.
        """
        await self._run(OPS.set_viewport_config, None, {"rotation": rotation, "metadata": metadata}, request_options)

    async def get_autotracking_target(
        self, *, request_options: RequestOptions | None = None
    ) -> GetAutotrackingTargetResult:
        """Return the ID of the currently tracked object (-1 if not tracking). Access: viewer."""
        return await self._run(OPS.get_autotracking_target, None, {}, request_options)

    async def set_autotracking_target(self, *, target_id: int, request_options: RequestOptions | None = None) -> None:
        """Start following an object (positive ID from the object stream) or stop with -1.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_autotracking_target, None, {"target_id": target_id}, request_options)

    async def get_autotracking_state(
        self, *, request_options: RequestOptions | None = None
    ) -> GetAutotrackingStateResult:
        """Return whether automatic triggering in zones is enabled (automatic mode). Access: viewer."""
        return await self._run(OPS.get_autotracking_state, None, {}, request_options)

    async def set_autotracking_state(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Enable (automatic mode: first object entering a visible zone triggers tracking) or disable (manual: client calls setAutotrackingTarget).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_autotracking_state, None, {"enabled": enabled}, request_options)

    @overload
    async def add_profile(
        self, request: AddProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddProfileResult: ...
    @overload
    async def add_profile(
        self,
        /,
        *,
        name: str | MISSING = MISSING,
        preset: int,
        enabled: bool | MISSING = MISSING,
        timeout_to_home: int | MISSING = MISSING,
        aoa_id: str | MISSING = MISSING,
        px_polygon: list[float] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddProfileResult: ...
    async def add_profile(
        self,
        request: AddProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AddProfileResult:
        """Create a new profile (zone). Access: operator."""
        return await self._run(OPS.add_profile, request, kwargs, request_options)

    async def get_profile(self, *, id: int, request_options: RequestOptions | None = None) -> Profile:
        """Return all settings of a profile. Access: viewer."""
        return await self._run(OPS.get_profile, None, {"id": id}, request_options)

    @overload
    async def update_profile(
        self, request: UpdateProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> ProfileSummary: ...
    @overload
    async def update_profile(
        self,
        /,
        *,
        id: int,
        name: str | MISSING = MISSING,
        preset: int | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        timeout_to_home: int | MISSING = MISSING,
        aoa_id: str | MISSING = MISSING,
        px_polygon: list[float] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ProfileSummary: ...
    async def update_profile(
        self,
        request: UpdateProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ProfileSummary:
        """Change settings of an existing profile; only included fields are updated.

        Changes only the fields given. Access: operator.
        """
        return await self._run(OPS.update_profile, request, kwargs, request_options)

    async def delete_profile(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Remove a profile. Access: operator."""
        await self._run(OPS.delete_profile, None, {"id": id}, request_options)

    async def set_temp_zone(
        self,
        *,
        zone_type: str | MISSING = MISSING,
        timeout: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Create a temporary zone for automatic detection and tracking. Access: operator."""
        await self._run(OPS.set_temp_zone, None, {"zone_type": zone_type, "timeout": timeout}, request_options)

    async def get_radar_autotracking_settings(
        self, *, request_options: RequestOptions | None = None
    ) -> GetRadarAutotrackingSettingsResult:
        """Get the radar autotracker settings (alignment, radar profiles, object priority).

        Access: viewer.
        """
        return await self._run(OPS.get_radar_autotracking_settings, None, {}, request_options)

    @overload
    async def set_radar_autotracking_settings(
        self, request: SetRadarAutotrackingSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_radar_autotracking_settings(
        self,
        /,
        *,
        radar_ptz_alignment: RadarPtzAlignment | MISSING = MISSING,
        radar_profiles: list[RadarProfileSettings] | MISSING = MISSING,
        object_priority: ObjectPriority | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_radar_autotracking_settings(
        self,
        request: SetRadarAutotrackingSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change radar autotracker settings; omitted objects keep previous settings.

        Changes only the entries given; entries that do not exist yet may be created. Access: operator.
        """
        await self._run(OPS.set_radar_autotracking_settings, request, kwargs, request_options)

    async def get_radar_autotracking_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetRadarAutotrackingCapabilitiesResult:
        """Get radar autotracker capabilities (valid ranges and allowed values). Access: viewer."""
        return await self._run(OPS.get_radar_autotracking_capabilities, None, {}, request_options)

    @overload
    async def add_radar_profile(
        self, request: AddRadarProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_radar_profile(
        self,
        /,
        *,
        radar_scenario_uuid: str,
        name: str,
        enabled: bool,
        priority: int,
        video_object_classifications: list[VideoObjectClassification],
        tracking_requirement: TrackingRequirement,
        vod_confirmation_time: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_radar_profile(
        self,
        request: AddRadarProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a radar profile (service must be active; fails if radarScenarioUuid already exists).

        radarScenarioUuid identifies a scenario in the Radar Configuration CGI; you must keep radar profiles
        updated if UUIDs change or are removed.

        Access: operator.
        """
        await self._run(OPS.add_radar_profile, request, kwargs, request_options)

    async def get_radar_profile(self, *, id: int, request_options: RequestOptions | None = None) -> RadarProfile:
        """Get the settings of a radar profile. Access: viewer."""
        return await self._run(OPS.get_radar_profile, None, {"id": id}, request_options)

    @overload
    async def update_radar_profile(
        self, request: UpdateRadarProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_radar_profile(
        self,
        /,
        *,
        id: int,
        radar_scenario_uuid: str | MISSING = MISSING,
        name: str | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        priority: int | MISSING = MISSING,
        video_object_classifications: list[VideoObjectClassification] | MISSING = MISSING,
        tracking_requirement: TrackingRequirement | MISSING = MISSING,
        vod_confirmation_time: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_radar_profile(
        self,
        request: UpdateRadarProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a radar profile; only included fields are updated.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_radar_profile, request, kwargs, request_options)

    async def delete_radar_profile(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Delete a radar profile. Access: operator."""
        await self._run(OPS.delete_radar_profile, None, {"id": id}, request_options)

    async def send_test_autotracking_event(
        self,
        *,
        event_type: Literal[0, 1],
        profile_id: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Temporarily trigger an autotracking event (service must be active). Access: operator."""
        await self._run(
            OPS.send_test_autotracking_event,
            None,
            {"event_type": event_type, "profile_id": profile_id},
            request_options,
        )
