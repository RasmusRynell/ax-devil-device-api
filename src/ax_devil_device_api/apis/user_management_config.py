# GENERATED from specs/apis/device-configuration/user-management-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""View the available passphrase-complexity policies and manage the one in use.

Docs: https://developer.axis.com/vapix/device-configuration/user-management-v2-api/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PassphrasePolicy(Model):
    """A passphrase policy"""

    desc: str
    """The description of the policy"""
    id: str
    """Unique identifier for a PassphraseProfile"""


PassphrasePolicyList = list[PassphrasePolicy]


class PassphraseComplexity(Model):
    """Passphrase complexity"""

    policies: PassphrasePolicyList | None = None
    """Available passphrase complexity policies"""
    policy: str | None = None
    """Selected passphrase complexity policy"""


class Settings(Model):
    """Global settings for User Management"""

    passphrase_complexity: PassphraseComplexity | None = Field(
        default=None, validation_alias="passphraseComplexity", serialization_alias="passphraseComplexity"
    )


class UserManagement(Model):
    """The whole API tree."""

    settings: Settings | None = None


class SetPassphraseComplexityPolicyRequest(Model):
    policy: str
    """Id of the selected passphrase-complexity policy"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/user-management/v2"

INFO = ApiInfo(
    id="user-management-config",
    name="User management API",
    family=Family.DCA,
    discovery=(DcaDiscovery("user-management", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/user-management-v2-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=UserManagement, access="admin", effect="read")
    get_settings = Operation(
        INFO, "get_settings", DcaBinding("GET", f"{ROOT}/settings"), result=Settings, access="admin", effect="read"
    )
    get_passphrase_complexity = Operation(
        INFO,
        "get_passphrase_complexity",
        DcaBinding("GET", f"{ROOT}/settings/passphraseComplexity"),
        result=PassphraseComplexity,
        access="admin",
        effect="read",
    )
    list_passphrase_policies = Operation(
        INFO,
        "list_passphrase_policies",
        DcaBinding("GET", f"{ROOT}/settings/passphraseComplexity/policies"),
        result=PassphrasePolicyList,
        access="viewer",
        effect="read",
    )
    get_passphrase_complexity_policy = Operation(
        INFO,
        "get_passphrase_complexity_policy",
        DcaBinding("GET", f"{ROOT}/settings/passphraseComplexity/policy"),
        result=str,
        access="viewer",
        effect="read",
    )
    set_passphrase_complexity_policy = Operation(
        INFO,
        "set_passphrase_complexity_policy",
        DcaBinding("PATCH", f"{ROOT}/settings/passphraseComplexity/policy", body="value", body_field="policy"),
        params=SetPassphraseComplexityPolicyRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class UserManagementConfigApi(SyncApi):
    """User management API (``user-management-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> UserManagement:
        """All data of the User management API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_settings(self, *, request_options: RequestOptions | None = None) -> Settings:
        """Get the global User management settings. Access: admin."""
        return self._run(OPS.get_settings, None, {}, request_options)

    def get_passphrase_complexity(self, *, request_options: RequestOptions | None = None) -> PassphraseComplexity:
        """Get the passphrase complexity settings. Access: admin."""
        return self._run(OPS.get_passphrase_complexity, None, {}, request_options)

    def list_passphrase_policies(self, *, request_options: RequestOptions | None = None) -> PassphrasePolicyList:
        """List the available passphrase-complexity policies.

        Available without access rights on a factory-reset unit until the first account is registered.

        Access: viewer.
        """
        return self._run(OPS.list_passphrase_policies, None, {}, request_options)

    def get_passphrase_complexity_policy(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the passphrase-complexity policy in use. Access: viewer."""
        return self._run(OPS.get_passphrase_complexity_policy, None, {}, request_options)

    def set_passphrase_complexity_policy(self, policy: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the passphrase-complexity policy in use. Changes only the fields given. Access: admin."""
        self._run(OPS.set_passphrase_complexity_policy, None, {"policy": policy}, request_options)


class AsyncUserManagementConfigApi(AsyncApi):
    """User management API (``user-management-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> UserManagement:
        """All data of the User management API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_settings(self, *, request_options: RequestOptions | None = None) -> Settings:
        """Get the global User management settings. Access: admin."""
        return await self._run(OPS.get_settings, None, {}, request_options)

    async def get_passphrase_complexity(self, *, request_options: RequestOptions | None = None) -> PassphraseComplexity:
        """Get the passphrase complexity settings. Access: admin."""
        return await self._run(OPS.get_passphrase_complexity, None, {}, request_options)

    async def list_passphrase_policies(self, *, request_options: RequestOptions | None = None) -> PassphrasePolicyList:
        """List the available passphrase-complexity policies.

        Available without access rights on a factory-reset unit until the first account is registered.

        Access: viewer.
        """
        return await self._run(OPS.list_passphrase_policies, None, {}, request_options)

    async def get_passphrase_complexity_policy(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the passphrase-complexity policy in use. Access: viewer."""
        return await self._run(OPS.get_passphrase_complexity_policy, None, {}, request_options)

    async def set_passphrase_complexity_policy(
        self, policy: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the passphrase-complexity policy in use. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_passphrase_complexity_policy, None, {"policy": policy}, request_options)
