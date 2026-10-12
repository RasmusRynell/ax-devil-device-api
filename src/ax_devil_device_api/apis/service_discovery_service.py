# GENERATED from specs/apis/physical-access-control/service-discovery-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Axis Discovery Service (axissd): polled API that searches for remote service providers (remote devices, e.g.

Docs: https://developer.axis.com/vapix/physical-access-control/peripherals/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Attribute(Model):
    """A name and value pair, used both to filter the search and to describe a provider or service."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Attribute name, for example `IO`, `Address`, `IP` or `MAC`."""
    type: str | None = None
    """Value type; `string` in every example."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """Attribute value."""


class Service(Model):
    """A service of an added provider, for example one remote I/O."""

    id: str | None = Field(default=None, validation_alias="Id", serialization_alias="Id")
    """Id of the service, in the form `remote/<device token>/<id>`; use it as `Lock.Hardware.Address` in the door control service."""
    nice_name: str | None = Field(default=None, validation_alias="NiceName", serialization_alias="NiceName")
    """Name of the service, for example `Output 1`."""
    attributes: list[Attribute] | None = Field(
        default=None, validation_alias="Attributes", serialization_alias="Attributes"
    )


class ServiceProvider(Model):
    """A remote device found on the network or added to the door controller."""

    id: str | None = Field(default=None, validation_alias="Id", serialization_alias="Id")
    """Empty for a device that is not added; the device token once it is added."""
    nice_name: str | None = Field(default=None, validation_alias="NiceName", serialization_alias="NiceName")
    """Name of the device, for example `AXIS A9188`; empty if not added."""
    status: str | None = Field(default=None, validation_alias="Status", serialization_alias="Status")
    """`NotAdded` for a device that is not added, `OK` for an added one. Other values are not documented."""
    attributes: list[Attribute] | None = Field(
        default=None, validation_alias="Attributes", serialization_alias="Attributes"
    )
    """Attributes of the device, `IP` and `MAC` in the examples."""
    service_list: list[Service] | None = Field(
        default=None, validation_alias="ServiceList", serialization_alias="ServiceList"
    )
    """The services (remote I/Os) of an added device; empty for a device that is not added."""


class GetServiceProviderListRequest(Model):
    timeout: int | None = Field(default=None, validation_alias="Timeout", serialization_alias="Timeout")
    """Discovery timeout; follow-up calls must come before it expires. The unit is not documented; the examples use 10."""
    type: str | None = Field(default=None, validation_alias="Type", serialization_alias="Type")
    """Type of service provider to search for; `RIO` for a remote I/O module such as AXIS A9188."""
    attributes: list[Attribute] | None = Field(
        default=None, validation_alias="Attributes", serialization_alias="Attributes"
    )
    """Search attributes: `IO` = `Eth0` for a remote I/O module, and `Address` = a device token, IP address or MAC address to limit the search to one added device."""


class ServiceProviderListResult(Model):
    service_provider_list: list[ServiceProvider] | None = Field(
        default=None, validation_alias="ServiceProviderList", serialization_alias="ServiceProviderList"
    )


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/axissd"

INFO = ApiInfo(
    id="service-discovery-service",
    name="Service discovery service",
    family=Family.SERVICE_JSON,
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
        "https://developer.axis.com/vapix/physical-access-control/",
    ),
)


class OPS:
    get_service_provider_list = Operation(
        INFO,
        "get_service_provider_list",
        ServiceJsonBinding(PATH, "axissd:GetServiceProviderList"),
        params=GetServiceProviderListRequest,
        result=ServiceProviderListResult,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class ServiceDiscoveryServiceApi(SyncApi):
    """Service discovery service (``service-discovery-service``)."""

    INFO = INFO

    @overload
    def get_service_provider_list(
        self, request: GetServiceProviderListRequest, /, *, request_options: RequestOptions | None = None
    ) -> ServiceProviderListResult: ...
    @overload
    def get_service_provider_list(
        self,
        /,
        *,
        timeout: int | MISSING = MISSING,
        type: str | MISSING = MISSING,
        attributes: list[Attribute] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ServiceProviderListResult: ...
    def get_service_provider_list(
        self,
        request: GetServiceProviderListRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ServiceProviderListResult:
        """Search for remote devices and list the ones already added with their services.

        A polled call: the first call starts the discovery and later calls, issued before `Timeout` expires,
        return the devices found so far, so call it several times to find every device. Added devices need
        not be on the local network.

        Access: admin.
        """
        return self._run(OPS.get_service_provider_list, request, kwargs, request_options)


class AsyncServiceDiscoveryServiceApi(AsyncApi):
    """Service discovery service (``service-discovery-service``)."""

    INFO = INFO

    @overload
    async def get_service_provider_list(
        self, request: GetServiceProviderListRequest, /, *, request_options: RequestOptions | None = None
    ) -> ServiceProviderListResult: ...
    @overload
    async def get_service_provider_list(
        self,
        /,
        *,
        timeout: int | MISSING = MISSING,
        type: str | MISSING = MISSING,
        attributes: list[Attribute] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ServiceProviderListResult: ...
    async def get_service_provider_list(
        self,
        request: GetServiceProviderListRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> ServiceProviderListResult:
        """Search for remote devices and list the ones already added with their services.

        A polled call: the first call starts the discovery and later calls, issued before `Timeout` expires,
        return the devices found so far, so call it several times to find every device. Added devices need
        not be on the local network.

        Access: admin.
        """
        return await self._run(OPS.get_service_provider_list, request, kwargs, request_options)
