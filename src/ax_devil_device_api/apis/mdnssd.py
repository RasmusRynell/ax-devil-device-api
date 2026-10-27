# GENERATED from specs/apis/network-video/mdnssd.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the mDNS-SD (Bonjour) service (enabled state, friendly name) and discover mDNS-SD services on the network via /axis-cgi/mdnssd.cgi.

Docs: https://developer.axis.com/vapix/network-video/mdns-sd-api/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class MdnssdInfo(Model):
    enabled: bool
    """Whether the mDNS-SD service is enabled and running."""
    friendly_name: str = Field(validation_alias="friendlyName", serialization_alias="friendlyName")
    """The friendly name used when responding to discover queries."""


class Service(Model):
    name: str
    """The name of the service."""
    port: int
    """The port on which the service may be found."""
    txt: str | None = None
    """The text record of the service."""


class DiscoveredDevice(Model):
    friendly_name: str | None = Field(default=None, validation_alias="friendlyName", serialization_alias="friendlyName")
    hostname: str | None = None
    interface: str | None = None
    """The network interface on which the device was discovered."""
    ipv4_addresses: list[str] | None = Field(
        default=None, validation_alias="ipv4Addresses", serialization_alias="ipv4Addresses"
    )
    ipv6_addresses: list[str] | None = Field(
        default=None, validation_alias="ipv6Addresses", serialization_alias="ipv6Addresses"
    )
    services: list[Service] | None = None


class DiscoverResult(Model):
    devices: list[DiscoveredDevice]


class SetMdnssdConfigurationRequest(Model):
    enabled: bool | None = None
    """*Optional*. Specifies the desired enabled state of the mDNS-SD service. `true` means that the service is enabled and running, `false` that it is disabled and not running."""
    friendly_name: str | None = Field(
        default=None, validation_alias="friendlyName", serialization_alias="friendlyName", max_length=48
    )
    """*Optional*. The friendly name the mDNS-SD service should use when responding to a discovery query. This string is limited to a maximum size of 48 bytes."""


class DiscoverRequest(Model):
    services: list[str]
    """The list of services, wherein at least one must be in the DNS SRV record format."""
    timeout: int = Field(ge=1, le=15)
    """The timeout for the discover services procedure that must be between 1–15 seconds. (unit=seconds)"""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/mdnssd.cgi"

INFO = ApiInfo(
    id="mdnssd",
    name="mDNS-SD API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1)),
    discovery=(ApiDiscovery("mdnssd"),),
    docs=("https://developer.axis.com/vapix/network-video/mdns-sd-api/",),
    errors={
        1000: ErrorCode("Internal error", "internal"),
        2000: ErrorCode("Invalid request", "invalid_argument"),
        2001: ErrorCode("Request body too large", "invalid_argument"),
        3000: ErrorCode("Invalid JSON data", "invalid_argument"),
        4000: ErrorCode("Method does not exist", "not_found"),
        4001: ErrorCode("The specified version is not supported", "unsupported"),
        4002: ErrorCode("Authorization failed", "access_denied"),
        4003: ErrorCode("Missing parameter(s)", "invalid_argument"),
        4004: ErrorCode("Invalid parameter(s)", "invalid_argument"),
    },
)


class OPS:
    get_mdnssd_info = Operation(
        INFO, "get_mdnssd_info", JsonRpcBinding("getMdnssdInfo", PATH), result=MdnssdInfo, access="admin", effect="read"
    )
    set_mdnssd_configuration = Operation(
        INFO,
        "set_mdnssd_configuration",
        JsonRpcBinding("setMdnssdConfiguration", PATH),
        params=SetMdnssdConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "4004/subCode 1": ErrorCode("The invalid parameter is enabled.", "invalid_argument"),
            "4004/subCode 2": ErrorCode("The invalid parameter is friendlyName.", "invalid_argument"),
        },
    )
    discover = Operation(
        INFO,
        "discover",
        JsonRpcBinding("discover", PATH),
        params=DiscoverRequest,
        result=DiscoverResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 1),
    )


# ---------------------------------------------------------------------------
# API classes


class MdnssdApi(SyncApi):
    """mDNS-SD API (``mdnssd``, version 1)."""

    INFO = INFO

    def get_mdnssd_info(self, *, request_options: RequestOptions | None = None) -> MdnssdInfo:
        """Retrieve the mDNS-SD configuration: enabled state and friendly name used when responding to discover queries.

        Access: admin.
        """
        return self._run(OPS.get_mdnssd_info, None, {}, request_options)

    def set_mdnssd_configuration(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        friendly_name: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the enabled state of the mDNS-SD service and the friendly name.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_mdnssd_configuration, None, {"enabled": enabled, "friendly_name": friendly_name}, request_options
        )

    def discover(
        self, *, services: list[str], timeout: int, request_options: RequestOptions | None = None
    ) -> DiscoverResult:
        """Discover devices on the network exposing the specified mDNS-SD services; returns after the timeout.

        Access: admin.
        """
        return self._run(OPS.discover, None, {"services": services, "timeout": timeout}, request_options)


class AsyncMdnssdApi(AsyncApi):
    """mDNS-SD API (``mdnssd``, version 1)."""

    INFO = INFO

    async def get_mdnssd_info(self, *, request_options: RequestOptions | None = None) -> MdnssdInfo:
        """Retrieve the mDNS-SD configuration: enabled state and friendly name used when responding to discover queries.

        Access: admin.
        """
        return await self._run(OPS.get_mdnssd_info, None, {}, request_options)

    async def set_mdnssd_configuration(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        friendly_name: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the enabled state of the mDNS-SD service and the friendly name.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_mdnssd_configuration, None, {"enabled": enabled, "friendly_name": friendly_name}, request_options
        )

    async def discover(
        self, *, services: list[str], timeout: int, request_options: RequestOptions | None = None
    ) -> DiscoverResult:
        """Discover devices on the network exposing the specified mDNS-SD services; returns after the timeout.

        Access: admin.
        """
        return await self._run(OPS.discover, None, {"services": services, "timeout": timeout}, request_options)
