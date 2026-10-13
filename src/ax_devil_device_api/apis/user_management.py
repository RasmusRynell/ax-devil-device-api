# GENERATED from specs/apis/network-video/user-management.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Add, update, remove and list user accounts with password and group membership via ``/axis-cgi/pwdgrp.cgi``.

Docs: https://developer.axis.com/vapix/network-video/system-settings/
"""

from __future__ import annotations

from typing import Annotated, Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

UserName = Annotated[str, Field(min_length=1, max_length=14, pattern="^[a-zA-Z0-9]+$")]
SecondaryGroups = Annotated[str, Field(pattern="^(viewer|operator|admin|ptz)(:(viewer|operator|admin|ptz))*$")]


class AddUserRequest(Model):
    user: UserName
    pwd: str = Field(min_length=1, max_length=64)
    """The password for the account. It must contain one or more characters and comply with any configured passphrase policy."""
    grp: str
    """An existing primary group name. The recommended value is ``users``; ``root`` is supported but should only be used when creating the initial user account."""
    sgrp: SecondaryGroups
    comment: str | None = None
    """Description of the user account; may be empty. Optional in device software and service releases since autumn 2019, required before."""
    strict_pwd: int | None = Field(default=None, ge=1, le=1)
    """Set to 1 to enforce the VAPIX password standard (ASCII characters 0x20-0x7E, at most 64 characters)."""


class UpdateUserRequest(Model):
    user: UserName
    pwd: str | None = Field(default=None, min_length=1, max_length=64)
    """The new password. It must comply with any configured passphrase policy."""
    grp: str | None = None
    """The primary group."""
    sgrp: SecondaryGroups | None = None
    comment: str | None = None
    """Description of the user account."""
    strict_pwd: int | None = Field(default=None, ge=1, le=1)
    """Set to 1 to enforce the VAPIX password standard."""


class UserRequest(Model):
    user: UserName


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/pwdgrp.cgi"

INFO = ApiInfo(
    id="user-management",
    name="Add, modify and delete user accounts (pwdgrp.cgi)",
    family=Family.CGI,
    discovery=(ApiDiscovery("user-management"), ParamDiscovery("Properties.API.HTTP.Version", "3")),
    docs=("https://developer.axis.com/vapix/network-video/system-settings/",),
    errors={
        "system_log": ErrorCode(
            "Generic failure; the details are in the system log", "internal", message="consult the system log file."
        ),
        "action_operation_type": ErrorCode(
            "The action is omitted or is not add, update, remove or get",
            "invalid_argument",
            message="action operation type.",
        ),
        "account_user_name": ErrorCode(
            "The user name is missing or contains characters other than A-Z, a-z and 0-9",
            "invalid_argument",
            message="account user name.",
        ),
        "malformed_action": ErrorCode(
            "The user name is not appropriate for the action (the message ends with the action)",
            "invalid_argument",
            message_prefix="malformed action operation,",
        ),
        "not_initial_admin": ErrorCode(
            "No administrator exists yet and the user is not a valid initial administrator (HTTP 401)",
            "access_denied",
            message="not a valid initial admin user.",
        ),
        "initial_admin_first": ErrorCode(
            "No administrator exists yet; create one first and log in with it (HTTP 401)",
            "access_denied",
            message="initial admin user must be created first.",
        ),
        "invalid_password": ErrorCode(
            "The password is shorter than 1 or longer than 64 characters, or breaks the configured passphrase policy",
            "invalid_argument",
            message="invalid password.",
        ),
    },
)


class OPS:
    add_user = Operation(
        INFO,
        "add_user",
        CgiBinding(
            PATH,
            method="POST",
            encoding="form",
            fixed_query=(("action", "add"),),
            args=(
                CgiArg("user"),
                CgiArg("pwd"),
                CgiArg("grp"),
                CgiArg("sgrp"),
                CgiArg("comment"),
                CgiArg("strict_pwd"),
            ),
            reply=Text(),
            auth="if_challenged",
        ),
        params=AddUserRequest,
        result=str,
        access="admin",
        effect="write",
        write="create",
    )
    update_user = Operation(
        INFO,
        "update_user",
        CgiBinding(
            PATH,
            method="POST",
            encoding="form",
            fixed_query=(("action", "update"),),
            args=(
                CgiArg("user"),
                CgiArg("pwd"),
                CgiArg("grp"),
                CgiArg("sgrp"),
                CgiArg("comment"),
                CgiArg("strict_pwd"),
            ),
            reply=Text(),
        ),
        params=UpdateUserRequest,
        result=str,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_user = Operation(
        INFO,
        "remove_user",
        CgiBinding(
            PATH,
            method="POST",
            encoding="form",
            fixed_query=(("action", "remove"),),
            args=(CgiArg("user"),),
            reply=Text(),
        ),
        params=UserRequest,
        result=str,
        access="admin",
        effect="write",
        write="delete",
    )
    get_users = Operation(
        INFO,
        "get_users",
        CgiBinding(PATH, fixed_query=(("action", "get"),), reply=TextKv(), accept="text/plain"),
        result=dict[str, str],
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class UserManagementApi(SyncApi):
    """Add, modify and delete user accounts (pwdgrp.cgi) (``user-management``)."""

    INFO = INFO

    @overload
    def add_user(self, request: AddUserRequest, /, *, request_options: RequestOptions | None = None) -> str: ...
    @overload
    def add_user(
        self,
        /,
        *,
        user: UserName,
        pwd: str,
        grp: str,
        sgrp: SecondaryGroups,
        comment: str | MISSING = MISSING,
        strict_pwd: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    def add_user(
        self, request: AddUserRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> str:
        """Create a new user account; returns the device message (``"Created account joe."``).

        The arguments are sent in the request body, as the docs advise against putting credentials in the
        URL. The initial administrator account can be created without authentication, and on devices older
        than AXIS OS 11.5 it must be named ``root``; the role must be Administrator with PTZ control. The
        device reports failures as a text line starting with ``Error:`` and a message, with no numeric code
        (HTTP 200, except HTTP 401 for the two initial-admin cases); the API-level ``errors`` match them by
        message. The documented messages are: ``consult the system log file.`` (generic), ``action operation
        type.`` (action omitted or not add, update, remove or get), ``account user name.`` (no or invalid
        user name), ``malformed action operation, <action>.`` (user name not appropriate for the action),
        ``not a valid initial admin user.`` and ``initial admin user must be created first.`` (no admin
        exists yet, HTTP 401) and ``invalid password.`` (password shorter than 1 or longer than 64
        characters, or against the passphrase policy).

        Access: admin.
        """
        return self._run(OPS.add_user, request, kwargs, request_options)

    @overload
    def update_user(self, request: UpdateUserRequest, /, *, request_options: RequestOptions | None = None) -> str: ...
    @overload
    def update_user(
        self,
        /,
        *,
        user: UserName,
        pwd: str | MISSING = MISSING,
        grp: str | MISSING = MISSING,
        sgrp: SecondaryGroups | MISSING = MISSING,
        comment: str | MISSING = MISSING,
        strict_pwd: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    def update_user(
        self,
        request: UpdateUserRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> str:
        """Change the given properties of an existing user account; returns the device message (``"Modified account joe."``).

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.update_user, request, kwargs, request_options)

    def remove_user(self, user: UserName, *, request_options: RequestOptions | None = None) -> str:
        """Remove an existing user account; returns the device message (``"Removed account joe."``).

        Access: admin.
        """
        return self._run(OPS.remove_user, None, {"user": user}, request_options)

    def get_users(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List the user accounts that belong to each group, as ``{"admin": "\\"root,joe\\""}``.

        The keys are the groups ``admin``, ``operator``, ``viewer`` and ``ptz`` (access rights; a user is
        listed in every group it has rights to) and ``digusers`` (all created users). Each value is a
        double-quoted, comma separated list of user names.

        Access: admin.
        """
        return self._run(OPS.get_users, None, {}, request_options)


class AsyncUserManagementApi(AsyncApi):
    """Add, modify and delete user accounts (pwdgrp.cgi) (``user-management``)."""

    INFO = INFO

    @overload
    async def add_user(self, request: AddUserRequest, /, *, request_options: RequestOptions | None = None) -> str: ...
    @overload
    async def add_user(
        self,
        /,
        *,
        user: UserName,
        pwd: str,
        grp: str,
        sgrp: SecondaryGroups,
        comment: str | MISSING = MISSING,
        strict_pwd: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    async def add_user(
        self, request: AddUserRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> str:
        """Create a new user account; returns the device message (``"Created account joe."``).

        The arguments are sent in the request body, as the docs advise against putting credentials in the
        URL. The initial administrator account can be created without authentication, and on devices older
        than AXIS OS 11.5 it must be named ``root``; the role must be Administrator with PTZ control. The
        device reports failures as a text line starting with ``Error:`` and a message, with no numeric code
        (HTTP 200, except HTTP 401 for the two initial-admin cases); the API-level ``errors`` match them by
        message. The documented messages are: ``consult the system log file.`` (generic), ``action operation
        type.`` (action omitted or not add, update, remove or get), ``account user name.`` (no or invalid
        user name), ``malformed action operation, <action>.`` (user name not appropriate for the action),
        ``not a valid initial admin user.`` and ``initial admin user must be created first.`` (no admin
        exists yet, HTTP 401) and ``invalid password.`` (password shorter than 1 or longer than 64
        characters, or against the passphrase policy).

        Access: admin.
        """
        return await self._run(OPS.add_user, request, kwargs, request_options)

    @overload
    async def update_user(
        self, request: UpdateUserRequest, /, *, request_options: RequestOptions | None = None
    ) -> str: ...
    @overload
    async def update_user(
        self,
        /,
        *,
        user: UserName,
        pwd: str | MISSING = MISSING,
        grp: str | MISSING = MISSING,
        sgrp: SecondaryGroups | MISSING = MISSING,
        comment: str | MISSING = MISSING,
        strict_pwd: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str: ...
    async def update_user(
        self,
        request: UpdateUserRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> str:
        """Change the given properties of an existing user account; returns the device message (``"Modified account joe."``).

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.update_user, request, kwargs, request_options)

    async def remove_user(self, user: UserName, *, request_options: RequestOptions | None = None) -> str:
        """Remove an existing user account; returns the device message (``"Removed account joe."``).

        Access: admin.
        """
        return await self._run(OPS.remove_user, None, {"user": user}, request_options)

    async def get_users(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """List the user accounts that belong to each group, as ``{"admin": "\\"root,joe\\""}``.

        The keys are the groups ``admin``, ``operator``, ``viewer`` and ``ptz`` (access rights; a user is
        listed in every group it has rights to) and ``digusers`` (all created users). Each value is a
        double-quoted, comma separated list of user names.

        Access: admin.
        """
        return await self._run(OPS.get_users, None, {}, request_options)
