# GENERATED from specs/apis/applications/digital-autotracking.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read the configuration of the AXIS Digital Autotracking ACAP (view area, include and exclude areas, ignore filters) via vaconfig.cgi.

Docs: https://developer.axis.com/vapix/applications/digital-autotracking-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import AcapDiscovery, ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.cgi import CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap, XmlStatusError
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Point(Model):
    x: float
    """X coordinate, -1.0 to 1.0. The top right corner of the camera view is x=1.0, y=1.0."""
    y: float
    """Y coordinate, -1.0 to 1.0."""


class IntValue(Model):
    value: int


class NamedObjectData(Model):
    known_name_type: str | None = Field(
        default=None, validation_alias="knownNameType", serialization_alias="knownNameType"
    )
    """Type of the data, for example geometry.polygon or core.int. The docs' attribute table spells it knownTypeName."""
    polygon: list[Point] | None = None
    """Corner points of a polygon object; empty for other object types."""
    integer: IntValue | None = Field(default=None, validation_alias="int", serialization_alias="int")
    """Integer data of a core.int object, such as a filter value or a view area number."""


class NamedObject(Model):
    name: str
    """Name of the object. Rule parameters refer to it by this name."""
    data: NamedObjectData | None = None


class RuleParameter(Model):
    name: str
    """Name of a parameter used by the rule function."""
    value: str
    """Value of the parameter; the name of the named object to use."""


class Rule(Model):
    name: str
    """Name of the rule."""
    function: str | None = None
    """Name of the rule function, defined in a script file."""
    parameters: list[RuleParameter] | None = Field(
        default=None, validation_alias="parameter", serialization_alias="parameter"
    )


class Script(Model):
    name: str | None = None
    """Name of the script file."""
    encryption: Literal["0", "1"] | None = None
    """1 = the script is encrypted, 0 = not encrypted."""


class EventAttribute(Model):
    key: str | None = None
    nicename: str | None = None
    tag: Literal["source", "data", "property-state"] | None = None
    """source = source info of the event metadata, data = data info, property-state = stateful event (0 or 1)."""
    value: str | None = None


class Event(Model):
    name: str
    """Name of an event emitted by the application."""
    nicename: str | None = None
    attributes: list[EventAttribute] | None = Field(default=None, validation_alias="attr", serialization_alias="attr")


class MoteOption(Model):
    name: str
    """Option name: boundingBox, polygon or velocity."""
    value: Literal["true", "false"]


class NameValue(Model):
    name: str | None = None
    value: str | None = None


class Library(Model):
    name: str | None = None


class RuleEngine(Model):
    status: Literal["enabled", "disabled"] | None = None
    """Whether the AXIS OS parses this configuration (AXIS OS 5.61 and later)."""
    named_objects: list[NamedObject] | None = Field(
        default=None, validation_alias="namedObjects", serialization_alias="namedObjects"
    )
    """All named objects used by the application."""
    rules: list[Rule] | None = None
    """All rules used by the application."""
    scripts: list[Script] | None = None
    events: list[Event] | None = None
    analytic_sources: list[NameValue] | None = Field(
        default=None, validation_alias="analyticSources", serialization_alias="analyticSources"
    )
    mote_config: list[MoteOption] | None = Field(
        default=None, validation_alias="moteConfig", serialization_alias="moteConfig"
    )
    """MOTE configuration options."""
    libraries: list[Library] | None = None


class Application(Model):
    name: str
    """Name of the application."""
    nicename: str | None = None
    rule_engine: RuleEngine | None = Field(
        default=None, validation_alias="ruleEngine", serialization_alias="ruleEngine"
    )


class ApplicationConfig(Model):
    version: str | None = None
    """Version of the configuration format."""
    application: Application | None = None


class ModifyConfigurationRequest(Model):
    configuration: str
    """The complete configuration document to apply (the application element, or the config element around it, as returned by get_configuration), edited as described above. All settings that are not to change must be kept as is."""


class EventStreamUrlRequest(Model):
    video: int | None = None
    """Video source number (the documented example uses 0)."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/vaconfig.cgi"

INFO = ApiInfo(
    id="digital-autotracking",
    name="Digital autotracking API",
    family=Family.CGI,
    discovery=(AcapDiscovery("DigitalAutotracking"),),
    docs=("https://developer.axis.com/vapix/applications/digital-autotracking-api/",),
    errors={
        "bad_request": ErrorCode("Bad request. The request URL was not formatted correctly.", "invalid_argument"),
        "no_such_application": ErrorCode("There is no application with the given name.", "not_found"),
        "internal": ErrorCode(
            "The action could not be performed, for example because the application failed to restart after a configuration modification.",
            "internal",
        ),
    },
)


class OPS:
    get_configuration = Operation(
        INFO,
        "get_configuration",
        CgiBinding(
            PATH,
            fixed_query=(("action", "get"), ("name", "DigitalAutotracking")),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("version"),
                        XmlField(
                            "application",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("name"),
                                    XmlField("nicename"),
                                    XmlField(
                                        "ruleEngine",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("status"),
                                                XmlField(
                                                    "namedObjects",
                                                    source="path",
                                                    name="namedObjects/namedObject",
                                                    many=True,
                                                    nested=XmlMap(
                                                        fields=(
                                                            XmlField("name"),
                                                            XmlField(
                                                                "data",
                                                                source="path",
                                                                nested=XmlMap(
                                                                    fields=(
                                                                        XmlField("knownNameType"),
                                                                        XmlField(
                                                                            "polygon",
                                                                            source="path",
                                                                            name="polygon/point",
                                                                            many=True,
                                                                            nested=XmlMap(
                                                                                fields=(XmlField("x"), XmlField("y"))
                                                                            ),
                                                                        ),
                                                                        XmlField(
                                                                            "int",
                                                                            source="path",
                                                                            nested=XmlMap(fields=(XmlField("value"),)),
                                                                        ),
                                                                    )
                                                                ),
                                                            ),
                                                        )
                                                    ),
                                                ),
                                                XmlField(
                                                    "rules",
                                                    source="path",
                                                    name="rules/rule",
                                                    many=True,
                                                    nested=XmlMap(
                                                        fields=(
                                                            XmlField("name"),
                                                            XmlField("function"),
                                                            XmlField(
                                                                "parameter",
                                                                source="path",
                                                                many=True,
                                                                nested=XmlMap(
                                                                    fields=(XmlField("name"), XmlField("value"))
                                                                ),
                                                            ),
                                                        )
                                                    ),
                                                ),
                                                XmlField(
                                                    "scripts",
                                                    source="path",
                                                    name="scripts/script",
                                                    many=True,
                                                    nested=XmlMap(
                                                        fields=(XmlField("name", source="text"), XmlField("encryption"))
                                                    ),
                                                ),
                                                XmlField(
                                                    "events",
                                                    source="path",
                                                    name="events/event",
                                                    many=True,
                                                    nested=XmlMap(
                                                        fields=(
                                                            XmlField("name"),
                                                            XmlField("nicename"),
                                                            XmlField(
                                                                "attr",
                                                                source="path",
                                                                many=True,
                                                                nested=XmlMap(
                                                                    fields=(
                                                                        XmlField("key"),
                                                                        XmlField("nicename"),
                                                                        XmlField("tag"),
                                                                        XmlField("value"),
                                                                    )
                                                                ),
                                                            ),
                                                        )
                                                    ),
                                                ),
                                                XmlField(
                                                    "analyticSources",
                                                    source="path",
                                                    name="analyticSources/analyticSource",
                                                    many=True,
                                                    nested=XmlMap(fields=(XmlField("name"), XmlField("value"))),
                                                ),
                                                XmlField(
                                                    "moteConfig",
                                                    source="path",
                                                    name="moteConfig/option",
                                                    many=True,
                                                    nested=XmlMap(fields=(XmlField("name"), XmlField("value"))),
                                                ),
                                                XmlField(
                                                    "libraries",
                                                    source="path",
                                                    name="libraries/library",
                                                    many=True,
                                                    nested=XmlMap(fields=(XmlField("name"),)),
                                                ),
                                            )
                                        ),
                                    ),
                                )
                            ),
                        ),
                    ),
                    root="config",
                ),
                status_error=XmlStatusError(attribute="result", value="error"),
            ),
        ),
        result=ApplicationConfig,
        access="admin",
        effect="read",
    )
    modify_configuration = Operation(
        INFO,
        "modify_configuration",
        CgiBinding(
            PATH,
            method="POST",
            encoding="body",
            fixed_query=(("action", "modify"), ("name", "DigitalAutotracking")),
            content_type="text/xml",
            body_field="configuration",
            reply=Xml(status_error=XmlStatusError(attribute="result", value="error")),
        ),
        params=ModifyConfigurationRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    event_stream_url = Operation(
        INFO,
        "event_stream_url",
        RtspBinding(
            fixed_query=(("event", "on"), ("eventtopic", "onvif:RuleEngine/axis:DigitalAutotracking/tracking//"))
        ),
        params=EventStreamUrlRequest,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class DigitalAutotrackingApi(SyncApi):
    """Digital autotracking API (``digital-autotracking``)."""

    INFO = INFO

    def get_configuration(self, *, request_options: RequestOptions | None = None) -> ApplicationConfig:
        """Retrieve the application configuration.

        Deprecated. Version 2 defines the view area, include area, exclude areas and the swaying, short-
        lived and small object filters as named objects; version 1 only has the view area, exclude areas and
        the swaying filter.

        Access: admin.
        """
        return self._run(OPS.get_configuration, None, {}, request_options)

    def modify_configuration(self, *, configuration: str, request_options: RequestOptions | None = None) -> None:
        """Modify the application configuration.

        Defines which view area to use, the size of the include area, exclude areas and the filter values;
        all other settings must be kept as is, and if a named object is renamed the matching parameter value
        must change too. Posts the XML as the raw request body with action and name in the URL, as the API
        syntax shows.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.modify_configuration, None, {"configuration": configuration}, request_options)

    def event_stream_url(
        self, *, video: int | MISSING = MISSING, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with event metadata.

        RTSP stream that carries the tracking event as metadata. The library only builds the URL; use an
        RTSP client to read the stream.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.event_stream_url, {"video": video}, port=port, include_credentials=include_credentials
        )


class AsyncDigitalAutotrackingApi(AsyncApi):
    """Digital autotracking API (``digital-autotracking``)."""

    INFO = INFO

    async def get_configuration(self, *, request_options: RequestOptions | None = None) -> ApplicationConfig:
        """Retrieve the application configuration.

        Deprecated. Version 2 defines the view area, include area, exclude areas and the swaying, short-
        lived and small object filters as named objects; version 1 only has the view area, exclude areas and
        the swaying filter.

        Access: admin.
        """
        return await self._run(OPS.get_configuration, None, {}, request_options)

    async def modify_configuration(self, *, configuration: str, request_options: RequestOptions | None = None) -> None:
        """Modify the application configuration.

        Defines which view area to use, the size of the include area, exclude areas and the filter values;
        all other settings must be kept as is, and if a named object is renamed the matching parameter value
        must change too. Posts the XML as the raw request body with action and name in the URL, as the API
        syntax shows.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.modify_configuration, None, {"configuration": configuration}, request_options)

    def event_stream_url(
        self, *, video: int | MISSING = MISSING, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with event metadata.

        RTSP stream that carries the tracking event as metadata. The library only builds the URL; use an
        RTSP client to read the stream.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.event_stream_url, {"video": video}, port=port, include_credentials=include_credentials
        )
