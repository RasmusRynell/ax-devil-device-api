# GENERATED from specs/apis/network-video/remote-syslog.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Send the device's system logs to up to two remote syslog servers; enable, disable, query and test.

Docs: https://developer.axis.com/vapix/network-video/remote-syslog/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Protocol = Literal["UDP", "TCP", "TLS"]
SyslogFormat = Literal["AXIS", "RFC3164", "RFC5424"]
Severity = Literal["Emergency", "Alert", "Critical", "Error", "Warning", "Notice", "Informational", "Debug"]
LogType = Literal["Audit", "All"]


class ServerConfig(Model):
    """One remote syslog server. Omitted optional fields get the device defaults, which the responses show."""

    address: str
    """Remote server address (IPv4, IPv6 or host)."""
    port: int | None = Field(default=None, le=65535)
    """Optional. Default depends on protocol/format (see notes: UDP 514; TCP 514 (AXIS/RFC3164) or 601 (RFC5424); TLS 6514)."""
    protocol: Protocol | None = None
    """Default: 'TLS'."""
    syslog_format: SyslogFormat | None = Field(
        default=None, validation_alias="syslogFormat", serialization_alias="syslogFormat"
    )
    """Default: 'RFC5424'."""
    severity: Severity | None = None
    """Default: 'Warning'."""
    type: LogType | None = None
    """Default: 'All'."""


class Status(Model):
    enabled: bool
    """Whether the remote syslog feature is enabled."""
    servers: list[ServerConfig]
    """The configured servers; empty if none."""


class SetupRequest(Model):
    servers: list[ServerConfig]
    """At most 2 servers per request. An empty list removes the servers."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/remotesyslog.cgi"

INFO = ApiInfo(
    id="remote-syslog",
    name="Remote Syslog",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("remote-syslog"),),
    docs=("https://developer.axis.com/vapix/network-video/remote-syslog/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        2105: ErrorCode("Authorization failed", "access_denied"),
        2106: ErrorCode("Authentication failed", "access_denied"),
        2107: ErrorCode("Request too large", "invalid_argument"),
        2200: ErrorCode("No server configured", "unavailable"),
        2201: ErrorCode("Identical servers not allowed", "invalid_argument"),
        2202: ErrorCode("Remote syslog is disabled, sending test messages is not possible", "unavailable"),
        2203: ErrorCode("Too many servers specified", "invalid_argument"),
    },
)


class OPS:
    setup = Operation(
        INFO,
        "setup",
        JsonRpcBinding("setup", PATH),
        params=SetupRequest,
        result=Status,
        access="admin",
        effect="write",
        write="replace",
        errors={
            2103: ErrorCode("Required parameter missing (e.g. details.propertyName=address).", "invalid_argument"),
            2104: ErrorCode(
                "Invalid parameter value specified (details.address, details.propertyName; errors[] when several).",
                "invalid_argument",
            ),
        },
    )
    enable = Operation(
        INFO, "enable", JsonRpcBinding("enable", PATH), result=Status, access="admin", effect="write", write="patch"
    )
    disable = Operation(
        INFO, "disable", JsonRpcBinding("disable", PATH), result=Status, access="admin", effect="write", write="patch"
    )
    status = Operation(INFO, "status", JsonRpcBinding("status", PATH), result=Status, access="admin", effect="read")
    test = Operation(INFO, "test", JsonRpcBinding("test", PATH), result=Status, access="admin", effect="action")


# ---------------------------------------------------------------------------
# API classes


class RemoteSyslogApi(SyncApi):
    """Remote Syslog (``remote-syslog``, version 1)."""

    INFO = INFO

    @overload
    def setup(self, request: SetupRequest, /, *, request_options: RequestOptions | None = None) -> Status: ...
    @overload
    def setup(self, servers: list[ServerConfig], /, *, request_options: RequestOptions | None = None) -> Status: ...
    def setup(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> Status:
        """Set the server configuration and send system logs to the remote servers.

        Replaces the configured servers (an empty list removes them) and returns the resulting status.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetupRequest):
            kwargs = {**dict(zip(("servers",), (request, *args), strict=False)), **kwargs}
            request = None
        return self._run(OPS.setup, request, kwargs, request_options)

    def enable(self, *, request_options: RequestOptions | None = None) -> Status:
        """Start sending system logs to the remote servers.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.enable, None, {}, request_options)

    def disable(self, *, request_options: RequestOptions | None = None) -> Status:
        """Stop sending system logs to the remote servers.

        No messages are buffered while sending is stopped.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.disable, None, {}, request_options)

    def status(self, *, request_options: RequestOptions | None = None) -> Status:
        """Retrieve whether remote syslog is enabled and the configured servers. Access: admin."""
        return self._run(OPS.status, None, {}, request_options)

    def test(self, *, request_options: RequestOptions | None = None) -> Status:
        """Send test log messages to the remote servers.

        Generates messages for all severity levels; only the configured levels are sent.

        Access: admin.
        """
        return self._run(OPS.test, None, {}, request_options)


class AsyncRemoteSyslogApi(AsyncApi):
    """Remote Syslog (``remote-syslog``, version 1)."""

    INFO = INFO

    @overload
    async def setup(self, request: SetupRequest, /, *, request_options: RequestOptions | None = None) -> Status: ...
    @overload
    async def setup(
        self, servers: list[ServerConfig], /, *, request_options: RequestOptions | None = None
    ) -> Status: ...
    async def setup(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> Status:
        """Set the server configuration and send system logs to the remote servers.

        Replaces the configured servers (an empty list removes them) and returns the resulting status.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetupRequest):
            kwargs = {**dict(zip(("servers",), (request, *args), strict=False)), **kwargs}
            request = None
        return await self._run(OPS.setup, request, kwargs, request_options)

    async def enable(self, *, request_options: RequestOptions | None = None) -> Status:
        """Start sending system logs to the remote servers.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.enable, None, {}, request_options)

    async def disable(self, *, request_options: RequestOptions | None = None) -> Status:
        """Stop sending system logs to the remote servers.

        No messages are buffered while sending is stopped.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.disable, None, {}, request_options)

    async def status(self, *, request_options: RequestOptions | None = None) -> Status:
        """Retrieve whether remote syslog is enabled and the configured servers. Access: admin."""
        return await self._run(OPS.status, None, {}, request_options)

    async def test(self, *, request_options: RequestOptions | None = None) -> Status:
        """Send test log messages to the remote servers.

        Generates messages for all severity levels; only the configured levels are sent.

        Access: admin.
        """
        return await self._run(OPS.test, None, {}, request_options)
