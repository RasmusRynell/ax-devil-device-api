# GENERATED from specs/apis/network-video/ssh.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve and configure (enable/disable) the SSH function on an Axis device.

Docs: https://developer.axis.com/vapix/network-video/ssh/
"""

from __future__ import annotations

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SshInfo(Model):
    """State of the SSH functionality."""

    enabled: bool
    """``true``: SSH is enabled and running. ``false``: disabled and not running."""


class SetSshConfigurationRequest(Model):
    enabled: bool
    """Desired state. ``true``: enabled and running. ``false``: disabled and not running."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/ssh.cgi"

INFO = ApiInfo(
    id="ssh",
    name="SSH",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("ssh"),),
    docs=("https://developer.axis.com/vapix/network-video/ssh/",),
    errors={
        1000: ErrorCode("Internal error", "internal"),
        2000: ErrorCode("Invalid request", "invalid_argument"),
        2001: ErrorCode("Request body too large", "invalid_argument"),
        3000: ErrorCode("Invalid JSON data", "invalid_argument"),
        4000: ErrorCode("Method does not exist", "not_found"),
        4001: ErrorCode("The specified version is not supported", "unsupported"),
        4002: ErrorCode("Authorization failed", "access_denied"),
        4003: ErrorCode("Missing parameter(s)", "invalid_argument"),
        4004: ErrorCode("Invalid parameter(s)", "invalid_argument"),
    },
)


class OPS:
    get_ssh_info = Operation(
        INFO, "get_ssh_info", JsonRpcBinding("getSshInfo", PATH), result=SshInfo, access="admin", effect="read"
    )
    set_ssh_configuration = Operation(
        INFO,
        "set_ssh_configuration",
        JsonRpcBinding("setSshConfiguration", PATH),
        params=SetSshConfigurationRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SshApi(SyncApi):
    """SSH (``ssh``, version 1)."""

    INFO = INFO

    def get_ssh_info(self, *, request_options: RequestOptions | None = None) -> SshInfo:
        """Retrieve the SSH configuration (enabled/disabled). Access: admin."""
        return self._run(OPS.get_ssh_info, None, {}, request_options)

    def set_ssh_configuration(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the SSH functionality. Changes only the fields given. Access: admin."""
        self._run(OPS.set_ssh_configuration, None, {"enabled": enabled}, request_options)


class AsyncSshApi(AsyncApi):
    """SSH (``ssh``, version 1)."""

    INFO = INFO

    async def get_ssh_info(self, *, request_options: RequestOptions | None = None) -> SshInfo:
        """Retrieve the SSH configuration (enabled/disabled). Access: admin."""
        return await self._run(OPS.get_ssh_info, None, {}, request_options)

    async def set_ssh_configuration(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the SSH functionality. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_ssh_configuration, None, {"enabled": enabled}, request_options)
