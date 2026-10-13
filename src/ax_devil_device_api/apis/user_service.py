# GENERATED from specs/apis/physical-access-control/user-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The user service is tightly coupled with the AccessControl service, and provides storage of user specific data.

Docs: https://developer.axis.com/vapix/physical-access-control/user-service/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ServiceDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ReferenceToken = str


class ServiceCapabilities(Model):
    """The capabilities of the user service."""

    max_limit: int | None = Field(default=None, validation_alias="MaxLimit", serialization_alias="MaxLimit")
    """The maximum number of entries the device returns in one list response."""


class Attribute(Model):
    """A typed name and value pair."""

    type: str | None = None
    """Value type; `string` in every example."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")


class UserInfo(Model):
    """Summary of a user."""

    token: ReferenceToken
    """A service-unique identifier of the user."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the user."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the user."""


class User(Model):
    """A user as returned by the device."""

    token: ReferenceToken
    """A service-unique identifier of the user."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the user."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the user."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes of the user, for example first and last name."""


class UserInput(Model):
    """A user to add or update. It holds the complete information about the user."""

    token: ReferenceToken | None = None
    """Token of the user to update. If empty or absent the device allocates a token and adds a new user."""
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """Name of the user."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the user."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes of the user, for example first and last name."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities."""


class ListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If absent, or higher than the device supports, the device decides."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this reference. If absent, start from the beginning."""


class TokensRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the users."""


class UserInfoList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    user_info: list[UserInfo] | None = Field(default=None, validation_alias="UserInfo", serialization_alias="UserInfo")
    """The users."""


class UserList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    user: list[User] | None = Field(default=None, validation_alias="User", serialization_alias="User")
    """The users."""


class UserInfos(Model):
    user_info: list[UserInfo] | None = Field(default=None, validation_alias="UserInfo", serialization_alias="UserInfo")


class Users(Model):
    user: list[User] | None = Field(default=None, validation_alias="User", serialization_alias="User")


class SetUserRequest(Model):
    user: list[UserInput] = Field(validation_alias="User", serialization_alias="User", min_length=1)
    """The users to add or update."""


class TokenList(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the added or updated users."""


class GetUserInfoByCredentialTokenRequest(Model):
    credential_token: ReferenceToken = Field(validation_alias="CredentialToken", serialization_alias="CredentialToken")
    """The credential to look up the users for."""


class GetUserRequest(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the users to get."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/pacs"

INFO = ApiInfo(
    id="user-service",
    name="User service",
    family=Family.SERVICE_JSON,
    discovery=(ServiceDiscovery("http://www.axis.com/vapix/ws/user"),),
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/user-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
        "https://developer.axis.com/vapix/physical-access-control/system-integration-examples/",
    ),
    errors={"ter:InvalidArgs": ErrorCode("Invalid argument", "invalid_argument")},
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "axudb:GetServiceCapabilities", auth="if_challenged"),
        result=GetServiceCapabilitiesResult,
        access="anonymous",
        effect="read",
    )
    get_user_info_list = Operation(
        INFO,
        "get_user_info_list",
        ServiceJsonBinding(PATH, "axudb:GetUserInfoList"),
        params=ListRequest,
        result=UserInfoList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning.", "invalid_argument"
            )
        },
    )
    get_user_info = Operation(
        INFO,
        "get_user_info",
        ServiceJsonBinding(PATH, "axudb:GetUserInfo"),
        params=TokensRequest,
        result=UserInfos,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    get_user_list = Operation(
        INFO,
        "get_user_list",
        ServiceJsonBinding(PATH, "axudb:GetUserList"),
        params=ListRequest,
        result=UserList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning.", "invalid_argument"
            )
        },
    )
    get_user = Operation(
        INFO,
        "get_user",
        ServiceJsonBinding(PATH, "axudb:GetUser"),
        params=GetUserRequest,
        result=Users,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    set_user = Operation(
        INFO,
        "set_user",
        ServiceJsonBinding(PATH, "axudb:SetUser"),
        params=SetUserRequest,
        result=TokenList,
        access="admin",
        effect="write",
        write="patch",
        errors={
            "ter:ActionNotSupported": ErrorCode("Action not supported.", "unsupported"),
            "ter:NotAllowed": ErrorCode("Not allowed."),
        },
    )
    remove_user = Operation(
        INFO,
        "remove_user",
        ServiceJsonBinding(PATH, "axudb:RemoveUser"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("User not found.", "not_found")},
    )
    get_user_info_by_credential_token = Operation(
        INFO,
        "get_user_info_by_credential_token",
        ServiceJsonBinding(PATH, "axudb:GetUserInfoByCredentialToken"),
        params=GetUserInfoByCredentialTokenRequest,
        result=UserInfos,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("User not found.", "not_found")},
    )


# ---------------------------------------------------------------------------
# API classes


class UserServiceApi(SyncApi):
    """User service (``user-service``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the user service. Access: anonymous."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def get_user_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UserInfoList:
        """List the summaries of all users.

        Pages through the users. Pass the returned `NextStartReference` as `StartReference` in the next call
        and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return self._run(
            OPS.get_user_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_user_info(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> UserInfos:
        """Get the summaries of the users with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_user_info, None, {"token": token}, request_options)

    def get_user_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UserList:
        """List all users with their attributes.

        Pages through the users. Pass the returned `NextStartReference` as `StartReference` in the next call
        and never reuse a reference.

        Access: admin.
        """
        return self._run(OPS.get_user_list, None, {"limit": limit, "start_reference": start_reference}, request_options)

    def get_user(
        self, *, token: list[ReferenceToken] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Users:
        """Get the users with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_user, None, {"token": token}, request_options)

    @overload
    def set_user(self, request: SetUserRequest, /, *, request_options: RequestOptions | None = None) -> TokenList: ...
    @overload
    def set_user(self, /, *, user: list[UserInput], request_options: RequestOptions | None = None) -> TokenList: ...
    def set_user(
        self, request: SetUserRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> TokenList:
        """Add or update users.

        Each user item holds the complete information about the user. A user whose token exists is updated,
        any other is added, and a user without a token gets one allocated by the device. All tokens are
        returned.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return self._run(OPS.set_user, request, kwargs, request_options)

    def remove_user(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """Remove the users with the given tokens. Access: admin."""
        self._run(OPS.remove_user, None, {"token": token}, request_options)

    def get_user_info_by_credential_token(
        self, *, credential_token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> UserInfos:
        """Get the summaries of the users linked to a credential.

        A user is linked to a credential by setting the user's token as `UserToken` of the credential in the
        access control service.

        Access: admin.
        """
        return self._run(
            OPS.get_user_info_by_credential_token, None, {"credential_token": credential_token}, request_options
        )


class AsyncUserServiceApi(AsyncApi):
    """User service (``user-service``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the user service. Access: anonymous."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def get_user_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UserInfoList:
        """List the summaries of all users.

        Pages through the users. Pass the returned `NextStartReference` as `StartReference` in the next call
        and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return await self._run(
            OPS.get_user_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_user_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> UserInfos:
        """Get the summaries of the users with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_user_info, None, {"token": token}, request_options)

    async def get_user_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> UserList:
        """List all users with their attributes.

        Pages through the users. Pass the returned `NextStartReference` as `StartReference` in the next call
        and never reuse a reference.

        Access: admin.
        """
        return await self._run(
            OPS.get_user_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_user(
        self, *, token: list[ReferenceToken] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Users:
        """Get the users with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_user, None, {"token": token}, request_options)

    @overload
    async def set_user(
        self, request: SetUserRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    async def set_user(
        self, /, *, user: list[UserInput], request_options: RequestOptions | None = None
    ) -> TokenList: ...
    async def set_user(
        self, request: SetUserRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> TokenList:
        """Add or update users.

        Each user item holds the complete information about the user. A user whose token exists is updated,
        any other is added, and a user without a token gets one allocated by the device. All tokens are
        returned.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return await self._run(OPS.set_user, request, kwargs, request_options)

    async def remove_user(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """Remove the users with the given tokens. Access: admin."""
        await self._run(OPS.remove_user, None, {"token": token}, request_options)

    async def get_user_info_by_credential_token(
        self, *, credential_token: ReferenceToken, request_options: RequestOptions | None = None
    ) -> UserInfos:
        """Get the summaries of the users linked to a credential.

        A user is linked to a credential by setting the user's token as `UserToken` of the credential in the
        access control service.

        Access: admin.
        """
        return await self._run(
            OPS.get_user_info_by_credential_token, None, {"credential_token": credential_token}, request_options
        )
