# GENERATED from specs/apis/network-video/customhttpheader.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List, add (set) and remove custom HTTP headers added to the HTTP responses of the device's web server.

Docs: https://developer.axis.com/vapix/network-video/custom-http-header-api/
"""

from __future__ import annotations

from collections.abc import Mapping

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

HeaderMap = dict[str, str]


class SetHeadersRequest(Model):
    headers: dict[str, str]
    """Header name to header value."""


class RemoveHeadersRequest(Model):
    headers: dict[str, str]
    """Header name to header value; the value is not used to identify the header."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/customhttpheader.cgi"

INFO = ApiInfo(
    id="customhttpheader",
    name="Custom HTTP header API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("customhttpheader"),),
    requires_firmware="9.80",
    docs=("https://developer.axis.com/vapix/network-video/custom-http-header-api/",),
    errors={
        1100: ErrorCode("Internal error. Refer to message field or logs.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON format.", "invalid_argument"),
        2102: ErrorCode("Method does not exist.", "unsupported"),
    },
)


class OPS:
    list_headers = Operation(
        INFO, "list_headers", JsonRpcBinding("list", PATH), result=HeaderMap, access="admin", effect="read"
    )
    set_headers = Operation(
        INFO,
        "set_headers",
        JsonRpcBinding("set", PATH, params_field="headers"),
        params=SetHeadersRequest,
        result=HeaderMap,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_headers = Operation(
        INFO,
        "remove_headers",
        JsonRpcBinding("remove", PATH, params_field="headers"),
        params=RemoveHeadersRequest,
        result=HeaderMap,
        access="admin",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class CustomHttpHeaderApi(SyncApi):
    """Custom HTTP header API (``customhttpheader``, version 1)."""

    INFO = INFO

    def list_headers(self, *, request_options: RequestOptions | None = None) -> HeaderMap:
        """List the custom headers available on the device.

        Includes headers that come pre-installed on some devices.

        Access: admin.
        """
        return self._run(OPS.list_headers, None, {}, request_options)

    def set_headers(self, headers: Mapping[str, str], *, request_options: RequestOptions | None = None) -> HeaderMap:
        """Set one or more custom headers.

        Each entry is a header name and its value. Setting several headers in one call requires AXIS OS
        10.11. The headers are included in the responses of the web server once it has been restarted.
        Returns the headers that were set.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.set_headers, None, {"headers": dict(headers)}, request_options)

    def remove_headers(self, headers: Mapping[str, str], *, request_options: RequestOptions | None = None) -> HeaderMap:
        """Remove custom headers.

        The header is identified by its name, so the value is optional and can be omitted (pass an empty
        string). Pre-installed headers can be removed too. The headers are no longer included once the web
        server has been restarted. Returns the headers that were removed.

        Access: admin.
        """
        return self._run(OPS.remove_headers, None, {"headers": dict(headers)}, request_options)


class AsyncCustomHttpHeaderApi(AsyncApi):
    """Custom HTTP header API (``customhttpheader``, version 1)."""

    INFO = INFO

    async def list_headers(self, *, request_options: RequestOptions | None = None) -> HeaderMap:
        """List the custom headers available on the device.

        Includes headers that come pre-installed on some devices.

        Access: admin.
        """
        return await self._run(OPS.list_headers, None, {}, request_options)

    async def set_headers(
        self, headers: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> HeaderMap:
        """Set one or more custom headers.

        Each entry is a header name and its value. Setting several headers in one call requires AXIS OS
        10.11. The headers are included in the responses of the web server once it has been restarted.
        Returns the headers that were set.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.set_headers, None, {"headers": dict(headers)}, request_options)

    async def remove_headers(
        self, headers: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> HeaderMap:
        """Remove custom headers.

        The header is identified by its name, so the value is optional and can be omitted (pass an empty
        string). Pre-installed headers can be removed too. The headers are no longer included once the web
        server has been restarted. Returns the headers that were removed.

        Access: admin.
        """
        return await self._run(OPS.remove_headers, None, {"headers": dict(headers)}, request_options)
