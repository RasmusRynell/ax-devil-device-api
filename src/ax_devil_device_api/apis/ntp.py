# GENERATED from specs/apis/network-video/ntp.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Get NTP/NTS client info and set NTP client configuration (static/DHCP servers, NTS KE servers, poll intervals) via /axis-cgi/ntp.cgi.

Docs: https://developer.axis.com/vapix/network-video/ntp-api/
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class NtpClient(Model):
    """State and configuration of the NTP client."""

    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {"advertised_servers", "max_supported_static_servers", "synced", "time_offset", "time_to_next_sync"}
    )
    enabled: bool | None = None
    """Enabled state of the NTP client. true: enabled and running; false: disabled and not running."""
    nts_enabled: bool | None = Field(default=None, validation_alias="NTSEnabled", serialization_alias="NTSEnabled")
    """true: the NTP client uses NTS instead of regular NTP; false: NTS is disabled."""
    ntske_server_ca_certs: list[str] | None = Field(
        default=None, validation_alias="NTSKEServerCACerts", serialization_alias="NTSKEServerCACerts"
    )
    """Optional. List of CA certificates to trust for certification validation."""
    servers_source: Literal["DHCP", "static"] | None = Field(
        default=None, validation_alias="serversSource", serialization_alias="serversSource"
    )
    """DHCP: uses NTP servers listed in a DHCP lease, falls back to static if none were obtained. static: uses a static list of NTP servers set by the user."""
    max_supported_static_servers: int | None = Field(
        default=None, validation_alias="maxSupportedStaticServers", serialization_alias="maxSupportedStaticServers"
    )
    """The maximum number of static servers that the client can use for time synchronization."""
    static_servers: list[str] | None = Field(
        default=None, validation_alias="staticServers", serialization_alias="staticServers"
    )
    """A list of static NTP servers. Used if serversSource is static and NTS is disabled."""
    advertised_servers: list[str] | None = Field(
        default=None, validation_alias="advertisedServers", serialization_alias="advertisedServers"
    )
    """A list of NTP servers received in a DHCP lease. Used if serversSource is DHCP and NTS is disabled."""
    static_ntske_servers: list[str] | None = Field(
        default=None, validation_alias="staticNTSKEServers", serialization_alias="staticNTSKEServers"
    )
    """A static list of NTS Key Establishment servers, validated by system trusted CA certificates if not specified by NTSKEServerCACerts."""
    synced: bool | None = None
    """Indicates that time has been synced with NTP after a reboot."""
    time_to_next_sync: int | None = Field(
        default=None, validation_alias="timeToNextSync", serialization_alias="timeToNextSync"
    )
    """Remaining time (seconds) until the next synchronization attempt; 0 if no NTP servers are used."""
    time_offset: float | None = Field(default=None, validation_alias="timeOffset", serialization_alias="timeOffset")
    """Time offset between local and server time (milliseconds). Only used if synced is true."""
    minpoll: int | None = None
    """Minimum interval between synchronization attempts, as a power of 2 in seconds (e.g. 6 = 64 s)."""
    maxpoll: int | None = None
    """Maximum interval between synchronization attempts, as a power of 2 in seconds."""


class NtpInfo(Model):
    """NTP configuration of the device. The ``client`` section is present only on devices with NTP client support."""

    client: NtpClient | None = None


class SetNtpClientConfigurationRequest(Model):
    enabled: bool | None = None
    """Desired state of the NTP client. true: enabled and running; false: disabled. enabled=true must be used in order to use NTP, both with or without NTS."""
    nts_enabled: bool | None = Field(default=None, validation_alias="NTSEnabled", serialization_alias="NTSEnabled")
    """Specifies if NTS is used. true: use NTS instead of regular NTP; false: NTS disabled."""
    ntske_server_ca_certs: list[str] | None = Field(
        default=None, validation_alias="NTSKEServerCACerts", serialization_alias="NTSKEServerCACerts"
    )
    """Optional. List of CA certificates to trust for certification validation. Table lists it as params.client.NTSKEServerCACerts; request syntax as params.NTSKEServerCACerts."""
    servers_source: Literal["DHCP", "static"] | None = Field(
        default=None, validation_alias="serversSource", serialization_alias="serversSource"
    )
    """Source of the server list. DHCP: NTP servers from a DHCP lease; static: user-set static list."""
    static_servers: list[str] | None = Field(
        default=None, validation_alias="staticServers", serialization_alias="staticServers"
    )
    """List of static NTP servers (IP addresses or domain names); used if serversSource is static and NTS disabled."""
    static_ntske_servers: list[str] | None = Field(
        default=None, validation_alias="staticNTSKEServers", serialization_alias="staticNTSKEServers"
    )
    """Static list of NTS KE servers used to synchronize time over NTS; limited by maxSupportedStaticServers. Validated by system trusted CA certificates if NTSKEServerCACerts not specified."""
    minpoll: int | None = Field(default=None, ge=0, le=24)
    """Minimum poll interval (power of 2 seconds). Default 6. Allowed 0-24; should not be greater than maxpoll. Default: 6."""
    maxpoll: int | None = Field(default=None, ge=0, le=24)
    """Maximum poll interval (power of 2 seconds). Default 10. Allowed 0-24. Default: 10."""

    @classmethod
    def from_current(cls, client: NtpClient) -> SetNtpClientConfigurationRequest:
        """A request that rewrites ``client`` unchanged: copy it, edit fields, send it back."""
        data = client.request_data()
        return cls(**data)


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/ntp.cgi"

INFO = ApiInfo(
    id="ntp",
    name="NTP API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("ntp"),),
    docs=("https://developer.axis.com/vapix/network-video/ntp-api/",),
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
    get_ntp_info = Operation(
        INFO, "get_ntp_info", JsonRpcBinding("getNTPInfo", PATH), result=NtpInfo, access="admin", effect="read"
    )
    set_ntp_client_configuration = Operation(
        INFO,
        "set_ntp_client_configuration",
        JsonRpcBinding("setNTPClientConfiguration", PATH),
        params=SetNtpClientConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "4004/subCode 1": ErrorCode("The invalid parameter is `enabled`.", "invalid_argument"),
            "4004/subCode 2": ErrorCode("The invalid parameter is `serversSource`.", "invalid_argument"),
            "4004/subCode 3": ErrorCode(
                "The invalid parameter is `staticServers` or one of its list values.", "invalid_argument"
            ),
            "4004/subCode 5": ErrorCode("The invalid parameter is `NTSEnabled`.", "invalid_argument"),
            "4004/subCode 6": ErrorCode(
                "The invalid parameter is `staticNTSKEServers` or one of its list values.", "invalid_argument"
            ),
            "4004/subCode 7": ErrorCode(
                "The invalid parameter is `minpoll` valid values range from (0) to (24).", "invalid_argument"
            ),
            "4004/subCode 8": ErrorCode(
                "The invalid parameter is `maxpoll` valid values range from (0) to (24).", "invalid_argument"
            ),
            "4004/subCode 9": ErrorCode("The invalid parameter is `NTSKEServerCACerts`.", "invalid_argument"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class NtpApi(SyncApi):
    """NTP API (``ntp``, version 1)."""

    INFO = INFO

    def get_ntp_info(self, *, request_options: RequestOptions | None = None) -> NtpInfo:
        """Retrieve the NTP configuration of the device. Access: admin."""
        return self._run(OPS.get_ntp_info, None, {}, request_options)

    @overload
    def set_ntp_client_configuration(
        self, request: SetNtpClientConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_ntp_client_configuration(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        nts_enabled: bool | MISSING = MISSING,
        ntske_server_ca_certs: list[str] | MISSING = MISSING,
        servers_source: Literal["DHCP", "static"] | MISSING = MISSING,
        static_servers: list[str] | MISSING = MISSING,
        static_ntske_servers: list[str] | MISSING = MISSING,
        minpoll: int | MISSING = MISSING,
        maxpoll: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_ntp_client_configuration(
        self,
        request: SetNtpClientConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the NTP client configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_ntp_client_configuration, request, kwargs, request_options)


class AsyncNtpApi(AsyncApi):
    """NTP API (``ntp``, version 1)."""

    INFO = INFO

    async def get_ntp_info(self, *, request_options: RequestOptions | None = None) -> NtpInfo:
        """Retrieve the NTP configuration of the device. Access: admin."""
        return await self._run(OPS.get_ntp_info, None, {}, request_options)

    @overload
    async def set_ntp_client_configuration(
        self, request: SetNtpClientConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_ntp_client_configuration(
        self,
        /,
        *,
        enabled: bool | MISSING = MISSING,
        nts_enabled: bool | MISSING = MISSING,
        ntske_server_ca_certs: list[str] | MISSING = MISSING,
        servers_source: Literal["DHCP", "static"] | MISSING = MISSING,
        static_servers: list[str] | MISSING = MISSING,
        static_ntske_servers: list[str] | MISSING = MISSING,
        minpoll: int | MISSING = MISSING,
        maxpoll: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_ntp_client_configuration(
        self,
        request: SetNtpClientConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the NTP client configuration. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_ntp_client_configuration, request, kwargs, request_options)
