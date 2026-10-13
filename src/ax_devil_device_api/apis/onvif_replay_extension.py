# GENERATED from specs/apis/network-video/onvif-replay-extension.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Check for and enable by default the ONVIF replay RTP header extension (NTP timestamps) on video and audio streams.

Docs: https://developer.axis.com/vapix/network-video/onvif-replay-extension/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class OnvifReplayExtSupport(Model):
    supported: bool = Field(
        validation_alias="Properties.API.RTP.OnvifReplayExt", serialization_alias="Properties.API.RTP.OnvifReplayExt"
    )
    """True when the device supports the RTP header extension."""


class OnvifReplayExtDefault(Model):
    enabled: bool = Field(
        validation_alias="Network.RTP.OnvifReplayExt", serialization_alias="Network.RTP.OnvifReplayExt"
    )
    """True when the RTP header extension is used by default, without ``onvifreplayext=1`` in the RTSP setup."""


class SetDefaultEnabledRequest(Model):
    enabled: bool = Field(
        validation_alias="Network.RTP.OnvifReplayExt", serialization_alias="Network.RTP.OnvifReplayExt"
    )
    """The new default for ``Network.RTP.OnvifReplayExt``."""


class StreamWithReplayExtensionRequest(Model):
    videocodec: str | None = None
    """Video codec of the stream, for example h264."""
    onvifreplayext: Literal[0, 1]
    """1 enables the RTP header extension, 0 disables it."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="onvif-replay-extension",
    name="Onvif Replay Extension",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.RTP.OnvifReplayExt", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/onvif-replay-extension/",),
)


class OPS:
    get_support = Operation(
        INFO,
        "get_support",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "Properties.API.RTP.OnvifReplayExt")),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        result=OnvifReplayExtSupport,
        access="viewer",
        effect="read",
    )
    get_default_enabled = Operation(
        INFO,
        "get_default_enabled",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "Network.RTP.OnvifReplayExt")),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        result=OnvifReplayExtDefault,
        access="admin",
        effect="read",
    )
    set_default_enabled = Operation(
        INFO,
        "set_default_enabled",
        CgiBinding(
            PATH,
            fixed_query=(("action", "update"),),
            args=(CgiArg("enabled", wire="Network.RTP.OnvifReplayExt", style="axis_bool"),),
            reply=TextOk(),
        ),
        params=SetDefaultEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    stream_with_replay_extension = Operation(
        INFO,
        "stream_with_replay_extension",
        RtspBinding(),
        params=StreamWithReplayExtensionRequest,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class OnvifReplayExtensionApi(SyncApi):
    """Onvif Replay Extension (``onvif-replay-extension``)."""

    INFO = INFO

    def get_support(self, *, request_options: RequestOptions | None = None) -> OnvifReplayExtSupport:
        """Check whether the device supports the RTP header extension.

        A device without support answers with a ``# Error`` text, which raises an API error.

        Access: viewer.
        """
        return self._run(OPS.get_support, None, {}, request_options)

    def get_default_enabled(self, *, request_options: RequestOptions | None = None) -> OnvifReplayExtDefault:
        """Check whether the RTP header extension is enabled by default. Access: admin."""
        return self._run(OPS.get_default_enabled, None, {}, request_options)

    def set_default_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the RTP header extension by default.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_default_enabled, None, {"enabled": enabled}, request_options)

    def stream_with_replay_extension(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        onvifreplayext: Literal[0, 1],
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream that uses (or does not use) the ONVIF replay RTP header extension.

        ``onvifreplayext=1`` includes NTP timestamps in the RTP packets; ``0`` disables the extension when
        it is enabled by default.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.stream_with_replay_extension,
            {"videocodec": videocodec, "onvifreplayext": onvifreplayext},
            port=port,
            include_credentials=include_credentials,
        )


class AsyncOnvifReplayExtensionApi(AsyncApi):
    """Onvif Replay Extension (``onvif-replay-extension``)."""

    INFO = INFO

    async def get_support(self, *, request_options: RequestOptions | None = None) -> OnvifReplayExtSupport:
        """Check whether the device supports the RTP header extension.

        A device without support answers with a ``# Error`` text, which raises an API error.

        Access: viewer.
        """
        return await self._run(OPS.get_support, None, {}, request_options)

    async def get_default_enabled(self, *, request_options: RequestOptions | None = None) -> OnvifReplayExtDefault:
        """Check whether the RTP header extension is enabled by default. Access: admin."""
        return await self._run(OPS.get_default_enabled, None, {}, request_options)

    async def set_default_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable the RTP header extension by default.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_default_enabled, None, {"enabled": enabled}, request_options)

    def stream_with_replay_extension(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        onvifreplayext: Literal[0, 1],
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream that uses (or does not use) the ONVIF replay RTP header extension.

        ``onvifreplayext=1`` includes NTP timestamps in the RTP packets; ``0`` disables the extension when
        it is enabled by default.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.stream_with_replay_extension,
            {"videocodec": videocodec, "onvifreplayext": onvifreplayext},
            port=port,
            include_credentials=include_credentials,
        )
