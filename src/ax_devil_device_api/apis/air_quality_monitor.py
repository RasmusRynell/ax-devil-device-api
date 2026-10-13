# GENERATED from specs/apis/device-configuration/airqualitymonitor-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read and configure air quality sensors, their limits and dashboard, and query their history.

Docs: https://developer.axis.com/vapix/device-configuration/environmental-sensor/air-quality-api/
"""

from __future__ import annotations

from typing import Any, ClassVar, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

CloudMetadataFrequency = int


class DashboardItems(Model):
    """Which measurements the dashboard shows or hides."""

    hidden: list[str] | None = None
    visible: list[str] | None = None


Limit = float
SensorId = str
StorageMode = int
TemperatureScale = str
ValidationPeriod = int
VapeSensitivity = int


class Configuration(Model):
    """Configuration of air quality monitor"""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"sensor_id"})
    cloud_metadata_enable: bool | None = Field(
        default=None, validation_alias="cloudMetadataEnable", serialization_alias="cloudMetadataEnable"
    )
    """Cloud metadata enable"""
    cloud_metadata_frequency: CloudMetadataFrequency | None = Field(
        default=None, validation_alias="cloudMetadataFrequency", serialization_alias="cloudMetadataFrequency"
    )
    """Cloud metadata frequency"""
    dashboard_items: DashboardItems | None = Field(
        default=None, validation_alias="dashboardItems", serialization_alias="dashboardItems"
    )
    """Dashboard items"""
    dashboard_title: str | None = Field(
        default=None, validation_alias="dashboardTitle", serialization_alias="dashboardTitle"
    )
    """Dashboard title"""
    max_aqi: Limit | None = Field(default=None, validation_alias="maxAqi", serialization_alias="maxAqi")
    """Maximum AQI"""
    max_co2: Limit | None = Field(default=None, validation_alias="maxCo2", serialization_alias="maxCo2")
    """Maximum CO2"""
    max_humidity: Limit | None = Field(default=None, validation_alias="maxHumidity", serialization_alias="maxHumidity")
    """Maximum humidity"""
    max_nox: Limit | None = Field(default=None, validation_alias="maxNox", serialization_alias="maxNox")
    """Maximum NOx"""
    max_pm10p0: Limit | None = Field(default=None, validation_alias="maxPm10p0", serialization_alias="maxPm10p0")
    """Maximum PM10.0"""
    max_pm1p0: Limit | None = Field(default=None, validation_alias="maxPm1p0", serialization_alias="maxPm1p0")
    """Maximum PM1.0"""
    max_pm2p5: Limit | None = Field(default=None, validation_alias="maxPm2p5", serialization_alias="maxPm2p5")
    """Maximum PM2.5"""
    max_pm4p0: Limit | None = Field(default=None, validation_alias="maxPm4p0", serialization_alias="maxPm4p0")
    """Maximum PM4.0"""
    max_temperature: Limit | None = Field(
        default=None, validation_alias="maxTemperature", serialization_alias="maxTemperature"
    )
    """Maximum temperature"""
    max_voc: Limit | None = Field(default=None, validation_alias="maxVoc", serialization_alias="maxVoc")
    """Maximum VOC"""
    min_aqi: Limit | None = Field(default=None, validation_alias="minAqi", serialization_alias="minAqi")
    """Minimum AQI"""
    min_co2: Limit | None = Field(default=None, validation_alias="minCo2", serialization_alias="minCo2")
    """Minimum CO2"""
    min_humidity: Limit | None = Field(default=None, validation_alias="minHumidity", serialization_alias="minHumidity")
    """Minimum humidity"""
    min_nox: Limit | None = Field(default=None, validation_alias="minNox", serialization_alias="minNox")
    """Minimum NOx"""
    min_pm10p0: Limit | None = Field(default=None, validation_alias="minPm10p0", serialization_alias="minPm10p0")
    """Minimum PM10.0"""
    min_pm1p0: Limit | None = Field(default=None, validation_alias="minPm1p0", serialization_alias="minPm1p0")
    """Minimum PM1.0"""
    min_pm2p5: Limit | None = Field(default=None, validation_alias="minPm2p5", serialization_alias="minPm2p5")
    """Minimum PM2.5"""
    min_pm4p0: Limit | None = Field(default=None, validation_alias="minPm4p0", serialization_alias="minPm4p0")
    """Minimum PM4.0"""
    min_temperature: Limit | None = Field(
        default=None, validation_alias="minTemperature", serialization_alias="minTemperature"
    )
    """Minimum temperature"""
    min_voc: Limit | None = Field(default=None, validation_alias="minVoc", serialization_alias="minVoc")
    """Minimum VOC"""
    sensor_id: SensorId = Field(default_factory=not_sent, validation_alias="sensorId", serialization_alias="sensorId")
    """Sensor ID"""
    storage_enable: bool | None = Field(
        default=None, validation_alias="storageEnable", serialization_alias="storageEnable"
    )
    """Storage enable"""
    storage_mode: StorageMode | None = Field(
        default=None, validation_alias="storageMode", serialization_alias="storageMode"
    )
    """Storage mode"""
    temperature_scale: TemperatureScale | None = Field(
        default=None, validation_alias="temperatureScale", serialization_alias="temperatureScale"
    )
    """Temperature scale unit"""
    validation_period_aqi: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodAqi", serialization_alias="validationPeriodAqi"
    )
    """Validation period AQI"""
    validation_period_co2: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodCo2", serialization_alias="validationPeriodCo2"
    )
    """Validation period CO2"""
    validation_period_humidity: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodHumidity", serialization_alias="validationPeriodHumidity"
    )
    """Validation period humidity"""
    validation_period_nox: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodNox", serialization_alias="validationPeriodNox"
    )
    """Validation period NOx"""
    validation_period_pm10p0: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm10p0", serialization_alias="validationPeriodPm10p0"
    )
    """Validation period PM10.0"""
    validation_period_pm1p0: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm1p0", serialization_alias="validationPeriodPm1p0"
    )
    """Validation period PM1.0"""
    validation_period_pm2p5: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm2p5", serialization_alias="validationPeriodPm2p5"
    )
    """Validation period PM2.5"""
    validation_period_pm4p0: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm4p0", serialization_alias="validationPeriodPm4p0"
    )
    """Validation period PM4.0"""
    validation_period_temperature: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodTemperature", serialization_alias="validationPeriodTemperature"
    )
    """Validation period temperature"""
    validation_period_vaping: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodVaping", serialization_alias="validationPeriodVaping"
    )
    """Validation period vaping"""
    validation_period_voc: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodVoc", serialization_alias="validationPeriodVoc"
    )
    """Validation period VOC"""
    vape_sensitivity: VapeSensitivity | None = Field(
        default=None, validation_alias="vapeSensitivity", serialization_alias="vapeSensitivity"
    )
    """Vape sensitivity"""


class Sensor(Model):
    """Status of air quality sensor"""

    connected: bool | None = None
    """Sensor connection status"""
    default_sensor: bool | None = Field(
        default=None, validation_alias="defaultSensor", serialization_alias="defaultSensor"
    )
    """True if it's a default sensor"""
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    """Sensor ID"""
    type: str | None = None
    """Sensor type name"""


class AirQualityMonitor(Model):
    """The whole API tree."""

    configurations: list[Configuration] | None = None
    sensors: list[Sensor] | None = None


class UpdateConfigurationRequest(Model):
    """Arguments of ``update_configuration``."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    """Sensor ID"""
    cloud_metadata_enable: bool | None = Field(
        default=None, validation_alias="cloudMetadataEnable", serialization_alias="cloudMetadataEnable"
    )
    """Cloud metadata enable"""
    cloud_metadata_frequency: CloudMetadataFrequency | None = Field(
        default=None, validation_alias="cloudMetadataFrequency", serialization_alias="cloudMetadataFrequency"
    )
    """Cloud metadata frequency"""
    dashboard_items: DashboardItems | None = Field(
        default=None, validation_alias="dashboardItems", serialization_alias="dashboardItems"
    )
    """Dashboard items"""
    dashboard_title: str | None = Field(
        default=None, validation_alias="dashboardTitle", serialization_alias="dashboardTitle"
    )
    """Dashboard title"""
    max_aqi: Limit | None = Field(default=None, validation_alias="maxAqi", serialization_alias="maxAqi")
    """Maximum AQI"""
    max_co2: Limit | None = Field(default=None, validation_alias="maxCo2", serialization_alias="maxCo2")
    """Maximum CO2"""
    max_humidity: Limit | None = Field(default=None, validation_alias="maxHumidity", serialization_alias="maxHumidity")
    """Maximum humidity"""
    max_nox: Limit | None = Field(default=None, validation_alias="maxNox", serialization_alias="maxNox")
    """Maximum NOx"""
    max_pm10p0: Limit | None = Field(default=None, validation_alias="maxPm10p0", serialization_alias="maxPm10p0")
    """Maximum PM10.0"""
    max_pm1p0: Limit | None = Field(default=None, validation_alias="maxPm1p0", serialization_alias="maxPm1p0")
    """Maximum PM1.0"""
    max_pm2p5: Limit | None = Field(default=None, validation_alias="maxPm2p5", serialization_alias="maxPm2p5")
    """Maximum PM2.5"""
    max_pm4p0: Limit | None = Field(default=None, validation_alias="maxPm4p0", serialization_alias="maxPm4p0")
    """Maximum PM4.0"""
    max_temperature: Limit | None = Field(
        default=None, validation_alias="maxTemperature", serialization_alias="maxTemperature"
    )
    """Maximum temperature"""
    max_voc: Limit | None = Field(default=None, validation_alias="maxVoc", serialization_alias="maxVoc")
    """Maximum VOC"""
    min_aqi: Limit | None = Field(default=None, validation_alias="minAqi", serialization_alias="minAqi")
    """Minimum AQI"""
    min_co2: Limit | None = Field(default=None, validation_alias="minCo2", serialization_alias="minCo2")
    """Minimum CO2"""
    min_humidity: Limit | None = Field(default=None, validation_alias="minHumidity", serialization_alias="minHumidity")
    """Minimum humidity"""
    min_nox: Limit | None = Field(default=None, validation_alias="minNox", serialization_alias="minNox")
    """Minimum NOx"""
    min_pm10p0: Limit | None = Field(default=None, validation_alias="minPm10p0", serialization_alias="minPm10p0")
    """Minimum PM10.0"""
    min_pm1p0: Limit | None = Field(default=None, validation_alias="minPm1p0", serialization_alias="minPm1p0")
    """Minimum PM1.0"""
    min_pm2p5: Limit | None = Field(default=None, validation_alias="minPm2p5", serialization_alias="minPm2p5")
    """Minimum PM2.5"""
    min_pm4p0: Limit | None = Field(default=None, validation_alias="minPm4p0", serialization_alias="minPm4p0")
    """Minimum PM4.0"""
    min_temperature: Limit | None = Field(
        default=None, validation_alias="minTemperature", serialization_alias="minTemperature"
    )
    """Minimum temperature"""
    min_voc: Limit | None = Field(default=None, validation_alias="minVoc", serialization_alias="minVoc")
    """Minimum VOC"""
    storage_enable: bool | None = Field(
        default=None, validation_alias="storageEnable", serialization_alias="storageEnable"
    )
    """Storage enable"""
    storage_mode: StorageMode | None = Field(
        default=None, validation_alias="storageMode", serialization_alias="storageMode"
    )
    """Storage mode"""
    temperature_scale: TemperatureScale | None = Field(
        default=None, validation_alias="temperatureScale", serialization_alias="temperatureScale"
    )
    """Temperature scale unit"""
    validation_period_aqi: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodAqi", serialization_alias="validationPeriodAqi"
    )
    """Validation period AQI"""
    validation_period_co2: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodCo2", serialization_alias="validationPeriodCo2"
    )
    """Validation period CO2"""
    validation_period_humidity: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodHumidity", serialization_alias="validationPeriodHumidity"
    )
    """Validation period humidity"""
    validation_period_nox: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodNox", serialization_alias="validationPeriodNox"
    )
    """Validation period NOx"""
    validation_period_pm10p0: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm10p0", serialization_alias="validationPeriodPm10p0"
    )
    """Validation period PM10.0"""
    validation_period_pm1p0: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm1p0", serialization_alias="validationPeriodPm1p0"
    )
    """Validation period PM1.0"""
    validation_period_pm2p5: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm2p5", serialization_alias="validationPeriodPm2p5"
    )
    """Validation period PM2.5"""
    validation_period_pm4p0: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodPm4p0", serialization_alias="validationPeriodPm4p0"
    )
    """Validation period PM4.0"""
    validation_period_temperature: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodTemperature", serialization_alias="validationPeriodTemperature"
    )
    """Validation period temperature"""
    validation_period_vaping: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodVaping", serialization_alias="validationPeriodVaping"
    )
    """Validation period vaping"""
    validation_period_voc: ValidationPeriod | None = Field(
        default=None, validation_alias="validationPeriodVoc", serialization_alias="validationPeriodVoc"
    )
    """Validation period VOC"""
    vape_sensitivity: VapeSensitivity | None = Field(
        default=None, validation_alias="vapeSensitivity", serialization_alias="vapeSensitivity"
    )
    """Vape sensitivity"""

    @classmethod
    def from_current(cls, configuration: Configuration) -> UpdateConfigurationRequest:
        """A request that rewrites ``configuration`` unchanged: copy it, edit fields, send it back."""
        data = configuration.request_data(exclude={"sensor_id"})
        missing = [name for name in ("sensor_id",) if name not in data]
        if missing:
            raise ValueError(f"the current value has no {', '.join(missing)} to keep")
        return cls(**data)


MeasurementCategory = str


class HistoryDataResult(Model):
    """Historical measurements; measurement[i] was taken at timestamp[i]."""

    measurement: list[float] | None = None
    timestamp: list[int] | None = None


class VapingRecord(Model):
    """Times when vaping was detected."""

    timestamp: list[int] | None = None


class GetHistoryDataRequest(Model):
    """Arguments of ``get_history_data``."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    category: MeasurementCategory
    start_time: int = Field(validation_alias="startTime", serialization_alias="startTime")
    """Start of the period, Unix time in seconds."""
    end_time: int = Field(validation_alias="endTime", serialization_alias="endTime")
    """End of the period, Unix time in seconds."""


class GetVapingRecordRequest(Model):
    """Arguments of ``get_vaping_record``."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    start_time: int = Field(validation_alias="startTime", serialization_alias="startTime")
    """Start of the period, Unix time in seconds."""
    end_time: int = Field(validation_alias="endTime", serialization_alias="endTime")
    """End of the period, Unix time in seconds."""


class SensorIdRequest(Model):
    """Arguments of the per-sensor reads."""

    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")


class SetConfigurationCloudMetadataEnableRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    cloud_metadata_enable: bool = Field(
        validation_alias="cloudMetadataEnable", serialization_alias="cloudMetadataEnable"
    )
    """Cloud metadata enable"""


class SetConfigurationCloudMetadataFrequencyRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    cloud_metadata_frequency: CloudMetadataFrequency = Field(
        validation_alias="cloudMetadataFrequency", serialization_alias="cloudMetadataFrequency"
    )
    """Cloud metadata frequency"""


class SetConfigurationDashboardItemsRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    dashboard_items: DashboardItems = Field(validation_alias="dashboardItems", serialization_alias="dashboardItems")
    """Dashboard items"""


class SetConfigurationDashboardTitleRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    dashboard_title: str = Field(validation_alias="dashboardTitle", serialization_alias="dashboardTitle")
    """Dashboard title"""


class SetConfigurationMaxAqiRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_aqi: Limit = Field(validation_alias="maxAqi", serialization_alias="maxAqi")
    """Maximum AQI"""


class SetConfigurationMaxCo2Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_co2: Limit = Field(validation_alias="maxCo2", serialization_alias="maxCo2")
    """Maximum CO2"""


class SetConfigurationMaxHumidityRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_humidity: Limit = Field(validation_alias="maxHumidity", serialization_alias="maxHumidity")
    """Maximum humidity"""


class SetConfigurationMaxNoxRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_nox: Limit = Field(validation_alias="maxNox", serialization_alias="maxNox")
    """Maximum NOx"""


class SetConfigurationMaxPm10p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_pm10p0: Limit = Field(validation_alias="maxPm10p0", serialization_alias="maxPm10p0")
    """Maximum PM10.0"""


class SetConfigurationMaxPm1p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_pm1p0: Limit = Field(validation_alias="maxPm1p0", serialization_alias="maxPm1p0")
    """Maximum PM1.0"""


class SetConfigurationMaxPm2p5Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_pm2p5: Limit = Field(validation_alias="maxPm2p5", serialization_alias="maxPm2p5")
    """Maximum PM2.5"""


class SetConfigurationMaxPm4p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_pm4p0: Limit = Field(validation_alias="maxPm4p0", serialization_alias="maxPm4p0")
    """Maximum PM4.0"""


class SetConfigurationMaxTemperatureRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_temperature: Limit = Field(validation_alias="maxTemperature", serialization_alias="maxTemperature")
    """Maximum temperature"""


class SetConfigurationMaxVocRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    max_voc: Limit = Field(validation_alias="maxVoc", serialization_alias="maxVoc")
    """Maximum VOC"""


class SetConfigurationMinAqiRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_aqi: Limit = Field(validation_alias="minAqi", serialization_alias="minAqi")
    """Minimum AQI"""


class SetConfigurationMinCo2Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_co2: Limit = Field(validation_alias="minCo2", serialization_alias="minCo2")
    """Minimum CO2"""


class SetConfigurationMinHumidityRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_humidity: Limit = Field(validation_alias="minHumidity", serialization_alias="minHumidity")
    """Minimum humidity"""


class SetConfigurationMinNoxRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_nox: Limit = Field(validation_alias="minNox", serialization_alias="minNox")
    """Minimum NOx"""


class SetConfigurationMinPm10p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_pm10p0: Limit = Field(validation_alias="minPm10p0", serialization_alias="minPm10p0")
    """Minimum PM10.0"""


class SetConfigurationMinPm1p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_pm1p0: Limit = Field(validation_alias="minPm1p0", serialization_alias="minPm1p0")
    """Minimum PM1.0"""


class SetConfigurationMinPm2p5Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_pm2p5: Limit = Field(validation_alias="minPm2p5", serialization_alias="minPm2p5")
    """Minimum PM2.5"""


class SetConfigurationMinPm4p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_pm4p0: Limit = Field(validation_alias="minPm4p0", serialization_alias="minPm4p0")
    """Minimum PM4.0"""


class SetConfigurationMinTemperatureRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_temperature: Limit = Field(validation_alias="minTemperature", serialization_alias="minTemperature")
    """Minimum temperature"""


class SetConfigurationMinVocRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    min_voc: Limit = Field(validation_alias="minVoc", serialization_alias="minVoc")
    """Minimum VOC"""


class SetConfigurationStorageEnableRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    storage_enable: bool = Field(validation_alias="storageEnable", serialization_alias="storageEnable")
    """Storage enable"""


class SetConfigurationStorageModeRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    storage_mode: StorageMode = Field(validation_alias="storageMode", serialization_alias="storageMode")
    """Storage mode"""


class SetConfigurationTemperatureScaleRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    temperature_scale: TemperatureScale = Field(
        validation_alias="temperatureScale", serialization_alias="temperatureScale"
    )
    """Temperature scale unit"""


class SetConfigurationValidationPeriodAqiRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_aqi: ValidationPeriod = Field(
        validation_alias="validationPeriodAqi", serialization_alias="validationPeriodAqi"
    )
    """Validation period AQI"""


class SetConfigurationValidationPeriodCo2Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_co2: ValidationPeriod = Field(
        validation_alias="validationPeriodCo2", serialization_alias="validationPeriodCo2"
    )
    """Validation period CO2"""


class SetConfigurationValidationPeriodHumidityRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_humidity: ValidationPeriod = Field(
        validation_alias="validationPeriodHumidity", serialization_alias="validationPeriodHumidity"
    )
    """Validation period humidity"""


class SetConfigurationValidationPeriodNoxRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_nox: ValidationPeriod = Field(
        validation_alias="validationPeriodNox", serialization_alias="validationPeriodNox"
    )
    """Validation period NOx"""


class SetConfigurationValidationPeriodPm10p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_pm10p0: ValidationPeriod = Field(
        validation_alias="validationPeriodPm10p0", serialization_alias="validationPeriodPm10p0"
    )
    """Validation period PM10.0"""


class SetConfigurationValidationPeriodPm1p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_pm1p0: ValidationPeriod = Field(
        validation_alias="validationPeriodPm1p0", serialization_alias="validationPeriodPm1p0"
    )
    """Validation period PM1.0"""


class SetConfigurationValidationPeriodPm2p5Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_pm2p5: ValidationPeriod = Field(
        validation_alias="validationPeriodPm2p5", serialization_alias="validationPeriodPm2p5"
    )
    """Validation period PM2.5"""


class SetConfigurationValidationPeriodPm4p0Request(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_pm4p0: ValidationPeriod = Field(
        validation_alias="validationPeriodPm4p0", serialization_alias="validationPeriodPm4p0"
    )
    """Validation period PM4.0"""


class SetConfigurationValidationPeriodTemperatureRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_temperature: ValidationPeriod = Field(
        validation_alias="validationPeriodTemperature", serialization_alias="validationPeriodTemperature"
    )
    """Validation period temperature"""


class SetConfigurationValidationPeriodVapingRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_vaping: ValidationPeriod = Field(
        validation_alias="validationPeriodVaping", serialization_alias="validationPeriodVaping"
    )
    """Validation period vaping"""


class SetConfigurationValidationPeriodVocRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    validation_period_voc: ValidationPeriod = Field(
        validation_alias="validationPeriodVoc", serialization_alias="validationPeriodVoc"
    )
    """Validation period VOC"""


class SetConfigurationVapeSensitivityRequest(Model):
    sensor_id: SensorId = Field(validation_alias="sensorId", serialization_alias="sensorId")
    vape_sensitivity: VapeSensitivity = Field(validation_alias="vapeSensitivity", serialization_alias="vapeSensitivity")
    """Vape sensitivity"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/airqualitymonitor/v1"

INFO = ApiInfo(
    id="airqualitymonitor-config",
    name="Air Quality monitor API",
    family=Family.DCA,
    discovery=(DcaDiscovery("airqualitymonitor", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/environmental-sensor/air-quality-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=AirQualityMonitor, access="admin", effect="read"
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
        DcaBinding("GET", f"{ROOT}/configurations/{{sensor_id}}"),
        params=SensorIdRequest,
        result=Configuration,
        access="viewer",
        effect="read",
    )
    update_configuration = Operation(
        INFO,
        "update_configuration",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}", body="object"),
        params=UpdateConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_cloud_metadata_enable = Operation(
        INFO,
        "set_configuration_cloud_metadata_enable",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/cloudMetadataEnable",
            body="value",
            body_field="cloud_metadata_enable",
        ),
        params=SetConfigurationCloudMetadataEnableRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_cloud_metadata_frequency = Operation(
        INFO,
        "set_configuration_cloud_metadata_frequency",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/cloudMetadataFrequency",
            body="value",
            body_field="cloud_metadata_frequency",
        ),
        params=SetConfigurationCloudMetadataFrequencyRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_dashboard_items = Operation(
        INFO,
        "set_configuration_dashboard_items",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/dashboardItems", body="value", body_field="dashboard_items"
        ),
        params=SetConfigurationDashboardItemsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_dashboard_title = Operation(
        INFO,
        "set_configuration_dashboard_title",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/dashboardTitle", body="value", body_field="dashboard_title"
        ),
        params=SetConfigurationDashboardTitleRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_aqi = Operation(
        INFO,
        "set_configuration_max_aqi",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxAqi", body="value", body_field="max_aqi"),
        params=SetConfigurationMaxAqiRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_co2 = Operation(
        INFO,
        "set_configuration_max_co2",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxCo2", body="value", body_field="max_co2"),
        params=SetConfigurationMaxCo2Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_humidity = Operation(
        INFO,
        "set_configuration_max_humidity",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxHumidity", body="value", body_field="max_humidity"
        ),
        params=SetConfigurationMaxHumidityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_nox = Operation(
        INFO,
        "set_configuration_max_nox",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxNox", body="value", body_field="max_nox"),
        params=SetConfigurationMaxNoxRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_pm10p0 = Operation(
        INFO,
        "set_configuration_max_pm10p0",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxPm10p0", body="value", body_field="max_pm10p0"),
        params=SetConfigurationMaxPm10p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_pm1p0 = Operation(
        INFO,
        "set_configuration_max_pm1p0",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxPm1p0", body="value", body_field="max_pm1p0"),
        params=SetConfigurationMaxPm1p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_pm2p5 = Operation(
        INFO,
        "set_configuration_max_pm2p5",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxPm2p5", body="value", body_field="max_pm2p5"),
        params=SetConfigurationMaxPm2p5Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_pm4p0 = Operation(
        INFO,
        "set_configuration_max_pm4p0",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxPm4p0", body="value", body_field="max_pm4p0"),
        params=SetConfigurationMaxPm4p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_temperature = Operation(
        INFO,
        "set_configuration_max_temperature",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxTemperature", body="value", body_field="max_temperature"
        ),
        params=SetConfigurationMaxTemperatureRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_max_voc = Operation(
        INFO,
        "set_configuration_max_voc",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/maxVoc", body="value", body_field="max_voc"),
        params=SetConfigurationMaxVocRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_aqi = Operation(
        INFO,
        "set_configuration_min_aqi",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minAqi", body="value", body_field="min_aqi"),
        params=SetConfigurationMinAqiRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_co2 = Operation(
        INFO,
        "set_configuration_min_co2",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minCo2", body="value", body_field="min_co2"),
        params=SetConfigurationMinCo2Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_humidity = Operation(
        INFO,
        "set_configuration_min_humidity",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/minHumidity", body="value", body_field="min_humidity"
        ),
        params=SetConfigurationMinHumidityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_nox = Operation(
        INFO,
        "set_configuration_min_nox",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minNox", body="value", body_field="min_nox"),
        params=SetConfigurationMinNoxRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_pm10p0 = Operation(
        INFO,
        "set_configuration_min_pm10p0",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minPm10p0", body="value", body_field="min_pm10p0"),
        params=SetConfigurationMinPm10p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_pm1p0 = Operation(
        INFO,
        "set_configuration_min_pm1p0",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minPm1p0", body="value", body_field="min_pm1p0"),
        params=SetConfigurationMinPm1p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_pm2p5 = Operation(
        INFO,
        "set_configuration_min_pm2p5",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minPm2p5", body="value", body_field="min_pm2p5"),
        params=SetConfigurationMinPm2p5Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_pm4p0 = Operation(
        INFO,
        "set_configuration_min_pm4p0",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minPm4p0", body="value", body_field="min_pm4p0"),
        params=SetConfigurationMinPm4p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_temperature = Operation(
        INFO,
        "set_configuration_min_temperature",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/minTemperature", body="value", body_field="min_temperature"
        ),
        params=SetConfigurationMinTemperatureRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_min_voc = Operation(
        INFO,
        "set_configuration_min_voc",
        DcaBinding("PATCH", f"{ROOT}/configurations/{{sensor_id}}/minVoc", body="value", body_field="min_voc"),
        params=SetConfigurationMinVocRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_storage_enable = Operation(
        INFO,
        "set_configuration_storage_enable",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/storageEnable", body="value", body_field="storage_enable"
        ),
        params=SetConfigurationStorageEnableRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_storage_mode = Operation(
        INFO,
        "set_configuration_storage_mode",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/storageMode", body="value", body_field="storage_mode"
        ),
        params=SetConfigurationStorageModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_temperature_scale = Operation(
        INFO,
        "set_configuration_temperature_scale",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/temperatureScale",
            body="value",
            body_field="temperature_scale",
        ),
        params=SetConfigurationTemperatureScaleRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_aqi = Operation(
        INFO,
        "set_configuration_validation_period_aqi",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodAqi",
            body="value",
            body_field="validation_period_aqi",
        ),
        params=SetConfigurationValidationPeriodAqiRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_co2 = Operation(
        INFO,
        "set_configuration_validation_period_co2",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodCo2",
            body="value",
            body_field="validation_period_co2",
        ),
        params=SetConfigurationValidationPeriodCo2Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_humidity = Operation(
        INFO,
        "set_configuration_validation_period_humidity",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodHumidity",
            body="value",
            body_field="validation_period_humidity",
        ),
        params=SetConfigurationValidationPeriodHumidityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_nox = Operation(
        INFO,
        "set_configuration_validation_period_nox",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodNox",
            body="value",
            body_field="validation_period_nox",
        ),
        params=SetConfigurationValidationPeriodNoxRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_pm10p0 = Operation(
        INFO,
        "set_configuration_validation_period_pm10p0",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodPm10p0",
            body="value",
            body_field="validation_period_pm10p0",
        ),
        params=SetConfigurationValidationPeriodPm10p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_pm1p0 = Operation(
        INFO,
        "set_configuration_validation_period_pm1p0",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodPm1p0",
            body="value",
            body_field="validation_period_pm1p0",
        ),
        params=SetConfigurationValidationPeriodPm1p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_pm2p5 = Operation(
        INFO,
        "set_configuration_validation_period_pm2p5",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodPm2p5",
            body="value",
            body_field="validation_period_pm2p5",
        ),
        params=SetConfigurationValidationPeriodPm2p5Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_pm4p0 = Operation(
        INFO,
        "set_configuration_validation_period_pm4p0",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodPm4p0",
            body="value",
            body_field="validation_period_pm4p0",
        ),
        params=SetConfigurationValidationPeriodPm4p0Request,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_temperature = Operation(
        INFO,
        "set_configuration_validation_period_temperature",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodTemperature",
            body="value",
            body_field="validation_period_temperature",
        ),
        params=SetConfigurationValidationPeriodTemperatureRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_vaping = Operation(
        INFO,
        "set_configuration_validation_period_vaping",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodVaping",
            body="value",
            body_field="validation_period_vaping",
        ),
        params=SetConfigurationValidationPeriodVapingRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_validation_period_voc = Operation(
        INFO,
        "set_configuration_validation_period_voc",
        DcaBinding(
            "PATCH",
            f"{ROOT}/configurations/{{sensor_id}}/validationPeriodVoc",
            body="value",
            body_field="validation_period_voc",
        ),
        params=SetConfigurationValidationPeriodVocRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_configuration_vape_sensitivity = Operation(
        INFO,
        "set_configuration_vape_sensitivity",
        DcaBinding(
            "PATCH", f"{ROOT}/configurations/{{sensor_id}}/vapeSensitivity", body="value", body_field="vape_sensitivity"
        ),
        params=SetConfigurationVapeSensitivityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_sensors = Operation(
        INFO, "list_sensors", DcaBinding("GET", f"{ROOT}/sensors"), result=list[Sensor], access="viewer", effect="read"
    )
    get_sensor = Operation(
        INFO,
        "get_sensor",
        DcaBinding("GET", f"{ROOT}/sensors/{{sensor_id}}"),
        params=SensorIdRequest,
        result=Sensor,
        access="viewer",
        effect="read",
    )
    get_history_data = Operation(
        INFO,
        "get_history_data",
        DcaBinding("POST", f"{ROOT}/sensors/{{sensor_id}}/getHistoryData", body="object"),
        params=GetHistoryDataRequest,
        result=HistoryDataResult,
        access="operator",
        effect="read",
    )
    get_vaping_record = Operation(
        INFO,
        "get_vaping_record",
        DcaBinding("POST", f"{ROOT}/sensors/{{sensor_id}}/getVapingRecord", body="object"),
        params=GetVapingRecordRequest,
        result=VapingRecord,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class AirQualityMonitorApi(SyncApi):
    """Air Quality monitor API (``airqualitymonitor-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> AirQualityMonitor:
        """All data of the Air Quality monitor API API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_configurations(self, *, request_options: RequestOptions | None = None) -> list[Configuration]:
        """List the configurations. Access: viewer."""
        return self._run(OPS.list_configurations, None, {}, request_options)

    def get_configuration(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> Configuration:
        """Get one configuration. Access: viewer."""
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
        cloud_metadata_enable: bool | MISSING = MISSING,
        cloud_metadata_frequency: CloudMetadataFrequency | MISSING = MISSING,
        dashboard_items: DashboardItems | MISSING = MISSING,
        dashboard_title: str | MISSING = MISSING,
        max_aqi: Limit | MISSING = MISSING,
        max_co2: Limit | MISSING = MISSING,
        max_humidity: Limit | MISSING = MISSING,
        max_nox: Limit | MISSING = MISSING,
        max_pm10p0: Limit | MISSING = MISSING,
        max_pm1p0: Limit | MISSING = MISSING,
        max_pm2p5: Limit | MISSING = MISSING,
        max_pm4p0: Limit | MISSING = MISSING,
        max_temperature: Limit | MISSING = MISSING,
        max_voc: Limit | MISSING = MISSING,
        min_aqi: Limit | MISSING = MISSING,
        min_co2: Limit | MISSING = MISSING,
        min_humidity: Limit | MISSING = MISSING,
        min_nox: Limit | MISSING = MISSING,
        min_pm10p0: Limit | MISSING = MISSING,
        min_pm1p0: Limit | MISSING = MISSING,
        min_pm2p5: Limit | MISSING = MISSING,
        min_pm4p0: Limit | MISSING = MISSING,
        min_temperature: Limit | MISSING = MISSING,
        min_voc: Limit | MISSING = MISSING,
        storage_enable: bool | MISSING = MISSING,
        storage_mode: StorageMode | MISSING = MISSING,
        temperature_scale: TemperatureScale | MISSING = MISSING,
        validation_period_aqi: ValidationPeriod | MISSING = MISSING,
        validation_period_co2: ValidationPeriod | MISSING = MISSING,
        validation_period_humidity: ValidationPeriod | MISSING = MISSING,
        validation_period_nox: ValidationPeriod | MISSING = MISSING,
        validation_period_pm10p0: ValidationPeriod | MISSING = MISSING,
        validation_period_pm1p0: ValidationPeriod | MISSING = MISSING,
        validation_period_pm2p5: ValidationPeriod | MISSING = MISSING,
        validation_period_pm4p0: ValidationPeriod | MISSING = MISSING,
        validation_period_temperature: ValidationPeriod | MISSING = MISSING,
        validation_period_vaping: ValidationPeriod | MISSING = MISSING,
        validation_period_voc: ValidationPeriod | MISSING = MISSING,
        vape_sensitivity: VapeSensitivity | MISSING = MISSING,
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
        """Update a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.update_configuration, request, kwargs, request_options)

    def set_configuration_cloud_metadata_enable(
        self, sensor_id: SensorId, *, cloud_metadata_enable: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the cloud metadata enable of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_cloud_metadata_enable,
            None,
            {"sensor_id": sensor_id, "cloud_metadata_enable": cloud_metadata_enable},
            request_options,
        )

    def set_configuration_cloud_metadata_frequency(
        self,
        sensor_id: SensorId,
        *,
        cloud_metadata_frequency: CloudMetadataFrequency,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the cloud metadata frequency of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_cloud_metadata_frequency,
            None,
            {"sensor_id": sensor_id, "cloud_metadata_frequency": cloud_metadata_frequency},
            request_options,
        )

    @overload
    def set_configuration_dashboard_items(
        self, request: SetConfigurationDashboardItemsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_configuration_dashboard_items(
        self, /, *, sensor_id: SensorId, dashboard_items: DashboardItems, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_configuration_dashboard_items(
        self,
        request: SetConfigurationDashboardItemsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the dashboard items of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_dashboard_items, request, kwargs, request_options)

    def set_configuration_dashboard_title(
        self, sensor_id: SensorId, *, dashboard_title: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the dashboard title of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_dashboard_title,
            None,
            {"sensor_id": sensor_id, "dashboard_title": dashboard_title},
            request_options,
        )

    def set_configuration_max_aqi(
        self, sensor_id: SensorId, *, max_aqi: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the maximum AQI of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_max_aqi, None, {"sensor_id": sensor_id, "max_aqi": max_aqi}, request_options)

    def set_configuration_max_co2(
        self, sensor_id: SensorId, *, max_co2: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max co2 of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_max_co2, None, {"sensor_id": sensor_id, "max_co2": max_co2}, request_options)

    def set_configuration_max_humidity(
        self, sensor_id: SensorId, *, max_humidity: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max humidity of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_max_humidity,
            None,
            {"sensor_id": sensor_id, "max_humidity": max_humidity},
            request_options,
        )

    def set_configuration_max_nox(
        self, sensor_id: SensorId, *, max_nox: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max nox of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_max_nox, None, {"sensor_id": sensor_id, "max_nox": max_nox}, request_options)

    def set_configuration_max_pm10p0(
        self, sensor_id: SensorId, *, max_pm10p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm10p0 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_max_pm10p0, None, {"sensor_id": sensor_id, "max_pm10p0": max_pm10p0}, request_options
        )

    def set_configuration_max_pm1p0(
        self, sensor_id: SensorId, *, max_pm1p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm1p0 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_max_pm1p0, None, {"sensor_id": sensor_id, "max_pm1p0": max_pm1p0}, request_options
        )

    def set_configuration_max_pm2p5(
        self, sensor_id: SensorId, *, max_pm2p5: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm2p5 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_max_pm2p5, None, {"sensor_id": sensor_id, "max_pm2p5": max_pm2p5}, request_options
        )

    def set_configuration_max_pm4p0(
        self, sensor_id: SensorId, *, max_pm4p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm4p0 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_max_pm4p0, None, {"sensor_id": sensor_id, "max_pm4p0": max_pm4p0}, request_options
        )

    def set_configuration_max_temperature(
        self, sensor_id: SensorId, *, max_temperature: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max temperature of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_max_temperature,
            None,
            {"sensor_id": sensor_id, "max_temperature": max_temperature},
            request_options,
        )

    def set_configuration_max_voc(
        self, sensor_id: SensorId, *, max_voc: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max voc of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_max_voc, None, {"sensor_id": sensor_id, "max_voc": max_voc}, request_options)

    def set_configuration_min_aqi(
        self, sensor_id: SensorId, *, min_aqi: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min aqi of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_min_aqi, None, {"sensor_id": sensor_id, "min_aqi": min_aqi}, request_options)

    def set_configuration_min_co2(
        self, sensor_id: SensorId, *, min_co2: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min co2 of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_min_co2, None, {"sensor_id": sensor_id, "min_co2": min_co2}, request_options)

    def set_configuration_min_humidity(
        self, sensor_id: SensorId, *, min_humidity: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min humidity of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_min_humidity,
            None,
            {"sensor_id": sensor_id, "min_humidity": min_humidity},
            request_options,
        )

    def set_configuration_min_nox(
        self, sensor_id: SensorId, *, min_nox: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min nox of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_min_nox, None, {"sensor_id": sensor_id, "min_nox": min_nox}, request_options)

    def set_configuration_min_pm10p0(
        self, sensor_id: SensorId, *, min_pm10p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm10p0 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_min_pm10p0, None, {"sensor_id": sensor_id, "min_pm10p0": min_pm10p0}, request_options
        )

    def set_configuration_min_pm1p0(
        self, sensor_id: SensorId, *, min_pm1p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm1p0 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_min_pm1p0, None, {"sensor_id": sensor_id, "min_pm1p0": min_pm1p0}, request_options
        )

    def set_configuration_min_pm2p5(
        self, sensor_id: SensorId, *, min_pm2p5: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm2p5 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_min_pm2p5, None, {"sensor_id": sensor_id, "min_pm2p5": min_pm2p5}, request_options
        )

    def set_configuration_min_pm4p0(
        self, sensor_id: SensorId, *, min_pm4p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm4p0 of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_min_pm4p0, None, {"sensor_id": sensor_id, "min_pm4p0": min_pm4p0}, request_options
        )

    def set_configuration_min_temperature(
        self, sensor_id: SensorId, *, min_temperature: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min temperature of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_min_temperature,
            None,
            {"sensor_id": sensor_id, "min_temperature": min_temperature},
            request_options,
        )

    def set_configuration_min_voc(
        self, sensor_id: SensorId, *, min_voc: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min voc of a configuration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_configuration_min_voc, None, {"sensor_id": sensor_id, "min_voc": min_voc}, request_options)

    def set_configuration_storage_enable(
        self, sensor_id: SensorId, *, storage_enable: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the storage enable of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_storage_enable,
            None,
            {"sensor_id": sensor_id, "storage_enable": storage_enable},
            request_options,
        )

    def set_configuration_storage_mode(
        self, sensor_id: SensorId, *, storage_mode: StorageMode, request_options: RequestOptions | None = None
    ) -> None:
        """Set the storage mode of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_storage_mode,
            None,
            {"sensor_id": sensor_id, "storage_mode": storage_mode},
            request_options,
        )

    def set_configuration_temperature_scale(
        self, sensor_id: SensorId, *, temperature_scale: TemperatureScale, request_options: RequestOptions | None = None
    ) -> None:
        """Set the temperature scale of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_temperature_scale,
            None,
            {"sensor_id": sensor_id, "temperature_scale": temperature_scale},
            request_options,
        )

    def set_configuration_validation_period_aqi(
        self,
        sensor_id: SensorId,
        *,
        validation_period_aqi: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period aqi of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_aqi,
            None,
            {"sensor_id": sensor_id, "validation_period_aqi": validation_period_aqi},
            request_options,
        )

    def set_configuration_validation_period_co2(
        self,
        sensor_id: SensorId,
        *,
        validation_period_co2: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period co2 of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_co2,
            None,
            {"sensor_id": sensor_id, "validation_period_co2": validation_period_co2},
            request_options,
        )

    def set_configuration_validation_period_humidity(
        self,
        sensor_id: SensorId,
        *,
        validation_period_humidity: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period humidity of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_humidity,
            None,
            {"sensor_id": sensor_id, "validation_period_humidity": validation_period_humidity},
            request_options,
        )

    def set_configuration_validation_period_nox(
        self,
        sensor_id: SensorId,
        *,
        validation_period_nox: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period nox of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_nox,
            None,
            {"sensor_id": sensor_id, "validation_period_nox": validation_period_nox},
            request_options,
        )

    def set_configuration_validation_period_pm10p0(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm10p0: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm10p0 of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_pm10p0,
            None,
            {"sensor_id": sensor_id, "validation_period_pm10p0": validation_period_pm10p0},
            request_options,
        )

    def set_configuration_validation_period_pm1p0(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm1p0: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm1p0 of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_pm1p0,
            None,
            {"sensor_id": sensor_id, "validation_period_pm1p0": validation_period_pm1p0},
            request_options,
        )

    def set_configuration_validation_period_pm2p5(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm2p5: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm2p5 of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_pm2p5,
            None,
            {"sensor_id": sensor_id, "validation_period_pm2p5": validation_period_pm2p5},
            request_options,
        )

    def set_configuration_validation_period_pm4p0(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm4p0: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm4p0 of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_pm4p0,
            None,
            {"sensor_id": sensor_id, "validation_period_pm4p0": validation_period_pm4p0},
            request_options,
        )

    def set_configuration_validation_period_temperature(
        self,
        sensor_id: SensorId,
        *,
        validation_period_temperature: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period temperature of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_temperature,
            None,
            {"sensor_id": sensor_id, "validation_period_temperature": validation_period_temperature},
            request_options,
        )

    def set_configuration_validation_period_vaping(
        self,
        sensor_id: SensorId,
        *,
        validation_period_vaping: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period vaping of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_vaping,
            None,
            {"sensor_id": sensor_id, "validation_period_vaping": validation_period_vaping},
            request_options,
        )

    def set_configuration_validation_period_voc(
        self,
        sensor_id: SensorId,
        *,
        validation_period_voc: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period voc of a configuration.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_configuration_validation_period_voc,
            None,
            {"sensor_id": sensor_id, "validation_period_voc": validation_period_voc},
            request_options,
        )

    def set_configuration_vape_sensitivity(
        self, sensor_id: SensorId, *, vape_sensitivity: VapeSensitivity, request_options: RequestOptions | None = None
    ) -> None:
        """Set the vape sensitivity of a configuration. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_configuration_vape_sensitivity,
            None,
            {"sensor_id": sensor_id, "vape_sensitivity": vape_sensitivity},
            request_options,
        )

    def list_sensors(self, *, request_options: RequestOptions | None = None) -> list[Sensor]:
        """List the sensors. Access: viewer."""
        return self._run(OPS.list_sensors, None, {}, request_options)

    def get_sensor(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> Sensor:
        """Get one sensor. Access: viewer."""
        return self._run(OPS.get_sensor, None, {"sensor_id": sensor_id}, request_options)

    def get_history_data(
        self,
        sensor_id: SensorId,
        *,
        category: MeasurementCategory,
        start_time: int,
        end_time: int,
        request_options: RequestOptions | None = None,
    ) -> HistoryDataResult:
        """Historical measurements of one category between two times. Access: operator."""
        return self._run(
            OPS.get_history_data,
            None,
            {"sensor_id": sensor_id, "category": category, "start_time": start_time, "end_time": end_time},
            request_options,
        )

    def get_vaping_record(
        self, sensor_id: SensorId, *, start_time: int, end_time: int, request_options: RequestOptions | None = None
    ) -> VapingRecord:
        """Times when vaping was detected between two times. Access: operator."""
        return self._run(
            OPS.get_vaping_record,
            None,
            {"sensor_id": sensor_id, "start_time": start_time, "end_time": end_time},
            request_options,
        )


class AsyncAirQualityMonitorApi(AsyncApi):
    """Air Quality monitor API (``airqualitymonitor-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> AirQualityMonitor:
        """All data of the Air Quality monitor API API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_configurations(self, *, request_options: RequestOptions | None = None) -> list[Configuration]:
        """List the configurations. Access: viewer."""
        return await self._run(OPS.list_configurations, None, {}, request_options)

    async def get_configuration(
        self, sensor_id: SensorId, *, request_options: RequestOptions | None = None
    ) -> Configuration:
        """Get one configuration. Access: viewer."""
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
        cloud_metadata_enable: bool | MISSING = MISSING,
        cloud_metadata_frequency: CloudMetadataFrequency | MISSING = MISSING,
        dashboard_items: DashboardItems | MISSING = MISSING,
        dashboard_title: str | MISSING = MISSING,
        max_aqi: Limit | MISSING = MISSING,
        max_co2: Limit | MISSING = MISSING,
        max_humidity: Limit | MISSING = MISSING,
        max_nox: Limit | MISSING = MISSING,
        max_pm10p0: Limit | MISSING = MISSING,
        max_pm1p0: Limit | MISSING = MISSING,
        max_pm2p5: Limit | MISSING = MISSING,
        max_pm4p0: Limit | MISSING = MISSING,
        max_temperature: Limit | MISSING = MISSING,
        max_voc: Limit | MISSING = MISSING,
        min_aqi: Limit | MISSING = MISSING,
        min_co2: Limit | MISSING = MISSING,
        min_humidity: Limit | MISSING = MISSING,
        min_nox: Limit | MISSING = MISSING,
        min_pm10p0: Limit | MISSING = MISSING,
        min_pm1p0: Limit | MISSING = MISSING,
        min_pm2p5: Limit | MISSING = MISSING,
        min_pm4p0: Limit | MISSING = MISSING,
        min_temperature: Limit | MISSING = MISSING,
        min_voc: Limit | MISSING = MISSING,
        storage_enable: bool | MISSING = MISSING,
        storage_mode: StorageMode | MISSING = MISSING,
        temperature_scale: TemperatureScale | MISSING = MISSING,
        validation_period_aqi: ValidationPeriod | MISSING = MISSING,
        validation_period_co2: ValidationPeriod | MISSING = MISSING,
        validation_period_humidity: ValidationPeriod | MISSING = MISSING,
        validation_period_nox: ValidationPeriod | MISSING = MISSING,
        validation_period_pm10p0: ValidationPeriod | MISSING = MISSING,
        validation_period_pm1p0: ValidationPeriod | MISSING = MISSING,
        validation_period_pm2p5: ValidationPeriod | MISSING = MISSING,
        validation_period_pm4p0: ValidationPeriod | MISSING = MISSING,
        validation_period_temperature: ValidationPeriod | MISSING = MISSING,
        validation_period_vaping: ValidationPeriod | MISSING = MISSING,
        validation_period_voc: ValidationPeriod | MISSING = MISSING,
        vape_sensitivity: VapeSensitivity | MISSING = MISSING,
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
        """Update a configuration. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_configuration, request, kwargs, request_options)

    async def set_configuration_cloud_metadata_enable(
        self, sensor_id: SensorId, *, cloud_metadata_enable: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the cloud metadata enable of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_cloud_metadata_enable,
            None,
            {"sensor_id": sensor_id, "cloud_metadata_enable": cloud_metadata_enable},
            request_options,
        )

    async def set_configuration_cloud_metadata_frequency(
        self,
        sensor_id: SensorId,
        *,
        cloud_metadata_frequency: CloudMetadataFrequency,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the cloud metadata frequency of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_cloud_metadata_frequency,
            None,
            {"sensor_id": sensor_id, "cloud_metadata_frequency": cloud_metadata_frequency},
            request_options,
        )

    @overload
    async def set_configuration_dashboard_items(
        self, request: SetConfigurationDashboardItemsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_configuration_dashboard_items(
        self, /, *, sensor_id: SensorId, dashboard_items: DashboardItems, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_configuration_dashboard_items(
        self,
        request: SetConfigurationDashboardItemsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the dashboard items of a configuration. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_configuration_dashboard_items, request, kwargs, request_options)

    async def set_configuration_dashboard_title(
        self, sensor_id: SensorId, *, dashboard_title: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the dashboard title of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_dashboard_title,
            None,
            {"sensor_id": sensor_id, "dashboard_title": dashboard_title},
            request_options,
        )

    async def set_configuration_max_aqi(
        self, sensor_id: SensorId, *, max_aqi: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the maximum AQI of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_aqi, None, {"sensor_id": sensor_id, "max_aqi": max_aqi}, request_options
        )

    async def set_configuration_max_co2(
        self, sensor_id: SensorId, *, max_co2: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max co2 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_co2, None, {"sensor_id": sensor_id, "max_co2": max_co2}, request_options
        )

    async def set_configuration_max_humidity(
        self, sensor_id: SensorId, *, max_humidity: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max humidity of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_humidity,
            None,
            {"sensor_id": sensor_id, "max_humidity": max_humidity},
            request_options,
        )

    async def set_configuration_max_nox(
        self, sensor_id: SensorId, *, max_nox: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max nox of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_nox, None, {"sensor_id": sensor_id, "max_nox": max_nox}, request_options
        )

    async def set_configuration_max_pm10p0(
        self, sensor_id: SensorId, *, max_pm10p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm10p0 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_pm10p0, None, {"sensor_id": sensor_id, "max_pm10p0": max_pm10p0}, request_options
        )

    async def set_configuration_max_pm1p0(
        self, sensor_id: SensorId, *, max_pm1p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm1p0 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_pm1p0, None, {"sensor_id": sensor_id, "max_pm1p0": max_pm1p0}, request_options
        )

    async def set_configuration_max_pm2p5(
        self, sensor_id: SensorId, *, max_pm2p5: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm2p5 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_pm2p5, None, {"sensor_id": sensor_id, "max_pm2p5": max_pm2p5}, request_options
        )

    async def set_configuration_max_pm4p0(
        self, sensor_id: SensorId, *, max_pm4p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max pm4p0 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_pm4p0, None, {"sensor_id": sensor_id, "max_pm4p0": max_pm4p0}, request_options
        )

    async def set_configuration_max_temperature(
        self, sensor_id: SensorId, *, max_temperature: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max temperature of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_temperature,
            None,
            {"sensor_id": sensor_id, "max_temperature": max_temperature},
            request_options,
        )

    async def set_configuration_max_voc(
        self, sensor_id: SensorId, *, max_voc: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the max voc of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_max_voc, None, {"sensor_id": sensor_id, "max_voc": max_voc}, request_options
        )

    async def set_configuration_min_aqi(
        self, sensor_id: SensorId, *, min_aqi: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min aqi of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_aqi, None, {"sensor_id": sensor_id, "min_aqi": min_aqi}, request_options
        )

    async def set_configuration_min_co2(
        self, sensor_id: SensorId, *, min_co2: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min co2 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_co2, None, {"sensor_id": sensor_id, "min_co2": min_co2}, request_options
        )

    async def set_configuration_min_humidity(
        self, sensor_id: SensorId, *, min_humidity: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min humidity of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_humidity,
            None,
            {"sensor_id": sensor_id, "min_humidity": min_humidity},
            request_options,
        )

    async def set_configuration_min_nox(
        self, sensor_id: SensorId, *, min_nox: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min nox of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_nox, None, {"sensor_id": sensor_id, "min_nox": min_nox}, request_options
        )

    async def set_configuration_min_pm10p0(
        self, sensor_id: SensorId, *, min_pm10p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm10p0 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_pm10p0, None, {"sensor_id": sensor_id, "min_pm10p0": min_pm10p0}, request_options
        )

    async def set_configuration_min_pm1p0(
        self, sensor_id: SensorId, *, min_pm1p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm1p0 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_pm1p0, None, {"sensor_id": sensor_id, "min_pm1p0": min_pm1p0}, request_options
        )

    async def set_configuration_min_pm2p5(
        self, sensor_id: SensorId, *, min_pm2p5: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm2p5 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_pm2p5, None, {"sensor_id": sensor_id, "min_pm2p5": min_pm2p5}, request_options
        )

    async def set_configuration_min_pm4p0(
        self, sensor_id: SensorId, *, min_pm4p0: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min pm4p0 of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_pm4p0, None, {"sensor_id": sensor_id, "min_pm4p0": min_pm4p0}, request_options
        )

    async def set_configuration_min_temperature(
        self, sensor_id: SensorId, *, min_temperature: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min temperature of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_temperature,
            None,
            {"sensor_id": sensor_id, "min_temperature": min_temperature},
            request_options,
        )

    async def set_configuration_min_voc(
        self, sensor_id: SensorId, *, min_voc: Limit, request_options: RequestOptions | None = None
    ) -> None:
        """Set the min voc of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_min_voc, None, {"sensor_id": sensor_id, "min_voc": min_voc}, request_options
        )

    async def set_configuration_storage_enable(
        self, sensor_id: SensorId, *, storage_enable: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the storage enable of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_storage_enable,
            None,
            {"sensor_id": sensor_id, "storage_enable": storage_enable},
            request_options,
        )

    async def set_configuration_storage_mode(
        self, sensor_id: SensorId, *, storage_mode: StorageMode, request_options: RequestOptions | None = None
    ) -> None:
        """Set the storage mode of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_storage_mode,
            None,
            {"sensor_id": sensor_id, "storage_mode": storage_mode},
            request_options,
        )

    async def set_configuration_temperature_scale(
        self, sensor_id: SensorId, *, temperature_scale: TemperatureScale, request_options: RequestOptions | None = None
    ) -> None:
        """Set the temperature scale of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_temperature_scale,
            None,
            {"sensor_id": sensor_id, "temperature_scale": temperature_scale},
            request_options,
        )

    async def set_configuration_validation_period_aqi(
        self,
        sensor_id: SensorId,
        *,
        validation_period_aqi: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period aqi of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_aqi,
            None,
            {"sensor_id": sensor_id, "validation_period_aqi": validation_period_aqi},
            request_options,
        )

    async def set_configuration_validation_period_co2(
        self,
        sensor_id: SensorId,
        *,
        validation_period_co2: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period co2 of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_co2,
            None,
            {"sensor_id": sensor_id, "validation_period_co2": validation_period_co2},
            request_options,
        )

    async def set_configuration_validation_period_humidity(
        self,
        sensor_id: SensorId,
        *,
        validation_period_humidity: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period humidity of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_humidity,
            None,
            {"sensor_id": sensor_id, "validation_period_humidity": validation_period_humidity},
            request_options,
        )

    async def set_configuration_validation_period_nox(
        self,
        sensor_id: SensorId,
        *,
        validation_period_nox: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period nox of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_nox,
            None,
            {"sensor_id": sensor_id, "validation_period_nox": validation_period_nox},
            request_options,
        )

    async def set_configuration_validation_period_pm10p0(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm10p0: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm10p0 of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_pm10p0,
            None,
            {"sensor_id": sensor_id, "validation_period_pm10p0": validation_period_pm10p0},
            request_options,
        )

    async def set_configuration_validation_period_pm1p0(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm1p0: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm1p0 of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_pm1p0,
            None,
            {"sensor_id": sensor_id, "validation_period_pm1p0": validation_period_pm1p0},
            request_options,
        )

    async def set_configuration_validation_period_pm2p5(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm2p5: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm2p5 of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_pm2p5,
            None,
            {"sensor_id": sensor_id, "validation_period_pm2p5": validation_period_pm2p5},
            request_options,
        )

    async def set_configuration_validation_period_pm4p0(
        self,
        sensor_id: SensorId,
        *,
        validation_period_pm4p0: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period pm4p0 of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_pm4p0,
            None,
            {"sensor_id": sensor_id, "validation_period_pm4p0": validation_period_pm4p0},
            request_options,
        )

    async def set_configuration_validation_period_temperature(
        self,
        sensor_id: SensorId,
        *,
        validation_period_temperature: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period temperature of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_temperature,
            None,
            {"sensor_id": sensor_id, "validation_period_temperature": validation_period_temperature},
            request_options,
        )

    async def set_configuration_validation_period_vaping(
        self,
        sensor_id: SensorId,
        *,
        validation_period_vaping: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period vaping of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_vaping,
            None,
            {"sensor_id": sensor_id, "validation_period_vaping": validation_period_vaping},
            request_options,
        )

    async def set_configuration_validation_period_voc(
        self,
        sensor_id: SensorId,
        *,
        validation_period_voc: ValidationPeriod,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the validation period voc of a configuration.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_configuration_validation_period_voc,
            None,
            {"sensor_id": sensor_id, "validation_period_voc": validation_period_voc},
            request_options,
        )

    async def set_configuration_vape_sensitivity(
        self, sensor_id: SensorId, *, vape_sensitivity: VapeSensitivity, request_options: RequestOptions | None = None
    ) -> None:
        """Set the vape sensitivity of a configuration. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_configuration_vape_sensitivity,
            None,
            {"sensor_id": sensor_id, "vape_sensitivity": vape_sensitivity},
            request_options,
        )

    async def list_sensors(self, *, request_options: RequestOptions | None = None) -> list[Sensor]:
        """List the sensors. Access: viewer."""
        return await self._run(OPS.list_sensors, None, {}, request_options)

    async def get_sensor(self, sensor_id: SensorId, *, request_options: RequestOptions | None = None) -> Sensor:
        """Get one sensor. Access: viewer."""
        return await self._run(OPS.get_sensor, None, {"sensor_id": sensor_id}, request_options)

    async def get_history_data(
        self,
        sensor_id: SensorId,
        *,
        category: MeasurementCategory,
        start_time: int,
        end_time: int,
        request_options: RequestOptions | None = None,
    ) -> HistoryDataResult:
        """Historical measurements of one category between two times. Access: operator."""
        return await self._run(
            OPS.get_history_data,
            None,
            {"sensor_id": sensor_id, "category": category, "start_time": start_time, "end_time": end_time},
            request_options,
        )

    async def get_vaping_record(
        self, sensor_id: SensorId, *, start_time: int, end_time: int, request_options: RequestOptions | None = None
    ) -> VapingRecord:
        """Times when vaping was detected between two times. Access: operator."""
        return await self._run(
            OPS.get_vaping_record,
            None,
            {"sensor_id": sensor_id, "start_time": start_time, "end_time": end_time},
            request_options,
        )
