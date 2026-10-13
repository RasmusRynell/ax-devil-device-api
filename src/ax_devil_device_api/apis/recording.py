# GENERATED from specs/apis/network-video/recording.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage edge recordings, namely continuous recording profiles, searching, starting, stopping and removing recordings.

Docs: https://developer.axis.com/vapix/network-video/edge-storage-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Stream, Xml
from .._protocols.xmlmap import XmlField, XmlMap, XmlStatusError
from .._runtime.driver import AsyncStreamResult, StreamResult
from .._streams import Part
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

RecordingType = Literal["triggered", "scheduled", "continuous"]
RecordingStatus = Literal["recording", "completed", "unknown"]


class ContinuousProfile(Model):
    profile: int
    """The number of the new continuous recording profile."""


class ContinuousConfiguration(Model):
    profile: int
    """The profile number."""
    diskid: str | None = None
    """The ID of the disk where the recording is stored."""
    options: str | None = None
    """The stream options."""
    eventid: str | None = None
    """The event ID of the profile."""


class ContinuousConfigurations(Model):
    configurations: list[ContinuousConfiguration] | None = None


class RecordingVideo(Model):
    mimetype: str | None = None
    """Video MIME type, for example image/jpeg or video/x-h264."""
    source: str | None = None
    """Video source."""
    framerate: str | None = None
    """Frame rate."""
    resolution: str | None = None
    """Video resolution."""
    width: int | None = None
    """Image width in pixels."""
    height: int | None = None
    """Image height in pixels."""


class RecordingAudio(Model):
    mimetype: str | None = None
    """Audio MIME type."""
    source: str | None = None
    """Audio source."""
    bitrate: int | None = None
    """Bit rate."""
    samplerate: int | None = None
    """Sample rate."""


class RecordingInfo(Model):
    diskid: str
    """The ID of the disk the recording is stored on."""
    recordingid: str
    """The recording ID."""
    recordinggroupid: str | None = None
    """The recording group used to create the recording."""
    starttime: str | None = None
    """Start time of the recording (UTC)."""
    starttimelocal: str | None = None
    """Start time of the recording (local time)."""
    stoptime: str | None = None
    """Stop time of the recording (UTC); empty while the recording is ongoing."""
    stoptimelocal: str | None = None
    """Stop time of the recording (local time); empty while the recording is ongoing."""
    recordingtype: RecordingType | None = None
    eventid: str | None = None
    """Name of the event that initiated the recording."""
    eventtrigger: str | None = None
    """The trigger of the event that initiated the recording."""
    recordingstatus: RecordingStatus | None = None
    source: str | None = None
    """Multichannel video encoders only: the video channel used for the recording."""
    video: list[RecordingVideo] | None = None
    audio: list[RecordingAudio] | None = None


class RecordingList(Model):
    total_number_of_recordings: int | None = Field(
        default=None, validation_alias="totalNumberOfRecordings", serialization_alias="totalNumberOfRecordings"
    )
    """The number of recordings on all attached disks, or on the given disk when diskid is used."""
    number_of_recordings: int | None = Field(
        default=None, validation_alias="numberOfRecordings", serialization_alias="numberOfRecordings"
    )
    """The number of matched recordings, without regard to startatresultnumber and maxnumberofresults."""
    recordings: list[RecordingInfo] | None = None


class EventIds(Model):
    event_ids: list[str] | None = Field(default=None, validation_alias="eventIds", serialization_alias="eventIds")


class RecordingSources(Model):
    sources: list[str] | None = None


class StartedRecording(Model):
    recordingid: str
    """The ID of the started recording."""


class AddContinuousConfigurationRequest(Model):
    diskid: str
    """The ID of the disk to record to, for example SD_DISK."""
    options: str
    """Stream options for the recording as plain text, for example ``streamprofile=MyProfile`` or other image URL settings. The client percent-encodes them."""
    eventid: str | None = None
    """The event ID that classifies the recording. Used with ``list_recordings`` to select recordings from this profile. Default: 'continuous'."""


class ListContinuousConfigurationsRequest(Model):
    profile: int | None = None
    """The profile to list. If omitted, all profiles are listed."""


class RemoveContinuousConfigurationRequest(Model):
    profile: int
    """The profile number from ``add_continuous_configuration`` or ``list_continuous_configurations``."""


class ListRecordingsRequest(Model):
    recordingid: str | None = None
    """"all" or a recording ID."""
    maxnumberofresults: int | None = Field(default=None, ge=1)
    """Maximum number of recordings returned."""
    startatresultnumber: int | None = Field(default=None, ge=1)
    """Start the result on the n:th recording."""
    recordinggroupid: str | None = None
    """Include recordings that belong to this recording group."""
    eventid: str | None = None
    """Name of the event that triggered the recording."""
    diskid: str | None = None
    """The ID of the disk to search."""
    starttime: str | None = None
    """Include recordings with any part on or after this time. UTC ISO 8601 combined date and time, ``<yyyy>-<mm>-<dd>T<HH>:<MM>:<SS>[.<mmmm>]Z`` or with a ``±hh:mm`` offset."""
    stoptime: str | None = None
    """Include recordings with any part on or before this time. UTC ISO 8601 combined date and time, ``<yyyy>-<mm>-<dd>T<HH>:<MM>:<SS>[.<mmmm>]Z`` or with a ``±hh:mm`` offset."""
    sortorder: Literal["ascending", "descending"] | None = None
    """Sort by recording start time. Default: 'descending'."""
    source: str | None = None
    """Multichannel video encoders: "Quad" or a channel number (product dependent)."""


class ListEventIdsRequest(Model):
    diskid: str | None = None
    """Only list event IDs of recordings on this disk."""


class ListRecordingSourcesRequest(Model):
    diskid: str | None = None
    """Only list sources of recordings on this disk."""


class StartRecordingRequest(Model):
    diskid: str
    """The ID of the disk to record to, for example SD_DISK."""
    options: str | None = None
    """Stream options as plain text, for example ``streamprofile=MyProfile``. The system default is used if omitted."""


class StopRecordingRequest(Model):
    recordingid: str
    """The ID of the recording to stop."""


class RemoveRecordingsRequest(Model):
    recordingid: str | None = None
    """"all" or comma-separated recording IDs."""
    recordinggroupid: str | None = None
    """Remove all non-ongoing recordings of a recording group. Cannot be combined with recordingid, beforetime, eventid or source."""
    diskid: str | None = None
    """The ID of the disk to remove recordings from."""
    beforetime: str | None = None
    """Remove all recordings with any part on or before this time (UTC ISO 8601). Cannot be combined with recordingid or recordinggroupid."""
    eventid: str | None = None
    """Remove recordings triggered by this event ID. Cannot be combined with recordingid or recordinggroupid."""
    source: str | None = None
    """Remove recordings from this video source. Cannot be combined with recordingid or recordinggroupid."""


class PlayRecordingRequest(Model):
    recordingid: str
    """The ID of the recording to play."""
    mediatype: Literal["video", "audio"] | None = None
    """What to play. Default: video."""
    rate: str | None = Field(default=None, pattern="^(max|[0-9]+/[0-9]+)$")
    """The playback rate: ``max`` (as fast as possible) or a fraction numerator/denominator of the original rate."""
    starttime: str | None = None
    """Playback start time (UTC ISO 8601); playback starts at the frame closest to it. Default is the beginning."""
    stoptime: str | None = None
    """Playback stop time (UTC ISO 8601); playback stops at the frame closest to it. Default is the end."""


class PlayRecordingRtspRequest(Model):
    recordingid: str
    """The ID of the recording to play."""
    pull: bool | None = None
    """Stream as fast as possible; only useful when tunneling RTSP over HTTP. Default: off."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/record/continuous/addconfiguration.cgi"

INFO = ApiInfo(
    id="recording",
    name="Recording API (Edge storage)",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.LocalStorage.LocalStorage", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/edge-storage-api/",),
)


class OPS:
    add_continuous_configuration = Operation(
        INFO,
        "add_continuous_configuration",
        CgiBinding(
            PATH,
            args=(CgiArg("diskid"), CgiArg("options"), CgiArg("eventid")),
            reply=Xml(
                map=XmlMap(fields=(XmlField("profile"),), root="configure"),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="errormsg"),
            ),
        ),
        params=AddContinuousConfigurationRequest,
        result=ContinuousProfile,
        access="operator",
        effect="write",
        write="create",
    )
    list_continuous_configurations = Operation(
        INFO,
        "list_continuous_configurations",
        CgiBinding(
            "/axis-cgi/record/continuous/listconfiguration.cgi",
            args=(CgiArg("profile"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "configurations",
                            source="path",
                            name="continuousrecordingconfiguration",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("profile"),
                                    XmlField("diskid"),
                                    XmlField("options"),
                                    XmlField("eventid"),
                                )
                            ),
                        ),
                    ),
                    root="continuousrecordingconfigurations",
                )
            ),
        ),
        params=ListContinuousConfigurationsRequest,
        result=ContinuousConfigurations,
        access="viewer",
        effect="read",
    )
    remove_continuous_configuration = Operation(
        INFO,
        "remove_continuous_configuration",
        CgiBinding(
            "/axis-cgi/record/continuous/removeconfiguration.cgi",
            args=(CgiArg("profile"),),
            reply=Xml(status_error=XmlStatusError(attribute="result", value="ERROR", message="errormsg")),
        ),
        params=RemoveContinuousConfigurationRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    list_recordings = Operation(
        INFO,
        "list_recordings",
        CgiBinding(
            "/axis-cgi/record/list.cgi",
            args=(
                CgiArg("recordingid"),
                CgiArg("maxnumberofresults"),
                CgiArg("startatresultnumber"),
                CgiArg("recordinggroupid"),
                CgiArg("eventid"),
                CgiArg("diskid"),
                CgiArg("starttime"),
                CgiArg("stoptime"),
                CgiArg("sortorder"),
                CgiArg("source"),
            ),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("totalNumberOfRecordings", name="totalnumberofrecordings"),
                        XmlField("numberOfRecordings", name="numberofrecordings"),
                        XmlField(
                            "recordings",
                            source="path",
                            name="recording",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("diskid"),
                                    XmlField("recordingid"),
                                    XmlField("recordinggroupid"),
                                    XmlField("starttime"),
                                    XmlField("starttimelocal"),
                                    XmlField("stoptime"),
                                    XmlField("stoptimelocal"),
                                    XmlField("recordingtype"),
                                    XmlField("eventid"),
                                    XmlField("eventtrigger"),
                                    XmlField("recordingstatus"),
                                    XmlField("source"),
                                    XmlField(
                                        "video",
                                        source="path",
                                        many=True,
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("mimetype"),
                                                XmlField("source"),
                                                XmlField("framerate"),
                                                XmlField("resolution"),
                                                XmlField("width"),
                                                XmlField("height"),
                                            )
                                        ),
                                    ),
                                    XmlField(
                                        "audio",
                                        source="path",
                                        many=True,
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("mimetype"),
                                                XmlField("source"),
                                                XmlField("bitrate"),
                                                XmlField("samplerate"),
                                            )
                                        ),
                                    ),
                                )
                            ),
                        ),
                    ),
                    root="recordings",
                )
            ),
        ),
        params=ListRecordingsRequest,
        result=RecordingList,
        access="viewer",
        effect="read",
    )
    list_event_ids = Operation(
        INFO,
        "list_event_ids",
        CgiBinding(
            "/axis-cgi/record/list.cgi",
            fixed_query=(("listentity", "eventid"),),
            args=(CgiArg("diskid"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("eventIds", source="path", name="eventid", many=True),), root="eventids")
            ),
        ),
        params=ListEventIdsRequest,
        result=EventIds,
        access="viewer",
        effect="read",
    )
    list_recording_sources = Operation(
        INFO,
        "list_recording_sources",
        CgiBinding(
            "/axis-cgi/record/list.cgi",
            fixed_query=(("listentity", "source"),),
            args=(CgiArg("diskid"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("sources", source="path", name="source", many=True),), root="sources")
            ),
        ),
        params=ListRecordingSourcesRequest,
        result=RecordingSources,
        access="viewer",
        effect="read",
    )
    start_recording = Operation(
        INFO,
        "start_recording",
        CgiBinding(
            "/axis-cgi/record/record.cgi",
            args=(CgiArg("diskid"), CgiArg("options")),
            reply=Xml(
                map=XmlMap(fields=(XmlField("recordingid"),), root="record"),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="errormsg"),
            ),
        ),
        params=StartRecordingRequest,
        result=StartedRecording,
        access="operator",
        effect="action",
    )
    stop_recording = Operation(
        INFO,
        "stop_recording",
        CgiBinding(
            "/axis-cgi/record/stop.cgi",
            args=(CgiArg("recordingid"),),
            reply=Xml(status_error=XmlStatusError(attribute="result", value="ERROR", message="errormsg")),
        ),
        params=StopRecordingRequest,
        access="operator",
        effect="action",
    )
    remove_recordings = Operation(
        INFO,
        "remove_recordings",
        CgiBinding(
            "/axis-cgi/record/remove.cgi",
            args=(
                CgiArg("recordingid"),
                CgiArg("recordinggroupid"),
                CgiArg("diskid"),
                CgiArg("beforetime"),
                CgiArg("eventid"),
                CgiArg("source"),
            ),
            reply=Xml(status_error=XmlStatusError(attribute="result", value="ERROR", message="errormsg")),
        ),
        params=RemoveRecordingsRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    play_recording = Operation(
        INFO,
        "play_recording",
        CgiBinding(
            "/axis-cgi/record/play.cgi",
            args=(CgiArg("recordingid"), CgiArg("mediatype"), CgiArg("rate"), CgiArg("starttime"), CgiArg("stoptime")),
            reply=Stream("mjpeg"),
            stream=True,
        ),
        params=PlayRecordingRequest,
        access="viewer",
        effect="read",
    )
    play_recording_rtsp = Operation(
        INFO, "play_recording_rtsp", RtspBinding(), params=PlayRecordingRtspRequest, access="viewer", effect="read"
    )


# ---------------------------------------------------------------------------
# API classes


class RecordingApi(SyncApi):
    """Recording API (Edge storage) (``recording``)."""

    INFO = INFO

    def add_continuous_configuration(
        self,
        *,
        diskid: str,
        options: str,
        eventid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ContinuousProfile:
        """Add a continuous recording profile; recording starts when possible.

        Available if Properties.LocalStorage.ContinuousRecording=yes and
        Properties.LocalStorage.NbrOfContinuousRecordingProfiles > 0. An existing profile cannot be changed;
        remove it and add a new one instead.

        Access: operator.
        """
        return self._run(
            OPS.add_continuous_configuration,
            None,
            {"diskid": diskid, "options": options, "eventid": eventid},
            request_options,
        )

    def list_continuous_configurations(
        self, profile: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> ContinuousConfigurations:
        """List continuous recording profiles. Access: viewer."""
        return self._run(OPS.list_continuous_configurations, None, {"profile": profile}, request_options)

    def remove_continuous_configuration(self, profile: int, *, request_options: RequestOptions | None = None) -> None:
        """Stop and remove a continuous recording profile. Access: operator."""
        self._run(OPS.remove_continuous_configuration, None, {"profile": profile}, request_options)

    @overload
    def list_recordings(
        self, request: ListRecordingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> RecordingList: ...
    @overload
    def list_recordings(
        self,
        recordingid: str | MISSING = MISSING,
        /,
        *,
        maxnumberofresults: int | MISSING = MISSING,
        startatresultnumber: int | MISSING = MISSING,
        recordinggroupid: str | MISSING = MISSING,
        eventid: str | MISSING = MISSING,
        diskid: str | MISSING = MISSING,
        starttime: str | MISSING = MISSING,
        stoptime: str | MISSING = MISSING,
        sortorder: Literal["ascending", "descending"] | MISSING = MISSING,
        source: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordingList: ...
    def list_recordings(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> RecordingList:
        """Search for recordings and list information about the recordings found.

        With ``listentity=recording`` (the default) one of recordinggroupid, eventid, source, starttime,
        stoptime or recordingid is required. Pass ``recordingid="all"`` to list every recording.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ListRecordingsRequest):
            kwargs = {**dict(zip(("recordingid",), (request, *args), strict=False)), **kwargs}
            request = None
        return self._run(OPS.list_recordings, request, kwargs, request_options)

    def list_event_ids(
        self, diskid: str | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> EventIds:
        """List all event IDs used by recordings. Access: viewer."""
        return self._run(OPS.list_event_ids, None, {"diskid": diskid}, request_options)

    def list_recording_sources(
        self, diskid: str | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> RecordingSources:
        """List all sources in which recordings were found. Access: viewer."""
        return self._run(OPS.list_recording_sources, None, {"diskid": diskid}, request_options)

    def start_recording(
        self, diskid: str, *, options: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> StartedRecording:
        """Start a recording at once and return its recording ID.

        Deprecated; removed in AXIS OS 13. The recording must be stopped with ``stop_recording``.

        Access: operator.
        """
        return self._run(OPS.start_recording, None, {"diskid": diskid, "options": options}, request_options)

    def stop_recording(self, recordingid: str, *, request_options: RequestOptions | None = None) -> None:
        """Stop an active recording.

        Deprecated; removed in AXIS OS 13.

        Access: operator.
        """
        self._run(OPS.stop_recording, None, {"recordingid": recordingid}, request_options)

    @overload
    def remove_recordings(
        self, request: RemoveRecordingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def remove_recordings(
        self,
        recordingid: str | MISSING = MISSING,
        /,
        *,
        recordinggroupid: str | MISSING = MISSING,
        diskid: str | MISSING = MISSING,
        beforetime: str | MISSING = MISSING,
        eventid: str | MISSING = MISSING,
        source: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def remove_recordings(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Remove one or more recordings.

        Required if none of recordinggroupid, beforetime, eventid or source is given: recordingid. Active
        recordings matched by beforetime are stopped and then removed.

        Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, RemoveRecordingsRequest):
            kwargs = {**dict(zip(("recordingid",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.remove_recordings, request, kwargs, request_options)

    @overload
    def play_recording(
        self, request: PlayRecordingRequest, /, *, request_options: RequestOptions | None = None
    ) -> StreamResult[Part]: ...
    @overload
    def play_recording(
        self,
        recordingid: str,
        /,
        *,
        mediatype: Literal["video", "audio"] | MISSING = MISSING,
        rate: str | MISSING = MISSING,
        starttime: str | MISSING = MISSING,
        stoptime: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StreamResult[Part]: ...
    def play_recording(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> StreamResult[Part]:
        """Play an MJPEG recording as a stream (deprecated since AXIS OS 10.2).

        The stream has the same format as the live view stream. Only MJPEG recordings can be played this
        way; use ``play_recording_rtsp`` for other formats. Use the result as a context manager.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, PlayRecordingRequest):
            kwargs = {**dict(zip(("recordingid",), (request, *args), strict=False)), **kwargs}
            request = None
        return self._run(OPS.play_recording, request, kwargs, request_options)

    def play_recording_rtsp(
        self,
        recordingid: str,
        *,
        pull: bool | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL for playing a recording in any media format.

        Send PLAY to the URL. A ``Range`` header (``npt``, ``clock`` or ``smpte``) selects the part to play;
        that header is not part of the URL.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.play_recording_rtsp,
            {"recordingid": recordingid, "pull": pull},
            port=port,
            include_credentials=include_credentials,
        )


class AsyncRecordingApi(AsyncApi):
    """Recording API (Edge storage) (``recording``)."""

    INFO = INFO

    async def add_continuous_configuration(
        self,
        *,
        diskid: str,
        options: str,
        eventid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ContinuousProfile:
        """Add a continuous recording profile; recording starts when possible.

        Available if Properties.LocalStorage.ContinuousRecording=yes and
        Properties.LocalStorage.NbrOfContinuousRecordingProfiles > 0. An existing profile cannot be changed;
        remove it and add a new one instead.

        Access: operator.
        """
        return await self._run(
            OPS.add_continuous_configuration,
            None,
            {"diskid": diskid, "options": options, "eventid": eventid},
            request_options,
        )

    async def list_continuous_configurations(
        self, profile: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> ContinuousConfigurations:
        """List continuous recording profiles. Access: viewer."""
        return await self._run(OPS.list_continuous_configurations, None, {"profile": profile}, request_options)

    async def remove_continuous_configuration(
        self, profile: int, *, request_options: RequestOptions | None = None
    ) -> None:
        """Stop and remove a continuous recording profile. Access: operator."""
        await self._run(OPS.remove_continuous_configuration, None, {"profile": profile}, request_options)

    @overload
    async def list_recordings(
        self, request: ListRecordingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> RecordingList: ...
    @overload
    async def list_recordings(
        self,
        recordingid: str | MISSING = MISSING,
        /,
        *,
        maxnumberofresults: int | MISSING = MISSING,
        startatresultnumber: int | MISSING = MISSING,
        recordinggroupid: str | MISSING = MISSING,
        eventid: str | MISSING = MISSING,
        diskid: str | MISSING = MISSING,
        starttime: str | MISSING = MISSING,
        stoptime: str | MISSING = MISSING,
        sortorder: Literal["ascending", "descending"] | MISSING = MISSING,
        source: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordingList: ...
    async def list_recordings(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> RecordingList:
        """Search for recordings and list information about the recordings found.

        With ``listentity=recording`` (the default) one of recordinggroupid, eventid, source, starttime,
        stoptime or recordingid is required. Pass ``recordingid="all"`` to list every recording.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ListRecordingsRequest):
            kwargs = {**dict(zip(("recordingid",), (request, *args), strict=False)), **kwargs}
            request = None
        return await self._run(OPS.list_recordings, request, kwargs, request_options)

    async def list_event_ids(
        self, diskid: str | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> EventIds:
        """List all event IDs used by recordings. Access: viewer."""
        return await self._run(OPS.list_event_ids, None, {"diskid": diskid}, request_options)

    async def list_recording_sources(
        self, diskid: str | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> RecordingSources:
        """List all sources in which recordings were found. Access: viewer."""
        return await self._run(OPS.list_recording_sources, None, {"diskid": diskid}, request_options)

    async def start_recording(
        self, diskid: str, *, options: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> StartedRecording:
        """Start a recording at once and return its recording ID.

        Deprecated; removed in AXIS OS 13. The recording must be stopped with ``stop_recording``.

        Access: operator.
        """
        return await self._run(OPS.start_recording, None, {"diskid": diskid, "options": options}, request_options)

    async def stop_recording(self, recordingid: str, *, request_options: RequestOptions | None = None) -> None:
        """Stop an active recording.

        Deprecated; removed in AXIS OS 13.

        Access: operator.
        """
        await self._run(OPS.stop_recording, None, {"recordingid": recordingid}, request_options)

    @overload
    async def remove_recordings(
        self, request: RemoveRecordingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def remove_recordings(
        self,
        recordingid: str | MISSING = MISSING,
        /,
        *,
        recordinggroupid: str | MISSING = MISSING,
        diskid: str | MISSING = MISSING,
        beforetime: str | MISSING = MISSING,
        eventid: str | MISSING = MISSING,
        source: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def remove_recordings(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Remove one or more recordings.

        Required if none of recordinggroupid, beforetime, eventid or source is given: recordingid. Active
        recordings matched by beforetime are stopped and then removed.

        Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, RemoveRecordingsRequest):
            kwargs = {**dict(zip(("recordingid",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.remove_recordings, request, kwargs, request_options)

    @overload
    async def play_recording(
        self, request: PlayRecordingRequest, /, *, request_options: RequestOptions | None = None
    ) -> AsyncStreamResult[Part]: ...
    @overload
    async def play_recording(
        self,
        recordingid: str,
        /,
        *,
        mediatype: Literal["video", "audio"] | MISSING = MISSING,
        rate: str | MISSING = MISSING,
        starttime: str | MISSING = MISSING,
        stoptime: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AsyncStreamResult[Part]: ...
    async def play_recording(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AsyncStreamResult[Part]:
        """Play an MJPEG recording as a stream (deprecated since AXIS OS 10.2).

        The stream has the same format as the live view stream. Only MJPEG recordings can be played this
        way; use ``play_recording_rtsp`` for other formats. Use the result as a context manager.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, PlayRecordingRequest):
            kwargs = {**dict(zip(("recordingid",), (request, *args), strict=False)), **kwargs}
            request = None
        return await self._run(OPS.play_recording, request, kwargs, request_options)

    def play_recording_rtsp(
        self,
        recordingid: str,
        *,
        pull: bool | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL for playing a recording in any media format.

        Send PLAY to the URL. A ``Range`` header (``npt``, ``clock`` or ``smpte``) selects the part to play;
        that header is not part of the URL.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.play_recording_rtsp,
            {"recordingid": recordingid, "pull": pull},
            port=port,
            include_credentials=include_credentials,
        )
