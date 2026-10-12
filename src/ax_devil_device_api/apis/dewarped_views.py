# GENERATED from specs/apis/network-video/dewarped-views.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read the dewarping parameters and set the camera orientation for the view modes of Axis 360/180 degree cameras.

Docs: https://developer.axis.com/vapix/network-video/dewarped-views/
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListParametersRequest(Model):
    group: str
    """Parameter group, wildcards allowed (e.g. Image.*.Name)."""


class SetCameraTiltOrientationRequest(Model):
    camera_tilt_orientation: Literal[-90, 0, 90] = Field(
        validation_alias="ImageSource.I0.CameraTiltOrientation",
        serialization_alias="ImageSource.I0.CameraTiltOrientation",
    )


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="dewarped-views",
    name="Dewarped views",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.Image.Dewarp", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/dewarped-views/",),
)


class OPS:
    list_parameters = Operation(
        INFO,
        "list_parameters",
        CgiBinding(
            PATH, fixed_query=(("action", "list"),), args=(CgiArg("group"),), reply=TextKv(strip_prefix="root.")
        ),
        params=ListParametersRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    get_camera_tilt_orientation = Operation(
        INFO,
        "get_camera_tilt_orientation",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "ImageSource.I0.CameraTiltOrientation")),
            reply=TextKv(strip_prefix="root."),
        ),
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    set_camera_tilt_orientation = Operation(
        INFO,
        "set_camera_tilt_orientation",
        CgiBinding(
            PATH,
            method="POST",
            encoding="form",
            fixed_query=(("action", "update"),),
            args=(CgiArg("camera_tilt_orientation", wire="ImageSource.I0.CameraTiltOrientation"),),
            reply=TextOk(),
        ),
        params=SetCameraTiltOrientationRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class DewarpedViewsApi(SyncApi):
    """Dewarped views (``dewarped-views``)."""

    INFO = INFO

    def list_parameters(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List dewarping-related parameters as ``{"Group.Name": "value"}`` (``root.`` removed).

        ``group`` may use ``*`` wildcards, for example ``Properties.Image.Dewarp``,
        ``Properties.Image.NbrOfViews``, ``Properties.Image.I0`` (resolutions and rotations of view mode 0),
        ``Image.*.Name`` or ``Image.I1.Enabled``.

        Access: viewer.
        """
        return self._run(OPS.list_parameters, None, {"group": group}, request_options)

    def get_camera_tilt_orientation(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the camera orientation (mounting position) as a parameter map.

        The map holds ``ImageSource.I0.CameraTiltOrientation``: -90 (ceiling), 0 (wall) or 90 (desk or
        similar). The orientation decides which view modes are available.

        Access: viewer.
        """
        return self._run(OPS.get_camera_tilt_orientation, None, {}, request_options)

    def set_camera_tilt_orientation(
        self, camera_tilt_orientation: Literal[-90, 0, 90], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the camera orientation (mounting position), which affects view modes and PTZ.

        -90 = mounted in the ceiling, 0 = on a wall, 90 = on a desk or similar. View modes 2, 3 and 8 to 11
        are not available on a wall mount.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_camera_tilt_orientation, None, {"camera_tilt_orientation": camera_tilt_orientation}, request_options
        )


class AsyncDewarpedViewsApi(AsyncApi):
    """Dewarped views (``dewarped-views``)."""

    INFO = INFO

    async def list_parameters(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List dewarping-related parameters as ``{"Group.Name": "value"}`` (``root.`` removed).

        ``group`` may use ``*`` wildcards, for example ``Properties.Image.Dewarp``,
        ``Properties.Image.NbrOfViews``, ``Properties.Image.I0`` (resolutions and rotations of view mode 0),
        ``Image.*.Name`` or ``Image.I1.Enabled``.

        Access: viewer.
        """
        return await self._run(OPS.list_parameters, None, {"group": group}, request_options)

    async def get_camera_tilt_orientation(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the camera orientation (mounting position) as a parameter map.

        The map holds ``ImageSource.I0.CameraTiltOrientation``: -90 (ceiling), 0 (wall) or 90 (desk or
        similar). The orientation decides which view modes are available.

        Access: viewer.
        """
        return await self._run(OPS.get_camera_tilt_orientation, None, {}, request_options)

    async def set_camera_tilt_orientation(
        self, camera_tilt_orientation: Literal[-90, 0, 90], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the camera orientation (mounting position), which affects view modes and PTZ.

        -90 = mounted in the ceiling, 0 = on a wall, 90 = on a desk or similar. View modes 2, 3 and 8 to 11
        are not available on a wall mount.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_camera_tilt_orientation, None, {"camera_tilt_orientation": camera_tilt_orientation}, request_options
        )
