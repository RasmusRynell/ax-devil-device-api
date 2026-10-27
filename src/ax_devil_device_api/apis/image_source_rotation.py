# GENERATED from specs/apis/network-video/image-source-rotation.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""``param.cgi`` parameters that detect and control image source rotation and auto rotation (``ImageSource.I#``).

Docs: https://developer.axis.com/vapix/network-video/image-source-rotation/
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListImageSourceParametersRequest(Model):
    group: list[str] = Field(min_length=1)
    """Groups to list, e.g. ``ImageSource.I0``."""


class UpdateImageSourceParametersRequest(Model):
    parameters: dict[str, str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="image-source-rotation",
    name="Image source rotation",
    family=Family.CGI,
    discovery=(ParamDiscovery("ImageSource.I0.SourceRotation", "yes"),),
    requires_firmware="8.40",
    docs=("https://developer.axis.com/vapix/network-video/image-source-rotation/",),
)


class OPS:
    list_image_source_parameters = Operation(
        INFO,
        "list_image_source_parameters",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListImageSourceParametersRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    update_image_source_parameters = Operation(
        INFO,
        "update_image_source_parameters",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=UpdateImageSourceParametersRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class ImageSourceRotationApi(SyncApi):
    """Image source rotation (``image-source-rotation``)."""

    INFO = INFO

    def list_image_source_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Read ``ImageSource.I#`` parameters as ``{"ImageSource.I0.Rotation": "180"}`` (``root.`` removed).

        Use ``ImageSource.I0`` (``#`` runs from 0 to the number of image sources - 1). ``SourceRotation``
        (yes/no, read-only) tells whether the device has image source rotation; ``Rotation`` (0, 90, 180 or
        270 as listed in ``Properties.Image.Rotation``) is the rotation; ``AutoRotationEnabled`` (yes/no)
        tells whether the rotation follows the device orientation. Rotation is present when
        ``SourceRotation`` is yes and a rotation value is set.

        Access: viewer.
        """
        return self._run(OPS.list_image_source_parameters, None, {"group": group}, request_options)

    def update_image_source_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set ``Rotation`` or ``AutoRotationEnabled``, e.g. ``{"ImageSource.I0.Rotation": "90"}``.

        ``ImageSource.I#.Rotation`` takes a value from ``Properties.Image.Rotation`` (typically 0, 90, 180,
        270; default 0). Changing it closes all open streams, which must be requested again, and turns
        ``AutoRotationEnabled`` off. ``ImageSource.I#.AutoRotationEnabled`` takes ``yes`` or ``no``;
        ``SourceRotation`` is read-only.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_image_source_parameters, None, {"parameters": dict(parameters)}, request_options)


class AsyncImageSourceRotationApi(AsyncApi):
    """Image source rotation (``image-source-rotation``)."""

    INFO = INFO

    async def list_image_source_parameters(
        self, group: list[str], *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Read ``ImageSource.I#`` parameters as ``{"ImageSource.I0.Rotation": "180"}`` (``root.`` removed).

        Use ``ImageSource.I0`` (``#`` runs from 0 to the number of image sources - 1). ``SourceRotation``
        (yes/no, read-only) tells whether the device has image source rotation; ``Rotation`` (0, 90, 180 or
        270 as listed in ``Properties.Image.Rotation``) is the rotation; ``AutoRotationEnabled`` (yes/no)
        tells whether the rotation follows the device orientation. Rotation is present when
        ``SourceRotation`` is yes and a rotation value is set.

        Access: viewer.
        """
        return await self._run(OPS.list_image_source_parameters, None, {"group": group}, request_options)

    async def update_image_source_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set ``Rotation`` or ``AutoRotationEnabled``, e.g. ``{"ImageSource.I0.Rotation": "90"}``.

        ``ImageSource.I#.Rotation`` takes a value from ``Properties.Image.Rotation`` (typically 0, 90, 180,
        270; default 0). Changing it closes all open streams, which must be requested again, and turns
        ``AutoRotationEnabled`` off. ``ImageSource.I#.AutoRotationEnabled`` takes ``yes`` or ``no``;
        ``SourceRotation`` is read-only.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_image_source_parameters, None, {"parameters": dict(parameters)}, request_options)
