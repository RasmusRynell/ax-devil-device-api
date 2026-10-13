# GENERATED from specs/apis/applications/queue-monitor.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Queue Monitor ACAP: live people-in-queue counts per region, CSV queue history, data clearing, parameters and logs.

Docs: https://developer.axis.com/vapix/applications/queue-monitor-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.cgi import Binary, CgiArg, CgiBinding, JsonReply, Text, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DateSelection = Annotated[str, Field(pattern="^(all|[0-9]{8}(-[0-9]{8})?|[0-9]{8}(,[0-9]{8})*)$")]
MinutesResolution = Literal["15m", "1h", "24h"]
PeopleResolution = Literal["1m", "15m", "1h", "24h"]


class LiveSumPeople(Model):
    """The docs list only the region 1 fields; the examples show regions 1 to 3."""

    serial: str
    """Camera serial number."""
    name: str
    """Name of the counter."""
    timestamp: str
    """Time in the camera, YYYYMMDDhhmmss."""
    region1name: str | None = None
    """Name of region 1."""
    region1people: int | None = None
    """Number of people standing in region 1."""
    region2name: str | None = None
    """Name of region 2."""
    region2people: int | None = None
    """Number of people standing in region 2."""
    region3name: str | None = None
    """Name of region 3."""
    region3people: int | None = None
    """Number of people standing in region 3."""


class ExportRequest(Model):
    date: DateSelection | None = None
    """Default: 'all'."""
    res: MinutesResolution | None = None
    """Default: '15m'."""


class ExportPeopleRequest(Model):
    date: DateSelection | None = None
    """Default: 'all'."""
    res: PeopleResolution | None = None
    """Default: '15m'."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/queue/.api"

INFO = ApiInfo(
    id="queue-monitor",
    name="Queue monitor API",
    family=Family.CGI,
    requires_application="Queue Monitor ACAP",
    docs=("https://developer.axis.com/vapix/applications/queue-monitor-api/",),
)


class OPS:
    get_live_sum_people = Operation(
        INFO,
        "get_live_sum_people",
        CgiBinding(PATH, fixed_query=(("live-sum-people.json", None),), reply=JsonReply()),
        result=LiveSumPeople,
        access="admin",
        effect="read",
    )
    export_csv_minutes = Operation(
        INFO,
        "export_csv_minutes",
        CgiBinding(
            PATH, fixed_query=(("export-csv-minutes", None),), args=(CgiArg("date"), CgiArg("res")), reply=Text()
        ),
        params=ExportRequest,
        result=str,
        access="admin",
        effect="read",
    )
    export_csv_people = Operation(
        INFO,
        "export_csv_people",
        CgiBinding(
            PATH, fixed_query=(("export-csv-people", None),), args=(CgiArg("date"), CgiArg("res")), reply=Text()
        ),
        params=ExportPeopleRequest,
        result=str,
        access="admin",
        effect="read",
    )
    clear_data = Operation(
        INFO,
        "clear_data",
        CgiBinding("/local/queue/.apioperator", fixed_query=(("clear-data", None),), reply=TextOk()),
        access="operator",
        effect="write",
        write="delete",
    )
    get_params = Operation(
        INFO,
        "get_params",
        CgiBinding(PATH, fixed_query=(("params.json", None),), reply=JsonReply()),
        result=dict[str, Any],
        access="admin",
        effect="read",
    )
    show_logs = Operation(
        INFO,
        "show_logs",
        CgiBinding("/local/queue/.apioperator", fixed_query=(("show-logs", None),), reply=Text()),
        result=str,
        access="operator",
        effect="read",
    )
    generate_logs = Operation(
        INFO,
        "generate_logs",
        CgiBinding(
            "/local/queue/.apioperator",
            fixed_query=(("generate-logs", None),),
            reply=Binary(media_types=("application/gzip",)),
        ),
        result=bytes,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class QueueMonitorApi(SyncApi):
    """Queue monitor API (``queue-monitor``)."""

    INFO = INFO

    def get_live_sum_people(self, *, request_options: RequestOptions | None = None) -> LiveSumPeople:
        """Get real-time people-in-queue data (people standing in queue at this moment).

        Access: admin.
        """
        return self._run(OPS.get_live_sum_people, None, {}, request_options)

    def export_csv_minutes(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: MinutesResolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Request CSV minute data: minutes per region with High, Mid and Low queue.

        Returns plain text comma-separated values. The first line is a comma-separated header describing
        each column. Each integer value states the number of minutes for which there has been a certain
        amount of queue (High/Mid/Low) for a certain region.

        Access: admin.
        """
        return self._run(OPS.export_csv_minutes, None, {"date": date, "res": res}, request_options)

    def export_csv_people(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: PeopleResolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Request CSV people data: average number of people per region.

        Returns plain text comma-separated values. The first line is a comma separated header describing
        each column. Each integer value states the average number of people within a certain region of
        interest.

        Access: admin.
        """
        return self._run(OPS.export_csv_people, None, {"date": date, "res": res}, request_options)

    def clear_data(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear the local queue data. Access: operator."""
        self._run(OPS.clear_data, None, {}, request_options)

    def get_params(self, *, request_options: RequestOptions | None = None) -> dict[str, Any]:
        """List the application parameters. Access: admin."""
        return self._run(OPS.get_params, None, {}, request_options)

    def show_logs(self, *, request_options: RequestOptions | None = None) -> str:
        """Show the system log. Access: operator."""
        return self._run(OPS.show_logs, None, {}, request_options)

    def generate_logs(self, *, request_options: RequestOptions | None = None) -> bytes:
        """Generate and download a log archive (tar.gz). Access: operator."""
        return self._run(OPS.generate_logs, None, {}, request_options)


class AsyncQueueMonitorApi(AsyncApi):
    """Queue monitor API (``queue-monitor``)."""

    INFO = INFO

    async def get_live_sum_people(self, *, request_options: RequestOptions | None = None) -> LiveSumPeople:
        """Get real-time people-in-queue data (people standing in queue at this moment).

        Access: admin.
        """
        return await self._run(OPS.get_live_sum_people, None, {}, request_options)

    async def export_csv_minutes(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: MinutesResolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Request CSV minute data: minutes per region with High, Mid and Low queue.

        Returns plain text comma-separated values. The first line is a comma-separated header describing
        each column. Each integer value states the number of minutes for which there has been a certain
        amount of queue (High/Mid/Low) for a certain region.

        Access: admin.
        """
        return await self._run(OPS.export_csv_minutes, None, {"date": date, "res": res}, request_options)

    async def export_csv_people(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: PeopleResolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Request CSV people data: average number of people per region.

        Returns plain text comma-separated values. The first line is a comma separated header describing
        each column. Each integer value states the average number of people within a certain region of
        interest.

        Access: admin.
        """
        return await self._run(OPS.export_csv_people, None, {"date": date, "res": res}, request_options)

    async def clear_data(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear the local queue data. Access: operator."""
        await self._run(OPS.clear_data, None, {}, request_options)

    async def get_params(self, *, request_options: RequestOptions | None = None) -> dict[str, Any]:
        """List the application parameters. Access: admin."""
        return await self._run(OPS.get_params, None, {}, request_options)

    async def show_logs(self, *, request_options: RequestOptions | None = None) -> str:
        """Show the system log. Access: operator."""
        return await self._run(OPS.show_logs, None, {}, request_options)

    async def generate_logs(self, *, request_options: RequestOptions | None = None) -> bytes:
        """Generate and download a log archive (tar.gz). Access: operator."""
        return await self._run(OPS.generate_logs, None, {}, request_options)
