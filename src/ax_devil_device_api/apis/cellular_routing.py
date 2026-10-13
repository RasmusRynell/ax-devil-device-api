# GENERATED from specs/apis/device-configuration/cellular-routing-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Routing, DHCP and port mapping between the cellular WWAN interface and the Ethernet LAN port of a cellular host.

Docs: https://developer.axis.com/vapix/device-configuration/cellular-routing-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

NetworkPort = Annotated[int, Field(ge=0, le=65535)]
PortAlignment = Annotated[int, Field(ge=1, le=100)]
Ipv4Address = Annotated[str, Field(min_length=0, max_length=15)]
MacAddress = Annotated[str, Field(min_length=17, max_length=17)]
ListIndex = Annotated[str, Field(min_length=1, max_length=3, pattern="^[0-9]+$")]
DhcpServerMode = Literal["LOCAL", "PASSTHROUGH"]
MainMode = Literal["DUAL_UPLINK", "WWAN_ROUTING", "DUAL_UPLINK_WWAN_OUT_ONLY"]
PortMapMode = Literal["PRIMARY_CELLULAR_HOST", "PRIMARY_LAN_HOST", "PRIMARY_CELLULAR_HOST_WWAN_OUT_ONLY"]


class IpRange(Model):
    """The first and last IP in a range."""

    first_ip: Ipv4Address = Field(validation_alias="firstIp", serialization_alias="firstIp")
    last_ip: Ipv4Address = Field(validation_alias="lastIp", serialization_alias="lastIp")


class StaticMacIpLease(Model):
    """A static lease tying a MAC address to an IP address."""

    ip: Ipv4Address
    mac_address: MacAddress = Field(validation_alias="macAddress", serialization_alias="macAddress")


class CellularIpv4Info(Model):
    """IPv4 information provided by the cellular network (the UE IP is the publicly visible address)."""

    ue_ip: Ipv4Address | None = Field(default=None, validation_alias="ueIp", serialization_alias="ueIp")
    gateway: Ipv4Address | None = None
    ip_prefix_length: int | None = Field(
        default=None, validation_alias="ipPrefixLength", serialization_alias="ipPrefixLength"
    )
    name_servers: list[Ipv4Address] | None = Field(
        default=None, validation_alias="nameServers", serialization_alias="nameServers"
    )
    """DNS name servers provided by the cellular network."""


class SourceDestinationPort(Model):
    """A mapped port."""

    name: str | None = None
    """The protocol name of the port."""
    source: NetworkPort | None = None
    destination: NetworkPort | None = None


class DestinationPort(Model):
    """A LAN host port."""

    name: str | None = None
    """The protocol name of the port."""
    destination: NetworkPort | None = None


class ConfiguredPortMapping(Model):
    """The configured port mappings of one destination IP."""

    destination_ip: Ipv4Address | None = Field(
        default=None, validation_alias="destinationIp", serialization_alias="destinationIp"
    )
    name: str | None = None
    """The mDNS name of the LAN host. Only filled in when LAN host discovery was requested."""
    ports: list[SourceDestinationPort] | None = None


class ConnectionMonitor(Model):
    """Features to monitor the cellular network connection."""

    auto_recovery: bool = Field(validation_alias="autoRecovery", serialization_alias="autoRecovery")
    """Monitor the cellular data connection and try to recover if it goes down."""


class MacLease(Model):
    """A MAC address for static leases. The first one decides which device gets all ports in ``PRIMARY_LAN_HOST`` mode and the first IP of the range."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"index"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"index"})
    index: ListIndex = Field(default_factory=not_sent)
    mac_address: MacAddress = Field(validation_alias="macAddress", serialization_alias="macAddress")


class DhcpLocalConfig(Model):
    """DHCP server configuration for a private LAN network (``LOCAL`` mode)."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"ip_prefix_length", "server_ip", "static_leases"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"ip_prefix_length", "server_ip", "static_leases"})
    ip_prefix_length: int = Field(
        default_factory=not_sent, validation_alias="ipPrefixLength", serialization_alias="ipPrefixLength"
    )
    """Prefix length of the smallest subnet that contains ipRange. Calculated."""
    ip_range: IpRange = Field(validation_alias="ipRange", serialization_alias="ipRange")
    server_ip: Ipv4Address = Field(
        default_factory=not_sent, validation_alias="serverIp", serialization_alias="serverIp"
    )
    static_leases: list[StaticMacIpLease] = Field(
        default_factory=not_sent, validation_alias="staticLeases", serialization_alias="staticLeases"
    )


class DhcpPassthroughConfig(Model):
    """DHCP configuration that extends the cellular subnet to the LAN (``PASSTHROUGH`` mode). Before the cellular connection is up, ipRange may be empty."""

    __response_required__: ClassVar[frozenset[str]] = frozenset(
        {"ip_prefix_length", "ip_prefix_length_override", "server_ip", "static_leases"}
    )
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {"ip_prefix_length", "ip_prefix_length_override", "server_ip", "static_leases"}
    )
    ip_prefix_length: int = Field(
        default_factory=not_sent, validation_alias="ipPrefixLength", serialization_alias="ipPrefixLength"
    )
    """Prefix length of the DHCP server IP based on the uplink DHCP configuration."""
    ip_prefix_length_override: int = Field(
        default_factory=not_sent,
        validation_alias="ipPrefixLengthOverride",
        serialization_alias="ipPrefixLengthOverride",
    )
    """0 when ipRange fits the cellular subnet; otherwise the expanded prefix length (smaller than ipPrefixLength)."""
    ip_range: IpRange | None = Field(default=None, validation_alias="ipRange", serialization_alias="ipRange")
    server_ip: Ipv4Address = Field(
        default_factory=not_sent, validation_alias="serverIp", serialization_alias="serverIp"
    )
    static_leases: list[StaticMacIpLease] = Field(
        default_factory=not_sent, validation_alias="staticLeases", serialization_alias="staticLeases"
    )


class DhcpServer(Model):
    """DHCP server settings for the LAN port."""

    mode: DhcpServerMode
    server_check_enabled: bool = Field(validation_alias="serverCheckEnabled", serialization_alias="serverCheckEnabled")
    """Check for an existing DHCP server on the LAN network."""
    local_config: DhcpLocalConfig | None = Field(
        default=None, validation_alias="localConfig", serialization_alias="localConfig"
    )
    mac_leases: list[MacLease] | None = Field(
        default=None, validation_alias="macLeases", serialization_alias="macLeases"
    )
    passthrough_config: DhcpPassthroughConfig | None = Field(
        default=None, validation_alias="passthroughConfig", serialization_alias="passthroughConfig"
    )


class MainSettings(Model):
    """The main configuration of cellular routing."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"cellular_ipv4_info"})
    mode: MainMode
    cellular_ipv4_info: CellularIpv4Info | None = Field(
        default=None, validation_alias="cellularIpv4Info", serialization_alias="cellularIpv4Info"
    )


class CellularHostDefaultPort(Model):
    """A default management port of the cellular host. It cannot be added or removed; only the source port can change."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"index", "name", "destination"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"destination", "index", "name"})
    index: ListIndex = Field(default_factory=not_sent)
    name: str = Field(default_factory=not_sent)
    """The protocol name of the port."""
    source: NetworkPort
    destination: NetworkPort = Field(default_factory=not_sent)


class CellularHostPort(Model):
    """A custom port of the cellular host."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"index"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"index"})
    index: ListIndex = Field(default_factory=not_sent)
    name: str
    """The protocol name of the port."""
    source: NetworkPort
    destination: NetworkPort


class CellularHost(Model):
    """Network ports for the cellular host."""

    default_ports: list[CellularHostDefaultPort] | None = Field(
        default=None, validation_alias="defaultPorts", serialization_alias="defaultPorts"
    )
    ports: list[CellularHostPort] | None = None


class LanHostPort(Model):
    """A custom port applied symmetrically to all LAN hosts."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"index"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"index"})
    index: ListIndex = Field(default_factory=not_sent)
    name: str
    """The protocol name of the port."""
    destination: NetworkPort


class LanHost(Model):
    """Network ports for the hosts on the LAN DHCP server network."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"default_ports", "source_max_port"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"default_ports", "source_max_port"})
    default_ports: list[DestinationPort] = Field(
        default_factory=not_sent, validation_alias="defaultPorts", serialization_alias="defaultPorts"
    )
    """Default destination ports applied to all LAN hosts."""
    source_base_port: NetworkPort = Field(validation_alias="sourceBasePort", serialization_alias="sourceBasePort")
    source_max_port: NetworkPort = Field(
        default_factory=not_sent, validation_alias="sourceMaxPort", serialization_alias="sourceMaxPort"
    )
    source_port_list_alignment: PortAlignment = Field(
        validation_alias="sourcePortListAlignment", serialization_alias="sourcePortListAlignment"
    )
    ports: list[LanHostPort] | None = None


class PortMapping(Model):
    """Port mapping configuration for the cellular host and LAN hosts."""

    mode: PortMapMode
    cellular_host: CellularHost | None = Field(
        default=None, validation_alias="cellularHost", serialization_alias="cellularHost"
    )
    lan_host: LanHost | None = Field(default=None, validation_alias="lanHost", serialization_alias="lanHost")


class CellularRouting(Model):
    """The whole API tree."""

    connection_monitor: ConnectionMonitor | None = Field(
        default=None, validation_alias="connectionMonitor", serialization_alias="connectionMonitor"
    )
    dhcp_server: DhcpServer | None = Field(
        default=None, validation_alias="dhcpServer", serialization_alias="dhcpServer"
    )
    main: MainSettings | None = None
    port_mapping: PortMapping | None = Field(
        default=None, validation_alias="portMapping", serialization_alias="portMapping"
    )


class AddMacLeaseRequest(Model):
    """Arguments of ``add_mac_lease``."""

    mac_address: MacAddress = Field(validation_alias="macAddress", serialization_alias="macAddress")

    @classmethod
    def from_current(cls, lease: MacLease) -> AddMacLeaseRequest:
        """A request that rewrites ``lease`` unchanged: copy it, edit fields, send it back."""
        data = lease.request_data()
        return cls(**data)


class AddCellularHostPortRequest(Model):
    """Arguments of ``add_cellular_host_port``."""

    name: str
    """The protocol name of the port."""
    source: NetworkPort
    destination: NetworkPort

    @classmethod
    def from_current(cls, port: CellularHostPort) -> AddCellularHostPortRequest:
        """A request that rewrites ``port`` unchanged: copy it, edit fields, send it back."""
        data = port.request_data()
        return cls(**data)


class AddLanHostPortRequest(Model):
    """Arguments of ``add_lan_host_port``."""

    name: str
    """The protocol name of the port."""
    destination: NetworkPort

    @classmethod
    def from_current(cls, port: LanHostPort) -> AddLanHostPortRequest:
        """A request that rewrites ``port`` unchanged: copy it, edit fields, send it back."""
        data = port.request_data()
        return cls(**data)


class ConfiguredPortMappingsRequest(Model):
    """Arguments of ``get_configured_port_mappings``."""

    include_only_active_ports: bool | None = Field(
        default=None, validation_alias="includeOnlyActivePorts", serialization_alias="includeOnlyActivePorts"
    )
    """Only active mappings (an empty list when ports are inactive, for example in DUAL_UPLINK mode). When false, all potential mappings for the whole DHCP IP range."""
    enable_lan_host_discovery: bool | None = Field(
        default=None, validation_alias="enableLanHostDiscovery", serialization_alias="enableLanHostDiscovery"
    )
    """Look up mDNS names of the connected LAN hosts and fill in the name field of the result."""


class SetConnectionMonitorAutoRecoveryRequest(Model):
    auto_recovery: bool = Field(validation_alias="autoRecovery", serialization_alias="autoRecovery")


class SetDhcpServerModeRequest(Model):
    mode: DhcpServerMode


class SetDhcpServerServerCheckEnabledRequest(Model):
    server_check_enabled: bool = Field(validation_alias="serverCheckEnabled", serialization_alias="serverCheckEnabled")


class SetDhcpLocalConfigIpRangeRequest(Model):
    ip_range: IpRange = Field(validation_alias="ipRange", serialization_alias="ipRange")


class SetDhcpPassthroughConfigIpRangeRequest(Model):
    ip_range: IpRange = Field(validation_alias="ipRange", serialization_alias="ipRange")


class IndexRequest(Model):
    index: ListIndex


class SetMacLeaseMacAddressRequest(Model):
    index: ListIndex
    mac_address: MacAddress = Field(validation_alias="macAddress", serialization_alias="macAddress")


class SetMainModeRequest(Model):
    mode: MainMode


class SetPortMappingModeRequest(Model):
    mode: PortMapMode


class SetCellularHostDefaultPortSourceRequest(Model):
    index: ListIndex
    source: NetworkPort


class SetCellularHostPortDestinationRequest(Model):
    index: ListIndex
    destination: NetworkPort


class SetCellularHostPortNameRequest(Model):
    index: ListIndex
    name: str


class SetCellularHostPortSourceRequest(Model):
    index: ListIndex
    source: NetworkPort


class SetLanHostSourceBasePortRequest(Model):
    source_base_port: NetworkPort = Field(validation_alias="sourceBasePort", serialization_alias="sourceBasePort")


class SetLanHostSourcePortListAlignmentRequest(Model):
    source_port_list_alignment: PortAlignment = Field(
        validation_alias="sourcePortListAlignment", serialization_alias="sourcePortListAlignment"
    )


class SetLanHostPortDestinationRequest(Model):
    index: ListIndex
    destination: NetworkPort


class SetLanHostPortNameRequest(Model):
    index: ListIndex
    name: str


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/cellular-routing/v1beta"

INFO = ApiInfo(
    id="cellular-routing-config",
    name="Cellular routing API",
    family=Family.DCA,
    discovery=(DcaDiscovery("cellular-routing", "v1beta"),),
    docs=("https://developer.axis.com/vapix/device-configuration/cellular-routing-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=CellularRouting, access="operator", effect="read"
    )
    get_connection_monitor = Operation(
        INFO,
        "get_connection_monitor",
        DcaBinding("GET", f"{ROOT}/connectionMonitor"),
        result=ConnectionMonitor,
        access="operator",
        effect="read",
    )
    set_connection_monitor_auto_recovery = Operation(
        INFO,
        "set_connection_monitor_auto_recovery",
        DcaBinding("PATCH", f"{ROOT}/connectionMonitor/autoRecovery", body="value", body_field="autoRecovery"),
        params=SetConnectionMonitorAutoRecoveryRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_dhcp_server = Operation(
        INFO,
        "get_dhcp_server",
        DcaBinding("GET", f"{ROOT}/dhcpServer"),
        result=DhcpServer,
        access="operator",
        effect="read",
    )
    set_dhcp_server_mode = Operation(
        INFO,
        "set_dhcp_server_mode",
        DcaBinding("PATCH", f"{ROOT}/dhcpServer/mode", body="value", body_field="mode"),
        params=SetDhcpServerModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_dhcp_server_server_check_enabled = Operation(
        INFO,
        "set_dhcp_server_server_check_enabled",
        DcaBinding("PATCH", f"{ROOT}/dhcpServer/serverCheckEnabled", body="value", body_field="serverCheckEnabled"),
        params=SetDhcpServerServerCheckEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_dhcp_local_config = Operation(
        INFO,
        "get_dhcp_local_config",
        DcaBinding("GET", f"{ROOT}/dhcpServer/localConfig"),
        result=DhcpLocalConfig,
        access="operator",
        effect="read",
    )
    set_dhcp_local_config_ip_range = Operation(
        INFO,
        "set_dhcp_local_config_ip_range",
        DcaBinding("PATCH", f"{ROOT}/dhcpServer/localConfig/ipRange", body="value", body_field="ipRange"),
        params=SetDhcpLocalConfigIpRangeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_dhcp_passthrough_config = Operation(
        INFO,
        "get_dhcp_passthrough_config",
        DcaBinding("GET", f"{ROOT}/dhcpServer/passthroughConfig"),
        result=DhcpPassthroughConfig,
        access="operator",
        effect="read",
    )
    set_dhcp_passthrough_config_ip_range = Operation(
        INFO,
        "set_dhcp_passthrough_config_ip_range",
        DcaBinding("PATCH", f"{ROOT}/dhcpServer/passthroughConfig/ipRange", body="value", body_field="ipRange"),
        params=SetDhcpPassthroughConfigIpRangeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_mac_leases = Operation(
        INFO,
        "list_mac_leases",
        DcaBinding("GET", f"{ROOT}/dhcpServer/macLeases"),
        result=list[MacLease],
        access="operator",
        effect="read",
    )
    get_mac_lease = Operation(
        INFO,
        "get_mac_lease",
        DcaBinding("GET", f"{ROOT}/dhcpServer/macLeases/{{index}}"),
        params=IndexRequest,
        result=MacLease,
        access="operator",
        effect="read",
    )
    add_mac_lease = Operation(
        INFO,
        "add_mac_lease",
        DcaBinding("POST", f"{ROOT}/dhcpServer/macLeases", body="object"),
        params=AddMacLeaseRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_mac_lease = Operation(
        INFO,
        "remove_mac_lease",
        DcaBinding("DELETE", f"{ROOT}/dhcpServer/macLeases/{{index}}"),
        params=IndexRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_mac_lease_mac_address = Operation(
        INFO,
        "set_mac_lease_mac_address",
        DcaBinding("PATCH", f"{ROOT}/dhcpServer/macLeases/{{index}}/macAddress", body="value", body_field="macAddress"),
        params=SetMacLeaseMacAddressRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_main = Operation(
        INFO, "get_main", DcaBinding("GET", f"{ROOT}/main"), result=MainSettings, access="operator", effect="read"
    )
    set_main_mode = Operation(
        INFO,
        "set_main_mode",
        DcaBinding("PATCH", f"{ROOT}/main/mode", body="value", body_field="mode"),
        params=SetMainModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_port_mapping = Operation(
        INFO,
        "get_port_mapping",
        DcaBinding("GET", f"{ROOT}/portMapping"),
        result=PortMapping,
        access="operator",
        effect="read",
    )
    set_port_mapping_mode = Operation(
        INFO,
        "set_port_mapping_mode",
        DcaBinding("PATCH", f"{ROOT}/portMapping/mode", body="value", body_field="mode"),
        params=SetPortMappingModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_configured_port_mappings = Operation(
        INFO,
        "get_configured_port_mappings",
        DcaBinding("POST", f"{ROOT}/portMapping/getConfiguredPortMappings", body="object"),
        params=ConfiguredPortMappingsRequest,
        result=list[ConfiguredPortMapping],
        access="operator",
        effect="read",
    )
    get_cellular_host = Operation(
        INFO,
        "get_cellular_host",
        DcaBinding("GET", f"{ROOT}/portMapping/cellularHost"),
        result=CellularHost,
        access="operator",
        effect="read",
    )
    list_cellular_host_default_ports = Operation(
        INFO,
        "list_cellular_host_default_ports",
        DcaBinding("GET", f"{ROOT}/portMapping/cellularHost/defaultPorts"),
        result=list[CellularHostDefaultPort],
        access="operator",
        effect="read",
    )
    get_cellular_host_default_port = Operation(
        INFO,
        "get_cellular_host_default_port",
        DcaBinding("GET", f"{ROOT}/portMapping/cellularHost/defaultPorts/{{index}}"),
        params=IndexRequest,
        result=CellularHostDefaultPort,
        access="operator",
        effect="read",
    )
    set_cellular_host_default_port_source = Operation(
        INFO,
        "set_cellular_host_default_port_source",
        DcaBinding(
            "PATCH", f"{ROOT}/portMapping/cellularHost/defaultPorts/{{index}}/source", body="value", body_field="source"
        ),
        params=SetCellularHostDefaultPortSourceRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_cellular_host_ports = Operation(
        INFO,
        "list_cellular_host_ports",
        DcaBinding("GET", f"{ROOT}/portMapping/cellularHost/ports"),
        result=list[CellularHostPort],
        access="operator",
        effect="read",
    )
    get_cellular_host_port = Operation(
        INFO,
        "get_cellular_host_port",
        DcaBinding("GET", f"{ROOT}/portMapping/cellularHost/ports/{{index}}"),
        params=IndexRequest,
        result=CellularHostPort,
        access="operator",
        effect="read",
    )
    add_cellular_host_port = Operation(
        INFO,
        "add_cellular_host_port",
        DcaBinding("POST", f"{ROOT}/portMapping/cellularHost/ports", body="object"),
        params=AddCellularHostPortRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_cellular_host_port = Operation(
        INFO,
        "remove_cellular_host_port",
        DcaBinding("DELETE", f"{ROOT}/portMapping/cellularHost/ports/{{index}}"),
        params=IndexRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_cellular_host_port_destination = Operation(
        INFO,
        "set_cellular_host_port_destination",
        DcaBinding(
            "PATCH",
            f"{ROOT}/portMapping/cellularHost/ports/{{index}}/destination",
            body="value",
            body_field="destination",
        ),
        params=SetCellularHostPortDestinationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_cellular_host_port_name = Operation(
        INFO,
        "set_cellular_host_port_name",
        DcaBinding("PATCH", f"{ROOT}/portMapping/cellularHost/ports/{{index}}/name", body="value", body_field="name"),
        params=SetCellularHostPortNameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_cellular_host_port_source = Operation(
        INFO,
        "set_cellular_host_port_source",
        DcaBinding(
            "PATCH", f"{ROOT}/portMapping/cellularHost/ports/{{index}}/source", body="value", body_field="source"
        ),
        params=SetCellularHostPortSourceRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_lan_host = Operation(
        INFO,
        "get_lan_host",
        DcaBinding("GET", f"{ROOT}/portMapping/lanHost"),
        result=LanHost,
        access="operator",
        effect="read",
    )
    set_lan_host_source_base_port = Operation(
        INFO,
        "set_lan_host_source_base_port",
        DcaBinding("PATCH", f"{ROOT}/portMapping/lanHost/sourceBasePort", body="value", body_field="sourceBasePort"),
        params=SetLanHostSourceBasePortRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_lan_host_source_port_list_alignment = Operation(
        INFO,
        "set_lan_host_source_port_list_alignment",
        DcaBinding(
            "PATCH",
            f"{ROOT}/portMapping/lanHost/sourcePortListAlignment",
            body="value",
            body_field="sourcePortListAlignment",
        ),
        params=SetLanHostSourcePortListAlignmentRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_lan_host_ports = Operation(
        INFO,
        "list_lan_host_ports",
        DcaBinding("GET", f"{ROOT}/portMapping/lanHost/ports"),
        result=list[LanHostPort],
        access="operator",
        effect="read",
    )
    get_lan_host_port = Operation(
        INFO,
        "get_lan_host_port",
        DcaBinding("GET", f"{ROOT}/portMapping/lanHost/ports/{{index}}"),
        params=IndexRequest,
        result=LanHostPort,
        access="operator",
        effect="read",
    )
    add_lan_host_port = Operation(
        INFO,
        "add_lan_host_port",
        DcaBinding("POST", f"{ROOT}/portMapping/lanHost/ports", body="object"),
        params=AddLanHostPortRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_lan_host_port = Operation(
        INFO,
        "remove_lan_host_port",
        DcaBinding("DELETE", f"{ROOT}/portMapping/lanHost/ports/{{index}}"),
        params=IndexRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_lan_host_port_destination = Operation(
        INFO,
        "set_lan_host_port_destination",
        DcaBinding(
            "PATCH", f"{ROOT}/portMapping/lanHost/ports/{{index}}/destination", body="value", body_field="destination"
        ),
        params=SetLanHostPortDestinationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_lan_host_port_name = Operation(
        INFO,
        "set_lan_host_port_name",
        DcaBinding("PATCH", f"{ROOT}/portMapping/lanHost/ports/{{index}}/name", body="value", body_field="name"),
        params=SetLanHostPortNameRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class CellularRoutingApi(SyncApi):
    """Cellular routing API (``cellular-routing-config``, v1beta)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> CellularRouting:
        """The whole API tree. Access: operator."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_connection_monitor(self, *, request_options: RequestOptions | None = None) -> ConnectionMonitor:
        """Get the connection monitor settings. Access: operator."""
        return self._run(OPS.get_connection_monitor, None, {}, request_options)

    def set_connection_monitor_auto_recovery(
        self, *, auto_recovery: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set whether the cellular connection is monitored and recovered.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_connection_monitor_auto_recovery, None, {"auto_recovery": auto_recovery}, request_options)

    def get_dhcp_server(self, *, request_options: RequestOptions | None = None) -> DhcpServer:
        """Get the DHCP server settings. Access: operator."""
        return self._run(OPS.get_dhcp_server, None, {}, request_options)

    def set_dhcp_server_mode(self, *, mode: DhcpServerMode, request_options: RequestOptions | None = None) -> None:
        """Set the DHCP server mode. Changes only the fields given. Access: admin."""
        self._run(OPS.set_dhcp_server_mode, None, {"mode": mode}, request_options)

    def set_dhcp_server_server_check_enabled(
        self, *, server_check_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the check for an existing DHCP server on the LAN.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_dhcp_server_server_check_enabled,
            None,
            {"server_check_enabled": server_check_enabled},
            request_options,
        )

    def get_dhcp_local_config(self, *, request_options: RequestOptions | None = None) -> DhcpLocalConfig:
        """Get the DHCP configuration of LOCAL mode. Access: operator."""
        return self._run(OPS.get_dhcp_local_config, None, {}, request_options)

    @overload
    def set_dhcp_local_config_ip_range(
        self, request: SetDhcpLocalConfigIpRangeRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_dhcp_local_config_ip_range(
        self, /, *, ip_range: IpRange, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_dhcp_local_config_ip_range(
        self,
        request: SetDhcpLocalConfigIpRangeRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the IP range of LOCAL mode. Changes only the fields given. Access: admin."""
        self._run(OPS.set_dhcp_local_config_ip_range, request, kwargs, request_options)

    def get_dhcp_passthrough_config(self, *, request_options: RequestOptions | None = None) -> DhcpPassthroughConfig:
        """Get the DHCP configuration of PASSTHROUGH mode. Access: operator."""
        return self._run(OPS.get_dhcp_passthrough_config, None, {}, request_options)

    @overload
    def set_dhcp_passthrough_config_ip_range(
        self, request: SetDhcpPassthroughConfigIpRangeRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_dhcp_passthrough_config_ip_range(
        self, /, *, ip_range: IpRange, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_dhcp_passthrough_config_ip_range(
        self,
        request: SetDhcpPassthroughConfigIpRangeRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the IP range of PASSTHROUGH mode. Changes only the fields given. Access: admin."""
        self._run(OPS.set_dhcp_passthrough_config_ip_range, request, kwargs, request_options)

    def list_mac_leases(self, *, request_options: RequestOptions | None = None) -> list[MacLease]:
        """List the MAC addresses for static leases. Access: operator."""
        return self._run(OPS.list_mac_leases, None, {}, request_options)

    def get_mac_lease(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> MacLease:
        """Get one MAC address lease. Access: operator."""
        return self._run(OPS.get_mac_lease, None, {"index": index}, request_options)

    def add_mac_lease(self, *, mac_address: MacAddress, request_options: RequestOptions | None = None) -> None:
        """Add a MAC address for static leases. Access: admin."""
        self._run(OPS.add_mac_lease, None, {"mac_address": mac_address}, request_options)

    def remove_mac_lease(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> None:
        """Remove a MAC address lease. Access: admin."""
        self._run(OPS.remove_mac_lease, None, {"index": index}, request_options)

    def set_mac_lease_mac_address(
        self, index: ListIndex, *, mac_address: MacAddress, request_options: RequestOptions | None = None
    ) -> None:
        """Set the MAC address of a lease. Changes only the fields given. Access: admin."""
        self._run(OPS.set_mac_lease_mac_address, None, {"index": index, "mac_address": mac_address}, request_options)

    def get_main(self, *, request_options: RequestOptions | None = None) -> MainSettings:
        """Get the main settings, including the cellular IPv4 information. Access: operator."""
        return self._run(OPS.get_main, None, {}, request_options)

    def set_main_mode(self, *, mode: MainMode, request_options: RequestOptions | None = None) -> None:
        """Set the main mode that controls routing. Changes only the fields given. Access: admin."""
        self._run(OPS.set_main_mode, None, {"mode": mode}, request_options)

    def get_port_mapping(self, *, request_options: RequestOptions | None = None) -> PortMapping:
        """Get the port mapping settings. Access: operator."""
        return self._run(OPS.get_port_mapping, None, {}, request_options)

    def set_port_mapping_mode(self, *, mode: PortMapMode, request_options: RequestOptions | None = None) -> None:
        """Set which host is the primary host. Changes only the fields given. Access: admin."""
        self._run(OPS.set_port_mapping_mode, None, {"mode": mode}, request_options)

    def get_configured_port_mappings(
        self,
        *,
        include_only_active_ports: bool | MISSING = MISSING,
        enable_lan_host_discovery: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> list[ConfiguredPortMapping]:
        """Get the currently configured port mappings. Access: operator."""
        return self._run(
            OPS.get_configured_port_mappings,
            None,
            {
                "include_only_active_ports": include_only_active_ports,
                "enable_lan_host_discovery": enable_lan_host_discovery,
            },
            request_options,
        )

    def get_cellular_host(self, *, request_options: RequestOptions | None = None) -> CellularHost:
        """Get the cellular host ports. Access: operator."""
        return self._run(OPS.get_cellular_host, None, {}, request_options)

    def list_cellular_host_default_ports(
        self, *, request_options: RequestOptions | None = None
    ) -> list[CellularHostDefaultPort]:
        """List the default ports of the cellular host. Access: operator."""
        return self._run(OPS.list_cellular_host_default_ports, None, {}, request_options)

    def get_cellular_host_default_port(
        self, index: ListIndex, *, request_options: RequestOptions | None = None
    ) -> CellularHostDefaultPort:
        """Get one default port of the cellular host. Access: operator."""
        return self._run(OPS.get_cellular_host_default_port, None, {"index": index}, request_options)

    def set_cellular_host_default_port_source(
        self, index: ListIndex, *, source: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the source port of a default cellular host port.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_cellular_host_default_port_source, None, {"index": index, "source": source}, request_options)

    def list_cellular_host_ports(self, *, request_options: RequestOptions | None = None) -> list[CellularHostPort]:
        """List the custom ports of the cellular host. Access: operator."""
        return self._run(OPS.list_cellular_host_ports, None, {}, request_options)

    def get_cellular_host_port(
        self, index: ListIndex, *, request_options: RequestOptions | None = None
    ) -> CellularHostPort:
        """Get one custom port of the cellular host. Access: operator."""
        return self._run(OPS.get_cellular_host_port, None, {"index": index}, request_options)

    def add_cellular_host_port(
        self, *, name: str, source: NetworkPort, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Add a custom port to the cellular host. Access: admin."""
        self._run(
            OPS.add_cellular_host_port,
            None,
            {"name": name, "source": source, "destination": destination},
            request_options,
        )

    def remove_cellular_host_port(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> None:
        """Remove a custom port of the cellular host. Access: admin."""
        self._run(OPS.remove_cellular_host_port, None, {"index": index}, request_options)

    def set_cellular_host_port_destination(
        self, index: ListIndex, *, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the destination port of a custom cellular host port.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_cellular_host_port_destination, None, {"index": index, "destination": destination}, request_options
        )

    def set_cellular_host_port_name(
        self, index: ListIndex, *, name: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the name of a custom cellular host port. Changes only the fields given. Access: admin."""
        self._run(OPS.set_cellular_host_port_name, None, {"index": index, "name": name}, request_options)

    def set_cellular_host_port_source(
        self, index: ListIndex, *, source: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the source port of a custom cellular host port.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_cellular_host_port_source, None, {"index": index, "source": source}, request_options)

    def get_lan_host(self, *, request_options: RequestOptions | None = None) -> LanHost:
        """Get the LAN host port settings. Access: operator."""
        return self._run(OPS.get_lan_host, None, {}, request_options)

    def set_lan_host_source_base_port(
        self, *, source_base_port: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the base source port of the LAN host ports.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_lan_host_source_base_port, None, {"source_base_port": source_base_port}, request_options)

    def set_lan_host_source_port_list_alignment(
        self, *, source_port_list_alignment: PortAlignment, request_options: RequestOptions | None = None
    ) -> None:
        """Set the alignment of the LAN host source port ranges.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_lan_host_source_port_list_alignment,
            None,
            {"source_port_list_alignment": source_port_list_alignment},
            request_options,
        )

    def list_lan_host_ports(self, *, request_options: RequestOptions | None = None) -> list[LanHostPort]:
        """List the custom ports of the LAN hosts. Access: operator."""
        return self._run(OPS.list_lan_host_ports, None, {}, request_options)

    def get_lan_host_port(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> LanHostPort:
        """Get one custom LAN host port. Access: operator."""
        return self._run(OPS.get_lan_host_port, None, {"index": index}, request_options)

    def add_lan_host_port(
        self, *, name: str, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Add a custom port applied to all LAN hosts. Access: admin."""
        self._run(OPS.add_lan_host_port, None, {"name": name, "destination": destination}, request_options)

    def remove_lan_host_port(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> None:
        """Remove a custom LAN host port. Access: admin."""
        self._run(OPS.remove_lan_host_port, None, {"index": index}, request_options)

    def set_lan_host_port_destination(
        self, index: ListIndex, *, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the destination port of a custom LAN host port.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_lan_host_port_destination, None, {"index": index, "destination": destination}, request_options
        )

    def set_lan_host_port_name(
        self, index: ListIndex, *, name: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the name of a custom LAN host port. Changes only the fields given. Access: admin."""
        self._run(OPS.set_lan_host_port_name, None, {"index": index, "name": name}, request_options)


class AsyncCellularRoutingApi(AsyncApi):
    """Cellular routing API (``cellular-routing-config``, v1beta)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> CellularRouting:
        """The whole API tree. Access: operator."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_connection_monitor(self, *, request_options: RequestOptions | None = None) -> ConnectionMonitor:
        """Get the connection monitor settings. Access: operator."""
        return await self._run(OPS.get_connection_monitor, None, {}, request_options)

    async def set_connection_monitor_auto_recovery(
        self, *, auto_recovery: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set whether the cellular connection is monitored and recovered.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_connection_monitor_auto_recovery, None, {"auto_recovery": auto_recovery}, request_options
        )

    async def get_dhcp_server(self, *, request_options: RequestOptions | None = None) -> DhcpServer:
        """Get the DHCP server settings. Access: operator."""
        return await self._run(OPS.get_dhcp_server, None, {}, request_options)

    async def set_dhcp_server_mode(
        self, *, mode: DhcpServerMode, request_options: RequestOptions | None = None
    ) -> None:
        """Set the DHCP server mode. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_dhcp_server_mode, None, {"mode": mode}, request_options)

    async def set_dhcp_server_server_check_enabled(
        self, *, server_check_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the check for an existing DHCP server on the LAN.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_dhcp_server_server_check_enabled,
            None,
            {"server_check_enabled": server_check_enabled},
            request_options,
        )

    async def get_dhcp_local_config(self, *, request_options: RequestOptions | None = None) -> DhcpLocalConfig:
        """Get the DHCP configuration of LOCAL mode. Access: operator."""
        return await self._run(OPS.get_dhcp_local_config, None, {}, request_options)

    @overload
    async def set_dhcp_local_config_ip_range(
        self, request: SetDhcpLocalConfigIpRangeRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_dhcp_local_config_ip_range(
        self, /, *, ip_range: IpRange, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_dhcp_local_config_ip_range(
        self,
        request: SetDhcpLocalConfigIpRangeRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the IP range of LOCAL mode. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_dhcp_local_config_ip_range, request, kwargs, request_options)

    async def get_dhcp_passthrough_config(
        self, *, request_options: RequestOptions | None = None
    ) -> DhcpPassthroughConfig:
        """Get the DHCP configuration of PASSTHROUGH mode. Access: operator."""
        return await self._run(OPS.get_dhcp_passthrough_config, None, {}, request_options)

    @overload
    async def set_dhcp_passthrough_config_ip_range(
        self, request: SetDhcpPassthroughConfigIpRangeRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_dhcp_passthrough_config_ip_range(
        self, /, *, ip_range: IpRange, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_dhcp_passthrough_config_ip_range(
        self,
        request: SetDhcpPassthroughConfigIpRangeRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the IP range of PASSTHROUGH mode. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_dhcp_passthrough_config_ip_range, request, kwargs, request_options)

    async def list_mac_leases(self, *, request_options: RequestOptions | None = None) -> list[MacLease]:
        """List the MAC addresses for static leases. Access: operator."""
        return await self._run(OPS.list_mac_leases, None, {}, request_options)

    async def get_mac_lease(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> MacLease:
        """Get one MAC address lease. Access: operator."""
        return await self._run(OPS.get_mac_lease, None, {"index": index}, request_options)

    async def add_mac_lease(self, *, mac_address: MacAddress, request_options: RequestOptions | None = None) -> None:
        """Add a MAC address for static leases. Access: admin."""
        await self._run(OPS.add_mac_lease, None, {"mac_address": mac_address}, request_options)

    async def remove_mac_lease(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> None:
        """Remove a MAC address lease. Access: admin."""
        await self._run(OPS.remove_mac_lease, None, {"index": index}, request_options)

    async def set_mac_lease_mac_address(
        self, index: ListIndex, *, mac_address: MacAddress, request_options: RequestOptions | None = None
    ) -> None:
        """Set the MAC address of a lease. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_mac_lease_mac_address, None, {"index": index, "mac_address": mac_address}, request_options
        )

    async def get_main(self, *, request_options: RequestOptions | None = None) -> MainSettings:
        """Get the main settings, including the cellular IPv4 information. Access: operator."""
        return await self._run(OPS.get_main, None, {}, request_options)

    async def set_main_mode(self, *, mode: MainMode, request_options: RequestOptions | None = None) -> None:
        """Set the main mode that controls routing. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_main_mode, None, {"mode": mode}, request_options)

    async def get_port_mapping(self, *, request_options: RequestOptions | None = None) -> PortMapping:
        """Get the port mapping settings. Access: operator."""
        return await self._run(OPS.get_port_mapping, None, {}, request_options)

    async def set_port_mapping_mode(self, *, mode: PortMapMode, request_options: RequestOptions | None = None) -> None:
        """Set which host is the primary host. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_port_mapping_mode, None, {"mode": mode}, request_options)

    async def get_configured_port_mappings(
        self,
        *,
        include_only_active_ports: bool | MISSING = MISSING,
        enable_lan_host_discovery: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> list[ConfiguredPortMapping]:
        """Get the currently configured port mappings. Access: operator."""
        return await self._run(
            OPS.get_configured_port_mappings,
            None,
            {
                "include_only_active_ports": include_only_active_ports,
                "enable_lan_host_discovery": enable_lan_host_discovery,
            },
            request_options,
        )

    async def get_cellular_host(self, *, request_options: RequestOptions | None = None) -> CellularHost:
        """Get the cellular host ports. Access: operator."""
        return await self._run(OPS.get_cellular_host, None, {}, request_options)

    async def list_cellular_host_default_ports(
        self, *, request_options: RequestOptions | None = None
    ) -> list[CellularHostDefaultPort]:
        """List the default ports of the cellular host. Access: operator."""
        return await self._run(OPS.list_cellular_host_default_ports, None, {}, request_options)

    async def get_cellular_host_default_port(
        self, index: ListIndex, *, request_options: RequestOptions | None = None
    ) -> CellularHostDefaultPort:
        """Get one default port of the cellular host. Access: operator."""
        return await self._run(OPS.get_cellular_host_default_port, None, {"index": index}, request_options)

    async def set_cellular_host_default_port_source(
        self, index: ListIndex, *, source: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the source port of a default cellular host port.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_cellular_host_default_port_source, None, {"index": index, "source": source}, request_options
        )

    async def list_cellular_host_ports(
        self, *, request_options: RequestOptions | None = None
    ) -> list[CellularHostPort]:
        """List the custom ports of the cellular host. Access: operator."""
        return await self._run(OPS.list_cellular_host_ports, None, {}, request_options)

    async def get_cellular_host_port(
        self, index: ListIndex, *, request_options: RequestOptions | None = None
    ) -> CellularHostPort:
        """Get one custom port of the cellular host. Access: operator."""
        return await self._run(OPS.get_cellular_host_port, None, {"index": index}, request_options)

    async def add_cellular_host_port(
        self, *, name: str, source: NetworkPort, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Add a custom port to the cellular host. Access: admin."""
        await self._run(
            OPS.add_cellular_host_port,
            None,
            {"name": name, "source": source, "destination": destination},
            request_options,
        )

    async def remove_cellular_host_port(
        self, index: ListIndex, *, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a custom port of the cellular host. Access: admin."""
        await self._run(OPS.remove_cellular_host_port, None, {"index": index}, request_options)

    async def set_cellular_host_port_destination(
        self, index: ListIndex, *, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the destination port of a custom cellular host port.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_cellular_host_port_destination, None, {"index": index, "destination": destination}, request_options
        )

    async def set_cellular_host_port_name(
        self, index: ListIndex, *, name: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the name of a custom cellular host port. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_cellular_host_port_name, None, {"index": index, "name": name}, request_options)

    async def set_cellular_host_port_source(
        self, index: ListIndex, *, source: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the source port of a custom cellular host port.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_cellular_host_port_source, None, {"index": index, "source": source}, request_options)

    async def get_lan_host(self, *, request_options: RequestOptions | None = None) -> LanHost:
        """Get the LAN host port settings. Access: operator."""
        return await self._run(OPS.get_lan_host, None, {}, request_options)

    async def set_lan_host_source_base_port(
        self, *, source_base_port: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the base source port of the LAN host ports.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_lan_host_source_base_port, None, {"source_base_port": source_base_port}, request_options
        )

    async def set_lan_host_source_port_list_alignment(
        self, *, source_port_list_alignment: PortAlignment, request_options: RequestOptions | None = None
    ) -> None:
        """Set the alignment of the LAN host source port ranges.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_lan_host_source_port_list_alignment,
            None,
            {"source_port_list_alignment": source_port_list_alignment},
            request_options,
        )

    async def list_lan_host_ports(self, *, request_options: RequestOptions | None = None) -> list[LanHostPort]:
        """List the custom ports of the LAN hosts. Access: operator."""
        return await self._run(OPS.list_lan_host_ports, None, {}, request_options)

    async def get_lan_host_port(
        self, index: ListIndex, *, request_options: RequestOptions | None = None
    ) -> LanHostPort:
        """Get one custom LAN host port. Access: operator."""
        return await self._run(OPS.get_lan_host_port, None, {"index": index}, request_options)

    async def add_lan_host_port(
        self, *, name: str, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Add a custom port applied to all LAN hosts. Access: admin."""
        await self._run(OPS.add_lan_host_port, None, {"name": name, "destination": destination}, request_options)

    async def remove_lan_host_port(self, index: ListIndex, *, request_options: RequestOptions | None = None) -> None:
        """Remove a custom LAN host port. Access: admin."""
        await self._run(OPS.remove_lan_host_port, None, {"index": index}, request_options)

    async def set_lan_host_port_destination(
        self, index: ListIndex, *, destination: NetworkPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the destination port of a custom LAN host port.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_lan_host_port_destination, None, {"index": index, "destination": destination}, request_options
        )

    async def set_lan_host_port_name(
        self, index: ListIndex, *, name: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the name of a custom LAN host port. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_lan_host_port_name, None, {"index": index, "name": name}, request_options)
