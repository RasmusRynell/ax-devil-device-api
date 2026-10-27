# GENERATED from specs/apis/network-video/parameter-management.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""``param.cgi``: list, update, add and remove device parameters.

Docs: https://developer.axis.com/vapix/network-video/parameter-management/
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Mapping
from typing import Any, Literal

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv, TextOk, Xml
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

UserGroup = Literal["anonymous", "viewer", "operator", "admin"]


class ListRequest(Model):
    group: list[str] | None = None
    usergroup: UserGroup | None = None


class ListDefinitionsRequest(Model):
    group: str | None = None
    usergroup: UserGroup | None = None


class UpdateRequest(Model):
    parameters: dict[str, str]
    usergroup: UserGroup | None = None


class AddRequest(Model):
    template: str
    group: str
    parameters: dict[str, str] | None = None
    force: bool | None = None


class RemoveRequest(Model):
    group: list[str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="parameter-management",
    name="Parameter management",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    docs=("https://developer.axis.com/vapix/network-video/parameter-management/",),
)


class OPS:
    list = Operation(
        INFO,
        "list",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group", style="csv"), CgiArg("usergroup")),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    list_definitions = Operation(
        INFO,
        "list_definitions",
        CgiBinding(
            PATH,
            fixed_query=(("action", "listdefinitions"), ("listformat", "xmlschema")),
            args=(CgiArg("group"), CgiArg("usergroup")),
            reply=Xml(),
        ),
        params=ListDefinitionsRequest,
        result=ET.Element,
        access="viewer",
        effect="read",
    )
    update = Operation(
        INFO,
        "update",
        CgiBinding(
            PATH,
            method="POST",
            encoding="form",
            fixed_query=(("action", "update"),),
            args=(CgiArg("parameters", style="spread"), CgiArg("usergroup")),
            reply=TextOk(),
        ),
        params=UpdateRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    add = Operation(
        INFO,
        "add",
        CgiBinding(
            PATH,
            method="POST",
            encoding="form",
            fixed_query=(("action", "add"),),
            args=(
                CgiArg("template"),
                CgiArg("group"),
                CgiArg("parameters", style="spread"),
                CgiArg("force", style="axis_bool"),
            ),
            reply=Text(),
        ),
        params=AddRequest,
        result=str,
        access="operator",
        effect="write",
        write="create",
    )
    remove = Operation(
        INFO,
        "remove",
        CgiBinding(PATH, fixed_query=(("action", "remove"),), args=(CgiArg("group", style="csv"),), reply=TextOk()),
        params=RemoveRequest,
        access="operator",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class ParameterManagementApi(SyncApi):
    """Parameter management (``parameter-management``)."""

    INFO = INFO

    def list(
        self,
        group: list[str] | MISSING = MISSING,
        *,
        usergroup: UserGroup | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> dict[str, str]:
        """Parameter values as ``{"Group.Name": "value"}`` (``root.`` removed).

        ``group`` entries may use ``*`` wildcards; omit it to list everything. Only parameters readable by
        the user are returned.

        Access: viewer.
        """
        return self._run(OPS.list, None, {"group": group, "usergroup": usergroup}, request_options)

    def list_definitions(
        self,
        group: str | MISSING = MISSING,
        *,
        usergroup: UserGroup | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ET.Element:
        """Parameter definitions (value, type, security level) as an XML element. Access: viewer."""
        return self._run(OPS.list_definitions, None, {"group": group, "usergroup": usergroup}, request_options)

    def update(
        self,
        parameters: Mapping[str, str],
        *,
        usergroup: UserGroup | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set parameters, e.g. ``{"Image.I0.Appearance.Resolution": "1920x1080"}``.

        Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update, None, {"parameters": dict(parameters), "usergroup": usergroup}, request_options)

    def add(
        self,
        template: str,
        group: str,
        parameters: Mapping[str, str] | MISSING = MISSING,
        *,
        force: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Add a dynamic group from a template; returns the device reply (``"<entry> OK"``).

        Access: operator.
        """
        args: dict[str, Any] = {"template": template, "group": group, "force": force}
        if parameters is not MISSING:
            args["parameters"] = dict(parameters)
        return self._run(OPS.add, None, args, request_options)

    def remove(self, group: list[str], *, request_options: RequestOptions | None = None) -> None:
        """Delete dynamic groups, e.g. ``["StreamProfile.S7"]``. Access: operator."""
        self._run(OPS.remove, None, {"group": group}, request_options)


class AsyncParameterManagementApi(AsyncApi):
    """Parameter management (``parameter-management``)."""

    INFO = INFO

    async def list(
        self,
        group: list[str] | MISSING = MISSING,
        *,
        usergroup: UserGroup | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> dict[str, str]:
        """Parameter values as ``{"Group.Name": "value"}`` (``root.`` removed).

        ``group`` entries may use ``*`` wildcards; omit it to list everything. Only parameters readable by
        the user are returned.

        Access: viewer.
        """
        return await self._run(OPS.list, None, {"group": group, "usergroup": usergroup}, request_options)

    async def list_definitions(
        self,
        group: str | MISSING = MISSING,
        *,
        usergroup: UserGroup | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ET.Element:
        """Parameter definitions (value, type, security level) as an XML element. Access: viewer."""
        return await self._run(OPS.list_definitions, None, {"group": group, "usergroup": usergroup}, request_options)

    async def update(
        self,
        parameters: Mapping[str, str],
        *,
        usergroup: UserGroup | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set parameters, e.g. ``{"Image.I0.Appearance.Resolution": "1920x1080"}``.

        Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update, None, {"parameters": dict(parameters), "usergroup": usergroup}, request_options)

    async def add(
        self,
        template: str,
        group: str,
        parameters: Mapping[str, str] | MISSING = MISSING,
        *,
        force: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Add a dynamic group from a template; returns the device reply (``"<entry> OK"``).

        Access: operator.
        """
        args: dict[str, Any] = {"template": template, "group": group, "force": force}
        if parameters is not MISSING:
            args["parameters"] = dict(parameters)
        return await self._run(OPS.add, None, args, request_options)

    async def remove(self, group: list[str], *, request_options: RequestOptions | None = None) -> None:
        """Delete dynamic groups, e.g. ``["StreamProfile.S7"]``. Access: operator."""
        await self._run(OPS.remove, None, {"group": group}, request_options)
