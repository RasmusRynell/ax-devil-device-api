# GENERATED from specs/apis/network-video/regional-settings.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Store regional settings such as the length unit used when presenting values.

Docs: https://developer.axis.com/vapix/network-video/regional-settings/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

LengthUnit = Literal["metric", "us_customary"]


class Units(Model):
    length: LengthUnit


class RegionalSettings(Model):
    """Regional settings stored on the device."""

    units: Units | None = None


class SetRegionalSettingsRequest(Model):
    """Arguments of ``set_regional_settings``. The device answers 1003 if no parameters are given."""

    units: Units


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/regionalsettings.cgi"

INFO = ApiInfo(
    id="regional-settings",
    name="Regional settings",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1)),
    discovery=(
        ApiDiscovery("regional-settings"),
        ParamDiscovery("root.Properties.RegionalSettings.RegionalSettings", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/regional-settings/",),
    errors={
        1000: ErrorCode("Internal error.", "internal"),
        1001: ErrorCode("The requested API version is not supported.", "unsupported"),
        1002: ErrorCode("Unknown method.", "unsupported"),
        1003: ErrorCode("Invalid argument.", "invalid_argument"),
        1004: ErrorCode("Invalid request.", "invalid_argument"),
    },
)


class OPS:
    get_regional_settings = Operation(
        INFO,
        "get_regional_settings",
        JsonRpcBinding("getRegionalSettings", PATH),
        result=RegionalSettings,
        access="operator",
        effect="read",
    )
    set_regional_settings = Operation(
        INFO,
        "set_regional_settings",
        JsonRpcBinding("setRegionalSettings", PATH),
        params=SetRegionalSettingsRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1003: ErrorCode("Invalid argument. The request has no parameters or an invalid value.", "invalid_argument")
        },
    )


# ---------------------------------------------------------------------------
# API classes


class RegionalSettingsApi(SyncApi):
    """Regional settings (``regional-settings``, version 1)."""

    INFO = INFO

    def get_regional_settings(self, *, request_options: RequestOptions | None = None) -> RegionalSettings:
        """Retrieve the current regional settings, for example the length unit used in the GUI.

        Access: operator.
        """
        return self._run(OPS.get_regional_settings, None, {}, request_options)

    @overload
    def set_regional_settings(
        self, request: SetRegionalSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_regional_settings(self, /, *, units: Units, request_options: RequestOptions | None = None) -> None: ...
    def set_regional_settings(
        self,
        request: SetRegionalSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the regional settings used in the GUI.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_regional_settings, request, kwargs, request_options)


class AsyncRegionalSettingsApi(AsyncApi):
    """Regional settings (``regional-settings``, version 1)."""

    INFO = INFO

    async def get_regional_settings(self, *, request_options: RequestOptions | None = None) -> RegionalSettings:
        """Retrieve the current regional settings, for example the length unit used in the GUI.

        Access: operator.
        """
        return await self._run(OPS.get_regional_settings, None, {}, request_options)

    @overload
    async def set_regional_settings(
        self, request: SetRegionalSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_regional_settings(
        self, /, *, units: Units, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_regional_settings(
        self,
        request: SetRegionalSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the regional settings used in the GUI.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_regional_settings, request, kwargs, request_options)
