# GENERATED from specs/apis/network-video/geolocation.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Set and get the geographical position (latitude, longitude, heading, free text) of a device.

Docs: https://developer.axis.com/vapix/network-video/geolocation-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Coordinate = str
Heading = Annotated[int, Field(ge=0, le=360)]


class GeoLocation(Model):
    lat: Coordinate | None = Field(default=None, validation_alias="Lat", serialization_alias="Lat")
    lng: Coordinate | None = Field(default=None, validation_alias="Lng", serialization_alias="Lng")
    heading: Heading | None = Field(default=None, validation_alias="Heading", serialization_alias="Heading")


class Position(Model):
    """The position of the device. Default values (0 and an empty string) are returned when nothing is set."""

    location: GeoLocation | None = Field(default=None, validation_alias="Location", serialization_alias="Location")
    text: str | None = Field(default=None, validation_alias="Text", serialization_alias="Text")
    """Free text such as a location tag."""
    valid_position: bool | None = Field(
        default=None, validation_alias="ValidPosition", serialization_alias="ValidPosition"
    )
    """False when no geographical position is available or the data is outdated."""
    valid_heading: bool | None = Field(
        default=None, validation_alias="ValidHeading", serialization_alias="ValidHeading"
    )
    """False when no valid heading is available or the data is outdated."""


class SetPositionRequest(Model):
    lat: Coordinate | None = None
    """New value for latitude (WGS-84)."""
    lng: Coordinate | None = None
    """New value for longitude (WGS-84)."""
    heading: Heading | None = None
    """New value for heading."""
    text: str | None = None
    """New value for free text (location tag, e.g. "floor 2")."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/geolocation/get.cgi"

INFO = ApiInfo(
    id="geolocation",
    name="Geolocation API",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.Geolocation.Geolocation", "yes"),
        ParamDiscovery("Properties.Geolocation.Version", "0.01"),
    ),
    requires_firmware="6.25",
    docs=("https://developer.axis.com/vapix/network-video/geolocation-api/",),
)


class OPS:
    get_position = Operation(
        INFO,
        "get_position",
        CgiBinding(
            PATH,
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "Location",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("Lat", source="child"),
                                    XmlField("Lng", source="child"),
                                    XmlField("Heading", source="child"),
                                )
                            ),
                        ),
                        XmlField("Text", source="child"),
                        XmlField("ValidPosition", source="child"),
                        XmlField("ValidHeading", source="child"),
                    ),
                    root="Success/GetSuccess",
                )
            ),
        ),
        result=Position,
        access="admin",
        effect="read",
    )
    set_position = Operation(
        INFO,
        "set_position",
        CgiBinding(
            "/axis-cgi/geolocation/set.cgi",
            args=(CgiArg("lat"), CgiArg("lng"), CgiArg("heading"), CgiArg("text")),
            reply=Xml(error_elements=("Error",)),
        ),
        params=SetPositionRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            1: ErrorCode("Invalid parameter", "invalid_argument"),
            2: ErrorCode("Invalid value", "invalid_argument"),
            3: ErrorCode("Internal Error", "internal"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class GeolocationApi(SyncApi):
    """Geolocation API (``geolocation``)."""

    INFO = INFO

    def get_position(self, *, request_options: RequestOptions | None = None) -> Position:
        """Get the position (latitude, longitude, heading, free text) and its validity flags.

        Access: admin.
        """
        return self._run(OPS.get_position, None, {}, request_options)

    def set_position(
        self,
        *,
        lat: Coordinate | MISSING = MISSING,
        lng: Coordinate | MISSING = MISSING,
        heading: Heading | MISSING = MISSING,
        text: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set some or all of the position fields.

        Only the given fields change. The device stores coordinates as given, without conversion between DD,
        DDMM and DDMMSS.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_position, None, {"lat": lat, "lng": lng, "heading": heading, "text": text}, request_options)


class AsyncGeolocationApi(AsyncApi):
    """Geolocation API (``geolocation``)."""

    INFO = INFO

    async def get_position(self, *, request_options: RequestOptions | None = None) -> Position:
        """Get the position (latitude, longitude, heading, free text) and its validity flags.

        Access: admin.
        """
        return await self._run(OPS.get_position, None, {}, request_options)

    async def set_position(
        self,
        *,
        lat: Coordinate | MISSING = MISSING,
        lng: Coordinate | MISSING = MISSING,
        heading: Heading | MISSING = MISSING,
        text: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set some or all of the position fields.

        Only the given fields change. The device stores coordinates as given, without conversion between DD,
        DDMM and DDMMSS.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_position, None, {"lat": lat, "lng": lng, "heading": heading, "text": text}, request_options
        )
