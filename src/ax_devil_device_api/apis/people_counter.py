# GENERATED from specs/apis/applications/people-counter.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""AXIS People Counter ACAP: real-time and historical two-way people counts (JSON, CSV, XML, binary cnt), occupancy data, live view line placement, parameters and logs.

Docs: https://developer.axis.com/vapix/applications/people-counter-api/
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.cgi import Binary, CgiArg, CgiBinding, JsonReply, Stream, Text, TextOk, Xml
from .._runtime.driver import AsyncStreamResult, StreamResult
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DateSelection = Annotated[str, Field(pattern="^(all|[0-9]{8}(-[0-9]{8})?|[0-9]{8}(,[0-9]{8})*)$")]
Resolution = Literal["15m", "1h", "24h"]
OccupancyResolution = Literal["1m", "15m", "1h", "24h"]


class LiveSum(Model):
    serial: str
    """Camera serial number."""
    name: str
    """Name of the counter."""
    timestamp: str
    """Time in the camera, YYYYMMDDhhmmss."""
    in_: int = Field(validation_alias="in", serialization_alias="in")
    """Number of people passing in until now today."""
    out: int
    """Number of people passing out until now."""


class DayList(Model):
    timestamp: str
    """Time in the camera, YYYYMMDDhhmmss."""
    days: list[str]
    """Days (YYYYMMDD) for which data exists."""


class CountPosition(Model):
    width: int
    """Width of the video stream in pixels."""
    height: int
    """Height of the video stream in pixels."""
    left: int
    """X coordinate in pixels where the blue lines in Live view start."""
    right: int
    """X coordinate in pixels where the blue lines in Live view stop."""
    top: int
    """Y coordinate in pixels of the first blue line in Live view."""
    bottom: int
    """Y coordinate in pixels of the second blue line in Live view."""
    yfirst: int
    """Y coordinate in pixels of the top of the red counting area, disregarding curvature."""
    ylast: int
    """Y coordinate in pixels of the bottom of the red counting area, disregarding curvature."""
    radius: int
    """Radius in pixels of the curvature of the red counting area, measured in the center on both axes. The docs omit the value for a non-curved area; the example shows 0."""


class OccupancyCounter(Model):
    name: str | None = None
    """The name of the application, chosen by the client."""
    serial: str | None = None
    """The MAC address of the camera."""
    delta: int | None = None
    """Time difference between data entries, in seconds."""
    types: dict[str, int] | None = None
    """Column ids by column name: Occupancy, Average Time, Total In, Total Out."""


class OccupancyExport(Model):
    counter: OccupancyCounter
    data: dict[str, list[int]]
    """Values keyed by timestamp YYYYMMDDhhmmss, ordered as Occupancy, Average Time, Total In, Total Out in the example."""


class ExportCntRequest(Model):
    date: DateSelection


class HistoricalDataRequest(Model):
    date: DateSelection | None = None
    """Default: 'all'."""
    res: Resolution | None = None
    """Default: '15m'."""


class SetParamsRequest(Model):
    values: dict[str, str]
    """Parameter names mapped to their new values, for example Counter.Height to 280."""


class ResetOccupancyRequest(Model):
    occ: int | None = None
    """Occupancy value to reset to; documented only as the placeholder [value]."""


class OccupancyExportRequest(Model):
    date: str
    """A date YYYYMMDD, for example 20180520. The JSON example also uses all."""
    res: OccupancyResolution


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/tvpc/.api"

INFO = ApiInfo(
    id="people-counter",
    name="People counter API",
    family=Family.CGI,
    requires_application="AXIS People Counter",
    docs=("https://developer.axis.com/vapix/applications/people-counter-api/",),
)


class OPS:
    get_live_sum = Operation(
        INFO,
        "get_live_sum",
        CgiBinding(PATH, fixed_query=(("live-sum.json", None),), reply=JsonReply()),
        result=LiveSum,
        access="admin",
        effect="read",
    )
    list_available_days = Operation(
        INFO,
        "list_available_days",
        CgiBinding(PATH, fixed_query=(("list-cnt.json", None),), reply=JsonReply()),
        result=DayList,
        access="admin",
        effect="read",
    )
    export_cnt = Operation(
        INFO,
        "export_cnt",
        CgiBinding(PATH, fixed_query=(("export-cnt", None),), args=(CgiArg("date"),), reply=Binary()),
        params=ExportCntRequest,
        result=bytes,
        access="admin",
        effect="read",
    )
    export_csv = Operation(
        INFO,
        "export_csv",
        CgiBinding(PATH, fixed_query=(("export-csv", None),), args=(CgiArg("date"), CgiArg("res")), reply=Text()),
        params=HistoricalDataRequest,
        result=str,
        access="admin",
        effect="read",
    )
    export_json = Operation(
        INFO,
        "export_json",
        CgiBinding(PATH, fixed_query=(("export-json", None),), args=(CgiArg("date"), CgiArg("res")), reply=JsonReply()),
        params=HistoricalDataRequest,
        result=Any,
        access="admin",
        effect="read",
    )
    export_xml = Operation(
        INFO,
        "export_xml",
        CgiBinding(PATH, fixed_query=(("export-xml", None),), args=(CgiArg("date"), CgiArg("res")), reply=Xml()),
        params=HistoricalDataRequest,
        result=ET.Element,
        access="admin",
        effect="read",
    )
    clear_data = Operation(
        INFO,
        "clear_data",
        CgiBinding("/local/tvpc/.apioperator", fixed_query=(("clear-data", None),), reply=TextOk()),
        access="operator",
        effect="write",
        write="delete",
    )
    get_count_position = Operation(
        INFO,
        "get_count_position",
        CgiBinding(PATH, fixed_query=(("cntpos.json", None),), reply=JsonReply()),
        result=CountPosition,
        access="admin",
        effect="read",
    )
    show_logs = Operation(
        INFO,
        "show_logs",
        CgiBinding("/local/tvpc/.apioperator", fixed_query=(("show-logs", None),), reply=Text()),
        result=str,
        access="operator",
        effect="read",
    )
    generate_logs = Operation(
        INFO,
        "generate_logs",
        CgiBinding("/local/tvpc/.apioperator", fixed_query=(("generate-logs", None),), reply=Stream(), stream=True),
        access="operator",
        effect="read",
    )
    get_params = Operation(
        INFO,
        "get_params",
        CgiBinding(PATH, fixed_query=(("params.json", None),), reply=JsonReply()),
        result=dict[str, Any],
        access="admin",
        effect="read",
    )
    set_params = Operation(
        INFO,
        "set_params",
        CgiBinding(
            "/local/tvpc/.apioperator",
            method="POST",
            encoding="form",
            url_query=(("setparams", None),),
            args=(CgiArg("values", style="spread"),),
            reply=TextOk(),
        ),
        params=SetParamsRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_live_occupancy = Operation(
        INFO,
        "get_live_occupancy",
        CgiBinding("/tvpc/.api", fixed_query=(("live-occupancy.json", None),), reply=JsonReply()),
        result=Any,
        access="admin",
        effect="read",
    )
    reset_occupancy = Operation(
        INFO,
        "reset_occupancy",
        CgiBinding("/tvpc/.api", fixed_query=(("occupancy-reset", None),), args=(CgiArg("occ"),), reply=Text()),
        params=ResetOccupancyRequest,
        access="admin",
        effect="action",
    )
    occupancy_export_csv = Operation(
        INFO,
        "occupancy_export_csv",
        CgiBinding(
            PATH, fixed_query=(("occupancy-export-csv", None),), args=(CgiArg("date"), CgiArg("res")), reply=Text()
        ),
        params=OccupancyExportRequest,
        result=str,
        access="admin",
        effect="read",
    )
    occupancy_export_json = Operation(
        INFO,
        "occupancy_export_json",
        CgiBinding(
            PATH,
            fixed_query=(("occupancy-export-json", None),),
            args=(CgiArg("date"), CgiArg("res")),
            reply=JsonReply(),
        ),
        params=OccupancyExportRequest,
        result=OccupancyExport,
        access="admin",
        effect="read",
    )
    occupancy_export_xml = Operation(
        INFO,
        "occupancy_export_xml",
        CgiBinding(
            PATH, fixed_query=(("occupancy-export-xml", None),), args=(CgiArg("date"), CgiArg("res")), reply=Xml()
        ),
        params=OccupancyExportRequest,
        result=ET.Element,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class PeopleCounterApi(SyncApi):
    """People counter API (``people-counter``)."""

    INFO = INFO

    def get_live_sum(self, *, request_options: RequestOptions | None = None) -> LiveSum:
        """Request real-time counting data. Access: admin."""
        return self._run(OPS.get_live_sum, None, {}, request_options)

    def list_available_days(self, *, request_options: RequestOptions | None = None) -> DayList:
        """List the days for which counting data exists. Access: admin."""
        return self._run(OPS.list_available_days, None, {}, request_options)

    def export_cnt(self, date: DateSelection, *, request_options: RequestOptions | None = None) -> bytes:
        """Download a binary data file (.cnt) for the given dates, for use in AXIS Store Data Manager.

        Access: admin.
        """
        return self._run(OPS.export_cnt, None, {"date": date}, request_options)

    def export_csv(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Resolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Request historical data in CSV format.

        Plain text, comma-separated values. The first line describes each element; the following lines hold
        the data for the chosen interval and resolution.

        Access: admin.
        """
        return self._run(OPS.export_csv, None, {"date": date, "res": res}, request_options)

    def export_json(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Resolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Request historical data in JSON format.

        The docs do not describe the JSON structure, so the result is the parsed JSON document.

        Access: admin.
        """
        return self._run(OPS.export_json, None, {"date": date, "res": res}, request_options)

    def export_xml(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Resolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ET.Element:
        """Request historical data in XML format.

        The structure is defined by a DTD at /local/tvpc/appdata.dtd, so the result is the parsed XML root
        element.

        Access: admin.
        """
        return self._run(OPS.export_xml, None, {"date": date, "res": res}, request_options)

    def clear_data(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear all counting data.

        Permanently deletes all counting data from the device.

        Access: operator.
        """
        self._run(OPS.clear_data, None, {}, request_options)

    def get_count_position(self, *, request_options: RequestOptions | None = None) -> CountPosition:
        """Live view information: placement of the counting lines in Live view. Access: admin."""
        return self._run(OPS.get_count_position, None, {}, request_options)

    def show_logs(self, *, request_options: RequestOptions | None = None) -> str:
        """Show the system log. Access: operator."""
        return self._run(OPS.show_logs, None, {}, request_options)

    def generate_logs(self, *, request_options: RequestOptions | None = None) -> StreamResult[bytes]:
        """Generate and download a log archive (tar.gz).

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: operator.
        """
        return self._run(OPS.generate_logs, None, {}, request_options)

    def get_params(self, *, request_options: RequestOptions | None = None) -> dict[str, Any]:
        """List the people counter parameters. Access: admin."""
        return self._run(OPS.get_params, None, {}, request_options)

    def set_params(self, values: Mapping[str, str], *, request_options: RequestOptions | None = None) -> None:
        """Set people counter parameters.

        Posts the parameters to the operator endpoint. The keys are parameter names (for example
        Counter.Height) and the values are sent as form fields next to the setparams marker (AXIS OS 5.60
        and later). Older AXIS OS versions expect pairs p1=<name>&v1=<value> instead, which this operation
        does not send.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_params, None, {"values": dict(values)}, request_options)

    def get_live_occupancy(self, *, request_options: RequestOptions | None = None) -> Any:
        """Request real-time occupancy data.

        The docs do not describe the JSON reply, so the result is the parsed JSON document.

        Access: admin.
        """
        return self._run(OPS.get_live_occupancy, None, {}, request_options)

    def reset_occupancy(self, *, occ: int | MISSING = MISSING, request_options: RequestOptions | None = None) -> None:
        """Reset the occupancy data.

        Only works while the people counter is in naive occupancy mode.

        Access: admin.
        """
        self._run(OPS.reset_occupancy, None, {"occ": occ}, request_options)

    def occupancy_export_csv(
        self, *, date: str, res: OccupancyResolution, request_options: RequestOptions | None = None
    ) -> str:
        """Export occupancy data in CSV format. Access: admin."""
        return self._run(OPS.occupancy_export_csv, None, {"date": date, "res": res}, request_options)

    def occupancy_export_json(
        self, *, date: str, res: OccupancyResolution, request_options: RequestOptions | None = None
    ) -> OccupancyExport:
        """Export occupancy data in JSON format (people entering and leaving, average visit time).

        Access: admin.
        """
        return self._run(OPS.occupancy_export_json, None, {"date": date, "res": res}, request_options)

    def occupancy_export_xml(
        self, *, date: str, res: OccupancyResolution, request_options: RequestOptions | None = None
    ) -> ET.Element:
        """Export occupancy data in XML format.

        The structure is not documented, so the result is the parsed XML root element.

        Access: admin.
        """
        return self._run(OPS.occupancy_export_xml, None, {"date": date, "res": res}, request_options)


class AsyncPeopleCounterApi(AsyncApi):
    """People counter API (``people-counter``)."""

    INFO = INFO

    async def get_live_sum(self, *, request_options: RequestOptions | None = None) -> LiveSum:
        """Request real-time counting data. Access: admin."""
        return await self._run(OPS.get_live_sum, None, {}, request_options)

    async def list_available_days(self, *, request_options: RequestOptions | None = None) -> DayList:
        """List the days for which counting data exists. Access: admin."""
        return await self._run(OPS.list_available_days, None, {}, request_options)

    async def export_cnt(self, date: DateSelection, *, request_options: RequestOptions | None = None) -> bytes:
        """Download a binary data file (.cnt) for the given dates, for use in AXIS Store Data Manager.

        Access: admin.
        """
        return await self._run(OPS.export_cnt, None, {"date": date}, request_options)

    async def export_csv(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Resolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Request historical data in CSV format.

        Plain text, comma-separated values. The first line describes each element; the following lines hold
        the data for the chosen interval and resolution.

        Access: admin.
        """
        return await self._run(OPS.export_csv, None, {"date": date, "res": res}, request_options)

    async def export_json(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Resolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Request historical data in JSON format.

        The docs do not describe the JSON structure, so the result is the parsed JSON document.

        Access: admin.
        """
        return await self._run(OPS.export_json, None, {"date": date, "res": res}, request_options)

    async def export_xml(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Resolution | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ET.Element:
        """Request historical data in XML format.

        The structure is defined by a DTD at /local/tvpc/appdata.dtd, so the result is the parsed XML root
        element.

        Access: admin.
        """
        return await self._run(OPS.export_xml, None, {"date": date, "res": res}, request_options)

    async def clear_data(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear all counting data.

        Permanently deletes all counting data from the device.

        Access: operator.
        """
        await self._run(OPS.clear_data, None, {}, request_options)

    async def get_count_position(self, *, request_options: RequestOptions | None = None) -> CountPosition:
        """Live view information: placement of the counting lines in Live view. Access: admin."""
        return await self._run(OPS.get_count_position, None, {}, request_options)

    async def show_logs(self, *, request_options: RequestOptions | None = None) -> str:
        """Show the system log. Access: operator."""
        return await self._run(OPS.show_logs, None, {}, request_options)

    async def generate_logs(self, *, request_options: RequestOptions | None = None) -> AsyncStreamResult[bytes]:
        """Generate and download a log archive (tar.gz).

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: operator.
        """
        return await self._run(OPS.generate_logs, None, {}, request_options)

    async def get_params(self, *, request_options: RequestOptions | None = None) -> dict[str, Any]:
        """List the people counter parameters. Access: admin."""
        return await self._run(OPS.get_params, None, {}, request_options)

    async def set_params(self, values: Mapping[str, str], *, request_options: RequestOptions | None = None) -> None:
        """Set people counter parameters.

        Posts the parameters to the operator endpoint. The keys are parameter names (for example
        Counter.Height) and the values are sent as form fields next to the setparams marker (AXIS OS 5.60
        and later). Older AXIS OS versions expect pairs p1=<name>&v1=<value> instead, which this operation
        does not send.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_params, None, {"values": dict(values)}, request_options)

    async def get_live_occupancy(self, *, request_options: RequestOptions | None = None) -> Any:
        """Request real-time occupancy data.

        The docs do not describe the JSON reply, so the result is the parsed JSON document.

        Access: admin.
        """
        return await self._run(OPS.get_live_occupancy, None, {}, request_options)

    async def reset_occupancy(
        self, *, occ: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Reset the occupancy data.

        Only works while the people counter is in naive occupancy mode.

        Access: admin.
        """
        await self._run(OPS.reset_occupancy, None, {"occ": occ}, request_options)

    async def occupancy_export_csv(
        self, *, date: str, res: OccupancyResolution, request_options: RequestOptions | None = None
    ) -> str:
        """Export occupancy data in CSV format. Access: admin."""
        return await self._run(OPS.occupancy_export_csv, None, {"date": date, "res": res}, request_options)

    async def occupancy_export_json(
        self, *, date: str, res: OccupancyResolution, request_options: RequestOptions | None = None
    ) -> OccupancyExport:
        """Export occupancy data in JSON format (people entering and leaving, average visit time).

        Access: admin.
        """
        return await self._run(OPS.occupancy_export_json, None, {"date": date, "res": res}, request_options)

    async def occupancy_export_xml(
        self, *, date: str, res: OccupancyResolution, request_options: RequestOptions | None = None
    ) -> ET.Element:
        """Export occupancy data in XML format.

        The structure is not documented, so the result is the parsed XML root element.

        Access: admin.
        """
        return await self._run(OPS.occupancy_export_xml, None, {"date": date, "res": res}, request_options)
