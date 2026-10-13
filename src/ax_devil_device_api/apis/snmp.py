# GENERATED from specs/apis/device-configuration/snmp-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the SNMP settings (v1, v2c, v3, traps and v3 users) on the device.

Docs: https://developer.axis.com/vapix/device-configuration/snmp-api/
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

CommunityNameType = Annotated[str, Field(min_length=1, max_length=32)]
DscpType = Annotated[int, Field(ge=0, le=63)]
EngineBootsType = Annotated[int, Field(ge=0)]
UserEncryptionTypeEnum = Literal["AES-128", "AES-256"]
SupportedEncryptionTypeArray = list[UserEncryptionTypeEnum]
TransportProtocolEnum = Literal["tcp", "udp"]
TrapAddressType = Annotated[str, Field(max_length=46)]
UserPasswdType = Annotated[str, Field(min_length=8, max_length=50)]
UserNameType = Annotated[str, Field(min_length=1, max_length=32, pattern="^[a-zA-Z_][a-zA-Z0-9_-]*$")]
UserAuthenticationTypeEnum = Literal["SHA-256", "SHA-512"]
SecurityLevelTypeEnum = Literal["authNoPriv", "authPriv"]
AccessTypeEnum = Literal["readOnly", "readWrite"]


class Ntcip(Model):
    """NTCIP support"""

    enabled: bool
    """Status of NTCIP support"""


class SnmpV1(Model):
    """V1 snmp support"""

    enabled: bool
    """Status of V1 snmp support"""


class Trap(Model):
    """Trap"""

    auth_fail_enabled: bool | None = Field(
        default=None, validation_alias="authFailEnabled", serialization_alias="authFailEnabled"
    )
    """Status of trap auth fail"""
    cold_start_enabled: bool | None = Field(
        default=None, validation_alias="coldStartEnabled", serialization_alias="coldStartEnabled"
    )
    """Status of trap coldstart"""
    community: CommunityNameType | None = None
    """Trap Community"""
    enabled: bool | None = None
    """Status of Trap usage"""
    link_down_enabled: bool | None = Field(
        default=None, validation_alias="linkDownEnabled", serialization_alias="linkDownEnabled"
    )
    """Status of trap link down"""
    link_up_enabled: bool | None = Field(
        default=None, validation_alias="linkUpEnabled", serialization_alias="linkUpEnabled"
    )
    """Status of trap link up"""


class SnmpV1V2Common(Model):
    """Entity that has common properties for snmp V1 and V2c"""

    address: TrapAddressType
    """Trap Address"""
    read_community: CommunityNameType = Field(validation_alias="readCommunity", serialization_alias="readCommunity")
    """Read Community string"""
    write_community: CommunityNameType = Field(validation_alias="writeCommunity", serialization_alias="writeCommunity")
    """Write Community string"""
    trap: Trap | None = None


class SnmpV2(Model):
    """V2c snmp support"""

    enabled: bool
    """Status of V2c snmp support"""


class User(Model):
    """SNMPv3 user collection"""

    access: AccessTypeEnum | None = None
    """Access rights for the user"""
    security_level: SecurityLevelTypeEnum = Field(validation_alias="securityLevel", serialization_alias="securityLevel")
    """Security level"""
    user_authentication: UserAuthenticationTypeEnum = Field(
        validation_alias="userAuthentication", serialization_alias="userAuthentication"
    )
    """User authentication"""
    user_encryption: UserEncryptionTypeEnum | None = Field(
        default=None, validation_alias="userEncryption", serialization_alias="userEncryption"
    )
    """User encryption"""
    username: UserNameType
    """User name"""


class SnmpV3(Model):
    """V3 snmp support"""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"supported_encryption"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"supported_encryption"})
    enabled: bool
    """Status of V3 snmp support"""
    supported_encryption: SupportedEncryptionTypeArray = Field(
        default_factory=not_sent, validation_alias="supportedEncryption", serialization_alias="supportedEncryption"
    )
    """AES-128 or AES-256 encryption"""
    user_encryption: UserEncryptionTypeEnum | None = Field(
        default=None, validation_alias="userEncryption", serialization_alias="userEncryption"
    )
    """Encryption algorithm for the SNMPv3 "initial" user"""
    user_passwd_set: bool = Field(validation_alias="userPasswdSet", serialization_alias="userPasswdSet")
    """Initial password-set status for the SNMPv3 "initial" user"""
    users: list[User] | None = None


class Snmp(Model):
    """The whole API tree."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"ntcip_supported"})
    dscp: DscpType
    """The DSCP value used for QoS"""
    enabled: bool
    """Status of snmpd service"""
    engine_boots: EngineBootsType = Field(validation_alias="engineBoots", serialization_alias="engineBoots")
    """Number of times snmpd has been started"""
    transport_protocol: TransportProtocolEnum = Field(
        validation_alias="transportProtocol", serialization_alias="transportProtocol"
    )
    """Transport Protocol string"""
    ntcip_supported: bool | None = None
    """Whether NTCIP is supported by the device."""
    ntcip: Ntcip | None = None
    snmp_v1: SnmpV1 | None = Field(default=None, validation_alias="snmpV1", serialization_alias="snmpV1")
    snmp_v1_v2_common: SnmpV1V2Common | None = Field(
        default=None, validation_alias="snmpV1V2Common", serialization_alias="snmpV1V2Common"
    )
    snmp_v2: SnmpV2 | None = Field(default=None, validation_alias="snmpV2", serialization_alias="snmpV2")
    snmp_v3: SnmpV3 | None = Field(default=None, validation_alias="snmpV3", serialization_alias="snmpV3")


class UpdateTrapRequest(Model):
    """Arguments of ``update_trap``."""

    auth_fail_enabled: bool | None = Field(
        default=None, validation_alias="authFailEnabled", serialization_alias="authFailEnabled"
    )
    """Status of trap auth fail"""
    cold_start_enabled: bool | None = Field(
        default=None, validation_alias="coldStartEnabled", serialization_alias="coldStartEnabled"
    )
    """Status of trap coldstart"""
    community: CommunityNameType | None = None
    """Trap Community"""
    enabled: bool | None = None
    """Status of Trap usage"""
    link_up_enabled: bool | None = Field(
        default=None, validation_alias="linkUpEnabled", serialization_alias="linkUpEnabled"
    )
    """Status of trap link up"""
    link_down_enabled: bool | None = Field(
        default=None, validation_alias="linkDownEnabled", serialization_alias="linkDownEnabled"
    )
    """Status of trap link down"""

    @classmethod
    def from_current(cls, trap: Trap) -> UpdateTrapRequest:
        """A request that rewrites ``trap`` unchanged: copy it, edit fields, send it back."""
        data = trap.request_data()
        return cls.from_response_data(data)


class UpdateSnmpV1V2CommonRequest(Model):
    """Arguments of ``update_snmp_v1_v2_common``."""

    read_community: CommunityNameType | None = Field(
        default=None, validation_alias="readCommunity", serialization_alias="readCommunity"
    )
    """Read Community string"""
    write_community: CommunityNameType | None = Field(
        default=None, validation_alias="writeCommunity", serialization_alias="writeCommunity"
    )
    """Write Community string"""
    address: TrapAddressType | None = None
    """Trap Address"""
    trap: UpdateTrapRequest | None = None

    @classmethod
    def from_current(cls, common: SnmpV1V2Common) -> UpdateSnmpV1V2CommonRequest:
        """A request that rewrites ``common`` unchanged: copy it, edit fields, send it back."""
        data = common.request_data()
        return cls.from_response_data(data)


class UpdateSnmpV1Request(Model):
    """Arguments of ``update_snmp_v1``."""

    enabled: bool | None = None
    """Status of V1 snmp support"""

    @classmethod
    def from_current(cls, v1: SnmpV1) -> UpdateSnmpV1Request:
        """A request that rewrites ``v1`` unchanged: copy it, edit fields, send it back."""
        data = v1.request_data()
        return cls.from_response_data(data)


class UpdateSnmpV2Request(Model):
    """Arguments of ``update_snmp_v2``."""

    enabled: bool | None = None
    """Status of V2c snmp support"""

    @classmethod
    def from_current(cls, v2: SnmpV2) -> UpdateSnmpV2Request:
        """A request that rewrites ``v2`` unchanged: copy it, edit fields, send it back."""
        data = v2.request_data()
        return cls.from_response_data(data)


class UpdateSnmpV3Request(Model):
    """Arguments of ``update_snmp_v3``."""

    enabled: bool | None = None
    """Status of V3 snmp support"""
    user_passwd: UserPasswdType | None = Field(
        default=None, validation_alias="userPasswd", serialization_alias="userPasswd"
    )
    """Initial password for the SNMPv3 "initial" user"""
    user_passwd_set: bool | None = Field(
        default=None, validation_alias="userPasswdSet", serialization_alias="userPasswdSet"
    )
    """Initial password-set status for the SNMPv3 "initial" user"""
    user_encryption: UserEncryptionTypeEnum | None = Field(
        default=None, validation_alias="userEncryption", serialization_alias="userEncryption"
    )
    """Encryption algorithm for the SNMPv3 "initial" user"""


class UpdateNtcipRequest(Model):
    """Arguments of ``update_ntcip``."""

    enabled: bool | None = None
    """Status of NTCIP support"""

    @classmethod
    def from_current(cls, ntcip: Ntcip) -> UpdateNtcipRequest:
        """A request that rewrites ``ntcip`` unchanged: copy it, edit fields, send it back."""
        data = ntcip.request_data()
        return cls.from_response_data(data)


class UpdateAllRequest(Model):
    """Arguments of ``update_all``."""

    enabled: bool | None = None
    """Status of snmpd service"""
    engine_boots: EngineBootsType | None = Field(
        default=None, validation_alias="engineBoots", serialization_alias="engineBoots"
    )
    """Number of times snmpd has been started"""
    transport_protocol: TransportProtocolEnum | None = Field(
        default=None, validation_alias="transportProtocol", serialization_alias="transportProtocol"
    )
    """Transport Protocol string"""
    snmp_v1_v2_common: UpdateSnmpV1V2CommonRequest | None = Field(
        default=None, validation_alias="snmpV1V2Common", serialization_alias="snmpV1V2Common"
    )
    snmp_v1: UpdateSnmpV1Request | None = Field(default=None, validation_alias="snmpV1", serialization_alias="snmpV1")
    snmp_v2: UpdateSnmpV2Request | None = Field(default=None, validation_alias="snmpV2", serialization_alias="snmpV2")
    snmp_v3: UpdateSnmpV3Request | None = Field(default=None, validation_alias="snmpV3", serialization_alias="snmpV3")
    ntcip: UpdateNtcipRequest | None = None


class UpdateUserRequest(Model):
    """Arguments of ``update_user``."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"encrypt_passphrase"})
    username: UserNameType
    user_authentication: UserAuthenticationTypeEnum | None = Field(
        default=None, validation_alias="userAuthentication", serialization_alias="userAuthentication"
    )
    """User authentication"""
    auth_passphrase: UserPasswdType | None = Field(
        default=None, validation_alias="authPassphrase", serialization_alias="authPassphrase"
    )
    """Authentication passphrase"""
    user_encryption: UserEncryptionTypeEnum | None = Field(
        default=None, validation_alias="userEncryption", serialization_alias="userEncryption"
    )
    """User encryption"""
    encrypt_passphrase: UserPasswdType | None = Field(
        default=None, validation_alias="encryptPassphrase", serialization_alias="encryptPassphrase"
    )
    """Encryption passphrase"""
    security_level: SecurityLevelTypeEnum | None = Field(
        default=None, validation_alias="securityLevel", serialization_alias="securityLevel"
    )
    """Security level"""
    access: AccessTypeEnum | None = None
    """Access rights for the user"""


class AddUserRequest(Model):
    """Arguments of ``add_user``."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"encrypt_passphrase"})
    username: UserNameType
    """User name"""
    user_authentication: UserAuthenticationTypeEnum = Field(
        validation_alias="userAuthentication", serialization_alias="userAuthentication"
    )
    """User authentication"""
    auth_passphrase: UserPasswdType = Field(validation_alias="authPassphrase", serialization_alias="authPassphrase")
    """Authentication passphrase"""
    security_level: SecurityLevelTypeEnum = Field(validation_alias="securityLevel", serialization_alias="securityLevel")
    """Security level"""
    user_encryption: UserEncryptionTypeEnum | None = Field(
        default=None, validation_alias="userEncryption", serialization_alias="userEncryption"
    )
    """User encryption"""
    encrypt_passphrase: UserPasswdType | None = Field(
        default=None, validation_alias="encryptPassphrase", serialization_alias="encryptPassphrase"
    )
    """Encryption passphrase"""
    access: AccessTypeEnum | None = None
    """Access rights for the user"""


class SetDscpRequest(Model):
    dscp: DscpType
    """The DSCP value used for QoS"""


class SetEnabledRequest(Model):
    enabled: bool
    """Status of snmpd service"""


class SetEngineBootsRequest(Model):
    engine_boots: EngineBootsType = Field(validation_alias="engineBoots", serialization_alias="engineBoots")
    """Number of times snmpd has been started"""


class SetTransportProtocolRequest(Model):
    transport_protocol: TransportProtocolEnum = Field(
        validation_alias="transportProtocol", serialization_alias="transportProtocol"
    )
    """Transport Protocol string"""


class SetNtcipEnabledRequest(Model):
    enabled: bool
    """Status of NTCIP support"""


class SetSnmpV1EnabledRequest(Model):
    enabled: bool
    """Status of V1 snmp support"""


class SetSnmpV1V2CommonAddressRequest(Model):
    address: TrapAddressType
    """Trap Address"""


class SetSnmpV1V2CommonReadCommunityRequest(Model):
    read_community: CommunityNameType = Field(validation_alias="readCommunity", serialization_alias="readCommunity")
    """Read Community string"""


class SetSnmpV1V2CommonWriteCommunityRequest(Model):
    write_community: CommunityNameType = Field(validation_alias="writeCommunity", serialization_alias="writeCommunity")
    """Write Community string"""


class SetTrapAuthFailEnabledRequest(Model):
    auth_fail_enabled: bool = Field(validation_alias="authFailEnabled", serialization_alias="authFailEnabled")
    """Status of trap auth fail"""


class SetTrapColdStartEnabledRequest(Model):
    cold_start_enabled: bool = Field(validation_alias="coldStartEnabled", serialization_alias="coldStartEnabled")
    """Status of trap coldstart"""


class SetTrapCommunityRequest(Model):
    community: CommunityNameType
    """Trap Community"""


class SetTrapEnabledRequest(Model):
    enabled: bool
    """Status of Trap usage"""


class SetTrapLinkDownEnabledRequest(Model):
    link_down_enabled: bool = Field(validation_alias="linkDownEnabled", serialization_alias="linkDownEnabled")
    """Status of trap link down"""


class SetTrapLinkUpEnabledRequest(Model):
    link_up_enabled: bool = Field(validation_alias="linkUpEnabled", serialization_alias="linkUpEnabled")
    """Status of trap link up"""


class SetSnmpV2EnabledRequest(Model):
    enabled: bool
    """Status of V2c snmp support"""


class SetSnmpV3EnabledRequest(Model):
    enabled: bool
    """Status of V3 snmp support"""


class SetSnmpV3UserEncryptionRequest(Model):
    user_encryption: UserEncryptionTypeEnum = Field(
        validation_alias="userEncryption", serialization_alias="userEncryption"
    )
    """Encryption algorithm for the SNMPv3 "initial" user"""


class SetSnmpV3UserPasswdRequest(Model):
    user_passwd: UserPasswdType = Field(validation_alias="userPasswd", serialization_alias="userPasswd")
    """Initial password for the SNMPv3 "initial" user"""


class SetSnmpV3UserPasswdSetRequest(Model):
    user_passwd_set: bool = Field(validation_alias="userPasswdSet", serialization_alias="userPasswdSet")
    """Initial password-set status for the SNMPv3 "initial" user"""


class UserUsernameRequest(Model):
    username: UserNameType


class SetUserAccessRequest(Model):
    username: UserNameType
    access: AccessTypeEnum
    """Access rights for the user"""


class SetUserAuthPassphraseRequest(Model):
    username: UserNameType
    auth_passphrase: UserPasswdType = Field(validation_alias="authPassphrase", serialization_alias="authPassphrase")
    """Authentication passphrase"""


class SetUserEncryptPassphraseRequest(Model):
    username: UserNameType
    encrypt_passphrase: UserPasswdType = Field(
        validation_alias="encryptPassphrase", serialization_alias="encryptPassphrase"
    )
    """Encryption passphrase"""


class SetUserSecurityLevelRequest(Model):
    username: UserNameType
    security_level: SecurityLevelTypeEnum = Field(validation_alias="securityLevel", serialization_alias="securityLevel")
    """Security level"""


class SetUserAuthenticationRequest(Model):
    username: UserNameType
    user_authentication: UserAuthenticationTypeEnum = Field(
        validation_alias="userAuthentication", serialization_alias="userAuthentication"
    )
    """User authentication"""


class SetUserEncryptionRequest(Model):
    username: UserNameType
    user_encryption: UserEncryptionTypeEnum = Field(
        validation_alias="userEncryption", serialization_alias="userEncryption"
    )
    """User encryption"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/snmp/v1"

INFO = ApiInfo(
    id="snmp-config",
    name="SNMP Configuration API",
    family=Family.DCA,
    discovery=(DcaDiscovery("snmp", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/snmp-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Snmp, access="admin", effect="read")
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_dscp = Operation(
        INFO, "get_dscp", DcaBinding("GET", f"{ROOT}/dscp"), result=DscpType, access="admin", effect="read"
    )
    set_dscp = Operation(
        INFO,
        "set_dscp",
        DcaBinding("PATCH", f"{ROOT}/dscp", body="value", body_field="dscp"),
        params=SetDscpRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_engine_boots = Operation(
        INFO,
        "get_engine_boots",
        DcaBinding("GET", f"{ROOT}/engineBoots"),
        result=EngineBootsType,
        access="admin",
        effect="read",
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
    set_engine_boots = Operation(
        INFO,
        "set_engine_boots",
        DcaBinding("PATCH", f"{ROOT}/engineBoots", body="value", body_field="engineBoots"),
        params=SetEngineBootsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_transport_protocol = Operation(
        INFO,
        "set_transport_protocol",
        DcaBinding("PATCH", f"{ROOT}/transportProtocol", body="value", body_field="transportProtocol"),
        params=SetTransportProtocolRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_ntcip = Operation(
        INFO, "get_ntcip", DcaBinding("GET", f"{ROOT}/ntcip"), result=Ntcip, access="admin", effect="read"
    )
    update_ntcip = Operation(
        INFO,
        "update_ntcip",
        DcaBinding("PATCH", f"{ROOT}/ntcip", body="object"),
        params=UpdateNtcipRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_ntcip_enabled = Operation(
        INFO,
        "set_ntcip_enabled",
        DcaBinding("PATCH", f"{ROOT}/ntcip/enabled", body="value", body_field="enabled"),
        params=SetNtcipEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_snmp_v1 = Operation(
        INFO, "get_snmp_v1", DcaBinding("GET", f"{ROOT}/snmpV1"), result=SnmpV1, access="admin", effect="read"
    )
    update_snmp_v1 = Operation(
        INFO,
        "update_snmp_v1",
        DcaBinding("PATCH", f"{ROOT}/snmpV1", body="object"),
        params=UpdateSnmpV1Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v1_enabled = Operation(
        INFO,
        "set_snmp_v1_enabled",
        DcaBinding("PATCH", f"{ROOT}/snmpV1/enabled", body="value", body_field="enabled"),
        params=SetSnmpV1EnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_snmp_v1_v2_common = Operation(
        INFO,
        "get_snmp_v1_v2_common",
        DcaBinding("GET", f"{ROOT}/snmpV1V2Common"),
        result=SnmpV1V2Common,
        access="admin",
        effect="read",
    )
    update_snmp_v1_v2_common = Operation(
        INFO,
        "update_snmp_v1_v2_common",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common", body="object"),
        params=UpdateSnmpV1V2CommonRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v1_v2_common_address = Operation(
        INFO,
        "set_snmp_v1_v2_common_address",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/address", body="value", body_field="address"),
        params=SetSnmpV1V2CommonAddressRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v1_v2_common_read_community = Operation(
        INFO,
        "set_snmp_v1_v2_common_read_community",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/readCommunity", body="value", body_field="readCommunity"),
        params=SetSnmpV1V2CommonReadCommunityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v1_v2_common_write_community = Operation(
        INFO,
        "set_snmp_v1_v2_common_write_community",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/writeCommunity", body="value", body_field="writeCommunity"),
        params=SetSnmpV1V2CommonWriteCommunityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_trap = Operation(
        INFO, "get_trap", DcaBinding("GET", f"{ROOT}/snmpV1V2Common/trap"), result=Trap, access="admin", effect="read"
    )
    update_trap = Operation(
        INFO,
        "update_trap",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/trap", body="object"),
        params=UpdateTrapRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_trap_auth_fail_enabled = Operation(
        INFO,
        "set_trap_auth_fail_enabled",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/trap/authFailEnabled", body="value", body_field="authFailEnabled"),
        params=SetTrapAuthFailEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_trap_cold_start_enabled = Operation(
        INFO,
        "set_trap_cold_start_enabled",
        DcaBinding(
            "PATCH", f"{ROOT}/snmpV1V2Common/trap/coldStartEnabled", body="value", body_field="coldStartEnabled"
        ),
        params=SetTrapColdStartEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_trap_community = Operation(
        INFO,
        "set_trap_community",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/trap/community", body="value", body_field="community"),
        params=SetTrapCommunityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_trap_enabled = Operation(
        INFO,
        "set_trap_enabled",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/trap/enabled", body="value", body_field="enabled"),
        params=SetTrapEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_trap_link_down_enabled = Operation(
        INFO,
        "set_trap_link_down_enabled",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/trap/linkDownEnabled", body="value", body_field="linkDownEnabled"),
        params=SetTrapLinkDownEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_trap_link_up_enabled = Operation(
        INFO,
        "set_trap_link_up_enabled",
        DcaBinding("PATCH", f"{ROOT}/snmpV1V2Common/trap/linkUpEnabled", body="value", body_field="linkUpEnabled"),
        params=SetTrapLinkUpEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_snmp_v2 = Operation(
        INFO, "get_snmp_v2", DcaBinding("GET", f"{ROOT}/snmpV2"), result=SnmpV2, access="admin", effect="read"
    )
    update_snmp_v2 = Operation(
        INFO,
        "update_snmp_v2",
        DcaBinding("PATCH", f"{ROOT}/snmpV2", body="object"),
        params=UpdateSnmpV2Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v2_enabled = Operation(
        INFO,
        "set_snmp_v2_enabled",
        DcaBinding("PATCH", f"{ROOT}/snmpV2/enabled", body="value", body_field="enabled"),
        params=SetSnmpV2EnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_snmp_v3 = Operation(
        INFO, "get_snmp_v3", DcaBinding("GET", f"{ROOT}/snmpV3"), result=SnmpV3, access="admin", effect="read"
    )
    update_snmp_v3 = Operation(
        INFO,
        "update_snmp_v3",
        DcaBinding("PATCH", f"{ROOT}/snmpV3", body="object"),
        params=UpdateSnmpV3Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v3_enabled = Operation(
        INFO,
        "set_snmp_v3_enabled",
        DcaBinding("PATCH", f"{ROOT}/snmpV3/enabled", body="value", body_field="enabled"),
        params=SetSnmpV3EnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v3_user_encryption = Operation(
        INFO,
        "set_snmp_v3_user_encryption",
        DcaBinding("PATCH", f"{ROOT}/snmpV3/userEncryption", body="value", body_field="userEncryption"),
        params=SetSnmpV3UserEncryptionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v3_user_passwd = Operation(
        INFO,
        "set_snmp_v3_user_passwd",
        DcaBinding("PATCH", f"{ROOT}/snmpV3/userPasswd", body="value", body_field="userPasswd", sensitive=True),
        params=SetSnmpV3UserPasswdRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_snmp_v3_user_passwd_set = Operation(
        INFO,
        "set_snmp_v3_user_passwd_set",
        DcaBinding("PATCH", f"{ROOT}/snmpV3/userPasswdSet", body="value", body_field="userPasswdSet", sensitive=True),
        params=SetSnmpV3UserPasswdSetRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_users = Operation(
        INFO, "list_users", DcaBinding("GET", f"{ROOT}/snmpV3/users"), result=list[User], access="admin", effect="read"
    )
    get_user = Operation(
        INFO,
        "get_user",
        DcaBinding("GET", f"{ROOT}/snmpV3/users/{{username}}"),
        params=UserUsernameRequest,
        result=User,
        access="admin",
        effect="read",
    )
    update_user = Operation(
        INFO,
        "update_user",
        DcaBinding("PATCH", f"{ROOT}/snmpV3/users/{{username}}", body="object"),
        params=UpdateUserRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    add_user = Operation(
        INFO,
        "add_user",
        DcaBinding("POST", f"{ROOT}/snmpV3/users", body="object"),
        params=AddUserRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_user = Operation(
        INFO,
        "remove_user",
        DcaBinding("DELETE", f"{ROOT}/snmpV3/users/{{username}}"),
        params=UserUsernameRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_user_access = Operation(
        INFO,
        "set_user_access",
        DcaBinding("PATCH", f"{ROOT}/snmpV3/users/{{username}}/access", body="value", body_field="access"),
        params=SetUserAccessRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_user_auth_passphrase = Operation(
        INFO,
        "set_user_auth_passphrase",
        DcaBinding(
            "PATCH",
            f"{ROOT}/snmpV3/users/{{username}}/authPassphrase",
            body="value",
            body_field="authPassphrase",
            sensitive=True,
        ),
        params=SetUserAuthPassphraseRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_user_encrypt_passphrase = Operation(
        INFO,
        "set_user_encrypt_passphrase",
        DcaBinding(
            "PATCH",
            f"{ROOT}/snmpV3/users/{{username}}/encryptPassphrase",
            body="value",
            body_field="encryptPassphrase",
            sensitive=True,
        ),
        params=SetUserEncryptPassphraseRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_user_security_level = Operation(
        INFO,
        "set_user_security_level",
        DcaBinding(
            "PATCH", f"{ROOT}/snmpV3/users/{{username}}/securityLevel", body="value", body_field="securityLevel"
        ),
        params=SetUserSecurityLevelRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_user_authentication = Operation(
        INFO,
        "set_user_authentication",
        DcaBinding(
            "PATCH",
            f"{ROOT}/snmpV3/users/{{username}}/userAuthentication",
            body="value",
            body_field="userAuthentication",
        ),
        params=SetUserAuthenticationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_user_encryption = Operation(
        INFO,
        "set_user_encryption",
        DcaBinding(
            "PATCH", f"{ROOT}/snmpV3/users/{{username}}/userEncryption", body="value", body_field="userEncryption"
        ),
        params=SetUserEncryptionRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SnmpApi(SyncApi):
    """SNMP Configuration API (``snmp-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Snmp:
        """All SNMP settings. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    @overload
    def update_all(self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_all(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        engine_boots: EngineBootsType | MISSING = MISSING,
        transport_protocol: TransportProtocolEnum | MISSING = MISSING,
        snmp_v1_v2_common: UpdateSnmpV1V2CommonRequest | MISSING = MISSING,
        snmp_v1: UpdateSnmpV1Request | MISSING = MISSING,
        snmp_v2: UpdateSnmpV2Request | MISSING = MISSING,
        snmp_v3: UpdateSnmpV3Request | MISSING = MISSING,
        ntcip: UpdateNtcipRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the general SNMP settings and any nested entity in one call.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_all, request, kwargs, request_options)

    def get_dscp(self, *, request_options: RequestOptions | None = None) -> DscpType:
        """Get the DSCP value used for SNMP traffic. Access: admin."""
        return self._run(OPS.get_dscp, None, {}, request_options)

    def set_dscp(self, *, dscp: DscpType, request_options: RequestOptions | None = None) -> None:
        """Set the dscp of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_dscp, None, {"dscp": dscp}, request_options)

    def get_engine_boots(self, *, request_options: RequestOptions | None = None) -> EngineBootsType:
        """Get the number of times snmpd has been started. Access: admin."""
        return self._run(OPS.get_engine_boots, None, {}, request_options)

    def set_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    def set_engine_boots(self, *, engine_boots: EngineBootsType, request_options: RequestOptions | None = None) -> None:
        """Set the engine boots of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_engine_boots, None, {"engine_boots": engine_boots}, request_options)

    def set_transport_protocol(
        self, *, transport_protocol: TransportProtocolEnum, request_options: RequestOptions | None = None
    ) -> None:
        """Set the transport protocol of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_transport_protocol, None, {"transport_protocol": transport_protocol}, request_options)

    def get_ntcip(self, *, request_options: RequestOptions | None = None) -> Ntcip:
        """Get the ntcip settings. Access: admin."""
        return self._run(OPS.get_ntcip, None, {}, request_options)

    def update_ntcip(self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None) -> None:
        """Update the ntcip settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_ntcip, None, {"enabled": enabled}, request_options)

    def set_ntcip_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the ntcip. Changes only the fields given. Access: admin."""
        self._run(OPS.set_ntcip_enabled, None, {"enabled": enabled}, request_options)

    def get_snmp_v1(self, *, request_options: RequestOptions | None = None) -> SnmpV1:
        """Get the snmp v1 settings. Access: admin."""
        return self._run(OPS.get_snmp_v1, None, {}, request_options)

    def update_snmp_v1(
        self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Update the snmp v1 settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_snmp_v1, None, {"enabled": enabled}, request_options)

    def set_snmp_v1_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the snmp v1. Changes only the fields given. Access: admin."""
        self._run(OPS.set_snmp_v1_enabled, None, {"enabled": enabled}, request_options)

    def get_snmp_v1_v2_common(self, *, request_options: RequestOptions | None = None) -> SnmpV1V2Common:
        """Get the snmp v1 v2 common settings. Access: admin."""
        return self._run(OPS.get_snmp_v1_v2_common, None, {}, request_options)

    @overload
    def update_snmp_v1_v2_common(
        self, request: UpdateSnmpV1V2CommonRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_snmp_v1_v2_common(
        self,
        /,
        *,
        read_community: CommunityNameType | MISSING = MISSING,
        write_community: CommunityNameType | MISSING = MISSING,
        address: TrapAddressType | MISSING = MISSING,
        trap: UpdateTrapRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_snmp_v1_v2_common(
        self,
        request: UpdateSnmpV1V2CommonRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the snmp v1 v2 common settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_snmp_v1_v2_common, request, kwargs, request_options)

    def set_snmp_v1_v2_common_address(
        self, *, address: TrapAddressType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the address of the snmp v1 v2 common. Changes only the fields given. Access: admin."""
        self._run(OPS.set_snmp_v1_v2_common_address, None, {"address": address}, request_options)

    def set_snmp_v1_v2_common_read_community(
        self, *, read_community: CommunityNameType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the read community of the snmp v1 v2 common.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_snmp_v1_v2_common_read_community, None, {"read_community": read_community}, request_options)

    def set_snmp_v1_v2_common_write_community(
        self, *, write_community: CommunityNameType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the write community of the snmp v1 v2 common.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_snmp_v1_v2_common_write_community, None, {"write_community": write_community}, request_options
        )

    def get_trap(self, *, request_options: RequestOptions | None = None) -> Trap:
        """Get the trap settings. Access: admin."""
        return self._run(OPS.get_trap, None, {}, request_options)

    @overload
    def update_trap(self, request: UpdateTrapRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_trap(
        self,
        /,
        *,
        auth_fail_enabled: bool | MISSING = MISSING,
        cold_start_enabled: bool | MISSING = MISSING,
        community: CommunityNameType | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        link_up_enabled: bool | MISSING = MISSING,
        link_down_enabled: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_trap(
        self,
        request: UpdateTrapRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the trap settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_trap, request, kwargs, request_options)

    def set_trap_auth_fail_enabled(
        self, *, auth_fail_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the auth fail enabled of the trap. Changes only the fields given. Access: admin."""
        self._run(OPS.set_trap_auth_fail_enabled, None, {"auth_fail_enabled": auth_fail_enabled}, request_options)

    def set_trap_cold_start_enabled(
        self, *, cold_start_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the cold start enabled of the trap. Changes only the fields given. Access: admin."""
        self._run(OPS.set_trap_cold_start_enabled, None, {"cold_start_enabled": cold_start_enabled}, request_options)

    def set_trap_community(
        self, *, community: CommunityNameType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the community of the trap. Changes only the fields given. Access: admin."""
        self._run(OPS.set_trap_community, None, {"community": community}, request_options)

    def set_trap_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the trap. Changes only the fields given. Access: admin."""
        self._run(OPS.set_trap_enabled, None, {"enabled": enabled}, request_options)

    def set_trap_link_down_enabled(
        self, *, link_down_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the link down enabled of the trap. Changes only the fields given. Access: admin."""
        self._run(OPS.set_trap_link_down_enabled, None, {"link_down_enabled": link_down_enabled}, request_options)

    def set_trap_link_up_enabled(self, *, link_up_enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the link up enabled of the trap. Changes only the fields given. Access: admin."""
        self._run(OPS.set_trap_link_up_enabled, None, {"link_up_enabled": link_up_enabled}, request_options)

    def get_snmp_v2(self, *, request_options: RequestOptions | None = None) -> SnmpV2:
        """Get the snmp v2 settings. Access: admin."""
        return self._run(OPS.get_snmp_v2, None, {}, request_options)

    def update_snmp_v2(
        self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Update the snmp v2 settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_snmp_v2, None, {"enabled": enabled}, request_options)

    def set_snmp_v2_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the snmp v2. Changes only the fields given. Access: admin."""
        self._run(OPS.set_snmp_v2_enabled, None, {"enabled": enabled}, request_options)

    def get_snmp_v3(self, *, request_options: RequestOptions | None = None) -> SnmpV3:
        """Get the snmp v3 settings. Access: admin."""
        return self._run(OPS.get_snmp_v3, None, {}, request_options)

    def update_snmp_v3(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        user_passwd: UserPasswdType | MISSING = MISSING,
        user_passwd_set: bool | MISSING = MISSING,
        user_encryption: UserEncryptionTypeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the snmp v3 settings. Changes only the fields given. Access: admin."""
        self._run(
            OPS.update_snmp_v3,
            None,
            {
                "enabled": enabled,
                "user_passwd": user_passwd,
                "user_passwd_set": user_passwd_set,
                "user_encryption": user_encryption,
            },
            request_options,
        )

    def set_snmp_v3_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the snmp v3. Changes only the fields given. Access: admin."""
        self._run(OPS.set_snmp_v3_enabled, None, {"enabled": enabled}, request_options)

    def set_snmp_v3_user_encryption(
        self, *, user_encryption: UserEncryptionTypeEnum, request_options: RequestOptions | None = None
    ) -> None:
        """Set the user encryption of the snmp v3. Changes only the fields given. Access: admin."""
        self._run(OPS.set_snmp_v3_user_encryption, None, {"user_encryption": user_encryption}, request_options)

    def set_snmp_v3_user_passwd(
        self, *, user_passwd: UserPasswdType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the user passwd of the snmp v3. Changes only the fields given. Access: admin."""
        self._run(OPS.set_snmp_v3_user_passwd, None, {"user_passwd": user_passwd}, request_options)

    def set_snmp_v3_user_passwd_set(
        self, *, user_passwd_set: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the user passwd set of the snmp v3. Changes only the fields given. Access: admin."""
        self._run(OPS.set_snmp_v3_user_passwd_set, None, {"user_passwd_set": user_passwd_set}, request_options)

    def list_users(self, *, request_options: RequestOptions | None = None) -> list[User]:
        """List the users. Access: admin."""
        return self._run(OPS.list_users, None, {}, request_options)

    def get_user(self, username: UserNameType, *, request_options: RequestOptions | None = None) -> User:
        """Get one user. Access: admin."""
        return self._run(OPS.get_user, None, {"username": username}, request_options)

    @overload
    def update_user(self, request: UpdateUserRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_user(
        self,
        /,
        *,
        username: UserNameType,
        user_authentication: UserAuthenticationTypeEnum | MISSING = MISSING,
        auth_passphrase: UserPasswdType | MISSING = MISSING,
        user_encryption: UserEncryptionTypeEnum | MISSING = MISSING,
        encrypt_passphrase: UserPasswdType | None | MISSING = MISSING,
        security_level: SecurityLevelTypeEnum | MISSING = MISSING,
        access: AccessTypeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_user(
        self,
        request: UpdateUserRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a user. Changes only the fields given. Access: admin."""
        self._run(OPS.update_user, request, kwargs, request_options)

    @overload
    def add_user(self, request: AddUserRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def add_user(
        self,
        /,
        *,
        username: UserNameType,
        user_authentication: UserAuthenticationTypeEnum,
        auth_passphrase: UserPasswdType,
        security_level: SecurityLevelTypeEnum,
        user_encryption: UserEncryptionTypeEnum | MISSING = MISSING,
        encrypt_passphrase: UserPasswdType | None | MISSING = MISSING,
        access: AccessTypeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_user(
        self, request: AddUserRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Add a user. Access: admin."""
        self._run(OPS.add_user, request, kwargs, request_options)

    def remove_user(self, username: UserNameType, *, request_options: RequestOptions | None = None) -> None:
        """Remove a user. Access: admin."""
        self._run(OPS.remove_user, None, {"username": username}, request_options)

    def set_user_access(
        self, username: UserNameType, *, access: AccessTypeEnum, request_options: RequestOptions | None = None
    ) -> None:
        """Set the access of a user. Changes only the fields given. Access: admin."""
        self._run(OPS.set_user_access, None, {"username": username, "access": access}, request_options)

    def set_user_auth_passphrase(
        self, username: UserNameType, *, auth_passphrase: UserPasswdType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the auth passphrase of a user. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_user_auth_passphrase,
            None,
            {"username": username, "auth_passphrase": auth_passphrase},
            request_options,
        )

    def set_user_encrypt_passphrase(
        self,
        username: UserNameType,
        *,
        encrypt_passphrase: UserPasswdType,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the encrypt passphrase of a user. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_user_encrypt_passphrase,
            None,
            {"username": username, "encrypt_passphrase": encrypt_passphrase},
            request_options,
        )

    def set_user_security_level(
        self,
        username: UserNameType,
        *,
        security_level: SecurityLevelTypeEnum,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the security level of a user. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_user_security_level, None, {"username": username, "security_level": security_level}, request_options
        )

    def set_user_authentication(
        self,
        username: UserNameType,
        *,
        user_authentication: UserAuthenticationTypeEnum,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the authentication algorithm of a user. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_user_authentication,
            None,
            {"username": username, "user_authentication": user_authentication},
            request_options,
        )

    def set_user_encryption(
        self,
        username: UserNameType,
        *,
        user_encryption: UserEncryptionTypeEnum,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the encryption algorithm of a user. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_user_encryption, None, {"username": username, "user_encryption": user_encryption}, request_options
        )


class AsyncSnmpApi(AsyncApi):
    """SNMP Configuration API (``snmp-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Snmp:
        """All SNMP settings. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    @overload
    async def update_all(
        self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_all(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        engine_boots: EngineBootsType | MISSING = MISSING,
        transport_protocol: TransportProtocolEnum | MISSING = MISSING,
        snmp_v1_v2_common: UpdateSnmpV1V2CommonRequest | MISSING = MISSING,
        snmp_v1: UpdateSnmpV1Request | MISSING = MISSING,
        snmp_v2: UpdateSnmpV2Request | MISSING = MISSING,
        snmp_v3: UpdateSnmpV3Request | MISSING = MISSING,
        ntcip: UpdateNtcipRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the general SNMP settings and any nested entity in one call.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_all, request, kwargs, request_options)

    async def get_dscp(self, *, request_options: RequestOptions | None = None) -> DscpType:
        """Get the DSCP value used for SNMP traffic. Access: admin."""
        return await self._run(OPS.get_dscp, None, {}, request_options)

    async def set_dscp(self, *, dscp: DscpType, request_options: RequestOptions | None = None) -> None:
        """Set the dscp of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_dscp, None, {"dscp": dscp}, request_options)

    async def get_engine_boots(self, *, request_options: RequestOptions | None = None) -> EngineBootsType:
        """Get the number of times snmpd has been started. Access: admin."""
        return await self._run(OPS.get_engine_boots, None, {}, request_options)

    async def set_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    async def set_engine_boots(
        self, *, engine_boots: EngineBootsType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the engine boots of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_engine_boots, None, {"engine_boots": engine_boots}, request_options)

    async def set_transport_protocol(
        self, *, transport_protocol: TransportProtocolEnum, request_options: RequestOptions | None = None
    ) -> None:
        """Set the transport protocol of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_transport_protocol, None, {"transport_protocol": transport_protocol}, request_options)

    async def get_ntcip(self, *, request_options: RequestOptions | None = None) -> Ntcip:
        """Get the ntcip settings. Access: admin."""
        return await self._run(OPS.get_ntcip, None, {}, request_options)

    async def update_ntcip(
        self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Update the ntcip settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_ntcip, None, {"enabled": enabled}, request_options)

    async def set_ntcip_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the ntcip. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_ntcip_enabled, None, {"enabled": enabled}, request_options)

    async def get_snmp_v1(self, *, request_options: RequestOptions | None = None) -> SnmpV1:
        """Get the snmp v1 settings. Access: admin."""
        return await self._run(OPS.get_snmp_v1, None, {}, request_options)

    async def update_snmp_v1(
        self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Update the snmp v1 settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_snmp_v1, None, {"enabled": enabled}, request_options)

    async def set_snmp_v1_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the snmp v1. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_snmp_v1_enabled, None, {"enabled": enabled}, request_options)

    async def get_snmp_v1_v2_common(self, *, request_options: RequestOptions | None = None) -> SnmpV1V2Common:
        """Get the snmp v1 v2 common settings. Access: admin."""
        return await self._run(OPS.get_snmp_v1_v2_common, None, {}, request_options)

    @overload
    async def update_snmp_v1_v2_common(
        self, request: UpdateSnmpV1V2CommonRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_snmp_v1_v2_common(
        self,
        /,
        *,
        read_community: CommunityNameType | MISSING = MISSING,
        write_community: CommunityNameType | MISSING = MISSING,
        address: TrapAddressType | MISSING = MISSING,
        trap: UpdateTrapRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_snmp_v1_v2_common(
        self,
        request: UpdateSnmpV1V2CommonRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the snmp v1 v2 common settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_snmp_v1_v2_common, request, kwargs, request_options)

    async def set_snmp_v1_v2_common_address(
        self, *, address: TrapAddressType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the address of the snmp v1 v2 common. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_snmp_v1_v2_common_address, None, {"address": address}, request_options)

    async def set_snmp_v1_v2_common_read_community(
        self, *, read_community: CommunityNameType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the read community of the snmp v1 v2 common.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_snmp_v1_v2_common_read_community, None, {"read_community": read_community}, request_options
        )

    async def set_snmp_v1_v2_common_write_community(
        self, *, write_community: CommunityNameType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the write community of the snmp v1 v2 common.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_snmp_v1_v2_common_write_community, None, {"write_community": write_community}, request_options
        )

    async def get_trap(self, *, request_options: RequestOptions | None = None) -> Trap:
        """Get the trap settings. Access: admin."""
        return await self._run(OPS.get_trap, None, {}, request_options)

    @overload
    async def update_trap(
        self, request: UpdateTrapRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_trap(
        self,
        /,
        *,
        auth_fail_enabled: bool | MISSING = MISSING,
        cold_start_enabled: bool | MISSING = MISSING,
        community: CommunityNameType | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        link_up_enabled: bool | MISSING = MISSING,
        link_down_enabled: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_trap(
        self,
        request: UpdateTrapRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the trap settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_trap, request, kwargs, request_options)

    async def set_trap_auth_fail_enabled(
        self, *, auth_fail_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the auth fail enabled of the trap. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_trap_auth_fail_enabled, None, {"auth_fail_enabled": auth_fail_enabled}, request_options)

    async def set_trap_cold_start_enabled(
        self, *, cold_start_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the cold start enabled of the trap. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_trap_cold_start_enabled, None, {"cold_start_enabled": cold_start_enabled}, request_options
        )

    async def set_trap_community(
        self, *, community: CommunityNameType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the community of the trap. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_trap_community, None, {"community": community}, request_options)

    async def set_trap_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the trap. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_trap_enabled, None, {"enabled": enabled}, request_options)

    async def set_trap_link_down_enabled(
        self, *, link_down_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the link down enabled of the trap. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_trap_link_down_enabled, None, {"link_down_enabled": link_down_enabled}, request_options)

    async def set_trap_link_up_enabled(
        self, *, link_up_enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the link up enabled of the trap. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_trap_link_up_enabled, None, {"link_up_enabled": link_up_enabled}, request_options)

    async def get_snmp_v2(self, *, request_options: RequestOptions | None = None) -> SnmpV2:
        """Get the snmp v2 settings. Access: admin."""
        return await self._run(OPS.get_snmp_v2, None, {}, request_options)

    async def update_snmp_v2(
        self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Update the snmp v2 settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_snmp_v2, None, {"enabled": enabled}, request_options)

    async def set_snmp_v2_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the snmp v2. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_snmp_v2_enabled, None, {"enabled": enabled}, request_options)

    async def get_snmp_v3(self, *, request_options: RequestOptions | None = None) -> SnmpV3:
        """Get the snmp v3 settings. Access: admin."""
        return await self._run(OPS.get_snmp_v3, None, {}, request_options)

    async def update_snmp_v3(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        user_passwd: UserPasswdType | MISSING = MISSING,
        user_passwd_set: bool | MISSING = MISSING,
        user_encryption: UserEncryptionTypeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the snmp v3 settings. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.update_snmp_v3,
            None,
            {
                "enabled": enabled,
                "user_passwd": user_passwd,
                "user_passwd_set": user_passwd_set,
                "user_encryption": user_encryption,
            },
            request_options,
        )

    async def set_snmp_v3_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Set the enabled of the snmp v3. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_snmp_v3_enabled, None, {"enabled": enabled}, request_options)

    async def set_snmp_v3_user_encryption(
        self, *, user_encryption: UserEncryptionTypeEnum, request_options: RequestOptions | None = None
    ) -> None:
        """Set the user encryption of the snmp v3. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_snmp_v3_user_encryption, None, {"user_encryption": user_encryption}, request_options)

    async def set_snmp_v3_user_passwd(
        self, *, user_passwd: UserPasswdType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the user passwd of the snmp v3. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_snmp_v3_user_passwd, None, {"user_passwd": user_passwd}, request_options)

    async def set_snmp_v3_user_passwd_set(
        self, *, user_passwd_set: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the user passwd set of the snmp v3. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_snmp_v3_user_passwd_set, None, {"user_passwd_set": user_passwd_set}, request_options)

    async def list_users(self, *, request_options: RequestOptions | None = None) -> list[User]:
        """List the users. Access: admin."""
        return await self._run(OPS.list_users, None, {}, request_options)

    async def get_user(self, username: UserNameType, *, request_options: RequestOptions | None = None) -> User:
        """Get one user. Access: admin."""
        return await self._run(OPS.get_user, None, {"username": username}, request_options)

    @overload
    async def update_user(
        self, request: UpdateUserRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_user(
        self,
        /,
        *,
        username: UserNameType,
        user_authentication: UserAuthenticationTypeEnum | MISSING = MISSING,
        auth_passphrase: UserPasswdType | MISSING = MISSING,
        user_encryption: UserEncryptionTypeEnum | MISSING = MISSING,
        encrypt_passphrase: UserPasswdType | None | MISSING = MISSING,
        security_level: SecurityLevelTypeEnum | MISSING = MISSING,
        access: AccessTypeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_user(
        self,
        request: UpdateUserRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a user. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_user, request, kwargs, request_options)

    @overload
    async def add_user(self, request: AddUserRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def add_user(
        self,
        /,
        *,
        username: UserNameType,
        user_authentication: UserAuthenticationTypeEnum,
        auth_passphrase: UserPasswdType,
        security_level: SecurityLevelTypeEnum,
        user_encryption: UserEncryptionTypeEnum | MISSING = MISSING,
        encrypt_passphrase: UserPasswdType | None | MISSING = MISSING,
        access: AccessTypeEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_user(
        self, request: AddUserRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Add a user. Access: admin."""
        await self._run(OPS.add_user, request, kwargs, request_options)

    async def remove_user(self, username: UserNameType, *, request_options: RequestOptions | None = None) -> None:
        """Remove a user. Access: admin."""
        await self._run(OPS.remove_user, None, {"username": username}, request_options)

    async def set_user_access(
        self, username: UserNameType, *, access: AccessTypeEnum, request_options: RequestOptions | None = None
    ) -> None:
        """Set the access of a user. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_user_access, None, {"username": username, "access": access}, request_options)

    async def set_user_auth_passphrase(
        self, username: UserNameType, *, auth_passphrase: UserPasswdType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the auth passphrase of a user. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_user_auth_passphrase,
            None,
            {"username": username, "auth_passphrase": auth_passphrase},
            request_options,
        )

    async def set_user_encrypt_passphrase(
        self,
        username: UserNameType,
        *,
        encrypt_passphrase: UserPasswdType,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the encrypt passphrase of a user. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_user_encrypt_passphrase,
            None,
            {"username": username, "encrypt_passphrase": encrypt_passphrase},
            request_options,
        )

    async def set_user_security_level(
        self,
        username: UserNameType,
        *,
        security_level: SecurityLevelTypeEnum,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the security level of a user. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_user_security_level, None, {"username": username, "security_level": security_level}, request_options
        )

    async def set_user_authentication(
        self,
        username: UserNameType,
        *,
        user_authentication: UserAuthenticationTypeEnum,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the authentication algorithm of a user. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_user_authentication,
            None,
            {"username": username, "user_authentication": user_authentication},
            request_options,
        )

    async def set_user_encryption(
        self,
        username: UserNameType,
        *,
        user_encryption: UserEncryptionTypeEnum,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the encryption algorithm of a user. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_user_encryption, None, {"username": username, "user_encryption": user_encryption}, request_options
        )
