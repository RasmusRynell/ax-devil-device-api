# GENERATED from specs/apis/network-video/raid.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Set up and monitor a RAID (status, component devices, sync progress, capabilities, recreate with another level); emits tnsaxis:Storage/RAID events.

Docs: https://developer.axis.com/vapix/network-video/raid-management/
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

RaidLevel = Literal["raid0", "raid1", "raid5", "raid6", "raid10"]
RaidStatus = Literal["active", "degraded", "syncing", "failure"]
ComponentStatus = Literal["connected", "missing", "spare"]


class Component(Model):
    component_id: str = Field(validation_alias="componentId", serialization_alias="componentId")
    """The component device ID. Maps to a hard drive slot."""
    component_status: ComponentStatus = Field(validation_alias="componentStatus", serialization_alias="componentStatus")
    serial_number: str | None = Field(default=None, validation_alias="serialNumber", serialization_alias="serialNumber")
    capacity: int | None = None
    """Capacity in gigabytes."""


class Raid(Model):
    status: RaidStatus
    sync_progress: int | None = Field(
        default=None, validation_alias="syncProgress", serialization_alias="syncProgress", ge=0, le=100
    )
    """Percentage of completion during an active sync. 100 when active and not syncing; 0 when degraded or failed."""
    sync_time_remaining: int | None = Field(
        default=None, validation_alias="syncTimeRemaining", serialization_alias="syncTimeRemaining"
    )
    """Estimated seconds until an active sync finishes; 0 when not syncing."""
    raid_level: RaidLevel | None = Field(default=None, validation_alias="raidLevel", serialization_alias="raidLevel")
    """Configured RAID level."""
    components: list[Component] | None = None


class RaidStatusResult(Model):
    raids: list[Raid]


class Capabilities(Model):
    raid_levels: list[RaidLevel] = Field(validation_alias="raidLevels", serialization_alias="raidLevels")


class RecreateRaidOnAllComponentsRequest(Model):
    raid_level: RaidLevel = Field(validation_alias="raidLevel", serialization_alias="raidLevel")
    """The RAID level. Use ``get_capabilities`` for the supported levels."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/disks/raid.cgi"

INFO = ApiInfo(
    id="raid",
    name="RAID Management",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("raid"),),
    docs=("https://developer.axis.com/vapix/network-video/raid-management/",),
    errors={
        1200: ErrorCode("Generic RAID error.", "internal"),
        1201: ErrorCode("RAID level not supported.", "unsupported"),
        1202: ErrorCode("Component device error.", "internal"),
        1100: ErrorCode("Internal error.", "internal"),
        2101: ErrorCode("Invalid JSON", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
        2106: ErrorCode("Authentication failed.", "access_denied"),
        2107: ErrorCode("Transport level error.", "internal"),
    },
)


class OPS:
    get_status = Operation(
        INFO, "get_status", JsonRpcBinding("getStatus", PATH), result=RaidStatusResult, access="operator", effect="read"
    )
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        result=Capabilities,
        access="operator",
        effect="read",
    )
    recreate_raid_on_all_components = Operation(
        INFO,
        "recreate_raid_on_all_components",
        JsonRpcBinding("recreateRaidOnAllComponents", PATH),
        params=RecreateRaidOnAllComponentsRequest,
        access="admin",
        effect="write",
        write="replace",
    )


# ---------------------------------------------------------------------------
# API classes


class RaidApi(SyncApi):
    """RAID Management (``raid``, version 1)."""

    INFO = INFO

    def get_status(self, *, request_options: RequestOptions | None = None) -> RaidStatusResult:
        """Check the RAID state and its component devices. Access: operator."""
        return self._run(OPS.get_status, None, {}, request_options)

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Retrieve the RAID levels the product supports. Access: operator."""
        return self._run(OPS.get_capabilities, None, {}, request_options)

    def recreate_raid_on_all_components(
        self, raid_level: RaidLevel, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set up a RAID on all available components (destroys the active RAID and its data).

        Stops, destroys and replaces the active RAID with a new one. Unmount the RAID first with the action
        ``unmount`` of ``/axis-cgi/disks/mount.cgi`` (Edge storage API). Creates a logical device in a
        syncing state usable immediately; it must be formatted and mounted. Can create a RAID on fewer
        components as long as the level is supported for that number.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.recreate_raid_on_all_components, None, {"raid_level": raid_level}, request_options)


class AsyncRaidApi(AsyncApi):
    """RAID Management (``raid``, version 1)."""

    INFO = INFO

    async def get_status(self, *, request_options: RequestOptions | None = None) -> RaidStatusResult:
        """Check the RAID state and its component devices. Access: operator."""
        return await self._run(OPS.get_status, None, {}, request_options)

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Retrieve the RAID levels the product supports. Access: operator."""
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    async def recreate_raid_on_all_components(
        self, raid_level: RaidLevel, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set up a RAID on all available components (destroys the active RAID and its data).

        Stops, destroys and replaces the active RAID with a new one. Unmount the RAID first with the action
        ``unmount`` of ``/axis-cgi/disks/mount.cgi`` (Edge storage API). Creates a logical device in a
        syncing state usable immediately; it must be formatted and mounted. Can create a RAID on fewer
        components as long as the level is supported for that number.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.recreate_raid_on_all_components, None, {"raid_level": raid_level}, request_options)
