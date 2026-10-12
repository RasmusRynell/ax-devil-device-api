# GENERATED from specs/apis/audio-systems/audio-analytics.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read the JSON schemas and the settings of the audio analytics plugins, and apply new settings.

Docs: https://developer.axis.com/vapix/audio-systems/audio-analytics/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PluginSchema(Model):
    """The JSON schema of the settings of one plugin."""

    schema_: str | None = Field(default=None, validation_alias="$schema", serialization_alias="$schema")
    """The URL for the core schema meta-schema (plugins use draft/2020-12, e.g. http://json-schema.org/draft/2020-12/schema#)."""
    title: str | None = None
    """The schema title."""
    id: str | None = None
    """Identification of the plugin."""
    type: str | None = None
    """The settings type, usually an object."""
    properties: dict[str, Any] | None = None
    """A unique JSON schema describing the properties of the settings objects returned by getPluginsSettings and sent by setPluginsSettings. Deviations from draft/2020-12 are explained in the schema itself."""


class PluginSettings(Model):
    """The settings of one plugin instance."""

    id: str
    """The plugin instance id (e.g. AdaptiveAudioDetection, DirectionOfArrival, AggressionDetection)."""
    settings: dict[str, Any]
    """Settings parameters detailed by the response from getPluginsSchemas."""


class IoPlugins(Model):
    """The plugins of one audio input or output."""

    id: str
    """The input/output id."""
    plugins: list[PluginSettings] | None = None
    """The plugin settings."""


class AudioDevicePlugins(Model):
    """The plugins of one audio device."""

    id: str
    """The audio device id (as in Audio Device Control)."""
    inputs: list[IoPlugins] | None = None
    """Lists the device inputs."""
    outputs: list[IoPlugins] | None = None
    """Lists the device outputs."""


class PluginsSettings(Model):
    """The plugin settings of all audio devices."""

    devices: list[AudioDevicePlugins]
    """Lists all available audio devices."""


class PluginSchemas(Model):
    """The available plugin schemas."""

    schemas: list[PluginSchema]
    """List of available plugin schemas."""


class SetPluginsSettingsRequest(Model):
    """Arguments of ``set_plugins_settings``."""

    devices: list[AudioDevicePlugins]
    """The audio devices and the plugin settings to apply."""

    @classmethod
    def from_current(cls, settings: PluginsSettings) -> SetPluginsSettingsRequest:
        """A request that rewrites ``settings`` unchanged: copy it, edit fields, send it back."""
        data = settings.request_data()
        return cls(**data)


class GetPluginsSchemasRequest(Model):
    plugin: str | None = None
    """The plugin name. Optional in practice, because the documented example sends empty params and gets all schemas."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/audioanalytics.cgi"

INFO = ApiInfo(
    id="audio-analytics",
    name="Audio Analytics",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 3)),
    discovery=(ApiDiscovery("audio-analytics"),),
    docs=("https://developer.axis.com/vapix/audio-systems/audio-analytics/",),
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
        2107: ErrorCode("TRANSPORT_LEVEL_ERROR. Transport Level Error."),
    },
)


class OPS:
    get_plugins_schemas = Operation(
        INFO,
        "get_plugins_schemas",
        JsonRpcBinding("getPluginsSchemas", PATH),
        params=GetPluginsSchemasRequest,
        result=PluginSchemas,
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


class AudioAnalyticsApi(SyncApi):
    """Audio Analytics (``audio-analytics``, version 1)."""

    INFO = INFO

    def get_plugins_schemas(
        self, *, plugin: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PluginSchemas:
        """Lists the JSON schema for all settings related to the analytics plugins. Access: operator."""
        return self._run(OPS.get_plugins_schemas, None, {"plugin": plugin}, request_options)

    def get_plugins_settings(self, *, request_options: RequestOptions | None = None) -> PluginsSettings:
        """Lists the plugin settings for all plugin instances for all audio sources.

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
        """Applies the plugin settings for plugin instances.

        The settings returned by get_plugins_settings can be sent back to configure the plugins.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_plugins_settings, request, kwargs, request_options)


class AsyncAudioAnalyticsApi(AsyncApi):
    """Audio Analytics (``audio-analytics``, version 1)."""

    INFO = INFO

    async def get_plugins_schemas(
        self, *, plugin: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PluginSchemas:
        """Lists the JSON schema for all settings related to the analytics plugins. Access: operator."""
        return await self._run(OPS.get_plugins_schemas, None, {"plugin": plugin}, request_options)

    async def get_plugins_settings(self, *, request_options: RequestOptions | None = None) -> PluginsSettings:
        """Lists the plugin settings for all plugin instances for all audio sources.

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
        """Applies the plugin settings for plugin instances.

        The settings returned by get_plugins_settings can be sent back to configure the plugins.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_plugins_settings, request, kwargs, request_options)
