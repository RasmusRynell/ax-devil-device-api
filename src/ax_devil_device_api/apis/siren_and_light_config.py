# GENERATED from specs/apis/device-configuration/siren-and-light-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control sirens and lights: start and stop patterns, manage profiles, beam shapes, maintenance mode and health checks.

Docs: https://developer.axis.com/vapix/device-configuration/siren-and-light-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, ErrorCode, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

CalibrationStatusString = Literal["CALIBRATED", "UNCALIBRATED"]
ColorsArray = list[str]
DescriptionString = Annotated[
    str,
    Field(
        min_length=1,
        max_length=250,
        pattern=r"^[\p{L}\p{N}.:*,;/_\-+{}!#$%()=\'\x22?@\[\]^](?:[\p{L}\p{N}.:*,;/_\-+{}!#$%()=\'\x22?@\[\]^ ]*[\p{L}\p{N}.:*,;/_\-+{}!#$%()=\'\x22?@\[\]^])?$",
    ),
]
DurationUnit = Literal["SECONDS", "REPETITIONS", "CONTINUOUS"]


class Duration(Model):
    """Duration input"""

    unit: DurationUnit | None = None
    """The unit of duration: SECONDS, REPETITIONS or CONTINUOUS"""
    value: int | None = None
    """Duration value in seconds or number of pattern repetitions"""


FunctionClass = Literal["SIREN", "LIGHT"]
NameString = Annotated[
    str,
    Field(
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9.:*,;/_\-+{}!#$%()=\'\x22?@\[\]^](?:[a-zA-Z0-9.:*,;/_\-+{}!#$%()=\'\x22?@\[\]^ ]*[a-zA-Z0-9.:*,;/_\-+{}!#$%()=\'\x22?@\[\]^])?$",
    ),
]
TaskId = Annotated[str, Field(min_length=1, max_length=10)]


class FunctionTaskIdMap(Model):
    """Map of function and task ID"""

    function: NameString
    """The name of the function"""
    task_id: TaskId = Field(validation_alias="taskId", serialization_alias="taskId")
    """The ID of the task"""


FunctionTaskList = list[FunctionTaskIdMap]
Integer0To100 = Annotated[int, Field(ge=0, le=100)]
Integer0To5 = Annotated[int, Field(ge=0, le=5)]
Integer1To10 = Annotated[int, Field(ge=1, le=10)]
Integer1To13 = Annotated[int, Field(ge=1, le=13)]
Integer1To5 = Annotated[int, Field(ge=1, le=5)]
IntegerArray = list[int]
IntegerMinimum0 = Annotated[int, Field(ge=0)]
IntegerMinimum1 = Annotated[int, Field(ge=1)]
PowerModeString = Literal["FULL", "LIMITED", "LIMITED_LEVEL_2"]


class RunHealthCheckResponse(Model):
    """The response from health check"""

    is_healthy: bool = Field(validation_alias="isHealthy", serialization_alias="isHealthy")
    """Health check result, passed or failed"""


class StartPatternResponse(Model):
    """The response from start pattern"""

    task_id: TaskId = Field(validation_alias="taskId", serialization_alias="taskId")
    """Id of started task"""


class StartProfileResponse(Model):
    """The response from start profile"""

    tasks: FunctionTaskList
    """List of started tasks"""


Timestamp = str


class BeamShapeEntry(Model):
    """The supported beam shapes"""

    beam_shape: NameString = Field(validation_alias="beamShape", serialization_alias="beamShape")
    """The name of the beam shape"""


class BeamShape(Model):
    """The default and supported beam shapes"""

    default: NameString | None = None
    """The default beam shape"""
    beam_shapes: list[BeamShapeEntry] | None = Field(
        default=None, validation_alias="beamShapes", serialization_alias="beamShapes"
    )


class Pattern(Model):
    """The supported patterns"""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {
            "colors",
            "default_colors",
            "default_intensity_limited",
            "default_speed",
            "intensity_limited",
            "max_nbr_colors",
            "min_nbr_colors",
            "speed",
        }
    )
    audio_visualizer: bool | None = Field(
        default=None, validation_alias="audioVisualizer", serialization_alias="audioVisualizer"
    )
    """Whether the pattern is synchronized with audio"""
    colors: ColorsArray | None = None
    """The possible colors"""
    default_colors: ColorsArray | None = Field(
        default=None, validation_alias="defaultColors", serialization_alias="defaultColors"
    )
    """The default colors"""
    default_intensity: Integer0To5 = Field(validation_alias="defaultIntensity", serialization_alias="defaultIntensity")
    """The default intensity on full power"""
    default_intensity_limited: Integer0To5 | None = Field(
        default=None, validation_alias="defaultIntensityLimited", serialization_alias="defaultIntensityLimited"
    )
    """The default intensity on limited power"""
    default_priority: Integer1To10 = Field(validation_alias="defaultPriority", serialization_alias="defaultPriority")
    """The default priority"""
    default_speed: Integer1To5 | None = Field(
        default=None, validation_alias="defaultSpeed", serialization_alias="defaultSpeed"
    )
    """The default speed"""
    default_threshold: Integer0To100 | None = Field(
        default=None, validation_alias="defaultThreshold", serialization_alias="defaultThreshold"
    )
    """The default threshold of audio visualizer"""
    intensity: IntegerArray
    """The possible intensities on full power"""
    intensity_limited: IntegerArray | None = Field(
        default=None, validation_alias="intensityLimited", serialization_alias="intensityLimited"
    )
    """The possible intensities on limited power"""
    max_nbr_colors: int | None = Field(
        default=None, validation_alias="maxNbrColors", serialization_alias="maxNbrColors"
    )
    """The maximum number of colors allowed"""
    min_nbr_colors: int | None = Field(
        default=None, validation_alias="minNbrColors", serialization_alias="minNbrColors"
    )
    """The minimum number of colors required"""
    pattern: NameString
    """The name of the pattern"""
    priority: IntegerArray
    """The possible priorities"""
    speed: IntegerArray | None = None
    """The possible speeds"""
    colors_supported: bool | None = None
    default_colors_supported: bool | None = Field(
        default=None, validation_alias="defaultColors_supported", serialization_alias="defaultColors_supported"
    )
    default_intensity_limited_supported: bool | None = Field(
        default=None,
        validation_alias="defaultIntensityLimited_supported",
        serialization_alias="defaultIntensityLimited_supported",
    )
    default_speed_supported: bool | None = Field(
        default=None, validation_alias="defaultSpeed_supported", serialization_alias="defaultSpeed_supported"
    )
    default_threshold_supported: bool | None = Field(
        default=None, validation_alias="defaultThreshold_supported", serialization_alias="defaultThreshold_supported"
    )
    intensity_limited_supported: bool | None = Field(
        default=None, validation_alias="intensityLimited_supported", serialization_alias="intensityLimited_supported"
    )
    max_nbr_colors_supported: bool | None = Field(
        default=None, validation_alias="maxNbrColors_supported", serialization_alias="maxNbrColors_supported"
    )
    min_nbr_colors_supported: bool | None = Field(
        default=None, validation_alias="minNbrColors_supported", serialization_alias="minNbrColors_supported"
    )
    speed_supported: bool | None = None


class Task(Model):
    """Active tasks"""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"colors", "duration_left", "profile", "speed", "threshold"})
    __response_required__: ClassVar[frozenset[str]] = frozenset({"pattern", "priority", "task_id"})
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {
            "beam_shape_supported",
            "colors",
            "colors_supported",
            "duration_left",
            "duration_left_supported",
            "pattern",
            "priority",
            "profile",
            "profile_supported",
            "speed",
            "speed_supported",
            "task_id",
            "threshold_supported",
        }
    )
    beam_shape: NameString | None = Field(default=None, validation_alias="beamShape", serialization_alias="beamShape")
    """The beam shape of the pattern"""
    colors: ColorsArray | None = None
    """A list of colors used in the pattern"""
    duration_left: IntegerMinimum0 | None = Field(
        default=None, validation_alias="durationLeft", serialization_alias="durationLeft"
    )
    """The number of seconds left"""
    intensity: Integer0To5
    """The intensity level"""
    pattern: NameString = Field(default_factory=not_sent)
    """The name of the pattern"""
    priority: Integer1To13 = Field(default_factory=not_sent)
    """The priority level"""
    profile: NameString | None = None
    """The name of the profile"""
    speed: Integer1To5 | None = None
    """The speed of the pattern"""
    task_id: TaskId = Field(default_factory=not_sent, validation_alias="taskId", serialization_alias="taskId")
    """The ID of the task"""
    threshold: Integer0To100 | None = None
    """The threshold value to trigger the audio visualizer"""
    beam_shape_supported: bool | None = Field(
        default=None, validation_alias="beamShape_supported", serialization_alias="beamShape_supported"
    )
    colors_supported: bool | None = None
    duration_left_supported: bool | None = Field(
        default=None, validation_alias="durationLeft_supported", serialization_alias="durationLeft_supported"
    )
    profile_supported: bool | None = None
    speed_supported: bool | None = None
    threshold_supported: bool | None = None


class Function(Model):
    """The collection of siren and light functions"""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"calibration_status", "scheduled_start_tolerance_ms"})
    calibration_status: CalibrationStatusString | None = Field(
        default=None, validation_alias="calibrationStatus", serialization_alias="calibrationStatus"
    )
    """Whether the function has been calibrated"""
    function: NameString
    """The name of the function"""
    function_class: FunctionClass = Field(validation_alias="functionClass", serialization_alias="functionClass")
    """The class of the function"""
    health_check_supported: bool | None = Field(
        default=None, validation_alias="healthCheckSupported", serialization_alias="healthCheckSupported"
    )
    """Whether the function supports health check"""
    power_mode: PowerModeString = Field(validation_alias="powerMode", serialization_alias="powerMode")
    """The power mode used by the function"""
    scheduled_start_supported: bool | None = Field(
        default=None, validation_alias="scheduledStartSupported", serialization_alias="scheduledStartSupported"
    )
    """Whether the function supports scheduled start"""
    scheduled_start_tolerance_ms: IntegerMinimum1 | None = Field(
        default=None, validation_alias="scheduledStartToleranceMs", serialization_alias="scheduledStartToleranceMs"
    )
    """The maximum allowed deviation for the scheduled start timestamp, in milliseconds"""
    calibration_status_supported: bool | None = Field(
        default=None, validation_alias="calibrationStatus_supported", serialization_alias="calibrationStatus_supported"
    )
    scheduled_start_tolerance_ms_supported: bool | None = Field(
        default=None,
        validation_alias="scheduledStartToleranceMs_supported",
        serialization_alias="scheduledStartToleranceMs_supported",
    )
    beam_shape_supported: bool | None = Field(
        default=None, validation_alias="beamShape_supported", serialization_alias="beamShape_supported"
    )
    beam_shape: BeamShape | None = Field(default=None, validation_alias="beamShape", serialization_alias="beamShape")
    patterns: list[Pattern] | None = None
    tasks: list[Task] | None = None


class MaintenanceMode(Model):
    """Maintenance mode"""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"running", "supported"})
    running: bool | None = None
    """Whether maintenance mode is currently running"""
    supported: bool | None = None
    """Whether maintenance mode is supported"""


class ProfileFunction(Model):
    """Functions in profile"""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"beam_shape_override", "colors", "duration", "speed", "threshold"}
    )
    __response_required__: ClassVar[frozenset[str]] = frozenset({"function_class"})
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {
            "beam_shape_override_supported",
            "colors_supported",
            "duration_supported",
            "function_class",
            "pattern_available",
            "speed_supported",
            "threshold_supported",
        }
    )
    beam_shape_override: NameString | None = Field(
        default=None, validation_alias="beamShapeOverride", serialization_alias="beamShapeOverride"
    )
    """Override beam shape for this function"""
    colors: ColorsArray | None = None
    """A list of colors used in the pattern"""
    duration: Duration | None = None
    """The duration the function stays active"""
    function: NameString
    """The name of the function"""
    function_class: FunctionClass = Field(
        default_factory=not_sent, validation_alias="functionClass", serialization_alias="functionClass"
    )
    """The class of function"""
    intensity: Integer0To5 | None = None
    """The intensity level"""
    pattern: NameString
    """The name of the pattern"""
    pattern_available: bool | None = Field(
        default=None, validation_alias="patternAvailable", serialization_alias="patternAvailable"
    )
    """Whether the pattern is currently available"""
    priority: Integer1To13 | None = None
    """The priority level"""
    speed: Integer1To5 | None = None
    """The speed of the pattern"""
    threshold: Integer0To100 | None = None
    """The threshold value to trigger the audio visualizer"""
    beam_shape_override_supported: bool | None = Field(
        default=None, validation_alias="beamShapeOverride_supported", serialization_alias="beamShapeOverride_supported"
    )
    colors_supported: bool | None = None
    duration_supported: bool | None = None
    speed_supported: bool | None = None
    threshold_supported: bool | None = None


class Profile(Model):
    """The collection of siren and light profiles"""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"description"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"description_supported"})
    description: DescriptionString | None = None
    """Description of the profile"""
    profile: NameString
    """The name of the profile"""
    resume_on_startup: bool = Field(validation_alias="resumeOnStartup", serialization_alias="resumeOnStartup")
    """Whether the profile should resume after restart"""
    description_supported: bool | None = None
    functions: list[ProfileFunction] | None = None


class SirenAndLight(Model):
    """The whole API tree."""

    functions: list[Function] | None = None
    maintenance_mode: MaintenanceMode | None = Field(
        default=None, validation_alias="maintenanceMode", serialization_alias="maintenanceMode"
    )
    profiles: list[Profile] | None = None


class AddProfileRequest(Model):
    """Arguments of ``add_profile``."""

    profile: NameString
    """The name of the profile"""
    description: DescriptionString | None = None
    """Description of the profile"""
    resume_on_startup: bool | None = Field(
        default=None, validation_alias="resumeOnStartup", serialization_alias="resumeOnStartup"
    )
    """Whether the profile should resume after restart"""


class AddProfileFunctionRequest(Model):
    """Arguments of ``add_profile_function``."""

    profile: NameString
    function: NameString
    """The name of the function"""
    pattern: NameString
    """The name of the pattern"""
    intensity: Integer0To5 | None = None
    """The intensity level"""
    speed: Integer1To5 | None = None
    """The speed of the pattern"""
    colors: ColorsArray | None = None
    """A list of colors used in the pattern"""
    duration: Duration | None = None
    """The duration the function stays active"""
    priority: Integer1To13 | None = None
    """The priority level"""
    threshold: Integer0To100 | None = None
    """The threshold value to trigger the audio visualizer"""
    beam_shape_override: NameString | None = Field(
        default=None, validation_alias="beamShapeOverride", serialization_alias="beamShapeOverride"
    )
    """Override beam shape for this function"""


class FunctionRequest(Model):
    function: NameString


class SetDefaultBeamShapeRequest(Model):
    function: NameString
    default: NameString
    """The default beam shape"""


class FunctionBeamShapeRequest(Model):
    function: NameString
    beam_shape: NameString = Field(validation_alias="beamShape", serialization_alias="beamShape")


class FunctionPatternRequest(Model):
    function: NameString
    pattern: NameString


class StartPatternRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {"beam_shape_override", "colors", "duration", "intensity", "priority", "speed", "start_at", "threshold"}
    )
    function: NameString
    pattern: NameString
    beam_shape_override: NameString | None = Field(
        default=None, validation_alias="beamShapeOverride", serialization_alias="beamShapeOverride"
    )
    """Override beam shape for the pattern"""
    colors: ColorsArray | None = None
    """A list of colors used in the pattern"""
    duration: Duration | None = None
    """The duration the function stays active"""
    intensity: Integer0To5 | None = None
    """The intensity level"""
    priority: Integer1To10 | None = None
    """The priority level"""
    speed: Integer1To5 | None = None
    """The speed of the pattern"""
    start_at: Timestamp | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt")
    """Optional timestamp for scheduled start; only valid if the function supports scheduled start and must be within scheduledStartToleranceMs"""
    threshold: Integer0To100 | None = None
    """The threshold value to trigger the audio visualizer"""


class FunctionTaskRequest(Model):
    function: NameString
    task_id: TaskId = Field(validation_alias="taskId", serialization_alias="taskId")


class SetTaskBeamShapeRequest(Model):
    function: NameString
    task_id: TaskId = Field(validation_alias="taskId", serialization_alias="taskId")
    beam_shape: NameString = Field(validation_alias="beamShape", serialization_alias="beamShape")
    """The beam shape of the pattern"""


class SetTaskIntensityRequest(Model):
    function: NameString
    task_id: TaskId = Field(validation_alias="taskId", serialization_alias="taskId")
    intensity: Integer0To5
    """The intensity level"""


class SetTaskThresholdRequest(Model):
    function: NameString
    task_id: TaskId = Field(validation_alias="taskId", serialization_alias="taskId")
    threshold: Integer0To100
    """The threshold value to trigger the audio visualizer"""


class StartMaintenanceModeRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"time"})
    time: IntegerMinimum1 | None = None
    """The number of seconds that maintenance mode is active"""


class ProfileRequest(Model):
    profile: NameString


class StartProfileRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"start_at"})
    profile: NameString
    start_at: Timestamp | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt")
    """Optional timestamp for scheduled start; only valid if the function supports scheduled start and must be within scheduledStartToleranceMs"""


class ProfileFunctionRequest(Model):
    profile: NameString
    function: NameString


class SetProfileFunctionBeamShapeOverrideRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"beam_shape_override"})
    profile: NameString
    function: NameString
    beam_shape_override: NameString | None = Field(
        validation_alias="beamShapeOverride", serialization_alias="beamShapeOverride"
    )
    """Override beam shape for this function"""


class SetProfileFunctionIntensityRequest(Model):
    profile: NameString
    function: NameString
    intensity: Integer0To5
    """The intensity level"""


class SetProfileFunctionThresholdRequest(Model):
    profile: NameString
    function: NameString
    threshold: Integer0To100
    """The threshold value to trigger the audio visualizer"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/siren-and-light/v2"

INFO = ApiInfo(
    id="siren-and-light-config",
    name="Siren and light configuration",
    family=Family.DCA,
    discovery=(DcaDiscovery("siren-and-light", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/siren-and-light-api/",),
    errors={
        100: ErrorCode("The specified pattern is invalid or does not exist.", "not_found"),
        101: ErrorCode(
            "The specified intensity is invalid, e.g. it may exceed the available power.", "invalid_argument"
        ),
        102: ErrorCode("The specified priority is not supported for the chosen function and pattern.", "unsupported"),
        103: ErrorCode("The specified speed is is not supported for the chosen function and pattern.", "unsupported"),
        104: ErrorCode(
            "The specified function is invalid, e.g. it does not exist or the combination of function and pattern is invalid.",
            "not_found",
        ),
        105: ErrorCode(
            "The specified number of colors is invalid, the pattern does not support the number of colors.",
            "invalid_argument",
        ),
        106: ErrorCode(
            "The specified color is invalid, e.g. the combination of function and pattern does not support this color.",
            "invalid_argument",
        ),
        107: ErrorCode(
            "The specified duration unit is invalid, see the DurationUnit type for valid values.", "invalid_argument"
        ),
        108: ErrorCode(
            "The specified duration value is invalid, e.g. the number of repetitions exceed the maximum value.",
            "invalid_argument",
        ),
        109: ErrorCode("The specified profile does not exist.", "not_found"),
        110: ErrorCode(
            "The specified timestamp is invalid, it must be in ISO 8601 format and within the time diff tolerance for the function.",
            "invalid_argument",
        ),
        111: ErrorCode("The specified beam shape is is not supported for the chosen function.", "unsupported"),
    },
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=SirenAndLight, access="operator", effect="read"
    )
    stop = Operation(
        INFO, "stop", DcaBinding("POST", f"{ROOT}/stop", body="object"), access="operator", effect="action"
    )
    list_functions = Operation(
        INFO,
        "list_functions",
        DcaBinding("GET", f"{ROOT}/functions"),
        result=list[Function],
        access="operator",
        effect="read",
    )
    get_function = Operation(
        INFO,
        "get_function",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}"),
        params=FunctionRequest,
        result=Function,
        access="operator",
        effect="read",
    )
    get_health_check_supported = Operation(
        INFO,
        "get_health_check_supported",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/healthCheckSupported"),
        params=FunctionRequest,
        result=bool,
        access="operator",
        effect="read",
    )
    run_health_check = Operation(
        INFO,
        "run_health_check",
        DcaBinding("POST", f"{ROOT}/functions/{{function}}/runHealthCheck", body="object"),
        params=FunctionRequest,
        result=RunHealthCheckResponse,
        access="operator",
        effect="action",
    )
    stop_function = Operation(
        INFO,
        "stop_function",
        DcaBinding("POST", f"{ROOT}/functions/{{function}}/stop", body="object"),
        params=FunctionRequest,
        access="operator",
        effect="action",
    )
    get_function_beam_shape = Operation(
        INFO,
        "get_function_beam_shape",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/beamShape"),
        params=FunctionRequest,
        result=BeamShape,
        access="operator",
        effect="read",
    )
    set_default_beam_shape = Operation(
        INFO,
        "set_default_beam_shape",
        DcaBinding("PATCH", f"{ROOT}/functions/{{function}}/beamShape/default", body="value", body_field="default"),
        params=SetDefaultBeamShapeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_default_beam_shape = Operation(
        INFO,
        "get_default_beam_shape",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/beamShape/default"),
        params=FunctionRequest,
        result=NameString,
        access="operator",
        effect="read",
    )
    list_beam_shapes = Operation(
        INFO,
        "list_beam_shapes",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/beamShape/beamShapes"),
        params=FunctionRequest,
        result=list[BeamShapeEntry],
        access="operator",
        effect="read",
    )
    get_supported_beam_shape = Operation(
        INFO,
        "get_supported_beam_shape",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/beamShape/beamShapes/{{beamShape}}"),
        params=FunctionBeamShapeRequest,
        result=BeamShapeEntry,
        access="operator",
        effect="read",
    )
    list_patterns = Operation(
        INFO,
        "list_patterns",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/patterns"),
        params=FunctionRequest,
        result=list[Pattern],
        access="operator",
        effect="read",
    )
    get_pattern = Operation(
        INFO,
        "get_pattern",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/patterns/{{pattern}}"),
        params=FunctionPatternRequest,
        result=Pattern,
        access="operator",
        effect="read",
    )
    start_pattern = Operation(
        INFO,
        "start_pattern",
        DcaBinding("POST", f"{ROOT}/functions/{{function}}/patterns/{{pattern}}/start", body="object"),
        params=StartPatternRequest,
        result=StartPatternResponse,
        access="operator",
        effect="action",
    )
    list_tasks = Operation(
        INFO,
        "list_tasks",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/tasks"),
        params=FunctionRequest,
        result=list[Task],
        access="operator",
        effect="read",
    )
    get_task = Operation(
        INFO,
        "get_task",
        DcaBinding("GET", f"{ROOT}/functions/{{function}}/tasks/{{taskId}}"),
        params=FunctionTaskRequest,
        result=Task,
        access="operator",
        effect="read",
    )
    set_task_beam_shape = Operation(
        INFO,
        "set_task_beam_shape",
        DcaBinding(
            "PATCH", f"{ROOT}/functions/{{function}}/tasks/{{taskId}}/beamShape", body="value", body_field="beamShape"
        ),
        params=SetTaskBeamShapeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_task_intensity = Operation(
        INFO,
        "set_task_intensity",
        DcaBinding(
            "PATCH", f"{ROOT}/functions/{{function}}/tasks/{{taskId}}/intensity", body="value", body_field="intensity"
        ),
        params=SetTaskIntensityRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_task_threshold = Operation(
        INFO,
        "set_task_threshold",
        DcaBinding(
            "PATCH", f"{ROOT}/functions/{{function}}/tasks/{{taskId}}/threshold", body="value", body_field="threshold"
        ),
        params=SetTaskThresholdRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    stop_task = Operation(
        INFO,
        "stop_task",
        DcaBinding("POST", f"{ROOT}/functions/{{function}}/tasks/{{taskId}}/stop", body="object"),
        params=FunctionTaskRequest,
        access="operator",
        effect="action",
    )
    get_maintenance_mode = Operation(
        INFO,
        "get_maintenance_mode",
        DcaBinding("GET", f"{ROOT}/maintenanceMode"),
        result=MaintenanceMode,
        access="operator",
        effect="read",
    )
    get_maintenance_mode_supported = Operation(
        INFO,
        "get_maintenance_mode_supported",
        DcaBinding("GET", f"{ROOT}/maintenanceMode/supported"),
        result=bool,
        access="operator",
        effect="read",
    )
    get_maintenance_mode_running = Operation(
        INFO,
        "get_maintenance_mode_running",
        DcaBinding("GET", f"{ROOT}/maintenanceMode/running"),
        result=bool,
        access="operator",
        effect="read",
    )
    start_maintenance_mode = Operation(
        INFO,
        "start_maintenance_mode",
        DcaBinding("POST", f"{ROOT}/maintenanceMode/start", body="object"),
        params=StartMaintenanceModeRequest,
        access="operator",
        effect="action",
    )
    stop_maintenance_mode = Operation(
        INFO,
        "stop_maintenance_mode",
        DcaBinding("POST", f"{ROOT}/maintenanceMode/stop", body="object"),
        access="operator",
        effect="action",
    )
    list_profiles = Operation(
        INFO,
        "list_profiles",
        DcaBinding("GET", f"{ROOT}/profiles"),
        result=list[Profile],
        access="operator",
        effect="read",
    )
    get_profile = Operation(
        INFO,
        "get_profile",
        DcaBinding("GET", f"{ROOT}/profiles/{{profile}}"),
        params=ProfileRequest,
        result=Profile,
        access="operator",
        effect="read",
    )
    add_profile = Operation(
        INFO,
        "add_profile",
        DcaBinding("POST", f"{ROOT}/profiles", body="object"),
        params=AddProfileRequest,
        access="operator",
        effect="write",
        write="create",
    )
    remove_profile = Operation(
        INFO,
        "remove_profile",
        DcaBinding("DELETE", f"{ROOT}/profiles/{{profile}}"),
        params=ProfileRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    start_profile = Operation(
        INFO,
        "start_profile",
        DcaBinding("POST", f"{ROOT}/profiles/{{profile}}/start", body="object"),
        params=StartProfileRequest,
        result=StartProfileResponse,
        access="operator",
        effect="action",
    )
    stop_profile = Operation(
        INFO,
        "stop_profile",
        DcaBinding("POST", f"{ROOT}/profiles/{{profile}}/stop", body="object"),
        params=ProfileRequest,
        access="operator",
        effect="action",
    )
    list_profile_functions = Operation(
        INFO,
        "list_profile_functions",
        DcaBinding("GET", f"{ROOT}/profiles/{{profile}}/functions"),
        params=ProfileRequest,
        result=list[ProfileFunction],
        access="operator",
        effect="read",
    )
    get_profile_function = Operation(
        INFO,
        "get_profile_function",
        DcaBinding("GET", f"{ROOT}/profiles/{{profile}}/functions/{{function}}"),
        params=ProfileFunctionRequest,
        result=ProfileFunction,
        access="operator",
        effect="read",
    )
    add_profile_function = Operation(
        INFO,
        "add_profile_function",
        DcaBinding("POST", f"{ROOT}/profiles/{{profile}}/functions", body="object"),
        params=AddProfileFunctionRequest,
        access="operator",
        effect="write",
        write="create",
    )
    remove_profile_function = Operation(
        INFO,
        "remove_profile_function",
        DcaBinding("DELETE", f"{ROOT}/profiles/{{profile}}/functions/{{function}}"),
        params=ProfileFunctionRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    set_profile_function_beam_shape_override = Operation(
        INFO,
        "set_profile_function_beam_shape_override",
        DcaBinding(
            "PATCH",
            f"{ROOT}/profiles/{{profile}}/functions/{{function}}/beamShapeOverride",
            body="value",
            body_field="beamShapeOverride",
        ),
        params=SetProfileFunctionBeamShapeOverrideRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_profile_function_intensity = Operation(
        INFO,
        "set_profile_function_intensity",
        DcaBinding(
            "PATCH",
            f"{ROOT}/profiles/{{profile}}/functions/{{function}}/intensity",
            body="value",
            body_field="intensity",
        ),
        params=SetProfileFunctionIntensityRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_profile_function_threshold = Operation(
        INFO,
        "set_profile_function_threshold",
        DcaBinding(
            "PATCH",
            f"{ROOT}/profiles/{{profile}}/functions/{{function}}/threshold",
            body="value",
            body_field="threshold",
        ),
        params=SetProfileFunctionThresholdRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SirenAndLightConfigApi(SyncApi):
    """Siren and light configuration (``siren-and-light-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> SirenAndLight:
        """All data of the Siren and light configuration API. Access: operator."""
        return self._run(OPS.get_all, None, {}, request_options)

    def stop(self, *, request_options: RequestOptions | None = None) -> None:
        """Send a request to stop all tasks for all functions. Access: operator."""
        self._run(OPS.stop, None, {}, request_options)

    def list_functions(self, *, request_options: RequestOptions | None = None) -> list[Function]:
        """List the functions. Access: operator."""
        return self._run(OPS.list_functions, None, {}, request_options)

    def get_function(self, function: NameString, *, request_options: RequestOptions | None = None) -> Function:
        """Get one function. Access: operator."""
        return self._run(OPS.get_function, None, {"function": function}, request_options)

    def get_health_check_supported(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> bool:
        """Whether a function supports health check. Access: operator."""
        return self._run(OPS.get_health_check_supported, None, {"function": function}, request_options)

    def run_health_check(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> RunHealthCheckResponse:
        """Run a health check on a function. Access: operator."""
        return self._run(OPS.run_health_check, None, {"function": function}, request_options)

    def stop_function(self, function: NameString, *, request_options: RequestOptions | None = None) -> None:
        """Send a request to stop all running tasks on the function. Access: operator."""
        self._run(OPS.stop_function, None, {"function": function}, request_options)

    def get_function_beam_shape(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> BeamShape:
        """Get the default beam shape and the supported beam shapes of a function. Access: operator."""
        return self._run(OPS.get_function_beam_shape, None, {"function": function}, request_options)

    def set_default_beam_shape(
        self, function: NameString, *, default: NameString, request_options: RequestOptions | None = None
    ) -> None:
        """Set the default of the beam shape. Changes only the fields given. Access: operator."""
        self._run(OPS.set_default_beam_shape, None, {"function": function, "default": default}, request_options)

    def get_default_beam_shape(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> NameString:
        """Get the default beam shape of a function. Access: operator."""
        return self._run(OPS.get_default_beam_shape, None, {"function": function}, request_options)

    def list_beam_shapes(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> list[BeamShapeEntry]:
        """List the beam shapes supported by a function. Access: operator."""
        return self._run(OPS.list_beam_shapes, None, {"function": function}, request_options)

    def get_supported_beam_shape(
        self, function: NameString, beam_shape: NameString, *, request_options: RequestOptions | None = None
    ) -> BeamShapeEntry:
        """Get one beam shape. Access: operator."""
        return self._run(
            OPS.get_supported_beam_shape, None, {"function": function, "beam_shape": beam_shape}, request_options
        )

    def list_patterns(self, function: NameString, *, request_options: RequestOptions | None = None) -> list[Pattern]:
        """List the patterns. Access: operator."""
        return self._run(OPS.list_patterns, None, {"function": function}, request_options)

    def get_pattern(
        self, function: NameString, pattern: NameString, *, request_options: RequestOptions | None = None
    ) -> Pattern:
        """Get one pattern. Access: operator."""
        return self._run(OPS.get_pattern, None, {"function": function, "pattern": pattern}, request_options)

    @overload
    def start_pattern(
        self, request: StartPatternRequest, /, *, request_options: RequestOptions | None = None
    ) -> StartPatternResponse: ...
    @overload
    def start_pattern(
        self,
        /,
        *,
        function: NameString,
        pattern: NameString,
        beam_shape_override: NameString | None | MISSING = MISSING,
        colors: ColorsArray | None | MISSING = MISSING,
        duration: Duration | None | MISSING = MISSING,
        intensity: Integer0To5 | None | MISSING = MISSING,
        priority: Integer1To10 | None | MISSING = MISSING,
        speed: Integer1To5 | None | MISSING = MISSING,
        start_at: Timestamp | None | MISSING = MISSING,
        threshold: Integer0To100 | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartPatternResponse: ...
    def start_pattern(
        self,
        request: StartPatternRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> StartPatternResponse:
        """Send a request to start pattern. Access: operator."""
        return self._run(OPS.start_pattern, request, kwargs, request_options)

    def list_tasks(self, function: NameString, *, request_options: RequestOptions | None = None) -> list[Task]:
        """List the tasks. Access: operator."""
        return self._run(OPS.list_tasks, None, {"function": function}, request_options)

    def get_task(self, function: NameString, task_id: TaskId, *, request_options: RequestOptions | None = None) -> Task:
        """Get one task. Access: operator."""
        return self._run(OPS.get_task, None, {"function": function, "task_id": task_id}, request_options)

    def set_task_beam_shape(
        self,
        function: NameString,
        task_id: TaskId,
        *,
        beam_shape: NameString,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the beam shape of a task. Changes only the fields given. Access: operator."""
        self._run(
            OPS.set_task_beam_shape,
            None,
            {"function": function, "task_id": task_id, "beam_shape": beam_shape},
            request_options,
        )

    def set_task_intensity(
        self,
        function: NameString,
        task_id: TaskId,
        *,
        intensity: Integer0To5,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the intensity of a task. Changes only the fields given. Access: operator."""
        self._run(
            OPS.set_task_intensity,
            None,
            {"function": function, "task_id": task_id, "intensity": intensity},
            request_options,
        )

    def set_task_threshold(
        self,
        function: NameString,
        task_id: TaskId,
        *,
        threshold: Integer0To100,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the threshold of a task. Changes only the fields given. Access: operator."""
        self._run(
            OPS.set_task_threshold,
            None,
            {"function": function, "task_id": task_id, "threshold": threshold},
            request_options,
        )

    def stop_task(
        self, function: NameString, task_id: TaskId, *, request_options: RequestOptions | None = None
    ) -> None:
        """Send a request to stop the task. Access: operator."""
        self._run(OPS.stop_task, None, {"function": function, "task_id": task_id}, request_options)

    def get_maintenance_mode(self, *, request_options: RequestOptions | None = None) -> MaintenanceMode:
        """Get the maintenance mode settings. Access: operator."""
        return self._run(OPS.get_maintenance_mode, None, {}, request_options)

    def get_maintenance_mode_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether maintenance mode is supported on the device. Access: operator."""
        return self._run(OPS.get_maintenance_mode_supported, None, {}, request_options)

    def get_maintenance_mode_running(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether maintenance mode is currently running. Access: operator."""
        return self._run(OPS.get_maintenance_mode_running, None, {}, request_options)

    def start_maintenance_mode(
        self, *, time: IntegerMinimum1 | None | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Start maintenance mode, which mutes siren-type functions. Without time it runs until stopped.

        Access: operator.
        """
        self._run(OPS.start_maintenance_mode, None, {"time": time}, request_options)

    def stop_maintenance_mode(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop maintenance mode. Access: operator."""
        self._run(OPS.stop_maintenance_mode, None, {}, request_options)

    def list_profiles(self, *, request_options: RequestOptions | None = None) -> list[Profile]:
        """List the profiles. Access: operator."""
        return self._run(OPS.list_profiles, None, {}, request_options)

    def get_profile(self, profile: NameString, *, request_options: RequestOptions | None = None) -> Profile:
        """Get one profile. Access: operator."""
        return self._run(OPS.get_profile, None, {"profile": profile}, request_options)

    def add_profile(
        self,
        *,
        profile: NameString,
        description: DescriptionString | MISSING = MISSING,
        resume_on_startup: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Add a profile. Access: operator."""
        self._run(
            OPS.add_profile,
            None,
            {"profile": profile, "description": description, "resume_on_startup": resume_on_startup},
            request_options,
        )

    def remove_profile(self, profile: NameString, *, request_options: RequestOptions | None = None) -> None:
        """Remove a profile. Access: operator."""
        self._run(OPS.remove_profile, None, {"profile": profile}, request_options)

    def start_profile(
        self,
        profile: NameString,
        *,
        start_at: Timestamp | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartProfileResponse:
        """Send a request to start a Siren and Light profile. Access: operator."""
        return self._run(OPS.start_profile, None, {"profile": profile, "start_at": start_at}, request_options)

    def stop_profile(self, profile: NameString, *, request_options: RequestOptions | None = None) -> None:
        """Send a request to stop a Siren and Light profile. Access: operator."""
        self._run(OPS.stop_profile, None, {"profile": profile}, request_options)

    def list_profile_functions(
        self, profile: NameString, *, request_options: RequestOptions | None = None
    ) -> list[ProfileFunction]:
        """List the functions. Access: operator."""
        return self._run(OPS.list_profile_functions, None, {"profile": profile}, request_options)

    def get_profile_function(
        self, profile: NameString, function: NameString, *, request_options: RequestOptions | None = None
    ) -> ProfileFunction:
        """Get one function. Access: operator."""
        return self._run(OPS.get_profile_function, None, {"profile": profile, "function": function}, request_options)

    @overload
    def add_profile_function(
        self, request: AddProfileFunctionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_profile_function(
        self,
        /,
        *,
        profile: NameString,
        function: NameString,
        pattern: NameString,
        intensity: Integer0To5 | MISSING = MISSING,
        speed: Integer1To5 | MISSING = MISSING,
        colors: ColorsArray | MISSING = MISSING,
        duration: Duration | MISSING = MISSING,
        priority: Integer1To13 | MISSING = MISSING,
        threshold: Integer0To100 | MISSING = MISSING,
        beam_shape_override: NameString | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_profile_function(
        self,
        request: AddProfileFunctionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a function. Access: operator."""
        self._run(OPS.add_profile_function, request, kwargs, request_options)

    def remove_profile_function(
        self, profile: NameString, function: NameString, *, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a function. Access: operator."""
        self._run(OPS.remove_profile_function, None, {"profile": profile, "function": function}, request_options)

    def set_profile_function_beam_shape_override(
        self,
        profile: NameString,
        function: NameString,
        *,
        beam_shape_override: NameString | None,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the beam shape override of a function.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_profile_function_beam_shape_override,
            None,
            {"profile": profile, "function": function, "beam_shape_override": beam_shape_override},
            request_options,
        )

    def set_profile_function_intensity(
        self,
        profile: NameString,
        function: NameString,
        *,
        intensity: Integer0To5,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the intensity of a function. Changes only the fields given. Access: operator."""
        self._run(
            OPS.set_profile_function_intensity,
            None,
            {"profile": profile, "function": function, "intensity": intensity},
            request_options,
        )

    def set_profile_function_threshold(
        self,
        profile: NameString,
        function: NameString,
        *,
        threshold: Integer0To100,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the threshold of a function. Changes only the fields given. Access: operator."""
        self._run(
            OPS.set_profile_function_threshold,
            None,
            {"profile": profile, "function": function, "threshold": threshold},
            request_options,
        )


class AsyncSirenAndLightConfigApi(AsyncApi):
    """Siren and light configuration (``siren-and-light-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> SirenAndLight:
        """All data of the Siren and light configuration API. Access: operator."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def stop(self, *, request_options: RequestOptions | None = None) -> None:
        """Send a request to stop all tasks for all functions. Access: operator."""
        await self._run(OPS.stop, None, {}, request_options)

    async def list_functions(self, *, request_options: RequestOptions | None = None) -> list[Function]:
        """List the functions. Access: operator."""
        return await self._run(OPS.list_functions, None, {}, request_options)

    async def get_function(self, function: NameString, *, request_options: RequestOptions | None = None) -> Function:
        """Get one function. Access: operator."""
        return await self._run(OPS.get_function, None, {"function": function}, request_options)

    async def get_health_check_supported(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> bool:
        """Whether a function supports health check. Access: operator."""
        return await self._run(OPS.get_health_check_supported, None, {"function": function}, request_options)

    async def run_health_check(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> RunHealthCheckResponse:
        """Run a health check on a function. Access: operator."""
        return await self._run(OPS.run_health_check, None, {"function": function}, request_options)

    async def stop_function(self, function: NameString, *, request_options: RequestOptions | None = None) -> None:
        """Send a request to stop all running tasks on the function. Access: operator."""
        await self._run(OPS.stop_function, None, {"function": function}, request_options)

    async def get_function_beam_shape(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> BeamShape:
        """Get the default beam shape and the supported beam shapes of a function. Access: operator."""
        return await self._run(OPS.get_function_beam_shape, None, {"function": function}, request_options)

    async def set_default_beam_shape(
        self, function: NameString, *, default: NameString, request_options: RequestOptions | None = None
    ) -> None:
        """Set the default of the beam shape. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_default_beam_shape, None, {"function": function, "default": default}, request_options)

    async def get_default_beam_shape(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> NameString:
        """Get the default beam shape of a function. Access: operator."""
        return await self._run(OPS.get_default_beam_shape, None, {"function": function}, request_options)

    async def list_beam_shapes(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> list[BeamShapeEntry]:
        """List the beam shapes supported by a function. Access: operator."""
        return await self._run(OPS.list_beam_shapes, None, {"function": function}, request_options)

    async def get_supported_beam_shape(
        self, function: NameString, beam_shape: NameString, *, request_options: RequestOptions | None = None
    ) -> BeamShapeEntry:
        """Get one beam shape. Access: operator."""
        return await self._run(
            OPS.get_supported_beam_shape, None, {"function": function, "beam_shape": beam_shape}, request_options
        )

    async def list_patterns(
        self, function: NameString, *, request_options: RequestOptions | None = None
    ) -> list[Pattern]:
        """List the patterns. Access: operator."""
        return await self._run(OPS.list_patterns, None, {"function": function}, request_options)

    async def get_pattern(
        self, function: NameString, pattern: NameString, *, request_options: RequestOptions | None = None
    ) -> Pattern:
        """Get one pattern. Access: operator."""
        return await self._run(OPS.get_pattern, None, {"function": function, "pattern": pattern}, request_options)

    @overload
    async def start_pattern(
        self, request: StartPatternRequest, /, *, request_options: RequestOptions | None = None
    ) -> StartPatternResponse: ...
    @overload
    async def start_pattern(
        self,
        /,
        *,
        function: NameString,
        pattern: NameString,
        beam_shape_override: NameString | None | MISSING = MISSING,
        colors: ColorsArray | None | MISSING = MISSING,
        duration: Duration | None | MISSING = MISSING,
        intensity: Integer0To5 | None | MISSING = MISSING,
        priority: Integer1To10 | None | MISSING = MISSING,
        speed: Integer1To5 | None | MISSING = MISSING,
        start_at: Timestamp | None | MISSING = MISSING,
        threshold: Integer0To100 | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartPatternResponse: ...
    async def start_pattern(
        self,
        request: StartPatternRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> StartPatternResponse:
        """Send a request to start pattern. Access: operator."""
        return await self._run(OPS.start_pattern, request, kwargs, request_options)

    async def list_tasks(self, function: NameString, *, request_options: RequestOptions | None = None) -> list[Task]:
        """List the tasks. Access: operator."""
        return await self._run(OPS.list_tasks, None, {"function": function}, request_options)

    async def get_task(
        self, function: NameString, task_id: TaskId, *, request_options: RequestOptions | None = None
    ) -> Task:
        """Get one task. Access: operator."""
        return await self._run(OPS.get_task, None, {"function": function, "task_id": task_id}, request_options)

    async def set_task_beam_shape(
        self,
        function: NameString,
        task_id: TaskId,
        *,
        beam_shape: NameString,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the beam shape of a task. Changes only the fields given. Access: operator."""
        await self._run(
            OPS.set_task_beam_shape,
            None,
            {"function": function, "task_id": task_id, "beam_shape": beam_shape},
            request_options,
        )

    async def set_task_intensity(
        self,
        function: NameString,
        task_id: TaskId,
        *,
        intensity: Integer0To5,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the intensity of a task. Changes only the fields given. Access: operator."""
        await self._run(
            OPS.set_task_intensity,
            None,
            {"function": function, "task_id": task_id, "intensity": intensity},
            request_options,
        )

    async def set_task_threshold(
        self,
        function: NameString,
        task_id: TaskId,
        *,
        threshold: Integer0To100,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the threshold of a task. Changes only the fields given. Access: operator."""
        await self._run(
            OPS.set_task_threshold,
            None,
            {"function": function, "task_id": task_id, "threshold": threshold},
            request_options,
        )

    async def stop_task(
        self, function: NameString, task_id: TaskId, *, request_options: RequestOptions | None = None
    ) -> None:
        """Send a request to stop the task. Access: operator."""
        await self._run(OPS.stop_task, None, {"function": function, "task_id": task_id}, request_options)

    async def get_maintenance_mode(self, *, request_options: RequestOptions | None = None) -> MaintenanceMode:
        """Get the maintenance mode settings. Access: operator."""
        return await self._run(OPS.get_maintenance_mode, None, {}, request_options)

    async def get_maintenance_mode_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether maintenance mode is supported on the device. Access: operator."""
        return await self._run(OPS.get_maintenance_mode_supported, None, {}, request_options)

    async def get_maintenance_mode_running(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether maintenance mode is currently running. Access: operator."""
        return await self._run(OPS.get_maintenance_mode_running, None, {}, request_options)

    async def start_maintenance_mode(
        self, *, time: IntegerMinimum1 | None | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Start maintenance mode, which mutes siren-type functions. Without time it runs until stopped.

        Access: operator.
        """
        await self._run(OPS.start_maintenance_mode, None, {"time": time}, request_options)

    async def stop_maintenance_mode(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop maintenance mode. Access: operator."""
        await self._run(OPS.stop_maintenance_mode, None, {}, request_options)

    async def list_profiles(self, *, request_options: RequestOptions | None = None) -> list[Profile]:
        """List the profiles. Access: operator."""
        return await self._run(OPS.list_profiles, None, {}, request_options)

    async def get_profile(self, profile: NameString, *, request_options: RequestOptions | None = None) -> Profile:
        """Get one profile. Access: operator."""
        return await self._run(OPS.get_profile, None, {"profile": profile}, request_options)

    async def add_profile(
        self,
        *,
        profile: NameString,
        description: DescriptionString | MISSING = MISSING,
        resume_on_startup: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Add a profile. Access: operator."""
        await self._run(
            OPS.add_profile,
            None,
            {"profile": profile, "description": description, "resume_on_startup": resume_on_startup},
            request_options,
        )

    async def remove_profile(self, profile: NameString, *, request_options: RequestOptions | None = None) -> None:
        """Remove a profile. Access: operator."""
        await self._run(OPS.remove_profile, None, {"profile": profile}, request_options)

    async def start_profile(
        self,
        profile: NameString,
        *,
        start_at: Timestamp | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartProfileResponse:
        """Send a request to start a Siren and Light profile. Access: operator."""
        return await self._run(OPS.start_profile, None, {"profile": profile, "start_at": start_at}, request_options)

    async def stop_profile(self, profile: NameString, *, request_options: RequestOptions | None = None) -> None:
        """Send a request to stop a Siren and Light profile. Access: operator."""
        await self._run(OPS.stop_profile, None, {"profile": profile}, request_options)

    async def list_profile_functions(
        self, profile: NameString, *, request_options: RequestOptions | None = None
    ) -> list[ProfileFunction]:
        """List the functions. Access: operator."""
        return await self._run(OPS.list_profile_functions, None, {"profile": profile}, request_options)

    async def get_profile_function(
        self, profile: NameString, function: NameString, *, request_options: RequestOptions | None = None
    ) -> ProfileFunction:
        """Get one function. Access: operator."""
        return await self._run(
            OPS.get_profile_function, None, {"profile": profile, "function": function}, request_options
        )

    @overload
    async def add_profile_function(
        self, request: AddProfileFunctionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_profile_function(
        self,
        /,
        *,
        profile: NameString,
        function: NameString,
        pattern: NameString,
        intensity: Integer0To5 | MISSING = MISSING,
        speed: Integer1To5 | MISSING = MISSING,
        colors: ColorsArray | MISSING = MISSING,
        duration: Duration | MISSING = MISSING,
        priority: Integer1To13 | MISSING = MISSING,
        threshold: Integer0To100 | MISSING = MISSING,
        beam_shape_override: NameString | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_profile_function(
        self,
        request: AddProfileFunctionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a function. Access: operator."""
        await self._run(OPS.add_profile_function, request, kwargs, request_options)

    async def remove_profile_function(
        self, profile: NameString, function: NameString, *, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a function. Access: operator."""
        await self._run(OPS.remove_profile_function, None, {"profile": profile, "function": function}, request_options)

    async def set_profile_function_beam_shape_override(
        self,
        profile: NameString,
        function: NameString,
        *,
        beam_shape_override: NameString | None,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the beam shape override of a function.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_profile_function_beam_shape_override,
            None,
            {"profile": profile, "function": function, "beam_shape_override": beam_shape_override},
            request_options,
        )

    async def set_profile_function_intensity(
        self,
        profile: NameString,
        function: NameString,
        *,
        intensity: Integer0To5,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the intensity of a function. Changes only the fields given. Access: operator."""
        await self._run(
            OPS.set_profile_function_intensity,
            None,
            {"profile": profile, "function": function, "intensity": intensity},
            request_options,
        )

    async def set_profile_function_threshold(
        self,
        profile: NameString,
        function: NameString,
        *,
        threshold: Integer0To100,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the threshold of a function. Changes only the fields given. Access: operator."""
        await self._run(
            OPS.set_profile_function_threshold,
            None,
            {"profile": profile, "function": function, "threshold": threshold},
            request_options,
        )
