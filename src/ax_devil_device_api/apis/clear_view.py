# GENERATED from specs/apis/network-video/clear-view.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Activate lens/dome cleaning functions (wiper, speed dry) and query their capabilities and status.

Docs: https://developer.axis.com/vapix/network-video/clear-view/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ServiceType = Literal["wiper", "speeddry"]
ServiceState = Literal["idle", "running", "waiting"]


class ServiceInfo(Model):
    """Static description of one Clear view service."""

    id: int
    """The ID of the clear view device."""
    type: ServiceType
    """``wiper`` or ``speeddry``."""
    duration_variable: bool = Field(validation_alias="durationVariable", serialization_alias="durationVariable")
    """Whether the duration can be set."""
    duration_min: int | None = Field(default=None, validation_alias="durationMin", serialization_alias="durationMin")
    """Present if ``durationVariable`` is true."""
    duration_max: int | None = Field(default=None, validation_alias="durationMax", serialization_alias="durationMax")
    """Present if ``durationVariable`` is true."""
    duration_default: int = Field(validation_alias="durationDefault", serialization_alias="durationDefault")
    """The default duration, measured in seconds."""
    stoppable: bool
    """Whether the stop command is supported for the device."""
    idle_time_min: int | None = Field(default=None, validation_alias="idleTimeMin", serialization_alias="idleTimeMin")
    """Included if the device needs to rest between runs, measured in seconds."""


class ServiceInfoResult(Model):
    service_info: list[ServiceInfo] = Field(validation_alias="serviceInfo", serialization_alias="serviceInfo")
    """The supported Clear view services."""


class ServiceStatus(Model):
    """Dynamic status of one Clear view service."""

    id: int | None = None
    """The ID of the clear view device."""
    state: ServiceState
    stops_in: int | None = Field(default=None, validation_alias="stopsIn", serialization_alias="stopsIn")
    """Present if ``state`` is ``running``."""
    available_in: int | None = Field(default=None, validation_alias="availableIn", serialization_alias="availableIn")
    """Present if ``idleTimeMin`` > 0 and ``state`` is ``running`` or ``waiting``."""


class StatusResult(Model):
    status: ServiceStatus | None = None
    """The status of the Clear view service."""


class GetStatusRequest(Model):
    id: int
    """The device ID (from getServiceInfo)."""


class StartRequest(Model):
    id: int
    """The device ID."""
    duration: int | None = None
    """The duration, measured in seconds. Defaults to ``durationDefault`` of the service."""


class StopRequest(Model):
    id: int
    """The device ID. Only services with ``stoppable`` true can be stopped."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/clearviewcontrol.cgi"

INFO = ApiInfo(
    id="clear-view",
    name="Clear view",
    family=Family.JSONRPC,
    major=2,
    known_versions=(ApiVersion(2, 1),),
    discovery=(
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.ClearView.ClearView", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/clear-view/",),
    errors={
        1000: ErrorCode("Invalid parameter value.", "invalid_argument"),
        1001: ErrorCode("The requested Clear View device ID is not supported.", "invalid_argument"),
        1002: ErrorCode("Device in incompatible state.", "unavailable"),
        1003: ErrorCode("Requested duration outside supported limits.", "invalid_argument"),
        1005: ErrorCode("Temperature out of range.", "unavailable"),
        2000: ErrorCode("Out of memory.", "internal"),
        2001: ErrorCode("Access forbidden (similar to HTTP 403).", "access_denied"),
        2002: ErrorCode("HTTP request type not supported. Only POST supported.", "unsupported"),
        2003: ErrorCode("The requested API version is not supported.", "unsupported"),
        2004: ErrorCode("Method not supported.", "unsupported"),
        4000: ErrorCode("The provided JSON input was invalid.", "invalid_argument"),
        4001: ErrorCode("A mandatory input parameter was not found in the input.", "invalid_argument"),
        4002: ErrorCode("The type of a provided JSON parameter was incorrect.", "invalid_argument"),
        8000: ErrorCode("Internal error.", "internal"),
    },
)


class OPS:
    get_service_info = Operation(
        INFO,
        "get_service_info",
        JsonRpcBinding("getServiceInfo", PATH),
        result=ServiceInfoResult,
        access="operator",
        effect="read",
    )
    get_status = Operation(
        INFO,
        "get_status",
        JsonRpcBinding("getStatus", PATH),
        params=GetStatusRequest,
        result=StatusResult,
        access="operator",
        effect="read",
    )
    start = Operation(
        INFO, "start", JsonRpcBinding("start", PATH), params=StartRequest, access="operator", effect="action"
    )
    stop = Operation(INFO, "stop", JsonRpcBinding("stop", PATH), params=StopRequest, access="operator", effect="action")


# ---------------------------------------------------------------------------
# API classes


class ClearViewApi(SyncApi):
    """Clear view (``clear-view``, version 2)."""

    INFO = INFO

    def get_service_info(self, *, request_options: RequestOptions | None = None) -> ServiceInfoResult:
        """Retrieves the Clear view service information (static values only). Access: operator."""
        return self._run(OPS.get_service_info, None, {}, request_options)

    def get_status(self, *, id: int, request_options: RequestOptions | None = None) -> StatusResult:
        """Retrieves the Clear view service status for one service (dynamic values).

        Access: operator.
        """
        return self._run(OPS.get_status, None, {"id": id}, request_options)

    def start(
        self, *, id: int, duration: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Initiates the Clear view function for one service (default or specified duration).

        Access: operator.
        """
        self._run(OPS.start, None, {"id": id, "duration": duration}, request_options)

    def stop(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Halts a currently running Clear view function on a service. Access: operator."""
        self._run(OPS.stop, None, {"id": id}, request_options)


class AsyncClearViewApi(AsyncApi):
    """Clear view (``clear-view``, version 2)."""

    INFO = INFO

    async def get_service_info(self, *, request_options: RequestOptions | None = None) -> ServiceInfoResult:
        """Retrieves the Clear view service information (static values only). Access: operator."""
        return await self._run(OPS.get_service_info, None, {}, request_options)

    async def get_status(self, *, id: int, request_options: RequestOptions | None = None) -> StatusResult:
        """Retrieves the Clear view service status for one service (dynamic values).

        Access: operator.
        """
        return await self._run(OPS.get_status, None, {"id": id}, request_options)

    async def start(
        self, *, id: int, duration: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Initiates the Clear view function for one service (default or specified duration).

        Access: operator.
        """
        await self._run(OPS.start, None, {"id": id, "duration": duration}, request_options)

    async def stop(self, *, id: int, request_options: RequestOptions | None = None) -> None:
        """Halts a currently running Clear view function on a service. Access: operator."""
        await self._run(OPS.stop, None, {"id": id}, request_options)
