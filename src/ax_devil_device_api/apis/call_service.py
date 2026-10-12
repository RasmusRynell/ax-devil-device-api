# GENERATED from specs/apis/intercom/call-service-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""SIP and VMS calling: make and terminate calls, SIP configuration and accounts, DTMF configurations, events and triggers, VMS call configuration and audio codecs.

Docs: https://developer.axis.com/vapix/intercom/call-service-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

CallId = Annotated[str, Field(min_length=0, max_length=64)]
SIPAccountId = Annotated[str, Field(min_length=0, max_length=64)]
DTMFConfigurationId = Annotated[str, Field(min_length=0, max_length=64)]
DTMFEventId = Annotated[str, Field(min_length=0, max_length=64)]
DTMFTriggerId = Annotated[str, Field(min_length=0, max_length=64)]
DTMFSequence = Annotated[str, Field(min_length=0, max_length=64, pattern="^[0-9A-D*#]*$")]


class ServiceCapabilities(Model):
    sip: bool = Field(validation_alias="SIP", serialization_alias="SIP")
    """SIP operations are supported."""
    dtmf: bool = Field(validation_alias="DTMF", serialization_alias="DTMF")
    """DTMF operations are supported."""
    audio_codec: bool | None = Field(default=None, validation_alias="AudioCodec", serialization_alias="AudioCodec")
    """Audio codec operations (getting and setting the audio codec priority list) are supported. Available from API version 1.4."""
    media_encryption: bool | None = Field(
        default=None, validation_alias="MediaEncryption", serialization_alias="MediaEncryption"
    )
    """Media encryption operations are supported. Available from API version 1.7."""
    certificate: bool | None = Field(default=None, validation_alias="Certificate", serialization_alias="Certificate")
    """Certificate operations are supported. Available from API version 1.7."""
    attribute: bool | None = Field(default=None, validation_alias="Attribute", serialization_alias="Attribute")
    """Attribute operations for SIP accounts and SIP configurations are supported. Available from API version 1.7."""


CallState = Literal["Idle", "Calling", "Active", "Terminating", "Terminated"]
CallDirection = Literal["Outgoing", "Incoming"]


class CallStatus(Model):
    """The current status of a call in progress or recently terminated."""

    call_id: CallId = Field(validation_alias="CallId", serialization_alias="CallId")
    """Call identifier."""
    source: str = Field(validation_alias="Source", serialization_alias="Source")
    """Media source used for the call, for example the video channel on a multichannel product."""
    call_state: CallState = Field(validation_alias="CallState", serialization_alias="CallState")
    """State of the call."""
    call_state_reason: str = Field(validation_alias="CallStateReason", serialization_alias="CallStateReason")
    """Why the call is in the current state. Non-normative CallStateChangeReason: Initiated, Denied, NoAnswer, Busy, Failed, AcceptedByRemote, AcceptedByDevice, Terminated."""
    start_time: str = Field(validation_alias="StartTime", serialization_alias="StartTime")
    """Start time of the call (dateTime)."""
    direction: CallDirection = Field(validation_alias="Direction", serialization_alias="Direction")
    """Direction of the call."""
    device_uri: str = Field(validation_alias="DeviceURI", serialization_alias="DeviceURI")
    """The Axis product's address."""
    remote_uri: str = Field(validation_alias="RemoteURI", serialization_alias="RemoteURI")
    """The remote device's address."""
    call_type: str = Field(validation_alias="CallType", serialization_alias="CallType")
    """The type of call. Non-normative CallType: SIP (a call to a SIP URI) or VMS (a simulated call)."""
    stop_time: str | None = Field(default=None, validation_alias="StopTime", serialization_alias="StopTime")
    """End time of the call (dateTime). Only available for terminated calls."""
    audio_codec: str | None = Field(default=None, validation_alias="AudioCodec", serialization_alias="AudioCodec")
    """Audio codec used for the call."""
    video_codec: str | None = Field(default=None, validation_alias="VideoCodec", serialization_alias="VideoCodec")
    """Video codec used for the call."""
    sip_account_id: SIPAccountId | None = Field(
        default=None, validation_alias="SIPAccountId", serialization_alias="SIPAccountId"
    )
    """The SIP account used for the call."""


SIPTransport = Literal["udp", "tcp", "tls"]


class STUNServer(Model):
    server: str = Field(validation_alias="Server", serialization_alias="Server")
    """Address (URI)."""


class TURNServer(Model):
    server: str = Field(validation_alias="Server", serialization_alias="Server")
    """Address (URI) of the server."""
    username: str = Field(validation_alias="Username", serialization_alias="Username")
    """User name for the server."""
    password: str = Field(validation_alias="Password", serialization_alias="Password")
    """Password for the server user."""


class Attribute(Model):
    """An attribute name and value: additional configuration for SIP accounts or SIP configurations."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Attribute name."""
    value: str = Field(validation_alias="Value", serialization_alias="Value")
    """Attribute value."""


class AttributeInfo(Model):
    """Information about an attribute: additional configuration for SIP accounts or SIP configurations."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Attribute name."""
    type: str = Field(validation_alias="Type", serialization_alias="Type")
    """Attribute type. Non-normative AttributeType: string, int or bool."""
    default: str | None = Field(default=None, validation_alias="Default", serialization_alias="Default")
    """The attribute's default value."""


class SIPConfiguration(Model):
    """The SIP configuration. All fields are optional."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"access_list_policy"})
    sip_enabled: bool | None = Field(default=None, validation_alias="SIPEnabled", serialization_alias="SIPEnabled")
    """SIP is enabled. Default: False."""
    sip_port: int | None = Field(default=None, validation_alias="SIPPort", serialization_alias="SIPPort")
    """The port for incoming SIP requests. Traffic is not encrypted. Default: 5060."""
    siptls_port: int | None = Field(default=None, validation_alias="SIPTLSPort", serialization_alias="SIPTLSPort")
    """The port for incoming SIPS and TLS-secured SIP requests. Default: 5061."""
    stun_enabled: bool | None = Field(default=None, validation_alias="STUNEnabled", serialization_alias="STUNEnabled")
    """STUN is enabled. Default: False."""
    stun_servers: list[STUNServer] | None = Field(
        default=None, validation_alias="STUNServers", serialization_alias="STUNServers"
    )
    """List of STUN servers."""
    turn_enabled: bool | None = Field(default=None, validation_alias="TURNEnabled", serialization_alias="TURNEnabled")
    """TURN is enabled. Default: False."""
    turn_servers: list[TURNServer] | None = Field(
        default=None, validation_alias="TURNServers", serialization_alias="TURNServers"
    )
    """List of TURN servers."""
    ice_enabled: bool | None = Field(default=None, validation_alias="ICEEnabled", serialization_alias="ICEEnabled")
    """ICE is enabled. Default: False."""
    allow_incoming_calls: bool | None = Field(
        default=None, validation_alias="AllowIncomingCalls", serialization_alias="AllowIncomingCalls"
    )
    """Incoming calls are enabled. Default: False."""
    apply_user_authentication: bool | None = Field(
        default=None, validation_alias="ApplyUserAuthentication", serialization_alias="ApplyUserAuthentication"
    )
    """For future use."""
    allowed_users: list[Any] | None = Field(
        default=None, validation_alias="AllowedUsers", serialization_alias="AllowedUsers"
    )
    """For future use. Array of UserAuthentication (type undefined in doc)."""
    apply_allowed_ur_is: bool | None = Field(
        default=None, validation_alias="ApplyAllowedURIs", serialization_alias="ApplyAllowedURIs"
    )
    """Deprecated. Use ApplyAccessList."""
    allowed_ur_is: list[str] | None = Field(
        default=None, validation_alias="AllowedURIs", serialization_alias="AllowedURIs"
    )
    """Deprecated. Use AccessList. (Doc type String; examples show array.)"""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes for additional configuration. Use get_supported_sip_configuration_attributes to list the supported ones."""
    rtp_start_port: int | None = Field(
        default=None, validation_alias="RTPStartPort", serialization_alias="RTPStartPort"
    )
    """RTP start port for SIP call media. Default: 4000. Available from API version 1.6."""
    calling_timeout: int | None = Field(
        default=None, validation_alias="CallingTimeout", serialization_alias="CallingTimeout", le=600
    )
    """Seconds before an initiated call terminates with NoAnswer. Default: 60. Available from API version 1.7."""
    apply_access_list: bool | None = Field(
        default=None, validation_alias="ApplyAccessList", serialization_alias="ApplyAccessList"
    )
    """Enables use of AccessList."""
    access_list: list[str] | None = Field(default=None, validation_alias="AccessList", serialization_alias="AccessList")
    """A list of SIP URIs; AccessListPolicy says whether it is an allowlist or a blocklist (the table types it String, the examples show an array)."""
    access_list_policy: Literal["Allow", "Block", None] | None = Field(
        default=None, validation_alias="AccessListPolicy", serialization_alias="AccessListPolicy"
    )
    """Allow: use AccessList as an allowlist; Block: use it as a blocklist. Null defaults to Allow."""


class SIPProxy(Model):
    server: str = Field(validation_alias="Server", serialization_alias="Server")
    """Address (URI) of the server."""
    username: str = Field(validation_alias="Username", serialization_alias="Username")
    """User name for the server."""
    password: str = Field(validation_alias="Password", serialization_alias="Password")
    """Password for the server user."""


class SIPAccount(Model):
    """AOR built as sip|sips:UserId[@Domain]. Registrar used for registration; if empty PublicDomain used; if both empty, not registered."""

    user_id: str = Field(validation_alias="UserId", serialization_alias="UserId")
    """User name for registration in the SIP registrar; can be an extension. Mandatory."""
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password")
    """Password for the UserId."""
    registrar: str | None = Field(default=None, validation_alias="Registrar", serialization_alias="Registrar")
    """Address of the SIP registrar used for registration. If empty, PublicDomain is used; if both are empty the account is not registered."""
    public_domain: str | None = Field(default=None, validation_alias="PublicDomain", serialization_alias="PublicDomain")
    """The SIP registrar's public domain."""
    sip_proxies: list[SIPProxy] | None = Field(
        default=None, validation_alias="SIPProxies", serialization_alias="SIPProxies"
    )
    """SIP proxies for outgoing calls from this account, contacted in order."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes for additional configuration. Use get_supported_sip_account_attributes to list the supported ones."""
    id: SIPAccountId | None = Field(default=None, validation_alias="Id", serialization_alias="Id")
    """Identifier for the SIP account. Created automatically when empty or missing."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")
    """The account is enabled. Defaults to true. Default: True."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Descriptive name displayed in the product's user interface."""
    caller_id: str | None = Field(default=None, validation_alias="CallerId", serialization_alias="CallerId")
    """CallerId (caller identifier) used in SIP."""
    authentication_id: str | None = Field(
        default=None, validation_alias="AuthenticationId", serialization_alias="AuthenticationId"
    )
    """Authentication identifier used in the registration. If empty, it is set to UserId."""
    secondary_registrar: str | None = Field(
        default=None, validation_alias="SecondaryRegistrar", serialization_alias="SecondaryRegistrar"
    )
    """Address of the secondary (backup) registrar. Defaults to empty. Default: ''. Available from API version 1.9."""
    secondary_public_domain: str | None = Field(
        default=None, validation_alias="SecondaryPublicDomain", serialization_alias="SecondaryPublicDomain"
    )
    """Public domain of the secondary (backup) registrar. Defaults to empty. Default: ''. Available from API version 1.9."""
    is_default: bool | None = Field(default=None, validation_alias="IsDefault", serialization_alias="IsDefault")
    """The account is the default SIP account. Only one can be the default; the last set wins."""
    sips_enabled: bool | None = Field(default=None, validation_alias="SIPSEnabled", serialization_alias="SIPSEnabled")
    """SIPS (secure SIP) is enabled. If enabled, Transport is set to tls."""
    transport: SIPTransport | None = Field(default=None, validation_alias="Transport", serialization_alias="Transport")
    """The transport protocol for calls from and to this account. tls if SIPSEnabled is true."""
    prioritize_i_pv6: bool | None = Field(
        default=None, validation_alias="PrioritizeIPv6", serialization_alias="PrioritizeIPv6"
    )
    """Prioritize IPv6 over IPv4 (default IPv4). Adding an account checks the network availability and may change this flag."""
    stream_parameters: str | None = Field(
        default=None, validation_alias="StreamParameters", serialization_alias="StreamParameters"
    )
    """Percent-encoded stream parameters (resolution, fps in API 1.6). If empty, default stream parameters are used."""
    allow_mwi: bool | None = Field(default=None, validation_alias="AllowMWI", serialization_alias="AllowMWI")
    """Allow a SIP server to convey an updated listen port using MWI (Message Waiting Indication). Default false. Default: False."""
    dtmf_configuration_id: DTMFConfigurationId | None = Field(
        default=None, validation_alias="DTMFConfigurationId", serialization_alias="DTMFConfigurationId"
    )
    """Identifier of the DTMFConfiguration associated with the account. Default empty. Default: ''."""
    media_encryption: str | None = Field(
        default=None, validation_alias="MediaEncryption", serialization_alias="MediaEncryption"
    )
    """Media encryption preference for calls from this account. Non-normative: None, SRTPBestEffort or SRTPMandatory. Anything but None requires Transport tls. Available from API version 1.7."""
    certificate: str | None = Field(default=None, validation_alias="Certificate", serialization_alias="Certificate")
    """The TLS transport certificate to use; applies to all TLS-enabled accounts. Available from API version 1.7."""
    encryption_protocols: str | None = Field(
        default=None, validation_alias="EncryptionProtocols", serialization_alias="EncryptionProtocols"
    )
    """Comma-separated list of allowed encryption protocols (non-normative EncryptionProtocol: TLSv1, TLSv12, TLSv13); applies to all TLS-enabled accounts. Available from API version 1.7."""
    verify_server_certificate: bool | None = Field(
        default=None, validation_alias="VerifyServerCertificate", serialization_alias="VerifyServerCertificate"
    )
    """Verify the remote server's certificate; applies to all TLS-enabled accounts. Available from API version 1.7."""


class SIPAccountStatus(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"reg_uri"})
    sip_account_id: SIPAccountId | None = Field(
        default=None, validation_alias="SIPAccountId", serialization_alias="SIPAccountId"
    )
    """The SIP account."""
    sipuri: str | None = Field(default=None, validation_alias="SIPURI", serialization_alias="SIPURI")
    """The SIP URI of the account."""
    is_default: bool | None = Field(default=None, validation_alias="IsDefault", serialization_alias="IsDefault")
    """The account is the default account (in the examples, not in the table)."""
    reg_uri: str | None = Field(default=None, validation_alias="RegURI", serialization_alias="RegURI")
    """The registration URI. Empty (or null) if not registered."""
    status: int | None = Field(default=None, validation_alias="Status", serialization_alias="Status")
    """SIP response code from registrar; 0 if not registered."""
    status_text: str | None = Field(default=None, validation_alias="StatusText", serialization_alias="StatusText")
    """SIP response phrase, or "Does not register" / "SIP disabled"."""


class DTMFConfiguration(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the configuration."""
    dtmf_trigger_id: list[DTMFTriggerId] = Field(validation_alias="DTMFTriggerId", serialization_alias="DTMFTriggerId")
    """The DTMF triggers that belong to the configuration."""
    id: DTMFConfigurationId | None = Field(default=None, validation_alias="Id", serialization_alias="Id")
    """Identifier. Created when empty or missing."""
    rfc2833: bool | None = Field(default=None, validation_alias="RFC2833", serialization_alias="RFC2833")
    """DTMF is sent over RTP (RFC 2833). Default true. Default: True."""
    rfc2976: bool | None = Field(default=None, validation_alias="RFC2976", serialization_alias="RFC2976")
    """DTMF is sent over SIP INFO (RFC 2976). Default true. Default: True."""


class DTMFEvent(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Used as nice name in aev:GetEventInstances."""
    id: DTMFEventId | None = Field(default=None, validation_alias="Id", serialization_alias="Id")
    """Identifier. Created when empty or missing."""


class DTMFTrigger(Model):
    id: DTMFTriggerId = Field(validation_alias="Id", serialization_alias="Id")
    """Identifier."""
    dtmf_sequence: DTMFSequence = Field(validation_alias="DTMFSequence", serialization_alias="DTMFSequence")
    """The DTMF sequence that triggers the event. Allowed characters are 0-9, A-D, * and #."""
    dtmf_event_id: DTMFEventId = Field(validation_alias="DTMFEventId", serialization_alias="DTMFEventId")
    """The DTMF event to emit when the sequence is received."""


class VMSCallConfiguration(Model):
    enabled: bool = Field(validation_alias="Enabled", serialization_alias="Enabled")
    """VMS calls are enabled."""
    audio_from_device_to_network_streams: int = Field(
        validation_alias="AudioFromDeviceToNetworkStreams", serialization_alias="AudioFromDeviceToNetworkStreams"
    )
    """Threshold for the minimum number of audio streams from the product to the VMS at which a VMS call is considered active. 0 or negative: not used."""
    audio_from_network_to_device_streams: int = Field(
        validation_alias="AudioFromNetworkToDeviceStreams", serialization_alias="AudioFromNetworkToDeviceStreams"
    )
    """Threshold for the minimum number of audio streams from the VMS to the product at which a VMS call is considered active. 0 or negative: not used."""
    video_from_device_to_network_streams: int = Field(
        validation_alias="VideoFromDeviceToNetworkStreams", serialization_alias="VideoFromDeviceToNetworkStreams"
    )
    """Threshold for the minimum number of video streams from the product to the VMS at which a VMS call is considered active. 0 or negative: not used."""
    timeout: int | None = Field(default=None, validation_alias="Timeout", serialization_alias="Timeout")
    """Seconds to wait before an initiated VMS call terminates with NoAnswer. Default 30. Default: 30. Available from API version 1.5."""


class AudioCodec(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """The audio codec's name."""
    options: str | None = Field(default=None, validation_alias="Options", serialization_alias="Options")
    """Additional parameters for the audio codec."""
    sample_rate: int | None = Field(default=None, validation_alias="SampleRate", serialization_alias="SampleRate")
    """Supported sample rate. Returned in responses; not required in set_audio_codecs."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")


class CallRequest(Model):
    sip_account_id: SIPAccountId | None = Field(
        default=None, validation_alias="SIPAccountId", serialization_alias="SIPAccountId"
    )
    """The SIP account to use. If not specified, the default account is used."""
    to: str = Field(validation_alias="To", serialization_alias="To")
    """Address to call: sip:ip (peer-to-peer), sip:user@domain (SIP), or VMS_CALL (simulated VMS call)."""


class CallResult(Model):
    call_id: CallId = Field(validation_alias="CallId", serialization_alias="CallId")


class TerminateCallRequest(Model):
    call_id: CallId = Field(validation_alias="CallId", serialization_alias="CallId")
    """Call identifier."""


class GetCallStatusRequest(Model):
    call_id: CallId = Field(validation_alias="CallId", serialization_alias="CallId")
    """Call identifier."""


class GetCallStatusResult(Model):
    call_status: CallStatus = Field(validation_alias="CallStatus", serialization_alias="CallStatus")


class GetCallStatusesRequest(Model):
    call_id: list[CallId] | None = Field(default=None, validation_alias="CallId", serialization_alias="CallId")
    """List of call identifiers."""


class GetCallStatusesResult(Model):
    call_status: list[CallStatus] | None = Field(
        default=None, validation_alias="CallStatus", serialization_alias="CallStatus"
    )


class GetSupportedSipConfigurationAttributesResult(Model):
    attribute_info: list[AttributeInfo] | None = Field(
        default=None, validation_alias="AttributeInfo", serialization_alias="AttributeInfo"
    )


class GetSipConfigurationResult(Model):
    sip_configuration: SIPConfiguration = Field(
        validation_alias="SIPConfiguration", serialization_alias="SIPConfiguration"
    )


class SetSipConfigurationRequest(Model):
    sip_configuration: SIPConfiguration = Field(
        validation_alias="SIPConfiguration", serialization_alias="SIPConfiguration"
    )
    """The SIPConfiguration to update."""
    keep_current: bool | None = Field(default=None, validation_alias="KeepCurrent", serialization_alias="KeepCurrent")
    """true: keep current values for fields not specified; false: set unspecified fields to default. Null defaults to true. Default: True."""


class GetSupportedMediaEncryptionModesResult(Model):
    media_encryption: list[str] | None = Field(
        default=None, validation_alias="MediaEncryption", serialization_alias="MediaEncryption"
    )


class GetSupportedSipAccountAttributesResult(Model):
    attribute_info: list[AttributeInfo] | None = Field(
        default=None, validation_alias="AttributeInfo", serialization_alias="AttributeInfo"
    )
    disable_tcp_switch: bool | None = Field(
        default=None, validation_alias="DisableTCPSwitch", serialization_alias="DisableTCPSwitch"
    )
    """SIP can temporarily switch from UDP to TCP when a request is within 200 bytes of the MTU or larger than 1300 bytes; can be disabled for compatibility."""
    max_call_duration: int | None = Field(
        default=None, validation_alias="MaxCallDuration", serialization_alias="MaxCallDuration"
    )
    """Seconds; device hangs up SIP calls lasting longer (no effect on VMS calls)."""
    registration_interval: int | None = Field(
        default=None, validation_alias="RegistrationInterval", serialization_alias="RegistrationInterval"
    )
    """Seconds; re-registration interval when registering to a PBX."""


class GetSipAccountRequest(Model):
    sip_account_id: SIPAccountId = Field(validation_alias="SIPAccountId", serialization_alias="SIPAccountId")
    """Identifier of the SIP account to retrieve."""


class GetSipAccountResult(Model):
    sip_account: SIPAccount = Field(validation_alias="SIPAccount", serialization_alias="SIPAccount")


class GetSipAccountsRequest(Model):
    sip_account_id: list[SIPAccountId] | None = Field(
        default=None, validation_alias="SIPAccountId", serialization_alias="SIPAccountId"
    )
    """Identifiers of the SIP accounts to retrieve."""


class GetSipAccountsResult(Model):
    sip_account: list[SIPAccount] | None = Field(
        default=None, validation_alias="SIPAccount", serialization_alias="SIPAccount"
    )


class SetSipAccountRequest(Model):
    sip_account: SIPAccount = Field(validation_alias="SIPAccount", serialization_alias="SIPAccount")
    """The SIPAccount to add or update."""


class SetSipAccountResult(Model):
    sip_account_id: SIPAccountId = Field(validation_alias="SIPAccountId", serialization_alias="SIPAccountId")


class SetSipAccountsRequest(Model):
    sip_account: list[SIPAccount] = Field(validation_alias="SIPAccount", serialization_alias="SIPAccount")
    """The SIPAccounts to add or update."""


class SetSipAccountsResult(Model):
    sip_account_id: list[SIPAccountId] | None = Field(
        default=None, validation_alias="SIPAccountId", serialization_alias="SIPAccountId"
    )


class RemoveSipAccountRequest(Model):
    sip_account_id: SIPAccountId = Field(validation_alias="SIPAccountId", serialization_alias="SIPAccountId")
    """Identifier of the SIP account to remove."""


class RemoveSipAccountsRequest(Model):
    sip_account_id: list[SIPAccountId] = Field(validation_alias="SIPAccountId", serialization_alias="SIPAccountId")
    """Identifiers of the SIP accounts to remove."""


class GetSipAccountStatusRequest(Model):
    sip_account_id: SIPAccountId = Field(validation_alias="SIPAccountId", serialization_alias="SIPAccountId")
    """Identifier of the SIP account."""


class GetSipAccountStatusResult(Model):
    sip_account_status: SIPAccountStatus = Field(
        validation_alias="SIPAccountStatus", serialization_alias="SIPAccountStatus"
    )


class GetSipAccountStatusesRequest(Model):
    sip_account_id: list[SIPAccountId] | None = Field(
        default=None, validation_alias="SIPAccountId", serialization_alias="SIPAccountId"
    )
    """Identifiers of the SIP accounts."""


class GetSipAccountStatusesResult(Model):
    sip_account_status: list[SIPAccountStatus] | None = Field(
        default=None, validation_alias="SIPAccountStatus", serialization_alias="SIPAccountStatus"
    )


class GetDtmfConfigurationRequest(Model):
    dtmf_configuration_id: DTMFConfigurationId = Field(
        validation_alias="DTMFConfigurationId", serialization_alias="DTMFConfigurationId"
    )
    """Identifier of the DTMF configuration to retrieve."""


class GetDtmfConfigurationResult(Model):
    dtmf_configuration: DTMFConfiguration = Field(
        validation_alias="DTMFConfiguration", serialization_alias="DTMFConfiguration"
    )


class GetDtmfConfigurationsRequest(Model):
    dtmf_configuration_id: list[DTMFConfigurationId] | None = Field(
        default=None, validation_alias="DTMFConfigurationId", serialization_alias="DTMFConfigurationId"
    )
    """Identifiers of the DTMF configurations to retrieve."""


class GetDtmfConfigurationsResult(Model):
    dtmf_configuration: list[DTMFConfiguration] | None = Field(
        default=None, validation_alias="DTMFConfiguration", serialization_alias="DTMFConfiguration"
    )


class SetDtmfConfigurationRequest(Model):
    dtmf_configuration: DTMFConfiguration = Field(
        validation_alias="DTMFConfiguration", serialization_alias="DTMFConfiguration"
    )
    """The DTMFConfiguration to add or update."""


class SetDtmfConfigurationResult(Model):
    dtmf_configuration_id: DTMFConfigurationId = Field(
        validation_alias="DTMFConfigurationId", serialization_alias="DTMFConfigurationId"
    )


class SetDtmfConfigurationsRequest(Model):
    dtmf_configuration: list[DTMFConfiguration] = Field(
        validation_alias="DTMFConfiguration", serialization_alias="DTMFConfiguration"
    )
    """The DTMFConfigurations to add or update."""


class SetDtmfConfigurationsResult(Model):
    dtmf_configuration_id: list[DTMFConfigurationId] | None = Field(
        default=None, validation_alias="DTMFConfigurationId", serialization_alias="DTMFConfigurationId"
    )


class RemoveDtmfConfigurationRequest(Model):
    dtmf_configuration_id: DTMFConfigurationId = Field(
        validation_alias="DTMFConfigurationId", serialization_alias="DTMFConfigurationId"
    )
    """Identifier of the DTMF configuration to remove."""


class RemoveDtmfConfigurationsRequest(Model):
    dtmf_configuration_id: list[DTMFConfigurationId] = Field(
        validation_alias="DTMFConfigurationId", serialization_alias="DTMFConfigurationId"
    )
    """Identifiers of the DTMF configurations to remove."""


class GetDtmfEventRequest(Model):
    dtmf_event_id: DTMFEventId = Field(validation_alias="DTMFEventId", serialization_alias="DTMFEventId")
    """Identifier of the DTMF event to retrieve."""


class GetDtmfEventResult(Model):
    dtmf_event: DTMFEvent = Field(validation_alias="DTMFEvent", serialization_alias="DTMFEvent")


class GetDtmfEventsRequest(Model):
    dtmf_event_id: list[DTMFEventId] | None = Field(
        default=None, validation_alias="DTMFEventId", serialization_alias="DTMFEventId"
    )
    """Identifiers of the DTMF events to retrieve."""


class GetDtmfEventsResult(Model):
    dtmf_event: list[DTMFEvent] | None = Field(
        default=None, validation_alias="DTMFEvent", serialization_alias="DTMFEvent"
    )


class SetDtmfEventRequest(Model):
    dtmf_event: DTMFEvent = Field(validation_alias="DTMFEvent", serialization_alias="DTMFEvent")
    """The DTMFEvent to add or update. (Request table spells the field 'DTMEvent'; syntax uses DTMFEvent.)"""


class SetDtmfEventResult(Model):
    dtmf_event_id: DTMFEventId = Field(validation_alias="DTMFEventId", serialization_alias="DTMFEventId")


class SetDtmfEventsRequest(Model):
    dtmf_event: list[DTMFEvent] = Field(validation_alias="DTMFEvent", serialization_alias="DTMFEvent")
    """The DTMFEvents to add or update."""


class SetDtmfEventsResult(Model):
    dtmf_event_id: list[DTMFEventId] | None = Field(
        default=None, validation_alias="DTMFEventId", serialization_alias="DTMFEventId"
    )


class RemoveDtmfEventRequest(Model):
    dtmf_event_id: DTMFEventId = Field(validation_alias="DTMFEventId", serialization_alias="DTMFEventId")
    """Identifier of the DTMF event to remove."""


class RemoveDtmfEventsRequest(Model):
    dtmf_event_id: list[DTMFEventId] = Field(validation_alias="DTMFEventId", serialization_alias="DTMFEventId")
    """Identifiers of the DTMF events to remove."""


class GetDtmfTriggerRequest(Model):
    dtmf_trigger_id: DTMFTriggerId = Field(validation_alias="DTMFTriggerId", serialization_alias="DTMFTriggerId")
    """Identifier of the DTMF trigger to retrieve."""


class GetDtmfTriggerResult(Model):
    dtmf_trigger: DTMFTrigger = Field(validation_alias="DTMFTrigger", serialization_alias="DTMFTrigger")


class GetDtmfTriggersRequest(Model):
    dtmf_trigger_id: list[DTMFTriggerId] | None = Field(
        default=None, validation_alias="DTMFTriggerId", serialization_alias="DTMFTriggerId"
    )
    """Identifiers of the DTMF triggers to retrieve."""


class GetDtmfTriggersResult(Model):
    dtmf_trigger: list[DTMFTrigger] | None = Field(
        default=None, validation_alias="DTMFTrigger", serialization_alias="DTMFTrigger"
    )


class SetDtmfTriggerRequest(Model):
    dtmf_trigger: DTMFTrigger = Field(validation_alias="DTMFTrigger", serialization_alias="DTMFTrigger")
    """The DTMFTrigger to add or update. (Request table spells the field 'DTMTrigger'.)"""


class SetDtmfTriggerResult(Model):
    dtmf_trigger_id: DTMFTriggerId = Field(validation_alias="DTMFTriggerId", serialization_alias="DTMFTriggerId")


class SetDtmfTriggersRequest(Model):
    dtmf_trigger: list[DTMFTrigger] = Field(validation_alias="DTMFTrigger", serialization_alias="DTMFTrigger")
    """The DTMFTriggers to add or update."""


class SetDtmfTriggersResult(Model):
    dtmf_trigger_id: list[DTMFTriggerId] | None = Field(
        default=None, validation_alias="DTMFTriggerId", serialization_alias="DTMFTriggerId"
    )


class RemoveDtmfTriggerRequest(Model):
    dtmf_trigger_id: DTMFTriggerId = Field(validation_alias="DTMFTriggerId", serialization_alias="DTMFTriggerId")
    """Identifier of the DTMF trigger to remove."""


class RemoveDtmfTriggersRequest(Model):
    dtmf_trigger_id: list[DTMFTriggerId] = Field(validation_alias="DTMFTriggerId", serialization_alias="DTMFTriggerId")
    """Identifiers of the DTMF triggers to remove."""


class GetVmsCallConfigurationResult(Model):
    vms_call_configuration: VMSCallConfiguration = Field(
        validation_alias="VMSCallConfiguration", serialization_alias="VMSCallConfiguration"
    )


class SetVmsCallConfigurationRequest(Model):
    vms_call_configuration: VMSCallConfiguration = Field(
        validation_alias="VMSCallConfiguration", serialization_alias="VMSCallConfiguration"
    )
    """The updated VMSCallConfiguration."""


class GetDefaultAudioCodecsResult(Model):
    audio_codec: list[AudioCodec] | None = Field(
        default=None, validation_alias="AudioCodec", serialization_alias="AudioCodec"
    )


class GetSupportedAudioCodecsResult(Model):
    audio_codec: list[AudioCodec] | None = Field(
        default=None, validation_alias="AudioCodec", serialization_alias="AudioCodec"
    )


class GetAudioCodecsResult(Model):
    audio_codec: list[AudioCodec] | None = Field(
        default=None, validation_alias="AudioCodec", serialization_alias="AudioCodec"
    )


class SetAudioCodecsRequest(Model):
    audio_codec: list[AudioCodec] = Field(validation_alias="AudioCodec", serialization_alias="AudioCodec")
    """AudioCodecs in priority order."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/call"

INFO = ApiInfo(
    id="call-service-api",
    name="Call service API",
    family=Family.SERVICE_JSON,
    discovery=(
        ParamDiscovery("Properties.API.SIP.SIP", "yes"),
        ParamDiscovery("Properties.API.SIP.Version", "2.0", ">="),
    ),
    docs=("https://developer.axis.com/vapix/intercom/call-service-api/",),
    errors={
        "ter:NotFound": ErrorCode("Not found.", "not_found"),
        "ter:Failure": ErrorCode("The action failed.", "internal"),
        "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
        "ter:InvalidArgs": ErrorCode(
            "Missing data. The request does not contain all required data.", "invalid_argument"
        ),
        "ter:NotSupported": ErrorCode("The action is not supported.", "unsupported"),
    },
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "axcall:GetServiceCapabilities"),
        result=GetServiceCapabilitiesResult,
        access="admin",
        effect="read",
    )
    call = Operation(
        INFO,
        "call",
        ServiceJsonBinding(PATH, "axcall:Call"),
        params=CallRequest,
        result=CallResult,
        access="admin",
        effect="action",
        errors={"ter:Failure": ErrorCode("Failed to initiate the call.", "internal")},
    )
    terminate_call = Operation(
        INFO,
        "terminate_call",
        ServiceJsonBinding(PATH, "axcall:TerminateCall"),
        params=TerminateCallRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("There is no ongoing call with the specified CallId.", "not_found"),
            "ter:Failure": ErrorCode("Failed to terminate the call.", "internal"),
        },
    )
    get_call_status = Operation(
        INFO,
        "get_call_status",
        ServiceJsonBinding(PATH, "axcall:GetCallStatus"),
        params=GetCallStatusRequest,
        result=GetCallStatusResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("env:Sender ter:InvalidArgVal ter:NotFound — Not found.", "not_found"),
            "ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal"),
        },
    )
    get_call_statuses = Operation(
        INFO,
        "get_call_statuses",
        ServiceJsonBinding(PATH, "axcall:GetCallStatuses"),
        params=GetCallStatusesRequest,
        result=GetCallStatusesResult,
        access="admin",
        effect="read",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    get_supported_sip_configuration_attributes = Operation(
        INFO,
        "get_supported_sip_configuration_attributes",
        ServiceJsonBinding(PATH, "axcall:GetSupportedSIPConfigurationAttributes"),
        result=GetSupportedSipConfigurationAttributesResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 7),
    )
    get_sip_configuration = Operation(
        INFO,
        "get_sip_configuration",
        ServiceJsonBinding(PATH, "axcall:GetSIPConfiguration"),
        result=GetSipConfigurationResult,
        access="admin",
        effect="read",
    )
    set_sip_configuration = Operation(
        INFO,
        "set_sip_configuration",
        ServiceJsonBinding(PATH, "axcall:SetSIPConfiguration"),
        params=SetSipConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
            "ter:NotSupported": ErrorCode("The action is not supported.", "unsupported"),
        },
    )
    get_supported_media_encryption_modes = Operation(
        INFO,
        "get_supported_media_encryption_modes",
        ServiceJsonBinding(PATH, "axcall:GetSupportedMediaEncryptionModes"),
        result=GetSupportedMediaEncryptionModesResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 7),
    )
    get_supported_sip_account_attributes = Operation(
        INFO,
        "get_supported_sip_account_attributes",
        ServiceJsonBinding(PATH, "axcall:GetSupportedSIPAccountAttributes"),
        result=GetSupportedSipAccountAttributesResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 7),
    )
    get_sip_account = Operation(
        INFO,
        "get_sip_account",
        ServiceJsonBinding(PATH, "axcall:GetSIPAccount"),
        params=GetSipAccountRequest,
        result=GetSipAccountResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("env:Sender ter:InvalidArgVal ter:NotFound — Not found.", "not_found"),
            "ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal"),
        },
    )
    get_sip_accounts = Operation(
        INFO,
        "get_sip_accounts",
        ServiceJsonBinding(PATH, "axcall:GetSIPAccounts"),
        params=GetSipAccountsRequest,
        result=GetSipAccountsResult,
        access="admin",
        effect="read",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    set_sip_account = Operation(
        INFO,
        "set_sip_account",
        ServiceJsonBinding(PATH, "axcall:SetSIPAccount"),
        params=SetSipAccountRequest,
        result=SetSipAccountResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    set_sip_accounts = Operation(
        INFO,
        "set_sip_accounts",
        ServiceJsonBinding(PATH, "axcall:SetSIPAccounts"),
        params=SetSipAccountsRequest,
        result=SetSipAccountsResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    remove_sip_account = Operation(
        INFO,
        "remove_sip_account",
        ServiceJsonBinding(PATH, "axcall:RemoveSIPAccount"),
        params=RemoveSipAccountRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    remove_sip_accounts = Operation(
        INFO,
        "remove_sip_accounts",
        ServiceJsonBinding(PATH, "axcall:RemoveSIPAccounts"),
        params=RemoveSipAccountsRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    get_sip_account_status = Operation(
        INFO,
        "get_sip_account_status",
        ServiceJsonBinding(PATH, "axcall:GetSIPAccountStatus"),
        params=GetSipAccountStatusRequest,
        result=GetSipAccountStatusResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("env:Sender ter:InvalidArgVal ter:NotFound — Not found.", "not_found"),
            "ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal"),
        },
    )
    get_sip_account_statuses = Operation(
        INFO,
        "get_sip_account_statuses",
        ServiceJsonBinding(PATH, "axcall:GetSIPAccountStatuses"),
        params=GetSipAccountStatusesRequest,
        result=GetSipAccountStatusesResult,
        access="admin",
        effect="read",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    get_dtmf_configuration = Operation(
        INFO,
        "get_dtmf_configuration",
        ServiceJsonBinding(PATH, "axcall:GetDTMFConfiguration"),
        params=GetDtmfConfigurationRequest,
        result=GetDtmfConfigurationResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("env:Sender ter:InvalidArgVal ter:NotFound — Not found.", "not_found"),
            "ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal"),
        },
    )
    get_dtmf_configurations = Operation(
        INFO,
        "get_dtmf_configurations",
        ServiceJsonBinding(PATH, "axcall:GetDTMFConfigurations"),
        params=GetDtmfConfigurationsRequest,
        result=GetDtmfConfigurationsResult,
        access="admin",
        effect="read",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    set_dtmf_configuration = Operation(
        INFO,
        "set_dtmf_configuration",
        ServiceJsonBinding(PATH, "axcall:SetDTMFConfiguration"),
        params=SetDtmfConfigurationRequest,
        result=SetDtmfConfigurationResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    set_dtmf_configurations = Operation(
        INFO,
        "set_dtmf_configurations",
        ServiceJsonBinding(PATH, "axcall:SetDTMFConfigurations"),
        params=SetDtmfConfigurationsRequest,
        result=SetDtmfConfigurationsResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    remove_dtmf_configuration = Operation(
        INFO,
        "remove_dtmf_configuration",
        ServiceJsonBinding(PATH, "axcall:RemoveDTMFConfiguration"),
        params=RemoveDtmfConfigurationRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    remove_dtmf_configurations = Operation(
        INFO,
        "remove_dtmf_configurations",
        ServiceJsonBinding(PATH, "axcall:RemoveDTMFConfigurations"),
        params=RemoveDtmfConfigurationsRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    get_dtmf_event = Operation(
        INFO,
        "get_dtmf_event",
        ServiceJsonBinding(PATH, "axcall:GetDTMFEvent"),
        params=GetDtmfEventRequest,
        result=GetDtmfEventResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("env:Sender ter:InvalidArgVal ter:NotFound — Not found.", "not_found"),
            "ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal"),
        },
    )
    get_dtmf_events = Operation(
        INFO,
        "get_dtmf_events",
        ServiceJsonBinding(PATH, "axcall:GetDTMFEvents"),
        params=GetDtmfEventsRequest,
        result=GetDtmfEventsResult,
        access="admin",
        effect="read",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    set_dtmf_event = Operation(
        INFO,
        "set_dtmf_event",
        ServiceJsonBinding(PATH, "axcall:SetDTMFEvent"),
        params=SetDtmfEventRequest,
        result=SetDtmfEventResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    set_dtmf_events = Operation(
        INFO,
        "set_dtmf_events",
        ServiceJsonBinding(PATH, "axcall:SetDTMFEvents"),
        params=SetDtmfEventsRequest,
        result=SetDtmfEventsResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    remove_dtmf_event = Operation(
        INFO,
        "remove_dtmf_event",
        ServiceJsonBinding(PATH, "axcall:RemoveDTMFEvent"),
        params=RemoveDtmfEventRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    remove_dtmf_events = Operation(
        INFO,
        "remove_dtmf_events",
        ServiceJsonBinding(PATH, "axcall:RemoveDTMFEvents"),
        params=RemoveDtmfEventsRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    get_dtmf_trigger = Operation(
        INFO,
        "get_dtmf_trigger",
        ServiceJsonBinding(PATH, "axcall:GetDTMFTrigger"),
        params=GetDtmfTriggerRequest,
        result=GetDtmfTriggerResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("env:Sender ter:InvalidArgVal ter:NotFound — Not found.", "not_found"),
            "ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal"),
        },
    )
    get_dtmf_triggers = Operation(
        INFO,
        "get_dtmf_triggers",
        ServiceJsonBinding(PATH, "axcall:GetDTMFTriggers"),
        params=GetDtmfTriggersRequest,
        result=GetDtmfTriggersResult,
        access="admin",
        effect="read",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    set_dtmf_trigger = Operation(
        INFO,
        "set_dtmf_trigger",
        ServiceJsonBinding(PATH, "axcall:SetDTMFTrigger"),
        params=SetDtmfTriggerRequest,
        result=SetDtmfTriggerResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    set_dtmf_triggers = Operation(
        INFO,
        "set_dtmf_triggers",
        ServiceJsonBinding(PATH, "axcall:SetDTMFTriggers"),
        params=SetDtmfTriggersRequest,
        result=SetDtmfTriggersResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )
    remove_dtmf_trigger = Operation(
        INFO,
        "remove_dtmf_trigger",
        ServiceJsonBinding(PATH, "axcall:RemoveDTMFTrigger"),
        params=RemoveDtmfTriggerRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    remove_dtmf_triggers = Operation(
        INFO,
        "remove_dtmf_triggers",
        ServiceJsonBinding(PATH, "axcall:RemoveDTMFTriggers"),
        params=RemoveDtmfTriggersRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:Failure": ErrorCode("env:Receiver ter:Action ter:Failure — operation failed.", "internal")},
    )
    get_vms_call_configuration = Operation(
        INFO,
        "get_vms_call_configuration",
        ServiceJsonBinding(PATH, "axcall:GetVMSCallConfiguration"),
        result=GetVmsCallConfigurationResult,
        access="admin",
        effect="read",
    )
    set_vms_call_configuration = Operation(
        INFO,
        "set_vms_call_configuration",
        ServiceJsonBinding(PATH, "axcall:SetVMSCallConfiguration"),
        params=SetVmsCallConfigurationRequest,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
            "ter:NotSupported": ErrorCode("The action is not supported.", "unsupported"),
        },
    )
    get_default_audio_codecs = Operation(
        INFO,
        "get_default_audio_codecs",
        ServiceJsonBinding(PATH, "axcall:GetDefaultAudioCodecs"),
        result=GetDefaultAudioCodecsResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 4),
    )
    get_supported_audio_codecs = Operation(
        INFO,
        "get_supported_audio_codecs",
        ServiceJsonBinding(PATH, "axcall:GetSupportedAudioCodecs"),
        result=GetSupportedAudioCodecsResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 4),
    )
    get_audio_codecs = Operation(
        INFO,
        "get_audio_codecs",
        ServiceJsonBinding(PATH, "axcall:GetAudioCodecs"),
        result=GetAudioCodecsResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 4),
    )
    set_audio_codecs = Operation(
        INFO,
        "set_audio_codecs",
        ServiceJsonBinding(PATH, "axcall:SetAudioCodecs"),
        params=SetAudioCodecsRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 4),
        write="replace",
        errors={
            "ter:InvalidArgVal": ErrorCode("Invalid data. The request contains invalid values.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "Missing data. The request does not contain all required data.", "invalid_argument"
            ),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class CallServiceApi(SyncApi):
    """Call service API (``call-service-api``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Retrieve the capabilities supported by the service. Access: admin."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def call(
        self,
        *,
        sip_account_id: SIPAccountId | MISSING = MISSING,
        to: str,
        request_options: RequestOptions | None = None,
    ) -> CallResult:
        """Make a call; returns a CallId. Access: admin."""
        return self._run(OPS.call, None, {"sip_account_id": sip_account_id, "to": to}, request_options)

    def terminate_call(self, *, call_id: CallId, request_options: RequestOptions | None = None) -> None:
        """Terminate an ongoing call. Access: admin."""
        self._run(OPS.terminate_call, None, {"call_id": call_id}, request_options)

    def get_call_status(self, *, call_id: CallId, request_options: RequestOptions | None = None) -> GetCallStatusResult:
        """Get the current CallStatus of a given call. Access: admin."""
        return self._run(OPS.get_call_status, None, {"call_id": call_id}, request_options)

    def get_call_statuses(
        self, *, call_id: list[CallId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetCallStatusesResult:
        """Get CallStatus for multiple calls (all if no CallId given; unresolvable ids ignored).

        Access: admin.
        """
        return self._run(OPS.get_call_statuses, None, {"call_id": call_id}, request_options)

    def get_supported_sip_configuration_attributes(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedSipConfigurationAttributesResult:
        """List supported attributes for the SIP configuration.

        Since 1.7.

        Access: admin.
        """
        return self._run(OPS.get_supported_sip_configuration_attributes, None, {}, request_options)

    def get_sip_configuration(self, *, request_options: RequestOptions | None = None) -> GetSipConfigurationResult:
        """Retrieve the current SIP configuration. Access: admin."""
        return self._run(OPS.get_sip_configuration, None, {}, request_options)

    @overload
    def set_sip_configuration(
        self, request: SetSipConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_sip_configuration(
        self,
        /,
        *,
        sip_configuration: SIPConfiguration,
        keep_current: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_sip_configuration(
        self,
        request: SetSipConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the SIP configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_sip_configuration, request, kwargs, request_options)

    def get_supported_media_encryption_modes(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedMediaEncryptionModesResult:
        """List supported media encryption modes.

        Since 1.7.

        Access: admin.
        """
        return self._run(OPS.get_supported_media_encryption_modes, None, {}, request_options)

    def get_supported_sip_account_attributes(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedSipAccountAttributesResult:
        """List supported attributes for SIP accounts (unimplemented attributes are silently ignored when set).

        Since 1.7.

        Access: admin.
        """
        return self._run(OPS.get_supported_sip_account_attributes, None, {}, request_options)

    def get_sip_account(
        self, *, sip_account_id: SIPAccountId, request_options: RequestOptions | None = None
    ) -> GetSipAccountResult:
        """Retrieve a single SIP account. Access: admin."""
        return self._run(OPS.get_sip_account, None, {"sip_account_id": sip_account_id}, request_options)

    def get_sip_accounts(
        self, *, sip_account_id: list[SIPAccountId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetSipAccountsResult:
        """Retrieve multiple SIP accounts; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return self._run(OPS.get_sip_accounts, None, {"sip_account_id": sip_account_id}, request_options)

    @overload
    def set_sip_account(
        self, request: SetSipAccountRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetSipAccountResult: ...
    @overload
    def set_sip_account(
        self, /, *, sip_account: SIPAccount, request_options: RequestOptions | None = None
    ) -> SetSipAccountResult: ...
    def set_sip_account(
        self,
        request: SetSipAccountRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetSipAccountResult:
        """Add or update a SIP account (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_sip_account, request, kwargs, request_options)

    @overload
    def set_sip_accounts(
        self, request: SetSipAccountsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetSipAccountsResult: ...
    @overload
    def set_sip_accounts(
        self, /, *, sip_account: list[SIPAccount], request_options: RequestOptions | None = None
    ) -> SetSipAccountsResult: ...
    def set_sip_accounts(
        self,
        request: SetSipAccountsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetSipAccountsResult:
        """Add or update multiple SIP accounts.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_sip_accounts, request, kwargs, request_options)

    def remove_sip_account(
        self, *, sip_account_id: SIPAccountId, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a SIP account; unresolvable id is ignored. Access: admin."""
        self._run(OPS.remove_sip_account, None, {"sip_account_id": sip_account_id}, request_options)

    def remove_sip_accounts(
        self, *, sip_account_id: list[SIPAccountId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple SIP accounts; unresolvable ids ignored. Access: admin."""
        self._run(OPS.remove_sip_accounts, None, {"sip_account_id": sip_account_id}, request_options)

    def get_sip_account_status(
        self, *, sip_account_id: SIPAccountId, request_options: RequestOptions | None = None
    ) -> GetSipAccountStatusResult:
        """Retrieve the status of a SIP account. Access: admin."""
        return self._run(OPS.get_sip_account_status, None, {"sip_account_id": sip_account_id}, request_options)

    def get_sip_account_statuses(
        self, *, sip_account_id: list[SIPAccountId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetSipAccountStatusesResult:
        """Retrieve statuses of multiple SIP accounts (all if no ids). Access: admin."""
        return self._run(OPS.get_sip_account_statuses, None, {"sip_account_id": sip_account_id}, request_options)

    def get_dtmf_configuration(
        self, *, dtmf_configuration_id: DTMFConfigurationId, request_options: RequestOptions | None = None
    ) -> GetDtmfConfigurationResult:
        """Retrieve a single DTMF configuration. Access: admin."""
        return self._run(
            OPS.get_dtmf_configuration, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    def get_dtmf_configurations(
        self,
        *,
        dtmf_configuration_id: list[DTMFConfigurationId] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDtmfConfigurationsResult:
        """Retrieve multiple DTMF configurations; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return self._run(
            OPS.get_dtmf_configurations, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    @overload
    def set_dtmf_configuration(
        self, request: SetDtmfConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationResult: ...
    @overload
    def set_dtmf_configuration(
        self, /, *, dtmf_configuration: DTMFConfiguration, request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationResult: ...
    def set_dtmf_configuration(
        self,
        request: SetDtmfConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfConfigurationResult:
        """Add or update a DTMF configuration (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_dtmf_configuration, request, kwargs, request_options)

    @overload
    def set_dtmf_configurations(
        self, request: SetDtmfConfigurationsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationsResult: ...
    @overload
    def set_dtmf_configurations(
        self, /, *, dtmf_configuration: list[DTMFConfiguration], request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationsResult: ...
    def set_dtmf_configurations(
        self,
        request: SetDtmfConfigurationsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfConfigurationsResult:
        """Add or update multiple DTMF configurations.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_dtmf_configurations, request, kwargs, request_options)

    def remove_dtmf_configuration(
        self, *, dtmf_configuration_id: DTMFConfigurationId, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a DTMF configuration; unresolvable id is ignored. Access: admin."""
        self._run(
            OPS.remove_dtmf_configuration, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    def remove_dtmf_configurations(
        self, *, dtmf_configuration_id: list[DTMFConfigurationId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple DTMF configurations; unresolvable ids ignored. Access: admin."""
        self._run(
            OPS.remove_dtmf_configurations, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    def get_dtmf_event(
        self, *, dtmf_event_id: DTMFEventId, request_options: RequestOptions | None = None
    ) -> GetDtmfEventResult:
        """Retrieve a single DTMF event. Access: admin."""
        return self._run(OPS.get_dtmf_event, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    def get_dtmf_events(
        self, *, dtmf_event_id: list[DTMFEventId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetDtmfEventsResult:
        """Retrieve multiple DTMF events; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return self._run(OPS.get_dtmf_events, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    @overload
    def set_dtmf_event(
        self, request: SetDtmfEventRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfEventResult: ...
    @overload
    def set_dtmf_event(
        self, /, *, dtmf_event: DTMFEvent, request_options: RequestOptions | None = None
    ) -> SetDtmfEventResult: ...
    def set_dtmf_event(
        self,
        request: SetDtmfEventRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfEventResult:
        """Add or update a DTMF event (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_dtmf_event, request, kwargs, request_options)

    @overload
    def set_dtmf_events(
        self, request: SetDtmfEventsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfEventsResult: ...
    @overload
    def set_dtmf_events(
        self, /, *, dtmf_event: list[DTMFEvent], request_options: RequestOptions | None = None
    ) -> SetDtmfEventsResult: ...
    def set_dtmf_events(
        self,
        request: SetDtmfEventsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfEventsResult:
        """Add or update multiple DTMF events.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_dtmf_events, request, kwargs, request_options)

    def remove_dtmf_event(self, *, dtmf_event_id: DTMFEventId, request_options: RequestOptions | None = None) -> None:
        """Remove a DTMF event; unresolvable id is ignored. Access: admin."""
        self._run(OPS.remove_dtmf_event, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    def remove_dtmf_events(
        self, *, dtmf_event_id: list[DTMFEventId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple DTMF events; unresolvable ids ignored. Access: admin."""
        self._run(OPS.remove_dtmf_events, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    def get_dtmf_trigger(
        self, *, dtmf_trigger_id: DTMFTriggerId, request_options: RequestOptions | None = None
    ) -> GetDtmfTriggerResult:
        """Retrieve a single DTMF trigger. Access: admin."""
        return self._run(OPS.get_dtmf_trigger, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    def get_dtmf_triggers(
        self, *, dtmf_trigger_id: list[DTMFTriggerId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetDtmfTriggersResult:
        """Retrieve multiple DTMF triggers; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return self._run(OPS.get_dtmf_triggers, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    @overload
    def set_dtmf_trigger(
        self, request: SetDtmfTriggerRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfTriggerResult: ...
    @overload
    def set_dtmf_trigger(
        self, /, *, dtmf_trigger: DTMFTrigger, request_options: RequestOptions | None = None
    ) -> SetDtmfTriggerResult: ...
    def set_dtmf_trigger(
        self,
        request: SetDtmfTriggerRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfTriggerResult:
        """Add or update a DTMF trigger (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_dtmf_trigger, request, kwargs, request_options)

    @overload
    def set_dtmf_triggers(
        self, request: SetDtmfTriggersRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfTriggersResult: ...
    @overload
    def set_dtmf_triggers(
        self, /, *, dtmf_trigger: list[DTMFTrigger], request_options: RequestOptions | None = None
    ) -> SetDtmfTriggersResult: ...
    def set_dtmf_triggers(
        self,
        request: SetDtmfTriggersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfTriggersResult:
        """Add or update multiple DTMF triggers.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_dtmf_triggers, request, kwargs, request_options)

    def remove_dtmf_trigger(
        self, *, dtmf_trigger_id: DTMFTriggerId, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a DTMF trigger; unresolvable id is ignored. Access: admin."""
        self._run(OPS.remove_dtmf_trigger, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    def remove_dtmf_triggers(
        self, *, dtmf_trigger_id: list[DTMFTriggerId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple DTMF triggers; unresolvable ids ignored. Access: admin."""
        self._run(OPS.remove_dtmf_triggers, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    def get_vms_call_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> GetVmsCallConfigurationResult:
        """Retrieve the VMS call configuration. Access: admin."""
        return self._run(OPS.get_vms_call_configuration, None, {}, request_options)

    @overload
    def set_vms_call_configuration(
        self, request: SetVmsCallConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_vms_call_configuration(
        self, /, *, vms_call_configuration: VMSCallConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_vms_call_configuration(
        self,
        request: SetVmsCallConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the VMS call configuration.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_vms_call_configuration, request, kwargs, request_options)

    def get_default_audio_codecs(self, *, request_options: RequestOptions | None = None) -> GetDefaultAudioCodecsResult:
        """Default audio codec priority list (highest priority first).

        Since 1.4.

        Access: admin.
        """
        return self._run(OPS.get_default_audio_codecs, None, {}, request_options)

    def get_supported_audio_codecs(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedAudioCodecsResult:
        """All audio codecs available in the product.

        Since 1.4.

        Access: admin.
        """
        return self._run(OPS.get_supported_audio_codecs, None, {}, request_options)

    def get_audio_codecs(self, *, request_options: RequestOptions | None = None) -> GetAudioCodecsResult:
        """Current audio codec priority list sent to call recipients.

        Since 1.4.

        Access: admin.
        """
        return self._run(OPS.get_audio_codecs, None, {}, request_options)

    @overload
    def set_audio_codecs(
        self, request: SetAudioCodecsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_audio_codecs(
        self, /, *, audio_codec: list[AudioCodec], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_audio_codecs(
        self,
        request: SetAudioCodecsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the audio codec priority list (first = highest priority).

        Since 1.4.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_audio_codecs, request, kwargs, request_options)


class AsyncCallServiceApi(AsyncApi):
    """Call service API (``call-service-api``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Retrieve the capabilities supported by the service. Access: admin."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def call(
        self,
        *,
        sip_account_id: SIPAccountId | MISSING = MISSING,
        to: str,
        request_options: RequestOptions | None = None,
    ) -> CallResult:
        """Make a call; returns a CallId. Access: admin."""
        return await self._run(OPS.call, None, {"sip_account_id": sip_account_id, "to": to}, request_options)

    async def terminate_call(self, *, call_id: CallId, request_options: RequestOptions | None = None) -> None:
        """Terminate an ongoing call. Access: admin."""
        await self._run(OPS.terminate_call, None, {"call_id": call_id}, request_options)

    async def get_call_status(
        self, *, call_id: CallId, request_options: RequestOptions | None = None
    ) -> GetCallStatusResult:
        """Get the current CallStatus of a given call. Access: admin."""
        return await self._run(OPS.get_call_status, None, {"call_id": call_id}, request_options)

    async def get_call_statuses(
        self, *, call_id: list[CallId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetCallStatusesResult:
        """Get CallStatus for multiple calls (all if no CallId given; unresolvable ids ignored).

        Access: admin.
        """
        return await self._run(OPS.get_call_statuses, None, {"call_id": call_id}, request_options)

    async def get_supported_sip_configuration_attributes(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedSipConfigurationAttributesResult:
        """List supported attributes for the SIP configuration.

        Since 1.7.

        Access: admin.
        """
        return await self._run(OPS.get_supported_sip_configuration_attributes, None, {}, request_options)

    async def get_sip_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSipConfigurationResult:
        """Retrieve the current SIP configuration. Access: admin."""
        return await self._run(OPS.get_sip_configuration, None, {}, request_options)

    @overload
    async def set_sip_configuration(
        self, request: SetSipConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_sip_configuration(
        self,
        /,
        *,
        sip_configuration: SIPConfiguration,
        keep_current: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_sip_configuration(
        self,
        request: SetSipConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the SIP configuration. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_sip_configuration, request, kwargs, request_options)

    async def get_supported_media_encryption_modes(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedMediaEncryptionModesResult:
        """List supported media encryption modes.

        Since 1.7.

        Access: admin.
        """
        return await self._run(OPS.get_supported_media_encryption_modes, None, {}, request_options)

    async def get_supported_sip_account_attributes(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedSipAccountAttributesResult:
        """List supported attributes for SIP accounts (unimplemented attributes are silently ignored when set).

        Since 1.7.

        Access: admin.
        """
        return await self._run(OPS.get_supported_sip_account_attributes, None, {}, request_options)

    async def get_sip_account(
        self, *, sip_account_id: SIPAccountId, request_options: RequestOptions | None = None
    ) -> GetSipAccountResult:
        """Retrieve a single SIP account. Access: admin."""
        return await self._run(OPS.get_sip_account, None, {"sip_account_id": sip_account_id}, request_options)

    async def get_sip_accounts(
        self, *, sip_account_id: list[SIPAccountId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetSipAccountsResult:
        """Retrieve multiple SIP accounts; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return await self._run(OPS.get_sip_accounts, None, {"sip_account_id": sip_account_id}, request_options)

    @overload
    async def set_sip_account(
        self, request: SetSipAccountRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetSipAccountResult: ...
    @overload
    async def set_sip_account(
        self, /, *, sip_account: SIPAccount, request_options: RequestOptions | None = None
    ) -> SetSipAccountResult: ...
    async def set_sip_account(
        self,
        request: SetSipAccountRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetSipAccountResult:
        """Add or update a SIP account (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_sip_account, request, kwargs, request_options)

    @overload
    async def set_sip_accounts(
        self, request: SetSipAccountsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetSipAccountsResult: ...
    @overload
    async def set_sip_accounts(
        self, /, *, sip_account: list[SIPAccount], request_options: RequestOptions | None = None
    ) -> SetSipAccountsResult: ...
    async def set_sip_accounts(
        self,
        request: SetSipAccountsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetSipAccountsResult:
        """Add or update multiple SIP accounts.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_sip_accounts, request, kwargs, request_options)

    async def remove_sip_account(
        self, *, sip_account_id: SIPAccountId, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a SIP account; unresolvable id is ignored. Access: admin."""
        await self._run(OPS.remove_sip_account, None, {"sip_account_id": sip_account_id}, request_options)

    async def remove_sip_accounts(
        self, *, sip_account_id: list[SIPAccountId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple SIP accounts; unresolvable ids ignored. Access: admin."""
        await self._run(OPS.remove_sip_accounts, None, {"sip_account_id": sip_account_id}, request_options)

    async def get_sip_account_status(
        self, *, sip_account_id: SIPAccountId, request_options: RequestOptions | None = None
    ) -> GetSipAccountStatusResult:
        """Retrieve the status of a SIP account. Access: admin."""
        return await self._run(OPS.get_sip_account_status, None, {"sip_account_id": sip_account_id}, request_options)

    async def get_sip_account_statuses(
        self, *, sip_account_id: list[SIPAccountId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetSipAccountStatusesResult:
        """Retrieve statuses of multiple SIP accounts (all if no ids). Access: admin."""
        return await self._run(OPS.get_sip_account_statuses, None, {"sip_account_id": sip_account_id}, request_options)

    async def get_dtmf_configuration(
        self, *, dtmf_configuration_id: DTMFConfigurationId, request_options: RequestOptions | None = None
    ) -> GetDtmfConfigurationResult:
        """Retrieve a single DTMF configuration. Access: admin."""
        return await self._run(
            OPS.get_dtmf_configuration, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    async def get_dtmf_configurations(
        self,
        *,
        dtmf_configuration_id: list[DTMFConfigurationId] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDtmfConfigurationsResult:
        """Retrieve multiple DTMF configurations; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return await self._run(
            OPS.get_dtmf_configurations, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    @overload
    async def set_dtmf_configuration(
        self, request: SetDtmfConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationResult: ...
    @overload
    async def set_dtmf_configuration(
        self, /, *, dtmf_configuration: DTMFConfiguration, request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationResult: ...
    async def set_dtmf_configuration(
        self,
        request: SetDtmfConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfConfigurationResult:
        """Add or update a DTMF configuration (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_dtmf_configuration, request, kwargs, request_options)

    @overload
    async def set_dtmf_configurations(
        self, request: SetDtmfConfigurationsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationsResult: ...
    @overload
    async def set_dtmf_configurations(
        self, /, *, dtmf_configuration: list[DTMFConfiguration], request_options: RequestOptions | None = None
    ) -> SetDtmfConfigurationsResult: ...
    async def set_dtmf_configurations(
        self,
        request: SetDtmfConfigurationsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfConfigurationsResult:
        """Add or update multiple DTMF configurations.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_dtmf_configurations, request, kwargs, request_options)

    async def remove_dtmf_configuration(
        self, *, dtmf_configuration_id: DTMFConfigurationId, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a DTMF configuration; unresolvable id is ignored. Access: admin."""
        await self._run(
            OPS.remove_dtmf_configuration, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    async def remove_dtmf_configurations(
        self, *, dtmf_configuration_id: list[DTMFConfigurationId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple DTMF configurations; unresolvable ids ignored. Access: admin."""
        await self._run(
            OPS.remove_dtmf_configurations, None, {"dtmf_configuration_id": dtmf_configuration_id}, request_options
        )

    async def get_dtmf_event(
        self, *, dtmf_event_id: DTMFEventId, request_options: RequestOptions | None = None
    ) -> GetDtmfEventResult:
        """Retrieve a single DTMF event. Access: admin."""
        return await self._run(OPS.get_dtmf_event, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    async def get_dtmf_events(
        self, *, dtmf_event_id: list[DTMFEventId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetDtmfEventsResult:
        """Retrieve multiple DTMF events; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return await self._run(OPS.get_dtmf_events, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    @overload
    async def set_dtmf_event(
        self, request: SetDtmfEventRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfEventResult: ...
    @overload
    async def set_dtmf_event(
        self, /, *, dtmf_event: DTMFEvent, request_options: RequestOptions | None = None
    ) -> SetDtmfEventResult: ...
    async def set_dtmf_event(
        self,
        request: SetDtmfEventRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfEventResult:
        """Add or update a DTMF event (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_dtmf_event, request, kwargs, request_options)

    @overload
    async def set_dtmf_events(
        self, request: SetDtmfEventsRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfEventsResult: ...
    @overload
    async def set_dtmf_events(
        self, /, *, dtmf_event: list[DTMFEvent], request_options: RequestOptions | None = None
    ) -> SetDtmfEventsResult: ...
    async def set_dtmf_events(
        self,
        request: SetDtmfEventsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfEventsResult:
        """Add or update multiple DTMF events.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_dtmf_events, request, kwargs, request_options)

    async def remove_dtmf_event(
        self, *, dtmf_event_id: DTMFEventId, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a DTMF event; unresolvable id is ignored. Access: admin."""
        await self._run(OPS.remove_dtmf_event, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    async def remove_dtmf_events(
        self, *, dtmf_event_id: list[DTMFEventId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple DTMF events; unresolvable ids ignored. Access: admin."""
        await self._run(OPS.remove_dtmf_events, None, {"dtmf_event_id": dtmf_event_id}, request_options)

    async def get_dtmf_trigger(
        self, *, dtmf_trigger_id: DTMFTriggerId, request_options: RequestOptions | None = None
    ) -> GetDtmfTriggerResult:
        """Retrieve a single DTMF trigger. Access: admin."""
        return await self._run(OPS.get_dtmf_trigger, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    async def get_dtmf_triggers(
        self, *, dtmf_trigger_id: list[DTMFTriggerId] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetDtmfTriggersResult:
        """Retrieve multiple DTMF triggers; unresolvable ids ignored; no ids returns all.

        Access: admin.
        """
        return await self._run(OPS.get_dtmf_triggers, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    @overload
    async def set_dtmf_trigger(
        self, request: SetDtmfTriggerRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfTriggerResult: ...
    @overload
    async def set_dtmf_trigger(
        self, /, *, dtmf_trigger: DTMFTrigger, request_options: RequestOptions | None = None
    ) -> SetDtmfTriggerResult: ...
    async def set_dtmf_trigger(
        self,
        request: SetDtmfTriggerRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfTriggerResult:
        """Add or update a DTMF trigger (updated if Id matches, otherwise created).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_dtmf_trigger, request, kwargs, request_options)

    @overload
    async def set_dtmf_triggers(
        self, request: SetDtmfTriggersRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDtmfTriggersResult: ...
    @overload
    async def set_dtmf_triggers(
        self, /, *, dtmf_trigger: list[DTMFTrigger], request_options: RequestOptions | None = None
    ) -> SetDtmfTriggersResult: ...
    async def set_dtmf_triggers(
        self,
        request: SetDtmfTriggersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDtmfTriggersResult:
        """Add or update multiple DTMF triggers.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_dtmf_triggers, request, kwargs, request_options)

    async def remove_dtmf_trigger(
        self, *, dtmf_trigger_id: DTMFTriggerId, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a DTMF trigger; unresolvable id is ignored. Access: admin."""
        await self._run(OPS.remove_dtmf_trigger, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    async def remove_dtmf_triggers(
        self, *, dtmf_trigger_id: list[DTMFTriggerId], request_options: RequestOptions | None = None
    ) -> None:
        """Remove multiple DTMF triggers; unresolvable ids ignored. Access: admin."""
        await self._run(OPS.remove_dtmf_triggers, None, {"dtmf_trigger_id": dtmf_trigger_id}, request_options)

    async def get_vms_call_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> GetVmsCallConfigurationResult:
        """Retrieve the VMS call configuration. Access: admin."""
        return await self._run(OPS.get_vms_call_configuration, None, {}, request_options)

    @overload
    async def set_vms_call_configuration(
        self, request: SetVmsCallConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_vms_call_configuration(
        self, /, *, vms_call_configuration: VMSCallConfiguration, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_vms_call_configuration(
        self,
        request: SetVmsCallConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the VMS call configuration.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_vms_call_configuration, request, kwargs, request_options)

    async def get_default_audio_codecs(
        self, *, request_options: RequestOptions | None = None
    ) -> GetDefaultAudioCodecsResult:
        """Default audio codec priority list (highest priority first).

        Since 1.4.

        Access: admin.
        """
        return await self._run(OPS.get_default_audio_codecs, None, {}, request_options)

    async def get_supported_audio_codecs(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedAudioCodecsResult:
        """All audio codecs available in the product.

        Since 1.4.

        Access: admin.
        """
        return await self._run(OPS.get_supported_audio_codecs, None, {}, request_options)

    async def get_audio_codecs(self, *, request_options: RequestOptions | None = None) -> GetAudioCodecsResult:
        """Current audio codec priority list sent to call recipients.

        Since 1.4.

        Access: admin.
        """
        return await self._run(OPS.get_audio_codecs, None, {}, request_options)

    @overload
    async def set_audio_codecs(
        self, request: SetAudioCodecsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_audio_codecs(
        self, /, *, audio_codec: list[AudioCodec], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_audio_codecs(
        self,
        request: SetAudioCodecsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the audio codec priority list (first = highest priority).

        Since 1.4.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_audio_codecs, request, kwargs, request_options)
