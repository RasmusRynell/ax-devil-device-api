# GENERATED from specs/apis/network-video/gpio-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List, read and configure I/O ports, including supervised inputs and relay outputs, through the axgpio service.

Docs: https://developer.axis.com/vapix/network-video/input-and-outputs/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ServiceCapabilities(Model):
    max_limit: int = Field(validation_alias="MaxLimit", serialization_alias="MaxLimit")
    """Maximum number of entries returned by GetPortList and GetPort."""


PortId = Annotated[str, Field(min_length=1, max_length=64)]
PortMode = Annotated[str, Field(min_length=1, max_length=32)]
PortState = Annotated[str, Field(min_length=1, max_length=32)]
ActiveState = str


class SupervisedInputCapabilities(Model):
    max_number_of_ranges: int = Field(validation_alias="MaxNumberOfRanges", serialization_alias="MaxNumberOfRanges")
    """The maximum number of SupervisionRange structures supported by the supervised input."""
    min_voltage_range: str = Field(validation_alias="MinVoltageRange", serialization_alias="MinVoltageRange")
    """The minimum voltage span that is viable to use with respect to noise and ADC resolution. Unit: mV."""
    min_voltage_level: str = Field(validation_alias="MinVoltageLevel", serialization_alias="MinVoltageLevel")
    """The minimum voltage that can be specified in a SupervisionRange. Unit: mV."""
    max_voltage_level: str = Field(validation_alias="MaxVoltageLevel", serialization_alias="MaxVoltageLevel")
    """The maximum voltage that can be specified in a SupervisionRange. Unit: mV."""


class Properties(Model):
    """Input or output properties of a port."""

    nice_name: str | None = Field(default=None, validation_alias="NiceName", serialization_alias="NiceName")
    """The port's nice name."""
    active_state: ActiveState | None = Field(
        default=None, validation_alias="ActiveState", serialization_alias="ActiveState"
    )
    """Specifies when the port is active."""


class SupervisionRange(Model):
    state: PortState = Field(validation_alias="State", serialization_alias="State")
    """Behavior may change; assume any string."""
    lower_limit: str = Field(validation_alias="LowerLimit", serialization_alias="LowerLimit")
    """Lower voltage limit (inclusive), mV."""
    upper_limit: str = Field(validation_alias="UpperLimit", serialization_alias="UpperLimit")
    """Upper voltage limit (exclusive), mV."""


class SupervisedInput(Model):
    """Configuration for a supervised input."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"analog_level", "capabilities"})
    triggers: list[SupervisionRange] = Field(validation_alias="Triggers", serialization_alias="Triggers")
    """User-defined ranges for the supervised input."""
    analog_level: int | None = Field(default=None, validation_alias="AnalogLevel", serialization_alias="AnalogLevel")
    """The current analog voltage at the input pin. Unit: mV."""
    capabilities: SupervisedInputCapabilities | None = Field(
        default=None, validation_alias="Capabilities", serialization_alias="Capabilities"
    )
    """The supervised input's capabilities."""


class Port(Model):
    """The configuration of a port. Only PortId and the fields to modify are needed when configuring a port."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"current_state", "supported_modes"})
    port_id: PortId = Field(validation_alias="PortId", serialization_alias="PortId")
    """The port identifier."""
    supported_modes: list[PortMode] | None = Field(
        default=None, validation_alias="SupportedModes", serialization_alias="SupportedModes"
    )
    """Supported port modes."""
    port_usage: str | None = Field(default=None, validation_alias="PortUsage", serialization_alias="PortUsage")
    """String describing the port usage."""
    current_mode: PortMode | None = Field(
        default=None, validation_alias="CurrentMode", serialization_alias="CurrentMode"
    )
    """The port's current mode."""
    current_state: PortState | None = Field(
        default=None, validation_alias="CurrentState", serialization_alias="CurrentState"
    )
    """The port's current state. Use Active to set the port active or inactive."""
    active: bool | None = Field(default=None, validation_alias="Active", serialization_alias="Active")
    """true when the port is active."""
    input_properties: Properties | None = Field(
        default=None, validation_alias="InputProperties", serialization_alias="InputProperties"
    )
    """The port's input properties."""
    output_properties: Properties | None = Field(
        default=None, validation_alias="OutputProperties", serialization_alias="OutputProperties"
    )
    """The port's output properties."""
    supervised_input: SupervisedInput | None = Field(
        default=None, validation_alias="SupervisedInput", serialization_alias="SupervisedInput"
    )
    """The configuration used when the port is a supervised input."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The supported service capabilities."""


class GetPortListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of items to return. Actual number may be less; if omitted determined by ServiceCapabilities."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Internal reference of the first item to return; use NextStartReference from the previous call; do not reuse."""


class GetPortListResult(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """Reference to use as StartReference in the next call. Returned if the response does not include all available Port items."""
    port: list[Port] | None = Field(default=None, validation_alias="Port", serialization_alias="Port")
    """The returned Port items."""


class GetPortRequest(Model):
    port_id: list[PortId] = Field(validation_alias="PortId", serialization_alias="PortId")
    """List of port identifiers; unresolved IDs are ignored."""


class GetPortResult(Model):
    port: list[Port] | None = Field(default=None, validation_alias="Port", serialization_alias="Port")
    """The returned Port items."""


class SetPortRequest(Model):
    port: list[Port] = Field(validation_alias="Port", serialization_alias="Port")
    """List of Port items; omitted fields keep their current values."""


class SetPortResult(Model):
    port_id: list[PortId] = Field(validation_alias="PortId", serialization_alias="PortId")
    """PortIds of the updated items."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/axgpio"

INFO = ApiInfo(
    id="gpio-service",
    name="General purpose I/O service",
    family=Family.SERVICE_JSON,
    discovery=(ParamDiscovery("Properties.API.GPIO.Version", "1.0", ">="),),
    docs=("https://developer.axis.com/vapix/network-video/input-and-outputs/",),
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "axgpio:GetServiceCapabilities", auth="if_challenged"),
        result=GetServiceCapabilitiesResult,
        access="anonymous",
        effect="read",
    )
    get_port_list = Operation(
        INFO,
        "get_port_list",
        ServiceJsonBinding(PATH, "axgpio:GetPortList"),
        params=GetPortListRequest,
        result=GetPortListResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode("StartReference is invalid or has timed out.", "invalid_argument"),
            "ter:InvalidArgVal": ErrorCode("The request has an invalid argument value.", "invalid_argument"),
        },
    )
    get_port = Operation(
        INFO,
        "get_port",
        ServiceJsonBinding(PATH, "axgpio:GetPort"),
        params=GetPortRequest,
        result=GetPortResult,
        access="admin",
        effect="read",
        errors={"ter:TooManyItems": ErrorCode("Too many items were requested.", "invalid_argument")},
    )
    set_port = Operation(
        INFO,
        "set_port",
        ServiceJsonBinding(PATH, "axgpio:SetPort"),
        params=SetPortRequest,
        result=SetPortResult,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:InvalidArgs": ErrorCode("The data in the request is missing.", "invalid_argument"),
            "ter:InvalidArgVal": ErrorCode("The data in the request is invalid.", "invalid_argument"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class GpioServiceApi(SyncApi):
    """General purpose I/O service (``gpio-service``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Retrieve the capabilities supported by the service. Access: anonymous."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def get_port_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetPortListResult:
        """List the product Port data structures (paged). Access: admin."""
        return self._run(OPS.get_port_list, None, {"limit": limit, "start_reference": start_reference}, request_options)

    def get_port(self, *, port_id: list[PortId], request_options: RequestOptions | None = None) -> GetPortResult:
        """List specified Port data structures by PortId. Access: admin."""
        return self._run(OPS.get_port, None, {"port_id": port_id}, request_options)

    @overload
    def set_port(
        self, request: SetPortRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetPortResult: ...
    @overload
    def set_port(self, /, *, port: list[Port], request_options: RequestOptions | None = None) -> SetPortResult: ...
    def set_port(
        self, request: SetPortRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetPortResult:
        """Update one or more Port data structures (all fields except PortId optional).

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return self._run(OPS.set_port, request, kwargs, request_options)


class AsyncGpioServiceApi(AsyncApi):
    """General purpose I/O service (``gpio-service``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Retrieve the capabilities supported by the service. Access: anonymous."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def get_port_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> GetPortListResult:
        """List the product Port data structures (paged). Access: admin."""
        return await self._run(
            OPS.get_port_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_port(self, *, port_id: list[PortId], request_options: RequestOptions | None = None) -> GetPortResult:
        """List specified Port data structures by PortId. Access: admin."""
        return await self._run(OPS.get_port, None, {"port_id": port_id}, request_options)

    @overload
    async def set_port(
        self, request: SetPortRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetPortResult: ...
    @overload
    async def set_port(
        self, /, *, port: list[Port], request_options: RequestOptions | None = None
    ) -> SetPortResult: ...
    async def set_port(
        self, request: SetPortRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> SetPortResult:
        """Update one or more Port data structures (all fields except PortId optional).

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return await self._run(OPS.set_port, request, kwargs, request_options)
