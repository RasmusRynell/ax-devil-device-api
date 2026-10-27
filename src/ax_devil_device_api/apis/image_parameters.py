# GENERATED from specs/apis/network-video/image-api.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""``param.cgi`` groups that hold the per-video-channel stream defaults (``Image``, ``Image.I#``, ``ImageSource.I#``) and the stream capabilities (``Properties.Image``).

Docs: https://developer.axis.com/vapix/network-video/parameter-management/image-api/
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListParametersRequest(Model):
    group: list[str] = Field(min_length=1)
    """Parameter groups to list."""


class UpdateParametersRequest(Model):
    parameters: dict[str, str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="image-api",
    name="Parameter management for video channels",
    family=Family.CGI,
    docs=("https://developer.axis.com/vapix/network-video/parameter-management/image-api/",),
)


class OPS:
    list_parameters = Operation(
        INFO,
        "list_parameters",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListParametersRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    update_parameters = Operation(
        INFO,
        "update_parameters",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=UpdateParametersRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class ImageParametersApi(SyncApi):
    """Parameter management for video channels (``image-api``)."""

    INFO = INFO

    def list_parameters(self, group: list[str], *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Video channel parameters as ``{"Image.I0.Appearance.Resolution": "1920x1080"}`` (``root.`` removed).

        ``group`` entries such as ``Image.I0.Appearance``, ``Image.I0.MPEG``, ``Image.I0.RateControl``,
        ``Image.I0.Stream``, ``ImageSource.I0`` and ``Properties.Image``. The channel number ``#`` runs from
        0 to the number of video channels - 1. The defaults apply to a stream request unless a URL option
        overrides them. Reading needs viewer access.

        Access: viewer.
        """
        return self._run(OPS.list_parameters, None, {"group": group}, request_options)

    def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set video channel parameters, e.g. ``{"Image.I0.Appearance.Compression": "30"}``.

        Only the given parameters change. Writable groups include ``Image``, ``Image.I#`` (``Enabled``,
        ``Name``), ``Image.I#.Appearance``, ``Image.I#.Layers``, ``Image.I#.MPEG``,
        ``Image.I#.RateControl``, ``Image.I#.Stream`` and ``ImageSource.I#.Rotation``. ``Properties.Image``
        is read-only except ``ShowSuboptimalResolutions``.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)


class AsyncImageParametersApi(AsyncApi):
    """Parameter management for video channels (``image-api``)."""

    INFO = INFO

    async def list_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Video channel parameters as ``{"Image.I0.Appearance.Resolution": "1920x1080"}`` (``root.`` removed).

        ``group`` entries such as ``Image.I0.Appearance``, ``Image.I0.MPEG``, ``Image.I0.RateControl``,
        ``Image.I0.Stream``, ``ImageSource.I0`` and ``Properties.Image``. The channel number ``#`` runs from
        0 to the number of video channels - 1. The defaults apply to a stream request unless a URL option
        overrides them. Reading needs viewer access.

        Access: viewer.
        """
        return await self._run(OPS.list_parameters, None, {"group": group}, request_options)

    async def update_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set video channel parameters, e.g. ``{"Image.I0.Appearance.Compression": "30"}``.

        Only the given parameters change. Writable groups include ``Image``, ``Image.I#`` (``Enabled``,
        ``Name``), ``Image.I#.Appearance``, ``Image.I#.Layers``, ``Image.I#.MPEG``,
        ``Image.I#.RateControl``, ``Image.I#.Stream`` and ``ImageSource.I#.Rotation``. ``Properties.Image``
        is read-only except ``ShowSuboptimalResolutions``.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_parameters, None, {"parameters": dict(parameters)}, request_options)
