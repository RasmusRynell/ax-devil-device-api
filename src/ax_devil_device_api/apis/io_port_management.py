# GENERATED from specs/apis/network-video/io-port-management.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve I/O port information and capabilities, configure ports (name, usage, direction, normal state, output state) and run output state sequences.

Docs: https://developer.axis.com/vapix/network-video/io-port-management/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

PortState = Literal["open", "closed"]
PortDirection = Literal["input", "output"]


class Port(Model):
    """An I/O port with its capabilities and current configuration."""

    port: str
    """The port ID."""
    state: PortState | None = None
    """The current state of the port."""
    configurable: bool | None = None
    """Indicates if the port direction can be configured."""
    readonly: bool | None = None
    """Tells if the port is read-only and is only present if the value is true."""
    usage: str | None = None
    """Tells the intended usage of a port. In this case `usage` is treated as a nice name. Any underlying behavior will not be affected by its value."""
    direction: PortDirection | None = None
    """The direction of the port."""
    name: str | None = None
    """Specifies the nice name of the port."""
    normal_state: PortState | None = Field(
        default=None, validation_alias="normalState", serialization_alias="normalState"
    )
    """Specifies the normal state of the port."""


class PortList(Model):
    number_of_ports: int = Field(validation_alias="numberOfPorts", serialization_alias="numberOfPorts", ge=0, le=255)
    """The number of ports available on the device."""
    items: list[Port] | None = None
    """The ports. Omitted if numberOfPorts is zero."""


class PortConfig(Model):
    """Changes to apply to one port. If all optional fields are omitted nothing changes."""

    port: str
    """The port ID affected, as returned by ``get_ports``."""
    usage: str | None = None
    """The intended usage of the port, for example Button, Door, REX or Tampering. Treated as a nice name."""
    direction: PortDirection | None = None
    """The direction to apply. Read-only for non-configurable ports."""
    name: str | None = None
    """The nice name to use for the port."""
    normal_state: PortState | None = Field(
        default=None, validation_alias="normalState", serialization_alias="normalState"
    )
    """The normal state: ``open`` or ``closed`` circuit."""
    state: PortState | None = None
    """The current state of the port; output ports only."""


class SequenceStep(Model):
    state: PortState
    """The state that should be set."""
    time: int = Field(ge=0, le=65535)
    """The delay in milliseconds between state changes. The maximum is 65535 milliseconds."""


class SetPortsResult(Model):
    ports: list[str]
    """IDs of the affected ports."""


class SetStateSequenceResult(Model):
    port: str
    """The affected port ID."""


class SetPortsRequest(Model):
    ports: list[PortConfig] = Field(max_length=256)
    """List of port configurations. At most 256 ports per request."""


class SetStateSequenceRequest(Model):
    port: str
    """The affected output port ID, as returned by ``get_ports``."""
    sequence: list[SequenceStep]
    """The state changes to apply in order."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/io/portmanagement.cgi"

INFO = ApiInfo(
    id="io-port-management",
    name="I/O port management",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("io-port-management"),),
    docs=("https://developer.axis.com/vapix/network-video/io-port-management/",),
    errors={
        1100: ErrorCode("Internal error.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
    },
)


class OPS:
    get_ports = Operation(
        INFO, "get_ports", JsonRpcBinding("getPorts", PATH), result=PortList, access="viewer", effect="read"
    )
    set_ports = Operation(
        INFO,
        "set_ports",
        JsonRpcBinding("setPorts", PATH),
        params=SetPortsRequest,
        result=SetPortsResult,
        access="operator",
        effect="write",
        write="patch",
    )
    set_state_sequence = Operation(
        INFO,
        "set_state_sequence",
        JsonRpcBinding("setStateSequence", PATH),
        params=SetStateSequenceRequest,
        result=SetStateSequenceResult,
        access="viewer",
        effect="action",
        errors={2200: ErrorCode("State sequence already ongoing.", "unavailable")},
    )


# ---------------------------------------------------------------------------
# API classes


class IoPortManagementApi(SyncApi):
    """I/O port management (``io-port-management``, version 1)."""

    INFO = INFO

    def get_ports(self, *, request_options: RequestOptions | None = None) -> PortList:
        """Retrieve all ports and their capabilities. Access: viewer."""
        return self._run(OPS.get_ports, None, {}, request_options)

    @overload
    def set_ports(
        self, request: SetPortsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetPortsResult: ...
    @overload
    def set_ports(
        self, /, *, ports: list[PortConfig], request_options: RequestOptions | None = None
    ) -> SetPortsResult: ...
    def set_ports(
        self, request: SetPortsRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetPortsResult:
        """Configure one to several ports (nice name, usage, direction, normal state, output state).

        Changes only the fields given. Access: operator.
        """
        return self._run(OPS.set_ports, request, kwargs, request_options)

    @overload
    def set_state_sequence(
        self, request: SetStateSequenceRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetStateSequenceResult: ...
    @overload
    def set_state_sequence(
        self, /, *, port: str, sequence: list[SequenceStep], request_options: RequestOptions | None = None
    ) -> SetStateSequenceResult: ...
    def set_state_sequence(
        self,
        request: SetStateSequenceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetStateSequenceResult:
        """Apply a sequence of state changes with a delay in milliseconds between states (output ports only).

        The sequence runs once and returns immediately; the last state stays until a new sequence is
        launched. Starting a sequence while another runs fails with 2200. Changing direction or normalState
        cancels a running sequence.

        Access: viewer.
        """
        return self._run(OPS.set_state_sequence, request, kwargs, request_options)


class AsyncIoPortManagementApi(AsyncApi):
    """I/O port management (``io-port-management``, version 1)."""

    INFO = INFO

    async def get_ports(self, *, request_options: RequestOptions | None = None) -> PortList:
        """Retrieve all ports and their capabilities. Access: viewer."""
        return await self._run(OPS.get_ports, None, {}, request_options)

    @overload
    async def set_ports(
        self, request: SetPortsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetPortsResult: ...
    @overload
    async def set_ports(
        self, /, *, ports: list[PortConfig], request_options: RequestOptions | None = None
    ) -> SetPortsResult: ...
    async def set_ports(
        self, request: SetPortsRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetPortsResult:
        """Configure one to several ports (nice name, usage, direction, normal state, output state).

        Changes only the fields given. Access: operator.
        """
        return await self._run(OPS.set_ports, request, kwargs, request_options)

    @overload
    async def set_state_sequence(
        self, request: SetStateSequenceRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetStateSequenceResult: ...
    @overload
    async def set_state_sequence(
        self, /, *, port: str, sequence: list[SequenceStep], request_options: RequestOptions | None = None
    ) -> SetStateSequenceResult: ...
    async def set_state_sequence(
        self,
        request: SetStateSequenceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetStateSequenceResult:
        """Apply a sequence of state changes with a delay in milliseconds between states (output ports only).

        The sequence runs once and returns immediately; the last state stays until a new sequence is
        launched. Starting a sequence while another runs fails with 2200. Changing direction or normalState
        cancels a running sequence.

        Access: viewer.
        """
        return await self._run(OPS.set_state_sequence, request, kwargs, request_options)
