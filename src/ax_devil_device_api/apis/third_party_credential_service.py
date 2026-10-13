# GENERATED from specs/apis/physical-access-control/third-party-credential-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The third party credential service handles credentials that are issued by third-party providers, as opposed to the normal credential management provided by the...

Docs: https://developer.axis.com/vapix/physical-access-control/third-party-credential-service/
"""

from __future__ import annotations

from typing import Any, ClassVar, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ServiceDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ReferenceToken = str


class Attribute(Model):
    """A name with an optional value and type."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the attribute."""
    type: str | None = None
    """Type of the value: `int`, `bool` or `string`."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """Value of the attribute."""


class ConfigurationInfo(Model):
    """A configuration setting and its description."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the setting."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """Value of the setting."""
    enums: list[str] | None = Field(default=None, validation_alias="Enums", serialization_alias="Enums")
    """Suggested or allowed values."""
    type: str | None = Field(default=None, validation_alias="Type", serialization_alias="Type")
    """Type of the setting, for example `string`."""
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


class HIDMobilePartNumberInfo(Model):
    """A part number of the HID Mobile Access account."""

    token: str | None = None
    """Unique id of the part number. Use it as `DefaultPartNumberToken`."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Human readable name of the part number."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the part number."""
    quantity: int | None = Field(default=None, validation_alias="Quantity", serialization_alias="Quantity")
    """The number of mobile IDs (card numbers) that can still be issued from the part number."""


class HIDMobileConfiguration(Model):
    """Configuration of the HID Mobile Access credential provider. An empty configuration disables the provider."""

    part_numbers: list[HIDMobilePartNumberInfo] | None = Field(
        default=None, validation_alias="PartNumbers", serialization_alias="PartNumbers"
    )
    """The part numbers of the account. Only returned by get_provider_configuration."""
    client_id: str | None = Field(default=None, validation_alias="ClientId", serialization_alias="ClientId")
    """The client id (login) of the HID Mobile Access account."""
    client_secret: str | None = Field(default=None, validation_alias="ClientSecret", serialization_alias="ClientSecret")
    """The password of the HID Mobile Access account. Shown as `***` in responses."""
    proxy_url: str | None = Field(default=None, validation_alias="ProxyURL", serialization_alias="ProxyURL")
    """HTTP(S) proxy URL."""
    proxy_port: str | None = Field(default=None, validation_alias="ProxyPort", serialization_alias="ProxyPort")
    """HTTP(S) proxy port."""
    proxy_user: str | None = Field(default=None, validation_alias="ProxyUser", serialization_alias="ProxyUser")
    """HTTP(S) proxy user name."""
    proxy_password: str | None = Field(
        default=None, validation_alias="ProxyPassword", serialization_alias="ProxyPassword"
    )
    """HTTP(S) proxy password."""
    default_part_number_token: str | None = Field(
        default=None, validation_alias="DefaultPartNumberToken", serialization_alias="DefaultPartNumberToken"
    )
    """Token of the part number to use when `set_third_party_credential` names none."""
    portal_api_url: str | None = Field(
        default=None, validation_alias="PortalApiURL", serialization_alias="PortalApiURL"
    )
    """URL of the HID Mobile Access portal API. Only to override the built-in default."""
    idp_url: str | None = Field(default=None, validation_alias="IdpURL", serialization_alias="IdpURL")
    """URL of the HID Mobile Access authentication API. Only to override the built-in default."""
    card_id_data_name: str | None = Field(
        default=None, validation_alias="CardIdDataName", serialization_alias="CardIdDataName"
    )
    """Name of the credential IdData element that receives the card number. Default `CardNr`."""


class ProviderConfigurationInfo(Model):
    """Wrapper for the configuration of each provider."""

    hid_mobile_config: HIDMobileConfiguration | None = Field(
        default=None, validation_alias="HIDMobileConfig", serialization_alias="HIDMobileConfig"
    )
    """Configuration of HID Mobile Access."""


class HIDMobileOptions(Model):
    """HID Mobile Access options of a credential."""

    part_number_token: str | None = Field(
        default=None, validation_alias="PartNumberToken", serialization_alias="PartNumberToken"
    )
    """Token of the part number used to create the credential's mobile id."""
    invitation_code: str | None = Field(
        default=None, validation_alias="InvitationCode", serialization_alias="InvitationCode"
    )
    """The invitation code sent to the user's e-mail address; it can be entered by hand in the HID Mobile Access app."""


class ThirdPartyOptions(Model):
    """Wrapper for the provider specific options of a credential."""

    hid_mobile_options: HIDMobileOptions | None = Field(
        default=None, validation_alias="HIDMobileOptions", serialization_alias="HIDMobileOptions"
    )
    """Options of HID Mobile Access."""


class IdData(Model):
    """One identification value of a credential, for example a card number or a PIN."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the field, for example `CardNr` or `PIN`."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """The value to match against."""


class CredentialAccessProfile(Model):
    """A reference to an access profile, optionally restricted in time."""

    access_profile: ReferenceToken | None = Field(
        default=None, validation_alias="AccessProfile", serialization_alias="AccessProfile"
    )
    """Token of the access profile."""
    valid_from: str | None = Field(default=None, validation_alias="ValidFrom", serialization_alias="ValidFrom")
    """Start of the validity period. Empty or null for no restriction."""
    valid_to: str | None = Field(default=None, validation_alias="ValidTo", serialization_alias="ValidTo")
    """End of the validity period. Empty or null for no restriction."""


class Credential(Model):
    """A regular access control credential, as returned by the device."""

    token: ReferenceToken
    """A service-unique identifier of the credential."""
    user_token: str | None = Field(default=None, validation_alias="UserToken", serialization_alias="UserToken")
    """Token of the user of the credential."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the credential."""
    valid_from: str | None = Field(default=None, validation_alias="ValidFrom", serialization_alias="ValidFrom")
    """When the credential starts to be valid. Empty or null for no restriction."""
    valid_to: str | None = Field(default=None, validation_alias="ValidTo", serialization_alias="ValidTo")
    """When the credential stops being valid. Empty or null for no restriction."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the credential is enabled."""
    status: str | None = Field(default=None, validation_alias="Status", serialization_alias="Status")
    """Status of the credential, for example `Enabled`, or `NotActivated` until the provider has issued a card."""
    id_data: list[IdData] | None = Field(default=None, validation_alias="IdData", serialization_alias="IdData")
    """The identification data of the credential."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes of the credential. For HID Mobile Access `Email`, `FirstName` and `LastName` are needed to create a mobile user."""
    authentication_profile: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile"
    )
    """Overrides the authentication profiles of the access profiles."""
    credential_access_profile: list[CredentialAccessProfile] | None = Field(
        default=None, validation_alias="CredentialAccessProfile", serialization_alias="CredentialAccessProfile"
    )
    """The access profiles of the credential."""


class CredentialInput(Model):
    """A regular access control credential to create."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"valid_from", "valid_to"})
    token: ReferenceToken | None = None
    """Token of the credential."""
    user_token: str | None = Field(default=None, validation_alias="UserToken", serialization_alias="UserToken")
    """Token of the user of the credential."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the credential."""
    valid_from: str | None = Field(default=None, validation_alias="ValidFrom", serialization_alias="ValidFrom")
    """When the credential starts to be valid. Empty or null for no restriction."""
    valid_to: str | None = Field(default=None, validation_alias="ValidTo", serialization_alias="ValidTo")
    """When the credential stops being valid. Empty or null for no restriction."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the credential is enabled."""
    status: str | None = Field(default=None, validation_alias="Status", serialization_alias="Status")
    """Status of the credential."""
    id_data: list[IdData] | None = Field(default=None, validation_alias="IdData", serialization_alias="IdData")
    """The identification data of the credential. Do not set the id data the provider writes (`CardNr` by default); it is overwritten when the card is issued."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes of the credential. For HID Mobile Access `Email`, `FirstName` and `LastName` are needed to create a mobile user."""
    authentication_profile: list[ReferenceToken] | None = Field(
        default=None, validation_alias="AuthenticationProfile", serialization_alias="AuthenticationProfile"
    )
    """Overrides the authentication profiles of the access profiles."""
    credential_access_profile: list[CredentialAccessProfile] | None = Field(
        default=None, validation_alias="CredentialAccessProfile", serialization_alias="CredentialAccessProfile"
    )
    """The access profiles of the credential."""


class ThirdPartyCredential(Model):
    """A regular access control credential with the options of the third-party provider."""

    credential: Credential | None = Field(default=None, validation_alias="Credential", serialization_alias="Credential")
    """The regular access control credential."""
    options: ThirdPartyOptions | None = Field(default=None, validation_alias="Options", serialization_alias="Options")
    """Provider specific options."""


class ThirdPartyCredentialInput(Model):
    """A third-party credential to create."""

    credential: CredentialInput | None = Field(
        default=None, validation_alias="Credential", serialization_alias="Credential"
    )
    """The regular access control credential."""
    options: ThirdPartyOptions | None = Field(default=None, validation_alias="Options", serialization_alias="Options")
    """Provider specific options, for example the part number to generate the mobile id from."""


class ProvidersResult(Model):
    providers: list[ConfigurationInfo] | None = Field(
        default=None, validation_alias="Providers", serialization_alias="Providers"
    )
    """The supported credential providers."""


class GetProviderConfigurationRequest(Model):
    provider_name: ReferenceToken = Field(validation_alias="ProviderName", serialization_alias="ProviderName")
    """Provider to use, as returned by get_providers."""
    provider_actions: list[Attribute] | None = Field(
        default=None, validation_alias="ProviderActions", serialization_alias="ProviderActions"
    )
    """Additional actions and options for the provider."""


class GetProviderConfigurationResult(Model):
    configuration: ProviderConfigurationInfo = Field(
        validation_alias="Configuration", serialization_alias="Configuration"
    )
    """Configuration of the provider."""


class SetProviderConfigurationRequest(Model):
    provider_name: ReferenceToken = Field(validation_alias="ProviderName", serialization_alias="ProviderName")
    """Provider to use, as returned by get_providers."""
    provider_actions: list[Attribute] | None = Field(
        default=None, validation_alias="ProviderActions", serialization_alias="ProviderActions"
    )
    """Additional actions and options for the provider."""
    configuration: ProviderConfigurationInfo = Field(
        validation_alias="Configuration", serialization_alias="Configuration"
    )
    """Configuration of the provider. An empty `HIDMobileConfig` disables it."""


class SetThirdPartyCredentialRequest(Model):
    provider_name: ReferenceToken = Field(validation_alias="ProviderName", serialization_alias="ProviderName")
    """Provider to use, as returned by get_providers."""
    provider_actions: list[Attribute] | None = Field(
        default=None, validation_alias="ProviderActions", serialization_alias="ProviderActions"
    )
    """Additional actions and options for the provider, as `{Name: ...}` attributes: `ForceUpdate` forces an update to the HID Mobile service and overwrites any old user with the same e-mail, `SendInvitationOnly` only sends a new invitation e-mail and writes nothing locally, `NoLocalModification` leaves the access control credential unchanged when the card number has been issued."""
    third_party_credential: ThirdPartyCredentialInput = Field(
        validation_alias="ThirdPartyCredential", serialization_alias="ThirdPartyCredential"
    )
    """The credential to create."""


class TokenResult(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the added credential."""


class GetThirdPartyCredentialListRequest(Model):
    provider_name: ReferenceToken = Field(validation_alias="ProviderName", serialization_alias="ProviderName")
    """Provider to use, as returned by get_providers."""
    provider_actions: list[Attribute] | None = Field(
        default=None, validation_alias="ProviderActions", serialization_alias="ProviderActions"
    )
    """Additional actions and options for the provider."""
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If absent, or higher than the device supports, the device decides."""
    start_reference: ReferenceToken | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this reference."""


class ThirdPartyCredentialList(Model):
    next_start_reference: ReferenceToken | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    third_party_credentials: list[ThirdPartyCredential] | None = Field(
        default=None, validation_alias="ThirdPartyCredentials", serialization_alias="ThirdPartyCredentials"
    )
    """The credentials."""


class ThirdPartyCredentialTokenRequest(Model):
    provider_name: ReferenceToken = Field(validation_alias="ProviderName", serialization_alias="ProviderName")
    """Provider to use, as returned by get_providers."""
    provider_actions: list[Attribute] | None = Field(
        default=None, validation_alias="ProviderActions", serialization_alias="ProviderActions"
    )
    """Additional actions and options for the provider. For removal `NoLocalModification` removes only the third-party credential and keeps the local access control credential; for a get `ForceUpdate` also contacts the provider."""
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the credential."""


class ThirdPartyCredentialEmailRequest(Model):
    provider_name: ReferenceToken = Field(validation_alias="ProviderName", serialization_alias="ProviderName")
    """Provider to use, as returned by get_providers."""
    provider_actions: list[Attribute] | None = Field(
        default=None, validation_alias="ProviderActions", serialization_alias="ProviderActions"
    )
    """Additional actions and options for the provider. For removal `NoLocalModification` removes only the third-party credential and keeps the local access control credential; for a get `ForceUpdate` also contacts the provider."""
    email: str = Field(validation_alias="Email", serialization_alias="Email")
    """E-mail address of the credential."""


class ThirdPartyCredentialResult(Model):
    third_party_credential: ThirdPartyCredential = Field(
        validation_alias="ThirdPartyCredential", serialization_alias="ThirdPartyCredential"
    )
    """The requested credential."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/axtpc"

INFO = ApiInfo(
    id="third-party-credential-service",
    name="Third party credential service",
    family=Family.SERVICE_JSON,
    discovery=(ServiceDiscovery("http://www.axis.com/vapix/ws/thirdpartycredential"),),
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/third-party-credential-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/event-logger-service/",
        "https://developer.axis.com/vapix/physical-access-control/access-control-service/",
        "https://developer.axis.com/vapix/physical-access-control/door-control-service/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
    ),
    errors={
        "ter:NotFound": ErrorCode("The requested resource was not found", "not_found"),
        "ter:InvalidArgument": ErrorCode(
            "The request contained an invalid argument; the fault reason has more details", "invalid_argument"
        ),
        "ter:ResourceExists": ErrorCode("The requested resource already exists"),
        "ter:NetworkError": ErrorCode("Network error", "unavailable"),
        "ter:CurlError": ErrorCode("Unspecified CURL error"),
        "ter:ConnectionError": ErrorCode("Failed to connect to the network resource", "unavailable"),
        "ter:Timeout": ErrorCode("Network request timed out", "unavailable"),
        "ter:CredentialProviderError": ErrorCode("Error from the credential provider"),
        "ter:GeneralProviderError": ErrorCode(
            "Unspecified error when communicating with the provider; the fault reason has more details"
        ),
        "ter:AuthenticationFailed": ErrorCode(
            "Failed to authenticate with the credential provider; check the provider login credentials"
        ),
        "ter:Unavailable": ErrorCode("The credential provider is currently unavailable", "unavailable"),
        "ter:CriticalInternalError": ErrorCode("Critical internal error", "internal"),
    },
)


class OPS:
    get_providers = Operation(
        INFO,
        "get_providers",
        ServiceJsonBinding(PATH, "axtpc:GetProviders"),
        result=ProvidersResult,
        access="admin",
        effect="read",
    )
    get_provider_configuration = Operation(
        INFO,
        "get_provider_configuration",
        ServiceJsonBinding(PATH, "axtpc:GetProviderConfiguration"),
        params=GetProviderConfigurationRequest,
        result=GetProviderConfigurationResult,
        access="admin",
        effect="read",
    )
    set_provider_configuration = Operation(
        INFO,
        "set_provider_configuration",
        ServiceJsonBinding(PATH, "axtpc:SetProviderConfiguration"),
        params=SetProviderConfigurationRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_third_party_credential = Operation(
        INFO,
        "set_third_party_credential",
        ServiceJsonBinding(PATH, "axtpc:SetThirdPartyCredential"),
        params=SetThirdPartyCredentialRequest,
        result=TokenResult,
        access="admin",
        effect="write",
        write="create",
    )
    get_third_party_credential_list = Operation(
        INFO,
        "get_third_party_credential_list",
        ServiceJsonBinding(PATH, "axtpc:GetThirdPartyCredentialList"),
        params=GetThirdPartyCredentialListRequest,
        result=ThirdPartyCredentialList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning", "invalid_argument"
            )
        },
    )
    get_third_party_credential = Operation(
        INFO,
        "get_third_party_credential",
        ServiceJsonBinding(PATH, "axtpc:GetThirdPartyCredential"),
        params=ThirdPartyCredentialTokenRequest,
        result=ThirdPartyCredentialResult,
        access="admin",
        effect="read",
    )
    get_third_party_credential_by_email = Operation(
        INFO,
        "get_third_party_credential_by_email",
        ServiceJsonBinding(PATH, "axtpc:GetThirdPartyCredentialByEmail"),
        params=ThirdPartyCredentialEmailRequest,
        result=ThirdPartyCredentialResult,
        access="admin",
        effect="read",
    )
    remove_third_party_credential = Operation(
        INFO,
        "remove_third_party_credential",
        ServiceJsonBinding(PATH, "axtpc:RemoveThirdPartyCredential"),
        params=ThirdPartyCredentialTokenRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    remove_third_party_credential_by_email = Operation(
        INFO,
        "remove_third_party_credential_by_email",
        ServiceJsonBinding(PATH, "axtpc:RemoveThirdPartyCredentialByEmail"),
        params=ThirdPartyCredentialEmailRequest,
        access="admin",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class ThirdPartyCredentialServiceApi(SyncApi):
    """Third party credential service (``third-party-credential-service``)."""

    INFO = INFO

    def get_providers(self, *, request_options: RequestOptions | None = None) -> ProvidersResult:
        """Get the supported third-party credential providers.

        The `ProviderName` of the other calls must be one of the returned provider names. HID Mobile Access
        (`HIDMobileAccess`) is the only provider. The API is only supported by AXIS A1001.

        Access: admin.
        """
        return self._run(OPS.get_providers, None, {}, request_options)

    @overload
    def get_provider_configuration(
        self, request: GetProviderConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> GetProviderConfigurationResult: ...
    @overload
    def get_provider_configuration(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetProviderConfigurationResult: ...
    def get_provider_configuration(
        self,
        request: GetProviderConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> GetProviderConfigurationResult:
        """Get the configuration of a credential provider.

        The client secret is masked and the response lists the part numbers of the account.

        Access: admin.
        """
        return self._run(OPS.get_provider_configuration, request, kwargs, request_options)

    @overload
    def set_provider_configuration(
        self, request: SetProviderConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_provider_configuration(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        configuration: ProviderConfigurationInfo,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_provider_configuration(
        self,
        request: SetProviderConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the configuration of a credential provider.

        One configuration exists per provider; a new call overwrites it. An empty configuration disables the
        provider.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_provider_configuration, request, kwargs, request_options)

    @overload
    def set_third_party_credential(
        self, request: SetThirdPartyCredentialRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    def set_third_party_credential(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        third_party_credential: ThirdPartyCredentialInput,
        request_options: RequestOptions | None = None,
    ) -> TokenResult: ...
    def set_third_party_credential(
        self,
        request: SetThirdPartyCredentialRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Create a third-party credential, with its user, at a provider.

        Creates a user and a credential linked to it. The credential has status `NotActivated` until the
        provider has issued a card; for HID Mobile Access that happens when the user accepts the invitation
        sent to the `Email` attribute, usually a couple of minutes after. The `Email`, `FirstName` and
        `LastName` attributes are needed for a new HID Mobile user.

        Access: admin.
        """
        return self._run(OPS.set_third_party_credential, request, kwargs, request_options)

    @overload
    def get_third_party_credential_list(
        self, request: GetThirdPartyCredentialListRequest, /, *, request_options: RequestOptions | None = None
    ) -> ThirdPartyCredentialList: ...
    @overload
    def get_third_party_credential_list(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        start_reference: ReferenceToken | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ThirdPartyCredentialList: ...
    def get_third_party_credential_list(
        self,
        request: GetThirdPartyCredentialListRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ThirdPartyCredentialList:
        """List the third-party credentials of a provider.

        Pages through the credentials. Pass the returned `NextStartReference` as `StartReference` in the
        next call and never reuse a reference.

        Access: admin.
        """
        return self._run(OPS.get_third_party_credential_list, request, kwargs, request_options)

    @overload
    def get_third_party_credential(
        self, request: ThirdPartyCredentialTokenRequest, /, *, request_options: RequestOptions | None = None
    ) -> ThirdPartyCredentialResult: ...
    @overload
    def get_third_party_credential(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        token: ReferenceToken,
        request_options: RequestOptions | None = None,
    ) -> ThirdPartyCredentialResult: ...
    def get_third_party_credential(
        self,
        request: ThirdPartyCredentialTokenRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ThirdPartyCredentialResult:
        """Get a third-party credential by token.

        With the `ForceUpdate` provider action the call also asks the provider; normally the information is
        stored locally.

        Access: admin.
        """
        return self._run(OPS.get_third_party_credential, request, kwargs, request_options)

    @overload
    def get_third_party_credential_by_email(
        self, request: ThirdPartyCredentialEmailRequest, /, *, request_options: RequestOptions | None = None
    ) -> ThirdPartyCredentialResult: ...
    @overload
    def get_third_party_credential_by_email(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        email: str,
        request_options: RequestOptions | None = None,
    ) -> ThirdPartyCredentialResult: ...
    def get_third_party_credential_by_email(
        self,
        request: ThirdPartyCredentialEmailRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ThirdPartyCredentialResult:
        """Get a third-party credential by e-mail address. Access: admin."""
        return self._run(OPS.get_third_party_credential_by_email, request, kwargs, request_options)

    @overload
    def remove_third_party_credential(
        self, request: ThirdPartyCredentialTokenRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def remove_third_party_credential(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        token: ReferenceToken,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def remove_third_party_credential(
        self,
        request: ThirdPartyCredentialTokenRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove a third-party credential by token.

        With the `NoLocalModification` provider action only the third-party credential is removed and the
        local access control credential stays.

        Access: admin.
        """
        self._run(OPS.remove_third_party_credential, request, kwargs, request_options)

    @overload
    def remove_third_party_credential_by_email(
        self, request: ThirdPartyCredentialEmailRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def remove_third_party_credential_by_email(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        email: str,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def remove_third_party_credential_by_email(
        self,
        request: ThirdPartyCredentialEmailRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove a third-party credential by e-mail address.

        With the `NoLocalModification` provider action only the third-party credential is removed and the
        local access control credential stays.

        Access: admin.
        """
        self._run(OPS.remove_third_party_credential_by_email, request, kwargs, request_options)


class AsyncThirdPartyCredentialServiceApi(AsyncApi):
    """Third party credential service (``third-party-credential-service``)."""

    INFO = INFO

    async def get_providers(self, *, request_options: RequestOptions | None = None) -> ProvidersResult:
        """Get the supported third-party credential providers.

        The `ProviderName` of the other calls must be one of the returned provider names. HID Mobile Access
        (`HIDMobileAccess`) is the only provider. The API is only supported by AXIS A1001.

        Access: admin.
        """
        return await self._run(OPS.get_providers, None, {}, request_options)

    @overload
    async def get_provider_configuration(
        self, request: GetProviderConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> GetProviderConfigurationResult: ...
    @overload
    async def get_provider_configuration(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetProviderConfigurationResult: ...
    async def get_provider_configuration(
        self,
        request: GetProviderConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> GetProviderConfigurationResult:
        """Get the configuration of a credential provider.

        The client secret is masked and the response lists the part numbers of the account.

        Access: admin.
        """
        return await self._run(OPS.get_provider_configuration, request, kwargs, request_options)

    @overload
    async def set_provider_configuration(
        self, request: SetProviderConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_provider_configuration(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        configuration: ProviderConfigurationInfo,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_provider_configuration(
        self,
        request: SetProviderConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the configuration of a credential provider.

        One configuration exists per provider; a new call overwrites it. An empty configuration disables the
        provider.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_provider_configuration, request, kwargs, request_options)

    @overload
    async def set_third_party_credential(
        self, request: SetThirdPartyCredentialRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenResult: ...
    @overload
    async def set_third_party_credential(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        third_party_credential: ThirdPartyCredentialInput,
        request_options: RequestOptions | None = None,
    ) -> TokenResult: ...
    async def set_third_party_credential(
        self,
        request: SetThirdPartyCredentialRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenResult:
        """Create a third-party credential, with its user, at a provider.

        Creates a user and a credential linked to it. The credential has status `NotActivated` until the
        provider has issued a card; for HID Mobile Access that happens when the user accepts the invitation
        sent to the `Email` attribute, usually a couple of minutes after. The `Email`, `FirstName` and
        `LastName` attributes are needed for a new HID Mobile user.

        Access: admin.
        """
        return await self._run(OPS.set_third_party_credential, request, kwargs, request_options)

    @overload
    async def get_third_party_credential_list(
        self, request: GetThirdPartyCredentialListRequest, /, *, request_options: RequestOptions | None = None
    ) -> ThirdPartyCredentialList: ...
    @overload
    async def get_third_party_credential_list(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        start_reference: ReferenceToken | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ThirdPartyCredentialList: ...
    async def get_third_party_credential_list(
        self,
        request: GetThirdPartyCredentialListRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ThirdPartyCredentialList:
        """List the third-party credentials of a provider.

        Pages through the credentials. Pass the returned `NextStartReference` as `StartReference` in the
        next call and never reuse a reference.

        Access: admin.
        """
        return await self._run(OPS.get_third_party_credential_list, request, kwargs, request_options)

    @overload
    async def get_third_party_credential(
        self, request: ThirdPartyCredentialTokenRequest, /, *, request_options: RequestOptions | None = None
    ) -> ThirdPartyCredentialResult: ...
    @overload
    async def get_third_party_credential(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        token: ReferenceToken,
        request_options: RequestOptions | None = None,
    ) -> ThirdPartyCredentialResult: ...
    async def get_third_party_credential(
        self,
        request: ThirdPartyCredentialTokenRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ThirdPartyCredentialResult:
        """Get a third-party credential by token.

        With the `ForceUpdate` provider action the call also asks the provider; normally the information is
        stored locally.

        Access: admin.
        """
        return await self._run(OPS.get_third_party_credential, request, kwargs, request_options)

    @overload
    async def get_third_party_credential_by_email(
        self, request: ThirdPartyCredentialEmailRequest, /, *, request_options: RequestOptions | None = None
    ) -> ThirdPartyCredentialResult: ...
    @overload
    async def get_third_party_credential_by_email(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        email: str,
        request_options: RequestOptions | None = None,
    ) -> ThirdPartyCredentialResult: ...
    async def get_third_party_credential_by_email(
        self,
        request: ThirdPartyCredentialEmailRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ThirdPartyCredentialResult:
        """Get a third-party credential by e-mail address. Access: admin."""
        return await self._run(OPS.get_third_party_credential_by_email, request, kwargs, request_options)

    @overload
    async def remove_third_party_credential(
        self, request: ThirdPartyCredentialTokenRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def remove_third_party_credential(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        token: ReferenceToken,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def remove_third_party_credential(
        self,
        request: ThirdPartyCredentialTokenRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove a third-party credential by token.

        With the `NoLocalModification` provider action only the third-party credential is removed and the
        local access control credential stays.

        Access: admin.
        """
        await self._run(OPS.remove_third_party_credential, request, kwargs, request_options)

    @overload
    async def remove_third_party_credential_by_email(
        self, request: ThirdPartyCredentialEmailRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def remove_third_party_credential_by_email(
        self,
        /,
        *,
        provider_name: ReferenceToken,
        provider_actions: list[Attribute] | MISSING = MISSING,
        email: str,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def remove_third_party_credential_by_email(
        self,
        request: ThirdPartyCredentialEmailRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove a third-party credential by e-mail address.

        With the `NoLocalModification` provider action only the third-party credential is removed and the
        local access control credential stays.

        Access: admin.
        """
        await self._run(OPS.remove_third_party_credential_by_email, request, kwargs, request_options)
