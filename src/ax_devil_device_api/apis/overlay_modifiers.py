# GENERATED from specs/apis/network-video/overlay-modifiers.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List the overlay modifiers (``%`` and ``#`` markup expanded in overlay text, file names and notifications) the device supports, grouped by function.

Docs: https://developer.axis.com/vapix/network-video/overlay-api/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, JsonReply
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Modifier(Model):
    mod: str
    """The modifier. It starts with ``%`` or ``#``, followed by one or two characters."""
    index: bool | None = None
    """True for modifiers that need an additional index to be complete, such as ``#U`` (fan) and ``#TC`` (temperature sensor in Celsius): fan 1 is ``#U1`` and sensor 2 in Celsius is ``#TC2``. Absent otherwise."""


class ModifiersData(Model):
    groups: dict[str, list[Modifier]]
    """Modifiers by group name: date, time, year, month, week, day, hour, minute, second, sysinfo, vidinfo, ptzinfo, eventinfo, sensor, zwave, mqtt, autotracking, others. Which groups exist depends on the device."""


class ModifiersResponse(Model):
    api_version: str = Field(validation_alias="apiVersion", serialization_alias="apiVersion")
    """The API version the data complies with."""
    context: int | None = None
    """The ``context`` of the request, or 0 when it was left out."""
    method: str | None = None
    """The requested method, ``getOverlayModifiers``."""
    data: ModifiersData


class GetOverlayModifiersRequest(Model):
    context: int | None = None
    """Integer user data echoed in the response, or returned as 0 when left out."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/overlaymodifiers.cgi"

INFO = ApiInfo(
    id="overlay-modifiers",
    name="Overlay modifiers",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.OverlayModifiers.OverlayModifiers", "yes"),),
    requires_firmware="5.1",
    docs=("https://developer.axis.com/vapix/network-video/overlay-api/",),
)


class OPS:
    get_overlay_modifiers = Operation(
        INFO,
        "get_overlay_modifiers",
        CgiBinding(PATH, args=(CgiArg("context"),), reply=JsonReply()),
        params=GetOverlayModifiersRequest,
        result=ModifiersResponse,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class OverlayModifiersApi(SyncApi):
    """Overlay modifiers (``overlay-modifiers``)."""

    INFO = INFO

    def get_overlay_modifiers(
        self, *, context: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> ModifiersResponse:
        """Retrieve the supported overlay modifiers grouped by function. Access: operator."""
        return self._run(OPS.get_overlay_modifiers, None, {"context": context}, request_options)


class AsyncOverlayModifiersApi(AsyncApi):
    """Overlay modifiers (``overlay-modifiers``)."""

    INFO = INFO

    async def get_overlay_modifiers(
        self, *, context: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> ModifiersResponse:
        """Retrieve the supported overlay modifiers grouped by function. Access: operator."""
        return await self._run(OPS.get_overlay_modifiers, None, {"context": context}, request_options)
