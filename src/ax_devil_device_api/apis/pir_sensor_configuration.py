# GENERATED from specs/apis/network-video/pir-sensor-configuration.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List PIR (passive infrared) sensors and get/set their sensitivity.

Docs: https://developer.axis.com/vapix/network-video/pir-sensor-configuration/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Sensitivity = Annotated[float, Field(ge=0, le=1)]


class Sensor(Model):
    id: int
    """The sensor identifier."""
    sensitivity_configurable: bool = Field(
        validation_alias="sensitivityConfigurable", serialization_alias="sensitivityConfigurable"
    )
    """Whether the sensor sensitivity can be configured."""
    sensitivity: Sensitivity | None = None
    """Configured sensitivity. Only present when the sensitivity is configurable."""


class SensorList(Model):
    sensors: list[Sensor]


class SensorIdRequest(Model):
    id: int
    """The sensor identifier."""


class SensitivityResult(Model):
    sensitivity: Sensitivity


class SetSensitivityRequest(Model):
    id: int
    """The sensor to configure."""
    sensitivity: Sensitivity
    """The sensitivity to set, 0 to 1. The resulting value may be rounded; read it back with ``get_sensitivity`` or ``list_sensors``."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/pirsensor.cgi"

INFO = ApiInfo(
    id="pir-sensor-configuration",
    name="PIR sensor configuration",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("pir-sensor-configuration"),),
    docs=("https://developer.axis.com/vapix/network-video/pir-sensor-configuration/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
    },
)


class OPS:
    list_sensors = Operation(
        INFO, "list_sensors", JsonRpcBinding("listSensors", PATH), result=SensorList, access="operator", effect="read"
    )
    get_sensitivity = Operation(
        INFO,
        "get_sensitivity",
        JsonRpcBinding("getSensitivity", PATH),
        params=SensorIdRequest,
        result=SensitivityResult,
        access="operator",
        effect="read",
        errors={
            2200: ErrorCode("Invalid sensor id.", "invalid_argument"),
            2201: ErrorCode("Sensor does not have configurable sensitivity.", "unsupported"),
        },
    )
    set_sensitivity = Operation(
        INFO,
        "set_sensitivity",
        JsonRpcBinding("setSensitivity", PATH),
        params=SetSensitivityRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            2200: ErrorCode("Invalid sensor id.", "invalid_argument"),
            2201: ErrorCode("Sensor does not have configurable sensitivity.", "unsupported"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class PirSensorConfigurationApi(SyncApi):
    """PIR sensor configuration (``pir-sensor-configuration``, version 1)."""

    INFO = INFO

    def list_sensors(self, *, request_options: RequestOptions | None = None) -> SensorList:
        """List all PIR sensors and whether their sensitivity is configurable. Access: operator."""
        return self._run(OPS.list_sensors, None, {}, request_options)

    def get_sensitivity(self, id: int, *, request_options: RequestOptions | None = None) -> SensitivityResult:
        """Get the sensitivity configured for a sensor. Access: operator."""
        return self._run(OPS.get_sensitivity, None, {"id": id}, request_options)

    def set_sensitivity(
        self, id: int, sensitivity: Sensitivity, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the sensitivity of a sensor. Changes only the fields given. Access: operator."""
        self._run(OPS.set_sensitivity, None, {"id": id, "sensitivity": sensitivity}, request_options)


class AsyncPirSensorConfigurationApi(AsyncApi):
    """PIR sensor configuration (``pir-sensor-configuration``, version 1)."""

    INFO = INFO

    async def list_sensors(self, *, request_options: RequestOptions | None = None) -> SensorList:
        """List all PIR sensors and whether their sensitivity is configurable. Access: operator."""
        return await self._run(OPS.list_sensors, None, {}, request_options)

    async def get_sensitivity(self, id: int, *, request_options: RequestOptions | None = None) -> SensitivityResult:
        """Get the sensitivity configured for a sensor. Access: operator."""
        return await self._run(OPS.get_sensitivity, None, {"id": id}, request_options)

    async def set_sensitivity(
        self, id: int, sensitivity: Sensitivity, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the sensitivity of a sensor. Changes only the fields given. Access: operator."""
        await self._run(OPS.set_sensitivity, None, {"id": id, "sensitivity": sensitivity}, request_options)
