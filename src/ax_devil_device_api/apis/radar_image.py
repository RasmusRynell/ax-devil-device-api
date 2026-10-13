# GENERATED from specs/apis/radar/radar-image.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the radar virtual video stream (background/reference map, grid, echoes, tracks, trails) and calibrate a reference map against radar data.

Docs: https://developer.axis.com/vapix/radar/radar-image/
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import GetSupportedVersions, JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

CalibrationState = Literal["reset", "image_uploaded", "tracking", "successful", "calibrated"]


class CalibrationStateResult(Model):
    value: CalibrationState
    """The current calibration state."""


class CalibrationPointRequest(Model):
    """A point on the reference map in coordinates normalized to -1..1."""

    x_pos: float = Field(ge=-1, le=1)
    """The x coordinate of the calibration point, normalized between -1 and 1."""
    y_pos: float = Field(ge=-1, le=1)
    """The y coordinate of the calibration point, normalized between -1 and 1."""


class SetManualCalibrationPointRequest(Model):
    x_pos: float = Field(ge=-1, le=1)
    """The x coordinate of the calibration point, normalized between -1 and 1."""
    y_pos: float = Field(ge=-1, le=1)
    """The y coordinate of the calibration point, normalized between -1 and 1."""
    range: float
    """Actual distance of the calibration point from the radar in meters."""
    angle: float
    """Actual angle from the radar to the calibration point in degrees."""


class TrailLifetime(Model):
    value: int
    """The trail lifetime in seconds."""
    min_value: int | None = Field(default=None, validation_alias="minValue", serialization_alias="minValue")
    """The smallest allowed lifetime in seconds."""
    max_value: int | None = Field(default=None, validation_alias="maxValue", serialization_alias="maxValue")
    """The largest allowed lifetime in seconds."""


class ColorScheme(Model):
    value: str
    """The current color scheme."""
    allowed_values: list[str] | None = Field(
        default=None, validation_alias="allowedValues", serialization_alias="allowedValues"
    )
    """The possible color schemes."""


class GridOpaque(Model):
    value: int
    """The grid opaque level."""
    min_value: int | None = Field(default=None, validation_alias="minValue", serialization_alias="minValue")
    """The smallest allowed level."""
    max_value: int | None = Field(default=None, validation_alias="maxValue", serialization_alias="maxValue")
    """The largest allowed level."""


EchoVisualizationLevelName = Literal["disable", "associated", "all"]


class EchoVisualizationLevel(Model):
    value: EchoVisualizationLevelName
    """The current level."""
    allowed_values: list[EchoVisualizationLevelName] | None = Field(
        default=None, validation_alias="allowedValues", serialization_alias="allowedValues"
    )
    """The possible levels."""


class ImageMetricSize(Model):
    value: float
    """The height of the video stream in meters."""


class Filename(Model):
    value: str
    """The name of the reference map shown in the video stream."""


class SetTrailLifetimeRequest(Model):
    value: int
    """How long the trails are shown, in seconds."""


class SetColorSchemeRequest(Model):
    value: str
    """The color scheme; the possible values come from ``get_color_scheme``."""


class SetGridOpaqueRequest(Model):
    value: int = Field(ge=0, le=100)
    """The opaque level of the grid in the video stream."""


class SetEchoVisualizationLevelRequest(Model):
    value: EchoVisualizationLevelName
    """The visualization level."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/radar/radarimage.cgi"

INFO = ApiInfo(
    id="radar-image",
    name="Radar image",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(
        ParamDiscovery("Properties.Radar.Radar", "yes"),
        ParamDiscovery("Properties.AddOnFramework.AddOnFramework", "yes"),
    ),
    requires_firmware="7.10",
    requires_application="axis-rmd",
    docs=("https://developer.axis.com/vapix/radar/radar-image/",),
    errors={
        1000: ErrorCode("PARAM_INVALID_VALUE_ERROR. Invalid parameter value.", "invalid_argument"),
        2000: ErrorCode("RESOURCE_MEM_ERROR. Failed to allocate memory.", "internal"),
        3000: ErrorCode("UNSUPPORTED_API_VERSION. The requested API version is not supported.", "unsupported"),
        3001: ErrorCode("CGI_INVALID_PARAM_ERROR. A CGI parameter is missing or invalid.", "invalid_argument"),
        3002: ErrorCode("CGI_NOT_FOUND. The cgi name was not found.", "not_found"),
        4000: ErrorCode("JSON_INVALID_ERROR. The provided JSON input was invalid.", "invalid_argument"),
        4001: ErrorCode(
            "JSON_KEY_NOT_FOUND_ERROR. A mandatory input parameter was not found in the input.", "invalid_argument"
        ),
        4002: ErrorCode("JSON_INVALID_TYPE. The type of a provided JSON parameter was incorrect.", "invalid_argument"),
        4003: ErrorCode("JSON_METHOD_NOT_FOUND_ERROR. The JSON method was not found.", "unsupported"),
        4004: ErrorCode("JSON_FAIL_TO_LOAD_ERROR. Failed to load JSON from HTTP POST data.", "invalid_argument"),
        6000: ErrorCode(
            "CALIB_INVALID_STATE_ERROR. Can not perform command in current calibration state.", "invalid_argument"
        ),
        8000: ErrorCode("INTERNAL_ERROR. Internal error.", "internal"),
        8001: ErrorCode("UNEXPECTED_ERROR. Unexpected error.", "internal"),
        8002: ErrorCode("GENERIC_ERROR. Generic error.", "internal"),
    },
)


class OPS:
    start_calibration_tracking = Operation(
        INFO,
        "start_calibration_tracking",
        JsonRpcBinding("startCalibrationTracking", PATH, negotiation=GetSupportedVersions(key="value")),
        access="operator",
        effect="action",
    )
    set_calibration_point = Operation(
        INFO,
        "set_calibration_point",
        JsonRpcBinding("setCalibrationPoint", PATH, negotiation=GetSupportedVersions(key="value")),
        params=CalibrationPointRequest,
        access="operator",
        effect="action",
        errors={
            6001: ErrorCode(
                "CALIB_OUT_OF_RANGE_ERROR. The tracked object walked out of range so tracking is lost and calibration needs to be restarted."
            ),
            6003: ErrorCode(
                "CALIB_NOT_DETECTED_ERROR. The first calibration point was placed before tracking detected any object close to the radar unit."
            ),
            6004: ErrorCode("CALIB_TOO_CLOSE_TO_RADAR_ERROR. The tracked object is too close to the radar."),
            6005: ErrorCode("CALIB_TOO_CLOSE_TO_POINT_ERROR. The tracked object is too close to the last point."),
            6006: ErrorCode("CALIB_INVALID_SCALE_ERROR. Calibration resulted in invalid scale.", "invalid_argument"),
            6007: ErrorCode(
                "CALIB_INVALID_POSITION_ERROR. The calculated radar direction (x, y) is too far outside of the image.",
                "invalid_argument",
            ),
            6008: ErrorCode(
                "CALIB_GENERAL_CALC_ERROR. The calibration calculation result is invalid so calibration should be done again.",
                "invalid_argument",
            ),
            6009: ErrorCode("CALIB_POINT_INVALID. The calibration point is out of range -1 to 1.", "invalid_argument"),
            6010: ErrorCode(
                "CALIB_OBJ_MOVING. The tracked object was moving when setting the calibration point. May indicate that the wrong object is being tracked."
            ),
        },
    )
    stop_calibration_tracking = Operation(
        INFO,
        "stop_calibration_tracking",
        JsonRpcBinding("stopCalibrationTracking", PATH, negotiation=GetSupportedVersions(key="value")),
        access="operator",
        effect="action",
        errors={
            6002: ErrorCode(
                "CALIB_NOT_ENOUGH_POINTS_ERROR. At least two calibration points are needed to stop the calibration successfully."
            )
        },
    )
    abort_calibration = Operation(
        INFO,
        "abort_calibration",
        JsonRpcBinding("abortCalibration", PATH, negotiation=GetSupportedVersions(key="value")),
        access="operator",
        effect="action",
    )
    reset_calibration = Operation(
        INFO,
        "reset_calibration",
        JsonRpcBinding("resetCalibration", PATH, negotiation=GetSupportedVersions(key="value")),
        access="operator",
        effect="write",
        write="delete",
    )
    get_calibration_state = Operation(
        INFO,
        "get_calibration_state",
        JsonRpcBinding("getCalibrationState", PATH, negotiation=GetSupportedVersions(key="value")),
        result=CalibrationStateResult,
        access="operator",
        effect="read",
    )
    set_manual_radar_position = Operation(
        INFO,
        "set_manual_radar_position",
        JsonRpcBinding("setManualRadarPosition", PATH, negotiation=GetSupportedVersions(key="value")),
        params=CalibrationPointRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_manual_calibration_point = Operation(
        INFO,
        "set_manual_calibration_point",
        JsonRpcBinding("setManualCalibrationPoint", PATH, negotiation=GetSupportedVersions(key="value")),
        params=SetManualCalibrationPointRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_trail_lifetime = Operation(
        INFO,
        "get_trail_lifetime",
        JsonRpcBinding("getTrailLifetime", PATH, negotiation=GetSupportedVersions(key="value")),
        result=TrailLifetime,
        access="operator",
        effect="read",
    )
    set_trail_lifetime = Operation(
        INFO,
        "set_trail_lifetime",
        JsonRpcBinding("setTrailLifetime", PATH, negotiation=GetSupportedVersions(key="value")),
        params=SetTrailLifetimeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_color_scheme = Operation(
        INFO,
        "get_color_scheme",
        JsonRpcBinding("getColorScheme", PATH, negotiation=GetSupportedVersions(key="value")),
        result=ColorScheme,
        access="operator",
        effect="read",
    )
    set_color_scheme = Operation(
        INFO,
        "set_color_scheme",
        JsonRpcBinding("setColorScheme", PATH, negotiation=GetSupportedVersions(key="value")),
        params=SetColorSchemeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_grid_opaque = Operation(
        INFO,
        "get_grid_opaque",
        JsonRpcBinding("getGridOpaque", PATH, negotiation=GetSupportedVersions(key="value")),
        result=GridOpaque,
        access="operator",
        effect="read",
    )
    set_grid_opaque = Operation(
        INFO,
        "set_grid_opaque",
        JsonRpcBinding("setGridOpaque", PATH, negotiation=GetSupportedVersions(key="value")),
        params=SetGridOpaqueRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_echo_visualization_level = Operation(
        INFO,
        "get_echo_visualization_level",
        JsonRpcBinding("getEchoVisualizationLevel", PATH, negotiation=GetSupportedVersions(key="value")),
        result=EchoVisualizationLevel,
        access="operator",
        effect="read",
    )
    set_echo_visualization_level = Operation(
        INFO,
        "set_echo_visualization_level",
        JsonRpcBinding("setEchoVisualizationLevel", PATH, negotiation=GetSupportedVersions(key="value")),
        params=SetEchoVisualizationLevelRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_image_metric_size = Operation(
        INFO,
        "get_image_metric_size",
        JsonRpcBinding("getImageMetricSize", PATH, negotiation=GetSupportedVersions(key="value")),
        result=ImageMetricSize,
        access="operator",
        effect="read",
    )
    get_filename = Operation(
        INFO,
        "get_filename",
        JsonRpcBinding("getFilename", PATH, negotiation=GetSupportedVersions(key="value")),
        result=Filename,
        access="operator",
        effect="read",
        errors={5002: ErrorCode("FILE_NOT_UPLOADED_ERROR. No image file uploaded to the radar.", "not_found")},
    )


# ---------------------------------------------------------------------------
# API classes


class RadarImageApi(SyncApi):
    """Radar image (``radar-image``, version 1)."""

    INFO = INFO

    def start_calibration_tracking(self, *, request_options: RequestOptions | None = None) -> None:
        """Start or restart the reference map calibration by tracking the installer moving away from the radar.

        The installer walks away from the radar within its field of view while calibration points are set.

        Access: operator.
        """
        self._run(OPS.start_calibration_tracking, None, {}, request_options)

    def set_calibration_point(
        self, x_pos: float, y_pos: float, *, request_options: RequestOptions | None = None
    ) -> None:
        """Use the given reference map coordinates and the tracked object's current position as a calibration point.

        Access: operator.
        """
        self._run(OPS.set_calibration_point, None, {"x_pos": x_pos, "y_pos": y_pos}, request_options)

    def stop_calibration_tracking(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop tracking the calibration object and store the result if the calibration was successful.

        Access: operator.
        """
        self._run(OPS.stop_calibration_tracking, None, {}, request_options)

    def abort_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop tracking the calibration object and reset all parameters related to the current reference map.

        Access: operator.
        """
        self._run(OPS.abort_calibration, None, {}, request_options)

    def reset_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the calibration by removing the reference map and its parameters. Access: operator."""
        self._run(OPS.reset_calibration, None, {}, request_options)

    def get_calibration_state(self, *, request_options: RequestOptions | None = None) -> CalibrationStateResult:
        """Get the current state of the calibration. Access: operator."""
        return self._run(OPS.get_calibration_state, None, {}, request_options)

    def set_manual_radar_position(
        self, x_pos: float, y_pos: float, *, request_options: RequestOptions | None = None
    ) -> None:
        """Manually set a point on the reference map as the radar position, without tracking an object.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_manual_radar_position, None, {"x_pos": x_pos, "y_pos": y_pos}, request_options)

    def set_manual_calibration_point(
        self, *, x_pos: float, y_pos: float, range: float, angle: float, request_options: RequestOptions | None = None
    ) -> None:
        """Manually set a point on the reference map, with its real range and angle, to calibrate the radar.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_manual_calibration_point,
            None,
            {"x_pos": x_pos, "y_pos": y_pos, "range": range, "angle": angle},
            request_options,
        )

    def get_trail_lifetime(self, *, request_options: RequestOptions | None = None) -> TrailLifetime:
        """Get the trail lifetime in seconds with its minimum and maximum. Access: operator."""
        return self._run(OPS.get_trail_lifetime, None, {}, request_options)

    def set_trail_lifetime(self, value: int, *, request_options: RequestOptions | None = None) -> None:
        """Set how long, in seconds, the trail of a tracked object is visible in the video stream.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_trail_lifetime, None, {"value": value}, request_options)

    def get_color_scheme(self, *, request_options: RequestOptions | None = None) -> ColorScheme:
        """Get the current color scheme and the possible color schemes. Access: operator."""
        return self._run(OPS.get_color_scheme, None, {}, request_options)

    def set_color_scheme(self, value: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the color scheme of the video stream. It affects the grid, the echoes and the radar trail.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_color_scheme, None, {"value": value}, request_options)

    def get_grid_opaque(self, *, request_options: RequestOptions | None = None) -> GridOpaque:
        """Get the opaque level of the grid with its minimum and maximum. Access: operator."""
        return self._run(OPS.get_grid_opaque, None, {}, request_options)

    def set_grid_opaque(self, value: int, *, request_options: RequestOptions | None = None) -> None:
        """Set the opaque level of the grid: 0 is fully transparent and 100 is fully opaque.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_grid_opaque, None, {"value": value}, request_options)

    def get_echo_visualization_level(self, *, request_options: RequestOptions | None = None) -> EchoVisualizationLevel:
        """Get the current level of echo visualization and the possible levels. Access: operator."""
        return self._run(OPS.get_echo_visualization_level, None, {}, request_options)

    def set_echo_visualization_level(
        self, value: EchoVisualizationLevelName, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the level of visualization of the radar echoes, the raw responses of the radar's electromagnetic waves.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_echo_visualization_level, None, {"value": value}, request_options)

    def get_image_metric_size(self, *, request_options: RequestOptions | None = None) -> ImageMetricSize:
        """Get the height of the video stream in meters, to transform between pixels and meters.

        Only a 16:9 aspect ratio is supported.

        Access: operator.
        """
        return self._run(OPS.get_image_metric_size, None, {}, request_options)

    def get_filename(self, *, request_options: RequestOptions | None = None) -> Filename:
        """Get the name of the reference map currently shown in the video stream. Access: operator."""
        return self._run(OPS.get_filename, None, {}, request_options)


class AsyncRadarImageApi(AsyncApi):
    """Radar image (``radar-image``, version 1)."""

    INFO = INFO

    async def start_calibration_tracking(self, *, request_options: RequestOptions | None = None) -> None:
        """Start or restart the reference map calibration by tracking the installer moving away from the radar.

        The installer walks away from the radar within its field of view while calibration points are set.

        Access: operator.
        """
        await self._run(OPS.start_calibration_tracking, None, {}, request_options)

    async def set_calibration_point(
        self, x_pos: float, y_pos: float, *, request_options: RequestOptions | None = None
    ) -> None:
        """Use the given reference map coordinates and the tracked object's current position as a calibration point.

        Access: operator.
        """
        await self._run(OPS.set_calibration_point, None, {"x_pos": x_pos, "y_pos": y_pos}, request_options)

    async def stop_calibration_tracking(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop tracking the calibration object and store the result if the calibration was successful.

        Access: operator.
        """
        await self._run(OPS.stop_calibration_tracking, None, {}, request_options)

    async def abort_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop tracking the calibration object and reset all parameters related to the current reference map.

        Access: operator.
        """
        await self._run(OPS.abort_calibration, None, {}, request_options)

    async def reset_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the calibration by removing the reference map and its parameters. Access: operator."""
        await self._run(OPS.reset_calibration, None, {}, request_options)

    async def get_calibration_state(self, *, request_options: RequestOptions | None = None) -> CalibrationStateResult:
        """Get the current state of the calibration. Access: operator."""
        return await self._run(OPS.get_calibration_state, None, {}, request_options)

    async def set_manual_radar_position(
        self, x_pos: float, y_pos: float, *, request_options: RequestOptions | None = None
    ) -> None:
        """Manually set a point on the reference map as the radar position, without tracking an object.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_manual_radar_position, None, {"x_pos": x_pos, "y_pos": y_pos}, request_options)

    async def set_manual_calibration_point(
        self, *, x_pos: float, y_pos: float, range: float, angle: float, request_options: RequestOptions | None = None
    ) -> None:
        """Manually set a point on the reference map, with its real range and angle, to calibrate the radar.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_manual_calibration_point,
            None,
            {"x_pos": x_pos, "y_pos": y_pos, "range": range, "angle": angle},
            request_options,
        )

    async def get_trail_lifetime(self, *, request_options: RequestOptions | None = None) -> TrailLifetime:
        """Get the trail lifetime in seconds with its minimum and maximum. Access: operator."""
        return await self._run(OPS.get_trail_lifetime, None, {}, request_options)

    async def set_trail_lifetime(self, value: int, *, request_options: RequestOptions | None = None) -> None:
        """Set how long, in seconds, the trail of a tracked object is visible in the video stream.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_trail_lifetime, None, {"value": value}, request_options)

    async def get_color_scheme(self, *, request_options: RequestOptions | None = None) -> ColorScheme:
        """Get the current color scheme and the possible color schemes. Access: operator."""
        return await self._run(OPS.get_color_scheme, None, {}, request_options)

    async def set_color_scheme(self, value: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the color scheme of the video stream. It affects the grid, the echoes and the radar trail.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_color_scheme, None, {"value": value}, request_options)

    async def get_grid_opaque(self, *, request_options: RequestOptions | None = None) -> GridOpaque:
        """Get the opaque level of the grid with its minimum and maximum. Access: operator."""
        return await self._run(OPS.get_grid_opaque, None, {}, request_options)

    async def set_grid_opaque(self, value: int, *, request_options: RequestOptions | None = None) -> None:
        """Set the opaque level of the grid: 0 is fully transparent and 100 is fully opaque.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_grid_opaque, None, {"value": value}, request_options)

    async def get_echo_visualization_level(
        self, *, request_options: RequestOptions | None = None
    ) -> EchoVisualizationLevel:
        """Get the current level of echo visualization and the possible levels. Access: operator."""
        return await self._run(OPS.get_echo_visualization_level, None, {}, request_options)

    async def set_echo_visualization_level(
        self, value: EchoVisualizationLevelName, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the level of visualization of the radar echoes, the raw responses of the radar's electromagnetic waves.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_echo_visualization_level, None, {"value": value}, request_options)

    async def get_image_metric_size(self, *, request_options: RequestOptions | None = None) -> ImageMetricSize:
        """Get the height of the video stream in meters, to transform between pixels and meters.

        Only a 16:9 aspect ratio is supported.

        Access: operator.
        """
        return await self._run(OPS.get_image_metric_size, None, {}, request_options)

    async def get_filename(self, *, request_options: RequestOptions | None = None) -> Filename:
        """Get the name of the reference map currently shown in the video stream. Access: operator."""
        return await self._run(OPS.get_filename, None, {}, request_options)
