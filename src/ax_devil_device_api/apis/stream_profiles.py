# GENERATED from specs/apis/network-video/stream-profiles.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Create and manage stream profiles (named sets of video stream request parameters) via /axis-cgi/streamprofile.cgi.

Docs: https://developer.axis.com/vapix/network-video/stream-profiles/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class StreamProfile(Model):
    """A stream profile. The structure is the same in list responses and create/update requests."""

    name: str
    """ASCII string that represents the name of the profile."""
    description: str | None = None
    """ASCII string that describes the stream profile."""
    parameters: str | None = None
    """List of parameters, separated by a &, which defines the stream profile (e.g. resolution=640x360&fps=25&rotation=180)."""


class ProfileName(Model):
    """Reference to a stream profile by name."""

    name: str
    """ASCII string that represents the name of the profile."""


class ListRequest(Model):
    stream_profile_name: list[ProfileName] = Field(
        validation_alias="streamProfileName", serialization_alias="streamProfileName"
    )
    """List of profile names whose profile needs to be listed. Empty list [] lists all profiles."""


class ListResult(Model):
    stream_profile: list[StreamProfile] = Field(validation_alias="streamProfile", serialization_alias="streamProfile")
    max_profiles: int | None = Field(default=None, validation_alias="maxProfiles", serialization_alias="maxProfiles")
    """Maximum number of supported stream profiles."""


class CreateRequest(Model):
    stream_profile: list[StreamProfile] = Field(validation_alias="streamProfile", serialization_alias="streamProfile")
    """Stream profiles to create."""


class UpdateRequest(Model):
    stream_profile: list[StreamProfile] = Field(validation_alias="streamProfile", serialization_alias="streamProfile")
    """Stream profiles to update (matched by name)."""


class RemoveRequest(Model):
    stream_profile_name: list[ProfileName] = Field(
        validation_alias="streamProfileName", serialization_alias="streamProfileName"
    )
    """List of profile names to remove."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/streamprofile.cgi"

INFO = ApiInfo(
    id="stream-profiles",
    name="Stream profiles",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1)),
    discovery=(ApiDiscovery("stream-profiles"),),
    docs=("https://developer.axis.com/vapix/network-video/stream-profiles/",),
    errors={
        1000: ErrorCode("Application error. The application failed to return or set the configuration.", "internal"),
        2000: ErrorCode("Unsupported version. The major version number is not supported.", "unsupported"),
        2001: ErrorCode("Invalid format. The request does not follow the JSON schema.", "invalid_argument"),
        2002: ErrorCode(
            "Incoherent configuration. Parts of the configuration contradict each other, for example several profiles with the same name.",
            "invalid_argument",
        ),
        2003: ErrorCode("Missing parameter. A mandatory parameter is missing.", "invalid_argument"),
        2004: ErrorCode("Invalid parameter. A parameter has an invalid value.", "invalid_argument"),
        2005: ErrorCode("Unsupported method.", "unsupported"),
        2006: ErrorCode("Profile does not exist.", "not_found"),
    },
)


class OPS:
    list = Operation(
        INFO,
        "list",
        JsonRpcBinding("list", PATH),
        params=ListRequest,
        result=ListResult,
        access="viewer",
        effect="read",
    )
    create = Operation(
        INFO,
        "create",
        JsonRpcBinding("create", PATH),
        params=CreateRequest,
        access="operator",
        effect="write",
        write="create",
    )
    update = Operation(
        INFO,
        "update",
        JsonRpcBinding("update", PATH),
        params=UpdateRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    remove = Operation(
        INFO,
        "remove",
        JsonRpcBinding("remove", PATH),
        params=RemoveRequest,
        access="operator",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class StreamProfilesApi(SyncApi):
    """Stream profiles (``stream-profiles``, version 1)."""

    INFO = INFO

    @overload
    def list(self, request: ListRequest, /, *, request_options: RequestOptions | None = None) -> ListResult: ...
    @overload
    def list(
        self, /, *, stream_profile_name: list[ProfileName], request_options: RequestOptions | None = None
    ) -> ListResult: ...
    def list(
        self, request: ListRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ListResult:
        """List one, several or all stream profiles.

        It is possible to list either one or multiple profiles and if the parameter streamProfileName is the
        empty list [] all available stream profiles will be listed.

        Access: viewer.
        """
        return self._run(OPS.list, request, kwargs, request_options)

    @overload
    def create(self, request: CreateRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def create(
        self, /, *, stream_profile: list[StreamProfile], request_options: RequestOptions | None = None
    ) -> None: ...
    def create(
        self, request: CreateRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Add one or more new stream profiles.

        The name of each stream profile needs to be unique, otherwise, an error will be returned.

        Access: operator.
        """
        self._run(OPS.create, request, kwargs, request_options)

    @overload
    def update(self, request: UpdateRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update(
        self, /, *, stream_profile: list[StreamProfile], request_options: RequestOptions | None = None
    ) -> None: ...
    def update(
        self, request: UpdateRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Update existing stream profiles.

        You can not rename a profile unless you first delete it and create a new one with the required name.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update, request, kwargs, request_options)

    @overload
    def remove(self, request: RemoveRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def remove(
        self, /, *, stream_profile_name: list[ProfileName], request_options: RequestOptions | None = None
    ) -> None: ...
    def remove(
        self, request: RemoveRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Remove one or several stream profiles by name. Access: operator."""
        self._run(OPS.remove, request, kwargs, request_options)


class AsyncStreamProfilesApi(AsyncApi):
    """Stream profiles (``stream-profiles``, version 1)."""

    INFO = INFO

    @overload
    async def list(self, request: ListRequest, /, *, request_options: RequestOptions | None = None) -> ListResult: ...
    @overload
    async def list(
        self, /, *, stream_profile_name: list[ProfileName], request_options: RequestOptions | None = None
    ) -> ListResult: ...
    async def list(
        self, request: ListRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ListResult:
        """List one, several or all stream profiles.

        It is possible to list either one or multiple profiles and if the parameter streamProfileName is the
        empty list [] all available stream profiles will be listed.

        Access: viewer.
        """
        return await self._run(OPS.list, request, kwargs, request_options)

    @overload
    async def create(self, request: CreateRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def create(
        self, /, *, stream_profile: list[StreamProfile], request_options: RequestOptions | None = None
    ) -> None: ...
    async def create(
        self, request: CreateRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Add one or more new stream profiles.

        The name of each stream profile needs to be unique, otherwise, an error will be returned.

        Access: operator.
        """
        await self._run(OPS.create, request, kwargs, request_options)

    @overload
    async def update(self, request: UpdateRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def update(
        self, /, *, stream_profile: list[StreamProfile], request_options: RequestOptions | None = None
    ) -> None: ...
    async def update(
        self, request: UpdateRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Update existing stream profiles.

        You can not rename a profile unless you first delete it and create a new one with the required name.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update, request, kwargs, request_options)

    @overload
    async def remove(self, request: RemoveRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def remove(
        self, /, *, stream_profile_name: list[ProfileName], request_options: RequestOptions | None = None
    ) -> None: ...
    async def remove(
        self, request: RemoveRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Remove one or several stream profiles by name. Access: operator."""
        await self._run(OPS.remove, request, kwargs, request_options)
