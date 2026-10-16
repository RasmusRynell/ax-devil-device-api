# GENERATED from specs/apis/network-video/capture-mode.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Retrieve the current and available capture modes (image sensor settings) per channel and set the capture mode for a channel.

Docs: https://developer.axis.com/vapix/network-video/capture-mode/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import FixedVersion, JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class CaptureMode(Model):
    capture_mode_id: int = Field(validation_alias="captureModeId", serialization_alias="captureModeId")
    """The value/identifier to use when calling setCaptureMode to set this capture mode."""
    enabled: bool
    """True if this is the current capture mode, otherwise false."""
    max_fps: float | None = Field(default=None, validation_alias="maxFPS", serialization_alias="maxFPS")
    """Max frames per second. Optional; guaranteed to exist only if enabled is true."""
    description: str
    """Friendly description of this capture mode."""


class ChannelCaptureModes(Model):
    channel: int
    """Channel index."""
    capture_mode: list[CaptureMode] = Field(validation_alias="captureMode", serialization_alias="captureMode")


class SetCaptureModeRequest(Model):
    channel: int
    """The index number of the channel. Top-level request key (not under params)."""
    capture_mode_id: int = Field(validation_alias="captureModeId", serialization_alias="captureModeId")
    """The index number of the capture mode (captureModeId from getCaptureModes)."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/capturemode.cgi"

INFO = ApiInfo(
    id="capture-mode",
    name="Capture mode",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    requires_firmware="8.50",
    docs=("https://developer.axis.com/vapix/network-video/capture-mode/",),
    errors={
        2000: ErrorCode("Resource allocation failed. Check log for details.", "unavailable"),
        4000: ErrorCode("Invalid JSON format. Check message field for details.", "invalid_argument"),
        4001: ErrorCode(
            "Parameter not found or invalid value/format. Check message field for details.", "invalid_argument"
        ),
        8000: ErrorCode("Internal error. Check log for details.", "internal"),
    },
)


class OPS:
    get_capture_modes = Operation(
        INFO,
        "get_capture_modes",
        JsonRpcBinding(
            "getCaptureModes", PATH, negotiation=FixedVersion(ApiVersion(1, 0)), params_placement="top_level"
        ),
        result=list[ChannelCaptureModes],
        access="viewer",
        effect="read",
    )
    set_capture_mode = Operation(
        INFO,
        "set_capture_mode",
        JsonRpcBinding(
            "setCaptureMode", PATH, negotiation=FixedVersion(ApiVersion(1, 0)), params_placement="top_level"
        ),
        params=SetCaptureModeRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class CaptureModeApi(SyncApi):
    """Capture mode (``capture-mode``, version 1)."""

    INFO = INFO

    def get_capture_modes(self, *, request_options: RequestOptions | None = None) -> list[ChannelCaptureModes]:
        """Get current and available capture modes for each channel. Access: viewer."""
        return self._run(OPS.get_capture_modes, None, {}, request_options)

    def set_capture_mode(
        self, *, channel: int, capture_mode_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set a capture mode for one channel.

        The new capture mode takes effect only after a reboot.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_capture_mode, None, {"channel": channel, "capture_mode_id": capture_mode_id}, request_options)


class AsyncCaptureModeApi(AsyncApi):
    """Capture mode (``capture-mode``, version 1)."""

    INFO = INFO

    async def get_capture_modes(self, *, request_options: RequestOptions | None = None) -> list[ChannelCaptureModes]:
        """Get current and available capture modes for each channel. Access: viewer."""
        return await self._run(OPS.get_capture_modes, None, {}, request_options)

    async def set_capture_mode(
        self, *, channel: int, capture_mode_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set a capture mode for one channel.

        The new capture mode takes effect only after a reboot.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_capture_mode, None, {"channel": channel, "capture_mode_id": capture_mode_id}, request_options
        )
