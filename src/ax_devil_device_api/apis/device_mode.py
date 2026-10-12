# GENERATED from specs/apis/device-configuration/device-mode-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List the available device modes, read the active and pending mode, and select the mode to switch to.

Docs: https://developer.axis.com/vapix/device-configuration/device-mode-configuration-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ModeId = Annotated[str, Field(min_length=2, max_length=32, pattern="^[a-z][a-z0-9-]*$")]


class AvailableMode(Model):
    """The `availableModes` entity collection contains all device modes that are available on the device. Each mode is accessed by its ID (`fisheye`, `double-panorama`, etc.)."""

    id: ModeId
    """The device mode identifier (short descriptive string)"""


class DeviceMode(Model):
    """The whole API tree."""

    active_mode: ModeId | None = Field(default=None, validation_alias="activeMode", serialization_alias="activeMode")
    """The device mode that is currently active"""
    mode: ModeId | None = None
    """The pending device mode if different from activeMode, otherwise same as activeMode"""
    restart_required: bool | None = Field(
        default=None, validation_alias="restartRequired", serialization_alias="restartRequired"
    )
    """Indicates if a restart is required to apply the mode change. This is typically true for current implementations."""
    available_modes: dict[str, AvailableMode] | None = Field(
        default=None, validation_alias="availableModes", serialization_alias="availableModes"
    )
    """Available modes keyed by mode id."""


class SetModeRequest(Model):
    mode: ModeId
    """The pending device mode if different from activeMode, otherwise same as activeMode"""


class AvailableModeIdRequest(Model):
    id: ModeId


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/device-mode/v1beta"

INFO = ApiInfo(
    id="device-mode-config",
    name="Device mode configuration",
    family=Family.DCA,
    discovery=(DcaDiscovery("device-mode", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/device-mode-configuration-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=DeviceMode, access="admin", effect="read")
    get_mode = Operation(INFO, "get_mode", DcaBinding("GET", f"{ROOT}/mode"), result=str, access="admin", effect="read")
    get_active_mode = Operation(
        INFO, "get_active_mode", DcaBinding("GET", f"{ROOT}/activeMode"), result=str, access="admin", effect="read"
    )
    get_restart_required = Operation(
        INFO,
        "get_restart_required",
        DcaBinding("GET", f"{ROOT}/restartRequired"),
        result=bool,
        access="admin",
        effect="read",
    )
    set_mode = Operation(
        INFO,
        "set_mode",
        DcaBinding("PATCH", f"{ROOT}/mode", body="value", body_field="mode"),
        params=SetModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_available_modes = Operation(
        INFO,
        "list_available_modes",
        DcaBinding("GET", f"{ROOT}/availableModes"),
        result=dict[str, AvailableMode],
        access="admin",
        effect="read",
    )
    get_available_mode = Operation(
        INFO,
        "get_available_mode",
        DcaBinding("GET", f"{ROOT}/availableModes/{{id}}"),
        params=AvailableModeIdRequest,
        result=AvailableMode,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class DeviceModeApi(SyncApi):
    """Device mode configuration (``device-mode-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> DeviceMode:
        """All data of the Device mode configuration API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_mode(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the pending device mode. Access: admin."""
        return self._run(OPS.get_mode, None, {}, request_options)

    def get_active_mode(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the device mode that is currently running. Access: admin."""
        return self._run(OPS.get_active_mode, None, {}, request_options)

    def get_restart_required(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether a restart is needed for the pending mode to take effect. Access: admin."""
        return self._run(OPS.get_restart_required, None, {}, request_options)

    def set_mode(self, mode: ModeId, *, request_options: RequestOptions | None = None) -> None:
        """Set the pending device mode.

        The mode becomes active after a restart when restartRequired is true. Setting the mode back to the
        active mode reverts a pending change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_mode, None, {"mode": mode}, request_options)

    def list_available_modes(self, *, request_options: RequestOptions | None = None) -> dict[str, AvailableMode]:
        """List the available modes. Access: admin."""
        return self._run(OPS.list_available_modes, None, {}, request_options)

    def get_available_mode(self, id: ModeId, *, request_options: RequestOptions | None = None) -> AvailableMode:
        """Get one available mode. Access: admin."""
        return self._run(OPS.get_available_mode, None, {"id": id}, request_options)


class AsyncDeviceModeApi(AsyncApi):
    """Device mode configuration (``device-mode-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> DeviceMode:
        """All data of the Device mode configuration API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_mode(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the pending device mode. Access: admin."""
        return await self._run(OPS.get_mode, None, {}, request_options)

    async def get_active_mode(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the device mode that is currently running. Access: admin."""
        return await self._run(OPS.get_active_mode, None, {}, request_options)

    async def get_restart_required(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether a restart is needed for the pending mode to take effect. Access: admin."""
        return await self._run(OPS.get_restart_required, None, {}, request_options)

    async def set_mode(self, mode: ModeId, *, request_options: RequestOptions | None = None) -> None:
        """Set the pending device mode.

        The mode becomes active after a restart when restartRequired is true. Setting the mode back to the
        active mode reverts a pending change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_mode, None, {"mode": mode}, request_options)

    async def list_available_modes(self, *, request_options: RequestOptions | None = None) -> dict[str, AvailableMode]:
        """List the available modes. Access: admin."""
        return await self._run(OPS.list_available_modes, None, {}, request_options)

    async def get_available_mode(self, id: ModeId, *, request_options: RequestOptions | None = None) -> AvailableMode:
        """Get one available mode. Access: admin."""
        return await self._run(OPS.get_available_mode, None, {"id": id}, request_options)
