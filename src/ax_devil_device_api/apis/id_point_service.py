# GENERATED from specs/apis/physical-access-control/idpoint-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The IdPoint service is used for management of IdPoints.

Docs: https://developer.axis.com/vapix/physical-access-control/idpoint-service/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ServiceDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ReferenceToken = str


class NameValue(Model):
    """A name and value pair."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")


class IdData(Model):
    """One identification value, for example a card number or a PIN."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the field, for example `Card`, `PIN` or `CardNr`."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """The value."""


class ServiceCapabilities(Model):
    """Optional functionality of the IdPoint service. Static during device operation."""

    set_id_point: bool | None = Field(default=None, validation_alias="SetIdPoint", serialization_alias="SetIdPoint")
    """True if SetIdPoint is supported."""


class IdPointCapabilities(Model):
    """Optional functionality of one IdPoint. It can change during device operation, for example if hardware settings change."""

    configurable: bool | None = Field(default=None, validation_alias="Configurable", serialization_alias="Configurable")
    """True if the IdPoint settings can be modified."""
    support_card: bool | None = Field(default=None, validation_alias="SupportCard", serialization_alias="SupportCard")
    """True if the IdPoint can read card data."""
    support_pin: bool | None = Field(default=None, validation_alias="SupportPIN", serialization_alias="SupportPIN")
    """True if the IdPoint supports PIN or keypad entry."""
    support_rex: bool | None = Field(default=None, validation_alias="SupportREX", serialization_alias="SupportREX")
    """True if the IdPoint has a REX input."""
    support_biometric: bool | None = Field(
        default=None, validation_alias="SupportBiometric", serialization_alias="SupportBiometric"
    )
    """True if the IdPoint has some kind of biometric input."""
    supported_message_types: list[str] | None = Field(
        default=None, validation_alias="SupportedMessageTypes", serialization_alias="SupportedMessageTypes"
    )
    """Supported mime types of the Message in feedback_message, for example `text/plain`. May be empty."""
    supported_graphics_types: list[str] | None = Field(
        default=None, validation_alias="SupportedGraphicsTypes", serialization_alias="SupportedGraphicsTypes"
    )
    """Supported mime types of the Graphics in feedback_message, for example `image/jpeg`. May be empty."""
    supported_audio_types: list[str] | None = Field(
        default=None, validation_alias="SupportedAudioTypes", serialization_alias="SupportedAudioTypes"
    )
    """Supported audio formats of the Audio in feedback_message, for example `audio/basic`."""
    additional_capabilities: Any | None = Field(
        default=None, validation_alias="AdditionalCapabilities", serialization_alias="AdditionalCapabilities"
    )
    """General list of supported features; not specified in the docs."""


class IdPointInfo(Model):
    """An IdPoint as a physical object, with its capabilities."""

    token: ReferenceToken | None = None
    """A service-unique identifier of the IdPoint. The docs call the field `Token`, the examples elsewhere use `token`."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the IdPoint."""
    location: str = Field(validation_alias="Location", serialization_alias="Location")
    """Text description of the location."""
    area: str = Field(validation_alias="Area", serialization_alias="Area")
    """The area the IdPoint is in."""
    capabilities: IdPointCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities of the IdPoint."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the IdPoint."""


class IdPoint(Model):
    """The full configuration of an IdPoint, as returned by the device."""

    token: ReferenceToken
    """A service-unique identifier of the IdPoint."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the IdPoint."""
    location: str | None = Field(default=None, validation_alias="Location", serialization_alias="Location")
    """Text description of the location."""
    area: str | None = Field(default=None, validation_alias="Area", serialization_alias="Area")
    """The area the IdPoint is in."""
    timeout: str | None = Field(default=None, validation_alias="Timeout", serialization_alias="Timeout")
    """Timeout between user interactions, as an ISO 8601 duration such as `PT10S`."""
    heartbeat_interval: str | None = Field(
        default=None, validation_alias="HeartbeatInterval", serialization_alias="HeartbeatInterval"
    )
    """Time between heartbeat events, as an ISO 8601 duration such as `PT10M`. A time of 0 means no heartbeat events."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the IdPoint."""
    action: str | None = Field(default=None, validation_alias="Action", serialization_alias="Action")
    """The default action of the IdPoint, for example `Access` (assumed if not set) or `AccessDoorWithoutUnlock`."""
    min_pin_size: int | None = Field(default=None, validation_alias="MinPINSize", serialization_alias="MinPINSize")
    """Minimum number of characters in a PIN."""
    max_pin_size: int | None = Field(default=None, validation_alias="MaxPINSize", serialization_alias="MaxPINSize")
    """Maximum number of characters in a PIN."""
    end_of_pin: str | None = Field(default=None, validation_alias="EndOfPIN", serialization_alias="EndOfPIN")
    """Character or string that ends a PIN and triggers sending it."""


class IdPointInput(Model):
    """An IdPoint to add or update."""

    token: ReferenceToken | None = None
    """Token of the IdPoint. If empty or absent the device allocates one; if it exists the IdPoint is updated. Use the same token for the IdPointConfiguration."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the IdPoint."""
    location: str | None = Field(default=None, validation_alias="Location", serialization_alias="Location")
    """Text description of the location."""
    area: str | None = Field(default=None, validation_alias="Area", serialization_alias="Area")
    """The area the IdPoint is in."""
    timeout: str | None = Field(default=None, validation_alias="Timeout", serialization_alias="Timeout")
    """Timeout between user interactions, as an ISO 8601 duration such as `PT10S`."""
    heartbeat_interval: str | None = Field(
        default=None, validation_alias="HeartbeatInterval", serialization_alias="HeartbeatInterval"
    )
    """Time between heartbeat events, as an ISO 8601 duration such as `PT10M`. A time of 0 means no heartbeat events."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the IdPoint."""
    action: str | None = Field(default=None, validation_alias="Action", serialization_alias="Action")
    """The default action of the IdPoint, for example `Access` (assumed if not set) or `AccessDoorWithoutUnlock`."""
    min_pin_size: int | None = Field(default=None, validation_alias="MinPINSize", serialization_alias="MinPINSize")
    """Minimum number of characters in a PIN."""
    max_pin_size: int | None = Field(default=None, validation_alias="MaxPINSize", serialization_alias="MaxPINSize")
    """Maximum number of characters in a PIN."""
    end_of_pin: str | None = Field(default=None, validation_alias="EndOfPIN", serialization_alias="EndOfPIN")
    """Character or string that ends a PIN and triggers sending it."""


IdPointFeedback = Literal[
    "Other",
    "Idle",
    "DoorLocked",
    "DoorUnlocked",
    "DoorOpenTooLong",
    "DoorPreAlarmWarning",
    "RequirePIN",
    "RequireCard",
    "Processing",
    "InvalidCredential",
    "AccessGranted",
    "AccessDenied",
    "Ok",
    "Fault",
    "Warning",
    "Alarm",
    "Custom",
]


class IdPointConfiguration(Model):
    """The device and hardware configuration of an IdPoint, bound to the IdPoint by the same token. Without a value for every parameter in Configuration, the supplied parameters replace those of an existing configuration, and a new configuration gets the first value of each parameter's list of valid values. The parameters are named like `IdPoint.Reader.Type` (`None`, `Wiegand`, `RS-485FD`, `RS-485HD`, `TCPIP`), `IdPoint.RS-485HD.Protocol` (`None`, `AADP`, `OSDP`, `HADP`), `IdPoint.LED.Type`, `IdPoint.Beeper.Type`, `IdPoint.Tampering.Type`, `IdPoint.REX.Type`, `IdPoint.Keypress.Types`, `IdPoint.Hardware.Address`, `IdPoint.Hardware.DetectionMode`, `IdPoint.SecureChannel.KeyToken` and `IdPoint.SecureChannel.KeyType`; get_id_point_configuration_info lists them."""

    token: ReferenceToken | None = None
    """IdPoint token to use for set, remove and usage."""
    device_uuid: str | None = Field(default=None, validation_alias="DeviceUUID", serialization_alias="DeviceUUID")
    """The device the IdPoint is on. When empty in a set request it is filled in with the UUID of the device that receives the request."""
    id_data_configuration: list[ReferenceToken] | None = Field(
        default=None, validation_alias="IdDataConfiguration", serialization_alias="IdDataConfiguration"
    )
    """Tokens of the IdDataConfigurations to use."""
    configuration: list[NameValue] | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )
    """The hardware configuration parameters of the IdPoint."""


class ConfigurationInfo(Model):
    """A configuration setting and its description."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the setting."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """Value of the setting."""
    enums: list[str] | None = Field(default=None, validation_alias="Enums", serialization_alias="Enums")
    """Suggested or allowed values."""
    type: str | None = Field(default=None, validation_alias="Type", serialization_alias="Type")
    """Type of the setting, for example `xs:string`, `xs:boolean` or `xs:int`."""
    depend_on_name: str | None = Field(
        default=None, validation_alias="DependOnName", serialization_alias="DependOnName"
    )
    """Name of the setting this one depends on."""
    depend_on_value: str | None = Field(
        default=None, validation_alias="DependOnValue", serialization_alias="DependOnValue"
    )
    """Value of the setting this one depends on."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the setting."""


IdDataEncoding = Literal[
    "Other",
    "BinLE2hex",
    "BinBE2hex",
    "Bin2Base64",
    "Bin2String",
    "BinLEBCD2String",
    "BinBEBCD2String",
    "BinLE2Int",
    "BinBE2Int",
    "BinLEIBO2hex",
    "BinBEIBO2hex",
    "BinIBO2Base64",
    "BinIBO2String",
    "BinLEIBO2Int",
    "BinBEIBO2Int",
]


class IdDataFieldMap(Model):
    """How binary card data maps to one IdData name and value."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the IdData field, for example `CardNr` or `FacilityCode`."""
    map: str | None = Field(default=None, validation_alias="Map", serialization_alias="Map")
    """Location of the field in the card data: bit `N`, bits `M-N`, constant binary `bBBB`, constant hex `xHHH`, joined by commas. Bit 1 is the first bit received, for example over Wiegand."""
    encoding: IdDataEncoding | None = Field(default=None, validation_alias="Encoding", serialization_alias="Encoding")
    """How the resulting bits are encoded to a value."""


class IdDataConfiguration(Model):
    """How binary data from a card reader or keypad maps to the IdData of Request events. The complete raw data is always sent as `Card` and its length as `BitCount`."""

    token: ReferenceToken | None = None
    """Id of the configuration. If empty in a set request the device allocates one."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the configuration."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the configuration."""
    input_bitlength: int | None = Field(
        default=None, validation_alias="InputBitlength", serialization_alias="InputBitlength"
    )
    """The number of bits the input must have to use this configuration."""
    id_data_field_map: list[IdDataFieldMap] | None = Field(
        default=None, validation_alias="IdDataFieldMap", serialization_alias="IdDataFieldMap"
    )
    """The field maps."""


SecureChannel = Literal["Unknown", "ConnectionLost", "ConnectionEstablished", "NotSupported", "NoKey"]


class SecureChannelStatus(Model):
    """Status of the secure channel of an IdPoint."""

    active: bool | None = Field(default=None, validation_alias="Active", serialization_alias="Active")
    """True if there is an active secure channel on the IdPoint."""
    reason: SecureChannel | None = Field(default=None, validation_alias="Reason", serialization_alias="Reason")
    """Status of the secure channel; more information when Active is false."""


IdPointWhiteList = Any


class Activity(Model):
    """One activity at a remote IdPoint."""

    type: Literal["REX", "Card", "PIN"] = Field(validation_alias="Type", serialization_alias="Type")
    """The kind of activity."""
    params: list[NameValue] | None = Field(default=None, validation_alias="Params", serialization_alias="Params")
    """Custom fields of the Request event. Mandatory for `Card` and `PIN` (for `PIN` a param named `PIN` is mandatory) and not allowed for `REX`."""


class ListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If absent, or higher than the device supports, the device decides."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this reference. If absent, start from the beginning."""


class TokensRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the items."""


class TokenRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the IdPoint."""


class TokenResult(Model):
    token: ReferenceToken | list[ReferenceToken] | None = Field(
        default=None, validation_alias="Token", serialization_alias="Token"
    )
    """Tokens of the added or updated items. The docs' examples show a single token as a plain string and the message tables a list."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities of the service."""


class IdPointInfoList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    id_point_info: list[IdPointInfo] | None = Field(
        default=None, validation_alias="IdPointInfo", serialization_alias="IdPointInfo"
    )
    """The IdPoints."""


class IdPointInfos(Model):
    id_point_info: list[IdPointInfo] | None = Field(
        default=None, validation_alias="IdPointInfo", serialization_alias="IdPointInfo"
    )


class IdPoints(Model):
    id_point: list[IdPoint] | None = Field(default=None, validation_alias="IdPoint", serialization_alias="IdPoint")


class SetIdPointRequest(Model):
    id_point: list[IdPointInput] = Field(validation_alias="IdPoint", serialization_alias="IdPoint", min_length=1)
    """The IdPoints to add or update."""


class GetIdPointCapabilitiesResult(Model):
    id_point_capabilities: IdPointCapabilities = Field(
        validation_alias="IdPointCapabilities", serialization_alias="IdPointCapabilities"
    )
    """The capabilities of the IdPoint."""


class FeedbackMessageRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the IdPoint to control."""
    profile: IdPointFeedback = Field(validation_alias="Profile", serialization_alias="Profile")
    """The feedback profile to use."""
    other_profile: str | None = Field(default=None, validation_alias="OtherProfile", serialization_alias="OtherProfile")
    """The extended profile information when Profile is `Other`."""
    message: str | None = Field(default=None, validation_alias="Message", serialization_alias="Message")
    """Optional textual feedback message."""
    graphics: Any | None = Field(default=None, validation_alias="Graphics", serialization_alias="Graphics")
    """Optional graphical message (tt:BinaryData, not defined in the docs)."""
    audio: Any | None = Field(default=None, validation_alias="Audio", serialization_alias="Audio")
    """Optional audio message (tt:BinaryData, not defined in the docs)."""


class IdPointConfigurationList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    id_point_configuration: list[IdPointConfiguration] | None = Field(
        default=None, validation_alias="IdPointConfiguration", serialization_alias="IdPointConfiguration"
    )


class IdPointConfigurations(Model):
    id_point_configuration: list[IdPointConfiguration] | None = Field(
        default=None, validation_alias="IdPointConfiguration", serialization_alias="IdPointConfiguration"
    )


class SetIdPointConfigurationRequest(Model):
    id_point_configuration: list[IdPointConfiguration] = Field(
        validation_alias="IdPointConfiguration", serialization_alias="IdPointConfiguration", min_length=1
    )
    """The new versions of the configurations. The token should normally refer to an existing IdPoint."""


class ConfigurationInfoResult(Model):
    configuration_info: list[ConfigurationInfo] | None = Field(
        default=None, validation_alias="ConfigurationInfo", serialization_alias="ConfigurationInfo"
    )
    """The configuration parameters of the IdPoint."""


class LastCredentialResult(Model):
    id_data: list[IdData] | None = Field(default=None, validation_alias="IdData", serialization_alias="IdData")
    """The last credential, parsed with the IdDataConfiguration. `Card` and `BitCount` are always included."""


class IdDataConfigurations(Model):
    id_data_configuration: list[IdDataConfiguration] | None = Field(
        default=None, validation_alias="IdDataConfiguration", serialization_alias="IdDataConfiguration"
    )


class SetIdDataConfigurationRequest(Model):
    id_data_configuration: list[IdDataConfiguration] = Field(
        validation_alias="IdDataConfiguration", serialization_alias="IdDataConfiguration", min_length=1
    )
    """The IdDataConfigurations to add or modify."""


class FeedbackProfileResult(Model):
    profile: IdPointFeedback = Field(validation_alias="Profile", serialization_alias="Profile")
    """The current feedback profile."""


class SecureChannelStatusResult(Model):
    secure_channel_status: SecureChannelStatus = Field(
        validation_alias="SecureChannelStatus", serialization_alias="SecureChannelStatus"
    )
    """Status of the secure channel."""


class IdPointWhiteListResult(Model):
    id_point_white_list: list[IdPointWhiteList] | None = Field(
        default=None, validation_alias="IdPointWhiteList", serialization_alias="IdPointWhiteList"
    )


class IdPointWhiteListList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    id_point_white_list: list[IdPointWhiteList] | None = Field(
        default=None, validation_alias="IdPointWhiteList", serialization_alias="IdPointWhiteList"
    )


class IndicateRemoteActivitiesRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the IdPoint to indicate activities for."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description added to the events that are sent."""
    activities: list[Activity] = Field(validation_alias="Activities", serialization_alias="Activities", min_length=1)
    """The activities."""
    attributes: list[NameValue] | None = Field(
        default=None, validation_alias="Attributes", serialization_alias="Attributes"
    )
    """Reserved for future extension; not in use."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/idpoint"

INFO = ApiInfo(
    id="idpoint-service",
    name="IdPoint service",
    family=Family.SERVICE_JSON,
    discovery=(ServiceDiscovery("http://www.axis.com/vapix/ws/IdPoint"),),
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/idpoint-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/event-logger-service/",
        "https://developer.axis.com/vapix/physical-access-control/access-control-service/",
        "https://developer.axis.com/vapix/physical-access-control/door-control-service/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
        "https://developer.axis.com/vapix/physical-access-control/system-integration-examples/",
    ),
    errors={"ter:InvalidArgs": ErrorCode("Invalid argument", "invalid_argument")},
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "axtid:GetServiceCapabilities", auth="if_challenged"),
        result=GetServiceCapabilitiesResult,
        access="anonymous",
        effect="read",
    )
    get_id_point_info_list = Operation(
        INFO,
        "get_id_point_info_list",
        ServiceJsonBinding(PATH, "axtid:GetIdPointInfoList"),
        params=ListRequest,
        result=IdPointInfoList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning", "invalid_argument"
            )
        },
    )
    get_id_point_info = Operation(
        INFO,
        "get_id_point_info",
        ServiceJsonBinding(PATH, "axtid:GetIdPointInfo"),
        params=TokensRequest,
        result=IdPointInfos,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability", "invalid_argument"
            )
        },
    )
    get_id_point_list = Operation(
        INFO,
        "get_id_point_list",
        ServiceJsonBinding(PATH, "axtid:GetIdPointList"),
        params=ListRequest,
        result=IdPointInfoList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning", "invalid_argument"
            )
        },
    )
    get_id_point = Operation(
        INFO,
        "get_id_point",
        ServiceJsonBinding(PATH, "axtid:GetIdPoint"),
        params=TokensRequest,
        result=IdPoints,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability", "invalid_argument"
            )
        },
    )
    set_id_point = Operation(
        INFO,
        "set_id_point",
        ServiceJsonBinding(PATH, "axtid:SetIdPoint"),
        params=SetIdPointRequest,
        result=TokenResult,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:NotSupported": ErrorCode("Not allowed to create or modify the IdPoint", "unsupported")},
    )
    remove_id_point = Operation(
        INFO,
        "remove_id_point",
        ServiceJsonBinding(PATH, "axtid:RemoveIdPoint"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={
            "ter:NotSupported": ErrorCode("Not allowed to remove the IdPoint", "unsupported"),
            "ter:NotFound": ErrorCode("IdPoint not found", "not_found"),
        },
    )
    get_id_point_capabilities = Operation(
        INFO,
        "get_id_point_capabilities",
        ServiceJsonBinding(PATH, "axtid:GetIdPointCapabilities"),
        params=TokenRequest,
        result=GetIdPointCapabilitiesResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("IdPoint not found", "not_found")},
    )
    feedback_message = Operation(
        INFO,
        "feedback_message",
        ServiceJsonBinding(PATH, "axtid:FeedbackMessage"),
        params=FeedbackMessageRequest,
        access="admin",
        effect="action",
        errors={"ter:NotFound": ErrorCode("The specified token is not found", "not_found")},
    )
    get_id_point_configuration_list = Operation(
        INFO,
        "get_id_point_configuration_list",
        ServiceJsonBinding(PATH, "axtid:GetIdPointConfigurationList"),
        params=ListRequest,
        result=IdPointConfigurationList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning", "invalid_argument"
            )
        },
    )
    get_id_point_configuration = Operation(
        INFO,
        "get_id_point_configuration",
        ServiceJsonBinding(PATH, "axtid:GetIdPointConfiguration"),
        params=TokensRequest,
        result=IdPointConfigurations,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability", "invalid_argument"
            )
        },
    )
    set_id_point_configuration = Operation(
        INFO,
        "set_id_point_configuration",
        ServiceJsonBinding(PATH, "axtid:SetIdPointConfiguration"),
        params=SetIdPointConfigurationRequest,
        result=TokenResult,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:InvalidIdPointConfigurationFault": ErrorCode(
                "The IdPoint configuration is invalid", "invalid_argument"
            )
        },
    )
    remove_id_point_configuration = Operation(
        INFO,
        "remove_id_point_configuration",
        ServiceJsonBinding(PATH, "axtid:RemoveIdPointConfiguration"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("IdPointConfiguration not found", "not_found")},
    )
    get_id_point_configuration_info = Operation(
        INFO,
        "get_id_point_configuration_info",
        ServiceJsonBinding(PATH, "axtid:GetIdPointConfigurationInfo"),
        params=TokenRequest,
        result=ConfigurationInfoResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("IdPoint not found", "not_found")},
    )
    get_last_credential = Operation(
        INFO,
        "get_last_credential",
        ServiceJsonBinding(PATH, "axtid:GetLastCredential"),
        params=TokenRequest,
        result=LastCredentialResult,
        access="admin",
        effect="read",
        errors={"ter:ConfigurationNotFound": ErrorCode("Configuration not found", "not_found")},
    )
    get_id_data_configuration_list = Operation(
        INFO,
        "get_id_data_configuration_list",
        ServiceJsonBinding(PATH, "axtid:GetIdDataConfigurationList"),
        params=ListRequest,
        result=IdPointConfigurationList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning", "invalid_argument"
            )
        },
    )
    get_id_data_configuration = Operation(
        INFO,
        "get_id_data_configuration",
        ServiceJsonBinding(PATH, "axtid:GetIdDataConfiguration"),
        params=TokensRequest,
        result=IdDataConfigurations,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability", "invalid_argument"
            )
        },
    )
    set_id_data_configuration = Operation(
        INFO,
        "set_id_data_configuration",
        ServiceJsonBinding(PATH, "axtid:SetIdDataConfiguration"),
        params=SetIdDataConfigurationRequest,
        result=TokenResult,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:InvalidConfigurationFault": ErrorCode("The IdDataConfiguration is invalid", "invalid_argument")},
    )
    remove_id_data_configuration = Operation(
        INFO,
        "remove_id_data_configuration",
        ServiceJsonBinding(PATH, "axtid:RemoveIdDataConfiguration"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("IdDataConfiguration not found", "not_found")},
    )
    get_feedback_message = Operation(
        INFO,
        "get_feedback_message",
        ServiceJsonBinding(PATH, "axtid:GetFeedbackMessage"),
        params=TokenRequest,
        result=FeedbackProfileResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("IdPoint not found", "not_found")},
    )
    get_secure_channel_status = Operation(
        INFO,
        "get_secure_channel_status",
        ServiceJsonBinding(PATH, "axtid:GetSecureChannelStatus"),
        params=TokenRequest,
        result=SecureChannelStatusResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("IdPoint not found", "not_found")},
    )
    get_id_point_white_list = Operation(
        INFO,
        "get_id_point_white_list",
        ServiceJsonBinding(PATH, "axtid:GetIdPointWhiteList"),
        params=TokensRequest,
        result=IdPointWhiteListResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability", "invalid_argument"
            )
        },
    )
    get_id_point_white_list_list = Operation(
        INFO,
        "get_id_point_white_list_list",
        ServiceJsonBinding(PATH, "axtid:GetIdPointWhiteListList"),
        params=ListRequest,
        result=IdPointWhiteListList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning", "invalid_argument"
            )
        },
    )
    indicate_remote_activities = Operation(
        INFO,
        "indicate_remote_activities",
        ServiceJsonBinding(PATH, "axtid:IndicateRemoteActivities"),
        params=IndicateRemoteActivitiesRequest,
        access="admin",
        effect="action",
        errors={"ter:NotFound": ErrorCode("IdPoint not found", "not_found")},
    )


# ---------------------------------------------------------------------------
# API classes


class IdPointServiceApi(SyncApi):
    """IdPoint service (``idpoint-service``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the IdPoint service. Access: anonymous."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def get_id_point_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointInfoList:
        """List the summaries and capabilities of all IdPoints.

        Pages through the IdPoints. Pass the returned `NextStartReference` as `StartReference` in the next
        call and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return self._run(
            OPS.get_id_point_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_id_point_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdPointInfos:
        """Get the summaries and capabilities of the IdPoints with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_id_point_info, None, {"token": token}, request_options)

    def get_id_point_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointInfoList:
        """List all IdPoints.

        Pages through the IdPoints. The message table of the docs says the response holds `IdPointInfo`
        items, although the guide says the call returns the IdPoints with their configuration.

        Access: admin.
        """
        return self._run(
            OPS.get_id_point_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_id_point(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> IdPoints:
        """Get the IdPoints with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_id_point, None, {"token": token}, request_options)

    @overload
    def set_id_point(
        self, request: SetIdPointRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    def set_id_point(
        self, /, *, id_point: list[IdPointInput], request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    def set_id_point(
        self,
        request: SetIdPointRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Add or update IdPoints.

        An IdPoint whose token exists is updated, any other is created, and one with an empty token gets a
        token from the device. The tokens are returned. An IdPoint works only once an IdPointConfiguration
        with the same token exists.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return self._run(OPS.set_id_point, request, kwargs, request_options)

    def remove_id_point(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """Remove the IdPoints with the given tokens. Access: admin."""
        self._run(OPS.remove_id_point, None, {"token": token}, request_options)

    def get_id_point_capabilities(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetIdPointCapabilitiesResult:
        """Get the capabilities of one IdPoint. Access: admin."""
        return self._run(OPS.get_id_point_capabilities, None, {"token": token}, request_options)

    @overload
    def feedback_message(
        self, request: FeedbackMessageRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def feedback_message(
        self,
        /,
        *,
        token: ReferenceToken,
        profile: IdPointFeedback,
        other_profile: str | MISSING = MISSING,
        message: str | MISSING = MISSING,
        graphics: Any | MISSING = MISSING,
        audio: Any | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def feedback_message(
        self,
        request: FeedbackMessageRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Make an IdPoint give feedback, with its LED, beeper or display.

        The Access Controller uses this to annunciate the state of a door or an access decision to the user.
        What each profile does is up to the reader.

        Access: admin.
        """
        self._run(OPS.feedback_message, request, kwargs, request_options)

    def get_id_point_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointConfigurationList:
        """List all IdPoint configurations. Access: admin."""
        return self._run(
            OPS.get_id_point_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_id_point_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdPointConfigurations:
        """Get the IdPoint configurations with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_id_point_configuration, None, {"token": token}, request_options)

    @overload
    def set_id_point_configuration(
        self, request: SetIdPointConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    def set_id_point_configuration(
        self, /, *, id_point_configuration: list[IdPointConfiguration], request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    def set_id_point_configuration(
        self,
        request: SetIdPointConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Add or update IdPoint configurations.

        The token should normally refer to an existing IdPoint. For an existing configuration only the
        supplied Configuration parameters are replaced; for a new one missing parameters get their default
        (the first valid value). Settings such as the reader type create IoUsers that are assigned to pins
        with the I/O assignment service.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return self._run(OPS.set_id_point_configuration, request, kwargs, request_options)

    def remove_id_point_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the IdPoint configurations with the given tokens.

        Normally not needed, since removing an IdPoint removes its configuration too, although a
        configuration can exist without an IdPoint.

        Access: admin.
        """
        self._run(OPS.remove_id_point_configuration, None, {"token": token}, request_options)

    def get_id_point_configuration_info(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> ConfigurationInfoResult:
        """Get the configuration parameters of one IdPoint with their allowed values. Access: admin."""
        return self._run(OPS.get_id_point_configuration_info, None, {"token": token}, request_options)

    def get_last_credential(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> LastCredentialResult:
        """Get the last credential entered at a reader.

        The data is parsed with the IdDataConfiguration. `Card` and `BitCount` are always included.

        Access: admin.
        """
        return self._run(OPS.get_last_credential, None, {"token": token}, request_options)

    def get_id_data_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointConfigurationList:
        """List all IdDataConfigurations (access card formats).

        Some formats exist by default, for example the Wiegand 26-bit H10301. The message table of the docs
        says the response holds `IdPointConfiguration` items, which is probably a copy of
        get_id_point_configuration_list.

        Access: admin.
        """
        return self._run(
            OPS.get_id_data_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_id_data_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdDataConfigurations:
        """Get the IdDataConfigurations with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_id_data_configuration, None, {"token": token}, request_options)

    @overload
    def set_id_data_configuration(
        self, request: SetIdDataConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    def set_id_data_configuration(
        self, /, *, id_data_configuration: list[IdDataConfiguration], request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    def set_id_data_configuration(
        self,
        request: SetIdDataConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Add or modify IdDataConfigurations (access card formats).

        A configuration with an empty token gets a token from the device. All supplied and generated tokens
        are returned.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return self._run(OPS.set_id_data_configuration, request, kwargs, request_options)

    def remove_id_data_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the IdDataConfigurations with the given tokens. Access: admin."""
        self._run(OPS.remove_id_data_configuration, None, {"token": token}, request_options)

    def get_feedback_message(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> FeedbackProfileResult:
        """Get the current feedback profile of an IdPoint. Access: admin."""
        return self._run(OPS.get_feedback_message, None, {"token": token}, request_options)

    def get_secure_channel_status(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> SecureChannelStatusResult:
        """Get the secure channel status of an IdPoint. Access: admin."""
        return self._run(OPS.get_secure_channel_status, None, {"token": token}, request_options)

    def get_id_point_white_list(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdPointWhiteListResult:
        """Get the whitelists with the given tokens, with the state of their entries.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_id_point_white_list, None, {"token": token}, request_options)

    def get_id_point_white_list_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointWhiteListList:
        """List all whitelists, with the state of their entries. Access: admin."""
        return self._run(
            OPS.get_id_point_white_list_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    @overload
    def indicate_remote_activities(
        self, request: IndicateRemoteActivitiesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def indicate_remote_activities(
        self,
        /,
        *,
        token: ReferenceToken,
        description: str | MISSING = MISSING,
        activities: list[Activity],
        attributes: list[NameValue] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def indicate_remote_activities(
        self,
        request: IndicateRemoteActivitiesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Report activities, such as a card read, a PIN or a REX press, from a remote device to an IdPoint.

        Triggers the same events as a physical reader. For each activity two IdPoint events are sent: first
        `tns1:IdPoint/tnsaxis:Activity` (Reason `CardPresented`, `REX` or `CodeEntered`), then
        `tns1:IdPoint/tnsaxis:Request/tnsaxis:IdData`, `...:REX` or `...:PIN`. The IdPoint must have a
        hardware configuration. Access is granted when the Name/Value pairs of the params match the IdData
        of a credential in the same order, and each name appears as an IdDataName in an authentication
        profile of the credential, access point or access profile.

        Access: admin.
        """
        self._run(OPS.indicate_remote_activities, request, kwargs, request_options)


class AsyncIdPointServiceApi(AsyncApi):
    """IdPoint service (``idpoint-service``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the IdPoint service. Access: anonymous."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def get_id_point_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointInfoList:
        """List the summaries and capabilities of all IdPoints.

        Pages through the IdPoints. Pass the returned `NextStartReference` as `StartReference` in the next
        call and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return await self._run(
            OPS.get_id_point_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_id_point_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdPointInfos:
        """Get the summaries and capabilities of the IdPoints with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_id_point_info, None, {"token": token}, request_options)

    async def get_id_point_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointInfoList:
        """List all IdPoints.

        Pages through the IdPoints. The message table of the docs says the response holds `IdPointInfo`
        items, although the guide says the call returns the IdPoints with their configuration.

        Access: admin.
        """
        return await self._run(
            OPS.get_id_point_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_id_point(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdPoints:
        """Get the IdPoints with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_id_point, None, {"token": token}, request_options)

    @overload
    async def set_id_point(
        self, request: SetIdPointRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    async def set_id_point(
        self, /, *, id_point: list[IdPointInput], request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    async def set_id_point(
        self,
        request: SetIdPointRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Add or update IdPoints.

        An IdPoint whose token exists is updated, any other is created, and one with an empty token gets a
        token from the device. The tokens are returned. An IdPoint works only once an IdPointConfiguration
        with the same token exists.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return await self._run(OPS.set_id_point, request, kwargs, request_options)

    async def remove_id_point(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the IdPoints with the given tokens. Access: admin."""
        await self._run(OPS.remove_id_point, None, {"token": token}, request_options)

    async def get_id_point_capabilities(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetIdPointCapabilitiesResult:
        """Get the capabilities of one IdPoint. Access: admin."""
        return await self._run(OPS.get_id_point_capabilities, None, {"token": token}, request_options)

    @overload
    async def feedback_message(
        self, request: FeedbackMessageRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def feedback_message(
        self,
        /,
        *,
        token: ReferenceToken,
        profile: IdPointFeedback,
        other_profile: str | MISSING = MISSING,
        message: str | MISSING = MISSING,
        graphics: Any | MISSING = MISSING,
        audio: Any | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def feedback_message(
        self,
        request: FeedbackMessageRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Make an IdPoint give feedback, with its LED, beeper or display.

        The Access Controller uses this to annunciate the state of a door or an access decision to the user.
        What each profile does is up to the reader.

        Access: admin.
        """
        await self._run(OPS.feedback_message, request, kwargs, request_options)

    async def get_id_point_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointConfigurationList:
        """List all IdPoint configurations. Access: admin."""
        return await self._run(
            OPS.get_id_point_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_id_point_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdPointConfigurations:
        """Get the IdPoint configurations with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_id_point_configuration, None, {"token": token}, request_options)

    @overload
    async def set_id_point_configuration(
        self, request: SetIdPointConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    async def set_id_point_configuration(
        self, /, *, id_point_configuration: list[IdPointConfiguration], request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    async def set_id_point_configuration(
        self,
        request: SetIdPointConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Add or update IdPoint configurations.

        The token should normally refer to an existing IdPoint. For an existing configuration only the
        supplied Configuration parameters are replaced; for a new one missing parameters get their default
        (the first valid value). Settings such as the reader type create IoUsers that are assigned to pins
        with the I/O assignment service.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return await self._run(OPS.set_id_point_configuration, request, kwargs, request_options)

    async def remove_id_point_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the IdPoint configurations with the given tokens.

        Normally not needed, since removing an IdPoint removes its configuration too, although a
        configuration can exist without an IdPoint.

        Access: admin.
        """
        await self._run(OPS.remove_id_point_configuration, None, {"token": token}, request_options)

    async def get_id_point_configuration_info(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> ConfigurationInfoResult:
        """Get the configuration parameters of one IdPoint with their allowed values. Access: admin."""
        return await self._run(OPS.get_id_point_configuration_info, None, {"token": token}, request_options)

    async def get_last_credential(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> LastCredentialResult:
        """Get the last credential entered at a reader.

        The data is parsed with the IdDataConfiguration. `Card` and `BitCount` are always included.

        Access: admin.
        """
        return await self._run(OPS.get_last_credential, None, {"token": token}, request_options)

    async def get_id_data_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointConfigurationList:
        """List all IdDataConfigurations (access card formats).

        Some formats exist by default, for example the Wiegand 26-bit H10301. The message table of the docs
        says the response holds `IdPointConfiguration` items, which is probably a copy of
        get_id_point_configuration_list.

        Access: admin.
        """
        return await self._run(
            OPS.get_id_data_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_id_data_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdDataConfigurations:
        """Get the IdDataConfigurations with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_id_data_configuration, None, {"token": token}, request_options)

    @overload
    async def set_id_data_configuration(
        self, request: SetIdDataConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    async def set_id_data_configuration(
        self, /, *, id_data_configuration: list[IdDataConfiguration], request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    async def set_id_data_configuration(
        self,
        request: SetIdDataConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Add or modify IdDataConfigurations (access card formats).

        A configuration with an empty token gets a token from the device. All supplied and generated tokens
        are returned.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return await self._run(OPS.set_id_data_configuration, request, kwargs, request_options)

    async def remove_id_data_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the IdDataConfigurations with the given tokens. Access: admin."""
        await self._run(OPS.remove_id_data_configuration, None, {"token": token}, request_options)

    async def get_feedback_message(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> FeedbackProfileResult:
        """Get the current feedback profile of an IdPoint. Access: admin."""
        return await self._run(OPS.get_feedback_message, None, {"token": token}, request_options)

    async def get_secure_channel_status(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> SecureChannelStatusResult:
        """Get the secure channel status of an IdPoint. Access: admin."""
        return await self._run(OPS.get_secure_channel_status, None, {"token": token}, request_options)

    async def get_id_point_white_list(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> IdPointWhiteListResult:
        """Get the whitelists with the given tokens, with the state of their entries.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_id_point_white_list, None, {"token": token}, request_options)

    async def get_id_point_white_list_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> IdPointWhiteListList:
        """List all whitelists, with the state of their entries. Access: admin."""
        return await self._run(
            OPS.get_id_point_white_list_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    @overload
    async def indicate_remote_activities(
        self, request: IndicateRemoteActivitiesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def indicate_remote_activities(
        self,
        /,
        *,
        token: ReferenceToken,
        description: str | MISSING = MISSING,
        activities: list[Activity],
        attributes: list[NameValue] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def indicate_remote_activities(
        self,
        request: IndicateRemoteActivitiesRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Report activities, such as a card read, a PIN or a REX press, from a remote device to an IdPoint.

        Triggers the same events as a physical reader. For each activity two IdPoint events are sent: first
        `tns1:IdPoint/tnsaxis:Activity` (Reason `CardPresented`, `REX` or `CodeEntered`), then
        `tns1:IdPoint/tnsaxis:Request/tnsaxis:IdData`, `...:REX` or `...:PIN`. The IdPoint must have a
        hardware configuration. Access is granted when the Name/Value pairs of the params match the IdData
        of a credential in the same order, and each name appears as an IdDataName in an authentication
        profile of the credential, access point or access profile.

        Access: admin.
        """
        await self._run(OPS.indicate_remote_activities, request, kwargs, request_options)
