# GENERATED from specs/apis/network-video/power-settings.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control device power: power saving, delayed power down, status, consumers, profiles, configurations, dynamic power mode, history, PoE warning overlay and IO port power.

Docs: https://developer.axis.com/vapix/network-video/power-settings/
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PowerConsumer(Model):
    """A part of the device whose power use can be limited."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"adjustable_power", "type"})
    power_consumer: str = Field(validation_alias="powerConsumer", serialization_alias="powerConsumer")
    """Name of the power consumer."""
    type: str | None = None
    """Consumer type."""
    max_power: float | None = Field(default=None, validation_alias="maxPower", serialization_alias="maxPower")
    """Maximum power in watts used by the consumer."""
    adjustable_power: bool | None = Field(
        default=None, validation_alias="adjustablePower", serialization_alias="adjustablePower"
    )
    """Whether the consumer power can be adjusted."""
    enabled: bool | None = None
    """Whether the consumer is enabled."""


ProfileLabel = Literal[
    "disableHeaters", "highPerformance", "lowPower", "temperatureRange", "enableIo", "enableHdmiAndAudio"
]


class ProfileConsumer(Model):
    """Setting of a power consumer when a profile is used."""

    power_consumer: str = Field(validation_alias="powerConsumer", serialization_alias="powerConsumer")
    """Consumer name."""
    max_power: float | None = Field(default=None, validation_alias="maxPower", serialization_alias="maxPower")
    """Maximum power in watts when the profile is used."""
    enabled: bool | None = None
    """Whether the consumer is active when the profile is used."""


class PowerProfile(Model):
    power_profile: str = Field(validation_alias="powerProfile", serialization_alias="powerProfile")
    """Profile name."""
    power_rank: int | None = Field(default=None, validation_alias="powerRank", serialization_alias="powerRank")
    """Ranks power usage relative to other profiles, lowest to highest."""
    lower_temperature: int | None = Field(
        default=None, validation_alias="lowerTemperature", serialization_alias="lowerTemperature"
    )
    """Lowest profile-specific temperature limit (full functionality not guaranteed below)."""
    upper_temperature: int | None = Field(
        default=None, validation_alias="upperTemperature", serialization_alias="upperTemperature"
    )
    """Highest profile-specific temperature limit."""
    labels: list[ProfileLabel] | None = None
    default: bool | None = None
    """Whether this is the default profile."""
    consumers: list[ProfileConsumer] | None = None


class Capabilities(Model):
    """Supported power features. Fields missing on older API versions are absent."""

    power_saving_support: bool | None = Field(
        default=None, validation_alias="powerSavingSupport", serialization_alias="powerSavingSupport"
    )
    """Power saving mode supported."""
    delayed_power_down_support: bool | None = Field(
        default=None, validation_alias="delayedPowerDownSupport", serialization_alias="delayedPowerDownSupport"
    )
    """Delayed power down mode supported."""
    power_profile_support: bool | None = Field(
        default=None, validation_alias="powerProfileSupport", serialization_alias="powerProfileSupport"
    )
    """Power profiles supported."""
    power_consumer_support: bool | None = Field(
        default=None, validation_alias="powerConsumerSupport", serialization_alias="powerConsumerSupport"
    )
    """Power consumers supported."""
    power_status_support: bool | None = Field(
        default=None, validation_alias="powerStatusSupport", serialization_alias="powerStatusSupport"
    )
    """Power status supported. Value is -1 if the parameter is not available on the device."""
    power_configuration_support: bool | None = Field(
        default=None, validation_alias="powerConfigurationSupport", serialization_alias="powerConfigurationSupport"
    )
    """Power configurations supported."""
    dynamic_power_mode_support: bool | None = Field(
        default=None, validation_alias="dynamicPowerModeSupport", serialization_alias="dynamicPowerModeSupport"
    )
    """Dynamic power mode supported."""
    power_history_support: bool | None = Field(
        default=None, validation_alias="powerHistorySupport", serialization_alias="powerHistorySupport"
    )
    """Power history supported."""
    disable_power_warning_overlay_support: bool | None = Field(
        default=None,
        validation_alias="disablePowerWarningOverlaySupport",
        serialization_alias="disablePowerWarningOverlaySupport",
    )
    """Device can toggle the power warning overlay."""
    io_port_power_support: bool | None = Field(
        default=None, validation_alias="ioPortPowerSupport", serialization_alias="ioPortPowerSupport"
    )
    """Device can toggle IO Port Power on or off."""


class PowerSavingMode(Model):
    power_saving_mode: bool = Field(validation_alias="powerSavingMode", serialization_alias="powerSavingMode")
    """true if power saving mode is active."""


class SetPowerSavingModeRequest(Model):
    power_saving_mode: bool = Field(validation_alias="powerSavingMode", serialization_alias="powerSavingMode")
    """true activates, false deactivates power saving mode."""


class DelayedPowerDownMode(Model):
    delayed_power_down_mode: bool = Field(
        validation_alias="delayedPowerDownMode", serialization_alias="delayedPowerDownMode"
    )
    """true if delayed power down mode is active."""
    delay_time: int | None = Field(default=None, validation_alias="delayTime", serialization_alias="delayTime", ge=0)
    """Delay time in seconds; not used if delayedPowerDownMode is false."""


class SetDelayedPowerDownModeRequest(Model):
    delayed_power_down_mode: bool = Field(
        validation_alias="delayedPowerDownMode", serialization_alias="delayedPowerDownMode"
    )
    """true activates, false deactivates delayed power down mode."""
    delay_time: int | None = Field(default=None, validation_alias="delayTime", serialization_alias="delayTime", ge=0)
    """Delay time in seconds. Not used if delayedPowerDownMode is false. (unit=s)"""


class PowerUsage(Model):
    """Power use statistics."""

    current_power: float | None = Field(
        default=None, validation_alias="currentPower", serialization_alias="currentPower"
    )
    """Power in watts currently used."""
    average_power: float | None = Field(
        default=None, validation_alias="averagePower", serialization_alias="averagePower"
    )
    """Average power in watts used."""
    max_power: float | None = Field(default=None, validation_alias="maxPower", serialization_alias="maxPower")
    """Maximum power in watts used."""


class PowerStatus(Model):
    usage: PowerUsage | None = None
    pse_poe_class: int | None = Field(default=None, validation_alias="psePoeClass", serialization_alias="psePoeClass")
    """PoE class according to the hardware power source equipment."""
    lldp_poe_class: int | None = Field(
        default=None, validation_alias="lldpPoeClass", serialization_alias="lldpPoeClass"
    )
    """PoE class according to LLDP software negotiation."""
    power_requested: float | None = Field(
        default=None, validation_alias="powerRequested", serialization_alias="powerRequested"
    )
    """Power in watts requested by the device."""


class PowerConsumerList(Model):
    consumers: list[PowerConsumer]


class SetPowerConsumerRequest(Model):
    power_consumer: str = Field(validation_alias="powerConsumer", serialization_alias="powerConsumer")
    """Name of the power consumer."""
    max_power: float | None = Field(default=None, validation_alias="maxPower", serialization_alias="maxPower")
    """Maximum power in watts used by the consumer. (unit=W)"""
    enabled: bool | None = None
    """Whether the consumer is enabled."""


class PowerProfileList(Model):
    current_power_profile: str | None = Field(
        default=None, validation_alias="currentPowerProfile", serialization_alias="currentPowerProfile"
    )
    """Name of the active profile."""
    profiles: list[PowerProfile]


class SetPowerProfileRequest(Model):
    power_profile: str = Field(validation_alias="powerProfile", serialization_alias="powerProfile")
    """Name of the profile to apply."""


class PowerConfiguration(Model):
    """A selectable power configuration."""

    index: int
    """Index of the power configuration."""
    name: str
    """Name of the power configuration."""


class PowerConfigurationList(Model):
    power_configurations: list[PowerConfiguration] = Field(
        validation_alias="powerConfigurations", serialization_alias="powerConfigurations"
    )


class ActivePowerConfiguration(Model):
    index: int
    """Index of the active power configuration."""


class SetActivePowerConfigurationRequest(Model):
    index: int
    """Index of the power configuration to set."""


class DynamicPowerMode(Model):
    dynamic_power_mode: bool = Field(validation_alias="dynamicPowerMode", serialization_alias="dynamicPowerMode")
    """true if dynamic power mode is active."""


class SetDynamicPowerModeRequest(Model):
    dynamic_power_mode: bool = Field(validation_alias="dynamicPowerMode", serialization_alias="dynamicPowerMode")
    """true enables, false disables dynamic power mode."""


class GetPowerHistoryRequest(Model):
    requested_time_span: int = Field(
        validation_alias="requestedTimeSpan", serialization_alias="requestedTimeSpan", ge=0
    )
    """Requested time length in seconds. Acquired span will likely differ (closest set of data points with highest resolution). Must be >= 0 or error 302. (unit=s)"""


class PowerHistory(Model):
    acquired_time_span: int = Field(validation_alias="acquiredTimeSpan", serialization_alias="acquiredTimeSpan")
    """Length of the acquired time span in seconds."""
    number_of_samples: int = Field(validation_alias="numberOfSamples", serialization_alias="numberOfSamples")
    """Number of data points in powerMeasurements."""
    end_time_stamp: str = Field(validation_alias="endTimeStamp", serialization_alias="endTimeStamp")
    """ISO8601 time stamp of the last data point. (format=date-time)"""
    power_measurements: list[float] = Field(
        validation_alias="powerMeasurements", serialization_alias="powerMeasurements"
    )
    """Data points in watts."""
    power_average: float = Field(validation_alias="powerAverage", serialization_alias="powerAverage")
    """Average power in watts over the acquired span."""


class PowerWarningOverlay(Model):
    enabled: bool
    """State of the power warning overlay functionality."""


class SetPowerWarningOverlayRequest(Model):
    enable: bool
    """true = enabled, false = disabled."""


class IoPortPower(Model):
    enabled: bool
    """IO Port Power state."""


class SetIoPortPowerRequest(Model):
    enable: bool
    """true = enabled, false = disabled."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/power-settings.cgi"

INFO = ApiInfo(
    id="power-settings",
    name="Power settings",
    family=Family.JSONRPC,
    major=1,
    known_versions=(
        ApiVersion(1, 0),
        ApiVersion(1, 1),
        ApiVersion(1, 2),
        ApiVersion(1, 4),
        ApiVersion(1, 5),
        ApiVersion(1, 6),
        ApiVersion(1, 7),
        ApiVersion(1, 9),
    ),
    discovery=(ApiDiscovery("power-settings"),),
    docs=("https://developer.axis.com/vapix/network-video/power-settings/",),
    errors={
        100: ErrorCode("The requested API version is not supported", "unsupported"),
        4001: ErrorCode("Mandatory input parameters were not found in the input", "invalid_argument"),
        4002: ErrorCode("The type of a provided JSON parameter was incorrect", "invalid_argument"),
        8000: ErrorCode("Internal error", "internal"),
    },
)


class OPS:
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        result=Capabilities,
        access="operator",
        effect="read",
    )
    get_power_saving_mode = Operation(
        INFO,
        "get_power_saving_mode",
        JsonRpcBinding("getPowerSavingMode", PATH),
        result=PowerSavingMode,
        access="operator",
        effect="read",
        errors={300: ErrorCode("Power saving mode is not supported.", "unsupported")},
    )
    set_power_saving_mode = Operation(
        INFO,
        "set_power_saving_mode",
        JsonRpcBinding("setPowerSavingMode", PATH),
        params=SetPowerSavingModeRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            300: ErrorCode("Power saving mode is not supported.", "unsupported"),
            301: ErrorCode("Unable to store Power saving mode.", "internal"),
        },
    )
    get_delayed_power_down_mode = Operation(
        INFO,
        "get_delayed_power_down_mode",
        JsonRpcBinding("getDelayedPowerDownMode", PATH),
        result=DelayedPowerDownMode,
        access="operator",
        effect="read",
        since=ApiVersion(1, 1),
        errors={300: ErrorCode("Delayed power down mode is not supported.", "unsupported")},
    )
    set_delayed_power_down_mode = Operation(
        INFO,
        "set_delayed_power_down_mode",
        JsonRpcBinding("setDelayedPowerDownMode", PATH),
        params=SetDelayedPowerDownModeRequest,
        access="operator",
        effect="write",
        since=ApiVersion(1, 1),
        write="patch",
        errors={
            300: ErrorCode("Delayed power down mode is not supported.", "unsupported"),
            301: ErrorCode("Unable to set delayed power down mode.", "internal"),
        },
    )
    get_power_status = Operation(
        INFO,
        "get_power_status",
        JsonRpcBinding("getPowerStatus", PATH),
        result=PowerStatus,
        access="operator",
        effect="read",
        since=ApiVersion(1, 2),
        errors={300: ErrorCode("Power status is not supported.", "unsupported")},
    )
    get_power_consumers = Operation(
        INFO,
        "get_power_consumers",
        JsonRpcBinding("getPowerConsumers", PATH),
        result=PowerConsumerList,
        access="admin",
        effect="read",
        since=ApiVersion(1, 2),
        errors={300: ErrorCode("Power consumers is not supported.", "unsupported")},
    )
    set_power_consumer = Operation(
        INFO,
        "set_power_consumer",
        JsonRpcBinding("setPowerConsumer", PATH),
        params=SetPowerConsumerRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 2),
        write="patch",
        errors={
            300: ErrorCode("Power consumers is not supported.", "unsupported"),
            301: ErrorCode("Unable to set power consumer.", "internal"),
            302: ErrorCode("Invalid parameter value for power consumer.", "invalid_argument"),
        },
    )
    get_power_profiles = Operation(
        INFO,
        "get_power_profiles",
        JsonRpcBinding("getPowerProfiles", PATH),
        result=PowerProfileList,
        access="admin",
        effect="read",
        since=ApiVersion(1, 2),
        errors={300: ErrorCode("Power profiles is not supported.", "unsupported")},
    )
    set_power_profile = Operation(
        INFO,
        "set_power_profile",
        JsonRpcBinding("setPowerProfile", PATH),
        params=SetPowerProfileRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 2),
        write="patch",
        errors={
            300: ErrorCode("Power profiles is not supported.", "unsupported"),
            301: ErrorCode("Unable to set power profile.", "internal"),
            302: ErrorCode("Invalid parameter value for power profile.", "invalid_argument"),
        },
    )
    get_power_configurations = Operation(
        INFO,
        "get_power_configurations",
        JsonRpcBinding("getPowerConfigurations", PATH),
        result=PowerConfigurationList,
        access="admin",
        effect="read",
        since=ApiVersion(1, 4),
        errors={300: ErrorCode("Power configurations are not supported.", "unsupported")},
    )
    get_active_power_configuration = Operation(
        INFO,
        "get_active_power_configuration",
        JsonRpcBinding("getActivePowerConfiguration", PATH),
        result=ActivePowerConfiguration,
        access="admin",
        effect="read",
        since=ApiVersion(1, 4),
        errors={300: ErrorCode("Power configurations are not supported.", "unsupported")},
    )
    set_active_power_configuration = Operation(
        INFO,
        "set_active_power_configuration",
        JsonRpcBinding("setActivePowerConfiguration", PATH),
        params=SetActivePowerConfigurationRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 4),
        write="patch",
        errors={
            300: ErrorCode("Power configurations are not supported.", "unsupported"),
            301: ErrorCode("Unable to set power configuration, index out of bounds.", "internal"),
            302: ErrorCode("Invalid parameter value for power configuration.", "invalid_argument"),
        },
    )
    get_dynamic_power_mode = Operation(
        INFO,
        "get_dynamic_power_mode",
        JsonRpcBinding("getDynamicPowerMode", PATH),
        result=DynamicPowerMode,
        access="admin",
        effect="read",
        since=ApiVersion(1, 5),
        errors={300: ErrorCode("Dynamic power mode is not supported.", "unsupported")},
    )
    set_dynamic_power_mode = Operation(
        INFO,
        "set_dynamic_power_mode",
        JsonRpcBinding("setDynamicPowerMode", PATH),
        params=SetDynamicPowerModeRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 5),
        write="patch",
        errors={
            300: ErrorCode("Dynamic power mode is not supported.", "unsupported"),
            301: ErrorCode("Unable to set dynamic power mode.", "internal"),
            302: ErrorCode("Invalid parameter value for dynamic power mode.", "invalid_argument"),
        },
    )
    get_power_history = Operation(
        INFO,
        "get_power_history",
        JsonRpcBinding("getPowerHistory", PATH),
        params=GetPowerHistoryRequest,
        result=PowerHistory,
        access="admin",
        effect="read",
        since=ApiVersion(1, 6),
        errors={
            300: ErrorCode("Power history is not supported.", "unsupported"),
            301: ErrorCode("Unable to retrieve power history data.", "internal"),
            302: ErrorCode("Invalid parameter value for power history.", "invalid_argument"),
        },
    )
    get_power_warning_overlay = Operation(
        INFO,
        "get_power_warning_overlay",
        JsonRpcBinding("getPowerWarningOverlay", PATH),
        result=PowerWarningOverlay,
        access="admin",
        effect="read",
        since=ApiVersion(1, 7),
        errors={
            300: ErrorCode("Disable Power Warning Overlay is not supported.", "unsupported"),
            301: ErrorCode("Unable to disable Power Warning Overlay.", "internal"),
        },
    )
    set_power_warning_overlay = Operation(
        INFO,
        "set_power_warning_overlay",
        JsonRpcBinding("setPowerWarningOverlay", PATH),
        params=SetPowerWarningOverlayRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 7),
        write="patch",
        errors={
            300: ErrorCode("Disable Power Warning Overlay is not supported.", "unsupported"),
            301: ErrorCode("Unable to disable Power Warning Overlay.", "internal"),
        },
    )
    get_io_port_power = Operation(
        INFO,
        "get_io_port_power",
        JsonRpcBinding("getIoPortPower", PATH),
        result=IoPortPower,
        access="admin",
        effect="read",
        since=ApiVersion(1, 9),
        errors={300: ErrorCode("IO Port Power is not supported.", "unsupported")},
    )
    set_io_port_power = Operation(
        INFO,
        "set_io_port_power",
        JsonRpcBinding("setIoPortPower", PATH),
        params=SetIoPortPowerRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 9),
        write="patch",
        errors={
            300: ErrorCode("IO Port Power is not supported.", "unsupported"),
            301: ErrorCode("Unable to set IO Port Power to its new state.", "internal"),
            302: ErrorCode("Invalid parameter value for set IO Port Power.", "invalid_argument"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class PowerSettingsApi(SyncApi):
    """Power settings (``power-settings``, version 1)."""

    INFO = INFO

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Retrieve which power features the device supports. Access: operator."""
        return self._run(OPS.get_capabilities, None, {}, request_options)

    def get_power_saving_mode(self, *, request_options: RequestOptions | None = None) -> PowerSavingMode:
        """Retrieve the current state of the power saving mode. Access: operator."""
        return self._run(OPS.get_power_saving_mode, None, {}, request_options)

    def set_power_saving_mode(self, power_saving_mode: bool, *, request_options: RequestOptions | None = None) -> None:
        """Apply a new state to the power saving mode (no reboot needed).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_power_saving_mode, None, {"power_saving_mode": power_saving_mode}, request_options)

    def get_delayed_power_down_mode(self, *, request_options: RequestOptions | None = None) -> DelayedPowerDownMode:
        """Retrieve the state of delayed power down mode (vehicle ignition pin). Access: operator."""
        return self._run(OPS.get_delayed_power_down_mode, None, {}, request_options)

    def set_delayed_power_down_mode(
        self,
        *,
        delayed_power_down_mode: bool,
        delay_time: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Apply delayed power down mode and its delay timer.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_delayed_power_down_mode,
            None,
            {"delayed_power_down_mode": delayed_power_down_mode, "delay_time": delay_time},
            request_options,
        )

    def get_power_status(self, *, request_options: RequestOptions | None = None) -> PowerStatus:
        """Retrieve the power status: usage statistics, PoE classes and requested power.

        Access: operator.
        """
        return self._run(OPS.get_power_status, None, {}, request_options)

    def get_power_consumers(self, *, request_options: RequestOptions | None = None) -> PowerConsumerList:
        """Retrieve all available power consumers. Access: admin."""
        return self._run(OPS.get_power_consumers, None, {}, request_options)

    def set_power_consumer(
        self,
        *,
        power_consumer: str,
        max_power: float | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Apply properties (max power, enabled) to a power consumer.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_power_consumer,
            None,
            {"power_consumer": power_consumer, "max_power": max_power, "enabled": enabled},
            request_options,
        )

    def get_power_profiles(self, *, request_options: RequestOptions | None = None) -> PowerProfileList:
        """Retrieve the available pre-defined power profiles and the current profile. Access: admin."""
        return self._run(OPS.get_power_profiles, None, {}, request_options)

    def set_power_profile(self, power_profile: str, *, request_options: RequestOptions | None = None) -> None:
        """Apply a pre-defined power profile. Changes only the fields given. Access: admin."""
        self._run(OPS.set_power_profile, None, {"power_profile": power_profile}, request_options)

    def get_power_configurations(self, *, request_options: RequestOptions | None = None) -> PowerConfigurationList:
        """Retrieve the available power configurations. Access: admin."""
        return self._run(OPS.get_power_configurations, None, {}, request_options)

    def get_active_power_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> ActivePowerConfiguration:
        """Retrieve the active power configuration. Access: admin."""
        return self._run(OPS.get_active_power_configuration, None, {}, request_options)

    def set_active_power_configuration(self, index: int, *, request_options: RequestOptions | None = None) -> None:
        """Set the active power configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_active_power_configuration, None, {"index": index}, request_options)

    def get_dynamic_power_mode(self, *, request_options: RequestOptions | None = None) -> DynamicPowerMode:
        """Retrieve the dynamic power mode state. Access: admin."""
        return self._run(OPS.get_dynamic_power_mode, None, {}, request_options)

    def set_dynamic_power_mode(
        self, dynamic_power_mode: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable dynamic power mode (lower performance/power during inactivity).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_dynamic_power_mode, None, {"dynamic_power_mode": dynamic_power_mode}, request_options)

    def get_power_history(
        self, requested_time_span: int, *, request_options: RequestOptions | None = None
    ) -> PowerHistory:
        """Retrieve persistent long-term power history data. Access: admin."""
        return self._run(OPS.get_power_history, None, {"requested_time_span": requested_time_span}, request_options)

    def get_power_warning_overlay(self, *, request_options: RequestOptions | None = None) -> PowerWarningOverlay:
        """Check whether the insufficient-PoE text overlay warning is enabled.

        If enabled, the system shows the overlay when appropriate. Some products support changing the power
        configuration with set_active_power_configuration instead of disabling the overlay.

        Access: admin.
        """
        return self._run(OPS.get_power_warning_overlay, None, {}, request_options)

    def set_power_warning_overlay(self, enable: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the power warning overlay. Changes only the fields given. Access: admin."""
        self._run(OPS.set_power_warning_overlay, None, {"enable": enable}, request_options)

    def get_io_port_power(self, *, request_options: RequestOptions | None = None) -> IoPortPower:
        """Check whether the 12V IO Port Power output on the IO connector is enabled. Access: admin."""
        return self._run(OPS.get_io_port_power, None, {}, request_options)

    def set_io_port_power(self, enable: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn the 12V IO Port Power on or off.

        The extra power can then be used by another consumer in the camera, such as the heater, IR or deep
        learning.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_io_port_power, None, {"enable": enable}, request_options)


class AsyncPowerSettingsApi(AsyncApi):
    """Power settings (``power-settings``, version 1)."""

    INFO = INFO

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Retrieve which power features the device supports. Access: operator."""
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    async def get_power_saving_mode(self, *, request_options: RequestOptions | None = None) -> PowerSavingMode:
        """Retrieve the current state of the power saving mode. Access: operator."""
        return await self._run(OPS.get_power_saving_mode, None, {}, request_options)

    async def set_power_saving_mode(
        self, power_saving_mode: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Apply a new state to the power saving mode (no reboot needed).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_power_saving_mode, None, {"power_saving_mode": power_saving_mode}, request_options)

    async def get_delayed_power_down_mode(
        self, *, request_options: RequestOptions | None = None
    ) -> DelayedPowerDownMode:
        """Retrieve the state of delayed power down mode (vehicle ignition pin). Access: operator."""
        return await self._run(OPS.get_delayed_power_down_mode, None, {}, request_options)

    async def set_delayed_power_down_mode(
        self,
        *,
        delayed_power_down_mode: bool,
        delay_time: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Apply delayed power down mode and its delay timer.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_delayed_power_down_mode,
            None,
            {"delayed_power_down_mode": delayed_power_down_mode, "delay_time": delay_time},
            request_options,
        )

    async def get_power_status(self, *, request_options: RequestOptions | None = None) -> PowerStatus:
        """Retrieve the power status: usage statistics, PoE classes and requested power.

        Access: operator.
        """
        return await self._run(OPS.get_power_status, None, {}, request_options)

    async def get_power_consumers(self, *, request_options: RequestOptions | None = None) -> PowerConsumerList:
        """Retrieve all available power consumers. Access: admin."""
        return await self._run(OPS.get_power_consumers, None, {}, request_options)

    async def set_power_consumer(
        self,
        *,
        power_consumer: str,
        max_power: float | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Apply properties (max power, enabled) to a power consumer.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_power_consumer,
            None,
            {"power_consumer": power_consumer, "max_power": max_power, "enabled": enabled},
            request_options,
        )

    async def get_power_profiles(self, *, request_options: RequestOptions | None = None) -> PowerProfileList:
        """Retrieve the available pre-defined power profiles and the current profile. Access: admin."""
        return await self._run(OPS.get_power_profiles, None, {}, request_options)

    async def set_power_profile(self, power_profile: str, *, request_options: RequestOptions | None = None) -> None:
        """Apply a pre-defined power profile. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_power_profile, None, {"power_profile": power_profile}, request_options)

    async def get_power_configurations(
        self, *, request_options: RequestOptions | None = None
    ) -> PowerConfigurationList:
        """Retrieve the available power configurations. Access: admin."""
        return await self._run(OPS.get_power_configurations, None, {}, request_options)

    async def get_active_power_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> ActivePowerConfiguration:
        """Retrieve the active power configuration. Access: admin."""
        return await self._run(OPS.get_active_power_configuration, None, {}, request_options)

    async def set_active_power_configuration(
        self, index: int, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the active power configuration. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_active_power_configuration, None, {"index": index}, request_options)

    async def get_dynamic_power_mode(self, *, request_options: RequestOptions | None = None) -> DynamicPowerMode:
        """Retrieve the dynamic power mode state. Access: admin."""
        return await self._run(OPS.get_dynamic_power_mode, None, {}, request_options)

    async def set_dynamic_power_mode(
        self, dynamic_power_mode: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable dynamic power mode (lower performance/power during inactivity).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_dynamic_power_mode, None, {"dynamic_power_mode": dynamic_power_mode}, request_options)

    async def get_power_history(
        self, requested_time_span: int, *, request_options: RequestOptions | None = None
    ) -> PowerHistory:
        """Retrieve persistent long-term power history data. Access: admin."""
        return await self._run(
            OPS.get_power_history, None, {"requested_time_span": requested_time_span}, request_options
        )

    async def get_power_warning_overlay(self, *, request_options: RequestOptions | None = None) -> PowerWarningOverlay:
        """Check whether the insufficient-PoE text overlay warning is enabled.

        If enabled, the system shows the overlay when appropriate. Some products support changing the power
        configuration with set_active_power_configuration instead of disabling the overlay.

        Access: admin.
        """
        return await self._run(OPS.get_power_warning_overlay, None, {}, request_options)

    async def set_power_warning_overlay(self, enable: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the power warning overlay. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_power_warning_overlay, None, {"enable": enable}, request_options)

    async def get_io_port_power(self, *, request_options: RequestOptions | None = None) -> IoPortPower:
        """Check whether the 12V IO Port Power output on the IO connector is enabled. Access: admin."""
        return await self._run(OPS.get_io_port_power, None, {}, request_options)

    async def set_io_port_power(self, enable: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn the 12V IO Port Power on or off.

        The extra power can then be used by another consumer in the camera, such as the heater, IR or deep
        learning.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_io_port_power, None, {"enable": enable}, request_options)
