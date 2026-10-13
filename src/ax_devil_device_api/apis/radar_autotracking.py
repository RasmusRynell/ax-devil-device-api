# GENERATED from specs/apis/radar/radar-autotracking.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the autotracking software of an Axis radar, which steers a PTZ camera to follow detected objects.

Docs: https://developer.axis.com/vapix/radar/radar-autotracking/
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ConnectionState = Literal["disconnected", "connecting", "autotune", "connected", "connect_failed"]


class CameraConnection(Model):
    """The PTZ camera the radar is connected to. The password is never returned."""

    ip: str | None = None
    """IP address of the PTZ camera. Empty when disconnected."""
    user: str | None = None
    """User name used to log in to the PTZ camera."""
    state: ConnectionState
    """State of the connection."""


class RangedValue(Model):
    """A current value with its allowed range. The unit depends on the operation."""

    value: float
    """The current value."""
    min_value: float | None = Field(default=None, validation_alias="minValue", serialization_alias="minValue")
    """The smallest allowed value."""
    max_value: float | None = Field(default=None, validation_alias="maxValue", serialization_alias="maxValue")
    """The largest allowed value."""


class Flag(Model):
    value: bool
    """Whether the feature is enabled."""


class ReturnToHomeTimeout(Model):
    value: float
    """The timeout in seconds."""
    min_timeout: float | None = Field(default=None, validation_alias="minTimeout", serialization_alias="minTimeout")
    """The minimum timeout in seconds."""
    max_timeout: float | None = Field(default=None, validation_alias="maxTimeout", serialization_alias="maxTimeout")
    """The maximum timeout in seconds."""


class ObjectTypes(Model):
    """Which object types the camera tracks."""

    small: bool
    """Track small objects."""
    human: bool
    """Track humans."""
    vehicle: bool
    """Track vehicles."""
    unknown: bool
    """Track unidentified objects."""


class SetObjectTypesToTrackRequest(Model):
    """Arguments of ``set_object_types_to_track``. All four object types are set at once."""

    small: bool
    """Track small objects."""
    human: bool
    """Track humans."""
    vehicle: bool
    """Track vehicles."""
    unknown: bool
    """Track unidentified objects."""

    @classmethod
    def from_current(cls, types: ObjectTypes) -> SetObjectTypesToTrackRequest:
        """A request that rewrites ``types`` unchanged: copy it, edit fields, send it back."""
        data = types.request_data()
        return cls(**data)


ObjectType = Literal["small", "human", "vehicle", "unknown"]


class ReturnToHomeTimeoutCapabilities(Model):
    min_value: float | None = Field(default=None, validation_alias="minValue", serialization_alias="minValue")
    max_value: float | None = Field(default=None, validation_alias="maxValue", serialization_alias="maxValue")


class ObjectTypesCapabilities(Model):
    types: list[ObjectType] | None = None
    """The object types that can be tracked."""


class Capabilities(Model):
    """The capabilities of the API version in use."""

    return_to_home_enabled: dict[str, Any] | None = Field(
        default=None, validation_alias="returnToHomeEnabled", serialization_alias="returnToHomeEnabled"
    )
    """Present if return to home is supported."""
    return_to_home_timeout: ReturnToHomeTimeoutCapabilities | None = Field(
        default=None, validation_alias="returnToHomeTimeout", serialization_alias="returnToHomeTimeout"
    )
    object_types_to_track: ObjectTypesCapabilities | None = Field(
        default=None, validation_alias="objectTypesToTrack", serialization_alias="objectTypesToTrack"
    )


class SetCameraConnectionRequest(Model):
    """Arguments of ``set_camera_connection``. An empty ``ip`` disconnects from the camera."""

    ip: str
    """The camera's IP address."""
    user: str
    """The username to log in to the camera."""
    password: str = Field(validation_alias="pass", serialization_alias="pass")
    """The password to log in to the camera."""


class SetCameraMountingHeightRequest(Model):
    value: float
    """The vertical mounting height of the camera, measured in meters."""


class SetCameraPanOffsetRequest(Model):
    value: float
    """The camera pan offset, measured in degrees."""


class SetCameraTiltOffsetRequest(Model):
    value: float
    """The camera tilt offset, measured in degrees."""


class SetCameraZoomDegreeRequest(Model):
    value: float
    """The camera zoom degree, measured in percent."""


class SetTrackingEnabledRequest(Model):
    value: bool
    """True to enable tracking, false to disable it."""


class SetGuardTourEnabledRequest(Model):
    value: bool
    """True to enable the guard tour, false to disable it."""


class SetGuardTourTimeRequest(Model):
    value: float
    """The guard tour time, measured in seconds."""


class SetReturnToHomeEnabledRequest(Model):
    value: bool
    """True to enable return to home, false to disable it."""


class SetReturnToHomeTimeoutRequest(Model):
    value: float
    """The timeout in seconds."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/radar-autotracking.cgi"

INFO = ApiInfo(
    id="radar-autotracking",
    name="Radar autotracking",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("radar-autotracking"), ParamDiscovery("Properties.Radar.Radar", "yes")),
    docs=("https://developer.axis.com/vapix/radar/radar-autotracking/",),
    errors={
        100: ErrorCode(
            "UNSUPPORTED_API_VERSION. The requested API version is not supported by this implementation.", "unsupported"
        ),
        102: ErrorCode(
            "JSON_KEY_NOT_FOUND_ERROR. A mandatory input parameter was not found in the input.", "invalid_argument"
        ),
        103: ErrorCode("JSON_INVALID_TYPE. The type of a provided JSON parameter was incorrect.", "invalid_argument"),
        200: ErrorCode("JSON_INVALID_ERROR. The provided JSON input was invalid.", "invalid_argument"),
        300: ErrorCode("PARAM_INVALID_VALUE_ERROR. Invalid parameter value., kind: invalid_argument"),
    },
)


class OPS:
    get_camera_connection = Operation(
        INFO,
        "get_camera_connection",
        JsonRpcBinding("getCameraConnection", PATH),
        result=CameraConnection,
        access="operator",
        effect="read",
    )
    set_camera_connection = Operation(
        INFO,
        "set_camera_connection",
        JsonRpcBinding("setCameraConnection", PATH),
        params=SetCameraConnectionRequest,
        access="operator",
        effect="write",
        write="replace",
    )
    get_camera_mounting_height = Operation(
        INFO,
        "get_camera_mounting_height",
        JsonRpcBinding("getCameraMountingHeight", PATH),
        result=RangedValue,
        access="operator",
        effect="read",
    )
    set_camera_mounting_height = Operation(
        INFO,
        "set_camera_mounting_height",
        JsonRpcBinding("setCameraMountingHeight", PATH),
        params=SetCameraMountingHeightRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_camera_pan_offset = Operation(
        INFO,
        "get_camera_pan_offset",
        JsonRpcBinding("getCameraPanOffset", PATH),
        result=RangedValue,
        access="operator",
        effect="read",
    )
    set_camera_pan_offset = Operation(
        INFO,
        "set_camera_pan_offset",
        JsonRpcBinding("setCameraPanOffset", PATH),
        params=SetCameraPanOffsetRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    save_camera_pan_offset = Operation(
        INFO,
        "save_camera_pan_offset",
        JsonRpcBinding("saveCameraPanOffset", PATH),
        access="operator",
        effect="action",
        errors={301: ErrorCode("INVALID_CONNECTION_ERROR. Invalid connection to the camera., kind: unavailable")},
    )
    get_camera_tilt_offset = Operation(
        INFO,
        "get_camera_tilt_offset",
        JsonRpcBinding("getCameraTiltOffset", PATH),
        result=RangedValue,
        access="operator",
        effect="read",
    )
    set_camera_tilt_offset = Operation(
        INFO,
        "set_camera_tilt_offset",
        JsonRpcBinding("setCameraTiltOffset", PATH),
        params=SetCameraTiltOffsetRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    save_camera_tilt_offset = Operation(
        INFO,
        "save_camera_tilt_offset",
        JsonRpcBinding("saveCameraTiltOffset", PATH),
        access="operator",
        effect="action",
        errors={301: ErrorCode("INVALID_CONNECTION_ERROR. Invalid connection to the camera., kind: unavailable")},
    )
    get_camera_zoom_degree = Operation(
        INFO,
        "get_camera_zoom_degree",
        JsonRpcBinding("getCameraZoomDegree", PATH),
        result=RangedValue,
        access="operator",
        effect="read",
    )
    set_camera_zoom_degree = Operation(
        INFO,
        "set_camera_zoom_degree",
        JsonRpcBinding("setCameraZoomDegree", PATH),
        params=SetCameraZoomDegreeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_tracking_enabled = Operation(
        INFO,
        "get_tracking_enabled",
        JsonRpcBinding("getTrackingEnabled", PATH),
        result=Flag,
        access="operator",
        effect="read",
    )
    set_tracking_enabled = Operation(
        INFO,
        "set_tracking_enabled",
        JsonRpcBinding("setTrackingEnabled", PATH),
        params=SetTrackingEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_guard_tour_enabled = Operation(
        INFO,
        "get_guard_tour_enabled",
        JsonRpcBinding("getGuardTourEnabled", PATH),
        result=Flag,
        access="operator",
        effect="read",
    )
    set_guard_tour_enabled = Operation(
        INFO,
        "set_guard_tour_enabled",
        JsonRpcBinding("setGuardTourEnabled", PATH),
        params=SetGuardTourEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_guard_tour_time = Operation(
        INFO,
        "get_guard_tour_time",
        JsonRpcBinding("getGuardTourTime", PATH),
        result=RangedValue,
        access="operator",
        effect="read",
    )
    set_guard_tour_time = Operation(
        INFO,
        "set_guard_tour_time",
        JsonRpcBinding("setGuardTourTime", PATH),
        params=SetGuardTourTimeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_return_to_home_enabled = Operation(
        INFO,
        "get_return_to_home_enabled",
        JsonRpcBinding("getReturnToHomeEnabled", PATH),
        result=Flag,
        access="operator",
        effect="read",
    )
    set_return_to_home_enabled = Operation(
        INFO,
        "set_return_to_home_enabled",
        JsonRpcBinding("setReturnToHomeEnabled", PATH),
        params=SetReturnToHomeEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_return_to_home_timeout = Operation(
        INFO,
        "get_return_to_home_timeout",
        JsonRpcBinding("getReturnToHomeTimeout", PATH),
        result=ReturnToHomeTimeout,
        access="operator",
        effect="read",
    )
    set_return_to_home_timeout = Operation(
        INFO,
        "set_return_to_home_timeout",
        JsonRpcBinding("setReturnToHomeTimeout", PATH),
        params=SetReturnToHomeTimeoutRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_object_types_to_track = Operation(
        INFO,
        "get_object_types_to_track",
        JsonRpcBinding("getObjectTypesToTrack", PATH),
        result=ObjectTypes,
        access="operator",
        effect="read",
    )
    set_object_types_to_track = Operation(
        INFO,
        "set_object_types_to_track",
        JsonRpcBinding("setObjectTypesToTrack", PATH),
        params=SetObjectTypesToTrackRequest,
        access="operator",
        effect="write",
        write="replace",
    )
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        result=Capabilities,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RadarAutotrackingApi(SyncApi):
    """Radar autotracking (``radar-autotracking``, version 1)."""

    INFO = INFO

    def get_camera_connection(self, *, request_options: RequestOptions | None = None) -> CameraConnection:
        """Get the current camera connection and its state. Access: operator."""
        return self._run(OPS.get_camera_connection, None, {}, request_options)

    def set_camera_connection(
        self, *, ip: str, user: str, password: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the camera connection of the radar and try to connect.

        Information on the connection state is available from ``get_camera_connection``. An empty IP address
        disconnects.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        self._run(OPS.set_camera_connection, None, {"ip": ip, "user": user, "password": password}, request_options)

    def get_camera_mounting_height(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the mounting height in meters and its allowed range. Access: operator."""
        return self._run(OPS.get_camera_mounting_height, None, {}, request_options)

    def set_camera_mounting_height(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the mounting height (see ``get_camera_mounting_height`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_camera_mounting_height, None, {"value": value}, request_options)

    def get_camera_pan_offset(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the camera pan offset in degrees and its allowed range. Access: operator."""
        return self._run(OPS.get_camera_pan_offset, None, {}, request_options)

    def set_camera_pan_offset(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the camera pan offset (see ``get_camera_pan_offset`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_camera_pan_offset, None, {"value": value}, request_options)

    def save_camera_pan_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Read the current pan position from the connected camera and save it as the camera pan offset.

        Access: operator.
        """
        self._run(OPS.save_camera_pan_offset, None, {}, request_options)

    def get_camera_tilt_offset(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the camera tilt offset in degrees and its allowed range. Access: operator."""
        return self._run(OPS.get_camera_tilt_offset, None, {}, request_options)

    def set_camera_tilt_offset(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the camera tilt offset (see ``get_camera_tilt_offset`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_camera_tilt_offset, None, {"value": value}, request_options)

    def save_camera_tilt_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Read the current tilt position from the connected camera and save it as the camera tilt offset.

        Access: operator.
        """
        self._run(OPS.save_camera_tilt_offset, None, {}, request_options)

    def get_camera_zoom_degree(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the zoom degree in percent and its allowed range. Access: operator."""
        return self._run(OPS.get_camera_zoom_degree, None, {}, request_options)

    def set_camera_zoom_degree(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the zoom degree (in percent) of the camera.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_camera_zoom_degree, None, {"value": value}, request_options)

    def get_tracking_enabled(self, *, request_options: RequestOptions | None = None) -> Flag:
        """Get whether tracking is enabled. Access: operator."""
        return self._run(OPS.get_tracking_enabled, None, {}, request_options)

    def set_tracking_enabled(self, value: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the radar tracking. Changes only the fields given. Access: operator."""
        self._run(OPS.set_tracking_enabled, None, {"value": value}, request_options)

    def get_guard_tour_enabled(self, *, request_options: RequestOptions | None = None) -> Flag:
        """Get whether the guard tour is enabled. Access: operator."""
        return self._run(OPS.get_guard_tour_enabled, None, {}, request_options)

    def set_guard_tour_enabled(self, value: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the guard tour. Changes only the fields given. Access: operator."""
        self._run(OPS.set_guard_tour_enabled, None, {"value": value}, request_options)

    def get_guard_tour_time(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the guard tour time in seconds and its allowed range. Access: operator."""
        return self._run(OPS.get_guard_tour_time, None, {}, request_options)

    def set_guard_tour_time(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the guard tour time (see ``get_guard_tour_time`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_guard_tour_time, None, {"value": value}, request_options)

    def get_return_to_home_enabled(self, *, request_options: RequestOptions | None = None) -> Flag:
        """Get whether return to home is enabled. Access: operator."""
        return self._run(OPS.get_return_to_home_enabled, None, {}, request_options)

    def set_return_to_home_enabled(self, value: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the return to home function.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_return_to_home_enabled, None, {"value": value}, request_options)

    def get_return_to_home_timeout(self, *, request_options: RequestOptions | None = None) -> ReturnToHomeTimeout:
        """Get the return to home timeout in seconds and its allowed range. Access: operator."""
        return self._run(OPS.get_return_to_home_timeout, None, {}, request_options)

    def set_return_to_home_timeout(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the return to home timeout. Changes only the fields given. Access: operator."""
        self._run(OPS.set_return_to_home_timeout, None, {"value": value}, request_options)

    def get_object_types_to_track(self, *, request_options: RequestOptions | None = None) -> ObjectTypes:
        """Get which object types are tracked. Access: operator."""
        return self._run(OPS.get_object_types_to_track, None, {}, request_options)

    def set_object_types_to_track(
        self, *, small: bool, human: bool, vehicle: bool, unknown: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set which object types are tracked.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        self._run(
            OPS.set_object_types_to_track,
            None,
            {"small": small, "human": human, "vehicle": vehicle, "unknown": unknown},
            request_options,
        )

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Get the capabilities of the API version in use. Access: operator."""
        return self._run(OPS.get_capabilities, None, {}, request_options)


class AsyncRadarAutotrackingApi(AsyncApi):
    """Radar autotracking (``radar-autotracking``, version 1)."""

    INFO = INFO

    async def get_camera_connection(self, *, request_options: RequestOptions | None = None) -> CameraConnection:
        """Get the current camera connection and its state. Access: operator."""
        return await self._run(OPS.get_camera_connection, None, {}, request_options)

    async def set_camera_connection(
        self, *, ip: str, user: str, password: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the camera connection of the radar and try to connect.

        Information on the connection state is available from ``get_camera_connection``. An empty IP address
        disconnects.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        await self._run(
            OPS.set_camera_connection, None, {"ip": ip, "user": user, "password": password}, request_options
        )

    async def get_camera_mounting_height(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the mounting height in meters and its allowed range. Access: operator."""
        return await self._run(OPS.get_camera_mounting_height, None, {}, request_options)

    async def set_camera_mounting_height(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the mounting height (see ``get_camera_mounting_height`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_camera_mounting_height, None, {"value": value}, request_options)

    async def get_camera_pan_offset(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the camera pan offset in degrees and its allowed range. Access: operator."""
        return await self._run(OPS.get_camera_pan_offset, None, {}, request_options)

    async def set_camera_pan_offset(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the camera pan offset (see ``get_camera_pan_offset`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_camera_pan_offset, None, {"value": value}, request_options)

    async def save_camera_pan_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Read the current pan position from the connected camera and save it as the camera pan offset.

        Access: operator.
        """
        await self._run(OPS.save_camera_pan_offset, None, {}, request_options)

    async def get_camera_tilt_offset(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the camera tilt offset in degrees and its allowed range. Access: operator."""
        return await self._run(OPS.get_camera_tilt_offset, None, {}, request_options)

    async def set_camera_tilt_offset(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the camera tilt offset (see ``get_camera_tilt_offset`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_camera_tilt_offset, None, {"value": value}, request_options)

    async def save_camera_tilt_offset(self, *, request_options: RequestOptions | None = None) -> None:
        """Read the current tilt position from the connected camera and save it as the camera tilt offset.

        Access: operator.
        """
        await self._run(OPS.save_camera_tilt_offset, None, {}, request_options)

    async def get_camera_zoom_degree(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the zoom degree in percent and its allowed range. Access: operator."""
        return await self._run(OPS.get_camera_zoom_degree, None, {}, request_options)

    async def set_camera_zoom_degree(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the zoom degree (in percent) of the camera.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_camera_zoom_degree, None, {"value": value}, request_options)

    async def get_tracking_enabled(self, *, request_options: RequestOptions | None = None) -> Flag:
        """Get whether tracking is enabled. Access: operator."""
        return await self._run(OPS.get_tracking_enabled, None, {}, request_options)

    async def set_tracking_enabled(self, value: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the radar tracking. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_tracking_enabled, None, {"value": value}, request_options)

    async def get_guard_tour_enabled(self, *, request_options: RequestOptions | None = None) -> Flag:
        """Get whether the guard tour is enabled. Access: operator."""
        return await self._run(OPS.get_guard_tour_enabled, None, {}, request_options)

    async def set_guard_tour_enabled(self, value: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the guard tour. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_guard_tour_enabled, None, {"value": value}, request_options)

    async def get_guard_tour_time(self, *, request_options: RequestOptions | None = None) -> RangedValue:
        """Get the guard tour time in seconds and its allowed range. Access: operator."""
        return await self._run(OPS.get_guard_tour_time, None, {}, request_options)

    async def set_guard_tour_time(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the guard tour time (see ``get_guard_tour_time`` for allowed values).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_guard_tour_time, None, {"value": value}, request_options)

    async def get_return_to_home_enabled(self, *, request_options: RequestOptions | None = None) -> Flag:
        """Get whether return to home is enabled. Access: operator."""
        return await self._run(OPS.get_return_to_home_enabled, None, {}, request_options)

    async def set_return_to_home_enabled(self, value: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the return to home function.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_return_to_home_enabled, None, {"value": value}, request_options)

    async def get_return_to_home_timeout(self, *, request_options: RequestOptions | None = None) -> ReturnToHomeTimeout:
        """Get the return to home timeout in seconds and its allowed range. Access: operator."""
        return await self._run(OPS.get_return_to_home_timeout, None, {}, request_options)

    async def set_return_to_home_timeout(self, value: float, *, request_options: RequestOptions | None = None) -> None:
        """Set the return to home timeout. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_return_to_home_timeout, None, {"value": value}, request_options)

    async def get_object_types_to_track(self, *, request_options: RequestOptions | None = None) -> ObjectTypes:
        """Get which object types are tracked. Access: operator."""
        return await self._run(OPS.get_object_types_to_track, None, {}, request_options)

    async def set_object_types_to_track(
        self, *, small: bool, human: bool, vehicle: bool, unknown: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set which object types are tracked.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        await self._run(
            OPS.set_object_types_to_track,
            None,
            {"small": small, "human": human, "vehicle": vehicle, "unknown": unknown},
            request_options,
        )

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> Capabilities:
        """Get the capabilities of the API version in use. Access: operator."""
        return await self._run(OPS.get_capabilities, None, {}, request_options)
