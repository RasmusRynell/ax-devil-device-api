# GENERATED from specs/apis/applications/fence-guard.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the AXIS Fence Guard ACAP (virtual fence lines, crossing direction, exclusion filters, perspective, PTZ presets, alarm overlay).

Docs: https://developer.axis.com/vapix/applications/fence-guard/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import AcapDiscovery, ApiInfo, ApiVersion, Applicability, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Point = list[Annotated[float, Field(ge=-1, le=1)]]


class Camera(Model):
    """General settings of one camera, shared by all profiles using it."""

    active: bool
    """Profiles for the camera may be active if true; all profiles for the camera are inactivated if false. Default: True."""
    id: int = Field(ge=1)
    """Camera value used with media.amp (starts at 1). Default: 1."""
    rotation: Literal[0, 90, 180, 270]
    """Rotation of the camera in degrees; should match Image.I<camera>.Appearance.Rotation. Default: 0."""
    overlay_resolution: str | None = Field(
        default=None,
        validation_alias="overlayResolution",
        serialization_alias="overlayResolution",
        pattern="^[0-9]+x[0-9]+$",
    )
    """Resolution <width>x<height> of the video streams with the alarm overlay burnt in. Optional if alarmOverlayEnabled is not active. Since 1.3."""


FilterType = Literal["sizePercentage", "sizePerspective", "timeShortLivedLimit"]


class Filter(Model):
    """Exclusion filter. A filter that is not present is disabled. Only one size filter (sizePercentage or sizePerspective) can be active at a time."""

    type: FilterType
    data: list[int] | int
    """Depends on the type. sizePercentage: [w, h] in percent of the image, each 3..100 (default [5, 5]); objects at or below are ignored. sizePerspective: [w, h] real-world size in cm; needs perspective bars. timeShortLivedLimit: integer seconds 1..5 (default 1)."""
    active: bool | None = None
    """If the filter is active."""


class Trigger(Model):
    type: Literal["fence"]
    data: list[Point]
    """Fence polyline [[x0,y0], ..., [xn,yn]]."""
    alarm_direction: Literal["leftToRight", "rightToLeft", "both"] = Field(
        validation_alias="alarmDirection", serialization_alias="alarmDirection"
    )
    """Left/right from a viewer at the segment start looking towards its end."""


class PerspectiveBar(Model):
    type: Literal["bar"]
    """A vertical line in the rotation of the camera."""
    data: list[Point]
    """Start (touches the ground plane) and end point. (minItems=2, maxItems=2)"""
    height: int
    """Real-world height (cm) of an object at the same location and with the same perceived height."""


class Profile(Model):
    name: str = Field(max_length=15)
    """Unicode, up to 15 characters; part of the event nice name. Invalid: '&&', '<', '>'. Default: 'Profile <uid>'."""
    uid: int
    """Unique id of the profile. Default: 1."""
    camera: int
    """Shall match the id of the corresponding camera. Default: 1."""
    alarm_overlay_enabled: bool | None = Field(
        default=None, validation_alias="alarmOverlayEnabled", serialization_alias="alarmOverlayEnabled"
    )
    """True if the profile's alarming objects are shown in an alarm overlay video stream. Since 1.3. Default: False."""
    filters: list[Filter] | None = None
    """Exclusion filters; all optional; a filter not present is disabled."""
    triggers: list[Trigger]
    """Exactly one fence (may change in the future). (minItems=1, maxItems=1)"""
    presets: list[int] = []
    """Since 1.1. PTZ only (error on non-PTZ; absent on other cameras). At most one preset index (PTZ.Preset.P0.Position.P<index>), -1 any preset, -2 anywhere; empty means always active."""
    perspective: list[PerspectiveBar] = []
    """Perspective bars calibrating the view; needed for the sizePerspective filter."""


class Configuration(Model):
    """The complete ACAP configuration, as read by get_configuration and written by set_configuration."""

    cameras: list[Camera]
    profiles: list[Profile]
    """To remove a profile, remove it from the array."""
    configuration_status: int | None = Field(
        default=None, validation_alias="configurationStatus", serialization_alias="configurationStatus", ge=0
    )
    """Read-only (ignored by setConfiguration). 0 is the default configuration; incremented by each set; reset to 1 after MAX_INT."""

    @classmethod
    def from_current(cls, configuration: Configuration) -> Configuration:
        """A request that rewrites ``configuration`` unchanged: copy it, edit fields, send it back."""
        data = configuration.request_data(exclude={"configuration_status"})
        return cls(**data)


class AlarmOverlayCamera(Model):
    id: int | None = None
    """Same as cameras[i].id in the configuration (starts at 1)."""
    available_resolutions: list[str] | None = Field(
        default=None, validation_alias="availableResolutions", serialization_alias="availableResolutions"
    )
    """Resolutions <width>x<height> for which the alarm overlay can be used on this camera."""


class AlarmOverlayCapabilities(Model):
    is_supported: bool | None = Field(default=None, validation_alias="isSupported", serialization_alias="isSupported")
    """True if the camera supports the burnt-in overlay feature."""
    max_nbr_active_cameras: int | None = Field(
        default=None, validation_alias="maxNbrActiveCameras", serialization_alias="maxNbrActiveCameras"
    )
    """Number of cameras of a multichannel device that can use the feature at once; 0 if not supported."""
    cameras: list[AlarmOverlayCamera] | None = None


class FilterCapability(Model):
    type: FilterType | None = None
    min: list[int] | int | None = None
    """Minimum allowed value; [w, h] percent for sizePercentage, seconds for timeShortLivedLimit."""
    max: list[int] | int | None = None
    """Maximum allowed value; same shape as min."""
    default: list[int] | int | None = None
    """Default value; same shape as min."""
    default_active: bool | None = Field(
        default=None, validation_alias="defaultActive", serialization_alias="defaultActive"
    )
    """If the filter is active by default. The docs table misspells it defautActive for timeShortLivedLimit."""


class TriggerCapability(Model):
    type: Literal["fence"] | None = None
    min: list[float] | None = None
    """[xPos, yPos] minimum allowed values for the fence."""
    max: list[float] | None = None
    """[xPos, yPos] maximum allowed values for the fence."""
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
    valid_alarm_directions: list[str] | None = Field(
        default=None, validation_alias="validAlarmDirections", serialization_alias="validAlarmDirections"
    )
    default_instance: list[Point] | None = Field(
        default=None, validation_alias="defaultInstance", serialization_alias="defaultInstance"
    )
    default_alarm_direction: str | None = Field(
        default=None, validation_alias="defaultAlarmDirection", serialization_alias="defaultAlarmDirection"
    )


class ProfileCapabilities(Model):
    min_nbr_profiles_per_camera: int | None = Field(
        default=None, validation_alias="minNbrProfilesPerCamera", serialization_alias="minNbrProfilesPerCamera"
    )
    max_nbr_profiles_per_camera: int | None = Field(
        default=None, validation_alias="maxNbrProfilesPerCamera", serialization_alias="maxNbrProfilesPerCamera"
    )
    min_length_name: int | None = Field(
        default=None, validation_alias="minLengthName", serialization_alias="minLengthName"
    )
    max_length_name: int | None = Field(
        default=None, validation_alias="maxLengthName", serialization_alias="maxLengthName"
    )


class PresetCapabilities(Model):
    """Only for mechanical PTZ cameras."""

    max_nbr_presets_per_profile: int | None = Field(
        default=None, validation_alias="maxNbrPresetsPerProfile", serialization_alias="maxNbrPresetsPerProfile"
    )
    default_preset: int | None = Field(
        default=None, validation_alias="defaultPreset", serialization_alias="defaultPreset"
    )


class ConfigurationCapabilities(Model):
    alarm_overlay: AlarmOverlayCapabilities | None = Field(
        default=None, validation_alias="alarmOverlay", serialization_alias="alarmOverlay"
    )
    filters: list[FilterCapability] | None = None
    triggers: list[TriggerCapability] | None = None
    profiles: ProfileCapabilities | None = None
    presets: PresetCapabilities | None = None


class SendAlarmEventRequest(Model):
    profile: int
    """The unique id (uid) of the profile that will send the alarm event. There must be a profile with the specified uid."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/fenceguard/control.cgi"

INFO = ApiInfo(
    id="fence-guard",
    name="Fence guard",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 1), ApiVersion(1, 2), ApiVersion(1, 3)),
    discovery=(AcapDiscovery("FenceGuard"),),
    docs=("https://developer.axis.com/vapix/applications/fence-guard/",),
    errors={
        1000: ErrorCode(
            "Application error; the application failed to handle the request (see the server log; a restart may help).",
            "internal",
        ),
        2000: ErrorCode("Unsupported version; the major version number isn't supported.", "unsupported"),
        2001: ErrorCode("Invalid format; the request does not follow the JSON schema.", "invalid_argument"),
        2002: ErrorCode(
            "Incoherent format; parts of the request contradict each other or refer to something that does not exist.",
            "invalid_argument",
        ),
        2003: ErrorCode("Missing parameter; a mandatory parameter is missing.", "invalid_argument"),
        2004: ErrorCode("Invalid parameter; a parameter has an invalid value.", "invalid_argument"),
        8000: ErrorCode(
            "Unsupported product; the camera is not supported by this version of the application.", "unsupported"
        ),
        9000: ErrorCode("Invalid license; the license file is invalid or missing.", "access_denied"),
        "1001-1999": ErrorCode(
            "Reserved for camera application (server) errors, e.g. could not read configuration from file.", "internal"
        ),
        "2005-2999": ErrorCode(
            "Reserved for client errors, e.g. wrong format of configuration file or invalid parameter.",
            "invalid_argument",
        ),
        "9001-9999": ErrorCode(
            "Reserved for license related errors, e.g. license invalid or missing.", "access_denied"
        ),
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
        params=Configuration,
        access="admin",
        effect="write",
        write="replace",
        applicability=(
            Applicability("cameras.overlay_resolution", ApiVersion(1, 3)),
            Applicability("profiles.alarm_overlay_enabled", ApiVersion(1, 3)),
            Applicability("profiles.presets", ApiVersion(1, 1)),
        ),
        errors={
            2002: ErrorCode(
                "Incoherent format; parts of the configuration contradict each other, e.g. several profiles have the same uid.",
                "invalid_argument",
            )
        },
    )
    get_configuration_capabilities = Operation(
        INFO,
        "get_configuration_capabilities",
        JsonRpcBinding("getConfigurationCapabilities", PATH),
        result=ConfigurationCapabilities,
        access="admin",
        effect="read",
    )
    send_alarm_event = Operation(
        INFO,
        "send_alarm_event",
        JsonRpcBinding("sendAlarmEvent", PATH),
        params=SendAlarmEventRequest,
        access="operator",
        effect="action",
        errors={
            2002: ErrorCode(
                "Incoherent format; the request cannot be handled, e.g. the profile id does not exist or is on an inactive camera.",
                "not_found",
            )
        },
    )


# ---------------------------------------------------------------------------
# API classes


class FenceGuardApi(SyncApi):
    """Fence guard (``fence-guard``, version 1)."""

    INFO = INFO

    def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Request the current configuration of the ACAP. Access: admin."""
        return self._run(OPS.get_configuration, None, {}, request_options)

    @overload
    def set_configuration(
        self, request: Configuration, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_configuration(
        self, /, *, cameras: list[Camera], profiles: list[Profile], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_configuration(
        self, request: Configuration | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set the complete configuration of the ACAP.

        Replaces the whole configuration, so send everything that should stay; to remove a profile, leave it
        out of profiles. If the ACAP is not restarted beforehand, ongoing events are set inactive when the
        new configuration is applied, stopping ongoing recordings; on multichannel products all cameras are
        affected simultaneously. Prefer a minified body, as POST requests have a size limit. apiVersion 1.2
        or older clients cannot change alarmOverlayEnabled and overlayResolution: those values are ignored
        and the existing ones are kept.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_configuration, request, kwargs, request_options)

    def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Request the boundaries and default values of the ACAP (constant per camera).

        Access: admin.
        """
        return self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    def send_alarm_event(self, profile: int, *, request_options: RequestOptions | None = None) -> None:
        """Send a stateful alarm event (active for a few seconds) for a profile, for VMS testing.

        The response is returned immediately. All events related to the profile are sent, independent of its
        current state (e.g. PTZ profiles connected to other presets).

        Access: operator.
        """
        self._run(OPS.send_alarm_event, None, {"profile": profile}, request_options)


class AsyncFenceGuardApi(AsyncApi):
    """Fence guard (``fence-guard``, version 1)."""

    INFO = INFO

    async def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Request the current configuration of the ACAP. Access: admin."""
        return await self._run(OPS.get_configuration, None, {}, request_options)

    @overload
    async def set_configuration(
        self, request: Configuration, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_configuration(
        self, /, *, cameras: list[Camera], profiles: list[Profile], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_configuration(
        self, request: Configuration | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set the complete configuration of the ACAP.

        Replaces the whole configuration, so send everything that should stay; to remove a profile, leave it
        out of profiles. If the ACAP is not restarted beforehand, ongoing events are set inactive when the
        new configuration is applied, stopping ongoing recordings; on multichannel products all cameras are
        affected simultaneously. Prefer a minified body, as POST requests have a size limit. apiVersion 1.2
        or older clients cannot change alarmOverlayEnabled and overlayResolution: those values are ignored
        and the existing ones are kept.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_configuration, request, kwargs, request_options)

    async def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Request the boundaries and default values of the ACAP (constant per camera).

        Access: admin.
        """
        return await self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    async def send_alarm_event(self, profile: int, *, request_options: RequestOptions | None = None) -> None:
        """Send a stateful alarm event (active for a few seconds) for a profile, for VMS testing.

        The response is returned immediately. All events related to the profile are sent, independent of its
        current state (e.g. PTZ profiles connected to other presets).

        Access: operator.
        """
        await self._run(OPS.send_alarm_event, None, {"profile": profile}, request_options)
