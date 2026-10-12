# GENERATED from specs/apis/network-video/systemready.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Find out, without authentication, whether the device is ready to handle external communication, configuration and video streaming.

Docs: https://developer.axis.com/vapix/network-video/systemready-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SystemreadyRequest(Model):
    timeout: int | None = Field(default=None, ge=0)
    """Maximum time in seconds the call waits for the system to become ready before answering."""


class SystemreadyResult(Model):
    systemready: Literal["yes", "no"]
    needsetup: Literal["yes", "no"]
    uptime: str | None = None
    """Seconds since boot, as a string."""
    bootid: str | None = None
    previewmode: str | None = None
    """Preview mode duration in seconds; only present when preview mode is enabled."""
    passphrasepolicy: Literal["none", "length", "complex"] | None = None


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/systemready.cgi"

INFO = ApiInfo(
    id="systemready",
    name="Systemready API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1), ApiVersion(1, 4)),
    discovery=(ApiDiscovery("systemready"),),
    docs=("https://developer.axis.com/vapix/network-video/systemready-api/",),
    errors={
        1000: ErrorCode("Internal error. Refer to message field or logs.", "internal"),
        9000: ErrorCode("Internal error.", "internal"),
    },
)


class OPS:
    systemready = Operation(
        INFO,
        "systemready",
        JsonRpcBinding("systemready", PATH),
        params=SystemreadyRequest,
        result=SystemreadyResult,
        access="anonymous",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class SystemreadyApi(SyncApi):
    """Systemready API (``systemready``, version 1)."""

    INFO = INFO

    def systemready(
        self, *, timeout: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> SystemreadyResult:
        """Check if the system is ready for operation. Access: anonymous."""
        return self._run(OPS.systemready, None, {"timeout": timeout}, request_options)


class AsyncSystemreadyApi(AsyncApi):
    """Systemready API (``systemready``, version 1)."""

    INFO = INFO

    async def systemready(
        self, *, timeout: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> SystemreadyResult:
        """Check if the system is ready for operation. Access: anonymous."""
        return await self._run(OPS.systemready, None, {"timeout": timeout}, request_options)
