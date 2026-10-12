# GENERATED from specs/apis/network-video/api-discovery.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve information about the public APIs (id, version, status, doc link, name) supported on the device.

Docs: https://developer.axis.com/vapix/network-video/api-discovery-service/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ApiStatus = Literal["released", "alpha", "beta", "deprecated"]


class ApiEntry(Model):
    """One public API supported by the device."""

    id: str
    """The API id, that together with the version forms an unique id."""
    version: str
    """The current API version."""
    status: ApiStatus
    doc_link: str | None = Field(default=None, validation_alias="docLink", serialization_alias="docLink")
    """HTTP link to documentation."""
    name: str | None = None
    """The name of the API."""


class GetApiListRequest(Model):
    id: str | None = Field(default=None, pattern="^[A-Za-z0-9_*?-]+$")
    """Provides the API id, that together with version forms a unique id. Supports globbing (* matches a string, ? one character). If omitted, the id filter defaults to no filtering (same as GLOB pattern *)."""
    version: str | None = Field(default=None, pattern="^[A-Za-z0-9_.*?-]+$")
    """Provides the API version. Supports globing. If omitted, defaults to no filtering (same as GLOB pattern *). If both params.id and params.version are omitted, params need not be provided."""


class ApiList(Model):
    api_list: list[ApiEntry] = Field(validation_alias="apiList", serialization_alias="apiList")


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/apidiscovery.cgi"

INFO = ApiInfo(
    id="api-discovery",
    name="API Discovery service",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ParamDiscovery("Properties.ApiDiscovery.ApiDiscovery", "yes"), ApiDiscovery("api-discovery")),
    docs=("https://developer.axis.com/vapix/network-video/api-discovery-service/",),
    errors={
        1000: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2002: ErrorCode("HTTP request type not supported. Only POST is supported.", "unsupported"),
        2003: ErrorCode("The requested API version is not supported.", "unsupported"),
        2004: ErrorCode("This method is not supported.", "unsupported"),
        4000: ErrorCode("Invalid JSON format.", "invalid_argument"),
        4002: ErrorCode("Required parameter missing or invalid.", "invalid_argument"),
        8000: ErrorCode("Internal error. Refer to message field or logs.", "internal"),
    },
)


class OPS:
    get_api_list = Operation(
        INFO,
        "get_api_list",
        JsonRpcBinding("getApiList", PATH),
        params=GetApiListRequest,
        result=ApiList,
        access="anonymous",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class ApiDiscoveryApi(SyncApi):
    """API Discovery service (``api-discovery``, version 1)."""

    INFO = INFO

    def get_api_list(
        self,
        *,
        id: str | MISSING = MISSING,
        version: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ApiList:
        """Retrieve all public APIs that are supported by the device, optionally filtered by id and/or version.

        Access: anonymous.
        """
        return self._run(OPS.get_api_list, None, {"id": id, "version": version}, request_options)


class AsyncApiDiscoveryApi(AsyncApi):
    """API Discovery service (``api-discovery``, version 1)."""

    INFO = INFO

    async def get_api_list(
        self,
        *,
        id: str | MISSING = MISSING,
        version: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ApiList:
        """Retrieve all public APIs that are supported by the device, optionally filtered by id and/or version.

        Access: anonymous.
        """
        return await self._run(OPS.get_api_list, None, {"id": id, "version": version}, request_options)
