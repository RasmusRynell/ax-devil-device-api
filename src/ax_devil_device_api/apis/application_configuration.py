# GENERATED from specs/apis/applications/application-configuration-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Obsolete vaconfig.cgi API: get the XML configuration of Axis-developed applications (for example Video Motion Detection and Cross Line Detection) and list installed applications.

Docs: https://developer.axis.com/vapix/applications/application-configuration-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
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
    segment: list[Point] | None = None
    """End points of a virtual line (geometry.segment); empty for other object types."""
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
    """Application configuration. Most parts define how the application runs and should not be modified."""

    version: str | None = None
    """Version of the configuration format."""
    application: Application | None = None


class InstalledApplication(Model):
    name: str
    """Application name."""


class ApplicationList(Model):
    applications: list[InstalledApplication] | None = None


class GetConfigurationRequest(Model):
    name: str
    """Application name."""


class ModifyConfigurationRequest(Model):
    name: str
    """The application name."""
    config: str
    """The <config version="1.0"> XML document holding the <application> configuration."""


class GetRtspStreamWithEventTopicFilterRequest(Model):
    video: bool | None = None
    """Whether video is available in the stream."""
    event: Literal["on", "off"] | None = None
    """Whether event metadata is included in the stream."""
    eventtopic: str | None = None
    """The event topic filter to include."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/vaconfig.cgi"

INFO = ApiInfo(
    id="application-configuration-api",
    name="Application configuration API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.EmbeddedDevelopment.Version", "1.00", ">="),),
    status="deprecated",
    requires_firmware="5.11",
    docs=("https://developer.axis.com/vapix/applications/application-configuration-api/",),
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
            fixed_query=(("action", "get"),),
            args=(CgiArg("name"),),
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
                                                                            "segment",
                                                                            source="path",
                                                                            name="segment/point",
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
        params=GetConfigurationRequest,
        result=ApplicationConfig,
        access="admin",
        effect="read",
    )
    list_applications = Operation(
        INFO,
        "list_applications",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "applications",
                            source="path",
                            name="application",
                            many=True,
                            nested=XmlMap(fields=(XmlField("name"),)),
                        ),
                    )
                ),
                status_error=XmlStatusError(attribute="result", value="error"),
            ),
        ),
        result=ApplicationList,
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
            fixed_query=(("action", "modify"),),
            content_type="text/xml",
            args=(CgiArg("name"),),
            body_field="config",
            reply=Xml(status_error=XmlStatusError(attribute="result", value="error")),
        ),
        params=ModifyConfigurationRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    get_rtsp_stream_with_event_topic_filter = Operation(
        INFO,
        "get_rtsp_stream_with_event_topic_filter",
        RtspBinding(),
        params=GetRtspStreamWithEventTopicFilterRequest,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class ApplicationConfigurationApi(SyncApi):
    """Application configuration API (``application-configuration-api``)."""

    INFO = INFO

    def get_configuration(self, name: str, *, request_options: RequestOptions | None = None) -> ApplicationConfig:
        """Retrieve the configuration of an application.

        Obsolete; removed in AXIS OS 12.0. The configuration of a particular application is described in
        that application's API documentation.

        Access: admin.
        """
        return self._run(OPS.get_configuration, None, {"name": name}, request_options)

    def list_applications(self, *, request_options: RequestOptions | None = None) -> ApplicationList:
        """List the installed applications.

        Obsolete; removed in AXIS OS 12.0. Replaced by /axis-cgi/applications/list.cgi in the Application
        API.

        Access: admin.
        """
        return self._run(OPS.list_applications, None, {}, request_options)

    def modify_configuration(self, name: str, config: str, *, request_options: RequestOptions | None = None) -> None:
        """Modify the configuration of an application.

        Obsolete; removed in AXIS OS 12.0. Posts the application's <config version="1.0"> XML. The device
        answers with a failure reply only if the request failed.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.modify_configuration, None, {"name": name, "config": config}, request_options)

    def get_rtsp_stream_with_event_topic_filter(
        self,
        *,
        video: bool | MISSING = MISSING,
        event: Literal["on", "off"] | MISSING = MISSING,
        eventtopic: str | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with an event topic filter.

        Builds the URL only. Event topic filters: AXIS Video Motion Detection 3
        ``onvif:RuleEngine/axis:VMD3//.``, Video Motion Detection 2.1
        ``onvif:RuleEngine/axis:VideoMotionDetection//motion``, Digital Autotracking
        ``onvif:RuleEngine/axis:DigitalAutotracking/tracking//.``, Cross Line Detection 1.1
        ``onvif:RuleEngine/axis:CrossLineDetection//.``. For more arguments see the RTSP URL parameters of
        the Video streaming API.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_event_topic_filter,
            {"video": video, "event": event, "eventtopic": eventtopic},
            port=port,
            include_credentials=include_credentials,
        )


class AsyncApplicationConfigurationApi(AsyncApi):
    """Application configuration API (``application-configuration-api``)."""

    INFO = INFO

    async def get_configuration(self, name: str, *, request_options: RequestOptions | None = None) -> ApplicationConfig:
        """Retrieve the configuration of an application.

        Obsolete; removed in AXIS OS 12.0. The configuration of a particular application is described in
        that application's API documentation.

        Access: admin.
        """
        return await self._run(OPS.get_configuration, None, {"name": name}, request_options)

    async def list_applications(self, *, request_options: RequestOptions | None = None) -> ApplicationList:
        """List the installed applications.

        Obsolete; removed in AXIS OS 12.0. Replaced by /axis-cgi/applications/list.cgi in the Application
        API.

        Access: admin.
        """
        return await self._run(OPS.list_applications, None, {}, request_options)

    async def modify_configuration(
        self, name: str, config: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Modify the configuration of an application.

        Obsolete; removed in AXIS OS 12.0. Posts the application's <config version="1.0"> XML. The device
        answers with a failure reply only if the request failed.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.modify_configuration, None, {"name": name, "config": config}, request_options)

    def get_rtsp_stream_with_event_topic_filter(
        self,
        *,
        video: bool | MISSING = MISSING,
        event: Literal["on", "off"] | MISSING = MISSING,
        eventtopic: str | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with an event topic filter.

        Builds the URL only. Event topic filters: AXIS Video Motion Detection 3
        ``onvif:RuleEngine/axis:VMD3//.``, Video Motion Detection 2.1
        ``onvif:RuleEngine/axis:VideoMotionDetection//motion``, Digital Autotracking
        ``onvif:RuleEngine/axis:DigitalAutotracking/tracking//.``, Cross Line Detection 1.1
        ``onvif:RuleEngine/axis:CrossLineDetection//.``. For more arguments see the RTSP URL parameters of
        the Video streaming API.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_event_topic_filter,
            {"video": video, "event": event, "eventtopic": eventtopic},
            port=port,
            include_credentials=include_credentials,
        )
