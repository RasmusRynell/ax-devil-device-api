# GENERATED from specs/apis/device-configuration/network-diagnostics-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Diagnose network issues with ping and TCP reachability tests, active connection lists and TCP retransmission statistics.

Docs: https://developer.axis.com/vapix/device-configuration/network-diagnostics/
"""

from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

IpAddress = str
PositiveInteger = Annotated[int, Field(ge=0)]
PortNumber = Annotated[int, Field(ge=1, le=65535)]
Protocol = Literal["TCP", "UDP"]
ConnectionState = Literal["LISTEN", "ESTABLISHED", "TIME_WAIT", "STATELESS"]


class ConnectionEntry(Model):
    """A single network connection entry"""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"state"})
    address: IpAddress
    """Local bound or remote peer IP address of the connection"""
    pid: PositiveInteger
    """Process ID of the owning process"""
    port: PortNumber
    """Port number of the connection"""
    process: str
    """Name of the owning process"""
    protocol: Protocol
    """Network protocol used by the connection"""
    service: str
    """IANA service name associated with the port number, e.g. http, https or ssh; empty if the port has no registered service name"""
    state: ConnectionState | None = None
    """Current state of the connection"""


ConnectionList = list[ConnectionEntry]
IsoTimestamp = Annotated[str, Field(pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")]


class PingRequest(Model):
    """Parameters for a ping request"""

    address: IpAddress
    """The IP address to ping"""


class TcpRetransmissionSpike(Model):
    """Representation of a TCP retransmission spike"""

    retransmissions: PositiveInteger
    """Magnitude of the spike"""
    timestamp: IsoTimestamp
    """Timestamp of the spike"""


class TcpTestRequest(Model):
    """Data to be used in TCP connection request"""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"interface", "timeout"})
    address: IpAddress
    """The IP address to send TCP connection request to"""
    interface: str | None = None
    """The local network interface to bind the connection to, such as eth0. If omitted, the operating system routing table will select the outgoing interface automatically"""
    port: PortNumber
    """The port number to be used for TCP connection request"""
    timeout: PositiveInteger | None = None
    """Optional timeout in seconds for TCP connection request. If omitted or set to 0, default 1 second-timeout is used"""


class TestResult(Model):
    """Connectivity test result"""

    success: bool
    """Device or service reachability test result"""


class Connectivity(Model):
    """Interface for network connectivity tests."""


class Netstats(Model):
    """Interface that retrieves network statistics"""

    sampling_interval: int = Field(validation_alias="samplingInterval", serialization_alias="samplingInterval")
    """The interval at which retransmissions and spikes are sampled in seconds."""


class NetworkDiagnostics(Model):
    """The whole API tree."""

    connectivity: Connectivity | None = None
    netstats: Netstats | None = None


class TcpRetransmissionSpikesRequest(Model):
    count: PositiveInteger
    """Number of spikes to get; 0 gets all recorded spikes."""


class TcpRetransmissionsRequest(Model):
    hours: PositiveInteger
    """Number of hours to look back; 0 gets all recorded retransmissions."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/network-diagnostics/v1"

INFO = ApiInfo(
    id="network-diagnostics-config",
    name="Network diagnostics API",
    family=Family.DCA,
    discovery=(DcaDiscovery("network-diagnostics", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/network-diagnostics/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=NetworkDiagnostics, access="admin", effect="read"
    )
    connection_list = Operation(
        INFO,
        "connection_list",
        DcaBinding("POST", f"{ROOT}/connectivity/connectionList", body="object"),
        result=list[ConnectionEntry],
        access="admin",
        effect="action",
    )
    ping_test = Operation(
        INFO,
        "ping_test",
        DcaBinding("POST", f"{ROOT}/connectivity/pingTest", body="object"),
        params=PingRequest,
        result=TestResult,
        access="admin",
        effect="action",
    )
    tcp_test = Operation(
        INFO,
        "tcp_test",
        DcaBinding("POST", f"{ROOT}/connectivity/tcpTest", body="object"),
        params=TcpTestRequest,
        result=TestResult,
        access="admin",
        effect="action",
    )
    get_netstats = Operation(
        INFO, "get_netstats", DcaBinding("GET", f"{ROOT}/netstats"), result=Netstats, access="admin", effect="read"
    )
    get_sampling_interval = Operation(
        INFO,
        "get_sampling_interval",
        DcaBinding("GET", f"{ROOT}/netstats/samplingInterval"),
        result=int,
        access="admin",
        effect="read",
    )
    tcp_retransmission_spikes = Operation(
        INFO,
        "tcp_retransmission_spikes",
        DcaBinding("POST", f"{ROOT}/netstats/tcpRetransmissionSpikes", body="value", body_field="count"),
        params=TcpRetransmissionSpikesRequest,
        result=list[TcpRetransmissionSpike],
        access="admin",
        effect="action",
    )
    tcp_retransmissions = Operation(
        INFO,
        "tcp_retransmissions",
        DcaBinding("POST", f"{ROOT}/netstats/tcpRetransmissions", body="value", body_field="hours"),
        params=TcpRetransmissionsRequest,
        result=int,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class NetworkDiagnosticsApi(SyncApi):
    """Network diagnostics API (``network-diagnostics-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> NetworkDiagnostics:
        """All data of the Network diagnostics API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def connection_list(self, *, request_options: RequestOptions | None = None) -> list[ConnectionEntry]:
        """Get a list of active network connections. Access: admin."""
        return self._run(OPS.connection_list, None, {}, request_options)

    def ping_test(self, *, address: IpAddress, request_options: RequestOptions | None = None) -> TestResult:
        """Test if an address is reachable via ICMP ping. Access: admin."""
        return self._run(OPS.ping_test, None, {"address": address}, request_options)

    def tcp_test(
        self,
        *,
        address: IpAddress,
        interface: str | None | MISSING = MISSING,
        port: PortNumber,
        timeout: PositiveInteger | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> TestResult:
        """Test whether a service is reachable by performing a TCP connection request.

        Omitting the timeout or giving 0 uses the default of 1 second. Without an interface the routing
        table selects the outgoing interface.

        Access: admin.
        """
        return self._run(
            OPS.tcp_test,
            None,
            {"address": address, "interface": interface, "port": port, "timeout": timeout},
            request_options,
        )

    def get_netstats(self, *, request_options: RequestOptions | None = None) -> Netstats:
        """Get the network statistics settings. Access: admin."""
        return self._run(OPS.get_netstats, None, {}, request_options)

    def get_sampling_interval(self, *, request_options: RequestOptions | None = None) -> int:
        """Get the interval (s) at which retransmissions and spikes are sampled. Access: admin."""
        return self._run(OPS.get_sampling_interval, None, {}, request_options)

    def tcp_retransmission_spikes(
        self, count: PositiveInteger, *, request_options: RequestOptions | None = None
    ) -> list[TcpRetransmissionSpike]:
        """Get the last N TCP retransmission spikes.

        Specifying 0 returns all buffered spikes. The device stores up to 1024 spikes and replaces the
        oldest ones when the limit is reached.

        Access: admin.
        """
        return self._run(OPS.tcp_retransmission_spikes, None, {"count": count}, request_options)

    def tcp_retransmissions(self, hours: PositiveInteger, *, request_options: RequestOptions | None = None) -> int:
        """Get the number of TCP retransmissions in the last N hours.

        Specifying 0 returns the total recorded on the device. The device buffers a limited number of
        samples and overwrites older data after a few days.

        Access: admin.
        """
        return self._run(OPS.tcp_retransmissions, None, {"hours": hours}, request_options)


class AsyncNetworkDiagnosticsApi(AsyncApi):
    """Network diagnostics API (``network-diagnostics-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> NetworkDiagnostics:
        """All data of the Network diagnostics API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def connection_list(self, *, request_options: RequestOptions | None = None) -> list[ConnectionEntry]:
        """Get a list of active network connections. Access: admin."""
        return await self._run(OPS.connection_list, None, {}, request_options)

    async def ping_test(self, *, address: IpAddress, request_options: RequestOptions | None = None) -> TestResult:
        """Test if an address is reachable via ICMP ping. Access: admin."""
        return await self._run(OPS.ping_test, None, {"address": address}, request_options)

    async def tcp_test(
        self,
        *,
        address: IpAddress,
        interface: str | None | MISSING = MISSING,
        port: PortNumber,
        timeout: PositiveInteger | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> TestResult:
        """Test whether a service is reachable by performing a TCP connection request.

        Omitting the timeout or giving 0 uses the default of 1 second. Without an interface the routing
        table selects the outgoing interface.

        Access: admin.
        """
        return await self._run(
            OPS.tcp_test,
            None,
            {"address": address, "interface": interface, "port": port, "timeout": timeout},
            request_options,
        )

    async def get_netstats(self, *, request_options: RequestOptions | None = None) -> Netstats:
        """Get the network statistics settings. Access: admin."""
        return await self._run(OPS.get_netstats, None, {}, request_options)

    async def get_sampling_interval(self, *, request_options: RequestOptions | None = None) -> int:
        """Get the interval (s) at which retransmissions and spikes are sampled. Access: admin."""
        return await self._run(OPS.get_sampling_interval, None, {}, request_options)

    async def tcp_retransmission_spikes(
        self, count: PositiveInteger, *, request_options: RequestOptions | None = None
    ) -> list[TcpRetransmissionSpike]:
        """Get the last N TCP retransmission spikes.

        Specifying 0 returns all buffered spikes. The device stores up to 1024 spikes and replaces the
        oldest ones when the limit is reached.

        Access: admin.
        """
        return await self._run(OPS.tcp_retransmission_spikes, None, {"count": count}, request_options)

    async def tcp_retransmissions(
        self, hours: PositiveInteger, *, request_options: RequestOptions | None = None
    ) -> int:
        """Get the number of TCP retransmissions in the last N hours.

        Specifying 0 returns the total recorded on the device. The device buffers a limited number of
        samples and overwrites older data after a few days.

        Access: admin.
        """
        return await self._run(OPS.tcp_retransmissions, None, {"hours": hours}, request_options)
