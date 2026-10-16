# GENERATED from specs/apis/applications/p8815-2-3d-people-counter.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Export foot traffic and occupancy statistics (CSV/JSON) and read real-time occupancy on the AXIS P8815-2 3D People Counter.

Docs: https://developer.axis.com/vapix/applications/p8815-2-3d-people-counter-api/
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, JsonReply, Text
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

StatisticsDate = Annotated[str, Field(pattern="^([0-9]{8}|yesterday|today|now)$")]
TrafficResolution = Literal["minute", "hour", "day"]
OccupancyResolution = Literal["hour", "day"]


class TrafficRecord(Model):
    start: str
    """Interval start, YYYY-MM-DD hh:mm:ss."""
    end: str
    """Interval end, YYYY-MM-DD hh:mm:ss."""
    in_: int = Field(validation_alias="in", serialization_alias="in")
    """People counted in during the interval."""
    out: int
    """People counted out during the interval."""


class TrafficStatistics(Model):
    data: list[TrafficRecord]


class OccupancyRecord(Model):
    start: str
    """Interval start, YYYY-MM-DD hh:mm:ss."""
    end: str
    """Interval end, YYYY-MM-DD hh:mm:ss."""
    peak: int
    """Peak occupancy during the interval."""


class OccupancyStatistics(Model):
    data: list[OccupancyRecord]


class RealTimeOccupancy(Model):
    """Real-time estimated occupancy and counting statistics for the primary camera and its connected secondary cameras."""

    occupancy: int
    """Estimated occupancy."""
    serial: str
    """Serial of the camera, for example 00:40:8c:18:82:27."""
    timestamp: str
    """Time of the reading, ISO 8601 with offset."""
    total_in: int
    """Total people counted in."""
    total_out: int
    """Total people counted out."""


class TrafficExportRequest(Model):
    start: StatisticsDate
    end: StatisticsDate
    resolution: TrafficResolution


class OccupancyExportRequest(Model):
    start: StatisticsDate
    end: StatisticsDate
    resolution: OccupancyResolution


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/a3dpc/api/export/csv"

INFO = ApiInfo(
    id="p8815-2-3d-people-counter",
    name="P8815-2 3D people counter API",
    family=Family.CGI,
    requires_application="AXIS 3D People Counter",
    docs=("https://developer.axis.com/vapix/applications/p8815-2-3d-people-counter-api/",),
)


class OPS:
    export_traffic_csv = Operation(
        INFO,
        "export_traffic_csv",
        CgiBinding("/a3dpc/api/export/csv", args=(CgiArg("start"), CgiArg("end"), CgiArg("resolution")), reply=Text()),
        params=TrafficExportRequest,
        result=str,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode(
                "Bad Request. Validation failed; the error list gives the field and reason.", "invalid_argument"
            )
        },
    )
    export_traffic_json = Operation(
        INFO,
        "export_traffic_json",
        CgiBinding(
            "/a3dpc/api/export/json", args=(CgiArg("start"), CgiArg("end"), CgiArg("resolution")), reply=JsonReply()
        ),
        params=TrafficExportRequest,
        result=TrafficStatistics,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode(
                "Bad Request. Validation failed; the error list gives the field and reason.", "invalid_argument"
            )
        },
    )
    export_occupancy_csv = Operation(
        INFO,
        "export_occupancy_csv",
        CgiBinding(
            "/a3dpc/api/export_occupancy/csv", args=(CgiArg("start"), CgiArg("end"), CgiArg("resolution")), reply=Text()
        ),
        params=OccupancyExportRequest,
        result=str,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode(
                "Bad Request. Validation failed; the error list gives the field and reason.", "invalid_argument"
            )
        },
    )
    export_occupancy_json = Operation(
        INFO,
        "export_occupancy_json",
        CgiBinding(
            "/a3dpc/api/export_occupancy/json",
            args=(CgiArg("start"), CgiArg("end"), CgiArg("resolution")),
            reply=JsonReply(),
        ),
        params=OccupancyExportRequest,
        result=OccupancyStatistics,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode(
                "Bad Request. Validation failed; the error list gives the field and reason.", "invalid_argument"
            )
        },
    )
    get_occupancy = Operation(
        INFO,
        "get_occupancy",
        CgiBinding("/a3dpc/api/occupancy", reply=JsonReply()),
        result=RealTimeOccupancy,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class P8815PeopleCounter3DApi(SyncApi):
    """P8815-2 3D people counter API (``p8815-2-3d-people-counter``)."""

    INFO = INFO

    def export_traffic_csv(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: TrafficResolution,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Download foot traffic statistics (In/Out) as CSV.

        The first line names the columns: start, end, in, out.

        Access: admin.
        """
        return self._run(
            OPS.export_traffic_csv, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    def export_traffic_json(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: TrafficResolution,
        request_options: RequestOptions | None = None,
    ) -> TrafficStatistics:
        """Download foot traffic statistics (In/Out) as JSON. Access: admin."""
        return self._run(
            OPS.export_traffic_json, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    def export_occupancy_csv(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: OccupancyResolution,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Download occupancy statistics as CSV.

        The first line names the columns: start, end, peak.

        Access: admin.
        """
        return self._run(
            OPS.export_occupancy_csv, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    def export_occupancy_json(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: OccupancyResolution,
        request_options: RequestOptions | None = None,
    ) -> OccupancyStatistics:
        """Download occupancy statistics as JSON. Access: admin."""
        return self._run(
            OPS.export_occupancy_json, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    def get_occupancy(self, *, request_options: RequestOptions | None = None) -> RealTimeOccupancy:
        """Request real-time estimated occupancy and counting statistics (primary camera and connected secondary cameras).

        Access: admin.
        """
        return self._run(OPS.get_occupancy, None, {}, request_options)


class AsyncP8815PeopleCounter3DApi(AsyncApi):
    """P8815-2 3D people counter API (``p8815-2-3d-people-counter``)."""

    INFO = INFO

    async def export_traffic_csv(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: TrafficResolution,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Download foot traffic statistics (In/Out) as CSV.

        The first line names the columns: start, end, in, out.

        Access: admin.
        """
        return await self._run(
            OPS.export_traffic_csv, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    async def export_traffic_json(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: TrafficResolution,
        request_options: RequestOptions | None = None,
    ) -> TrafficStatistics:
        """Download foot traffic statistics (In/Out) as JSON. Access: admin."""
        return await self._run(
            OPS.export_traffic_json, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    async def export_occupancy_csv(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: OccupancyResolution,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Download occupancy statistics as CSV.

        The first line names the columns: start, end, peak.

        Access: admin.
        """
        return await self._run(
            OPS.export_occupancy_csv, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    async def export_occupancy_json(
        self,
        *,
        start: StatisticsDate,
        end: StatisticsDate,
        resolution: OccupancyResolution,
        request_options: RequestOptions | None = None,
    ) -> OccupancyStatistics:
        """Download occupancy statistics as JSON. Access: admin."""
        return await self._run(
            OPS.export_occupancy_json, None, {"start": start, "end": end, "resolution": resolution}, request_options
        )

    async def get_occupancy(self, *, request_options: RequestOptions | None = None) -> RealTimeOccupancy:
        """Request real-time estimated occupancy and counting statistics (primary camera and connected secondary cameras).

        Access: admin.
        """
        return await self._run(OPS.get_occupancy, None, {}, request_options)
