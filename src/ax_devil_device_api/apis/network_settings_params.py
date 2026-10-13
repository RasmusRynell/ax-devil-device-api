# GENERATED from specs/apis/network-video/network-settings.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""``param.cgi`` network parameters (``Network``, ``SNMP``): IPv4/IPv6, DNS, DNS update, Bonjour, UPnP, IP filter, 802.1X, QoS, RTP/RTSP, ZeroConf and SNMP.

Docs: https://developer.axis.com/vapix/network-video/network-settings/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListParametersRequest(Model):
    group: list[str] = Field(min_length=1)
    """Parameter groups to list, e.g. ``Network`` or ``SNMP``."""


class UpdateParametersRequest(Model):
    parameters: dict[str, str]


class SetDnsNameRequest(Model):
    dns_name: str = Field(validation_alias="Network.DNSUpdate.DNSName", serialization_alias="Network.DNSUpdate.DNSName")
    """Fully qualified domain name or host name that the DNS server associates with the product's IP address."""


class RequestDnsUpdateRequest(Model):
    add: str
    """The DNS name to add; the name set with ``set_dns_name``."""
    hdgen: Literal["yes"] | None = None
    """Shown as ``hdgen=yes`` in the docs example; its meaning is not documented."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="network-settings",
    name="Network settings",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    requires_firmware="5.00",
    docs=("https://developer.axis.com/vapix/network-video/network-settings/",),
)


class OPS:
    list_parameters = Operation(
        INFO,
        "list_parameters",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListParametersRequest,
        result=dict[str, str],
        access="admin",
        effect="read",
    )
    update_parameters = Operation(
        INFO,
        "update_parameters",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=UpdateParametersRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_dns_name = Operation(
        INFO,
        "set_dns_name",
        CgiBinding(
            PATH,
            fixed_query=(("action", "update"),),
            args=(CgiArg("dns_name", wire="Network.DNSUpdate.DNSName"),),
            reply=TextOk(),
        ),
        params=SetDnsNameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    request_dns_update = Operation(
        INFO,
        "request_dns_update",
        CgiBinding("/axis-cgi/dnsupdate.cgi", args=(CgiArg("add"), CgiArg("hdgen")), reply=Text()),
        params=RequestDnsUpdateRequest,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class NetworkSettingsParamsApi(SyncApi):
    """Network settings (``network-settings``)."""

    INFO = INFO

    def list_parameters(self, group: list[str], *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Network parameters as ``{"Network.Bonjour.Enabled": "yes"}`` (``root.`` removed).

        Groups: ``Network`` (static interface settings, ``BootProto``, ...), ``Network.ARPPingIPAddress``,
        ``Network.Bonjour``, ``Network.DNSUpdate``, ``Network.eth0`` (and ``.IPv6``), ``Network.Filter``
        (and ``.Input``, ``.Log``), ``Network.HTTP.AuthenticationPolicy``, ``Network.Interface.I0.dot1x``
        (and ``.EAPTLS``), ``Network.IPv6``, ``Network.QoS.Class1`` to ``Class4``, ``Network.Resolver``,
        ``Network.Routing`` (and ``.IPv6``), ``Network.RTP`` (and ``.R#``), ``Network.RTSP``,
        ``Network.UPnP`` (and ``.NATTraversal``), ``Network.VolatileHostName``, ``Network.ZeroConf`` and
        ``SNMP`` (with ``.Trap``, ``.Trap.T#`` and its events, and ``.NTCIP``). With ``BootProto=dhcp`` the
        static settings may not be in use; read the read-only subgroups for the settings in effect.

        Access: admin.
        """
        return self._run(OPS.list_parameters, None, {"group": group}, request_options)

    def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set network or SNMP parameters, e.g. ``{"Network.Bonjour.Enabled": "no"}``.

        Only the given parameters change. To change the DNS name use ``set_dns_name`` and
        ``request_dns_update``; setting only ``Network.DNSUpdate.DNSName`` does not trigger a DNS update.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)

    def set_dns_name(self, dns_name: str, *, request_options: RequestOptions | None = None) -> None:
        """Step 1 of a DNS name update: set ``Network.DNSUpdate.DNSName``.

        Follow with ``request_dns_update`` to make the device send the update to the DNS server.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_dns_name, None, {"dns_name": dns_name}, request_options)

    def request_dns_update(
        self, add: str, *, hdgen: Literal["yes"] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Step 2 of a DNS name update: send a new DNS update request to the DNS server.

        Access: admin.
        """
        self._run(OPS.request_dns_update, None, {"add": add, "hdgen": hdgen}, request_options)


class AsyncNetworkSettingsParamsApi(AsyncApi):
    """Network settings (``network-settings``)."""

    INFO = INFO

    async def list_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Network parameters as ``{"Network.Bonjour.Enabled": "yes"}`` (``root.`` removed).

        Groups: ``Network`` (static interface settings, ``BootProto``, ...), ``Network.ARPPingIPAddress``,
        ``Network.Bonjour``, ``Network.DNSUpdate``, ``Network.eth0`` (and ``.IPv6``), ``Network.Filter``
        (and ``.Input``, ``.Log``), ``Network.HTTP.AuthenticationPolicy``, ``Network.Interface.I0.dot1x``
        (and ``.EAPTLS``), ``Network.IPv6``, ``Network.QoS.Class1`` to ``Class4``, ``Network.Resolver``,
        ``Network.Routing`` (and ``.IPv6``), ``Network.RTP`` (and ``.R#``), ``Network.RTSP``,
        ``Network.UPnP`` (and ``.NATTraversal``), ``Network.VolatileHostName``, ``Network.ZeroConf`` and
        ``SNMP`` (with ``.Trap``, ``.Trap.T#`` and its events, and ``.NTCIP``). With ``BootProto=dhcp`` the
        static settings may not be in use; read the read-only subgroups for the settings in effect.

        Access: admin.
        """
        return await self._run(OPS.list_parameters, None, {"group": group}, request_options)

    async def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set network or SNMP parameters, e.g. ``{"Network.Bonjour.Enabled": "no"}``.

        Only the given parameters change. To change the DNS name use ``set_dns_name`` and
        ``request_dns_update``; setting only ``Network.DNSUpdate.DNSName`` does not trigger a DNS update.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)

    async def set_dns_name(self, dns_name: str, *, request_options: RequestOptions | None = None) -> None:
        """Step 1 of a DNS name update: set ``Network.DNSUpdate.DNSName``.

        Follow with ``request_dns_update`` to make the device send the update to the DNS server.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_dns_name, None, {"dns_name": dns_name}, request_options)

    async def request_dns_update(
        self, add: str, *, hdgen: Literal["yes"] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Step 2 of a DNS name update: send a new DNS update request to the DNS server.

        Access: admin.
        """
        await self._run(OPS.request_dns_update, None, {"add": add, "hdgen": hdgen}, request_options)
