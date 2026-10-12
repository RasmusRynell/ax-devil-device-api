# GENERATED from specs/apis/applications/demographic-identifier.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Demographic Identifier ACAP: live and ended face tracks (estimated gender, age and box size), FPS, historical statistics, service restart and camera reboot.

Docs: https://developer.axis.com/vapix/applications/demographic-identifier-api/
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


class LiveTrack(Model):
    time_start: float
    """Time of the first face observation, in seconds, UTC."""
    time_end: float
    """Time of the last face observation, in seconds."""
    gender_average: Literal[-1, 1]
    """-1 for a female estimate and 1 for a male estimate, on average since time_start."""
    age_average: int
    """Estimated age over the track since time_start."""
    boxsize_average: int
    """Average box size over the track since time_start."""
    gender_last: Literal[-1, 1]
    """-1 for a female guess and 1 for a male guess on the last observation."""
    age_last: int
    """Estimated age on the last observation."""
    boxsize_last: int
    """Box size on the last observation."""


class EndedTrack(Model):
    time_start: float
    """Time of the first face observation, in seconds, UTC."""
    time_end: float
    """Time of the last face observation, in seconds."""
    gender_average: Literal[-1, 1]
    """-1 for a female estimate and 1 for a male estimate, on average since time_start."""
    age_average: int
    """Estimated age over the track since time_start."""
    boxsize_average: int
    """Average box size over the track since time_start."""


class LiveTracks(Model):
    tracks: list[LiveTrack]


class EndedTracks(Model):
    time_start: float
    """Start of the covered time window."""
    time_end: float
    """End of the covered time window."""
    tracks: list[EndedTrack]


class LiveTracksResult(Model):
    live: LiveTracks


class EndedTracksResult(Model):
    ended: EndedTracks


class LiveAndEndedTracksResult(Model):
    live: LiveTracks
    ended: EndedTracks


class Fps(Model):
    fps: float
    """FPS used by the Demographics algorithm."""


DateSelection = Annotated[str, Field(pattern="^(all|[0-9]{8}(-[0-9]{8})?|[0-9]{8}(,[0-9]{8})*)$")]


class TracksWindow(Model):
    time: int | None = None
    """Amount of time, in seconds, to include in the return. The default is 15 minutes (900 s). Default: 900."""


class GetStatisticsRequest(Model):
    date: DateSelection | None = None
    """Default: 'all'."""
    res: Literal["15m", "1h", "24h"] | None = None
    """15m = 15 minute bins (default), 1h = 1 hour bins, 24h = 1 day bins. Default: '15m'."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/demographics/.api"

INFO = ApiInfo(
    id="demographic-identifier",
    name="Demographic identifier API",
    family=Family.CGI,
    docs=("https://developer.axis.com/vapix/applications/demographic-identifier-api/",),
)


class OPS:
    get_live_tracks = Operation(
        INFO,
        "get_live_tracks",
        CgiBinding(PATH, fixed_query=(("tracks-live.json", ""),), reply=JsonReply()),
        result=LiveTracksResult,
        access="admin",
        effect="read",
    )
    get_ended_tracks = Operation(
        INFO,
        "get_ended_tracks",
        CgiBinding(PATH, fixed_query=(("tracks-ended.json", ""),), args=(CgiArg("time"),), reply=JsonReply()),
        params=TracksWindow,
        result=EndedTracksResult,
        access="admin",
        effect="read",
    )
    get_live_and_ended_tracks = Operation(
        INFO,
        "get_live_and_ended_tracks",
        CgiBinding(PATH, fixed_query=(("tracks-live-and-ended.json", ""),), args=(CgiArg("time"),), reply=JsonReply()),
        params=TracksWindow,
        result=LiveAndEndedTracksResult,
        access="admin",
        effect="read",
    )
    get_fps = Operation(
        INFO,
        "get_fps",
        CgiBinding("/demographics/.api", fixed_query=(("fps.json", ""),), reply=JsonReply()),
        result=Fps,
        access="admin",
        effect="read",
    )
    restart_service = Operation(
        INFO,
        "restart_service",
        CgiBinding("/demographics/.apioperator", fixed_query=(("restart", ""),), reply=Text()),
        access="operator",
        effect="action",
    )
    reboot_camera = Operation(
        INFO,
        "reboot_camera",
        CgiBinding("/demographics/.apioperator", fixed_query=(("reboot", ""),), reply=Text()),
        access="operator",
        effect="action",
    )
    get_statistics = Operation(
        INFO,
        "get_statistics",
        CgiBinding(PATH, fixed_query=(("export-json", ""),), args=(CgiArg("date"), CgiArg("res")), reply=JsonReply()),
        params=GetStatisticsRequest,
        result=Any,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class DemographicIdentifierApi(SyncApi):
    """Demographic identifier API (``demographic-identifier``)."""

    INFO = INFO

    def get_live_tracks(self, *, request_options: RequestOptions | None = None) -> LiveTracksResult:
        """Return the live face tracks (boxes) currently active in the video stream. Access: admin."""
        return self._run(OPS.get_live_tracks, None, {}, request_options)

    def get_ended_tracks(
        self, *, time: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> EndedTracksResult:
        """Return previously detected (ended) tracks. Access: admin."""
        return self._run(OPS.get_ended_tracks, None, {"time": time}, request_options)

    def get_live_and_ended_tracks(
        self, *, time: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> LiveAndEndedTracksResult:
        """Return both the live tracks and the ended tracks. Access: admin."""
        return self._run(OPS.get_live_and_ended_tracks, None, {"time": time}, request_options)

    def get_fps(self, *, request_options: RequestOptions | None = None) -> Fps:
        """Check the FPS used by the Demographics algorithm. Access: admin."""
        return self._run(OPS.get_fps, None, {}, request_options)

    def restart_service(self, *, request_options: RequestOptions | None = None) -> None:
        """Restart the Demographics service. Access: operator."""
        self._run(OPS.restart_service, None, {}, request_options)

    def reboot_camera(self, *, request_options: RequestOptions | None = None) -> None:
        """Reboot the camera. Access: operator."""
        self._run(OPS.reboot_camera, None, {}, request_options)

    def get_statistics(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Literal["15m", "1h", "24h"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Return historical data in JSON format.

        The docs do not describe the JSON structure, so the result is the parsed JSON document.

        Access: admin.
        """
        return self._run(OPS.get_statistics, None, {"date": date, "res": res}, request_options)


class AsyncDemographicIdentifierApi(AsyncApi):
    """Demographic identifier API (``demographic-identifier``)."""

    INFO = INFO

    async def get_live_tracks(self, *, request_options: RequestOptions | None = None) -> LiveTracksResult:
        """Return the live face tracks (boxes) currently active in the video stream. Access: admin."""
        return await self._run(OPS.get_live_tracks, None, {}, request_options)

    async def get_ended_tracks(
        self, *, time: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> EndedTracksResult:
        """Return previously detected (ended) tracks. Access: admin."""
        return await self._run(OPS.get_ended_tracks, None, {"time": time}, request_options)

    async def get_live_and_ended_tracks(
        self, *, time: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> LiveAndEndedTracksResult:
        """Return both the live tracks and the ended tracks. Access: admin."""
        return await self._run(OPS.get_live_and_ended_tracks, None, {"time": time}, request_options)

    async def get_fps(self, *, request_options: RequestOptions | None = None) -> Fps:
        """Check the FPS used by the Demographics algorithm. Access: admin."""
        return await self._run(OPS.get_fps, None, {}, request_options)

    async def restart_service(self, *, request_options: RequestOptions | None = None) -> None:
        """Restart the Demographics service. Access: operator."""
        await self._run(OPS.restart_service, None, {}, request_options)

    async def reboot_camera(self, *, request_options: RequestOptions | None = None) -> None:
        """Reboot the camera. Access: operator."""
        await self._run(OPS.reboot_camera, None, {}, request_options)

    async def get_statistics(
        self,
        *,
        date: DateSelection | MISSING = MISSING,
        res: Literal["15m", "1h", "24h"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Return historical data in JSON format.

        The docs do not describe the JSON structure, so the result is the parsed JSON document.

        Access: admin.
        """
        return await self._run(OPS.get_statistics, None, {"date": date, "res": res}, request_options)
