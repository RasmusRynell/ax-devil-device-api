# GENERATED from specs/apis/network-video/entry-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Web services (SOAP) API to query the product for supported services, their XAddr, versions and capabilities.

Docs: https://developer.axis.com/vapix/network-video/entry-service-api/
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery, ServiceDiscovery
from .._protocols.soap import SoapBinding
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Version(Model):
    major: int = Field(validation_alias="Major", serialization_alias="Major")
    """Major version number (xs:int)."""
    minor: int = Field(validation_alias="Minor", serialization_alias="Minor")
    """Two digit minor version number (e.g. 1 maps to "01" and 20 maps to "20") (xs:int)."""


class Service(Model):
    namespace: str = Field(validation_alias="Namespace", serialization_alias="Namespace")
    """Namespace of the service being described. Allows matching the service capabilities to the service. Only one set of capabilities is supported per namespace. (format=uri)"""
    x_addr: str = Field(validation_alias="XAddr", serialization_alias="XAddr")
    """The transport address where the service can be reached. The schema and IP part shall match the one used in the GetServices request. Absolute URL; modify as required to support NAT. (format=uri)"""
    capabilities: Any | None = Field(default=None, validation_alias="Capabilities", serialization_alias="Capabilities")
    """Optional (minOccurs=0). Untyped placeholder (xs:any, lax) for the service capability element, e.g. tds:DeviceServiceCapabilities for the device service."""
    version: Version = Field(validation_alias="Version", serialization_alias="Version")


class GetServicesRequest(Model):
    include_capability: bool = Field(validation_alias="IncludeCapability", serialization_alias="IncludeCapability")
    """Indicates if the service capabilities (untyped) should be included in the response. GetServices(false) lists services without capabilities; GetServices(true) with."""


class GetServicesResult(Model):
    service: list[Service] | None = Field(default=None, validation_alias="Service", serialization_alias="Service")
    """minItems=1"""


class GetServiceCapabilitiesResult(Model):
    capabilities: Any | None = Field(default=None, validation_alias="Capabilities", serialization_alias="Capabilities")
    """aentry:Capabilities — empty sequence with anyAttribute (lax)."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/services"

INFO = ApiInfo(
    id="entry-service",
    name="Entry service API",
    family=Family.SOAP,
    discovery=(
        ParamDiscovery("Properties.API.WebService.EntryService", "yes"),
        ServiceDiscovery("http://www.axis.com/vapix/ws/entry"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/entry-service-api/",),
)


class OPS:
    get_services = Operation(
        INFO,
        "get_services",
        SoapBinding(
            "http://www.axis.com/vapix/ws/entry/GetServices",
            "GetServices",
            "http://www.axis.com/vapix/ws/entry",
            reply=XmlMap(
                fields=(
                    XmlField(
                        "Service",
                        source="path",
                        many=True,
                        nested=XmlMap(
                            fields=(
                                XmlField("Namespace", source="child"),
                                XmlField("XAddr", source="child"),
                                XmlField("Capabilities", source="child"),
                                XmlField(
                                    "Version",
                                    source="path",
                                    nested=XmlMap(
                                        fields=(XmlField("Major", source="child"), XmlField("Minor", source="child"))
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
            namespaces=(("aentry", "http://www.axis.com/vapix/ws/entry"),),
        ),
        params=GetServicesRequest,
        result=GetServicesResult,
        access="admin",
        effect="read",
    )
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        SoapBinding(
            "http://www.axis.com/vapix/ws/entry/GetServiceCapabilities",
            "GetServiceCapabilities",
            "http://www.axis.com/vapix/ws/entry",
            reply=XmlMap(fields=(XmlField("Capabilities", source="child"),)),
            namespaces=(("aentry", "http://www.axis.com/vapix/ws/entry"),),
        ),
        result=GetServiceCapabilitiesResult,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class EntryServiceApi(SyncApi):
    """Entry service API (``entry-service``)."""

    INFO = INFO

    def get_services(
        self, *, include_capability: bool, request_options: RequestOptions | None = None
    ) -> GetServicesResult:
        """Returns information about the services available in the Axis product (namespace, XAddr, version and optionally untyped capabilities).

        Access: admin.
        """
        return self._run(OPS.get_services, None, {"include_capability": include_capability}, request_options)

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Returns the capabilities supported by the entry service (typed answer). Access: admin."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)


class AsyncEntryServiceApi(AsyncApi):
    """Entry service API (``entry-service``)."""

    INFO = INFO

    async def get_services(
        self, *, include_capability: bool, request_options: RequestOptions | None = None
    ) -> GetServicesResult:
        """Returns information about the services available in the Axis product (namespace, XAddr, version and optionally untyped capabilities).

        Access: admin.
        """
        return await self._run(OPS.get_services, None, {"include_capability": include_capability}, request_options)

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Returns the capabilities supported by the entry service (typed answer). Access: admin."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)
