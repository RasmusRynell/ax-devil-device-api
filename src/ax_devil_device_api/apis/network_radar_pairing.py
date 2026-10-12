# GENERATED from specs/apis/radar/network-radar-pairing.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Pair a camera with a network-connected Axis radar so it appears as a built-in radar sensor.

Docs: https://developer.axis.com/vapix/radar/network-radar-pairing/
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

ConnectionState = Literal[
    "failed",
    "address-failed",
    "connect-failed",
    "authentication-failed",
    "transfer-failed",
    "not-configured",
    "not-active",
    "ok",
]


class RadarConnection(Model):
    """The network radar pairing configuration and state. The password is never returned."""

    address: str | None = None
    """The IP address."""
    user: str | None = None
    """The user name."""
    state: ConnectionState


class SetRadarConnectionRequest(Model):
    address: str
    """The IP address."""
    user: str
    """The user name."""
    password: str = Field(min_length=1, max_length=64)
    """The remote radar account password."""
    tls_certificate_cn: str | None = Field(
        default=None, validation_alias="tls-certificate-cn", serialization_alias="tls-certificate-cn"
    )
    """The common name for which the remote radar's certificate is issued."""


class GetActiveResult(Model):
    active: bool


class SetActiveRequest(Model):
    active: bool


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/networkradarpairing.cgi"

INFO = ApiInfo(
    id="network-radar-pairing",
    name="Network Radar Pairing",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("network-radar-pairing"),),
    docs=("https://developer.axis.com/vapix/radar/network-radar-pairing/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        2105: ErrorCode("Authorization failed", "access_denied"),
        2106: ErrorCode("Authentication failed", "access_denied"),
        2107: ErrorCode("Transport level error (HTTP 405, 411 or 413)", "invalid_argument"),
        2200: ErrorCode("Configuration cannot be changed or removed while enabled", "unavailable"),
        2201: ErrorCode("Missing configuration", "not_found"),
        2202: ErrorCode("Usability test of the configuration failed", "invalid_argument"),
    },
)


class OPS:
    get_radar_connection = Operation(
        INFO,
        "get_radar_connection",
        JsonRpcBinding("getRadarConnection", PATH),
        result=RadarConnection,
        access="admin",
        effect="read",
    )
    set_radar_connection = Operation(
        INFO,
        "set_radar_connection",
        JsonRpcBinding("setRadarConnection", PATH),
        params=SetRadarConnectionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    clear_configuration = Operation(
        INFO,
        "clear_configuration",
        JsonRpcBinding("clearConfiguration", PATH),
        access="admin",
        effect="write",
        write="delete",
    )
    get_active = Operation(
        INFO, "get_active", JsonRpcBinding("getActive", PATH), result=GetActiveResult, access="admin", effect="read"
    )
    set_active = Operation(
        INFO,
        "set_active",
        JsonRpcBinding("setActive", PATH),
        params=SetActiveRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class NetworkRadarPairingApi(SyncApi):
    """Network Radar Pairing (``network-radar-pairing``, version 1)."""

    INFO = INFO

    def get_radar_connection(self, *, request_options: RequestOptions | None = None) -> RadarConnection:
        """Retrieve the network radar pairing configuration and all of its setting information.

        Access: admin.
        """
        return self._run(OPS.get_radar_connection, None, {}, request_options)

    def set_radar_connection(
        self,
        *,
        address: str,
        user: str,
        password: str,
        tls_certificate_cn: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the network radar pairing configuration (radar address and credentials).

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_radar_connection,
            None,
            {"address": address, "user": user, "password": password, "tls_certificate_cn": tls_certificate_cn},
            request_options,
        )

    def clear_configuration(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear all stored configurations from the network radar pairing.

        Fails with error 2200 while the pairing is active.

        Access: admin.
        """
        self._run(OPS.clear_configuration, None, {}, request_options)

    def get_active(self, *, request_options: RequestOptions | None = None) -> GetActiveResult:
        """Retrieve the activation state of the network radar pairing.

        Fails with error 2201 if no configuration exists.

        Access: admin.
        """
        return self._run(OPS.get_active, None, {}, request_options)

    def set_active(self, *, active: bool, request_options: RequestOptions | None = None) -> None:
        """Activate (or deactivate) an already configured network radar pairing.

        Fails with error 2201 if no configuration exists. Succeeds if the active state already matches.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_active, None, {"active": active}, request_options)


class AsyncNetworkRadarPairingApi(AsyncApi):
    """Network Radar Pairing (``network-radar-pairing``, version 1)."""

    INFO = INFO

    async def get_radar_connection(self, *, request_options: RequestOptions | None = None) -> RadarConnection:
        """Retrieve the network radar pairing configuration and all of its setting information.

        Access: admin.
        """
        return await self._run(OPS.get_radar_connection, None, {}, request_options)

    async def set_radar_connection(
        self,
        *,
        address: str,
        user: str,
        password: str,
        tls_certificate_cn: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the network radar pairing configuration (radar address and credentials).

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_radar_connection,
            None,
            {"address": address, "user": user, "password": password, "tls_certificate_cn": tls_certificate_cn},
            request_options,
        )

    async def clear_configuration(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear all stored configurations from the network radar pairing.

        Fails with error 2200 while the pairing is active.

        Access: admin.
        """
        await self._run(OPS.clear_configuration, None, {}, request_options)

    async def get_active(self, *, request_options: RequestOptions | None = None) -> GetActiveResult:
        """Retrieve the activation state of the network radar pairing.

        Fails with error 2201 if no configuration exists.

        Access: admin.
        """
        return await self._run(OPS.get_active, None, {}, request_options)

    async def set_active(self, *, active: bool, request_options: RequestOptions | None = None) -> None:
        """Activate (or deactivate) an already configured network radar pairing.

        Fails with error 2201 if no configuration exists. Succeeds if the active state already matches.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_active, None, {"active": active}, request_options)
