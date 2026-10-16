# GENERATED from specs/apis/intercom/intercom-configuration.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read, update (POST) or replace (PUT) the general intercom configuration, including the card reader, PIN and call button settings, through the Configuration REST resource.

Docs: https://developer.axis.com/vapix/intercom/intercom-service/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.rest import RestBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ParityType = Literal["None", "Even", "Odd", "Fix0", "Fix1"]
CardOutputFormat = Literal["Raw", "Wiegand26", "Wiegand34", "Wiegand37", "Wiegand37FacilityCode", "Custom"]
FacilityCodeOverrideMode = Literal["Auto", "Optional", "Override"]
KeypressOutputFormat = Literal[
    "FourBit",
    "EightBitZeroPadded",
    "EightBitInvertPadded",
    "Wiegand26",
    "Wiegand34",
    "Wiegand37",
    "Wiegand37FacilityCode",
]
IOPinName = Literal["I1", "I2", "I3", "I4"]
AccesscontrolIntegrationProtocol = Literal["None", "IPAccess", "OSDP", "Wiegand"]
IPIntegrationProtocol = Literal["None", "RequestAccess", "RemoteActivity"]
IPAccessScheme = Literal["https", "http"]
RegisteredReaderPolicy = Literal["Fixed", "Auto"]
CallButtonIdleBehavior = Literal["Automatic", "Off", "On"]


class Attribute(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """The attribute name."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """The value of the attribute."""


class CustomOutputFormatConfiguration(Model):
    """Custom parameters used when cardFormat is Custom."""

    facility_code_size: int | None = Field(
        default=None, validation_alias="facilityCodeSize", serialization_alias="facilityCodeSize"
    )
    card_number_size: int | None = Field(
        default=None, validation_alias="cardNumberSize", serialization_alias="cardNumberSize"
    )
    start_parity: ParityType | None = Field(
        default=None, validation_alias="startParity", serialization_alias="startParity"
    )
    """The start parity bit type. Default None."""
    start_parity_bits: int | None = Field(
        default=None, validation_alias="startParityBits", serialization_alias="startParityBits"
    )
    """Number of data bits used for start parity"""
    stop_parity: ParityType | None = Field(
        default=None, validation_alias="stopParity", serialization_alias="stopParity"
    )
    """The stop parity bit type. Default None."""
    stop_parity_bits: int | None = Field(
        default=None, validation_alias="stopParityBits", serialization_alias="stopParityBits"
    )
    """Number of data bits used for stop parity"""


class OutputFormatConfiguration(Model):
    card_format: CardOutputFormat | None = Field(
        default=None, validation_alias="cardFormat", serialization_alias="cardFormat"
    )
    """How the card data is formatted. The default is Raw, which means that all following fields are disregarded."""
    card_facility_code_override_mode: FacilityCodeOverrideMode | None = Field(
        default=None,
        validation_alias="cardFacilityCodeOverrideMode",
        serialization_alias="cardFacilityCodeOverrideMode",
    )
    """Default Auto."""
    card_facility_code: int | None = Field(
        default=None, validation_alias="cardFacilityCode", serialization_alias="cardFacilityCode"
    )
    """Override facility code (Optional/Override modes); max 255 for Wiegand26, 65535 for Wiegand34 and Wiegand37FacilityCode."""
    custom: CustomOutputFormatConfiguration | None = Field(
        default=None, validation_alias="Custom", serialization_alias="Custom"
    )


class WiegandConfiguration(Model):
    """All fields optional; existing values kept if not set."""

    nbr_of_led_pins: Literal[0, 1, 2] | None = Field(
        default=None, validation_alias="nbrOfLEDPins", serialization_alias="nbrOfLEDPins"
    )
    """Number of LED control pins connected to the access control system."""
    beeper: bool | None = None
    """True if a beeper control line is connected."""
    beeper_pin: IOPinName | None = Field(default=None, validation_alias="beeperPin", serialization_alias="beeperPin")
    """The I/O input pin the beeper is connected to."""
    led1_pin: IOPinName | None = Field(default=None, validation_alias="LED1Pin", serialization_alias="LED1Pin")
    """The I/O input pin LED1 is connected to (normally green or red/green)."""
    led2_pin: IOPinName | None = Field(default=None, validation_alias="LED2Pin", serialization_alias="LED2Pin")
    """The I/O input pin LED2 is connected to (normally red)."""
    pulse_width: int | None = Field(
        default=None, validation_alias="pulseWidth", serialization_alias="pulseWidth", ge=20, le=100
    )
    """Data pulse time in µs. Default: 40."""
    pulse_interval: int | None = Field(
        default=None, validation_alias="pulseInterval", serialization_alias="pulseInterval", ge=200, le=20000
    )
    """Time between data pulses in µs. Default: 2000."""
    frame_interval: int | None = Field(
        default=None, validation_alias="frameInterval", serialization_alias="frameInterval", ge=20000, le=1000000
    )
    """Minimum time between data transfers in µs. Default: 25000."""
    led_color_default: str | None = Field(
        default=None, validation_alias="LEDColorDefault", serialization_alias="LEDColorDefault"
    )
    """Color when no wires connected (nbrOfLEDPins=0). ColorName or #RRGGBB."""
    led_color0: str | None = Field(default=None, validation_alias="LEDColor0", serialization_alias="LEDColor0")
    """1 wire"""
    led_color1: str | None = Field(default=None, validation_alias="LEDColor1", serialization_alias="LEDColor1")
    """1 wire"""
    led_color00: str | None = Field(default=None, validation_alias="LEDColor00", serialization_alias="LEDColor00")
    """2 wires"""
    led_color01: str | None = Field(default=None, validation_alias="LEDColor01", serialization_alias="LEDColor01")
    """2 wires, state 01 (LED1=1, LED2=0), typically red."""
    led_color10: str | None = Field(default=None, validation_alias="LEDColor10", serialization_alias="LEDColor10")
    """2 wires, state 10 (LED1=0, LED2=1), typically green."""
    led_color11: str | None = Field(default=None, validation_alias="LEDColor11", serialization_alias="LEDColor11")
    """2 wires, state 11, typically amber."""
    keypress_format: KeypressOutputFormat | None = Field(
        default=None, validation_alias="keypressFormat", serialization_alias="keypressFormat"
    )
    """The PIN code format. Default FourBit."""
    keypress_facility_code: int | None = Field(
        default=None, validation_alias="keypressFacilityCode", serialization_alias="keypressFacilityCode"
    )
    """Facility code for PIN; max 255 for Wiegand26, 65535 for Wiegand34/Wiegand37FacilityCode. Default: 0."""


class OSDPConfiguration(Model):
    osdp_address: int | None = Field(
        default=None, validation_alias="OSDPAddress", serialization_alias="OSDPAddress", ge=0, le=126
    )
    """The OSDP PD address (client). Default: 0."""


class PinConfiguration(Model):
    """Should match the Access Control Unit configuration."""

    pin_length: int | None = Field(
        default=None, validation_alias="pinLength", serialization_alias="pinLength", ge=0, le=32
    )
    """Number of PIN digits; 0 disables PIN. Default: 4."""
    pin_timeout: int | None = Field(
        default=None, validation_alias="pinTimeout", serialization_alias="pinTimeout", ge=1, le=60
    )
    """Seconds before returning to idle when no PIN is received. Default: 10."""


class RequestAccessConfiguration(Model):
    """Axis Request Access protocol configuration; name derived from Target and Source unless present in the AccessPoint."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Nice name of the Access point."""
    id: str | None = Field(default=None, validation_alias="Id", serialization_alias="Id")
    """Internal ID of the RequestAccess (Access point) configuration."""
    address: str | None = Field(default=None, validation_alias="Address", serialization_alias="Address")
    """Address used to access the correct controller."""
    access_controller_token: str | None = Field(
        default=None, validation_alias="AccessControllerToken", serialization_alias="AccessControllerToken"
    )
    source_token: str | None = Field(default=None, validation_alias="SourceToken", serialization_alias="SourceToken")
    """Source token (Reader / IdPoint)."""
    target_token: str | None = Field(default=None, validation_alias="TargetToken", serialization_alias="TargetToken")
    """Target token (Door)."""
    access_point_token: str | None = Field(
        default=None, validation_alias="AccessPointToken", serialization_alias="AccessPointToken"
    )


class IPAccessConfiguration(Model):
    __masked__: ClassVar[frozenset[str]] = frozenset({"password"})
    scheme: IPAccessScheme | None = Field(default=None, validation_alias="Scheme", serialization_alias="Scheme")
    """The scheme to use (optional)."""
    address: str | None = Field(default=None, validation_alias="Address", serialization_alias="Address")
    """Controller address, typically hostname[:port]."""
    username: str | None = Field(default=None, validation_alias="Username", serialization_alias="Username")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password")
    verify_certificate: bool | None = Field(
        default=None, validation_alias="VerifyCertificate", serialization_alias="VerifyCertificate"
    )
    """Default: True."""
    ip_protocol: IPIntegrationProtocol | None = Field(
        default=None, validation_alias="IPProtocol", serialization_alias="IPProtocol"
    )
    """The protocol to use (optional)."""
    request_access_configuration: RequestAccessConfiguration | None = Field(
        default=None, validation_alias="RequestAccessConfiguration", serialization_alias="RequestAccessConfiguration"
    )


class CompatibilityConfiguration(Model):
    compatibility_configs: list[Attribute] | None = Field(
        default=None, validation_alias="CompatibilityConfigs", serialization_alias="CompatibilityConfigs"
    )
    """Compatibility configuration values (see ServiceCapabilities / CompatibilityFlag)."""


KeyFormat = Literal["Plaintext", "Protected"]
DESFireKeyType = Literal["Compatible_3DES", "EV1_3DES", "EV1_3K3DES", "EV1_AES"]
DESFireCommMode = Literal["Auto", "Plain", "Plain_MACed", "Encrypted"]


class DESFireEncryption(Model):
    """Only used if cardType=MIFARE_DESFire."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"key"})
    aid: str | None = Field(default=None, validation_alias="AID", serialization_alias="AID")
    """Application ID, 3 bytes little endian first. (format=hexBinary)"""
    key_format: KeyFormat | None = Field(default=None, validation_alias="keyFormat", serialization_alias="keyFormat")
    key: str | None = None
    """16 bytes for 3DES and AES, 24 bytes for 3K3DES."""
    key_type: DESFireKeyType | None = Field(default=None, validation_alias="keyType", serialization_alias="keyType")
    comm_mode: DESFireCommMode | None = Field(default=None, validation_alias="commMode", serialization_alias="commMode")
    key_nbr: int | None = Field(default=None, validation_alias="keyNbr", serialization_alias="keyNbr", ge=0, le=13)
    """0 is the main key."""
    file_nbr: int | None = Field(default=None, validation_alias="fileNbr", serialization_alias="fileNbr", ge=0, le=31)


class MifareClassicEncryption(Model):
    """Only used if cardType=MIFARE_Classic. Sectors 0-31 have 4 blocks, 32-39 have 16 (4K cards); 16-byte blocks; total offset (+length) up to 4096 bytes."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"key_a", "key_b"})
    key_a_format: KeyFormat | None = Field(
        default=None, validation_alias="keyAFormat", serialization_alias="keyAFormat"
    )
    key_a: str | None = Field(default=None, validation_alias="keyA", serialization_alias="keyA")
    """Key A"""
    key_b_format: KeyFormat | None = Field(
        default=None, validation_alias="keyBFormat", serialization_alias="keyBFormat"
    )
    key_b: str | None = Field(default=None, validation_alias="keyB", serialization_alias="keyB")
    """Key B"""
    start_sector: int | None = Field(
        default=None, validation_alias="startSector", serialization_alias="startSector", ge=0, le=39
    )
    """Default: 0."""
    start_block: int | None = Field(
        default=None, validation_alias="startBlock", serialization_alias="startBlock", ge=0, le=15
    )
    """Default: 0."""
    skip_last_block_in_sector: bool | None = Field(
        default=None, validation_alias="skipLastBlockInSector", serialization_alias="skipLastBlockInSector"
    )


class MifareULEncryption(Model):
    """Ultralight C credentials only."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"key"})
    key_format: KeyFormat | None = Field(default=None, validation_alias="keyFormat", serialization_alias="keyFormat")
    key: str | None = None
    """Optional 16-byte key (Ultralight C only)."""


class CardDataConfig(Model):
    """How to extract a data chunk from an RFID card, including addressing and (sensitive) credentials."""

    name: str | None = None
    """Unique identifier (e.g. face template, fingerprint, employee_id); the resulting CardData uses this name."""
    card_type: str | None = Field(default=None, validation_alias="cardType", serialization_alias="cardType")
    """Card type this configuration is valid for (CardTypeNames)."""
    data_source: str | None = Field(default=None, validation_alias="dataSource", serialization_alias="dataSource")
    """CardDataSources. Default: 'CSN'."""
    enabled: bool | None = None
    """Disabled configs are kept but not used."""
    required: bool | None = None
    """If true and extraction fails, the call fails and the swipe is ignored; if false the chunk is omitted."""
    use_as_uid: bool | None = Field(default=None, validation_alias="useAsUid", serialization_alias="useAsUid")
    """Replace the original UID with extracted data; multiple are concatenated."""
    offset_byte: int | None = Field(default=None, validation_alias="offsetByte", serialization_alias="offsetByte")
    """Default: 0."""
    length_in_bytes: int | None = Field(
        default=None, validation_alias="lengthInBytes", serialization_alias="lengthInBytes"
    )
    """0 = all. Default: 0."""
    offset_bits: int | None = Field(default=None, validation_alias="offsetBits", serialization_alias="offsetBits")
    """Default: 0."""
    length_in_bits: int | None = Field(
        default=None, validation_alias="lengthInBits", serialization_alias="lengthInBits"
    )
    """0 = all. Bytes and bits sum (bytes*8+bits). Default: 0."""
    attributes: list[Attribute] | None = None
    """For future use."""
    des_fire_encryption: DESFireEncryption | None = Field(
        default=None, validation_alias="DESFireEncryption", serialization_alias="DESFireEncryption"
    )
    mifare_classic_encryption: MifareClassicEncryption | None = Field(
        default=None, validation_alias="MifareClassicEncryption", serialization_alias="MifareClassicEncryption"
    )
    mifare_ul_encryption: MifareULEncryption | None = Field(
        default=None, validation_alias="MifareULEncryption", serialization_alias="MifareULEncryption"
    )


class RegisteredReaderConfiguration(Model):
    reader_ids: list[str] | None = Field(default=None, validation_alias="ReaderIds", serialization_alias="ReaderIds")
    """Readers allowed to InjectTag (only when Policy is Fixed). Default: ['Internal']."""
    policy: RegisteredReaderPolicy | None = Field(default=None, validation_alias="Policy", serialization_alias="Policy")
    """The policy to use."""


class CardReaderConfiguration(Model):
    """All fields optional; current values kept unless specified in SetConfiguration/UpdateConfiguration."""

    protocol: AccesscontrolIntegrationProtocol | None = Field(
        default=None, validation_alias="Protocol", serialization_alias="Protocol"
    )
    """The integration protocol."""
    card_types: list[str] | None = Field(default=None, validation_alias="CardTypes", serialization_alias="CardTypes")
    """Accepted card types (CardTypeNames)."""
    wiegand_configuration: WiegandConfiguration | None = Field(
        default=None, validation_alias="WiegandConfiguration", serialization_alias="WiegandConfiguration"
    )
    osdp_configuration: OSDPConfiguration | None = Field(
        default=None, validation_alias="OSDPConfiguration", serialization_alias="OSDPConfiguration"
    )
    pin_configuration: PinConfiguration | None = Field(
        default=None, validation_alias="PinConfiguration", serialization_alias="PinConfiguration"
    )
    ip_access_configuration: IPAccessConfiguration | None = Field(
        default=None, validation_alias="IPAccessConfiguration", serialization_alias="IPAccessConfiguration"
    )
    compatibility_configuration: CompatibilityConfiguration | None = Field(
        default=None, validation_alias="CompatibilityConfiguration", serialization_alias="CompatibilityConfiguration"
    )
    card_data_configs: list[CardDataConfig] | None = Field(
        default=None, validation_alias="CardDataConfigs", serialization_alias="CardDataConfigs"
    )
    """Optional. Ways to extract CardData."""
    registered_reader_configuration: RegisteredReaderConfiguration | None = Field(
        default=None,
        validation_alias="RegisteredReaderConfiguration",
        serialization_alias="RegisteredReaderConfiguration",
    )
    output_format: OutputFormatConfiguration | None = Field(
        default=None, validation_alias="OutputFormat", serialization_alias="OutputFormat"
    )
    sensitive_rfid_event_enabled: bool | None = Field(
        default=None, validation_alias="SensitiveRFIDEventEnabled", serialization_alias="SensitiveRFIDEventEnabled"
    )
    """True if actual UID and card number are present in events."""
    sensitive_pin_event_enabled: bool | None = Field(
        default=None, validation_alias="SensitivePINEventEnabled", serialization_alias="SensitivePINEventEnabled"
    )
    """True if the actual PIN is present in events."""


SuppressionMode = Literal["None", "Timeout", "NeverHangUp"]


class CallButtonConfiguration(Model):
    call_button_key_trigger: str | None = Field(
        default=None, validation_alias="callButtonKeyTrigger", serialization_alias="callButtonKeyTrigger"
    )
    """The call button, represented by the letter 'C'."""
    suppression_timeout: int | None = Field(
        default=None, validation_alias="suppressionTimeout", serialization_alias="suppressionTimeout"
    )
    """Seconds the call button is suppressed. Default: 1."""
    suppression_mode: SuppressionMode | None = Field(
        default=None, validation_alias="suppressionMode", serialization_alias="suppressionMode"
    )


DefaultContactSorting = Literal["SortByFirstName", "SortByLastName"]
DefaultNameFormat = Literal["FirstNameFirst", "LastNameFirst"]


class Configuration(Model):
    """General intercom configuration. Optional fields not set keep current value."""

    version: str | None = Field(default=None, validation_alias="Version", serialization_alias="Version")
    call_triggers_enabled: bool | None = Field(
        default=None, validation_alias="CallTriggersEnabled", serialization_alias="CallTriggersEnabled"
    )
    """Processing triggers in PhonebookEntries enabled."""
    call_by_numbers_enabled: bool | None = Field(
        default=None, validation_alias="CallByNumbersEnabled", serialization_alias="CallByNumbersEnabled"
    )
    """Calls to dialed numbers not matching any CallRule enabled."""
    default_contact_sorting: DefaultContactSorting | None = Field(
        default=None, validation_alias="DefaultContactSorting", serialization_alias="DefaultContactSorting"
    )
    default_name_format: DefaultNameFormat | None = Field(
        default=None, validation_alias="DefaultNameFormat", serialization_alias="DefaultNameFormat"
    )
    default_call_by_number_sip_account_id: str | None = Field(
        default=None,
        validation_alias="DefaultCallByNumberSIPAccountId",
        serialization_alias="DefaultCallByNumberSIPAccountId",
    )
    """Optional. Default SIPAccount used by CallByNumber."""
    audioclip_volume: int | None = Field(
        default=None, validation_alias="AudioclipVolume", serialization_alias="AudioclipVolume", ge=0, le=1000
    )
    """Volume for built-in audio files (button presses, calling, ringing). Default: 100."""
    beeper_volume: int | None = Field(
        default=None, validation_alias="BeeperVolume", serialization_alias="BeeperVolume", ge=0, le=100
    )
    """Beeper (Wiegand and OSDP) feedback volume. Default: 80."""
    presence_timeout: int | None = Field(
        default=None, validation_alias="PresenceTimeout", serialization_alias="PresenceTimeout", ge=2, le=86400
    )
    """Seconds before user presence times out. Default: 12."""
    card_reader_configuration: CardReaderConfiguration | None = Field(
        default=None, validation_alias="CardReaderConfiguration", serialization_alias="CardReaderConfiguration"
    )
    call_button_configurations: list[CallButtonConfiguration] | None = Field(
        default=None, validation_alias="CallButtonConfigurations", serialization_alias="CallButtonConfigurations"
    )
    call_button_idle_behavior: CallButtonIdleBehavior | None = Field(
        default=None, validation_alias="CallButtonIdleBehavior", serialization_alias="CallButtonIdleBehavior"
    )


class GetConfigurationRequest(Model):
    include_image_file: bool | None = Field(
        default=None, validation_alias="includeImageFile", serialization_alias="includeImageFile"
    )
    """Include imageFile fields in the response."""


class GetConfigurationResult(Model):
    configuration: Configuration | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )


class UpdateConfigurationRequest(Model):
    configuration: Configuration | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )
    """Configuration to set (POST/PUT)."""
    image_file: dict[str, Any] | None = Field(
        default=None, validation_alias="imageFile", serialization_alias="imageFile"
    )
    """ImageFile used to update an image (ImageFile type not documented)."""


class UpdateConfigurationResult(Model):
    configuration: Configuration | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )


class SetConfigurationRequest(Model):
    configuration: Configuration | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )
    """Configuration to set (POST/PUT)."""
    image_file: dict[str, Any] | None = Field(
        default=None, validation_alias="imageFile", serialization_alias="imageFile"
    )
    """ImageFile used to update an image (ImageFile type not documented)."""


class SetConfigurationResult(Model):
    configuration: Configuration | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/vapix/intercom/Configuration"

INFO = ApiInfo(
    id="intercom-configuration",
    name="Intercom configuration resource",
    family=Family.REST,
    discovery=(
        ParamDiscovery("Properties.API.Intercom.Intercom", "yes"),
        ParamDiscovery("Properties.API.Intercom.Version", "1.1"),
        ApiDiscovery("intercom-api"),
        ApiDiscovery("intercom-reader"),
    ),
    docs=("https://developer.axis.com/vapix/intercom/intercom-service/",),
    errors={
        400: ErrorCode(
            "Invalid request (env:Sender ter:InvalidArgVal: invalid argument; ter:InvalidArgs: missing or invalid combination of inputs; ter:TagMismatch: unknown field).",
            "invalid_argument",
        )
    },
)


class OPS:
    get_configuration = Operation(
        INFO,
        "get_configuration",
        RestBinding("GET", ROOT, query=(("include_image_file", "includeImageFile"),)),
        params=GetConfigurationRequest,
        result=GetConfigurationResult,
        access="admin",
        effect="read",
    )
    update_configuration = Operation(
        INFO,
        "update_configuration",
        RestBinding("POST", ROOT, body="object"),
        params=UpdateConfigurationRequest,
        result=UpdateConfigurationResult,
        access="admin",
        effect="write",
        write="patch",
        errors={400: ErrorCode("Invalid argument or invalid combination of inputs.", "invalid_argument")},
    )
    set_configuration = Operation(
        INFO,
        "set_configuration",
        RestBinding("PUT", ROOT, body="object"),
        params=SetConfigurationRequest,
        result=SetConfigurationResult,
        access="admin",
        effect="write",
        write="replace",
    )


# ---------------------------------------------------------------------------
# API classes


class IntercomConfigurationApi(SyncApi):
    """Intercom configuration resource (``intercom-configuration``)."""

    INFO = INFO

    def get_configuration(
        self, *, include_image_file: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetConfigurationResult:
        """Get the configuration (GET). Access: admin."""
        return self._run(OPS.get_configuration, None, {"include_image_file": include_image_file}, request_options)

    @overload
    def update_configuration(
        self, request: UpdateConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> UpdateConfigurationResult: ...
    @overload
    def update_configuration(
        self,
        /,
        *,
        configuration: Configuration | MISSING = MISSING,
        image_file: Mapping[str, Any] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UpdateConfigurationResult: ...
    def update_configuration(
        self,
        request: UpdateConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> UpdateConfigurationResult:
        """Update the configuration (POST, UpdateConfiguration).

        Only the given fields change; omitted fields keep their values.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.update_configuration, request, kwargs, request_options)

    @overload
    def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetConfigurationResult: ...
    @overload
    def set_configuration(
        self,
        /,
        *,
        configuration: Configuration | MISSING = MISSING,
        image_file: Mapping[str, Any] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SetConfigurationResult: ...
    def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetConfigurationResult:
        """Replace the configuration (PUT, SetConfiguration).

        An optional field that is not set keeps its current value.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_configuration, request, kwargs, request_options)


class AsyncIntercomConfigurationApi(AsyncApi):
    """Intercom configuration resource (``intercom-configuration``)."""

    INFO = INFO

    async def get_configuration(
        self, *, include_image_file: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetConfigurationResult:
        """Get the configuration (GET). Access: admin."""
        return await self._run(OPS.get_configuration, None, {"include_image_file": include_image_file}, request_options)

    @overload
    async def update_configuration(
        self, request: UpdateConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> UpdateConfigurationResult: ...
    @overload
    async def update_configuration(
        self,
        /,
        *,
        configuration: Configuration | MISSING = MISSING,
        image_file: Mapping[str, Any] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UpdateConfigurationResult: ...
    async def update_configuration(
        self,
        request: UpdateConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> UpdateConfigurationResult:
        """Update the configuration (POST, UpdateConfiguration).

        Only the given fields change; omitted fields keep their values.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.update_configuration, request, kwargs, request_options)

    @overload
    async def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetConfigurationResult: ...
    @overload
    async def set_configuration(
        self,
        /,
        *,
        configuration: Configuration | MISSING = MISSING,
        image_file: Mapping[str, Any] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SetConfigurationResult: ...
    async def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetConfigurationResult:
        """Replace the configuration (PUT, SetConfiguration).

        An optional field that is not set keeps its current value.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_configuration, request, kwargs, request_options)
