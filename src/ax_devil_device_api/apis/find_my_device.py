# GENERATED from specs/apis/network-video/findmydevice.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Locate an Axis device, for instance by playing a sound or flashing a status LED.

Docs: https://developer.axis.com/vapix/network-video/find-my-device/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class FindRequest(Model):
    duration: int | None = Field(default=None, le=3600)
    """How long the search sequence lasts, in seconds, at most 3600."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/findmydevice.cgi"

INFO = ApiInfo(
    id="findmydevice",
    name="Find my device",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1)),
    discovery=(ApiDiscovery("findmydevice"),),
    docs=("https://developer.axis.com/vapix/network-video/find-my-device/",),
    errors={
        1100: ErrorCode("Internal error. Out-of-memory errors will also return this error code.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON format.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing or invalid.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2200: ErrorCode("Transport layer error (e.g. request not HTTP POST)."),
        2201: ErrorCode("Busy, already performing method.", "unavailable"),
    },
)


class OPS:
    find = Operation(INFO, "find", JsonRpcBinding("find", PATH), params=FindRequest, access="admin", effect="action")
    stop = Operation(INFO, "stop", JsonRpcBinding("stop", PATH), access="admin", effect="action")


# ---------------------------------------------------------------------------
# API classes


class FindMyDeviceApi(SyncApi):
    """Find my device (``findmydevice``, version 1)."""

    INFO = INFO

    def find(self, *, duration: int | MISSING = MISSING, request_options: RequestOptions | None = None) -> None:
        """Start the mechanism that locates the device.

        The identification methods (sound, LED) depend on the device. Using them while another API uses the
        same functions can cause unexpected behavior.

        Access: admin.
        """
        self._run(OPS.find, None, {"duration": duration}, request_options)

    def stop(self, *, request_options: RequestOptions | None = None) -> None:
        """Halt the mechanism that locates the device during a duration period set by find.

        Access: admin.
        """
        self._run(OPS.stop, None, {}, request_options)


class AsyncFindMyDeviceApi(AsyncApi):
    """Find my device (``findmydevice``, version 1)."""

    INFO = INFO

    async def find(self, *, duration: int | MISSING = MISSING, request_options: RequestOptions | None = None) -> None:
        """Start the mechanism that locates the device.

        The identification methods (sound, LED) depend on the device. Using them while another API uses the
        same functions can cause unexpected behavior.

        Access: admin.
        """
        await self._run(OPS.find, None, {"duration": duration}, request_options)

    async def stop(self, *, request_options: RequestOptions | None = None) -> None:
        """Halt the mechanism that locates the device during a duration period set by find.

        Access: admin.
        """
        await self._run(OPS.stop, None, {}, request_options)
