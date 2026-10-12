# GENERATED from specs/apis/network-video/recorded-guard-tour.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Record, play, pause, resume, stop, list, modify and remove recorded PTZ tours.

Docs: https://developer.axis.com/vapix/network-video/guard-tour-api/
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

SchemaVersion = Annotated[int, Field(ge=1)]
RecordedTourId = Annotated[int, Field(ge=0, le=9999)]
RecordedTourName = Annotated[str, Field(max_length=31, pattern="^[a-zA-Z0-9._-]*$")]
TourStatus = Literal["playing", "recording", "stopped"]


class SchemaVersionInfo(Model):
    version_number: str = Field(validation_alias="versionNumber", serialization_alias="versionNumber")
    """The version of the XML schema in the form [major].[minor], for example 1.0."""
    deprecated: bool | None = None
    """When true the schema version is deprecated and should not be used. Defaults to false."""


class SchemaVersions(Model):
    versions: list[SchemaVersionInfo] | None = None


class RecordedTourInfo(Model):
    recording_id: RecordedTourId = Field(validation_alias="recordingId", serialization_alias="recordingId")
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """Descriptive name of the recorded tour."""
    status: TourStatus
    camera: int | None = None
    """Video channel or view area."""
    default_loop_delay: int | None = Field(
        default=None, validation_alias="defaultLoopDelay", serialization_alias="defaultLoopDelay"
    )
    """Seconds to wait before continuing a looped tour."""


class RecordedTours(Model):
    tours: list[RecordedTourInfo] | None = None


class RecordedTourRef(Model):
    recording_id: RecordedTourId = Field(validation_alias="recordingId", serialization_alias="recordingId")


class ListRecordedToursRequest(Model):
    schemaversion: SchemaVersion
    camera: int | None = Field(default=None, ge=1)
    """Video channel or view area. If omitted, tours from all channels are listed."""
    recordedtourid: RecordedTourId | None = None
    """ID of the recorded tour to list. If omitted, all recorded tours are listed."""


class RecordTourRequest(Model):
    schemaversion: SchemaVersion
    nicename: RecordedTourName | None = None
    camera: int = Field(ge=1)
    """The video channel or view area."""
    recordedtourid: RecordedTourId | None = None
    """Recorded tour ID, unique per tour. If omitted, an ID is generated."""


class StopRecordingRequest(Model):
    schemaversion: SchemaVersion
    recordedtourid: RecordedTourId | None = None
    """ID of the recorded tour to stop. If omitted, all ongoing recordings are stopped."""


class PlayTourRequest(Model):
    schemaversion: SchemaVersion
    recordedtourid: RecordedTourId
    """ID of the recorded tour to play."""
    loop: Literal[0, 1] | None = None
    """0 plays the tour once. 1 loops until stopped, pausing ``loopdelay`` seconds at the end point before restarting. Default: 0."""
    loopdelay: int | None = Field(default=None, ge=0, le=9999)
    """Seconds to wait before continuing the loop. If omitted, the ``defaultloopdelay`` set by ``modify_tour`` is used."""


class StopPlaybackRequest(Model):
    schemaversion: SchemaVersion
    recordedtourid: RecordedTourId | None = None
    """ID of the recorded tour to stop. If omitted, playback of all recorded tours is stopped."""


class PausePlaybackRequest(Model):
    schemaversion: SchemaVersion
    recordedtourid: RecordedTourId | None = None
    """ID of the recorded tour to pause. If omitted, all playing recorded tours are paused."""


class ResumePlaybackRequest(Model):
    schemaversion: SchemaVersion
    recordedtourid: RecordedTourId | None = None
    """ID of the paused recorded tour to resume. If omitted, all paused recorded tours are resumed."""


class ModifyTourRequest(Model):
    schemaversion: SchemaVersion
    recordedtourid: RecordedTourId
    """ID of the recorded tour to modify."""
    nicename: RecordedTourName | None = None
    """New descriptive name. If omitted, the current name is kept."""
    defaultloopdelay: int | None = Field(default=None, ge=0, le=9999)
    """New loop delay in seconds. If omitted, the current delay is kept. The default is 60."""


class RemoveTourRequest(Model):
    schemaversion: SchemaVersion
    recordedtourid: RecordedTourId
    """ID of the recorded tour to remove."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/recordedtour/getschemaversions.cgi"

INFO = ApiInfo(
    id="recorded-guard-tour",
    name="Recorded tour API",
    family=Family.CGI,
    discovery=(
        ApiDiscovery("recorded-guard-tour"),
        ParamDiscovery("Properties.GuardTour.RecordedTour", "yes"),
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/guard-tour-api/",),
    errors={
        10: ErrorCode("Invalid recorded tour ID.", "invalid_argument"),
        20: ErrorCode("The provided recorded tour ID is not unique.", "invalid_argument"),
        30: ErrorCode(
            "Maximum number of recorded tours is already reached; a new tour cannot be recorded.", "unavailable"
        ),
        40: ErrorCode("No space left; a new tour cannot be recorded.", "unavailable"),
        50: ErrorCode("Invalid argument; the provided value is not supported.", "invalid_argument"),
        60: ErrorCode("Invalid state."),
        70: ErrorCode("Missing or invalid XML schema version.", "invalid_argument"),
        100: ErrorCode("General error.", "internal"),
    },
)


class OPS:
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            PATH,
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "versions",
                            source="path",
                            name="SchemaVersion",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("versionNumber", source="child", name="VersionNumber"),
                                    XmlField("deprecated", source="child", name="Deprecated"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetSchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="viewer",
        effect="read",
    )
    list_recorded_tours = Operation(
        INFO,
        "list_recorded_tours",
        CgiBinding(
            "/axis-cgi/recordedtour/list.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("camera"), CgiArg("recordedtourid")),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "tours",
                            source="path",
                            name="RecordingInformation",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("recordingId", source="child", name="RecordingId"),
                                    XmlField("niceName", source="child", name="NiceName"),
                                    XmlField("status", source="child", name="Status"),
                                    XmlField("camera", source="child", name="Camera"),
                                    XmlField("defaultLoopDelay", source="child", name="DefaultLoopDelay"),
                                )
                            ),
                        ),
                    ),
                    root="Success/ListSuccess",
                )
            ),
        ),
        params=ListRecordedToursRequest,
        result=RecordedTours,
        access="viewer",
        effect="read",
    )
    record_tour = Operation(
        INFO,
        "record_tour",
        CgiBinding(
            "/axis-cgi/recordedtour/record.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("nicename"), CgiArg("camera"), CgiArg("recordedtourid")),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("recordingId", source="child", name="RecordingId"),), root="Success/RecordSuccess"
                )
            ),
        ),
        params=RecordTourRequest,
        result=RecordedTourRef,
        access="operator",
        effect="action",
    )
    stop_recording = Operation(
        INFO,
        "stop_recording",
        CgiBinding(
            "/axis-cgi/recordedtour/stoprecording.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("recordedtourid")),
            reply=Xml(),
        ),
        params=StopRecordingRequest,
        access="operator",
        effect="action",
    )
    play_tour = Operation(
        INFO,
        "play_tour",
        CgiBinding(
            "/axis-cgi/recordedtour/play.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("recordedtourid"), CgiArg("loop"), CgiArg("loopdelay")),
            reply=Xml(),
        ),
        params=PlayTourRequest,
        access="viewer",
        effect="action",
    )
    stop_playback = Operation(
        INFO,
        "stop_playback",
        CgiBinding(
            "/axis-cgi/recordedtour/stopplayback.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("recordedtourid")),
            reply=Xml(),
        ),
        params=StopPlaybackRequest,
        access="viewer",
        effect="action",
    )
    pause_playback = Operation(
        INFO,
        "pause_playback",
        CgiBinding(
            "/axis-cgi/recordedtour/pause.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("recordedtourid")),
            reply=Xml(),
        ),
        params=PausePlaybackRequest,
        access="viewer",
        effect="action",
    )
    resume_playback = Operation(
        INFO,
        "resume_playback",
        CgiBinding(
            "/axis-cgi/recordedtour/resume.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("recordedtourid")),
            reply=Xml(),
        ),
        params=ResumePlaybackRequest,
        access="viewer",
        effect="action",
    )
    modify_tour = Operation(
        INFO,
        "modify_tour",
        CgiBinding(
            "/axis-cgi/recordedtour/modify.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("recordedtourid"), CgiArg("nicename"), CgiArg("defaultloopdelay")),
            reply=Xml(),
        ),
        params=ModifyTourRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    remove_tour = Operation(
        INFO,
        "remove_tour",
        CgiBinding(
            "/axis-cgi/recordedtour/remove.cgi",
            method="POST",
            args=(CgiArg("schemaversion"), CgiArg("recordedtourid")),
            reply=Xml(),
        ),
        params=RemoveTourRequest,
        access="operator",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class RecordedTourApi(SyncApi):
    """Recorded tour API (``recorded-guard-tour``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Get the supported XML schema versions and whether they are deprecated. Access: viewer."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def list_recorded_tours(
        self,
        schemaversion: SchemaVersion,
        *,
        camera: int | MISSING = MISSING,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordedTours:
        """List recorded tours. Access: viewer."""
        return self._run(
            OPS.list_recorded_tours,
            None,
            {"schemaversion": schemaversion, "camera": camera, "recordedtourid": recordedtourid},
            request_options,
        )

    def record_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        nicename: RecordedTourName | MISSING = MISSING,
        camera: int,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordedTourRef:
        """Start recording a tour; any running guard tour on the channel is stopped.

        Stop the recording with ``stop_recording``. The returned ID identifies the new tour.

        Access: operator.
        """
        return self._run(
            OPS.record_tour,
            None,
            {"schemaversion": schemaversion, "nicename": nicename, "camera": camera, "recordedtourid": recordedtourid},
            request_options,
        )

    def stop_recording(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Stop an ongoing recording. Access: operator."""
        self._run(
            OPS.stop_recording,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid},
            request_options,
        )

    def play_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        recordedtourid: RecordedTourId,
        loop: Literal[0, 1] | MISSING = MISSING,
        loopdelay: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Play a recorded tour.

        A running playback on the same channel is stopped. Other PTZ operations with lower priority than the
        recorded tour are stopped.

        Access: viewer.
        """
        self._run(
            OPS.play_tour,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid, "loop": loop, "loopdelay": loopdelay},
            request_options,
        )

    def stop_playback(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Stop playback of a recorded tour. Access: viewer."""
        self._run(
            OPS.stop_playback, None, {"schemaversion": schemaversion, "recordedtourid": recordedtourid}, request_options
        )

    def pause_playback(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Pause playback of a recorded tour.

        Resume with ``resume_playback``.

        Access: viewer.
        """
        self._run(
            OPS.pause_playback,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid},
            request_options,
        )

    def resume_playback(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Resume playback of a paused recorded tour. Access: viewer."""
        self._run(
            OPS.resume_playback,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid},
            request_options,
        )

    def modify_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        recordedtourid: RecordedTourId,
        nicename: RecordedTourName | MISSING = MISSING,
        defaultloopdelay: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Change the name and loop delay of a recorded tour.

        The tour must be inactive, so recording and playback must be stopped.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.modify_tour,
            None,
            {
                "schemaversion": schemaversion,
                "recordedtourid": recordedtourid,
                "nicename": nicename,
                "defaultloopdelay": defaultloopdelay,
            },
            request_options,
        )

    def remove_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        recordedtourid: RecordedTourId,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Remove a recorded tour.

        The tour must be inactive, so recording and playback must be stopped.

        Access: operator.
        """
        self._run(
            OPS.remove_tour, None, {"schemaversion": schemaversion, "recordedtourid": recordedtourid}, request_options
        )


class AsyncRecordedTourApi(AsyncApi):
    """Recorded tour API (``recorded-guard-tour``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Get the supported XML schema versions and whether they are deprecated. Access: viewer."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def list_recorded_tours(
        self,
        schemaversion: SchemaVersion,
        *,
        camera: int | MISSING = MISSING,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordedTours:
        """List recorded tours. Access: viewer."""
        return await self._run(
            OPS.list_recorded_tours,
            None,
            {"schemaversion": schemaversion, "camera": camera, "recordedtourid": recordedtourid},
            request_options,
        )

    async def record_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        nicename: RecordedTourName | MISSING = MISSING,
        camera: int,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordedTourRef:
        """Start recording a tour; any running guard tour on the channel is stopped.

        Stop the recording with ``stop_recording``. The returned ID identifies the new tour.

        Access: operator.
        """
        return await self._run(
            OPS.record_tour,
            None,
            {"schemaversion": schemaversion, "nicename": nicename, "camera": camera, "recordedtourid": recordedtourid},
            request_options,
        )

    async def stop_recording(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Stop an ongoing recording. Access: operator."""
        await self._run(
            OPS.stop_recording,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid},
            request_options,
        )

    async def play_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        recordedtourid: RecordedTourId,
        loop: Literal[0, 1] | MISSING = MISSING,
        loopdelay: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Play a recorded tour.

        A running playback on the same channel is stopped. Other PTZ operations with lower priority than the
        recorded tour are stopped.

        Access: viewer.
        """
        await self._run(
            OPS.play_tour,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid, "loop": loop, "loopdelay": loopdelay},
            request_options,
        )

    async def stop_playback(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Stop playback of a recorded tour. Access: viewer."""
        await self._run(
            OPS.stop_playback, None, {"schemaversion": schemaversion, "recordedtourid": recordedtourid}, request_options
        )

    async def pause_playback(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Pause playback of a recorded tour.

        Resume with ``resume_playback``.

        Access: viewer.
        """
        await self._run(
            OPS.pause_playback,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid},
            request_options,
        )

    async def resume_playback(
        self,
        schemaversion: SchemaVersion,
        *,
        recordedtourid: RecordedTourId | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Resume playback of a paused recorded tour. Access: viewer."""
        await self._run(
            OPS.resume_playback,
            None,
            {"schemaversion": schemaversion, "recordedtourid": recordedtourid},
            request_options,
        )

    async def modify_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        recordedtourid: RecordedTourId,
        nicename: RecordedTourName | MISSING = MISSING,
        defaultloopdelay: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Change the name and loop delay of a recorded tour.

        The tour must be inactive, so recording and playback must be stopped.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.modify_tour,
            None,
            {
                "schemaversion": schemaversion,
                "recordedtourid": recordedtourid,
                "nicename": nicename,
                "defaultloopdelay": defaultloopdelay,
            },
            request_options,
        )

    async def remove_tour(
        self,
        *,
        schemaversion: SchemaVersion,
        recordedtourid: RecordedTourId,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Remove a recorded tour.

        The tour must be inactive, so recording and playback must be stopped.

        Access: operator.
        """
        await self._run(
            OPS.remove_tour, None, {"schemaversion": schemaversion, "recordedtourid": recordedtourid}, request_options
        )
