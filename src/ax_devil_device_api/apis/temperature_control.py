# GENERATED from specs/apis/network-video/temperaturecontrol.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Monitor temperature sensors and control heaters and fans with ``temperaturecontrol.cgi``; read and set the ``TemperatureControl.*`` parameters with ``param.cgi``.

Docs: https://developer.axis.com/vapix/network-video/temperature-control/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

TemperatureDevice = Literal["heater", "fan", "sensor"]
ControllableDevice = Literal["heater", "fan"]
TemperatureUnit = Literal["celsius", "fahrenheit"]


class DeviceRequest(Model):
    device: TemperatureDevice
    id: int = Field(ge=0)
    """The index number of the temperature device."""


class QueryRequest(Model):
    device: TemperatureDevice
    id: int = Field(ge=0)
    """The index number of the temperature device."""
    temperatureunit: TemperatureUnit | None = None


class SetUserControlModeRequest(Model):
    device: ControllableDevice
    id: int = Field(ge=0)
    """The index number of the heater or fan."""
    usercontrolmode: bool
    """Enable (true) or disable (false) manual control. Reset to false on reboot."""
    intensity: int | None = Field(default=None, ge=0, le=100)
    """The intensity of the heater or fan in percent."""


class SetParametersRequest(Model):
    parameters: dict[str, str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/temperaturecontrol.cgi"

INFO = ApiInfo(
    id="temperaturecontrol",
    name="Temperature control",
    family=Family.CGI,
    discovery=(
        ApiDiscovery("temperaturecontrol"),
        ParamDiscovery("Properties.TemperatureSensor.TemperatureControl", "yes"),
        ParamDiscovery("Properties.TemperatureSensor.Fan"),
        ParamDiscovery("Properties.TemperatureSensor.Heater"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/temperature-control/",),
)


class OPS:
    start = Operation(
        INFO,
        "start",
        CgiBinding(PATH, fixed_query=(("action", "start"),), args=(CgiArg("device"), CgiArg("id")), reply=TextOk()),
        params=DeviceRequest,
        access="operator",
        effect="action",
    )
    stop = Operation(
        INFO,
        "stop",
        CgiBinding(PATH, fixed_query=(("action", "stop"),), args=(CgiArg("device"), CgiArg("id")), reply=TextOk()),
        params=DeviceRequest,
        access="operator",
        effect="action",
    )
    query = Operation(
        INFO,
        "query",
        CgiBinding(
            PATH,
            fixed_query=(("action", "query"),),
            args=(CgiArg("device"), CgiArg("id"), CgiArg("temperatureunit")),
            reply=Text(),
        ),
        params=QueryRequest,
        result=str,
        access="operator",
        effect="read",
    )
    time_until_stop = Operation(
        INFO,
        "time_until_stop",
        CgiBinding(
            PATH, fixed_query=(("action", "timeuntilstop"),), args=(CgiArg("device"), CgiArg("id")), reply=Text()
        ),
        params=DeviceRequest,
        result=str,
        access="operator",
        effect="read",
    )
    status_all = Operation(
        INFO,
        "status_all",
        CgiBinding(PATH, fixed_query=(("action", "statusall"),), reply=TextKv()),
        result=dict[str, str],
        access="operator",
        effect="read",
    )
    set_user_control_mode = Operation(
        INFO,
        "set_user_control_mode",
        CgiBinding(
            PATH, args=(CgiArg("device"), CgiArg("id"), CgiArg("usercontrolmode"), CgiArg("intensity")), reply=TextOk()
        ),
        params=SetUserControlModeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_parameters = Operation(
        INFO,
        "get_parameters",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "list"), ("group", "TemperatureControl")),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    set_parameters = Operation(
        INFO,
        "set_parameters",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "update"),),
            args=(CgiArg("parameters", style="spread"),),
            reply=TextOk(),
        ),
        params=SetParametersRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class TemperatureControlApi(SyncApi):
    """Temperature control (``temperaturecontrol``)."""

    INFO = INFO

    def start(self, device: TemperatureDevice, id: int, *, request_options: RequestOptions | None = None) -> None:
        """Manually start a heater or fan for the duration set in its ``ManualControlDuration`` parameter.

        Which devices exist and can be controlled depends on the product hardware.

        Access: operator.
        """
        self._run(OPS.start, None, {"device": device, "id": id}, request_options)

    def stop(self, device: TemperatureDevice, id: int, *, request_options: RequestOptions | None = None) -> None:
        """Manually stop a heater or fan. Any duration left is reset. Access: operator."""
        self._run(OPS.stop, None, {"device": device, "id": id}, request_options)

    def query(
        self,
        device: TemperatureDevice,
        id: int,
        *,
        temperatureunit: TemperatureUnit | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Read a heater or fan status, or the temperature of a sensor, as text.

        A sensor returns the temperature as a number (``46.71``), a heater or fan returns its status:
        ``Running``, ``Running[XX]`` (XX is the intensity, for example ``Running[100%]``), ``Stopped``,
        ``Heater Failure`` or ``Fan Failure``.

        Access: operator.
        """
        return self._run(
            OPS.query, None, {"device": device, "id": id, "temperatureunit": temperatureunit}, request_options
        )

    def time_until_stop(
        self, device: TemperatureDevice, id: int, *, request_options: RequestOptions | None = None
    ) -> str:
        """Read the number of seconds left until a heater or fan stops following a manual start.

        Access: operator.
        """
        return self._run(OPS.time_until_stop, None, {"device": device, "id": id}, request_options)

    def status_all(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the status of all sensors, heaters and fans as ``{"Sensor.S0.Celsius": "43.50", "Heater.H0.Status": "Stopped"}``.

        Entries are ``Sensor.S#.Name``, ``Sensor.S#.Celsius``, ``Sensor.S#.Fahrenheit``,
        ``Heater.H#.Status``, ``Heater.H#.TimeUntilStop``, ``Fan.F#.Status`` and ``Fan.F#.TimeUntilStop``.
        This is the one action that does not depend on the hardware.

        Access: operator.
        """
        return self._run(OPS.status_all, None, {}, request_options)

    def set_user_control_mode(
        self,
        *,
        device: ControllableDevice,
        id: int,
        usercontrolmode: bool,
        intensity: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Enable or disable manual (user) control of a heater or fan, and optionally set its intensity.

        The control is reset to false whenever the device is rebooted. Dependent on the device and
        heater/fan capabilities; products where ``UserControlSupport`` is ``no`` reply with an error.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_user_control_mode,
            None,
            {"device": device, "id": id, "usercontrolmode": usercontrolmode, "intensity": intensity},
            request_options,
        )

    def get_parameters(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the ``TemperatureControl.*`` parameters (trigger levels, control policy, manual duration) as ``{"TemperatureControl.Sensor.S0.TriggerHigh": "60"}``.

        Access: viewer.
        """
        return self._run(OPS.get_parameters, None, {}, request_options)

    def set_parameters(self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None) -> None:
        """Set ``TemperatureControl.*`` parameters, e.g. ``{"TemperatureControl.Sensor.S2.TriggerLow": "-10"}``.

        Keys are ``TemperatureControl.Sensor.S#.Name``, ``.TriggerLow`` and ``.TriggerHigh`` (the limits of
        the ``Temperature`` below and above events; an integer in Celsius, or with an ``F`` suffix for
        Fahrenheit, such as ``30F``), and ``TemperatureControl.Heater.H#`` or ``TemperatureControl.Fan.F#``
        with ``.ManualControlDuration`` (seconds), ``.ControlPolicyLimit`` and ``.ControlPolicyDelta``.
        ``#`` runs from 0 to the number of devices minus 1. ``UserControlSupport`` is read-only, and the
        heater and fan parameters cannot be updated when it is ``no``. Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_parameters, None, {"parameters": dict(parameters)}, request_options)


class AsyncTemperatureControlApi(AsyncApi):
    """Temperature control (``temperaturecontrol``)."""

    INFO = INFO

    async def start(self, device: TemperatureDevice, id: int, *, request_options: RequestOptions | None = None) -> None:
        """Manually start a heater or fan for the duration set in its ``ManualControlDuration`` parameter.

        Which devices exist and can be controlled depends on the product hardware.

        Access: operator.
        """
        await self._run(OPS.start, None, {"device": device, "id": id}, request_options)

    async def stop(self, device: TemperatureDevice, id: int, *, request_options: RequestOptions | None = None) -> None:
        """Manually stop a heater or fan. Any duration left is reset. Access: operator."""
        await self._run(OPS.stop, None, {"device": device, "id": id}, request_options)

    async def query(
        self,
        device: TemperatureDevice,
        id: int,
        *,
        temperatureunit: TemperatureUnit | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Read a heater or fan status, or the temperature of a sensor, as text.

        A sensor returns the temperature as a number (``46.71``), a heater or fan returns its status:
        ``Running``, ``Running[XX]`` (XX is the intensity, for example ``Running[100%]``), ``Stopped``,
        ``Heater Failure`` or ``Fan Failure``.

        Access: operator.
        """
        return await self._run(
            OPS.query, None, {"device": device, "id": id, "temperatureunit": temperatureunit}, request_options
        )

    async def time_until_stop(
        self, device: TemperatureDevice, id: int, *, request_options: RequestOptions | None = None
    ) -> str:
        """Read the number of seconds left until a heater or fan stops following a manual start.

        Access: operator.
        """
        return await self._run(OPS.time_until_stop, None, {"device": device, "id": id}, request_options)

    async def status_all(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the status of all sensors, heaters and fans as ``{"Sensor.S0.Celsius": "43.50", "Heater.H0.Status": "Stopped"}``.

        Entries are ``Sensor.S#.Name``, ``Sensor.S#.Celsius``, ``Sensor.S#.Fahrenheit``,
        ``Heater.H#.Status``, ``Heater.H#.TimeUntilStop``, ``Fan.F#.Status`` and ``Fan.F#.TimeUntilStop``.
        This is the one action that does not depend on the hardware.

        Access: operator.
        """
        return await self._run(OPS.status_all, None, {}, request_options)

    async def set_user_control_mode(
        self,
        *,
        device: ControllableDevice,
        id: int,
        usercontrolmode: bool,
        intensity: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Enable or disable manual (user) control of a heater or fan, and optionally set its intensity.

        The control is reset to false whenever the device is rebooted. Dependent on the device and
        heater/fan capabilities; products where ``UserControlSupport`` is ``no`` reply with an error.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_user_control_mode,
            None,
            {"device": device, "id": id, "usercontrolmode": usercontrolmode, "intensity": intensity},
            request_options,
        )

    async def get_parameters(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the ``TemperatureControl.*`` parameters (trigger levels, control policy, manual duration) as ``{"TemperatureControl.Sensor.S0.TriggerHigh": "60"}``.

        Access: viewer.
        """
        return await self._run(OPS.get_parameters, None, {}, request_options)

    async def set_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set ``TemperatureControl.*`` parameters, e.g. ``{"TemperatureControl.Sensor.S2.TriggerLow": "-10"}``.

        Keys are ``TemperatureControl.Sensor.S#.Name``, ``.TriggerLow`` and ``.TriggerHigh`` (the limits of
        the ``Temperature`` below and above events; an integer in Celsius, or with an ``F`` suffix for
        Fahrenheit, such as ``30F``), and ``TemperatureControl.Heater.H#`` or ``TemperatureControl.Fan.F#``
        with ``.ManualControlDuration`` (seconds), ``.ControlPolicyLimit`` and ``.ControlPolicyDelta``.
        ``#`` runs from 0 to the number of devices minus 1. ``UserControlSupport`` is read-only, and the
        heater and fan parameters cannot be updated when it is ``no``. Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_parameters, None, {"parameters": dict(parameters)}, request_options)
