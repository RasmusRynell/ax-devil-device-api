# GENERATED from specs/apis/network-video/temperature-alarm.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure temperature alarm zones on thermal cameras, read zone status and spot temperatures, set the temperature scale.

Docs: https://developer.axis.com/vapix/network-video/thermal-imaging/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DetectionType = Literal["above", "below", "increase"]
TemperatureType = Literal["maximum", "minimum"]


class AlarmZone(Model):
    """The configuration of one temperature alarm zone. Temperatures are in the unit set with set_temperature_scale."""

    zone_id: int = Field(validation_alias="ZoneId", serialization_alias="ZoneId")
    """The zone ID."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """The zone name."""
    xleft: int | None = Field(default=None, validation_alias="Xleft", serialization_alias="Xleft")
    """The left X coordinate."""
    xright: int | None = Field(default=None, validation_alias="Xright", serialization_alias="Xright")
    """The right X coordinate."""
    ytop: int | None = Field(default=None, validation_alias="Ytop", serialization_alias="Ytop")
    """The top Y coordinate."""
    ybottom: int | None = Field(default=None, validation_alias="Ybottom", serialization_alias="Ybottom")
    """The bottom Y coordinate."""
    emissivity: float | None = Field(default=None, validation_alias="Emissivity", serialization_alias="Emissivity")
    """The emissivity."""
    detection_type: DetectionType | None = Field(
        default=None, validation_alias="DetectionType", serialization_alias="DetectionType"
    )
    temperature: int | None = Field(default=None, validation_alias="Temperature", serialization_alias="Temperature")
    """The threshold temperature; for detection type increase the maximum allowed increase during the delay time."""
    temperature_type: TemperatureType | None = Field(
        default=None, validation_alias="TemperatureType", serialization_alias="TemperatureType"
    )
    delay_time: int | None = Field(default=None, validation_alias="DelayTime", serialization_alias="DelayTime")
    """The delay time in seconds."""


class AlarmZones(Model):
    zones: list[AlarmZone] = Field(validation_alias="AlarmZone", serialization_alias="AlarmZone")


class AlarmZoneStatus(Model):
    """The status of one temperature alarm zone. Temperatures are in the unit set with set_temperature_scale."""

    zone_id: int = Field(validation_alias="ZoneId", serialization_alias="ZoneId")
    """The zone ID."""
    average_temperature: float | None = Field(
        default=None, validation_alias="AverageTemperature", serialization_alias="AverageTemperature"
    )
    """The average temperature in the zone."""
    minimum_temperature: float | None = Field(
        default=None, validation_alias="MinimumTemperature", serialization_alias="MinimumTemperature"
    )
    """The minimum temperature in the zone."""
    maximum_temperature: float | None = Field(
        default=None, validation_alias="MaximumTemperature", serialization_alias="MaximumTemperature"
    )
    """The maximum temperature in the zone."""
    triggered: Literal["Yes", "No"] | None = Field(
        default=None, validation_alias="Triggered", serialization_alias="Triggered"
    )
    """Yes while the stateful tns1:VideoSource/tnsaxis:TemperatureDetection event is active."""


class AlarmZoneStatuses(Model):
    zones: list[AlarmZoneStatus] = Field(validation_alias="AlarmZone", serialization_alias="AlarmZone")


class SpotTemperature(Model):
    spot_temperature: float = Field(validation_alias="SpotTemperature", serialization_alias="SpotTemperature")
    """The returned spot temperature in the unit set with set_temperature_scale."""


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version, major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class SetTemperatureScaleRequest(Model):
    unit: Literal["Celsius", "Fahrenheit"]
    """The temperature scale to use."""


class SetZoneRequest(Model):
    id: int = Field(ge=0)
    """The zone ID."""
    name: str | None = None
    """A user-friendly name for the zone."""
    left: int | None = Field(default=None, ge=0, le=9999)
    """The left X coordinate of the zone."""
    right: int | None = Field(default=None, ge=0, le=9999)
    """The right X coordinate of the zone."""
    top: int | None = Field(default=None, ge=0, le=9999)
    """The top Y coordinate of the zone."""
    bottom: int | None = Field(default=None, ge=0, le=9999)
    """The bottom Y coordinate of the zone."""
    emissivity: float | None = Field(default=None, ge=0.5, le=1)
    """Emissivity of the objects in the zone; used to improve temperature measurement. The device default is 0.95."""
    detectiontype: DetectionType | None = None
    temperature: int | None = None
    """The threshold temperature; for detectiontype increase the maximum allowed increase during delaytime. In the unit set with set_temperature_scale."""
    temperaturetype: TemperatureType | None = None
    delaytime: int | None = Field(default=None, ge=0, le=60)
    """Time between successive temperature measurements (or the time window for detectiontype increase) in seconds."""


class RemoveZoneRequest(Model):
    id: int = Field(ge=0)
    """Zone ID of the zone to remove."""


class GetSpotTemperatureRequest(Model):
    coordinates: list[Annotated[int, Field(ge=0, le=9999)]] = Field(min_length=2, max_length=2)
    """The X and Y coordinates of the point, each 0 to 9999, with X=0 Y=0 in the image upper left corner."""
    emissivity: float | None = Field(default=None, ge=0.5, le=1)
    """Emissivity of the object; used to improve temperature measurement. The device default is 0.95."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/temperature_alarm/schemaversions.cgi"

INFO = ApiInfo(
    id="temperature-alarm",
    name="Temperature alarm API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.TemperatureAlarm.TemperatureDetection", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/thermal-imaging/",),
    errors={
        10: ErrorCode("Error while processing the request."),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
    },
)


class OPS:
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            PATH,
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "SchemaVersion",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("VersionNumber", source="child"),
                                    XmlField("Deprecated", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="SchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="viewer",
        effect="read",
    )
    set_temperature_scale = Operation(
        INFO,
        "set_temperature_scale",
        CgiBinding("/axis-cgi/temperature_alarm/settemperaturescale.cgi", args=(CgiArg("unit"),), reply=Xml()),
        params=SetTemperatureScaleRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_zone = Operation(
        INFO,
        "set_zone",
        CgiBinding(
            "/axis-cgi/temperature_alarm/set.cgi",
            args=(
                CgiArg("id"),
                CgiArg("name"),
                CgiArg("left"),
                CgiArg("right"),
                CgiArg("top"),
                CgiArg("bottom"),
                CgiArg("emissivity"),
                CgiArg("detectiontype"),
                CgiArg("temperature"),
                CgiArg("temperaturetype"),
                CgiArg("delaytime"),
            ),
            reply=Xml(),
        ),
        params=SetZoneRequest,
        access="operator",
        effect="write",
        write="create",
    )
    get_zones = Operation(
        INFO,
        "get_zones",
        CgiBinding(
            "/axis-cgi/temperature_alarm/get.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "AlarmZone",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("ZoneId", source="child"),
                                    XmlField("Name", source="child"),
                                    XmlField("Xleft", source="child"),
                                    XmlField("Xright", source="child"),
                                    XmlField("Ytop", source="child"),
                                    XmlField("Ybottom", source="child"),
                                    XmlField("Emissivity", source="child"),
                                    XmlField("DetectionType", source="child"),
                                    XmlField("Temperature", source="child"),
                                    XmlField("TemperatureType", source="child"),
                                    XmlField("DelayTime", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetSuccess",
                )
            ),
        ),
        result=AlarmZones,
        access="viewer",
        effect="read",
    )
    get_zone_status = Operation(
        INFO,
        "get_zone_status",
        CgiBinding(
            "/axis-cgi/temperature_alarm/getzonestatus.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "AlarmZone",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("ZoneId", source="child"),
                                    XmlField("AverageTemperature", source="child"),
                                    XmlField("MinimumTemperature", source="child"),
                                    XmlField("MaximumTemperature", source="child"),
                                    XmlField("Triggered", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetZoneStatusSuccess",
                )
            ),
        ),
        result=AlarmZoneStatuses,
        access="viewer",
        effect="read",
    )
    remove_zone = Operation(
        INFO,
        "remove_zone",
        CgiBinding("/axis-cgi/temperature_alarm/remove.cgi", args=(CgiArg("id"),), reply=Xml()),
        params=RemoveZoneRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    get_spot_temperature = Operation(
        INFO,
        "get_spot_temperature",
        CgiBinding(
            "/axis-cgi/temperature_alarm/getspottemperature.cgi",
            args=(CgiArg("coordinates", style="csv"), CgiArg("emissivity")),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("SpotTemperature", source="child"),), root="Success/GetSpotTemperatureSuccess"
                )
            ),
        ),
        params=GetSpotTemperatureRequest,
        result=SpotTemperature,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class TemperatureAlarmApi(SyncApi):
    """Temperature alarm API (``temperature-alarm``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: viewer."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def set_temperature_scale(
        self, unit: Literal["Celsius", "Fahrenheit"], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the temperature scale to Celsius or Fahrenheit (also used by the Isotherm API).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_temperature_scale, None, {"unit": unit}, request_options)

    @overload
    def set_zone(self, request: SetZoneRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_zone(
        self,
        id: int,
        /,
        *,
        name: str | MISSING = MISSING,
        left: int | MISSING = MISSING,
        right: int | MISSING = MISSING,
        top: int | MISSING = MISSING,
        bottom: int | MISSING = MISSING,
        emissivity: float | MISSING = MISSING,
        detectiontype: DetectionType | MISSING = MISSING,
        temperature: int | MISSING = MISSING,
        temperaturetype: TemperatureType | MISSING = MISSING,
        delaytime: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_zone(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Create or update a temperature alarm zone.

        The zone is identified by its ID. Zone coordinates are those of the unrotated and unmirrored image,
        with (0,0) in the upper left corner. For detection types above and below, temperature is the
        threshold and delaytime the time between successive measurements. For increase, temperature is the
        change and delaytime the time window.

        Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetZoneRequest):
            kwargs = {**dict(zip(("id",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_zone, request, kwargs, request_options)

    def get_zones(self, *, request_options: RequestOptions | None = None) -> AlarmZones:
        """Retrieve all temperature alarm zones. Access: viewer."""
        return self._run(OPS.get_zones, None, {}, request_options)

    def get_zone_status(self, *, request_options: RequestOptions | None = None) -> AlarmZoneStatuses:
        """Retrieve the status of each temperature alarm zone.

        The status includes the average, minimum and maximum temperature of each zone and whether an alarm
        is triggered.

        Access: viewer.
        """
        return self._run(OPS.get_zone_status, None, {}, request_options)

    def remove_zone(self, id: int, *, request_options: RequestOptions | None = None) -> None:
        """Remove a temperature alarm zone. Access: operator."""
        self._run(OPS.remove_zone, None, {"id": id}, request_options)

    def get_spot_temperature(
        self,
        coordinates: list[Annotated[int, Field(ge=0, le=9999)]],
        *,
        emissivity: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SpotTemperature:
        """Retrieve the temperature at a point in the image. Access: viewer."""
        return self._run(
            OPS.get_spot_temperature, None, {"coordinates": coordinates, "emissivity": emissivity}, request_options
        )


class AsyncTemperatureAlarmApi(AsyncApi):
    """Temperature alarm API (``temperature-alarm``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: viewer."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def set_temperature_scale(
        self, unit: Literal["Celsius", "Fahrenheit"], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the temperature scale to Celsius or Fahrenheit (also used by the Isotherm API).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_temperature_scale, None, {"unit": unit}, request_options)

    @overload
    async def set_zone(self, request: SetZoneRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def set_zone(
        self,
        id: int,
        /,
        *,
        name: str | MISSING = MISSING,
        left: int | MISSING = MISSING,
        right: int | MISSING = MISSING,
        top: int | MISSING = MISSING,
        bottom: int | MISSING = MISSING,
        emissivity: float | MISSING = MISSING,
        detectiontype: DetectionType | MISSING = MISSING,
        temperature: int | MISSING = MISSING,
        temperaturetype: TemperatureType | MISSING = MISSING,
        delaytime: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_zone(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Create or update a temperature alarm zone.

        The zone is identified by its ID. Zone coordinates are those of the unrotated and unmirrored image,
        with (0,0) in the upper left corner. For detection types above and below, temperature is the
        threshold and delaytime the time between successive measurements. For increase, temperature is the
        change and delaytime the time window.

        Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetZoneRequest):
            kwargs = {**dict(zip(("id",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_zone, request, kwargs, request_options)

    async def get_zones(self, *, request_options: RequestOptions | None = None) -> AlarmZones:
        """Retrieve all temperature alarm zones. Access: viewer."""
        return await self._run(OPS.get_zones, None, {}, request_options)

    async def get_zone_status(self, *, request_options: RequestOptions | None = None) -> AlarmZoneStatuses:
        """Retrieve the status of each temperature alarm zone.

        The status includes the average, minimum and maximum temperature of each zone and whether an alarm
        is triggered.

        Access: viewer.
        """
        return await self._run(OPS.get_zone_status, None, {}, request_options)

    async def remove_zone(self, id: int, *, request_options: RequestOptions | None = None) -> None:
        """Remove a temperature alarm zone. Access: operator."""
        await self._run(OPS.remove_zone, None, {"id": id}, request_options)

    async def get_spot_temperature(
        self,
        coordinates: list[Annotated[int, Field(ge=0, le=9999)]],
        *,
        emissivity: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> SpotTemperature:
        """Retrieve the temperature at a point in the image. Access: viewer."""
        return await self._run(
            OPS.get_spot_temperature, None, {"coordinates": coordinates, "emissivity": emissivity}, request_options
        )
