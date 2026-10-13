# GENERATED from specs/apis/physical-access-control/access-control-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage access points, areas, access controllers, credentials, access and authentication profiles and anti-passback data, and request or verify access.

Docs: https://developer.axis.com/vapix/physical-access-control/access-control-service/
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ServiceDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ReferenceToken = str


class ServiceCapabilities(Model):
    """Optional functionality of the service. Static; does not change during device operation."""

    max_limit: int | None = Field(default=None, validation_alias="MaxLimit", serialization_alias="MaxLimit")
    """The maximum number of entries returned by a single GetList request. The device never returns more entities in a single response."""
    disable_credential: bool | None = Field(
        default=None, validation_alias="DisableCredential", serialization_alias="DisableCredential"
    )
    """True if EnableCredential and DisableCredential are supported."""
    get_access_point: bool | None = Field(
        default=None, validation_alias="GetAccessPoint", serialization_alias="GetAccessPoint"
    )
    """True if GetAccessPointList and GetAccessPoint are supported."""
    set_access_point: bool | None = Field(
        default=None, validation_alias="SetAccessPoint", serialization_alias="SetAccessPoint"
    )
    """True if SetAccessPoint is supported."""
    remove_access_point: bool | None = Field(
        default=None, validation_alias="RemoveAccessPoint", serialization_alias="RemoveAccessPoint"
    )
    """True if RemoveAccessPoint is supported."""
    get_area: bool | None = Field(default=None, validation_alias="GetArea", serialization_alias="GetArea")
    """True if GetAreaList and GetArea are supported."""
    set_area: bool | None = Field(default=None, validation_alias="SetArea", serialization_alias="SetArea")
    """True if SetArea is supported."""
    remove_area: bool | None = Field(default=None, validation_alias="RemoveArea", serialization_alias="RemoveArea")
    """True if RemoveArea is supported."""
    get_credential: bool | None = Field(
        default=None, validation_alias="GetCredential", serialization_alias="GetCredential"
    )
    """True if GetCredentialList and GetCredential are supported."""
    set_credential: bool | None = Field(
        default=None, validation_alias="SetCredential", serialization_alias="SetCredential"
    )
    """True if SetCredential is supported."""
    remove_credential: bool | None = Field(
        default=None, validation_alias="RemoveCredential", serialization_alias="RemoveCredential"
    )
    """True if RemoveCredential is supported."""
    standard_attributes_supported: bool | None = Field(
        default=None, validation_alias="StandardAttributesSupported", serialization_alias="StandardAttributesSupported"
    )
    """True if GetStandardAttributeList is supported."""
    vendor_attributes_supported: bool | None = Field(
        default=None, validation_alias="VendorAttributesSupported", serialization_alias="VendorAttributesSupported"
    )
    """True if GetVendorAttributeList is supported."""


class AccessPointCapabilities(Model):
    """Optional functionality of one access point. Different access points may differ, and the capabilities may change if hardware settings change."""

    disable_access_point: bool | None = Field(
        default=None, validation_alias="DisableAccessPoint", serialization_alias="DisableAccessPoint"
    )
    """The access point supports EnableAccessPoint and DisableAccessPoint."""
    duress: bool | None = Field(default=None, validation_alias="Duress", serialization_alias="Duress")
    """The access point supports generation of duress events."""
    anonymous_access: bool | None = Field(
        default=None, validation_alias="AnonymousAccess", serialization_alias="AnonymousAccess"
    )
    """The access point has a REX switch or other input that allows anonymous access."""
    access_taken: bool | None = Field(default=None, validation_alias="AccessTaken", serialization_alias="AccessTaken")
    """The access point generates AccessTaken and AccessNotTaken events (anonymous versions too when AnonymousAccess is also true)."""
    external_authorization: bool | None = Field(
        default=None, validation_alias="ExternalAuthorization", serialization_alias="ExternalAuthorization"
    )
    """The access point supports ExternalAuthorization and generation of Request events (anonymous version too when AnonymousAccess is also true)."""


class AccessPointInfo(Model):
    """Basic information about an AccessPoint: how access is controlled in one direction for a door (from which area to which area)."""

    token: ReferenceToken
    """A service-unique identifier of the AccessPoint."""
    name: str = Field(validation_alias="Name", serialization_alias="Name", max_length=64)
    """A user readable name. It shall be up to 64 characters."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """Optional user readable description. It shall be up to 1024 characters."""
    area_from: ReferenceToken | None = Field(default=None, validation_alias="AreaFrom", serialization_alias="AreaFrom")
    """Optional reference to the Area from which access is requested."""
    area_to: ReferenceToken | None = Field(default=None, validation_alias="AreaTo", serialization_alias="AreaTo")
    """Optional reference to the Area to which access is requested."""
    entity: ReferenceToken = Field(validation_alias="Entity", serialization_alias="Entity")
    """Reference to the entity used to control access; typically a Door."""
    entity_type: str | None = Field(default=None, validation_alias="EntityType", serialization_alias="EntityType")
    """Optional entity type; a Door (tdc:Door) is assumed if missing."""
    capabilities: AccessPointCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities for the AccessPoint."""


class AreaInfo(Model):
    """Basic information about an Area."""

    token: ReferenceToken
    """A service-unique identifier of the Area."""
    name: str = Field(validation_alias="Name", serialization_alias="Name", max_length=64)
    """User readable name. It shall be up to 64 characters."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """User readable description. It shall be up to 1024 characters."""


class AccessPointState(Model):
    """State information for an AccessPoint."""

    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the AccessPoint is enabled. True by default if the DisableAccessPoint capability is not supported."""


Decision = Literal["Granted", "Denied"]


class Attribute(Model):
    """A generic name and optional value and type that can be added to various data structures."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the attribute."""
    type: str | None = None
    """Type of the attribute: int, bool or string."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """Value of the attribute."""


class NameValue(Model):
    """A generic name and value pair."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name."""
    value: str = Field(validation_alias="Value", serialization_alias="Value")
    """Value."""


class IdPointDevice(Model):
    """An IdPoint and the device it is on."""

    id_point: ReferenceToken = Field(validation_alias="IdPoint", serialization_alias="IdPoint")
    """Reference to an IdPoint."""
    device_uuid: str | None = Field(default=None, validation_alias="DeviceUUID", serialization_alias="DeviceUUID")
    """DeviceUUID of the device where the IdPoint is located. If empty or omitted, the IdPoint token refers to this device."""


class ActionArgument(Model):
    """An argument to be used with the Action of an AccessPoint."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the argument."""
    value: str = Field(validation_alias="Value", serialization_alias="Value")
    """Value of the argument."""
    type: str | None = None
    """Type of the argument."""


class AccessPoint(Model):
    """The full configuration of an AccessPoint, the mapping between one or more IdPoints and an entity (typically a Door) used to control access."""

    token: ReferenceToken | None = None
    """A service-unique identifier. May be omitted or empty when adding; the service then allocates a token."""
    name: str = Field(validation_alias="Name", serialization_alias="Name", max_length=64)
    """A user readable name. It shall be up to 64 characters."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """Optional user readable description. It shall be up to 1024 characters."""
    area_from: ReferenceToken | None = Field(default=None, validation_alias="AreaFrom", serialization_alias="AreaFrom")
    """Optional reference to the Area from which access is requested."""
    area_to: ReferenceToken | None = Field(default=None, validation_alias="AreaTo", serialization_alias="AreaTo")
    """Optional reference to the Area to which access is requested."""
    entity: ReferenceToken = Field(validation_alias="Entity", serialization_alias="Entity")
    """Reference to the entity used to control access; typically a Door."""
    entity_type: str | None = Field(default=None, validation_alias="EntityType", serialization_alias="EntityType")
    """Optional entity type, for example axtdc:Door or tdc:Door. A Door is assumed if empty."""
    door_device_uuid: str | None = Field(
        default=None, validation_alias="DoorDeviceUUID", serialization_alias="DoorDeviceUUID"
    )
    """DeviceUUID of the device the Door is on. If empty or omitted, the Door token refers to this device."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")
    """Whether this AccessPoint is enabled."""
    id_point_device: list[IdPointDevice] | None = Field(
        default=None, validation_alias="IdPointDevice", serialization_alias="IdPointDevice"
    )
    """The IdPoints, and their devices, that can request access here. May contain several, for example a fingerprint reader and a card reader."""
    authentication_profile: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile"
    )
    """Tokens of the AuthenticationProfile items that apply for this AccessPoint."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Optional attributes associated with the AccessPoint."""
    action_argument: list[ActionArgument] | None = Field(
        default=None, validation_alias="ActionArgument", serialization_alias="ActionArgument"
    )
    """Optional arguments to the Action."""
    action: str | None = Field(default=None, validation_alias="Action", serialization_alias="Action")
    """Action associated with the AccessPoint: typically Access, AccessDoor or AccessDoorWithoutUnlock. Access is used if empty."""


class Area(Model):
    """An area and its settings."""

    token: ReferenceToken | None = None
    """A service-unique identifier. May be omitted or empty when adding; the service then allocates a token."""
    name: str = Field(validation_alias="Name", serialization_alias="Name", max_length=64)
    """User readable name. It shall be up to 64 characters."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """User readable description. It shall be up to 1024 characters."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attribute list for the Area."""


class AccessControllerInfo(Model):
    """Information for an AccessController, listing the AccessPoints it controls."""

    token: ReferenceToken
    """A service-unique identifier of the AccessController."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Short name of the AccessController."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the AccessController."""
    access_point: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AccessPoint", serialization_alias="AccessPoint"
    )
    """Tokens of the AccessPoint items the AccessController manages."""


class AccessController(Model):
    """The full configuration of an AccessController, which receives access requests from IdPoints and controls doors and other resources."""

    token: ReferenceToken | None = None
    """A service-unique identifier. May be omitted or empty when adding; the service then allocates a token."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Short name of the AccessController."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the AccessController."""
    access_point: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AccessPoint", serialization_alias="AccessPoint"
    )
    """Tokens of the AccessPoint items the AccessController manages."""


CredentialStatusEnum = Literal[
    "NotActivated",
    "Enabled",
    "Disabled",
    "LockedOut",
    "Lost",
    "Stolen",
    "Damaged",
    "Destroyed",
    "Inactive",
    "MaxDays",
    "MaxUses",
    "Expired",
]


class CredentialInfo(Model):
    """Information about a Credential."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"valid_from", "valid_to"})
    token: ReferenceToken
    """A service-unique identifier of the Credential."""
    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the Credential is enabled."""
    status: CredentialStatusEnum = Field(validation_alias="Status", serialization_alias="Status")
    """Status of the Credential, for example the reason for being disabled. Should normally be one of the CredentialStatusEnum values."""
    user_token: ReferenceToken | None = Field(
        default=None, validation_alias="UserToken", serialization_alias="UserToken"
    )
    """Identifies the User of the Credential. Optional for security and privacy reasons."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the Credential."""
    valid_from: str | None = Field(default=None, validation_alias="ValidFrom", serialization_alias="ValidFrom")
    """When the Credential starts to be valid. If null, there is no restriction (valid from whenever)."""
    valid_to: str | None = Field(default=None, validation_alias="ValidTo", serialization_alias="ValidTo")
    """When the Credential stops being valid. If null, there is no restriction (valid forever)."""


class IdData(Model):
    """A single identification or authentication name and value, such as a card number or PIN."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the field."""
    value: str = Field(validation_alias="Value", serialization_alias="Value")
    """The value to match against."""


class CredentialAccessProfile(Model):
    """A reference from a Credential to an AccessProfile, optionally restricting the period further than the AccessProfile does."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"valid_from", "valid_to"})
    access_profile: ReferenceToken = Field(validation_alias="AccessProfile", serialization_alias="AccessProfile")
    """Reference to the AccessProfile."""
    valid_from: str | None = Field(default=None, validation_alias="ValidFrom", serialization_alias="ValidFrom")
    """Optional start of the period for the AccessProfile. If null, there is no additional restriction."""
    valid_to: str | None = Field(default=None, validation_alias="ValidTo", serialization_alias="ValidTo")
    """Optional end of the period for the AccessProfile. If null, there is no additional restriction."""


class Credential(Model):
    """A Credential: the information needed to authenticate a user and the AccessProfiles it is authorized through."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"valid_from", "valid_to"})
    token: ReferenceToken | None = None
    """A service-unique identifier. May be omitted or empty when adding; the service then allocates a token."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the Credential is enabled."""
    status: CredentialStatusEnum | None = Field(default=None, validation_alias="Status", serialization_alias="Status")
    """Status of the Credential, for example the reason for being disabled."""
    id_data: list[IdData] | None = Field(default=None, validation_alias="IdData", serialization_alias="IdData")
    """The identification data for the credential."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes associated with the credential. ExtendedTime is a standard attribute."""
    authentication_profile: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile"
    )
    """Tokens of AuthenticationProfile items that override the ones in an AccessProfile or AccessPolicy when set."""
    credential_access_profile: list[CredentialAccessProfile] | None = Field(
        default=None, validation_alias="CredentialAccessProfile", serialization_alias="CredentialAccessProfile"
    )
    """AccessProfile items associated with the credential."""
    user_token: ReferenceToken | None = Field(
        default=None, validation_alias="UserToken", serialization_alias="UserToken"
    )
    """Identifies the User of the Credential. Optional for security and privacy reasons."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the Credential."""
    valid_from: str | None = Field(default=None, validation_alias="ValidFrom", serialization_alias="ValidFrom")
    """When the Credential starts to be valid. If null, there is no restriction (valid from whenever)."""
    valid_to: str | None = Field(default=None, validation_alias="ValidTo", serialization_alias="ValidTo")
    """When the Credential stops being valid. If null, there is no restriction (valid forever)."""


class AuthenticationProfileInfo(Model):
    """Information about an AuthenticationProfile."""

    token: ReferenceToken
    """A service-unique identifier of the AuthenticationProfile."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the AuthenticationProfile."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the AuthenticationProfile."""


class IdFactor(Model):
    """An IdData name and the IdMatchOperator used to check it."""

    id_data_name: str = Field(validation_alias="IdDataName", serialization_alias="IdDataName")
    """The Name of an IdData field to check."""
    id_match_operator_name: str = Field(
        validation_alias="IdMatchOperatorName", serialization_alias="IdMatchOperatorName"
    )
    """A Name of an existing IdMatchOperator."""
    operator_value: str | None = Field(
        default=None, validation_alias="OperatorValue", serialization_alias="OperatorValue"
    )
    """Information for certain operators; typically empty."""


class AuthenticationProfile(Model):
    """The authentication requirements: which IdFactor items are required at which schedules. Referenced by an AccessPoint and can be overridden in an AccessProfile and a Credential."""

    token: ReferenceToken | None = None
    """A service-unique identifier. May be omitted or empty when adding; the service then allocates a token."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the AuthenticationProfile."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the AuthenticationProfile."""
    schedule: list[ReferenceToken] | None = Field(
        default=None, validation_alias="Schedule", serialization_alias="Schedule"
    )
    """Tokens of the Schedule items that determine when the AuthenticationProfile is applicable."""
    id_factor: list[IdFactor] | None = Field(default=None, validation_alias="IdFactor", serialization_alias="IdFactor")
    """The IdFactor items needed to authenticate. All must be provided, in this order."""


class IdMatchOperator(Model):
    """Determines how the IdData value in a request is evaluated. ONVIF defines mandatory operators; vendors may add more."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the IdMatchOperator."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the operator."""


class RuleOperator(Model):
    """Determines how the IdData value in a request and other conditions are evaluated. ONVIF defines mandatory operators; vendors may add more."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the RuleOperator."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the operator."""


class AccessProfileInfo(Model):
    """Information about an AccessProfile."""

    token: ReferenceToken
    """A service-unique identifier of the AccessProfile."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the AccessProfile."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the AccessProfile."""


class AccessPolicy(Model):
    """Authentication and authorization requirements for one AccessPoint, used by an AccessProfile."""

    access_point: ReferenceToken | None = Field(
        default=None, validation_alias="AccessPoint", serialization_alias="AccessPoint"
    )
    """Reference to the AccessPoint this AccessPolicy applies to."""
    authorization_profile: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AuthorizationProfile", serialization_alias="AuthorizationProfile"
    )
    """Tokens of the AuthorizationProfile items that apply to this policy (a placeholder for future extensions)."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Optional attributes that apply to the AccessPolicy."""
    schedule: list[ReferenceToken] | None = Field(
        default=None, validation_alias="Schedule", serialization_alias="Schedule"
    )
    """Tokens of the Schedule items when authorized by this AccessPolicy if the other conditions are met."""


class AccessProfile(Model):
    """Determines which resources can be accessed and when, through AccessPolicy items, and which authentication profiles apply."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"valid_from", "valid_to"})
    token: ReferenceToken | None = None
    """A service-unique identifier. May be omitted or empty when adding; the service then allocates a token."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the AccessProfile."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the AccessProfile."""
    schedule: list[ReferenceToken] | None = Field(
        default=None, validation_alias="Schedule", serialization_alias="Schedule"
    )
    """Tokens of the Schedule items that determine when the AccessProfile is applicable."""
    authentication_profile: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile"
    )
    """Tokens of the authentication profiles for this AccessProfile. Overrides the list in the AccessPoint, so it is typically empty."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes associated with the AccessProfile."""
    access_policy: list[AccessPolicy] | None = Field(
        default=None, validation_alias="AccessPolicy", serialization_alias="AccessPolicy"
    )
    """The AccessPolicy items that are allowed."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the AccessProfile is enabled."""
    valid_from: str | None = Field(default=None, validation_alias="ValidFrom", serialization_alias="ValidFrom")
    """When the AccessProfile starts to be valid. If null, there is no restriction on the start time."""
    valid_to: str | None = Field(default=None, validation_alias="ValidTo", serialization_alias="ValidTo")
    """When the AccessProfile stops being valid. If null, there is no restriction on the stop time."""


class AccessControllerConfiguration(Model):
    """The device and hardware configuration for an AccessController."""

    token: ReferenceToken
    """AccessController Id to use for set, remove and usage."""
    device_uuid: str | None = Field(default=None, validation_alias="DeviceUUID", serialization_alias="DeviceUUID")
    """The device the AccessController is on."""
    configuration: list[NameValue] | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )
    """Configuration settings for the AccessController as name and value pairs."""


class CredentialStatistics(Model):
    """Statistics related to Credential items."""

    number_of_credentials: int | None = Field(
        default=None, validation_alias="NumberOfCredentials", serialization_alias="NumberOfCredentials"
    )
    """Number of Credential items in the system."""
    number_of_disabled_credentials: int | None = Field(
        default=None, validation_alias="NumberOfDisabledCredentials", serialization_alias="NumberOfDisabledCredentials"
    )
    """Number of disabled Credential items in the system."""


class AntipassbackData(Model):
    """One anti-passback monitoring entry."""

    credential_token: ReferenceToken = Field(validation_alias="CredentialToken", serialization_alias="CredentialToken")
    """The Credential."""
    pass_ok_threshold: int | None = Field(
        default=None, validation_alias="PassOkThreshold", serialization_alias="PassOkThreshold"
    )
    """Anti-passback timer value. The unit is documented as seconds in the API section and microseconds in the guide."""
    current_area: ReferenceToken | None = Field(
        default=None, validation_alias="CurrentArea", serialization_alias="CurrentArea"
    )
    """The current area token."""
    by_time: bool | None = Field(default=None, validation_alias="ByTime", serialization_alias="ByTime")
    """The anti-passback mode: false means Logical, true means TimedLogical."""
    violation: str | None = Field(default=None, validation_alias="Violation", serialization_alias="Violation")
    """Whether monitoring has resulted in one or more violations (shown as an empty string in the example)."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capability response message contains the requested Access Control service capabilities using a hierarchical XML capability structure."""


class GetAccessPointInfoListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAccessPointInfoListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    access_point_info: list[AccessPointInfo] | None = Field(
        default=None, validation_alias="AccessPointInfo", serialization_alias="AccessPointInfo"
    )
    """List of AccessPointInfo items."""


class GetAccessPointInfoRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessPointInfo items to get."""


class GetAccessPointInfoResult(Model):
    access_point_info: list[AccessPointInfo] | None = Field(
        default=None, validation_alias="AccessPointInfo", serialization_alias="AccessPointInfo"
    )
    """List of AccessPointInfo items."""


class GetAreaInfoListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAreaInfoListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    area_info: list[AreaInfo] | None = Field(default=None, validation_alias="AreaInfo", serialization_alias="AreaInfo")
    """List of AreaInfo items. xs:string NextStartReference [0][1] tac:AreaInfo AreaInfo [0][unbounded]"""


class GetAreaInfoRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AreaInfo items to get."""


class GetAreaInfoResult(Model):
    area_info: list[AreaInfo] | None = Field(default=None, validation_alias="AreaInfo", serialization_alias="AreaInfo")
    """List of AreaInfo items."""


class GetAccessPointStateRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of AccessPoint instance to get AccessPointState for."""


class GetAccessPointStateResult(Model):
    access_point_state: AccessPointState = Field(
        validation_alias="AccessPointState", serialization_alias="AccessPointState"
    )
    """AccessPointState item."""


class EnableAccessPointRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the AccessPoint instance to enable."""


class DisableAccessPointRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the AccessPoint instance to disable."""


class ExternalAuthorizationRequest(Model):
    access_point_token: ReferenceToken = Field(
        validation_alias="AccessPointToken", serialization_alias="AccessPointToken"
    )
    """Token of the AccessPoint instance."""
    credential_token: ReferenceToken | None = Field(
        default=None, validation_alias="CredentialToken", serialization_alias="CredentialToken"
    )
    """Optional. Token of the Credential involved."""
    reason: str | None = Field(default=None, validation_alias="Reason", serialization_alias="Reason")
    """Optional. Reason for decision."""
    decision: Decision = Field(validation_alias="Decision", serialization_alias="Decision")
    """Decision. Granted or Denied."""


class GetAccessPointListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAccessPointListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    access_point: list[AccessPoint] | None = Field(
        default=None, validation_alias="AccessPoint", serialization_alias="AccessPoint"
    )
    """List of AccessPoint items."""


class GetAccessPointRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessPoint items to get."""


class GetAccessPointResult(Model):
    access_point: list[AccessPoint] | None = Field(
        default=None, validation_alias="AccessPoint", serialization_alias="AccessPoint"
    )
    """List of AccessPoint items."""


class SetAccessPointRequest(Model):
    access_point: list[AccessPoint] = Field(
        validation_alias="AccessPoint", serialization_alias="AccessPoint", min_length=1
    )
    """The AccessPoint items to add/update."""


class SetAccessPointResult(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token")
    """The Tokens of the added/updated AccessPoint items."""


class RemoveAccessPointRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessPoint items to remove."""


class GetAreaListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAreaListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    area: list[Area] | None = Field(default=None, validation_alias="Area", serialization_alias="Area")
    """List of Area items."""


class GetAreaRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of Area items to get."""


class GetAreaResult(Model):
    area: list[Area] | None = Field(default=None, validation_alias="Area", serialization_alias="Area")
    """List of Area items."""


class SetAreaRequest(Model):
    area: list[Area] = Field(validation_alias="Area", serialization_alias="Area", min_length=1)
    """The Area items to add/update."""


class SetAreaResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """The tokens of the added/updated Area items."""


class RemoveAreaRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of Area items to remove."""


class GetAccessControllerInfoListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAccessControllerInfoListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    access_controller_info: list[AccessControllerInfo] | None = Field(
        default=None, validation_alias="AccessControllerInfo", serialization_alias="AccessControllerInfo"
    )
    """List of AccessControllerInfo items."""


class GetAccessControllerInfoRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessControllerInfo items to get."""


class GetAccessControllerInfoResult(Model):
    access_controller_info: list[AccessControllerInfo] | None = Field(
        default=None, validation_alias="AccessControllerInfo", serialization_alias="AccessControllerInfo"
    )
    """List of AccessControllerInfo items."""


class GetAccessControllerListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAccessControllerListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    access_controller: list[AccessController] | None = Field(
        default=None, validation_alias="AccessController", serialization_alias="AccessController"
    )
    """List of AccessController items."""


class GetAccessControllerRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessController items to get."""


class GetAccessControllerResult(Model):
    access_controller: list[AccessController] | None = Field(
        default=None, validation_alias="AccessController", serialization_alias="AccessController"
    )
    """List of AccessController items."""


class SetAccessControllerRequest(Model):
    access_controller: list[AccessController] = Field(
        validation_alias="AccessController", serialization_alias="AccessController", min_length=1
    )
    """The AccessController items to add/update."""


class SetAccessControllerResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """The Tokens of the added/updated AccessController items."""


class RemoveAccessControllerRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessController items to remove."""


class GetStandardAttributeListResult(Model):
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """List of supported standardized Attribute items"""


class GetVendorAttributeListResult(Model):
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """List of supported vendor specific attributes."""


class VerifyRequestRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """The AccessController to send request to."""
    id_data: list[IdData] | None = Field(default=None, validation_alias="IdData", serialization_alias="IdData")
    """The id data, typically including entries for card and PIN."""
    source_token: ReferenceToken | None = Field(
        default=None, validation_alias="SourceToken", serialization_alias="SourceToken"
    )
    """Where the request comes from."""
    target_token: ReferenceToken | None = Field(
        default=None, validation_alias="TargetToken", serialization_alias="TargetToken"
    )
    """The Resource the subject identified by IdField items and/or PIN want access to."""
    action: str | None = Field(default=None, validation_alias="Action", serialization_alias="Action")
    """The desired action on the resource. If missing "Access" should be assumed."""
    environment: list[NameValue] | None = Field(
        default=None, validation_alias="Environment", serialization_alias="Environment"
    )
    """Additional information."""


class VerifyRequestResult(Model):
    access_granted: bool = Field(validation_alias="AccessGranted", serialization_alias="AccessGranted")
    """True if access is granted, false if denied."""
    reason: str = Field(validation_alias="Reason", serialization_alias="Reason")
    """Reason for denial."""


class RequestAccessRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """The AccessController to send request to."""
    id_data: list[IdData] | None = Field(default=None, validation_alias="IdData", serialization_alias="IdData")
    """The id data, typically including entries for card and PIN."""
    source_token: ReferenceToken | None = Field(
        default=None, validation_alias="SourceToken", serialization_alias="SourceToken"
    )
    """Where the request comes from."""
    target_token: ReferenceToken | None = Field(
        default=None, validation_alias="TargetToken", serialization_alias="TargetToken"
    )
    """The Resource the subject identified by IdField items and/or PIN want access to."""
    action: str | None = Field(default=None, validation_alias="Action", serialization_alias="Action")
    """The desired action on the resource. If missing "Access" should be assumed."""
    environment: list[NameValue] | None = Field(
        default=None, validation_alias="Environment", serialization_alias="Environment"
    )
    """Additional information."""


class RequestAccessResult(Model):
    access_granted: bool = Field(validation_alias="AccessGranted", serialization_alias="AccessGranted")
    """True if access is granted, false if denied."""
    reason: str = Field(validation_alias="Reason", serialization_alias="Reason")
    """Reason for denial."""


class GetCredentialInfoListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetCredentialInfoListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    credential_info: list[CredentialInfo] | None = Field(
        default=None, validation_alias="CredentialInfo", serialization_alias="CredentialInfo"
    )
    """List of CredentialInfo items."""


class GetCredentialInfoRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of CredentialInfo items to get."""


class GetCredentialInfoResult(Model):
    credential_info: list[CredentialInfo] | None = Field(
        default=None, validation_alias="CredentialInfo", serialization_alias="CredentialInfo"
    )
    """List of CredentialInfo items."""


class EnableCredentialRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """The Credential to enable."""


class DisableCredentialRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """The Credential to disable."""
    status: CredentialStatusEnum | None = Field(default=None, validation_alias="Status", serialization_alias="Status")
    """Optional status to set about the reason to disable the credential. If missing "Disabled" should be assumed."""


class GetCredentialListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetCredentialListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    credential_info: list[CredentialInfo] | None = Field(
        default=None, validation_alias="CredentialInfo", serialization_alias="CredentialInfo"
    )
    """List of CredentialInfo items."""


class GetCredentialRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of Credential items to get."""


class GetCredentialResult(Model):
    credential: list[Credential] | None = Field(
        default=None, validation_alias="Credential", serialization_alias="Credential"
    )
    """List of Credential items."""


class SetCredentialRequest(Model):
    credential: list[Credential] = Field(validation_alias="Credential", serialization_alias="Credential", min_length=1)
    """The Credential items to add/update."""


class SetCredentialResult(Model):
    credential: list[Credential] | None = Field(
        default=None, validation_alias="Credential", serialization_alias="Credential"
    )
    """List of Credential items (as documented in the message table)."""
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the added or updated Credential items (as shown in the examples)."""


class RemoveCredentialRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the Credential items to remove."""


class GetAccessProfileInfoListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAccessProfileInfoListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    access_profile_info: list[AccessProfileInfo] | None = Field(
        default=None, validation_alias="AccessProfileInfo", serialization_alias="AccessProfileInfo"
    )
    """List of AccessProfileInfo items."""


class GetAccessProfileInfoRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessProfileInfo items to get."""


class GetAccessProfileInfoResult(Model):
    access_profile_info: list[AccessProfileInfo] | None = Field(
        default=None, validation_alias="AccessProfileInfo", serialization_alias="AccessProfileInfo"
    )
    """List of AccessProfileInfo items."""


class GetAccessProfileListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAccessProfileListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    access_profile: list[AccessProfile] | None = Field(
        default=None, validation_alias="AccessProfile", serialization_alias="AccessProfile"
    )
    """List of AccessProfile items."""


class GetAccessProfileRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessProfile items to get."""


class GetAccessProfileResult(Model):
    access_profile: list[AccessProfile] | None = Field(
        default=None, validation_alias="AccessProfile", serialization_alias="AccessProfile"
    )
    """List of AccessProfile items."""


class SetAccessProfileRequest(Model):
    access_profile: list[AccessProfile] = Field(
        validation_alias="AccessProfile", serialization_alias="AccessProfile", min_length=1
    )
    """The AccessProfile items to add/update."""


class SetAccessProfileResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the added/updated AccessProfile items."""


class RemoveAccessProfileRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the AccessProfile items to remove."""


class GetAuthenticationProfileInfoListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAuthenticationProfileInfoListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    authentication_profile_info: list[AuthenticationProfileInfo] | None = Field(
        default=None, validation_alias="AuthenticationProfileInfo", serialization_alias="AuthenticationProfileInfo"
    )
    """List of AuthenticationProfileInfo items."""


class GetAuthenticationProfileInfoRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AuthenticationProfileInfo items to get."""


class GetAuthenticationProfileInfoResult(Model):
    authentication_profile_info: list[AuthenticationProfileInfo] | None = Field(
        default=None, validation_alias="AuthenticationProfileInfo", serialization_alias="AuthenticationProfileInfo"
    )
    """List of AuthenticationProfileInfo items."""


class GetAuthenticationProfileListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, less than one or higher than what the device supports, the number of items is determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAuthenticationProfileListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    authentication_profile: list[AuthenticationProfile] | None = Field(
        default=None, validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile"
    )
    """List of AuthenticationProfile items."""


class GetAuthenticationProfileRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AuthenticationProfile items to get."""


class GetAuthenticationProfileResult(Model):
    authentication_profile: list[AuthenticationProfile] | None = Field(
        default=None, validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile"
    )
    """List of AuthenticationProfile items."""


class SetAuthenticationProfileRequest(Model):
    authentication_profile: list[AuthenticationProfile] = Field(
        validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile", min_length=1
    )
    """List of AuthenticationProfile items to set."""


class SetAuthenticationProfileResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """List of supplied and generated tokens"""


class RemoveAuthenticationProfileRequest(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """List of tokens for the AuthenticationProfile items to remove If list is empty, no profiles will be removed."""


class GetIdMatchOperatorsResult(Model):
    id_match_operator: list[IdMatchOperator] | None = Field(
        default=None, validation_alias="IdMatchOperator", serialization_alias="IdMatchOperator"
    )
    """List of supported IdMatchOperator items."""


class GetRuleOperatorsResult(Model):
    rule_operator: list[RuleOperator] | None = Field(
        default=None, validation_alias="RuleOperator", serialization_alias="RuleOperator"
    )
    """List of supported RuleOperator items."""


class GetAccessControllerConfigurationListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, or higher than what the device supports, the number of items shall be determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAccessControllerConfigurationListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    access_controller_configuration: list[AccessControllerConfiguration] | None = Field(
        default=None,
        validation_alias="AccessControllerConfiguration",
        serialization_alias="AccessControllerConfiguration",
    )
    """List of AccessControllerConfiguration items."""


class GetAccessControllerConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessControllerConfiguration items to get."""


class GetAccessControllerConfigurationResult(Model):
    access_controller_configuration: list[AccessControllerConfiguration] | None = Field(
        default=None,
        validation_alias="AccessControllerConfiguration",
        serialization_alias="AccessControllerConfiguration",
    )
    """List of AccessControllerConfiguration items."""


class SetAccessControllerConfigurationRequest(Model):
    access_controller_configuration: list[AccessControllerConfiguration] = Field(
        validation_alias="AccessControllerConfiguration",
        serialization_alias="AccessControllerConfiguration",
        min_length=1,
    )
    """The AccessControllerConfiguration items to add/update."""


class SetAccessControllerConfigurationResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """The tokens of the added/updated AccessController items."""


class RemoveAccessControllerConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of AccessControllerConfiguration items to get."""


class GetCredentialStatisticsResult(Model):
    credential_statistics: CredentialStatistics = Field(
        validation_alias="CredentialStatistics", serialization_alias="CredentialStatistics"
    )


class GetMasterDbStateResult(Model):
    nbr_total_pages: int = Field(validation_alias="NbrTotalPages", serialization_alias="NbrTotalPages")
    """Number of total pages in the database."""
    nbr_free_pages: int = Field(validation_alias="NbrFreePages", serialization_alias="NbrFreePages")
    """Number of free pages in the database."""
    size_on_disk: int = Field(validation_alias="SizeOnDisk", serialization_alias="SizeOnDisk")
    """Number of bytes the database occupies on disk."""


class ReOpenMasterDbResult(Model):
    nbr_total_pages: int = Field(validation_alias="NbrTotalPages", serialization_alias="NbrTotalPages")
    """Number of total pages in the database."""
    nbr_free_pages: int = Field(validation_alias="NbrFreePages", serialization_alias="NbrFreePages")
    """Number of free pages in the database."""
    size_on_disk: int = Field(validation_alias="SizeOnDisk", serialization_alias="SizeOnDisk")
    """Number of bytes the database occupies on disk."""


class ResetAntipassbackViolationRequest(Model):
    credential_token: ReferenceToken = Field(validation_alias="CredentialToken", serialization_alias="CredentialToken")
    """Token of Credential"""


class GetAntipassbackDataListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, or greater than the device supports, the number of items shall be determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetAntipassbackDataListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    antipassback_data: list[AntipassbackData] | None = Field(
        default=None, validation_alias="AntipassbackData", serialization_alias="AntipassbackData"
    )
    """List of AntipassbackData items."""


class SetAntipassbackDataRequest(Model):
    antipassback_data: list[AntipassbackData] = Field(
        validation_alias="AntipassbackData", serialization_alias="AntipassbackData", min_length=1
    )
    """List of AntipassbackData to set"""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/pacs"

INFO = ApiInfo(
    id="access-control-service",
    name="Access control service",
    family=Family.SERVICE_JSON,
    discovery=(
        ServiceDiscovery("http://www.onvif.org/ver10/accesscontrol/wsdl"),
        ServiceDiscovery("http://www.axis.com/vapix/ws/pacs"),
    ),
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/access-control-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/event-logger-service/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
        "https://developer.axis.com/vapix/physical-access-control/system-integration-examples/",
    ),
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "tac:GetServiceCapabilities", auth="if_challenged"),
        result=GetServiceCapabilitiesResult,
        access="anonymous",
        effect="read",
    )
    get_access_point_info_list = Operation(
        INFO,
        "get_access_point_info_list",
        ServiceJsonBinding(PATH, "tac:GetAccessPointInfoList"),
        params=GetAccessPointInfoListRequest,
        result=GetAccessPointInfoListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_access_point_info = Operation(
        INFO,
        "get_access_point_info",
        ServiceJsonBinding(PATH, "tac:GetAccessPointInfo"),
        params=GetAccessPointInfoRequest,
        result=GetAccessPointInfoResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    get_area_info_list = Operation(
        INFO,
        "get_area_info_list",
        ServiceJsonBinding(PATH, "tac:GetAreaInfoList"),
        params=GetAreaInfoListRequest,
        result=GetAreaInfoListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_area_info = Operation(
        INFO,
        "get_area_info",
        ServiceJsonBinding(PATH, "tac:GetAreaInfo"),
        params=GetAreaInfoRequest,
        result=GetAreaInfoResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    get_access_point_state = Operation(
        INFO,
        "get_access_point_state",
        ServiceJsonBinding(PATH, "tac:GetAccessPointState"),
        params=GetAccessPointStateRequest,
        result=GetAccessPointStateResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("AccessPoint is not found.", "not_found")},
    )
    enable_access_point = Operation(
        INFO,
        "enable_access_point",
        ServiceJsonBinding(PATH, "tac:EnableAccessPoint"),
        params=EnableAccessPointRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:NotSupported": ErrorCode("The operation is not supported.", "unsupported"),
        },
    )
    disable_access_point = Operation(
        INFO,
        "disable_access_point",
        ServiceJsonBinding(PATH, "tac:DisableAccessPoint"),
        params=DisableAccessPointRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:NotSupported": ErrorCode("The operation is not supported.", "unsupported"),
        },
    )
    external_authorization = Operation(
        INFO,
        "external_authorization",
        ServiceJsonBinding(PATH, "tac:ExternalAuthorization"),
        params=ExternalAuthorizationRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:NotSupported": ErrorCode(
                "The operation is not supported (documented as: AccessPoint is not found).", "unsupported"
            ),
        },
    )
    get_access_point_list = Operation(
        INFO,
        "get_access_point_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessPointList"),
        params=GetAccessPointListRequest,
        result=GetAccessPointListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_access_point = Operation(
        INFO,
        "get_access_point",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessPoint"),
        params=GetAccessPointRequest,
        result=GetAccessPointResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    set_access_point = Operation(
        INFO,
        "set_access_point",
        ServiceJsonBinding(PATH, "pacsaxis:SetAccessPoint"),
        params=SetAccessPointRequest,
        result=SetAccessPointResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgs": ErrorCode("Invalid arguments.", "invalid_argument"),
            "ter:NotAllowed": ErrorCode("The operation is not allowed.", "access_denied"),
        },
    )
    remove_access_point = Operation(
        INFO,
        "remove_access_point",
        ServiceJsonBinding(PATH, "pacsaxis:RemoveAccessPoint"),
        params=RemoveAccessPointRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("AccessPoint is not found.", "not_found")},
    )
    get_area_list = Operation(
        INFO,
        "get_area_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAreaList"),
        params=GetAreaListRequest,
        result=GetAreaListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_area = Operation(
        INFO,
        "get_area",
        ServiceJsonBinding(PATH, "pacsaxis:GetArea"),
        params=GetAreaRequest,
        result=GetAreaResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    set_area = Operation(
        INFO,
        "set_area",
        ServiceJsonBinding(PATH, "pacsaxis:SetArea"),
        params=SetAreaRequest,
        result=SetAreaResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgs": ErrorCode("Invalid arguments.", "invalid_argument"),
            "ter:NotAllowed": ErrorCode("The operation is not allowed.", "access_denied"),
        },
    )
    remove_area = Operation(
        INFO,
        "remove_area",
        ServiceJsonBinding(PATH, "pacsaxis:RemoveArea"),
        params=RemoveAreaRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("Area is not found.", "not_found")},
    )
    get_access_controller_info_list = Operation(
        INFO,
        "get_access_controller_info_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessControllerInfoList"),
        params=GetAccessControllerInfoListRequest,
        result=GetAccessControllerInfoListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_access_controller_info = Operation(
        INFO,
        "get_access_controller_info",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessControllerInfo"),
        params=GetAccessControllerInfoRequest,
        result=GetAccessControllerInfoResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    get_access_controller_list = Operation(
        INFO,
        "get_access_controller_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessControllerList"),
        params=GetAccessControllerListRequest,
        result=GetAccessControllerListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_access_controller = Operation(
        INFO,
        "get_access_controller",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessController"),
        params=GetAccessControllerRequest,
        result=GetAccessControllerResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    set_access_controller = Operation(
        INFO,
        "set_access_controller",
        ServiceJsonBinding(PATH, "pacsaxis:SetAccessController"),
        params=SetAccessControllerRequest,
        result=SetAccessControllerResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgs": ErrorCode("Invalid arguments.", "invalid_argument"),
            "ter:NotAllowed": ErrorCode("The operation is not allowed.", "access_denied"),
        },
    )
    remove_access_controller = Operation(
        INFO,
        "remove_access_controller",
        ServiceJsonBinding(PATH, "pacsaxis:RemoveAccessController"),
        params=RemoveAccessControllerRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("AccessController is not found.", "not_found")},
    )
    get_standard_attribute_list = Operation(
        INFO,
        "get_standard_attribute_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetStandardAttributeList"),
        result=GetStandardAttributeListResult,
        access="admin",
        effect="read",
    )
    get_vendor_attribute_list = Operation(
        INFO,
        "get_vendor_attribute_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetVendorAttributeList"),
        result=GetVendorAttributeListResult,
        access="admin",
        effect="read",
    )
    verify_request = Operation(
        INFO,
        "verify_request",
        ServiceJsonBinding(PATH, "pacsaxis:VerifyRequest"),
        params=VerifyRequestRequest,
        result=VerifyRequestResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("AccessController is not found.", "not_found")},
    )
    request_access = Operation(
        INFO,
        "request_access",
        ServiceJsonBinding(PATH, "pacsaxis:RequestAccess"),
        params=RequestAccessRequest,
        result=RequestAccessResult,
        access="admin",
        effect="action",
        errors={"ter:NotFound": ErrorCode("AccessController is not found.", "not_found")},
    )
    get_credential_info_list = Operation(
        INFO,
        "get_credential_info_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetCredentialInfoList"),
        params=GetCredentialInfoListRequest,
        result=GetCredentialInfoListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_credential_info = Operation(
        INFO,
        "get_credential_info",
        ServiceJsonBinding(PATH, "pacsaxis:GetCredentialInfo"),
        params=GetCredentialInfoRequest,
        result=GetCredentialInfoResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    enable_credential = Operation(
        INFO,
        "enable_credential",
        ServiceJsonBinding(PATH, "pacsaxis:EnableCredential"),
        params=EnableCredentialRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:NotFound": ErrorCode("Not found.", "not_found")},
    )
    disable_credential = Operation(
        INFO,
        "disable_credential",
        ServiceJsonBinding(PATH, "pacsaxis:DisableCredential"),
        params=DisableCredentialRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:NotFound": ErrorCode("Not found.", "not_found")},
    )
    get_credential_list = Operation(
        INFO,
        "get_credential_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetCredentialList"),
        params=GetCredentialListRequest,
        result=GetCredentialListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_credential = Operation(
        INFO,
        "get_credential",
        ServiceJsonBinding(PATH, "pacsaxis:GetCredential"),
        params=GetCredentialRequest,
        result=GetCredentialResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    set_credential = Operation(
        INFO,
        "set_credential",
        ServiceJsonBinding(PATH, "pacsaxis:SetCredential"),
        params=SetCredentialRequest,
        result=SetCredentialResult,
        access="admin",
        effect="write",
        write="replace",
        errors={"ter:InvalidCredentialFault": ErrorCode("Invalid credential.", "invalid_argument")},
    )
    remove_credential = Operation(
        INFO,
        "remove_credential",
        ServiceJsonBinding(PATH, "pacsaxis:RemoveCredential"),
        params=RemoveCredentialRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("Credential is not found.", "not_found")},
    )
    get_access_profile_info_list = Operation(
        INFO,
        "get_access_profile_info_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessProfileInfoList"),
        params=GetAccessProfileInfoListRequest,
        result=GetAccessProfileInfoListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_access_profile_info = Operation(
        INFO,
        "get_access_profile_info",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessProfileInfo"),
        params=GetAccessProfileInfoRequest,
        result=GetAccessProfileInfoResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    get_access_profile_list = Operation(
        INFO,
        "get_access_profile_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessProfileList"),
        params=GetAccessProfileListRequest,
        result=GetAccessProfileListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_access_profile = Operation(
        INFO,
        "get_access_profile",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessProfile"),
        params=GetAccessProfileRequest,
        result=GetAccessProfileResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    set_access_profile = Operation(
        INFO,
        "set_access_profile",
        ServiceJsonBinding(PATH, "pacsaxis:SetAccessProfile"),
        params=SetAccessProfileRequest,
        result=SetAccessProfileResult,
        access="admin",
        effect="write",
        write="replace",
        errors={"ter:InvalidAccessProfileFault": ErrorCode("Invalid access profile.", "invalid_argument")},
    )
    remove_access_profile = Operation(
        INFO,
        "remove_access_profile",
        ServiceJsonBinding(PATH, "pacsaxis:RemoveAccessProfile"),
        params=RemoveAccessProfileRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("AccessProfile is not found.", "not_found")},
    )
    get_authentication_profile_info_list = Operation(
        INFO,
        "get_authentication_profile_info_list",
        ServiceJsonBinding(PATH, "tac:GetAuthenticationProfileInfoList"),
        params=GetAuthenticationProfileInfoListRequest,
        result=GetAuthenticationProfileInfoListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_authentication_profile_info = Operation(
        INFO,
        "get_authentication_profile_info",
        ServiceJsonBinding(PATH, "tac:GetAuthenticationProfileInfo"),
        params=GetAuthenticationProfileInfoRequest,
        result=GetAuthenticationProfileInfoResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    get_authentication_profile_list = Operation(
        INFO,
        "get_authentication_profile_list",
        ServiceJsonBinding(PATH, "tac:GetAuthenticationProfileList"),
        params=GetAuthenticationProfileListRequest,
        result=GetAuthenticationProfileListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_authentication_profile = Operation(
        INFO,
        "get_authentication_profile",
        ServiceJsonBinding(PATH, "tac:GetAuthenticationProfile"),
        params=GetAuthenticationProfileRequest,
        result=GetAuthenticationProfileResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    set_authentication_profile = Operation(
        INFO,
        "set_authentication_profile",
        ServiceJsonBinding(PATH, "tac:SetAuthenticationProfile"),
        params=SetAuthenticationProfileRequest,
        result=SetAuthenticationProfileResult,
        access="admin",
        effect="write",
        write="replace",
    )
    remove_authentication_profile = Operation(
        INFO,
        "remove_authentication_profile",
        ServiceJsonBinding(PATH, "tac:RemoveAuthenticationProfile"),
        params=RemoveAuthenticationProfileRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("AuthenticationProfile is not found.", "not_found")},
    )
    get_id_match_operators = Operation(
        INFO,
        "get_id_match_operators",
        ServiceJsonBinding(PATH, "pacsaxis:GetIdMatchOperators"),
        result=GetIdMatchOperatorsResult,
        access="admin",
        effect="read",
    )
    get_rule_operators = Operation(
        INFO,
        "get_rule_operators",
        ServiceJsonBinding(PATH, "pacsaxis:GetRuleOperators"),
        result=GetRuleOperatorsResult,
        access="admin",
        effect="read",
    )
    get_access_controller_configuration_list = Operation(
        INFO,
        "get_access_controller_configuration_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessControllerConfigurationList"),
        params=GetAccessControllerConfigurationListRequest,
        result=GetAccessControllerConfigurationListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client need to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_access_controller_configuration = Operation(
        INFO,
        "get_access_controller_configuration",
        ServiceJsonBinding(PATH, "pacsaxis:GetAccessControllerConfiguration"),
        params=GetAccessControllerConfigurationRequest,
        result=GetAccessControllerConfigurationResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode("Too many items were requested, see MaxLimit capability.", "invalid_argument")
        },
    )
    set_access_controller_configuration = Operation(
        INFO,
        "set_access_controller_configuration",
        ServiceJsonBinding(PATH, "pacsaxis:SetAccessControllerConfiguration"),
        params=SetAccessControllerConfigurationRequest,
        result=SetAccessControllerConfigurationResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgs": ErrorCode("Invalid arguments.", "invalid_argument"),
            "ter:NotAllowed": ErrorCode("The operation is not allowed.", "access_denied"),
        },
    )
    remove_access_controller_configuration = Operation(
        INFO,
        "remove_access_controller_configuration",
        ServiceJsonBinding(PATH, "pacsaxis:RemoveAccessControllerConfiguration"),
        params=RemoveAccessControllerConfigurationRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("AccessController not found.", "not_found")},
    )
    get_credential_statistics = Operation(
        INFO,
        "get_credential_statistics",
        ServiceJsonBinding(PATH, "pacsaxis:GetCredentialStatistics"),
        result=GetCredentialStatisticsResult,
        access="admin",
        effect="read",
    )
    get_master_db_state = Operation(
        INFO,
        "get_master_db_state",
        ServiceJsonBinding(PATH, "pacsaxis:GetMasterDBState"),
        result=GetMasterDbStateResult,
        access="admin",
        effect="read",
    )
    re_open_master_db = Operation(
        INFO,
        "re_open_master_db",
        ServiceJsonBinding(PATH, "pacsaxis:ReOpenMasterDB"),
        result=ReOpenMasterDbResult,
        access="admin",
        effect="action",
    )
    reset_antipassback_violation = Operation(
        INFO,
        "reset_antipassback_violation",
        ServiceJsonBinding(PATH, "pacsaxis:ResetAntipassbackViolation"),
        params=ResetAntipassbackViolationRequest,
        access="admin",
        effect="action",
        errors={"ter:NotFound": ErrorCode("Credential token", "not_found")},
    )
    reset_all_antipassback_violations = Operation(
        INFO,
        "reset_all_antipassback_violations",
        ServiceJsonBinding(PATH, "pacsaxis:ResetAllAntipassbackViolations"),
        access="admin",
        effect="action",
    )
    get_antipassback_data_list = Operation(
        INFO,
        "get_antipassback_data_list",
        ServiceJsonBinding(PATH, "pacsaxis:GetAntipassbackDataList"),
        params=GetAntipassbackDataListRequest,
        result=GetAntipassbackDataListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. Client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    set_antipassback_data = Operation(
        INFO,
        "set_antipassback_data",
        ServiceJsonBinding(PATH, "pacsaxis:SetAntipassbackData"),
        params=SetAntipassbackDataRequest,
        access="admin",
        effect="write",
        write="replace",
    )


# ---------------------------------------------------------------------------
# API classes


class AccessControlServiceApi(SyncApi):
    """Access control service (``access-control-service``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """This operation returns the capabilities of the Access Control service.

        An ONVIF compliant device which provides the Access Control service shall implement this method.

        Access: anonymous.
        """
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def get_access_point_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessPointInfoListResult:
        """This operation requests a list of all `AccessPointInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_access_point_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_access_point_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessPointInfoResult:
        """This operation requests a list of `AccessPointInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_access_point_info, None, {"token": token}, request_options)

    def get_area_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAreaInfoListResult:
        """This operation requests a list of all `AreaInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_area_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_area_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAreaInfoResult:
        """This operation requests a list of `AreaInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_area_info, None, {"token": token}, request_options)

    def get_access_point_state(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetAccessPointStateResult:
        """This operation requests the `AccessPointState` for the `AccessPoint` instance specified by token.

        An ONVIF compliant device that provides Access Control service shall implement this method.

        Access: admin.
        """
        return self._run(OPS.get_access_point_state, None, {"token": token}, request_options)

    def enable_access_point(self, *, token: ReferenceToken, request_options: RequestOptions | None = None) -> None:
        """This operation allows enabling an access point.

        A device that signals support for `DisableAccessPoint` capability for a particular `AccessPoint`
        instance shall implement this command.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.enable_access_point, None, {"token": token}, request_options)

    def disable_access_point(self, *, token: ReferenceToken, request_options: RequestOptions | None = None) -> None:
        """This operation allows disabling an access point.

        A device that signals support for `DisableAccessPoint` capability for a particular `AccessPoint`
        instance shall implement this command.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.disable_access_point, None, {"token": token}, request_options)

    def external_authorization(
        self,
        *,
        access_point_token: ReferenceToken,
        credential_token: ReferenceToken | MISSING = MISSING,
        reason: str | MISSING = MISSING,
        decision: Decision,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows to deny or grant decision at an `AccessPoint` instance.

        A device that signals support for `ExternalAuthorization` capability for a particular `AccessPoint`
        instance shall implement this method.

        Access: admin.
        """
        self._run(
            OPS.external_authorization,
            None,
            {
                "access_point_token": access_point_token,
                "credential_token": credential_token,
                "reason": reason,
                "decision": decision,
            },
            request_options,
        )

    def get_access_point_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessPointListResult:
        """This operation requests a list of all of `AccessPoint` items provided by the device.

        This function shall be implemented if the `GetAccessPoint` service capability is true. A call to
        this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_access_point_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_access_point(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessPointResult:
        """This operation requests a list of `AccessPoint` items matching the given tokens.

        This method shall be supported if the `GetAccessPoint` service capability is true. At least one
        token shall be specified. The device shall ignore tokens it cannot resolve and may return an empty
        list if there are no items matching specified tokens. If the number of requested items is greater
        than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_access_point, None, {"token": token}, request_options)

    @overload
    def set_access_point(
        self, request: SetAccessPointRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessPointResult: ...
    @overload
    def set_access_point(
        self, /, *, access_point: list[AccessPoint], request_options: RequestOptions | None = None
    ) -> SetAccessPointResult: ...
    def set_access_point(
        self,
        request: SetAccessPointRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessPointResult:
        """Add/update a list of `AccessPoint` items.

        If `AccessPoint` items with the specified tokens already exist, they shall be updated. If not, they
        shall be added. If the token field of any `AccessPoint` is empty, the service shall allocate a token
        for the `AccessPoint`. All tokens shall be returned in the response. This function must be available
        if the `SetAccessPoint` service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_access_point, request, kwargs, request_options)

    def remove_access_point(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessPoint` items.

        This function must be available if the `RemoveAccessPoint` service capability is true.

        Access: admin.
        """
        self._run(OPS.remove_access_point, None, {"token": token}, request_options)

    def get_area_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAreaListResult:
        """This operation requests a list of all of `Area` items provided by the device.

        This function shall be implemented if the `GetArea` service capability is true. A call to this
        method shall return a `StartReference` when not all data is returned and more data is available. The
        reference shall be valid for retrieving the next set of data. See section Retrieving system
        configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(OPS.get_area_list, None, {"limit": limit, "start_reference": start_reference}, request_options)

    def get_area(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> GetAreaResult:
        """This operation requests a list of `Area` items matching the given tokens.

        This method shall be supported if the `GetArea` service capability is true. At least one token shall
        be specified. The device shall ignore tokens it cannot resolve and may return an empty list if there
        are no items matching specified tokens. If the number of requested items is greater than `MaxLimit`,
        a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_area, None, {"token": token}, request_options)

    @overload
    def set_area(
        self, request: SetAreaRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAreaResult: ...
    @overload
    def set_area(self, /, *, area: list[Area], request_options: RequestOptions | None = None) -> SetAreaResult: ...
    def set_area(
        self, request: SetAreaRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetAreaResult:
        """Add/update a list of `Area` items.

        If `Area` with the specified tokens already exist, they shall be updated. If not, they shall be
        added. If the token field of any `Area` is empty, the service shall allocate a token for the `Area`.
        All tokens shall be returned in the response. This function must be available if the `SetArea`
        service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_area, request, kwargs, request_options)

    def remove_area(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """Remove the specified `Area` items.

        This function must be available if the `RemoveArea` service capability is true.

        Access: admin.
        """
        self._run(OPS.remove_area, None, {"token": token}, request_options)

    def get_access_controller_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessControllerInfoListResult:
        """This operation requests a list of all `AccessControllerInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_access_controller_info_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_access_controller_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessControllerInfoResult:
        """This operation requests a list of `AccessControllerInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_access_controller_info, None, {"token": token}, request_options)

    def get_access_controller_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessControllerListResult:
        """This operation requests a list of all `AccessController` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_access_controller_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_access_controller(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessControllerResult:
        """This operation requests a list of `AccessController` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_access_controller, None, {"token": token}, request_options)

    @overload
    def set_access_controller(
        self, request: SetAccessControllerRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessControllerResult: ...
    @overload
    def set_access_controller(
        self, /, *, access_controller: list[AccessController], request_options: RequestOptions | None = None
    ) -> SetAccessControllerResult: ...
    def set_access_controller(
        self,
        request: SetAccessControllerRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessControllerResult:
        """Add/update a list of `AccessController` items.

        If `AccessController` items with the specified tokens already exist, they shall be updated. If not,
        they shall be added. If the `Token` field of any `AccessController` is empty, the service shall
        allocate a token for the `AccessController`. All tokens shall be returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_access_controller, request, kwargs, request_options)

    def remove_access_controller(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessController` items. Access: admin."""
        self._run(OPS.remove_access_controller, None, {"token": token}, request_options)

    def get_standard_attribute_list(
        self, *, request_options: RequestOptions | None = None
    ) -> GetStandardAttributeListResult:
        """Returns a list of attributes and their value type supported by the service. Access: admin."""
        return self._run(OPS.get_standard_attribute_list, None, {}, request_options)

    def get_vendor_attribute_list(
        self, *, request_options: RequestOptions | None = None
    ) -> GetVendorAttributeListResult:
        """This function shall return the vendor specific attributes supported. Access: admin."""
        return self._run(OPS.get_vendor_attribute_list, None, {}, request_options)

    @overload
    def verify_request(
        self, request: VerifyRequestRequest, /, *, request_options: RequestOptions | None = None
    ) -> VerifyRequestResult: ...
    @overload
    def verify_request(
        self,
        /,
        *,
        token: ReferenceToken,
        id_data: list[IdData] | MISSING = MISSING,
        source_token: ReferenceToken | MISSING = MISSING,
        target_token: ReferenceToken | MISSING = MISSING,
        action: str | MISSING = MISSING,
        environment: list[NameValue] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> VerifyRequestResult: ...
    def verify_request(
        self,
        request: VerifyRequestRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> VerifyRequestResult:
        """Perform a validation of the request, and return the result, but does not perform any action.

        Access: admin.
        """
        return self._run(OPS.verify_request, request, kwargs, request_options)

    @overload
    def request_access(
        self, request: RequestAccessRequest, /, *, request_options: RequestOptions | None = None
    ) -> RequestAccessResult: ...
    @overload
    def request_access(
        self,
        /,
        *,
        token: ReferenceToken,
        id_data: list[IdData] | MISSING = MISSING,
        source_token: ReferenceToken | MISSING = MISSING,
        target_token: ReferenceToken | MISSING = MISSING,
        action: str | MISSING = MISSING,
        environment: list[NameValue] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RequestAccessResult: ...
    def request_access(
        self,
        request: RequestAccessRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> RequestAccessResult:
        """Request access to the specified `Resource` with the given `IdField` items. Access: admin."""
        return self._run(OPS.request_access, request, kwargs, request_options)

    def get_credential_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCredentialInfoListResult:
        """This operation requests a list of all `CredentialInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter. This
        function must be available if the `GetCredentialListSupported` service capability is true.

        Access: admin.
        """
        return self._run(
            OPS.get_credential_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_credential_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetCredentialInfoResult:
        """This operation requests a list of `CredentialInfo` items matching the given tokens.

        This method shall be supported if the `GetCredential` service capability is true. At least one token
        shall be specified. The device shall ignore tokens it cannot resolve and may return an empty list if
        there are no items matching specified tokens. If the number of requested items is greater than
        `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_credential_info, None, {"token": token}, request_options)

    def enable_credential(self, *, token: ReferenceToken, request_options: RequestOptions | None = None) -> None:
        """This operation shall enable a credential.

        This function must be available if the `DisableCredential` service capability is true.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.enable_credential, None, {"token": token}, request_options)

    def disable_credential(
        self,
        *,
        token: ReferenceToken,
        status: CredentialStatusEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation shall disable a credential.

        This function must be available if the `DisableCredential` service capability is true.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.disable_credential, None, {"token": token, "status": status}, request_options)

    def get_credential_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCredentialListResult:
        """This operation requests a list of all `Credential` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter. This
        function must be available if the `GetCredential` service capability is true. > INFO > > This could
        be a security risk.

        Access: admin.
        """
        return self._run(
            OPS.get_credential_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_credential(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetCredentialResult:
        """This operation requests a list of `Credential` items matching the given tokens.

        This method shall be supported if the `GetCredential` service capability is true. At least one token
        shall be specified. The device shall ignore tokens it cannot resolve and may return an empty list if
        there are no items matching specified tokens. If the number of requested items is greater than
        `MaxLimit`, a `TooManyItems` fault shall be returned. > INFO > > This could be a security risk.

        Access: admin.
        """
        return self._run(OPS.get_credential, None, {"token": token}, request_options)

    @overload
    def set_credential(
        self, request: SetCredentialRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetCredentialResult: ...
    @overload
    def set_credential(
        self, /, *, credential: list[Credential], request_options: RequestOptions | None = None
    ) -> SetCredentialResult: ...
    def set_credential(
        self,
        request: SetCredentialRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetCredentialResult:
        """Add/update a list of `Credential` items.

        If `Credential` items with the specified tokens already exist, they shall be updated. If not, they
        shall be added. If the `Token` field of any Credential item is empty, the service shall allocate a
        token for the `Credential`. All tokens shall be returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_credential, request, kwargs, request_options)

    def remove_credential(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """Remove the specified `Credential` items. Access: admin."""
        self._run(OPS.remove_credential, None, {"token": token}, request_options)

    def get_access_profile_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessProfileInfoListResult:
        """This operation requests a list of all `AccessProfileInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter. This
        function is mandatory.

        Access: admin.
        """
        return self._run(
            OPS.get_access_profile_info_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_access_profile_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessProfileInfoResult:
        """This operation requests a list of `AccessProfileInfo` items matching the given tokens.

        This method shall be supported if the `GetAccessProfile` service capability is true. At least one
        token shall be specified. The device shall ignore tokens it cannot resolve and may return an empty
        list if there are no items matching specified tokens. If the number of requested items is greater
        than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_access_profile_info, None, {"token": token}, request_options)

    def get_access_profile_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessProfileListResult:
        """This operation requests a list of all of `AccessProfile` items provided by the device.

        This function shall be implemented if the `GetAccessProfile` service capability is true. A call to
        this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_access_profile_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_access_profile(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessProfileResult:
        """This operation requests a list of `AccessProfile` items matching the given tokens.

        This method shall be supported if the `GetAccessProfile` service capability is true. At least one
        token shall be specified. The device shall ignore tokens it cannot resolve and may return an empty
        list if there are no items matching specified tokens. If the number of requested items is greater
        than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_access_profile, None, {"token": token}, request_options)

    @overload
    def set_access_profile(
        self, request: SetAccessProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessProfileResult: ...
    @overload
    def set_access_profile(
        self, /, *, access_profile: list[AccessProfile], request_options: RequestOptions | None = None
    ) -> SetAccessProfileResult: ...
    def set_access_profile(
        self,
        request: SetAccessProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessProfileResult:
        """Add/update a list of `AccessProfile` items.

        If `AccessProfile` items with the specified tokens already exist, they will be updated. If not, they
        shall be added. If the `Token` field of any `AccessProfile` is empty, the service shall allocate a
        token for the `AccessProfile`. All tokens shall be returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_access_profile, request, kwargs, request_options)

    def remove_access_profile(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessProfile` items. Access: admin."""
        self._run(OPS.remove_access_profile, None, {"token": token}, request_options)

    def get_authentication_profile_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAuthenticationProfileInfoListResult:
        """This operation requests a list of all `AuthenticationProfileInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_authentication_profile_info_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_authentication_profile_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAuthenticationProfileInfoResult:
        """This operation requests a list of `AuthenticationProfileInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_authentication_profile_info, None, {"token": token}, request_options)

    def get_authentication_profile_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAuthenticationProfileListResult:
        """This operation requests a list of all `AuthenticationProfile` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_authentication_profile_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_authentication_profile(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAuthenticationProfileResult:
        """This operation requests a list of `AuthenticationProfile` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_authentication_profile, None, {"token": token}, request_options)

    @overload
    def set_authentication_profile(
        self, request: SetAuthenticationProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAuthenticationProfileResult: ...
    @overload
    def set_authentication_profile(
        self, /, *, authentication_profile: list[AuthenticationProfile], request_options: RequestOptions | None = None
    ) -> SetAuthenticationProfileResult: ...
    def set_authentication_profile(
        self,
        request: SetAuthenticationProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAuthenticationProfileResult:
        """Set (adds or modifies) the supplied list of `AuthenticationProfile` items to the internal storage/database.

        If the token attribute is empty, a new unique token will be generated by the service. All supplied
        and generated tokens are returned.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_authentication_profile, request, kwargs, request_options)

    def remove_authentication_profile(
        self, *, token: list[ReferenceToken] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AuthenticationProfile` items. Access: admin."""
        self._run(OPS.remove_authentication_profile, None, {"token": token}, request_options)

    def get_id_match_operators(self, *, request_options: RequestOptions | None = None) -> GetIdMatchOperatorsResult:
        """Returns the `IdMatchOperator` items supported by the service. Access: admin."""
        return self._run(OPS.get_id_match_operators, None, {}, request_options)

    def get_rule_operators(self, *, request_options: RequestOptions | None = None) -> GetRuleOperatorsResult:
        """Returns the `RuleOperator` items supported by the service. Access: admin."""
        return self._run(OPS.get_rule_operators, None, {}, request_options)

    def get_access_controller_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessControllerConfigurationListResult:
        """This operation requests a list of all of `AccessControllerConfiguration` items provided by the device.

        Access: admin.
        """
        return self._run(
            OPS.get_access_controller_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_access_controller_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessControllerConfigurationResult:
        """This operation request a list of `AccessControllerConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than the max limit supported,
        a `TooManyItems` fault shall be returned

        Access: admin.
        """
        return self._run(OPS.get_access_controller_configuration, None, {"token": token}, request_options)

    @overload
    def set_access_controller_configuration(
        self, request: SetAccessControllerConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessControllerConfigurationResult: ...
    @overload
    def set_access_controller_configuration(
        self,
        /,
        *,
        access_controller_configuration: list[AccessControllerConfiguration],
        request_options: RequestOptions | None = None,
    ) -> SetAccessControllerConfigurationResult: ...
    def set_access_controller_configuration(
        self,
        request: SetAccessControllerConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessControllerConfigurationResult:
        """Add/update a list of `AccessControllerConfiguration` items.

        If `AccessController` items with the specified tokens already exist, they will be updated. If not,
        they will be added. If the `Token` field of any `AccessController` is empty, the service will
        allocate a token for the `AccessController`. All tokens are returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_access_controller_configuration, request, kwargs, request_options)

    def remove_access_controller_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessControllerConfiguration` items. Access: admin."""
        self._run(OPS.remove_access_controller_configuration, None, {"token": token}, request_options)

    def get_credential_statistics(
        self, *, request_options: RequestOptions | None = None
    ) -> GetCredentialStatisticsResult:
        """Get statistics related to the `Credential` items in the system. Access: admin."""
        return self._run(OPS.get_credential_statistics, None, {}, request_options)

    def get_master_db_state(self, *, request_options: RequestOptions | None = None) -> GetMasterDbStateResult:
        """Returns the current state of the `MasterDB`. Access: admin."""
        return self._run(OPS.get_master_db_state, None, {}, request_options)

    def re_open_master_db(self, *, request_options: RequestOptions | None = None) -> ReOpenMasterDbResult:
        """Reopens the `MasterDB`, optionally: \\* deleting the current database \\* opening the new one in a specified path and \\* enabling encryption with a specific key.

        Access: admin.
        """
        return self._run(OPS.re_open_master_db, None, {}, request_options)

    def reset_antipassback_violation(
        self, *, credential_token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> None:
        """Reset anti-passback for the specified credential(s).

        If the credential is currently not in anti-passback violation, nothing happens.

        Access: admin.
        """
        self._run(OPS.reset_antipassback_violation, None, {"credential_token": credential_token}, request_options)

    def reset_all_antipassback_violations(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset anti-passback for all credentials. Access: admin."""
        self._run(OPS.reset_all_antipassback_violations, None, {}, request_options)

    def get_antipassback_data_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAntipassbackDataListResult:
        """This operation requests a list of all of `AntipassbackData` items provided by the device.

        Access: admin.
        """
        return self._run(
            OPS.get_antipassback_data_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    @overload
    def set_antipassback_data(
        self, request: SetAntipassbackDataRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_antipassback_data(
        self, /, *, antipassback_data: list[AntipassbackData], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_antipassback_data(
        self,
        request: SetAntipassbackDataRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """set_antipassback_data.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_antipassback_data, request, kwargs, request_options)


class AsyncAccessControlServiceApi(AsyncApi):
    """Access control service (``access-control-service``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """This operation returns the capabilities of the Access Control service.

        An ONVIF compliant device which provides the Access Control service shall implement this method.

        Access: anonymous.
        """
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def get_access_point_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessPointInfoListResult:
        """This operation requests a list of all `AccessPointInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_access_point_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_access_point_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessPointInfoResult:
        """This operation requests a list of `AccessPointInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_access_point_info, None, {"token": token}, request_options)

    async def get_area_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAreaInfoListResult:
        """This operation requests a list of all `AreaInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_area_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_area_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAreaInfoResult:
        """This operation requests a list of `AreaInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_area_info, None, {"token": token}, request_options)

    async def get_access_point_state(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetAccessPointStateResult:
        """This operation requests the `AccessPointState` for the `AccessPoint` instance specified by token.

        An ONVIF compliant device that provides Access Control service shall implement this method.

        Access: admin.
        """
        return await self._run(OPS.get_access_point_state, None, {"token": token}, request_options)

    async def enable_access_point(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> None:
        """This operation allows enabling an access point.

        A device that signals support for `DisableAccessPoint` capability for a particular `AccessPoint`
        instance shall implement this command.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.enable_access_point, None, {"token": token}, request_options)

    async def disable_access_point(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> None:
        """This operation allows disabling an access point.

        A device that signals support for `DisableAccessPoint` capability for a particular `AccessPoint`
        instance shall implement this command.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.disable_access_point, None, {"token": token}, request_options)

    async def external_authorization(
        self,
        *,
        access_point_token: ReferenceToken,
        credential_token: ReferenceToken | MISSING = MISSING,
        reason: str | MISSING = MISSING,
        decision: Decision,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows to deny or grant decision at an `AccessPoint` instance.

        A device that signals support for `ExternalAuthorization` capability for a particular `AccessPoint`
        instance shall implement this method.

        Access: admin.
        """
        await self._run(
            OPS.external_authorization,
            None,
            {
                "access_point_token": access_point_token,
                "credential_token": credential_token,
                "reason": reason,
                "decision": decision,
            },
            request_options,
        )

    async def get_access_point_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessPointListResult:
        """This operation requests a list of all of `AccessPoint` items provided by the device.

        This function shall be implemented if the `GetAccessPoint` service capability is true. A call to
        this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_access_point_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_access_point(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessPointResult:
        """This operation requests a list of `AccessPoint` items matching the given tokens.

        This method shall be supported if the `GetAccessPoint` service capability is true. At least one
        token shall be specified. The device shall ignore tokens it cannot resolve and may return an empty
        list if there are no items matching specified tokens. If the number of requested items is greater
        than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_access_point, None, {"token": token}, request_options)

    @overload
    async def set_access_point(
        self, request: SetAccessPointRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessPointResult: ...
    @overload
    async def set_access_point(
        self, /, *, access_point: list[AccessPoint], request_options: RequestOptions | None = None
    ) -> SetAccessPointResult: ...
    async def set_access_point(
        self,
        request: SetAccessPointRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessPointResult:
        """Add/update a list of `AccessPoint` items.

        If `AccessPoint` items with the specified tokens already exist, they shall be updated. If not, they
        shall be added. If the token field of any `AccessPoint` is empty, the service shall allocate a token
        for the `AccessPoint`. All tokens shall be returned in the response. This function must be available
        if the `SetAccessPoint` service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_access_point, request, kwargs, request_options)

    async def remove_access_point(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessPoint` items.

        This function must be available if the `RemoveAccessPoint` service capability is true.

        Access: admin.
        """
        await self._run(OPS.remove_access_point, None, {"token": token}, request_options)

    async def get_area_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAreaListResult:
        """This operation requests a list of all of `Area` items provided by the device.

        This function shall be implemented if the `GetArea` service capability is true. A call to this
        method shall return a `StartReference` when not all data is returned and more data is available. The
        reference shall be valid for retrieving the next set of data. See section Retrieving system
        configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_area_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_area(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAreaResult:
        """This operation requests a list of `Area` items matching the given tokens.

        This method shall be supported if the `GetArea` service capability is true. At least one token shall
        be specified. The device shall ignore tokens it cannot resolve and may return an empty list if there
        are no items matching specified tokens. If the number of requested items is greater than `MaxLimit`,
        a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_area, None, {"token": token}, request_options)

    @overload
    async def set_area(
        self, request: SetAreaRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAreaResult: ...
    @overload
    async def set_area(
        self, /, *, area: list[Area], request_options: RequestOptions | None = None
    ) -> SetAreaResult: ...
    async def set_area(
        self, request: SetAreaRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetAreaResult:
        """Add/update a list of `Area` items.

        If `Area` with the specified tokens already exist, they shall be updated. If not, they shall be
        added. If the token field of any `Area` is empty, the service shall allocate a token for the `Area`.
        All tokens shall be returned in the response. This function must be available if the `SetArea`
        service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_area, request, kwargs, request_options)

    async def remove_area(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """Remove the specified `Area` items.

        This function must be available if the `RemoveArea` service capability is true.

        Access: admin.
        """
        await self._run(OPS.remove_area, None, {"token": token}, request_options)

    async def get_access_controller_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessControllerInfoListResult:
        """This operation requests a list of all `AccessControllerInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_access_controller_info_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_access_controller_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessControllerInfoResult:
        """This operation requests a list of `AccessControllerInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_access_controller_info, None, {"token": token}, request_options)

    async def get_access_controller_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessControllerListResult:
        """This operation requests a list of all `AccessController` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_access_controller_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_access_controller(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessControllerResult:
        """This operation requests a list of `AccessController` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_access_controller, None, {"token": token}, request_options)

    @overload
    async def set_access_controller(
        self, request: SetAccessControllerRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessControllerResult: ...
    @overload
    async def set_access_controller(
        self, /, *, access_controller: list[AccessController], request_options: RequestOptions | None = None
    ) -> SetAccessControllerResult: ...
    async def set_access_controller(
        self,
        request: SetAccessControllerRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessControllerResult:
        """Add/update a list of `AccessController` items.

        If `AccessController` items with the specified tokens already exist, they shall be updated. If not,
        they shall be added. If the `Token` field of any `AccessController` is empty, the service shall
        allocate a token for the `AccessController`. All tokens shall be returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_access_controller, request, kwargs, request_options)

    async def remove_access_controller(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessController` items. Access: admin."""
        await self._run(OPS.remove_access_controller, None, {"token": token}, request_options)

    async def get_standard_attribute_list(
        self, *, request_options: RequestOptions | None = None
    ) -> GetStandardAttributeListResult:
        """Returns a list of attributes and their value type supported by the service. Access: admin."""
        return await self._run(OPS.get_standard_attribute_list, None, {}, request_options)

    async def get_vendor_attribute_list(
        self, *, request_options: RequestOptions | None = None
    ) -> GetVendorAttributeListResult:
        """This function shall return the vendor specific attributes supported. Access: admin."""
        return await self._run(OPS.get_vendor_attribute_list, None, {}, request_options)

    @overload
    async def verify_request(
        self, request: VerifyRequestRequest, /, *, request_options: RequestOptions | None = None
    ) -> VerifyRequestResult: ...
    @overload
    async def verify_request(
        self,
        /,
        *,
        token: ReferenceToken,
        id_data: list[IdData] | MISSING = MISSING,
        source_token: ReferenceToken | MISSING = MISSING,
        target_token: ReferenceToken | MISSING = MISSING,
        action: str | MISSING = MISSING,
        environment: list[NameValue] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> VerifyRequestResult: ...
    async def verify_request(
        self,
        request: VerifyRequestRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> VerifyRequestResult:
        """Perform a validation of the request, and return the result, but does not perform any action.

        Access: admin.
        """
        return await self._run(OPS.verify_request, request, kwargs, request_options)

    @overload
    async def request_access(
        self, request: RequestAccessRequest, /, *, request_options: RequestOptions | None = None
    ) -> RequestAccessResult: ...
    @overload
    async def request_access(
        self,
        /,
        *,
        token: ReferenceToken,
        id_data: list[IdData] | MISSING = MISSING,
        source_token: ReferenceToken | MISSING = MISSING,
        target_token: ReferenceToken | MISSING = MISSING,
        action: str | MISSING = MISSING,
        environment: list[NameValue] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RequestAccessResult: ...
    async def request_access(
        self,
        request: RequestAccessRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> RequestAccessResult:
        """Request access to the specified `Resource` with the given `IdField` items. Access: admin."""
        return await self._run(OPS.request_access, request, kwargs, request_options)

    async def get_credential_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCredentialInfoListResult:
        """This operation requests a list of all `CredentialInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter. This
        function must be available if the `GetCredentialListSupported` service capability is true.

        Access: admin.
        """
        return await self._run(
            OPS.get_credential_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_credential_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetCredentialInfoResult:
        """This operation requests a list of `CredentialInfo` items matching the given tokens.

        This method shall be supported if the `GetCredential` service capability is true. At least one token
        shall be specified. The device shall ignore tokens it cannot resolve and may return an empty list if
        there are no items matching specified tokens. If the number of requested items is greater than
        `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_credential_info, None, {"token": token}, request_options)

    async def enable_credential(self, *, token: ReferenceToken, request_options: RequestOptions | None = None) -> None:
        """This operation shall enable a credential.

        This function must be available if the `DisableCredential` service capability is true.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.enable_credential, None, {"token": token}, request_options)

    async def disable_credential(
        self,
        *,
        token: ReferenceToken,
        status: CredentialStatusEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation shall disable a credential.

        This function must be available if the `DisableCredential` service capability is true.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.disable_credential, None, {"token": token, "status": status}, request_options)

    async def get_credential_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCredentialListResult:
        """This operation requests a list of all `Credential` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter. This
        function must be available if the `GetCredential` service capability is true. > INFO > > This could
        be a security risk.

        Access: admin.
        """
        return await self._run(
            OPS.get_credential_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_credential(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetCredentialResult:
        """This operation requests a list of `Credential` items matching the given tokens.

        This method shall be supported if the `GetCredential` service capability is true. At least one token
        shall be specified. The device shall ignore tokens it cannot resolve and may return an empty list if
        there are no items matching specified tokens. If the number of requested items is greater than
        `MaxLimit`, a `TooManyItems` fault shall be returned. > INFO > > This could be a security risk.

        Access: admin.
        """
        return await self._run(OPS.get_credential, None, {"token": token}, request_options)

    @overload
    async def set_credential(
        self, request: SetCredentialRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetCredentialResult: ...
    @overload
    async def set_credential(
        self, /, *, credential: list[Credential], request_options: RequestOptions | None = None
    ) -> SetCredentialResult: ...
    async def set_credential(
        self,
        request: SetCredentialRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetCredentialResult:
        """Add/update a list of `Credential` items.

        If `Credential` items with the specified tokens already exist, they shall be updated. If not, they
        shall be added. If the `Token` field of any Credential item is empty, the service shall allocate a
        token for the `Credential`. All tokens shall be returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_credential, request, kwargs, request_options)

    async def remove_credential(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `Credential` items. Access: admin."""
        await self._run(OPS.remove_credential, None, {"token": token}, request_options)

    async def get_access_profile_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessProfileInfoListResult:
        """This operation requests a list of all `AccessProfileInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter. This
        function is mandatory.

        Access: admin.
        """
        return await self._run(
            OPS.get_access_profile_info_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_access_profile_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessProfileInfoResult:
        """This operation requests a list of `AccessProfileInfo` items matching the given tokens.

        This method shall be supported if the `GetAccessProfile` service capability is true. At least one
        token shall be specified. The device shall ignore tokens it cannot resolve and may return an empty
        list if there are no items matching specified tokens. If the number of requested items is greater
        than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_access_profile_info, None, {"token": token}, request_options)

    async def get_access_profile_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessProfileListResult:
        """This operation requests a list of all of `AccessProfile` items provided by the device.

        This function shall be implemented if the `GetAccessProfile` service capability is true. A call to
        this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_access_profile_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_access_profile(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessProfileResult:
        """This operation requests a list of `AccessProfile` items matching the given tokens.

        This method shall be supported if the `GetAccessProfile` service capability is true. At least one
        token shall be specified. The device shall ignore tokens it cannot resolve and may return an empty
        list if there are no items matching specified tokens. If the number of requested items is greater
        than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_access_profile, None, {"token": token}, request_options)

    @overload
    async def set_access_profile(
        self, request: SetAccessProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessProfileResult: ...
    @overload
    async def set_access_profile(
        self, /, *, access_profile: list[AccessProfile], request_options: RequestOptions | None = None
    ) -> SetAccessProfileResult: ...
    async def set_access_profile(
        self,
        request: SetAccessProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessProfileResult:
        """Add/update a list of `AccessProfile` items.

        If `AccessProfile` items with the specified tokens already exist, they will be updated. If not, they
        shall be added. If the `Token` field of any `AccessProfile` is empty, the service shall allocate a
        token for the `AccessProfile`. All tokens shall be returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_access_profile, request, kwargs, request_options)

    async def remove_access_profile(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessProfile` items. Access: admin."""
        await self._run(OPS.remove_access_profile, None, {"token": token}, request_options)

    async def get_authentication_profile_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAuthenticationProfileInfoListResult:
        """This operation requests a list of all `AuthenticationProfileInfo` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_authentication_profile_info_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_authentication_profile_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAuthenticationProfileInfoResult:
        """This operation requests a list of `AuthenticationProfileInfo` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_authentication_profile_info, None, {"token": token}, request_options)

    async def get_authentication_profile_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAuthenticationProfileListResult:
        """This operation requests a list of all `AuthenticationProfile` items provided by the device.

        An ONVIF compliant device which provides the Access Control service shall implement this method. A
        call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. See section Retrieving
        system configuration. The number of items returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_authentication_profile_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_authentication_profile(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAuthenticationProfileResult:
        """This operation requests a list of `AuthenticationProfile` items matching the given tokens.

        An ONVIF compliant device which provides Access Control service shall implement this method. The
        device shall ignore tokens it cannot resolve and shall return an empty list if there are no items
        matching specified tokens. The device shall not return a fault in this case. If the number of
        requested items is greater than `MaxLimit`, a `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_authentication_profile, None, {"token": token}, request_options)

    @overload
    async def set_authentication_profile(
        self, request: SetAuthenticationProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAuthenticationProfileResult: ...
    @overload
    async def set_authentication_profile(
        self, /, *, authentication_profile: list[AuthenticationProfile], request_options: RequestOptions | None = None
    ) -> SetAuthenticationProfileResult: ...
    async def set_authentication_profile(
        self,
        request: SetAuthenticationProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAuthenticationProfileResult:
        """Set (adds or modifies) the supplied list of `AuthenticationProfile` items to the internal storage/database.

        If the token attribute is empty, a new unique token will be generated by the service. All supplied
        and generated tokens are returned.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_authentication_profile, request, kwargs, request_options)

    async def remove_authentication_profile(
        self, *, token: list[ReferenceToken] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AuthenticationProfile` items. Access: admin."""
        await self._run(OPS.remove_authentication_profile, None, {"token": token}, request_options)

    async def get_id_match_operators(
        self, *, request_options: RequestOptions | None = None
    ) -> GetIdMatchOperatorsResult:
        """Returns the `IdMatchOperator` items supported by the service. Access: admin."""
        return await self._run(OPS.get_id_match_operators, None, {}, request_options)

    async def get_rule_operators(self, *, request_options: RequestOptions | None = None) -> GetRuleOperatorsResult:
        """Returns the `RuleOperator` items supported by the service. Access: admin."""
        return await self._run(OPS.get_rule_operators, None, {}, request_options)

    async def get_access_controller_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAccessControllerConfigurationListResult:
        """This operation requests a list of all of `AccessControllerConfiguration` items provided by the device.

        Access: admin.
        """
        return await self._run(
            OPS.get_access_controller_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_access_controller_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetAccessControllerConfigurationResult:
        """This operation request a list of `AccessControllerConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than the max limit supported,
        a `TooManyItems` fault shall be returned

        Access: admin.
        """
        return await self._run(OPS.get_access_controller_configuration, None, {"token": token}, request_options)

    @overload
    async def set_access_controller_configuration(
        self, request: SetAccessControllerConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetAccessControllerConfigurationResult: ...
    @overload
    async def set_access_controller_configuration(
        self,
        /,
        *,
        access_controller_configuration: list[AccessControllerConfiguration],
        request_options: RequestOptions | None = None,
    ) -> SetAccessControllerConfigurationResult: ...
    async def set_access_controller_configuration(
        self,
        request: SetAccessControllerConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetAccessControllerConfigurationResult:
        """Add/update a list of `AccessControllerConfiguration` items.

        If `AccessController` items with the specified tokens already exist, they will be updated. If not,
        they will be added. If the `Token` field of any `AccessController` is empty, the service will
        allocate a token for the `AccessController`. All tokens are returned in the response.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_access_controller_configuration, request, kwargs, request_options)

    async def remove_access_controller_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `AccessControllerConfiguration` items. Access: admin."""
        await self._run(OPS.remove_access_controller_configuration, None, {"token": token}, request_options)

    async def get_credential_statistics(
        self, *, request_options: RequestOptions | None = None
    ) -> GetCredentialStatisticsResult:
        """Get statistics related to the `Credential` items in the system. Access: admin."""
        return await self._run(OPS.get_credential_statistics, None, {}, request_options)

    async def get_master_db_state(self, *, request_options: RequestOptions | None = None) -> GetMasterDbStateResult:
        """Returns the current state of the `MasterDB`. Access: admin."""
        return await self._run(OPS.get_master_db_state, None, {}, request_options)

    async def re_open_master_db(self, *, request_options: RequestOptions | None = None) -> ReOpenMasterDbResult:
        """Reopens the `MasterDB`, optionally: \\* deleting the current database \\* opening the new one in a specified path and \\* enabling encryption with a specific key.

        Access: admin.
        """
        return await self._run(OPS.re_open_master_db, None, {}, request_options)

    async def reset_antipassback_violation(
        self, *, credential_token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> None:
        """Reset anti-passback for the specified credential(s).

        If the credential is currently not in anti-passback violation, nothing happens.

        Access: admin.
        """
        await self._run(OPS.reset_antipassback_violation, None, {"credential_token": credential_token}, request_options)

    async def reset_all_antipassback_violations(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset anti-passback for all credentials. Access: admin."""
        await self._run(OPS.reset_all_antipassback_violations, None, {}, request_options)

    async def get_antipassback_data_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAntipassbackDataListResult:
        """This operation requests a list of all of `AntipassbackData` items provided by the device.

        Access: admin.
        """
        return await self._run(
            OPS.get_antipassback_data_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    @overload
    async def set_antipassback_data(
        self, request: SetAntipassbackDataRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_antipassback_data(
        self, /, *, antipassback_data: list[AntipassbackData], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_antipassback_data(
        self,
        request: SetAntipassbackDataRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """set_antipassback_data.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_antipassback_data, request, kwargs, request_options)
