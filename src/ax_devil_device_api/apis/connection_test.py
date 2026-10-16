# GENERATED from specs/apis/network-video/connection-test.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Test whether the device can ping a host (pingtest.cgi) or reach an IP address and port (tcptest.cgi).

Docs: https://developer.axis.com/vapix/network-video/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, Text
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PingTestRequest(Model):
    ip: str
    """IP address or DNS hostname of the device or server to ping."""


class TcpTestRequest(Model):
    address: str
    """IP address to reach."""
    port: int = Field(ge=1, le=65535)
    """Port to reach."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/pingtest.cgi"

INFO = ApiInfo(
    id="connection-test",
    name="Connection test: Ping, ports and IP addresses",
    family=Family.CGI,
    docs=("https://developer.axis.com/vapix/network-video/",),
)


class OPS:
    ping_test = Operation(
        INFO,
        "ping_test",
        CgiBinding(PATH, args=(CgiArg("ip"),), reply=Text()),
        params=PingTestRequest,
        result=str,
        access="admin",
        effect="action",
    )
    tcp_test = Operation(
        INFO,
        "tcp_test",
        CgiBinding("/axis-cgi/tcptest.cgi", args=(CgiArg("address"), CgiArg("port")), reply=Text()),
        params=TcpTestRequest,
        result=str,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class ConnectionTestApi(SyncApi):
    """Connection test: Ping, ports and IP addresses (``connection-test``)."""

    INFO = INFO

    def ping_test(self, ip: str, *, request_options: RequestOptions | None = None) -> str:
        """Ping another device or server by IP address or DNS hostname. Access: admin."""
        return self._run(OPS.ping_test, None, {"ip": ip}, request_options)

    def tcp_test(self, address: str, port: int, *, request_options: RequestOptions | None = None) -> str:
        """Test whether the device can reach an IP address and port. Access: admin."""
        return self._run(OPS.tcp_test, None, {"address": address, "port": port}, request_options)


class AsyncConnectionTestApi(AsyncApi):
    """Connection test: Ping, ports and IP addresses (``connection-test``)."""

    INFO = INFO

    async def ping_test(self, ip: str, *, request_options: RequestOptions | None = None) -> str:
        """Ping another device or server by IP address or DNS hostname. Access: admin."""
        return await self._run(OPS.ping_test, None, {"ip": ip}, request_options)

    async def tcp_test(self, address: str, port: int, *, request_options: RequestOptions | None = None) -> str:
        """Test whether the device can reach an IP address and port. Access: admin."""
        return await self._run(OPS.tcp_test, None, {"address": address, "port": port}, request_options)
