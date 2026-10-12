# GENERATED from specs/apis/network-video/streamstatus.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List running (RTSP) streams on a device via /axis-cgi/streamstatus.cgi.

Docs: https://developer.axis.com/vapix/network-video/stream-status-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Stream(Model):
    """One running RTSP stream. Streams with inconsistent information are omitted by the device."""

    destination_address: str | None = None
    """The IPv4 or IPv6 address of the client."""
    destination_port: int | None = None
    """The port of the client."""
    direction: Literal["incoming", "outgoing"] | None = None
    """Direction of the stream."""
    encrypted: bool | None = None
    """Indicates whether the stream is encrypted or not."""
    id: int = Field(ge=1)
    """The ID of the stream. It should be one or greater than one."""
    media: Literal["audio", "metadata", "video"] | None = None
    """The media type."""
    mime: (
        Literal[
            "audio/mpeg",
            "application/x-onvif-metadata+xml",
            "video/x-h264",
            "audio/x-opus",
            "audio/x-adpcm",
            "audio/x-mulaw",
            "audio/x-raw",
            "image/jpeg",
            "video/x-h265",
        ]
        | None
    ) = None
    """The MIME type."""
    multicast: bool | None = None
    """Optional. Indicates whether the stream uses multicast or not."""
    options: dict[str, str] | None = None
    """Container for URL options in a stream request. See Video streaming public parameter description / RTSP URL parameter specification."""
    path: str | None = None
    """The server path."""
    source_address: str | None = None
    """The IPv4 or IPv6 address of the server."""
    source_port: int | None = None
    """The port of the server."""
    state: Literal["paused", "playing"] | None = None
    """The current state of the streaming pipeline."""
    stream_protocol: str | None = None
    """The stream protocol that is used."""
    transport_protocol: Literal["TCP", "UDP"] | None = None
    """The transport protocol that is used."""
    user_agent: str | None = None
    """Information about the client."""


class GetAllStreamsResult(Model):
    streams: list[Stream]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/streamstatus.cgi"

INFO = ApiInfo(
    id="streamstatus",
    name="Stream status API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("streamstatus"),),
    docs=("https://developer.axis.com/vapix/network-video/stream-status-api/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON format", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        2105: ErrorCode("Authorization failure", "access_denied"),
        2106: ErrorCode("Authentication failure", "access_denied"),
        2107: ErrorCode("Transport level error", "unavailable"),
    },
)


class OPS:
    get_all_streams = Operation(
        INFO,
        "get_all_streams",
        JsonRpcBinding("getAllStreams", PATH),
        result=GetAllStreamsResult,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class StreamStatusApi(SyncApi):
    """Stream status API (``streamstatus``, version 1)."""

    INFO = INFO

    def get_all_streams(self, *, request_options: RequestOptions | None = None) -> GetAllStreamsResult:
        """List all running streams on a device. Access: admin."""
        return self._run(OPS.get_all_streams, None, {}, request_options)


class AsyncStreamStatusApi(AsyncApi):
    """Stream status API (``streamstatus``, version 1)."""

    INFO = INFO

    async def get_all_streams(self, *, request_options: RequestOptions | None = None) -> GetAllStreamsResult:
        """List all running streams on a device. Access: admin."""
        return await self._run(OPS.get_all_streams, None, {}, request_options)
