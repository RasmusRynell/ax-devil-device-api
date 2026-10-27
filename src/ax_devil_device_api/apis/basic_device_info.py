# GENERATED from specs/apis/network-video/basic-device-info.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve simple identifying information about the product (brand, model, serial number, firmware version, ...).

Docs: https://developer.axis.com/vapix/network-video/basic-device-information/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import GetSupportedVersions, JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PropertyList(Model):
    """All properties of the device, by name. Which of them a device returns is product dependent, so all are optional."""

    architecture: str | None = Field(default=None, validation_alias="Architecture", serialization_alias="Architecture")
    brand: str | None = Field(default=None, validation_alias="Brand", serialization_alias="Brand")
    build_date: str | None = Field(default=None, validation_alias="BuildDate", serialization_alias="BuildDate")
    hardware_id: str | None = Field(default=None, validation_alias="HardwareID", serialization_alias="HardwareID")
    prod_full_name: str | None = Field(
        default=None, validation_alias="ProdFullName", serialization_alias="ProdFullName"
    )
    prod_nbr: str | None = Field(default=None, validation_alias="ProdNbr", serialization_alias="ProdNbr")
    prod_short_name: str | None = Field(
        default=None, validation_alias="ProdShortName", serialization_alias="ProdShortName"
    )
    prod_type: str | None = Field(default=None, validation_alias="ProdType", serialization_alias="ProdType")
    prod_variant: str | None = Field(default=None, validation_alias="ProdVariant", serialization_alias="ProdVariant")
    serial_number: str | None = Field(default=None, validation_alias="SerialNumber", serialization_alias="SerialNumber")
    soc: str | None = Field(default=None, validation_alias="Soc", serialization_alias="Soc")
    soc_serial_number: str | None = Field(
        default=None, validation_alias="SocSerialNumber", serialization_alias="SocSerialNumber"
    )
    version: str | None = Field(default=None, validation_alias="Version", serialization_alias="Version")
    web_url: str | None = Field(default=None, validation_alias="WebURL", serialization_alias="WebURL")


class UnrestrictedPropertyList(Model):
    """The properties anyone may read, also before a root user is defined."""

    brand: str | None = Field(default=None, validation_alias="Brand", serialization_alias="Brand")
    build_date: str | None = Field(default=None, validation_alias="BuildDate", serialization_alias="BuildDate")
    hardware_id: str | None = Field(default=None, validation_alias="HardwareID", serialization_alias="HardwareID")
    prod_full_name: str | None = Field(
        default=None, validation_alias="ProdFullName", serialization_alias="ProdFullName"
    )
    prod_nbr: str | None = Field(default=None, validation_alias="ProdNbr", serialization_alias="ProdNbr")
    prod_short_name: str | None = Field(
        default=None, validation_alias="ProdShortName", serialization_alias="ProdShortName"
    )
    prod_type: str | None = Field(default=None, validation_alias="ProdType", serialization_alias="ProdType")
    prod_variant: str | None = Field(default=None, validation_alias="ProdVariant", serialization_alias="ProdVariant")
    serial_number: str | None = Field(default=None, validation_alias="SerialNumber", serialization_alias="SerialNumber")
    version: str | None = Field(default=None, validation_alias="Version", serialization_alias="Version")
    web_url: str | None = Field(default=None, validation_alias="WebURL", serialization_alias="WebURL")


SelectedPropertyList = dict[str, str]


class AllProperties(Model):
    property_list: PropertyList = Field(validation_alias="propertyList", serialization_alias="propertyList")


class GetPropertiesRequest(Model):
    property_list: list[str] = Field(validation_alias="propertyList", serialization_alias="propertyList")
    """Specifies which properties should be returned with the response. If this field is empty an empty list will be returned."""


class SelectedProperties(Model):
    property_list: SelectedPropertyList = Field(validation_alias="propertyList", serialization_alias="propertyList")


class UnrestrictedProperties(Model):
    property_list: UnrestrictedPropertyList = Field(validation_alias="propertyList", serialization_alias="propertyList")


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/basicdeviceinfo.cgi"

INFO = ApiInfo(
    id="basic-device-info",
    name="Basic device information",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 2)),
    discovery=(ApiDiscovery("basic-device-info"), ParamDiscovery("BasicDeviceInfo.BasicDeviceInfo", "yes")),
    requires_firmware="8.40",
    docs=("https://developer.axis.com/vapix/network-video/basic-device-information/",),
    errors={
        1000: ErrorCode("Invalid parameter with the value specified.", "invalid_argument"),
        2001: ErrorCode("Access forbidden.", "access_denied"),
        2002: ErrorCode("HTTP request types are not supported. Only POST is supported.", "unsupported"),
        2003: ErrorCode("The requested API version is not supported.", "unsupported"),
        2004: ErrorCode("The method is not supported.", "unsupported"),
        4000: ErrorCode("Invalid JSON format.", "invalid_argument"),
        4002: ErrorCode("Required parameter is either missing or invalid.", "invalid_argument"),
        8000: ErrorCode("Internal error. Refer to the message field or logs.", "internal"),
    },
)


class OPS:
    get_all_properties = Operation(
        INFO,
        "get_all_properties",
        JsonRpcBinding("getAllProperties", PATH, negotiation=GetSupportedVersions(auth="if_challenged")),
        result=AllProperties,
        access="operator",
        effect="read",
    )
    get_properties = Operation(
        INFO,
        "get_properties",
        JsonRpcBinding("getProperties", PATH, negotiation=GetSupportedVersions(auth="if_challenged")),
        params=GetPropertiesRequest,
        result=SelectedProperties,
        access="operator",
        effect="read",
    )
    get_all_unrestricted_properties = Operation(
        INFO,
        "get_all_unrestricted_properties",
        JsonRpcBinding(
            "getAllUnrestrictedProperties",
            PATH,
            negotiation=GetSupportedVersions(auth="if_challenged"),
            auth="if_challenged",
        ),
        result=UnrestrictedProperties,
        access="anonymous",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class BasicDeviceInfoApi(SyncApi):
    """Basic device information (``basic-device-info``, version 1)."""

    INFO = INFO

    def get_all_properties(self, *, request_options: RequestOptions | None = None) -> AllProperties:
        """Retrieve all properties provided by the BDI service. Access: operator."""
        return self._run(OPS.get_all_properties, None, {}, request_options)

    def get_properties(
        self, *, property_list: list[str], request_options: RequestOptions | None = None
    ) -> SelectedProperties:
        """Retrieve a subset of the properties provided by the BDI service. Access: operator."""
        return self._run(OPS.get_properties, None, {"property_list": property_list}, request_options)

    def get_all_unrestricted_properties(
        self, *, request_options: RequestOptions | None = None
    ) -> UnrestrictedProperties:
        """Retrieve all unrestricted properties (usable before a root user is defined or without login).

        Access: anonymous.
        """
        return self._run(OPS.get_all_unrestricted_properties, None, {}, request_options)


class AsyncBasicDeviceInfoApi(AsyncApi):
    """Basic device information (``basic-device-info``, version 1)."""

    INFO = INFO

    async def get_all_properties(self, *, request_options: RequestOptions | None = None) -> AllProperties:
        """Retrieve all properties provided by the BDI service. Access: operator."""
        return await self._run(OPS.get_all_properties, None, {}, request_options)

    async def get_properties(
        self, *, property_list: list[str], request_options: RequestOptions | None = None
    ) -> SelectedProperties:
        """Retrieve a subset of the properties provided by the BDI service. Access: operator."""
        return await self._run(OPS.get_properties, None, {"property_list": property_list}, request_options)

    async def get_all_unrestricted_properties(
        self, *, request_options: RequestOptions | None = None
    ) -> UnrestrictedProperties:
        """Retrieve all unrestricted properties (usable before a root user is defined or without login).

        Access: anonymous.
        """
        return await self._run(OPS.get_all_unrestricted_properties, None, {}, request_options)
