# GENERATED from specs/apis/device-configuration/network-time-sync-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure how the device uses network protocols (NTP client) to synchronize the system time.

Docs: https://developer.axis.com/vapix/device-configuration/network-time-sync-api/
"""

from __future__ import annotations

from typing import Any, ClassVar, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class NtpClient(Model):
    """Client-specific configuration settings for the NTP protocol, such as polling intervals, server sources and synchronization status. Property types are inferred from the docs example."""

    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {"advertised_servers", "synced", "time_offset", "time_to_next_sync"}
    )
    advertised_servers: list[str] | None = Field(
        default=None, validation_alias="advertisedServers", serialization_alias="advertisedServers"
    )
    """NTP servers in use, for example advertised by DHCP."""
    enabled: bool | None = None
    """Whether the NTP client is enabled (default true)."""
    maximum_poll: int | None = Field(default=None, validation_alias="maximumPoll", serialization_alias="maximumPoll")
    """Maximum polling interval."""
    minimum_poll: int | None = Field(default=None, validation_alias="minimumPoll", serialization_alias="minimumPoll")
    """Minimum polling interval."""
    servers_source: str | None = Field(
        default=None, validation_alias="serversSource", serialization_alias="serversSource"
    )
    """Where the servers come from, for example DHCP."""
    static_servers: list[str] | None = Field(
        default=None, validation_alias="staticServers", serialization_alias="staticServers"
    )
    """Statically configured NTP servers."""
    synced: bool | None = None
    """Whether the clock is synchronized."""
    time_offset: int | None = Field(default=None, validation_alias="timeOffset", serialization_alias="timeOffset")
    """Current time offset."""
    time_to_next_sync: int | None = Field(
        default=None, validation_alias="timeToNextSync", serialization_alias="timeToNextSync"
    )
    """Time to the next synchronization."""


class Ntp(Model):
    """This entity contains properties for the NTP protocol."""

    client: NtpClient | None = None


class NetworkTimeSync(Model):
    """The whole API tree."""

    ntp: Ntp | None = None


class UpdateClientRequest(Model):
    """Arguments of ``update_client``. Only the given settings change."""

    enabled: bool | None = None
    """Whether the NTP client is enabled (default true)."""
    maximum_poll: int | None = Field(default=None, validation_alias="maximumPoll", serialization_alias="maximumPoll")
    """Maximum polling interval."""
    minimum_poll: int | None = Field(default=None, validation_alias="minimumPoll", serialization_alias="minimumPoll")
    """Minimum polling interval."""
    servers_source: str | None = Field(
        default=None, validation_alias="serversSource", serialization_alias="serversSource"
    )
    """Where the servers come from, for example DHCP."""
    static_servers: list[str] | None = Field(
        default=None, validation_alias="staticServers", serialization_alias="staticServers"
    )
    """Statically configured NTP servers."""

    @classmethod
    def from_current(cls, client: NtpClient) -> UpdateClientRequest:
        """A request that rewrites ``client`` unchanged: copy it, edit fields, send it back."""
        data = client.request_data()
        return cls(**data)


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/network-time-sync/v1"

INFO = ApiInfo(
    id="network-time-sync-config",
    name="Network time synchronization configuration API",
    family=Family.DCA,
    discovery=(DcaDiscovery("network-time-sync", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/network-time-sync-api/",),
)


class OPS:
    get_client = Operation(
        INFO, "get_client", DcaBinding("GET", f"{ROOT}/ntp/client"), result=NtpClient, access="admin", effect="read"
    )
    update_client = Operation(
        INFO,
        "update_client",
        DcaBinding("PATCH", f"{ROOT}/ntp/client", body="object"),
        params=UpdateClientRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class NetworkTimeSyncApi(SyncApi):
    """Network time synchronization configuration API (``network-time-sync-config``, v1)."""

    INFO = INFO

    def get_client(self, *, request_options: RequestOptions | None = None) -> NtpClient:
        """Get the NTP client configuration and synchronization status. Access: admin."""
        return self._run(OPS.get_client, None, {}, request_options)

    @overload
    def update_client(
        self, request: UpdateClientRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_client(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        maximum_poll: int | MISSING = MISSING,
        minimum_poll: int | MISSING = MISSING,
        servers_source: str | MISSING = MISSING,
        static_servers: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_client(
        self,
        request: UpdateClientRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the NTP client configuration; only the given settings change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_client, request, kwargs, request_options)


class AsyncNetworkTimeSyncApi(AsyncApi):
    """Network time synchronization configuration API (``network-time-sync-config``, v1)."""

    INFO = INFO

    async def get_client(self, *, request_options: RequestOptions | None = None) -> NtpClient:
        """Get the NTP client configuration and synchronization status. Access: admin."""
        return await self._run(OPS.get_client, None, {}, request_options)

    @overload
    async def update_client(
        self, request: UpdateClientRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_client(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        maximum_poll: int | MISSING = MISSING,
        minimum_poll: int | MISSING = MISSING,
        servers_source: str | MISSING = MISSING,
        static_servers: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_client(
        self,
        request: UpdateClientRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the NTP client configuration; only the given settings change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_client, request, kwargs, request_options)
