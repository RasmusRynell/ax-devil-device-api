# GENERATED from specs/apis/audio-systems/audio-mixer-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read the JSON schema of audio plugins, and read and apply the settings of the audio plugins in the audio chain.

Docs: https://developer.axis.com/vapix/audio-systems/audio-mixer-api/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PluginSettings(Model):
    """The settings of one plugin instance."""

    id: str
    """The plugin instance identification (e.g. automaticGainControl, voiceEnhancer, simpleEq)."""
    settings: dict[str, Any]
    """Settings parameters described by the response from getPluginSchema."""


class IoPlugins(Model):
    """The plugins of one audio input or output."""

    id: str
    """The input/output ID."""
    plugins: list[PluginSettings] | None = None
    """List of plugin settings."""


class AudioDevicePlugins(Model):
    """The plugins of one audio device."""

    id: str
    """The audio device ID."""
    inputs: list[IoPlugins] | None = None
    """List of device inputs."""
    outputs: list[IoPlugins] | None = None
    """List of outputs in a device."""


class PluginsSettings(Model):
    """The plugin settings of all audio devices."""

    devices: list[AudioDevicePlugins]
    """List of available audio devices."""


class PluginSchema(Model):
    """The JSON schema of the settings object of one plugin."""

    schema_: str | None = Field(default=None, validation_alias="$schema", serialization_alias="$schema")
    """The URL to the core schema meta-schema."""
    title: str | None = None
    """The schema title."""
    type: str | None = None
    """The type of settings, most likely an object."""
    properties: dict[str, Any] | None = None
    """A unique JSON schema describing the properties of the settings object returned by getPluginsSettings and sent to setPluginsSettings."""


class SetPluginsSettingsRequest(Model):
    """Arguments of ``set_plugins_settings``. Only changed parameters need to be specified."""

    devices: list[AudioDevicePlugins]
    """List of audio devices and the plugin settings to apply."""

    @classmethod
    def from_current(cls, settings: PluginsSettings) -> SetPluginsSettingsRequest:
        """A request that rewrites ``settings`` unchanged: copy it, edit fields, send it back."""
        data = settings.request_data()
        return cls.from_response_data(data)


class GetPluginSchemaRequest(Model):
    plugin: str
    """The name of the plugin that retrieves the settings object JSON schema."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/audiomixer.cgi"

INFO = ApiInfo(
    id="audio-mixer-api",
    name="Audio mixer API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 3)),
    docs=("https://developer.axis.com/vapix/audio-systems/audio-mixer-api/",),
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
    get_plugin_schema = Operation(
        INFO,
        "get_plugin_schema",
        JsonRpcBinding("getPluginSchema", PATH),
        params=GetPluginSchemaRequest,
        result=PluginSchema,
        access="operator",
        effect="read",
    )
    get_plugins_settings = Operation(
        INFO,
        "get_plugins_settings",
        JsonRpcBinding("getPluginsSettings", PATH),
        result=PluginsSettings,
        access="operator",
        effect="read",
    )
    set_plugins_settings = Operation(
        INFO,
        "set_plugins_settings",
        JsonRpcBinding("setPluginsSettings", PATH),
        params=SetPluginsSettingsRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class AudioMixerApi(SyncApi):
    """Audio mixer API (``audio-mixer-api``, version 1)."""

    INFO = INFO

    def get_plugin_schema(self, plugin: str, *, request_options: RequestOptions | None = None) -> PluginSchema:
        """Retrieve the JSON schema for a plugin's settings object (as used by getPluginsSettings/setPluginsSettings).

        Access: operator.
        """
        return self._run(OPS.get_plugin_schema, None, {"plugin": plugin}, request_options)

    def get_plugins_settings(self, *, request_options: RequestOptions | None = None) -> PluginsSettings:
        """Retrieve the plugin settings for all plugin instances on all audio devices/inputs/outputs.

        Access: operator.
        """
        return self._run(OPS.get_plugins_settings, None, {}, request_options)

    @overload
    def set_plugins_settings(
        self, request: SetPluginsSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_plugins_settings(
        self, /, *, devices: list[AudioDevicePlugins], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_plugins_settings(
        self,
        request: SetPluginsSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure plugin instances (structure as returned by getPluginsSettings).

        Only parameters that are changed need to be specified; non-specified parameters retain their
        existing values.

        Changes only the entries given; entries that do not exist yet may be created. Access: operator.
        """
        self._run(OPS.set_plugins_settings, request, kwargs, request_options)


class AsyncAudioMixerApi(AsyncApi):
    """Audio mixer API (``audio-mixer-api``, version 1)."""

    INFO = INFO

    async def get_plugin_schema(self, plugin: str, *, request_options: RequestOptions | None = None) -> PluginSchema:
        """Retrieve the JSON schema for a plugin's settings object (as used by getPluginsSettings/setPluginsSettings).

        Access: operator.
        """
        return await self._run(OPS.get_plugin_schema, None, {"plugin": plugin}, request_options)

    async def get_plugins_settings(self, *, request_options: RequestOptions | None = None) -> PluginsSettings:
        """Retrieve the plugin settings for all plugin instances on all audio devices/inputs/outputs.

        Access: operator.
        """
        return await self._run(OPS.get_plugins_settings, None, {}, request_options)

    @overload
    async def set_plugins_settings(
        self, request: SetPluginsSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_plugins_settings(
        self, /, *, devices: list[AudioDevicePlugins], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_plugins_settings(
        self,
        request: SetPluginsSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure plugin instances (structure as returned by getPluginsSettings).

        Only parameters that are changed need to be specified; non-specified parameters retain their
        existing values.

        Changes only the entries given; entries that do not exist yet may be created. Access: operator.
        """
        await self._run(OPS.set_plugins_settings, request, kwargs, request_options)
