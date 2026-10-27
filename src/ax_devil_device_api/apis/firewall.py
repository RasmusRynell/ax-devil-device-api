# GENERATED from specs/apis/device-configuration/firewall-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Activate the firewall, manage and test its rules, and configure brute force protection.

Docs: https://developer.axis.com/vapix/device-configuration/firewall-configuration-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, ErrorCode, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

AttemptsLimit = Annotated[int, Field(ge=1, le=65535)]
BlockInterval = Annotated[int, Field(ge=1, le=3600)]
BlockTime = Annotated[int, Field(ge=1, le=3600)]
Policy = Literal["DROP", "ACCEPT"]


class Filter(Model):
    """Firewall filter type"""

    policy: Policy
    """Filter policy"""


class IPRange(Model):
    """IP range type. Both lower and upper bounds are included."""

    end: str
    """IP range end address"""
    start: str
    """IP range start address"""


LimitAmount = Annotated[int, Field(ge=1, le=65535)]
LimitPeriod = Literal["NEWCONNECTIONS", "SECOND", "MINUTE"]
LimitUnit = Literal["NEWCONNECTIONS", "PACKETS"]


class Limit(Model):
    """Firewall limit type to define packet rate filtering. With the NEWCONNECTIONS unit on UDP, packets from the same source and destination count as one tracked connection with a 30 second timeout."""

    amount: LimitAmount
    """Max limit units allowed within the specified period"""
    burst: LimitAmount | None = None
    """If the burst limit is reached, the firewall will filter all packets matching the rate limit strategy for the rate specified by amount and period"""
    period: LimitPeriod
    """Limit rate period"""
    unit: LimitUnit
    """Limit rate strategy indicating how to enforce the limit rate"""


MAC = Annotated[str, Field(pattern="^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$|^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$")]
PortType = Literal["TCP", "UDP", "BOTH"]
Port = Annotated[int, Field(ge=1, le=65535)]


class NetworkPort(Model):
    """Port address type"""

    port_type: PortType = Field(validation_alias="portType", serialization_alias="portType")
    """Port type"""
    port_num: Port = Field(validation_alias="portNum", serialization_alias="portNum")
    """Port number"""


PktType = Literal["UNICAST", "BROADCAST", "MULTICAST"]


class PortRange(Model):
    """Port range"""

    port_type: PortType | None = Field(default=None, validation_alias="portType", serialization_alias="portType")
    """Port type"""
    start: Port
    """Port range start number"""
    end: Port
    """Port range end number"""


PositiveNumValue = Annotated[int, Field(ge=0)]
RuleType = Literal["FILTER", "LIMIT"]


class Rule(Model):
    """Firewall rule entry type. Only one option from layer 2, 3 or 4 is allowed per rule; nullable members can be omitted when setting rules."""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"filter", "ip", "ip_range", "limit", "mac", "pkt_type", "port", "port_range", "tcp_port", "udp_port"}
    )
    filter: Filter | None = None
    """Filter rule"""
    ip: str | None = None
    """IPv4/IPv6 address or network"""
    ip_range: IPRange | None = Field(default=None, validation_alias="ipRange", serialization_alias="ipRange")
    """IPv4/IPv6 address range"""
    limit: Limit | None = None
    """Limit rule"""
    mac: MAC | None = None
    """MAC address"""
    pkt_type: PktType | None = Field(default=None, validation_alias="pktType", serialization_alias="pktType")
    """The link-layer packet type"""
    port: NetworkPort | None = None
    """A generic port"""
    port_range: PortRange | None = Field(default=None, validation_alias="portRange", serialization_alias="portRange")
    """Port address range"""
    rule_type: RuleType = Field(validation_alias="ruleType", serialization_alias="ruleType")
    """Firewall rule entry type"""
    tcp_port: Port | None = Field(default=None, validation_alias="tcpPort", serialization_alias="tcpPort")
    """The TCP port"""
    udp_port: Port | None = Field(default=None, validation_alias="udpPort", serialization_alias="udpPort")
    """The UDP port"""


RuleList = list[Rule]


class BruteForceProtection(Model):
    """Brute force protection"""

    attempts: AttemptsLimit
    """The fail limit for the brute force protection."""
    block_time: BlockTime = Field(validation_alias="blockTime", serialization_alias="blockTime")
    """The time an IP is blocked for the brute force protection."""
    enabled: bool
    """The enabled state of the brute force protection."""
    interval: BlockInterval
    """The interval for the amount of fails for the brute force protection."""


class Rules(Model):
    """Firewall rules. Read-only; change them with set_rules."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"pending_default_policy"})
    __response_required__: ClassVar[frozenset[str]] = frozenset(
        {"active_default_policy", "active_rules", "pending_rules", "test_time_left"}
    )
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {"active_default_policy", "active_rules", "pending_default_policy", "pending_rules", "test_time_left"}
    )
    active_default_policy: Policy = Field(
        default_factory=not_sent, validation_alias="activeDefaultPolicy", serialization_alias="activeDefaultPolicy"
    )
    """Active default firewall policy. Default to `ACCEPT`."""
    active_rules: RuleList = Field(
        default_factory=not_sent, validation_alias="activeRules", serialization_alias="activeRules"
    )
    """Active firewall rules"""
    pending_default_policy: Policy | None = Field(
        default=None, validation_alias="pendingDefaultPolicy", serialization_alias="pendingDefaultPolicy"
    )
    """Pending default firewall policy set by the `setRules` action"""
    pending_rules: RuleList = Field(
        default_factory=not_sent, validation_alias="pendingRules", serialization_alias="pendingRules"
    )
    """Pending firewall rules"""
    test_time_left: PositiveNumValue = Field(
        default_factory=not_sent, validation_alias="testTimeLeft", serialization_alias="testTimeLeft"
    )
    """Measures the remaining test time for the pending firewall rules"""


class Conf(Model):
    """Firewall configuration"""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"rules"})
    brute_force_protection: BruteForceProtection | None = Field(
        default=None, validation_alias="bruteForceProtection", serialization_alias="bruteForceProtection"
    )
    rules: Rules | None = None


class Firewall(Model):
    """The whole API tree."""

    activated: bool | None = None
    """Firewall service state"""
    conf: Conf | None = None


class UpdateAllRequest(Model):
    """Arguments of ``update_all``."""

    activated: bool | None = None
    """Firewall service state"""


class UpdateBruteForceProtectionRequest(Model):
    """Arguments of ``update_brute_force_protection``."""

    attempts: AttemptsLimit | None = None
    """The fail limit for the brute force protection."""
    block_time: BlockTime | None = Field(default=None, validation_alias="blockTime", serialization_alias="blockTime")
    """The time an IP is blocked for the brute force protection."""
    enabled: bool | None = None
    """The enabled state of the brute force protection."""
    interval: BlockInterval | None = None
    """The interval for the amount of fails for the brute force protection."""


class SetActivatedRequest(Model):
    activated: bool
    """Firewall service state"""


class SetRulesRequest(Model):
    default_policy: Policy | None = Field(
        default=None, validation_alias="defaultPolicy", serialization_alias="defaultPolicy"
    )
    """Default firewall policy"""
    fallback_time: PositiveNumValue | None = Field(
        default=None, validation_alias="fallbackTime", serialization_alias="fallbackTime"
    )
    """Maximum time in seconds to wait before reverting back to previous active rules"""
    rules: RuleList | None = None
    """Rules to set as active"""


class SetBruteForceProtectionAttemptsRequest(Model):
    attempts: AttemptsLimit
    """The fail limit for the brute force protection."""


class SetBruteForceProtectionBlockTimeRequest(Model):
    block_time: BlockTime = Field(validation_alias="blockTime", serialization_alias="blockTime")
    """The time an IP is blocked for the brute force protection."""


class SetBruteForceProtectionEnabledRequest(Model):
    enabled: bool
    """The enabled state of the brute force protection."""


class SetBruteForceProtectionIntervalRequest(Model):
    interval: BlockInterval
    """The interval for the amount of fails for the brute force protection."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/firewall/v1"

INFO = ApiInfo(
    id="firewall-config",
    name="Firewall configuration service",
    family=Family.DCA,
    discovery=(DcaDiscovery("firewall", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/firewall-configuration-api/",),
    errors={
        100: ErrorCode("Invalid IP address. The IP address is not a valid IPv4 or IPv6 address.", "invalid_argument"),
        101: ErrorCode("Invalid IP address range.", "invalid_argument"),
        103: ErrorCode(
            "Invalid request. The request doesn't meet the internal requirements. See the following use cases.",
            "invalid_argument",
        ),
        104: ErrorCode("Invalid port range.", "invalid_argument"),
    },
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Firewall, access="admin", effect="read")
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_activated = Operation(
        INFO,
        "set_activated",
        DcaBinding("PATCH", f"{ROOT}/activated", body="value", body_field="activated"),
        params=SetActivatedRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_activated = Operation(
        INFO, "get_activated", DcaBinding("GET", f"{ROOT}/activated"), result=bool, access="admin", effect="read"
    )
    get_conf = Operation(
        INFO, "get_conf", DcaBinding("GET", f"{ROOT}/conf"), result=Conf, access="admin", effect="read"
    )
    clear_pending_rules = Operation(
        INFO,
        "clear_pending_rules",
        DcaBinding("POST", f"{ROOT}/conf/clearPendingRules", body="object"),
        access="admin",
        effect="action",
    )
    confirm_rules = Operation(
        INFO,
        "confirm_rules",
        DcaBinding("POST", f"{ROOT}/conf/confirmRules", body="object"),
        access="admin",
        effect="action",
    )
    set_rules = Operation(
        INFO,
        "set_rules",
        DcaBinding("POST", f"{ROOT}/conf/setRules", body="object"),
        params=SetRulesRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    get_active_default_policy = Operation(
        INFO,
        "get_active_default_policy",
        DcaBinding("GET", f"{ROOT}/conf/rules/activeDefaultPolicy"),
        result=Policy,
        access="admin",
        effect="read",
    )
    get_pending_default_policy = Operation(
        INFO,
        "get_pending_default_policy",
        DcaBinding("GET", f"{ROOT}/conf/rules/pendingDefaultPolicy"),
        result=Policy | None,
        access="admin",
        effect="read",
    )
    get_brute_force_protection = Operation(
        INFO,
        "get_brute_force_protection",
        DcaBinding("GET", f"{ROOT}/conf/bruteForceProtection"),
        result=BruteForceProtection,
        access="admin",
        effect="read",
    )
    update_brute_force_protection = Operation(
        INFO,
        "update_brute_force_protection",
        DcaBinding("PATCH", f"{ROOT}/conf/bruteForceProtection", body="object"),
        params=UpdateBruteForceProtectionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brute_force_protection_attempts = Operation(
        INFO,
        "set_brute_force_protection_attempts",
        DcaBinding("PATCH", f"{ROOT}/conf/bruteForceProtection/attempts", body="value", body_field="attempts"),
        params=SetBruteForceProtectionAttemptsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brute_force_protection_block_time = Operation(
        INFO,
        "set_brute_force_protection_block_time",
        DcaBinding("PATCH", f"{ROOT}/conf/bruteForceProtection/blockTime", body="value", body_field="blockTime"),
        params=SetBruteForceProtectionBlockTimeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brute_force_protection_enabled = Operation(
        INFO,
        "set_brute_force_protection_enabled",
        DcaBinding("PATCH", f"{ROOT}/conf/bruteForceProtection/enabled", body="value", body_field="enabled"),
        params=SetBruteForceProtectionEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_brute_force_protection_interval = Operation(
        INFO,
        "set_brute_force_protection_interval",
        DcaBinding("PATCH", f"{ROOT}/conf/bruteForceProtection/interval", body="value", body_field="interval"),
        params=SetBruteForceProtectionIntervalRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_rules = Operation(
        INFO, "get_rules", DcaBinding("GET", f"{ROOT}/conf/rules"), result=Rules, access="admin", effect="read"
    )


# ---------------------------------------------------------------------------
# API classes


class FirewallApi(SyncApi):
    """Firewall configuration service (``firewall-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Firewall:
        """All data of the Firewall configuration service API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def update_all(self, *, activated: bool | MISSING = MISSING, request_options: RequestOptions | None = None) -> None:
        """Update the Firewall configuration service settings.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_all, None, {"activated": activated}, request_options)

    def set_activated(self, activated: bool, *, request_options: RequestOptions | None = None) -> None:
        """Activate or deactivate the firewall. Changes only the fields given. Access: admin."""
        self._run(OPS.set_activated, None, {"activated": activated}, request_options)

    def get_activated(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the firewall is activated. Access: admin."""
        return self._run(OPS.get_activated, None, {}, request_options)

    def get_conf(self, *, request_options: RequestOptions | None = None) -> Conf:
        """Get the firewall configuration. Access: admin."""
        return self._run(OPS.get_conf, None, {}, request_options)

    def clear_pending_rules(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear the pending rules, abort any active test and restore the previous rules.

        Access: admin.
        """
        self._run(OPS.clear_pending_rules, None, {}, request_options)

    def confirm_rules(self, *, request_options: RequestOptions | None = None) -> None:
        """Confirm the active firewall rules, deactivating the fallback and clearing the pending rules.

        Access: admin.
        """
        self._run(OPS.confirm_rules, None, {}, request_options)

    @overload
    def set_rules(self, request: SetRulesRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_rules(
        self,
        /,
        *,
        default_policy: Policy | MISSING = MISSING,
        fallback_time: PositiveNumValue | MISSING = MISSING,
        rules: RuleList | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_rules(
        self, request: SetRulesRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set the active firewall rule list.

        The changes are written to the active rules. With a fallbackTime greater than 0 the previous rules
        are restored unless confirm_rules is called in time; 0 applies the rules immediately and clears the
        pending rules. A fallbackTime greater than 0 while the firewall is inactive fails with error 103.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_rules, request, kwargs, request_options)

    def get_active_default_policy(self, *, request_options: RequestOptions | None = None) -> Policy:
        """Get the active default firewall policy. Access: admin."""
        return self._run(OPS.get_active_default_policy, None, {}, request_options)

    def get_pending_default_policy(self, *, request_options: RequestOptions | None = None) -> Policy | None:
        """Get the pending default firewall policy set by set_rules, or null. Access: admin."""
        return self._run(OPS.get_pending_default_policy, None, {}, request_options)

    def get_brute_force_protection(self, *, request_options: RequestOptions | None = None) -> BruteForceProtection:
        """Get the brute force protection settings. Access: admin."""
        return self._run(OPS.get_brute_force_protection, None, {}, request_options)

    def update_brute_force_protection(
        self,
        *,
        attempts: AttemptsLimit | MISSING = MISSING,
        block_time: BlockTime | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        interval: BlockInterval | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the brute force protection settings. Changes only the fields given. Access: admin."""
        self._run(
            OPS.update_brute_force_protection,
            None,
            {"attempts": attempts, "block_time": block_time, "enabled": enabled, "interval": interval},
            request_options,
        )

    def set_brute_force_protection_attempts(
        self, attempts: AttemptsLimit, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the fail limit for the brute force protection.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_brute_force_protection_attempts, None, {"attempts": attempts}, request_options)

    def set_brute_force_protection_block_time(
        self, block_time: BlockTime, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set how long (s) an IP is blocked by the brute force protection.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_brute_force_protection_block_time, None, {"block_time": block_time}, request_options)

    def set_brute_force_protection_enabled(
        self, enabled: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the brute force protection.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_brute_force_protection_enabled, None, {"enabled": enabled}, request_options)

    def set_brute_force_protection_interval(
        self, interval: BlockInterval, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the interval (s) in which failures are counted by the brute force protection.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_brute_force_protection_interval, None, {"interval": interval}, request_options)

    def get_rules(self, *, request_options: RequestOptions | None = None) -> Rules:
        """Get the active and pending firewall rules. Access: admin."""
        return self._run(OPS.get_rules, None, {}, request_options)


class AsyncFirewallApi(AsyncApi):
    """Firewall configuration service (``firewall-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Firewall:
        """All data of the Firewall configuration service API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def update_all(
        self, *, activated: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Update the Firewall configuration service settings.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_all, None, {"activated": activated}, request_options)

    async def set_activated(self, activated: bool, *, request_options: RequestOptions | None = None) -> None:
        """Activate or deactivate the firewall. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_activated, None, {"activated": activated}, request_options)

    async def get_activated(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the firewall is activated. Access: admin."""
        return await self._run(OPS.get_activated, None, {}, request_options)

    async def get_conf(self, *, request_options: RequestOptions | None = None) -> Conf:
        """Get the firewall configuration. Access: admin."""
        return await self._run(OPS.get_conf, None, {}, request_options)

    async def clear_pending_rules(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear the pending rules, abort any active test and restore the previous rules.

        Access: admin.
        """
        await self._run(OPS.clear_pending_rules, None, {}, request_options)

    async def confirm_rules(self, *, request_options: RequestOptions | None = None) -> None:
        """Confirm the active firewall rules, deactivating the fallback and clearing the pending rules.

        Access: admin.
        """
        await self._run(OPS.confirm_rules, None, {}, request_options)

    @overload
    async def set_rules(
        self, request: SetRulesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_rules(
        self,
        /,
        *,
        default_policy: Policy | MISSING = MISSING,
        fallback_time: PositiveNumValue | MISSING = MISSING,
        rules: RuleList | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_rules(
        self, request: SetRulesRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Set the active firewall rule list.

        The changes are written to the active rules. With a fallbackTime greater than 0 the previous rules
        are restored unless confirm_rules is called in time; 0 applies the rules immediately and clears the
        pending rules. A fallbackTime greater than 0 while the firewall is inactive fails with error 103.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_rules, request, kwargs, request_options)

    async def get_active_default_policy(self, *, request_options: RequestOptions | None = None) -> Policy:
        """Get the active default firewall policy. Access: admin."""
        return await self._run(OPS.get_active_default_policy, None, {}, request_options)

    async def get_pending_default_policy(self, *, request_options: RequestOptions | None = None) -> Policy | None:
        """Get the pending default firewall policy set by set_rules, or null. Access: admin."""
        return await self._run(OPS.get_pending_default_policy, None, {}, request_options)

    async def get_brute_force_protection(
        self, *, request_options: RequestOptions | None = None
    ) -> BruteForceProtection:
        """Get the brute force protection settings. Access: admin."""
        return await self._run(OPS.get_brute_force_protection, None, {}, request_options)

    async def update_brute_force_protection(
        self,
        *,
        attempts: AttemptsLimit | MISSING = MISSING,
        block_time: BlockTime | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        interval: BlockInterval | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the brute force protection settings. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.update_brute_force_protection,
            None,
            {"attempts": attempts, "block_time": block_time, "enabled": enabled, "interval": interval},
            request_options,
        )

    async def set_brute_force_protection_attempts(
        self, attempts: AttemptsLimit, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the fail limit for the brute force protection.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_brute_force_protection_attempts, None, {"attempts": attempts}, request_options)

    async def set_brute_force_protection_block_time(
        self, block_time: BlockTime, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set how long (s) an IP is blocked by the brute force protection.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_brute_force_protection_block_time, None, {"block_time": block_time}, request_options)

    async def set_brute_force_protection_enabled(
        self, enabled: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable the brute force protection.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_brute_force_protection_enabled, None, {"enabled": enabled}, request_options)

    async def set_brute_force_protection_interval(
        self, interval: BlockInterval, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the interval (s) in which failures are counted by the brute force protection.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_brute_force_protection_interval, None, {"interval": interval}, request_options)

    async def get_rules(self, *, request_options: RequestOptions | None = None) -> Rules:
        """Get the active and pending firewall rules. Access: admin."""
        return await self._run(OPS.get_rules, None, {}, request_options)
