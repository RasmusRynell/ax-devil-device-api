# GENERATED from specs/apis/audio-systems/axis-audio-manager-pro-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""REST API of the AXIS Audio Manager Pro server. Manage audio sessions (HTTP, RTP, SIP, WS), targets, audio files, volume controllers, visual profiles, paging configurations and server information.

Docs: https://developer.axis.com/vapix/audio-systems/axis-audio-manager-pro-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.rest import RestBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

VisualProfileEnabled = Literal["DEFAULT", "FALSE", "TRUE"]


class HttpWsCodec(Model):
    bitrate: int | None = None
    """Max bitrate in bps. Required for codecs PCM, OPUS, MP2 and MP3."""
    channel_layout: Literal["MONO", "STEREO"] | None = Field(
        default=None, validation_alias="channelLayout", serialization_alias="channelLayout"
    )
    codec: (
        Literal[
            "PCM",
            "G711_ULAW",
            "G711_ALAW",
            "G722",
            "G723",
            "G726",
            "G728",
            "G729",
            "GSM",
            "MP2",
            "MP3",
            "AAC",
            "OPUS",
            "VORBIS",
            "FLAC",
            "WMA",
        ]
        | None
    ) = None
    sample_format: Literal["S8", "S16", "S24", "S32", "FLOAT", "DOUBLE"] | None = Field(
        default=None, validation_alias="sampleFormat", serialization_alias="sampleFormat"
    )
    sample_rate: int | None = Field(default=None, validation_alias="sampleRate", serialization_alias="sampleRate")
    """PCM sample rate in Hz."""


class RtpCodec(Model):
    audio_profile: (
        Literal[
            "g711aMono8kHz",
            "g711uMono8kHz",
            "g722Mono16kHz",
            "l16Stereo48kHz",
            "l16Mono48kHz",
            "l16Stereo44kHz",
            "l16Mono44kHz",
            "l16Stereo32kHz",
            "l16Mono32kHz",
            "l16Stereo16kHz",
            "l16Mono16kHz",
            "mp2Stereo48kHz",
            "opusStereo48kHz",
            "opusMono48kHz",
        ]
        | None
    ) = Field(default=None, validation_alias="audioProfile", serialization_alias="audioProfile")
    payload_type: int | None = Field(default=None, validation_alias="payloadType", serialization_alias="payloadType")
    """Only used by codecs with dynamic payload types."""


class DuplexDevice(Model):
    """Device used for two-way audio; its source input is sent back to the session. sourceId may be omitted if multiple inputs; omitting duplexDevice disables audio input."""

    id: str | None = None
    """Unique device ID (e.g. dev_15)."""
    source_id: str | None = Field(default=None, validation_alias="sourceId", serialization_alias="sourceId")
    """Unique device source ID (e.g. dsc_15)."""


class HttpAudioSession(Model):
    type: Literal["HTTP"]
    custom_id: str | None = Field(default=None, validation_alias="customId", serialization_alias="customId")
    """Client-provided identifier used to reference the session."""
    custom_text: str | None = Field(default=None, validation_alias="customText", serialization_alias="customText")
    """Custom text overriding the default text of the visual profile."""
    id: str | None = None
    """A unique audio session ID. Assigned by the server."""
    prio: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    """Priority of the session relative to other playing audio. A higher priority silences sessions with a lower priority in the same targets. Default: 'LOW'."""
    targets: list[str]
    """The target IDs where audio will be played. Audio plays on all specified targets and cascades to their children and descendants in the zone hierarchy."""
    visual_profile_enabled: VisualProfileEnabled | None = Field(
        default=None, validation_alias="visualProfileEnabled", serialization_alias="visualProfileEnabled"
    )
    visual_profile_id: int | None = Field(
        default=None, validation_alias="visualProfileId", serialization_alias="visualProfileId"
    )
    """The visual profile ID."""
    codec: HttpWsCodec | None = None
    """The codec of the session. The table of the docs calls it 'codecs=<object>'; the examples use 'codec'."""
    holdup: int | None = None
    """Audio buffering delay in ms (typical 100-400). Higher values give stable delivery over unreliable networks at the cost of latency. Default: 200."""


class RtpAudioSession(Model):
    type: Literal["RTP"]
    custom_id: str | None = Field(default=None, validation_alias="customId", serialization_alias="customId")
    """Client-provided identifier used to reference the session."""
    custom_text: str | None = Field(default=None, validation_alias="customText", serialization_alias="customText")
    """Custom text overriding the default text of the visual profile."""
    id: str | None = None
    """A unique audio session ID. Assigned by the server."""
    prio: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    """Priority of the session relative to other playing audio. A higher priority silences sessions with a lower priority in the same targets. Default: 'LOW'."""
    targets: list[str]
    """The target IDs where audio will be played. Audio plays on all specified targets and cascades to their children and descendants in the zone hierarchy."""
    visual_profile_enabled: VisualProfileEnabled | None = Field(
        default=None, validation_alias="visualProfileEnabled", serialization_alias="visualProfileEnabled"
    )
    visual_profile_id: int | None = Field(
        default=None, validation_alias="visualProfileId", serialization_alias="visualProfileId"
    )
    """The visual profile ID."""
    codecs: list[RtpCodec] | None = None
    multicast_group: str | None = Field(
        default=None, validation_alias="multicastGroup", serialization_alias="multicastGroup"
    )
    """IPv4/IPv6 multicast group address; specify when RTP is transmitted via multicast."""
    port: int | None = None
    """RTP port; assigned by the server if omitted; error if occupied or outside configured range."""


class SipAudioSession(Model):
    type: Literal["SIP"]
    custom_id: str | None = Field(default=None, validation_alias="customId", serialization_alias="customId")
    """Client-provided identifier used to reference the session."""
    custom_text: str | None = Field(default=None, validation_alias="customText", serialization_alias="customText")
    """Custom text overriding the default text of the visual profile."""
    id: str | None = None
    """A unique audio session ID. Assigned by the server."""
    prio: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    """Priority of the session relative to other playing audio. A higher priority silences sessions with a lower priority in the same targets. Default: 'LOW'."""
    targets: list[str]
    """The target IDs where audio will be played. Audio plays on all specified targets and cascades to their children and descendants in the zone hierarchy."""
    visual_profile_enabled: VisualProfileEnabled | None = Field(
        default=None, validation_alias="visualProfileEnabled", serialization_alias="visualProfileEnabled"
    )
    visual_profile_id: int | None = Field(
        default=None, validation_alias="visualProfileId", serialization_alias="visualProfileId"
    )
    """The visual profile ID."""
    duplex_device: DuplexDevice | None = Field(
        default=None, validation_alias="duplexDevice", serialization_alias="duplexDevice"
    )
    extension: str | None = None
    """Dialing extension; when dialed, the session is used."""


class WsAudioSession(Model):
    type: Literal["WS"]
    custom_id: str | None = Field(default=None, validation_alias="customId", serialization_alias="customId")
    """Client-provided identifier used to reference the session."""
    custom_text: str | None = Field(default=None, validation_alias="customText", serialization_alias="customText")
    """Custom text overriding the default text of the visual profile."""
    id: str | None = None
    """A unique audio session ID. Assigned by the server."""
    prio: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    """Priority of the session relative to other playing audio. A higher priority silences sessions with a lower priority in the same targets. Default: 'LOW'."""
    targets: list[str]
    """The target IDs where audio will be played. Audio plays on all specified targets and cascades to their children and descendants in the zone hierarchy."""
    visual_profile_enabled: VisualProfileEnabled | None = Field(
        default=None, validation_alias="visualProfileEnabled", serialization_alias="visualProfileEnabled"
    )
    visual_profile_id: int | None = Field(
        default=None, validation_alias="visualProfileId", serialization_alias="visualProfileId"
    )
    """The visual profile ID."""
    codec: HttpWsCodec | None = None
    duplex_device: DuplexDevice | None = Field(
        default=None, validation_alias="duplexDevice", serialization_alias="duplexDevice"
    )
    holdup: int | None = None
    """Audio buffering delay in ms (typical 100-400). Default: 200."""


AudioSession = HttpAudioSession | RtpAudioSession | SipAudioSession | WsAudioSession


class PlayAudioFilesRequest(Model):
    custom_text: str | None = Field(default=None, validation_alias="customText", serialization_alias="customText")
    """Optional text overriding the visual profile's text."""
    file_ids: list[str] = Field(validation_alias="fileIds", serialization_alias="fileIds")
    """Audio file IDs played in sequence, each starting immediately after the previous."""
    repeat: int | None = None
    """Number of times to play; <= 0 means infinite (stop with stopAudioFiles or by deleting the session). Default: 1."""
    visual_profile_enabled: VisualProfileEnabled | None = Field(
        default=None, validation_alias="visualProfileEnabled", serialization_alias="visualProfileEnabled"
    )
    visual_profile_id: int | None = Field(
        default=None, validation_alias="visualProfileId", serialization_alias="visualProfileId"
    )


class AudioSessionStatus(Model):
    available_devices: list[str] | None = Field(
        default=None, validation_alias="availableDevices", serialization_alias="availableDevices"
    )
    """Devices currently available to receive audio in this session."""
    id: str
    playback_started: str | None = Field(
        default=None, validation_alias="playbackStarted", serialization_alias="playbackStarted"
    )
    """When the session started, e.g. 2023-01-12 12:53:32+0100."""
    prio: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    """The priority of the audio session."""
    status: Literal["notPlaying", "playing"]
    type: Literal["HTTP", "SIP", "RTP", "WS"]
    unavailable_devices: list[str] | None = Field(
        default=None, validation_alias="unavailableDevices", serialization_alias="unavailableDevices"
    )
    """Devices unavailable because a higher-priority session is active on the same targets."""


class TargetIssues(Model):
    """Device targets only. Major and minor issues."""

    major: (
        list[
            Literal[
                "MULTICAST_ERROR",
                "OUTPUT_GAIN_LOW",
                "UNSUPPORTED_HOST_FW",
                "UNSUPPORTED_DEV_TYPE",
                "UNSUPPORTED_TRANSPORT",
            ]
        ]
        | None
    ) = None
    minor: (
        list[
            Literal[
                "MULTICAST_ERROR",
                "OUTPUT_GAIN_LOW",
                "UNSUPPORTED_HOST_FW",
                "UNSUPPORTED_DEV_TYPE",
                "UNSUPPORTED_TRANSPORT",
            ]
        ]
        | None
    ) = None


class TargetSourcesItem(Model):
    enabled: bool | None = None
    id: str | None = None
    name: str | None = None


class Target(Model):
    children: list[str] | None = None
    """IDs of direct child targets; always empty for devices (leaf nodes)."""
    enabled: bool | None = None
    """Whether the target should play audio. For a destination all mapped sources are stopped, but other audio can still play in its targets."""
    id: str
    """Unique target ID (e.g. zon_1255)."""
    issues: TargetIssues | None = None
    """Device targets only. Major and minor issues."""
    lowest_priority_available: Literal["LOW", "MEDIUM", "HIGH", "NONE"] | None = Field(
        default=None, validation_alias="lowestPriorityAvailable", serialization_alias="lowestPriorityAvailable"
    )
    """Lowest priority for which the target is currently available; NONE if unavailable even for HIGH."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    sources: list[TargetSourcesItem] | None = None
    """Device targets only. Device sources such as Line-in."""
    status: (
        Literal[
            "unmanaged",
            "online",
            "offline",
            "playing",
            "error: NO_LICENCE",
            "error: FACTORY_DEFAULTS",
            "error: UNAUTHORIZED",
            "error: UNSUPPORTED_HOST_FW",
            "error: UNSUPPORTED_TRANSPORT",
        ]
        | None
    ) = None
    """End devices only."""
    type: Literal["physicalZone", "site", "device", "destination", "outputStream"]


class AudioFile(Model):
    id: str
    length: float | None = None
    """Length in seconds."""
    library: str | None = None
    """Library containing the file (e.g. Announcement)."""
    name: str
    path: str | None = None
    """Optional folder info (e.g. /Closing/)."""
    type: Literal["FILE", "PLAYLIST"]


class VolumeControllerContentClassesItem(Model):
    id: str | None = None
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")


class VolumeController(Model):
    allow_mute: bool | None = Field(default=None, validation_alias="allowMute", serialization_alias="allowMute")
    content_classes: list[VolumeControllerContentClassesItem] | None = Field(
        default=None, validation_alias="contentClasses", serialization_alias="contentClasses"
    )
    id: str
    max_negative_volume_offset: int | None = Field(
        default=None,
        validation_alias="maxNegativeVolumeOffset",
        serialization_alias="maxNegativeVolumeOffset",
        ge=-100,
        le=100,
    )
    """Minimum allowed value of the controller."""
    max_positive_volume_offset: int | None = Field(
        default=None,
        validation_alias="maxPositiveVolumeOffset",
        serialization_alias="maxPositiveVolumeOffset",
        ge=-100,
        le=100,
    )
    """Maximum allowed value of the controller."""
    muted: bool | None = None
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    targets: list[str] | None = None
    volume_offset: float | None = Field(
        default=None, validation_alias="volumeOffset", serialization_alias="volumeOffset", ge=-100, le=100
    )
    """Current volume offset [-100, +100]."""


class LightProfile(Model):
    audio_sync: bool | None = Field(default=None, validation_alias="audioSync", serialization_alias="audioSync")
    """TRUE: light duration synchronized with audio playback; FALSE: controlled by duration."""
    colors: Literal["RED", "GREEN", "BLUE", "YELLOW", "PURPLE", "TURQUOISE", "WHITE", "PINK", "AMBER"] | None = None
    description: str | None = None
    duration: int | None = None
    """Strobe time (s)."""
    id: int
    intensity: int | None = Field(default=None, ge=0, le=5)
    name: str | None = None
    pattern: Literal["OFF", "STEADY", "ALTERNATE", "BLINK", "PULSE", "ROTATION"] | None = None
    speed: int | None = Field(default=None, ge=0, le=5)
    type: Literal["AUDIO", "SIGNALING"] | None = None
    """Whether the profile controls audio LEDs or signaling LEDs."""


class VisualProfileDefaultCategoriesItem(Model):
    category: Literal["ANY", "MUSIC", "ADVERTISEMENT", "ANNOUNCEMENT", "PAGING"] | None = None
    enabled: bool | None = None


class VisualProfile(Model):
    audio_sync: bool | None = Field(default=None, validation_alias="audioSync", serialization_alias="audioSync")
    """True if the text should be synchronized with the audio."""
    default_categories: list[VisualProfileDefaultCategoriesItem] | None = Field(
        default=None, validation_alias="defaultCategories", serialization_alias="defaultCategories"
    )
    description: str | None = None
    id: int
    light_enabled: bool | None = Field(
        default=None, validation_alias="lightEnabled", serialization_alias="lightEnabled"
    )
    light_profile: LightProfile | None = Field(
        default=None, validation_alias="lightProfile", serialization_alias="lightProfile"
    )
    name: str | None = None
    text: str | None = None
    """Supported encodings: Latin 1 (8859-1), Latin CE (8859-2), Greek (8859-7), Cyrillic (8859-5), Hebrew (8859-8)."""
    text_background_color: str | None = Field(
        default=None,
        validation_alias="textBackgroundColor",
        serialization_alias="textBackgroundColor",
        pattern="^#[0-9A-Fa-f]{6}$",
    )
    text_color: str | None = Field(
        default=None, validation_alias="textColor", serialization_alias="textColor", pattern="^#[0-9A-Fa-f]{6}$"
    )
    text_duration: int | None = Field(default=None, validation_alias="textDuration", serialization_alias="textDuration")
    """Text playback time in seconds."""
    text_layout: Literal["LARGE", "MEDIUM", "SMALL", "LARGE_LEFT_TO_RIGHT"] | None = Field(
        default=None, validation_alias="textLayout", serialization_alias="textLayout"
    )
    """Large: single line, horizontal scroll; medium/small: multiple lines, vertical scroll."""
    text_repetition: int | None = Field(
        default=None, validation_alias="textRepetition", serialization_alias="textRepetition"
    )
    text_scroll_speed: int | None = Field(
        default=None, validation_alias="textScrollSpeed", serialization_alias="textScrollSpeed", ge=1, le=10
    )
    text_time_limit: bool | None = Field(
        default=None, validation_alias="textTimeLimit", serialization_alias="textTimeLimit"
    )
    """When textAudioSync is false: true = show for textDuration; false = show textRepetition times."""
    used: bool | None = None


class ServerInfo(Model):
    api_versions: list[str] | None = Field(
        default=None, validation_alias="apiVersions", serialization_alias="apiVersions"
    )
    license_until: str | None = Field(default=None, validation_alias="licenseUntil", serialization_alias="licenseUntil")
    licensing_status: bool | None = Field(
        default=None, validation_alias="licensingStatus", serialization_alias="licensingStatus"
    )
    locale: str | None = None
    server_ips: list[str] | None = Field(default=None, validation_alias="serverIps", serialization_alias="serverIps")
    server_name: str | None = Field(default=None, validation_alias="serverName", serialization_alias="serverName")
    server_port: int | None = Field(default=None, validation_alias="serverPort", serialization_alias="serverPort")
    server_version: str | None = Field(
        default=None, validation_alias="serverVersion", serialization_alias="serverVersion"
    )
    site_id: str | None = Field(default=None, validation_alias="siteId", serialization_alias="siteId")
    site_name: str | None = Field(default=None, validation_alias="siteName", serialization_alias="siteName")
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone")
    trial_active: bool | None = Field(default=None, validation_alias="trialActive", serialization_alias="trialActive")


class PagingConfiguration(Model):
    duplex_device: DuplexDevice | None = Field(
        default=None, validation_alias="duplexDevice", serialization_alias="duplexDevice"
    )
    """Only for TWOWAY."""
    extension: str | None = None
    """Extension used for SIP dialing."""
    id: str
    """Paging source ID (e.g. pac_16)."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    targets: list[str] | None = None
    """Destinations (ONEWAY) or a specific device (TWOWAY)."""
    type: Literal["ONEWAY", "TWOWAY"]


class CreateAudioSessionRequest(Model):
    body: AudioSession
    """The session to create; 'type' selects HTTP, RTP, SIP or WS."""


class DeleteAudioSessionByCustomIdRequest(Model):
    custom_id: str = Field(validation_alias="customId", serialization_alias="customId")
    """Must match the customId specified when the session was created (the docs mark it Optional, but it is a path segment)."""


class PlayAudioFilesByCustomIdRequest(Model):
    custom_id: str = Field(validation_alias="customId", serialization_alias="customId")
    body: PlayAudioFilesRequest


class StopAudioFilesByCustomIdRequest(Model):
    custom_id: str = Field(validation_alias="customId", serialization_alias="customId")


class OneshotPlayAudioFilesRequest(Model):
    custom_id: str | None = Field(default=None, validation_alias="customId", serialization_alias="customId")
    custom_text: str | None = Field(default=None, validation_alias="customText", serialization_alias="customText")
    file_ids: list[str] = Field(validation_alias="fileIds", serialization_alias="fileIds")
    prio: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    """Priority of the session. The table lists it without the Optional marker but with the default LOW. Default: 'LOW'."""
    repeat: int | None = None
    """Number of times to play the files; <= 0 means infinite."""
    targets: list[str]
    """The target IDs where audio will be played. In the example body; missing from the parameter table."""
    visual_profile_enabled: VisualProfileEnabled | None = Field(
        default=None, validation_alias="visualProfileEnabled", serialization_alias="visualProfileEnabled"
    )
    visual_profile_id: int | None = Field(
        default=None, validation_alias="visualProfileId", serialization_alias="visualProfileId"
    )


class DeleteAudioSessionRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")


class GetAudioSessionRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")


class UpdateAudioSessionRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")
    prio: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    targets: list[str] | None = None
    """List of target identifiers (zones or devices)."""


class PlayAudioFilesRequestArgs(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")
    """The ID of the HTTP audio session."""
    body: PlayAudioFilesRequest


class GetAudioSessionStatusRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")


class StopAudioFilesRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")


class GetTargetRequest(Model):
    target_id: str = Field(validation_alias="targetId", serialization_alias="targetId")


class UpdateTargetRequest(Model):
    target_id: str = Field(validation_alias="targetId", serialization_alias="targetId")
    enabled: bool


class GetAudioFileRequest(Model):
    audio_file_id: str = Field(validation_alias="audioFileId", serialization_alias="audioFileId")


class GetVolumeControllerRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")


class UpdateVolumeControllerRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")
    muted: bool | None = None
    """Mutes all audio of the content types and targets the controller controls. Default: False."""
    volume_offset: float | None = Field(
        default=None, validation_alias="volumeOffset", serialization_alias="volumeOffset", ge=-100, le=100
    )


class OffsetVolumeRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")
    volume_offset: float = Field(validation_alias="volumeOffset", serialization_alias="volumeOffset", ge=-100, le=100)


class ToggleMuteRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")


class GetVisualProfileRequest(Model):
    visual_profile_id: int = Field(validation_alias="visualProfileId", serialization_alias="visualProfileId")


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/api"

INFO = ApiInfo(
    id="axis-audio-manager-pro-api",
    name="AXIS Audio Manager Pro API",
    family=Family.REST,
    docs=("https://developer.axis.com/vapix/audio-systems/axis-audio-manager-pro-api/",),
    errors={
        400: ErrorCode(
            "Invalid parameters. application/json error object, e.g. message \"Unknown priority 'HIGHER'\".",
            "invalid_argument",
        ),
        404: ErrorCode("Not found", "not_found"),
        422: ErrorCode("Change not allowed", "invalid_argument"),
        500: ErrorCode("Internal server error", "internal"),
    },
)


class OPS:
    list_audio_sessions = Operation(
        INFO,
        "list_audio_sessions",
        RestBinding("GET", f"{ROOT}/v1.2/audioSessions"),
        result=list[AudioSession],
        access="admin",
        effect="read",
    )
    create_audio_session = Operation(
        INFO,
        "create_audio_session",
        RestBinding("POST", f"{ROOT}/v1.2/audioSessions", body="value", body_field="body"),
        params=CreateAudioSessionRequest,
        result=AudioSession,
        access="admin",
        effect="write",
        write="create",
    )
    delete_audio_session_by_custom_id = Operation(
        INFO,
        "delete_audio_session_by_custom_id",
        RestBinding("DELETE", f"{ROOT}/v1.2/audioSessions/custom/{{customId}}"),
        params=DeleteAudioSessionByCustomIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    play_audio_files_by_custom_id = Operation(
        INFO,
        "play_audio_files_by_custom_id",
        RestBinding(
            "POST", f"{ROOT}/v1.2/audioSessions/custom/{{customId}}/playAudioFiles", body="value", body_field="body"
        ),
        params=PlayAudioFilesByCustomIdRequest,
        access="admin",
        effect="action",
    )
    stop_audio_files_by_custom_id = Operation(
        INFO,
        "stop_audio_files_by_custom_id",
        RestBinding("POST", f"{ROOT}/v1.2/audioSessions/custom/{{customId}}/stopAudioFiles"),
        params=StopAudioFilesByCustomIdRequest,
        access="admin",
        effect="action",
    )
    oneshot_play_audio_files = Operation(
        INFO,
        "oneshot_play_audio_files",
        RestBinding("POST", f"{ROOT}/v1.2/audioSessions/oneshotPlayAudioFiles", body="object"),
        params=OneshotPlayAudioFilesRequest,
        result=AudioSession,
        access="admin",
        effect="action",
    )
    delete_audio_session = Operation(
        INFO,
        "delete_audio_session",
        RestBinding("DELETE", f"{ROOT}/v1.2/audioSessions/{{audioSessionId}}"),
        params=DeleteAudioSessionRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_audio_session = Operation(
        INFO,
        "get_audio_session",
        RestBinding("GET", f"{ROOT}/v1.2/audioSessions/{{audioSessionId}}"),
        params=GetAudioSessionRequest,
        result=AudioSession,
        access="admin",
        effect="read",
    )
    update_audio_session = Operation(
        INFO,
        "update_audio_session",
        RestBinding("PATCH", f"{ROOT}/v1.2/audioSessions/{{audioSessionId}}", body="object"),
        params=UpdateAudioSessionRequest,
        result=AudioSession,
        access="admin",
        effect="write",
        write="patch",
    )
    play_audio_files = Operation(
        INFO,
        "play_audio_files",
        RestBinding(
            "POST", f"{ROOT}/v1.2/audioSessions/{{audioSessionId}}/playAudioFiles", body="value", body_field="body"
        ),
        params=PlayAudioFilesRequestArgs,
        access="admin",
        effect="action",
    )
    get_audio_session_status = Operation(
        INFO,
        "get_audio_session_status",
        RestBinding("GET", f"{ROOT}/v1.2/audioSessions/{{audioSessionId}}/status"),
        params=GetAudioSessionStatusRequest,
        result=AudioSessionStatus,
        access="admin",
        effect="read",
    )
    stop_audio_files = Operation(
        INFO,
        "stop_audio_files",
        RestBinding("POST", f"{ROOT}/v1.2/audioSessions/{{audioSessionId}}/stopAudioFiles"),
        params=StopAudioFilesRequest,
        access="admin",
        effect="action",
    )
    list_targets = Operation(
        INFO,
        "list_targets",
        RestBinding("GET", f"{ROOT}/v1.2/targets"),
        result=list[Target],
        access="admin",
        effect="read",
    )
    get_target = Operation(
        INFO,
        "get_target",
        RestBinding("GET", f"{ROOT}/v1.2/targets/{{targetId}}"),
        params=GetTargetRequest,
        result=Target,
        access="admin",
        effect="read",
    )
    update_target = Operation(
        INFO,
        "update_target",
        RestBinding("PATCH", f"{ROOT}/v1.2/targets/{{targetId}}", body="object"),
        params=UpdateTargetRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_audio_files = Operation(
        INFO,
        "list_audio_files",
        RestBinding("GET", f"{ROOT}/v1.2/audioFiles"),
        result=list[AudioFile],
        access="admin",
        effect="read",
    )
    get_audio_file = Operation(
        INFO,
        "get_audio_file",
        RestBinding("GET", f"{ROOT}/v1.2/audioFiles/{{audioFileId}}"),
        params=GetAudioFileRequest,
        result=AudioFile,
        access="admin",
        effect="read",
    )
    list_volume_controllers = Operation(
        INFO,
        "list_volume_controllers",
        RestBinding("GET", f"{ROOT}/v1.2/volumeControllers"),
        result=list[VolumeController],
        access="admin",
        effect="read",
    )
    get_volume_controller = Operation(
        INFO,
        "get_volume_controller",
        RestBinding("GET", f"{ROOT}/v1.2/volumeControllers/{{volumeControllerId}}"),
        params=GetVolumeControllerRequest,
        result=VolumeController,
        access="admin",
        effect="read",
    )
    update_volume_controller = Operation(
        INFO,
        "update_volume_controller",
        RestBinding("PATCH", f"{ROOT}/v1.2/volumeControllers/{{volumeControllerId}}", body="object"),
        params=UpdateVolumeControllerRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    offset_volume = Operation(
        INFO,
        "offset_volume",
        RestBinding("POST", f"{ROOT}/v1.2/volumeControllers/{{volumeControllerId}}/offsetVolume", body="object"),
        params=OffsetVolumeRequest,
        access="admin",
        effect="action",
    )
    toggle_mute = Operation(
        INFO,
        "toggle_mute",
        RestBinding("POST", f"{ROOT}/v1.2/volumeControllers/{{volumeControllerId}}/toggleMute"),
        params=ToggleMuteRequest,
        access="admin",
        effect="action",
    )
    list_visual_profiles = Operation(
        INFO,
        "list_visual_profiles",
        RestBinding("GET", f"{ROOT}/v1.2/visualProfiles"),
        result=list[VisualProfile],
        access="admin",
        effect="read",
    )
    get_visual_profile = Operation(
        INFO,
        "get_visual_profile",
        RestBinding("GET", f"{ROOT}/v1.2/visualProfiles/{{visualProfileId}}"),
        params=GetVisualProfileRequest,
        result=VisualProfile,
        access="admin",
        effect="read",
    )
    get_server_info = Operation(
        INFO,
        "get_server_info",
        RestBinding("GET", f"{ROOT}/serverInfo"),
        result=ServerInfo,
        access="admin",
        effect="read",
    )
    list_paging_configurations = Operation(
        INFO,
        "list_paging_configurations",
        RestBinding("GET", f"{ROOT}/v1.2/pagingConfigurations"),
        result=list[PagingConfiguration],
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class AxisAudioManagerProApi(SyncApi):
    """AXIS Audio Manager Pro API (``axis-audio-manager-pro-api``)."""

    INFO = INFO

    def list_audio_sessions(self, *, request_options: RequestOptions | None = None) -> list[AudioSession]:
        """Retrieve a list of available audio sessions. Access: admin."""
        return self._run(OPS.list_audio_sessions, None, {}, request_options)

    @overload
    def create_audio_session(
        self, request: CreateAudioSessionRequest, /, *, request_options: RequestOptions | None = None
    ) -> AudioSession: ...
    @overload
    def create_audio_session(
        self, /, *, body: AudioSession, request_options: RequestOptions | None = None
    ) -> AudioSession: ...
    def create_audio_session(
        self,
        request: CreateAudioSessionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AudioSession:
        """Create a new audio session (types HTTP, RTP, SIP, WS).

        The docs show the request and response as arrays holding one session of each type; they are read as
        an illustration of the four types, so one session is sent and one is returned (see the open
        questions).

        Access: admin.
        """
        return self._run(OPS.create_audio_session, request, kwargs, request_options)

    def delete_audio_session_by_custom_id(
        self, custom_id: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Delete an audio session identified by customId (cancels ongoing playback). Access: admin."""
        self._run(OPS.delete_audio_session_by_custom_id, None, {"custom_id": custom_id}, request_options)

    @overload
    def play_audio_files_by_custom_id(
        self, request: PlayAudioFilesByCustomIdRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def play_audio_files_by_custom_id(
        self, /, *, custom_id: str, body: PlayAudioFilesRequest, request_options: RequestOptions | None = None
    ) -> None: ...
    def play_audio_files_by_custom_id(
        self,
        request: PlayAudioFilesByCustomIdRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Trigger playback of audio files from the site content library in the session (replaces current playback).

        Access: admin.
        """
        self._run(OPS.play_audio_files_by_custom_id, request, kwargs, request_options)

    def stop_audio_files_by_custom_id(self, custom_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Stop playback of audio files in a session identified by customId. Access: admin."""
        self._run(OPS.stop_audio_files_by_custom_id, None, {"custom_id": custom_id}, request_options)

    @overload
    def oneshot_play_audio_files(
        self, request: OneshotPlayAudioFilesRequest, /, *, request_options: RequestOptions | None = None
    ) -> AudioSession: ...
    @overload
    def oneshot_play_audio_files(
        self,
        /,
        *,
        custom_id: str | MISSING = MISSING,
        custom_text: str | MISSING = MISSING,
        file_ids: list[str],
        prio: Literal["HIGH", "MEDIUM", "LOW"] | MISSING = MISSING,
        repeat: int | MISSING = MISSING,
        targets: list[str],
        visual_profile_enabled: VisualProfileEnabled | MISSING = MISSING,
        visual_profile_id: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AudioSession: ...
    def oneshot_play_audio_files(
        self,
        request: OneshotPlayAudioFilesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AudioSession:
        """Create a temporary audio session and play audio files; deleted after playback (or stop by deleting the returned session).

        Access: admin.
        """
        return self._run(OPS.oneshot_play_audio_files, request, kwargs, request_options)

    def delete_audio_session(self, audio_session_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Delete an audio session by id (cancels ongoing playback). Access: admin."""
        self._run(OPS.delete_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    def get_audio_session(
        self, audio_session_id: str, *, request_options: RequestOptions | None = None
    ) -> AudioSession:
        """Retrieve an existing audio session. Access: admin."""
        return self._run(OPS.get_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    def update_audio_session(
        self,
        audio_session_id: str,
        *,
        prio: Literal["HIGH", "MEDIUM", "LOW"] | MISSING = MISSING,
        targets: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AudioSession:
        """Update targets and/or priority of an existing audio session.

        Changes only the fields given. Access: admin.
        """
        return self._run(
            OPS.update_audio_session,
            None,
            {"audio_session_id": audio_session_id, "prio": prio, "targets": targets},
            request_options,
        )

    @overload
    def play_audio_files(
        self, request: PlayAudioFilesRequestArgs, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def play_audio_files(
        self, /, *, audio_session_id: str, body: PlayAudioFilesRequest, request_options: RequestOptions | None = None
    ) -> None: ...
    def play_audio_files(
        self,
        request: PlayAudioFilesRequestArgs | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Play audio files in succession in an (HTTP) audio session; replaces current playback.

        Access: admin.
        """
        self._run(OPS.play_audio_files, request, kwargs, request_options)

    def get_audio_session_status(
        self, audio_session_id: str, *, request_options: RequestOptions | None = None
    ) -> AudioSessionStatus:
        """Check session status including playback and device availability.

        Since 1.1.

        Access: admin.
        """
        return self._run(OPS.get_audio_session_status, None, {"audio_session_id": audio_session_id}, request_options)

    def stop_audio_files(self, audio_session_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Stop the audio files playback in the session. Access: admin."""
        self._run(OPS.stop_audio_files, None, {"audio_session_id": audio_session_id}, request_options)

    def list_targets(self, *, request_options: RequestOptions | None = None) -> list[Target]:
        """List all targets (physical zones, destinations, devices, ...). Access: admin."""
        return self._run(OPS.list_targets, None, {}, request_options)

    def get_target(self, target_id: str, *, request_options: RequestOptions | None = None) -> Target:
        """Retrieve a specific target. Access: admin."""
        return self._run(OPS.get_target, None, {"target_id": target_id}, request_options)

    def update_target(self, target_id: str, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Enable or disable a target (disabled = silenced; for destinations all mapped sources stop).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_target, None, {"target_id": target_id, "enabled": enabled}, request_options)

    def list_audio_files(self, *, request_options: RequestOptions | None = None) -> list[AudioFile]:
        """List audio files in the announcement and music library. Access: admin."""
        return self._run(OPS.list_audio_files, None, {}, request_options)

    def get_audio_file(self, audio_file_id: str, *, request_options: RequestOptions | None = None) -> AudioFile:
        """Retrieve metadata for an audio file. Access: admin."""
        return self._run(OPS.get_audio_file, None, {"audio_file_id": audio_file_id}, request_options)

    def list_volume_controllers(self, *, request_options: RequestOptions | None = None) -> list[VolumeController]:
        """Retrieve all volume controllers. Access: admin."""
        return self._run(OPS.list_volume_controllers, None, {}, request_options)

    def get_volume_controller(
        self, volume_controller_id: str, *, request_options: RequestOptions | None = None
    ) -> VolumeController:
        """Retrieve a specific volume controller. Access: admin."""
        return self._run(
            OPS.get_volume_controller, None, {"volume_controller_id": volume_controller_id}, request_options
        )

    def update_volume_controller(
        self,
        volume_controller_id: str,
        *,
        muted: bool | MISSING = MISSING,
        volume_offset: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Modify a volume controller's mute state or volume offset.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.update_volume_controller,
            None,
            {"volume_controller_id": volume_controller_id, "muted": muted, "volume_offset": volume_offset},
            request_options,
        )

    def offset_volume(
        self, volume_controller_id: str, *, volume_offset: float, request_options: RequestOptions | None = None
    ) -> None:
        """Relative volume change (-100..+100); result clamped to [-100, +100] or configured max/min offset.

        Access: admin.
        """
        self._run(
            OPS.offset_volume,
            None,
            {"volume_controller_id": volume_controller_id, "volume_offset": volume_offset},
            request_options,
        )

    def toggle_mute(self, volume_controller_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Switch between mute/unmute. Access: admin."""
        self._run(OPS.toggle_mute, None, {"volume_controller_id": volume_controller_id}, request_options)

    def list_visual_profiles(self, *, request_options: RequestOptions | None = None) -> list[VisualProfile]:
        """Retrieve all visual profiles. Access: admin."""
        return self._run(OPS.list_visual_profiles, None, {}, request_options)

    def get_visual_profile(
        self, visual_profile_id: int, *, request_options: RequestOptions | None = None
    ) -> VisualProfile:
        """Retrieve a visual profile. Access: admin."""
        return self._run(OPS.get_visual_profile, None, {"visual_profile_id": visual_profile_id}, request_options)

    def get_server_info(self, *, request_options: RequestOptions | None = None) -> ServerInfo:
        """Basic information about the AXIS Audio Manager Pro server (versions, licensing, name and addresses).

        Access: admin.
        """
        return self._run(OPS.get_server_info, None, {}, request_options)

    def list_paging_configurations(self, *, request_options: RequestOptions | None = None) -> list[PagingConfiguration]:
        """List all SIP paging configurations. Access: admin."""
        return self._run(OPS.list_paging_configurations, None, {}, request_options)


class AsyncAxisAudioManagerProApi(AsyncApi):
    """AXIS Audio Manager Pro API (``axis-audio-manager-pro-api``)."""

    INFO = INFO

    async def list_audio_sessions(self, *, request_options: RequestOptions | None = None) -> list[AudioSession]:
        """Retrieve a list of available audio sessions. Access: admin."""
        return await self._run(OPS.list_audio_sessions, None, {}, request_options)

    @overload
    async def create_audio_session(
        self, request: CreateAudioSessionRequest, /, *, request_options: RequestOptions | None = None
    ) -> AudioSession: ...
    @overload
    async def create_audio_session(
        self, /, *, body: AudioSession, request_options: RequestOptions | None = None
    ) -> AudioSession: ...
    async def create_audio_session(
        self,
        request: CreateAudioSessionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AudioSession:
        """Create a new audio session (types HTTP, RTP, SIP, WS).

        The docs show the request and response as arrays holding one session of each type; they are read as
        an illustration of the four types, so one session is sent and one is returned (see the open
        questions).

        Access: admin.
        """
        return await self._run(OPS.create_audio_session, request, kwargs, request_options)

    async def delete_audio_session_by_custom_id(
        self, custom_id: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Delete an audio session identified by customId (cancels ongoing playback). Access: admin."""
        await self._run(OPS.delete_audio_session_by_custom_id, None, {"custom_id": custom_id}, request_options)

    @overload
    async def play_audio_files_by_custom_id(
        self, request: PlayAudioFilesByCustomIdRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def play_audio_files_by_custom_id(
        self, /, *, custom_id: str, body: PlayAudioFilesRequest, request_options: RequestOptions | None = None
    ) -> None: ...
    async def play_audio_files_by_custom_id(
        self,
        request: PlayAudioFilesByCustomIdRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Trigger playback of audio files from the site content library in the session (replaces current playback).

        Access: admin.
        """
        await self._run(OPS.play_audio_files_by_custom_id, request, kwargs, request_options)

    async def stop_audio_files_by_custom_id(
        self, custom_id: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Stop playback of audio files in a session identified by customId. Access: admin."""
        await self._run(OPS.stop_audio_files_by_custom_id, None, {"custom_id": custom_id}, request_options)

    @overload
    async def oneshot_play_audio_files(
        self, request: OneshotPlayAudioFilesRequest, /, *, request_options: RequestOptions | None = None
    ) -> AudioSession: ...
    @overload
    async def oneshot_play_audio_files(
        self,
        /,
        *,
        custom_id: str | MISSING = MISSING,
        custom_text: str | MISSING = MISSING,
        file_ids: list[str],
        prio: Literal["HIGH", "MEDIUM", "LOW"] | MISSING = MISSING,
        repeat: int | MISSING = MISSING,
        targets: list[str],
        visual_profile_enabled: VisualProfileEnabled | MISSING = MISSING,
        visual_profile_id: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AudioSession: ...
    async def oneshot_play_audio_files(
        self,
        request: OneshotPlayAudioFilesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> AudioSession:
        """Create a temporary audio session and play audio files; deleted after playback (or stop by deleting the returned session).

        Access: admin.
        """
        return await self._run(OPS.oneshot_play_audio_files, request, kwargs, request_options)

    async def delete_audio_session(
        self, audio_session_id: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Delete an audio session by id (cancels ongoing playback). Access: admin."""
        await self._run(OPS.delete_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    async def get_audio_session(
        self, audio_session_id: str, *, request_options: RequestOptions | None = None
    ) -> AudioSession:
        """Retrieve an existing audio session. Access: admin."""
        return await self._run(OPS.get_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    async def update_audio_session(
        self,
        audio_session_id: str,
        *,
        prio: Literal["HIGH", "MEDIUM", "LOW"] | MISSING = MISSING,
        targets: list[str] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AudioSession:
        """Update targets and/or priority of an existing audio session.

        Changes only the fields given. Access: admin.
        """
        return await self._run(
            OPS.update_audio_session,
            None,
            {"audio_session_id": audio_session_id, "prio": prio, "targets": targets},
            request_options,
        )

    @overload
    async def play_audio_files(
        self, request: PlayAudioFilesRequestArgs, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def play_audio_files(
        self, /, *, audio_session_id: str, body: PlayAudioFilesRequest, request_options: RequestOptions | None = None
    ) -> None: ...
    async def play_audio_files(
        self,
        request: PlayAudioFilesRequestArgs | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Play audio files in succession in an (HTTP) audio session; replaces current playback.

        Access: admin.
        """
        await self._run(OPS.play_audio_files, request, kwargs, request_options)

    async def get_audio_session_status(
        self, audio_session_id: str, *, request_options: RequestOptions | None = None
    ) -> AudioSessionStatus:
        """Check session status including playback and device availability.

        Since 1.1.

        Access: admin.
        """
        return await self._run(
            OPS.get_audio_session_status, None, {"audio_session_id": audio_session_id}, request_options
        )

    async def stop_audio_files(self, audio_session_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Stop the audio files playback in the session. Access: admin."""
        await self._run(OPS.stop_audio_files, None, {"audio_session_id": audio_session_id}, request_options)

    async def list_targets(self, *, request_options: RequestOptions | None = None) -> list[Target]:
        """List all targets (physical zones, destinations, devices, ...). Access: admin."""
        return await self._run(OPS.list_targets, None, {}, request_options)

    async def get_target(self, target_id: str, *, request_options: RequestOptions | None = None) -> Target:
        """Retrieve a specific target. Access: admin."""
        return await self._run(OPS.get_target, None, {"target_id": target_id}, request_options)

    async def update_target(
        self, target_id: str, *, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable a target (disabled = silenced; for destinations all mapped sources stop).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_target, None, {"target_id": target_id, "enabled": enabled}, request_options)

    async def list_audio_files(self, *, request_options: RequestOptions | None = None) -> list[AudioFile]:
        """List audio files in the announcement and music library. Access: admin."""
        return await self._run(OPS.list_audio_files, None, {}, request_options)

    async def get_audio_file(self, audio_file_id: str, *, request_options: RequestOptions | None = None) -> AudioFile:
        """Retrieve metadata for an audio file. Access: admin."""
        return await self._run(OPS.get_audio_file, None, {"audio_file_id": audio_file_id}, request_options)

    async def list_volume_controllers(self, *, request_options: RequestOptions | None = None) -> list[VolumeController]:
        """Retrieve all volume controllers. Access: admin."""
        return await self._run(OPS.list_volume_controllers, None, {}, request_options)

    async def get_volume_controller(
        self, volume_controller_id: str, *, request_options: RequestOptions | None = None
    ) -> VolumeController:
        """Retrieve a specific volume controller. Access: admin."""
        return await self._run(
            OPS.get_volume_controller, None, {"volume_controller_id": volume_controller_id}, request_options
        )

    async def update_volume_controller(
        self,
        volume_controller_id: str,
        *,
        muted: bool | MISSING = MISSING,
        volume_offset: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Modify a volume controller's mute state or volume offset.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.update_volume_controller,
            None,
            {"volume_controller_id": volume_controller_id, "muted": muted, "volume_offset": volume_offset},
            request_options,
        )

    async def offset_volume(
        self, volume_controller_id: str, *, volume_offset: float, request_options: RequestOptions | None = None
    ) -> None:
        """Relative volume change (-100..+100); result clamped to [-100, +100] or configured max/min offset.

        Access: admin.
        """
        await self._run(
            OPS.offset_volume,
            None,
            {"volume_controller_id": volume_controller_id, "volume_offset": volume_offset},
            request_options,
        )

    async def toggle_mute(self, volume_controller_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Switch between mute/unmute. Access: admin."""
        await self._run(OPS.toggle_mute, None, {"volume_controller_id": volume_controller_id}, request_options)

    async def list_visual_profiles(self, *, request_options: RequestOptions | None = None) -> list[VisualProfile]:
        """Retrieve all visual profiles. Access: admin."""
        return await self._run(OPS.list_visual_profiles, None, {}, request_options)

    async def get_visual_profile(
        self, visual_profile_id: int, *, request_options: RequestOptions | None = None
    ) -> VisualProfile:
        """Retrieve a visual profile. Access: admin."""
        return await self._run(OPS.get_visual_profile, None, {"visual_profile_id": visual_profile_id}, request_options)

    async def get_server_info(self, *, request_options: RequestOptions | None = None) -> ServerInfo:
        """Basic information about the AXIS Audio Manager Pro server (versions, licensing, name and addresses).

        Access: admin.
        """
        return await self._run(OPS.get_server_info, None, {}, request_options)

    async def list_paging_configurations(
        self, *, request_options: RequestOptions | None = None
    ) -> list[PagingConfiguration]:
        """List all SIP paging configurations. Access: admin."""
        return await self._run(OPS.list_paging_configurations, None, {}, request_options)
