# GENERATED from specs/apis/device-configuration/directional-audio-detection-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure directional audio detection, PTZ calibration, PTZ control and fisheye overlays, and read detected audio events.

Docs: https://developer.axis.com/vapix/device-configuration/directional-audio-detection-api/
"""

from __future__ import annotations

from typing import Annotated, Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DetectionThreshold = Annotated[float, Field(ge=1, le=20)]


class AudioEventData(Model):
    """Audio event data"""

    id: int
    """Event ID"""
    level: float
    """The audio level when triggered (dB)"""
    pan: float
    """Pan angle to audio source that triggered"""
    phi: float
    """Phi angle, the polar angle, measured from the positive z-axis"""
    phi_valid: bool = Field(validation_alias="phiValid", serialization_alias="phiValid")
    """Phi angle valid, not all audio detection generates a phi value"""
    theta: float
    """Theta angle, the azimuthal angle, measured in the xy-plane from the positive x-axis"""
    threshold: DetectionThreshold
    """Audio detection threshold value (dB)"""
    tilt: int
    """Tilt angle to audio source that triggered"""
    timestamp: int
    """The number of seconds since January 1, 1970 UTC."""


DefaultTilt = Annotated[float, Field(ge=-90, le=0)]
DwellTime = Annotated[int, Field(ge=1, le=600)]
PanOffset = Annotated[float, Field(ge=-180, le=180)]
ViewareaTimeout = Annotated[int, Field(ge=1, le=7200)]


class Adm(Model):
    """Entity for Audio Detection Multiview"""

    viewarea_timeout: ViewareaTimeout | None = Field(
        default=None, validation_alias="viewareaTimeout", serialization_alias="viewareaTimeout"
    )
    """Time (s) before the contents of a view area is considered obsolete"""


class BaseSettings(Model):
    """Entity for base settings for Directional Audio Detection"""

    detection_threshold: DetectionThreshold | None = Field(
        default=None, validation_alias="detectionThreshold", serialization_alias="detectionThreshold"
    )
    """The threshold (dB) for detecting a sound"""
    dwell_time: DwellTime | None = Field(default=None, validation_alias="dwellTime", serialization_alias="dwellTime")
    """The minimum time (s) before detecting a new sound"""
    enabled: bool | None = None
    """Turn on or off the Directional Audio Detection"""
    wind_detect: bool | None = Field(default=None, validation_alias="windDetect", serialization_alias="windDetect")
    """Detects if an audio event is wind or not. Should be on outdoors, and off indoors."""


class FisheyeOverlay(Model):
    """Entity for `FisheyeOverlay`"""

    enabled: bool | None = None
    """Turn fisheye overlays on or off"""


class DefaultTiltCalibration(Model):
    """Default tilt value to use when Directional Audio Detection event doesn't contain tilt value"""

    value: DefaultTilt | None = None
    """The default tilt value"""


class PanOffsetCalibration(Model):
    """Pan offset to PTZ camera"""

    manually_calibrated: bool | None = Field(
        default=None, validation_alias="manuallyCalibrated", serialization_alias="manuallyCalibrated"
    )
    """If panOffset has been manually calibrated"""
    pre_calibrated: bool | None = Field(
        default=None, validation_alias="preCalibrated", serialization_alias="preCalibrated"
    )
    """If panOffset is pre-calibrated from factory default"""
    value: PanOffset | None = None
    """The pan offset value"""


class Calibration(Model):
    """Calibration of ptz control"""

    default_tilt: DefaultTiltCalibration | None = Field(
        default=None, validation_alias="defaultTilt", serialization_alias="defaultTilt"
    )
    pan_offset: PanOffsetCalibration | None = Field(
        default=None, validation_alias="panOffset", serialization_alias="panOffset"
    )


class PtzControl(Model):
    """Entity for ptz control"""

    enabled: bool | None = None
    """Turn ptz control on or off"""
    use_visual_objects: bool | None = Field(
        default=None, validation_alias="useVisualObjects", serialization_alias="useVisualObjects"
    )
    """Turn use visual objects on or off"""
    calibration: Calibration | None = None


class DirectionalAudioDetection(Model):
    """The whole API tree."""

    audio_events: list[AudioEventData] | None = Field(
        default=None, validation_alias="audioEvents", serialization_alias="audioEvents"
    )
    """Up to 1000 of the latest detected audio events."""
    adm_supported: bool | None = None
    """Whether the device supports Audio Detection Multiview."""
    fisheye_overlay_supported: bool | None = Field(
        default=None, validation_alias="fisheyeOverlay_supported", serialization_alias="fisheyeOverlay_supported"
    )
    """Whether the device supports fisheye overlays."""
    ptz_control_supported: bool | None = Field(
        default=None, validation_alias="ptzControl_supported", serialization_alias="ptzControl_supported"
    )
    """Whether the device supports PTZ control."""
    adm: Adm | None = None
    base_settings: BaseSettings | None = Field(
        default=None, validation_alias="baseSettings", serialization_alias="baseSettings"
    )
    fisheye_overlay: FisheyeOverlay | None = Field(
        default=None, validation_alias="fisheyeOverlay", serialization_alias="fisheyeOverlay"
    )
    ptz_control: PtzControl | None = Field(
        default=None, validation_alias="ptzControl", serialization_alias="ptzControl"
    )


class UpdateAllRequest(Model):
    """Arguments of ``update_all``. Only the given settings are changed."""

    adm: Adm | None = None
    base_settings: BaseSettings | None = Field(
        default=None, validation_alias="baseSettings", serialization_alias="baseSettings"
    )
    fisheye_overlay: FisheyeOverlay | None = Field(
        default=None, validation_alias="fisheyeOverlay", serialization_alias="fisheyeOverlay"
    )
    ptz_control: PtzControl | None = Field(
        default=None, validation_alias="ptzControl", serialization_alias="ptzControl"
    )


class SetAdmViewareaTimeoutRequest(Model):
    viewarea_timeout: ViewareaTimeout = Field(validation_alias="viewareaTimeout", serialization_alias="viewareaTimeout")
    """Time (s) before the contents of a view area is considered obsolete"""


class SetBaseSettingsDetectionThresholdRequest(Model):
    detection_threshold: DetectionThreshold = Field(
        validation_alias="detectionThreshold", serialization_alias="detectionThreshold"
    )
    """The threshold (dB) for detecting a sound"""


class SetBaseSettingsDwellTimeRequest(Model):
    dwell_time: DwellTime = Field(validation_alias="dwellTime", serialization_alias="dwellTime")
    """The minimum time (s) before detecting a new sound"""


class SetBaseSettingsEnabledRequest(Model):
    enabled: bool
    """Turn on or off the Directional Audio Detection"""


class SetBaseSettingsWindDetectRequest(Model):
    wind_detect: bool = Field(validation_alias="windDetect", serialization_alias="windDetect")
    """Detects if an audio event is wind or not. Should be on outdoors, and off indoors."""


class SetFisheyeOverlayEnabledRequest(Model):
    enabled: bool
    """Turn fisheye overlays on or off"""


class SetPtzControlEnabledRequest(Model):
    enabled: bool
    """Turn ptz control on or off"""


class SetPtzControlUseVisualObjectsRequest(Model):
    use_visual_objects: bool = Field(validation_alias="useVisualObjects", serialization_alias="useVisualObjects")
    """Turn use visual objects on or off"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/directional-audio-detection/v2"

INFO = ApiInfo(
    id="directional-audio-detection-config",
    name="Directional audio detection API",
    family=Family.DCA,
    discovery=(DcaDiscovery("directional-audio-detection", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/directional-audio-detection-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=DirectionalAudioDetection, access="admin", effect="read"
    )
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_audio_events = Operation(
        INFO,
        "list_audio_events",
        DcaBinding("GET", f"{ROOT}/audioEvents"),
        result=list[AudioEventData],
        access="admin",
        effect="read",
    )
    get_adm_supported = Operation(
        INFO,
        "get_adm_supported",
        DcaBinding("GET", f"{ROOT}/adm_supported"),
        result=bool,
        access="operator",
        effect="read",
    )
    get_fisheye_overlay_supported = Operation(
        INFO,
        "get_fisheye_overlay_supported",
        DcaBinding("GET", f"{ROOT}/fisheyeOverlay_supported"),
        result=bool,
        access="operator",
        effect="read",
    )
    get_ptz_control_supported = Operation(
        INFO,
        "get_ptz_control_supported",
        DcaBinding("GET", f"{ROOT}/ptzControl_supported"),
        result=bool,
        access="operator",
        effect="read",
    )
    get_adm = Operation(INFO, "get_adm", DcaBinding("GET", f"{ROOT}/adm"), result=Adm, access="admin", effect="read")
    set_adm_viewarea_timeout = Operation(
        INFO,
        "set_adm_viewarea_timeout",
        DcaBinding("PATCH", f"{ROOT}/adm/viewareaTimeout", body="value", body_field="viewareaTimeout"),
        params=SetAdmViewareaTimeoutRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_base_settings = Operation(
        INFO,
        "get_base_settings",
        DcaBinding("GET", f"{ROOT}/baseSettings"),
        result=BaseSettings,
        access="admin",
        effect="read",
    )
    set_base_settings_detection_threshold = Operation(
        INFO,
        "set_base_settings_detection_threshold",
        DcaBinding("PATCH", f"{ROOT}/baseSettings/detectionThreshold", body="value", body_field="detectionThreshold"),
        params=SetBaseSettingsDetectionThresholdRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_base_settings_dwell_time = Operation(
        INFO,
        "set_base_settings_dwell_time",
        DcaBinding("PATCH", f"{ROOT}/baseSettings/dwellTime", body="value", body_field="dwellTime"),
        params=SetBaseSettingsDwellTimeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_base_settings_enabled = Operation(
        INFO,
        "set_base_settings_enabled",
        DcaBinding("PATCH", f"{ROOT}/baseSettings/enabled", body="value", body_field="enabled"),
        params=SetBaseSettingsEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_base_settings_wind_detect = Operation(
        INFO,
        "set_base_settings_wind_detect",
        DcaBinding("PATCH", f"{ROOT}/baseSettings/windDetect", body="value", body_field="windDetect"),
        params=SetBaseSettingsWindDetectRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    test_event = Operation(
        INFO,
        "test_event",
        DcaBinding("POST", f"{ROOT}/baseSettings/testEvent", body="object"),
        access="admin",
        effect="action",
    )
    get_fisheye_overlay = Operation(
        INFO,
        "get_fisheye_overlay",
        DcaBinding("GET", f"{ROOT}/fisheyeOverlay"),
        result=FisheyeOverlay,
        access="admin",
        effect="read",
    )
    set_fisheye_overlay_enabled = Operation(
        INFO,
        "set_fisheye_overlay_enabled",
        DcaBinding("PATCH", f"{ROOT}/fisheyeOverlay/enabled", body="value", body_field="enabled"),
        params=SetFisheyeOverlayEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_ptz_control = Operation(
        INFO,
        "get_ptz_control",
        DcaBinding("GET", f"{ROOT}/ptzControl"),
        result=PtzControl,
        access="admin",
        effect="read",
    )
    set_ptz_control_enabled = Operation(
        INFO,
        "set_ptz_control_enabled",
        DcaBinding("PATCH", f"{ROOT}/ptzControl/enabled", body="value", body_field="enabled"),
        params=SetPtzControlEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_ptz_control_use_visual_objects = Operation(
        INFO,
        "set_ptz_control_use_visual_objects",
        DcaBinding("PATCH", f"{ROOT}/ptzControl/useVisualObjects", body="value", body_field="useVisualObjects"),
        params=SetPtzControlUseVisualObjectsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_calibration = Operation(
        INFO,
        "get_calibration",
        DcaBinding("GET", f"{ROOT}/ptzControl/calibration"),
        result=Calibration,
        access="admin",
        effect="read",
    )
    get_default_tilt = Operation(
        INFO,
        "get_default_tilt",
        DcaBinding("GET", f"{ROOT}/ptzControl/calibration/defaultTilt"),
        result=DefaultTiltCalibration,
        access="admin",
        effect="read",
    )
    save_default_tilt = Operation(
        INFO,
        "save_default_tilt",
        DcaBinding("POST", f"{ROOT}/ptzControl/calibration/defaultTilt/save", body="object"),
        access="admin",
        effect="action",
    )
    get_pan_offset = Operation(
        INFO,
        "get_pan_offset",
        DcaBinding("GET", f"{ROOT}/ptzControl/calibration/panOffset"),
        result=PanOffsetCalibration,
        access="admin",
        effect="read",
    )
    reset_pan_offset = Operation(
        INFO,
        "reset_pan_offset",
        DcaBinding("POST", f"{ROOT}/ptzControl/calibration/panOffset/reset", body="object"),
        access="admin",
        effect="action",
    )
    save_pan_offset = Operation(
        INFO,
        "save_pan_offset",
        DcaBinding("POST", f"{ROOT}/ptzControl/calibration/panOffset/save", body="object"),
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class DirectionalAudioDetectionApi(SyncApi):
    """Directional audio detection API (``directional-audio-detection-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> DirectionalAudioDetection:
        """All settings of the Directional audio detection API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    @overload
    def update_all(self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_all(
        self,
        /,
        *,
        adm: Adm | MISSING = MISSING,
        base_settings: BaseSettings | MISSING = MISSING,
        fisheye_overlay: FisheyeOverlay | MISSING = MISSING,
        ptz_control: PtzControl | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the Directional audio detection settings.

        Only the given settings are changed. Read-only settings such as the calibration are never sent.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_all, request, kwargs, request_options)

    def list_audio_events(self, *, request_options: RequestOptions | None = None) -> list[AudioEventData]:
        """Up to 1000 of the latest detected audio events. Access: admin."""
        return self._run(OPS.list_audio_events, None, {}, request_options)

    def get_adm_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports Audio Detection Multiview. Access: operator."""
        return self._run(OPS.get_adm_supported, None, {}, request_options)

    def get_fisheye_overlay_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports fisheye overlays. Access: operator."""
        return self._run(OPS.get_fisheye_overlay_supported, None, {}, request_options)

    def get_ptz_control_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports PTZ control. Access: operator."""
        return self._run(OPS.get_ptz_control_supported, None, {}, request_options)

    def get_adm(self, *, request_options: RequestOptions | None = None) -> Adm:
        """Get the Audio Detection Multiview settings. Access: admin."""
        return self._run(OPS.get_adm, None, {}, request_options)

    def set_adm_viewarea_timeout(
        self, viewarea_timeout: ViewareaTimeout, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the time before the contents of a view area is considered obsolete.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_adm_viewarea_timeout, None, {"viewarea_timeout": viewarea_timeout}, request_options)

    def get_base_settings(self, *, request_options: RequestOptions | None = None) -> BaseSettings:
        """Get the base settings. Access: admin."""
        return self._run(OPS.get_base_settings, None, {}, request_options)

    def set_base_settings_detection_threshold(
        self, detection_threshold: DetectionThreshold, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the threshold (dB) for detecting a sound.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_base_settings_detection_threshold,
            None,
            {"detection_threshold": detection_threshold},
            request_options,
        )

    def set_base_settings_dwell_time(
        self, dwell_time: DwellTime, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the minimum time (s) before detecting a new sound.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_base_settings_dwell_time, None, {"dwell_time": dwell_time}, request_options)

    def set_base_settings_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn directional audio detection on or off.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_base_settings_enabled, None, {"enabled": enabled}, request_options)

    def set_base_settings_wind_detect(
        self, wind_detect: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Turn wind detection on or off. Changes only the fields given. Access: admin."""
        self._run(OPS.set_base_settings_wind_detect, None, {"wind_detect": wind_detect}, request_options)

    def test_event(self, *, request_options: RequestOptions | None = None) -> None:
        """Generate a test event. Access: admin."""
        self._run(OPS.test_event, None, {}, request_options)

    def get_fisheye_overlay(self, *, request_options: RequestOptions | None = None) -> FisheyeOverlay:
        """Get the fisheye overlay settings. Access: admin."""
        return self._run(OPS.get_fisheye_overlay, None, {}, request_options)

    def set_fisheye_overlay_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn fisheye overlays on or off. Changes only the fields given. Access: operator."""
        self._run(OPS.set_fisheye_overlay_enabled, None, {"enabled": enabled}, request_options)

    def get_ptz_control(self, *, request_options: RequestOptions | None = None) -> PtzControl:
        """Get the PTZ control settings, including the calibration. Access: admin."""
        return self._run(OPS.get_ptz_control, None, {}, request_options)

    def set_ptz_control_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn PTZ control on or off. Changes only the fields given. Access: operator."""
        self._run(OPS.set_ptz_control_enabled, None, {"enabled": enabled}, request_options)

    def set_ptz_control_use_visual_objects(
        self, use_visual_objects: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Turn the use of visual objects on or off. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_ptz_control_use_visual_objects, None, {"use_visual_objects": use_visual_objects}, request_options
        )

    def get_calibration(self, *, request_options: RequestOptions | None = None) -> Calibration:
        """Get the PTZ calibration settings. Access: admin."""
        return self._run(OPS.get_calibration, None, {}, request_options)

    def get_default_tilt(self, *, request_options: RequestOptions | None = None) -> DefaultTiltCalibration:
        """Get the default tilt calibration. Access: admin."""
        return self._run(OPS.get_default_tilt, None, {}, request_options)

    def save_default_tilt(self, *, request_options: RequestOptions | None = None) -> None:
        """Save the current tilt of the PTZ camera as the default tilt. Access: admin."""
        self._run(OPS.save_default_tilt, None, {}, request_options)

    def get_pan_offset(self, *, request_options: RequestOptions | None = None) -> PanOffsetCalibration:
        """Get the pan offset calibration. Access: admin."""
        return self._run(OPS.get_pan_offset, None, {}, request_options)

    def reset_pan_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the pan offset to the pre-calibrated value, if a manual calibration has been done.

        Has no effect when preCalibrated is false.

        Access: admin.
        """
        self._run(OPS.reset_pan_offset, None, {}, request_options)

    def save_pan_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Save the current pan of the PTZ camera as the pan offset. Access: admin."""
        self._run(OPS.save_pan_offset, None, {}, request_options)


class AsyncDirectionalAudioDetectionApi(AsyncApi):
    """Directional audio detection API (``directional-audio-detection-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> DirectionalAudioDetection:
        """All settings of the Directional audio detection API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    @overload
    async def update_all(
        self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_all(
        self,
        /,
        *,
        adm: Adm | MISSING = MISSING,
        base_settings: BaseSettings | MISSING = MISSING,
        fisheye_overlay: FisheyeOverlay | MISSING = MISSING,
        ptz_control: PtzControl | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the Directional audio detection settings.

        Only the given settings are changed. Read-only settings such as the calibration are never sent.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_all, request, kwargs, request_options)

    async def list_audio_events(self, *, request_options: RequestOptions | None = None) -> list[AudioEventData]:
        """Up to 1000 of the latest detected audio events. Access: admin."""
        return await self._run(OPS.list_audio_events, None, {}, request_options)

    async def get_adm_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports Audio Detection Multiview. Access: operator."""
        return await self._run(OPS.get_adm_supported, None, {}, request_options)

    async def get_fisheye_overlay_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports fisheye overlays. Access: operator."""
        return await self._run(OPS.get_fisheye_overlay_supported, None, {}, request_options)

    async def get_ptz_control_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports PTZ control. Access: operator."""
        return await self._run(OPS.get_ptz_control_supported, None, {}, request_options)

    async def get_adm(self, *, request_options: RequestOptions | None = None) -> Adm:
        """Get the Audio Detection Multiview settings. Access: admin."""
        return await self._run(OPS.get_adm, None, {}, request_options)

    async def set_adm_viewarea_timeout(
        self, viewarea_timeout: ViewareaTimeout, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the time before the contents of a view area is considered obsolete.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_adm_viewarea_timeout, None, {"viewarea_timeout": viewarea_timeout}, request_options)

    async def get_base_settings(self, *, request_options: RequestOptions | None = None) -> BaseSettings:
        """Get the base settings. Access: admin."""
        return await self._run(OPS.get_base_settings, None, {}, request_options)

    async def set_base_settings_detection_threshold(
        self, detection_threshold: DetectionThreshold, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the threshold (dB) for detecting a sound.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_base_settings_detection_threshold,
            None,
            {"detection_threshold": detection_threshold},
            request_options,
        )

    async def set_base_settings_dwell_time(
        self, dwell_time: DwellTime, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the minimum time (s) before detecting a new sound.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_base_settings_dwell_time, None, {"dwell_time": dwell_time}, request_options)

    async def set_base_settings_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn directional audio detection on or off.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_base_settings_enabled, None, {"enabled": enabled}, request_options)

    async def set_base_settings_wind_detect(
        self, wind_detect: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Turn wind detection on or off. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_base_settings_wind_detect, None, {"wind_detect": wind_detect}, request_options)

    async def test_event(self, *, request_options: RequestOptions | None = None) -> None:
        """Generate a test event. Access: admin."""
        await self._run(OPS.test_event, None, {}, request_options)

    async def get_fisheye_overlay(self, *, request_options: RequestOptions | None = None) -> FisheyeOverlay:
        """Get the fisheye overlay settings. Access: admin."""
        return await self._run(OPS.get_fisheye_overlay, None, {}, request_options)

    async def set_fisheye_overlay_enabled(
        self, enabled: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Turn fisheye overlays on or off. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_fisheye_overlay_enabled, None, {"enabled": enabled}, request_options)

    async def get_ptz_control(self, *, request_options: RequestOptions | None = None) -> PtzControl:
        """Get the PTZ control settings, including the calibration. Access: admin."""
        return await self._run(OPS.get_ptz_control, None, {}, request_options)

    async def set_ptz_control_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn PTZ control on or off. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_ptz_control_enabled, None, {"enabled": enabled}, request_options)

    async def set_ptz_control_use_visual_objects(
        self, use_visual_objects: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Turn the use of visual objects on or off. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_ptz_control_use_visual_objects, None, {"use_visual_objects": use_visual_objects}, request_options
        )

    async def get_calibration(self, *, request_options: RequestOptions | None = None) -> Calibration:
        """Get the PTZ calibration settings. Access: admin."""
        return await self._run(OPS.get_calibration, None, {}, request_options)

    async def get_default_tilt(self, *, request_options: RequestOptions | None = None) -> DefaultTiltCalibration:
        """Get the default tilt calibration. Access: admin."""
        return await self._run(OPS.get_default_tilt, None, {}, request_options)

    async def save_default_tilt(self, *, request_options: RequestOptions | None = None) -> None:
        """Save the current tilt of the PTZ camera as the default tilt. Access: admin."""
        await self._run(OPS.save_default_tilt, None, {}, request_options)

    async def get_pan_offset(self, *, request_options: RequestOptions | None = None) -> PanOffsetCalibration:
        """Get the pan offset calibration. Access: admin."""
        return await self._run(OPS.get_pan_offset, None, {}, request_options)

    async def reset_pan_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the pan offset to the pre-calibrated value, if a manual calibration has been done.

        Has no effect when preCalibrated is false.

        Access: admin.
        """
        await self._run(OPS.reset_pan_offset, None, {}, request_options)

    async def save_pan_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Save the current pan of the PTZ camera as the pan offset. Access: admin."""
        await self._run(OPS.save_pan_offset, None, {}, request_options)
