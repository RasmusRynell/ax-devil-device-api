# GENERATED from specs/apis/applications/3d-people-counter-legacy.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Deprecated legacy AXIS 3D People Counter HTTP API under /stereo/ (real-time counts, statistics export, frame rate, I/O state, parameters).

Docs: https://developer.axis.com/vapix/applications/p8815-2-3d-people-counter-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, JsonReply, Text
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Counts(Model):
    in_: int = Field(validation_alias="in", serialization_alias="in")
    """Number of people passing in until now today."""
    out: int
    """Number of people passing out until now."""
    name: str | None = None
    """The name of the application, chosen by the client."""
    serial: str | None = None
    """The MAC address of the camera."""
    timestamp: str | None = None
    """Time in the camera in the format YYYYMMDDhhmmss."""


class Fps(Model):
    fps: float | None = None
    """Real-time frame rate."""
    fps_5: float | None = None
    """Average frame rate for the last 5 frames."""
    fps_50: float | None = None
    """Average frame rate for the last 50 frames."""
    fps_100: float | None = None
    """Average frame rate for the last 100 frames."""
    fps_1000: float | None = None
    """Average frame rate for the last 1000 frames."""
    frames: int | None = None
    """Frame counter."""


ExportResolution = Literal["minute", "hour", "day", "60", "3600", "86400"]
ExportDate = Annotated[str, Field(pattern="^(all|[0-9]{8}(-[0-9]{8})?|[0-9]{8}(,[0-9]{8})*)$")]
ExportMethod = Literal["open", "download"]


class ExportRequest(Model):
    resolution: ExportResolution | None = None
    date: ExportDate | None = None
    method: ExportMethod | None = None
    export_method: str | None = Field(
        default=None, validation_alias="export-method", serialization_alias="export-method"
    )
    """Appears only in a common example (``export-method=on``); undocumented."""


class ExportJsonRequest(Model):
    resolution: ExportResolution | None = None
    date: ExportDate | None = None
    method: ExportMethod | None = None


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/stereo/people-counter/counts.json"

INFO = ApiInfo(
    id="3d-people-counter-legacy",
    name="3D people counter API (Old version)",
    family=Family.CGI,
    status="deprecated",
    requires_application="AXIS 3D People Counter (legacy)",
    docs=("https://developer.axis.com/vapix/applications/p8815-2-3d-people-counter-api/",),
)


class OPS:
    get_counts = Operation(
        INFO, "get_counts", CgiBinding(PATH, reply=JsonReply()), result=Counts, access="admin", effect="read"
    )
    export_csv = Operation(
        INFO,
        "export_csv",
        CgiBinding(
            "/stereo/people-counter/export.csv",
            args=(
                CgiArg("resolution"),
                CgiArg("date"),
                CgiArg("method"),
                CgiArg("export_method", wire="export-method"),
            ),
            reply=Text(),
        ),
        params=ExportRequest,
        result=str,
        access="admin",
        effect="read",
    )
    export_json = Operation(
        INFO,
        "export_json",
        CgiBinding(
            "/stereo/people-counter/export.json",
            args=(CgiArg("resolution"), CgiArg("date"), CgiArg("method")),
            reply=JsonReply(),
        ),
        params=ExportJsonRequest,
        result=Any,
        access="admin",
        effect="read",
    )
    get_fps = Operation(
        INFO, "get_fps", CgiBinding("/stereo/fps.json", reply=JsonReply()), result=Fps, access="admin", effect="read"
    )
    get_io = Operation(
        INFO, "get_io", CgiBinding("/stereo/io.json", reply=JsonReply()), result=str, access="admin", effect="read"
    )
    get_params = Operation(
        INFO,
        "get_params",
        CgiBinding("/stereo/params.json", reply=JsonReply()),
        result=dict[str, Any],
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class PeopleCounter3DLegacyApi(SyncApi):
    """3D people counter API (Old version) (``3d-people-counter-legacy``)."""

    INFO = INFO

    def get_counts(self, *, request_options: RequestOptions | None = None) -> Counts:
        """Request real-time counting data.

        Deprecated.

        Access: admin.
        """
        return self._run(OPS.get_counts, None, {}, request_options)

    def export_csv(
        self,
        *,
        resolution: ExportResolution | MISSING = MISSING,
        date: ExportDate | MISSING = MISSING,
        method: ExportMethod | MISSING = MISSING,
        export_method: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """List or download the stored statistics as CSV.

        Deprecated. The first CSV line describes the columns; the following lines hold ``Interval Start,
        Interval Start (Unixtime), In, Out`` per bin.

        Access: admin.
        """
        return self._run(
            OPS.export_csv,
            None,
            {"resolution": resolution, "date": date, "method": method, "export_method": export_method},
            request_options,
        )

    def export_json(
        self,
        *,
        resolution: ExportResolution | MISSING = MISSING,
        date: ExportDate | MISSING = MISSING,
        method: ExportMethod | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """List or download the stored statistics as JSON.

        Deprecated. The JSON structure is not documented, so the result is the parsed JSON document.

        Access: admin.
        """
        return self._run(
            OPS.export_json, None, {"resolution": resolution, "date": date, "method": method}, request_options
        )

    def get_fps(self, *, request_options: RequestOptions | None = None) -> Fps:
        """Return the current internal frame rate.

        Deprecated.

        Access: admin.
        """
        return self._run(OPS.get_fps, None, {}, request_options)

    def get_io(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the latest I/O signal.

        Deprecated. The docs show the reply as "True" or "False".

        Access: admin.
        """
        return self._run(OPS.get_io, None, {}, request_options)

    def get_params(self, *, request_options: RequestOptions | None = None) -> dict[str, Any]:
        """Get all parameters currently set.

        Deprecated.

        Access: admin.
        """
        return self._run(OPS.get_params, None, {}, request_options)


class AsyncPeopleCounter3DLegacyApi(AsyncApi):
    """3D people counter API (Old version) (``3d-people-counter-legacy``)."""

    INFO = INFO

    async def get_counts(self, *, request_options: RequestOptions | None = None) -> Counts:
        """Request real-time counting data.

        Deprecated.

        Access: admin.
        """
        return await self._run(OPS.get_counts, None, {}, request_options)

    async def export_csv(
        self,
        *,
        resolution: ExportResolution | MISSING = MISSING,
        date: ExportDate | MISSING = MISSING,
        method: ExportMethod | MISSING = MISSING,
        export_method: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """List or download the stored statistics as CSV.

        Deprecated. The first CSV line describes the columns; the following lines hold ``Interval Start,
        Interval Start (Unixtime), In, Out`` per bin.

        Access: admin.
        """
        return await self._run(
            OPS.export_csv,
            None,
            {"resolution": resolution, "date": date, "method": method, "export_method": export_method},
            request_options,
        )

    async def export_json(
        self,
        *,
        resolution: ExportResolution | MISSING = MISSING,
        date: ExportDate | MISSING = MISSING,
        method: ExportMethod | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """List or download the stored statistics as JSON.

        Deprecated. The JSON structure is not documented, so the result is the parsed JSON document.

        Access: admin.
        """
        return await self._run(
            OPS.export_json, None, {"resolution": resolution, "date": date, "method": method}, request_options
        )

    async def get_fps(self, *, request_options: RequestOptions | None = None) -> Fps:
        """Return the current internal frame rate.

        Deprecated.

        Access: admin.
        """
        return await self._run(OPS.get_fps, None, {}, request_options)

    async def get_io(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the latest I/O signal.

        Deprecated. The docs show the reply as "True" or "False".

        Access: admin.
        """
        return await self._run(OPS.get_io, None, {}, request_options)

    async def get_params(self, *, request_options: RequestOptions | None = None) -> dict[str, Any]:
        """Get all parameters currently set.

        Deprecated.

        Access: admin.
        """
        return await self._run(OPS.get_params, None, {}, request_options)
