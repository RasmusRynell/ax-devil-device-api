# GENERATED from specs/apis/network-video/zwave.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Set up and use the Z-Wave network of the device: network and node management (asynchronous operations polled with getOperation), S2 and SmartStart security, and command class operations on end nodes.

Docs: https://developer.axis.com/vapix/network-video/z-wave-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models

LastUpdated = str
DeviceSpecificKey = Annotated[str, Field(pattern="^[0-9]{5}(-[0-9]{5}){7}$")]
SecurityKey = Literal["S2Key0", "S2Key1", "S2Key2", "S0LegacyKey"]
NodeAliveState = Literal["alive", "down", "sleeping", "unavailable"]
CommandClassName = Literal[
    "antiTheftUnlock",
    "association",
    "basic",
    "battery",
    "binarySwitch",
    "centralScene",
    "configuration",
    "firmwareUpdate",
    "indicator",
    "meter",
    "multilevelSensor",
    "notification",
    "wakeUp",
]
SensorType = Literal[
    "tempSensor",
    "gpSensor",
    "luminSensor",
    "powerSensor",
    "humidSensor",
    "veloSensor",
    "directionSensor",
    "atmSensor",
    "baroSensor",
    "solarSensor",
    "dewSensor",
    "rainSensor",
    "tideSensor",
    "weightSensor",
    "voltageSensor",
    "currentSensor",
    "co2Sensor",
    "airSensor",
    "tankSensor",
    "distSensor",
    "angleSensor",
    "rotationSensor",
    "waterTempSensor",
    "soilTempSensor",
    "seismicIntSensor",
    "seismicMagSensor",
    "uvSensor",
    "elecResistivitySensor",
    "elecCondSensor",
    "loudnessSensor",
    "moistSensor",
    "frequencySensor",
    "timeSensor",
    "targetTempSensor",
    "pm2_5Sensor",
    "ch2oSensor",
    "radonSensor",
    "ch4Sensor",
    "vocSensor",
    "coLvlSensor",
    "soilHumidSensor",
    "soilReactivitySensor",
    "soilSalinitySensor",
    "heartRateSensor",
    "bloodPressureSensor",
    "muscleMassSensor",
    "fatMassSensor",
    "boneMassSensor",
    "tbwSensor",
    "bmrSensor",
    "bmiSensor",
    "xAccSensor",
    "yAccSensor",
    "zAccSensor",
    "smokeDensitySensor",
    "waterFlowSensor",
    "waterPressureSensor",
    "rfSignalSensor",
    "pm10Sensor",
    "respiratoryRateSensor",
    "relativeModSensor",
    "boilerTempSensor",
    "dhwTempSensor",
    "outsideTempSensor",
    "exhaustTempSensor",
    "chlorineLvlSensor",
    "waterAcidSensor",
    "waterOxiRedSensor",
    "lfhfRatioSensor",
    "motionSensor",
    "appliedForceSensor",
    "returnAirTempSensor",
    "supplyAirTempSensor",
    "condenserCoilTempSensor",
    "evaporatorCoilTempSensor",
    "liquidLineTemp",
    "dischargeLineTempSensor",
    "suctionPressureSensor",
    "dischargePressureSensor",
    "defrostTempSensor",
    "ozoneSensor",
    "so2Sensor",
    "no2Sensor",
    "nh3Sensor",
    "pbSensor",
    "pm1Sensor",
    "personEnteringCounter",
    "personExitingCounter",
    "unknown",
]
MeterType = Literal["electric", "gas", "water", "heating", "cooling"]
MeterUnit = Literal[
    "eleckWh",
    "eleckVAh",
    "elecW",
    "elecPulse",
    "elecV",
    "elecA",
    "elecPF",
    "elecKVar",
    "elecKVarh",
    "gasCM",
    "gasCF",
    "gasPulse",
    "waterCM",
    "waterCF",
    "waterGal",
    "waterPulse",
    "heatkWh",
    "coolkWh",
]
MeterRateType = Literal["import", "export", "importExport", "notSupported"]
IndicatorName = Literal[
    "armed",
    "disarmed",
    "ready",
    "faulty",
    "busy",
    "enterID",
    "enterPIN",
    "codeOK",
    "codeNotOK",
    "armedStay",
    "armedAway",
    "alarm",
    "alarmBurglar",
    "alarmFire",
    "alarmCO",
    "bypassChallenge",
    "entryDelay",
    "exitDelay",
    "zone1",
    "zone2",
    "zone3",
    "zone4",
    "zone5",
    "zone6",
    "lcdBacklight",
    "readyForLetter",
    "readyForDigit",
    "readyForCommand",
    "button1",
    "button2",
    "button3",
    "button4",
    "button5",
    "button6",
    "button7",
    "button8",
    "button9",
    "button10",
    "button11",
    "button12",
    "identify",
    "buzzer",
]
IndicatorPropertyName = Literal[
    "level",
    "binary",
    "togglePeriod",
    "toggleCycle",
    "toggleOnTime",
    "timeoutMinutes",
    "timeoutSeconds",
    "timeout100thSeconds",
    "soundLevel",
    "lowPower",
]
CentralSceneKeyAttribute = Literal[
    "singleKeyPress",
    "keyReleased",
    "keyHeldDown",
    "keyPress2Times",
    "keyPress3Times",
    "keyPress4Times",
    "keyPress5Times",
    "unknown",
]


class InterfaceRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""


class InterfaceRefreshRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""


class NodeRequest(Model):
    node_descriptor: int = Field(validation_alias="nodeDescriptor", serialization_alias="nodeDescriptor")
    """The node descriptor."""


class EndpointRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""


class DeviceSpecificKeyRequest(Model):
    device_specific_key: DeviceSpecificKey = Field(
        validation_alias="deviceSpecificKey", serialization_alias="deviceSpecificKey"
    )


class AssociationMember(Model):
    node_id: int = Field(validation_alias="nodeID", serialization_alias="nodeID")
    """The node ID."""
    endpoint_id: int = Field(validation_alias="endpointID", serialization_alias="endpointID")
    """The endpoint ID. 255 denotes a node association, anything else an endpoint association."""


class AssociationRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    group_id: int = Field(validation_alias="groupID", serialization_alias="groupID")
    """The group ID."""
    member_count: int = Field(validation_alias="memberCount", serialization_alias="memberCount", ge=0, le=5)
    """The number of node/endpoint pairs in ``members`` (at most five)."""
    members: list[AssociationMember]
    """The node/endpoint pairs."""


class IndicatorProperty(Model):
    name: IndicatorPropertyName
    value: int
    """The property value. Valid ranges per property are listed in the docs."""


OperationName = Literal[
    "operationNone",
    "operationInitialize",
    "operationAddNode",
    "operationRemoveNode",
    "operationReplaceFailedNode",
    "operationRemoveFailedNode",
    "operationRefreshNetwork",
    "operationResetNetwork",
    "operationRefreshNode",
]
OperationStatusName = Literal[
    "operationStatusNone",
    "operationStatusError",
    "operationStatusNoNet",
    "operationStatusAborted",
    "addNodeStatusProtocolDone",
    "addNodeStatusGetNodeInfo",
    "addNodeStatusProtocolStart",
    "addNodeStatusRequestedKeyReady",
    "addNodeStatusDSKReady",
    "addNodeStatusOnBehalfRequestedKeyReady",
    "addNodeStatusOnBehalfDSKReady",
    "removeNodeStatusLearnReady",
    "removeNodeStatusFound",
    "removeNodeStatusRemoving",
    "replaceNodeStatusReady",
    "replaceNodeStatusProtocolDone",
    "replaceNodeStatusSecureInclusion",
    "replaceNodeStatusGetNodeInfo",
    "networkRefreshStatusTopology",
    "networkRefreshStatusNeighbor",
    "networkRefreshStatusGetNodeInfo",
]


class OperationInfo(Model):
    code: int
    """Operation code (0 none, 1 initialize, 2 add node, 3 remove node, 4 replace failed node, 5 remove failed node, 7 refresh network, 8 reset network, 13 refresh node)."""
    name: OperationName


class OperationStatus(Model):
    status: int
    """Status code. Generic codes: 0 none, -1 error, -4 network not initialized, -5 aborted; other codes depend on the operation."""
    name: OperationStatusName


class NetworkOperation(Model):
    operation: OperationInfo
    """The current network operation."""
    operation_status: OperationStatus = Field(validation_alias="operationStatus", serialization_alias="operationStatus")
    """The progress status of the current operation."""
    prev_operation: OperationInfo = Field(validation_alias="prevOperation", serialization_alias="prevOperation")
    """The previous network operation."""


class NamedCode(Model):
    name: str
    """The name."""
    code: int
    """The code."""


class DeviceCategory(Model):
    """Device category, for example ``onOffSwitch`` (code 2). The docs list the categories in the Device categories table."""

    name: str | None = None
    """The name of the device category."""
    code: int | None = None
    """The device category code."""
    id: int | None = None
    """The device category ID, as named by the parameter table (the response syntax and examples use ``code``)."""


class NodeProperty(Model):
    security_capabilities: list[Literal["S0", "S2"]] | None = Field(
        default=None, validation_alias="securityCapabilities", serialization_alias="securityCapabilities"
    )
    """Security capabilities of the node."""
    included_securely: bool | None = Field(
        default=None, validation_alias="includedSecurely", serialization_alias="includedSecurely"
    )
    """True if the node was included securely."""
    support_identification: bool | None = Field(
        default=None, validation_alias="supportIdentification", serialization_alias="supportIdentification"
    )
    """True if the node can identify itself, for example with a blinking LED."""


class Node(Model):
    node_descriptor: int = Field(validation_alias="nodeDescriptor", serialization_alias="nodeDescriptor")
    """The node descriptor."""
    node_id: int = Field(validation_alias="nodeID", serialization_alias="nodeID")
    """The node ID (below 232). Node IDs can be reused."""
    node_property: NodeProperty | None = Field(
        default=None, validation_alias="nodeProperty", serialization_alias="nodeProperty"
    )
    vendor_id: int | None = Field(default=None, validation_alias="vendorID", serialization_alias="vendorID")
    """The manufacturer specific vendor ID of the device."""
    vendor_product_id: int | None = Field(
        default=None, validation_alias="vendorProductID", serialization_alias="vendorProductID"
    )
    """The manufacturer specific product ID."""
    vendor_product_type: int | None = Field(
        default=None, validation_alias="vendorProductType", serialization_alias="vendorProductType"
    )
    """The manufacturer specific product type."""
    device_category: DeviceCategory | None = Field(
        default=None, validation_alias="deviceCategory", serialization_alias="deviceCategory"
    )
    node_alive_state: NodeAliveState | None = Field(
        default=None, validation_alias="nodeAliveState", serialization_alias="nodeAliveState"
    )
    is_secure: bool | None = Field(default=None, validation_alias="isSecure", serialization_alias="isSecure")
    """True if the node has secure interfaces."""
    secure_inclusion_failed: bool | None = Field(
        default=None, validation_alias="secureInclusionFailed", serialization_alias="secureInclusionFailed"
    )
    """True if the secure inclusion of the node failed."""
    is_f_li_rs_capable: bool | None = Field(
        default=None, validation_alias="isFLiRSCapable", serialization_alias="isFLiRSCapable"
    )
    """True if the node is a Frequency Listening Routing End Node (FLiRS): a battery powered device that wakes up with low latency when called."""
    is_sleep_capable: bool | None = Field(
        default=None, validation_alias="isSleepCapable", serialization_alias="isSleepCapable"
    )
    """True if the node can sleep (non-listening, supports the Wake Up command class)."""
    s2_grant_keys: list[SecurityKey] | None = Field(
        default=None, validation_alias="s2GrantKeys", serialization_alias="s2GrantKeys"
    )
    """The keys used for secure inclusion. Empty if the node was included non-securely."""


class NodeListNet(Model):
    node: list[Node]
    """The nodes on the Z-Wave network."""


class Endpoint(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor that gives access to the endpoint."""
    endpoint_id: int | None = Field(default=None, validation_alias="endpointID", serialization_alias="endpointID")
    """The endpoint ID."""
    generic_device_class: NamedCode | None = Field(
        default=None, validation_alias="genericDeviceClass", serialization_alias="genericDeviceClass"
    )
    """The Generic Device Class, for example ``switchBinary`` (16)."""
    specific_device_class: NamedCode | None = Field(
        default=None, validation_alias="specificDeviceClass", serialization_alias="specificDeviceClass"
    )
    """The Specific Device Class. Codes are scoped by the Generic Device Class."""
    endpoint_name: str | None = Field(default=None, validation_alias="endpointName", serialization_alias="endpointName")
    """The UTF-8 encoded endpoint name."""
    endpoint_location: str | None = Field(
        default=None, validation_alias="endpointLocation", serialization_alias="endpointLocation"
    )
    """The UTF-8 encoded endpoint location."""
    zwave_plus_version: int | None = Field(
        default=None, validation_alias="zwavePlusVersion", serialization_alias="zwavePlusVersion"
    )
    """Z-Wave+ version from the Z-Wave+ Info Report. 0 if the node does not support Z-Wave+."""
    role_type: NamedCode | None = Field(default=None, validation_alias="roleType", serialization_alias="roleType")
    """Z-Wave+ role type, for example ``alwaysOnEndNode`` (5). Only applicable when ``zwavePlusVersion`` is above 0."""
    node_type: NamedCode | None = Field(default=None, validation_alias="nodeType", serialization_alias="nodeType")
    """Z-Wave+ node type: ``zwavePlusNode`` (0) or ``zwavePlusForIPRouter`` (1). Only applicable when ``zwavePlusVersion`` is above 0."""
    installer_icon: int | None = Field(
        default=None, validation_alias="installerIcon", serialization_alias="installerIcon"
    )
    """The Z-Wave+ installer icon type."""
    user_icon: int | None = Field(default=None, validation_alias="userIcon", serialization_alias="userIcon")
    """The Z-Wave+ user icon type."""
    aggregated_endpoint_list: list[int] | None = Field(
        default=None, validation_alias="aggregatedEndpointList", serialization_alias="aggregatedEndpointList"
    )
    """IDs of the aggregated members of a Multi Channel endpoint. Empty if the endpoint is not aggregated."""


class NodeEndpoints(Model):
    node_descriptor: int = Field(validation_alias="nodeDescriptor", serialization_alias="nodeDescriptor")
    """The node descriptor."""
    endpoint: list[Endpoint]
    """The endpoints of the node."""


class AccessSupport(Model):
    secure: bool | None = None
    """True if the interface can be accessed securely."""
    unsecure: bool | None = None
    """True if the interface can be accessed insecurely."""


class Interface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The descriptor used to access the interface."""
    name: CommandClassName
    """The interface name (the Command Class short name)."""
    simulated_version: int | None = Field(
        default=None, validation_alias="simulatedVersion", serialization_alias="simulatedVersion"
    )
    """The Command Class version, upgradable by the device database. Equals ``realVersion`` unless upgraded."""
    real_version: int | None = Field(default=None, validation_alias="realVersion", serialization_alias="realVersion")
    """The Command Class version supported by the device. 0 for a simulated interface."""
    access_support: AccessSupport | None = Field(
        default=None, validation_alias="accessSupport", serialization_alias="accessSupport"
    )


class EndpointInterfaces(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    interface: list[Interface]
    """The interfaces of the endpoint."""


class SummaryInterface(Model):
    descriptor: int | None = None
    """The interface descriptor."""
    name: CommandClassName | None = None
    """The interface name (the Command Class short name)."""


class SummaryEndpoint(Model):
    descriptor: int | None = None
    """The endpoint descriptor."""
    name: str | None = None
    """The UTF-8 encoded endpoint name."""
    generic_device_class_name: str | None = Field(
        default=None, validation_alias="genericDeviceClassName", serialization_alias="genericDeviceClassName"
    )
    """The name of the Generic Device Class."""
    specific_device_class_name: str | None = Field(
        default=None, validation_alias="specificDeviceClassName", serialization_alias="specificDeviceClassName"
    )
    """The name of the Specific Device Class."""
    port_number: int | None = Field(default=None, validation_alias="portNumber", serialization_alias="portNumber")
    """The assigned I/O port number. Not applicable if no number was chosen."""
    interface: list[SummaryInterface] | None = None
    """Some of the endpoint interfaces."""


class SummaryNode(Model):
    descriptor: int | None = None
    """The node descriptor."""
    id: int | None = None
    """The node ID (below 232)."""
    device_category: str | None = Field(
        default=None, validation_alias="deviceCategory", serialization_alias="deviceCategory"
    )
    """The device category name, for example ``onOffSwitch``."""
    alive_state: NodeAliveState | None = Field(
        default=None, validation_alias="aliveState", serialization_alias="aliveState"
    )
    security_warning: Literal["failedToIncludeSecurely", "failedToIncludeWithHighestSecurity"] | None = Field(
        default=None, validation_alias="securityWarning", serialization_alias="securityWarning"
    )
    """``failedToIncludeSecurely``: the node was bootstrapped with S0 in an S2 capable network. ``failedToIncludeWithHighestSecurity``: an S2 node was not granted the highest requested S2 key."""
    endpoint: list[SummaryEndpoint] | None = None
    """The node endpoints."""


class SummaryNet(Model):
    node: list[SummaryNode]
    """The nodes on the Z-Wave network."""


class RequestedKeys(Model):
    requested_keys: list[SecurityKey] | None = Field(
        default=None, validation_alias="requestedKeys", serialization_alias="requestedKeys"
    )
    """The keys requested by the joining device."""


class RequestedKeysNet(Model):
    security: RequestedKeys


class DeviceSpecificKeyInfo(Model):
    pin_required: bool | None = Field(default=None, validation_alias="pinRequired", serialization_alias="pinRequired")
    """True if the user must enter a PIN to include the node with S2."""
    device_specific_key: str | None = Field(
        default=None, validation_alias="deviceSpecificKey", serialization_alias="deviceSpecificKey"
    )
    """The DSK. When ``pinRequired`` is true it is partial and lacks the first group of five digits (-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx); otherwise it is complete."""


class DeviceSpecificKeyNet(Model):
    security: DeviceSpecificKeyInfo


class ProvisioningEntry(Model):
    device_specific_key: str | None = Field(
        default=None, validation_alias="deviceSpecificKey", serialization_alias="deviceSpecificKey"
    )
    """The device specific key."""
    name: str | None = None
    """The nice name. Empty if not set."""
    location: str | None = None
    """The location. Empty if not set."""
    network_status: Literal["included", "notIncluded", "failing", "unknownStatus"] | None = Field(
        default=None, validation_alias="networkStatus", serialization_alias="networkStatus"
    )
    """``included``: on the network. ``notIncluded``: pending inclusion. ``failing``: included but now reported as failing. ``unknownStatus``: unknown."""


class ProvisioningList(Model):
    complete: bool | None = None
    """True if the list is complete."""
    device_info: list[ProvisioningEntry] | None = Field(
        default=None, validation_alias="deviceInfo", serialization_alias="deviceInfo"
    )
    """One entry per device in the provisioning list."""


class BatteryState(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    level: int | None = None
    """Battery level in percent (0-100). 255 means that the battery level is low."""


class BatteryInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    battery: BatteryState


class SensorReading(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    type: SensorType | None = None
    value: float | None = None
    """The sensor value (32-bit float)."""
    precision: int | None = None
    """The number of decimal places of the value."""
    unit: str | None = None
    """The sensor unit, for example ``celsius`` or ``lux``."""


class MultilevelSensorInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    multilevel_sensor: list[SensorReading] = Field(
        validation_alias="multilevelSensor", serialization_alias="multilevelSensor"
    )
    """The sensor states. A single entry when the request gives both a sensor type and a unit."""


class SensorTypeSupport(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    sensor_type_list: list[SensorType] | None = Field(
        default=None, validation_alias="sensorTypeList", serialization_alias="sensorTypeList"
    )
    """The supported sensor types."""


class MultilevelSensorSupportInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    multilevel_sensor: SensorTypeSupport = Field(
        validation_alias="multilevelSensor", serialization_alias="multilevelSensor"
    )


class SensorUnitSupport(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    sensor_type: SensorType | None = Field(
        default=None, validation_alias="sensorType", serialization_alias="sensorType"
    )
    """The sensor type given in the request."""
    sensor_unit_list: list[str] | None = Field(
        default=None, validation_alias="sensorUnitList", serialization_alias="sensorUnitList"
    )
    """The supported sensor units."""


class MultilevelSensorUnitSupportInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    multilevel_sensor: SensorUnitSupport = Field(
        validation_alias="multilevelSensor", serialization_alias="multilevelSensor"
    )


class ConfigurationParameter(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    param_num: int | None = Field(default=None, validation_alias="paramNum", serialization_alias="paramNum")
    """The parameter number."""
    param_value: float | None = Field(default=None, validation_alias="paramValue", serialization_alias="paramValue")
    """The parameter value (signed or unsigned)."""


class ConfigurationInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    configuration: ConfigurationParameter


class BinarySwitchState(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    current_state: bool | None = Field(
        default=None, validation_alias="currentState", serialization_alias="currentState"
    )
    """The current ON (true) or OFF (false) value."""
    target_state: bool | None = Field(default=None, validation_alias="targetState", serialization_alias="targetState")
    """The target value of the latest or ongoing transition."""
    duration: int | None = None
    """Time to reach the target value: 0 already there, 1-127 seconds, 128-253 are 1-126 minutes, 254 unknown, 255 reserved."""
    state_num: int | None = Field(default=None, validation_alias="stateNum", serialization_alias="stateNum")
    """Number of state changes. Wraps to 0 after 0xFFFF."""


class BinarySwitchInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    binary_switch: BinarySwitchState = Field(validation_alias="binarySwitch", serialization_alias="binarySwitch")


class BasicState(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    current_state: int | None = Field(default=None, validation_alias="currentState", serialization_alias="currentState")
    """The current value: 0 OFF, 1-99 percent, 254 unknown, 255 ON."""
    target_state: int | None = Field(default=None, validation_alias="targetState", serialization_alias="targetState")
    """The target value of the latest or ongoing transition: 0 OFF, 1-99 percent, 254 unknown, 255 ON."""
    duration: int | None = None
    """Time to reach the target value: 0 already there, 1-127 seconds, 128-253 are 1-126 minutes, 254 unknown, 255 reserved."""
    state_num: int | None = Field(default=None, validation_alias="stateNum", serialization_alias="stateNum")
    """Number of state changes. Wraps to 0 after 0xFFFF."""


class BasicInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    basic: BasicState


class AssociationGroup(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    group_id: int | None = Field(default=None, validation_alias="groupID", serialization_alias="groupID")
    """The group ID."""
    max_count: int | None = Field(default=None, validation_alias="maxCount", serialization_alias="maxCount")
    """The maximum number of members the group supports."""
    members: list[AssociationMember] | None = None
    """The group members. They may include nodes or endpoints that do not exist on the network."""


class AssociationGroupInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    association: AssociationGroup


class SupportedGroupings(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    group_i_ds: list[int] | None = Field(default=None, validation_alias="groupIDs", serialization_alias="groupIDs")
    """The supported group IDs."""


class SupportedGroupingsInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    association: SupportedGroupings


class WakeUpInfo(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    current_interval: int | None = Field(
        default=None, validation_alias="currentInterval", serialization_alias="currentInterval"
    )
    """The current wake-up interval in seconds."""
    node_id: int | None = Field(default=None, validation_alias="nodeID", serialization_alias="nodeID")
    """The ID of the node notified on wake-up, 255 for broadcast."""
    min_interval: int | None = Field(default=None, validation_alias="minInterval", serialization_alias="minInterval")
    """The minimum wake-up interval in seconds (Wake Up Command Class version 2 and above)."""
    max_interval: int | None = Field(default=None, validation_alias="maxInterval", serialization_alias="maxInterval")
    """The maximum wake-up interval in seconds (Wake Up Command Class version 2 and above)."""
    default_interval: int | None = Field(
        default=None, validation_alias="defaultInterval", serialization_alias="defaultInterval"
    )
    """The default wake-up interval in seconds (Wake Up Command Class version 2 and above)."""
    interval_step: int | None = Field(default=None, validation_alias="intervalStep", serialization_alias="intervalStep")
    """The step between settable wake-up intervals in seconds (Wake Up Command Class version 2 and above)."""


class WakeUpInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    wake_up: WakeUpInfo = Field(validation_alias="wakeUp", serialization_alias="wakeUp")


class MeterReading(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    type: MeterType | None = None
    value: float | None = None
    """The meter value."""
    precision: int | None = None
    """The number of decimal places of the value."""
    unit: MeterUnit | None = None
    rate_type: MeterRateType | None = Field(default=None, validation_alias="rateType", serialization_alias="rateType")
    """The meter rate type (Meter Command Class version 2)."""
    delta: int | None = None
    """Seconds since the previous meter data. 0 if there is no previous value (Meter Command Class version 2)."""
    prev_value: float | None = Field(default=None, validation_alias="prevValue", serialization_alias="prevValue")
    """The previous meter value. Only valid when ``delta`` is above 0; equals the current value when ``delta`` is 0 (Meter Command Class version 2)."""


class MeterReadingInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    meter: list[MeterReading]
    """The readings: one value for the preferred unit, or all available units."""


class MeterCapability(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    type: MeterType | None = None
    units: list[MeterUnit] | None = None
    """The supported units."""
    reset: bool | None = None
    """True if the device can reset all accumulated values."""
    rate_type: MeterRateType | None = Field(default=None, validation_alias="rateType", serialization_alias="rateType")
    """The supported rate type, or ``notSupported``."""


class MeterCapabilitiesInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    meter: list[MeterCapability]
    """The meter capabilities."""


class IndicatorValue(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    value: int | None = None
    """Indicator Command Class version 1 value: 0 off, 1-99, 255 on. Can be ignored when ``properties`` are present."""
    indicator_name: IndicatorName | None = Field(
        default=None, validation_alias="indicatorName", serialization_alias="indicatorName"
    )
    state_num: int | None = Field(default=None, validation_alias="stateNum", serialization_alias="stateNum")
    """Number of state changes. Wraps to 0 after 0xFFFF."""
    properties: list[IndicatorProperty] | None = None
    """The indicator properties (Indicator Command Class version 2 and above)."""


class IndicatorValueInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    indicator: IndicatorValue


class IndicatorSupport(Model):
    indicator_name: IndicatorName | None = Field(
        default=None, validation_alias="indicatorName", serialization_alias="indicatorName"
    )
    property_name_list: list[IndicatorPropertyName] | None = Field(
        default=None, validation_alias="propertyNameList", serialization_alias="propertyNameList"
    )
    """The supported property names (Indicator Command Class version 2 and above)."""


class IndicatorCapabilities(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    indicator_support: list[IndicatorSupport] | None = Field(
        default=None, validation_alias="indicatorSupport", serialization_alias="indicatorSupport"
    )
    """The supported indicators."""


class IndicatorCapabilitiesInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    indicator: IndicatorCapabilities


class FirmwareTarget(Model):
    firmware_target: int | None = Field(
        default=None, validation_alias="firmwareTarget", serialization_alias="firmwareTarget"
    )
    """The firmware target number (from 1)."""
    firmware_id: int | None = Field(default=None, validation_alias="firmwareID", serialization_alias="firmwareID")
    """The firmware ID of the target."""


class FirmwareInfo(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    vendor_id: int | None = Field(default=None, validation_alias="vendorID", serialization_alias="vendorID")
    """The manufacturer specific vendor ID of the device."""
    zwave_firmware_id: int | None = Field(
        default=None, validation_alias="zwaveFirmwareID", serialization_alias="zwaveFirmwareID"
    )
    """The Z-Wave firmware ID."""
    checksum: int | None = None
    """The CRC-CCITT checksum."""
    max_fragment_size: int | None = Field(
        default=None, validation_alias="maxFragmentSize", serialization_alias="maxFragmentSize"
    )
    """The maximum meta data fragment size for a firmware update."""
    fixed_fragment_size: bool | None = Field(
        default=None, validation_alias="fixedFragmentSize", serialization_alias="fixedFragmentSize"
    )
    """True if ``maxFragmentSize`` is a fixed size that must be used in firmware update requests, false for a variable size."""
    upgradable: bool | None = None
    """True if the firmware is upgradable."""
    hardware_version_valid: bool | None = Field(
        default=None, validation_alias="hardwareVersionValid", serialization_alias="hardwareVersionValid"
    )
    """True if the hardware version is valid. Firmware update requests with an invalid hardware version fail."""
    hardware_version: int | None = Field(
        default=None, validation_alias="hardwareVersion", serialization_alias="hardwareVersion"
    )
    """The hardware version."""
    upgrade_functionality: Literal["normal", "limited", "unknown"] | None = Field(
        default=None, validation_alias="upgradeFunctionality", serialization_alias="upgradeFunctionality"
    )
    """Whether other command classes work normally during a firmware upgrade."""
    activation: Literal["supported", "unsupported", "unknown"] | None = None
    """Whether activation after download is supported."""
    firmware_targets: list[FirmwareTarget] | None = Field(
        default=None, validation_alias="firmwareTargets", serialization_alias="firmwareTargets"
    )
    """The firmware targets."""


class FirmwareInfoInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    firmware_update: FirmwareInfo = Field(validation_alias="firmwareUpdate", serialization_alias="firmwareUpdate")


class FirmwareUpdateStatus(Model):
    latest_request_time: str | None = Field(
        default=None, validation_alias="latestRequestTime", serialization_alias="latestRequestTime"
    )
    """Time of the latest firmware update request in ISO 8601 basic format (YYYYMMDDThhmmss)."""
    request_status: (
        Literal[
            "invalidCombo",
            "authenticationNeeded",
            "fragmentSizeError",
            "upgradeError",
            "hardwareVersionError",
            "transferInProgress",
            "lowBattery",
            "validCombo",
            "unknownStatus",
        ]
        | None
    ) = Field(default=None, validation_alias="requestStatus", serialization_alias="requestStatus")
    """The request status. ``validCombo`` means the vendor and firmware ID combination is valid and the upgrade starts."""
    completion_status: (
        Literal[
            "checksumError",
            "downloadError",
            "vendorIDError",
            "firmwareIDError",
            "firmwareTargetError",
            "fileHeaderError",
            "headerFormatError",
            "memoryError",
            "hardwareVersionError",
            "lowBattery",
            "unknownBatteryLevel",
            "okWait",
            "okNoRestart",
            "okRestart",
            "unknownStatus",
        ]
        | None
    ) = Field(default=None, validation_alias="completionStatus", serialization_alias="completionStatus")
    """The completion status. ``okWait``: downloaded and waiting for activation. ``okNoRestart``: stored, no restart. ``okRestart``: stored, the device restarts."""


class FirmwareUpdateInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    firmware_update: FirmwareUpdateStatus = Field(
        validation_alias="firmwareUpdate", serialization_alias="firmwareUpdate"
    )


class FirmwareBackupStatus(Model):
    latest_request_time: str | None = Field(
        default=None, validation_alias="latestRequestTime", serialization_alias="latestRequestTime"
    )
    """Time of the latest firmware backup request in ISO 8601 basic format (YYYYMMDDThhmmss)."""
    request_status: (
        Literal[
            "invalidCombo",
            "authenticationNeeded",
            "fragmentSizeError",
            "downloadError",
            "hardwareVersionError",
            "requestOK",
            "unknownStatus",
        ]
        | None
    ) = Field(default=None, validation_alias="requestStatus", serialization_alias="requestStatus")
    """The backup request status. ``requestOK`` means the node can start the backup."""
    completion_status: (
        Literal[
            "checksumError",
            "downloadError",
            "memoryError",
            "requestStatusError",
            "requestTimeoutError",
            "writeError",
            "exceedSizeLimit",
            "errorOther",
            "statusOK",
            "unknownStatus",
        ]
        | None
    ) = Field(default=None, validation_alias="completionStatus", serialization_alias="completionStatus")
    """The backup completion status. ``statusOK`` means the firmware was downloaded and saved to file."""
    backup_path: str | None = Field(default=None, validation_alias="backupPath", serialization_alias="backupPath")
    """The path to the backup file."""


class FirmwareBackupInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    firmware_update: FirmwareBackupStatus = Field(
        validation_alias="firmwareUpdate", serialization_alias="firmwareUpdate"
    )


class FirmwareActivationStatus(Model):
    vendor_id: int | None = Field(default=None, validation_alias="vendorID", serialization_alias="vendorID")
    """The manufacturer specific vendor ID of the device."""
    firmware_target: int | None = Field(
        default=None, validation_alias="firmwareTarget", serialization_alias="firmwareTarget"
    )
    """The firmware target number: 0 is the Z-Wave firmware, 1-255 a target returned by getFirmwareInfo."""
    firmware_id: int | None = Field(default=None, validation_alias="firmwareID", serialization_alias="firmwareID")
    """The firmware ID."""
    hardware_version: int | None = Field(
        default=None, validation_alias="hardwareVersion", serialization_alias="hardwareVersion"
    )
    """The hardware version."""
    checksum: int | None = None
    """The CRC-CCITT checksum."""
    latest_request_time: str | None = Field(
        default=None, validation_alias="latestRequestTime", serialization_alias="latestRequestTime"
    )
    """Time of the latest request in ISO 8601 basic format (YYYYMMDDThhmmss)."""
    request_status: Literal["invalidCombo", "activationError", "requestOK", "unknownStatus"] | None = Field(
        default=None, validation_alias="requestStatus", serialization_alias="requestStatus"
    )
    """The activation status. ``activationError`` restores the original firmware. ``requestOK`` means the activation completed."""


class FirmwareActivationInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    firmware_update: FirmwareActivationStatus = Field(
        validation_alias="firmwareUpdate", serialization_alias="firmwareUpdate"
    )


class AlarmType(Model):
    type: str | None = None
    """The alarm/notification type, for example ``smoke`` (1) or ``burglar`` (7). Vendor specific types are reported as ``vendorSpecific``."""
    code: int | None = None
    """The alarm/notification type code."""


class NotificationCapabilities(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    has_vendor_specific_type: bool | None = Field(
        default=None, validation_alias="hasVendorSpecificType", serialization_alias="hasVendorSpecificType"
    )
    """True if the vendor specific alarm/notification type is supported."""
    zwave_alarm_type_list: list[AlarmType] | None = Field(
        default=None, validation_alias="zwaveAlarmTypeList", serialization_alias="zwaveAlarmTypeList"
    )
    """The supported alarm/notification types (Alarm/Notification Command Class version 2 and above)."""


class NotificationCapabilitiesInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    notification: NotificationCapabilities


class NotificationEventSupport(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    zwave_alarm_type: str | None = Field(
        default=None, validation_alias="zwaveAlarmType", serialization_alias="zwaveAlarmType"
    )
    """The alarm/notification type given in the request."""
    zwave_event_list: list[int] | None = Field(
        default=None, validation_alias="zwaveEventList", serialization_alias="zwaveEventList"
    )
    """The codes of the events supported by the alarm/notification type."""


class NotificationEventSupportInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    notification: NotificationEventSupport


class NotificationReport(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    vendor_alarm_type: int | None = Field(
        default=None, validation_alias="vendorAlarmType", serialization_alias="vendorAlarmType"
    )
    """The vendor specific alarm type."""
    vendor_alarm_level: int | None = Field(
        default=None, validation_alias="vendorAlarmLevel", serialization_alias="vendorAlarmLevel"
    )
    """The vendor specific alarm level."""
    extended_info_valid: bool | None = Field(
        default=None, validation_alias="extendedInfoValid", serialization_alias="extendedInfoValid"
    )
    """True if the extendedInfo* fields are valid (Alarm/Notification Command Class version 2 and above)."""
    extended_info_alarm_status: Literal["deactivated", "activated", "noPendingNotice"] | None = Field(
        default=None, validation_alias="extendedInfoAlarmStatus", serialization_alias="extendedInfoAlarmStatus"
    )
    """The alarm/notification status. ``deactivated``: unsolicited reports off (push mode), or the report carries valid information (pull mode). ``activated``: unsolicited reports on (push mode). ``noPendingNotice``: the queue is empty."""
    extended_info_alarm_type: str | None = Field(
        default=None, validation_alias="extendedInfoAlarmType", serialization_alias="extendedInfoAlarmType"
    )
    """The Z-Wave alarm/notification type."""
    extended_info_alarm_event: int | None = Field(
        default=None, validation_alias="extendedInfoAlarmEvent", serialization_alias="extendedInfoAlarmEvent"
    )
    """The Z-Wave event."""
    extended_info_parameter_length: int | None = Field(
        default=None, validation_alias="extendedInfoParameterLength", serialization_alias="extendedInfoParameterLength"
    )
    """The event parameter length in bytes. 0 means no parameters."""
    extended_info_parameter_type: (
        Literal["location", "userID", "oemError", "proprietary", "eventID", "unknown"] | None
    ) = Field(
        default=None, validation_alias="extendedInfoParameterType", serialization_alias="extendedInfoParameterType"
    )
    """The event parameter type."""
    extended_info_parameter: int | None = Field(
        default=None, validation_alias="extendedInfoParameter", serialization_alias="extendedInfoParameter"
    )
    """The event parameter, when ``extendedInfoParameterType`` is not ``location``."""
    extended_info_location: str | None = Field(
        default=None, validation_alias="extendedInfoLocation", serialization_alias="extendedInfoLocation"
    )
    """The UTF-8 encoded event location, when ``extendedInfoParameterType`` is ``location``."""


class NotificationState(Model):
    report: NotificationReport | None = None
    """An alarm/notification report."""


class NotificationStateInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    notification: NotificationState


class NotificationEvent(Model):
    type: str | None = None
    """The event name."""
    code: int | None = None
    """The event code."""


class AlarmTypeEvents(Model):
    type: str | None = None
    """The alarm/notification type."""
    code: int | None = None
    """The alarm/notification type code."""
    zwave_event_list: list[NotificationEvent] | None = Field(
        default=None, validation_alias="zwaveEventList", serialization_alias="zwaveEventList"
    )
    """The events supported by the alarm/notification type."""


class AllNotificationEventSupport(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    zwave_alarm_type_list: list[AlarmTypeEvents] | None = Field(
        default=None, validation_alias="zwaveAlarmTypeList", serialization_alias="zwaveAlarmTypeList"
    )
    """The supported alarm/notification types with their events."""


class AllNotificationEventSupportInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    notification: AllNotificationEventSupport


class SceneKeyAttributes(Model):
    scene_number: int | None = Field(default=None, validation_alias="sceneNumber", serialization_alias="sceneNumber")
    """The scene number."""
    support: list[CentralSceneKeyAttribute] | None = None
    """The supported key attributes."""


class CentralSceneCapabilities(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    max_scene_count: int | None = Field(
        default=None, validation_alias="maxSceneCount", serialization_alias="maxSceneCount"
    )
    """The maximum number of scenes."""
    slow_refresh: bool | None = Field(default=None, validation_alias="slowRefresh", serialization_alias="slowRefresh")
    """True if slow refresh is supported."""
    key_attributes: list[SceneKeyAttributes] | None = Field(
        default=None, validation_alias="keyAttributes", serialization_alias="keyAttributes"
    )
    """Supported key attributes per scene (Central Scene Command Class version 2 and above)."""


class CentralSceneCapabilitiesInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    central_scene: CentralSceneCapabilities = Field(validation_alias="centralScene", serialization_alias="centralScene")


class CentralSceneConfiguration(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    slow_refresh: bool | None = Field(default=None, validation_alias="slowRefresh", serialization_alias="slowRefresh")
    """True if slow refresh of the ``keyHeldDown`` notification is enabled."""


class CentralSceneConfigurationInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    central_scene: CentralSceneConfiguration = Field(
        validation_alias="centralScene", serialization_alias="centralScene"
    )


class CentralSceneState(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    sequence_number: int | None = Field(
        default=None, validation_alias="sequenceNumber", serialization_alias="sequenceNumber"
    )
    """Sequence number incremented for every new report."""
    key_attribute: CentralSceneKeyAttribute | None = Field(
        default=None, validation_alias="keyAttribute", serialization_alias="keyAttribute"
    )
    scene_number: int | None = Field(default=None, validation_alias="sceneNumber", serialization_alias="sceneNumber")
    """The scene identifier."""
    slow_refresh: bool | None = Field(default=None, validation_alias="slowRefresh", serialization_alias="slowRefresh")
    """True if slow refresh of the ``keyHeldDown`` notification is enabled."""


class CentralSceneStateInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    central_scene: CentralSceneState = Field(validation_alias="centralScene", serialization_alias="centralScene")


class AntiTheftUnlockState(Model):
    last_updated: LastUpdated | None = Field(
        default=None, validation_alias="lastUpdated", serialization_alias="lastUpdated"
    )
    state_num: int | None = Field(default=None, validation_alias="stateNum", serialization_alias="stateNum")
    """Number of state changes. Wraps to 0 after 0xFFFF."""
    state: bool | None = None
    """True if the node is locked."""
    restricted: bool | None = None
    """True if the node runs in restricted mode."""
    hint: str | None = None
    """Hex string of 0-10 bytes with hints for retrieving the Magic Code that unlocks the node."""
    manufacturer_id: int | None = Field(
        default=None, validation_alias="manufacturerID", serialization_alias="manufacturerID"
    )
    """The manufacturer ID of the company whose product locked the node."""
    entity_id: int | None = Field(default=None, validation_alias="entityID", serialization_alias="entityID")
    """Unique identifier of the entity that locked the node."""


class AntiTheftUnlockInterface(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    anti_theft_unlock: AntiTheftUnlockState = Field(
        validation_alias="antiTheftUnlock", serialization_alias="antiTheftUnlock"
    )


class IoConfiguration(Model):
    io_function: Literal["Set/Reset", "Toggle", "One-shot", "Binary-switch"] | None = Field(
        default=None, validation_alias="ioFunction", serialization_alias="ioFunction"
    )
    """The I/O function of the end node configuration."""
    enabled: bool | None = None
    """True if the configuration is in use."""
    io_port_number: int | None = Field(
        default=None, validation_alias="ioPortNumber", serialization_alias="ioPortNumber"
    )
    """The I/O port number."""
    alarm_type: int | None = Field(default=None, validation_alias="alarmType", serialization_alias="alarmType")
    """The alarm/notification type of the set event. 0 means unused."""
    event: int | None = None
    """The event used by the I/O function. 0 means unused."""
    reset_alarm_type: int | None = Field(
        default=None, validation_alias="resetAlarmType", serialization_alias="resetAlarmType"
    )
    """The alarm/notification type of the reset event (``Set/Reset`` only). 0 means unused."""
    reset_event: int | None = Field(default=None, validation_alias="resetEvent", serialization_alias="resetEvent")
    """The reset event (``Set/Reset`` only). 0 means unused."""
    invert: bool | None = None
    """True if the I/O action is inverted (``Set/Reset``, ``One-shot`` and ``Binary-switch``)."""
    duration: int | None = None
    """Seconds the I/O port is kept high or low (``One-shot`` only)."""


class SetEnabledRequest(Model):
    enabled: bool
    """True to enable Z-Wave, false to disable it."""


class GetEnabledResult(Model):
    enabled: bool
    """True if Z-Wave is enabled."""


class AddNodeRequest(Model):
    device_specific_key: DeviceSpecificKey | None = Field(
        default=None, validation_alias="deviceSpecificKey", serialization_alias="deviceSpecificKey"
    )


class GetOperationResult(Model):
    net: NetworkOperation


class GetNodeListRequest(Model):
    node_i_ds: list[int] | None = Field(default=None, validation_alias="nodeIDs", serialization_alias="nodeIDs")
    """Only list these node IDs. Unknown IDs are ignored, so the result may be empty."""


class GetNodeListResult(Model):
    net: NodeListNet


class GetEndpointListResult(Model):
    node: NodeEndpoints


class GetEndpointInterfaceListResult(Model):
    endpoint: EndpointInterfaces


class GetSummaryListResult(Model):
    net: SummaryNet


class ReplaceFailedNodeRequest(Model):
    node_descriptor: int = Field(validation_alias="nodeDescriptor", serialization_alias="nodeDescriptor")
    """The descriptor of the node to replace."""
    device_specific_key: DeviceSpecificKey | None = Field(
        default=None, validation_alias="deviceSpecificKey", serialization_alias="deviceSpecificKey"
    )


class SetEndpointInfoRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    name: str | None = Field(default=None, max_length=32)
    """The nice name. At most 32 bytes of UTF-8."""
    location: str | None = Field(default=None, max_length=32)
    """The location. At most 32 bytes of UTF-8."""


class GetS2RequestedKeysResult(Model):
    net: RequestedKeysNet


class SetS2GrantKeysRequest(Model):
    grant_keys: list[SecurityKey] = Field(validation_alias="grantKeys", serialization_alias="grantKeys")
    """All or a subset of the keys returned by get_s2_requested_keys."""
    accept: bool | None = None
    """True (default) to accept, false to interrupt S2 bootstrapping."""


class GetS2DeviceSpecificKeyResult(Model):
    net: DeviceSpecificKeyNet


class AcceptS2Request(Model):
    accept: bool
    """True to accept the node, false to reject it."""
    device_specific_key: DeviceSpecificKey | None = Field(
        default=None, validation_alias="deviceSpecificKey", serialization_alias="deviceSpecificKey"
    )
    """The complete DSK. If get_s2_device_specific_key returned a partial DSK, the PIN (the first five digits) completes it. Required when ``accept`` is true."""


class AddToProvisioningListRequest(Model):
    device_specific_key: DeviceSpecificKey = Field(
        validation_alias="deviceSpecificKey", serialization_alias="deviceSpecificKey"
    )
    name: str | None = Field(default=None, max_length=62, pattern="^([^_]*[^_-])?$")
    """The nice name. ``name`` and ``location`` together must not exceed 62 bytes. No underscore, no trailing dash, and ``.`` must be encoded as ``\\.``. Casing may not be kept."""
    location: str | None = Field(default=None, max_length=62, pattern="^([^_]*[^_-])?$")
    """The location. Same rules as ``name``."""


class GetProvisioningListResult(Model):
    net: ProvisioningList


class GetBatteryStateResult(Model):
    interface: BatteryInterface


class GetMultilevelSensorStateRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    type: SensorType | None = None
    """Preferred sensor type; the factory default type is reported when omitted. Not guaranteed to be reported. Only applies when ``refresh`` is true."""
    unit: str | None = None
    """Preferred sensor unit. Ignored unless ``type`` is given; not guaranteed to be reported. Only applies when ``refresh`` is true."""


class GetMultilevelSensorStateResult(Model):
    interface: MultilevelSensorInterface


class GetMultilevelSensorSupportResult(Model):
    interface: MultilevelSensorSupportInterface


class GetMultilevelSensorUnitSupportRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    sensor_type: SensorType = Field(validation_alias="sensorType", serialization_alias="sensorType")
    """The sensor type to list units for (short name)."""


class GetMultilevelSensorUnitSupportResult(Model):
    interface: MultilevelSensorUnitSupportInterface


class GetConfigurationRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    param_num: int = Field(validation_alias="paramNum", serialization_alias="paramNum")
    """The parameter number, usually found in the manufacturer's user manual."""


class GetConfigurationResult(Model):
    interface: ConfigurationInterface


class SetConfigurationRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    param_num: int = Field(validation_alias="paramNum", serialization_alias="paramNum")
    """The parameter number, usually found in the manufacturer's user manual."""
    use_default: bool = Field(validation_alias="useDefault", serialization_alias="useDefault")
    """True to restore the factory default value."""
    param_value: float | None = Field(default=None, validation_alias="paramValue", serialization_alias="paramValue")
    """The parameter value (signed or unsigned). Required unless ``useDefault`` is true."""
    param_size: int | None = Field(default=None, validation_alias="paramSize", serialization_alias="paramSize")
    """The fixed parameter size given in the manufacturer's user manual. Required unless ``useDefault`` is true."""


class GetBinarySwitchStateResult(Model):
    interface: BinarySwitchInterface


class SetBinarySwitchStateRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    value: bool
    """True for ON, false for OFF."""
    duration: int | None = Field(default=None, ge=0, le=255)
    """Time to reach the target value (Binary Switch Command Class version 2 and above): 0 instantly, 1-127 seconds, 128-253 are 1-126 minutes."""


class GetBasicStateResult(Model):
    interface: BasicInterface


class SetBasicStateRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    value: int
    """The value to set. The range is device specific."""


class GetAssociationDataRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    group_id: int = Field(validation_alias="groupID", serialization_alias="groupID")
    """The group ID."""


class GetAssociationDataResult(Model):
    interface: AssociationGroupInterface


class GetSupportedGroupingsResult(Model):
    interface: SupportedGroupingsInterface


class GetWakeUpInfoResult(Model):
    interface: WakeUpInterface


class SetWakeUpInfoRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    wake_up_interval: int = Field(validation_alias="wakeUpInterval", serialization_alias="wakeUpInterval")
    """The wake-up interval in seconds."""
    node_id: int = Field(validation_alias="nodeID", serialization_alias="nodeID")
    """The ID of the node to notify on wake-up, 255 for broadcast."""


class GetMeterReadingRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    unit: (
        Literal[
            "noPreference",
            "eleckWh",
            "eleckVAh",
            "elecW",
            "elecPulse",
            "elecV",
            "elecA",
            "elecPF",
            "elecKVar",
            "elecKVarh",
            "gasCM",
            "gasCF",
            "gasPulse",
            "waterCM",
            "waterCF",
            "waterGal",
            "waterPulse",
            "heatkWh",
            "coolkWh",
        ]
        | None
    ) = None
    """Preferred unit. Ignored if the end node does not support it. Defaults to ``noPreference`` when supported."""
    rate_type: Literal["noPreference", "import", "export"] | None = Field(
        default=None, validation_alias="rateType", serialization_alias="rateType"
    )
    """Preferred rate type. Ignored if the end node does not support it. Defaults to ``noPreference`` when supported."""


class GetMeterReadingResult(Model):
    interface: MeterReadingInterface


class GetMeterCapabilitiesResult(Model):
    interface: MeterCapabilitiesInterface


class GetIndicatorValueRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    indicator_name: IndicatorName | None = Field(
        default=None, validation_alias="indicatorName", serialization_alias="indicatorName"
    )
    """The indicator (Indicator Command Class version 2 and above)."""


class GetIndicatorValueResult(Model):
    interface: IndicatorValueInterface


class SetIndicatorValueRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    value: int | None = Field(default=None, ge=0, le=255)
    """Indicator Command Class version 1 value: 0 off, 1-99, 255 on."""
    indicator_name: IndicatorName | None = Field(
        default=None, validation_alias="indicatorName", serialization_alias="indicatorName"
    )
    """The indicator (Indicator Command Class version 2 and above)."""
    properties: list[IndicatorProperty] | None = None
    """The indicator properties to set (Indicator Command Class version 2 and above)."""


class GetIndicatorCapabilitiesResult(Model):
    interface: IndicatorCapabilitiesInterface


class GetFirmwareInfoResult(Model):
    interface: FirmwareInfoInterface


class RequestFirmwareUpdateRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    vendor_id: int = Field(validation_alias="vendorID", serialization_alias="vendorID")
    """The manufacturer specific vendor ID of the device."""
    firmware_target: int = Field(validation_alias="firmwareTarget", serialization_alias="firmwareTarget", ge=0, le=255)
    """The firmware target: 0 for the Z-Wave firmware, 1-255 for a target returned by get_firmware_info."""
    firmware_id: int = Field(validation_alias="firmwareID", serialization_alias="firmwareID")
    """The firmware ID of the new firmware."""
    file_name: str = Field(validation_alias="fileName", serialization_alias="fileName")
    """The firmware file path."""
    hardware_version: int = Field(validation_alias="hardwareVersion", serialization_alias="hardwareVersion")
    """The hardware version."""


class RequestFirmwareUpdateResult(Model):
    interface: FirmwareUpdateInterface


class GetFirmwareUpdateStatusResult(Model):
    interface: FirmwareUpdateInterface


class RequestFirmwareBackupRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    vendor_id: int = Field(validation_alias="vendorID", serialization_alias="vendorID")
    """The manufacturer specific vendor ID of the device."""
    firmware_target: int = Field(validation_alias="firmwareTarget", serialization_alias="firmwareTarget", ge=0, le=255)
    """The firmware target: 0 for the Z-Wave firmware, 1-255 for a target returned by get_firmware_info."""
    firmware_id: int = Field(validation_alias="firmwareID", serialization_alias="firmwareID")
    """The firmware ID."""
    hardware_version: int = Field(validation_alias="hardwareVersion", serialization_alias="hardwareVersion")
    """The hardware version."""


class RequestFirmwareBackupResult(Model):
    interface: FirmwareBackupInterface


class GetFirmwareBackupStatusResult(Model):
    interface: FirmwareBackupInterface


class RequestFirmwareActivationResult(Model):
    interface: FirmwareActivationInterface


class GetFirmwareActivationStatusResult(Model):
    interface: FirmwareActivationInterface


class GetNotificationCapabilitiesResult(Model):
    interface: NotificationCapabilitiesInterface


class GetNotificationEventSupportRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    zwave_alarm_type: str = Field(validation_alias="zwaveAlarmType", serialization_alias="zwaveAlarmType")
    """The alarm/notification type, for example ``smoke`` or ``burglar``."""


class GetNotificationEventSupportResult(Model):
    interface: NotificationEventSupportInterface


class GetNotificationStateRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    refresh: bool | None = None
    """True to fetch the value from the end node, false (default) to read the cache."""
    vendor_alarm_type: int | None = Field(
        default=None, validation_alias="vendorAlarmType", serialization_alias="vendorAlarmType"
    )
    """The vendor specific alarm type. Defaults to 0 when not used; -1 means no favorites when reading the cache."""
    zwave_alarm_type: str | None = Field(
        default=None, validation_alias="zwaveAlarmType", serialization_alias="zwaveAlarmType"
    )
    """The alarm/notification type. Defaults to ``latest``, which returns only the latest report (Alarm/Notification Command Class version 2 and above)."""
    zwave_event: int | None = Field(default=None, validation_alias="zwaveEvent", serialization_alias="zwaveEvent")
    """The event (push mode only). Defaults to 0, the latest event (Alarm/Notification Command Class version 3 and above)."""


class GetNotificationStateResult(Model):
    interface: NotificationStateInterface


class SetNotificationStateRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    zwave_alarm_type: str = Field(validation_alias="zwaveAlarmType", serialization_alias="zwaveAlarmType")
    """The alarm/notification type, for example ``smoke`` or ``burglar``."""
    status: Literal[0, 255]
    """Push mode: 0 disables and 255 enables unsolicited reports. Pull mode: 0 clears a persistent notification."""


class GetAllNotificationEventSupportResult(Model):
    interface: AllNotificationEventSupportInterface


class GetCentralSceneCapabilitiesResult(Model):
    interface: CentralSceneCapabilitiesInterface


class GetCentralSceneConfigurationResult(Model):
    interface: CentralSceneConfigurationInterface


class SetCentralSceneConfigurationRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    slow_refresh: bool = Field(validation_alias="slowRefresh", serialization_alias="slowRefresh")
    """True to use slow refresh."""


class GetCentralSceneStateResult(Model):
    interface: CentralSceneStateInterface


class GetAntiTheftUnlockStateResult(Model):
    interface: AntiTheftUnlockInterface


class SetAntiTheftUnlockStateRequest(Model):
    interface_descriptor: int = Field(validation_alias="interfaceDescriptor", serialization_alias="interfaceDescriptor")
    """The interface descriptor."""
    code: str = Field(pattern="^([0-9A-Fa-f]{2}){1,10}$")
    """The Magic Code as a hex string of 1-10 bytes, two characters per byte (0x01 0x02 0xFF is ``0102FF``)."""


class SetTemperatureThresholdRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    active: bool
    """True to activate the temperature threshold."""
    warning_rule: Literal["above", "below"] | None = Field(
        default=None, validation_alias="warningRule", serialization_alias="warningRule"
    )
    """Trigger the event when the temperature goes above or below the threshold."""
    threshold: int | None = None
    """The threshold value. Hysteresis is not included."""
    unit: str | None = None
    """The temperature unit (Celsius or Fahrenheit)."""


class GetTemperatureThresholdRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    unit: str | None = None
    """The temperature unit, Celsius (default) or Fahrenheit."""


class GetTemperatureThresholdResult(Model):
    active: bool | None = None
    """True if the temperature threshold is active."""
    warning_rule: Literal["above", "below", "unknown"] | None = Field(
        default=None, validation_alias="warningRule", serialization_alias="warningRule"
    )
    """When the event triggers. ``unknown`` if no value has been set."""
    threshold: int | None = None
    """The threshold value. 0 if no value has been set."""


class SetIoFunctionBinarySwitchRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    io_port_number: int = Field(validation_alias="ioPortNumber", serialization_alias="ioPortNumber")
    """The I/O port number."""
    invert: bool
    """True turns the switch on when the I/O port is low, false when it is high."""


class SetIoFunctionOneShotRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    io_port_number: int = Field(validation_alias="ioPortNumber", serialization_alias="ioPortNumber")
    """The I/O port number."""
    alarm_type: int = Field(validation_alias="alarmType", serialization_alias="alarmType")
    """The alarm/notification type."""
    event: int
    """The event that sets the I/O port for the duration."""
    invert: bool
    """True drives the I/O port low on the event, false drives it high."""
    duration: int
    """Seconds the I/O port is kept high or low before returning to its default value."""


class SetIoFunctionSetResetRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    io_port_number: int = Field(validation_alias="ioPortNumber", serialization_alias="ioPortNumber")
    """The I/O port number."""
    set_alarm_type: int = Field(validation_alias="setAlarmType", serialization_alias="setAlarmType")
    """The alarm/notification type of the set event."""
    set_event: int = Field(validation_alias="setEvent", serialization_alias="setEvent")
    """The event that sets the I/O port high."""
    reset_alarm_type: int = Field(validation_alias="resetAlarmType", serialization_alias="resetAlarmType")
    """The alarm/notification type of the reset event."""
    reset_event: int = Field(validation_alias="resetEvent", serialization_alias="resetEvent")
    """The event that resets the I/O port low."""
    invert: bool
    """True inverts the action: the set event drives the port low and the reset event drives it high."""


class SetIoFunctionToggleRequest(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor."""
    io_port_number: int = Field(validation_alias="ioPortNumber", serialization_alias="ioPortNumber")
    """The I/O port number."""
    alarm_type: int = Field(validation_alias="alarmType", serialization_alias="alarmType")
    """The alarm/notification type."""
    event: int
    """The event that toggles the I/O port."""


class GetIoConfigurationResult(Model):
    endpoint_descriptor: int = Field(validation_alias="endpointDescriptor", serialization_alias="endpointDescriptor")
    """The endpoint descriptor given in the request."""
    io_configuration: IoConfiguration = Field(validation_alias="ioConfiguration", serialization_alias="ioConfiguration")


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/zwave.cgi"

INFO = ApiInfo(
    id="zwave",
    name="Z-Wave API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("zwave"),),
    docs=("https://developer.axis.com/vapix/network-video/z-wave-api/",),
    errors={
        1100: ErrorCode("Internal error (also out of memory).", "internal"),
        1200: ErrorCode("Z-Wave is disabled.", "unavailable"),
        1201: ErrorCode("Open file error.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
        2106: ErrorCode("Authentication failed.", "access_denied"),
        2107: ErrorCode("Transport-level error (HTTP 4XX or 5XX)."),
        2200: ErrorCode("Bad interface descriptor.", "invalid_argument"),
        2201: ErrorCode("Command Class version not supported.", "unsupported"),
        2202: ErrorCode("Bad endpoint descriptor.", "invalid_argument"),
        2203: ErrorCode("Timeout.", "unavailable"),
        2204: ErrorCode("Operation already in progress.", "unavailable"),
        2205: ErrorCode("Maximum nodes reached."),
    },
)


class OPS:
    set_enabled = Operation(
        INFO,
        "set_enabled",
        JsonRpcBinding("setEnabled", PATH),
        params=SetEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_enabled = Operation(
        INFO, "get_enabled", JsonRpcBinding("getEnabled", PATH), result=GetEnabledResult, access="admin", effect="read"
    )
    add_node = Operation(
        INFO, "add_node", JsonRpcBinding("addNode", PATH), params=AddNodeRequest, access="admin", effect="action"
    )
    remove_node = Operation(INFO, "remove_node", JsonRpcBinding("removeNode", PATH), access="admin", effect="action")
    get_operation = Operation(
        INFO,
        "get_operation",
        JsonRpcBinding("getOperation", PATH),
        result=GetOperationResult,
        access="admin",
        effect="read",
    )
    abort_operation = Operation(
        INFO, "abort_operation", JsonRpcBinding("abortOperation", PATH), access="admin", effect="action"
    )
    reset_network = Operation(
        INFO, "reset_network", JsonRpcBinding("resetNetwork", PATH), access="admin", effect="action"
    )
    refresh_network = Operation(
        INFO, "refresh_network", JsonRpcBinding("refreshNetwork", PATH), access="admin", effect="action"
    )
    get_node_list = Operation(
        INFO,
        "get_node_list",
        JsonRpcBinding("getNodeList", PATH),
        params=GetNodeListRequest,
        result=GetNodeListResult,
        access="admin",
        effect="read",
    )
    get_endpoint_list = Operation(
        INFO,
        "get_endpoint_list",
        JsonRpcBinding("getEndpointList", PATH),
        params=NodeRequest,
        result=GetEndpointListResult,
        access="admin",
        effect="read",
    )
    get_endpoint_interface_list = Operation(
        INFO,
        "get_endpoint_interface_list",
        JsonRpcBinding("getEndpointInterfaceList", PATH),
        params=EndpointRequest,
        result=GetEndpointInterfaceListResult,
        access="admin",
        effect="read",
    )
    get_summary_list = Operation(
        INFO,
        "get_summary_list",
        JsonRpcBinding("getSummaryList", PATH),
        result=GetSummaryListResult,
        access="admin",
        effect="read",
    )
    replace_failed_node = Operation(
        INFO,
        "replace_failed_node",
        JsonRpcBinding("replaceFailedNode", PATH),
        params=ReplaceFailedNodeRequest,
        access="admin",
        effect="action",
    )
    remove_failed_node = Operation(
        INFO,
        "remove_failed_node",
        JsonRpcBinding("removeFailedNode", PATH),
        params=NodeRequest,
        access="admin",
        effect="action",
    )
    set_endpoint_info = Operation(
        INFO,
        "set_endpoint_info",
        JsonRpcBinding("setEndpointInfo", PATH),
        params=SetEndpointInfoRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_s2_requested_keys = Operation(
        INFO,
        "get_s2_requested_keys",
        JsonRpcBinding("getS2RequestedKeys", PATH),
        result=GetS2RequestedKeysResult,
        access="admin",
        effect="read",
    )
    set_s2_grant_keys = Operation(
        INFO,
        "set_s2_grant_keys",
        JsonRpcBinding("setS2GrantKeys", PATH),
        params=SetS2GrantKeysRequest,
        access="admin",
        effect="action",
    )
    get_s2_device_specific_key = Operation(
        INFO,
        "get_s2_device_specific_key",
        JsonRpcBinding("getS2DeviceSpecificKey", PATH),
        result=GetS2DeviceSpecificKeyResult,
        access="admin",
        effect="read",
    )
    accept_s2 = Operation(
        INFO, "accept_s2", JsonRpcBinding("acceptS2", PATH), params=AcceptS2Request, access="admin", effect="action"
    )
    refresh_node = Operation(
        INFO, "refresh_node", JsonRpcBinding("refreshNode", PATH), params=NodeRequest, access="admin", effect="action"
    )
    add_to_provisioning_list = Operation(
        INFO,
        "add_to_provisioning_list",
        JsonRpcBinding("addToProvisioningList", PATH),
        params=AddToProvisioningListRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_from_provisioning_list = Operation(
        INFO,
        "remove_from_provisioning_list",
        JsonRpcBinding("removeFromProvisioningList", PATH),
        params=DeviceSpecificKeyRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_provisioning_list = Operation(
        INFO,
        "get_provisioning_list",
        JsonRpcBinding("getProvisioningList", PATH),
        result=GetProvisioningListResult,
        access="admin",
        effect="read",
    )
    get_battery_state = Operation(
        INFO,
        "get_battery_state",
        JsonRpcBinding("getBatteryState", PATH),
        params=InterfaceRefreshRequest,
        result=GetBatteryStateResult,
        access="admin",
        effect="read",
    )
    get_multilevel_sensor_state = Operation(
        INFO,
        "get_multilevel_sensor_state",
        JsonRpcBinding("getMultilevelSensorState", PATH),
        params=GetMultilevelSensorStateRequest,
        result=GetMultilevelSensorStateResult,
        access="admin",
        effect="read",
    )
    get_multilevel_sensor_support = Operation(
        INFO,
        "get_multilevel_sensor_support",
        JsonRpcBinding("getMultilevelSensorSupport", PATH),
        params=InterfaceRefreshRequest,
        result=GetMultilevelSensorSupportResult,
        access="admin",
        effect="read",
    )
    get_multilevel_sensor_unit_support = Operation(
        INFO,
        "get_multilevel_sensor_unit_support",
        JsonRpcBinding("getMultilevelSensorUnitSupport", PATH),
        params=GetMultilevelSensorUnitSupportRequest,
        result=GetMultilevelSensorUnitSupportResult,
        access="admin",
        effect="read",
    )
    get_configuration = Operation(
        INFO,
        "get_configuration",
        JsonRpcBinding("getConfiguration", PATH),
        params=GetConfigurationRequest,
        result=GetConfigurationResult,
        access="admin",
        effect="read",
    )
    set_configuration = Operation(
        INFO,
        "set_configuration",
        JsonRpcBinding("setConfiguration", PATH),
        params=SetConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_binary_switch_state = Operation(
        INFO,
        "get_binary_switch_state",
        JsonRpcBinding("getBinarySwitchState", PATH),
        params=InterfaceRefreshRequest,
        result=GetBinarySwitchStateResult,
        access="admin",
        effect="read",
    )
    set_binary_switch_state = Operation(
        INFO,
        "set_binary_switch_state",
        JsonRpcBinding("setBinarySwitchState", PATH),
        params=SetBinarySwitchStateRequest,
        access="admin",
        effect="action",
    )
    get_basic_state = Operation(
        INFO,
        "get_basic_state",
        JsonRpcBinding("getBasicState", PATH),
        params=InterfaceRefreshRequest,
        result=GetBasicStateResult,
        access="admin",
        effect="read",
    )
    set_basic_state = Operation(
        INFO,
        "set_basic_state",
        JsonRpcBinding("setBasicState", PATH),
        params=SetBasicStateRequest,
        access="admin",
        effect="action",
    )
    add_association = Operation(
        INFO,
        "add_association",
        JsonRpcBinding("addAssociation", PATH),
        params=AssociationRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_association = Operation(
        INFO,
        "remove_association",
        JsonRpcBinding("removeAssociation", PATH),
        params=AssociationRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_association_data = Operation(
        INFO,
        "get_association_data",
        JsonRpcBinding("getAssociationData", PATH),
        params=GetAssociationDataRequest,
        result=GetAssociationDataResult,
        access="admin",
        effect="read",
    )
    get_supported_groupings = Operation(
        INFO,
        "get_supported_groupings",
        JsonRpcBinding("getSupportedGroupings", PATH),
        params=InterfaceRefreshRequest,
        result=GetSupportedGroupingsResult,
        access="admin",
        effect="read",
    )
    get_wake_up_info = Operation(
        INFO,
        "get_wake_up_info",
        JsonRpcBinding("getWakeUpInfo", PATH),
        params=InterfaceRefreshRequest,
        result=GetWakeUpInfoResult,
        access="admin",
        effect="read",
    )
    set_wake_up_info = Operation(
        INFO,
        "set_wake_up_info",
        JsonRpcBinding("setWakeUpInfo", PATH),
        params=SetWakeUpInfoRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_meter_reading = Operation(
        INFO,
        "get_meter_reading",
        JsonRpcBinding("getMeterReading", PATH),
        params=GetMeterReadingRequest,
        result=GetMeterReadingResult,
        access="admin",
        effect="read",
    )
    get_meter_capabilities = Operation(
        INFO,
        "get_meter_capabilities",
        JsonRpcBinding("getMeterCapabilities", PATH),
        params=InterfaceRefreshRequest,
        result=GetMeterCapabilitiesResult,
        access="admin",
        effect="read",
    )
    reset_meter = Operation(
        INFO,
        "reset_meter",
        JsonRpcBinding("resetMeter", PATH),
        params=InterfaceRequest,
        access="admin",
        effect="action",
    )
    get_indicator_value = Operation(
        INFO,
        "get_indicator_value",
        JsonRpcBinding("getIndicatorValue", PATH),
        params=GetIndicatorValueRequest,
        result=GetIndicatorValueResult,
        access="admin",
        effect="read",
    )
    set_indicator_value = Operation(
        INFO,
        "set_indicator_value",
        JsonRpcBinding("setIndicatorValue", PATH),
        params=SetIndicatorValueRequest,
        access="admin",
        effect="action",
    )
    get_indicator_capabilities = Operation(
        INFO,
        "get_indicator_capabilities",
        JsonRpcBinding("getIndicatorCapabilities", PATH),
        params=InterfaceRequest,
        result=GetIndicatorCapabilitiesResult,
        access="admin",
        effect="read",
    )
    get_firmware_info = Operation(
        INFO,
        "get_firmware_info",
        JsonRpcBinding("getFirmwareInfo", PATH),
        params=InterfaceRefreshRequest,
        result=GetFirmwareInfoResult,
        access="admin",
        effect="read",
    )
    request_firmware_update = Operation(
        INFO,
        "request_firmware_update",
        JsonRpcBinding("requestFirmwareUpdate", PATH),
        params=RequestFirmwareUpdateRequest,
        result=RequestFirmwareUpdateResult,
        access="admin",
        effect="action",
    )
    get_firmware_update_status = Operation(
        INFO,
        "get_firmware_update_status",
        JsonRpcBinding("getFirmwareUpdateStatus", PATH),
        params=InterfaceRequest,
        result=GetFirmwareUpdateStatusResult,
        access="admin",
        effect="read",
    )
    request_firmware_backup = Operation(
        INFO,
        "request_firmware_backup",
        JsonRpcBinding("requestFirmwareBackup", PATH),
        params=RequestFirmwareBackupRequest,
        result=RequestFirmwareBackupResult,
        access="admin",
        effect="action",
    )
    get_firmware_backup_status = Operation(
        INFO,
        "get_firmware_backup_status",
        JsonRpcBinding("getFirmwareBackupStatus", PATH),
        params=InterfaceRequest,
        result=GetFirmwareBackupStatusResult,
        access="admin",
        effect="read",
    )
    request_firmware_activation = Operation(
        INFO,
        "request_firmware_activation",
        JsonRpcBinding("requestFirmwareActivation", PATH),
        params=InterfaceRequest,
        result=RequestFirmwareActivationResult,
        access="admin",
        effect="action",
    )
    get_firmware_activation_status = Operation(
        INFO,
        "get_firmware_activation_status",
        JsonRpcBinding("getFirmwareActivationStatus", PATH),
        params=InterfaceRequest,
        result=GetFirmwareActivationStatusResult,
        access="admin",
        effect="read",
    )
    get_notification_capabilities = Operation(
        INFO,
        "get_notification_capabilities",
        JsonRpcBinding("getNotificationCapabilities", PATH),
        params=InterfaceRefreshRequest,
        result=GetNotificationCapabilitiesResult,
        access="admin",
        effect="read",
    )
    get_notification_event_support = Operation(
        INFO,
        "get_notification_event_support",
        JsonRpcBinding("getNotificationEventSupport", PATH),
        params=GetNotificationEventSupportRequest,
        result=GetNotificationEventSupportResult,
        access="admin",
        effect="read",
    )
    get_notification_state = Operation(
        INFO,
        "get_notification_state",
        JsonRpcBinding("getNotificationState", PATH),
        params=GetNotificationStateRequest,
        result=GetNotificationStateResult,
        access="admin",
        effect="read",
    )
    set_notification_state = Operation(
        INFO,
        "set_notification_state",
        JsonRpcBinding("setNotificationState", PATH),
        params=SetNotificationStateRequest,
        access="admin",
        effect="action",
    )
    get_all_notification_event_support = Operation(
        INFO,
        "get_all_notification_event_support",
        JsonRpcBinding("getAllNotificationEventSupport", PATH),
        params=InterfaceRefreshRequest,
        result=GetAllNotificationEventSupportResult,
        access="admin",
        effect="read",
    )
    get_central_scene_capabilities = Operation(
        INFO,
        "get_central_scene_capabilities",
        JsonRpcBinding("getCentralSceneCapabilities", PATH),
        params=InterfaceRefreshRequest,
        result=GetCentralSceneCapabilitiesResult,
        access="admin",
        effect="read",
    )
    get_central_scene_configuration = Operation(
        INFO,
        "get_central_scene_configuration",
        JsonRpcBinding("getCentralSceneConfiguration", PATH),
        params=InterfaceRequest,
        result=GetCentralSceneConfigurationResult,
        access="admin",
        effect="read",
    )
    set_central_scene_configuration = Operation(
        INFO,
        "set_central_scene_configuration",
        JsonRpcBinding("setCentralSceneConfiguration", PATH),
        params=SetCentralSceneConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_central_scene_state = Operation(
        INFO,
        "get_central_scene_state",
        JsonRpcBinding("getCentralSceneState", PATH),
        params=InterfaceRequest,
        result=GetCentralSceneStateResult,
        access="admin",
        effect="read",
    )
    get_anti_theft_unlock_state = Operation(
        INFO,
        "get_anti_theft_unlock_state",
        JsonRpcBinding("getAntiTheftUnlockState", PATH),
        params=InterfaceRefreshRequest,
        result=GetAntiTheftUnlockStateResult,
        access="admin",
        effect="read",
    )
    set_anti_theft_unlock_state = Operation(
        INFO,
        "set_anti_theft_unlock_state",
        JsonRpcBinding("setAntiTheftUnlockState", PATH),
        params=SetAntiTheftUnlockStateRequest,
        access="admin",
        effect="action",
    )
    set_temperature_threshold = Operation(
        INFO,
        "set_temperature_threshold",
        JsonRpcBinding("setTemperatureThreshold", PATH),
        params=SetTemperatureThresholdRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_temperature_threshold = Operation(
        INFO,
        "get_temperature_threshold",
        JsonRpcBinding("getTemperatureThreshold", PATH),
        params=GetTemperatureThresholdRequest,
        result=GetTemperatureThresholdResult,
        access="admin",
        effect="read",
    )
    set_io_function_binary_switch = Operation(
        INFO,
        "set_io_function_binary_switch",
        JsonRpcBinding("setIoFunctionBinarySwitch", PATH),
        params=SetIoFunctionBinarySwitchRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_io_function_one_shot = Operation(
        INFO,
        "set_io_function_one_shot",
        JsonRpcBinding("setIoFunctionOneShot", PATH),
        params=SetIoFunctionOneShotRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_io_function_set_reset = Operation(
        INFO,
        "set_io_function_set_reset",
        JsonRpcBinding("setIoFunctionSetReset", PATH),
        params=SetIoFunctionSetResetRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_io_function_toggle = Operation(
        INFO,
        "set_io_function_toggle",
        JsonRpcBinding("setIoFunctionToggle", PATH),
        params=SetIoFunctionToggleRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_io_function = Operation(
        INFO,
        "remove_io_function",
        JsonRpcBinding("removeIoFunction", PATH),
        params=EndpointRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_io_configuration = Operation(
        INFO,
        "get_io_configuration",
        JsonRpcBinding("getIoConfiguration", PATH),
        params=EndpointRequest,
        result=GetIoConfigurationResult,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class ZWaveApi(SyncApi):
    """Z-Wave API (``zwave``, version 1)."""

    INFO = INFO

    def set_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable Z-Wave on the device.

        The change shows up in the system log even if Z-Wave fails to start.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    def get_enabled(self, *, request_options: RequestOptions | None = None) -> GetEnabledResult:
        """Check whether Z-Wave is enabled (running) on the device. Access: admin."""
        return self._run(OPS.get_enabled, None, {}, request_options)

    def add_node(
        self,
        *,
        device_specific_key: DeviceSpecificKey | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Start adding (including) a Z-Wave device to the network.

        Asynchronous: poll get_operation until the operation completes. The operation times out after one
        minute if no device is found.

        Access: admin.
        """
        self._run(OPS.add_node, None, {"device_specific_key": device_specific_key}, request_options)

    def remove_node(self, *, request_options: RequestOptions | None = None) -> None:
        """Start removing (excluding) a Z-Wave device from the network.

        Asynchronous: poll get_operation until the operation completes. The operation times out after one
        minute if no device is found.

        Access: admin.
        """
        self._run(OPS.remove_node, None, {}, request_options)

    def get_operation(self, *, request_options: RequestOptions | None = None) -> GetOperationResult:
        """Get the current and previous network operation and the progress status. Access: admin."""
        return self._run(OPS.get_operation, None, {}, request_options)

    def abort_operation(self, *, request_options: RequestOptions | None = None) -> None:
        """Abort the ongoing network operation.

        Asynchronous: poll get_operation until the operation completes. Aborting after
        addNodeStatusProtocolDone or replaceNodeStatusProtocolDone leaves the node added or removed; undo it
        with remove_node or add_node.

        Access: admin.
        """
        self._run(OPS.abort_operation, None, {}, request_options)

    def reset_network(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the Z-Wave network to factory default settings.

        Asynchronous: poll get_operation until the operation completes. Devices of the old network must be
        removed (for example with remove_node) before they can be added again.

        Access: admin.
        """
        self._run(OPS.reset_network, None, {}, request_options)

    def refresh_network(self, *, request_options: RequestOptions | None = None) -> None:
        """Refresh the network topology, routing table and internal network data.

        Asynchronous: poll get_operation until the operation completes.

        Access: admin.
        """
        self._run(OPS.refresh_network, None, {}, request_options)

    def get_node_list(
        self, node_i_ds: list[int] | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> GetNodeListResult:
        """List all nodes of the network, or the nodes with the given node IDs. Access: admin."""
        return self._run(OPS.get_node_list, None, {"node_i_ds": node_i_ds}, request_options)

    def get_endpoint_list(
        self, node_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetEndpointListResult:
        """List the endpoints of a node. Access: admin."""
        return self._run(OPS.get_endpoint_list, None, {"node_descriptor": node_descriptor}, request_options)

    def get_endpoint_interface_list(
        self, endpoint_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetEndpointInterfaceListResult:
        """List and describe the interfaces of an endpoint. Access: admin."""
        return self._run(
            OPS.get_endpoint_interface_list, None, {"endpoint_descriptor": endpoint_descriptor}, request_options
        )

    def get_summary_list(self, *, request_options: RequestOptions | None = None) -> GetSummaryListResult:
        """Get a summary of all nodes, endpoints and interfaces of the network.

        A subset of what get_node_list, get_endpoint_list and get_endpoint_interface_list return, for all
        nodes and endpoints.

        Access: admin.
        """
        return self._run(OPS.get_summary_list, None, {}, request_options)

    def replace_failed_node(
        self,
        node_descriptor: int,
        *,
        device_specific_key: DeviceSpecificKey | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Start replacing a failed node with a new device.

        Asynchronous: poll get_operation until the operation completes. The operation times out after one
        minute if no new node is found.

        Access: admin.
        """
        self._run(
            OPS.replace_failed_node,
            None,
            {"node_descriptor": node_descriptor, "device_specific_key": device_specific_key},
            request_options,
        )

    def remove_failed_node(self, node_descriptor: int, *, request_options: RequestOptions | None = None) -> None:
        """Start removing a failed (unresponsive) node from the network.

        Asynchronous: poll get_operation until the operation completes. Unlike remove_node, this only works
        on an unresponsive node.

        Access: admin.
        """
        self._run(OPS.remove_failed_node, None, {"node_descriptor": node_descriptor}, request_options)

    def set_endpoint_info(
        self,
        endpoint_descriptor: int,
        *,
        name: str | MISSING = MISSING,
        location: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the nice name and/or location of an endpoint.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_endpoint_info,
            None,
            {"endpoint_descriptor": endpoint_descriptor, "name": name, "location": location},
            request_options,
        )

    def get_s2_requested_keys(self, *, request_options: RequestOptions | None = None) -> GetS2RequestedKeysResult:
        """Get the S2 keys requested by the joining node.

        Call during add_node when get_operation reports addNodeStatusRequestedKeyReady.

        Access: admin.
        """
        return self._run(OPS.get_s2_requested_keys, None, {}, request_options)

    def set_s2_grant_keys(
        self,
        grant_keys: list[SecurityKey],
        *,
        accept: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Grant S2 keys to the joining node, or interrupt S2 bootstrapping. Access: admin."""
        self._run(OPS.set_s2_grant_keys, None, {"grant_keys": grant_keys, "accept": accept}, request_options)

    def get_s2_device_specific_key(
        self, *, request_options: RequestOptions | None = None
    ) -> GetS2DeviceSpecificKeyResult:
        """Get the device specific key (DSK) of the joining node.

        Call during add_node when get_operation reports addNodeStatusDSKReady.

        Access: admin.
        """
        return self._run(OPS.get_s2_device_specific_key, None, {}, request_options)

    def accept_s2(
        self,
        accept: bool,
        *,
        device_specific_key: DeviceSpecificKey | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Accept or reject the joining node in S2 mode. Access: admin."""
        self._run(OPS.accept_s2, None, {"accept": accept, "device_specific_key": device_specific_key}, request_options)

    def refresh_node(self, node_descriptor: int, *, request_options: RequestOptions | None = None) -> None:
        """Refresh the information of a single node.

        Asynchronous: poll get_operation until the operation completes.

        Access: admin.
        """
        self._run(OPS.refresh_node, None, {"node_descriptor": node_descriptor}, request_options)

    def add_to_provisioning_list(
        self,
        device_specific_key: DeviceSpecificKey,
        *,
        name: str | MISSING = MISSING,
        location: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Add an end node to the SmartStart provisioning list. Access: admin."""
        self._run(
            OPS.add_to_provisioning_list,
            None,
            {"device_specific_key": device_specific_key, "name": name, "location": location},
            request_options,
        )

    def remove_from_provisioning_list(
        self, device_specific_key: DeviceSpecificKey, *, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an end node from the SmartStart provisioning list. Access: admin."""
        self._run(
            OPS.remove_from_provisioning_list, None, {"device_specific_key": device_specific_key}, request_options
        )

    def get_provisioning_list(self, *, request_options: RequestOptions | None = None) -> GetProvisioningListResult:
        """List the entries of the SmartStart provisioning list. Access: admin."""
        return self._run(OPS.get_provisioning_list, None, {}, request_options)

    def get_battery_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetBatteryStateResult:
        """Get the battery state of an end node, or the last known state from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_battery_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def get_multilevel_sensor_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        type: SensorType | MISSING = MISSING,
        unit: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMultilevelSensorStateResult:
        """Get the multilevel sensor state(s) of an end node, or the last known states from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_multilevel_sensor_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "type": type, "unit": unit},
            request_options,
        )

    def get_multilevel_sensor_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMultilevelSensorSupportResult:
        """Get the sensor types supported by a multilevel sensor.

        Requires Multilevel Sensor Command Class version 5 or above; all devices respond to
        get_multilevel_sensor_state.

        Access: admin.
        """
        return self._run(
            OPS.get_multilevel_sensor_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def get_multilevel_sensor_unit_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        sensor_type: SensorType,
        request_options: RequestOptions | None = None,
    ) -> GetMultilevelSensorUnitSupportResult:
        """Get the units supported by a multilevel sensor for one sensor type.

        Requires Multilevel Sensor Command Class version 5 or above.

        Access: admin.
        """
        return self._run(
            OPS.get_multilevel_sensor_unit_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "sensor_type": sensor_type},
            request_options,
        )

    def get_configuration(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        param_num: int,
        request_options: RequestOptions | None = None,
    ) -> GetConfigurationResult:
        """Get the value of a configuration parameter of an end node, or the last known value from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_configuration,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "param_num": param_num},
            request_options,
        )

    @overload
    def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_configuration(
        self,
        /,
        *,
        interface_descriptor: int,
        param_num: int,
        use_default: bool,
        param_value: float | MISSING = MISSING,
        param_size: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set a configuration parameter of an end node.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_configuration, request, kwargs, request_options)

    def get_binary_switch_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetBinarySwitchStateResult:
        """Get the binary switch state of an end node, or the last known state from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_binary_switch_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def set_binary_switch_state(
        self,
        interface_descriptor: int,
        *,
        value: bool,
        duration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Turn a binary switch ON or OFF. Access: admin."""
        self._run(
            OPS.set_binary_switch_state,
            None,
            {"interface_descriptor": interface_descriptor, "value": value, "duration": duration},
            request_options,
        )

    def get_basic_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetBasicStateResult:
        """Get the value mapped to the basic interface of an end node, or the last known value from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_basic_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def set_basic_state(
        self, interface_descriptor: int, *, value: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the value mapped to the basic interface of an end node. Access: admin."""
        self._run(
            OPS.set_basic_state, None, {"interface_descriptor": interface_descriptor, "value": value}, request_options
        )

    @overload
    def add_association(
        self, request: AssociationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_association(
        self,
        /,
        *,
        interface_descriptor: int,
        group_id: int,
        member_count: int,
        members: list[AssociationMember],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_association(
        self,
        request: AssociationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add devices to an association group (devices that communicate directly with each other).

        Access: admin.
        """
        self._run(OPS.add_association, request, kwargs, request_options)

    @overload
    def remove_association(
        self, request: AssociationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def remove_association(
        self,
        /,
        *,
        interface_descriptor: int,
        group_id: int,
        member_count: int,
        members: list[AssociationMember],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def remove_association(
        self,
        request: AssociationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove devices from an association group. Access: admin."""
        self._run(OPS.remove_association, request, kwargs, request_options)

    def get_association_data(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        group_id: int,
        request_options: RequestOptions | None = None,
    ) -> GetAssociationDataResult:
        """Get the members of an association group from the end node or the cache. Access: admin."""
        return self._run(
            OPS.get_association_data,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "group_id": group_id},
            request_options,
        )

    def get_supported_groupings(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetSupportedGroupingsResult:
        """Get the association group IDs supported by an end node. Access: admin."""
        return self._run(
            OPS.get_supported_groupings,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def get_wake_up_info(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetWakeUpInfoResult:
        """Get the wake-up interval settings of an end node, or the last known settings from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_wake_up_info,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def set_wake_up_info(
        self,
        interface_descriptor: int,
        *,
        wake_up_interval: int,
        node_id: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the wake-up interval of an end node and the node to notify on wake-up.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_wake_up_info,
            None,
            {"interface_descriptor": interface_descriptor, "wake_up_interval": wake_up_interval, "node_id": node_id},
            request_options,
        )

    def get_meter_reading(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        unit: Literal[
            "noPreference",
            "eleckWh",
            "eleckVAh",
            "elecW",
            "elecPulse",
            "elecV",
            "elecA",
            "elecPF",
            "elecKVar",
            "elecKVarh",
            "gasCM",
            "gasCF",
            "gasPulse",
            "waterCM",
            "waterCF",
            "waterGal",
            "waterPulse",
            "heatkWh",
            "coolkWh",
        ]
        | MISSING = MISSING,
        rate_type: Literal["noPreference", "import", "export"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMeterReadingResult:
        """Get the meter readings of an end node, or the last known readings from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_meter_reading,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "unit": unit, "rate_type": rate_type},
            request_options,
        )

    def get_meter_capabilities(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMeterCapabilitiesResult:
        """Get the meter capabilities of an end node, or the last known capabilities from the cache.

        Requires Meter Command Class version 2 or above; the result is otherwise undefined.

        Access: admin.
        """
        return self._run(
            OPS.get_meter_capabilities,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def reset_meter(self, interface_descriptor: int, *, request_options: RequestOptions | None = None) -> None:
        """Reset all accumulated values of a meter device.

        Requires Meter Command Class version 2 or above; the behavior is otherwise undefined.

        Access: admin.
        """
        self._run(OPS.reset_meter, None, {"interface_descriptor": interface_descriptor}, request_options)

    def get_indicator_value(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        indicator_name: IndicatorName | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetIndicatorValueResult:
        """Get the indicator values of an end node, or the last known values from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_indicator_value,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "indicator_name": indicator_name},
            request_options,
        )

    @overload
    def set_indicator_value(
        self, request: SetIndicatorValueRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_indicator_value(
        self,
        /,
        *,
        interface_descriptor: int,
        value: int | MISSING = MISSING,
        indicator_name: IndicatorName | MISSING = MISSING,
        properties: list[IndicatorProperty] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_indicator_value(
        self,
        request: SetIndicatorValueRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set an indicator value of an end node.

        Give ``value`` for Indicator Command Class version 1 nodes, and ``indicatorName`` with
        ``properties`` for version 2 and above.

        Access: admin.
        """
        self._run(OPS.set_indicator_value, request, kwargs, request_options)

    def get_indicator_capabilities(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetIndicatorCapabilitiesResult:
        """Get the supported indicators and their properties from the cache. Access: admin."""
        return self._run(
            OPS.get_indicator_capabilities, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    def get_firmware_info(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetFirmwareInfoResult:
        """Get the firmware information of an end node, or the last known information from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_firmware_info,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    @overload
    def request_firmware_update(
        self, request: RequestFirmwareUpdateRequest, /, *, request_options: RequestOptions | None = None
    ) -> RequestFirmwareUpdateResult: ...
    @overload
    def request_firmware_update(
        self,
        /,
        *,
        interface_descriptor: int,
        vendor_id: int,
        firmware_target: int,
        firmware_id: int,
        file_name: str,
        hardware_version: int,
        request_options: RequestOptions | None = None,
    ) -> RequestFirmwareUpdateResult: ...
    def request_firmware_update(
        self,
        request: RequestFirmwareUpdateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> RequestFirmwareUpdateResult:
        """Start a firmware update of an end node.

        Call get_firmware_info first. Poll get_firmware_update_status for progress.

        Access: admin.
        """
        return self._run(OPS.request_firmware_update, request, kwargs, request_options)

    def get_firmware_update_status(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetFirmwareUpdateStatusResult:
        """Get the status of the firmware update request of an end node. Access: admin."""
        return self._run(
            OPS.get_firmware_update_status, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    @overload
    def request_firmware_backup(
        self, request: RequestFirmwareBackupRequest, /, *, request_options: RequestOptions | None = None
    ) -> RequestFirmwareBackupResult: ...
    @overload
    def request_firmware_backup(
        self,
        /,
        *,
        interface_descriptor: int,
        vendor_id: int,
        firmware_target: int,
        firmware_id: int,
        hardware_version: int,
        request_options: RequestOptions | None = None,
    ) -> RequestFirmwareBackupResult: ...
    def request_firmware_backup(
        self,
        request: RequestFirmwareBackupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> RequestFirmwareBackupResult:
        """Start a firmware backup of an end node.

        Call get_firmware_info first. Requires Firmware Update Meta Data Command Class version 5 or above.

        Access: admin.
        """
        return self._run(OPS.request_firmware_backup, request, kwargs, request_options)

    def get_firmware_backup_status(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetFirmwareBackupStatusResult:
        """Get the status of the firmware backup request of an end node.

        Requires Firmware Update Meta Data Command Class version 5 or above.

        Access: admin.
        """
        return self._run(
            OPS.get_firmware_backup_status, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    def request_firmware_activation(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> RequestFirmwareActivationResult:
        """Start activating downloaded firmware on an end node.

        Requires Firmware Update Meta Data Command Class version 4 or above.

        Access: admin.
        """
        return self._run(
            OPS.request_firmware_activation, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    def get_firmware_activation_status(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetFirmwareActivationStatusResult:
        """Get the status of the firmware activation request of an end node.

        Requires Firmware Update Meta Data Command Class version 4 or above.

        Access: admin.
        """
        return self._run(
            OPS.get_firmware_activation_status, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    def get_notification_capabilities(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetNotificationCapabilitiesResult:
        """Get the alarm/notification types supported by an end node.

        Requires Alarm/Notification Command Class version 2 or above.

        Access: admin.
        """
        return self._run(
            OPS.get_notification_capabilities,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def get_notification_event_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        zwave_alarm_type: str,
        request_options: RequestOptions | None = None,
    ) -> GetNotificationEventSupportResult:
        """Get the events supported by one alarm/notification type of an end node.

        Requires Alarm/Notification Command Class version 3 or above.

        Access: admin.
        """
        return self._run(
            OPS.get_notification_event_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "zwave_alarm_type": zwave_alarm_type},
            request_options,
        )

    @overload
    def get_notification_state(
        self, request: GetNotificationStateRequest, /, *, request_options: RequestOptions | None = None
    ) -> GetNotificationStateResult: ...
    @overload
    def get_notification_state(
        self,
        interface_descriptor: int,
        /,
        *,
        refresh: bool | MISSING = MISSING,
        vendor_alarm_type: int | MISSING = MISSING,
        zwave_alarm_type: str | MISSING = MISSING,
        zwave_event: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetNotificationStateResult: ...
    def get_notification_state(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> GetNotificationStateResult:
        """Get the alarm/notification state (push mode) or a pending notification (pull mode) from the end node or the cache.

        The report list is not a history log; newer reports may overwrite older ones.

        Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, GetNotificationStateRequest):
            kwargs = bind_positional(OPS.get_notification_state, ("interface_descriptor",), (request, *args), kwargs)
            request = None
        return self._run(OPS.get_notification_state, request, kwargs, request_options)

    def set_notification_state(
        self,
        interface_descriptor: int,
        *,
        zwave_alarm_type: str,
        status: Literal[0, 255],
        request_options: RequestOptions | None = None,
    ) -> None:
        """Enable or disable unsolicited reports of an alarm type (push mode), or clear a persistent notification (pull mode).

        Requires Alarm/Notification Command Class version 2 or above.

        Access: admin.
        """
        self._run(
            OPS.set_notification_state,
            None,
            {"interface_descriptor": interface_descriptor, "zwave_alarm_type": zwave_alarm_type, "status": status},
            request_options,
        )

    def get_all_notification_event_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAllNotificationEventSupportResult:
        """Get all alarm/notification types and events supported by an end node. Access: admin."""
        return self._run(
            OPS.get_all_notification_event_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def get_central_scene_capabilities(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCentralSceneCapabilitiesResult:
        """Get the number of scenes and the supported key attributes of an end node. Access: admin."""
        return self._run(
            OPS.get_central_scene_capabilities,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def get_central_scene_configuration(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetCentralSceneConfigurationResult:
        """Get the scene notification configuration of an end node.

        Requires Central Scene Command Class version 3 or above.

        Access: admin.
        """
        return self._run(
            OPS.get_central_scene_configuration, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    def set_central_scene_configuration(
        self, interface_descriptor: int, *, slow_refresh: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Configure scene notifications (slow refresh) of an end node.

        Requires Central Scene Command Class version 3 or above.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_central_scene_configuration,
            None,
            {"interface_descriptor": interface_descriptor, "slow_refresh": slow_refresh},
            request_options,
        )

    def get_central_scene_state(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetCentralSceneStateResult:
        """Get the cached central scene data. Access: admin."""
        return self._run(
            OPS.get_central_scene_state, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    def get_anti_theft_unlock_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAntiTheftUnlockStateResult:
        """Get the anti-theft unlock state of an end node, or the last known state from the cache.

        Access: admin.
        """
        return self._run(
            OPS.get_anti_theft_unlock_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    def set_anti_theft_unlock_state(
        self, interface_descriptor: int, *, code: str, request_options: RequestOptions | None = None
    ) -> None:
        """Unlock an anti-theft locked node with its Magic Code. Access: admin."""
        self._run(
            OPS.set_anti_theft_unlock_state,
            None,
            {"interface_descriptor": interface_descriptor, "code": code},
            request_options,
        )

    @overload
    def set_temperature_threshold(
        self, request: SetTemperatureThresholdRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_temperature_threshold(
        self,
        endpoint_descriptor: int,
        /,
        *,
        active: bool,
        warning_rule: Literal["above", "below"] | MISSING = MISSING,
        threshold: int | MISSING = MISSING,
        unit: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_temperature_threshold(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Configure the temperature threshold event of an endpoint.

        Omitted optional parameters keep their current values. Requires the Multilevel Sensor Command Class.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetTemperatureThresholdRequest):
            kwargs = bind_positional(OPS.set_temperature_threshold, ("endpoint_descriptor",), (request, *args), kwargs)
            request = None
        self._run(OPS.set_temperature_threshold, request, kwargs, request_options)

    def get_temperature_threshold(
        self, endpoint_descriptor: int, *, unit: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetTemperatureThresholdResult:
        """Get the temperature threshold settings of an endpoint.

        Requires the Multilevel Sensor Command Class.

        Access: admin.
        """
        return self._run(
            OPS.get_temperature_threshold,
            None,
            {"endpoint_descriptor": endpoint_descriptor, "unit": unit},
            request_options,
        )

    def set_io_function_binary_switch(
        self,
        endpoint_descriptor: int,
        *,
        io_port_number: int,
        invert: bool,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Binary-switch I/O function of an endpoint.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_io_function_binary_switch,
            None,
            {"endpoint_descriptor": endpoint_descriptor, "io_port_number": io_port_number, "invert": invert},
            request_options,
        )

    @overload
    def set_io_function_one_shot(
        self, request: SetIoFunctionOneShotRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_io_function_one_shot(
        self,
        /,
        *,
        endpoint_descriptor: int,
        io_port_number: int,
        alarm_type: int,
        event: int,
        invert: bool,
        duration: int,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_io_function_one_shot(
        self,
        request: SetIoFunctionOneShotRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the One-shot I/O function of an endpoint.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_io_function_one_shot, request, kwargs, request_options)

    @overload
    def set_io_function_set_reset(
        self, request: SetIoFunctionSetResetRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_io_function_set_reset(
        self,
        /,
        *,
        endpoint_descriptor: int,
        io_port_number: int,
        set_alarm_type: int,
        set_event: int,
        reset_alarm_type: int,
        reset_event: int,
        invert: bool,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_io_function_set_reset(
        self,
        request: SetIoFunctionSetResetRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the Set/Reset I/O function of an endpoint.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_io_function_set_reset, request, kwargs, request_options)

    def set_io_function_toggle(
        self,
        endpoint_descriptor: int,
        *,
        io_port_number: int,
        alarm_type: int,
        event: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Toggle I/O function of an endpoint. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_io_function_toggle,
            None,
            {
                "endpoint_descriptor": endpoint_descriptor,
                "io_port_number": io_port_number,
                "alarm_type": alarm_type,
                "event": event,
            },
            request_options,
        )

    def remove_io_function(self, endpoint_descriptor: int, *, request_options: RequestOptions | None = None) -> None:
        """Remove the I/O function of an endpoint. Access: admin."""
        self._run(OPS.remove_io_function, None, {"endpoint_descriptor": endpoint_descriptor}, request_options)

    def get_io_configuration(
        self, endpoint_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetIoConfigurationResult:
        """Get the I/O function configuration of an endpoint. Access: admin."""
        return self._run(OPS.get_io_configuration, None, {"endpoint_descriptor": endpoint_descriptor}, request_options)


class AsyncZWaveApi(AsyncApi):
    """Z-Wave API (``zwave``, version 1)."""

    INFO = INFO

    async def set_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable Z-Wave on the device.

        The change shows up in the system log even if Z-Wave fails to start.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    async def get_enabled(self, *, request_options: RequestOptions | None = None) -> GetEnabledResult:
        """Check whether Z-Wave is enabled (running) on the device. Access: admin."""
        return await self._run(OPS.get_enabled, None, {}, request_options)

    async def add_node(
        self,
        *,
        device_specific_key: DeviceSpecificKey | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Start adding (including) a Z-Wave device to the network.

        Asynchronous: poll get_operation until the operation completes. The operation times out after one
        minute if no device is found.

        Access: admin.
        """
        await self._run(OPS.add_node, None, {"device_specific_key": device_specific_key}, request_options)

    async def remove_node(self, *, request_options: RequestOptions | None = None) -> None:
        """Start removing (excluding) a Z-Wave device from the network.

        Asynchronous: poll get_operation until the operation completes. The operation times out after one
        minute if no device is found.

        Access: admin.
        """
        await self._run(OPS.remove_node, None, {}, request_options)

    async def get_operation(self, *, request_options: RequestOptions | None = None) -> GetOperationResult:
        """Get the current and previous network operation and the progress status. Access: admin."""
        return await self._run(OPS.get_operation, None, {}, request_options)

    async def abort_operation(self, *, request_options: RequestOptions | None = None) -> None:
        """Abort the ongoing network operation.

        Asynchronous: poll get_operation until the operation completes. Aborting after
        addNodeStatusProtocolDone or replaceNodeStatusProtocolDone leaves the node added or removed; undo it
        with remove_node or add_node.

        Access: admin.
        """
        await self._run(OPS.abort_operation, None, {}, request_options)

    async def reset_network(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the Z-Wave network to factory default settings.

        Asynchronous: poll get_operation until the operation completes. Devices of the old network must be
        removed (for example with remove_node) before they can be added again.

        Access: admin.
        """
        await self._run(OPS.reset_network, None, {}, request_options)

    async def refresh_network(self, *, request_options: RequestOptions | None = None) -> None:
        """Refresh the network topology, routing table and internal network data.

        Asynchronous: poll get_operation until the operation completes.

        Access: admin.
        """
        await self._run(OPS.refresh_network, None, {}, request_options)

    async def get_node_list(
        self, node_i_ds: list[int] | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> GetNodeListResult:
        """List all nodes of the network, or the nodes with the given node IDs. Access: admin."""
        return await self._run(OPS.get_node_list, None, {"node_i_ds": node_i_ds}, request_options)

    async def get_endpoint_list(
        self, node_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetEndpointListResult:
        """List the endpoints of a node. Access: admin."""
        return await self._run(OPS.get_endpoint_list, None, {"node_descriptor": node_descriptor}, request_options)

    async def get_endpoint_interface_list(
        self, endpoint_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetEndpointInterfaceListResult:
        """List and describe the interfaces of an endpoint. Access: admin."""
        return await self._run(
            OPS.get_endpoint_interface_list, None, {"endpoint_descriptor": endpoint_descriptor}, request_options
        )

    async def get_summary_list(self, *, request_options: RequestOptions | None = None) -> GetSummaryListResult:
        """Get a summary of all nodes, endpoints and interfaces of the network.

        A subset of what get_node_list, get_endpoint_list and get_endpoint_interface_list return, for all
        nodes and endpoints.

        Access: admin.
        """
        return await self._run(OPS.get_summary_list, None, {}, request_options)

    async def replace_failed_node(
        self,
        node_descriptor: int,
        *,
        device_specific_key: DeviceSpecificKey | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Start replacing a failed node with a new device.

        Asynchronous: poll get_operation until the operation completes. The operation times out after one
        minute if no new node is found.

        Access: admin.
        """
        await self._run(
            OPS.replace_failed_node,
            None,
            {"node_descriptor": node_descriptor, "device_specific_key": device_specific_key},
            request_options,
        )

    async def remove_failed_node(self, node_descriptor: int, *, request_options: RequestOptions | None = None) -> None:
        """Start removing a failed (unresponsive) node from the network.

        Asynchronous: poll get_operation until the operation completes. Unlike remove_node, this only works
        on an unresponsive node.

        Access: admin.
        """
        await self._run(OPS.remove_failed_node, None, {"node_descriptor": node_descriptor}, request_options)

    async def set_endpoint_info(
        self,
        endpoint_descriptor: int,
        *,
        name: str | MISSING = MISSING,
        location: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the nice name and/or location of an endpoint.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_endpoint_info,
            None,
            {"endpoint_descriptor": endpoint_descriptor, "name": name, "location": location},
            request_options,
        )

    async def get_s2_requested_keys(self, *, request_options: RequestOptions | None = None) -> GetS2RequestedKeysResult:
        """Get the S2 keys requested by the joining node.

        Call during add_node when get_operation reports addNodeStatusRequestedKeyReady.

        Access: admin.
        """
        return await self._run(OPS.get_s2_requested_keys, None, {}, request_options)

    async def set_s2_grant_keys(
        self,
        grant_keys: list[SecurityKey],
        *,
        accept: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Grant S2 keys to the joining node, or interrupt S2 bootstrapping. Access: admin."""
        await self._run(OPS.set_s2_grant_keys, None, {"grant_keys": grant_keys, "accept": accept}, request_options)

    async def get_s2_device_specific_key(
        self, *, request_options: RequestOptions | None = None
    ) -> GetS2DeviceSpecificKeyResult:
        """Get the device specific key (DSK) of the joining node.

        Call during add_node when get_operation reports addNodeStatusDSKReady.

        Access: admin.
        """
        return await self._run(OPS.get_s2_device_specific_key, None, {}, request_options)

    async def accept_s2(
        self,
        accept: bool,
        *,
        device_specific_key: DeviceSpecificKey | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Accept or reject the joining node in S2 mode. Access: admin."""
        await self._run(
            OPS.accept_s2, None, {"accept": accept, "device_specific_key": device_specific_key}, request_options
        )

    async def refresh_node(self, node_descriptor: int, *, request_options: RequestOptions | None = None) -> None:
        """Refresh the information of a single node.

        Asynchronous: poll get_operation until the operation completes.

        Access: admin.
        """
        await self._run(OPS.refresh_node, None, {"node_descriptor": node_descriptor}, request_options)

    async def add_to_provisioning_list(
        self,
        device_specific_key: DeviceSpecificKey,
        *,
        name: str | MISSING = MISSING,
        location: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Add an end node to the SmartStart provisioning list. Access: admin."""
        await self._run(
            OPS.add_to_provisioning_list,
            None,
            {"device_specific_key": device_specific_key, "name": name, "location": location},
            request_options,
        )

    async def remove_from_provisioning_list(
        self, device_specific_key: DeviceSpecificKey, *, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an end node from the SmartStart provisioning list. Access: admin."""
        await self._run(
            OPS.remove_from_provisioning_list, None, {"device_specific_key": device_specific_key}, request_options
        )

    async def get_provisioning_list(
        self, *, request_options: RequestOptions | None = None
    ) -> GetProvisioningListResult:
        """List the entries of the SmartStart provisioning list. Access: admin."""
        return await self._run(OPS.get_provisioning_list, None, {}, request_options)

    async def get_battery_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetBatteryStateResult:
        """Get the battery state of an end node, or the last known state from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_battery_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def get_multilevel_sensor_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        type: SensorType | MISSING = MISSING,
        unit: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMultilevelSensorStateResult:
        """Get the multilevel sensor state(s) of an end node, or the last known states from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_multilevel_sensor_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "type": type, "unit": unit},
            request_options,
        )

    async def get_multilevel_sensor_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMultilevelSensorSupportResult:
        """Get the sensor types supported by a multilevel sensor.

        Requires Multilevel Sensor Command Class version 5 or above; all devices respond to
        get_multilevel_sensor_state.

        Access: admin.
        """
        return await self._run(
            OPS.get_multilevel_sensor_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def get_multilevel_sensor_unit_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        sensor_type: SensorType,
        request_options: RequestOptions | None = None,
    ) -> GetMultilevelSensorUnitSupportResult:
        """Get the units supported by a multilevel sensor for one sensor type.

        Requires Multilevel Sensor Command Class version 5 or above.

        Access: admin.
        """
        return await self._run(
            OPS.get_multilevel_sensor_unit_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "sensor_type": sensor_type},
            request_options,
        )

    async def get_configuration(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        param_num: int,
        request_options: RequestOptions | None = None,
    ) -> GetConfigurationResult:
        """Get the value of a configuration parameter of an end node, or the last known value from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_configuration,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "param_num": param_num},
            request_options,
        )

    @overload
    async def set_configuration(
        self, request: SetConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_configuration(
        self,
        /,
        *,
        interface_descriptor: int,
        param_num: int,
        use_default: bool,
        param_value: float | MISSING = MISSING,
        param_size: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_configuration(
        self,
        request: SetConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set a configuration parameter of an end node.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_configuration, request, kwargs, request_options)

    async def get_binary_switch_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetBinarySwitchStateResult:
        """Get the binary switch state of an end node, or the last known state from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_binary_switch_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def set_binary_switch_state(
        self,
        interface_descriptor: int,
        *,
        value: bool,
        duration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Turn a binary switch ON or OFF. Access: admin."""
        await self._run(
            OPS.set_binary_switch_state,
            None,
            {"interface_descriptor": interface_descriptor, "value": value, "duration": duration},
            request_options,
        )

    async def get_basic_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetBasicStateResult:
        """Get the value mapped to the basic interface of an end node, or the last known value from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_basic_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def set_basic_state(
        self, interface_descriptor: int, *, value: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the value mapped to the basic interface of an end node. Access: admin."""
        await self._run(
            OPS.set_basic_state, None, {"interface_descriptor": interface_descriptor, "value": value}, request_options
        )

    @overload
    async def add_association(
        self, request: AssociationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_association(
        self,
        /,
        *,
        interface_descriptor: int,
        group_id: int,
        member_count: int,
        members: list[AssociationMember],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_association(
        self,
        request: AssociationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add devices to an association group (devices that communicate directly with each other).

        Access: admin.
        """
        await self._run(OPS.add_association, request, kwargs, request_options)

    @overload
    async def remove_association(
        self, request: AssociationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def remove_association(
        self,
        /,
        *,
        interface_descriptor: int,
        group_id: int,
        member_count: int,
        members: list[AssociationMember],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def remove_association(
        self,
        request: AssociationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove devices from an association group. Access: admin."""
        await self._run(OPS.remove_association, request, kwargs, request_options)

    async def get_association_data(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        group_id: int,
        request_options: RequestOptions | None = None,
    ) -> GetAssociationDataResult:
        """Get the members of an association group from the end node or the cache. Access: admin."""
        return await self._run(
            OPS.get_association_data,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "group_id": group_id},
            request_options,
        )

    async def get_supported_groupings(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetSupportedGroupingsResult:
        """Get the association group IDs supported by an end node. Access: admin."""
        return await self._run(
            OPS.get_supported_groupings,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def get_wake_up_info(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetWakeUpInfoResult:
        """Get the wake-up interval settings of an end node, or the last known settings from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_wake_up_info,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def set_wake_up_info(
        self,
        interface_descriptor: int,
        *,
        wake_up_interval: int,
        node_id: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the wake-up interval of an end node and the node to notify on wake-up.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_wake_up_info,
            None,
            {"interface_descriptor": interface_descriptor, "wake_up_interval": wake_up_interval, "node_id": node_id},
            request_options,
        )

    async def get_meter_reading(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        unit: Literal[
            "noPreference",
            "eleckWh",
            "eleckVAh",
            "elecW",
            "elecPulse",
            "elecV",
            "elecA",
            "elecPF",
            "elecKVar",
            "elecKVarh",
            "gasCM",
            "gasCF",
            "gasPulse",
            "waterCM",
            "waterCF",
            "waterGal",
            "waterPulse",
            "heatkWh",
            "coolkWh",
        ]
        | MISSING = MISSING,
        rate_type: Literal["noPreference", "import", "export"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMeterReadingResult:
        """Get the meter readings of an end node, or the last known readings from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_meter_reading,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "unit": unit, "rate_type": rate_type},
            request_options,
        )

    async def get_meter_capabilities(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetMeterCapabilitiesResult:
        """Get the meter capabilities of an end node, or the last known capabilities from the cache.

        Requires Meter Command Class version 2 or above; the result is otherwise undefined.

        Access: admin.
        """
        return await self._run(
            OPS.get_meter_capabilities,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def reset_meter(self, interface_descriptor: int, *, request_options: RequestOptions | None = None) -> None:
        """Reset all accumulated values of a meter device.

        Requires Meter Command Class version 2 or above; the behavior is otherwise undefined.

        Access: admin.
        """
        await self._run(OPS.reset_meter, None, {"interface_descriptor": interface_descriptor}, request_options)

    async def get_indicator_value(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        indicator_name: IndicatorName | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetIndicatorValueResult:
        """Get the indicator values of an end node, or the last known values from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_indicator_value,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "indicator_name": indicator_name},
            request_options,
        )

    @overload
    async def set_indicator_value(
        self, request: SetIndicatorValueRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_indicator_value(
        self,
        /,
        *,
        interface_descriptor: int,
        value: int | MISSING = MISSING,
        indicator_name: IndicatorName | MISSING = MISSING,
        properties: list[IndicatorProperty] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_indicator_value(
        self,
        request: SetIndicatorValueRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set an indicator value of an end node.

        Give ``value`` for Indicator Command Class version 1 nodes, and ``indicatorName`` with
        ``properties`` for version 2 and above.

        Access: admin.
        """
        await self._run(OPS.set_indicator_value, request, kwargs, request_options)

    async def get_indicator_capabilities(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetIndicatorCapabilitiesResult:
        """Get the supported indicators and their properties from the cache. Access: admin."""
        return await self._run(
            OPS.get_indicator_capabilities, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    async def get_firmware_info(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetFirmwareInfoResult:
        """Get the firmware information of an end node, or the last known information from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_firmware_info,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    @overload
    async def request_firmware_update(
        self, request: RequestFirmwareUpdateRequest, /, *, request_options: RequestOptions | None = None
    ) -> RequestFirmwareUpdateResult: ...
    @overload
    async def request_firmware_update(
        self,
        /,
        *,
        interface_descriptor: int,
        vendor_id: int,
        firmware_target: int,
        firmware_id: int,
        file_name: str,
        hardware_version: int,
        request_options: RequestOptions | None = None,
    ) -> RequestFirmwareUpdateResult: ...
    async def request_firmware_update(
        self,
        request: RequestFirmwareUpdateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> RequestFirmwareUpdateResult:
        """Start a firmware update of an end node.

        Call get_firmware_info first. Poll get_firmware_update_status for progress.

        Access: admin.
        """
        return await self._run(OPS.request_firmware_update, request, kwargs, request_options)

    async def get_firmware_update_status(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetFirmwareUpdateStatusResult:
        """Get the status of the firmware update request of an end node. Access: admin."""
        return await self._run(
            OPS.get_firmware_update_status, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    @overload
    async def request_firmware_backup(
        self, request: RequestFirmwareBackupRequest, /, *, request_options: RequestOptions | None = None
    ) -> RequestFirmwareBackupResult: ...
    @overload
    async def request_firmware_backup(
        self,
        /,
        *,
        interface_descriptor: int,
        vendor_id: int,
        firmware_target: int,
        firmware_id: int,
        hardware_version: int,
        request_options: RequestOptions | None = None,
    ) -> RequestFirmwareBackupResult: ...
    async def request_firmware_backup(
        self,
        request: RequestFirmwareBackupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> RequestFirmwareBackupResult:
        """Start a firmware backup of an end node.

        Call get_firmware_info first. Requires Firmware Update Meta Data Command Class version 5 or above.

        Access: admin.
        """
        return await self._run(OPS.request_firmware_backup, request, kwargs, request_options)

    async def get_firmware_backup_status(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetFirmwareBackupStatusResult:
        """Get the status of the firmware backup request of an end node.

        Requires Firmware Update Meta Data Command Class version 5 or above.

        Access: admin.
        """
        return await self._run(
            OPS.get_firmware_backup_status, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    async def request_firmware_activation(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> RequestFirmwareActivationResult:
        """Start activating downloaded firmware on an end node.

        Requires Firmware Update Meta Data Command Class version 4 or above.

        Access: admin.
        """
        return await self._run(
            OPS.request_firmware_activation, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    async def get_firmware_activation_status(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetFirmwareActivationStatusResult:
        """Get the status of the firmware activation request of an end node.

        Requires Firmware Update Meta Data Command Class version 4 or above.

        Access: admin.
        """
        return await self._run(
            OPS.get_firmware_activation_status, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    async def get_notification_capabilities(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetNotificationCapabilitiesResult:
        """Get the alarm/notification types supported by an end node.

        Requires Alarm/Notification Command Class version 2 or above.

        Access: admin.
        """
        return await self._run(
            OPS.get_notification_capabilities,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def get_notification_event_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        zwave_alarm_type: str,
        request_options: RequestOptions | None = None,
    ) -> GetNotificationEventSupportResult:
        """Get the events supported by one alarm/notification type of an end node.

        Requires Alarm/Notification Command Class version 3 or above.

        Access: admin.
        """
        return await self._run(
            OPS.get_notification_event_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh, "zwave_alarm_type": zwave_alarm_type},
            request_options,
        )

    @overload
    async def get_notification_state(
        self, request: GetNotificationStateRequest, /, *, request_options: RequestOptions | None = None
    ) -> GetNotificationStateResult: ...
    @overload
    async def get_notification_state(
        self,
        interface_descriptor: int,
        /,
        *,
        refresh: bool | MISSING = MISSING,
        vendor_alarm_type: int | MISSING = MISSING,
        zwave_alarm_type: str | MISSING = MISSING,
        zwave_event: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetNotificationStateResult: ...
    async def get_notification_state(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> GetNotificationStateResult:
        """Get the alarm/notification state (push mode) or a pending notification (pull mode) from the end node or the cache.

        The report list is not a history log; newer reports may overwrite older ones.

        Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, GetNotificationStateRequest):
            kwargs = bind_positional(OPS.get_notification_state, ("interface_descriptor",), (request, *args), kwargs)
            request = None
        return await self._run(OPS.get_notification_state, request, kwargs, request_options)

    async def set_notification_state(
        self,
        interface_descriptor: int,
        *,
        zwave_alarm_type: str,
        status: Literal[0, 255],
        request_options: RequestOptions | None = None,
    ) -> None:
        """Enable or disable unsolicited reports of an alarm type (push mode), or clear a persistent notification (pull mode).

        Requires Alarm/Notification Command Class version 2 or above.

        Access: admin.
        """
        await self._run(
            OPS.set_notification_state,
            None,
            {"interface_descriptor": interface_descriptor, "zwave_alarm_type": zwave_alarm_type, "status": status},
            request_options,
        )

    async def get_all_notification_event_support(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAllNotificationEventSupportResult:
        """Get all alarm/notification types and events supported by an end node. Access: admin."""
        return await self._run(
            OPS.get_all_notification_event_support,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def get_central_scene_capabilities(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetCentralSceneCapabilitiesResult:
        """Get the number of scenes and the supported key attributes of an end node. Access: admin."""
        return await self._run(
            OPS.get_central_scene_capabilities,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def get_central_scene_configuration(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetCentralSceneConfigurationResult:
        """Get the scene notification configuration of an end node.

        Requires Central Scene Command Class version 3 or above.

        Access: admin.
        """
        return await self._run(
            OPS.get_central_scene_configuration, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    async def set_central_scene_configuration(
        self, interface_descriptor: int, *, slow_refresh: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Configure scene notifications (slow refresh) of an end node.

        Requires Central Scene Command Class version 3 or above.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_central_scene_configuration,
            None,
            {"interface_descriptor": interface_descriptor, "slow_refresh": slow_refresh},
            request_options,
        )

    async def get_central_scene_state(
        self, interface_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetCentralSceneStateResult:
        """Get the cached central scene data. Access: admin."""
        return await self._run(
            OPS.get_central_scene_state, None, {"interface_descriptor": interface_descriptor}, request_options
        )

    async def get_anti_theft_unlock_state(
        self,
        interface_descriptor: int,
        *,
        refresh: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetAntiTheftUnlockStateResult:
        """Get the anti-theft unlock state of an end node, or the last known state from the cache.

        Access: admin.
        """
        return await self._run(
            OPS.get_anti_theft_unlock_state,
            None,
            {"interface_descriptor": interface_descriptor, "refresh": refresh},
            request_options,
        )

    async def set_anti_theft_unlock_state(
        self, interface_descriptor: int, *, code: str, request_options: RequestOptions | None = None
    ) -> None:
        """Unlock an anti-theft locked node with its Magic Code. Access: admin."""
        await self._run(
            OPS.set_anti_theft_unlock_state,
            None,
            {"interface_descriptor": interface_descriptor, "code": code},
            request_options,
        )

    @overload
    async def set_temperature_threshold(
        self, request: SetTemperatureThresholdRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_temperature_threshold(
        self,
        endpoint_descriptor: int,
        /,
        *,
        active: bool,
        warning_rule: Literal["above", "below"] | MISSING = MISSING,
        threshold: int | MISSING = MISSING,
        unit: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_temperature_threshold(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Configure the temperature threshold event of an endpoint.

        Omitted optional parameters keep their current values. Requires the Multilevel Sensor Command Class.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetTemperatureThresholdRequest):
            kwargs = bind_positional(OPS.set_temperature_threshold, ("endpoint_descriptor",), (request, *args), kwargs)
            request = None
        await self._run(OPS.set_temperature_threshold, request, kwargs, request_options)

    async def get_temperature_threshold(
        self, endpoint_descriptor: int, *, unit: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> GetTemperatureThresholdResult:
        """Get the temperature threshold settings of an endpoint.

        Requires the Multilevel Sensor Command Class.

        Access: admin.
        """
        return await self._run(
            OPS.get_temperature_threshold,
            None,
            {"endpoint_descriptor": endpoint_descriptor, "unit": unit},
            request_options,
        )

    async def set_io_function_binary_switch(
        self,
        endpoint_descriptor: int,
        *,
        io_port_number: int,
        invert: bool,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Binary-switch I/O function of an endpoint.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_io_function_binary_switch,
            None,
            {"endpoint_descriptor": endpoint_descriptor, "io_port_number": io_port_number, "invert": invert},
            request_options,
        )

    @overload
    async def set_io_function_one_shot(
        self, request: SetIoFunctionOneShotRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_io_function_one_shot(
        self,
        /,
        *,
        endpoint_descriptor: int,
        io_port_number: int,
        alarm_type: int,
        event: int,
        invert: bool,
        duration: int,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_io_function_one_shot(
        self,
        request: SetIoFunctionOneShotRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the One-shot I/O function of an endpoint.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_io_function_one_shot, request, kwargs, request_options)

    @overload
    async def set_io_function_set_reset(
        self, request: SetIoFunctionSetResetRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_io_function_set_reset(
        self,
        /,
        *,
        endpoint_descriptor: int,
        io_port_number: int,
        set_alarm_type: int,
        set_event: int,
        reset_alarm_type: int,
        reset_event: int,
        invert: bool,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_io_function_set_reset(
        self,
        request: SetIoFunctionSetResetRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the Set/Reset I/O function of an endpoint.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_io_function_set_reset, request, kwargs, request_options)

    async def set_io_function_toggle(
        self,
        endpoint_descriptor: int,
        *,
        io_port_number: int,
        alarm_type: int,
        event: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Toggle I/O function of an endpoint. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_io_function_toggle,
            None,
            {
                "endpoint_descriptor": endpoint_descriptor,
                "io_port_number": io_port_number,
                "alarm_type": alarm_type,
                "event": event,
            },
            request_options,
        )

    async def remove_io_function(
        self, endpoint_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the I/O function of an endpoint. Access: admin."""
        await self._run(OPS.remove_io_function, None, {"endpoint_descriptor": endpoint_descriptor}, request_options)

    async def get_io_configuration(
        self, endpoint_descriptor: int, *, request_options: RequestOptions | None = None
    ) -> GetIoConfigurationResult:
        """Get the I/O function configuration of an endpoint. Access: admin."""
        return await self._run(
            OPS.get_io_configuration, None, {"endpoint_descriptor": endpoint_descriptor}, request_options
        )
