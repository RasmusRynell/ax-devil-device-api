# GENERATED from specs/apis/intercom/intercom-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the intercom: card reader and access control integration (OSDP, Wiegand, IP), card types and card data, tags, PIN keypad and user interface feedback.

Docs: https://developer.axis.com/vapix/intercom/intercom-service/
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Attribute(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """The attribute name."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """The value of the attribute."""


class AttributeInfo(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    type: Literal["bool", "int", "string"] | None = Field(
        default=None, validation_alias="Type", serialization_alias="Type"
    )
    """bool = boolean, int = integer, string."""


CardTypeCategory = Literal["HighFrequency", "LowFrequency"]


class CardType(Model):
    """Description of a card type."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Card type identifier (see CardTypeNames)."""
    display_name: str | None = Field(default=None, validation_alias="DisplayName", serialization_alias="DisplayName")
    """UI-friendly name."""
    category: CardTypeCategory | None = Field(default=None, validation_alias="Category", serialization_alias="Category")
    data_sources: list[str] | None = Field(
        default=None, validation_alias="DataSources", serialization_alias="DataSources"
    )
    """Supported data sources (see CardDataSources)."""


class CustomOutputFormatConfiguration(Model):
    """Custom parameters used when cardFormat is Custom."""

    facility_code_size: int | None = Field(
        default=None, validation_alias="facilityCodeSize", serialization_alias="facilityCodeSize"
    )
    card_number_size: int | None = Field(
        default=None, validation_alias="cardNumberSize", serialization_alias="cardNumberSize"
    )
    start_parity: str | None = Field(default=None, validation_alias="startParity", serialization_alias="startParity")
    """ParityType. Default: 'None'."""
    start_parity_bits: int | None = Field(
        default=None, validation_alias="startParityBits", serialization_alias="startParityBits"
    )
    """Number of data bits used for start parity"""
    stop_parity: str | None = Field(default=None, validation_alias="stopParity", serialization_alias="stopParity")
    """ParityType. Default: 'None'."""
    stop_parity_bits: int | None = Field(
        default=None, validation_alias="stopParityBits", serialization_alias="stopParityBits"
    )
    """Number of data bits used for stop parity"""


class OutputFormatConfiguration(Model):
    card_format: str | None = Field(default=None, validation_alias="cardFormat", serialization_alias="cardFormat")
    """CardOutputFormat; Raw means all following fields are disregarded. Default: 'Raw'."""
    card_facility_code_override_mode: str | None = Field(
        default=None,
        validation_alias="cardFacilityCodeOverrideMode",
        serialization_alias="cardFacilityCodeOverrideMode",
    )
    """FacilityCodeOverrideMode. Default: 'Auto'."""
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
    beeper_pin: str | None = Field(default=None, validation_alias="beeperPin", serialization_alias="beeperPin")
    """IOPinName of the beeper input."""
    led1_pin: str | None = Field(default=None, validation_alias="LED1Pin", serialization_alias="LED1Pin")
    """IOPinName for LED1 (normally green or red/green)."""
    led2_pin: str | None = Field(default=None, validation_alias="LED2Pin", serialization_alias="LED2Pin")
    """IOPinName for LED2 (normally red)."""
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
    keypress_format: str | None = Field(
        default=None, validation_alias="keypressFormat", serialization_alias="keypressFormat"
    )
    """KeypressOutputFormat. Default: 'FourBit'."""
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
    scheme: str | None = Field(default=None, validation_alias="Scheme", serialization_alias="Scheme")
    """Optional. IPAccessScheme."""
    address: str | None = Field(default=None, validation_alias="Address", serialization_alias="Address")
    """Controller address, typically hostname[:port]."""
    username: str | None = Field(default=None, validation_alias="Username", serialization_alias="Username")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password")
    verify_certificate: bool | None = Field(
        default=None, validation_alias="VerifyCertificate", serialization_alias="VerifyCertificate"
    )
    """Default: True."""
    ip_protocol: str | None = Field(default=None, validation_alias="IPProtocol", serialization_alias="IPProtocol")
    """Optional. IPIntegrationProtocol."""
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

    aid: str | None = Field(default=None, validation_alias="AID", serialization_alias="AID")
    """Application ID, 3 bytes little endian first."""
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
    policy: str | None = Field(default=None, validation_alias="Policy", serialization_alias="Policy")
    """RegisteredReaderPolicy."""


class CardReaderConfiguration(Model):
    """All fields optional; current values kept unless specified in SetConfiguration/UpdateConfiguration."""

    protocol: str | None = Field(default=None, validation_alias="Protocol", serialization_alias="Protocol")
    """AccesscontrolIntegrationProtocol."""
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


class TagPresentedInfo(Model):
    """Describes the tag together with metadata."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"card_number", "facility_code"})
    tag_uid: str | None = Field(default=None, validation_alias="TagUid", serialization_alias="TagUid", max_length=64)
    """UID of the tag. ASCII encoded hex value (32 bytes max), right justified."""
    bit_count: int | None = Field(default=None, validation_alias="BitCount", serialization_alias="BitCount")
    """Number of bits in TagUid."""
    tag_type: str | None = Field(default=None, validation_alias="TagType", serialization_alias="TagType")
    """Tag type, e.g. MIFARE_Classic (CardTypeNames)."""
    reader_id: str | None = Field(default=None, validation_alias="ReaderId", serialization_alias="ReaderId")
    """Reader ID; 'Internal' is the built-in reader; can be set with InjectTag."""
    age: int | None = Field(default=None, validation_alias="Age", serialization_alias="Age")
    """Seconds since the tag was presented."""
    facility_code: str | None = Field(default=None, validation_alias="FacilityCode", serialization_alias="FacilityCode")
    """Facility code in decimals (<64-bit). Null or empty = unavailable."""
    card_number: str | None = Field(default=None, validation_alias="CardNumber", serialization_alias="CardNumber")
    """Card number in decimals (<64-bit). Null or empty = unavailable."""
    format: str | None = Field(default=None, validation_alias="Format", serialization_alias="Format")
    """Detected card data format (CardOutputFormat). Default: 'Raw'."""
    masked: bool | None = Field(default=None, validation_alias="Masked", serialization_alias="Masked")
    """True if the reader is masked. Default: False."""


class CardData(Model):
    """Data chunk extracted from an RFID card (GetCardData result, InjectTag parameter)."""

    name: str | None = None
    """Name of the data chunk (from the CardDataConfig)."""
    bit_count: int | None = Field(default=None, validation_alias="bitCount", serialization_alias="bitCount")
    """Number of valuable data bits (left-justified)."""
    byte_count: int | None = Field(default=None, validation_alias="byteCount", serialization_alias="byteCount")
    """Bytes holding the chunk (bitCount <= byteCount*8)."""
    data: str | None = None
    """The data chunk."""


class ReaderIdWithMask(Model):
    reader_id: str | None = Field(default=None, validation_alias="readerId", serialization_alias="readerId")
    is_masked: bool | None = Field(default=None, validation_alias="isMasked", serialization_alias="isMasked")
    """True if card data is not sent using the configured protocol."""


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


class IntegerValidator(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    min: int | None = Field(default=None, validation_alias="Min", serialization_alias="Min")
    max: int | None = Field(default=None, validation_alias="Max", serialization_alias="Max")


TargetLedType = Literal["backlight", "callButton", "stripe", "statusDoor", "statusCall", "statusSpeak"]
LedControlType = Literal["none", "onoff", "pwm", "rgb", "rgbpwm"]


class UiLed(Model):
    led_id: TargetLedType | None = Field(default=None, validation_alias="ledId", serialization_alias="ledId")
    led_type: LedControlType | None = Field(default=None, validation_alias="ledType", serialization_alias="ledType")


class ServiceCapabilities(Model):
    version: str | None = Field(default=None, validation_alias="Version", serialization_alias="Version")
    call: bool | None = Field(default=None, validation_alias="Call", serialization_alias="Call")
    dtmf_event: bool | None = Field(default=None, validation_alias="DTMFEvent", serialization_alias="DTMFEvent")
    call_button: bool | None = Field(default=None, validation_alias="CallButton", serialization_alias="CallButton")
    call_keypad: bool | None = Field(default=None, validation_alias="CallKeypad", serialization_alias="CallKeypad")
    pin_keypad: bool | None = Field(default=None, validation_alias="PinKeypad", serialization_alias="PinKeypad")
    reader: bool | None = Field(default=None, validation_alias="Reader", serialization_alias="Reader")
    ui_leds: list[UiLed] | None = Field(default=None, validation_alias="uiLeds", serialization_alias="uiLeds")
    accesscontrol_integration_protocols: list[str] | None = Field(
        default=None,
        validation_alias="AccesscontrolIntegrationProtocols",
        serialization_alias="AccesscontrolIntegrationProtocols",
    )
    supported_cards: list[CardType] | None = Field(
        default=None, validation_alias="SupportedCards", serialization_alias="SupportedCards"
    )
    supported_io_pins: list[str] | None = Field(
        default=None, validation_alias="SupportedIOPins", serialization_alias="SupportedIOPins"
    )
    supported_color_names: list[str] | None = Field(
        default=None, validation_alias="SupportedColorNames", serialization_alias="SupportedColorNames"
    )
    integer_validators: list[IntegerValidator] | None = Field(
        default=None, validation_alias="IntegerValidators", serialization_alias="IntegerValidators"
    )
    compatibility_configs: list[AttributeInfo] | None = Field(
        default=None, validation_alias="CompatibilityConfigs", serialization_alias="CompatibilityConfigs"
    )
    supported_keypress_output_format_wiegand: list[str] | None = Field(
        default=None,
        validation_alias="SupportedKeypressOutputFormatWiegand",
        serialization_alias="SupportedKeypressOutputFormatWiegand",
    )
    supported_card_output_format: list[str] | None = Field(
        default=None, validation_alias="SupportedCardOutputFormat", serialization_alias="SupportedCardOutputFormat"
    )
    supported_facility_code_override_mode: list[str] | None = Field(
        default=None,
        validation_alias="SupportedFacilityCodeOverrideMode",
        serialization_alias="SupportedFacilityCodeOverrideMode",
    )
    supported_parity_type: list[str] | None = Field(
        default=None, validation_alias="SupportedParityType", serialization_alias="SupportedParityType"
    )
    supported_call_button_idle_behavior: list[str] | None = Field(
        default=None,
        validation_alias="SupportedCallButtonIdleBehavior",
        serialization_alias="SupportedCallButtonIdleBehavior",
    )
    supported_default_contact_sorting: list[str] | None = Field(
        default=None,
        validation_alias="SupportedDefaultContactSorting",
        serialization_alias="SupportedDefaultContactSorting",
    )
    supported_default_name_format: list[str] | None = Field(
        default=None, validation_alias="SupportedDefaultNameFormat", serialization_alias="SupportedDefaultNameFormat"
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
    call_button_idle_behavior: str | None = Field(
        default=None, validation_alias="CallButtonIdleBehavior", serialization_alias="CallButtonIdleBehavior"
    )
    """CallButtonIdleBehavior."""


class CallButtonInformation(Model):
    vms_call_enabled: bool | None = Field(
        default=None, validation_alias="VMSCallEnabled", serialization_alias="VMSCallEnabled"
    )
    """Current status of the CallButtonVMS."""
    number_of_recipients: int | None = Field(
        default=None, validation_alias="NumberOfRecipients", serialization_alias="NumberOfRecipients"
    )


class ContactsInformation(Model):
    number_of_contacts: int | None = Field(
        default=None, validation_alias="NumberOfContacts", serialization_alias="NumberOfContacts"
    )
    number_of_organizations: int | None = Field(
        default=None, validation_alias="NumberOfOrganizations", serialization_alias="NumberOfOrganizations"
    )


class IPAccessOption(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Door name visible to the user."""
    id: str | None = Field(default=None, validation_alias="Id", serialization_alias="Id")
    ip_protocol: str | None = Field(default=None, validation_alias="IPProtocol", serialization_alias="IPProtocol")
    """Detected IPIntegrationProtocol."""


class UiLedFeedback(Model):
    """ColorName or #RRGGBB (monochrome: LSB only; RGB: LSB blue, 2nd green, 3rd red). PWM: 0-255; non-PWM: 0 off, 1-255 on."""

    led: str | None = None
    """TargetLedType."""
    run_style: str | None = Field(default=None, validation_alias="runStyle", serialization_alias="runStyle")
    """RunStyleType."""
    duration_on_millisec: int | None = Field(
        default=None, validation_alias="durationOnMillisec", serialization_alias="durationOnMillisec"
    )
    duration_off_millisec: int | None = Field(
        default=None, validation_alias="durationOffMillisec", serialization_alias="durationOffMillisec"
    )
    value_on: str | None = Field(default=None, validation_alias="valueOn", serialization_alias="valueOn")
    value_off: str | None = Field(default=None, validation_alias="valueOff", serialization_alias="valueOff")
    loops: int | None = None
    handled: bool | None = None
    """Initially false; marks feedback as displayed."""


class UiAudioFeedback(Model):
    duration_on_millisec: int | None = Field(
        default=None, validation_alias="durationOnMillisec", serialization_alias="durationOnMillisec"
    )
    duration_off_millisec: int | None = Field(
        default=None, validation_alias="durationOffMillisec", serialization_alias="durationOffMillisec"
    )
    loops: int | None = None
    handled: bool | None = None
    file: str | None = None
    """Audio file to play."""


class UiGraphicFeedback(Model):
    image: str | None = None
    """Path to image or base64 data URL."""
    duration_millisec: int | None = Field(
        default=None, validation_alias="durationMillisec", serialization_alias="durationMillisec"
    )


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities of the service."""


class SetConfigurationRequest(Model):
    configuration: Configuration = Field(validation_alias="Configuration", serialization_alias="Configuration")
    """The configuration to set."""


class UpdateConfigurationRequest(Model):
    configuration: Configuration = Field(validation_alias="Configuration", serialization_alias="Configuration")
    """Partial configuration."""


class GetConfigurationRequest(Model):
    include_image_file: bool | None = Field(
        default=None, validation_alias="includeImageFile", serialization_alias="includeImageFile"
    )
    """If true, all imageFile fields are included in the response."""


class GetConfigurationResult(Model):
    configuration: Configuration = Field(validation_alias="Configuration", serialization_alias="Configuration")
    """The configuration."""


class GetServerReportResult(Model):
    configuration: Configuration = Field(validation_alias="Configuration", serialization_alias="Configuration")
    """The configuration fields that are safe to report."""
    discarded_fields: list[str] = Field(validation_alias="DiscardedFields", serialization_alias="DiscardedFields")
    """The configuration fields discarded because they contain sensitive data."""
    call_button_information: CallButtonInformation | None = Field(
        default=None, validation_alias="CallButtonInformation", serialization_alias="CallButtonInformation"
    )
    contacts_information: ContactsInformation | None = Field(
        default=None, validation_alias="ContactsInformation", serialization_alias="ContactsInformation"
    )


class GetCardReaderConfigurationResult(Model):
    card_reader_configuration: CardReaderConfiguration = Field(
        validation_alias="CardReaderConfiguration", serialization_alias="CardReaderConfiguration"
    )
    """The card reader configuration."""


class GetSupportedTagTypesResult(Model):
    card_types: list[CardType] | None = Field(
        default=None, validation_alias="CardTypes", serialization_alias="CardTypes"
    )
    """The tag types the reader supports."""


class GetDefaultTagTypesResult(Model):
    card_types: list[str] | None = Field(default=None, validation_alias="CardTypes", serialization_alias="CardTypes")
    """The card types enabled by default."""


class GetLastTagRequest(Model):
    reader_id: str | None = Field(default=None, validation_alias="ReaderId", serialization_alias="ReaderId")
    """Reader to get the last tag from; if omitted the last tag is returned."""


class GetLastTagResult(Model):
    tag: TagPresentedInfo = Field(validation_alias="Tag", serialization_alias="Tag")
    """The tag last seen."""


class GetTagRequest(Model):
    reader_id: str | None = Field(default=None, validation_alias="ReaderId", serialization_alias="ReaderId")
    """Reader ID."""
    timestamp: str | None = None
    """Timestamp from the RFID event notification; ensures data matches the event."""


class GetTagResult(Model):
    tag: TagPresentedInfo = Field(validation_alias="Tag", serialization_alias="Tag")
    """The tag matching the input parameters."""


class InjectTagRequest(Model):
    tag: TagPresentedInfo = Field(validation_alias="Tag", serialization_alias="Tag")
    """Tag to inject."""
    card_data: list[CardData] | None = Field(default=None, validation_alias="CardData", serialization_alias="CardData")
    """Card data to inject."""


class RegisterReaderRequest(Model):
    reader_id: str = Field(validation_alias="ReaderId", serialization_alias="ReaderId")
    """ID of the external reader."""
    disable_internal_reader: bool | None = Field(
        default=None, validation_alias="DisableInternalReader", serialization_alias="DisableInternalReader"
    )
    """If true, all internal readers are added to MaskedReaderIds."""
    masked_reader_ids: list[str] | None = Field(
        default=None, validation_alias="MaskedReaderIds", serialization_alias="MaskedReaderIds"
    )
    """Readers to mask (data still available as RFID events). Default masks nothing."""
    unmask_if_lost: bool | None = Field(
        default=None, validation_alias="UnmaskIfLost", serialization_alias="UnmaskIfLost"
    )
    """Release masked readers when the registration times out. Default: False."""


class RegisterReaderResult(Model):
    timeout: int = Field(validation_alias="Timeout", serialization_alias="Timeout")
    """Seconds until registration expires."""


class UnregisterReaderRequest(Model):
    reader_id: str = Field(validation_alias="ReaderId", serialization_alias="ReaderId")
    """ID of the external reader."""


class KeepAliveReaderRequest(Model):
    reader_id: str = Field(validation_alias="ReaderId", serialization_alias="ReaderId")
    """ID of the external reader."""


class KeepAliveReaderResult(Model):
    timeout: int = Field(validation_alias="Timeout", serialization_alias="Timeout")
    """Seconds until registration expires."""


class GetCurrentReadersResult(Model):
    readers: list[ReaderIdWithMask] | None = Field(
        default=None, validation_alias="Readers", serialization_alias="Readers"
    )
    """The available ReaderIds together with a masked flag."""


class ProbeIpAccessConfigurationRequest(Model):
    ip_access_configuration: IPAccessConfiguration = Field(
        validation_alias="IPAccessConfiguration", serialization_alias="IPAccessConfiguration"
    )
    """The IPAccessConfiguration."""


class ProbeIpAccessConfigurationResult(Model):
    status: str = Field(validation_alias="Status", serialization_alias="Status")
    """The status of the probe request (ProbeIPAccessStatus)."""
    status_text: str | None = Field(default=None, validation_alias="StatusText", serialization_alias="StatusText")
    """Textual status related to Status."""
    ip_access_options: list[IPAccessOption] = Field(
        validation_alias="IPAccessOptions", serialization_alias="IPAccessOptions"
    )
    """The selectable configurations."""
    suggested_id: str | None = Field(default=None, validation_alias="SuggestedId", serialization_alias="SuggestedId")
    """A configuration ID that matches the current configuration; omitted if none matches."""
    current_name: str | None = Field(default=None, validation_alias="CurrentName", serialization_alias="CurrentName")
    """The name of the current configuration, a hint when SuggestedId is absent."""


class UpdateIpAccessConfigurationRequest(Model):
    id: str = Field(validation_alias="Id", serialization_alias="Id")
    """ID from an IPAccessOption."""


class UpdateIpAccessConfigurationResult(Model):
    ip_access_configuration: IPAccessConfiguration | None = Field(
        default=None, validation_alias="IPAccessConfiguration", serialization_alias="IPAccessConfiguration"
    )
    """The resulting configuration."""


class GetCardDataRequest(Model):
    data_config_names: list[str] | None = Field(
        default=None, validation_alias="DataConfigNames", serialization_alias="DataConfigNames"
    )
    """Names under CardReaderConfiguration/CardDataConfigs."""
    card_data_configs: list[CardDataConfig] | None = Field(
        default=None, validation_alias="CardDataConfigs", serialization_alias="CardDataConfigs"
    )
    """Ad-hoc configurations (not stored)."""


class GetCardDataResult(Model):
    card_data: list[CardData] | None = Field(default=None, validation_alias="CardData", serialization_alias="CardData")
    """The extracted card data."""


class GetLastKeySequenceRequest(Model):
    source: str | None = Field(default=None, validation_alias="Source", serialization_alias="Source")
    """Source to get from; default last source (PinSourceType reserved ids)."""
    timestamp: str | None = None
    """Exact timestamp from Device/Intercom/KeyPin event."""


class GetLastKeySequenceResult(Model):
    key_sequence: str | None = Field(default=None, validation_alias="KeySequence", serialization_alias="KeySequence")
    """The latest completed key sequence."""
    source: str | None = Field(default=None, validation_alias="Source", serialization_alias="Source")
    """The source of the key sequence."""
    timestamp: str | None = None
    """When the key sequence was completed."""


class InjectKeySequenceRequest(Model):
    key_sequence: str = Field(validation_alias="KeySequence", serialization_alias="KeySequence")
    """The key sequence."""
    source: str | None = Field(default=None, validation_alias="Source", serialization_alias="Source")
    """Component posting the call."""


class SetUiFeedbackRequest(Model):
    highlevel_feedbacks: list[str] | None = Field(
        default=None, validation_alias="highlevelFeedbacks", serialization_alias="highlevelFeedbacks"
    )
    """UIHighLevelFeedback values."""
    led_feedbacks: list[UiLedFeedback] | None = Field(
        default=None, validation_alias="ledFeedbacks", serialization_alias="ledFeedbacks"
    )
    """LED feedbacks."""
    audio_feedback: UiAudioFeedback | None = Field(
        default=None, validation_alias="audioFeedback", serialization_alias="audioFeedback"
    )
    """Audio feedback."""
    source: str | None = None
    """Identifier of the posting component (FeedbackSourceType reserved)."""
    text: str | None = None
    """Text to display or speak."""
    attributes: list[Attribute] | None = None
    """Additional attributes."""
    graphic_feedback: UiGraphicFeedback | None = Field(
        default=None, validation_alias="graphicFeedback", serialization_alias="graphicFeedback"
    )
    """Graphic feedback."""


class SetUiFeedbackResult(Model):
    result: bool = Field(validation_alias="Result", serialization_alias="Result")
    """The result of the operation."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/intercom"

INFO = ApiInfo(
    id="intercom-service",
    name="Intercom service",
    family=Family.SERVICE_JSON,
    discovery=(
        ParamDiscovery("Properties.API.Intercom.Intercom", "yes"),
        ParamDiscovery("Properties.API.Intercom.Version", "1.1"),
        ApiDiscovery("intercom-api"),
        ApiDiscovery("intercom-reader"),
    ),
    docs=("https://developer.axis.com/vapix/intercom/intercom-service/",),
    errors={
        "ter:TagMismatch": ErrorCode(
            "A field in the request is not recognised (JSON parse error).", "invalid_argument"
        ),
        "ter:InvalidArgVal": ErrorCode(
            "The request contains an invalid argument, for example BeeperVolume should be <= 100.", "invalid_argument"
        ),
        "ter:InvalidArgs": ErrorCode(
            "The request is missing something or has an invalid combination of inputs.", "invalid_argument"
        ),
        "ter:NotSupported": ErrorCode("The method is not supported.", "unsupported"),
        "ter:NotFound": ErrorCode("No matching item was found.", "not_found"),
        "ter:Failure": ErrorCode("The operation failed.", "internal"),
    },
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "GetServiceCapabilities"),
        result=GetServiceCapabilitiesResult,
        access="admin",
        effect="read",
    )
    set_configuration = Operation(
        INFO,
        "set_configuration",
        ServiceJsonBinding(PATH, "SetConfiguration"),
        params=SetConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:InvalidArgVal": ErrorCode("The request contains an invalid argument.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "The request is missing something or has an invalid combination of inputs.", "invalid_argument"
            ),
        },
    )
    update_configuration = Operation(
        INFO,
        "update_configuration",
        ServiceJsonBinding(PATH, "UpdateConfiguration"),
        params=UpdateConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:InvalidArgVal": ErrorCode("The request contains an invalid argument.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "The request is missing something or has an invalid combination of inputs.", "invalid_argument"
            ),
        },
    )
    get_configuration = Operation(
        INFO,
        "get_configuration",
        ServiceJsonBinding(PATH, "GetConfiguration"),
        params=GetConfigurationRequest,
        result=GetConfigurationResult,
        access="admin",
        effect="read",
    )
    get_server_report = Operation(
        INFO,
        "get_server_report",
        ServiceJsonBinding(PATH, "GetServerReport"),
        result=GetServerReportResult,
        access="admin",
        effect="read",
    )
    get_card_reader_configuration = Operation(
        INFO,
        "get_card_reader_configuration",
        ServiceJsonBinding(PATH, "GetCardReaderConfiguration"),
        result=GetCardReaderConfigurationResult,
        access="admin",
        effect="read",
    )
    get_supported_tag_types = Operation(
        INFO,
        "get_supported_tag_types",
        ServiceJsonBinding(PATH, "GetSupportedTagTypes"),
        result=GetSupportedTagTypesResult,
        access="admin",
        effect="read",
    )
    get_default_tag_types = Operation(
        INFO,
        "get_default_tag_types",
        ServiceJsonBinding(PATH, "GetDefaultTagTypes"),
        result=GetDefaultTagTypesResult,
        access="admin",
        effect="read",
    )
    get_last_tag = Operation(
        INFO,
        "get_last_tag",
        ServiceJsonBinding(PATH, "GetLastTag"),
        params=GetLastTagRequest,
        result=GetLastTagResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("No tag with the specified reader ID was found.", "not_found"),
            "ter:NotSupported": ErrorCode("The method is not supported.", "unsupported"),
        },
    )
    get_tag = Operation(
        INFO,
        "get_tag",
        ServiceJsonBinding(PATH, "GetTag"),
        params=GetTagRequest,
        result=GetTagResult,
        access="admin",
        effect="read",
        errors={
            "ter:NotFound": ErrorCode("No tag with the specified reader ID and timestamp was found.", "not_found"),
            "ter:NotSupported": ErrorCode("The method is not supported.", "unsupported"),
        },
    )
    inject_tag = Operation(
        INFO,
        "inject_tag",
        ServiceJsonBinding(PATH, "InjectTag"),
        params=InjectTagRequest,
        access="admin",
        effect="action",
        errors={
            "ter:InvalidArgVal": ErrorCode("The request contains an invalid argument.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "The request is missing something or has an invalid combination of inputs.", "invalid_argument"
            ),
            "ter:NotSupported": ErrorCode("The method is not supported.", "unsupported"),
        },
    )
    register_reader = Operation(
        INFO,
        "register_reader",
        ServiceJsonBinding(PATH, "RegisterReader"),
        params=RegisterReaderRequest,
        result=RegisterReaderResult,
        access="admin",
        effect="action",
        errors={
            "ter:InvalidArgVal": ErrorCode("The request contains an invalid argument.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "The request is missing something or has an invalid combination of inputs.", "invalid_argument"
            ),
            "ter:Failure": ErrorCode("The operation failed.", "internal"),
        },
    )
    unregister_reader = Operation(
        INFO,
        "unregister_reader",
        ServiceJsonBinding(PATH, "UnregisterReader"),
        params=UnregisterReaderRequest,
        access="admin",
        effect="action",
        errors={
            "ter:InvalidArgVal": ErrorCode("The request contains an invalid argument.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "The request is missing something or has an invalid combination of inputs.", "invalid_argument"
            ),
        },
    )
    keep_alive_reader = Operation(
        INFO,
        "keep_alive_reader",
        ServiceJsonBinding(PATH, "KeepAliveReader"),
        params=KeepAliveReaderRequest,
        result=KeepAliveReaderResult,
        access="admin",
        effect="action",
        errors={
            "ter:InvalidArgVal": ErrorCode("The request contains an invalid argument.", "invalid_argument"),
            "ter:InvalidArgs": ErrorCode(
                "The request is missing something or has an invalid combination of inputs.", "invalid_argument"
            ),
        },
    )
    get_current_readers = Operation(
        INFO,
        "get_current_readers",
        ServiceJsonBinding(PATH, "GetCurrentReaders"),
        result=GetCurrentReadersResult,
        access="admin",
        effect="read",
    )
    probe_ip_access_configuration = Operation(
        INFO,
        "probe_ip_access_configuration",
        ServiceJsonBinding(PATH, "ProbeIPAccessConfiguration"),
        params=ProbeIpAccessConfigurationRequest,
        result=ProbeIpAccessConfigurationResult,
        access="admin",
        effect="write",
        write="patch",
    )
    update_ip_access_configuration = Operation(
        INFO,
        "update_ip_access_configuration",
        ServiceJsonBinding(PATH, "UpdateIPAccessConfiguration"),
        params=UpdateIpAccessConfigurationRequest,
        result=UpdateIpAccessConfigurationResult,
        access="admin",
        effect="write",
        write="patch",
    )
    get_card_data = Operation(
        INFO,
        "get_card_data",
        ServiceJsonBinding(PATH, "GetCardData"),
        params=GetCardDataRequest,
        result=GetCardDataResult,
        access="admin",
        effect="read",
    )
    get_last_key_sequence = Operation(
        INFO,
        "get_last_key_sequence",
        ServiceJsonBinding(PATH, "GetLastKeySequence"),
        params=GetLastKeySequenceRequest,
        result=GetLastKeySequenceResult,
        access="admin",
        effect="read",
    )
    inject_key_sequence = Operation(
        INFO,
        "inject_key_sequence",
        ServiceJsonBinding(PATH, "InjectKeySequence"),
        params=InjectKeySequenceRequest,
        access="admin",
        effect="action",
    )
    set_ui_feedback = Operation(
        INFO,
        "set_ui_feedback",
        ServiceJsonBinding(PATH, "SetUiFeedback"),
        params=SetUiFeedbackRequest,
        result=SetUiFeedbackResult,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class IntercomServiceApi(SyncApi):
    """Intercom service (``intercom-service``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Return the capabilities of the service. Access: admin."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    @overload
    def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_configuration(
        self, /, *, configuration: Configuration, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the general intercom configuration (optional fields not set keep current value).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_configuration, request, kwargs, request_options)

    @overload
    def update_configuration(
        self, request: UpdateConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_configuration(
        self, /, *, configuration: Configuration, request_options: RequestOptions | None = None
    ) -> None: ...
    def update_configuration(
        self,
        request: UpdateConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update selected parts of the configuration; omitted fields keep their values.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_configuration, request, kwargs, request_options)

    def get_configuration(
        self, *, include_image_file: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetConfigurationResult:
        """Get the full intercom configuration. Access: admin."""
        return self._run(OPS.get_configuration, None, {"include_image_file": include_image_file}, request_options)

    def get_server_report(self, *, request_options: RequestOptions | None = None) -> GetServerReportResult:
        """Return the safe parts of the server report (sensitive fields discarded). Access: admin."""
        return self._run(OPS.get_server_report, None, {}, request_options)

    def get_card_reader_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> GetCardReaderConfigurationResult:
        """Get only the CardReaderConfiguration. Access: admin."""
        return self._run(OPS.get_card_reader_configuration, None, {}, request_options)

    def get_supported_tag_types(self, *, request_options: RequestOptions | None = None) -> GetSupportedTagTypesResult:
        """List tag types supported by the reader. Access: admin."""
        return self._run(OPS.get_supported_tag_types, None, {}, request_options)

    def get_default_tag_types(self, *, request_options: RequestOptions | None = None) -> GetDefaultTagTypesResult:
        """List card types enabled by default. Access: admin."""
        return self._run(OPS.get_default_tag_types, None, {}, request_options)

    def get_last_tag(
        self, *, reader_id: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetLastTagResult:
        """Get the UID of the last presented tag. Access: admin."""
        return self._run(OPS.get_last_tag, None, {"reader_id": reader_id}, request_options)

    def get_tag(
        self,
        *,
        reader_id: str | MISSING = MISSING,
        timestamp: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetTagResult:
        """Get the last tag or a recent tag matching a timestamp from the Device/Intercom/RFID event.

        Access: admin.
        """
        return self._run(OPS.get_tag, None, {"reader_id": reader_id, "timestamp": timestamp}, request_options)

    @overload
    def inject_tag(self, request: InjectTagRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def inject_tag(
        self,
        /,
        *,
        tag: TagPresentedInfo,
        card_data: list[CardData] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def inject_tag(
        self,
        request: InjectTagRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Simulate presenting an RFID tag (third-party filtering/transforming). Access: admin."""
        self._run(OPS.inject_tag, request, kwargs, request_options)

    def register_reader(
        self,
        *,
        reader_id: str,
        disable_internal_reader: bool | MISSING = MISSING,
        masked_reader_ids: list[str] | MISSING = MISSING,
        unmask_if_lost: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RegisterReaderResult:
        """Register an external/application reader; optionally mask readers so swipes are not sent over the integration protocol.

        Access: admin.
        """
        return self._run(
            OPS.register_reader,
            None,
            {
                "reader_id": reader_id,
                "disable_internal_reader": disable_internal_reader,
                "masked_reader_ids": masked_reader_ids,
                "unmask_if_lost": unmask_if_lost,
            },
            request_options,
        )

    def unregister_reader(self, *, reader_id: str, request_options: RequestOptions | None = None) -> None:
        """Unregister an external or application reader. Access: admin."""
        self._run(OPS.unregister_reader, None, {"reader_id": reader_id}, request_options)

    def keep_alive_reader(
        self, *, reader_id: str, request_options: RequestOptions | None = None
    ) -> KeepAliveReaderResult:
        """Extend a RegisterReader registration; error if not registered or already timed out.

        Access: admin.
        """
        return self._run(OPS.keep_alive_reader, None, {"reader_id": reader_id}, request_options)

    def get_current_readers(self, *, request_options: RequestOptions | None = None) -> GetCurrentReadersResult:
        """List currently available readers with mask flag. Access: admin."""
        return self._run(OPS.get_current_readers, None, {}, request_options)

    @overload
    def probe_ip_access_configuration(
        self, request: ProbeIpAccessConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> ProbeIpAccessConfigurationResult: ...
    @overload
    def probe_ip_access_configuration(
        self, /, *, ip_access_configuration: IPAccessConfiguration, request_options: RequestOptions | None = None
    ) -> ProbeIpAccessConfigurationResult: ...
    def probe_ip_access_configuration(
        self,
        request: ProbeIpAccessConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ProbeIpAccessConfigurationResult:
        """Probe an IP access controller and list the selectable configurations.

        Any current IP access configuration is overridden by the given input. Pass the Id of the desired
        option to update_ip_access_configuration.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.probe_ip_access_configuration, request, kwargs, request_options)

    def update_ip_access_configuration(
        self, *, id: str, request_options: RequestOptions | None = None
    ) -> UpdateIpAccessConfigurationResult:
        """Apply an IPAccessOption returned by ProbeIPAccessConfiguration.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.update_ip_access_configuration, None, {"id": id}, request_options)

    @overload
    def get_card_data(
        self, request: GetCardDataRequest, /, *, request_options: RequestOptions | None = None
    ) -> GetCardDataResult: ...
    @overload
    def get_card_data(
        self,
        /,
        *,
        data_config_names: list[str] | MISSING = MISSING,
        card_data_configs: list[CardDataConfig] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCardDataResult: ...
    def get_card_data(
        self,
        request: GetCardDataRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> GetCardDataResult:
        """Read data stored on tags using pre-loaded config names or ad-hoc CardDataConfigs.

        Access: admin.
        """
        return self._run(OPS.get_card_data, request, kwargs, request_options)

    def get_last_key_sequence(
        self,
        *,
        source: str | MISSING = MISSING,
        timestamp: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetLastKeySequenceResult:
        """Get the latest completed key sequence (completed by #, C, or reaching pin length in PIN mode).

        Access: admin.
        """
        return self._run(OPS.get_last_key_sequence, None, {"source": source, "timestamp": timestamp}, request_options)

    def inject_key_sequence(
        self, *, key_sequence: str, source: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Simulate key presses. Access: admin."""
        self._run(OPS.inject_key_sequence, None, {"key_sequence": key_sequence, "source": source}, request_options)

    @overload
    def set_ui_feedback(
        self, request: SetUiFeedbackRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetUiFeedbackResult: ...
    @overload
    def set_ui_feedback(
        self,
        /,
        *,
        highlevel_feedbacks: list[str] | MISSING = MISSING,
        led_feedbacks: list[UiLedFeedback] | MISSING = MISSING,
        audio_feedback: UiAudioFeedback | MISSING = MISSING,
        source: str | MISSING = MISSING,
        text: str | MISSING = MISSING,
        attributes: list[Attribute] | MISSING = MISSING,
        graphic_feedback: UiGraphicFeedback | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SetUiFeedbackResult: ...
    def set_ui_feedback(
        self,
        request: SetUiFeedbackRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetUiFeedbackResult:
        """Set user interface feedback (high-level, LED, audio, text, graphic). Access: admin."""
        return self._run(OPS.set_ui_feedback, request, kwargs, request_options)


class AsyncIntercomServiceApi(AsyncApi):
    """Intercom service (``intercom-service``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Return the capabilities of the service. Access: admin."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    @overload
    async def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_configuration(
        self, /, *, configuration: Configuration, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the general intercom configuration (optional fields not set keep current value).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_configuration, request, kwargs, request_options)

    @overload
    async def update_configuration(
        self, request: UpdateConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_configuration(
        self, /, *, configuration: Configuration, request_options: RequestOptions | None = None
    ) -> None: ...
    async def update_configuration(
        self,
        request: UpdateConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update selected parts of the configuration; omitted fields keep their values.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_configuration, request, kwargs, request_options)

    async def get_configuration(
        self, *, include_image_file: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetConfigurationResult:
        """Get the full intercom configuration. Access: admin."""
        return await self._run(OPS.get_configuration, None, {"include_image_file": include_image_file}, request_options)

    async def get_server_report(self, *, request_options: RequestOptions | None = None) -> GetServerReportResult:
        """Return the safe parts of the server report (sensitive fields discarded). Access: admin."""
        return await self._run(OPS.get_server_report, None, {}, request_options)

    async def get_card_reader_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> GetCardReaderConfigurationResult:
        """Get only the CardReaderConfiguration. Access: admin."""
        return await self._run(OPS.get_card_reader_configuration, None, {}, request_options)

    async def get_supported_tag_types(
        self, *, request_options: RequestOptions | None = None
    ) -> GetSupportedTagTypesResult:
        """List tag types supported by the reader. Access: admin."""
        return await self._run(OPS.get_supported_tag_types, None, {}, request_options)

    async def get_default_tag_types(self, *, request_options: RequestOptions | None = None) -> GetDefaultTagTypesResult:
        """List card types enabled by default. Access: admin."""
        return await self._run(OPS.get_default_tag_types, None, {}, request_options)

    async def get_last_tag(
        self, *, reader_id: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetLastTagResult:
        """Get the UID of the last presented tag. Access: admin."""
        return await self._run(OPS.get_last_tag, None, {"reader_id": reader_id}, request_options)

    async def get_tag(
        self,
        *,
        reader_id: str | MISSING = MISSING,
        timestamp: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetTagResult:
        """Get the last tag or a recent tag matching a timestamp from the Device/Intercom/RFID event.

        Access: admin.
        """
        return await self._run(OPS.get_tag, None, {"reader_id": reader_id, "timestamp": timestamp}, request_options)

    @overload
    async def inject_tag(
        self, request: InjectTagRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def inject_tag(
        self,
        /,
        *,
        tag: TagPresentedInfo,
        card_data: list[CardData] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def inject_tag(
        self,
        request: InjectTagRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Simulate presenting an RFID tag (third-party filtering/transforming). Access: admin."""
        await self._run(OPS.inject_tag, request, kwargs, request_options)

    async def register_reader(
        self,
        *,
        reader_id: str,
        disable_internal_reader: bool | MISSING = MISSING,
        masked_reader_ids: list[str] | MISSING = MISSING,
        unmask_if_lost: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RegisterReaderResult:
        """Register an external/application reader; optionally mask readers so swipes are not sent over the integration protocol.

        Access: admin.
        """
        return await self._run(
            OPS.register_reader,
            None,
            {
                "reader_id": reader_id,
                "disable_internal_reader": disable_internal_reader,
                "masked_reader_ids": masked_reader_ids,
                "unmask_if_lost": unmask_if_lost,
            },
            request_options,
        )

    async def unregister_reader(self, *, reader_id: str, request_options: RequestOptions | None = None) -> None:
        """Unregister an external or application reader. Access: admin."""
        await self._run(OPS.unregister_reader, None, {"reader_id": reader_id}, request_options)

    async def keep_alive_reader(
        self, *, reader_id: str, request_options: RequestOptions | None = None
    ) -> KeepAliveReaderResult:
        """Extend a RegisterReader registration; error if not registered or already timed out.

        Access: admin.
        """
        return await self._run(OPS.keep_alive_reader, None, {"reader_id": reader_id}, request_options)

    async def get_current_readers(self, *, request_options: RequestOptions | None = None) -> GetCurrentReadersResult:
        """List currently available readers with mask flag. Access: admin."""
        return await self._run(OPS.get_current_readers, None, {}, request_options)

    @overload
    async def probe_ip_access_configuration(
        self, request: ProbeIpAccessConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> ProbeIpAccessConfigurationResult: ...
    @overload
    async def probe_ip_access_configuration(
        self, /, *, ip_access_configuration: IPAccessConfiguration, request_options: RequestOptions | None = None
    ) -> ProbeIpAccessConfigurationResult: ...
    async def probe_ip_access_configuration(
        self,
        request: ProbeIpAccessConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ProbeIpAccessConfigurationResult:
        """Probe an IP access controller and list the selectable configurations.

        Any current IP access configuration is overridden by the given input. Pass the Id of the desired
        option to update_ip_access_configuration.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.probe_ip_access_configuration, request, kwargs, request_options)

    async def update_ip_access_configuration(
        self, *, id: str, request_options: RequestOptions | None = None
    ) -> UpdateIpAccessConfigurationResult:
        """Apply an IPAccessOption returned by ProbeIPAccessConfiguration.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.update_ip_access_configuration, None, {"id": id}, request_options)

    @overload
    async def get_card_data(
        self, request: GetCardDataRequest, /, *, request_options: RequestOptions | None = None
    ) -> GetCardDataResult: ...
    @overload
    async def get_card_data(
        self,
        /,
        *,
        data_config_names: list[str] | MISSING = MISSING,
        card_data_configs: list[CardDataConfig] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCardDataResult: ...
    async def get_card_data(
        self,
        request: GetCardDataRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> GetCardDataResult:
        """Read data stored on tags using pre-loaded config names or ad-hoc CardDataConfigs.

        Access: admin.
        """
        return await self._run(OPS.get_card_data, request, kwargs, request_options)

    async def get_last_key_sequence(
        self,
        *,
        source: str | MISSING = MISSING,
        timestamp: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetLastKeySequenceResult:
        """Get the latest completed key sequence (completed by #, C, or reaching pin length in PIN mode).

        Access: admin.
        """
        return await self._run(
            OPS.get_last_key_sequence, None, {"source": source, "timestamp": timestamp}, request_options
        )

    async def inject_key_sequence(
        self, *, key_sequence: str, source: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Simulate key presses. Access: admin."""
        await self._run(
            OPS.inject_key_sequence, None, {"key_sequence": key_sequence, "source": source}, request_options
        )

    @overload
    async def set_ui_feedback(
        self, request: SetUiFeedbackRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetUiFeedbackResult: ...
    @overload
    async def set_ui_feedback(
        self,
        /,
        *,
        highlevel_feedbacks: list[str] | MISSING = MISSING,
        led_feedbacks: list[UiLedFeedback] | MISSING = MISSING,
        audio_feedback: UiAudioFeedback | MISSING = MISSING,
        source: str | MISSING = MISSING,
        text: str | MISSING = MISSING,
        attributes: list[Attribute] | MISSING = MISSING,
        graphic_feedback: UiGraphicFeedback | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SetUiFeedbackResult: ...
    async def set_ui_feedback(
        self,
        request: SetUiFeedbackRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetUiFeedbackResult:
        """Set user interface feedback (high-level, LED, audio, text, graphic). Access: admin."""
        return await self._run(OPS.set_ui_feedback, request, kwargs, request_options)
