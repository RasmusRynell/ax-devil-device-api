# GENERATED from specs/apis/network-video/heartbeat.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Send heartbeats from a master (door controller, VMS) to a device; a heartbeat lost event is emitted when a heartbeat expires.

Docs: https://developer.axis.com/vapix/network-video/heartbeat-service-api/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class HeartbeatRequest(Model):
    duration: int = Field(validation_alias="Duration", serialization_alias="Duration")
    """Heartbeat duration, that is, the time before a heartbeat lost event is emitted. Unit: milliseconds."""


class HeartbeatResult(Model):
    session_id: str = Field(validation_alias="SessionId", serialization_alias="SessionId")
    """Session identifier. It stays the same as long as the heartbeat is kept alive; a change between two successive calls means the heartbeat expired and the heartbeat lost event may have fired."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/axhbt"

INFO = ApiInfo(
    id="heartbeat",
    name="Heartbeat service API",
    family=Family.SERVICE_JSON,
    discovery=(
        ParamDiscovery("Properties.API.Heartbeat.Heartbeat", "yes"),
        ParamDiscovery("Properties.API.Heartbeat.Version", "1.0", ">="),
    ),
    docs=("https://developer.axis.com/vapix/network-video/heartbeat-service-api/",),
)


class OPS:
    heartbeat = Operation(
        INFO,
        "heartbeat",
        ServiceJsonBinding(PATH, "axhbt:Heartbeat"),
        params=HeartbeatRequest,
        result=HeartbeatResult,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class HeartbeatApi(SyncApi):
    """Heartbeat service API (``heartbeat``)."""

    INFO = INFO

    def heartbeat(self, *, duration: int, request_options: RequestOptions | None = None) -> HeartbeatResult:
        """Send a heartbeat.

        Heartbeats should be sent at regular intervals, typically within a few seconds. To keep the
        heartbeat alive, send a new heartbeat before Duration expires. If a heartbeat expires, the session
        identifier in the response changes and the heartbeat lost event becomes true.

        Access: admin.
        """
        return self._run(OPS.heartbeat, None, {"duration": duration}, request_options)


class AsyncHeartbeatApi(AsyncApi):
    """Heartbeat service API (``heartbeat``)."""

    INFO = INFO

    async def heartbeat(self, *, duration: int, request_options: RequestOptions | None = None) -> HeartbeatResult:
        """Send a heartbeat.

        Heartbeats should be sent at regular intervals, typically within a few seconds. To keep the
        heartbeat alive, send a new heartbeat before Duration expires. If a heartbeat expires, the session
        identifier in the response changes and the heartbeat lost event becomes true.

        Access: admin.
        """
        return await self._run(OPS.heartbeat, None, {"duration": duration}, request_options)
