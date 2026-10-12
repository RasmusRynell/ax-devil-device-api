# GENERATED from specs/apis/network-video/oak.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve the Owner Authentication Key (OAK) used to authenticate the device owner towards the AXIS O3C Dispatcher service.

Docs: https://developer.axis.com/vapix/network-video/oak-api/
"""

from __future__ import annotations

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class OakResult(Model):
    oak: str
    """The owner authentication key."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/oak.cgi"

INFO = ApiInfo(
    id="oak",
    name="OAK API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("oak"),),
    docs=("https://developer.axis.com/vapix/network-video/oak-api/",),
    errors={
        1100: ErrorCode("Internal error.", "internal"),
        2000: ErrorCode("Invalid request.", "invalid_argument"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON data.", "invalid_argument"),
        2102: ErrorCode("Method does not exist.", "not_found"),
        2103: ErrorCode("Missing parameter method.", "invalid_argument"),
    },
)


class OPS:
    get_oak = Operation(
        INFO, "get_oak", JsonRpcBinding("getOAK", PATH), result=OakResult, access="admin", effect="read"
    )


# ---------------------------------------------------------------------------
# API classes


class OakApi(SyncApi):
    """OAK API (``oak``, version 1)."""

    INFO = INFO

    def get_oak(self, *, request_options: RequestOptions | None = None) -> OakResult:
        """Retrieve the product specific OAK.

        Needs unhindered internet access from the device; a proxy makes the call fail with error 1100.

        Access: admin.
        """
        return self._run(OPS.get_oak, None, {}, request_options)


class AsyncOakApi(AsyncApi):
    """OAK API (``oak``, version 1)."""

    INFO = INFO

    async def get_oak(self, *, request_options: RequestOptions | None = None) -> OakResult:
        """Retrieve the product specific OAK.

        Needs unhindered internet access from the device; a proxy makes the call fail with error 1100.

        Access: admin.
        """
        return await self._run(OPS.get_oak, None, {}, request_options)
