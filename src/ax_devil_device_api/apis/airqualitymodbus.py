# GENERATED from specs/apis/device-configuration/airqualitymodbus-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The VAPIX® Air quality Modbus API enables applications and users to configure Modbus parameters(such as service status and port settings) for the Air quality...

Docs: https://developer.axis.com/vapix/device-configuration/environmental-sensor/air-quality-modbus-api/
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ModbusPort = Annotated[int, Field(ge=1024, le=65535)]
SensorId = Annotated[str, Field(min_length=1, pattern=r"^[1-9]\d*|0$")]


class Configuration(Model):
    """Configuration of air quality modbus"""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"sensor_id"})
    modbus_enable: bool | None = Field(
        default=None, validation_alias="modbusEnable", serialization_alias="modbusEnable"
    )
    """Modbus enable"""
    modbus_port: ModbusPort | None = Field(
        default=None, validation_alias="modbusPort", serialization_alias="modbusPort"
    )
    """Modbus port"""
    sensor_id: SensorId | None = Field(default=None, validation_alias="sensorId", serialization_alias="sensorId")
    """Sensor ID"""


class AirQualityModbus(Model):
    """The whole API tree."""

    configurations: list[Configuration] | None = None


class UpdateConfigurationRequest(Model):
    """Arguments of ``update_configuration``."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    modbus_enable: bool | None = Field(
        default=None, validation_alias="modbusEnable", serialization_alias="modbusEnable"
    )
    """Modbus enable"""
    modbus_port: ModbusPort | None = Field(
        default=None, validation_alias="modbusPort", serialization_alias="modbusPort"
    )
    """Modbus port"""


class ConfigurationSensorIdRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")


class SetConfigurationModbusEnableRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    modbus_enable: bool = Field(validation_alias="modbusEnable", serialization_alias="modbusEnable")
    """Modbus enable"""


class SetConfigurationModbusPortRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    modbus_port: ModbusPort = Field(validation_alias="modbusPort", serialization_alias="modbusPort")
    """Modbus port"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/airqualitymodbus/v1"

INFO = ApiInfo(
    id="airqualitymodbus-config",
    name="Air quality Modbus",
    family=Family.DCA,
    discovery=(DcaDiscovery("airqualitymodbus", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/environmental-sensor/air-quality-modbus-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=AirQualityModbus, access="viewer", effect="read"
    )
    list_configurations = Operation(
        INFO,
        "list_configurations",
        DcaBinding("GET", f"{ROOT}/configurations"),
        result=list[Configuration],
        access="viewer",
        effect="read",
    )
    get_configuration = Operation(
        INFO,
        "get_configuration",
        DcaBinding("GET", f"{ROOT}/configurations/{{sensorId}}"),
        params=ConfigurationSensorIdRequest,
        result=Configuration,
        access="viewer",
        effect="read",
    )
    get_configuration_modbus_enable = Operation(
        INFO,
        "get_configuration_modbus_enable",
        DcaBinding("GET", f"{ROOT}/configurations/{{sensorId}}/modbusEnable"),
        params=ConfigurationSensorIdRequest,
        result=bool,
        access="viewer",
        effect="read",
    )
    get_configuration_modbus_port = Operation(
        INFO,
        "get_configuration_modbus_port",
        DcaBinding("GET", f"{ROOT}/configurations/{{sensorId}}/modbusPort"),
        params=ConfigurationSensorIdRequest,
        result=ModbusPort,
        access="viewer",
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
    set_configuration_modbus_enable = Operation(
        INFO,
        "set_configuration_modbus_enable",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensorId}}/modbusEnable", body="value", body_field="modbusEnable"
        ),
        params=SetConfigurationModbusEnableRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_modbus_port = Operation(
        INFO,
        "set_configuration_modbus_port",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensorId}}/modbusPort", body="value", body_field="modbusPort"),
        params=SetConfigurationModbusPortRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class AirQualityModbusApi(SyncApi):
    """Air quality Modbus (``airqualitymodbus-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> AirQualityModbus:
        """All data of the Air quality Modbus API. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_configurations(self, *, request_options: RequestOptions | None = None) -> list[Configuration]:
        """List the configurations. Access: viewer."""
        return self._run(OPS.list_configurations, None, {}, request_options)

    def get_configuration(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> Configuration:
        """Get one configuration. Access: viewer."""
        return self._run(OPS.get_configuration, None, {"sensor_id": sensor_id}, request_options)

    def get_configuration_modbus_enable(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> bool:
        """Get the modbus enable of a configuration. Access: viewer."""
        return self._run(OPS.get_configuration_modbus_enable, None, {"sensor_id": sensor_id}, request_options)

    def get_configuration_modbus_port(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> ModbusPort:
        """Get the modbus port of a configuration. Access: viewer."""
        return self._run(OPS.get_configuration_modbus_port, None, {"sensor_id": sensor_id}, request_options)

    def update_configuration(
        self,
        sensor_id: SensorId,
        *,
        modbus_enable: bool | MISSING = MISSING,
        modbus_port: ModbusPort | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.update_configuration,
            None,
            {"sensor_id": sensor_id, "modbus_enable": modbus_enable, "modbus_port": modbus_port},
            request_options,
        )

    def set_configuration_modbus_enable(
        self, sensor_id: SensorId, *, modbus_enable: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the modbus enable of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_modbus_enable,
            None,
            {"sensor_id": sensor_id, "modbus_enable": modbus_enable},
            request_options,
        )

    def set_configuration_modbus_port(
        self, sensor_id: SensorId, *, modbus_port: ModbusPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the modbus port of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_modbus_port,
            None,
            {"sensor_id": sensor_id, "modbus_port": modbus_port},
            request_options,
        )


class AsyncAirQualityModbusApi(AsyncApi):
    """Air quality Modbus (``airqualitymodbus-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> AirQualityModbus:
        """All data of the Air quality Modbus API. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_configurations(self, *, request_options: RequestOptions | None = None) -> list[Configuration]:
        """List the configurations. Access: viewer."""
        return await self._run(OPS.list_configurations, None, {}, request_options)

    async def get_configuration(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> Configuration:
        """Get one configuration. Access: viewer."""
        return await self._run(OPS.get_configuration, None, {"sensor_id": sensor_id}, request_options)

    async def get_configuration_modbus_enable(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> bool:
        """Get the modbus enable of a configuration. Access: viewer."""
        return await self._run(OPS.get_configuration_modbus_enable, None, {"sensor_id": sensor_id}, request_options)

    async def get_configuration_modbus_port(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> ModbusPort:
        """Get the modbus port of a configuration. Access: viewer."""
        return await self._run(OPS.get_configuration_modbus_port, None, {"sensor_id": sensor_id}, request_options)

    async def update_configuration(
        self,
        sensor_id: SensorId,
        *,
        modbus_enable: bool | MISSING = MISSING,
        modbus_port: ModbusPort | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.update_configuration,
            None,
            {"sensor_id": sensor_id, "modbus_enable": modbus_enable, "modbus_port": modbus_port},
            request_options,
        )

    async def set_configuration_modbus_enable(
        self, sensor_id: SensorId, *, modbus_enable: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the modbus enable of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_modbus_enable,
            None,
            {"sensor_id": sensor_id, "modbus_enable": modbus_enable},
            request_options,
        )

    async def set_configuration_modbus_port(
        self, sensor_id: SensorId, *, modbus_port: ModbusPort, request_options: RequestOptions | None = None
    ) -> None:
        """Set the modbus port of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_modbus_port,
            None,
            {"sensor_id": sensor_id, "modbus_port": modbus_port},
            request_options,
        )
