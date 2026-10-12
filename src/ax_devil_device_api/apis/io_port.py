# GENERATED from specs/apis/network-video/io-port-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Query and activate the digital input and output ports with ``port.cgi`` and configure them with the ``IOPort.I#`` parameters.

Docs: https://developer.axis.com/vapix/network-video/input-and-outputs/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

PortIds = Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]


class CheckPortsRequest(Model):
    check: PortIds


class CheckPortsActiveRequest(Model):
    checkactive: PortIds


class CheckPortsDirectionRequest(Model):
    checkdirection: PortIds


class RunOutputActionRequest(Model):
    action: str = Field(pattern=r"^[0-9]*:[/\\]([0-9]+[/\\])*$")
    """The action string."""


class ListPortParametersRequest(Model):
    group: list[str] = Field(min_length=1)
    """Parameter groups to list, e.g. ``IOPort.I0`` or ``Input.NbrOfInputs``."""


class UpdatePortParametersRequest(Model):
    parameters: dict[str, str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/io/port.cgi"

INFO = ApiInfo(
    id="io-port-api",
    name="I/O port API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    docs=("https://developer.axis.com/vapix/network-video/input-and-outputs/",),
)


class OPS:
    check_ports = Operation(
        INFO,
        "check_ports",
        CgiBinding(PATH, args=(CgiArg("check", style="csv"),), reply=TextKv(), accept="text/plain"),
        params=CheckPortsRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    check_ports_active = Operation(
        INFO,
        "check_ports_active",
        CgiBinding(PATH, args=(CgiArg("checkactive", style="csv"),), reply=TextKv(), accept="text/plain"),
        params=CheckPortsActiveRequest,
        result=dict[str, Literal["active", "inactive"]],
        access="viewer",
        effect="read",
    )
    check_ports_direction = Operation(
        INFO,
        "check_ports_direction",
        CgiBinding(PATH, args=(CgiArg("checkdirection", style="csv"),), reply=TextKv(), accept="text/plain"),
        params=CheckPortsDirectionRequest,
        result=dict[str, Literal["input", "output"]],
        access="viewer",
        effect="read",
    )
    run_output_action = Operation(
        INFO,
        "run_output_action",
        CgiBinding(PATH, args=(CgiArg("action"),), reply=Text()),
        params=RunOutputActionRequest,
        access="viewer",
        effect="action",
    )
    list_port_parameters = Operation(
        INFO,
        "list_port_parameters",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListPortParametersRequest,
        result=dict[str, str],
        access="operator",
        effect="read",
    )
    update_port_parameters = Operation(
        INFO,
        "update_port_parameters",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "update"),),
            args=(CgiArg("parameters", style="spread"),),
            reply=TextOk(),
        ),
        params=UpdatePortParametersRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class IoPortApi(SyncApi):
    """I/O port API (``io-port-api``)."""

    INFO = INFO

    def check_ports(self, check: PortIds, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Circuit state of ports as ``{"port1": "0"}``: 1 closed circuit, 0 open circuit.

        Access: viewer.
        """
        return self._run(OPS.check_ports, None, {"check": check}, request_options)

    def check_ports_active(
        self, checkactive: PortIds, *, request_options: RequestOptions | None = None
    ) -> dict[str, Literal["active", "inactive"]]:
        """Whether ports are active as ``{"port3": "inactive"}``.

        Depends on ``Output.Active`` for an output and ``Input.Trig`` for an input: an output with
        ``Output.Active`` closed is active when its circuit is closed, and likewise for an input with
        ``Input.Trig`` closed.

        Access: viewer.
        """
        return self._run(OPS.check_ports_active, None, {"checkactive": checkactive}, request_options)

    def check_ports_direction(
        self, checkdirection: PortIds, *, request_options: RequestOptions | None = None
    ) -> dict[str, Literal["input", "output"]]:
        """Direction of ports as ``{"port1": "input"}``. Access: viewer."""
        return self._run(OPS.check_ports_direction, None, {"checkdirection": checkdirection}, request_options)

    def run_output_action(self, action: str, *, request_options: RequestOptions | None = None) -> None:
        """Activate or deactivate an output port, optionally as timed pulses.

        ``action`` is ``[<port>]:<a>[<wait><a>...]``: ``<port>`` is the port number (output 1 when omitted),
        ``<a>`` is ``/`` for active or ``\\`` for inactive, and ``<wait>`` is a delay in milliseconds before
        the next action. For example ``2:/300\\`` sets port 2 active, waits 300 ms and sets it inactive;
        ``2:/300\\500/300\\`` makes two 300 ms pulses 500 ms apart. Valid for output ports only. The reply
        body is empty.

        Access: viewer.
        """
        self._run(OPS.run_output_action, None, {"action": action}, request_options)

    def list_port_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Port parameters as ``{"IOPort.I0.Direction": "output"}`` (``root.`` removed).

        Groups: ``IOPort.I#`` (``Configurable``, ``Direction``, ``Usage``, ``Input.Name``, ``Input.Trig``,
        ``Output.Name``, ``Output.Active``, ``Output.Button``, ``Output.PulseTime``, ``Output.DelayTime``,
        ``Output.Mode``), ``Input.NbrOfInputs`` and ``Output.NbrOfOutputs`` (readable by viewers). ``#``
        starts from 0.

        Access: operator.
        """
        return self._run(OPS.list_port_parameters, None, {"group": group}, request_options)

    def update_port_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set port parameters, e.g. ``{"IOPort.I2.Direction": "output"}``.

        Only the given parameters change. Writing needs administrator access. ``Direction`` and the names
        and ``Usage`` can only be written for configurable ports.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_port_parameters, None, {"parameters": dict(parameters)}, request_options)


class AsyncIoPortApi(AsyncApi):
    """I/O port API (``io-port-api``)."""

    INFO = INFO

    async def check_ports(self, check: PortIds, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Circuit state of ports as ``{"port1": "0"}``: 1 closed circuit, 0 open circuit.

        Access: viewer.
        """
        return await self._run(OPS.check_ports, None, {"check": check}, request_options)

    async def check_ports_active(
        self, checkactive: PortIds, *, request_options: RequestOptions | None = None
    ) -> dict[str, Literal["active", "inactive"]]:
        """Whether ports are active as ``{"port3": "inactive"}``.

        Depends on ``Output.Active`` for an output and ``Input.Trig`` for an input: an output with
        ``Output.Active`` closed is active when its circuit is closed, and likewise for an input with
        ``Input.Trig`` closed.

        Access: viewer.
        """
        return await self._run(OPS.check_ports_active, None, {"checkactive": checkactive}, request_options)

    async def check_ports_direction(
        self, checkdirection: PortIds, *, request_options: RequestOptions | None = None
    ) -> dict[str, Literal["input", "output"]]:
        """Direction of ports as ``{"port1": "input"}``. Access: viewer."""
        return await self._run(OPS.check_ports_direction, None, {"checkdirection": checkdirection}, request_options)

    async def run_output_action(self, action: str, *, request_options: RequestOptions | None = None) -> None:
        """Activate or deactivate an output port, optionally as timed pulses.

        ``action`` is ``[<port>]:<a>[<wait><a>...]``: ``<port>`` is the port number (output 1 when omitted),
        ``<a>`` is ``/`` for active or ``\\`` for inactive, and ``<wait>`` is a delay in milliseconds before
        the next action. For example ``2:/300\\`` sets port 2 active, waits 300 ms and sets it inactive;
        ``2:/300\\500/300\\`` makes two 300 ms pulses 500 ms apart. Valid for output ports only. The reply
        body is empty.

        Access: viewer.
        """
        await self._run(OPS.run_output_action, None, {"action": action}, request_options)

    async def list_port_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Port parameters as ``{"IOPort.I0.Direction": "output"}`` (``root.`` removed).

        Groups: ``IOPort.I#`` (``Configurable``, ``Direction``, ``Usage``, ``Input.Name``, ``Input.Trig``,
        ``Output.Name``, ``Output.Active``, ``Output.Button``, ``Output.PulseTime``, ``Output.DelayTime``,
        ``Output.Mode``), ``Input.NbrOfInputs`` and ``Output.NbrOfOutputs`` (readable by viewers). ``#``
        starts from 0.

        Access: operator.
        """
        return await self._run(OPS.list_port_parameters, None, {"group": group}, request_options)

    async def update_port_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set port parameters, e.g. ``{"IOPort.I2.Direction": "output"}``.

        Only the given parameters change. Writing needs administrator access. ``Direction`` and the names
        and ``Usage`` can only be written for configurable ports.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_port_parameters, None, {"parameters": dict(parameters)}, request_options)
