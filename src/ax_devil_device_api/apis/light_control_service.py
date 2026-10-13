# GENERATED from specs/apis/network-video/light-control-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Legacy SOAP web service (namespace http://www.axis.com/vapix/ws/light) to control built-in lights; superseded by the Light control API.

Docs: https://developer.axis.com/vapix/network-video/light-control/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ServiceDiscovery
from .._protocols.soap import SoapBinding
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class LightInformation(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    light_type: str = Field(validation_alias="LightType", serialization_alias="LightType")
    """The light type."""
    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """The light is enabled."""
    synchronize_day_night_mode: bool = Field(
        validation_alias="SynchronizeDayNightMode", serialization_alias="SynchronizeDayNightMode"
    )
    """Indicating if the light is synchronized with day night."""
    light_state: bool = Field(validation_alias="LightState", serialization_alias="LightState")
    """Indicating if the light ON or OFF."""
    automatic_intensity_mode: bool = Field(
        validation_alias="AutomaticIntensityMode", serialization_alias="AutomaticIntensityMode"
    )
    """Indicating if the mode of automatic intensity."""
    automatic_angle_of_illumination_mode: bool = Field(
        validation_alias="AutomaticAngleOfIlluminationMode", serialization_alias="AutomaticAngleOfIlluminationMode"
    )
    """Indicating if the mode of automatic angle of illumination."""
    error: bool = Field(validation_alias="Error", serialization_alias="Error")
    """An error has occurred."""
    error_info: str = Field(validation_alias="ErrorInfo", serialization_alias="ErrorInfo")
    """Error description."""


class LightInformationList(Model):
    light_information: list[LightInformation] | None = Field(
        default=None, validation_alias="LightInformation", serialization_alias="LightInformation"
    )
    """Light Information."""


class Capabilities(Model):
    automatic_intensity_support: bool = Field(
        validation_alias="AutomaticIntensitySupport", serialization_alias="AutomaticIntensitySupport"
    )
    """SetAutomaticIntensityMode is supported."""
    manual_intensity_support: bool = Field(
        validation_alias="ManualIntensitySupport", serialization_alias="ManualIntensitySupport"
    )
    """GetManualIntensity and SetManualIntensity are supported."""
    individual_intensity_support: bool = Field(
        validation_alias="IndividualIntensitySupport", serialization_alias="IndividualIntensitySupport"
    )
    """GetIndividualIntensity, SetIndividualIntensity and GetNumberOfLeds are supported."""
    get_current_intensity_support: bool = Field(
        validation_alias="GetCurrentIntensitySupport", serialization_alias="GetCurrentIntensitySupport"
    )
    """GetCurrentIntensity is supported."""
    manual_angle_of_illumination_support: bool = Field(
        validation_alias="ManualAngleOfIlluminationSupport", serialization_alias="ManualAngleOfIlluminationSupport"
    )
    """SetManualAngleOfIllumination is supported."""
    automatic_angle_of_illumination_support: bool = Field(
        validation_alias="AutomaticAngleOfIlluminationSupport",
        serialization_alias="AutomaticAngleOfIlluminationSupport",
    )
    """SetAutomaticAngleOfIlluminationMode is supported."""
    day_night_synchronize_support: bool = Field(
        validation_alias="DayNightSynchronizeSupport", serialization_alias="DayNightSynchronizeSupport"
    )
    """SetLightSynchronizeDayNightMode is supported."""


class IntRange(Model):
    low: int = Field(validation_alias="Low", serialization_alias="Low")
    """The lowest value in the range."""
    high: int = Field(validation_alias="High", serialization_alias="High")
    """The highest value in the range."""


class IntRangeList(Model):
    int_range: list[IntRange] | None = Field(default=None, validation_alias="IntRange", serialization_alias="IntRange")
    """A list of IntRange objects."""


class ActivateLightRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class DeactivateLightRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class EnableLightRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class DisableLightRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetNumberOfLedsRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetNumberOfLedsResult(Model):
    nr_of_leds: int = Field(validation_alias="NrOfLeds", serialization_alias="NrOfLeds")
    """Number of IR leds provided in the request."""


class GetLightStatusRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetLightStatusResult(Model):
    status: bool = Field(validation_alias="Status", serialization_alias="Status")
    """The light is active or inactive."""


class GetLightInformationResult(Model):
    light_info: LightInformationList = Field(validation_alias="LightInfo", serialization_alias="LightInfo")
    """Available light information."""


class GetServiceCapabilitiesResult(Model):
    capabilities: Capabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """Capabilities supported by the Light Control Service."""


class SetAutomaticIntensityModeRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    automatic: bool = Field(validation_alias="Automatic", serialization_alias="Automatic")


class SetManualIntensityRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    intensity: int = Field(validation_alias="Intensity", serialization_alias="Intensity")
    """The intensity to set."""


class SetIndividualIntensityRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    led_id: int = Field(validation_alias="LedID", serialization_alias="LedID")
    """The Led ID"""
    intensity: int = Field(validation_alias="Intensity", serialization_alias="Intensity")
    """The intensity to set."""


class GetManualIntensityRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetManualIntensityResult(Model):
    intensity: int = Field(validation_alias="Intensity", serialization_alias="Intensity")
    """Intensity provided in the request."""


class GetIndividualIntensityRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    led_id: int = Field(validation_alias="LedID", serialization_alias="LedID")
    """The Led ID"""


class GetIndividualIntensityResult(Model):
    intensity: int = Field(validation_alias="Intensity", serialization_alias="Intensity")
    """Intensity provided in the request."""


class GetCurrentIntensityRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetCurrentIntensityResult(Model):
    intensity: int = Field(validation_alias="Intensity", serialization_alias="Intensity")
    """The current intensity."""


class GetValidIntensityRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetValidIntensityResult(Model):
    range_list: IntRangeList = Field(validation_alias="RangeList", serialization_alias="RangeList")
    """Valid intensity values."""


class SetManualAngleOfIlluminationRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    angle_of_illumination: int = Field(
        validation_alias="AngleOfIllumination", serialization_alias="AngleOfIllumination"
    )
    """The angle of illumination."""


class GetManualAngleOfIlluminationRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetManualAngleOfIlluminationResult(Model):
    angle_of_illumination: int = Field(
        validation_alias="AngleOfIllumination", serialization_alias="AngleOfIllumination"
    )
    """Angle of illumination provided in the request."""


class GetCurrentAngleOfIlluminationRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetCurrentAngleOfIlluminationResult(Model):
    angle_of_illumination: int = Field(
        validation_alias="AngleOfIllumination", serialization_alias="AngleOfIllumination"
    )
    """The current angle of illumination."""


class SetAutomaticAngleOfIlluminationModeRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    automatic: bool = Field(validation_alias="Automatic", serialization_alias="Automatic")


class GetValidAngleOfIlluminationRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetValidAngleOfIlluminationResult(Model):
    range_list: IntRangeList = Field(validation_alias="RangeList", serialization_alias="RangeList")
    """Valid angle of illumination values."""


class SetLightSynchronizeDayNightModeRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""
    synchronize: bool = Field(validation_alias="Synchronize", serialization_alias="Synchronize")


class GetLightSynchronizeDayNightModeRequest(Model):
    light_id: str = Field(validation_alias="LightID", serialization_alias="LightID")
    """The Light ID"""


class GetLightSynchronizeDayNightModeResult(Model):
    day_night_sync: bool = Field(validation_alias="DayNightSync", serialization_alias="DayNightSync")
    """Day/night synchronization is enabled."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/services"

INFO = ApiInfo(
    id="light-control-service",
    name="Light control service API",
    family=Family.SOAP,
    discovery=(ServiceDiscovery("http://www.axis.com/vapix/ws/light"),),
    status="deprecated",
    requires_firmware="5.40",
    docs=(
        "https://developer.axis.com/vapix/network-video/light-control/",
        "http://www.axis.com/vapix/ws/LightService.wsdl",
    ),
)


class OPS:
    activate_light = Operation(
        INFO,
        "activate_light",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/ActivateLight",
            "ActivateLight",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=ActivateLightRequest,
        access="admin",
        effect="action",
    )
    deactivate_light = Operation(
        INFO,
        "deactivate_light",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/DeactivateLight",
            "DeactivateLight",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=DeactivateLightRequest,
        access="admin",
        effect="action",
    )
    enable_light = Operation(
        INFO,
        "enable_light",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/EnableLight",
            "EnableLight",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=EnableLightRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    disable_light = Operation(
        INFO,
        "disable_light",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/DisableLight",
            "DisableLight",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=DisableLightRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_number_of_leds = Operation(
        INFO,
        "get_number_of_leds",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetNumberOfLeds",
            "GetNumberOfLeds",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("NrOfLeds", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetNumberOfLedsRequest,
        result=GetNumberOfLedsResult,
        access="admin",
        effect="read",
    )
    get_light_status = Operation(
        INFO,
        "get_light_status",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetLightStatus",
            "GetLightStatus",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("Status", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetLightStatusRequest,
        result=GetLightStatusResult,
        access="admin",
        effect="read",
    )
    get_light_information = Operation(
        INFO,
        "get_light_information",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetLightInformation",
            "GetLightInformation",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "LightInfo",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "LightInformation",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(
                                            XmlField("LightID", source="child"),
                                            XmlField("LightType", source="child"),
                                            XmlField("Enabled", source="child"),
                                            XmlField("SynchronizeDayNightMode", source="child"),
                                            XmlField("LightState", source="child"),
                                            XmlField("AutomaticIntensityMode", source="child"),
                                            XmlField("AutomaticAngleOfIlluminationMode", source="child"),
                                            XmlField("Error", source="child"),
                                            XmlField("ErrorInfo", source="child"),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        result=GetLightInformationResult,
        access="admin",
        effect="read",
    )
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetServiceCapabilities",
            "GetServiceCapabilities",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "Capabilities",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField("AutomaticIntensitySupport", source="child"),
                                XmlField("ManualIntensitySupport", source="child"),
                                XmlField("IndividualIntensitySupport", source="child"),
                                XmlField("GetCurrentIntensitySupport", source="child"),
                                XmlField("ManualAngleOfIlluminationSupport", source="child"),
                                XmlField("AutomaticAngleOfIlluminationSupport", source="child"),
                                XmlField("DayNightSynchronizeSupport", source="child"),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        result=GetServiceCapabilitiesResult,
        access="admin",
        effect="read",
    )
    set_automatic_intensity_mode = Operation(
        INFO,
        "set_automatic_intensity_mode",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/SetAutomaticIntensityMode",
            "SetAutomaticIntensityMode",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=SetAutomaticIntensityModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_manual_intensity = Operation(
        INFO,
        "set_manual_intensity",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/SetManualIntensity",
            "SetManualIntensity",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=SetManualIntensityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_individual_intensity = Operation(
        INFO,
        "set_individual_intensity",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/SetIndividualIntensity",
            "SetIndividualIntensity",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=SetIndividualIntensityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_manual_intensity = Operation(
        INFO,
        "get_manual_intensity",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetManualIntensity",
            "GetManualIntensity",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("Intensity", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetManualIntensityRequest,
        result=GetManualIntensityResult,
        access="admin",
        effect="read",
    )
    get_individual_intensity = Operation(
        INFO,
        "get_individual_intensity",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetIndividualIntensity",
            "GetIndividualIntensity",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("Intensity", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetIndividualIntensityRequest,
        result=GetIndividualIntensityResult,
        access="admin",
        effect="read",
    )
    get_current_intensity = Operation(
        INFO,
        "get_current_intensity",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetCurrentIntensity",
            "GetCurrentIntensity",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("Intensity", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetCurrentIntensityRequest,
        result=GetCurrentIntensityResult,
        access="admin",
        effect="read",
    )
    get_valid_intensity = Operation(
        INFO,
        "get_valid_intensity",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetValidIntensity",
            "GetValidIntensity",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "RangeList",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "IntRange",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(XmlField("Low", source="child"), XmlField("High", source="child"))
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetValidIntensityRequest,
        result=GetValidIntensityResult,
        access="admin",
        effect="read",
    )
    set_manual_angle_of_illumination = Operation(
        INFO,
        "set_manual_angle_of_illumination",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/SetManualAngleOfIllumination",
            "SetManualAngleOfIllumination",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=SetManualAngleOfIlluminationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_manual_angle_of_illumination = Operation(
        INFO,
        "get_manual_angle_of_illumination",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetManualAngleOfIllumination",
            "GetManualAngleOfIllumination",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("AngleOfIllumination", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetManualAngleOfIlluminationRequest,
        result=GetManualAngleOfIlluminationResult,
        access="admin",
        effect="read",
    )
    get_current_angle_of_illumination = Operation(
        INFO,
        "get_current_angle_of_illumination",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetCurrentAngleOfIllumination",
            "GetCurrentAngleOfIllumination",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("AngleOfIllumination", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetCurrentAngleOfIlluminationRequest,
        result=GetCurrentAngleOfIlluminationResult,
        access="admin",
        effect="read",
    )
    set_automatic_angle_of_illumination_mode = Operation(
        INFO,
        "set_automatic_angle_of_illumination_mode",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/SetAutomaticAngleOfIlluminationMode",
            "SetAutomaticAngleOfIlluminationMode",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=SetAutomaticAngleOfIlluminationModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_valid_angle_of_illumination = Operation(
        INFO,
        "get_valid_angle_of_illumination",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetValidAngleOfIllumination",
            "GetValidAngleOfIllumination",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "RangeList",
                        source="path",
                        nested=XmlMap(
                            fields=(
                                XmlField(
                                    "IntRange",
                                    source="path",
                                    many=True,
                                    nested=XmlMap(
                                        fields=(XmlField("Low", source="child"), XmlField("High", source="child"))
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetValidAngleOfIlluminationRequest,
        result=GetValidAngleOfIlluminationResult,
        access="admin",
        effect="read",
    )
    set_light_synchronize_day_night_mode = Operation(
        INFO,
        "set_light_synchronize_day_night_mode",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/SetLightSynchronizeDayNightMode",
            "SetLightSynchronizeDayNightMode",
            "http://www.axis.com/vapix/ws/light",
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=SetLightSynchronizeDayNightModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_light_synchronize_day_night_mode = Operation(
        INFO,
        "get_light_synchronize_day_night_mode",
        SoapBinding(
            "http://www.axis.com/vapix/ws/light/GetLightSynchronizeDayNightMode",
            "GetLightSynchronizeDayNightMode",
            "http://www.axis.com/vapix/ws/light",
            reply=XmlMap(fields=(XmlField("DayNightSync", source="child"),)),
            namespaces=(("ali", "http://www.axis.com/vapix/ws/light"),),
        ),
        params=GetLightSynchronizeDayNightModeRequest,
        result=GetLightSynchronizeDayNightModeResult,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class LightControlServiceApi(SyncApi):
    """Light control service API (``light-control-service``)."""

    INFO = INFO

    def activate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Activate the light. Access: admin."""
        self._run(OPS.activate_light, None, {"light_id": light_id}, request_options)

    def deactivate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Deativate the light. Access: admin."""
        self._run(OPS.deactivate_light, None, {"light_id": light_id}, request_options)

    def enable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Enable the light functionality. Changes only the fields given. Access: admin."""
        self._run(OPS.enable_light, None, {"light_id": light_id}, request_options)

    def disable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Disable the light functionality. Changes only the fields given. Access: admin."""
        self._run(OPS.disable_light, None, {"light_id": light_id}, request_options)

    def get_number_of_leds(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetNumberOfLedsResult:
        """Get number of IR leds. Access: admin."""
        return self._run(OPS.get_number_of_leds, None, {"light_id": light_id}, request_options)

    def get_light_status(self, *, light_id: str, request_options: RequestOptions | None = None) -> GetLightStatusResult:
        """Get the light status of a given Light ID. Access: admin."""
        return self._run(OPS.get_light_status, None, {"light_id": light_id}, request_options)

    def get_light_information(self, *, request_options: RequestOptions | None = None) -> GetLightInformationResult:
        """List light control information. Access: admin."""
        return self._run(OPS.get_light_information, None, {}, request_options)

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """List the light service capablilities. Access: admin."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def set_automatic_intensity_mode(
        self, *, light_id: str, automatic: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable automatic light intensity control. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_automatic_intensity_mode, None, {"light_id": light_id, "automatic": automatic}, request_options
        )

    def set_manual_intensity(
        self, *, light_id: str, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the intensity manually. Changes only the fields given. Access: admin."""
        self._run(OPS.set_manual_intensity, None, {"light_id": light_id, "intensity": intensity}, request_options)

    def set_individual_intensity(
        self, *, light_id: str, led_id: int, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the intensity individually. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_individual_intensity,
            None,
            {"light_id": light_id, "led_id": led_id, "intensity": intensity},
            request_options,
        )

    def get_manual_intensity(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetManualIntensityResult:
        """Get the intensity sent in the SetManualIntensity request. Access: admin."""
        return self._run(OPS.get_manual_intensity, None, {"light_id": light_id}, request_options)

    def get_individual_intensity(
        self, *, light_id: str, led_id: int, request_options: RequestOptions | None = None
    ) -> GetIndividualIntensityResult:
        """Get the intensity set in the SetIndividualIntensity request. Access: admin."""
        return self._run(OPS.get_individual_intensity, None, {"light_id": light_id, "led_id": led_id}, request_options)

    def get_current_intensity(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetCurrentIntensityResult:
        """Get the current intensity. Access: admin."""
        return self._run(OPS.get_current_intensity, None, {"light_id": light_id}, request_options)

    def get_valid_intensity(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetValidIntensityResult:
        """List valid light intensity values. Access: admin."""
        return self._run(OPS.get_valid_intensity, None, {"light_id": light_id}, request_options)

    def set_manual_angle_of_illumination(
        self, *, light_id: str, angle_of_illumination: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the angle of illumination manually. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_manual_angle_of_illumination,
            None,
            {"light_id": light_id, "angle_of_illumination": angle_of_illumination},
            request_options,
        )

    def get_manual_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetManualAngleOfIlluminationResult:
        """Get the angle of illumination sent in the SetManualAngleOfIllumination request.

        Access: admin.
        """
        return self._run(OPS.get_manual_angle_of_illumination, None, {"light_id": light_id}, request_options)

    def get_current_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetCurrentAngleOfIlluminationResult:
        """Get the current angle of illumination. Access: admin."""
        return self._run(OPS.get_current_angle_of_illumination, None, {"light_id": light_id}, request_options)

    def set_automatic_angle_of_illumination_mode(
        self, *, light_id: str, automatic: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Control the angle of illumination automatically.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_automatic_angle_of_illumination_mode,
            None,
            {"light_id": light_id, "automatic": automatic},
            request_options,
        )

    def get_valid_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetValidAngleOfIlluminationResult:
        """List valid angle of illumination values. Access: admin."""
        return self._run(OPS.get_valid_angle_of_illumination, None, {"light_id": light_id}, request_options)

    def set_light_synchronize_day_night_mode(
        self, *, light_id: str, synchronize: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable automatic synchronization with day/night mode.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_light_synchronize_day_night_mode,
            None,
            {"light_id": light_id, "synchronize": synchronize},
            request_options,
        )

    def get_light_synchronize_day_night_mode(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetLightSynchronizeDayNightModeResult:
        """Check if automatic synchronization with day/night mode is enabled. Access: admin."""
        return self._run(OPS.get_light_synchronize_day_night_mode, None, {"light_id": light_id}, request_options)


class AsyncLightControlServiceApi(AsyncApi):
    """Light control service API (``light-control-service``)."""

    INFO = INFO

    async def activate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Activate the light. Access: admin."""
        await self._run(OPS.activate_light, None, {"light_id": light_id}, request_options)

    async def deactivate_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Deativate the light. Access: admin."""
        await self._run(OPS.deactivate_light, None, {"light_id": light_id}, request_options)

    async def enable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Enable the light functionality. Changes only the fields given. Access: admin."""
        await self._run(OPS.enable_light, None, {"light_id": light_id}, request_options)

    async def disable_light(self, *, light_id: str, request_options: RequestOptions | None = None) -> None:
        """Disable the light functionality. Changes only the fields given. Access: admin."""
        await self._run(OPS.disable_light, None, {"light_id": light_id}, request_options)

    async def get_number_of_leds(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetNumberOfLedsResult:
        """Get number of IR leds. Access: admin."""
        return await self._run(OPS.get_number_of_leds, None, {"light_id": light_id}, request_options)

    async def get_light_status(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetLightStatusResult:
        """Get the light status of a given Light ID. Access: admin."""
        return await self._run(OPS.get_light_status, None, {"light_id": light_id}, request_options)

    async def get_light_information(
        self, *, request_options: RequestOptions | None = None
    ) -> GetLightInformationResult:
        """List light control information. Access: admin."""
        return await self._run(OPS.get_light_information, None, {}, request_options)

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """List the light service capablilities. Access: admin."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def set_automatic_intensity_mode(
        self, *, light_id: str, automatic: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable automatic light intensity control. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_automatic_intensity_mode, None, {"light_id": light_id, "automatic": automatic}, request_options
        )

    async def set_manual_intensity(
        self, *, light_id: str, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the intensity manually. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_manual_intensity, None, {"light_id": light_id, "intensity": intensity}, request_options)

    async def set_individual_intensity(
        self, *, light_id: str, led_id: int, intensity: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the intensity individually. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_individual_intensity,
            None,
            {"light_id": light_id, "led_id": led_id, "intensity": intensity},
            request_options,
        )

    async def get_manual_intensity(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetManualIntensityResult:
        """Get the intensity sent in the SetManualIntensity request. Access: admin."""
        return await self._run(OPS.get_manual_intensity, None, {"light_id": light_id}, request_options)

    async def get_individual_intensity(
        self, *, light_id: str, led_id: int, request_options: RequestOptions | None = None
    ) -> GetIndividualIntensityResult:
        """Get the intensity set in the SetIndividualIntensity request. Access: admin."""
        return await self._run(
            OPS.get_individual_intensity, None, {"light_id": light_id, "led_id": led_id}, request_options
        )

    async def get_current_intensity(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetCurrentIntensityResult:
        """Get the current intensity. Access: admin."""
        return await self._run(OPS.get_current_intensity, None, {"light_id": light_id}, request_options)

    async def get_valid_intensity(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetValidIntensityResult:
        """List valid light intensity values. Access: admin."""
        return await self._run(OPS.get_valid_intensity, None, {"light_id": light_id}, request_options)

    async def set_manual_angle_of_illumination(
        self, *, light_id: str, angle_of_illumination: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the angle of illumination manually. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_manual_angle_of_illumination,
            None,
            {"light_id": light_id, "angle_of_illumination": angle_of_illumination},
            request_options,
        )

    async def get_manual_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetManualAngleOfIlluminationResult:
        """Get the angle of illumination sent in the SetManualAngleOfIllumination request.

        Access: admin.
        """
        return await self._run(OPS.get_manual_angle_of_illumination, None, {"light_id": light_id}, request_options)

    async def get_current_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetCurrentAngleOfIlluminationResult:
        """Get the current angle of illumination. Access: admin."""
        return await self._run(OPS.get_current_angle_of_illumination, None, {"light_id": light_id}, request_options)

    async def set_automatic_angle_of_illumination_mode(
        self, *, light_id: str, automatic: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Control the angle of illumination automatically.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_automatic_angle_of_illumination_mode,
            None,
            {"light_id": light_id, "automatic": automatic},
            request_options,
        )

    async def get_valid_angle_of_illumination(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetValidAngleOfIlluminationResult:
        """List valid angle of illumination values. Access: admin."""
        return await self._run(OPS.get_valid_angle_of_illumination, None, {"light_id": light_id}, request_options)

    async def set_light_synchronize_day_night_mode(
        self, *, light_id: str, synchronize: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable automatic synchronization with day/night mode.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_light_synchronize_day_night_mode,
            None,
            {"light_id": light_id, "synchronize": synchronize},
            request_options,
        )

    async def get_light_synchronize_day_night_mode(
        self, *, light_id: str, request_options: RequestOptions | None = None
    ) -> GetLightSynchronizeDayNightModeResult:
        """Check if automatic synchronization with day/night mode is enabled. Access: admin."""
        return await self._run(OPS.get_light_synchronize_day_night_mode, None, {"light_id": light_id}, request_options)
