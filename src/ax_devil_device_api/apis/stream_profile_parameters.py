# GENERATED from specs/apis/network-video/stream-profile-parameters.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Add, configure, list and remove stream profiles through param.cgi (``StreamProfile.S#`` dynamic parameter group, template ``streamprofile``).

Docs: https://developer.axis.com/vapix/network-video/video-streaming/
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class AddStreamProfileRequest(Model):
    name: str | None = Field(
        default=None, validation_alias="StreamProfile.S.Name", serialization_alias="StreamProfile.S.Name"
    )
    """The name of the stream profile used in requests. Must be unique."""
    description: str | None = Field(
        default=None, validation_alias="StreamProfile.S.Description", serialization_alias="StreamProfile.S.Description"
    )
    """User-friendly description of the profile."""
    parameters: str | None = Field(
        default=None, validation_alias="StreamProfile.S.Parameters", serialization_alias="StreamProfile.S.Parameters"
    )
    """List of image request arguments, for example ``videocodec=h264&resolution=4CIF``, percent-encoded (space ``%20``, ``=`` ``%3d``, ``&`` ``%26``, ``%`` ``%25``; a space inside the list becomes ``%2520``)."""


class UpdateStreamProfileRequest(Model):
    parameters: dict[str, str]


class ListStreamProfileRequest(Model):
    group: str = Field(pattern=r"^StreamProfile(\.S[0-9]+)?$")
    """The group to list, for example ``StreamProfile.S5`` or ``StreamProfile``."""


class RemoveStreamProfileRequest(Model):
    group: str = Field(pattern=r"^StreamProfile\.S[0-9]+$")
    """The profile group, for example ``StreamProfile.S4``."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="stream-profile-parameters",
    name="Stream profiles (StreamProfile parameter group)",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    docs=("https://developer.axis.com/vapix/network-video/video-streaming/",),
)


class OPS:
    add_stream_profile = Operation(
        INFO,
        "add_stream_profile",
        CgiBinding(
            PATH,
            fixed_query=(("action", "add"), ("template", "streamprofile"), ("group", "StreamProfile")),
            args=(
                CgiArg("name", wire="StreamProfile.S.Name"),
                CgiArg("description", wire="StreamProfile.S.Description"),
                CgiArg("parameters", wire="StreamProfile.S.Parameters"),
            ),
            reply=Text(),
        ),
        params=AddStreamProfileRequest,
        result=str,
        access="operator",
        effect="write",
        write="create",
    )
    update_stream_profile = Operation(
        INFO,
        "update_stream_profile",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=UpdateStreamProfileRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    list_stream_profile = Operation(
        INFO,
        "list_stream_profile",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=ListStreamProfileRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    remove_stream_profile = Operation(
        INFO,
        "remove_stream_profile",
        CgiBinding(PATH, fixed_query=(("action", "remove"),), args=(CgiArg("group"),), reply=TextOk()),
        params=RemoveStreamProfileRequest,
        access="operator",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class StreamProfileParametersApi(SyncApi):
    """Stream profiles (StreamProfile parameter group) (``stream-profile-parameters``)."""

    INFO = INFO

    def add_stream_profile(
        self,
        *,
        name: str | MISSING = MISSING,
        description: str | MISSING = MISSING,
        parameters: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Add a new stream profile, optionally with name, description and parameters; returns the device reply (``"S4 OK"``).

        The new profile gets the next free group number (``S4`` in the documented example). Creating a
        dynamic parameter group needs administrator or operator access. The name may contain ``A-Z``,
        ``a-z``, ``0-9``, ``-`` and ``_`` and must be unique.

        Access: operator.
        """
        return self._run(
            OPS.add_stream_profile,
            None,
            {"name": name, "description": description, "parameters": parameters},
            request_options,
        )

    def update_stream_profile(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Configure stream profiles, e.g. ``{"StreamProfile.S4.Name": "myprofile"}``.

        Keys are ``StreamProfile.S#.Name``, ``StreamProfile.S#.Description`` and
        ``StreamProfile.S#.Parameters`` where ``#`` is the group number of the profile. ``Parameters`` is a
        percent-encoded argument list (see ``add_stream_profile``). Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_stream_profile, None, {"parameters": dict(parameters)}, request_options)

    def list_stream_profile(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List the parameters of a stream profile or of all profiles, as ``{"StreamProfile.S5.Name": "myprofile2"}``.

        Access: viewer.
        """
        return self._run(OPS.list_stream_profile, None, {"group": group}, request_options)

    def remove_stream_profile(self, group: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a user-created stream profile, e.g. ``StreamProfile.S4``.

        Predefined stream profiles cannot be removed.

        Access: operator.
        """
        self._run(OPS.remove_stream_profile, None, {"group": group}, request_options)


class AsyncStreamProfileParametersApi(AsyncApi):
    """Stream profiles (StreamProfile parameter group) (``stream-profile-parameters``)."""

    INFO = INFO

    async def add_stream_profile(
        self,
        *,
        name: str | MISSING = MISSING,
        description: str | MISSING = MISSING,
        parameters: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Add a new stream profile, optionally with name, description and parameters; returns the device reply (``"S4 OK"``).

        The new profile gets the next free group number (``S4`` in the documented example). Creating a
        dynamic parameter group needs administrator or operator access. The name may contain ``A-Z``,
        ``a-z``, ``0-9``, ``-`` and ``_`` and must be unique.

        Access: operator.
        """
        return await self._run(
            OPS.add_stream_profile,
            None,
            {"name": name, "description": description, "parameters": parameters},
            request_options,
        )

    async def update_stream_profile(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Configure stream profiles, e.g. ``{"StreamProfile.S4.Name": "myprofile"}``.

        Keys are ``StreamProfile.S#.Name``, ``StreamProfile.S#.Description`` and
        ``StreamProfile.S#.Parameters`` where ``#`` is the group number of the profile. ``Parameters`` is a
        percent-encoded argument list (see ``add_stream_profile``). Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_stream_profile, None, {"parameters": dict(parameters)}, request_options)

    async def list_stream_profile(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List the parameters of a stream profile or of all profiles, as ``{"StreamProfile.S5.Name": "myprofile2"}``.

        Access: viewer.
        """
        return await self._run(OPS.list_stream_profile, None, {"group": group}, request_options)

    async def remove_stream_profile(self, group: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a user-created stream profile, e.g. ``StreamProfile.S4``.

        Predefined stream profiles cannot be removed.

        Access: operator.
        """
        await self._run(OPS.remove_stream_profile, None, {"group": group}, request_options)
