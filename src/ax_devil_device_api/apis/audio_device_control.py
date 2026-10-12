# GENERATED from specs/apis/audio-systems/audio-device-control.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List audio device capabilities and read or change audio device input/output settings (connection type, signaling type, power type, per-channel gain and mute).

Docs: https://developer.axis.com/vapix/audio-systems/audio-device-control/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SignalingTypeCapability(Model):
    """One signal configuration (for example balanced or unbalanced) of a connection type."""

    id: str
    """The signal ID (e.g. balanced, unbalanced). Cannot be changed."""
    gain_values: list[int] | None = Field(default=None, validation_alias="gainValues", serialization_alias="gainValues")
    """The gain capabilities for the signaling type."""
    power_types: list[str] | None = Field(default=None, validation_alias="powerTypes", serialization_alias="powerTypes")
    """The power types available for the signal (inputs only; e.g. On, Off, P48, 5V)."""


class ConnectionTypeCapability(Model):
    """One input or output type (for example mic, line or external) and its signal configurations."""

    id: str
    """Input/output type ID (e.g. internal, mic, line, external)."""
    signaling_types: list[SignalingTypeCapability] | None = Field(
        default=None, validation_alias="signalingTypes", serialization_alias="signalingTypes"
    )
    """Lists the signal configuration settings."""


class IoCapability(Model):
    """The capabilities of one audio input or output."""

    id: str
    """The input/output ID."""
    connection_types: list[ConnectionTypeCapability] | None = Field(
        default=None, validation_alias="connectionTypes", serialization_alias="connectionTypes"
    )
    """Lists the input or output types."""


class DeviceCapability(Model):
    """The capabilities of one audio device."""

    id: str
    """The audio device ID."""
    inputs: list[IoCapability] | None = None
    """Lists the inputs on a device."""
    outputs: list[IoCapability] | None = None
    """Lists the outputs on a device."""


class DevicesCapabilities(Model):
    """The capabilities of all audio devices."""

    devices: list[DeviceCapability]
    """Lists available audio devices."""


class Channel(Model):
    """One audio channel."""

    id: int
    """The channel ID."""
    gain: int | None = None
    """The channel gain."""
    mute: bool | None = None
    """The channel mute."""


class SignalingTypeSettings(Model):
    """The settings of one signal configuration."""

    id: str
    """The signal ID. Not changeable."""
    power_type: str | None = Field(default=None, validation_alias="powerType", serialization_alias="powerType")
    """The selected power type for a signal (inputs only)."""
    channels: list[Channel] | None = None
    """Lists the channels."""


class ConnectionTypeSettings(Model):
    """The settings of one input or output type."""

    id: str
    """Input/output type ID."""
    signaling_type_selected: str | None = Field(
        default=None, validation_alias="signalingTypeSelected", serialization_alias="signalingTypeSelected"
    )
    """The selected signal."""
    signaling_types: list[SignalingTypeSettings] | None = Field(
        default=None, validation_alias="signalingTypes", serialization_alias="signalingTypes"
    )
    """Lists the signal configuration settings."""


class IoSettings(Model):
    """The settings of one audio input or output."""

    id: str
    """The input/output ID."""
    name: str | None = None
    """The input/output name."""
    connection_type_selected: str | None = Field(
        default=None, validation_alias="connectionTypeSelected", serialization_alias="connectionTypeSelected"
    )
    """The selected input/output type."""
    connection_types: list[ConnectionTypeSettings] | None = Field(
        default=None, validation_alias="connectionTypes", serialization_alias="connectionTypes"
    )
    """Lists the input or output types."""


class DeviceSettings(Model):
    """The settings of one audio device."""

    id: str
    """The audio device ID."""
    name: str | None = None
    """The audio device name."""
    inputs: list[IoSettings] | None = None
    """Lists the inputs on a device."""
    outputs: list[IoSettings] | None = None
    """Lists the outputs on a device."""


class DevicesSettings(Model):
    """The settings of all audio devices."""

    devices: list[DeviceSettings]
    """Lists available audio devices."""


class SetDevicesSettingsRequest(Model):
    """Arguments of ``set_devices_settings``."""

    devices: list[DeviceSettings]
    """The audio devices to configure (same structure as get_devices_settings)."""

    @classmethod
    def from_current(cls, settings: DevicesSettings) -> SetDevicesSettingsRequest:
        """A request that rewrites ``settings`` unchanged: copy it, edit fields, send it back."""
        data = settings.request_data()
        return cls(**data)


class HazardousSettings(Model):
    """Settings that may harm the hardware if used incorrectly. They are global."""

    power_types: list[str] = Field(validation_alias="powerTypes", serialization_alias="powerTypes")
    """The hazardous power types, e.g. ["R12"]."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/audiodevicecontrol.cgi"

INFO = ApiInfo(
    id="audio-device-control",
    name="Audio Device Control",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 3)),
    discovery=(ApiDiscovery("audio-device-control"),),
    docs=("https://developer.axis.com/vapix/audio-systems/audio-device-control/",),
    errors={
        1100: ErrorCode("INTERNAL_ERROR. Internal error.", "internal"),
        2100: ErrorCode("UNSUPPORTED_API_VERSION. The requested API version is not supported.", "unsupported"),
        2101: ErrorCode("JSON_INVALID_ERROR. The provided JSON input was invalid.", "invalid_argument"),
        2102: ErrorCode("METHOD_NOT_SUPPORTED. Method not supported.", "unsupported"),
        2103: ErrorCode(
            "JSON_KEY_NOT_FOUND. A mandatory input parameter was not found in the input.", "invalid_argument"
        ),
        2104: ErrorCode("PARAM_INVALID_VALUE_ERROR. Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("AUTHORIZATION_ERROR. Authorization failed.", "access_denied"),
        2106: ErrorCode("AUTHENTICATION_ERROR. Authentication failed.", "access_denied"),
        2107: ErrorCode("TRANSPORT_LEVEL_ERROR. Transport level error."),
    },
)


class OPS:
    get_devices_capabilities = Operation(
        INFO,
        "get_devices_capabilities",
        JsonRpcBinding("getDevicesCapabilities", PATH),
        result=DevicesCapabilities,
        access="operator",
        effect="read",
    )
    get_devices_settings = Operation(
        INFO,
        "get_devices_settings",
        JsonRpcBinding("getDevicesSettings", PATH),
        result=DevicesSettings,
        access="viewer",
        effect="read",
    )
    set_devices_settings = Operation(
        INFO,
        "set_devices_settings",
        JsonRpcBinding("setDevicesSettings", PATH),
        params=SetDevicesSettingsRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_hazardous_settings = Operation(
        INFO,
        "get_hazardous_settings",
        JsonRpcBinding("getHazardousSettings", PATH),
        result=HazardousSettings,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class AudioDeviceControlApi(SyncApi):
    """Audio Device Control (``audio-device-control``, version 1)."""

    INFO = INFO

    def get_devices_capabilities(self, *, request_options: RequestOptions | None = None) -> DevicesCapabilities:
        """Lists all audio capabilities (accepted gain values and power types) of the device's audio devices.

        Access: operator.
        """
        return self._run(OPS.get_devices_capabilities, None, {}, request_options)

    def get_devices_settings(self, *, request_options: RequestOptions | None = None) -> DevicesSettings:
        """Lists all available and currently applied audio settings. Access: viewer."""
        return self._run(OPS.get_devices_settings, None, {}, request_options)

    @overload
    def set_devices_settings(
        self, request: SetDevicesSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_devices_settings(
        self, /, *, devices: list[DeviceSettings], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_devices_settings(
        self,
        request: SetDevicesSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change the audio settings for one or multiple audio devices.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_devices_settings, request, kwargs, request_options)

    def get_hazardous_settings(self, *, request_options: RequestOptions | None = None) -> HazardousSettings:
        """List settings that may harm the hardware if used incorrectly (global, not per device/input/output).

        Access: operator.
        """
        return self._run(OPS.get_hazardous_settings, None, {}, request_options)


class AsyncAudioDeviceControlApi(AsyncApi):
    """Audio Device Control (``audio-device-control``, version 1)."""

    INFO = INFO

    async def get_devices_capabilities(self, *, request_options: RequestOptions | None = None) -> DevicesCapabilities:
        """Lists all audio capabilities (accepted gain values and power types) of the device's audio devices.

        Access: operator.
        """
        return await self._run(OPS.get_devices_capabilities, None, {}, request_options)

    async def get_devices_settings(self, *, request_options: RequestOptions | None = None) -> DevicesSettings:
        """Lists all available and currently applied audio settings. Access: viewer."""
        return await self._run(OPS.get_devices_settings, None, {}, request_options)

    @overload
    async def set_devices_settings(
        self, request: SetDevicesSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_devices_settings(
        self, /, *, devices: list[DeviceSettings], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_devices_settings(
        self,
        request: SetDevicesSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change the audio settings for one or multiple audio devices.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_devices_settings, request, kwargs, request_options)

    async def get_hazardous_settings(self, *, request_options: RequestOptions | None = None) -> HazardousSettings:
        """List settings that may harm the hardware if used incorrectly (global, not per device/input/output).

        Access: operator.
        """
        return await self._run(OPS.get_hazardous_settings, None, {}, request_options)
