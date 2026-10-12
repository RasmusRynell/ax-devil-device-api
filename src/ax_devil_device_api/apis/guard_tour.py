# GENERATED from specs/apis/network-video/guard-tour.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Preset guard tours for PTZ cameras, defined in the dynamic GuardTour.G and GuardTour.G.Tour.T parameter groups through param.cgi.

Docs: https://developer.axis.com/vapix/network-video/guard-tour-api/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

GuardTourGroup = Annotated[str, Field(pattern=r"^GuardTour\.G[0-9]+\.Tour$")]


class ListParametersRequest(Model):
    group: str
    """Group or parameter path, wildcards allowed (e.g. GuardTour.G0.Tour.*.PresetNbr)."""


class AddGuardTourRequest(Model):
    name: str | None = Field(default=None, validation_alias="GuardTour.G.Name", serialization_alias="GuardTour.G.Name")
    """Name of the guard tour. It cannot contain the characters ", < or >."""
    cam_nbr: int | None = Field(
        default=None, validation_alias="GuardTour.G.CamNbr", serialization_alias="GuardTour.G.CamNbr"
    )
    """View area or video source the guard tour is defined for."""
    random_enabled: bool | None = Field(
        default=None, validation_alias="GuardTour.G.RandomEnabled", serialization_alias="GuardTour.G.RandomEnabled"
    )
    """Move between the preset positions in random order."""
    time_between_sequences: int | None = Field(
        default=None,
        validation_alias="GuardTour.G.TimeBetweenSequences",
        serialization_alias="GuardTour.G.TimeBetweenSequences",
        ge=0,
        le=9999,
    )
    """Minutes to wait between successive tours. The default is product-dependent."""
    running: bool | None = Field(
        default=None, validation_alias="GuardTour.G.Running", serialization_alias="GuardTour.G.Running"
    )
    """Start the guard tour straight away."""


class AddTourPresetRequest(Model):
    group: GuardTourGroup
    parameters: dict[str, str]


class UpdateParametersRequest(Model):
    parameters: dict[str, str]


class RemoveGroupRequest(Model):
    group: str = Field(pattern=r"^GuardTour\.G[0-9]+(\.Tour\.T[0-9]+)?$")
    """The group to remove, for example GuardTour.G0 or GuardTour.G0.Tour.T0."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="guard-tour",
    name="Guard tour API (preset tours)",
    family=Family.CGI,
    discovery=(ApiDiscovery("guard-tour"), ParamDiscovery("Properties.GuardTour.GuardTour", "yes")),
    docs=("https://developer.axis.com/vapix/network-video/guard-tour-api/",),
)


class OPS:
    get_properties = Operation(
        INFO,
        "get_properties",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "Properties.GuardTour")),
            reply=TextKv(strip_prefix="root."),
        ),
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    list_parameters = Operation(
        INFO,
        "list_parameters",
        CgiBinding(
            PATH, fixed_query=(("action", "list"),), args=(CgiArg("group"),), reply=TextKv(strip_prefix="root.")
        ),
        params=ListParametersRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    add_guard_tour = Operation(
        INFO,
        "add_guard_tour",
        CgiBinding(
            PATH,
            fixed_query=(("action", "add"), ("group", "GuardTour"), ("template", "guardtour")),
            args=(
                CgiArg("name", wire="GuardTour.G.Name"),
                CgiArg("cam_nbr", wire="GuardTour.G.CamNbr"),
                CgiArg("random_enabled", wire="GuardTour.G.RandomEnabled", style="axis_bool"),
                CgiArg("time_between_sequences", wire="GuardTour.G.TimeBetweenSequences"),
                CgiArg("running", wire="GuardTour.G.Running", style="axis_bool"),
            ),
            reply=Text(),
        ),
        params=AddGuardTourRequest,
        result=str,
        access="operator",
        effect="write",
        write="create",
    )
    add_tour_preset = Operation(
        INFO,
        "add_tour_preset",
        CgiBinding(
            PATH,
            fixed_query=(("action", "add"), ("template", "tour")),
            args=(CgiArg("group"), CgiArg("parameters", style="spread")),
            reply=Text(),
        ),
        params=AddTourPresetRequest,
        result=str,
        access="operator",
        effect="write",
        write="create",
    )
    update_parameters = Operation(
        INFO,
        "update_parameters",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=UpdateParametersRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    remove_group = Operation(
        INFO,
        "remove_group",
        CgiBinding(PATH, fixed_query=(("action", "remove"),), args=(CgiArg("group"),), reply=TextOk()),
        params=RemoveGroupRequest,
        access="operator",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class GuardTourApi(SyncApi):
    """Guard tour API (preset tours) (``guard-tour``)."""

    INFO = INFO

    def get_properties(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Guard tour support and limits as ``{"Properties.GuardTour.GuardTour": "yes"}`` (``root.`` removed).

        Properties.GuardTour.GuardTour is yes or no. When it is yes, MaxGuardTour (most tours),
        MinGuardTourWaitTime (shortest preset wait time) and GuardTourChannels (channels with guard tour
        capability, comma separated) are also present.

        Access: viewer.
        """
        return self._run(OPS.get_properties, None, {}, request_options)

    def list_parameters(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List guard tour parameters as ``{"GuardTour.G0.Name": "value"}`` (``root.`` removed).

        ``group`` is a group or parameter path and may use ``*`` wildcards, for example ``GuardTour.G0``,
        ``GuardTour.G0.Tour.T0`` or ``GuardTour.G0.Tour.*.PresetNbr``. A tour (GuardTour.G#) has Running,
        Name, CamNbr, RandomEnabled and TimeBetweenSequences. A preset (GuardTour.G#.Tour.T#) has PresetNbr,
        Position, MoveSpeed, WaitTime and WaitTimeViewType.

        Access: viewer.
        """
        return self._run(OPS.list_parameters, None, {"group": group}, request_options)

    @overload
    def add_guard_tour(
        self, request: AddGuardTourRequest, /, *, request_options: RequestOptions | None = None
    ) -> str: ...
    @overload
    def add_guard_tour(
        self,
        /,
        *,
        name: str | MISSING = MISSING,
        cam_nbr: int | MISSING = MISSING,
        random_enabled: bool | MISSING = MISSING,
        time_between_sequences: int | MISSING = MISSING,
        running: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    def add_guard_tour(
        self,
        request: AddGuardTourRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> str:
        """Add a guard tour (group GuardTour.G#); returns the device reply (``"G0 OK"``).

        The device assigns the group number and returns it in the reply. All settings are optional; the
        defaults are Running=no, Name=GuardTourName, CamNbr=1, RandomEnabled=no. At most
        Properties.GuardTour.MaxGuardTour tours can exist (group range 0 to 9).

        Access: operator.
        """
        return self._run(OPS.add_guard_tour, request, kwargs, request_options)

    def add_tour_preset(
        self, group: GuardTourGroup, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> str:
        """Add a preset position to a guard tour (group GuardTour.G#.Tour.T#); returns the device reply (``"T0 OK"``).

        ``group`` is the Tour group of the guard tour, for example ``GuardTour.G0.Tour``. ``parameters``
        holds the preset settings with the preset number omitted from the key, for example
        ``{"GuardTour.G0.Tour.T.PresetNbr": "1", "GuardTour.G0.Tour.T.Position": "1"}``. PresetNbr (1 to
        3600) is required and must be given explicitly. Position (1 to 3600, default 1) orders the presets
        of a non-random tour. MoveSpeed (1 to 100, default 70) applies to mechanical PTZ. WaitTime (0 to
        3600, default 10) is in the unit set by WaitTimeViewType (Seconds or Minutes, default Seconds). A
        preset that does not exist is ignored when the tour runs.

        Access: operator.
        """
        return self._run(OPS.add_tour_preset, None, {"group": group, "parameters": dict(parameters)}, request_options)

    def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set guard tour or preset parameters, for example ``{"GuardTour.G0.Name": "DayTour"}``.

        Only the given parameters change. Use it to rename or reconfigure a tour and to start or stop it
        with ``GuardTour.G#.Running`` set to ``yes`` or ``no``. For tours: Name, CamNbr, RandomEnabled,
        TimeBetweenSequences (0 to 9999 minutes) and Running. For presets: PresetNbr, Position, MoveSpeed,
        WaitTime and WaitTimeViewType.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)

    def remove_group(self, group: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a preset position (``GuardTour.G0.Tour.T0``) or a whole guard tour (``GuardTour.G0``).

        This only removes the preset from the guard tour. To remove the preset position from the product,
        use the PTZ configuration API.

        Access: operator.
        """
        self._run(OPS.remove_group, None, {"group": group}, request_options)


class AsyncGuardTourApi(AsyncApi):
    """Guard tour API (preset tours) (``guard-tour``)."""

    INFO = INFO

    async def get_properties(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Guard tour support and limits as ``{"Properties.GuardTour.GuardTour": "yes"}`` (``root.`` removed).

        Properties.GuardTour.GuardTour is yes or no. When it is yes, MaxGuardTour (most tours),
        MinGuardTourWaitTime (shortest preset wait time) and GuardTourChannels (channels with guard tour
        capability, comma separated) are also present.

        Access: viewer.
        """
        return await self._run(OPS.get_properties, None, {}, request_options)

    async def list_parameters(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List guard tour parameters as ``{"GuardTour.G0.Name": "value"}`` (``root.`` removed).

        ``group`` is a group or parameter path and may use ``*`` wildcards, for example ``GuardTour.G0``,
        ``GuardTour.G0.Tour.T0`` or ``GuardTour.G0.Tour.*.PresetNbr``. A tour (GuardTour.G#) has Running,
        Name, CamNbr, RandomEnabled and TimeBetweenSequences. A preset (GuardTour.G#.Tour.T#) has PresetNbr,
        Position, MoveSpeed, WaitTime and WaitTimeViewType.

        Access: viewer.
        """
        return await self._run(OPS.list_parameters, None, {"group": group}, request_options)

    @overload
    async def add_guard_tour(
        self, request: AddGuardTourRequest, /, *, request_options: RequestOptions | None = None
    ) -> str: ...
    @overload
    async def add_guard_tour(
        self,
        /,
        *,
        name: str | MISSING = MISSING,
        cam_nbr: int | MISSING = MISSING,
        random_enabled: bool | MISSING = MISSING,
        time_between_sequences: int | MISSING = MISSING,
        running: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    async def add_guard_tour(
        self,
        request: AddGuardTourRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> str:
        """Add a guard tour (group GuardTour.G#); returns the device reply (``"G0 OK"``).

        The device assigns the group number and returns it in the reply. All settings are optional; the
        defaults are Running=no, Name=GuardTourName, CamNbr=1, RandomEnabled=no. At most
        Properties.GuardTour.MaxGuardTour tours can exist (group range 0 to 9).

        Access: operator.
        """
        return await self._run(OPS.add_guard_tour, request, kwargs, request_options)

    async def add_tour_preset(
        self, group: GuardTourGroup, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> str:
        """Add a preset position to a guard tour (group GuardTour.G#.Tour.T#); returns the device reply (``"T0 OK"``).

        ``group`` is the Tour group of the guard tour, for example ``GuardTour.G0.Tour``. ``parameters``
        holds the preset settings with the preset number omitted from the key, for example
        ``{"GuardTour.G0.Tour.T.PresetNbr": "1", "GuardTour.G0.Tour.T.Position": "1"}``. PresetNbr (1 to
        3600) is required and must be given explicitly. Position (1 to 3600, default 1) orders the presets
        of a non-random tour. MoveSpeed (1 to 100, default 70) applies to mechanical PTZ. WaitTime (0 to
        3600, default 10) is in the unit set by WaitTimeViewType (Seconds or Minutes, default Seconds). A
        preset that does not exist is ignored when the tour runs.

        Access: operator.
        """
        return await self._run(
            OPS.add_tour_preset, None, {"group": group, "parameters": dict(parameters)}, request_options
        )

    async def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set guard tour or preset parameters, for example ``{"GuardTour.G0.Name": "DayTour"}``.

        Only the given parameters change. Use it to rename or reconfigure a tour and to start or stop it
        with ``GuardTour.G#.Running`` set to ``yes`` or ``no``. For tours: Name, CamNbr, RandomEnabled,
        TimeBetweenSequences (0 to 9999 minutes) and Running. For presets: PresetNbr, Position, MoveSpeed,
        WaitTime and WaitTimeViewType.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)

    async def remove_group(self, group: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a preset position (``GuardTour.G0.Tour.T0``) or a whole guard tour (``GuardTour.G0``).

        This only removes the preset from the guard tour. To remove the preset position from the product,
        use the PTZ configuration API.

        Access: operator.
        """
        await self._run(OPS.remove_group, None, {"group": group}, request_options)
