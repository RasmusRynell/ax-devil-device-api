# GENERATED from specs/apis/network-video/audit-log.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve the audit log (entire or tail) and the version of /axis-cgi/auditlog.cgi.

Docs: https://developer.axis.com/vapix/network-video/audit-log/
"""

from __future__ import annotations

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, Text
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class GetAuditLogRequest(Model):
    tail: int | None = None
    """The number of recent entries that should be retrieved (from the tail end of the log). All entries will be retrieved if this parameter is not specified."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/auditlog.cgi"

INFO = ApiInfo(
    id="audit-log",
    name="Audit log",
    family=Family.CGI,
    discovery=(ApiDiscovery("audit-log"),),
    docs=("https://developer.axis.com/vapix/network-video/audit-log/",),
)


class OPS:
    get_audit_log = Operation(
        INFO,
        "get_audit_log",
        CgiBinding(PATH, args=(CgiArg("tail"),), reply=Text()),
        params=GetAuditLogRequest,
        result=str,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode("An invalid request method was provided.", "invalid_argument"),
            401: ErrorCode("The user was unauthorized.", "access_denied"),
            500: ErrorCode("Some unexpected error occurred.", "internal"),
        },
    )
    get_cgi_version = Operation(
        INFO,
        "get_cgi_version",
        CgiBinding(PATH, fixed_query=(("version", "true"),), reply=Text()),
        result=str,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode("An invalid request method was provided.", "invalid_argument"),
            401: ErrorCode("The user was unauthorized.", "access_denied"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class AuditLogApi(SyncApi):
    """Audit log (``audit-log``)."""

    INFO = INFO

    def get_audit_log(self, tail: int | MISSING = MISSING, *, request_options: RequestOptions | None = None) -> str:
        """Request a list of the entire audit log, or the tail end of it. Access: admin."""
        return self._run(OPS.get_audit_log, None, {"tail": tail}, request_options)

    def get_cgi_version(self, *, request_options: RequestOptions | None = None) -> str:
        """Check the current CGI version. Access: admin."""
        return self._run(OPS.get_cgi_version, None, {}, request_options)


class AsyncAuditLogApi(AsyncApi):
    """Audit log (``audit-log``)."""

    INFO = INFO

    async def get_audit_log(
        self, tail: int | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> str:
        """Request a list of the entire audit log, or the tail end of it. Access: admin."""
        return await self._run(OPS.get_audit_log, None, {"tail": tail}, request_options)

    async def get_cgi_version(self, *, request_options: RequestOptions | None = None) -> str:
        """Check the current CGI version. Access: admin."""
        return await self._run(OPS.get_cgi_version, None, {}, request_options)
