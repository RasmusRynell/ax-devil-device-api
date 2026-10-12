# GENERATED. Do not edit.
# (Hand-written target for the generator; see docs/design.md section 5.)
"""Namespaces exposing every generated API as ``device.apis.<name>``."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..device import AsyncDevice, Device
    from .analytics_mqtt import AnalyticsMqttApi, AsyncAnalyticsMqttApi
    from .mqtt_client import AsyncMqttClientApi, MqttClientApi
    from .parameter_management import AsyncParameterManagementApi, ParameterManagementApi


class Apis:
    """Every API, for a blocking ``Device``. Modules are imported on first use."""

    def __init__(self, device: Device) -> None:
        self._device = device

    @cached_property
    def analytics_mqtt(self) -> AnalyticsMqttApi:
        from .analytics_mqtt import AnalyticsMqttApi

        return self._device.api(AnalyticsMqttApi)

    @cached_property
    def mqtt_client(self) -> MqttClientApi:
        from .mqtt_client import MqttClientApi

        return self._device.api(MqttClientApi)

    @cached_property
    def parameter_management(self) -> ParameterManagementApi:
        from .parameter_management import ParameterManagementApi

        return self._device.api(ParameterManagementApi)


class AsyncApis:
    """Every API, for an ``AsyncDevice``. Modules are imported on first use."""

    def __init__(self, device: AsyncDevice) -> None:
        self._device = device

    @cached_property
    def analytics_mqtt(self) -> AsyncAnalyticsMqttApi:
        from .analytics_mqtt import AsyncAnalyticsMqttApi

        return self._device.api(AsyncAnalyticsMqttApi)

    @cached_property
    def mqtt_client(self) -> AsyncMqttClientApi:
        from .mqtt_client import AsyncMqttClientApi

        return self._device.api(AsyncMqttClientApi)

    @cached_property
    def parameter_management(self) -> AsyncParameterManagementApi:
        from .parameter_management import AsyncParameterManagementApi

        return self._device.api(AsyncParameterManagementApi)
