# GENERATED from specs/apis/network-video/on-screen-directional-indicator.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Name PTZ zones (pan/tilt/zoom ranges) through the ``PTZ.Locator`` parameters so the zone name can be shown in the text overlay.

Docs: https://developer.axis.com/vapix/network-video/on-screen-directional-indicator/
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListParametersRequest(Model):
    group: list[str] = Field(min_length=1)
    """Parameter groups to list, e.g. ``root.PTZ.Locator.L0.MaxZones`` or ``root.PTZ.Locator.L0.Zone``."""


class AddZoneRequest(Model):
    group: str
    """Zone group to add to, e.g. ``root.PTZ.Locator.L0.Zone``."""
    parameters: dict[str, str]
    """Initial values as full parameter names mapped to values."""


class UpdateZonesRequest(Model):
    parameters: dict[str, str]


class RemoveZoneRequest(Model):
    group: str
    """Zone group, e.g. ``root.PTZ.Locator.L0.Zone.Z1``."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="on-screen-directional-indicator",
    name="On-screen directional indicator",
    family=Family.CGI,
    discovery=(ParamDiscovery("PTZ.Locator.L0.MaxZones", "1", ">="),),
    docs=("https://developer.axis.com/vapix/network-video/on-screen-directional-indicator/",),
)


class OPS:
    list_parameters = Operation(
        INFO,
        "list_parameters",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListParametersRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    add_zone = Operation(
        INFO,
        "add_zone",
        CgiBinding(
            PATH,
            fixed_query=(("action", "add"), ("template", "ptzlocator")),
            args=(CgiArg("group"), CgiArg("parameters", style="spread")),
            reply=Text(),
        ),
        params=AddZoneRequest,
        result=str,
        access="operator",
        effect="write",
        write="create",
    )
    update_zones = Operation(
        INFO,
        "update_zones",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=UpdateZonesRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    remove_zone = Operation(
        INFO,
        "remove_zone",
        CgiBinding(PATH, fixed_query=(("action", "remove"),), args=(CgiArg("group"),), reply=TextOk()),
        params=RemoveZoneRequest,
        access="operator",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class OnScreenDirectionalIndicatorApi(SyncApi):
    """On-screen directional indicator (``on-screen-directional-indicator``)."""

    INFO = INFO

    def list_parameters(self, group: list[str], *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Parameter values as ``{"PTZ.Locator.L0.MaxZones": "..."}`` (``root.`` removed).

        List ``PTZ.Locator.L<n>.MaxZones`` (read-only: the maximum number of ``Zone.Z<m>`` groups for image
        source ``n``) or the zones with ``PTZ.Locator.L<n>.Zone``. If ``MaxZones`` is present and greater
        than 0, the device supports OSDI.

        Access: viewer.
        """
        return self._run(OPS.list_parameters, None, {"group": group}, request_options)

    def add_zone(
        self, group: str, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> str:
        """Create an OSDI zone parameter group.

        ``group`` is ``root.PTZ.Locator.L<n>.Zone``. Pass the new zone's values as full parameter names with
        a bare ``Z`` for the new group, e.g. ``{"root.PTZ.Locator.L0.Zone.Z.Name": "NewZone",
        "root.PTZ.Locator.L0.Zone.Z.Pan": "0.06:29.54", "root.PTZ.Locator.L0.Zone.Z.Tilt": "-44.99:-30.06",
        "root.PTZ.Locator.L0.Zone.Z.Enabled": "yes"}``. Pan and tilt are ``<float>:<float>`` in degrees;
        zoom is ``<unsigned integer>:<unsigned integer>`` and, when unset, the zoom level is not considered.
        The device replies with the reply of the underlying ``param.cgi`` add action.

        Access: operator.
        """
        return self._run(OPS.add_zone, None, {"group": group, "parameters": dict(parameters)}, request_options)

    def update_zones(self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None) -> None:
        """Update parameters of existing zones, e.g. ``{"PTZ.Locator.L0.Zone.Z0.Enabled": "no"}``.

        Per zone: ``Enabled`` (``yes``/``no``), ``Name``, ``Pan`` and ``Tilt`` (``<float>:<float>`` degrees)
        and ``Zoom`` (``<unsigned integer>:<unsigned integer>``). Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_zones, None, {"parameters": dict(parameters)}, request_options)

    def remove_zone(self, group: str, *, request_options: RequestOptions | None = None) -> None:
        """Delete a zone parameter group, which removes the zone. Access: operator."""
        self._run(OPS.remove_zone, None, {"group": group}, request_options)


class AsyncOnScreenDirectionalIndicatorApi(AsyncApi):
    """On-screen directional indicator (``on-screen-directional-indicator``)."""

    INFO = INFO

    async def list_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Parameter values as ``{"PTZ.Locator.L0.MaxZones": "..."}`` (``root.`` removed).

        List ``PTZ.Locator.L<n>.MaxZones`` (read-only: the maximum number of ``Zone.Z<m>`` groups for image
        source ``n``) or the zones with ``PTZ.Locator.L<n>.Zone``. If ``MaxZones`` is present and greater
        than 0, the device supports OSDI.

        Access: viewer.
        """
        return await self._run(OPS.list_parameters, None, {"group": group}, request_options)

    async def add_zone(
        self, group: str, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> str:
        """Create an OSDI zone parameter group.

        ``group`` is ``root.PTZ.Locator.L<n>.Zone``. Pass the new zone's values as full parameter names with
        a bare ``Z`` for the new group, e.g. ``{"root.PTZ.Locator.L0.Zone.Z.Name": "NewZone",
        "root.PTZ.Locator.L0.Zone.Z.Pan": "0.06:29.54", "root.PTZ.Locator.L0.Zone.Z.Tilt": "-44.99:-30.06",
        "root.PTZ.Locator.L0.Zone.Z.Enabled": "yes"}``. Pan and tilt are ``<float>:<float>`` in degrees;
        zoom is ``<unsigned integer>:<unsigned integer>`` and, when unset, the zoom level is not considered.
        The device replies with the reply of the underlying ``param.cgi`` add action.

        Access: operator.
        """
        return await self._run(OPS.add_zone, None, {"group": group, "parameters": dict(parameters)}, request_options)

    async def update_zones(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Update parameters of existing zones, e.g. ``{"PTZ.Locator.L0.Zone.Z0.Enabled": "no"}``.

        Per zone: ``Enabled`` (``yes``/``no``), ``Name``, ``Pan`` and ``Tilt`` (``<float>:<float>`` degrees)
        and ``Zoom`` (``<unsigned integer>:<unsigned integer>``). Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_zones, None, {"parameters": dict(parameters)}, request_options)

    async def remove_zone(self, group: str, *, request_options: RequestOptions | None = None) -> None:
        """Delete a zone parameter group, which removes the zone. Access: operator."""
        await self._run(OPS.remove_zone, None, {"group": group}, request_options)
