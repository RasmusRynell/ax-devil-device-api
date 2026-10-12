# GENERATED from specs/apis/physical-access-control/door-control-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control and monitor doors, and configure doors, door hardware, priority levels and door schedules.

Docs: https://developer.axis.com/vapix/physical-access-control/door-control-service/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ReferenceToken = str


class ServiceCapabilities(Model):
    """Optional functionality of the service. Static; does not change during device operation."""

    max_limit: int | None = Field(default=None, validation_alias="MaxLimit", serialization_alias="MaxLimit")
    """The maximum number of entries returned by a single GetList or Get request. The device never returns more entities in a single response."""
    get_door_supported: bool | None = Field(
        default=None, validation_alias="GetDoorSupported", serialization_alias="GetDoorSupported"
    )
    """True if GetDoor and GetDoorList are supported."""
    set_door_supported: bool | None = Field(
        default=None, validation_alias="SetDoorSupported", serialization_alias="SetDoorSupported"
    )
    """True if SetDoor is supported."""
    priority_configuration_supported: bool | None = Field(
        default=None,
        validation_alias="PriorityConfigurationSupported",
        serialization_alias="PriorityConfigurationSupported",
    )
    """True if PriorityConfigurations can be modified."""


class DoorCapabilities(Model):
    """Optional functionality of one door. Different doors may differ, and the capabilities may change if hardware settings change."""

    access: bool | None = Field(default=None, validation_alias="Access", serialization_alias="Access")
    """The door supports the AccessDoor command (momentary access)."""
    access_timing_override: bool | None = Field(
        default=None, validation_alias="AccessTimingOverride", serialization_alias="AccessTimingOverride"
    )
    """The door supports overriding the configured timing in AccessDoor."""
    lock: bool | None = Field(default=None, validation_alias="Lock", serialization_alias="Lock")
    """The door supports LockDoor."""
    unlock: bool | None = Field(default=None, validation_alias="Unlock", serialization_alias="Unlock")
    """The door supports UnlockDoor."""
    block: bool | None = Field(default=None, validation_alias="Block", serialization_alias="Block")
    """The door supports BlockDoor."""
    double_lock: bool | None = Field(default=None, validation_alias="DoubleLock", serialization_alias="DoubleLock")
    """The door supports DoubleLockDoor (multiple locks)."""
    lock_down: bool | None = Field(default=None, validation_alias="LockDown", serialization_alias="LockDown")
    """The door supports LockDownDoor and LockDownReleaseDoor."""
    lock_open: bool | None = Field(default=None, validation_alias="LockOpen", serialization_alias="LockOpen")
    """The door supports LockOpenDoor and LockOpenReleaseDoor."""
    door_monitor: bool | None = Field(default=None, validation_alias="DoorMonitor", serialization_alias="DoorMonitor")
    """The door has a door monitor and supports the DoorPhysicalState event."""
    lock_monitor: bool | None = Field(default=None, validation_alias="LockMonitor", serialization_alias="LockMonitor")
    """The door has a lock monitor and supports the LockPhysicalState event."""
    double_lock_monitor: bool | None = Field(
        default=None, validation_alias="DoubleLockMonitor", serialization_alias="DoubleLockMonitor"
    )
    """The door has a double lock monitor and supports the DoubleLockPhysicalState event."""
    alarm: bool | None = Field(default=None, validation_alias="Alarm", serialization_alias="Alarm")
    """The door supports door alarm and the DoorAlarm event."""
    tamper: bool | None = Field(default=None, validation_alias="Tamper", serialization_alias="Tamper")
    """The door has a tamper detector and supports the DoorTamper event."""
    fault: bool | None = Field(default=None, validation_alias="Fault", serialization_alias="Fault")
    """The door supports door fault and the DoorFault event."""
    warning: bool | None = Field(default=None, validation_alias="Warning", serialization_alias="Warning")
    """The door supports door warning and the DoorWarning event."""
    configurable: bool | None = Field(default=None, validation_alias="Configurable", serialization_alias="Configurable")
    """The door settings can be modified."""
    priority_levels: int | None = Field(
        default=None, validation_alias="PriorityLevels", serialization_alias="PriorityLevels"
    )
    """Number of priority levels supported for the door; 0 or 1 means priorities are not supported."""


class DoorInfo(Model):
    """The Door as a physical object, with its capabilities."""

    token: ReferenceToken
    """A service-unique identifier of the Door."""
    name: str = Field(validation_alias="Name", serialization_alias="Name", max_length=64)
    """A user readable name. It shall be up to 64 characters."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """A user readable description. It shall be up to 1024 characters."""
    capabilities: DoorCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities of the Door."""


DoorPhysicalState = Literal["Unknown", "Open", "Closed", "Fault"]
LockPhysicalState = Literal["Unknown", "Locked", "Unlocked", "Fault"]
DoorAlarmState = Literal["Normal", "DoorForcedOpen", "DoorOpenTooLong"]
DoorTamperState = Literal["Unknown", "NotInTamper", "TamperDetected"]
DoorFaultState = Literal["Unknown", "NotInFault", "FaultDetected"]
DoorMode = Literal["Unknown", "Locked", "Unlocked", "Accessed", "Blocked", "LockedDown", "LockedOpen", "DoubleLocked"]


class DoorTamper(Model):
    """Tampering information for a Door."""

    state: DoorTamperState = Field(validation_alias="State", serialization_alias="State")
    """State of the tamper detector."""
    reason: str | None = Field(default=None, validation_alias="Reason", serialization_alias="Reason")
    """Details describing the tampering state change (reason, place, time). May be localized."""


class DoorFault(Model):
    """Fault information for a Door."""

    state: DoorFaultState = Field(validation_alias="State", serialization_alias="State")
    """Overall fault state. FaultDetected if there are any faults; details are in Reason, the DoorState fields or extensions."""
    reason: str | None = Field(default=None, validation_alias="Reason", serialization_alias="Reason")
    """Optional reason for the fault."""
    door_monitor_fault: bool | None = Field(
        default=None, validation_alias="DoorMonitorFault", serialization_alias="DoorMonitorFault"
    )
    """True if there is a fault in the DoorMonitor."""
    lock_fault: bool | None = Field(default=None, validation_alias="LockFault", serialization_alias="LockFault")
    """True if there is a fault in the lock."""
    double_lock_fault: bool | None = Field(
        default=None, validation_alias="DoubleLockFault", serialization_alias="DoubleLockFault"
    )
    """True if there is a fault in the DoubleLockMonitor."""
    lock_monitor_fault: bool | None = Field(
        default=None, validation_alias="LockMonitorFault", serialization_alias="LockMonitorFault"
    )
    """True if there is a fault in the LockMonitor."""


class DoorState(Model):
    """The current aggregate runtime status of a Door. Optional fields are provided when the matching capability is signalled for the door."""

    door_mode: DoorMode = Field(validation_alias="DoorMode", serialization_alias="DoorMode")
    """The logical operating mode of the door."""
    door_physical_state: DoorPhysicalState | None = Field(
        default=None, validation_alias="DoorPhysicalState", serialization_alias="DoorPhysicalState"
    )
    """Physical state of the door (DoorMonitor capability)."""
    lock_physical_state: LockPhysicalState | None = Field(
        default=None, validation_alias="LockPhysicalState", serialization_alias="LockPhysicalState"
    )
    """Physical state of the lock (LockMonitor capability)."""
    double_lock_physical_state: LockPhysicalState | None = Field(
        default=None, validation_alias="DoubleLockPhysicalState", serialization_alias="DoubleLockPhysicalState"
    )
    """Physical state of the double lock (DoubleLockMonitor capability)."""
    alarm: DoorAlarmState | None = Field(default=None, validation_alias="Alarm", serialization_alias="Alarm")
    """Alarm state of the door (Alarm capability)."""
    tamper: DoorTamper | None = Field(default=None, validation_alias="Tamper", serialization_alias="Tamper")
    """Tampering state of the door (Tamper capability)."""
    fault: DoorFault | None = Field(default=None, validation_alias="Fault", serialization_alias="Fault")
    """Fault information for the door (Fault capability)."""


class Door(Model):
    """The device and configuration entity for a Door. Durations are ISO 8601 durations such as PT10S."""

    token: ReferenceToken
    """A service-unique identifier of the Door."""
    name: str = Field(validation_alias="Name", serialization_alias="Name", max_length=64)
    """A user readable name. It shall be up to 64 characters."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """A user readable description. It shall be up to 1024 characters."""
    access_time: str | None = Field(default=None, validation_alias="AccessTime", serialization_alias="AccessTime")
    """The normal open time for a door. Starts when the door goes to the Accessed state."""
    open_too_long_time: str | None = Field(
        default=None, validation_alias="OpenTooLongTime", serialization_alias="OpenTooLongTime"
    )
    """Normal open too long time for a door. Starts when the door is opened."""
    pre_alarm_time: str | None = Field(
        default=None, validation_alias="PreAlarmTime", serialization_alias="PreAlarmTime"
    )
    """Time before the OpenTooLong time expires at which a warning event is sent."""
    extended_access_time: str | None = Field(
        default=None, validation_alias="ExtendedAccessTime", serialization_alias="ExtendedAccessTime"
    )
    """The extended open time for a door."""
    extended_open_too_long_time: str | None = Field(
        default=None, validation_alias="ExtendedOpenTooLongTime", serialization_alias="ExtendedOpenTooLongTime"
    )
    """Extended open too long time for a door."""
    heartbeat_interval: str | None = Field(
        default=None, validation_alias="HeartbeatInterval", serialization_alias="HeartbeatInterval"
    )
    """The time between heartbeat event updates. A time of 0 means no heartbeat events."""
    priority_configuration: ReferenceToken | None = Field(
        default=None, validation_alias="PriorityConfiguration", serialization_alias="PriorityConfiguration"
    )
    """Token of the PriorityConfiguration to use."""
    default_priority: str | None = Field(
        default=None, validation_alias="DefaultPriority", serialization_alias="DefaultPriority"
    )
    """Default priority to use if no priority is given in a door control command. If empty, the DefaultPriority of the PriorityConfiguration is used."""


DoorActionType = Literal[
    "NoAction",
    "Release",
    "LockDownRelease",
    "LockOpenRelease",
    "Lock",
    "Unlock",
    "Access",
    "Block",
    "LockDown",
    "LockOpen",
    "DoubleLock",
]


class DoorPriorityAction(Model):
    """The action of a door at one priority level."""

    priority_level: str = Field(validation_alias="PriorityLevel", serialization_alias="PriorityLevel")
    """The priority level. Only a name; it does not affect the priority order."""
    door_action: DoorActionType = Field(validation_alias="DoorAction", serialization_alias="DoorAction")
    """The action at this level."""
    reason: str | None = Field(default=None, validation_alias="Reason", serialization_alias="Reason")
    """What caused the action, for example API or Schedule. May be empty."""


class PriorityConfiguration(Model):
    """The ordered list of door priority levels and the initial action at each level. The first in the list has the highest priority."""

    token: ReferenceToken
    """A service-unique identifier of the PriorityConfiguration."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the PriorityConfiguration."""
    default_priority: str | None = Field(
        default=None, validation_alias="DefaultPriority", serialization_alias="DefaultPriority"
    )
    """Suggested default priority."""
    door_priority_action: list[DoorPriorityAction] | None = Field(
        default=None, validation_alias="DoorPriorityAction", serialization_alias="DoorPriorityAction"
    )
    """Priority levels and their initial action, highest priority first."""


class Configuration(Model):
    """A configuration setting."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the configuration setting, for example Lock.Type."""
    value: str = Field(validation_alias="Value", serialization_alias="Value")
    """Value of the configuration setting."""


class ConfigurationInfo(Model):
    """A configuration setting and its description."""

    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the configuration setting."""
    value: str = Field(validation_alias="Value", serialization_alias="Value")
    """Value of the configuration setting."""
    enums: list[str] | None = Field(default=None, validation_alias="Enums", serialization_alias="Enums")
    """Suggested or allowed values."""
    type: str | None = Field(default=None, validation_alias="Type", serialization_alias="Type")
    """Type of the configuration setting, for example xs:string, xs:boolean, xs:int."""
    depend_on_name: str | None = Field(
        default=None, validation_alias="DependOnName", serialization_alias="DependOnName"
    )
    """Name of the configuration setting this one depends on."""
    depend_on_value: str | None = Field(
        default=None, validation_alias="DependOnValue", serialization_alias="DependOnValue"
    )
    """Value of the setting this one depends on."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the configuration setting."""


class DoorConfiguration(Model):
    """The device and hardware configuration for a Door. Settings not given are set to their defaults."""

    token: ReferenceToken | None = None
    """Id of the door controller; the same token links the Door, the DoorConfiguration and the DoorScheduleConfiguration. May be omitted or empty when setting."""
    device_uuid: str | None = Field(default=None, validation_alias="DeviceUUID", serialization_alias="DeviceUUID")
    """The device the door controller is on. May be omitted or empty when setting on the intended device."""
    configuration: list[Configuration] | None = Field(
        default=None, validation_alias="Configuration", serialization_alias="Configuration"
    )
    """The hardware configuration settings of the door."""
    door_schedule_configuration: ReferenceToken | None = Field(
        default=None, validation_alias="DoorScheduleConfiguration", serialization_alias="DoorScheduleConfiguration"
    )
    """Token of a DoorScheduleConfiguration. May be empty."""


class ScheduledState(Model):
    """Schedules and the action for a state."""

    schedule_token: list[ReferenceToken] | None = Field(
        default=None, validation_alias="ScheduleToken", serialization_alias="ScheduleToken"
    )
    """Schedules defining when the state is active."""
    enter_action: DoorActionType | None = Field(
        default=None, validation_alias="EnterAction", serialization_alias="EnterAction"
    )
    """The action to run when entering the state."""


class DoorSchedule(Model):
    """Scheduled states for one priority level."""

    scheduled_state: list[ScheduledState] | None = Field(
        default=None, validation_alias="ScheduledState", serialization_alias="ScheduledState"
    )
    """Scheduled states for the door on the priority level."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """The priority level."""


class DoorScheduleConfiguration(Model):
    """Schedule configuration for a Door."""

    token: ReferenceToken
    """A service-unique identifier of the DoorScheduleConfiguration; the same token as the Door."""
    door_schedule: list[DoorSchedule] | None = Field(
        default=None, validation_alias="DoorSchedule", serialization_alias="DoorSchedule"
    )
    """List of DoorSchedule items."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the door."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the door."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capability response message contains the requested Door Control service capabilities using a hierarchical XML capability structure."""


class GetDoorInfoListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, or higher than what the device supports, the number of items shall be determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetDoorInfoListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    door_info: list[DoorInfo] | None = Field(default=None, validation_alias="DoorInfo", serialization_alias="DoorInfo")
    """List of DoorInfo items."""


class GetDoorInfoRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of DoorInfo items to get."""


class GetDoorInfoResult(Model):
    door_info: list[DoorInfo] | None = Field(default=None, validation_alias="DoorInfo", serialization_alias="DoorInfo")
    """List of DoorInfo items."""


class GetDoorStateRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to get the state for."""


class GetDoorStateResult(Model):
    door_state: DoorState = Field(validation_alias="DoorState", serialization_alias="DoorState")
    """The state of the door."""


class AccessDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    use_extended_time: bool | None = Field(
        default=None, validation_alias="UseExtendedTime", serialization_alias="UseExtendedTime"
    )
    """Optional. Indicates that the configured extended time should be used."""
    access_time: str | None = Field(default=None, validation_alias="AccessTime", serialization_alias="AccessTime")
    """Optional. Overrides AccessTime if specified. ISO 8601 duration."""
    open_too_long_time: str | None = Field(
        default=None, validation_alias="OpenTooLongTime", serialization_alias="OpenTooLongTime"
    )
    """Optional. Overrides OpenTooLongTime if specified (DOTL). ISO 8601 duration."""
    pre_alarm_time: str | None = Field(
        default=None, validation_alias="PreAlarmTime", serialization_alias="PreAlarmTime"
    )
    """Optional. Overrides PreAlarmTime if specified. ISO 8601 duration."""


class LockDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the lock command, if empty use default priority."""


class UnlockDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the unlock command, if empty use default priority."""


class BlockDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the block door command, if empty use default priority."""


class LockDownDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the command, if empty use default priority."""


class LockDownReleaseDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the command, if empty use default priority."""


class LockOpenDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the command, if empty use default priority."""


class LockOpenReleaseDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the command, if empty use default priority."""


class DoubleLockDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the double lock command, if empty use default priority."""


class ReleaseDoorRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door to control."""
    priority_level: str | None = Field(
        default=None, validation_alias="PriorityLevel", serialization_alias="PriorityLevel"
    )
    """Priority level for the Release command, if empty use default priority."""


class SetDoorRequest(Model):
    door: list[Door] = Field(validation_alias="Door", serialization_alias="Door", min_length=1)
    """The new version of the Door(s)"""


class SetDoorResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the added or updated Doors."""


class GetDoorListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, or higher than what the device supports, the number of items shall be determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetDoorListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    door: list[Door] | None = Field(default=None, validation_alias="Door", serialization_alias="Door")
    """List of Door items."""


class GetDoorRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of Door items to get."""


class GetDoorResult(Model):
    door: list[Door] | None = Field(default=None, validation_alias="Door", serialization_alias="Door")
    """List of Door items."""


class RemoveDoorRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Token of the Door items to remove."""


class GetDoorPriorityStateRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door to get the state for."""


class GetDoorPriorityStateResult(Model):
    door_priority_action: list[DoorPriorityAction] | None = Field(
        default=None, validation_alias="DoorPriorityAction", serialization_alias="DoorPriorityAction"
    )
    """The Priority state of the door, with highest priorities first."""


class SetPriorityConfigurationRequest(Model):
    priority_configuration: list[PriorityConfiguration] = Field(
        validation_alias="PriorityConfiguration", serialization_alias="PriorityConfiguration", min_length=1
    )
    """List of PriorityConfiguration:s to set."""


class SetPriorityConfigurationResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the added or updated PriorityConfiguration items."""


class GetPriorityConfigurationListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, or higher than what the device supports, the number of items shall be determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetPriorityConfigurationListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    priority_configuration: list[PriorityConfiguration] | None = Field(
        default=None, validation_alias="PriorityConfiguration", serialization_alias="PriorityConfiguration"
    )
    """List of PriorityConfiguration items."""


class GetPriorityConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of PriorityConfiguration items to get."""


class GetPriorityConfigurationResult(Model):
    priority_configuration: list[PriorityConfiguration] | None = Field(
        default=None, validation_alias="PriorityConfiguration", serialization_alias="PriorityConfiguration"
    )
    """List of PriorityConfiguration items."""


class RemovePriorityConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Token of the PriorityConfiguration items to remove."""


class GetDoorConfigurationListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, or higher than what the device supports, the number of items shall be determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetDoorConfigurationListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    door_configuration: list[DoorConfiguration] | None = Field(
        default=None, validation_alias="DoorConfiguration", serialization_alias="DoorConfiguration"
    )
    """List of DoorConfiguration items."""


class GetDoorConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of DoorConfiguration items to get."""


class GetDoorConfigurationResult(Model):
    door_configuration: list[DoorConfiguration] | None = Field(
        default=None, validation_alias="DoorConfiguration", serialization_alias="DoorConfiguration"
    )
    """List of DoorConfiguration items."""


class SetDoorConfigurationRequest(Model):
    door_configuration: list[DoorConfiguration] = Field(
        validation_alias="DoorConfiguration", serialization_alias="DoorConfiguration", min_length=1
    )
    """The new version of the DoorConfiguration."""


class SetDoorConfigurationResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the updated DoorConfiguration items."""


class RemoveDoorConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Token of the DoorConfiguration items to remove."""


class GetDoorConfigurationInfoRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door to get the ConfigurationInfo for."""


class GetDoorConfigurationInfoResult(Model):
    configuration_info: list[ConfigurationInfo] | None = Field(
        default=None, validation_alias="ConfigurationInfo", serialization_alias="ConfigurationInfo"
    )
    """Configuration information for the specified token."""


class SetDoorScheduleConfigurationRequest(Model):
    door_schedule_configuration: list[DoorScheduleConfiguration] = Field(
        validation_alias="DoorScheduleConfiguration", serialization_alias="DoorScheduleConfiguration", min_length=1
    )
    """The new version of the DoorScheduleConfiguration."""


class SetDoorScheduleConfigurationResult(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the added or updated DoorScheduleConfiguration items."""


class GetDoorScheduleConfigurationListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If not specified, or higher than what the device supports, the number of items shall be determined by the device."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this start reference. If not specified, entries shall start from the beginning of the dataset."""


class GetDoorScheduleConfigurationListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in next call to get the following items. If absent, no more items to get."""
    door_schedule_configuration: list[DoorScheduleConfiguration] | None = Field(
        default=None, validation_alias="DoorScheduleConfiguration", serialization_alias="DoorScheduleConfiguration"
    )
    """List of DoorScheduleConfiguration items."""


class GetDoorScheduleConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of DoorConfiguration items to get."""


class GetDoorScheduleConfigurationResult(Model):
    door_schedule_configuration: list[DoorScheduleConfiguration] | None = Field(
        default=None, validation_alias="DoorScheduleConfiguration", serialization_alias="DoorScheduleConfiguration"
    )
    """List of DoorScheduleConfiguration items."""


class RemoveDoorScheduleConfigurationRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the added/updated DoorScheduleConfiguration items."""


class AccessDoorWithoutUnlockRequest(Model):
    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Token of the Door instance to control."""
    use_extended_time: bool | None = Field(
        default=None, validation_alias="UseExtendedTime", serialization_alias="UseExtendedTime"
    )
    """Optional. Indicates that the configured extended time should be used."""
    access_time: str | None = Field(default=None, validation_alias="AccessTime", serialization_alias="AccessTime")
    """Optional. Overrides AccessTime if specified. ISO 8601 duration."""
    open_too_long_time: str | None = Field(
        default=None, validation_alias="OpenTooLongTime", serialization_alias="OpenTooLongTime"
    )
    """Optional. Overrides OpenTooLongTime if specified (DOTL). ISO 8601 duration."""
    pre_alarm_time: str | None = Field(
        default=None, validation_alias="PreAlarmTime", serialization_alias="PreAlarmTime"
    )
    """Optional. Overrides PreAlarmTime if specified. ISO 8601 duration."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/doorcontrol"

INFO = ApiInfo(
    id="door-control-service",
    name="Door control service",
    family=Family.SERVICE_JSON,
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/door-control-service/",
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
        ServiceJsonBinding(PATH, "tdc:GetServiceCapabilities"),
        result=GetServiceCapabilitiesResult,
        access="anonymous",
        effect="read",
    )
    get_door_info_list = Operation(
        INFO,
        "get_door_info_list",
        ServiceJsonBinding(PATH, "tdc:GetDoorInfoList"),
        params=GetDoorInfoListRequest,
        result=GetDoorInfoListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. The client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_door_info = Operation(
        INFO,
        "get_door_info",
        ServiceJsonBinding(PATH, "tdc:GetDoorInfo"),
        params=GetDoorInfoRequest,
        result=GetDoorInfoResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested, see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    get_door_state = Operation(
        INFO,
        "get_door_state",
        ServiceJsonBinding(PATH, "tdc:GetDoorState"),
        params=GetDoorStateRequest,
        result=GetDoorStateResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("The specified token is not found.", "not_found")},
    )
    access_door = Operation(
        INFO,
        "access_door",
        ServiceJsonBinding(PATH, "tdc:AccessDoor"),
        params=AccessDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the Accessed state and unlock the door.", "internal"),
        },
    )
    lock_door = Operation(
        INFO,
        "lock_door",
        ServiceJsonBinding(PATH, "tdc:LockDoor"),
        params=LockDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the Locked state.", "internal"),
        },
    )
    unlock_door = Operation(
        INFO,
        "unlock_door",
        ServiceJsonBinding(PATH, "tdc:UnlockDoor"),
        params=UnlockDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the Unlocked state.", "internal"),
        },
    )
    block_door = Operation(
        INFO,
        "block_door",
        ServiceJsonBinding(PATH, "tdc:BlockDoor"),
        params=BlockDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the Blocked state.", "internal"),
        },
    )
    lock_down_door = Operation(
        INFO,
        "lock_down_door",
        ServiceJsonBinding(PATH, "tdc:LockDownDoor"),
        params=LockDownDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the LockedDown state.", "internal"),
        },
    )
    lock_down_release_door = Operation(
        INFO,
        "lock_down_release_door",
        ServiceJsonBinding(PATH, "tdc:LockDownReleaseDoor"),
        params=LockDownReleaseDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the Locked state.", "internal"),
        },
    )
    lock_open_door = Operation(
        INFO,
        "lock_open_door",
        ServiceJsonBinding(PATH, "tdc:LockOpenDoor"),
        params=LockOpenDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the LockedOpen state.", "internal"),
        },
    )
    lock_open_release_door = Operation(
        INFO,
        "lock_open_release_door",
        ServiceJsonBinding(PATH, "tdc:LockOpenReleaseDoor"),
        params=LockOpenReleaseDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the LockedOpen state.", "internal"),
        },
    )
    double_lock_door = Operation(
        INFO,
        "double_lock_door",
        ServiceJsonBinding(PATH, "tdc:DoubleLockDoor"),
        params=DoubleLockDoorRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the DoubleLocked state.", "internal"),
        },
    )
    release_door = Operation(
        INFO,
        "release_door",
        ServiceJsonBinding(PATH, "axtdc:ReleaseDoor"),
        params=ReleaseDoorRequest,
        access="admin",
        effect="action",
        errors={"ter:NotFound": ErrorCode("The specified token is not found.", "not_found")},
    )
    set_door = Operation(
        INFO,
        "set_door",
        ServiceJsonBinding(PATH, "axtdc:SetDoor"),
        params=SetDoorRequest,
        result=SetDoorResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidArgs": ErrorCode("The request is invalid.", "invalid_argument"),
            "ter:NotSupported": ErrorCode("The operation is not supported.", "unsupported"),
        },
    )
    get_door_list = Operation(
        INFO,
        "get_door_list",
        ServiceJsonBinding(PATH, "axtdc:GetDoorList"),
        params=GetDoorListRequest,
        result=GetDoorListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. The client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_door = Operation(
        INFO,
        "get_door",
        ServiceJsonBinding(PATH, "axtdc:GetDoor"),
        params=GetDoorRequest,
        result=GetDoorResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested, see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    remove_door = Operation(
        INFO,
        "remove_door",
        ServiceJsonBinding(PATH, "axtdc:RemoveDoor"),
        params=RemoveDoorRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={
            "ter:NotSupported": ErrorCode("Not allowed to remove the Door.", "unsupported"),
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
        },
    )
    get_door_priority_state = Operation(
        INFO,
        "get_door_priority_state",
        ServiceJsonBinding(PATH, "axtdc:GetDoorPriorityState"),
        params=GetDoorPriorityStateRequest,
        result=GetDoorPriorityStateResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("The specified token is not found.", "not_found")},
    )
    set_priority_configuration = Operation(
        INFO,
        "set_priority_configuration",
        ServiceJsonBinding(PATH, "axtdc:SetPriorityConfiguration"),
        params=SetPriorityConfigurationRequest,
        result=SetPriorityConfigurationResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:NotSupported": ErrorCode("Not allowed to modify the PriorityConfiguration.", "unsupported"),
            "ter:InvalidArgs": ErrorCode(
                "The request is invalid (documented as: the specified token is not found).", "invalid_argument"
            ),
        },
    )
    get_priority_configuration_list = Operation(
        INFO,
        "get_priority_configuration_list",
        ServiceJsonBinding(PATH, "axtdc:GetPriorityConfigurationList"),
        params=GetPriorityConfigurationListRequest,
        result=GetPriorityConfigurationListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. The client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_priority_configuration = Operation(
        INFO,
        "get_priority_configuration",
        ServiceJsonBinding(PATH, "axtdc:GetPriorityConfiguration"),
        params=GetPriorityConfigurationRequest,
        result=GetPriorityConfigurationResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested, see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    remove_priority_configuration = Operation(
        INFO,
        "remove_priority_configuration",
        ServiceJsonBinding(PATH, "axtdc:RemovePriorityConfiguration"),
        params=RemovePriorityConfigurationRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={
            "ter:NotSupported": ErrorCode("Not allowed to remove the PriorityConfiguration.", "unsupported"),
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
        },
    )
    get_door_configuration_list = Operation(
        INFO,
        "get_door_configuration_list",
        ServiceJsonBinding(PATH, "axtdc:GetDoorConfigurationList"),
        params=GetDoorConfigurationListRequest,
        result=GetDoorConfigurationListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. The client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_door_configuration = Operation(
        INFO,
        "get_door_configuration",
        ServiceJsonBinding(PATH, "axtdc:GetDoorConfiguration"),
        params=GetDoorConfigurationRequest,
        result=GetDoorConfigurationResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested, see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    set_door_configuration = Operation(
        INFO,
        "set_door_configuration",
        ServiceJsonBinding(PATH, "axtdc:SetDoorConfiguration"),
        params=SetDoorConfigurationRequest,
        result=SetDoorConfigurationResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidDoorConfigurationFault": ErrorCode("The DoorConfiguration is invalid.", "invalid_argument")
        },
    )
    remove_door_configuration = Operation(
        INFO,
        "remove_door_configuration",
        ServiceJsonBinding(PATH, "axtdc:RemoveDoorConfiguration"),
        params=RemoveDoorConfigurationRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("The specified token is not found.", "not_found")},
    )
    get_door_configuration_info = Operation(
        INFO,
        "get_door_configuration_info",
        ServiceJsonBinding(PATH, "axtdc:GetDoorConfigurationInfo"),
        params=GetDoorConfigurationInfoRequest,
        result=GetDoorConfigurationInfoResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("The specified token is not found.", "not_found")},
    )
    set_door_schedule_configuration = Operation(
        INFO,
        "set_door_schedule_configuration",
        ServiceJsonBinding(PATH, "axtdc:SetDoorScheduleConfiguration"),
        params=SetDoorScheduleConfigurationRequest,
        result=SetDoorScheduleConfigurationResult,
        access="admin",
        effect="write",
        write="replace",
        errors={
            "ter:InvalidDoorScheduleFault": ErrorCode("The DoorScheduleConfiguration is invalid.", "invalid_argument")
        },
    )
    get_door_schedule_configuration_list = Operation(
        INFO,
        "get_door_schedule_configuration_list",
        ServiceJsonBinding(PATH, "axtdc:GetDoorScheduleConfigurationList"),
        params=GetDoorScheduleConfigurationListRequest,
        result=GetDoorScheduleConfigurationListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out. The client needs to start fetching from the beginning.",
                "invalid_argument",
            )
        },
    )
    get_door_schedule_configuration = Operation(
        INFO,
        "get_door_schedule_configuration",
        ServiceJsonBinding(PATH, "axtdc:GetDoorScheduleConfiguration"),
        params=GetDoorScheduleConfigurationRequest,
        result=GetDoorScheduleConfigurationResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested, see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    remove_door_schedule_configuration = Operation(
        INFO,
        "remove_door_schedule_configuration",
        ServiceJsonBinding(PATH, "axtdc:RemoveDoorScheduleConfiguration"),
        params=RemoveDoorScheduleConfigurationRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("The specified token is not found.", "not_found")},
    )
    access_door_without_unlock = Operation(
        INFO,
        "access_door_without_unlock",
        ServiceJsonBinding(PATH, "axtdc:AccessDoorWithoutUnlock"),
        params=AccessDoorWithoutUnlockRequest,
        access="admin",
        effect="action",
        errors={
            "ter:NotFound": ErrorCode("The specified token is not found.", "not_found"),
            "ter:Failure": ErrorCode("Failed to go to the Accessed state.", "internal"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class DoorControlServiceApi(SyncApi):
    """Door control service (``door-control-service``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """This operation returns the capabilities of the service.

        An ONVIF compliant device which provides the door control service shall implement this method.

        Access: anonymous.
        """
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def get_door_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorInfoListResult:
        """This operation requests a list of all `DoorInfo` items provided by the device.

        An ONVIF compliant device that provides Door Control service shall implement this method. A call to
        this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. The number of items
        returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_door_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_door_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetDoorInfoResult:
        """This operation requests a list of `DoorInfo` items matching the given tokens.

        An ONVIF-compliant device that provides a door control service shall implement this method. The
        device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than `MaxLimit`, a
        `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_door_info, None, {"token": token}, request_options)

    def get_door_state(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetDoorStateResult:
        """This operation requests the state of a `Door` specified by the token.

        A device implementing the Door Control service shall be capable of reporting the status of a door
        using a `DoorState` structure available from the `GetDoorState` command.

        Access: admin.
        """
        return self._run(OPS.get_door_state, None, {"token": token}, request_options)

    @overload
    def access_door(self, request: AccessDoorRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def access_door(
        self,
        /,
        *,
        token: ReferenceToken,
        use_extended_time: bool | MISSING = MISSING,
        access_time: str | MISSING = MISSING,
        open_too_long_time: str | MISSING = MISSING,
        pre_alarm_time: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def access_door(
        self,
        request: AccessDoorRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """This operation allows momentarily accessing a `Door`. Access: admin."""
        self._run(OPS.access_door, request, kwargs, request_options)

    def lock_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows locking a `Door`.

        The `DoorMode` shall change to `Locked`. For more information about the `Locked` state and door mode
        restrictions, see section DoorMode data structure. A device that signals support for `Lock`
        capability for a particular `Door` instance shall implement this method. If the request cannot be
        fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        self._run(OPS.lock_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def unlock_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows unlocking a `Door`.

        The `DoorMode` shall change to `Unlocked`. For more information about the `Unlocked` state and door
        mode restrictions, see section DoorMode data structure. A device that signals support for `Unlock`
        capability for a particular `Door` instance shall implement this method. If the request cannot be
        fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        self._run(OPS.unlock_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def block_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows blocking a `Door` and preventing momentary access (`AccessDoor` command).

        The `DoorMode` shall change to `Blocked`. For more information about the `Blocked` state and door
        mode restrictions, see section DoorMode data structure. A device that signals support for `Block`
        capability for a particular `Door` instance shall implement this method. If the request cannot be
        fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        self._run(OPS.block_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def lock_down_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows locking and preventing other actions until a `LockDownReleaseDoor` command is invoked.

        Access: admin.
        """
        self._run(OPS.lock_down_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def lock_down_release_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows releasing the `LockedDown` state of a `Door`.

        The `DoorMode` shall change back to its previous/next state. It is not defined what the
        previous/next state shall be, but typically - `Locked`. This method shall only succeed if the
        current `DoorMode` is `LockedDown`.

        Access: admin.
        """
        self._run(OPS.lock_down_release_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def lock_open_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows unlocking a `Door` and preventing other actions until `LockOpenReleaseDoor` method is invoked.

        The `DoorMode` shall change to `LockedOpen`. For more information about the `LockedOpen` state and
        door mode restrictions, see section DoorMode data structure. The device shall ignore other door
        control commands until a `LockOpenReleaseDoor` command is performed. A device that signals support
        for `LockOpen` capability for a particular `Door` instance shall implement this method. If the
        request cannot be fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        self._run(OPS.lock_open_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def lock_open_release_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows releasing the `LockedOpen` state of a `Door`.

        The `DoorMode` shall change state from the `LockedOpen` state back to its previous/next state. It is
        not defined what the previous/next state shall be, but typically - `Unlocked`. This method shall
        only succeed if the current `DoorMode` is `LockedOpen`.

        Access: admin.
        """
        self._run(OPS.lock_open_release_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def double_lock_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation is used for securely locking a `Door`.

        The `DoorMode` shall change to `DoubleLocked`. For more information about the `DoubleLocked` state
        and door mode restrictions, see section DoorMode data structure. A device that signals support for
        `DoubleLock` capability for a particular `Door` instance shall implement this method. Otherwise this
        method can be performed as a standard `Lock` operation (see section LockDoor command). If the door
        has an extra lock that shall be locked as well. If the request cannot be fulfilled, a `Failure`
        fault shall be returned.

        Access: admin.
        """
        self._run(OPS.double_lock_door, None, {"token": token, "priority_level": priority_level}, request_options)

    def release_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows releasing a door from the operation at the specified `PriorityLevel`.

        A call to this method shall release door so that `DoorMode` contains no action for the specified
        `PriorityLevel`, the next state shall be determined by the next `PriorityLevel` specified by the
        `PriorityConfiguration` for the `Door`. This method is optional and must be supported if the
        `PriorityConfigurationSupported` capability is true.

        Access: admin.
        """
        self._run(OPS.release_door, None, {"token": token, "priority_level": priority_level}, request_options)

    @overload
    def set_door(
        self, request: SetDoorRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDoorResult: ...
    @overload
    def set_door(self, /, *, door: list[Door], request_options: RequestOptions | None = None) -> SetDoorResult: ...
    def set_door(
        self, request: SetDoorRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetDoorResult:
        """This operation to adds or updates a list of `Door`:s.

        This method must be implemented if the `SetDoorSupported` service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_door, request, kwargs, request_options)

    def get_door_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorListResult:
        """This operation requests a list of all Door items provided by the device.

        This method must be implemented if the `GetDoorSupported` service capability is true. A call to this
        method shall return a `StartReference` when not all data is returned and more data is available. The
        reference shall be valid for retrieving the next set of data. The number of items returned shall not
        be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(OPS.get_door_list, None, {"limit": limit, "start_reference": start_reference}, request_options)

    def get_door(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> GetDoorResult:
        """This operation request a list of `Door` items matching the given tokens.

        This method must be implemented if the `GetDoorSupported` service capability is true. The device
        shall ignore tokens it cannot resolve and may return an empty list if there are no items matching
        specified tokens. If the number of requested items is greater than `MaxLimit`, a `TooManyItems`
        fault shall be returned.

        Access: admin.
        """
        return self._run(OPS.get_door, None, {"token": token}, request_options)

    def remove_door(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """This operation removes `Door` items with specified tokens. Access: admin."""
        self._run(OPS.remove_door, None, {"token": token}, request_options)

    def get_door_priority_state(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetDoorPriorityStateResult:
        """If supported, a call to this method shall return the `Priority` state for a door specified by the token.

        This method must be implemented if the `PriorityConfigurationSupported` service capability is true.

        Access: admin.
        """
        return self._run(OPS.get_door_priority_state, None, {"token": token}, request_options)

    @overload
    def set_priority_configuration(
        self, request: SetPriorityConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetPriorityConfigurationResult: ...
    @overload
    def set_priority_configuration(
        self, /, *, priority_configuration: list[PriorityConfiguration], request_options: RequestOptions | None = None
    ) -> SetPriorityConfigurationResult: ...
    def set_priority_configuration(
        self,
        request: SetPriorityConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetPriorityConfigurationResult:
        """Set a list of `PriorityConfiguration` items.

        If supported, a call to this operation shall set the specified `PriorityConfiguration` items. This
        method must be implemented if the `PriorityConfigurationSupported` service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_priority_configuration, request, kwargs, request_options)

    def get_priority_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetPriorityConfigurationListResult:
        """This operation requests a list of all `PriorityConfiguration` items provided by the device.

        This method must be implemented if the `PriorityConfigurationSupported` service capability is true.
        A call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. The number of items
        returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return self._run(
            OPS.get_priority_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_priority_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetPriorityConfigurationResult:
        """This operation request a list of `PriorityConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than `MaxLimit`, a
        `TooManyItems` fault shall be returned. This method must be implemented if the
        `PriorityConfigurationSupported` service capability is true.

        Access: admin.
        """
        return self._run(OPS.get_priority_configuration, None, {"token": token}, request_options)

    def remove_priority_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """If supported, a call to this method shall remove the `PriorityConfiguration` items specified by the given tokens.

        This method must be implemented if the `PriorityConfigurationSupported` service capability is true.

        Access: admin.
        """
        self._run(OPS.remove_priority_configuration, None, {"token": token}, request_options)

    def get_door_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorConfigurationListResult:
        """This operation requests a list of all of `DoorConfiguration` items provided by the device.

        Access: admin.
        """
        return self._run(
            OPS.get_door_configuration_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_door_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetDoorConfigurationResult:
        """This operation request a list of `DoorConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than the max limit supported,
        a `TooManyItems` fault shall be returned

        Access: admin.
        """
        return self._run(OPS.get_door_configuration, None, {"token": token}, request_options)

    @overload
    def set_door_configuration(
        self, request: SetDoorConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDoorConfigurationResult: ...
    @overload
    def set_door_configuration(
        self, /, *, door_configuration: list[DoorConfiguration], request_options: RequestOptions | None = None
    ) -> SetDoorConfigurationResult: ...
    def set_door_configuration(
        self,
        request: SetDoorConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDoorConfigurationResult:
        """`SetDoorConfiguration`, the token in the `DoorConfiguration` should refer to an existing `DoorController`.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_door_configuration, request, kwargs, request_options)

    def remove_door_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the `DoorConfiguration` items specified by the given token.

        This is normally not needed, since when removing a `DoorController`, the configuration is removed as
        well - although it's possible to create configurations without a corresponding controller.

        Access: admin.
        """
        self._run(OPS.remove_door_configuration, None, {"token": token}, request_options)

    def get_door_configuration_info(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetDoorConfigurationInfoResult:
        """Get the `ConfigurationInfo` for a single `Door` specified by a token. Access: admin."""
        return self._run(OPS.get_door_configuration_info, None, {"token": token}, request_options)

    @overload
    def set_door_schedule_configuration(
        self, request: SetDoorScheduleConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDoorScheduleConfigurationResult: ...
    @overload
    def set_door_schedule_configuration(
        self,
        /,
        *,
        door_schedule_configuration: list[DoorScheduleConfiguration],
        request_options: RequestOptions | None = None,
    ) -> SetDoorScheduleConfigurationResult: ...
    def set_door_schedule_configuration(
        self,
        request: SetDoorScheduleConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDoorScheduleConfigurationResult:
        """Set `DoorScheduleConfiguration`, the token in the `DoorScheduleConfiguration` should refer to an existing `DoorController`.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return self._run(OPS.set_door_schedule_configuration, request, kwargs, request_options)

    def get_door_schedule_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorScheduleConfigurationListResult:
        """This operation requests a list of all of `DoorScheduleConfiguration` items provided by the device.

        Access: admin.
        """
        return self._run(
            OPS.get_door_schedule_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    def get_door_schedule_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetDoorScheduleConfigurationResult:
        """This operation request a list of `DoorScheduleConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than the max limit supported,
        a `TooManyItems` fault shall be returned

        Access: admin.
        """
        return self._run(OPS.get_door_schedule_configuration, None, {"token": token}, request_options)

    def remove_door_schedule_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `DoorScheduleConfiguration` items. Access: admin."""
        self._run(OPS.remove_door_schedule_configuration, None, {"token": token}, request_options)

    @overload
    def access_door_without_unlock(
        self, request: AccessDoorWithoutUnlockRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def access_door_without_unlock(
        self,
        /,
        *,
        token: ReferenceToken,
        use_extended_time: bool | MISSING = MISSING,
        access_time: str | MISSING = MISSING,
        open_too_long_time: str | MISSING = MISSING,
        pre_alarm_time: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def access_door_without_unlock(
        self,
        request: AccessDoorWithoutUnlockRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """This operation allows momentarily accessing a `Door`, without unlocking the door.

        Access: admin.
        """
        self._run(OPS.access_door_without_unlock, request, kwargs, request_options)


class AsyncDoorControlServiceApi(AsyncApi):
    """Door control service (``door-control-service``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """This operation returns the capabilities of the service.

        An ONVIF compliant device which provides the door control service shall implement this method.

        Access: anonymous.
        """
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def get_door_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorInfoListResult:
        """This operation requests a list of all `DoorInfo` items provided by the device.

        An ONVIF compliant device that provides Door Control service shall implement this method. A call to
        this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. The number of items
        returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_door_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_door_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetDoorInfoResult:
        """This operation requests a list of `DoorInfo` items matching the given tokens.

        An ONVIF-compliant device that provides a door control service shall implement this method. The
        device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than `MaxLimit`, a
        `TooManyItems` fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_door_info, None, {"token": token}, request_options)

    async def get_door_state(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetDoorStateResult:
        """This operation requests the state of a `Door` specified by the token.

        A device implementing the Door Control service shall be capable of reporting the status of a door
        using a `DoorState` structure available from the `GetDoorState` command.

        Access: admin.
        """
        return await self._run(OPS.get_door_state, None, {"token": token}, request_options)

    @overload
    async def access_door(
        self, request: AccessDoorRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def access_door(
        self,
        /,
        *,
        token: ReferenceToken,
        use_extended_time: bool | MISSING = MISSING,
        access_time: str | MISSING = MISSING,
        open_too_long_time: str | MISSING = MISSING,
        pre_alarm_time: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def access_door(
        self,
        request: AccessDoorRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """This operation allows momentarily accessing a `Door`. Access: admin."""
        await self._run(OPS.access_door, request, kwargs, request_options)

    async def lock_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows locking a `Door`.

        The `DoorMode` shall change to `Locked`. For more information about the `Locked` state and door mode
        restrictions, see section DoorMode data structure. A device that signals support for `Lock`
        capability for a particular `Door` instance shall implement this method. If the request cannot be
        fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        await self._run(OPS.lock_door, None, {"token": token, "priority_level": priority_level}, request_options)

    async def unlock_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows unlocking a `Door`.

        The `DoorMode` shall change to `Unlocked`. For more information about the `Unlocked` state and door
        mode restrictions, see section DoorMode data structure. A device that signals support for `Unlock`
        capability for a particular `Door` instance shall implement this method. If the request cannot be
        fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        await self._run(OPS.unlock_door, None, {"token": token, "priority_level": priority_level}, request_options)

    async def block_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows blocking a `Door` and preventing momentary access (`AccessDoor` command).

        The `DoorMode` shall change to `Blocked`. For more information about the `Blocked` state and door
        mode restrictions, see section DoorMode data structure. A device that signals support for `Block`
        capability for a particular `Door` instance shall implement this method. If the request cannot be
        fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        await self._run(OPS.block_door, None, {"token": token, "priority_level": priority_level}, request_options)

    async def lock_down_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows locking and preventing other actions until a `LockDownReleaseDoor` command is invoked.

        Access: admin.
        """
        await self._run(OPS.lock_down_door, None, {"token": token, "priority_level": priority_level}, request_options)

    async def lock_down_release_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows releasing the `LockedDown` state of a `Door`.

        The `DoorMode` shall change back to its previous/next state. It is not defined what the
        previous/next state shall be, but typically - `Locked`. This method shall only succeed if the
        current `DoorMode` is `LockedDown`.

        Access: admin.
        """
        await self._run(
            OPS.lock_down_release_door, None, {"token": token, "priority_level": priority_level}, request_options
        )

    async def lock_open_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows unlocking a `Door` and preventing other actions until `LockOpenReleaseDoor` method is invoked.

        The `DoorMode` shall change to `LockedOpen`. For more information about the `LockedOpen` state and
        door mode restrictions, see section DoorMode data structure. The device shall ignore other door
        control commands until a `LockOpenReleaseDoor` command is performed. A device that signals support
        for `LockOpen` capability for a particular `Door` instance shall implement this method. If the
        request cannot be fulfilled, a `Failure` fault shall be returned.

        Access: admin.
        """
        await self._run(OPS.lock_open_door, None, {"token": token, "priority_level": priority_level}, request_options)

    async def lock_open_release_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows releasing the `LockedOpen` state of a `Door`.

        The `DoorMode` shall change state from the `LockedOpen` state back to its previous/next state. It is
        not defined what the previous/next state shall be, but typically - `Unlocked`. This method shall
        only succeed if the current `DoorMode` is `LockedOpen`.

        Access: admin.
        """
        await self._run(
            OPS.lock_open_release_door, None, {"token": token, "priority_level": priority_level}, request_options
        )

    async def double_lock_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation is used for securely locking a `Door`.

        The `DoorMode` shall change to `DoubleLocked`. For more information about the `DoubleLocked` state
        and door mode restrictions, see section DoorMode data structure. A device that signals support for
        `DoubleLock` capability for a particular `Door` instance shall implement this method. Otherwise this
        method can be performed as a standard `Lock` operation (see section LockDoor command). If the door
        has an extra lock that shall be locked as well. If the request cannot be fulfilled, a `Failure`
        fault shall be returned.

        Access: admin.
        """
        await self._run(OPS.double_lock_door, None, {"token": token, "priority_level": priority_level}, request_options)

    async def release_door(
        self,
        *,
        token: ReferenceToken,
        priority_level: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """This operation allows releasing a door from the operation at the specified `PriorityLevel`.

        A call to this method shall release door so that `DoorMode` contains no action for the specified
        `PriorityLevel`, the next state shall be determined by the next `PriorityLevel` specified by the
        `PriorityConfiguration` for the `Door`. This method is optional and must be supported if the
        `PriorityConfigurationSupported` capability is true.

        Access: admin.
        """
        await self._run(OPS.release_door, None, {"token": token, "priority_level": priority_level}, request_options)

    @overload
    async def set_door(
        self, request: SetDoorRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDoorResult: ...
    @overload
    async def set_door(
        self, /, *, door: list[Door], request_options: RequestOptions | None = None
    ) -> SetDoorResult: ...
    async def set_door(
        self, request: SetDoorRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetDoorResult:
        """This operation to adds or updates a list of `Door`:s.

        This method must be implemented if the `SetDoorSupported` service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_door, request, kwargs, request_options)

    async def get_door_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorListResult:
        """This operation requests a list of all Door items provided by the device.

        This method must be implemented if the `GetDoorSupported` service capability is true. A call to this
        method shall return a `StartReference` when not all data is returned and more data is available. The
        reference shall be valid for retrieving the next set of data. The number of items returned shall not
        be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_door_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_door(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetDoorResult:
        """This operation request a list of `Door` items matching the given tokens.

        This method must be implemented if the `GetDoorSupported` service capability is true. The device
        shall ignore tokens it cannot resolve and may return an empty list if there are no items matching
        specified tokens. If the number of requested items is greater than `MaxLimit`, a `TooManyItems`
        fault shall be returned.

        Access: admin.
        """
        return await self._run(OPS.get_door, None, {"token": token}, request_options)

    async def remove_door(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """This operation removes `Door` items with specified tokens. Access: admin."""
        await self._run(OPS.remove_door, None, {"token": token}, request_options)

    async def get_door_priority_state(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetDoorPriorityStateResult:
        """If supported, a call to this method shall return the `Priority` state for a door specified by the token.

        This method must be implemented if the `PriorityConfigurationSupported` service capability is true.

        Access: admin.
        """
        return await self._run(OPS.get_door_priority_state, None, {"token": token}, request_options)

    @overload
    async def set_priority_configuration(
        self, request: SetPriorityConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetPriorityConfigurationResult: ...
    @overload
    async def set_priority_configuration(
        self, /, *, priority_configuration: list[PriorityConfiguration], request_options: RequestOptions | None = None
    ) -> SetPriorityConfigurationResult: ...
    async def set_priority_configuration(
        self,
        request: SetPriorityConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetPriorityConfigurationResult:
        """Set a list of `PriorityConfiguration` items.

        If supported, a call to this operation shall set the specified `PriorityConfiguration` items. This
        method must be implemented if the `PriorityConfigurationSupported` service capability is true.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_priority_configuration, request, kwargs, request_options)

    async def get_priority_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetPriorityConfigurationListResult:
        """This operation requests a list of all `PriorityConfiguration` items provided by the device.

        This method must be implemented if the `PriorityConfigurationSupported` service capability is true.
        A call to this method shall return a `StartReference` when not all data is returned and more data is
        available. The reference shall be valid for retrieving the next set of data. The number of items
        returned shall not be greater than `Limit` parameter.

        Access: admin.
        """
        return await self._run(
            OPS.get_priority_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_priority_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetPriorityConfigurationResult:
        """This operation request a list of `PriorityConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than `MaxLimit`, a
        `TooManyItems` fault shall be returned. This method must be implemented if the
        `PriorityConfigurationSupported` service capability is true.

        Access: admin.
        """
        return await self._run(OPS.get_priority_configuration, None, {"token": token}, request_options)

    async def remove_priority_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """If supported, a call to this method shall remove the `PriorityConfiguration` items specified by the given tokens.

        This method must be implemented if the `PriorityConfigurationSupported` service capability is true.

        Access: admin.
        """
        await self._run(OPS.remove_priority_configuration, None, {"token": token}, request_options)

    async def get_door_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorConfigurationListResult:
        """This operation requests a list of all of `DoorConfiguration` items provided by the device.

        Access: admin.
        """
        return await self._run(
            OPS.get_door_configuration_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_door_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetDoorConfigurationResult:
        """This operation request a list of `DoorConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than the max limit supported,
        a `TooManyItems` fault shall be returned

        Access: admin.
        """
        return await self._run(OPS.get_door_configuration, None, {"token": token}, request_options)

    @overload
    async def set_door_configuration(
        self, request: SetDoorConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDoorConfigurationResult: ...
    @overload
    async def set_door_configuration(
        self, /, *, door_configuration: list[DoorConfiguration], request_options: RequestOptions | None = None
    ) -> SetDoorConfigurationResult: ...
    async def set_door_configuration(
        self,
        request: SetDoorConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDoorConfigurationResult:
        """`SetDoorConfiguration`, the token in the `DoorConfiguration` should refer to an existing `DoorController`.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_door_configuration, request, kwargs, request_options)

    async def remove_door_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the `DoorConfiguration` items specified by the given token.

        This is normally not needed, since when removing a `DoorController`, the configuration is removed as
        well - although it's possible to create configurations without a corresponding controller.

        Access: admin.
        """
        await self._run(OPS.remove_door_configuration, None, {"token": token}, request_options)

    async def get_door_configuration_info(
        self, *, token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> GetDoorConfigurationInfoResult:
        """Get the `ConfigurationInfo` for a single `Door` specified by a token. Access: admin."""
        return await self._run(OPS.get_door_configuration_info, None, {"token": token}, request_options)

    @overload
    async def set_door_schedule_configuration(
        self, request: SetDoorScheduleConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetDoorScheduleConfigurationResult: ...
    @overload
    async def set_door_schedule_configuration(
        self,
        /,
        *,
        door_schedule_configuration: list[DoorScheduleConfiguration],
        request_options: RequestOptions | None = None,
    ) -> SetDoorScheduleConfigurationResult: ...
    async def set_door_schedule_configuration(
        self,
        request: SetDoorScheduleConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetDoorScheduleConfigurationResult:
        """Set `DoorScheduleConfiguration`, the token in the `DoorScheduleConfiguration` should refer to an existing `DoorController`.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        return await self._run(OPS.set_door_schedule_configuration, request, kwargs, request_options)

    async def get_door_schedule_configuration_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetDoorScheduleConfigurationListResult:
        """This operation requests a list of all of `DoorScheduleConfiguration` items provided by the device.

        Access: admin.
        """
        return await self._run(
            OPS.get_door_schedule_configuration_list,
            None,
            {"limit": limit, "start_reference": start_reference},
            request_options,
        )

    async def get_door_schedule_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> GetDoorScheduleConfigurationResult:
        """This operation request a list of `DoorScheduleConfiguration` items matching the given tokens.

        The device shall ignore tokens it cannot resolve and may return an empty list if there are no items
        matching specified tokens. If the number of requested items is greater than the max limit supported,
        a `TooManyItems` fault shall be returned

        Access: admin.
        """
        return await self._run(OPS.get_door_schedule_configuration, None, {"token": token}, request_options)

    async def remove_door_schedule_configuration(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the specified `DoorScheduleConfiguration` items. Access: admin."""
        await self._run(OPS.remove_door_schedule_configuration, None, {"token": token}, request_options)

    @overload
    async def access_door_without_unlock(
        self, request: AccessDoorWithoutUnlockRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def access_door_without_unlock(
        self,
        /,
        *,
        token: ReferenceToken,
        use_extended_time: bool | MISSING = MISSING,
        access_time: str | MISSING = MISSING,
        open_too_long_time: str | MISSING = MISSING,
        pre_alarm_time: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def access_door_without_unlock(
        self,
        request: AccessDoorWithoutUnlockRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """This operation allows momentarily accessing a `Door`, without unlocking the door.

        Access: admin.
        """
        await self._run(OPS.access_door_without_unlock, request, kwargs, request_options)
