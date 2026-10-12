# GENERATED from specs/apis/device-configuration/oidcsetup-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Set up OpenID Connect so users can log in to the device with the authorization code flow.

Docs: https://developer.axis.com/vapix/device-configuration/openid-connect-setup/
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

Claim = Annotated[str, Field(min_length=1, max_length=256, pattern="^.*$")]
RemoteUserClaim = Annotated[
    str, Field(min_length=1, max_length=64, pattern='^(sub|email|preferred_username|("[a-zA-Z0-9]*"))$')
]
ClientId = Annotated[str, Field(min_length=1, max_length=256)]
ClientSecret = Annotated[str, Field(min_length=1, max_length=256)]
Proxy = Annotated[str, Field(max_length=256, pattern="^[\\w \"'.:\\/\\/?]*$")]
ScopeList = Annotated[str, Field(max_length=256, pattern="^[\\w \"'.:\\/\\/?]*$")]
MetadataUrl = Annotated[str, Field(min_length=1, max_length=256, pattern="^[\\w \"'.:\\-\\/\\/~?]+$")]


class AuthEntity(Model):
    """Client authentication properties. The client secret is never returned."""

    oidc_authz_admin_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_AuthzAdminClaim", serialization_alias="OIDC_AuthzAdminClaim"
    )
    """Claim and value that corresponds to admin access."""
    oidc_authz_operator_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_AuthzOperatorClaim", serialization_alias="OIDC_AuthzOperatorClaim"
    )
    """Claim and value that corresponds to operator access."""
    oidc_authz_scopes: ScopeList | None = Field(
        default=None, validation_alias="OIDC_AuthzScopes", serialization_alias="OIDC_AuthzScopes"
    )
    """Optional list of additional scopes."""
    oidc_authz_viewer_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_AuthzViewerClaim", serialization_alias="OIDC_AuthzViewerClaim"
    )
    """Claim and value that corresponds to viewer access."""
    oidc_client_id: ClientId | None = Field(
        default=None, validation_alias="OIDC_ClientID", serialization_alias="OIDC_ClientID"
    )
    """OIDC client ID."""


class BaseConfigEntity(Model):
    """Required configuration for the OIDC client."""

    oidc_outgoing_proxy: Proxy | None = Field(
        default=None, validation_alias="OIDC_OutgoingProxy", serialization_alias="OIDC_OutgoingProxy"
    )
    """Proxy configuration. An empty string clears it."""
    oidc_provider_metadata_url: MetadataUrl | None = Field(
        default=None, validation_alias="OIDC_ProviderMetadataURL", serialization_alias="OIDC_ProviderMetadataURL"
    )
    """OIDC discovery API endpoint. Required format https://<host>/<optional directory>/.well-known/openid-configuration"""
    oidc_remote_user_claim: RemoteUserClaim | None = Field(
        default=None, validation_alias="OIDC_RemoteUserClaim", serialization_alias="OIDC_RemoteUserClaim"
    )
    """Claim identifying the logged in user (sub, email, preferred_username)."""
    oidc_require_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_RequireClaim", serialization_alias="OIDC_RequireClaim"
    )
    """Claim validated for all requests."""
    auth_entity: AuthEntity | None = Field(
        default=None, validation_alias="AuthEntity", serialization_alias="AuthEntity"
    )


class Oidcsetup(Model):
    """The whole API tree."""

    base_config_entity: BaseConfigEntity | None = Field(
        default=None, validation_alias="BaseConfigEntity", serialization_alias="BaseConfigEntity"
    )


class UpdateAuthEntityRequest(Model):
    """Arguments of ``update_auth_entity``. Only the given fields change."""

    oidc_authz_admin_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_AuthzAdminClaim", serialization_alias="OIDC_AuthzAdminClaim"
    )
    """Claim and value that corresponds to admin access."""
    oidc_authz_operator_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_AuthzOperatorClaim", serialization_alias="OIDC_AuthzOperatorClaim"
    )
    """Claim and value that corresponds to operator access."""
    oidc_authz_scopes: ScopeList | None = Field(
        default=None, validation_alias="OIDC_AuthzScopes", serialization_alias="OIDC_AuthzScopes"
    )
    """Optional list of additional scopes."""
    oidc_authz_viewer_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_AuthzViewerClaim", serialization_alias="OIDC_AuthzViewerClaim"
    )
    """Claim and value that corresponds to viewer access."""
    oidc_client_id: ClientId | None = Field(
        default=None, validation_alias="OIDC_ClientID", serialization_alias="OIDC_ClientID"
    )
    """OIDC client ID."""
    oidc_client_secret: ClientSecret | None = Field(
        default=None, validation_alias="OIDC_ClientSecret", serialization_alias="OIDC_ClientSecret"
    )
    """OIDC client secret. Write-only: the device never returns it."""

    @classmethod
    def from_current(cls, entity: AuthEntity) -> UpdateAuthEntityRequest:
        """A request that rewrites ``entity`` unchanged: copy it, edit fields, send it back."""
        data = entity.request_data()
        return cls(**data)


class UpdateBaseConfigEntityRequest(Model):
    """Arguments of ``update_base_config_entity``. Only the given fields change."""

    oidc_outgoing_proxy: Proxy | None = Field(
        default=None, validation_alias="OIDC_OutgoingProxy", serialization_alias="OIDC_OutgoingProxy"
    )
    """Proxy configuration. An empty string clears it."""
    oidc_provider_metadata_url: MetadataUrl | None = Field(
        default=None, validation_alias="OIDC_ProviderMetadataURL", serialization_alias="OIDC_ProviderMetadataURL"
    )
    """OIDC discovery API endpoint. Required format https://<host>/<optional directory>/.well-known/openid-configuration"""
    oidc_remote_user_claim: RemoteUserClaim | None = Field(
        default=None, validation_alias="OIDC_RemoteUserClaim", serialization_alias="OIDC_RemoteUserClaim"
    )
    """Claim identifying the logged in user (sub, email, preferred_username)."""
    oidc_require_claim: Claim | None = Field(
        default=None, validation_alias="OIDC_RequireClaim", serialization_alias="OIDC_RequireClaim"
    )
    """Claim validated for all requests."""
    auth_entity: UpdateAuthEntityRequest | None = Field(
        default=None, validation_alias="AuthEntity", serialization_alias="AuthEntity"
    )

    @classmethod
    def from_current(cls, entity: BaseConfigEntity) -> UpdateBaseConfigEntityRequest:
        """A request that rewrites ``entity`` unchanged: copy it, edit fields, send it back."""
        data = entity.request_data()
        return cls(**data)


class UpdateAllRequest(Model):
    """Arguments of ``update_all``. Only the given fields change."""

    base_config_entity: UpdateBaseConfigEntityRequest | None = Field(
        default=None, validation_alias="BaseConfigEntity", serialization_alias="BaseConfigEntity"
    )


class SetOutgoingProxyRequest(Model):
    oidc_outgoing_proxy: Proxy = Field(validation_alias="OIDC_OutgoingProxy", serialization_alias="OIDC_OutgoingProxy")


class SetProviderMetadataUrlRequest(Model):
    oidc_provider_metadata_url: MetadataUrl = Field(
        validation_alias="OIDC_ProviderMetadataURL", serialization_alias="OIDC_ProviderMetadataURL"
    )


class SetRemoteUserClaimRequest(Model):
    oidc_remote_user_claim: RemoteUserClaim = Field(
        validation_alias="OIDC_RemoteUserClaim", serialization_alias="OIDC_RemoteUserClaim"
    )


class SetRequireClaimRequest(Model):
    oidc_require_claim: Claim = Field(validation_alias="OIDC_RequireClaim", serialization_alias="OIDC_RequireClaim")


class SetAuthzAdminClaimRequest(Model):
    oidc_authz_admin_claim: Claim = Field(
        validation_alias="OIDC_AuthzAdminClaim", serialization_alias="OIDC_AuthzAdminClaim"
    )


class SetAuthzOperatorClaimRequest(Model):
    oidc_authz_operator_claim: Claim = Field(
        validation_alias="OIDC_AuthzOperatorClaim", serialization_alias="OIDC_AuthzOperatorClaim"
    )


class SetAuthzScopesRequest(Model):
    oidc_authz_scopes: ScopeList = Field(validation_alias="OIDC_AuthzScopes", serialization_alias="OIDC_AuthzScopes")


class SetAuthzViewerClaimRequest(Model):
    oidc_authz_viewer_claim: Claim = Field(
        validation_alias="OIDC_AuthzViewerClaim", serialization_alias="OIDC_AuthzViewerClaim"
    )


class SetClientIdRequest(Model):
    oidc_client_id: ClientId = Field(validation_alias="OIDC_ClientID", serialization_alias="OIDC_ClientID")


class SetClientSecretRequest(Model):
    oidc_client_secret: ClientSecret = Field(
        validation_alias="OIDC_ClientSecret", serialization_alias="OIDC_ClientSecret"
    )


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/oidcsetup/v1"

INFO = ApiInfo(
    id="oidcsetup-config",
    name="OpenID Connect Setup",
    family=Family.DCA,
    discovery=(DcaDiscovery("oidcsetup", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/openid-connect-setup/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Oidcsetup, access="admin", effect="read")
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_base_config_entity = Operation(
        INFO,
        "get_base_config_entity",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity"),
        result=BaseConfigEntity,
        access="admin",
        effect="read",
    )
    update_base_config_entity = Operation(
        INFO,
        "update_base_config_entity",
        DcaBinding("PATCH", f"{ROOT}/BaseConfigEntity", body="object"),
        params=UpdateBaseConfigEntityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_outgoing_proxy = Operation(
        INFO,
        "get_outgoing_proxy",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/OIDC_OutgoingProxy"),
        result=Proxy,
        access="admin",
        effect="read",
    )
    set_outgoing_proxy = Operation(
        INFO,
        "set_outgoing_proxy",
        DcaBinding(
            "PATCH", f"{ROOT}/BaseConfigEntity/OIDC_OutgoingProxy", body="value", body_field="OIDC_OutgoingProxy"
        ),
        params=SetOutgoingProxyRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_provider_metadata_url = Operation(
        INFO,
        "get_provider_metadata_url",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/OIDC_ProviderMetadataURL"),
        result=MetadataUrl,
        access="admin",
        effect="read",
    )
    set_provider_metadata_url = Operation(
        INFO,
        "set_provider_metadata_url",
        DcaBinding(
            "PATCH",
            f"{ROOT}/BaseConfigEntity/OIDC_ProviderMetadataURL",
            body="value",
            body_field="OIDC_ProviderMetadataURL",
        ),
        params=SetProviderMetadataUrlRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_remote_user_claim = Operation(
        INFO,
        "get_remote_user_claim",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/OIDC_RemoteUserClaim"),
        result=RemoteUserClaim,
        access="admin",
        effect="read",
    )
    set_remote_user_claim = Operation(
        INFO,
        "set_remote_user_claim",
        DcaBinding(
            "PATCH", f"{ROOT}/BaseConfigEntity/OIDC_RemoteUserClaim", body="value", body_field="OIDC_RemoteUserClaim"
        ),
        params=SetRemoteUserClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_require_claim = Operation(
        INFO,
        "get_require_claim",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/OIDC_RequireClaim"),
        result=Claim,
        access="admin",
        effect="read",
    )
    set_require_claim = Operation(
        INFO,
        "set_require_claim",
        DcaBinding("PATCH", f"{ROOT}/BaseConfigEntity/OIDC_RequireClaim", body="value", body_field="OIDC_RequireClaim"),
        params=SetRequireClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_auth_entity = Operation(
        INFO,
        "get_auth_entity",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/AuthEntity"),
        result=AuthEntity,
        access="admin",
        effect="read",
    )
    update_auth_entity = Operation(
        INFO,
        "update_auth_entity",
        DcaBinding("PATCH", f"{ROOT}/BaseConfigEntity/AuthEntity", body="object"),
        params=UpdateAuthEntityRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_authz_admin_claim = Operation(
        INFO,
        "get_authz_admin_claim",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzAdminClaim"),
        result=Claim,
        access="admin",
        effect="read",
    )
    set_authz_admin_claim = Operation(
        INFO,
        "set_authz_admin_claim",
        DcaBinding(
            "PATCH",
            f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzAdminClaim",
            body="value",
            body_field="OIDC_AuthzAdminClaim",
        ),
        params=SetAuthzAdminClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_authz_operator_claim = Operation(
        INFO,
        "get_authz_operator_claim",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzOperatorClaim"),
        result=Claim,
        access="admin",
        effect="read",
    )
    set_authz_operator_claim = Operation(
        INFO,
        "set_authz_operator_claim",
        DcaBinding(
            "PATCH",
            f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzOperatorClaim",
            body="value",
            body_field="OIDC_AuthzOperatorClaim",
        ),
        params=SetAuthzOperatorClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_authz_scopes = Operation(
        INFO,
        "get_authz_scopes",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzScopes"),
        result=ScopeList,
        access="admin",
        effect="read",
    )
    set_authz_scopes = Operation(
        INFO,
        "set_authz_scopes",
        DcaBinding(
            "PATCH", f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzScopes", body="value", body_field="OIDC_AuthzScopes"
        ),
        params=SetAuthzScopesRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_authz_viewer_claim = Operation(
        INFO,
        "get_authz_viewer_claim",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzViewerClaim"),
        result=Claim,
        access="admin",
        effect="read",
    )
    set_authz_viewer_claim = Operation(
        INFO,
        "set_authz_viewer_claim",
        DcaBinding(
            "PATCH",
            f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_AuthzViewerClaim",
            body="value",
            body_field="OIDC_AuthzViewerClaim",
        ),
        params=SetAuthzViewerClaimRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_client_id = Operation(
        INFO,
        "get_client_id",
        DcaBinding("GET", f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_ClientID"),
        result=ClientId,
        access="admin",
        effect="read",
    )
    set_client_id = Operation(
        INFO,
        "set_client_id",
        DcaBinding(
            "PATCH", f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_ClientID", body="value", body_field="OIDC_ClientID"
        ),
        params=SetClientIdRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_client_secret = Operation(
        INFO,
        "set_client_secret",
        DcaBinding(
            "PATCH",
            f"{ROOT}/BaseConfigEntity/AuthEntity/OIDC_ClientSecret",
            body="value",
            body_field="OIDC_ClientSecret",
        ),
        params=SetClientSecretRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class OidcsetupApi(SyncApi):
    """OpenID Connect Setup (``oidcsetup-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Oidcsetup:
        """All OpenID Connect settings. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    @overload
    def update_all(self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def update_all(
        self,
        /,
        *,
        base_config_entity: UpdateBaseConfigEntityRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the OpenID Connect settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_all, request, kwargs, request_options)

    def get_base_config_entity(self, *, request_options: RequestOptions | None = None) -> BaseConfigEntity:
        """Get the base configuration, including the client authentication settings. Access: admin."""
        return self._run(OPS.get_base_config_entity, None, {}, request_options)

    @overload
    def update_base_config_entity(
        self, request: UpdateBaseConfigEntityRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_base_config_entity(
        self,
        /,
        *,
        oidc_outgoing_proxy: Proxy | MISSING = MISSING,
        oidc_provider_metadata_url: MetadataUrl | MISSING = MISSING,
        oidc_remote_user_claim: RemoteUserClaim | MISSING = MISSING,
        oidc_require_claim: Claim | MISSING = MISSING,
        auth_entity: UpdateAuthEntityRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_base_config_entity(
        self,
        request: UpdateBaseConfigEntityRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the base configuration, optionally with the client authentication settings.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_base_config_entity, request, kwargs, request_options)

    def get_outgoing_proxy(self, *, request_options: RequestOptions | None = None) -> Proxy:
        """Get the outgoing proxy setting. Access: admin."""
        return self._run(OPS.get_outgoing_proxy, None, {}, request_options)

    def set_outgoing_proxy(self, *, oidc_outgoing_proxy: Proxy, request_options: RequestOptions | None = None) -> None:
        """Set the outgoing proxy setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_outgoing_proxy, None, {"oidc_outgoing_proxy": oidc_outgoing_proxy}, request_options)

    def get_provider_metadata_url(self, *, request_options: RequestOptions | None = None) -> MetadataUrl:
        """Get the provider metadata url setting. Access: admin."""
        return self._run(OPS.get_provider_metadata_url, None, {}, request_options)

    def set_provider_metadata_url(
        self, *, oidc_provider_metadata_url: MetadataUrl, request_options: RequestOptions | None = None
    ) -> None:
        """Set the provider metadata url setting. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_provider_metadata_url,
            None,
            {"oidc_provider_metadata_url": oidc_provider_metadata_url},
            request_options,
        )

    def get_remote_user_claim(self, *, request_options: RequestOptions | None = None) -> RemoteUserClaim:
        """Get the remote user claim setting. Access: admin."""
        return self._run(OPS.get_remote_user_claim, None, {}, request_options)

    def set_remote_user_claim(
        self, *, oidc_remote_user_claim: RemoteUserClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the remote user claim setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_remote_user_claim, None, {"oidc_remote_user_claim": oidc_remote_user_claim}, request_options)

    def get_require_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the require claim setting. Access: admin."""
        return self._run(OPS.get_require_claim, None, {}, request_options)

    def set_require_claim(self, *, oidc_require_claim: Claim, request_options: RequestOptions | None = None) -> None:
        """Set the require claim setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_require_claim, None, {"oidc_require_claim": oidc_require_claim}, request_options)

    def get_auth_entity(self, *, request_options: RequestOptions | None = None) -> AuthEntity:
        """Get the client authentication settings. The client secret is never returned.

        Access: admin.
        """
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
        oidc_authz_admin_claim: Claim | MISSING = MISSING,
        oidc_authz_operator_claim: Claim | MISSING = MISSING,
        oidc_authz_scopes: ScopeList | MISSING = MISSING,
        oidc_authz_viewer_claim: Claim | MISSING = MISSING,
        oidc_client_id: ClientId | MISSING = MISSING,
        oidc_client_secret: ClientSecret | MISSING = MISSING,
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
        """Update the client authentication settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_auth_entity, request, kwargs, request_options)

    def get_authz_admin_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the authz admin claim setting. Access: admin."""
        return self._run(OPS.get_authz_admin_claim, None, {}, request_options)

    def set_authz_admin_claim(
        self, *, oidc_authz_admin_claim: Claim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz admin claim setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_authz_admin_claim, None, {"oidc_authz_admin_claim": oidc_authz_admin_claim}, request_options)

    def get_authz_operator_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the authz operator claim setting. Access: admin."""
        return self._run(OPS.get_authz_operator_claim, None, {}, request_options)

    def set_authz_operator_claim(
        self, *, oidc_authz_operator_claim: Claim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz operator claim setting. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_authz_operator_claim,
            None,
            {"oidc_authz_operator_claim": oidc_authz_operator_claim},
            request_options,
        )

    def get_authz_scopes(self, *, request_options: RequestOptions | None = None) -> ScopeList:
        """Get the authz scopes setting. Access: admin."""
        return self._run(OPS.get_authz_scopes, None, {}, request_options)

    def set_authz_scopes(self, *, oidc_authz_scopes: ScopeList, request_options: RequestOptions | None = None) -> None:
        """Set the authz scopes setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_authz_scopes, None, {"oidc_authz_scopes": oidc_authz_scopes}, request_options)

    def get_authz_viewer_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the authz viewer claim setting. Access: admin."""
        return self._run(OPS.get_authz_viewer_claim, None, {}, request_options)

    def set_authz_viewer_claim(
        self, *, oidc_authz_viewer_claim: Claim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz viewer claim setting. Changes only the fields given. Access: admin."""
        self._run(
            OPS.set_authz_viewer_claim, None, {"oidc_authz_viewer_claim": oidc_authz_viewer_claim}, request_options
        )

    def get_client_id(self, *, request_options: RequestOptions | None = None) -> ClientId:
        """Get the client id setting. Access: admin."""
        return self._run(OPS.get_client_id, None, {}, request_options)

    def set_client_id(self, *, oidc_client_id: ClientId, request_options: RequestOptions | None = None) -> None:
        """Set the client id setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_client_id, None, {"oidc_client_id": oidc_client_id}, request_options)

    def set_client_secret(
        self, *, oidc_client_secret: ClientSecret, request_options: RequestOptions | None = None
    ) -> None:
        """Set the client secret setting. Changes only the fields given. Access: admin."""
        self._run(OPS.set_client_secret, None, {"oidc_client_secret": oidc_client_secret}, request_options)


class AsyncOidcsetupApi(AsyncApi):
    """OpenID Connect Setup (``oidcsetup-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Oidcsetup:
        """All OpenID Connect settings. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    @overload
    async def update_all(
        self, request: UpdateAllRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_all(
        self,
        /,
        *,
        base_config_entity: UpdateBaseConfigEntityRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_all(
        self,
        request: UpdateAllRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the OpenID Connect settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_all, request, kwargs, request_options)

    async def get_base_config_entity(self, *, request_options: RequestOptions | None = None) -> BaseConfigEntity:
        """Get the base configuration, including the client authentication settings. Access: admin."""
        return await self._run(OPS.get_base_config_entity, None, {}, request_options)

    @overload
    async def update_base_config_entity(
        self, request: UpdateBaseConfigEntityRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_base_config_entity(
        self,
        /,
        *,
        oidc_outgoing_proxy: Proxy | MISSING = MISSING,
        oidc_provider_metadata_url: MetadataUrl | MISSING = MISSING,
        oidc_remote_user_claim: RemoteUserClaim | MISSING = MISSING,
        oidc_require_claim: Claim | MISSING = MISSING,
        auth_entity: UpdateAuthEntityRequest | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_base_config_entity(
        self,
        request: UpdateBaseConfigEntityRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update the base configuration, optionally with the client authentication settings.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_base_config_entity, request, kwargs, request_options)

    async def get_outgoing_proxy(self, *, request_options: RequestOptions | None = None) -> Proxy:
        """Get the outgoing proxy setting. Access: admin."""
        return await self._run(OPS.get_outgoing_proxy, None, {}, request_options)

    async def set_outgoing_proxy(
        self, *, oidc_outgoing_proxy: Proxy, request_options: RequestOptions | None = None
    ) -> None:
        """Set the outgoing proxy setting. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_outgoing_proxy, None, {"oidc_outgoing_proxy": oidc_outgoing_proxy}, request_options)

    async def get_provider_metadata_url(self, *, request_options: RequestOptions | None = None) -> MetadataUrl:
        """Get the provider metadata url setting. Access: admin."""
        return await self._run(OPS.get_provider_metadata_url, None, {}, request_options)

    async def set_provider_metadata_url(
        self, *, oidc_provider_metadata_url: MetadataUrl, request_options: RequestOptions | None = None
    ) -> None:
        """Set the provider metadata url setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_provider_metadata_url,
            None,
            {"oidc_provider_metadata_url": oidc_provider_metadata_url},
            request_options,
        )

    async def get_remote_user_claim(self, *, request_options: RequestOptions | None = None) -> RemoteUserClaim:
        """Get the remote user claim setting. Access: admin."""
        return await self._run(OPS.get_remote_user_claim, None, {}, request_options)

    async def set_remote_user_claim(
        self, *, oidc_remote_user_claim: RemoteUserClaim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the remote user claim setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_remote_user_claim, None, {"oidc_remote_user_claim": oidc_remote_user_claim}, request_options
        )

    async def get_require_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the require claim setting. Access: admin."""
        return await self._run(OPS.get_require_claim, None, {}, request_options)

    async def set_require_claim(
        self, *, oidc_require_claim: Claim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the require claim setting. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_require_claim, None, {"oidc_require_claim": oidc_require_claim}, request_options)

    async def get_auth_entity(self, *, request_options: RequestOptions | None = None) -> AuthEntity:
        """Get the client authentication settings. The client secret is never returned.

        Access: admin.
        """
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
        oidc_authz_admin_claim: Claim | MISSING = MISSING,
        oidc_authz_operator_claim: Claim | MISSING = MISSING,
        oidc_authz_scopes: ScopeList | MISSING = MISSING,
        oidc_authz_viewer_claim: Claim | MISSING = MISSING,
        oidc_client_id: ClientId | MISSING = MISSING,
        oidc_client_secret: ClientSecret | MISSING = MISSING,
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
        """Update the client authentication settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_auth_entity, request, kwargs, request_options)

    async def get_authz_admin_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the authz admin claim setting. Access: admin."""
        return await self._run(OPS.get_authz_admin_claim, None, {}, request_options)

    async def set_authz_admin_claim(
        self, *, oidc_authz_admin_claim: Claim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz admin claim setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_authz_admin_claim, None, {"oidc_authz_admin_claim": oidc_authz_admin_claim}, request_options
        )

    async def get_authz_operator_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the authz operator claim setting. Access: admin."""
        return await self._run(OPS.get_authz_operator_claim, None, {}, request_options)

    async def set_authz_operator_claim(
        self, *, oidc_authz_operator_claim: Claim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz operator claim setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_authz_operator_claim,
            None,
            {"oidc_authz_operator_claim": oidc_authz_operator_claim},
            request_options,
        )

    async def get_authz_scopes(self, *, request_options: RequestOptions | None = None) -> ScopeList:
        """Get the authz scopes setting. Access: admin."""
        return await self._run(OPS.get_authz_scopes, None, {}, request_options)

    async def set_authz_scopes(
        self, *, oidc_authz_scopes: ScopeList, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz scopes setting. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_authz_scopes, None, {"oidc_authz_scopes": oidc_authz_scopes}, request_options)

    async def get_authz_viewer_claim(self, *, request_options: RequestOptions | None = None) -> Claim:
        """Get the authz viewer claim setting. Access: admin."""
        return await self._run(OPS.get_authz_viewer_claim, None, {}, request_options)

    async def set_authz_viewer_claim(
        self, *, oidc_authz_viewer_claim: Claim, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authz viewer claim setting. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_authz_viewer_claim, None, {"oidc_authz_viewer_claim": oidc_authz_viewer_claim}, request_options
        )

    async def get_client_id(self, *, request_options: RequestOptions | None = None) -> ClientId:
        """Get the client id setting. Access: admin."""
        return await self._run(OPS.get_client_id, None, {}, request_options)

    async def set_client_id(self, *, oidc_client_id: ClientId, request_options: RequestOptions | None = None) -> None:
        """Set the client id setting. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_client_id, None, {"oidc_client_id": oidc_client_id}, request_options)

    async def set_client_secret(
        self, *, oidc_client_secret: ClientSecret, request_options: RequestOptions | None = None
    ) -> None:
        """Set the client secret setting. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_client_secret, None, {"oidc_client_secret": oidc_client_secret}, request_options)
