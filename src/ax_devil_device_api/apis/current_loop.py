# GENERATED from specs/apis/network-video/current-loop.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read 4–20 mA current loop sensors, configure scaling/thresholds, monitor live status and receive alarm/fault/metadata events.

Docs: https://developer.axis.com/vapix/network-video/current-loop-input-api/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

SensorId = str
LoopState = Literal["OPEN_CIRCUIT", "UNDER_RANGE", "OK", "OVER_RANGE", "SHORT_CIRCUIT"]
ThresholdState = Literal[
    "BELOW_LOWER_CRITICAL", "BELOW_LOWER_WARNING", "OK", "ABOVE_UPPER_WARNING", "ABOVE_UPPER_CRITICAL"
]


class Configuration(Model):
    """Parameters used to convert loop current into physical values in engineering units, and to define alarm thresholds. The thresholds must satisfy minThresholdCritical <= minThresholdWarning <= maxThresholdWarning <= maxThresholdCritical."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    sensor_name: str | None = Field(default=None, validation_alias="sensorName", serialization_alias="sensorName")
    enabled: bool | None = None
    engineering_unit: str | None = Field(
        default=None, validation_alias="engineeringUnit", serialization_alias="engineeringUnit"
    )
    """Engineering unit of the physical value, for example a degree sign and C."""
    min_physical_value: float | None = Field(
        default=None, validation_alias="minPhysicalValue", serialization_alias="minPhysicalValue"
    )
    """Expected physical value at 4 mA."""
    max_physical_value: float | None = Field(
        default=None, validation_alias="maxPhysicalValue", serialization_alias="maxPhysicalValue"
    )
    """Expected physical value at 20 mA."""
    min_threshold_critical: float | None = Field(
        default=None, validation_alias="minThresholdCritical", serialization_alias="minThresholdCritical"
    )
    min_threshold_warning: float | None = Field(
        default=None, validation_alias="minThresholdWarning", serialization_alias="minThresholdWarning"
    )
    max_threshold_warning: float | None = Field(
        default=None, validation_alias="maxThresholdWarning", serialization_alias="maxThresholdWarning"
    )
    max_threshold_critical: float | None = Field(
        default=None, validation_alias="maxThresholdCritical", serialization_alias="maxThresholdCritical"
    )


class Status(Model):
    """Live sensor data and diagnostic results, updated every 100 ms. loopState and thresholdState can lag behind the values by a validation delay."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    current_value: float | None = Field(
        default=None, validation_alias="currentValue", serialization_alias="currentValue"
    )
    """Loop current in mA."""
    physical_value: float | None = Field(
        default=None, validation_alias="physicalValue", serialization_alias="physicalValue"
    )
    """Current converted to the engineering unit: minPhysicalValue + ((currentValue - 4) * (maxPhysicalValue - minPhysicalValue)) / 16."""
    raw_value: int | None = Field(default=None, validation_alias="rawValue", serialization_alias="rawValue")
    loop_state: LoopState | None = Field(default=None, validation_alias="loopState", serialization_alias="loopState")
    threshold_state: ThresholdState | None = Field(
        default=None, validation_alias="thresholdState", serialization_alias="thresholdState"
    )


class CurrentLoop(Model):
    """The whole API tree."""

    configurations: list[Configuration] | None = None
    status: list[Status] | None = None


class UpdateConfigurationRequest(Model):
    """Arguments of ``update_configuration``. Only the given fields change."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    sensor_name: str | None = Field(default=None, validation_alias="sensorName", serialization_alias="sensorName")
    enabled: bool | None = None
    engineering_unit: str | None = Field(
        default=None, validation_alias="engineeringUnit", serialization_alias="engineeringUnit"
    )
    min_physical_value: float | None = Field(
        default=None, validation_alias="minPhysicalValue", serialization_alias="minPhysicalValue"
    )
    max_physical_value: float | None = Field(
        default=None, validation_alias="maxPhysicalValue", serialization_alias="maxPhysicalValue"
    )
    min_threshold_critical: float | None = Field(
        default=None, validation_alias="minThresholdCritical", serialization_alias="minThresholdCritical"
    )
    min_threshold_warning: float | None = Field(
        default=None, validation_alias="minThresholdWarning", serialization_alias="minThresholdWarning"
    )
    max_threshold_warning: float | None = Field(
        default=None, validation_alias="maxThresholdWarning", serialization_alias="maxThresholdWarning"
    )
    max_threshold_critical: float | None = Field(
        default=None, validation_alias="maxThresholdCritical", serialization_alias="maxThresholdCritical"
    )

    @classmethod
    def from_current(cls, configuration: Configuration) -> UpdateConfigurationRequest:
        """A request that rewrites ``configuration`` unchanged: copy it, edit fields, send it back."""
        data = configuration.request_data()
        return cls.from_response_data(data)


class SensorIdRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")


class SetConfigurationEngineeringUnitRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    engineering_unit: str = Field(validation_alias="engineeringUnit", serialization_alias="engineeringUnit")


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/current-loop/v1"

INFO = ApiInfo(
    id="current-loop",
    name="Current loop input API",
    family=Family.DCA,
    discovery=(DcaDiscovery("current-loop", "v1"),),
    docs=("https://developer.axis.com/vapix/network-video/current-loop-input-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=CurrentLoop, access="admin", effect="read")
    list_configurations = Operation(
        INFO,
        "list_configurations",
        DcaBinding("GET", f"{ROOT}/configurations"),
        result=list[Configuration],
        access="admin",
        effect="read",
    )
    get_configuration = Operation(
        INFO,
        "get_configuration",
        DcaBinding("GET", f"{ROOT}/configurations/{{sensorId}}"),
        params=SensorIdRequest,
        result=Configuration,
        access="admin",
        effect="read",
    )
    update_configuration = Operation(
        INFO,
        "update_configuration",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensorId}}", body="object"),
        params=UpdateConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_configuration_engineering_unit = Operation(
        INFO,
        "get_configuration_engineering_unit",
        DcaBinding("GET", f"{ROOT}/configurations/{{sensorId}}/engineeringUnit"),
        params=SensorIdRequest,
        result=str,
        access="admin",
        effect="read",
    )
    set_configuration_engineering_unit = Operation(
        INFO,
        "set_configuration_engineering_unit",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensorId}}/engineeringUnit", body="value", body_field="engineeringUnit"
        ),
        params=SetConfigurationEngineeringUnitRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_status = Operation(
        INFO, "list_status", DcaBinding("GET", f"{ROOT}/status"), result=list[Status], access="admin", effect="read"
    )
    get_status = Operation(
        INFO,
        "get_status",
        DcaBinding("GET", f"{ROOT}/status/{{sensorId}}"),
        params=SensorIdRequest,
        result=Status,
        access="admin",
        effect="read",
    )
    get_status_physical_value = Operation(
        INFO,
        "get_status_physical_value",
        DcaBinding("GET", f"{ROOT}/status/{{sensorId}}/physicalValue"),
        params=SensorIdRequest,
        result=float,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class CurrentLoopApi(SyncApi):
    """Current loop input API (``current-loop``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> CurrentLoop:
        """The whole tree, with all configurations and the live status. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_configurations(self, *, request_options: RequestOptions | None = None) -> list[Configuration]:
        """List the sensor configurations. Access: admin."""
        return self._run(OPS.list_configurations, None, {}, request_options)

    def get_configuration(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> Configuration:
        """One sensor configuration. Access: admin."""
        return self._run(OPS.get_configuration, None, {"sensor_id": sensor_id}, request_options)

    @overload
    def update_configuration(
        self, request: UpdateConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_configuration(
        self,
        /,
        *,
        sensor_id: SensorId,
        sensor_name: str | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        engineering_unit: str | MISSING = MISSING,
        min_physical_value: float | MISSING = MISSING,
        max_physical_value: float | MISSING = MISSING,
        min_threshold_critical: float | MISSING = MISSING,
        min_threshold_warning: float | MISSING = MISSING,
        max_threshold_warning: float | MISSING = MISSING,
        max_threshold_critical: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_configuration(
        self,
        request: UpdateConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change a sensor configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.update_configuration, request, kwargs, request_options)

    def get_configuration_engineering_unit(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> str:
        """The engineering unit of a sensor. Access: admin."""
        return self._run(OPS.get_configuration_engineering_unit, None, {"sensor_id": sensor_id}, request_options)

    def set_configuration_engineering_unit(
        self, sensor_id: SensorId, *, engineering_unit: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the engineering unit of a sensor. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_engineering_unit,
            None,
            {"sensor_id": sensor_id, "engineering_unit": engineering_unit},
            request_options,
        )

    def list_status(self, *, request_options: RequestOptions | None = None) -> list[Status]:
        """Live status of all sensors. Access: admin."""
        return self._run(OPS.list_status, None, {}, request_options)

    def get_status(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> Status:
        """Live status of one sensor. Access: admin."""
        return self._run(OPS.get_status, None, {"sensor_id": sensor_id}, request_options)

    def get_status_physical_value(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> float:
        """The live physical value of one sensor. Access: admin."""
        return self._run(OPS.get_status_physical_value, None, {"sensor_id": sensor_id}, request_options)


class AsyncCurrentLoopApi(AsyncApi):
    """Current loop input API (``current-loop``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> CurrentLoop:
        """The whole tree, with all configurations and the live status. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_configurations(self, *, request_options: RequestOptions | None = None) -> list[Configuration]:
        """List the sensor configurations. Access: admin."""
        return await self._run(OPS.list_configurations, None, {}, request_options)

    async def get_configuration(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> Configuration:
        """One sensor configuration. Access: admin."""
        return await self._run(OPS.get_configuration, None, {"sensor_id": sensor_id}, request_options)

    @overload
    async def update_configuration(
        self, request: UpdateConfigurationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_configuration(
        self,
        /,
        *,
        sensor_id: SensorId,
        sensor_name: str | MISSING = MISSING,
        enabled: bool | MISSING = MISSING,
        engineering_unit: str | MISSING = MISSING,
        min_physical_value: float | MISSING = MISSING,
        max_physical_value: float | MISSING = MISSING,
        min_threshold_critical: float | MISSING = MISSING,
        min_threshold_warning: float | MISSING = MISSING,
        max_threshold_warning: float | MISSING = MISSING,
        max_threshold_critical: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_configuration(
        self,
        request: UpdateConfigurationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Change a sensor configuration. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_configuration, request, kwargs, request_options)

    async def get_configuration_engineering_unit(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> str:
        """The engineering unit of a sensor. Access: admin."""
        return await self._run(OPS.get_configuration_engineering_unit, None, {"sensor_id": sensor_id}, request_options)

    async def set_configuration_engineering_unit(
        self, sensor_id: SensorId, *, engineering_unit: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the engineering unit of a sensor. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_engineering_unit,
            None,
            {"sensor_id": sensor_id, "engineering_unit": engineering_unit},
            request_options,
        )

    async def list_status(self, *, request_options: RequestOptions | None = None) -> list[Status]:
        """Live status of all sensors. Access: admin."""
        return await self._run(OPS.list_status, None, {}, request_options)

    async def get_status(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> Status:
        """Live status of one sensor. Access: admin."""
        return await self._run(OPS.get_status, None, {"sensor_id": sensor_id}, request_options)

    async def get_status_physical_value(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> float:
        """The live physical value of one sensor. Access: admin."""
        return await self._run(OPS.get_status_physical_value, None, {"sensor_id": sensor_id}, request_options)
