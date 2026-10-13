# GENERATED from specs/apis/network-video/decoder2.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure and control playback on Axis decoders: media sources, sequences and views, player control, capabilities and line-out.

Docs: https://developer.axis.com/vapix/network-video/decoder2-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import FixedVersion, JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Pane(Model):
    """Where a media source is drawn in the view. The origin (0, 0) is the upper left corner of the view and (1, 1) the lower right."""

    left: float = Field(ge=0, le=1)
    """Left edge is 0, middle 0.5 and right edge 1."""
    right: float = Field(ge=0, le=1)
    """Left edge is 0, middle 0.5 and right edge 1."""
    top: float = Field(ge=0, le=1)
    """Top edge is 0, middle 0.5 and bottom edge 1."""
    bottom: float = Field(ge=0, le=1)
    """Top edge is 0, middle 0.5 and bottom edge 1."""


PlaybackEndAction = Literal["triggerError", "triggerFreezePlayback", "triggerNextView", "triggerRestartPlayback"]


class Segment(Model):
    """A pane, a media source and the end-of-playback action."""

    media_source_id: int = Field(validation_alias="mediaSourceId", serialization_alias="mediaSourceId", ge=0, le=999)
    """The media source ID."""
    action_on_playback_end: PlaybackEndAction | None = Field(
        default=None, validation_alias="actionOnPlaybackEnd", serialization_alias="actionOnPlaybackEnd"
    )
    """Defaults to triggerFreezePlayback."""
    pane: Pane


class View(Model):
    """A screen area divided into segments."""

    duration: int | None = Field(default=None, ge=1, le=86400)
    """The view's duration in seconds (1 s to 24 h). Ignored on single-view sequences."""
    segments: list[Segment]


class Sequence(Model):
    """A sequence of views."""

    id: int | None = Field(default=None, ge=0, le=24)
    """The sequence ID."""
    name: str | None = Field(default=None, max_length=64)
    views: list[View]


class SetSequenceRequest(Model):
    """Arguments of set_sequence."""

    id: int | None = Field(default=None, ge=0, le=24)
    """The sequence ID. If a sequence with this ID exists it is updated; otherwise one is created with this ID. Omit it to create a new sequence."""
    name: str | None = Field(default=None, max_length=64)
    """The sequence name."""
    views: list[View]


class SequenceId(Model):
    id: int = Field(ge=0, le=24)
    """The ID of the sequence."""


class SequenceSummary(Model):
    id: int = Field(ge=0, le=24)
    name: str | None = Field(default=None, max_length=64)
    duration: int | None = None
    """Total run time of the sequence in seconds."""


class SequenceList(Model):
    sequences: list[SequenceSummary]


class DeleteSequenceRequest(Model):
    id: int
    """The sequence ID."""
    force_sw_decoder: bool | None = Field(
        default=None, validation_alias="forceSWDecoder", serialization_alias="forceSWDecoder"
    )
    """Documented as: use software decoding instead of the VPU for this media source; with more views than the maximum VPU instances, the extra sources must use software decoding. It looks misplaced in deleteSequence."""


Manufacturer = Literal["com.axis.camera", "other"]


class StreamSource(Model):
    """A live stream."""

    external_ip_device_info_id: str | None = Field(
        default=None, validation_alias="externalIPDeviceInfoId", serialization_alias="externalIPDeviceInfoId"
    )
    """The ID from the External IP Device Information API, which lets the decoder get the credentials of the device securely."""
    manufacturer: Manufacturer | None = None
    external_ip_device_stream_parameters: str | None = Field(
        default=None,
        validation_alias="externalIPDeviceStreamParameters",
        serialization_alias="externalIPDeviceStreamParameters",
    )
    """Stream parameters, only for com.axis.camera, for example camera=1&resolution=1920x1080&fps=25&videocodec=h264."""
    video_uri: str | None = Field(
        default=None, validation_alias="videoUri", serialization_alias="videoUri", max_length=255
    )
    """The video URI, only for third party cameras (manufacturer other)."""


class FileSource(Model):
    """A file on the decoder."""

    file_id: str | None = Field(default=None, validation_alias="fileId", serialization_alias="fileId")
    """The file, for example USB/imagename.jpg."""


MediaSourceType = Literal["stream", "file"]


class MediaSource(Model):
    """A media source configuration."""

    media_source_id: int | None = Field(
        default=None, validation_alias="mediaSourceId", serialization_alias="mediaSourceId", ge=0, le=999
    )
    """The media source ID."""
    name: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=250)
    has_audio: bool | None = Field(default=None, validation_alias="hasAudio", serialization_alias="hasAudio")
    """True if audio should be enabled for the media source."""
    media_source_type: MediaSourceType = Field(
        validation_alias="mediaSourceType", serialization_alias="mediaSourceType"
    )
    """stream for a live stream, file for a file."""
    stream: StreamSource | None = None
    file: FileSource | None = None


class SetMediaSourcesRequest(Model):
    media_sources: list[MediaSource] = Field(validation_alias="mediaSources", serialization_alias="mediaSources")


class MediaSourceIds(Model):
    ids: list[int]
    """The IDs of the media sources that were created."""


class MediaSourceList(Model):
    media_sources: list[MediaSource] = Field(validation_alias="mediaSources", serialization_alias="mediaSources")


class DeleteMediaSourcesRequest(Model):
    ids: list[int]
    """The IDs of the media sources that should be deleted."""


class PlaySequenceRequest(Model):
    id: int
    """The sequence ID."""
    view_index: int | None = Field(default=None, validation_alias="viewIndex", serialization_alias="viewIndex")
    """The view index to start playing from."""
    resume_timeout: int | None = Field(
        default=None, validation_alias="resumeTimeout", serialization_alias="resumeTimeout"
    )
    """Seconds the new sequence plays before the currently playing sequence resumes."""


class PauseSequenceRequest(Model):
    resume_timeout: int | None = Field(
        default=None, validation_alias="resumeTimeout", serialization_alias="resumeTimeout"
    )
    """Seconds before the previous sequence resumes."""


Priority = Literal["high", "medium", "low"]


class PlayMediaSourceRequest(Model):
    high_resolution_id: int = Field(validation_alias="highResolutionId", serialization_alias="highResolutionId")
    """A media source ID suited for a single stream."""
    medium_resolution_id: int = Field(validation_alias="mediumResolutionId", serialization_alias="mediumResolutionId")
    """A media source ID suited to play alongside half the maximum number of simultaneous streams."""
    low_resolution_id: int = Field(validation_alias="lowResolutionId", serialization_alias="lowResolutionId")
    """A media source ID suited to play alongside the maximum number of simultaneous streams."""
    resume_timeout: int | None = Field(
        default=None, validation_alias="resumeTimeout", serialization_alias="resumeTimeout"
    )
    """Seconds after which the interrupted sequence resumes."""
    priority: Priority
    """Which media source is played if more than one is requested."""
    combine_media_sources: bool = Field(
        validation_alias="combineMediaSources", serialization_alias="combineMediaSources"
    )
    """Media sources are shown side by side if all requests set this to true."""


class StopMediaSourceRequest(Model):
    high_resolution_id: int = Field(validation_alias="highResolutionId", serialization_alias="highResolutionId")
    """The ID of the media source that should be stopped."""


class PlayViewRequest(Model):
    view_index: int | None = Field(default=None, validation_alias="viewIndex", serialization_alias="viewIndex")
    """Index in the currently playing sequence of the view to play."""


class CurrentPosition(Model):
    sequence_id: int = Field(validation_alias="sequenceId", serialization_alias="sequenceId", ge=0, le=24)
    """The sequence ID."""
    sequence_index: int = Field(validation_alias="sequenceIndex", serialization_alias="sequenceIndex", ge=0, le=999)
    """The index of the active view."""
    current_view_time: int = Field(validation_alias="currentViewTime", serialization_alias="currentViewTime")
    """Seconds the active view has been playing."""


class GetCameraCapabilitiesRequest(Model):
    external_ip_device_info_id: str = Field(
        validation_alias="externalIPDeviceInfoId", serialization_alias="externalIPDeviceInfoId"
    )
    """The external IP device info ID."""


class AudioSource(Model):
    audio_source_index: str | None = Field(
        default=None, validation_alias="audioSourceIndex", serialization_alias="audioSourceIndex"
    )
    enabled: str | None = None
    codec: str | None = None
    input_type: str | None = Field(default=None, validation_alias="inputType", serialization_alias="inputType")
    name: str | None = None


class VideoSource(Model):
    image_group_index: str | None = Field(
        default=None, validation_alias="imageGroupIndex", serialization_alias="imageGroupIndex"
    )
    name: str | None = None
    source: str | None = None
    enabled: str | None = None
    max_fps: str | None = Field(default=None, validation_alias="maxFPS", serialization_alias="maxFPS")
    resolution: list[str] | None = None


class CameraCapabilities(Model):
    """Capabilities of an Axis camera. Values are strings, including yes/no flags and indexes."""

    codec: list[str] | None = None
    """Video compression formats, for example h264 and h265."""
    audio_sources: list[AudioSource] | None = Field(
        default=None, validation_alias="audioSources", serialization_alias="audioSources"
    )
    video_sources: list[VideoSource] | None = Field(
        default=None, validation_alias="videoSources", serialization_alias="videoSources"
    )


class DecoderCapabilities(Model):
    resolutions: list[str] | None = None
    """Resolutions supported by the HDMI port, for example 3840x2160@30."""
    max_vpu_instances: int | None = Field(
        default=None, validation_alias="maxVPUInstances", serialization_alias="maxVPUInstances"
    )
    """Documented only in the example."""
    max_streams: int | None = Field(default=None, validation_alias="maxStreams", serialization_alias="maxStreams")
    """Documented as maxstreams in the table, maxStreams in the example."""
    streaming_protocols: list[str] | None = Field(
        default=None, validation_alias="streamingProtocols", serialization_alias="streamingProtocols"
    )
    """For example rtspt, rtsph, rtspsh."""
    audio_coding_formats: list[str] | None = Field(
        default=None, validation_alias="audioCodingFormats", serialization_alias="audioCodingFormats"
    )
    video_coding_formats: list[str] | None = Field(
        default=None, validation_alias="videoCodingFormats", serialization_alias="videoCodingFormats"
    )
    image_coding_formats: list[str] | None = Field(
        default=None, validation_alias="imageCodingFormats", serialization_alias="imageCodingFormats"
    )
    media_types: list[str] | None = Field(default=None, validation_alias="mediaTypes", serialization_alias="mediaTypes")


class UnsecureConnectionAllowed(Model):
    """Whether unencrypted (HTTP) connections are allowed when fetching camera capabilities."""

    unsecure_connection_allowed: bool = Field(
        validation_alias="UnsecureConnectionAllowed", serialization_alias="UnsecureConnectionAllowed"
    )


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/decoder/player.cgi"

INFO = ApiInfo(
    id="decoder2",
    name="Decoder 2",
    family=Family.JSONRPC,
    major=3,
    known_versions=(ApiVersion(3, 0),),
    discovery=(ApiDiscovery("decoder"),),
    docs=("https://developer.axis.com/vapix/network-video/decoder2-api/",),
    errors={
        1100: ErrorCode("Internal error.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
    },
)


class OPS:
    set_sequence = Operation(
        INFO,
        "set_sequence",
        JsonRpcBinding("setSequence", "/axis-cgi/decoder/layout.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=SetSequenceRequest,
        result=SequenceId,
        access="admin",
        effect="write",
        write="replace",
    )
    get_sequence = Operation(
        INFO,
        "get_sequence",
        JsonRpcBinding("getSequence", "/axis-cgi/decoder/layout.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=SequenceId,
        result=Sequence,
        access="admin",
        effect="read",
    )
    list_sequences = Operation(
        INFO,
        "list_sequences",
        JsonRpcBinding("listSequences", "/axis-cgi/decoder/layout.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        result=SequenceList,
        access="admin",
        effect="read",
    )
    delete_sequence = Operation(
        INFO,
        "delete_sequence",
        JsonRpcBinding("deleteSequence", "/axis-cgi/decoder/layout.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=DeleteSequenceRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_media_sources = Operation(
        INFO,
        "set_media_sources",
        JsonRpcBinding(
            "setMediaSources", "/axis-cgi/decoder/mediasource.cgi", negotiation=FixedVersion(ApiVersion(3, 0))
        ),
        params=SetMediaSourcesRequest,
        result=MediaSourceIds,
        access="admin",
        effect="write",
        write="create",
    )
    get_media_sources = Operation(
        INFO,
        "get_media_sources",
        JsonRpcBinding(
            "getMediaSources", "/axis-cgi/decoder/mediasource.cgi", negotiation=FixedVersion(ApiVersion(3, 0))
        ),
        result=MediaSourceList,
        access="admin",
        effect="read",
    )
    delete_media_sources = Operation(
        INFO,
        "delete_media_sources",
        JsonRpcBinding(
            "deleteMediaSources", "/axis-cgi/decoder/mediasource.cgi", negotiation=FixedVersion(ApiVersion(3, 0))
        ),
        params=DeleteMediaSourcesRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    play_sequence = Operation(
        INFO,
        "play_sequence",
        JsonRpcBinding("playSequence", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=PlaySequenceRequest,
        access="admin",
        effect="action",
    )
    stop_sequence = Operation(
        INFO,
        "stop_sequence",
        JsonRpcBinding("stopSequence", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        access="admin",
        effect="action",
    )
    pause_sequence = Operation(
        INFO,
        "pause_sequence",
        JsonRpcBinding("pauseSequence", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=PauseSequenceRequest,
        access="admin",
        effect="action",
    )
    resume_sequence = Operation(
        INFO,
        "resume_sequence",
        JsonRpcBinding("resumeSequence", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        access="admin",
        effect="action",
    )
    play_media_source = Operation(
        INFO,
        "play_media_source",
        JsonRpcBinding("playMediaSource", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=PlayMediaSourceRequest,
        access="admin",
        effect="action",
    )
    stop_media_source = Operation(
        INFO,
        "stop_media_source",
        JsonRpcBinding("stopMediaSource", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=StopMediaSourceRequest,
        access="admin",
        effect="action",
    )
    play_next_view = Operation(
        INFO,
        "play_next_view",
        JsonRpcBinding("playNextView", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        access="admin",
        effect="action",
    )
    play_previous_view = Operation(
        INFO,
        "play_previous_view",
        JsonRpcBinding("playPreviousView", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        access="admin",
        effect="action",
    )
    play_view = Operation(
        INFO,
        "play_view",
        JsonRpcBinding("playView", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))),
        params=PlayViewRequest,
        access="admin",
        effect="action",
    )
    get_current_position = Operation(
        INFO,
        "get_current_position",
        JsonRpcBinding(
            "getCurrentPosition", "/axis-cgi/decoder/player.cgi", negotiation=FixedVersion(ApiVersion(3, 0))
        ),
        result=CurrentPosition,
        access="admin",
        effect="read",
    )
    get_camera_capabilities = Operation(
        INFO,
        "get_camera_capabilities",
        JsonRpcBinding(
            "getCameraCapabilities",
            "/axis-cgi/decoder/decodercapabilities.cgi",
            negotiation=FixedVersion(ApiVersion(3, 0)),
        ),
        params=GetCameraCapabilitiesRequest,
        result=CameraCapabilities,
        access="admin",
        effect="read",
    )
    get_decoder_capabilities = Operation(
        INFO,
        "get_decoder_capabilities",
        JsonRpcBinding(
            "getDecoderCapabilities",
            "/axis-cgi/decoder/decodercapabilities.cgi",
            negotiation=FixedVersion(ApiVersion(3, 0)),
        ),
        result=DecoderCapabilities,
        access="admin",
        effect="read",
    )
    get_unsecure_connection_allowed = Operation(
        INFO,
        "get_unsecure_connection_allowed",
        JsonRpcBinding(
            "getUnsecureConnectionAllowed",
            "/axis-cgi/decoder/decodercapabilities.cgi",
            negotiation=FixedVersion(ApiVersion(3, 0)),
        ),
        result=UnsecureConnectionAllowed,
        access="admin",
        effect="read",
    )
    set_unsecure_connection_allowed = Operation(
        INFO,
        "set_unsecure_connection_allowed",
        JsonRpcBinding(
            "setUnsecureConnectionAllowed",
            "/axis-cgi/decoder/decodercapabilities.cgi",
            negotiation=FixedVersion(ApiVersion(3, 0)),
        ),
        params=UnsecureConnectionAllowed,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class Decoder2Api(SyncApi):
    """Decoder 2 (``decoder2``, version 3)."""

    INFO = INFO

    @overload
    def set_sequence(
        self, request: SetSequenceRequest, /, *, request_options: RequestOptions | None = None
    ) -> SequenceId: ...
    @overload
    def set_sequence(
        self,
        /,
        *,
        id: int | MISSING = MISSING,
        name: str | MISSING = MISSING,
        views: list[View],
        request_options: RequestOptions | None = None,
    ) -> SequenceId: ...
    def set_sequence(
        self,
        request: SetSequenceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SequenceId:
        """Create a new sequence or update an existing one.

        Views of segments, each segment a pane, a media source and an end-of-playback action. If the view
        duration is shorter than the file, the decoder switches view before the playback ends. If the file
        is shorter than the view duration, the decoder acts on the end-of-playback action.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_sequence, request, kwargs, request_options)

    def get_sequence(self, *, id: int, request_options: RequestOptions | None = None) -> Sequence:
        """Fetch the configuration of a sequence. Access: admin."""
        return self._run(OPS.get_sequence, None, {"id": id}, request_options)

    def list_sequences(self, *, request_options: RequestOptions | None = None) -> SequenceList:
        """Fetch the identifiers (id, name, duration) of all sequences. Access: admin."""
        return self._run(OPS.list_sequences, None, {}, request_options)

    def delete_sequence(
        self, *, id: int, force_sw_decoder: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Delete a sequence configuration. Access: admin."""
        self._run(OPS.delete_sequence, None, {"id": id, "force_sw_decoder": force_sw_decoder}, request_options)

    @overload
    def set_media_sources(
        self, request: SetMediaSourcesRequest, /, *, request_options: RequestOptions | None = None
    ) -> MediaSourceIds: ...
    @overload
    def set_media_sources(
        self, /, *, media_sources: list[MediaSource], request_options: RequestOptions | None = None
    ) -> MediaSourceIds: ...
    def set_media_sources(
        self,
        request: SetMediaSourcesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> MediaSourceIds:
        """Create media source configurations, streams or files.

        Configure the device first with the External IP Device Information API; its externalIPDeviceInfoId
        lets the decoder reach the device securely.

        Access: admin.
        """
        return self._run(OPS.set_media_sources, request, kwargs, request_options)

    def get_media_sources(self, *, request_options: RequestOptions | None = None) -> MediaSourceList:
        """Get the configuration of all media sources. Access: admin."""
        return self._run(OPS.get_media_sources, None, {}, request_options)

    def delete_media_sources(self, *, ids: list[int], request_options: RequestOptions | None = None) -> None:
        """Delete one or several media source configurations. Access: admin."""
        self._run(OPS.delete_media_sources, None, {"ids": ids}, request_options)

    def play_sequence(
        self,
        *,
        id: int,
        view_index: int | MISSING = MISSING,
        resume_timeout: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Start playing a sequence.

        A single-view sequence plays until it is stopped.

        Access: admin.
        """
        self._run(
            OPS.play_sequence,
            None,
            {"id": id, "view_index": view_index, "resume_timeout": resume_timeout},
            request_options,
        )

    def stop_sequence(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop the sequence playback. Access: admin."""
        self._run(OPS.stop_sequence, None, {}, request_options)

    def pause_sequence(
        self, *, resume_timeout: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Pause the sequence: the current view keeps playing but does not change to the next view.

        Access: admin.
        """
        self._run(OPS.pause_sequence, None, {"resume_timeout": resume_timeout}, request_options)

    def resume_sequence(self, *, request_options: RequestOptions | None = None) -> None:
        """Resume the playback of a sequence. Access: admin."""
        self._run(OPS.resume_sequence, None, {}, request_options)

    @overload
    def play_media_source(
        self, request: PlayMediaSourceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def play_media_source(
        self,
        /,
        *,
        high_resolution_id: int,
        medium_resolution_id: int,
        low_resolution_id: int,
        resume_timeout: int | MISSING = MISSING,
        priority: Priority,
        combine_media_sources: bool,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def play_media_source(
        self,
        request: PlayMediaSourceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Play a media source, interrupting the current sequence, which resumes afterwards.

        Access: admin.
        """
        self._run(OPS.play_media_source, request, kwargs, request_options)

    def stop_media_source(self, *, high_resolution_id: int, request_options: RequestOptions | None = None) -> None:
        """Stop a media source that is playing as an alarm; if it is the only one playing, the original sequence resumes.

        Access: admin.
        """
        self._run(OPS.stop_media_source, None, {"high_resolution_id": high_resolution_id}, request_options)

    def play_next_view(self, *, request_options: RequestOptions | None = None) -> None:
        """Play the next view in the currently playing sequence. Access: admin."""
        self._run(OPS.play_next_view, None, {}, request_options)

    def play_previous_view(self, *, request_options: RequestOptions | None = None) -> None:
        """Play the previous view in the currently playing sequence. Access: admin."""
        self._run(OPS.play_previous_view, None, {}, request_options)

    def play_view(self, *, view_index: int | MISSING = MISSING, request_options: RequestOptions | None = None) -> None:
        """Play a view in the currently playing sequence. Access: admin."""
        self._run(OPS.play_view, None, {"view_index": view_index}, request_options)

    def get_current_position(self, *, request_options: RequestOptions | None = None) -> CurrentPosition:
        """Get the sequence ID, the active view index and the time the active view has played.

        Access: admin.
        """
        return self._run(OPS.get_current_position, None, {}, request_options)

    def get_camera_capabilities(
        self, *, external_ip_device_info_id: str, request_options: RequestOptions | None = None
    ) -> CameraCapabilities:
        """Fetch the capabilities of an Axis camera configured through the External IP Device Information API.

        Access: admin.
        """
        return self._run(
            OPS.get_camera_capabilities,
            None,
            {"external_ip_device_info_id": external_ip_device_info_id},
            request_options,
        )

    def get_decoder_capabilities(self, *, request_options: RequestOptions | None = None) -> DecoderCapabilities:
        """Get the decoder capabilities. Access: admin."""
        return self._run(OPS.get_decoder_capabilities, None, {}, request_options)

    def get_unsecure_connection_allowed(
        self, *, request_options: RequestOptions | None = None
    ) -> UnsecureConnectionAllowed:
        """Check if camera capabilities can be fetched over an unencrypted (HTTP) connection.

        Access: admin.
        """
        return self._run(OPS.get_unsecure_connection_allowed, None, {}, request_options)

    def set_unsecure_connection_allowed(
        self, *, unsecure_connection_allowed: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Allow or forbid unencrypted (HTTP) connections when fetching camera capabilities.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_unsecure_connection_allowed,
            None,
            {"unsecure_connection_allowed": unsecure_connection_allowed},
            request_options,
        )


class AsyncDecoder2Api(AsyncApi):
    """Decoder 2 (``decoder2``, version 3)."""

    INFO = INFO

    @overload
    async def set_sequence(
        self, request: SetSequenceRequest, /, *, request_options: RequestOptions | None = None
    ) -> SequenceId: ...
    @overload
    async def set_sequence(
        self,
        /,
        *,
        id: int | MISSING = MISSING,
        name: str | MISSING = MISSING,
        views: list[View],
        request_options: RequestOptions | None = None,
    ) -> SequenceId: ...
    async def set_sequence(
        self,
        request: SetSequenceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SequenceId:
        """Create a new sequence or update an existing one.

        Views of segments, each segment a pane, a media source and an end-of-playback action. If the view
        duration is shorter than the file, the decoder switches view before the playback ends. If the file
        is shorter than the view duration, the decoder acts on the end-of-playback action.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_sequence, request, kwargs, request_options)

    async def get_sequence(self, *, id: int, request_options: RequestOptions | None = None) -> Sequence:
        """Fetch the configuration of a sequence. Access: admin."""
        return await self._run(OPS.get_sequence, None, {"id": id}, request_options)

    async def list_sequences(self, *, request_options: RequestOptions | None = None) -> SequenceList:
        """Fetch the identifiers (id, name, duration) of all sequences. Access: admin."""
        return await self._run(OPS.list_sequences, None, {}, request_options)

    async def delete_sequence(
        self, *, id: int, force_sw_decoder: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Delete a sequence configuration. Access: admin."""
        await self._run(OPS.delete_sequence, None, {"id": id, "force_sw_decoder": force_sw_decoder}, request_options)

    @overload
    async def set_media_sources(
        self, request: SetMediaSourcesRequest, /, *, request_options: RequestOptions | None = None
    ) -> MediaSourceIds: ...
    @overload
    async def set_media_sources(
        self, /, *, media_sources: list[MediaSource], request_options: RequestOptions | None = None
    ) -> MediaSourceIds: ...
    async def set_media_sources(
        self,
        request: SetMediaSourcesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> MediaSourceIds:
        """Create media source configurations, streams or files.

        Configure the device first with the External IP Device Information API; its externalIPDeviceInfoId
        lets the decoder reach the device securely.

        Access: admin.
        """
        return await self._run(OPS.set_media_sources, request, kwargs, request_options)

    async def get_media_sources(self, *, request_options: RequestOptions | None = None) -> MediaSourceList:
        """Get the configuration of all media sources. Access: admin."""
        return await self._run(OPS.get_media_sources, None, {}, request_options)

    async def delete_media_sources(self, *, ids: list[int], request_options: RequestOptions | None = None) -> None:
        """Delete one or several media source configurations. Access: admin."""
        await self._run(OPS.delete_media_sources, None, {"ids": ids}, request_options)

    async def play_sequence(
        self,
        *,
        id: int,
        view_index: int | MISSING = MISSING,
        resume_timeout: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Start playing a sequence.

        A single-view sequence plays until it is stopped.

        Access: admin.
        """
        await self._run(
            OPS.play_sequence,
            None,
            {"id": id, "view_index": view_index, "resume_timeout": resume_timeout},
            request_options,
        )

    async def stop_sequence(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop the sequence playback. Access: admin."""
        await self._run(OPS.stop_sequence, None, {}, request_options)

    async def pause_sequence(
        self, *, resume_timeout: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Pause the sequence: the current view keeps playing but does not change to the next view.

        Access: admin.
        """
        await self._run(OPS.pause_sequence, None, {"resume_timeout": resume_timeout}, request_options)

    async def resume_sequence(self, *, request_options: RequestOptions | None = None) -> None:
        """Resume the playback of a sequence. Access: admin."""
        await self._run(OPS.resume_sequence, None, {}, request_options)

    @overload
    async def play_media_source(
        self, request: PlayMediaSourceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def play_media_source(
        self,
        /,
        *,
        high_resolution_id: int,
        medium_resolution_id: int,
        low_resolution_id: int,
        resume_timeout: int | MISSING = MISSING,
        priority: Priority,
        combine_media_sources: bool,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def play_media_source(
        self,
        request: PlayMediaSourceRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Play a media source, interrupting the current sequence, which resumes afterwards.

        Access: admin.
        """
        await self._run(OPS.play_media_source, request, kwargs, request_options)

    async def stop_media_source(
        self, *, high_resolution_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Stop a media source that is playing as an alarm; if it is the only one playing, the original sequence resumes.

        Access: admin.
        """
        await self._run(OPS.stop_media_source, None, {"high_resolution_id": high_resolution_id}, request_options)

    async def play_next_view(self, *, request_options: RequestOptions | None = None) -> None:
        """Play the next view in the currently playing sequence. Access: admin."""
        await self._run(OPS.play_next_view, None, {}, request_options)

    async def play_previous_view(self, *, request_options: RequestOptions | None = None) -> None:
        """Play the previous view in the currently playing sequence. Access: admin."""
        await self._run(OPS.play_previous_view, None, {}, request_options)

    async def play_view(
        self, *, view_index: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Play a view in the currently playing sequence. Access: admin."""
        await self._run(OPS.play_view, None, {"view_index": view_index}, request_options)

    async def get_current_position(self, *, request_options: RequestOptions | None = None) -> CurrentPosition:
        """Get the sequence ID, the active view index and the time the active view has played.

        Access: admin.
        """
        return await self._run(OPS.get_current_position, None, {}, request_options)

    async def get_camera_capabilities(
        self, *, external_ip_device_info_id: str, request_options: RequestOptions | None = None
    ) -> CameraCapabilities:
        """Fetch the capabilities of an Axis camera configured through the External IP Device Information API.

        Access: admin.
        """
        return await self._run(
            OPS.get_camera_capabilities,
            None,
            {"external_ip_device_info_id": external_ip_device_info_id},
            request_options,
        )

    async def get_decoder_capabilities(self, *, request_options: RequestOptions | None = None) -> DecoderCapabilities:
        """Get the decoder capabilities. Access: admin."""
        return await self._run(OPS.get_decoder_capabilities, None, {}, request_options)

    async def get_unsecure_connection_allowed(
        self, *, request_options: RequestOptions | None = None
    ) -> UnsecureConnectionAllowed:
        """Check if camera capabilities can be fetched over an unencrypted (HTTP) connection.

        Access: admin.
        """
        return await self._run(OPS.get_unsecure_connection_allowed, None, {}, request_options)

    async def set_unsecure_connection_allowed(
        self, *, unsecure_connection_allowed: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Allow or forbid unencrypted (HTTP) connections when fetching camera capabilities.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_unsecure_connection_allowed,
            None,
            {"unsecure_connection_allowed": unsecure_connection_allowed},
            request_options,
        )
