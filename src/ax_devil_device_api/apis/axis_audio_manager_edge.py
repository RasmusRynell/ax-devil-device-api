# GENERATED from specs/apis/audio-systems/axis-audio-manager-edge-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Integrate external tools with AXIS Audio Manager Edge. List targets (devices and zones), control volume controllers, list, create and stop audio sessions, and list audio files.

Docs: https://developer.axis.com/vapix/audio-systems/axis-audio-manager-edge-api/
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.rest import RestBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class TargetStatus(Model):
    type: Literal["error", "warning", "pending", "ok"] | None = None
    """The status type."""


class TargetRef(Model):
    type: str | None = None
    """device, physicalZone (may be extended)."""
    id: str | None = None
    """A unique ID of the target."""


class DeviceTarget(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"ip_address", "nice_name", "serial_number"})
    type: Literal["device"]
    id: str
    """A unique ID of the device."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    status: TargetStatus | None = None
    ip_address: str | None = Field(default=None, validation_alias="ipAddress", serialization_alias="ipAddress")
    """The LAN IP address of the device."""
    serial_number: str | None = Field(default=None, validation_alias="serialNumber", serialization_alias="serialNumber")


class PhysicalZoneTarget(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"nice_name"})
    type: Literal["physicalZone"]
    id: str
    """A unique ID of the physical zone."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    children: list[TargetRef] | None = None
    """A list of devices contained in the zone."""


Target = DeviceTarget | PhysicalZoneTarget


class VolumeControllerContentClassesItem(Model):
    type: Literal["music", "paging", "announcements", "advertisements"] | None = None


class VolumeController(Model):
    allow_mute: bool | None = Field(default=None, validation_alias="allowMute", serialization_alias="allowMute")
    """Whether the volume controller can be muted."""
    content_classes: list[VolumeControllerContentClassesItem] | None = Field(
        default=None, validation_alias="contentClasses", serialization_alias="contentClasses"
    )
    """Target content classes."""
    id: str
    max_volume: float | None = Field(default=None, validation_alias="maxVolume", serialization_alias="maxVolume")
    min_volume: float | None = Field(default=None, validation_alias="minVolume", serialization_alias="minVolume")
    muted: bool | None = None
    target: list[TargetRef] | None = None
    """The targets of the volume controller."""
    volume: float | None = None
    """Volume for the content type of all targets associated with the controller; between minVolume and maxVolume."""


class AudioSession(Model):
    type: Literal[
        "vapixOneWay", "vapixTwoWay", "sipOneWay", "sipTwoWay", "lineIn", "vapixMediaclip", "externalRTP", "oneShot"
    ]
    intermediary_device: str | None = Field(
        default=None, validation_alias="intermediaryDevice", serialization_alias="intermediaryDevice"
    )
    """ID of the physical device used as intermediary. Not available when type is externalRTP."""
    targets: list[str] | None = None
    """Targets of the session. Not available when type is vapixTwoWay or sipTwoWay."""
    id: str
    prio: int | None = None
    """Priority; larger number = higher priority."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    multicast_address: str | None = Field(
        default=None, validation_alias="multicastAddress", serialization_alias="multicastAddress"
    )
    """Only when type is externalRTP."""
    port: int | None = None
    """Multicast port. Only when type is externalRTP."""


class AudioFile(Model):
    track_id: str = Field(validation_alias="trackId", serialization_alias="trackId")
    """The unique identifier of the audio file."""
    name: str | None = None


class GetTargetRequest(Model):
    target_id: str = Field(validation_alias="targetId", serialization_alias="targetId")
    """A unique target ID."""


class GetVolumeControllerRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")


class ModifyVolumeControllerRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")
    volume: float | None = None
    """Volume for the content type of all targets associated with the controller; between minVolume and maxVolume."""
    muted: bool | None = None


class ToggleMuteRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")


class ToggleMuteResult(Model):
    muted: bool
    """Whether the volume controller is muted after the toggle."""


class OffsetVolumeRequest(Model):
    volume_controller_id: str = Field(validation_alias="volumeControllerId", serialization_alias="volumeControllerId")
    volume_offset: float = Field(validation_alias="volumeOffset", serialization_alias="volumeOffset")
    """Requested volume change relative to the current value. Negative decreases."""


class OffsetVolumeResult(Model):
    volume: float
    """The volume after adjustment."""


class GetAudioSessionRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")


class CreateOneshotAudioSessionRequest(Model):
    file_ids: list[str] = Field(validation_alias="fileIds", serialization_alias="fileIds")
    """Array of file IDs (UUID format) to be used in the audio session."""
    prio: Literal["high", "medium", "low"] | None = None
    """The priority level of the audio session."""
    targets: list[str]
    """Array of target IDs (zones or devices) of the audio session."""


class CreateOneshotAudioSessionResult(Model):
    type: Literal["oneShot"]
    targets: list[str] | None = None
    prio: int | None = None
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")


class StopAudioSessionRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")
    """The ID (UUID format) of the audio session to stop."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/vapix/aam-edge/api"

INFO = ApiInfo(
    id="axis-audio-manager-edge-api",
    name="AXIS Audio Manager Edge API",
    family=Family.REST,
    docs=("https://developer.axis.com/vapix/audio-systems/axis-audio-manager-edge-api/",),
    errors={
        400: ErrorCode("Bad Request. application/json error object (see envelope.error_schema).", "invalid_argument"),
        404: ErrorCode("Not found. application/json error object, e.g. reason ResourceInstanceNotFound.", "not_found"),
        415: ErrorCode("Invalid content type. application/json error object.", "invalid_argument"),
        500: ErrorCode("Internal server error. application/json; body example missing in doc.", "internal"),
    },
)


class OPS:
    list_targets = Operation(
        INFO,
        "list_targets",
        RestBinding("GET", f"{ROOT}/v1.0/targets"),
        result=list[Target],
        access="admin",
        effect="read",
    )
    get_target = Operation(
        INFO,
        "get_target",
        RestBinding("GET", f"{ROOT}/v1.0/targets/{{targetId}}"),
        params=GetTargetRequest,
        result=Target,
        access="admin",
        effect="read",
    )
    list_volume_controllers = Operation(
        INFO,
        "list_volume_controllers",
        RestBinding("GET", f"{ROOT}/v1.1/volumeControllers"),
        result=list[VolumeController],
        access="admin",
        effect="read",
    )
    get_volume_controller = Operation(
        INFO,
        "get_volume_controller",
        RestBinding("GET", f"{ROOT}/v1.1/volumeControllers/{{volumeControllerId}}"),
        params=GetVolumeControllerRequest,
        result=VolumeController,
        access="admin",
        effect="read",
    )
    modify_volume_controller = Operation(
        INFO,
        "modify_volume_controller",
        RestBinding("PATCH", f"{ROOT}/v1.1/volumeControllers/{{volumeControllerId}}", body="object"),
        params=ModifyVolumeControllerRequest,
        result=VolumeController,
        access="admin",
        effect="write",
        write="patch",
    )
    toggle_mute = Operation(
        INFO,
        "toggle_mute",
        RestBinding("POST", f"{ROOT}/v1.3/volumeControllers/{{volumeControllerId}}/toggleMute"),
        params=ToggleMuteRequest,
        result=ToggleMuteResult,
        access="admin",
        effect="action",
    )
    offset_volume = Operation(
        INFO,
        "offset_volume",
        RestBinding("POST", f"{ROOT}/v1.3/volumeControllers/{{volumeControllerId}}/offsetVolume", body="object"),
        params=OffsetVolumeRequest,
        result=OffsetVolumeResult,
        access="admin",
        effect="action",
    )
    list_audio_sessions = Operation(
        INFO,
        "list_audio_sessions",
        RestBinding("GET", f"{ROOT}/v1.2/audioSessions"),
        result=list[AudioSession],
        access="admin",
        effect="read",
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
    create_oneshot_audio_session = Operation(
        INFO,
        "create_oneshot_audio_session",
        RestBinding("POST", f"{ROOT}/v1.2/audioSessions/oneshotPlayAudioFiles", body="object"),
        params=CreateOneshotAudioSessionRequest,
        result=CreateOneshotAudioSessionResult,
        access="admin",
        effect="write",
        write="create",
    )
    stop_audio_session = Operation(
        INFO,
        "stop_audio_session",
        RestBinding("POST", f"{ROOT}/v1.2/audioSessions/{{audioSessionId}}/stopAudioFiles"),
        params=StopAudioSessionRequest,
        access="admin",
        effect="action",
    )
    list_audio_files = Operation(
        INFO,
        "list_audio_files",
        RestBinding("GET", f"{ROOT}/v1.2/audioFiles"),
        result=list[AudioFile],
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class AxisAudioManagerEdgeApi(SyncApi):
    """AXIS Audio Manager Edge API (``axis-audio-manager-edge-api``)."""

    INFO = INFO

    def list_targets(self, *, request_options: RequestOptions | None = None) -> list[Target]:
        """Retrieve all targets managed by AXIS Audio Manager Edge. Access: admin."""
        return self._run(OPS.list_targets, None, {}, request_options)

    def get_target(self, target_id: str, *, request_options: RequestOptions | None = None) -> Target:
        """Retrieve the detailed information of a specified target. Access: admin."""
        return self._run(OPS.get_target, None, {"target_id": target_id}, request_options)

    def list_volume_controllers(self, *, request_options: RequestOptions | None = None) -> list[VolumeController]:
        """Retrieve all volume controllers. Access: admin."""
        return self._run(OPS.list_volume_controllers, None, {}, request_options)

    def get_volume_controller(
        self, volume_controller_id: str, *, request_options: RequestOptions | None = None
    ) -> VolumeController:
        """Retrieve a specified volume controller. Access: admin."""
        return self._run(
            OPS.get_volume_controller, None, {"volume_controller_id": volume_controller_id}, request_options
        )

    def modify_volume_controller(
        self,
        volume_controller_id: str,
        *,
        volume: float | MISSING = MISSING,
        muted: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> VolumeController:
        """Modify volume and/or mute status of a volume controller.

        Changes only the fields given. Access: admin.
        """
        return self._run(
            OPS.modify_volume_controller,
            None,
            {"volume_controller_id": volume_controller_id, "volume": volume, "muted": muted},
            request_options,
        )

    def toggle_mute(
        self, volume_controller_id: str, *, request_options: RequestOptions | None = None
    ) -> ToggleMuteResult:
        """Toggle the mute status of a volume controller. Access: admin."""
        return self._run(OPS.toggle_mute, None, {"volume_controller_id": volume_controller_id}, request_options)

    def offset_volume(
        self, volume_controller_id: str, *, volume_offset: float, request_options: RequestOptions | None = None
    ) -> OffsetVolumeResult:
        """Adjust volume by a specified relative amount. Access: admin."""
        return self._run(
            OPS.offset_volume,
            None,
            {"volume_controller_id": volume_controller_id, "volume_offset": volume_offset},
            request_options,
        )

    def list_audio_sessions(self, *, request_options: RequestOptions | None = None) -> list[AudioSession]:
        """Retrieve all audio sessions. Access: admin."""
        return self._run(OPS.list_audio_sessions, None, {}, request_options)

    def get_audio_session(
        self, audio_session_id: str, *, request_options: RequestOptions | None = None
    ) -> AudioSession:
        """Retrieve a specified audio session. Access: admin."""
        return self._run(OPS.get_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    def create_oneshot_audio_session(
        self,
        *,
        file_ids: list[str],
        prio: Literal["high", "medium", "low"] | MISSING = MISSING,
        targets: list[str],
        request_options: RequestOptions | None = None,
    ) -> CreateOneshotAudioSessionResult:
        """Create a one-shot audio session playing audio files on targets. Access: admin."""
        return self._run(
            OPS.create_oneshot_audio_session,
            None,
            {"file_ids": file_ids, "prio": prio, "targets": targets},
            request_options,
        )

    def stop_audio_session(self, audio_session_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Stop an audio session. Access: admin."""
        self._run(OPS.stop_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    def list_audio_files(self, *, request_options: RequestOptions | None = None) -> list[AudioFile]:
        """List audio files. Access: admin."""
        return self._run(OPS.list_audio_files, None, {}, request_options)


class AsyncAxisAudioManagerEdgeApi(AsyncApi):
    """AXIS Audio Manager Edge API (``axis-audio-manager-edge-api``)."""

    INFO = INFO

    async def list_targets(self, *, request_options: RequestOptions | None = None) -> list[Target]:
        """Retrieve all targets managed by AXIS Audio Manager Edge. Access: admin."""
        return await self._run(OPS.list_targets, None, {}, request_options)

    async def get_target(self, target_id: str, *, request_options: RequestOptions | None = None) -> Target:
        """Retrieve the detailed information of a specified target. Access: admin."""
        return await self._run(OPS.get_target, None, {"target_id": target_id}, request_options)

    async def list_volume_controllers(self, *, request_options: RequestOptions | None = None) -> list[VolumeController]:
        """Retrieve all volume controllers. Access: admin."""
        return await self._run(OPS.list_volume_controllers, None, {}, request_options)

    async def get_volume_controller(
        self, volume_controller_id: str, *, request_options: RequestOptions | None = None
    ) -> VolumeController:
        """Retrieve a specified volume controller. Access: admin."""
        return await self._run(
            OPS.get_volume_controller, None, {"volume_controller_id": volume_controller_id}, request_options
        )

    async def modify_volume_controller(
        self,
        volume_controller_id: str,
        *,
        volume: float | MISSING = MISSING,
        muted: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> VolumeController:
        """Modify volume and/or mute status of a volume controller.

        Changes only the fields given. Access: admin.
        """
        return await self._run(
            OPS.modify_volume_controller,
            None,
            {"volume_controller_id": volume_controller_id, "volume": volume, "muted": muted},
            request_options,
        )

    async def toggle_mute(
        self, volume_controller_id: str, *, request_options: RequestOptions | None = None
    ) -> ToggleMuteResult:
        """Toggle the mute status of a volume controller. Access: admin."""
        return await self._run(OPS.toggle_mute, None, {"volume_controller_id": volume_controller_id}, request_options)

    async def offset_volume(
        self, volume_controller_id: str, *, volume_offset: float, request_options: RequestOptions | None = None
    ) -> OffsetVolumeResult:
        """Adjust volume by a specified relative amount. Access: admin."""
        return await self._run(
            OPS.offset_volume,
            None,
            {"volume_controller_id": volume_controller_id, "volume_offset": volume_offset},
            request_options,
        )

    async def list_audio_sessions(self, *, request_options: RequestOptions | None = None) -> list[AudioSession]:
        """Retrieve all audio sessions. Access: admin."""
        return await self._run(OPS.list_audio_sessions, None, {}, request_options)

    async def get_audio_session(
        self, audio_session_id: str, *, request_options: RequestOptions | None = None
    ) -> AudioSession:
        """Retrieve a specified audio session. Access: admin."""
        return await self._run(OPS.get_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    async def create_oneshot_audio_session(
        self,
        *,
        file_ids: list[str],
        prio: Literal["high", "medium", "low"] | MISSING = MISSING,
        targets: list[str],
        request_options: RequestOptions | None = None,
    ) -> CreateOneshotAudioSessionResult:
        """Create a one-shot audio session playing audio files on targets. Access: admin."""
        return await self._run(
            OPS.create_oneshot_audio_session,
            None,
            {"file_ids": file_ids, "prio": prio, "targets": targets},
            request_options,
        )

    async def stop_audio_session(self, audio_session_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Stop an audio session. Access: admin."""
        await self._run(OPS.stop_audio_session, None, {"audio_session_id": audio_session_id}, request_options)

    async def list_audio_files(self, *, request_options: RequestOptions | None = None) -> list[AudioFile]:
        """List audio files. Access: admin."""
        return await self._run(OPS.list_audio_files, None, {}, request_options)
