# GENERATED from specs/apis/network-video/ptz-control-queue.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Request, drop and query PTZ control in the priority-based PTZ control queue.

Docs: https://developer.axis.com/vapix/network-video/pantiltzoom-api/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

QueueStatusText = str


class RequestControlRequest(Model):
    camera: int | None = Field(default=None, ge=1)
    """Video channel. The default channel is used if omitted."""


class ReleaseControlRequest(Model):
    camera: int | None = Field(default=None, ge=1)
    """Video channel. The default channel is used if omitted."""


class GetQueueStatusRequest(Model):
    camera: int | None = Field(default=None, ge=1)
    """Video channel. The default channel is used if omitted."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/com/ptzqueue.cgi"

INFO = ApiInfo(
    id="ptz-control-queue",
    name="PTZ control queue (Queuing API)",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.PTZ.PTZ", "yes"),
        ParamDiscovery("Properties.PTZ.DigitalPTZ", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/pantiltzoom-api/",),
)


class OPS:
    request_control = Operation(
        INFO,
        "request_control",
        CgiBinding(PATH, fixed_query=(("control", "request"),), args=(CgiArg("camera"),), reply=Text()),
        params=RequestControlRequest,
        result=QueueStatusText,
        access="viewer",
        effect="action",
    )
    release_control = Operation(
        INFO,
        "release_control",
        CgiBinding(PATH, fixed_query=(("control", "drop"),), args=(CgiArg("camera"),), reply=Text()),
        params=ReleaseControlRequest,
        access="viewer",
        effect="action",
    )
    get_queue_status = Operation(
        INFO,
        "get_queue_status",
        CgiBinding(PATH, fixed_query=(("control", "query"),), args=(CgiArg("camera"),), reply=Text()),
        params=GetQueueStatusRequest,
        result=QueueStatusText,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class PtzControlQueueApi(SyncApi):
    """PTZ control queue (Queuing API) (``ptz-control-queue``)."""

    INFO = INFO

    def request_control(
        self, *, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> QueueStatusText:
        """Request PTZ control.

        For a client that holds control and has no peers in the queue this resets the control timer. For all
        other clients it has the same effect as ``get_queue_status``.

        Access: viewer.
        """
        return self._run(OPS.request_control, None, {"camera": camera}, request_options)

    def release_control(
        self, *, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Drop PTZ control or leave the queue. Access: viewer."""
        self._run(OPS.release_control, None, {"camera": camera}, request_options)

    def get_queue_status(
        self, *, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> QueueStatusText:
        """Report the queue status for this client.

        A client in the queue must call this regularly (see the recommended period in the reply) to stay
        active.

        Access: viewer.
        """
        return self._run(OPS.get_queue_status, None, {"camera": camera}, request_options)


class AsyncPtzControlQueueApi(AsyncApi):
    """PTZ control queue (Queuing API) (``ptz-control-queue``)."""

    INFO = INFO

    async def request_control(
        self, *, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> QueueStatusText:
        """Request PTZ control.

        For a client that holds control and has no peers in the queue this resets the control timer. For all
        other clients it has the same effect as ``get_queue_status``.

        Access: viewer.
        """
        return await self._run(OPS.request_control, None, {"camera": camera}, request_options)

    async def release_control(
        self, *, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Drop PTZ control or leave the queue. Access: viewer."""
        await self._run(OPS.release_control, None, {"camera": camera}, request_options)

    async def get_queue_status(
        self, *, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> QueueStatusText:
        """Report the queue status for this client.

        A client in the queue must call this regularly (see the recommended period in the reply) to stay
        active.

        Access: viewer.
        """
        return await self._run(OPS.get_queue_status, None, {"camera": camera}, request_options)
