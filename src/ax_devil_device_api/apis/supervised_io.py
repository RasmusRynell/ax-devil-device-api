# GENERATED from specs/apis/network-video/supervised-io.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure supervised I/O (tamper detection on I/O ports via end-of-line resistor state ranges) through /axis-cgi/supervisedio.cgi.

Docs: https://developer.axis.com/vapix/network-video/supervised-io/
"""

from __future__ import annotations

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Range(Model):
    """Limits of the analog level that correspond to one port state."""

    state: str
    """Name of the state, for example ``short``, ``close``, ``open`` or ``cut``. The documentation is inconsistent on the exact names; use the ones from ``get_supported_states``."""
    lowerlimit: int
    """Lower limit of the analog level range."""
    upperlimit: int
    """Upper limit of the analog level range."""


class PortQuery(Model):
    """Selects one I/O port. An empty list of queries, or a query without a port, addresses all ports as described per operation."""

    port: int | None = None
    """The I/O port to address."""


class PortCapability(Model):
    port: int
    """The port number."""
    input: bool
    """True if a supervised input exists."""
    output: bool
    """True if a supervised output exists."""


class PortSupervision(Model):
    port: int
    supervised: bool
    """True if the port is supervised."""
    supervisable: bool
    """True if the port can be supervised."""
    state: str | None = None
    """The current state of the port."""
    level: int | None = None
    """The current analog level."""


class PortRanges(Model):
    port: int
    ranges: list[Range]
    """The ranges of each state. Empty if no ranges are set or the port is not supervisable."""


class State(Model):
    name: str


class PortStates(Model):
    port: int
    states: list[State]


class PortSupervisionSetting(Model):
    """Supervision settings for one port."""

    port: int | None = None
    """The port to configure. If omitted, all ports are configured."""
    supervised: bool
    """True activates supervised I/O for the port, false deactivates it."""
    ranges: list[Range] | None = None
    """The range of limits for each state."""


class SetResult(Model):
    port: int
    code: int
    """``1`` if the operation succeeded, otherwise one of the error codes."""
    message: str | None = None
    """Describes the error, if any."""


class NumberOfPorts(Model):
    inputs: int
    """Number of input ports."""
    outputs: int
    """Number of output ports."""


class SupervisableResult(Model):
    items: list[PortCapability]


class SupervisedResult(Model):
    items: list[PortSupervision]


class SupervisedRangesResult(Model):
    items: list[PortRanges]


class SupportedStatesResult(Model):
    items: list[PortStates]


class SetSupervisedResult(Model):
    items: list[SetResult]


class IsSupervisableRequest(Model):
    ports: list[PortQuery]


class GetSupervisedRequest(Model):
    ports: list[PortQuery]


class SetSupervisedRequest(Model):
    ports: list[PortSupervisionSetting]


class GetSupervisedRangesRequest(Model):
    ports: list[PortQuery]


class GetSupportedStatesRequest(Model):
    ports: list[PortQuery]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/supervisedio.cgi"

INFO = ApiInfo(
    id="supervised-io",
    name="Supervised I/O",
    family=Family.JSONRPC,
    major=2,
    known_versions=(ApiVersion(2, 0),),
    discovery=(
        ApiDiscovery("supervised-io"),
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.SupervisedIO.SupervisedIO", "yes"),
        ParamDiscovery("Properties.SupervisedIO.Version", "2.00"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/supervised-io/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("Unsupported API version", "unsupported"),
        2101: ErrorCode("JSON input error", "invalid_argument"),
        2102: ErrorCode("Invalid method", "unsupported"),
        2103: ErrorCode("Mandatory parameter(s) missing", "invalid_argument"),
        2200: ErrorCode("Unknown parameter supplied", "invalid_argument"),
        2201: ErrorCode("Unexpected error", "internal"),
        2202: ErrorCode("Generic error", "internal"),
        2203: ErrorCode("Faulty parameter value", "invalid_argument"),
        2204: ErrorCode("Invalid range", "invalid_argument"),
        2205: ErrorCode("Invalid port parameter", "invalid_argument"),
        2206: ErrorCode("Port not supervisable", "unsupported"),
    },
)


class OPS:
    get_number_of_ports = Operation(
        INFO,
        "get_number_of_ports",
        JsonRpcBinding("getNumberOfPorts", PATH),
        result=NumberOfPorts,
        access="operator",
        effect="read",
    )
    is_supervisable = Operation(
        INFO,
        "is_supervisable",
        JsonRpcBinding("isSupervisable", PATH, params_field="ports"),
        params=IsSupervisableRequest,
        result=SupervisableResult,
        access="operator",
        effect="read",
    )
    get_supervised = Operation(
        INFO,
        "get_supervised",
        JsonRpcBinding("getSupervised", PATH, params_field="ports"),
        params=GetSupervisedRequest,
        result=SupervisedResult,
        access="operator",
        effect="read",
    )
    set_supervised = Operation(
        INFO,
        "set_supervised",
        JsonRpcBinding("setSupervised", PATH, params_field="ports"),
        params=SetSupervisedRequest,
        result=SetSupervisedResult,
        access="operator",
        effect="write",
        write="patch",
    )
    get_supervised_ranges = Operation(
        INFO,
        "get_supervised_ranges",
        JsonRpcBinding("getSupervisedRanges", PATH, params_field="ports"),
        params=GetSupervisedRangesRequest,
        result=SupervisedRangesResult,
        access="operator",
        effect="read",
    )
    get_supported_states = Operation(
        INFO,
        "get_supported_states",
        JsonRpcBinding("getSupportedStates", PATH, params_field="ports"),
        params=GetSupportedStatesRequest,
        result=SupportedStatesResult,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class SupervisedIoApi(SyncApi):
    """Supervised I/O (``supervised-io``, version 2)."""

    INFO = INFO

    def get_number_of_ports(self, *, request_options: RequestOptions | None = None) -> NumberOfPorts:
        """Return the number of input and output ports. Access: operator."""
        return self._run(OPS.get_number_of_ports, None, {}, request_options)

    def is_supervisable(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupervisableResult:
        """Check which I/O ports can be set to supervised.

        Without port queries, only supervisable ports are returned.

        Access: operator.
        """
        return self._run(OPS.is_supervisable, None, {"ports": ports}, request_options)

    def get_supervised(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupervisedResult:
        """Check if I/O ports are supervised, with their current state and analog level.

        Without port queries, information about all supervised ports is returned.

        Access: operator.
        """
        return self._run(OPS.get_supervised, None, {"ports": ports}, request_options)

    def set_supervised(
        self, ports: list[PortSupervisionSetting], *, request_options: RequestOptions | None = None
    ) -> SetSupervisedResult:
        """Enable or disable supervision of I/O ports, or configure the ranges of supervised ports.

        Each port is reported separately in the result; a ``code`` of 1 means success.

        Changes only the fields given. Access: operator.
        """
        return self._run(OPS.set_supervised, None, {"ports": ports}, request_options)

    def get_supervised_ranges(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupervisedRangesResult:
        """Get the ranges that correspond to the states of each port.

        Without port queries, information about all ports is returned.

        Access: operator.
        """
        return self._run(OPS.get_supervised_ranges, None, {"ports": ports}, request_options)

    def get_supported_states(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupportedStatesResult:
        """Retrieve the states supported by each port.

        Without port queries, information about all ports is returned.

        Access: operator.
        """
        return self._run(OPS.get_supported_states, None, {"ports": ports}, request_options)


class AsyncSupervisedIoApi(AsyncApi):
    """Supervised I/O (``supervised-io``, version 2)."""

    INFO = INFO

    async def get_number_of_ports(self, *, request_options: RequestOptions | None = None) -> NumberOfPorts:
        """Return the number of input and output ports. Access: operator."""
        return await self._run(OPS.get_number_of_ports, None, {}, request_options)

    async def is_supervisable(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupervisableResult:
        """Check which I/O ports can be set to supervised.

        Without port queries, only supervisable ports are returned.

        Access: operator.
        """
        return await self._run(OPS.is_supervisable, None, {"ports": ports}, request_options)

    async def get_supervised(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupervisedResult:
        """Check if I/O ports are supervised, with their current state and analog level.

        Without port queries, information about all supervised ports is returned.

        Access: operator.
        """
        return await self._run(OPS.get_supervised, None, {"ports": ports}, request_options)

    async def set_supervised(
        self, ports: list[PortSupervisionSetting], *, request_options: RequestOptions | None = None
    ) -> SetSupervisedResult:
        """Enable or disable supervision of I/O ports, or configure the ranges of supervised ports.

        Each port is reported separately in the result; a ``code`` of 1 means success.

        Changes only the fields given. Access: operator.
        """
        return await self._run(OPS.set_supervised, None, {"ports": ports}, request_options)

    async def get_supervised_ranges(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupervisedRangesResult:
        """Get the ranges that correspond to the states of each port.

        Without port queries, information about all ports is returned.

        Access: operator.
        """
        return await self._run(OPS.get_supervised_ranges, None, {"ports": ports}, request_options)

    async def get_supported_states(
        self, ports: list[PortQuery], *, request_options: RequestOptions | None = None
    ) -> SupportedStatesResult:
        """Retrieve the states supported by each port.

        Without port queries, information about all ports is returned.

        Access: operator.
        """
        return await self._run(OPS.get_supported_states, None, {"ports": ports}, request_options)
