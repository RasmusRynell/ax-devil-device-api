# GENERATED from specs/apis/device-configuration/mdnssd-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Enable mDNS-SD, set its friendly name and discover devices that advertise given services on the local network.

Docs: https://developer.axis.com/vapix/device-configuration/mdns-sd-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, ErrorCode, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class DeviceService(Model):
    """A service which a discovered device offers."""

    service_name: str = Field(validation_alias="serviceName", serialization_alias="serviceName")
    """The name of the service."""
    service_port: int = Field(validation_alias="servicePort", serialization_alias="servicePort")
    """The port on which the service may be found."""
    service_txt: str = Field(validation_alias="serviceTxt", serialization_alias="serviceTxt")
    """The text record of the service."""


DeviceServiceList = list[DeviceService]
StringArray = list[str]


class Device(Model):
    """Device found by discovery."""

    device_services: DeviceServiceList = Field(validation_alias="deviceServices", serialization_alias="deviceServices")
    """The services this device offers."""
    friendly_name: str = Field(validation_alias="friendlyName", serialization_alias="friendlyName")
    """The friendlyname of the device."""
    hostname: str
    """The hostname of the device."""
    interface: str
    """On which local interface the device was discovered."""
    ipv4_address: StringArray = Field(validation_alias="ipv4Address", serialization_alias="ipv4Address")
    """A list of IPv4 addresses found on the device."""
    ipv6_address: StringArray = Field(validation_alias="ipv6Address", serialization_alias="ipv6Address")
    """A list of IPv6 addresses found on the device."""


Service = Annotated[
    str, Field(pattern=r"^_[A-Za-z0-9][A-Za-z0-9_-]{0,13}[A-Za-z0-9]\._(udp|tcp)$|^_[A-Za-z0-9]\._(udp|tcp)$")
]
ServiceList = list[Service]
Timeout = Annotated[int, Field(ge=1, le=15)]


class DiscoveryRequest(Model):
    """Arguments of ``discovery``."""

    services: ServiceList | None = None
    """The services to look for during the discovery."""
    timeout: Timeout | None = None
    """The timeout for how many seconds a discovery should last."""


class Mdnssd(Model):
    """The whole API tree."""

    enabled: bool
    """The enabled state for mDNS-SD."""
    friendly_name: str = Field(validation_alias="friendlyName", serialization_alias="friendlyName")
    """The friendly name for mDNS-SD."""


class SetEnabledRequest(Model):
    enabled: bool
    """The enabled state for mDNS-SD."""


class SetFriendlyNameRequest(Model):
    friendly_name: str = Field(validation_alias="friendlyName", serialization_alias="friendlyName")
    """The friendly name for mDNS-SD."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/mdnssd/v2beta"

INFO = ApiInfo(
    id="mdnssd-config",
    name="mDNS-SD Configuration API",
    family=Family.DCA,
    discovery=(DcaDiscovery("mdnssd", "v2"),),
    status="beta",
    docs=("https://developer.axis.com/vapix/device-configuration/mdns-sd-api/",),
    errors={100: ErrorCode("Invalid request. mDNS-SD is disabled during a discovery call.", "invalid_argument")},
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Mdnssd, access="admin", effect="read")
    get_enabled = Operation(
        INFO, "get_enabled", DcaBinding("GET", f"{ROOT}/enabled"), result=bool, access="admin", effect="read"
    )
    get_friendly_name = Operation(
        INFO, "get_friendly_name", DcaBinding("GET", f"{ROOT}/friendlyName"), result=str, access="admin", effect="read"
    )
    set_enabled = Operation(
        INFO,
        "set_enabled",
        DcaBinding("PATCH", f"{ROOT}/enabled", body="value", body_field="enabled"),
        params=SetEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_friendly_name = Operation(
        INFO,
        "set_friendly_name",
        DcaBinding("PATCH", f"{ROOT}/friendlyName", body="value", body_field="friendlyName"),
        params=SetFriendlyNameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    discovery = Operation(
        INFO,
        "discovery",
        DcaBinding("POST", f"{ROOT}/discovery", body="object"),
        params=DiscoveryRequest,
        result=list[Device],
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class MdnssdConfigApi(SyncApi):
    """mDNS-SD Configuration API (``mdnssd-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Mdnssd:
        """All data of the mDNS-SD Configuration API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_enabled(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether mDNS-SD is enabled. Access: admin."""
        return self._run(OPS.get_enabled, None, {}, request_options)

    def get_friendly_name(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the friendly name used for mDNS-SD. Access: admin."""
        return self._run(OPS.get_friendly_name, None, {}, request_options)

    def set_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable mDNS-SD. Changes only the fields given. Access: admin."""
        self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    def set_friendly_name(self, friendly_name: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the friendly name used for mDNS-SD. Changes only the fields given. Access: admin."""
        self._run(OPS.set_friendly_name, None, {"friendly_name": friendly_name}, request_options)

    def discovery(
        self,
        *,
        services: ServiceList | MISSING = MISSING,
        timeout: Timeout | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> list[Device]:
        """Discover devices on the local network that advertise any of the given services.

        Fails with error 100 when mDNS-SD is disabled.

        Access: admin.
        """
        return self._run(OPS.discovery, None, {"services": services, "timeout": timeout}, request_options)


class AsyncMdnssdConfigApi(AsyncApi):
    """mDNS-SD Configuration API (``mdnssd-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Mdnssd:
        """All data of the mDNS-SD Configuration API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_enabled(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether mDNS-SD is enabled. Access: admin."""
        return await self._run(OPS.get_enabled, None, {}, request_options)

    async def get_friendly_name(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the friendly name used for mDNS-SD. Access: admin."""
        return await self._run(OPS.get_friendly_name, None, {}, request_options)

    async def set_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable mDNS-SD. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    async def set_friendly_name(self, friendly_name: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the friendly name used for mDNS-SD. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_friendly_name, None, {"friendly_name": friendly_name}, request_options)

    async def discovery(
        self,
        *,
        services: ServiceList | MISSING = MISSING,
        timeout: Timeout | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> list[Device]:
        """Discover devices on the local network that advertise any of the given services.

        Fails with error 100 when mDNS-SD is disabled.

        Access: admin.
        """
        return await self._run(OPS.discovery, None, {"services": services, "timeout": timeout}, request_options)
