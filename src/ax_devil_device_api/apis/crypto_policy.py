# GENERATED from specs/apis/device-configuration/crypto-policy-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Choose the cryptographic policy that defines which algorithms and protocols the device's services may use.

Docs: https://developer.axis.com/vapix/device-configuration/cryptographic-policy-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Name = Annotated[str, Field(min_length=1, max_length=32)]
NiceName = Annotated[str, Field(min_length=1, max_length=128)]
PolDescription = Annotated[str, Field(max_length=1024)]


class Policy(Model):
    """The cryptographic policies"""

    description: PolDescription
    """The policy description"""
    name: Name
    """The policy identifier"""
    nice_name: NiceName
    """Human friendly name for the policy"""


class CryptoPolicy(Model):
    """The whole API tree."""

    active_policy: Name
    """The cryptographic policy that is active"""
    policies: list[Policy]


class SetActivePolicyRequest(Model):
    active_policy: Name
    """The cryptographic policy that is active"""


class PolicyNameRequest(Model):
    name: Name


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/crypto-policy/v1"

INFO = ApiInfo(
    id="crypto-policy-config",
    name="Cryptographic policy",
    family=Family.DCA,
    discovery=(DcaDiscovery("crypto-policy", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/cryptographic-policy-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=CryptoPolicy, access="viewer", effect="read")
    get_active_policy = Operation(
        INFO,
        "get_active_policy",
        DcaBinding("GET", f"{ROOT}/active_policy"),
        result=Name,
        access="viewer",
        effect="read",
    )
    set_active_policy = Operation(
        INFO,
        "set_active_policy",
        DcaBinding("PATCH", f"{ROOT}/active_policy", body="value", body_field="active_policy"),
        params=SetActivePolicyRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_policies = Operation(
        INFO,
        "list_policies",
        DcaBinding("GET", f"{ROOT}/policies"),
        result=list[Policy],
        access="viewer",
        effect="read",
    )
    get_policy = Operation(
        INFO,
        "get_policy",
        DcaBinding("GET", f"{ROOT}/policies/{{name}}"),
        params=PolicyNameRequest,
        result=Policy,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class CryptoPolicyApi(SyncApi):
    """Cryptographic policy (``crypto-policy-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> CryptoPolicy:
        """The active policy and all available policies. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_active_policy(self, *, request_options: RequestOptions | None = None) -> Name:
        """Name of the active cryptographic policy. Access: viewer."""
        return self._run(OPS.get_active_policy, None, {}, request_options)

    def set_active_policy(self, *, active_policy: Name, request_options: RequestOptions | None = None) -> None:
        """Set the active policy of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_active_policy, None, {"active_policy": active_policy}, request_options)

    def list_policies(self, *, request_options: RequestOptions | None = None) -> list[Policy]:
        """List the policies. Access: viewer."""
        return self._run(OPS.list_policies, None, {}, request_options)

    def get_policy(self, name: Name, *, request_options: RequestOptions | None = None) -> Policy:
        """Get one policy. Access: viewer."""
        return self._run(OPS.get_policy, None, {"name": name}, request_options)


class AsyncCryptoPolicyApi(AsyncApi):
    """Cryptographic policy (``crypto-policy-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> CryptoPolicy:
        """The active policy and all available policies. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_active_policy(self, *, request_options: RequestOptions | None = None) -> Name:
        """Name of the active cryptographic policy. Access: viewer."""
        return await self._run(OPS.get_active_policy, None, {}, request_options)

    async def set_active_policy(self, *, active_policy: Name, request_options: RequestOptions | None = None) -> None:
        """Set the active policy of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_active_policy, None, {"active_policy": active_policy}, request_options)

    async def list_policies(self, *, request_options: RequestOptions | None = None) -> list[Policy]:
        """List the policies. Access: viewer."""
        return await self._run(OPS.list_policies, None, {}, request_options)

    async def get_policy(self, name: Name, *, request_options: RequestOptions | None = None) -> Policy:
        """Get one policy. Access: viewer."""
        return await self._run(OPS.get_policy, None, {"name": name}, request_options)
