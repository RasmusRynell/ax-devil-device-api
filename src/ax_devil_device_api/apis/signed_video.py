# GENERATED from specs/apis/network-video/signed-video.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Enable or disable video signing per video channel with ``Image.I#.MPEG.SignedVideo.Enabled`` (param.cgi).

Docs: https://developer.axis.com/vapix/network-video/signed-video/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class GetSignedVideoRequest(Model):
    group: str = Field(pattern=r"^Image\.I[0-9]+\.MPEG\.SignedVideo(\.Enabled)?$")
    """The parameter or group to list, for example ``Image.I0.MPEG.SignedVideo.Enabled``."""


class SetSignedVideoRequest(Model):
    parameters: dict[str, Literal["yes", "no"]]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="signed-video",
    name="Signed Video",
    family=Family.CGI,
    discovery=(ApiDiscovery("signed-video"),),
    docs=("https://developer.axis.com/vapix/network-video/signed-video/",),
)


class OPS:
    get_signed_video = Operation(
        INFO,
        "get_signed_video",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=GetSignedVideoRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    set_signed_video = Operation(
        INFO,
        "set_signed_video",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=SetSignedVideoRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SignedVideoApi(SyncApi):
    """Signed Video (``signed-video``)."""

    INFO = INFO

    def get_signed_video(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read whether signed video is enabled for a channel, as ``{"Image.I0.MPEG.SignedVideo.Enabled": "yes"}``.

        ``group`` is ``Image.I#.MPEG.SignedVideo.Enabled`` (or the ``Image.I#.MPEG.SignedVideo`` group),
        where ``#`` is the channel index, from 0 up to the number of channels of the product minus 1.

        Access: viewer.
        """
        return self._run(OPS.get_signed_video, None, {"group": group}, request_options)

    def set_signed_video(
        self, parameters: Mapping[str, Literal["yes", "no"]], *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable signed video by default for a channel, e.g. ``{"Image.I0.MPEG.SignedVideo.Enabled": "yes"}``.

        Keys are ``Image.I#.MPEG.SignedVideo.Enabled`` where ``#`` is the channel index (0 up to the number
        of channels minus 1); values are ``yes`` or ``no`` (the default is ``no``). Only the given
        parameters change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_signed_video, None, {"parameters": dict(parameters)}, request_options)


class AsyncSignedVideoApi(AsyncApi):
    """Signed Video (``signed-video``)."""

    INFO = INFO

    async def get_signed_video(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read whether signed video is enabled for a channel, as ``{"Image.I0.MPEG.SignedVideo.Enabled": "yes"}``.

        ``group`` is ``Image.I#.MPEG.SignedVideo.Enabled`` (or the ``Image.I#.MPEG.SignedVideo`` group),
        where ``#`` is the channel index, from 0 up to the number of channels of the product minus 1.

        Access: viewer.
        """
        return await self._run(OPS.get_signed_video, None, {"group": group}, request_options)

    async def set_signed_video(
        self, parameters: Mapping[str, Literal["yes", "no"]], *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable signed video by default for a channel, e.g. ``{"Image.I0.MPEG.SignedVideo.Enabled": "yes"}``.

        Keys are ``Image.I#.MPEG.SignedVideo.Enabled`` where ``#`` is the channel index (0 up to the number
        of channels minus 1); values are ``yes`` or ``no`` (the default is ``no``). Only the given
        parameters change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_signed_video, None, {"parameters": dict(parameters)}, request_options)
