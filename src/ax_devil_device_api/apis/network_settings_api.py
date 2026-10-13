# GENERATED from specs/apis/network-video/network-settings-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read the network configuration and configure hostname, IPv4 and IPv6, DNS resolver, global proxy, VLANs, wired 802.1X and MACsec, and WLAN station and access point settings.

Docs: https://developer.axis.com/vapix/network-video/network-settings-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, Applicability, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import GetSupportedVersions, JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

TcpEcnMode = Literal["disabled", "acceptAndInitiate", "acceptOnly"]
DeviceSwitchingMode = Literal["auto", "manual", "none"]
DeviceType = Literal["wired", "wlan", "wwan", "bridged", "switchPort"]
ConfigurationMode = Literal["static", "dhcp"]
LinkLocalMode = Literal["off", "on", "fallback"]
AddressOrigin = Literal["unknown", "static", "dhcp", "linkLocal", "RA"]
AddressScope = Literal["nowhere", "host", "link", "site", "global"]
WiredLinkMode = Literal[
    "auto", "10BaseT-HD", "10BaseT-FD", "100BaseTX-HD", "100BaseTX-FD", "1000BaseTX-HD", "1000BaseTX-FD"
]
Wired8021xMode = Literal["WPA-Enterprise-PEAP-MSCHAPv2", "WPA-Enterprise-EAPTLS", "MACsec-PSK"]
PeapVersion = Literal["PEAPv0", "PEAPv1"]
PeapLabel = Literal[1, 2]
WlanAuthenticationMode = Literal[
    "none", "WPA-Personal-PSK", "WPA-Personal-HEX", "WPA-Enterprise-PEAP-MSCHAPv2", "WPA-Enterprise-EAPTLS"
]
Ieee8021xStatus = Literal["Unknown", "Stopped", "Unauthorized", "Authorized", "Connecting"]
EapolVersion = Literal["EAPoLv1", "EAPoLv2", "EAPoLv3"]
DeviceStaticState = Literal["up", "down"]
DeviceState = Literal["up", "down"]
WlanBand = Literal["2.4GHz", "5GHz"]
WlanSecurityType = Literal["None", "PSK", "IEEE 802.1X"]
WlanSecurityVersion = Literal["WPA1", "WPA2"]


class SystemInfoWlan(Model):
    """WLAN settings that are not tied to one device."""

    country_code: str | None = Field(default=None, validation_alias="countryCode", serialization_alias="countryCode")
    """The country code of the WLAN regulatory domain; XX means not configured. Only present when a WLAN device exists."""
    country_code_lock: bool | None = Field(
        default=None, validation_alias="countryCodeLock", serialization_alias="countryCodeLock"
    )
    """Whether setting the country code is disallowed, based on regulatory requirements."""


class SystemInfoDeviceSwitching(Model):
    """Selection of active network interface devices."""

    mode: DeviceSwitchingMode | None = None
    devices: list[str] | None = None
    """Available devices, highest priority first."""
    manual_active_devices: list[str] | None = Field(
        default=None, validation_alias="manualActiveDevices", serialization_alias="manualActiveDevices"
    )
    """Devices brought up when the mode is manual."""
    active_devices: list[str] | None = Field(
        default=None, validation_alias="activeDevices", serialization_alias="activeDevices"
    )
    """Devices that are currently active."""


class SystemInfoHostname(Model):
    """Hostname settings."""

    use_dhcp_hostname: bool | None = Field(
        default=None, validation_alias="useDhcpHostname", serialization_alias="useDhcpHostname"
    )
    """Prefer a DHCP provided hostname over the static hostname."""
    hostname: str | None = None
    """The hostname in use."""
    static_hostname: str | None = Field(
        default=None, validation_alias="staticHostname", serialization_alias="staticHostname"
    )
    """The static hostname."""


class SystemInfoResolver(Model):
    """DNS resolver settings."""

    use_dhcp_resolver_info: bool | None = Field(
        default=None, validation_alias="useDhcpResolverInfo", serialization_alias="useDhcpResolverInfo"
    )
    """Prefer the DHCP provided resolver configuration over the static one."""
    name_servers: list[str] | None = Field(
        default=None, validation_alias="nameServers", serialization_alias="nameServers"
    )
    """Name servers in use."""
    static_name_servers: list[str] | None = Field(
        default=None, validation_alias="staticNameServers", serialization_alias="staticNameServers"
    )
    """The static name servers."""
    max_supported_static_name_servers: int | None = Field(
        default=None,
        validation_alias="maxSupportedStaticNameServers",
        serialization_alias="maxSupportedStaticNameServers",
    )
    """Maximum number of static name servers."""
    search_domains: list[str] | None = Field(
        default=None, validation_alias="searchDomains", serialization_alias="searchDomains"
    )
    """Search domains in use."""
    static_search_domains: list[str] | None = Field(
        default=None, validation_alias="staticSearchDomains", serialization_alias="staticSearchDomains"
    )
    """The static search domains."""
    max_supported_static_search_domains: int | None = Field(
        default=None,
        validation_alias="maxSupportedStaticSearchDomains",
        serialization_alias="maxSupportedStaticSearchDomains",
    )
    """Maximum number of static search domains."""
    domain_name: str | None = Field(default=None, validation_alias="domainName", serialization_alias="domainName")
    """The domain name in use."""
    static_domain_name: str | None = Field(
        default=None, validation_alias="staticDomainName", serialization_alias="staticDomainName"
    )
    """The static domain name."""


class SystemInfoGlobalProxies(Model):
    """Global proxy settings."""

    http_proxy: str | None = Field(default=None, validation_alias="httpProxy", serialization_alias="httpProxy")
    """The global HTTP proxy. Sensitive information such as passwords is obscured."""
    https_proxy: str | None = Field(default=None, validation_alias="httpsProxy", serialization_alias="httpsProxy")
    """The global HTTPS proxy. Sensitive information such as passwords is obscured."""
    no_proxy: str | None = Field(default=None, validation_alias="noProxy", serialization_alias="noProxy")
    """The global no_proxy list."""


class SystemInfo(Model):
    """Network parameters that are not tied to one network interface device."""

    tcp_ecn_mode: TcpEcnMode | None = Field(
        default=None, validation_alias="tcpEcnMode", serialization_alias="tcpEcnMode"
    )
    """The TCP ECN mode."""
    wlan: SystemInfoWlan | None = None
    """WLAN settings that are not tied to one device."""
    device_switching: SystemInfoDeviceSwitching | None = Field(
        default=None, validation_alias="deviceSwitching", serialization_alias="deviceSwitching"
    )
    """Selection of active network interface devices."""
    hostname: SystemInfoHostname | None = None
    """Hostname settings."""
    resolver: SystemInfoResolver | None = None
    """DNS resolver settings."""
    global_proxies: SystemInfoGlobalProxies | None = Field(
        default=None, validation_alias="globalProxies", serialization_alias="globalProxies"
    )
    """Global proxy settings."""
    max_supported_vlans: int | None = Field(
        default=None, validation_alias="maxSupportedVlans", serialization_alias="maxSupportedVlans"
    )
    """The maximum number of VLANs."""


class IPv4Address(Model):
    """An IPv4 address in use."""

    address: str
    prefix_length: int | None = Field(default=None, validation_alias="prefixLength", serialization_alias="prefixLength")
    """The subnet prefix length."""
    broadcast: str | None = None
    """The broadcast address; not always available."""
    origin: AddressOrigin | None = None
    scope: AddressScope | None = None


class StaticIPv4Address(Model):
    """A static IPv4 address configuration."""

    address: str
    prefix_length: int | None = Field(default=None, validation_alias="prefixLength", serialization_alias="prefixLength")
    """The subnet prefix length."""
    broadcast: str | None = None
    """The broadcast address; not always available."""


class IPv4Settings(Model):
    """IPv4 configuration of a device."""

    enabled: bool | None = None
    """Whether IPv4 is enabled."""
    configuration_mode: ConfigurationMode | None = Field(
        default=None, validation_alias="configurationMode", serialization_alias="configurationMode"
    )
    link_local_mode: LinkLocalMode | None = Field(
        default=None, validation_alias="linkLocalMode", serialization_alias="linkLocalMode"
    )
    use_static_dhcp_fallback: bool | None = Field(
        default=None, validation_alias="useStaticDHCPFallback", serialization_alias="useStaticDHCPFallback"
    )
    """Use the static default router as fallback when a DHCP leased default router is unavailable."""
    use_dhcp_static_routes: bool | None = Field(
        default=None, validation_alias="useDHCPStaticRoutes", serialization_alias="useDHCPStaticRoutes"
    )
    """Use DHCP classless static routes; the DHCP leased default router is then ignored."""
    addresses: list[IPv4Address] | None = None
    """All addresses in use."""
    max_supported_static_address_configurations: int | None = Field(
        default=None,
        validation_alias="maxSupportedStaticAddressConfigurations",
        serialization_alias="maxSupportedStaticAddressConfigurations",
    )
    """Maximum number of static address configurations."""
    static_address_configurations: list[StaticIPv4Address] | None = Field(
        default=None, validation_alias="staticAddressConfigurations", serialization_alias="staticAddressConfigurations"
    )
    """The static address configurations."""
    default_router: str | None = Field(
        default=None, validation_alias="defaultRouter", serialization_alias="defaultRouter"
    )
    """The default router in use."""
    static_default_router: str | None = Field(
        default=None, validation_alias="staticDefaultRouter", serialization_alias="staticDefaultRouter"
    )
    """The static default router."""


class IPv6Address(Model):
    """An IPv6 address in use."""

    address: str
    prefix_length: int | None = Field(default=None, validation_alias="prefixLength", serialization_alias="prefixLength")
    """The subnet prefix length."""
    origin: AddressOrigin | None = None
    scope: AddressScope | None = None


class StaticIPv6Address(Model):
    """A static IPv6 address configuration."""

    address: str
    prefix_length: int | None = Field(default=None, validation_alias="prefixLength", serialization_alias="prefixLength")
    """The subnet prefix length."""


class IPv6Settings(Model):
    """IPv6 configuration of a device."""

    enabled: bool | None = None
    """Whether IPv6 is enabled."""
    configuration_mode: ConfigurationMode | None = Field(
        default=None, validation_alias="configurationMode", serialization_alias="configurationMode"
    )
    addresses: list[IPv6Address] | None = None
    """All addresses in use."""
    max_supported_static_address_configurations: int | None = Field(
        default=None,
        validation_alias="maxSupportedStaticAddressConfigurations",
        serialization_alias="maxSupportedStaticAddressConfigurations",
    )
    """Maximum number of static address configurations."""
    static_address_configurations: list[StaticIPv6Address] | None = Field(
        default=None, validation_alias="staticAddressConfigurations", serialization_alias="staticAddressConfigurations"
    )
    """The static address configurations."""
    default_router: str | None = Field(
        default=None, validation_alias="defaultRouter", serialization_alias="defaultRouter"
    )
    """The default router in use."""
    static_default_router: str | None = Field(
        default=None, validation_alias="staticDefaultRouter", serialization_alias="staticDefaultRouter"
    )
    """The static default router."""


class Wired8021xParams(Model):
    """Parameters of one wired 802.1X mode."""

    identity: str | None = None
    """The EAP identity."""
    is_password_set: bool | None = None
    """Whether a password is set."""
    eapol_version: EapolVersion | None = Field(
        default=None, validation_alias="eapolVersion", serialization_alias="eapolVersion"
    )
    peap_version: PeapVersion | None = Field(
        default=None, validation_alias="peapVersion", serialization_alias="peapVersion"
    )
    label: PeapLabel | None = None
    is_mka_cak_set: bool | None = None
    """Whether the MACsec Key Agreement CAK is set."""
    mka_ckn: str | None = Field(default=None, validation_alias="mkaCkn", serialization_alias="mkaCkn")
    """The MACsec Key Agreement CAK name."""
    cert_client: str | None = Field(default=None, validation_alias="certClient", serialization_alias="certClient")
    """The client certificate ID used for EAP-TLS."""
    certs_ca: list[str] | None = Field(default=None, validation_alias="certsCA", serialization_alias="certsCA")
    """The CA certificate IDs used for EAP-TLS and MSCHAPv2."""


class Wired8021xConfiguration(Model):
    """One configured wired 802.1X mode."""

    mode: Wired8021xMode | None = None
    params: Wired8021xParams | None = None


class Wired8021x(Model):
    """Wired 802.1X state; its presence indicates support."""

    enabled: bool | None = None
    """Whether 802.1X is enabled on the interface."""
    status: Ieee8021xStatus | None = None
    mode: Wired8021xMode | None = None
    """The active mode."""
    configurations: list[Wired8021xConfiguration] | None = None
    """The configured modes."""
    supported_modes: list[Wired8021xMode] | None = Field(
        default=None, validation_alias="supportedModes", serialization_alias="supportedModes"
    )
    """The supported modes."""
    ma_csec_secured: bool | None = Field(
        default=None, validation_alias="MACsecSecured", serialization_alias="MACsecSecured"
    )
    """Whether the connection is secured by MACsec; applies to MACsec-PSK, or WPA-Enterprise-EAPTLS with EAPoL version 3."""


class WiredSettings(Model):
    """Parameters exclusive to wired devices."""

    link_mode: WiredLinkMode | None = Field(default=None, validation_alias="linkMode", serialization_alias="linkMode")
    is_downlink: bool | None = Field(default=None, validation_alias="isDownlink", serialization_alias="isDownlink")
    """Whether the device is a downlink (towards leaf devices) rather than an uplink."""
    supported_link_modes: list[WiredLinkMode] | None = Field(
        default=None, validation_alias="supportedLinkModes", serialization_alias="supportedLinkModes"
    )
    """The supported link modes."""
    ieee_8021x: Wired8021x | None = Field(default=None, validation_alias="8021X", serialization_alias="8021X")


class WlanStationParams(Model):
    """Parameters of one WLAN station 802.1X mode."""

    is_psk_set: bool | None = None
    """Whether the pre-shared key is set."""
    is_hex_set: bool | None = None
    """Whether the hex key is set."""
    is_password_set: bool | None = None
    """Whether the password is set."""
    identity: str | None = None
    """The EAP identity."""
    eapol_version: EapolVersion | None = Field(
        default=None, validation_alias="eapolVersion", serialization_alias="eapolVersion"
    )
    peap_version: PeapVersion | None = Field(
        default=None, validation_alias="peapVersion", serialization_alias="peapVersion"
    )
    label: PeapLabel | None = None
    cert_client: str | None = Field(default=None, validation_alias="certClient", serialization_alias="certClient")
    """The client certificate ID."""
    certs_ca: list[str] | None = Field(default=None, validation_alias="certsCA", serialization_alias="certsCA")
    """The CA certificate IDs."""


class WlanStationConfiguration(Model):
    """One configured WLAN station mode."""

    mode: WlanAuthenticationMode | None = None
    params: WlanStationParams | None = None


class WlanStation8021x(Model):
    """WLAN station authentication state."""

    enabled: bool | None = None
    """Whether the WLAN station is enabled on the interface."""
    status: Ieee8021xStatus | None = None
    mode: WlanAuthenticationMode | None = None
    """The active mode."""
    configurations: list[WlanStationConfiguration] | None = None
    """The configured modes."""
    supported_modes: list[WlanAuthenticationMode] | None = Field(
        default=None, validation_alias="supportedModes", serialization_alias="supportedModes"
    )
    """The supported modes."""


class WlanStation(Model):
    """WLAN station feature; its presence indicates support."""

    active_ssid: str | None = Field(default=None, validation_alias="activeSsid", serialization_alias="activeSsid")
    """The SSID of the configured station."""
    ieee_8021x: WlanStation8021x | None = Field(default=None, validation_alias="8021X", serialization_alias="8021X")


class WlanAccessPoint(Model):
    """WLAN access point feature; its presence indicates support."""

    ssid: str | None = None
    """The access point SSID."""
    enabled: bool | None = None
    """Whether the access point is enabled on the interface."""
    authentication_mode: WlanAuthenticationMode | None = Field(
        default=None, validation_alias="authenticationMode", serialization_alias="authenticationMode"
    )
    """The active authentication mode."""
    installation_mode_supported: bool | None = Field(
        default=None, validation_alias="installationModeSupported", serialization_alias="installationModeSupported"
    )
    """Present when the access point supports the installation mode."""


class WlanSettings(Model):
    """Parameters exclusive to WLAN devices."""

    station: WlanStation | None = None
    access_point: WlanAccessPoint | None = Field(
        default=None, validation_alias="accessPoint", serialization_alias="accessPoint"
    )


class SwitchPortSettings(Model):
    """Parameters exclusive to switchPort devices."""

    port_number: int | None = Field(default=None, validation_alias="portNumber", serialization_alias="portNumber")
    """The switch port number."""
    remote_addresses: list[str] | None = Field(
        default=None, validation_alias="remoteAddresses", serialization_alias="remoteAddresses"
    )
    """Remote MAC addresses seen on the port."""


class NetworkDevice(Model):
    """A network interface device."""

    name: str
    """Name of the network interface device."""
    type: DeviceType
    mac_address: str | None = Field(default=None, validation_alias="macAddress", serialization_alias="macAddress")
    """The MAC address."""
    part_of_bridge: str | None = Field(
        default=None, validation_alias="partOfBridge", serialization_alias="partOfBridge"
    )
    """Name of the bridge device this device is part of, or an empty string."""
    link: bool | None = None
    """Whether a link is detected."""
    static_state: DeviceStaticState | None = Field(
        default=None, validation_alias="staticState", serialization_alias="staticState"
    )
    """Whether the interface should be up or down."""
    state: DeviceState | None = None
    """Whether the interface is up or down."""
    ipv4: IPv4Settings | None = Field(default=None, validation_alias="IPv4", serialization_alias="IPv4")
    ipv6: IPv6Settings | None = Field(default=None, validation_alias="IPv6", serialization_alias="IPv6")
    wired: WiredSettings | None = None
    wlan: WlanSettings | None = None
    switch_port: SwitchPortSettings | None = Field(
        default=None, validation_alias="switchPort", serialization_alias="switchPort"
    )


class NetworkInfo(Model):
    system: SystemInfo
    devices: list[NetworkDevice]
    """The network interface devices."""


class WlanSecurity(Model):
    """One security option of a network."""

    authentication: WlanSecurityType | None = None
    version: WlanSecurityVersion | None = None
    """Only applicable when authentication is PSK or IEEE 802.1X."""


class WlanNetwork(Model):
    """A WLAN network found by a scan."""

    ssid: str
    """The SSID."""
    band: WlanBand | None = None
    channel: int | None = None
    """The network channel."""
    signal_strength_d_bm: int | None = Field(
        default=None, validation_alias="signalStrengthDBm", serialization_alias="signalStrengthDBm"
    )
    """The signal strength in dBm."""
    security: list[WlanSecurity] | None = None
    """The security parameters available on the network."""


class WlanScanResult(Model):
    networks: list[WlanNetwork]


class WlanTestResult(Model):
    """Outcome of a WLAN station test."""

    code: int
    """Result of the test: 0 authentication successful, 1 authentication failed, 2 timeout connecting to the access point, 3 WLAN station configuration changed, 4 interrupted by interface change, 5 WLAN configuration is incomplete."""
    message: str
    """A message describing the result code."""


class WlanSwitchResult(Model):
    """Outcome of the switch from access point to station."""

    code: int
    """0: the connection process started."""
    message: str
    """A message describing the result code."""


class WlanStationAuthParams(Model):
    """WLAN station 802.1X authentication parameters."""

    identity: str | None = None
    """The EAP identity. Unchanged if omitted."""
    password: str | None = None
    """The password. Unchanged if omitted."""
    eapol_version: EapolVersion | None = Field(
        default=None, validation_alias="eapolVersion", serialization_alias="eapolVersion"
    )
    peap_version: PeapVersion | None = Field(
        default=None, validation_alias="peapVersion", serialization_alias="peapVersion"
    )
    label: PeapLabel | None = None
    cert_client: str | None = Field(default=None, validation_alias="certClient", serialization_alias="certClient")
    """The client certificate ID for EAP-TLS. Unchanged if omitted."""
    certs_ca: list[str] | None = Field(default=None, validation_alias="certsCA", serialization_alias="certsCA")
    """The CA certificate IDs for EAP-TLS and MSCHAPv2. Unchanged if omitted."""


class WlanStationAuthentication(Model):
    """WLAN station authentication settings."""

    mode: WlanAuthenticationMode | None = None
    """The authentication mode to use."""
    params: WlanStationAuthParams | None = None


class AddVlanRequest(Model):
    master_device_name: str = Field(validation_alias="masterDeviceName", serialization_alias="masterDeviceName")
    """The network device the VLAN is attached to, for example eth0."""
    vlan_id: int = Field(validation_alias="VlanId", serialization_alias="VlanId")
    """The numerical VLAN identifier. The VLAN is named after its master device and ID, for example eth0.4."""


class RemoveVlanRequest(Model):
    master_device_name: str = Field(validation_alias="masterDeviceName", serialization_alias="masterDeviceName")
    """The network device the VLAN is attached to, for example eth0."""
    vlan_name: str = Field(validation_alias="VlanName", serialization_alias="VlanName")
    """The full name of the VLAN to remove, for example eth0.4."""


class ScanWlanNetworksRequest(Model):
    device_name: str = Field(validation_alias="deviceName", serialization_alias="deviceName")
    """The name of the network interface device; see get_network_info."""
    refresh: bool | None = None
    """Make a new scan (true) or fetch the previous scan. A new scan is made if none exists or if this is not set."""


class SetDeviceConfigurationRequest(Model):
    device_name: str = Field(validation_alias="deviceName", serialization_alias="deviceName")
    """The name of the network interface device; see get_network_info."""
    static_state: DeviceStaticState | None = Field(
        default=None, validation_alias="staticState", serialization_alias="staticState"
    )
    """Whether the interface should be up or down. When down, link is false and state is down, which persistently disables network traffic."""


class SetHostnameConfigurationRequest(Model):
    use_dhcp_hostname: bool | None = Field(
        default=None, validation_alias="useDhcpHostname", serialization_alias="useDhcpHostname"
    )
    """Prefer a DHCP provided hostname over the static hostname. Unchanged if omitted."""
    static_hostname: str | None = Field(
        default=None, validation_alias="staticHostname", serialization_alias="staticHostname"
    )
    """The static hostname, used unless a DHCP server provides one while useDhcpHostname is set. Unchanged if omitted."""


class SetGlobalProxyConfigurationRequest(Model):
    http_proxy: str | None = Field(default=None, validation_alias="httpProxy", serialization_alias="httpProxy")
    """The global HTTP proxy."""
    https_proxy: str | None = Field(default=None, validation_alias="httpsProxy", serialization_alias="httpsProxy")
    """The global HTTPS proxy."""
    no_proxy: str | None = Field(default=None, validation_alias="noProxy", serialization_alias="noProxy")
    """The global no_proxy list. Wildcards are not allowed; use a dot prefix (.axis.com) for subdomains and CIDR notation (192.168.0.0/24) for networks."""


class SetResolverConfigurationRequest(Model):
    use_dhcp_resolver_info: bool | None = Field(
        default=None, validation_alias="useDhcpResolverInfo", serialization_alias="useDhcpResolverInfo"
    )
    """Prefer the DHCP provided resolver configuration over the static one. Unchanged if omitted."""
    static_name_servers: list[str] | None = Field(
        default=None, validation_alias="staticNameServers", serialization_alias="staticNameServers"
    )
    """Static name servers; the maximum count is maxSupportedStaticNameServers. Unchanged if omitted."""
    static_search_domains: list[str] | None = Field(
        default=None, validation_alias="staticSearchDomains", serialization_alias="staticSearchDomains"
    )
    """Static search domains; the maximum count is maxSupportedStaticSearchDomains. Unchanged if omitted."""
    static_domain_name: str | None = Field(
        default=None, validation_alias="staticDomainName", serialization_alias="staticDomainName"
    )
    """The static domain name. Unchanged if omitted."""


class SetWlanConfigurationRequest(Model):
    country_code: str = Field(validation_alias="countryCode", serialization_alias="countryCode")
    """The country code of the WLAN regulatory domain. XX cannot be set, and the code cannot change while countryCodeLock is true."""


class SetWlanStationConfigurationRequest(Model):
    device_name: str = Field(validation_alias="deviceName", serialization_alias="deviceName")
    """The name of the network interface device; see get_network_info."""
    ssid: str | None = None
    """The SSID of the wireless access point."""
    authentication: WlanStationAuthentication | None = None


class TestWlanStationSettingsRequest(Model):
    device_name: str = Field(validation_alias="deviceName", serialization_alias="deviceName")
    """The network interface device to test; see get_network_info."""
    timeout: int | None = None
    """The timeout of the call in seconds. Defaults to 10. Default: 10."""


class SetIpv4AddressConfigurationRequest(Model):
    device_name: str = Field(validation_alias="deviceName", serialization_alias="deviceName")
    """The name of the network interface device; see get_network_info."""
    enabled: bool | None = None
    """Whether IPv4 is enabled. IPv4 cannot be disabled while IPv6 is disabled. Unchanged if omitted."""
    configuration_mode: ConfigurationMode | None = Field(
        default=None, validation_alias="configurationMode", serialization_alias="configurationMode"
    )
    """The IPv4 address configuration mode. Unchanged if omitted."""
    link_local_mode: LinkLocalMode | None = Field(
        default=None, validation_alias="linkLocalMode", serialization_alias="linkLocalMode"
    )
    """The link-local mode. Unchanged if omitted."""
    static_default_router: str | None = Field(
        default=None, validation_alias="staticDefaultRouter", serialization_alias="staticDefaultRouter"
    )
    """The router address, used when the mode is static or dhcp but no router is advertised. Unchanged if omitted."""
    use_static_dhcp_fallback: bool | None = Field(
        default=None, validation_alias="useStaticDHCPFallback", serialization_alias="useStaticDHCPFallback"
    )
    """Use the static default router as fallback when a DHCP leased default router is unavailable."""
    use_dhcp_static_routes: bool | None = Field(
        default=None, validation_alias="useDHCPStaticRoutes", serialization_alias="useDHCPStaticRoutes"
    )
    """Use DHCP classless static routes; the DHCP leased default router is then ignored."""
    static_address_configurations: list[StaticIPv4Address] | None = Field(
        default=None, validation_alias="staticAddressConfigurations", serialization_alias="staticAddressConfigurations"
    )
    """The static addresses. The maximum count is maxSupportedStaticAddressConfigurations. Unchanged if omitted."""


class SetIpv6AddressConfigurationRequest(Model):
    device_name: str = Field(validation_alias="deviceName", serialization_alias="deviceName")
    """The name of the network interface device; see get_network_info."""
    enabled: bool | None = None
    """Whether IPv6 is enabled. Unchanged if omitted."""


class SetWired8021xConfigurationRequest(Model):
    device_name: str = Field(validation_alias="deviceName", serialization_alias="deviceName")
    """The name of the network interface device; see get_network_info."""
    enabled: bool | None = None
    """Enable 802.1X authentication. Unchanged if omitted."""
    mode: Wired8021xMode | None = None
    """The authentication mode. Unchanged if omitted."""
    identity: str | None = None
    """The EAP identity. Unchanged if omitted."""
    password: str | None = None
    """The EAP password; only used with WPA-Enterprise-PEAP-MSCHAPv2. Unchanged if omitted."""
    eapol_version: EapolVersion | None = Field(
        default=None, validation_alias="eapolVersion", serialization_alias="eapolVersion"
    )
    """The EAPoL version. Unchanged if omitted."""
    peap_version: PeapVersion | None = Field(
        default=None, validation_alias="peapVersion", serialization_alias="peapVersion"
    )
    """The PEAP version; only used with WPA-Enterprise-PEAP-MSCHAPv2. Unchanged if omitted."""
    label: PeapLabel | None = None
    """The PEAP label; only used with WPA-Enterprise-PEAP-MSCHAPv2. Unchanged if omitted."""
    cert_client: str | None = Field(default=None, validation_alias="certClient", serialization_alias="certClient")
    """The client certificate ID that identifies the client to the radius server; required to enable WPA-Enterprise-EAPTLS. An empty string unsets it. Unchanged if omitted."""
    certs_ca: list[str] | None = Field(default=None, validation_alias="certsCA", serialization_alias="certsCA")
    """The CA certificate IDs that identify the radius server certificate chain. An empty list unsets them. Unchanged if omitted."""
    mka_cak: str | None = Field(default=None, validation_alias="mkaCak", serialization_alias="mkaCak")
    """The MACsec Key Agreement CAK for MACsec-PSK: 32 or 64 hexadecimal characters. Unchanged if omitted."""
    mka_ckn: str | None = Field(default=None, validation_alias="mkaCkn", serialization_alias="mkaCkn")
    """The MACsec Key Agreement CAK name for MACsec-PSK: 2 to 64 hexadecimal characters, an even count. Unchanged if omitted."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/network_settings.cgi"

INFO = ApiInfo(
    id="network-settings-api",
    name="Network settings API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(
        ApiVersion(1, 0),
        ApiVersion(1, 6),
        ApiVersion(1, 9),
        ApiVersion(1, 12),
        ApiVersion(1, 14),
        ApiVersion(1, 15),
        ApiVersion(1, 16),
        ApiVersion(1, 17),
        ApiVersion(1, 21),
        ApiVersion(1, 27),
        ApiVersion(1, 29),
    ),
    discovery=(ApiDiscovery("network-settings"),),
    docs=("https://developer.axis.com/vapix/network-video/network-settings-api/",),
    errors={
        1000: ErrorCode("Internal error.", "internal"),
        2000: ErrorCode("Invalid request.", "invalid_argument"),
        2001: ErrorCode("Request body too large.", "invalid_argument"),
        3000: ErrorCode("Invalid JSON data.", "invalid_argument"),
        4000: ErrorCode("Method does not exist.", "not_found"),
        4001: ErrorCode("The specified version is not supported.", "unsupported"),
        4002: ErrorCode("Authorization failed.", "access_denied"),
        4003: ErrorCode("Missing parameter(s).", "invalid_argument"),
        4004: ErrorCode("Invalid parameter(s).", "invalid_argument"),
    },
)


class OPS:
    add_vlan = Operation(
        INFO,
        "add_vlan",
        JsonRpcBinding("addVlan", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=AddVlanRequest,
        access="admin",
        effect="write",
        write="create",
        errors={
            "4004/subCode 100": ErrorCode("Parameter masterDeviceName error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter VlanId error.", "invalid_argument"),
            "4004/subCode 201": ErrorCode("VLAN already exists.", "invalid_argument"),
            "4004/subCode 202": ErrorCode("Maximum number of VLANs in use.", "unavailable"),
        },
    )
    get_network_info = Operation(
        INFO,
        "get_network_info",
        JsonRpcBinding("getNetworkInfo", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        result=NetworkInfo,
        access="admin",
        effect="read",
    )
    remove_vlan = Operation(
        INFO,
        "remove_vlan",
        JsonRpcBinding("removeVlan", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=RemoveVlanRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={
            "4004/subCode 100": ErrorCode("Parameter VlanName error.", "invalid_argument"),
            "4004/subCode 200": ErrorCode("VLAN still present in manual active devices list.", "invalid_argument"),
            "4004/subCode 201": ErrorCode("VLAN does not exist.", "not_found"),
            "4004/subCode 202": ErrorCode("VLAN exists, but is not created by user.", "invalid_argument"),
        },
    )
    scan_wlan_networks = Operation(
        INFO,
        "scan_wlan_networks",
        JsonRpcBinding("scanWLANNetworks", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=ScanWlanNetworksRequest,
        result=WlanScanResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 14),
        errors={
            5000: ErrorCode("No device found for the given device name.", "not_found"),
            "4004/subCode 100": ErrorCode("Parameter deviceName error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter refresh error.", "invalid_argument"),
        },
    )
    set_device_configuration = Operation(
        INFO,
        "set_device_configuration",
        JsonRpcBinding("setDeviceConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetDeviceConfigurationRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 17),
        write="patch",
        errors={
            5000: ErrorCode("No device found for the given device name.", "not_found"),
            "4004/subCode 100": ErrorCode("Parameter deviceName error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter staticState error.", "invalid_argument"),
        },
    )
    set_hostname_configuration = Operation(
        INFO,
        "set_hostname_configuration",
        JsonRpcBinding("setHostnameConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetHostnameConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "4004/subCode 100": ErrorCode("Parameter staticHostname error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter useDhcpHostname error.", "invalid_argument"),
        },
    )
    set_global_proxy_configuration = Operation(
        INFO,
        "set_global_proxy_configuration",
        JsonRpcBinding("setGlobalProxyConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetGlobalProxyConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "4004/subCode 100": ErrorCode("Parameter httpProxy error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter httpsProxy error.", "invalid_argument"),
            "4004/subCode 102": ErrorCode("Parameter noProxy error.", "invalid_argument"),
        },
    )
    set_resolver_configuration = Operation(
        INFO,
        "set_resolver_configuration",
        JsonRpcBinding("setResolverConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetResolverConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "4004/subCode 100": ErrorCode("Parameter useDhcpResolverInfo error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter staticNameServers error.", "invalid_argument"),
            "4004/subCode 102": ErrorCode("Parameter staticSearchDomains error.", "invalid_argument"),
            "4004/subCode 103": ErrorCode("Parameter staticDomainName error.", "invalid_argument"),
        },
    )
    set_wlan_configuration = Operation(
        INFO,
        "set_wlan_configuration",
        JsonRpcBinding("setWlanConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetWlanConfigurationRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 27),
        write="patch",
        errors={
            "4004/subCode 100": ErrorCode("Parameter countryCode error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("No WLAN device present on the system.", "unsupported"),
            "4004/subCode 102": ErrorCode(
                "The countryCode of the WLAN device is locked and not allowed to change.", "unavailable"
            ),
        },
    )
    set_wlan_station_configuration = Operation(
        INFO,
        "set_wlan_station_configuration",
        JsonRpcBinding("setWLANStationConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetWlanStationConfigurationRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 12),
        write="patch",
        errors={
            5000: ErrorCode("No device found for the given device name.", "not_found"),
            "4004/subCode 100": ErrorCode("Parameter deviceName error.", "invalid_argument"),
            "4004/subCode 102": ErrorCode("Parameter mode error.", "invalid_argument"),
            "4004/subCode 103": ErrorCode("Parameter identity error.", "invalid_argument"),
            "4004/subCode 104": ErrorCode("Parameter eapolVersion error.", "invalid_argument"),
            "4004/subCode 105": ErrorCode("Parameter ssid error.", "invalid_argument"),
            "4004/subCode 106": ErrorCode("Parameter authentication error.", "invalid_argument"),
            "4004/subCode 107": ErrorCode("Parameter password error.", "invalid_argument"),
            "4004/subCode 108": ErrorCode("Parameter peapVersion error.", "invalid_argument"),
            "4004/subCode 109": ErrorCode("Parameter label error.", "invalid_argument"),
            "4004/subCode 110": ErrorCode("Parameter mkaCak error.", "invalid_argument"),
            "4004/subCode 111": ErrorCode("Parameter mkaCkn error.", "invalid_argument"),
            "4004/subCode 112": ErrorCode("Parameter certClient error.", "invalid_argument"),
            "4004/subCode 113": ErrorCode("Parameter certsCA error.", "invalid_argument"),
        },
    )
    test_wlan_station_settings = Operation(
        INFO,
        "test_wlan_station_settings",
        JsonRpcBinding("testWLANStationSettings", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=TestWlanStationSettingsRequest,
        result=WlanTestResult,
        access="admin",
        effect="action",
        errors={
            5000: ErrorCode("No device found for the given device name.", "not_found"),
            5001: ErrorCode("Invalid device supplied.", "invalid_argument"),
        },
    )
    wlan_switch_ap_to_station = Operation(
        INFO,
        "wlan_switch_ap_to_station",
        JsonRpcBinding("wlanSwitchAPToStation", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        result=WlanSwitchResult,
        access="admin",
        effect="action",
        since=ApiVersion(1, 16),
        errors={
            5000: ErrorCode("No device found for the given device name.", "not_found"),
            5003: ErrorCode("Device is not in installation mode.", "unavailable"),
            5004: ErrorCode("Incomplete WLAN configuration.", "unavailable"),
        },
    )
    set_ipv4_address_configuration = Operation(
        INFO,
        "set_ipv4_address_configuration",
        JsonRpcBinding("setIPv4AddressConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetIpv4AddressConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        applicability=(
            Applicability("link_local_mode", ApiVersion(1, 21)),
            Applicability("use_static_dhcp_fallback", ApiVersion(1, 21)),
            Applicability("use_dhcp_static_routes", ApiVersion(1, 29)),
        ),
        errors={
            5000: ErrorCode("No device found for the given device name.", "not_found"),
            "4004/subCode 100": ErrorCode("Parameter deviceName error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter configurationMode error.", "invalid_argument"),
            "4004/subCode 102": ErrorCode("Parameter staticDefaultRouter error.", "invalid_argument"),
            "4004/subCode 103": ErrorCode("Parameter staticAddressConfigurations error.", "invalid_argument"),
            "4004/subCode 104": ErrorCode("Parameter address error.", "invalid_argument"),
            "4004/subCode 105": ErrorCode("Parameter prefixLength error.", "invalid_argument"),
            "4004/subCode 106": ErrorCode("Parameter broadcast error.", "invalid_argument"),
            "4004/subCode 107": ErrorCode(
                "Parameter address/prefixLength/broadcast combination error.", "invalid_argument"
            ),
            "4004/subCode 108": ErrorCode("Parameter useStaticDHCPFallback error.", "invalid_argument"),
            "4004/subCode 109": ErrorCode("Parameter linkLocalMode error.", "invalid_argument"),
            "4004/subCode 110": ErrorCode("Parameter useDHCPStaticRoutes error.", "invalid_argument"),
            "4004/subCode 111": ErrorCode("Parameter enabled error.", "invalid_argument"),
        },
    )
    set_ipv6_address_configuration = Operation(
        INFO,
        "set_ipv6_address_configuration",
        JsonRpcBinding("setIPv6AddressConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetIpv6AddressConfigurationRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 6),
        write="patch",
        errors={
            5000: ErrorCode("No device found for the given device name.", "not_found"),
            "4004/subCode 100": ErrorCode("Parameter deviceName error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter enabled error.", "invalid_argument"),
        },
    )
    set_wired_8021x_configuration = Operation(
        INFO,
        "set_wired_8021x_configuration",
        JsonRpcBinding("setWired8021XConfiguration", PATH, negotiation=GetSupportedVersions(key="supportedVersions")),
        params=SetWired8021xConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "4004/subCode 100": ErrorCode("Parameter deviceName error.", "invalid_argument"),
            "4004/subCode 101": ErrorCode("Parameter enabled error.", "invalid_argument"),
            "4004/subCode 102": ErrorCode("Parameter mode error.", "invalid_argument"),
            "4004/subCode 103": ErrorCode("Parameter identity error.", "invalid_argument"),
            "4004/subCode 104": ErrorCode("Parameter eapolVersion error.", "invalid_argument"),
            "4004/subCode 112": ErrorCode("Parameter certClient error.", "invalid_argument"),
            "4004/subCode 113": ErrorCode("Parameter certCA error.", "invalid_argument"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class NetworkSettingsApi(SyncApi):
    """Network settings API (``network-settings-api``, version 1)."""

    INFO = INFO

    def add_vlan(self, *, master_device_name: str, vlan_id: int, request_options: RequestOptions | None = None) -> None:
        """Adds a new VLAN.

        This method adds a new VLAN attached to an existing network interface. The maximum number of VLANs
        is limited, see [getNetworkInfo](#get-network-info-api-specification) to determine the allowed
        number. Adds a new VLAN. The call verifies that the master device that should be used as the main
        interface for the VLAN exists. It will also ensure that no duplicates are added if the VLAN already
        exists.

        Access: admin.
        """
        self._run(OPS.add_vlan, None, {"master_device_name": master_device_name, "vlan_id": vlan_id}, request_options)

    def get_network_info(self, *, request_options: RequestOptions | None = None) -> NetworkInfo:
        """Retrieves the current network configuration and network-related parameters for the device.

        This method retrieves the network configuration and additional relevant information from the device.

        Access: admin.
        """
        return self._run(OPS.get_network_info, None, {}, request_options)

    def remove_vlan(
        self, *, master_device_name: str, vlan_name: str, request_options: RequestOptions | None = None
    ) -> None:
        """Removes an existing VLAN.

        This method removes the requested VLAN from the device.

        Access: admin.
        """
        self._run(
            OPS.remove_vlan, None, {"master_device_name": master_device_name, "vlan_name": vlan_name}, request_options
        )

    def scan_wlan_networks(
        self, *, device_name: str, refresh: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> WlanScanResult:
        """Scans for available WLAN networks.

        This method is used to scan for available WLAN networks for a specified WLAN network interface.
        Please note that this functionality is only available on interface devices of the WLAN type with
        indicated support for station in `getNetworkInfo`. See [Read network configuration](#read-network-
        configuration) for information on how to determine if your device has WLAN station support.

        Access: admin.
        """
        return self._run(
            OPS.scan_wlan_networks, None, {"device_name": device_name, "refresh": refresh}, request_options
        )

    def set_device_configuration(
        self,
        *,
        device_name: str,
        static_state: DeviceStaticState | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the network interface device configuration.

        This method is used to configure network interface devices on an Axis device. It can, for example,
        be used to persistently disable network interface devices.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_device_configuration,
            None,
            {"device_name": device_name, "static_state": static_state},
            request_options,
        )

    def set_hostname_configuration(
        self,
        *,
        use_dhcp_hostname: bool | MISSING = MISSING,
        static_hostname: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Configure how the device selects a hostname, with the possibility to set a static hostname and/or enable auto-configuration by DHCP.

        This method is used to configure a static hostname on the device or configure the device to
        automatically switch to a host name assigned to it by a DHCP server on the network. The latter only
        applies if a host name has been received.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_hostname_configuration,
            None,
            {"use_dhcp_hostname": use_dhcp_hostname, "static_hostname": static_hostname},
            request_options,
        )

    def set_global_proxy_configuration(
        self,
        *,
        http_proxy: str | MISSING = MISSING,
        https_proxy: str | MISSING = MISSING,
        no_proxy: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Configure how the Axis device connects to the network.

        This method configures the global proxy configuration on the Axis device. It can be used by all
        services supporting global proxy configuration. Please note that the Axis device must be rebooted
        for the global proxy settings to take effect.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_global_proxy_configuration,
            None,
            {"http_proxy": http_proxy, "https_proxy": https_proxy, "no_proxy": no_proxy},
            request_options,
        )

    def set_resolver_configuration(
        self,
        *,
        use_dhcp_resolver_info: bool | MISSING = MISSING,
        static_name_servers: list[str] | MISSING = MISSING,
        static_search_domains: list[str] | MISSING = MISSING,
        static_domain_name: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Configure how the device selects a DNS resolver configuration by either setting up a static configuration and/or enabling an auto-configuration by DHCP.

        This method is used to set a static domain name server (DNS) configuration on the device, but also
        to configure the device to use DNS servers supplied by a DHCP server.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_resolver_configuration,
            None,
            {
                "use_dhcp_resolver_info": use_dhcp_resolver_info,
                "static_name_servers": static_name_servers,
                "static_search_domains": static_search_domains,
                "static_domain_name": static_domain_name,
            },
            request_options,
        )

    def set_wlan_configuration(self, *, country_code: str, request_options: RequestOptions | None = None) -> None:
        """Apply the WLAN configuration used by WLAN devices.

        This method is used to configure device independent WLAN settings and provides the ability to set
        the regular domain used by all WLAN devices in station mode. Apply the WLAN configuration used by
        WLAN devices. Only regulatory domains can be set.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_wlan_configuration, None, {"country_code": country_code}, request_options)

    @overload
    def set_wlan_station_configuration(
        self, request: SetWlanStationConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_wlan_station_configuration(
        self,
        /,
        *,
        device_name: str,
        ssid: str | MISSING = MISSING,
        authentication: WlanStationAuthentication | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_wlan_station_configuration(
        self,
        request: SetWlanStationConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the connection to a WLAN access point.

        This method is used when you want to configure the WLAN station access control for a specified WLAN
        interface.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_wlan_station_configuration, request, kwargs, request_options)

    def test_wlan_station_settings(
        self, *, device_name: str, timeout: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> WlanTestResult:
        """Perform a test on the WLAN interface by trying to connect and authenticate using the current settings.

        This method triggers a test of the WLAN station settings on the network interface device to confirm
        that they are correct and it can connect to the WLAN Access Point.

        Access: admin.
        """
        return self._run(
            OPS.test_wlan_station_settings, None, {"device_name": device_name, "timeout": timeout}, request_options
        )

    def wlan_switch_ap_to_station(self, *, request_options: RequestOptions | None = None) -> WlanSwitchResult:
        """Connect to a configured access point when your device is in installation mode.

        This method makes the Axis device in installation mode switch from AP to Station mode.

        Access: admin.
        """
        return self._run(OPS.wlan_switch_ap_to_station, None, {}, request_options)

    @overload
    def set_ipv4_address_configuration(
        self, request: SetIpv4AddressConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_ipv4_address_configuration(
        self,
        /,
        *,
        device_name: str,
        enabled: bool | MISSING = MISSING,
        configuration_mode: ConfigurationMode | MISSING = MISSING,
        link_local_mode: LinkLocalMode | MISSING = MISSING,
        static_default_router: str | MISSING = MISSING,
        use_static_dhcp_fallback: bool | MISSING = MISSING,
        use_dhcp_static_routes: bool | MISSING = MISSING,
        static_address_configurations: list[StaticIPv4Address] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_ipv4_address_configuration(
        self,
        request: SetIpv4AddressConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure how the device selects an IPv4 address.

        This method is used to set up a static IPv4 address configuration on a network interface device, but
        also to configure the network interface device to automatically switch to an IPv4 address
        configuration assigned by a DHCP server on the network.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        self._run(OPS.set_ipv4_address_configuration, request, kwargs, request_options)

    def set_ipv6_address_configuration(
        self, *, device_name: str, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Configure IPv6 on your device.

        This method is used to toggle IPv6 on a network interface device.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_ipv6_address_configuration, None, {"device_name": device_name, "enabled": enabled}, request_options
        )

    @overload
    def set_wired_8021x_configuration(
        self, request: SetWired8021xConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_wired_8021x_configuration(
        self,
        /,
        *,
        device_name: str,
        enabled: bool | MISSING = MISSING,
        mode: Wired8021xMode | MISSING = MISSING,
        identity: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        eapol_version: EapolVersion | MISSING = MISSING,
        peap_version: PeapVersion | MISSING = MISSING,
        label: PeapLabel | MISSING = MISSING,
        cert_client: str | MISSING = MISSING,
        certs_ca: list[str] | MISSING = MISSING,
        mka_cak: str | MISSING = MISSING,
        mka_ckn: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_wired_8021x_configuration(
        self,
        request: SetWired8021xConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure how and if the device uses 802.1X authentication on the wired network interface.

        This method is used to configure 802.1X for a wired network interface device.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_wired_8021x_configuration, request, kwargs, request_options)


class AsyncNetworkSettingsApi(AsyncApi):
    """Network settings API (``network-settings-api``, version 1)."""

    INFO = INFO

    async def add_vlan(
        self, *, master_device_name: str, vlan_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Adds a new VLAN.

        This method adds a new VLAN attached to an existing network interface. The maximum number of VLANs
        is limited, see [getNetworkInfo](#get-network-info-api-specification) to determine the allowed
        number. Adds a new VLAN. The call verifies that the master device that should be used as the main
        interface for the VLAN exists. It will also ensure that no duplicates are added if the VLAN already
        exists.

        Access: admin.
        """
        await self._run(
            OPS.add_vlan, None, {"master_device_name": master_device_name, "vlan_id": vlan_id}, request_options
        )

    async def get_network_info(self, *, request_options: RequestOptions | None = None) -> NetworkInfo:
        """Retrieves the current network configuration and network-related parameters for the device.

        This method retrieves the network configuration and additional relevant information from the device.

        Access: admin.
        """
        return await self._run(OPS.get_network_info, None, {}, request_options)

    async def remove_vlan(
        self, *, master_device_name: str, vlan_name: str, request_options: RequestOptions | None = None
    ) -> None:
        """Removes an existing VLAN.

        This method removes the requested VLAN from the device.

        Access: admin.
        """
        await self._run(
            OPS.remove_vlan, None, {"master_device_name": master_device_name, "vlan_name": vlan_name}, request_options
        )

    async def scan_wlan_networks(
        self, *, device_name: str, refresh: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> WlanScanResult:
        """Scans for available WLAN networks.

        This method is used to scan for available WLAN networks for a specified WLAN network interface.
        Please note that this functionality is only available on interface devices of the WLAN type with
        indicated support for station in `getNetworkInfo`. See [Read network configuration](#read-network-
        configuration) for information on how to determine if your device has WLAN station support.

        Access: admin.
        """
        return await self._run(
            OPS.scan_wlan_networks, None, {"device_name": device_name, "refresh": refresh}, request_options
        )

    async def set_device_configuration(
        self,
        *,
        device_name: str,
        static_state: DeviceStaticState | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the network interface device configuration.

        This method is used to configure network interface devices on an Axis device. It can, for example,
        be used to persistently disable network interface devices.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_device_configuration,
            None,
            {"device_name": device_name, "static_state": static_state},
            request_options,
        )

    async def set_hostname_configuration(
        self,
        *,
        use_dhcp_hostname: bool | MISSING = MISSING,
        static_hostname: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Configure how the device selects a hostname, with the possibility to set a static hostname and/or enable auto-configuration by DHCP.

        This method is used to configure a static hostname on the device or configure the device to
        automatically switch to a host name assigned to it by a DHCP server on the network. The latter only
        applies if a host name has been received.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_hostname_configuration,
            None,
            {"use_dhcp_hostname": use_dhcp_hostname, "static_hostname": static_hostname},
            request_options,
        )

    async def set_global_proxy_configuration(
        self,
        *,
        http_proxy: str | MISSING = MISSING,
        https_proxy: str | MISSING = MISSING,
        no_proxy: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Configure how the Axis device connects to the network.

        This method configures the global proxy configuration on the Axis device. It can be used by all
        services supporting global proxy configuration. Please note that the Axis device must be rebooted
        for the global proxy settings to take effect.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_global_proxy_configuration,
            None,
            {"http_proxy": http_proxy, "https_proxy": https_proxy, "no_proxy": no_proxy},
            request_options,
        )

    async def set_resolver_configuration(
        self,
        *,
        use_dhcp_resolver_info: bool | MISSING = MISSING,
        static_name_servers: list[str] | MISSING = MISSING,
        static_search_domains: list[str] | MISSING = MISSING,
        static_domain_name: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Configure how the device selects a DNS resolver configuration by either setting up a static configuration and/or enabling an auto-configuration by DHCP.

        This method is used to set a static domain name server (DNS) configuration on the device, but also
        to configure the device to use DNS servers supplied by a DHCP server.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_resolver_configuration,
            None,
            {
                "use_dhcp_resolver_info": use_dhcp_resolver_info,
                "static_name_servers": static_name_servers,
                "static_search_domains": static_search_domains,
                "static_domain_name": static_domain_name,
            },
            request_options,
        )

    async def set_wlan_configuration(self, *, country_code: str, request_options: RequestOptions | None = None) -> None:
        """Apply the WLAN configuration used by WLAN devices.

        This method is used to configure device independent WLAN settings and provides the ability to set
        the regular domain used by all WLAN devices in station mode. Apply the WLAN configuration used by
        WLAN devices. Only regulatory domains can be set.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_wlan_configuration, None, {"country_code": country_code}, request_options)

    @overload
    async def set_wlan_station_configuration(
        self, request: SetWlanStationConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_wlan_station_configuration(
        self,
        /,
        *,
        device_name: str,
        ssid: str | MISSING = MISSING,
        authentication: WlanStationAuthentication | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_wlan_station_configuration(
        self,
        request: SetWlanStationConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the connection to a WLAN access point.

        This method is used when you want to configure the WLAN station access control for a specified WLAN
        interface.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_wlan_station_configuration, request, kwargs, request_options)

    async def test_wlan_station_settings(
        self, *, device_name: str, timeout: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> WlanTestResult:
        """Perform a test on the WLAN interface by trying to connect and authenticate using the current settings.

        This method triggers a test of the WLAN station settings on the network interface device to confirm
        that they are correct and it can connect to the WLAN Access Point.

        Access: admin.
        """
        return await self._run(
            OPS.test_wlan_station_settings, None, {"device_name": device_name, "timeout": timeout}, request_options
        )

    async def wlan_switch_ap_to_station(self, *, request_options: RequestOptions | None = None) -> WlanSwitchResult:
        """Connect to a configured access point when your device is in installation mode.

        This method makes the Axis device in installation mode switch from AP to Station mode.

        Access: admin.
        """
        return await self._run(OPS.wlan_switch_ap_to_station, None, {}, request_options)

    @overload
    async def set_ipv4_address_configuration(
        self, request: SetIpv4AddressConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_ipv4_address_configuration(
        self,
        /,
        *,
        device_name: str,
        enabled: bool | MISSING = MISSING,
        configuration_mode: ConfigurationMode | MISSING = MISSING,
        link_local_mode: LinkLocalMode | MISSING = MISSING,
        static_default_router: str | MISSING = MISSING,
        use_static_dhcp_fallback: bool | MISSING = MISSING,
        use_dhcp_static_routes: bool | MISSING = MISSING,
        static_address_configurations: list[StaticIPv4Address] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_ipv4_address_configuration(
        self,
        request: SetIpv4AddressConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure how the device selects an IPv4 address.

        This method is used to set up a static IPv4 address configuration on a network interface device, but
        also to configure the network interface device to automatically switch to an IPv4 address
        configuration assigned by a DHCP server on the network.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        await self._run(OPS.set_ipv4_address_configuration, request, kwargs, request_options)

    async def set_ipv6_address_configuration(
        self, *, device_name: str, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Configure IPv6 on your device.

        This method is used to toggle IPv6 on a network interface device.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_ipv6_address_configuration, None, {"device_name": device_name, "enabled": enabled}, request_options
        )

    @overload
    async def set_wired_8021x_configuration(
        self, request: SetWired8021xConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_wired_8021x_configuration(
        self,
        /,
        *,
        device_name: str,
        enabled: bool | MISSING = MISSING,
        mode: Wired8021xMode | MISSING = MISSING,
        identity: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        eapol_version: EapolVersion | MISSING = MISSING,
        peap_version: PeapVersion | MISSING = MISSING,
        label: PeapLabel | MISSING = MISSING,
        cert_client: str | MISSING = MISSING,
        certs_ca: list[str] | MISSING = MISSING,
        mka_cak: str | MISSING = MISSING,
        mka_ckn: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_wired_8021x_configuration(
        self,
        request: SetWired8021xConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure how and if the device uses 802.1X authentication on the wired network interface.

        This method is used to configure 802.1X for a wired network interface device.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_wired_8021x_configuration, request, kwargs, request_options)
