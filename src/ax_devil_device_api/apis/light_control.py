# GENERATED from specs/apis/network-video/light-control.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Query and control the IR and white light LED groups: activate, enable, intensity, angle of illumination, day/night synchronization, IR wavelength and beam shape.

Docs: https://developer.axis.com/vapix/network-video/light-control/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class LedCapabilities(Model):
    """Which methods a light supports."""

    automatic_intensity_support: bool | None = Field(
        default=None, validation_alias="automaticIntensitySupport", serialization_alias="automaticIntensitySupport"
    )
    """Indicates that `setAutomaticIntensityMode` is supported."""
    manual_intensity_support: bool | None = Field(
        default=None, validation_alias="manualIntensitySupport", serialization_alias="manualIntensitySupport"
    )
    """Indicates that `getManualIntensity` and `setManualIntensity` are supported."""
    individual_intensity_support: bool | None = Field(
        default=None, validation_alias="individualIntensitySupport", serialization_alias="individualIntensitySupport"
    )
    """Indicates that `getIndividualIntensity` and `setIndividualIntensity` are supported."""
    get_current_intensity_support: bool | None = Field(
        default=None, validation_alias="getCurrentIntensitySupport", serialization_alias="getCurrentIntensitySupport"
    )
    """Indicates that `getCurrentIntensity` is supported."""
    manual_angle_of_illumination_support: bool | None = Field(
        default=None,
        validation_alias="manualAngleOfIlluminationSupport",
        serialization_alias="manualAngleOfIlluminationSupport",
    )
    """Indicates that `setManualAngleOfIllumination` is supported."""
    automatic_angle_of_illumination_support: bool | None = Field(
        default=None,
        validation_alias="automaticAngleOfIlluminationSupport",
        serialization_alias="automaticAngleOfIlluminationSupport",
    )
    """Indicates that `setAutomaticAngleOfIlluminationMode` is supported."""
    day_night_synchronize_support: bool | None = Field(
        default=None, validation_alias="dayNightSynchronizeSupport", serialization_alias="dayNightSynchronizeSupport"
    )
    """Indicates that `setLightSynchronizeDayNightMode` is supported."""
    multi_ir_wave_length_support: bool | None = Field(
        default=None, validation_alias="multiIRWaveLengthSupport", serialization_alias="multiIRWaveLengthSupport"
    )
    """Indicates that `getValidIRWavelengths`, `setIRWavelength` and `getIRWavelength` are supported."""


class LightCapabilities(Model):
    """Capabilities of one LED group."""

    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The ID of the LED group."""
    automatic_intensity_support: bool | None = Field(
        default=None, validation_alias="automaticIntensitySupport", serialization_alias="automaticIntensitySupport"
    )
    """Indicates that `setAutomaticIntensityMode` is supported."""
    manual_intensity_support: bool | None = Field(
        default=None, validation_alias="manualIntensitySupport", serialization_alias="manualIntensitySupport"
    )
    """Indicates that `getManualIntensity` and `setManualIntensity` are supported."""
    individual_intensity_support: bool | None = Field(
        default=None, validation_alias="individualIntensitySupport", serialization_alias="individualIntensitySupport"
    )
    """Indicates that `getIndividualIntensity` and `setIndividualIntensity` are supported."""
    get_current_intensity_support: bool | None = Field(
        default=None, validation_alias="getCurrentIntensitySupport", serialization_alias="getCurrentIntensitySupport"
    )
    """Indicates that `getCurrentIntensity` is supported."""
    manual_angle_of_illumination_support: bool | None = Field(
        default=None,
        validation_alias="manualAngleOfIlluminationSupport",
        serialization_alias="manualAngleOfIlluminationSupport",
    )
    """Indicates that `setManualAngleOfIllumination` is supported."""
    automatic_angle_of_illumination_support: bool | None = Field(
        default=None,
        validation_alias="automaticAngleOfIlluminationSupport",
        serialization_alias="automaticAngleOfIlluminationSupport",
    )
    """Indicates that `setAutomaticAngleOfIlluminationMode` is supported."""
    day_night_synchronize_support: bool | None = Field(
        default=None, validation_alias="dayNightSynchronizeSupport", serialization_alias="dayNightSynchronizeSupport"
    )
    """Indicates that `setLightSynchronizeDayNightMode` is supported."""
    multi_ir_wave_length_support: bool | None = Field(
        default=None, validation_alias="multiIRWaveLengthSupport", serialization_alias="multiIRWaveLengthSupport"
    )
    """Indicates that `getValidIRWavelengths`, `setIRWavelength` and `getIRWavelength` are supported."""


class ServiceCapabilities(Model):
    """Capabilities of the light service as a whole, and per LED group."""

    automatic_intensity_support: bool | None = Field(
        default=None, validation_alias="automaticIntensitySupport", serialization_alias="automaticIntensitySupport"
    )
    """Indicates that `setAutomaticIntensityMode` is supported."""
    manual_intensity_support: bool | None = Field(
        default=None, validation_alias="manualIntensitySupport", serialization_alias="manualIntensitySupport"
    )
    """Indicates that `getManualIntensity` and `setManualIntensity` are supported."""
    individual_intensity_support: bool | None = Field(
        default=None, validation_alias="individualIntensitySupport", serialization_alias="individualIntensitySupport"
    )
    """Indicates that `getIndividualIntensity` and `setIndividualIntensity` are supported."""
    get_current_intensity_support: bool | None = Field(
        default=None, validation_alias="getCurrentIntensitySupport", serialization_alias="getCurrentIntensitySupport"
    )
    """Indicates that `getCurrentIntensity` is supported."""
    manual_angle_of_illumination_support: bool | None = Field(
        default=None,
        validation_alias="manualAngleOfIlluminationSupport",
        serialization_alias="manualAngleOfIlluminationSupport",
    )
    """Indicates that `setManualAngleOfIllumination` is supported."""
    automatic_angle_of_illumination_support: bool | None = Field(
        default=None,
        validation_alias="automaticAngleOfIlluminationSupport",
        serialization_alias="automaticAngleOfIlluminationSupport",
    )
    """Indicates that `setAutomaticAngleOfIlluminationMode` is supported."""
    day_night_synchronize_support: bool | None = Field(
        default=None, validation_alias="dayNightSynchronizeSupport", serialization_alias="dayNightSynchronizeSupport"
    )
    """Indicates that `setLightSynchronizeDayNightMode` is supported."""
    multi_ir_wave_length_support: bool | None = Field(
        default=None, validation_alias="multiIRWaveLengthSupport", serialization_alias="multiIRWaveLengthSupport"
    )
    """Indicates that `getValidIRWavelengths`, `setIRWavelength` and `getIRWavelength` are supported."""
    capabilities: list[LightCapabilities] | None = None
    """Supported capabilities for each LED group."""


class LightInformation(Model):
    """State of one light."""

    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """Unique ID of the light."""
    light_type: str | None = Field(default=None, validation_alias="lightType", serialization_alias="lightType")
    """Type identifier of the light."""
    enabled: bool | None = None
    """Indicates if the light is enabled."""
    synchronize_day_night_mode: bool | None = Field(
        default=None, validation_alias="synchronizeDayNightMode", serialization_alias="synchronizeDayNightMode"
    )
    """Indicates if the light is synchronized with day/night."""
    light_state: bool | None = Field(default=None, validation_alias="lightState", serialization_alias="lightState")
    """Indicates if the light is ON or OFF."""
    automatic_intensity_mode: bool | None = Field(
        default=None, validation_alias="automaticIntensityMode", serialization_alias="automaticIntensityMode"
    )
    """Indicates if the mode for automatic intensity is active."""
    automatic_angle_of_illumination_mode: bool | None = Field(
        default=None,
        validation_alias="automaticAngleOfIlluminationMode",
        serialization_alias="automaticAngleOfIlluminationMode",
    )
    """Indicates if the mode for automatic angle of illumination is active."""
    nr_of_le_ds: int | None = Field(default=None, validation_alias="nrOfLEDs", serialization_alias="nrOfLEDs")
    """Number of configurable LEDs in a light group. The light groups are identified by their Light ID."""
    error: bool | None = None
    """An error has occurred."""
    error_info: str | None = Field(default=None, validation_alias="errorInfo", serialization_alias="errorInfo")
    """Error description."""


class LightInformationList(Model):
    items: list[LightInformation] | None = None


class LightStatus(Model):
    status: bool
    """Indicates if the light is ON or OFF."""


class ValueRange(Model):
    low: int
    """The lower limit of the range."""
    high: int
    """The upper limit of the range."""


class ValidRanges(Model):
    ranges: list[ValueRange]
    """The valid ranges."""


class Intensity(Model):
    intensity: int
    """The intensity of the light."""


class AngleOfIllumination(Model):
    angle_of_illumination: int = Field(
        validation_alias="angleOfIllumination", serialization_alias="angleOfIllumination"
    )
    """The angle of illumination."""


class DayNightSynchronization(Model):
    enabled: bool
    """If the day/night cut filter synchronization of the light is active."""


class ValidIrWavelengths(Model):
    wavelengths: list[str] | None = None
    """The valid wavelength settings, for example 850nm."""


class IrWavelength(Model):
    ir_wavelength: str = Field(validation_alias="IRWavelength", serialization_alias="IRWavelength")
    """The currently set infrared wavelength."""


class BeamShape(Model):
    beam_shape: str = Field(validation_alias="beamShape", serialization_alias="beamShape")
    """The beam shape."""


class ValidBeamShapes(Model):
    items: list[BeamShape] | None = None
    """The valid beam shapes."""


class LightIdRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""


class SetAutomaticIntensityModeRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    enabled: bool
    """Enables automatic light intensity control."""


class SetManualIntensityRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    intensity: int
    """The intensity level of the light; see get_valid_intensity for the valid ranges."""


class SetIndividualIntensityRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    ledid: int = Field(validation_alias="LEDID", serialization_alias="LEDID")
    """The ID of the LED."""
    intensity: int
    """The intensity level of the light."""


class GetIndividualIntensityRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    ledid: int = Field(validation_alias="LEDID", serialization_alias="LEDID")
    """The ID of the LED."""


class SetAutomaticAngleOfIlluminationModeRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    enabled: bool
    """Activate or deactivate automatic angle of illumination mode for the light."""


class SetManualAngleOfIlluminationRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    angle_of_illumination: int = Field(
        validation_alias="angleOfIllumination", serialization_alias="angleOfIllumination"
    )
    """The angle of illumination; see get_valid_angle_of_illumination for the valid ranges."""


class SetLightSynchronizeDayNightModeRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    enabled: bool
    """Activate or deactivate synchronization with the day/night mode for the light."""


class SetIrWavelengthRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    ir_wavelength: str = Field(validation_alias="IRWavelength", serialization_alias="IRWavelength")
    """The infrared wavelength, one of get_valid_ir_wavelengths."""


class SetBeamShapeRequest(Model):
    light_id: str = Field(validation_alias="lightID", serialization_alias="lightID")
    """The light ID."""
    beam_shape: str = Field(validation_alias="beamShape", serialization_alias="beamShape")
    """The beam shape, one of get_valid_beam_shapes."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/lightcontrol.cgi"

INFO = ApiInfo(
    id="light-control",
    name="Light control API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 2), ApiVersion(1, 7)),
    discovery=(
        ApiDiscovery("light-control"),
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.LightControl.LightControl2", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/light-control/",),
    errors={
        1000: ErrorCode("PARAM_INVALID_VALUE_ERROR. Invalid parameter value.", "invalid_argument"),
        2000: ErrorCode("RESOURCE_MEM_ERROR. Failed to allocate memory.", "internal"),
        2001: ErrorCode("ACCESS_FORBIDDEN. Access forbidden", "access_denied"),
        2002: ErrorCode(
            "HTTP_METHOD_NOT_SUPPORTED. HTTP request type not supported. Only POST supported.", "unsupported"
        ),
        2003: ErrorCode("API_VERSION_NOT_SUPPORTED. The requested API version is not supported.", "unsupported"),
        2004: ErrorCode("METHOD_NOT_SUPPORTED. Method not supported.", "unsupported"),
        3000: ErrorCode("UNSUPPORTED_API_VERSION. The requested API version is not supported.", "unsupported"),
        4000: ErrorCode("JSON_INVALID_ERROR. The provided JSON input was invalid.", "invalid_argument"),
        4001: ErrorCode(
            "JSON_KEY_NOT_FOUND_ERROR. A mandatory input parameter was not found in the input.", "invalid_argument"
        ),
        4002: ErrorCode("JSON_INVALID_TYPE. The provided JSON parameter type was incorrect.", "invalid_argument"),
        7000: ErrorCode(
            "UNSUPPORTED_API_VERSION. The requested API version is not supported by this implementation.", "unsupported"
        ),
        8000: ErrorCode("INTERNAL_ERROR. Internal error.", "internal"),
        8001: ErrorCode("UNEXPECTED_ERROR. Unexpected error.", "internal"),
        8002: ErrorCode("GENERIC_ERROR. Generic error.", "internal"),
    },
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        JsonRpcBinding("getServiceCapabilities", PATH),
        result=ServiceCapabilities,
        access="operator",
        effect="read",
    )
    get_light_information = Operation(
        INFO,
        "get_light_information",
        JsonRpcBinding("getLightInformation", PATH),
        result=LightInformationList,
        access="operator",
        effect="read",
        errors={
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    activate_light = Operation(
        INFO,
        "activate_light",
        JsonRpcBinding("activateLight", PATH),
        params=LightIdRequest,
        access="operator",
        effect="action",
        errors={
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
            1008: ErrorCode("UPDATE_IRCUTFILTER_FAULT. Could not update IR cut filter.", "internal"),
            1009: ErrorCode(
                "LIGHT_DISABLED_FAULT. The light group is turned off and can’t be activated.", "unavailable"
            ),
        },
    )
    deactivate_light = Operation(
        INFO,
        "deactivate_light",
        JsonRpcBinding("deactivateLight", PATH),
        params=LightIdRequest,
        access="operator",
        effect="action",
        errors={
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    enable_light = Operation(
        INFO,
        "enable_light",
        JsonRpcBinding("enableLight", PATH),
        params=LightIdRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    disable_light = Operation(
        INFO,
        "disable_light",
        JsonRpcBinding("disableLight", PATH),
        params=LightIdRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_light_status = Operation(
        INFO,
        "get_light_status",
        JsonRpcBinding("getLightStatus", PATH),
        params=LightIdRequest,
        result=LightStatus,
        access="operator",
        effect="read",
        errors={
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_automatic_intensity_mode = Operation(
        INFO,
        "set_automatic_intensity_mode",
        JsonRpcBinding("setAutomaticIntensityMode", PATH),
        params=SetAutomaticIntensityModeRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_valid_intensity = Operation(
        INFO,
        "get_valid_intensity",
        JsonRpcBinding("getValidIntensity", PATH),
        params=LightIdRequest,
        result=ValidRanges,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_manual_intensity = Operation(
        INFO,
        "set_manual_intensity",
        JsonRpcBinding("setManualIntensity", PATH),
        params=SetManualIntensityRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1003: ErrorCode(
                "INVALID_INTENSITY_FAULT. Provided intensity level is out of the supported range.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_manual_intensity = Operation(
        INFO,
        "get_manual_intensity",
        JsonRpcBinding("getManualIntensity", PATH),
        params=LightIdRequest,
        result=Intensity,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_individual_intensity = Operation(
        INFO,
        "set_individual_intensity",
        JsonRpcBinding("setIndividualIntensity", PATH),
        params=SetIndividualIntensityRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1003: ErrorCode(
                "INVALID_INTENSITY_FAULT. Provided intensity level is out of the supported range.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_individual_intensity = Operation(
        INFO,
        "get_individual_intensity",
        JsonRpcBinding("getIndividualIntensity", PATH),
        params=GetIndividualIntensityRequest,
        result=Intensity,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_current_intensity = Operation(
        INFO,
        "get_current_intensity",
        JsonRpcBinding("getCurrentIntensity", PATH),
        params=LightIdRequest,
        result=Intensity,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_automatic_angle_of_illumination_mode = Operation(
        INFO,
        "set_automatic_angle_of_illumination_mode",
        JsonRpcBinding("setAutomaticAngleOfIlluminationMode", PATH),
        params=SetAutomaticAngleOfIlluminationModeRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_valid_angle_of_illumination = Operation(
        INFO,
        "get_valid_angle_of_illumination",
        JsonRpcBinding("getValidAngleOfIllumination", PATH),
        params=LightIdRequest,
        result=ValidRanges,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_manual_angle_of_illumination = Operation(
        INFO,
        "set_manual_angle_of_illumination",
        JsonRpcBinding("setManualAngleOfIllumination", PATH),
        params=SetManualAngleOfIlluminationRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1004: ErrorCode(
                "INVALID_ANGLE_OF_ILLUMINATION_FAULT. Provided angle of illumination is out of the supported range.",
                "invalid_argument",
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_manual_angle_of_illumination = Operation(
        INFO,
        "get_manual_angle_of_illumination",
        JsonRpcBinding("getManualAngleOfIllumination", PATH),
        params=LightIdRequest,
        result=AngleOfIllumination,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_current_angle_of_illumination = Operation(
        INFO,
        "get_current_angle_of_illumination",
        JsonRpcBinding("getCurrentAngleOfIllumination", PATH),
        params=LightIdRequest,
        result=AngleOfIllumination,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_light_synchronize_day_night_mode = Operation(
        INFO,
        "set_light_synchronize_day_night_mode",
        JsonRpcBinding("setLightSynchronizeDayNightMode", PATH),
        params=SetLightSynchronizeDayNightModeRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_light_synchronize_day_night_mode = Operation(
        INFO,
        "get_light_synchronize_day_night_mode",
        JsonRpcBinding("getLightSynchronizeDayNightMode", PATH),
        params=LightIdRequest,
        result=DayNightSynchronization,
        access="operator",
        effect="read",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_valid_ir_wavelengths = Operation(
        INFO,
        "get_valid_ir_wavelengths",
        JsonRpcBinding("getValidIRWavelengths", PATH),
        params=LightIdRequest,
        result=ValidIrWavelengths,
        access="operator",
        effect="read",
        since=ApiVersion(1, 2),
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_ir_wavelength = Operation(
        INFO,
        "set_ir_wavelength",
        JsonRpcBinding("setIRWavelength", PATH),
        params=SetIrWavelengthRequest,
        access="operator",
        effect="write",
        since=ApiVersion(1, 2),
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
            1007: ErrorCode(
                "INVALID_IR_WAVELENGTH_FAULT. Provided infrared wavelength is not valid.", "invalid_argument"
            ),
        },
    )
    get_ir_wavelength = Operation(
        INFO,
        "get_ir_wavelength",
        JsonRpcBinding("getIRWavelength", PATH),
        params=LightIdRequest,
        result=IrWavelength,
        access="operator",
        effect="read",
        since=ApiVersion(1, 2),
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    get_valid_beam_shapes = Operation(
        INFO,
        "get_valid_beam_shapes",
        JsonRpcBinding("getValidBeamShapes", PATH),
        params=LightIdRequest,
        result=ValidBeamShapes,
        access="admin",
        effect="read",
        since=ApiVersion(1, 7),
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )
    set_beam_shape = Operation(
        INFO,
        "set_beam_shape",
        JsonRpcBinding("setBeamShape", PATH),
        params=SetBeamShapeRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 7),
        write="patch",
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
            1010: ErrorCode("INVALID_BEAM_SHAPE_FAULT. Provided beam shape is not valid.", "invalid_argument"),
        },
    )
    get_beam_shape = Operation(
        INFO,
        "get_beam_shape",
        JsonRpcBinding("getBeamShape", PATH),
        params=LightIdRequest,
        result=BeamShape,
        access="admin",
        effect="read",
        since=ApiVersion(1, 7),
        errors={
            1001: ErrorCode("NOT_SUPPORTED_FAULT. Method call not supported by the device.", "unsupported"),
            1002: ErrorCode(
                "INVALID_LIGHT_ID_FAULT. Provided lightID parameter is not valid for the device.", "invalid_argument"
            ),
            1005: ErrorCode(
                "CARD_MALFUNCTIONING_FAULT. Could not find light hardware, could not complete request.", "unavailable"
            ),
            1006: ErrorCode("WRONG_POE_CLASS_FAULT. Wrong POE class, could not complete request.", "unavailable"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class LightControlApi(SyncApi):
    """Light control API (``light-control``, version 1)."""

    INFO = INFO

    def get_service_capabilities(self, *, request_options: RequestOptions | None = None) -> ServiceCapabilities:
        """Lists the capabilities of the light control.

        A CGI method that lists the light service capabilities.

        Access: operator.
        """
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def get_light_information(self, *, request_options: RequestOptions | None = None) -> LightInformationList:
        """Lists the light control information.

        A CGI method that lists the light control information.

        Access: operator.
        """
        return self._run(OPS.get_light_information, None, {}, request_options)

    def activate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Activates the light.

        A CGI method that activates the light.

        Access: operator.
        """
        self._run(OPS.activate_light, None, {"light_id": light_id}, request_options)

    def deactivate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Deactivates the light.

        A CGI method that deactivates the light.

        Access: operator.
        """
        self._run(OPS.deactivate_light, None, {"light_id": light_id}, request_options)

    def enable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Enables the light functionality on the device.

        A CGI method that enables the light functionality.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.enable_light, None, {"light_id": light_id}, request_options)

    def disable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Disables the light functionality on the device.

        A CGI method that disables the light functionality.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.disable_light, None, {"light_id": light_id}, request_options)

    def get_light_status(self, *, light_id: str, request_options: RequestOptions | None = None) -> LightStatus:
        """Retrieves the light status from a given Light ID.

        A CGI method that showcases the light status of a given Light ID.

        Access: operator.
        """
        return self._run(OPS.get_light_status, None, {"light_id": light_id}, request_options)

    def set_automatic_intensity_mode(
        self, *, light_id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enables the automatic light intensity control.

        A CGI method that enables the automatic light intensity control.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_automatic_intensity_mode, None, {"light_id": light_id, "enabled": enabled}, request_options)

    def get_valid_intensity(self, *, light_id: str, request_options: RequestOptions | None = None) -> ValidRanges:
        """Lists the valid light intensity values.

        A CGI method that lists the valid light intensity values.

        Access: operator.
        """
        return self._run(OPS.get_valid_intensity, None, {"light_id": light_id}, request_options)

    def set_manual_intensity(
        self, *, light_id: str, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Manually sets the intensity.

        A CGI method that sets the intensity manually.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_manual_intensity, None, {"light_id": light_id, "intensity": intensity}, request_options)

    def get_manual_intensity(self, *, light_id: str, request_options: RequestOptions | None = None) -> Intensity:
        """Retrieves the intensity from the `setManualIntensity` request.

        A CGI method that gets the intensity that was sent in the `setManualIntensity` request.

        Access: operator.
        """
        return self._run(OPS.get_manual_intensity, None, {"light_id": light_id}, request_options)

    def set_individual_intensity(
        self, *, light_id: str, ledid: int, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Manually sets the intensity for an individual LED.

        A CGI method that manually sets the intensity of an individual LED light.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_individual_intensity,
            None,
            {"light_id": light_id, "ledid": ledid, "intensity": intensity},
            request_options,
        )

    def get_individual_intensity(
        self, *, light_id: str, ledid: int, request_options: RequestOptions | None = None
    ) -> Intensity:
        """Retrieves the intensity from the `setIndividualIntensity` request.

        A CGI method that sends the intensity in the `setIndividualIntensity` request.

        Access: operator.
        """
        return self._run(OPS.get_individual_intensity, None, {"light_id": light_id, "ledid": ledid}, request_options)

    def get_current_intensity(self, *, light_id: str, request_options: RequestOptions | None = None) -> Intensity:
        """Retrieves the current intensity.

        A CGI method that gets the current intensity.

        Access: operator.
        """
        return self._run(OPS.get_current_intensity, None, {"light_id": light_id}, request_options)

    def set_automatic_angle_of_illumination_mode(
        self, *, light_id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Automatically controls the angle of illumination.

        A CGI method that controls the automatic angle of illumination.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_automatic_angle_of_illumination_mode,
            None,
            {"light_id": light_id, "enabled": enabled},
            request_options,
        )

    def get_valid_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> ValidRanges:
        """Lists the valid angle of illumination values.

        A CGI method that lists the valid angle of the illumination values.

        Access: operator.
        """
        return self._run(OPS.get_valid_angle_of_illumination, None, {"light_id": light_id}, request_options)

    def set_manual_angle_of_illumination(
        self, *, light_id: str, angle_of_illumination: int, request_options: RequestOptions | None = None
    ) -> None:
        """Sets the manual angle of illumination.

        A CGI method that sets the manual angle of illumination.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_manual_angle_of_illumination,
            None,
            {"light_id": light_id, "angle_of_illumination": angle_of_illumination},
            request_options,
        )

    def get_manual_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> AngleOfIllumination:
        """Retrieves the angle of illumination from the `setManualAngleOfIllumination` request.

        A CGI method that gets the angle of illumination sent by the `setManualAngleOfIllumination` request.

        Access: operator.
        """
        return self._run(OPS.get_manual_angle_of_illumination, None, {"light_id": light_id}, request_options)

    def get_current_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> AngleOfIllumination:
        """Retrieves the current angle of illumination.

        A CGI method that gets the current angle of illumination.

        Access: operator.
        """
        return self._run(OPS.get_current_angle_of_illumination, None, {"light_id": light_id}, request_options)

    def set_light_synchronize_day_night_mode(
        self, *, light_id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enables automatic synchronization with the day/night mode.

        A CGI method that let you enable or disable the automatic day/night synchronization mode.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_light_synchronize_day_night_mode, None, {"light_id": light_id, "enabled": enabled}, request_options
        )

    def get_light_synchronize_day_night_mode(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> DayNightSynchronization:
        """Checks if the automatic synchronization is enabled with the day/night mode.

        A CGI method that checks if the automatic synchronization with the day/night mode is enabled.

        Access: operator.
        """
        return self._run(OPS.get_light_synchronize_day_night_mode, None, {"light_id": light_id}, request_options)

    def get_valid_ir_wavelengths(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> ValidIrWavelengths:
        """Lists the valid IR wavelengths.

        A CGI method that returns a list containing the infrared wavelengths.

        Access: operator.
        """
        return self._run(OPS.get_valid_ir_wavelengths, None, {"light_id": light_id}, request_options)

    def set_ir_wavelength(
        self, *, light_id: str, ir_wavelength: str, request_options: RequestOptions | None = None
    ) -> None:
        """Sets the IR wavelength.

        A CGI method that sets the infrared wavelength.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_ir_wavelength, None, {"light_id": light_id, "ir_wavelength": ir_wavelength}, request_options)

    def get_ir_wavelength(self, *, light_id: str, request_options: RequestOptions | None = None) -> IrWavelength:
        """Retrieves the currently set IR wavelength.

        A CGI method that returns the current wavelength setting.

        Access: operator.
        """
        return self._run(OPS.get_ir_wavelength, None, {"light_id": light_id}, request_options)

    def get_valid_beam_shapes(self, *, light_id: str, request_options: RequestOptions | None = None) -> ValidBeamShapes:
        """Lists valid beam shapes.

        A CGI method that returns a list of supported beam shapes.

        Access: admin.
        """
        return self._run(OPS.get_valid_beam_shapes, None, {"light_id": light_id}, request_options)

    def set_beam_shape(self, *, light_id: str, beam_shape: str, request_options: RequestOptions | None = None) -> None:
        """Sets the beam shape.

        A CGI method that sets the beam shape.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_beam_shape, None, {"light_id": light_id, "beam_shape": beam_shape}, request_options)

    def get_beam_shape(self, *, light_id: str, request_options: RequestOptions | None = None) -> BeamShape:
        """Gets the currently set beam shape.

        A CGI method that gets the current beam shape setting.

        Access: admin.
        """
        return self._run(OPS.get_beam_shape, None, {"light_id": light_id}, request_options)


class AsyncLightControlApi(AsyncApi):
    """Light control API (``light-control``, version 1)."""

    INFO = INFO

    async def get_service_capabilities(self, *, request_options: RequestOptions | None = None) -> ServiceCapabilities:
        """Lists the capabilities of the light control.

        A CGI method that lists the light service capabilities.

        Access: operator.
        """
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def get_light_information(self, *, request_options: RequestOptions | None = None) -> LightInformationList:
        """Lists the light control information.

        A CGI method that lists the light control information.

        Access: operator.
        """
        return await self._run(OPS.get_light_information, None, {}, request_options)

    async def activate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Activates the light.

        A CGI method that activates the light.

        Access: operator.
        """
        await self._run(OPS.activate_light, None, {"light_id": light_id}, request_options)

    async def deactivate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Deactivates the light.

        A CGI method that deactivates the light.

        Access: operator.
        """
        await self._run(OPS.deactivate_light, None, {"light_id": light_id}, request_options)

    async def enable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Enables the light functionality on the device.

        A CGI method that enables the light functionality.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.enable_light, None, {"light_id": light_id}, request_options)

    async def disable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Disables the light functionality on the device.

        A CGI method that disables the light functionality.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.disable_light, None, {"light_id": light_id}, request_options)

    async def get_light_status(self, *, light_id: str, request_options: RequestOptions | None = None) -> LightStatus:
        """Retrieves the light status from a given Light ID.

        A CGI method that showcases the light status of a given Light ID.

        Access: operator.
        """
        return await self._run(OPS.get_light_status, None, {"light_id": light_id}, request_options)

    async def set_automatic_intensity_mode(
        self, *, light_id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enables the automatic light intensity control.

        A CGI method that enables the automatic light intensity control.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_automatic_intensity_mode, None, {"light_id": light_id, "enabled": enabled}, request_options
        )

    async def get_valid_intensity(self, *, light_id: str, request_options: RequestOptions | None = None) -> ValidRanges:
        """Lists the valid light intensity values.

        A CGI method that lists the valid light intensity values.

        Access: operator.
        """
        return await self._run(OPS.get_valid_intensity, None, {"light_id": light_id}, request_options)

    async def set_manual_intensity(
        self, *, light_id: str, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Manually sets the intensity.

        A CGI method that sets the intensity manually.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_manual_intensity, None, {"light_id": light_id, "intensity": intensity}, request_options)

    async def get_manual_intensity(self, *, light_id: str, request_options: RequestOptions | None = None) -> Intensity:
        """Retrieves the intensity from the `setManualIntensity` request.

        A CGI method that gets the intensity that was sent in the `setManualIntensity` request.

        Access: operator.
        """
        return await self._run(OPS.get_manual_intensity, None, {"light_id": light_id}, request_options)

    async def set_individual_intensity(
        self, *, light_id: str, ledid: int, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Manually sets the intensity for an individual LED.

        A CGI method that manually sets the intensity of an individual LED light.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_individual_intensity,
            None,
            {"light_id": light_id, "ledid": ledid, "intensity": intensity},
            request_options,
        )

    async def get_individual_intensity(
        self, *, light_id: str, ledid: int, request_options: RequestOptions | None = None
    ) -> Intensity:
        """Retrieves the intensity from the `setIndividualIntensity` request.

        A CGI method that sends the intensity in the `setIndividualIntensity` request.

        Access: operator.
        """
        return await self._run(
            OPS.get_individual_intensity, None, {"light_id": light_id, "ledid": ledid}, request_options
        )

    async def get_current_intensity(self, *, light_id: str, request_options: RequestOptions | None = None) -> Intensity:
        """Retrieves the current intensity.

        A CGI method that gets the current intensity.

        Access: operator.
        """
        return await self._run(OPS.get_current_intensity, None, {"light_id": light_id}, request_options)

    async def set_automatic_angle_of_illumination_mode(
        self, *, light_id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Automatically controls the angle of illumination.

        A CGI method that controls the automatic angle of illumination.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_automatic_angle_of_illumination_mode,
            None,
            {"light_id": light_id, "enabled": enabled},
            request_options,
        )

    async def get_valid_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> ValidRanges:
        """Lists the valid angle of illumination values.

        A CGI method that lists the valid angle of the illumination values.

        Access: operator.
        """
        return await self._run(OPS.get_valid_angle_of_illumination, None, {"light_id": light_id}, request_options)

    async def set_manual_angle_of_illumination(
        self, *, light_id: str, angle_of_illumination: int, request_options: RequestOptions | None = None
    ) -> None:
        """Sets the manual angle of illumination.

        A CGI method that sets the manual angle of illumination.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_manual_angle_of_illumination,
            None,
            {"light_id": light_id, "angle_of_illumination": angle_of_illumination},
            request_options,
        )

    async def get_manual_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> AngleOfIllumination:
        """Retrieves the angle of illumination from the `setManualAngleOfIllumination` request.

        A CGI method that gets the angle of illumination sent by the `setManualAngleOfIllumination` request.

        Access: operator.
        """
        return await self._run(OPS.get_manual_angle_of_illumination, None, {"light_id": light_id}, request_options)

    async def get_current_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> AngleOfIllumination:
        """Retrieves the current angle of illumination.

        A CGI method that gets the current angle of illumination.

        Access: operator.
        """
        return await self._run(OPS.get_current_angle_of_illumination, None, {"light_id": light_id}, request_options)

    async def set_light_synchronize_day_night_mode(
        self, *, light_id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enables automatic synchronization with the day/night mode.

        A CGI method that let you enable or disable the automatic day/night synchronization mode.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_light_synchronize_day_night_mode, None, {"light_id": light_id, "enabled": enabled}, request_options
        )

    async def get_light_synchronize_day_night_mode(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> DayNightSynchronization:
        """Checks if the automatic synchronization is enabled with the day/night mode.

        A CGI method that checks if the automatic synchronization with the day/night mode is enabled.

        Access: operator.
        """
        return await self._run(OPS.get_light_synchronize_day_night_mode, None, {"light_id": light_id}, request_options)

    async def get_valid_ir_wavelengths(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> ValidIrWavelengths:
        """Lists the valid IR wavelengths.

        A CGI method that returns a list containing the infrared wavelengths.

        Access: operator.
        """
        return await self._run(OPS.get_valid_ir_wavelengths, None, {"light_id": light_id}, request_options)

    async def set_ir_wavelength(
        self, *, light_id: str, ir_wavelength: str, request_options: RequestOptions | None = None
    ) -> None:
        """Sets the IR wavelength.

        A CGI method that sets the infrared wavelength.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_ir_wavelength, None, {"light_id": light_id, "ir_wavelength": ir_wavelength}, request_options
        )

    async def get_ir_wavelength(self, *, light_id: str, request_options: RequestOptions | None = None) -> IrWavelength:
        """Retrieves the currently set IR wavelength.

        A CGI method that returns the current wavelength setting.

        Access: operator.
        """
        return await self._run(OPS.get_ir_wavelength, None, {"light_id": light_id}, request_options)

    async def get_valid_beam_shapes(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> ValidBeamShapes:
        """Lists valid beam shapes.

        A CGI method that returns a list of supported beam shapes.

        Access: admin.
        """
        return await self._run(OPS.get_valid_beam_shapes, None, {"light_id": light_id}, request_options)

    async def set_beam_shape(
        self, *, light_id: str, beam_shape: str, request_options: RequestOptions | None = None
    ) -> None:
        """Sets the beam shape.

        A CGI method that sets the beam shape.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_beam_shape, None, {"light_id": light_id, "beam_shape": beam_shape}, request_options)

    async def get_beam_shape(self, *, light_id: str, request_options: RequestOptions | None = None) -> BeamShape:
        """Gets the currently set beam shape.

        A CGI method that gets the current beam shape setting.

        Access: admin.
        """
        return await self._run(OPS.get_beam_shape, None, {"light_id": light_id}, request_options)
