# GENERATED from specs/apis/network-video/scene-profile.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Switch between predefined sets of image settings (scene profiles) through the ImageSource.I#.SceneProfile parameter.

Docs: https://developer.axis.com/vapix/network-video/video-streaming/
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Mapping

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextOk, Xml
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ListSceneProfilesRequest(Model):
    group: str
    """The parameter to describe, ImageSource.I<n>.SceneProfile, for example ImageSource.I0.SceneProfile."""
    responseformat: str | None = None
    """The example uses rfc."""
    responsecharset: str | None = None
    """The example uses utrf (sic)."""


class SetSceneProfileRequest(Model):
    parameters: dict[str, str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="scene-profile",
    name="Scene profile API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    docs=("https://developer.axis.com/vapix/network-video/video-streaming/",),
)


class OPS:
    list_scene_profiles = Operation(
        INFO,
        "list_scene_profiles",
        CgiBinding(
            PATH,
            fixed_query=(("action", "listdefinitions"), ("listformat", "xmlschema")),
            args=(CgiArg("group"), CgiArg("responseformat"), CgiArg("responsecharset")),
            reply=Xml(),
        ),
        params=ListSceneProfilesRequest,
        result=ET.Element,
        access="operator",
        effect="read",
    )
    set_scene_profile = Operation(
        INFO,
        "set_scene_profile",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=SetSceneProfileRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SceneProfileApi(SyncApi):
    """Scene profile API (``scene-profile``)."""

    INFO = INFO

    def list_scene_profiles(
        self,
        group: str,
        *,
        responseformat: str | MISSING = MISSING,
        responsecharset: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ET.Element:
        """List the supported scene profile values and their display names.

        The reply is the XML schema definition of the parameter, whose ``<entry value="..."
        niceValue="..."/>`` elements list the supported profiles. Valid profiles are product dependent.

        Access: operator.
        """
        return self._run(
            OPS.list_scene_profiles,
            None,
            {"group": group, "responseformat": responseformat, "responsecharset": responsecharset},
            request_options,
        )

    def set_scene_profile(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Change the scene profile, e.g. ``{"ImageSource.I0.SceneProfile": "vivid"}``.

        The key is the parameter name ImageSource.I<n>.SceneProfile and the value one of forensic, vivid,
        traffic_overview, indoor, outdoor or license_plate (product dependent). The device answers 200 OK
        and changes nothing when the value is invalid. All streams are affected. The obsolete profile0,
        profile1 and profile2 are replaced by forensic, vivid and traffic_overview.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_scene_profile, None, {"parameters": dict(parameters)}, request_options)


class AsyncSceneProfileApi(AsyncApi):
    """Scene profile API (``scene-profile``)."""

    INFO = INFO

    async def list_scene_profiles(
        self,
        group: str,
        *,
        responseformat: str | MISSING = MISSING,
        responsecharset: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ET.Element:
        """List the supported scene profile values and their display names.

        The reply is the XML schema definition of the parameter, whose ``<entry value="..."
        niceValue="..."/>`` elements list the supported profiles. Valid profiles are product dependent.

        Access: operator.
        """
        return await self._run(
            OPS.list_scene_profiles,
            None,
            {"group": group, "responseformat": responseformat, "responsecharset": responsecharset},
            request_options,
        )

    async def set_scene_profile(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Change the scene profile, e.g. ``{"ImageSource.I0.SceneProfile": "vivid"}``.

        The key is the parameter name ImageSource.I<n>.SceneProfile and the value one of forensic, vivid,
        traffic_overview, indoor, outdoor or license_plate (product dependent). The device answers 200 OK
        and changes nothing when the value is invalid. All streams are affected. The obsolete profile0,
        profile1 and profile2 are replaced by forensic, vivid and traffic_overview.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_scene_profile, None, {"parameters": dict(parameters)}, request_options)
