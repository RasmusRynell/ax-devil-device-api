# GENERATED from specs/apis/device-configuration/oauth-ccgrant-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the claims and JWKS URI used to verify OAuth2 access tokens for machine-to-machine requests (client credentials grant).

Docs: https://developer.axis.com/vapix/device-configuration/client-credential-grants-configuration/
"""

from __future__ import annotations

from typing import Annotated, Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

OptionalClaim = Annotated[str, Field(max_length=256, pattern="^.*$")]
RequiredClaim = Annotated[str, Field(min_length=1, max_length=256, pattern="^.*$")]
JwksUrl = Annotated[str, Field(min_length=1, max_length=256, pattern="^[\\w \"'.:\\-\\/\\/~?]+$")]


class AuthEntity(Model):
    """Client authentication properties."""

    ccg_authz_admin_claim: OptionalClaim | None = Field(
        default=None, validation_alias="CCG_AuthzAdminClaim", serialization_alias="CCG_AuthzAdminClaim"
    )
    """Claim and value corresponding to admin access."""
    ccg_authz_operator_claim: OptionalClaim | None = Field(
        default=None, validation_alias="CCG_AuthzOperatorClaim", serialization_alias="CCG_AuthzOperatorClaim"
    )
    """Claim and value corresponding to operator access."""
    ccg_authz_viewer_claim: OptionalClaim | None = Field(
        default=None, validation_alias="CCG_AuthzViewerClaim", serialization_alias="CCG_AuthzViewerClaim"
    )
    """Claim and value corresponding to viewer access."""
    ccg_o_auth2_token_verify: JwksUrl | None = Field(
        default=None, validation_alias="CCG_OAuth2TokenVerify", serialization_alias="CCG_OAuth2TokenVerify"
    )
    """JWKS URI that serves the public keys."""
    ccg_require_claim: RequiredClaim | None = Field(
        default=None, validation_alias="CCG_RequireClaim", serialization_alias="CCG_RequireClaim"
    )
    """Claim that every request token must carry; one of admin, operator or viewer claims assigns the access level."""


class OauthCcgrant(Model):
    """The whole API tree."""

    auth_entity: AuthEntity | None = Field(
        default=None, validation_alias="AuthEntity", serialization_alias="AuthEntity"
    )


class UpdateAllRequest(Model):
    """Arguments of ``update_all``. Only the given fields change."""

    auth_entity: AuthEntity | None = Field(
        default=None, validation_alias="AuthEntity", serialization_alias="AuthEntity"
    )


class UpdateAuthEntityRequest(Model):
    """Arguments of ``update_auth_entity``. Only the given fields change."""

    ccg_authz_admin_claim: OptionalClaim | None = Field(
        default=None, validation_alias="CCG_AuthzAdminClaim", serialization_alias="CCG_AuthzAdminClaim"
    )
    """Claim and value corresponding to admin access."""
    ccg_authz_operator_claim: OptionalClaim | None = Field(
        default=None, validation_alias="CCG_AuthzOperatorClaim", serialization_alias="CCG_AuthzOperatorClaim"
    )
    """Claim and value corresponding to operator access."""
    ccg_authz_viewer_claim: OptionalClaim | None = Field(
        default=None, validation_alias="CCG_AuthzViewerClaim", serialization_alias="CCG_AuthzViewerClaim"
    )
    """Claim and value corresponding to viewer access."""
    ccg_o_auth2_token_verify: JwksUrl | None = Field(
        default=None, validation_alias="CCG_OAuth2TokenVerify", serialization_alias="CCG_OAuth2TokenVerify"
    )
    """JWKS URI that serves the public keys."""
    ccg_require_claim: RequiredClaim | None = Field(
        default=None, validation_alias="CCG_RequireClaim", serialization_alias="CCG_RequireClaim"
    )
    """Claim that every request token must carry; one of admin, operator or viewer claims assigns the access level."""

    @classmethod
    def from_current(cls, entity: AuthEntity) -> UpdateAuthEntityRequest:
        """A request that rewrites ``entity`` unchanged: copy it, edit fields, send it back."""
        data = entity.request_data()
        return cls.from_response_data(data)


class SetAuthzAdminClaimRequest(Model):
    ccg_authz_admin_claim: OptionalClaim = Field(
        validation_alias="CCG_AuthzAdminClaim", serialization_alias="CCG_AuthzAdminClaim"
    )


class SetAuthzOperatorClaimRequest(Model):
    ccg_authz_operator_claim: OptionalClaim = Field(
        validation_alias="CCG_AuthzOperatorClaim", serialization_alias="CCG_AuthzOperatorClaim"
    )


class SetAuthzViewerClaimRequest(Model):
    ccg_authz_viewer_claim: OptionalClaim = Field(
        validation_alias="CCG_AuthzViewerClaim", serialization_alias="CCG_AuthzViewerClaim"
    )


class SetOauth2TokenVerifyRequest(Model):
    ccg_o_auth2_token_verify: JwksUrl = Field(
        validation_alias="CCG_OAuth2TokenVerify", serialization_alias="CCG_OAuth2TokenVerify"
    )


class SetRequireClaimRequest(Model):
    ccg_require_claim: RequiredClaim = Field(
        validation_alias="CCG_RequireClaim", serialization_alias="CCG_RequireClaim"
    )


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/oauth-ccgrant/v1beta"

INFO = ApiInfo(
    id="oauth-ccgrant-config",
    name="Client credential grants configuration",
    family=Family.DCA,
    discovery=(DcaDiscovery("oauth-ccgrant", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/client-credential-grants-configuration/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=OauthCcgrant, access="admin", effect="read")
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_auth_entity = Operation(
        INFO,
        "get_auth_entity",
        DcaBinding("GET", f"{ROOT}/AuthEntity"),
        result=AuthEntity,
        access="admin",
        effect="read",
    )
    update_auth_entity = Operation(
        INFO,
        "update_auth_entity",
        DcaBinding("PATCH", f"{ROOT}/AuthEntity", body="object"),
        params=UpdateAuthEntityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_authz_admin_claim = Operation(
        INFO,
        "get_authz_admin_claim",
        DcaBinding("GET", f"{ROOT}/AuthEntity/CCG_AuthzAdminClaim"),
        result=OptionalClaim,
        access="admin",
        effect="read",
    )
    set_authz_admin_claim = Operation(
        INFO,
        "set_authz_admin_claim",
        DcaBinding("PATCH", f"{ROOT}/AuthEntity/CCG_AuthzAdminClaim", body="value", body_field="CCG_AuthzAdminClaim"),
        params=SetAuthzAdminClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_authz_operator_claim = Operation(
        INFO,
        "get_authz_operator_claim",
        DcaBinding("GET", f"{ROOT}/AuthEntity/CCG_AuthzOperatorClaim"),
        result=OptionalClaim,
        access="admin",
        effect="read",
    )
    set_authz_operator_claim = Operation(
        INFO,
        "set_authz_operator_claim",
        DcaBinding(
            "PATCH", f"{ROOT}/AuthEntity/CCG_AuthzOperatorClaim", body="value", body_field="CCG_AuthzOperatorClaim"
        ),
        params=SetAuthzOperatorClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_authz_viewer_claim = Operation(
        INFO,
        "get_authz_viewer_claim",
        DcaBinding("GET", f"{ROOT}/AuthEntity/CCG_AuthzViewerClaim"),
        result=OptionalClaim,
        access="admin",
        effect="read",
    )
    set_authz_viewer_claim = Operation(
        INFO,
        "set_authz_viewer_claim",
        DcaBinding("PATCH", f"{ROOT}/AuthEntity/CCG_AuthzViewerClaim", body="value", body_field="CCG_AuthzViewerClaim"),
        params=SetAuthzViewerClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_oauth2_token_verify = Operation(
        INFO,
        "get_oauth2_token_verify",
        DcaBinding("GET", f"{ROOT}/AuthEntity/CCG_OAuth2TokenVerify"),
        result=JwksUrl,
        access="admin",
        effect="read",
    )
    set_oauth2_token_verify = Operation(
        INFO,
        "set_oauth2_token_verify",
        DcaBinding(
            "PATCH",
            f"{ROOT}/AuthEntity/CCG_OAuth2TokenVerify",
            body="value",
            body_field="CCG_OAuth2TokenVerify",
            sensitive=True,
        ),
        params=SetOauth2TokenVerifyRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_require_claim = Operation(
        INFO,
        "get_require_claim",
        DcaBinding("GET", f"{ROOT}/AuthEntity/CCG_RequireClaim"),
        result=RequiredClaim,
        access="admin",
        effect="read",
    )
    set_require_claim = Operation(
        INFO,
        "set_require_claim",
        DcaBinding("PATCH", f"{ROOT}/AuthEntity/CCG_RequireClaim", body="value", body_field="CCG_RequireClaim"),
        params=SetRequireClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class OauthCcgrantApi(SyncApi):
    """Client credential grants configuration (``oauth-ccgrant-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> OauthCcgrant:
        """All client credential grant settings. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    @overload
    def update_all(self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_all(
        self, /, *, auth_entity: AuthEntity | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None: ...
    def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the client credential grant settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_all, request, kwargs, request_options)

    def get_auth_entity(self, *, request_options: RequestOptions | None = None) -> AuthEntity:
        """Get the authentication settings. Access: admin."""
        return self._run(OPS.get_auth_entity, None, {}, request_options)

    @overload
    def update_auth_entity(
        self, request: UpdateAuthEntityRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_auth_entity(
        self,
        /,
        *,
        ccg_authz_admin_claim: OptionalClaim | MISSING = MISSING,
        ccg_authz_operator_claim: OptionalClaim | MISSING = MISSING,
        ccg_authz_viewer_claim: OptionalClaim | MISSING = MISSING,
        ccg_o_auth2_token_verify: JwksUrl | MISSING = MISSING,
        ccg_require_claim: RequiredClaim | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_auth_entity(
        self,
        request: UpdateAuthEntityRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the authentication settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_auth_entity, request, kwargs, request_options)

    def get_authz_admin_claim(self, *, request_options: RequestOptions | None = None) -> OptionalClaim:
        """Get the authz admin claim setting. Access: admin."""
        return self._run(OPS.get_authz_admin_claim, None, {}, request_options)

    def set_authz_admin_claim(
        self, *, ccg_authz_admin_claim: OptionalClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz admin claim setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_authz_admin_claim, None, {"ccg_authz_admin_claim": ccg_authz_admin_claim}, request_options)

    def get_authz_operator_claim(self, *, request_options: RequestOptions | None = None) -> OptionalClaim:
        """Get the authz operator claim setting. Access: admin."""
        return self._run(OPS.get_authz_operator_claim, None, {}, request_options)

    def set_authz_operator_claim(
        self, *, ccg_authz_operator_claim: OptionalClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz operator claim setting. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_authz_operator_claim, None, {"ccg_authz_operator_claim": ccg_authz_operator_claim}, request_options
        )

    def get_authz_viewer_claim(self, *, request_options: RequestOptions | None = None) -> OptionalClaim:
        """Get the authz viewer claim setting. Access: admin."""
        return self._run(OPS.get_authz_viewer_claim, None, {}, request_options)

    def set_authz_viewer_claim(
        self, *, ccg_authz_viewer_claim: OptionalClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz viewer claim setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_authz_viewer_claim, None, {"ccg_authz_viewer_claim": ccg_authz_viewer_claim}, request_options)

    def get_oauth2_token_verify(self, *, request_options: RequestOptions | None = None) -> JwksUrl:
        """Get the oauth2 token verify setting. Access: admin."""
        return self._run(OPS.get_oauth2_token_verify, None, {}, request_options)

    def set_oauth2_token_verify(
        self, *, ccg_o_auth2_token_verify: JwksUrl, request_options: RequestOptions | None = None
    ) -> None:
        """Set the oauth2 token verify setting. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_oauth2_token_verify, None, {"ccg_o_auth2_token_verify": ccg_o_auth2_token_verify}, request_options
        )

    def get_require_claim(self, *, request_options: RequestOptions | None = None) -> RequiredClaim:
        """Get the require claim setting. Access: admin."""
        return self._run(OPS.get_require_claim, None, {}, request_options)

    def set_require_claim(
        self, *, ccg_require_claim: RequiredClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the require claim setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_require_claim, None, {"ccg_require_claim": ccg_require_claim}, request_options)


class AsyncOauthCcgrantApi(AsyncApi):
    """Client credential grants configuration (``oauth-ccgrant-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> OauthCcgrant:
        """All client credential grant settings. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    @overload
    async def update_all(
        self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_all(
        self, /, *, auth_entity: AuthEntity | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None: ...
    async def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the client credential grant settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_all, request, kwargs, request_options)

    async def get_auth_entity(self, *, request_options: RequestOptions | None = None) -> AuthEntity:
        """Get the authentication settings. Access: admin."""
        return await self._run(OPS.get_auth_entity, None, {}, request_options)

    @overload
    async def update_auth_entity(
        self, request: UpdateAuthEntityRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_auth_entity(
        self,
        /,
        *,
        ccg_authz_admin_claim: OptionalClaim | MISSING = MISSING,
        ccg_authz_operator_claim: OptionalClaim | MISSING = MISSING,
        ccg_authz_viewer_claim: OptionalClaim | MISSING = MISSING,
        ccg_o_auth2_token_verify: JwksUrl | MISSING = MISSING,
        ccg_require_claim: RequiredClaim | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_auth_entity(
        self,
        request: UpdateAuthEntityRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the authentication settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_auth_entity, request, kwargs, request_options)

    async def get_authz_admin_claim(self, *, request_options: RequestOptions | None = None) -> OptionalClaim:
        """Get the authz admin claim setting. Access: admin."""
        return await self._run(OPS.get_authz_admin_claim, None, {}, request_options)

    async def set_authz_admin_claim(
        self, *, ccg_authz_admin_claim: OptionalClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz admin claim setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_authz_admin_claim, None, {"ccg_authz_admin_claim": ccg_authz_admin_claim}, request_options
        )

    async def get_authz_operator_claim(self, *, request_options: RequestOptions | None = None) -> OptionalClaim:
        """Get the authz operator claim setting. Access: admin."""
        return await self._run(OPS.get_authz_operator_claim, None, {}, request_options)

    async def set_authz_operator_claim(
        self, *, ccg_authz_operator_claim: OptionalClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz operator claim setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_authz_operator_claim, None, {"ccg_authz_operator_claim": ccg_authz_operator_claim}, request_options
        )

    async def get_authz_viewer_claim(self, *, request_options: RequestOptions | None = None) -> OptionalClaim:
        """Get the authz viewer claim setting. Access: admin."""
        return await self._run(OPS.get_authz_viewer_claim, None, {}, request_options)

    async def set_authz_viewer_claim(
        self, *, ccg_authz_viewer_claim: OptionalClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz viewer claim setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_authz_viewer_claim, None, {"ccg_authz_viewer_claim": ccg_authz_viewer_claim}, request_options
        )

    async def get_oauth2_token_verify(self, *, request_options: RequestOptions | None = None) -> JwksUrl:
        """Get the oauth2 token verify setting. Access: admin."""
        return await self._run(OPS.get_oauth2_token_verify, None, {}, request_options)

    async def set_oauth2_token_verify(
        self, *, ccg_o_auth2_token_verify: JwksUrl, request_options: RequestOptions | None = None
    ) -> None:
        """Set the oauth2 token verify setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_oauth2_token_verify, None, {"ccg_o_auth2_token_verify": ccg_o_auth2_token_verify}, request_options
        )

    async def get_require_claim(self, *, request_options: RequestOptions | None = None) -> RequiredClaim:
        """Get the require claim setting. Access: admin."""
        return await self._run(OPS.get_require_claim, None, {}, request_options)

    async def set_require_claim(
        self, *, ccg_require_claim: RequiredClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the require claim setting. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_require_claim, None, {"ccg_require_claim": ccg_require_claim}, request_options)
