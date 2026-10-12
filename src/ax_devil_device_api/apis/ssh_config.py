# GENERATED from specs/apis/device-configuration/ssh-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage the SSH accounts on the device.

Docs: https://developer.axis.com/vapix/device-configuration/ssh-management/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

CommentType = Annotated[str, Field(min_length=0, max_length=256, pattern="^[^: ]*$")]
PasswordType = Annotated[str, Field(min_length=1, max_length=256)]
UsernameType = Annotated[str, Field(min_length=1, max_length=32, pattern="^[a-z*][a-z0-9-*]*[$]?$")]


class User(Model):
    """The SSH users collection"""

    comment: CommentType | None = None
    """The full name or comment of the SSH user"""
    username: UsernameType
    """The user name of the SSH user"""


class Ssh(Model):
    """The whole API tree."""

    users: list[User] | None = None


class UpdateUserRequest(Model):
    """Arguments of ``update_user``."""

    username: UsernameType
    password: PasswordType | None = None
    """The password of the SSH user"""
    comment: CommentType | None = None
    """The full name or comment of the SSH user"""


class AddUserRequest(Model):
    """Arguments of ``add_user``."""

    comment: CommentType | None = None
    """The full name or comment of the SSH user"""
    password: PasswordType
    """The password of the SSH user"""
    username: UsernameType
    """The user name of the SSH user"""


class UsernameRequest(Model):
    username: UsernameType


class SetUserPasswordRequest(Model):
    username: UsernameType
    password: PasswordType
    """The password of the SSH user"""


class SetUserCommentRequest(Model):
    username: UsernameType
    comment: CommentType
    """The full name or comment of the SSH user"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/ssh/v2"

INFO = ApiInfo(
    id="ssh-config",
    name="SSH management API",
    family=Family.DCA,
    discovery=(DcaDiscovery("ssh", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/ssh-management/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Ssh, access="admin", effect="read")
    list_users = Operation(
        INFO, "list_users", DcaBinding("GET", f"{ROOT}/users"), result=list[User], access="admin", effect="read"
    )
    get_user = Operation(
        INFO,
        "get_user",
        DcaBinding("GET", f"{ROOT}/users/{{username}}"),
        params=UsernameRequest,
        result=User,
        access="admin",
        effect="read",
    )
    update_user = Operation(
        INFO,
        "update_user",
        DcaBinding("PATCH", f"{ROOT}/users/{{username}}", body="object"),
        params=UpdateUserRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    add_user = Operation(
        INFO,
        "add_user",
        DcaBinding("POST", f"{ROOT}/users", body="object"),
        params=AddUserRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_user = Operation(
        INFO,
        "remove_user",
        DcaBinding("DELETE", f"{ROOT}/users/{{username}}"),
        params=UsernameRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_user_password = Operation(
        INFO,
        "set_user_password",
        DcaBinding("PATCH", f"{ROOT}/users/{{username}}/password", body="value", body_field="password"),
        params=SetUserPasswordRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_user_comment = Operation(
        INFO,
        "set_user_comment",
        DcaBinding("PATCH", f"{ROOT}/users/{{username}}/comment", body="value", body_field="comment"),
        params=SetUserCommentRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SshConfigApi(SyncApi):
    """SSH management API (``ssh-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Ssh:
        """All data of the SSH Management API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_users(self, *, request_options: RequestOptions | None = None) -> list[User]:
        """List the users. Access: admin."""
        return self._run(OPS.list_users, None, {}, request_options)

    def get_user(self, username: UsernameType, *, request_options: RequestOptions | None = None) -> User:
        """Get one user. Access: admin."""
        return self._run(OPS.get_user, None, {"username": username}, request_options)

    def update_user(
        self,
        username: UsernameType,
        *,
        password: PasswordType | MISSING = MISSING,
        comment: CommentType | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update a user. Changes only the fields given. Access: admin."""
        self._run(
            OPS.update_user, None, {"username": username, "password": password, "comment": comment}, request_options
        )

    def add_user(
        self,
        *,
        comment: CommentType | MISSING = MISSING,
        password: PasswordType,
        username: UsernameType,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Add a user. Access: admin."""
        self._run(OPS.add_user, None, {"comment": comment, "password": password, "username": username}, request_options)

    def remove_user(self, username: UsernameType, *, request_options: RequestOptions | None = None) -> None:
        """Remove a user. Access: admin."""
        self._run(OPS.remove_user, None, {"username": username}, request_options)

    def set_user_password(
        self, username: UsernameType, password: PasswordType, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the password of a user. Changes only the fields given. Access: admin."""
        self._run(OPS.set_user_password, None, {"username": username, "password": password}, request_options)

    def set_user_comment(
        self, username: UsernameType, comment: CommentType, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the comment (full name) of a user. Changes only the fields given. Access: admin."""
        self._run(OPS.set_user_comment, None, {"username": username, "comment": comment}, request_options)


class AsyncSshConfigApi(AsyncApi):
    """SSH management API (``ssh-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Ssh:
        """All data of the SSH Management API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_users(self, *, request_options: RequestOptions | None = None) -> list[User]:
        """List the users. Access: admin."""
        return await self._run(OPS.list_users, None, {}, request_options)

    async def get_user(self, username: UsernameType, *, request_options: RequestOptions | None = None) -> User:
        """Get one user. Access: admin."""
        return await self._run(OPS.get_user, None, {"username": username}, request_options)

    async def update_user(
        self,
        username: UsernameType,
        *,
        password: PasswordType | MISSING = MISSING,
        comment: CommentType | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update a user. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.update_user, None, {"username": username, "password": password, "comment": comment}, request_options
        )

    async def add_user(
        self,
        *,
        comment: CommentType | MISSING = MISSING,
        password: PasswordType,
        username: UsernameType,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Add a user. Access: admin."""
        await self._run(
            OPS.add_user, None, {"comment": comment, "password": password, "username": username}, request_options
        )

    async def remove_user(self, username: UsernameType, *, request_options: RequestOptions | None = None) -> None:
        """Remove a user. Access: admin."""
        await self._run(OPS.remove_user, None, {"username": username}, request_options)

    async def set_user_password(
        self, username: UsernameType, password: PasswordType, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the password of a user. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_user_password, None, {"username": username, "password": password}, request_options)

    async def set_user_comment(
        self, username: UsernameType, comment: CommentType, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the comment (full name) of a user. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_user_comment, None, {"username": username, "comment": comment}, request_options)
