# GENERATED from specs/apis/audio-systems/audio-control-service-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Adjust the foreground and background volume (and input configuration) of an audio device via /vapix/audiocontrol.

Docs: https://developer.axis.com/vapix/audio-systems/audio-control-service-api/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Range(Model):
    """Describes a range of valid values and the unit."""

    unit: str | None = Field(default=None, validation_alias="Unit", serialization_alias="Unit")
    """The unit of the value, (e.g. dB)."""
    max_value: int | None = Field(default=None, validation_alias="MaxValue", serialization_alias="MaxValue")
    """The maximum value of the range."""
    min_value: int | None = Field(default=None, validation_alias="MinValue", serialization_alias="MinValue")
    """The minimum value of the range."""


class ControlCapabilities(Model):
    """Reflects the optional functionality of the service. Static; does not change during device operation."""

    volume_ranges: Range | None = Field(
        default=None, validation_alias="VolumeRanges", serialization_alias="VolumeRanges"
    )
    """Master volume ranges as supported by this service."""


class Volume(Model):
    """The configuration of foreground and background volumes for a device. Valid parameter values may be defined by the service capabilities. All members are optional in SetVolume."""

    foreground_volume: int | None = Field(
        default=None, validation_alias="ForegroundVolume", serialization_alias="ForegroundVolume"
    )
    """The foreground volume."""
    foreground_volume_unit: str | None = Field(
        default=None, validation_alias="ForegroundVolumeUnit", serialization_alias="ForegroundVolumeUnit"
    )
    """The unit of the foreground volume. Optional parameter to use if default unit type is not used."""
    foreground_volume_mute: bool | None = Field(
        default=None, validation_alias="ForegroundVolumeMute", serialization_alias="ForegroundVolumeMute"
    )
    """Mutes the foreground volume."""
    background_volume: int | None = Field(
        default=None, validation_alias="BackgroundVolume", serialization_alias="BackgroundVolume"
    )
    """The background volume."""
    background_volume_unit: str | None = Field(
        default=None, validation_alias="BackgroundVolumeUnit", serialization_alias="BackgroundVolumeUnit"
    )
    """The unit of the background volume. Optional parameter to use if default unit type is not used."""
    background_volume_mute: bool | None = Field(
        default=None, validation_alias="BackgroundVolumeMute", serialization_alias="BackgroundVolumeMute"
    )
    """Mutes the background volume of the Audio Relay Network."""


class InputConfiguration(Model):
    """Only shown in an example; no field table is documented. Field types taken from the example."""

    input_id: str | None = Field(default=None, validation_alias="InputId", serialization_alias="InputId")
    """Audio input id (e.g. analog_1). Valid values via GetControlCapabilities (per doc text)."""
    channel_id: str | None = Field(default=None, validation_alias="ChannelId", serialization_alias="ChannelId")
    """Channel id (e.g. Background). Valid values via GetControlCapabilities (per doc text)."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")


class GetControlCapabilitiesResult(Model):
    capabilities: ControlCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capability response message contains the capabilities that are present in the device."""


class GetVolumeResult(Model):
    volume: Volume = Field(validation_alias="Volume", serialization_alias="Volume")
    """The returned volume."""


class SetVolumeRequest(Model):
    volume: Volume = Field(validation_alias="Volume", serialization_alias="Volume")
    """The volume to set."""


class SetInputConfigurationRequest(Model):
    input_configuration: InputConfiguration = Field(
        validation_alias="InputConfiguration", serialization_alias="InputConfiguration"
    )
    """The input configuration to apply."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/audiocontrol"

INFO = ApiInfo(
    id="audio-control-service-api",
    name="Audio control service API",
    family=Family.SERVICE_JSON,
    discovery=(ParamDiscovery("Properties.API.AudioControl.Version", "1.0"),),
    status="deprecated",
    docs=("https://developer.axis.com/vapix/audio-systems/audio-control-service-api/",),
)


class OPS:
    get_control_capabilities = Operation(
        INFO,
        "get_control_capabilities",
        ServiceJsonBinding(PATH, "axac:GetControlCapabilities"),
        result=GetControlCapabilitiesResult,
        access="admin",
        effect="read",
    )
    get_volume = Operation(
        INFO,
        "get_volume",
        ServiceJsonBinding(PATH, "axac:GetVolume"),
        result=GetVolumeResult,
        access="admin",
        effect="read",
    )
    set_volume = Operation(
        INFO,
        "set_volume",
        ServiceJsonBinding(PATH, "axac:SetVolume"),
        params=SetVolumeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_input_configuration = Operation(
        INFO,
        "set_input_configuration",
        ServiceJsonBinding(PATH, "axac:SetInputConfiguration"),
        params=SetInputConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class AudioControlServiceApi(SyncApi):
    """Audio control service API (``audio-control-service-api``)."""

    INFO = INFO

    def get_control_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetControlCapabilitiesResult:
        """Returns the capabilities of the service. Access: admin."""
        return self._run(OPS.get_control_capabilities, None, {}, request_options)

    def get_volume(self, *, request_options: RequestOptions | None = None) -> GetVolumeResult:
        """Returns the Volume of the Audio Relay network. Access: admin."""
        return self._run(OPS.get_volume, None, {}, request_options)

    @overload
    def set_volume(self, request: SetVolumeRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_volume(self, /, *, volume: Volume, request_options: RequestOptions | None = None) -> None: ...
    def set_volume(
        self,
        request: SetVolumeRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Requests that a Volume should be set.

        All members of the Volume are optional, so a Volume with all members empty will be accepted, but
        won't change anything.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_volume, request, kwargs, request_options)

    @overload
    def set_input_configuration(
        self, request: SetInputConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_input_configuration(
        self, /, *, input_configuration: InputConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_input_configuration(
        self,
        request: SetInputConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Specify which audio inputs should be used.

        Valid values for InputId and ChannelId can be requested using axac:GetControlCapabilities. Not all
        devices support line input capabilities, so it will not always be possible to adjust the feature.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_input_configuration, request, kwargs, request_options)


class AsyncAudioControlServiceApi(AsyncApi):
    """Audio control service API (``audio-control-service-api``)."""

    INFO = INFO

    async def get_control_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetControlCapabilitiesResult:
        """Returns the capabilities of the service. Access: admin."""
        return await self._run(OPS.get_control_capabilities, None, {}, request_options)

    async def get_volume(self, *, request_options: RequestOptions | None = None) -> GetVolumeResult:
        """Returns the Volume of the Audio Relay network. Access: admin."""
        return await self._run(OPS.get_volume, None, {}, request_options)

    @overload
    async def set_volume(
        self, request: SetVolumeRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_volume(self, /, *, volume: Volume, request_options: RequestOptions | None = None) -> None: ...
    async def set_volume(
        self,
        request: SetVolumeRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Requests that a Volume should be set.

        All members of the Volume are optional, so a Volume with all members empty will be accepted, but
        won't change anything.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_volume, request, kwargs, request_options)

    @overload
    async def set_input_configuration(
        self, request: SetInputConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_input_configuration(
        self, /, *, input_configuration: InputConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_input_configuration(
        self,
        request: SetInputConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Specify which audio inputs should be used.

        Valid values for InputId and ChannelId can be requested using axac:GetControlCapabilities. Not all
        devices support line input capabilities, so it will not always be possible to adjust the feature.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_input_configuration, request, kwargs, request_options)
