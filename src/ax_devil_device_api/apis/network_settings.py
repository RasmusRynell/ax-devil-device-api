# GENERATED from specs/apis/device-configuration/network-settings-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the hostname and resolver, the wired uplink and VLANs, the switch ports, and manage the modem, SIM cards and cellular connection.

Docs: https://developer.axis.com/vapix/device-configuration/network-settings-api/
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

AccessPointName = Annotated[str, Field(min_length=0, max_length=100, pattern="^[a-zA-Z0-9.-]*$")]
CellularConnectionStatus = Literal["NOT_REGISTERED", "REGISTERED", "DATA_ENABLED", "IP_ASSIGNED"]
DomainName = str
Hostname = Annotated[
    str, Field(min_length=1, max_length=63, pattern="^[a-zA-Z]$|^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$")
]
Iccid = str
Imei = Annotated[str, Field(min_length=15, max_length=15)]
IpAddress = str
Ipv4Address = Annotated[
    str,
    Field(
        pattern=r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$"
    ),
]
AuthServerEnforced = Literal["NONE", "AUTHENTICATED", "MACSEC_SECURED"]
AuthState = Literal["UNKNOWN", "AUTHENTICATED", "AUTHENTICATING", "STOPPED", "FAILED"]
LinkMode = Literal["UNKNOWN", "AUTO", "10HD", "10FD", "100HD", "100FD", "1000HD", "1000FD"]
LinkModes = list[LinkMode]
MacAddress = Annotated[str, Field(pattern="^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$")]
MacSecState = Literal["UNKNOWN", "SECURED", "CONNECTING", "STOPPED", "FAILED"]
Mtu = int
NameServers = Annotated[list[IpAddress], Field(max_length=3)]
RadioGeneration = Literal["4G", "5G"]
RadioInterface = Literal["4G", "5GSA", "5GNSA", "UNKNOWN"]
SignalStrengthIndex = Annotated[int, Field(ge=-1, le=4)]


class SignalStrength(Model):
    """The signal strength object."""

    rsrp: int
    """The Reference Signal Received Power (in dBm)."""
    rsrq: int
    """The Reference Signal Received Quality (in dB)."""
    rssi: int
    """The Received Signal Strength Indicator (in dBm)."""
    snr: int
    """The Signal to noise ratio (in dB)."""
    ssi: SignalStrengthIndex
    """The Signal Strength Index."""


class RadioParameters(Model):
    """The radio parameter object."""

    band: int
    """The radio band class."""
    bandwidth: int
    """The bandwidth (in MHz)."""
    downlink_modulation_coding_scheme: int = Field(
        validation_alias="downlinkModulationCodingScheme", serialization_alias="downlinkModulationCodingScheme"
    )
    """Typically 0-31 for 5G and 0-28 for 4G. Higher value means better signal quality and higher potential data rates."""
    physical_cell_id: int = Field(validation_alias="physicalCellId", serialization_alias="physicalCellId")
    """The physical cell ID."""
    signal_strength: SignalStrength = Field(validation_alias="signalStrength", serialization_alias="signalStrength")
    """The signal strength parameters."""
    tx_power: int = Field(validation_alias="txPower", serialization_alias="txPower")
    """The transmit power (in dBm/10)."""
    uplink_modulation_coding_scheme: int = Field(
        validation_alias="uplinkModulationCodingScheme", serialization_alias="uplinkModulationCodingScheme"
    )
    """Typically 0-31 for 5G and 0-28 for 4G. Higher value means better signal quality and higher potential data rates."""


RemoteAddresses = list[MacAddress]
SearchDomains = Annotated[list[DomainName], Field(max_length=6)]
SimPin = Annotated[str, Field(min_length=4, max_length=8, pattern="^[0-9]+$")]
SimPuk = Annotated[str, Field(min_length=8, max_length=8, pattern="^[0-9]+$")]
SimSlotId = Annotated[str, Field(min_length=1, max_length=2, pattern="^[0-9]+$")]
SimStatus = Literal["PIN_DISABLED", "UNLOCKED", "LOCKED", "BLOCKED", "PERMANENTLY_BLOCKED", "NO_SIM", "UNKNOWN"]
LinkState = Literal["UP", "DOWN"]
Uplink = Literal["NONE", "WIRED", "MODEM"]
VlanId = Annotated[str, Field(pattern="^([1-9][0-9]{0,2}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$")]


class SystemSettings(Model):
    """The global network configuration"""

    __response_required__: ClassVar[frozenset[str]] = frozenset(
        {"active_uplink", "hostname", "name_servers", "search_domains"}
    )
    __read_only__: ClassVar[frozenset[str]] = frozenset({"active_uplink", "hostname", "name_servers", "search_domains"})
    active_uplink: Uplink = Field(
        default_factory=not_sent, validation_alias="activeUplink", serialization_alias="activeUplink"
    )
    """Indicates which uplink is currently in use."""
    hostname: Hostname = Field(default_factory=not_sent)
    """The currently used hostname"""
    name_servers: NameServers = Field(
        default_factory=not_sent, validation_alias="nameServers", serialization_alias="nameServers"
    )
    """The name servers currently in use."""
    search_domains: SearchDomains = Field(
        default_factory=not_sent, validation_alias="searchDomains", serialization_alias="searchDomains"
    )
    """The search domains currently in use."""
    static_hostname: Hostname = Field(validation_alias="staticHostname", serialization_alias="staticHostname")
    """The statically configured hostname. It is used if `useDhcpHostname` is set to `false`, or if no `hostname` was obtained by DHCP."""
    static_name_servers: NameServers | None = Field(
        default=None, validation_alias="staticNameServers", serialization_alias="staticNameServers"
    )
    """The statically configured name servers. It is used if useDhcpResolver is set to false, or if no name servers were obtained by DHCP."""
    static_search_domains: SearchDomains = Field(
        validation_alias="staticSearchDomains", serialization_alias="staticSearchDomains"
    )
    """The statically configured search domains. It is used if useDhcpResolver is set to false, or if no search domains were obtained by DHCP."""
    use_dhcp_hostname: bool = Field(validation_alias="useDhcpHostname", serialization_alias="useDhcpHostname")
    """Checks which DHCP-assigned `hostname` should be used. If set to `false`, the `staticHostname` will be used."""


class Vlan(Model):
    """VLAN configurations."""

    id: VlanId
    """The ID of the VLAN. Needs to be between 1 and 4094."""


class Wired(Model):
    """The wired uplink configuration. Only available when wired_supported is true."""

    __response_required__: ClassVar[frozenset[str]] = frozenset(
        {"link_mode", "mac_address", "max_mtu", "max_number_of_vlans", "min_mtu", "mtu", "supported_link_modes"}
    )
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {
            "link_mode",
            "lower_state",
            "mac_address",
            "max_mtu",
            "max_number_of_vlans",
            "min_mtu",
            "mtu",
            "supported_link_modes",
        }
    )
    link_mode: LinkMode = Field(default_factory=not_sent, validation_alias="linkMode", serialization_alias="linkMode")
    """The current link mode."""
    lower_state: LinkState | None = Field(default=None, validation_alias="lowerState", serialization_alias="lowerState")
    """Indicates if the wired network interface device status is UP or DOWN."""
    mac_address: MacAddress = Field(
        default_factory=not_sent, validation_alias="macAddress", serialization_alias="macAddress"
    )
    """The MAC address of the wired device."""
    max_mtu: Mtu = Field(default_factory=not_sent, validation_alias="maxMtu", serialization_alias="maxMtu")
    """The maximum supported MTU of the wired device"""
    max_number_of_vlans: int = Field(
        default_factory=not_sent, validation_alias="maxNumberOfVlans", serialization_alias="maxNumberOfVlans"
    )
    """The maximum number of supported VLANs."""
    min_mtu: Mtu = Field(default_factory=not_sent, validation_alias="minMtu", serialization_alias="minMtu")
    """The minimum supported MTU of the wired device"""
    mtu: Mtu = Field(default_factory=not_sent)
    """The MTU of the wired device"""
    use_dhcp_resolver: bool | None = Field(
        default=None, validation_alias="useDhcpResolver", serialization_alias="useDhcpResolver"
    )
    """Checks if any DHCP-assigned resolver information should be used. If set to false, the static resolver values will be used."""
    static_link_mode: LinkMode = Field(validation_alias="staticLinkMode", serialization_alias="staticLinkMode")
    """The statically configured link mode."""
    static_mtu: Mtu = Field(validation_alias="staticMtu", serialization_alias="staticMtu")
    """The statically configured MTU of the wired device"""
    supported_link_modes: LinkModes = Field(
        default_factory=not_sent, validation_alias="supportedLinkModes", serialization_alias="supportedLinkModes"
    )
    """The supported link modes."""
    vlans: list[Vlan]
    """The configured VLANs."""


class Ipv4Info(Model):
    """IPv4 information of a cellular interface. The docs name the type Ipv4AddressStruct but do not define it; the fields come from the examples."""

    ip_address: Ipv4Address | None = Field(default=None, validation_alias="ipAddress", serialization_alias="ipAddress")
    """The assigned IPv4 address."""
    origin: str | None = None
    """How the address was obtained, for example CELLULAR."""
    prefix_length: int | None = Field(default=None, validation_alias="prefixLength", serialization_alias="prefixLength")
    """The network prefix length."""


class NetworkInterface(Model):
    """The collection of network interfaces for this SIM."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"ipv4_info"})
    access_point_name: str = Field(validation_alias="accessPointName", serialization_alias="accessPointName")
    """The Access Point Name for this interface."""
    interface_name: str = Field(validation_alias="interfaceName", serialization_alias="interfaceName")
    """The interface name."""
    ipv4_info: Ipv4Info | None = Field(default=None, validation_alias="ipv4Info", serialization_alias="ipv4Info")
    """The IPv4 information provided by the cellular network, null if an IPv4 connection is not established."""


class CellularConnection(Model):
    """The cellular network connection."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"operator_name"})
    connection_status: CellularConnectionStatus = Field(
        validation_alias="connectionStatus", serialization_alias="connectionStatus"
    )
    """The connection status."""
    operator_name: str | None = Field(default=None, validation_alias="operatorName", serialization_alias="operatorName")
    """The operator name, null if not connected to a cellular network."""
    radio_interface: RadioInterface = Field(validation_alias="radioInterface", serialization_alias="radioInterface")
    """The connected radio interface."""
    network_interface: list[NetworkInterface] | None = Field(
        default=None, validation_alias="networkInterface", serialization_alias="networkInterface"
    )
    """The network interfaces of the SIM."""


class Sim(Model):
    """The collection of SIM slots."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"iccid", "pin_retries", "provider", "puk_retries"})
    iccid: Iccid | None = None
    """The Integrated Circuit Card Identifier of the SIM, null if the SIM is absent."""
    pin_retries: int | None = Field(default=None, validation_alias="pinRetries", serialization_alias="pinRetries")
    """The number of attempts remaining for entering the SIM PIN, null if the SIM is absent."""
    provider: str | None = None
    """The name of the SIM provider, null if the SIM is absent."""
    puk_retries: int | None = Field(default=None, validation_alias="pukRetries", serialization_alias="pukRetries")
    """The number of attempts remaining for entering the SIM PUK, null if the SIM is absent."""
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    """The slot ID of the SIM."""
    status: SimStatus
    """The status of the SIM."""
    connection: CellularConnection | None = None
    """The cellular network connection of the SIM."""


class Modem(Model):
    """The modem configuration and SIM management. When the modem is not ready, imei is null and sim is empty."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"imei"})
    imei: Imei | None
    """The IMEI of the modem, null if the modem is not ready."""
    sim: list[Sim]
    """The SIM slots."""


class PortSecurity(Model):
    """Switch port security configurations."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"auth_state", "mac_sec_state"})
    auth_server_enabled: bool | None = Field(
        default=None, validation_alias="authServerEnabled", serialization_alias="authServerEnabled"
    )
    """Indicates if the authentication server is enabled."""
    auth_server_enforced: AuthServerEnforced | None = Field(
        default=None, validation_alias="authServerEnforced", serialization_alias="authServerEnforced"
    )
    """Indicates if the authentication server is enforced."""
    auth_state: AuthState | None = Field(default=None, validation_alias="authState", serialization_alias="authState")
    """Indicates the authentication state of the port."""
    mac_sec_state: MacSecState | None = Field(
        default=None, validation_alias="macSecState", serialization_alias="macSecState"
    )
    """Indicates the MACSec state of the port"""


class SwitchPort(Model):
    """Switch port configurations. security is left out when security_supported is false."""

    __response_required__: ClassVar[frozenset[str]] = frozenset(
        {"lower_state", "port_id", "remote_addresses", "security_supported"}
    )
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {"lower_state", "port_id", "remote_addresses", "security_supported"}
    )
    enabled: bool
    """Specifies if a network interface device is enabled."""
    lower_state: LinkState = Field(
        default_factory=not_sent, validation_alias="lowerState", serialization_alias="lowerState"
    )
    """Indicates if the network interface device status is UP or DOWN."""
    port_id: str = Field(default_factory=not_sent, validation_alias="portId", serialization_alias="portId")
    """Switch port ID."""
    remote_addresses: RemoteAddresses = Field(
        default_factory=not_sent, validation_alias="remoteAddresses", serialization_alias="remoteAddresses"
    )
    """List all stored remote MAC addresses observed on the switch port."""
    security_supported: bool = Field(default_factory=not_sent)
    """Indicates if security is supported."""
    security: PortSecurity | None = None
    """Security settings; only present when security_supported is true."""


class SwitchSettings(Model):
    """Global switch configurations. Only available when switch_supported is true."""

    port: list[SwitchPort] | None = None
    """The switch ports."""


class NetworkSettings(Model):
    """The whole API tree. Wired, modem and switch are only present when supported."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"modem_supported", "switch_supported", "wired_supported"})
    modem_supported: bool | None = None
    """Whether the device supports a cellular modem."""
    switch_supported: bool | None = None
    """Indicates if switch is supported."""
    wired_supported: bool | None = None
    """Whether the device has a wired uplink."""
    system: SystemSettings | None = None
    wired: Wired | None = None
    modem: Modem | None = None
    switch: SwitchSettings | None = None


class UpdateSystemRequest(Model):
    """Arguments of ``update_system``. Only the given settings change."""

    static_hostname: Hostname | None = Field(
        default=None, validation_alias="staticHostname", serialization_alias="staticHostname"
    )
    """The statically configured hostname. It is used if `useDhcpHostname` is set to `false`, or if no `hostname` was obtained by DHCP."""
    static_name_servers: NameServers | None = Field(
        default=None, validation_alias="staticNameServers", serialization_alias="staticNameServers"
    )
    """The statically configured name servers. It is used if useDhcpResolver is set to false, or if no name servers were obtained by DHCP."""
    static_search_domains: SearchDomains | None = Field(
        default=None, validation_alias="staticSearchDomains", serialization_alias="staticSearchDomains"
    )
    """The statically configured search domains. It is used if useDhcpResolver is set to false, or if no search domains were obtained by DHCP."""
    use_dhcp_hostname: bool | None = Field(
        default=None, validation_alias="useDhcpHostname", serialization_alias="useDhcpHostname"
    )
    """Checks which DHCP-assigned `hostname` should be used. If set to `false`, the `staticHostname` will be used."""

    @classmethod
    def from_current(cls, settings: SystemSettings) -> UpdateSystemRequest:
        """A request that rewrites ``settings`` unchanged: copy it, edit fields, send it back."""
        data = settings.request_data()
        return cls.from_response_data(data)


class UpdatePortRequest(Model):
    """Arguments of ``update_port``."""

    port_id: str = Field(validation_alias="portId", serialization_alias="portId")
    """Switch port ID."""
    enabled: bool | None = None
    """Specifies if a network interface device is enabled."""
    security: PortSecurity | None = None
    """Security settings; only settable when security_supported is true."""


class UpdatePortSecurityRequest(Model):
    """Arguments of ``update_port_security``."""

    port_id: str = Field(validation_alias="portId", serialization_alias="portId")
    """Switch port ID."""
    auth_server_enabled: bool | None = Field(
        default=None, validation_alias="authServerEnabled", serialization_alias="authServerEnabled"
    )
    """Indicates if the authentication server is enabled."""
    auth_server_enforced: AuthServerEnforced | None = Field(
        default=None, validation_alias="authServerEnforced", serialization_alias="authServerEnforced"
    )
    """Indicates if the authentication server is enforced."""


class AddVlanRequest(Model):
    """Arguments of ``add_vlan``."""

    id: VlanId
    """The ID of the VLAN. Needs to be between 1 and 4094."""


class SetSystemStaticHostnameRequest(Model):
    static_hostname: Hostname = Field(validation_alias="staticHostname", serialization_alias="staticHostname")
    """The statically configured hostname. It is used if `useDhcpHostname` is set to `false`, or if no `hostname` was obtained by DHCP."""


class SetSystemStaticNameServersRequest(Model):
    static_name_servers: NameServers = Field(
        validation_alias="staticNameServers", serialization_alias="staticNameServers"
    )
    """The statically configured name servers. It is used if useDhcpResolver is set to false, or if no name servers were obtained by DHCP."""


class SetSystemStaticSearchDomainsRequest(Model):
    static_search_domains: SearchDomains = Field(
        validation_alias="staticSearchDomains", serialization_alias="staticSearchDomains"
    )
    """The statically configured search domains. It is used if useDhcpResolver is set to false, or if no search domains were obtained by DHCP."""


class SetSystemUseDhcpHostnameRequest(Model):
    use_dhcp_hostname: bool = Field(validation_alias="useDhcpHostname", serialization_alias="useDhcpHostname")
    """Checks which DHCP-assigned `hostname` should be used. If set to `false`, the `staticHostname` will be used."""


class SetWiredUseDhcpResolverRequest(Model):
    use_dhcp_resolver: bool = Field(validation_alias="useDhcpResolver", serialization_alias="useDhcpResolver")
    """Checks if any DHCP-assigned resolver information should be used. If set to false, the static resolver values will be used."""


class SetWiredStaticLinkModeRequest(Model):
    static_link_mode: LinkMode = Field(validation_alias="staticLinkMode", serialization_alias="staticLinkMode")
    """The statically configured link mode."""


class SetWiredStaticMtuRequest(Model):
    static_mtu: Mtu = Field(validation_alias="staticMtu", serialization_alias="staticMtu")
    """The statically configured MTU of the wired device"""


class VlanIdRequest(Model):
    id: VlanId


class SimSlotIdRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")


class ChangeSimPinRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    oldpin: SimPin
    """The existing SIM PIN."""
    newpin: SimPin
    """The new SIM PIN."""


class SetSimProtectionRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    enable: bool
    """true if SIM PIN protection should be enabled, otherwise false."""
    pin: SimPin
    """The SIM PIN."""


class UnblockSimRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    pin: SimPin
    """The new SIM PIN."""
    puk: SimPuk
    """The PUK code of the SIM."""


class VerifySimPinRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    pin: SimPin
    """The SIM PIN."""


class GetRadioParametersRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    radio_generation: RadioGeneration = Field(validation_alias="radioGeneration", serialization_alias="radioGeneration")
    """The radio generation to get parameters for."""


class NetworkInterfaceKeyRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    interface_name: str = Field(validation_alias="interfaceName", serialization_alias="interfaceName")
    """The interface name."""


class SetAccessPointNameRequest(Model):
    slot_id: SimSlotId = Field(validation_alias="slotId", serialization_alias="slotId")
    interface_name: str = Field(validation_alias="interfaceName", serialization_alias="interfaceName")
    """The interface name."""
    access_point_name: AccessPointName = Field(
        validation_alias="accessPointName", serialization_alias="accessPointName"
    )
    """The Access Point Name (APN)."""


class PortIdRequest(Model):
    port_id: str = Field(validation_alias="portId", serialization_alias="portId")
    """Switch port ID."""


class SetPortEnabledRequest(Model):
    port_id: str = Field(validation_alias="portId", serialization_alias="portId")
    """Switch port ID."""
    enabled: bool
    """Specifies if a network interface device is enabled."""


class SetPortSecurityAuthServerEnabledRequest(Model):
    port_id: str = Field(validation_alias="portId", serialization_alias="portId")
    """Switch port ID."""
    auth_server_enabled: bool = Field(validation_alias="authServerEnabled", serialization_alias="authServerEnabled")
    """Indicates if the authentication server is enabled."""


class SetPortSecurityAuthServerEnforcedRequest(Model):
    port_id: str = Field(validation_alias="portId", serialization_alias="portId")
    """Switch port ID."""
    auth_server_enforced: AuthServerEnforced = Field(
        validation_alias="authServerEnforced", serialization_alias="authServerEnforced"
    )
    """Indicates if the authentication server is enforced."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/network-settings/v2beta"

INFO = ApiInfo(
    id="network-settings-config",
    name="Network settings API",
    family=Family.DCA,
    discovery=(DcaDiscovery("network-settings", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/network-settings-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=NetworkSettings, access="admin", effect="read")
    get_modem_supported = Operation(
        INFO,
        "get_modem_supported",
        DcaBinding("GET", f"{ROOT}/modem_supported"),
        result=bool,
        access="admin",
        effect="read",
    )
    get_switch_supported = Operation(
        INFO,
        "get_switch_supported",
        DcaBinding("GET", f"{ROOT}/switch_supported"),
        result=bool,
        access="admin",
        effect="read",
    )
    get_wired_supported = Operation(
        INFO,
        "get_wired_supported",
        DcaBinding("GET", f"{ROOT}/wired_supported"),
        result=bool,
        access="admin",
        effect="read",
    )
    get_system = Operation(
        INFO, "get_system", DcaBinding("GET", f"{ROOT}/system"), result=SystemSettings, access="admin", effect="read"
    )
    update_system = Operation(
        INFO,
        "update_system",
        DcaBinding("PATCH", f"{ROOT}/system", body="object"),
        params=UpdateSystemRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_system_static_hostname = Operation(
        INFO,
        "set_system_static_hostname",
        DcaBinding("PATCH", f"{ROOT}/system/staticHostname", body="value", body_field="staticHostname"),
        params=SetSystemStaticHostnameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_system_static_name_servers = Operation(
        INFO,
        "set_system_static_name_servers",
        DcaBinding("PATCH", f"{ROOT}/system/staticNameServers", body="value", body_field="staticNameServers"),
        params=SetSystemStaticNameServersRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_system_static_search_domains = Operation(
        INFO,
        "set_system_static_search_domains",
        DcaBinding("PATCH", f"{ROOT}/system/staticSearchDomains", body="value", body_field="staticSearchDomains"),
        params=SetSystemStaticSearchDomainsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_system_use_dhcp_hostname = Operation(
        INFO,
        "set_system_use_dhcp_hostname",
        DcaBinding("PATCH", f"{ROOT}/system/useDhcpHostname", body="value", body_field="useDhcpHostname"),
        params=SetSystemUseDhcpHostnameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_wired = Operation(
        INFO, "get_wired", DcaBinding("GET", f"{ROOT}/wired"), result=Wired, access="admin", effect="read"
    )
    set_wired_use_dhcp_resolver = Operation(
        INFO,
        "set_wired_use_dhcp_resolver",
        DcaBinding("PATCH", f"{ROOT}/wired/useDhcpResolver", body="value", body_field="useDhcpResolver"),
        params=SetWiredUseDhcpResolverRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_wired_static_link_mode = Operation(
        INFO,
        "set_wired_static_link_mode",
        DcaBinding("PATCH", f"{ROOT}/wired/staticLinkMode", body="value", body_field="staticLinkMode"),
        params=SetWiredStaticLinkModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_wired_static_mtu = Operation(
        INFO,
        "set_wired_static_mtu",
        DcaBinding("PATCH", f"{ROOT}/wired/staticMtu", body="value", body_field="staticMtu"),
        params=SetWiredStaticMtuRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_vlans = Operation(
        INFO, "list_vlans", DcaBinding("GET", f"{ROOT}/wired/vlans"), result=list[Vlan], access="admin", effect="read"
    )
    get_vlan = Operation(
        INFO,
        "get_vlan",
        DcaBinding("GET", f"{ROOT}/wired/vlans/{{id}}"),
        params=VlanIdRequest,
        result=Vlan,
        access="admin",
        effect="read",
    )
    add_vlan = Operation(
        INFO,
        "add_vlan",
        DcaBinding("POST", f"{ROOT}/wired/vlans", body="object"),
        params=AddVlanRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_vlan = Operation(
        INFO,
        "remove_vlan",
        DcaBinding("DELETE", f"{ROOT}/wired/vlans/{{id}}"),
        params=VlanIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_modem = Operation(
        INFO, "get_modem", DcaBinding("GET", f"{ROOT}/modem"), result=Modem, access="admin", effect="read"
    )
    list_sims = Operation(
        INFO, "list_sims", DcaBinding("GET", f"{ROOT}/modem/sim"), result=list[Sim], access="admin", effect="read"
    )
    get_sim = Operation(
        INFO,
        "get_sim",
        DcaBinding("GET", f"{ROOT}/modem/sim/{{slotId}}"),
        params=SimSlotIdRequest,
        result=Sim,
        access="admin",
        effect="read",
    )
    change_sim_pin = Operation(
        INFO,
        "change_sim_pin",
        DcaBinding("POST", f"{ROOT}/modem/sim/{{slotId}}/changeSimPin", body="object"),
        params=ChangeSimPinRequest,
        access="admin",
        effect="action",
    )
    set_sim_protection = Operation(
        INFO,
        "set_sim_protection",
        DcaBinding("POST", f"{ROOT}/modem/sim/{{slotId}}/setSimProtection", body="object"),
        params=SetSimProtectionRequest,
        access="admin",
        effect="action",
    )
    unblock_sim = Operation(
        INFO,
        "unblock_sim",
        DcaBinding("POST", f"{ROOT}/modem/sim/{{slotId}}/unblockSim", body="object"),
        params=UnblockSimRequest,
        access="admin",
        effect="action",
    )
    verify_sim_pin = Operation(
        INFO,
        "verify_sim_pin",
        DcaBinding("POST", f"{ROOT}/modem/sim/{{slotId}}/verifySimPin", body="value", body_field="pin"),
        params=VerifySimPinRequest,
        access="admin",
        effect="action",
    )
    get_sim_connection = Operation(
        INFO,
        "get_sim_connection",
        DcaBinding("GET", f"{ROOT}/modem/sim/{{slotId}}/connection"),
        params=SimSlotIdRequest,
        result=CellularConnection,
        access="admin",
        effect="read",
    )
    get_radio_parameters = Operation(
        INFO,
        "get_radio_parameters",
        DcaBinding(
            "POST",
            f"{ROOT}/modem/sim/{{slotId}}/connection/getRadioParameters",
            body="value",
            body_field="radioGeneration",
        ),
        params=GetRadioParametersRequest,
        result=RadioParameters,
        access="admin",
        effect="action",
    )
    list_network_interfaces = Operation(
        INFO,
        "list_network_interfaces",
        DcaBinding("GET", f"{ROOT}/modem/sim/{{slotId}}/connection/networkInterface"),
        params=SimSlotIdRequest,
        result=list[NetworkInterface],
        access="admin",
        effect="read",
    )
    get_network_interface = Operation(
        INFO,
        "get_network_interface",
        DcaBinding("GET", f"{ROOT}/modem/sim/{{slotId}}/connection/networkInterface/{{interfaceName}}"),
        params=NetworkInterfaceKeyRequest,
        result=NetworkInterface,
        access="admin",
        effect="read",
    )
    set_access_point_name = Operation(
        INFO,
        "set_access_point_name",
        DcaBinding(
            "POST",
            f"{ROOT}/modem/sim/{{slotId}}/connection/networkInterface/{{interfaceName}}/setAccessPointName",
            body="value",
            body_field="accessPointName",
        ),
        params=SetAccessPointNameRequest,
        access="admin",
        effect="action",
    )
    get_switch = Operation(
        INFO, "get_switch", DcaBinding("GET", f"{ROOT}/switch"), result=SwitchSettings, access="admin", effect="read"
    )
    list_ports = Operation(
        INFO,
        "list_ports",
        DcaBinding("GET", f"{ROOT}/switch/port"),
        result=list[SwitchPort],
        access="admin",
        effect="read",
    )
    get_port = Operation(
        INFO,
        "get_port",
        DcaBinding("GET", f"{ROOT}/switch/port/{{portId}}"),
        params=PortIdRequest,
        result=SwitchPort,
        access="admin",
        effect="read",
    )
    update_port = Operation(
        INFO,
        "update_port",
        DcaBinding("PATCH", f"{ROOT}/switch/port/{{portId}}", body="object"),
        params=UpdatePortRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_port_enabled = Operation(
        INFO,
        "set_port_enabled",
        DcaBinding("PATCH", f"{ROOT}/switch/port/{{portId}}/enabled", body="value", body_field="enabled"),
        params=SetPortEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_port_security = Operation(
        INFO,
        "get_port_security",
        DcaBinding("GET", f"{ROOT}/switch/port/{{portId}}/security"),
        params=PortIdRequest,
        result=PortSecurity,
        access="admin",
        effect="read",
    )
    update_port_security = Operation(
        INFO,
        "update_port_security",
        DcaBinding("PATCH", f"{ROOT}/switch/port/{{portId}}/security", body="object"),
        params=UpdatePortSecurityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_port_security_auth_server_enabled = Operation(
        INFO,
        "set_port_security_auth_server_enabled",
        DcaBinding(
            "PATCH",
            f"{ROOT}/switch/port/{{portId}}/security/authServerEnabled",
            body="value",
            body_field="authServerEnabled",
        ),
        params=SetPortSecurityAuthServerEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_port_security_auth_server_enforced = Operation(
        INFO,
        "set_port_security_auth_server_enforced",
        DcaBinding(
            "PATCH",
            f"{ROOT}/switch/port/{{portId}}/security/authServerEnforced",
            body="value",
            body_field="authServerEnforced",
        ),
        params=SetPortSecurityAuthServerEnforcedRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class NetworkSettingsApi(SyncApi):
    """Network settings API (``network-settings-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> NetworkSettings:
        """All data of the Network settings API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_modem_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports a cellular modem. Access: admin."""
        return self._run(OPS.get_modem_supported, None, {}, request_options)

    def get_switch_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device has a built-in switch. Access: admin."""
        return self._run(OPS.get_switch_supported, None, {}, request_options)

    def get_wired_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device has a wired uplink. Access: admin."""
        return self._run(OPS.get_wired_supported, None, {}, request_options)

    def get_system(self, *, request_options: RequestOptions | None = None) -> SystemSettings:
        """Get the hostname and resolver settings, including the values currently in use.

        Access: admin.
        """
        return self._run(OPS.get_system, None, {}, request_options)

    def update_system(
        self,
        *,
        static_hostname: Hostname | MISSING = MISSING,
        static_name_servers: NameServers | MISSING = MISSING,
        static_search_domains: SearchDomains | MISSING = MISSING,
        use_dhcp_hostname: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the hostname and resolver settings; only the given fields change.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.update_system,
            None,
            {
                "static_hostname": static_hostname,
                "static_name_servers": static_name_servers,
                "static_search_domains": static_search_domains,
                "use_dhcp_hostname": use_dhcp_hostname,
            },
            request_options,
        )

    def set_system_static_hostname(
        self, static_hostname: Hostname, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static hostname. Changes only the fields given. Access: admin."""
        self._run(OPS.set_system_static_hostname, None, {"static_hostname": static_hostname}, request_options)

    def set_system_static_name_servers(
        self, static_name_servers: NameServers, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static name servers. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_system_static_name_servers, None, {"static_name_servers": static_name_servers}, request_options
        )

    def set_system_static_search_domains(
        self, static_search_domains: SearchDomains, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static search domains. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_system_static_search_domains,
            None,
            {"static_search_domains": static_search_domains},
            request_options,
        )

    def set_system_use_dhcp_hostname(
        self, use_dhcp_hostname: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Use the DHCP-assigned hostname, or the static one when false.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_system_use_dhcp_hostname, None, {"use_dhcp_hostname": use_dhcp_hostname}, request_options)

    def get_wired(self, *, request_options: RequestOptions | None = None) -> Wired:
        """Get the wired uplink configuration. Only available when wired_supported is true.

        Access: admin.
        """
        return self._run(OPS.get_wired, None, {}, request_options)

    def set_wired_use_dhcp_resolver(
        self, use_dhcp_resolver: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Use DHCP-assigned resolver information, or the static resolver values when false.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_wired_use_dhcp_resolver, None, {"use_dhcp_resolver": use_dhcp_resolver}, request_options)

    def set_wired_static_link_mode(
        self, static_link_mode: LinkMode, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static link mode of the wired uplink; AUTO negotiates it.

        An unsupported link mode can result in a connection loss.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_wired_static_link_mode, None, {"static_link_mode": static_link_mode}, request_options)

    def set_wired_static_mtu(self, static_mtu: Mtu, *, request_options: RequestOptions | None = None) -> None:
        """Set the static MTU of the wired uplink.

        The value must be within minMtu and maxMtu. IPv6 requires an MTU of at least 1280.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_wired_static_mtu, None, {"static_mtu": static_mtu}, request_options)

    def list_vlans(self, *, request_options: RequestOptions | None = None) -> list[Vlan]:
        """List the configured VLANs. Access: admin."""
        return self._run(OPS.list_vlans, None, {}, request_options)

    def get_vlan(self, id: VlanId, *, request_options: RequestOptions | None = None) -> Vlan:
        """Get one VLAN. Access: admin."""
        return self._run(OPS.get_vlan, None, {"id": id}, request_options)

    def add_vlan(self, *, id: VlanId, request_options: RequestOptions | None = None) -> None:
        """Add a VLAN with an id between 1 and 4094. Access: admin."""
        self._run(OPS.add_vlan, None, {"id": id}, request_options)

    def remove_vlan(self, id: VlanId, *, request_options: RequestOptions | None = None) -> None:
        """Remove a VLAN. Access: admin."""
        self._run(OPS.remove_vlan, None, {"id": id}, request_options)

    def get_modem(self, *, request_options: RequestOptions | None = None) -> Modem:
        """Get the modem configuration with SIM, connection and interface details. Only available when modem_supported is true.

        Access: admin.
        """
        return self._run(OPS.get_modem, None, {}, request_options)

    def list_sims(self, *, request_options: RequestOptions | None = None) -> list[Sim]:
        """List the SIM slots. Access: admin."""
        return self._run(OPS.list_sims, None, {}, request_options)

    def get_sim(self, slot_id: SimSlotId, *, request_options: RequestOptions | None = None) -> Sim:
        """Get one SIM slot. Access: admin."""
        return self._run(OPS.get_sim, None, {"slot_id": slot_id}, request_options)

    def change_sim_pin(
        self, slot_id: SimSlotId, *, oldpin: SimPin, newpin: SimPin, request_options: RequestOptions | None = None
    ) -> None:
        """Change the SIM PIN. Both the old and the new PIN are required. Access: admin."""
        self._run(OPS.change_sim_pin, None, {"slot_id": slot_id, "oldpin": oldpin, "newpin": newpin}, request_options)

    def set_sim_protection(
        self, slot_id: SimSlotId, *, enable: bool, pin: SimPin, request_options: RequestOptions | None = None
    ) -> None:
        """Turn SIM PIN protection on or off. Access: admin."""
        self._run(OPS.set_sim_protection, None, {"slot_id": slot_id, "enable": enable, "pin": pin}, request_options)

    def unblock_sim(
        self, slot_id: SimSlotId, *, pin: SimPin, puk: SimPuk, request_options: RequestOptions | None = None
    ) -> None:
        """Unblock a blocked SIM with its PUK and set a new PIN.

        The SIM is blocked after three incorrect PIN attempts.

        Access: admin.
        """
        self._run(OPS.unblock_sim, None, {"slot_id": slot_id, "pin": pin, "puk": puk}, request_options)

    def verify_sim_pin(self, slot_id: SimSlotId, *, pin: SimPin, request_options: RequestOptions | None = None) -> None:
        """Unlock the SIM using the PIN, or just verify the PIN. Access: admin."""
        self._run(OPS.verify_sim_pin, None, {"slot_id": slot_id, "pin": pin}, request_options)

    def get_sim_connection(
        self, slot_id: SimSlotId, *, request_options: RequestOptions | None = None
    ) -> CellularConnection:
        """Get the cellular connection of a SIM. Access: admin."""
        return self._run(OPS.get_sim_connection, None, {"slot_id": slot_id}, request_options)

    def get_radio_parameters(
        self, slot_id: SimSlotId, *, radio_generation: RadioGeneration, request_options: RequestOptions | None = None
    ) -> RadioParameters:
        """Get the current radio parameters of the cellular connection. Access: admin."""
        return self._run(
            OPS.get_radio_parameters, None, {"slot_id": slot_id, "radio_generation": radio_generation}, request_options
        )

    def list_network_interfaces(
        self, slot_id: SimSlotId, *, request_options: RequestOptions | None = None
    ) -> list[NetworkInterface]:
        """List the network interfaces of a SIM connection. Access: admin."""
        return self._run(OPS.list_network_interfaces, None, {"slot_id": slot_id}, request_options)

    def get_network_interface(
        self, slot_id: SimSlotId, interface_name: str, *, request_options: RequestOptions | None = None
    ) -> NetworkInterface:
        """Get one network interface of a SIM connection. Access: admin."""
        return self._run(
            OPS.get_network_interface, None, {"slot_id": slot_id, "interface_name": interface_name}, request_options
        )

    def set_access_point_name(
        self,
        slot_id: SimSlotId,
        interface_name: str,
        *,
        access_point_name: AccessPointName,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Access Point Name of a network interface. Access: admin."""
        self._run(
            OPS.set_access_point_name,
            None,
            {"slot_id": slot_id, "interface_name": interface_name, "access_point_name": access_point_name},
            request_options,
        )

    def get_switch(self, *, request_options: RequestOptions | None = None) -> SwitchSettings:
        """Get the switch configuration. Only available when switch_supported is true. Access: admin."""
        return self._run(OPS.get_switch, None, {}, request_options)

    def list_ports(self, *, request_options: RequestOptions | None = None) -> list[SwitchPort]:
        """List the switch ports. Access: admin."""
        return self._run(OPS.list_ports, None, {}, request_options)

    def get_port(self, port_id: str, *, request_options: RequestOptions | None = None) -> SwitchPort:
        """Get one switch port. The security settings are left out when security_supported is false.

        Access: admin.
        """
        return self._run(OPS.get_port, None, {"port_id": port_id}, request_options)

    @overload
    def update_port(self, request: UpdatePortRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_port(
        self,
        /,
        *,
        port_id: str,
        enabled: bool | MISSING = MISSING,
        security: PortSecurity | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_port(
        self,
        request: UpdatePortRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a switch port; only the given fields change.

        The security settings can only be set when security_supported is true.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_port, request, kwargs, request_options)

    def set_port_enabled(self, port_id: str, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable a switch port. Changes only the fields given. Access: admin."""
        self._run(OPS.set_port_enabled, None, {"port_id": port_id, "enabled": enabled}, request_options)

    def get_port_security(self, port_id: str, *, request_options: RequestOptions | None = None) -> PortSecurity:
        """Get the security settings of a switch port. Only available when security_supported is true.

        Access: admin.
        """
        return self._run(OPS.get_port_security, None, {"port_id": port_id}, request_options)

    def update_port_security(
        self,
        port_id: str,
        *,
        auth_server_enabled: bool | MISSING = MISSING,
        auth_server_enforced: AuthServerEnforced | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the security settings of a switch port; only the given fields change.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.update_port_security,
            None,
            {
                "port_id": port_id,
                "auth_server_enabled": auth_server_enabled,
                "auth_server_enforced": auth_server_enforced,
            },
            request_options,
        )

    def set_port_security_auth_server_enabled(
        self, port_id: str, auth_server_enabled: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the authentication server of a switch port.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_port_security_auth_server_enabled,
            None,
            {"port_id": port_id, "auth_server_enabled": auth_server_enabled},
            request_options,
        )

    def set_port_security_auth_server_enforced(
        self, port_id: str, auth_server_enforced: AuthServerEnforced, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set how strongly the authentication server is enforced on a switch port.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_port_security_auth_server_enforced,
            None,
            {"port_id": port_id, "auth_server_enforced": auth_server_enforced},
            request_options,
        )


class AsyncNetworkSettingsApi(AsyncApi):
    """Network settings API (``network-settings-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> NetworkSettings:
        """All data of the Network settings API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_modem_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device supports a cellular modem. Access: admin."""
        return await self._run(OPS.get_modem_supported, None, {}, request_options)

    async def get_switch_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device has a built-in switch. Access: admin."""
        return await self._run(OPS.get_switch_supported, None, {}, request_options)

    async def get_wired_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the device has a wired uplink. Access: admin."""
        return await self._run(OPS.get_wired_supported, None, {}, request_options)

    async def get_system(self, *, request_options: RequestOptions | None = None) -> SystemSettings:
        """Get the hostname and resolver settings, including the values currently in use.

        Access: admin.
        """
        return await self._run(OPS.get_system, None, {}, request_options)

    async def update_system(
        self,
        *,
        static_hostname: Hostname | MISSING = MISSING,
        static_name_servers: NameServers | MISSING = MISSING,
        static_search_domains: SearchDomains | MISSING = MISSING,
        use_dhcp_hostname: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the hostname and resolver settings; only the given fields change.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.update_system,
            None,
            {
                "static_hostname": static_hostname,
                "static_name_servers": static_name_servers,
                "static_search_domains": static_search_domains,
                "use_dhcp_hostname": use_dhcp_hostname,
            },
            request_options,
        )

    async def set_system_static_hostname(
        self, static_hostname: Hostname, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static hostname. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_system_static_hostname, None, {"static_hostname": static_hostname}, request_options)

    async def set_system_static_name_servers(
        self, static_name_servers: NameServers, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static name servers. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_system_static_name_servers, None, {"static_name_servers": static_name_servers}, request_options
        )

    async def set_system_static_search_domains(
        self, static_search_domains: SearchDomains, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static search domains. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_system_static_search_domains,
            None,
            {"static_search_domains": static_search_domains},
            request_options,
        )

    async def set_system_use_dhcp_hostname(
        self, use_dhcp_hostname: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Use the DHCP-assigned hostname, or the static one when false.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_system_use_dhcp_hostname, None, {"use_dhcp_hostname": use_dhcp_hostname}, request_options
        )

    async def get_wired(self, *, request_options: RequestOptions | None = None) -> Wired:
        """Get the wired uplink configuration. Only available when wired_supported is true.

        Access: admin.
        """
        return await self._run(OPS.get_wired, None, {}, request_options)

    async def set_wired_use_dhcp_resolver(
        self, use_dhcp_resolver: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Use DHCP-assigned resolver information, or the static resolver values when false.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_wired_use_dhcp_resolver, None, {"use_dhcp_resolver": use_dhcp_resolver}, request_options
        )

    async def set_wired_static_link_mode(
        self, static_link_mode: LinkMode, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the static link mode of the wired uplink; AUTO negotiates it.

        An unsupported link mode can result in a connection loss.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_wired_static_link_mode, None, {"static_link_mode": static_link_mode}, request_options)

    async def set_wired_static_mtu(self, static_mtu: Mtu, *, request_options: RequestOptions | None = None) -> None:
        """Set the static MTU of the wired uplink.

        The value must be within minMtu and maxMtu. IPv6 requires an MTU of at least 1280.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_wired_static_mtu, None, {"static_mtu": static_mtu}, request_options)

    async def list_vlans(self, *, request_options: RequestOptions | None = None) -> list[Vlan]:
        """List the configured VLANs. Access: admin."""
        return await self._run(OPS.list_vlans, None, {}, request_options)

    async def get_vlan(self, id: VlanId, *, request_options: RequestOptions | None = None) -> Vlan:
        """Get one VLAN. Access: admin."""
        return await self._run(OPS.get_vlan, None, {"id": id}, request_options)

    async def add_vlan(self, *, id: VlanId, request_options: RequestOptions | None = None) -> None:
        """Add a VLAN with an id between 1 and 4094. Access: admin."""
        await self._run(OPS.add_vlan, None, {"id": id}, request_options)

    async def remove_vlan(self, id: VlanId, *, request_options: RequestOptions | None = None) -> None:
        """Remove a VLAN. Access: admin."""
        await self._run(OPS.remove_vlan, None, {"id": id}, request_options)

    async def get_modem(self, *, request_options: RequestOptions | None = None) -> Modem:
        """Get the modem configuration with SIM, connection and interface details. Only available when modem_supported is true.

        Access: admin.
        """
        return await self._run(OPS.get_modem, None, {}, request_options)

    async def list_sims(self, *, request_options: RequestOptions | None = None) -> list[Sim]:
        """List the SIM slots. Access: admin."""
        return await self._run(OPS.list_sims, None, {}, request_options)

    async def get_sim(self, slot_id: SimSlotId, *, request_options: RequestOptions | None = None) -> Sim:
        """Get one SIM slot. Access: admin."""
        return await self._run(OPS.get_sim, None, {"slot_id": slot_id}, request_options)

    async def change_sim_pin(
        self, slot_id: SimSlotId, *, oldpin: SimPin, newpin: SimPin, request_options: RequestOptions | None = None
    ) -> None:
        """Change the SIM PIN. Both the old and the new PIN are required. Access: admin."""
        await self._run(
            OPS.change_sim_pin, None, {"slot_id": slot_id, "oldpin": oldpin, "newpin": newpin}, request_options
        )

    async def set_sim_protection(
        self, slot_id: SimSlotId, *, enable: bool, pin: SimPin, request_options: RequestOptions | None = None
    ) -> None:
        """Turn SIM PIN protection on or off. Access: admin."""
        await self._run(
            OPS.set_sim_protection, None, {"slot_id": slot_id, "enable": enable, "pin": pin}, request_options
        )

    async def unblock_sim(
        self, slot_id: SimSlotId, *, pin: SimPin, puk: SimPuk, request_options: RequestOptions | None = None
    ) -> None:
        """Unblock a blocked SIM with its PUK and set a new PIN.

        The SIM is blocked after three incorrect PIN attempts.

        Access: admin.
        """
        await self._run(OPS.unblock_sim, None, {"slot_id": slot_id, "pin": pin, "puk": puk}, request_options)

    async def verify_sim_pin(
        self, slot_id: SimSlotId, *, pin: SimPin, request_options: RequestOptions | None = None
    ) -> None:
        """Unlock the SIM using the PIN, or just verify the PIN. Access: admin."""
        await self._run(OPS.verify_sim_pin, None, {"slot_id": slot_id, "pin": pin}, request_options)

    async def get_sim_connection(
        self, slot_id: SimSlotId, *, request_options: RequestOptions | None = None
    ) -> CellularConnection:
        """Get the cellular connection of a SIM. Access: admin."""
        return await self._run(OPS.get_sim_connection, None, {"slot_id": slot_id}, request_options)

    async def get_radio_parameters(
        self, slot_id: SimSlotId, *, radio_generation: RadioGeneration, request_options: RequestOptions | None = None
    ) -> RadioParameters:
        """Get the current radio parameters of the cellular connection. Access: admin."""
        return await self._run(
            OPS.get_radio_parameters, None, {"slot_id": slot_id, "radio_generation": radio_generation}, request_options
        )

    async def list_network_interfaces(
        self, slot_id: SimSlotId, *, request_options: RequestOptions | None = None
    ) -> list[NetworkInterface]:
        """List the network interfaces of a SIM connection. Access: admin."""
        return await self._run(OPS.list_network_interfaces, None, {"slot_id": slot_id}, request_options)

    async def get_network_interface(
        self, slot_id: SimSlotId, interface_name: str, *, request_options: RequestOptions | None = None
    ) -> NetworkInterface:
        """Get one network interface of a SIM connection. Access: admin."""
        return await self._run(
            OPS.get_network_interface, None, {"slot_id": slot_id, "interface_name": interface_name}, request_options
        )

    async def set_access_point_name(
        self,
        slot_id: SimSlotId,
        interface_name: str,
        *,
        access_point_name: AccessPointName,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Access Point Name of a network interface. Access: admin."""
        await self._run(
            OPS.set_access_point_name,
            None,
            {"slot_id": slot_id, "interface_name": interface_name, "access_point_name": access_point_name},
            request_options,
        )

    async def get_switch(self, *, request_options: RequestOptions | None = None) -> SwitchSettings:
        """Get the switch configuration. Only available when switch_supported is true. Access: admin."""
        return await self._run(OPS.get_switch, None, {}, request_options)

    async def list_ports(self, *, request_options: RequestOptions | None = None) -> list[SwitchPort]:
        """List the switch ports. Access: admin."""
        return await self._run(OPS.list_ports, None, {}, request_options)

    async def get_port(self, port_id: str, *, request_options: RequestOptions | None = None) -> SwitchPort:
        """Get one switch port. The security settings are left out when security_supported is false.

        Access: admin.
        """
        return await self._run(OPS.get_port, None, {"port_id": port_id}, request_options)

    @overload
    async def update_port(
        self, request: UpdatePortRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_port(
        self,
        /,
        *,
        port_id: str,
        enabled: bool | MISSING = MISSING,
        security: PortSecurity | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_port(
        self,
        request: UpdatePortRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a switch port; only the given fields change.

        The security settings can only be set when security_supported is true.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_port, request, kwargs, request_options)

    async def set_port_enabled(
        self, port_id: str, enabled: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable a switch port. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_port_enabled, None, {"port_id": port_id, "enabled": enabled}, request_options)

    async def get_port_security(self, port_id: str, *, request_options: RequestOptions | None = None) -> PortSecurity:
        """Get the security settings of a switch port. Only available when security_supported is true.

        Access: admin.
        """
        return await self._run(OPS.get_port_security, None, {"port_id": port_id}, request_options)

    async def update_port_security(
        self,
        port_id: str,
        *,
        auth_server_enabled: bool | MISSING = MISSING,
        auth_server_enforced: AuthServerEnforced | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the security settings of a switch port; only the given fields change.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.update_port_security,
            None,
            {
                "port_id": port_id,
                "auth_server_enabled": auth_server_enabled,
                "auth_server_enforced": auth_server_enforced,
            },
            request_options,
        )

    async def set_port_security_auth_server_enabled(
        self, port_id: str, auth_server_enabled: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the authentication server of a switch port.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_port_security_auth_server_enabled,
            None,
            {"port_id": port_id, "auth_server_enabled": auth_server_enabled},
            request_options,
        )

    async def set_port_security_auth_server_enforced(
        self, port_id: str, auth_server_enforced: AuthServerEnforced, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set how strongly the authentication server is enforced on a switch port.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_port_security_auth_server_enforced,
            None,
            {"port_id": port_id, "auth_server_enforced": auth_server_enforced},
            request_options,
        )
