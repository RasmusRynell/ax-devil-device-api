# GENERATED from specs/apis/device-configuration/speaker-display-settings-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The VAPIX® Speaker display settings API enables configurations for the appearance and availability of the display clock, display brightness and localization.

Docs: https://developer.axis.com/vapix/device-configuration/speaker-display-settings/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

BrightnessRange = Annotated[int, Field(ge=1, le=7)]
ColorFormat = Annotated[str, Field(pattern="^#[0-9a-fA-F]{6}$")]
DateLanguage = Literal["ar", "de", "en", "es", "fr", "global", "it", "ja", "ko", "th", "tr", "zh", "zh-TW"]
PowerSaveModes = Literal["alwaysOn", "alwaysOff", "presenceDetection", "schedule"]
PowerSaveTimerMinutes = Annotated[int, Field(ge=1, le=60)]


class PresenceDetection(Model):
    """Parameters belonging to the power save mode `"presenceDetection"`."""

    power_save_timer_minutes: PowerSaveTimerMinutes | None = Field(
        default=None, validation_alias="powerSaveTimerMinutes", serialization_alias="powerSaveTimerMinutes"
    )
    """Time without presence before the display turns off."""


ScheduleIdStr = Annotated[str, Field(max_length=100)]


class Schedule(Model):
    """Parameters belonging to the power save mode `"schedule"`."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"schedule_id"})
    invert: bool | None = None
    """When enabled, the schedule is inverted. The times it's normally active become inactive and the times it's normally inactive become active."""
    schedule_id: ScheduleIdStr | None = Field(
        default=None, validation_alias="scheduleId", serialization_alias="scheduleId"
    )
    """The identification string of a configured schedule."""


class Appearance(Model):
    """Speaker Display Appearance Entity."""

    background_color: ColorFormat = Field(validation_alias="backgroundColor", serialization_alias="backgroundColor")
    """Color of the background."""
    font_color: ColorFormat = Field(validation_alias="fontColor", serialization_alias="fontColor")
    """Color of the text when idle."""
    language: DateLanguage
    """Localization of the clock shown when idle."""
    show_date: bool = Field(validation_alias="showDate", serialization_alias="showDate")
    """If enabled, the current date will be displayed."""
    show_seconds: bool = Field(validation_alias="showSeconds", serialization_alias="showSeconds")
    """If enabled, seconds will be displayed."""
    use24_hour_clock: bool = Field(validation_alias="use24HourClock", serialization_alias="use24HourClock")
    """If enabled, the clock will display the 24-hour format; otherwise, it will display the 12-hour format with AM/PM."""


class Brightness(Model):
    """Speaker Display Brightness Entity."""

    adaptive_brightness: bool = Field(validation_alias="adaptiveBrightness", serialization_alias="adaptiveBrightness")
    """Adaptive display brightness enabled or disabled. If enabled, display brightness will be automatically adjusted to match ambient luminance. Adaptive display brightness is paused whenever there is an active notification."""
    manual_level: BrightnessRange = Field(validation_alias="manualLevel", serialization_alias="manualLevel")
    """Manual display brightness set by user. Applicable only if adaptive brightness is disabled."""
    max_adaptive_level: BrightnessRange = Field(
        validation_alias="maxAdaptiveLevel", serialization_alias="maxAdaptiveLevel"
    )
    """Maximum display brightness for adaptive mode."""
    min_adaptive_level: BrightnessRange = Field(
        validation_alias="minAdaptiveLevel", serialization_alias="minAdaptiveLevel"
    )
    """Minimum display brightness for adaptive mode."""


class PowerSave(Model):
    """Speaker Display Power Save Entity."""

    mode: PowerSaveModes
    """Power saving mode can be `alwaysOn`, `alwaysOff`, `schedule`, or `presenceDetection`."""
    presence_detection: PresenceDetection = Field(
        validation_alias="presenceDetection", serialization_alias="presenceDetection"
    )
    """Parameters belonging to the power save mode `presenceDetection`."""
    schedule: Schedule
    """Parameters belonging to the power save mode `schedule`."""


class SpeakerDisplaySettings(Model):
    """The whole API tree."""

    appearance: Appearance
    brightness: Brightness
    power_save: PowerSave = Field(validation_alias="powerSave", serialization_alias="powerSave")


class UpdateAppearanceRequest(Model):
    """Arguments of ``update_appearance``."""

    background_color: ColorFormat | None = Field(
        default=None, validation_alias="backgroundColor", serialization_alias="backgroundColor"
    )
    """Color of the background."""
    font_color: ColorFormat | None = Field(default=None, validation_alias="fontColor", serialization_alias="fontColor")
    """Color of the text when idle."""
    language: DateLanguage | None = None
    """Localization of the clock shown when idle."""
    show_date: bool | None = Field(default=None, validation_alias="showDate", serialization_alias="showDate")
    """If enabled, the current date will be displayed."""
    show_seconds: bool | None = Field(default=None, validation_alias="showSeconds", serialization_alias="showSeconds")
    """If enabled, seconds will be displayed."""
    use24_hour_clock: bool | None = Field(
        default=None, validation_alias="use24HourClock", serialization_alias="use24HourClock"
    )
    """If enabled, the clock will display the 24-hour format; otherwise, it will display the 12-hour format with AM/PM."""

    @classmethod
    def from_current(cls, appearance: Appearance) -> UpdateAppearanceRequest:
        """A request that rewrites ``appearance`` unchanged: copy it, edit fields, send it back."""
        data = appearance.request_data()
        return cls.from_response_data(data)


class UpdateBrightnessRequest(Model):
    """Arguments of ``update_brightness``."""

    adaptive_brightness: bool | None = Field(
        default=None, validation_alias="adaptiveBrightness", serialization_alias="adaptiveBrightness"
    )
    """Adaptive display brightness enabled or disabled. If enabled, display brightness will be automatically adjusted to match ambient luminance. Adaptive display brightness is paused whenever there is an active notification."""
    manual_level: BrightnessRange | None = Field(
        default=None, validation_alias="manualLevel", serialization_alias="manualLevel"
    )
    """Manual display brightness set by user. Applicable only if adaptive brightness is disabled."""
    max_adaptive_level: BrightnessRange | None = Field(
        default=None, validation_alias="maxAdaptiveLevel", serialization_alias="maxAdaptiveLevel"
    )
    """Maximum display brightness for adaptive mode."""
    min_adaptive_level: BrightnessRange | None = Field(
        default=None, validation_alias="minAdaptiveLevel", serialization_alias="minAdaptiveLevel"
    )
    """Minimum display brightness for adaptive mode."""

    @classmethod
    def from_current(cls, brightness: Brightness) -> UpdateBrightnessRequest:
        """A request that rewrites ``brightness`` unchanged: copy it, edit fields, send it back."""
        data = brightness.request_data()
        return cls.from_response_data(data)


class UpdatePowerSaveRequest(Model):
    """Arguments of ``update_power_save``."""

    mode: PowerSaveModes | None = None
    """Power saving mode can be `alwaysOn`, `alwaysOff`, `schedule`, or `presenceDetection`."""
    presence_detection: PresenceDetection | None = Field(
        default=None, validation_alias="presenceDetection", serialization_alias="presenceDetection"
    )
    """Parameters belonging to the power save mode `presenceDetection`."""
    schedule: Schedule | None = None
    """Parameters belonging to the power save mode `schedule`."""

    @classmethod
    def from_current(cls, save: PowerSave) -> UpdatePowerSaveRequest:
        """A request that rewrites ``save`` unchanged: copy it, edit fields, send it back."""
        data = save.request_data()
        return cls.from_response_data(data)


class UpdateAllRequest(Model):
    """Arguments of ``update_all``. Only the given entities and fields change."""

    appearance: UpdateAppearanceRequest | None = None
    brightness: UpdateBrightnessRequest | None = None
    power_save: UpdatePowerSaveRequest | None = Field(
        default=None, validation_alias="powerSave", serialization_alias="powerSave"
    )


class SetAppearanceBackgroundColorRequest(Model):
    background_color: ColorFormat = Field(validation_alias="backgroundColor", serialization_alias="backgroundColor")
    """Color of the background."""


class SetAppearanceFontColorRequest(Model):
    font_color: ColorFormat = Field(validation_alias="fontColor", serialization_alias="fontColor")
    """Color of the text when idle."""


class SetAppearanceLanguageRequest(Model):
    language: DateLanguage
    """Localization of the clock shown when idle."""


class SetAppearanceShowDateRequest(Model):
    show_date: bool = Field(validation_alias="showDate", serialization_alias="showDate")
    """If enabled, the current date will be displayed."""


class SetAppearanceShowSecondsRequest(Model):
    show_seconds: bool = Field(validation_alias="showSeconds", serialization_alias="showSeconds")
    """If enabled, seconds will be displayed."""


class SetAppearanceUse24HourClockRequest(Model):
    use24_hour_clock: bool = Field(validation_alias="use24HourClock", serialization_alias="use24HourClock")
    """If enabled, the clock will display the 24-hour format; otherwise, it will display the 12-hour format with AM/PM."""


class SetBrightnessAdaptiveBrightnessRequest(Model):
    adaptive_brightness: bool = Field(validation_alias="adaptiveBrightness", serialization_alias="adaptiveBrightness")
    """Adaptive display brightness enabled or disabled. If enabled, display brightness will be automatically adjusted to match ambient luminance. Adaptive display brightness is paused whenever there is an active notification."""


class SetBrightnessManualLevelRequest(Model):
    manual_level: BrightnessRange = Field(validation_alias="manualLevel", serialization_alias="manualLevel")
    """Manual display brightness set by user. Applicable only if adaptive brightness is disabled."""


class SetBrightnessMaxAdaptiveLevelRequest(Model):
    max_adaptive_level: BrightnessRange = Field(
        validation_alias="maxAdaptiveLevel", serialization_alias="maxAdaptiveLevel"
    )
    """Maximum display brightness for adaptive mode."""


class SetBrightnessMinAdaptiveLevelRequest(Model):
    min_adaptive_level: BrightnessRange = Field(
        validation_alias="minAdaptiveLevel", serialization_alias="minAdaptiveLevel"
    )
    """Minimum display brightness for adaptive mode."""


class SetPowerSaveModeRequest(Model):
    mode: PowerSaveModes
    """Power saving mode can be `alwaysOn`, `alwaysOff`, `schedule`, or `presenceDetection`."""


class SetPowerSavePresenceDetectionRequest(Model):
    presence_detection: PresenceDetection = Field(
        validation_alias="presenceDetection", serialization_alias="presenceDetection"
    )
    """Parameters belonging to the power save mode `presenceDetection`."""


class SetPowerSaveScheduleRequest(Model):
    schedule: Schedule
    """Parameters belonging to the power save mode `schedule`."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/speaker-display-settings/v1"

INFO = ApiInfo(
    id="speaker-display-settings-config",
    name="Speaker display settings",
    family=Family.DCA,
    discovery=(DcaDiscovery("speaker-display-settings", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/speaker-display-settings/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=SpeakerDisplaySettings, access="admin", effect="read"
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
    get_appearance = Operation(
        INFO,
        "get_appearance",
        DcaBinding("GET", f"{ROOT}/appearance"),
        result=Appearance,
        access="admin",
        effect="read",
    )
    update_appearance = Operation(
        INFO,
        "update_appearance",
        DcaBinding("PATCH", f"{ROOT}/appearance", body="object"),
        params=UpdateAppearanceRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_appearance_background_color = Operation(
        INFO,
        "set_appearance_background_color",
        DcaBinding("PATCH", f"{ROOT}/appearance/backgroundColor", body="value", body_field="backgroundColor"),
        params=SetAppearanceBackgroundColorRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_appearance_font_color = Operation(
        INFO,
        "set_appearance_font_color",
        DcaBinding("PATCH", f"{ROOT}/appearance/fontColor", body="value", body_field="fontColor"),
        params=SetAppearanceFontColorRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_appearance_language = Operation(
        INFO,
        "set_appearance_language",
        DcaBinding("PATCH", f"{ROOT}/appearance/language", body="value", body_field="language"),
        params=SetAppearanceLanguageRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_appearance_show_date = Operation(
        INFO,
        "set_appearance_show_date",
        DcaBinding("PATCH", f"{ROOT}/appearance/showDate", body="value", body_field="showDate"),
        params=SetAppearanceShowDateRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_appearance_show_seconds = Operation(
        INFO,
        "set_appearance_show_seconds",
        DcaBinding("PATCH", f"{ROOT}/appearance/showSeconds", body="value", body_field="showSeconds"),
        params=SetAppearanceShowSecondsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_appearance_use24_hour_clock = Operation(
        INFO,
        "set_appearance_use24_hour_clock",
        DcaBinding("PATCH", f"{ROOT}/appearance/use24HourClock", body="value", body_field="use24HourClock"),
        params=SetAppearanceUse24HourClockRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_brightness = Operation(
        INFO,
        "get_brightness",
        DcaBinding("GET", f"{ROOT}/brightness"),
        result=Brightness,
        access="admin",
        effect="read",
    )
    update_brightness = Operation(
        INFO,
        "update_brightness",
        DcaBinding("PATCH", f"{ROOT}/brightness", body="object"),
        params=UpdateBrightnessRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brightness_adaptive_brightness = Operation(
        INFO,
        "set_brightness_adaptive_brightness",
        DcaBinding("PATCH", f"{ROOT}/brightness/adaptiveBrightness", body="value", body_field="adaptiveBrightness"),
        params=SetBrightnessAdaptiveBrightnessRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brightness_manual_level = Operation(
        INFO,
        "set_brightness_manual_level",
        DcaBinding("PATCH", f"{ROOT}/brightness/manualLevel", body="value", body_field="manualLevel"),
        params=SetBrightnessManualLevelRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brightness_max_adaptive_level = Operation(
        INFO,
        "set_brightness_max_adaptive_level",
        DcaBinding("PATCH", f"{ROOT}/brightness/maxAdaptiveLevel", body="value", body_field="maxAdaptiveLevel"),
        params=SetBrightnessMaxAdaptiveLevelRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brightness_min_adaptive_level = Operation(
        INFO,
        "set_brightness_min_adaptive_level",
        DcaBinding("PATCH", f"{ROOT}/brightness/minAdaptiveLevel", body="value", body_field="minAdaptiveLevel"),
        params=SetBrightnessMinAdaptiveLevelRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_power_save = Operation(
        INFO, "get_power_save", DcaBinding("GET", f"{ROOT}/powerSave"), result=PowerSave, access="admin", effect="read"
    )
    update_power_save = Operation(
        INFO,
        "update_power_save",
        DcaBinding("PATCH", f"{ROOT}/powerSave", body="object"),
        params=UpdatePowerSaveRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_power_save_mode = Operation(
        INFO,
        "set_power_save_mode",
        DcaBinding("PATCH", f"{ROOT}/powerSave/mode", body="value", body_field="mode"),
        params=SetPowerSaveModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_power_save_presence_detection = Operation(
        INFO,
        "set_power_save_presence_detection",
        DcaBinding("PATCH", f"{ROOT}/powerSave/presenceDetection", body="value", body_field="presenceDetection"),
        params=SetPowerSavePresenceDetectionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_power_save_schedule = Operation(
        INFO,
        "set_power_save_schedule",
        DcaBinding("PATCH", f"{ROOT}/powerSave/schedule", body="value", body_field="schedule"),
        params=SetPowerSaveScheduleRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SpeakerDisplaySettingsApi(SyncApi):
    """Speaker display settings (``speaker-display-settings-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> SpeakerDisplaySettings:
        """All data of the Speaker display settings API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    @overload
    def update_all(self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_all(
        self,
        /,
        *,
        appearance: UpdateAppearanceRequest | MISSING = MISSING,
        brightness: UpdateBrightnessRequest | MISSING = MISSING,
        power_save: UpdatePowerSaveRequest | MISSING = MISSING,
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
        """Update appearance, brightness and power save settings in one call.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_all, request, kwargs, request_options)

    def get_appearance(self, *, request_options: RequestOptions | None = None) -> Appearance:
        """Get the appearance settings. Access: admin."""
        return self._run(OPS.get_appearance, None, {}, request_options)

    @overload
    def update_appearance(
        self, request: UpdateAppearanceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_appearance(
        self,
        /,
        *,
        background_color: ColorFormat | MISSING = MISSING,
        font_color: ColorFormat | MISSING = MISSING,
        language: DateLanguage | MISSING = MISSING,
        show_date: bool | MISSING = MISSING,
        show_seconds: bool | MISSING = MISSING,
        use24_hour_clock: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_appearance(
        self,
        request: UpdateAppearanceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the appearance settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_appearance, request, kwargs, request_options)

    def set_appearance_background_color(
        self, *, background_color: ColorFormat, request_options: RequestOptions | None = None
    ) -> None:
        """Set the background color of the appearance. Changes only the fields given. Access: admin."""
        self._run(OPS.set_appearance_background_color, None, {"background_color": background_color}, request_options)

    def set_appearance_font_color(
        self, *, font_color: ColorFormat, request_options: RequestOptions | None = None
    ) -> None:
        """Set the font color of the appearance. Changes only the fields given. Access: admin."""
        self._run(OPS.set_appearance_font_color, None, {"font_color": font_color}, request_options)

    def set_appearance_language(self, *, language: DateLanguage, request_options: RequestOptions | None = None) -> None:
        """Set the language of the appearance. Changes only the fields given. Access: admin."""
        self._run(OPS.set_appearance_language, None, {"language": language}, request_options)

    def set_appearance_show_date(self, *, show_date: bool, request_options: RequestOptions | None = None) -> None:
        """Set the show date of the appearance. Changes only the fields given. Access: admin."""
        self._run(OPS.set_appearance_show_date, None, {"show_date": show_date}, request_options)

    def set_appearance_show_seconds(self, *, show_seconds: bool, request_options: RequestOptions | None = None) -> None:
        """Set the show seconds of the appearance. Changes only the fields given. Access: admin."""
        self._run(OPS.set_appearance_show_seconds, None, {"show_seconds": show_seconds}, request_options)

    def set_appearance_use24_hour_clock(
        self, *, use24_hour_clock: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the use24 hour clock of the appearance. Changes only the fields given. Access: admin."""
        self._run(OPS.set_appearance_use24_hour_clock, None, {"use24_hour_clock": use24_hour_clock}, request_options)

    def get_brightness(self, *, request_options: RequestOptions | None = None) -> Brightness:
        """Get the brightness settings. Access: admin."""
        return self._run(OPS.get_brightness, None, {}, request_options)

    def update_brightness(
        self,
        *,
        adaptive_brightness: bool | MISSING = MISSING,
        manual_level: BrightnessRange | MISSING = MISSING,
        max_adaptive_level: BrightnessRange | MISSING = MISSING,
        min_adaptive_level: BrightnessRange | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the brightness settings. Changes only the fields given. Access: admin."""
        self._run(
            OPS.update_brightness,
            None,
            {
                "adaptive_brightness": adaptive_brightness,
                "manual_level": manual_level,
                "max_adaptive_level": max_adaptive_level,
                "min_adaptive_level": min_adaptive_level,
            },
            request_options,
        )

    def set_brightness_adaptive_brightness(
        self, *, adaptive_brightness: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the adaptive brightness of the brightness.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_brightness_adaptive_brightness, None, {"adaptive_brightness": adaptive_brightness}, request_options
        )

    def set_brightness_manual_level(
        self, *, manual_level: BrightnessRange, request_options: RequestOptions | None = None
    ) -> None:
        """Set the manual level of the brightness. Changes only the fields given. Access: admin."""
        self._run(OPS.set_brightness_manual_level, None, {"manual_level": manual_level}, request_options)

    def set_brightness_max_adaptive_level(
        self, *, max_adaptive_level: BrightnessRange, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max adaptive level of the brightness.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_brightness_max_adaptive_level, None, {"max_adaptive_level": max_adaptive_level}, request_options
        )

    def set_brightness_min_adaptive_level(
        self, *, min_adaptive_level: BrightnessRange, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min adaptive level of the brightness.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_brightness_min_adaptive_level, None, {"min_adaptive_level": min_adaptive_level}, request_options
        )

    def get_power_save(self, *, request_options: RequestOptions | None = None) -> PowerSave:
        """Get the power save settings. Access: admin."""
        return self._run(OPS.get_power_save, None, {}, request_options)

    @overload
    def update_power_save(
        self, request: UpdatePowerSaveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_power_save(
        self,
        /,
        *,
        mode: PowerSaveModes | MISSING = MISSING,
        presence_detection: PresenceDetection | MISSING = MISSING,
        schedule: Schedule | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_power_save(
        self,
        request: UpdatePowerSaveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the power save settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_power_save, request, kwargs, request_options)

    def set_power_save_mode(self, *, mode: PowerSaveModes, request_options: RequestOptions | None = None) -> None:
        """Set the mode of the power save. Changes only the fields given. Access: admin."""
        self._run(OPS.set_power_save_mode, None, {"mode": mode}, request_options)

    @overload
    def set_power_save_presence_detection(
        self, request: SetPowerSavePresenceDetectionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_power_save_presence_detection(
        self, /, *, presence_detection: PresenceDetection, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_power_save_presence_detection(
        self,
        request: SetPowerSavePresenceDetectionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the presence detection of the power save.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_power_save_presence_detection, request, kwargs, request_options)

    @overload
    def set_power_save_schedule(
        self, request: SetPowerSaveScheduleRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_power_save_schedule(
        self, /, *, schedule: Schedule, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_power_save_schedule(
        self,
        request: SetPowerSaveScheduleRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the schedule of the power save. Changes only the fields given. Access: admin."""
        self._run(OPS.set_power_save_schedule, request, kwargs, request_options)


class AsyncSpeakerDisplaySettingsApi(AsyncApi):
    """Speaker display settings (``speaker-display-settings-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> SpeakerDisplaySettings:
        """All data of the Speaker display settings API. Access: admin."""
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
        appearance: UpdateAppearanceRequest | MISSING = MISSING,
        brightness: UpdateBrightnessRequest | MISSING = MISSING,
        power_save: UpdatePowerSaveRequest | MISSING = MISSING,
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
        """Update appearance, brightness and power save settings in one call.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_all, request, kwargs, request_options)

    async def get_appearance(self, *, request_options: RequestOptions | None = None) -> Appearance:
        """Get the appearance settings. Access: admin."""
        return await self._run(OPS.get_appearance, None, {}, request_options)

    @overload
    async def update_appearance(
        self, request: UpdateAppearanceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_appearance(
        self,
        /,
        *,
        background_color: ColorFormat | MISSING = MISSING,
        font_color: ColorFormat | MISSING = MISSING,
        language: DateLanguage | MISSING = MISSING,
        show_date: bool | MISSING = MISSING,
        show_seconds: bool | MISSING = MISSING,
        use24_hour_clock: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_appearance(
        self,
        request: UpdateAppearanceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the appearance settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_appearance, request, kwargs, request_options)

    async def set_appearance_background_color(
        self, *, background_color: ColorFormat, request_options: RequestOptions | None = None
    ) -> None:
        """Set the background color of the appearance. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_appearance_background_color, None, {"background_color": background_color}, request_options
        )

    async def set_appearance_font_color(
        self, *, font_color: ColorFormat, request_options: RequestOptions | None = None
    ) -> None:
        """Set the font color of the appearance. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_appearance_font_color, None, {"font_color": font_color}, request_options)

    async def set_appearance_language(
        self, *, language: DateLanguage, request_options: RequestOptions | None = None
    ) -> None:
        """Set the language of the appearance. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_appearance_language, None, {"language": language}, request_options)

    async def set_appearance_show_date(self, *, show_date: bool, request_options: RequestOptions | None = None) -> None:
        """Set the show date of the appearance. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_appearance_show_date, None, {"show_date": show_date}, request_options)

    async def set_appearance_show_seconds(
        self, *, show_seconds: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the show seconds of the appearance. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_appearance_show_seconds, None, {"show_seconds": show_seconds}, request_options)

    async def set_appearance_use24_hour_clock(
        self, *, use24_hour_clock: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the use24 hour clock of the appearance. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_appearance_use24_hour_clock, None, {"use24_hour_clock": use24_hour_clock}, request_options
        )

    async def get_brightness(self, *, request_options: RequestOptions | None = None) -> Brightness:
        """Get the brightness settings. Access: admin."""
        return await self._run(OPS.get_brightness, None, {}, request_options)

    async def update_brightness(
        self,
        *,
        adaptive_brightness: bool | MISSING = MISSING,
        manual_level: BrightnessRange | MISSING = MISSING,
        max_adaptive_level: BrightnessRange | MISSING = MISSING,
        min_adaptive_level: BrightnessRange | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the brightness settings. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.update_brightness,
            None,
            {
                "adaptive_brightness": adaptive_brightness,
                "manual_level": manual_level,
                "max_adaptive_level": max_adaptive_level,
                "min_adaptive_level": min_adaptive_level,
            },
            request_options,
        )

    async def set_brightness_adaptive_brightness(
        self, *, adaptive_brightness: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the adaptive brightness of the brightness.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_brightness_adaptive_brightness, None, {"adaptive_brightness": adaptive_brightness}, request_options
        )

    async def set_brightness_manual_level(
        self, *, manual_level: BrightnessRange, request_options: RequestOptions | None = None
    ) -> None:
        """Set the manual level of the brightness. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_brightness_manual_level, None, {"manual_level": manual_level}, request_options)

    async def set_brightness_max_adaptive_level(
        self, *, max_adaptive_level: BrightnessRange, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max adaptive level of the brightness.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_brightness_max_adaptive_level, None, {"max_adaptive_level": max_adaptive_level}, request_options
        )

    async def set_brightness_min_adaptive_level(
        self, *, min_adaptive_level: BrightnessRange, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min adaptive level of the brightness.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_brightness_min_adaptive_level, None, {"min_adaptive_level": min_adaptive_level}, request_options
        )

    async def get_power_save(self, *, request_options: RequestOptions | None = None) -> PowerSave:
        """Get the power save settings. Access: admin."""
        return await self._run(OPS.get_power_save, None, {}, request_options)

    @overload
    async def update_power_save(
        self, request: UpdatePowerSaveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_power_save(
        self,
        /,
        *,
        mode: PowerSaveModes | MISSING = MISSING,
        presence_detection: PresenceDetection | MISSING = MISSING,
        schedule: Schedule | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_power_save(
        self,
        request: UpdatePowerSaveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the power save settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_power_save, request, kwargs, request_options)

    async def set_power_save_mode(self, *, mode: PowerSaveModes, request_options: RequestOptions | None = None) -> None:
        """Set the mode of the power save. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_power_save_mode, None, {"mode": mode}, request_options)

    @overload
    async def set_power_save_presence_detection(
        self, request: SetPowerSavePresenceDetectionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_power_save_presence_detection(
        self, /, *, presence_detection: PresenceDetection, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_power_save_presence_detection(
        self,
        request: SetPowerSavePresenceDetectionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the presence detection of the power save.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_power_save_presence_detection, request, kwargs, request_options)

    @overload
    async def set_power_save_schedule(
        self, request: SetPowerSaveScheduleRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_power_save_schedule(
        self, /, *, schedule: Schedule, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_power_save_schedule(
        self,
        request: SetPowerSaveScheduleRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the schedule of the power save. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_power_save_schedule, request, kwargs, request_options)
