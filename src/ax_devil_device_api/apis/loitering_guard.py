# GENERATED from specs/apis/applications/loitering-guard.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the AXIS Loitering Guard ACAP, which raises events when objects stay too long in a loitering area.

Docs: https://developer.axis.com/vapix/applications/loitering-guard/
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
    """Settings shared by all profiles that use the camera (video channel)."""

    active: bool | None = None
    """When false, all profiles of the camera are inactive. Default true."""
    id: int = Field(ge=1)
    """Camera value used with ``media.amp``; starts at 1."""
    rotation: Literal[0, 90, 180, 270] | None = None
    """Rotation of the camera in degrees. Should match ``Image.I<camera>.Appearance.Rotation``. Default 0."""
    overlay_resolution: str | None = Field(
        default=None,
        validation_alias="overlayResolution",
        serialization_alias="overlayResolution",
        pattern="^[0-9]+x[0-9]+$",
    )
    """Since 1.3. ``<width>x<height>`` of the video streams that get alarming objects burnt in. Optional unless a profile enables ``alarmOverlayEnabled``."""


class SizePercentageFilter(Model):
    """Objects at or below this width and height (percent of the image) cannot raise an alarm."""

    type: Literal["sizePercentage"]
    data: list[Annotated[int, Field(ge=3, le=100)]]
    """``[w, h]`` in percent of the image. Exactly two items. Default ``[5, 5]``."""
    active: bool | None = None


class SizePerspectiveFilter(Model):
    """Objects smaller than this real-world size cannot raise an alarm. Requires perspective bars; only one size filter may be active."""

    type: Literal["sizePerspective"]
    data: list[int]
    """``[w, h]`` real-world size in cm. Exactly two items."""
    active: bool | None = None


class DistanceSwayingObjectFilter(Model):
    """Global setting. Maximum distance an object may sway without raising an alarm; delays all alarms."""

    type: Literal["distanceSwayingObject"]
    data: int = Field(ge=3, le=10)
    """Percent of the image. Default 5."""
    active: bool | None = None


class ExcludeAreaFilter(Model):
    """Polygon in which objects are ignored. Up to three per profile; there is no ``active`` flag, an unused area is removed."""

    type: Literal["excludeArea"]
    data: list[Point]


Filter = SizePercentageFilter | SizePerspectiveFilter | DistanceSwayingObjectFilter | ExcludeAreaFilter
ConditionType = Literal["individual", "group"]


class Condition(Model):
    """A rule for when an alarm triggers. ``individual`` and ``group`` cannot be active at the same time."""

    type: ConditionType
    """``individual``: each object triggers on its own (default 120 s). ``group``: alarm if any object has been in the area too long (default 160 s)."""
    data: int = Field(ge=10, le=360)
    """Seconds."""
    active: bool | None = None


class Trigger(Model):
    """The loitering area of a profile. A profile has exactly one."""

    type: Literal["loiteringArea"]
    data: list[Point]
    """Loitering area polygon, normalized -1..1."""
    conditions: list[Condition] | None = None


class PerspectiveBar(Model):
    """A vertical line, in the rotation of the camera, that calibrates real-world sizes."""

    type: Literal["bar"]
    data: list[Point]
    """Start point (touching the ground plane) and end point. Exactly two items."""
    height: int | None = None
    """Real-world height (cm) of an object at the same location and with the same perceived height as the bar."""


class Profile(Model):
    """One loitering detection profile."""

    name: str | None = Field(default=None, max_length=15)
    """Up to 15 unicode characters; part of the event nice name. ``&&``, ``<`` and ``>`` are not allowed. Default ``Profile <uid>``."""
    camera: int
    """Must match the ``id`` of a camera in ``cameras``. Default 1."""
    uid: int
    """Unique id of the profile. Default 1."""
    alarm_overlay_enabled: bool | None = Field(
        default=None, validation_alias="alarmOverlayEnabled", serialization_alias="alarmOverlayEnabled"
    )
    """Since 1.3. Show the alarming objects of the profile burnt into the overlay video stream. Default false."""
    filters: list[Filter] | None = None
    triggers: list[Trigger] | None = None
    """Exactly one ``loiteringArea``."""
    presets: list[int] | None = None
    """Since 1.1. Mechanical PTZ cameras only (an error on other cameras). At most one preset index (``PTZ.Preset.P0.Position.P<index>``), -1 for any preset, -2 for anywhere. Empty or omitted: always active."""
    perspective: list[PerspectiveBar] | None = None
    """Perspective bars; needed for the ``sizePerspective`` filter. Default empty."""


class Configuration(Model):
    """The complete application configuration. The same shape is read and written."""

    cameras: list[Camera]
    profiles: list[Profile]
    """To remove a profile, leave it out of the array."""
    configuration_status: int | None = Field(
        default=None, validation_alias="configurationStatus", serialization_alias="configurationStatus", ge=0
    )
    """Ignored by ``set_configuration``. 0 is the default configuration; increased by one on every set and reset to 1 after ``INT_MAX``."""

    @classmethod
    def from_current(cls, configuration: Configuration) -> Configuration:
        """A request that rewrites ``configuration`` unchanged: copy it, edit fields, send it back."""
        data = configuration.request_data(exclude={"configuration_status"})
        return cls(**data)


class AlarmOverlayCamera(Model):
    id: int | None = None
    """Same as ``cameras[].id`` in the configuration."""
    available_resolutions: list[str] | None = Field(
        default=None, validation_alias="availableResolutions", serialization_alias="availableResolutions"
    )
    """Resolutions (``<width>x<height>``) that support alarm overlay for the camera."""


class AlarmOverlayCapabilities(Model):
    """Since 1.3."""

    is_supported: bool | None = Field(default=None, validation_alias="isSupported", serialization_alias="isSupported")
    max_nbr_active_cameras: int | None = Field(
        default=None, validation_alias="maxNbrActiveCameras", serialization_alias="maxNbrActiveCameras"
    )
    """Cameras of a multichannel device that can use the feature at once; 0 if not supported."""
    cameras: list[AlarmOverlayCamera] | None = None


class FilterCapability(Model):
    """Bounds of one filter type. The type of ``min``, ``max`` and ``default`` depends on the filter (``[w, h]`` percent, an integer, or ``[x, y]``)."""

    type: Literal["sizePercentage", "distanceSwayingObject", "excludeArea"] | None = None
    min: Any | None = None
    max: Any | None = None
    default: Any | None = None
    default_active: bool | None = Field(
        default=None, validation_alias="defaultActive", serialization_alias="defaultActive"
    )
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


class ConditionCapability(Model):
    type: ConditionType | None = None
    min: int | None = None
    """Seconds. 10."""
    max: int | None = None
    """Seconds. 360."""
    default: int | None = None
    """Seconds. ``individual`` 120, ``group`` 160."""
    default_active: bool | None = Field(
        default=None, validation_alias="defaultActive", serialization_alias="defaultActive"
    )
    """``individual`` true, ``group`` false."""


class TriggerCapability(Model):
    type: Literal["loiteringArea"] | None = None
    min: list[float] | None = None
    """``[x, y]`` minimum position."""
    max: list[float] | None = None
    """``[x, y]`` maximum position."""
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
    conditions: list[ConditionCapability] | None = None


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
    """Mechanical PTZ cameras only."""

    max_nbr_presets_per_profile: int | None = Field(
        default=None, validation_alias="maxNbrPresetsPerProfile", serialization_alias="maxNbrPresetsPerProfile"
    )
    default_preset: int | None = Field(
        default=None, validation_alias="defaultPreset", serialization_alias="defaultPreset"
    )


class ConfigurationCapabilities(Model):
    """Boundaries and default values. Constant for a given camera."""

    alarm_overlay: AlarmOverlayCapabilities | None = Field(
        default=None, validation_alias="alarmOverlay", serialization_alias="alarmOverlay"
    )
    filters: list[FilterCapability] | None = None
    triggers: list[TriggerCapability] | None = None
    profiles: ProfileCapabilities | None = None
    presets: PresetCapabilities | None = None


class SendAlarmEventRequest(Model):
    profile: int
    """The ``uid`` of the profile that sends the event. A profile with this uid must exist."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/loiteringguard/control.cgi"

INFO = ApiInfo(
    id="loitering-guard",
    name="Loitering guard",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 1), ApiVersion(1, 2), ApiVersion(1, 3)),
    discovery=(AcapDiscovery("LoiteringGuard"),),
    docs=("https://developer.axis.com/vapix/applications/loitering-guard/",),
    errors={
        1000: ErrorCode("Application error. The application failed to handle the request.", "internal"),
        2000: ErrorCode("Unsupported version. The major version number is not supported.", "unsupported"),
        2001: ErrorCode("Invalid format. The request does not follow the JSON schema.", "invalid_argument"),
        2002: ErrorCode(
            "Incoherent format. Parts of the request contradict each other (for example several profiles with the same uid).",
            "invalid_argument",
        ),
        2003: ErrorCode("Missing parameter. A mandatory parameter is missing.", "invalid_argument"),
        2004: ErrorCode("Invalid parameter. A parameter has an invalid value.", "invalid_argument"),
        8000: ErrorCode(
            "Unsupported product. The product is not supported by this version of the application.", "unsupported"
        ),
        9000: ErrorCode("Invalid license. The license file is invalid or missing.", "unavailable"),
        "1000-1999": ErrorCode(
            "Reserved for camera application (server) errors, for example a configuration that could not be read; see the server log. Restarting the camera may help.",
            "internal",
        ),
        "2000-2999": ErrorCode(
            "Reserved for client errors, for example a wrong format or an invalid parameter.", "invalid_argument"
        ),
        "9000-9999": ErrorCode("Reserved for license errors; upload a valid license file for the ACAP.", "unavailable"),
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
        errors={1000: ErrorCode("Application error. The application failed to return a configuration.", "internal")},
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
    )


# ---------------------------------------------------------------------------
# API classes


class LoiteringGuardApi(SyncApi):
    """Loitering guard (``loitering-guard``, version 1)."""

    INFO = INFO

    def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Get the current configuration of the ACAP. Access: admin."""
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
        """Replace the complete configuration of the ACAP.

        Uploads a complete configuration; a profile that is left out is removed. The application is not
        restarted, but ongoing events are set inactive when the configuration is applied, which stops
        ongoing recordings (for all cameras on multichannel products). The size perspective filter is
        disabled while the camera rotation differs from the configured rotation. Clients using apiVersion
        1.2 or lower leave the alarm overlay settings unchanged. The POST size is limited, so the request is
        sent minified.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_configuration, request, kwargs, request_options)

    def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Get the boundaries and default values of the ACAP. Access: admin."""
        return self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    def send_alarm_event(self, profile: int, *, request_options: RequestOptions | None = None) -> None:
        """Send a stateful alarm event for a profile, to test VMS integrations.

        Sends a stateful alarm event, in Axis and ONVIF format, for the profile. The event is active for a
        few seconds and the response returns immediately. The profile sends events regardless of its current
        state; on PTZ products a profile connected to another preset also sends them.

        Access: operator.
        """
        self._run(OPS.send_alarm_event, None, {"profile": profile}, request_options)


class AsyncLoiteringGuardApi(AsyncApi):
    """Loitering guard (``loitering-guard``, version 1)."""

    INFO = INFO

    async def get_configuration(self, *, request_options: RequestOptions | None = None) -> Configuration:
        """Get the current configuration of the ACAP. Access: admin."""
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
        """Replace the complete configuration of the ACAP.

        Uploads a complete configuration; a profile that is left out is removed. The application is not
        restarted, but ongoing events are set inactive when the configuration is applied, which stops
        ongoing recordings (for all cameras on multichannel products). The size perspective filter is
        disabled while the camera rotation differs from the configured rotation. Clients using apiVersion
        1.2 or lower leave the alarm overlay settings unchanged. The POST size is limited, so the request is
        sent minified.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_configuration, request, kwargs, request_options)

    async def get_configuration_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> ConfigurationCapabilities:
        """Get the boundaries and default values of the ACAP. Access: admin."""
        return await self._run(OPS.get_configuration_capabilities, None, {}, request_options)

    async def send_alarm_event(self, profile: int, *, request_options: RequestOptions | None = None) -> None:
        """Send a stateful alarm event for a profile, to test VMS integrations.

        Sends a stateful alarm event, in Axis and ONVIF format, for the profile. The event is active for a
        few seconds and the response returns immediately. The profile sends events regardless of its current
        state; on PTZ products a profile connected to another preset also sends them.

        Access: operator.
        """
        await self._run(OPS.send_alarm_event, None, {"profile": profile}, request_options)
