# GENERATED from specs/apis/network-video/speed-dry.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Shake a PTZ dome so water runs off and dries faster (one-shot speed dry); get speed dry capabilities.

Docs: https://developer.axis.com/vapix/network-video/pantiltzoom-api/
"""

from __future__ import annotations

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Operation, ParamDiscovery
from .._protocols.cgi import CgiBinding, Text, Xml
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/com/ptz.cgi"

INFO = ApiInfo(
    id="speed-dry",
    name="Speed dry API",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.SpeedDry.SpeedDry", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/pantiltzoom-api/",),
)


class OPS:
    speed_dry = Operation(
        INFO,
        "speed_dry",
        CgiBinding(PATH, fixed_query=(("auxiliary", "speeddry"),), reply=Xml()),
        access="viewer",
        effect="action",
    )
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        CgiBinding("/axis-cgi/speeddry/getcapabilities.cgi", reply=Text()),
        result=str,
        access="viewer",
        effect="read",
    )
    oneshot = Operation(
        INFO, "oneshot", CgiBinding("/axis-cgi/speeddry/oneshot.cgi", reply=Xml()), access="viewer", effect="action"
    )


# ---------------------------------------------------------------------------
# API classes


class SpeedDryApi(SyncApi):
    """Speed dry API (``speed-dry``)."""

    INFO = INFO

    def speed_dry(self, *, request_options: RequestOptions | None = None) -> None:
        """Execute a one-shot speed dry operation through ptz.cgi.

        After the operation has finished the device is idle for about 20 seconds, during which other speed
        dry requests are discarded. The reply carries no success or failure information.

        Access: viewer.
        """
        self._run(OPS.speed_dry, None, {}, request_options)

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the speed dry capabilities (one ``path type`` line per supported attribute).

        Access: viewer.
        """
        return self._run(OPS.get_capabilities, None, {}, request_options)

    def oneshot(self, *, request_options: RequestOptions | None = None) -> None:
        """Initiate a one-shot speed dry operation. Access: viewer."""
        self._run(OPS.oneshot, None, {}, request_options)


class AsyncSpeedDryApi(AsyncApi):
    """Speed dry API (``speed-dry``)."""

    INFO = INFO

    async def speed_dry(self, *, request_options: RequestOptions | None = None) -> None:
        """Execute a one-shot speed dry operation through ptz.cgi.

        After the operation has finished the device is idle for about 20 seconds, during which other speed
        dry requests are discarded. The reply carries no success or failure information.

        Access: viewer.
        """
        await self._run(OPS.speed_dry, None, {}, request_options)

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the speed dry capabilities (one ``path type`` line per supported attribute).

        Access: viewer.
        """
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    async def oneshot(self, *, request_options: RequestOptions | None = None) -> None:
        """Initiate a one-shot speed dry operation. Access: viewer."""
        await self._run(OPS.oneshot, None, {}, request_options)
