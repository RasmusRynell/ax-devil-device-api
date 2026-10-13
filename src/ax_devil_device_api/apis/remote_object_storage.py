# GENERATED from specs/apis/device-configuration/remote-object-storage-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure storage of recordings on remote object stores (Azure, S3) and the local failover storage.

Docs: https://developer.axis.com/vapix/device-configuration/remote-object-storage-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, ErrorCode, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

IdString = Annotated[str, Field(min_length=1, max_length=50, pattern="^[a-zA-Z0-9_]+$")]
DiskIdString = Annotated[str, Field(min_length=1, max_length=50, pattern="^[a-zA-Z0-9_-]+$")]
PositiveInteger = Annotated[int, Field(ge=1)]
FailoverDiskSelection = Literal["AUTO", "MANUAL"]
ClientAuthenticationMethod = Literal["private_key_jwt"]


class AuthorizationServer(Model):
    """An external authorization server that supplies the object store credentials through the OAuth 2.0 client credentials flow. With private_key_jwt a certificate set named like the destination id must be configured afterwards."""

    client_authentication_method: ClientAuthenticationMethod | None = Field(
        default=None, validation_alias="clientAuthenticationMethod", serialization_alias="clientAuthenticationMethod"
    )
    client_id: str | None = Field(default=None, validation_alias="clientId", serialization_alias="clientId")
    token_endpoint: str | None = Field(
        default=None, validation_alias="tokenEndpoint", serialization_alias="tokenEndpoint"
    )


class AzureDestination(Model):
    """Azure settings. Valid credentials are accountName with sharedKey (url may then be omitted), or a sas token. Unset fields are returned as empty strings."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"sas", "shared_key"})
    account_name: str | None = Field(default=None, validation_alias="accountName", serialization_alias="accountName")
    container: str | None = None
    sas: str | None = None
    shared_key: str | None = Field(default=None, validation_alias="sharedKey", serialization_alias="sharedKey")
    url: str | None = None


class S3Destination(Model):
    """S3 settings. sessionToken may be empty when temporary credentials are not used. An empty region means us-east-1. Unset fields are returned as empty strings."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"access_key_id", "secret_access_key", "session_token"})
    access_key_id: str | None = Field(default=None, validation_alias="accessKeyId", serialization_alias="accessKeyId")
    bucket: str | None = None
    region: str | None = None
    secret_access_key: str | None = Field(
        default=None, validation_alias="secretAccessKey", serialization_alias="secretAccessKey"
    )
    session_token: str | None = Field(default=None, validation_alias="sessionToken", serialization_alias="sessionToken")
    url: str | None = None


class FailoverConfiguration(Model):
    """Local failover storage for objects that cannot be uploaded to the remote object store. Setting the whole failover configuration to null disables failover."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"disk_id", "storage_limit", "upload_limit"})
    disk_selection: FailoverDiskSelection | None = Field(
        default=None, validation_alias="diskSelection", serialization_alias="diskSelection"
    )
    """The failover disk selection mode. Default: AUTO."""
    disk_id: DiskIdString | None = Field(default=None, validation_alias="diskId", serialization_alias="diskId")
    """The disk used for failover in MANUAL mode, where it must be set. Default: null (not configured)."""
    storage_limit: PositiveInteger | None = Field(
        default=None, validation_alias="storageLimit", serialization_alias="storageLimit"
    )
    """Maximum failover storage size in KiB. Only applies in MANUAL mode. Default: null (unlimited)."""
    upload_limit: PositiveInteger | None = Field(
        default=None, validation_alias="uploadLimit", serialization_alias="uploadLimit"
    )
    """Maximum upload bandwidth for objects stored in failover, in kbit/s. Default: null (unlimited)."""


class Destination(Model):
    """A remote object store that recordings are uploaded to. Secrets are masked in responses."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"authorization_server", "azure", "s3"})
    id: IdString
    """ID of the destination"""
    description: str
    """Description of the destination"""
    authorization_server: AuthorizationServer | None = Field(
        default=None, validation_alias="authorizationServer", serialization_alias="authorizationServer"
    )
    """Authorization server configuration"""
    azure: AzureDestination | None = None
    """Azure related settings"""
    s3: S3Destination | None = None
    """S3 related settings"""


class RemoteObjectStorage(Model):
    """The whole API tree."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"failover"})
    failover: FailoverConfiguration | None = None
    """Failover configuration. Null means failover is disabled."""
    destinations: list[Destination] = []


class AddDestinationRequest(Model):
    """Arguments of ``add_destination``. Give at most one of azure and s3."""

    id: IdString
    """ID of the destination"""
    description: str | None = None
    """Description of the destination"""
    authorization_server: AuthorizationServer | None = Field(
        default=None, validation_alias="authorizationServer", serialization_alias="authorizationServer"
    )
    """Authorization server configuration"""
    azure: AzureDestination | None = None
    """Azure related settings"""
    s3: S3Destination | None = None
    """S3 related settings"""

    @classmethod
    def from_current(cls, destination: Destination) -> AddDestinationRequest:
        """A request that rewrites ``destination`` unchanged: copy it, edit fields, send it back.

        Masked secrets (``azure.sas``, ``azure.shared_key``, ``s3.access_key_id``, ``s3.secret_access_key``,
        ``s3.session_token``) are never copied, at any depth; set a new value on the request when the device
        needs one.
        """
        data = destination.request_data()
        return cls(**data)


class SetFailoverRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"failover"})
    failover: FailoverConfiguration | None


class DestinationIdRequest(Model):
    id: IdString


class UpdateDestinationRequest(Model):
    id: IdString
    description: str | None = None
    """Description of the destination"""
    authorization_server: AuthorizationServer | None = Field(
        default=None, validation_alias="authorizationServer", serialization_alias="authorizationServer"
    )
    """Authorization server configuration"""
    azure: AzureDestination | None = None
    """Azure related settings"""
    s3: S3Destination | None = None
    """S3 related settings"""


class SetDestinationDescriptionRequest(Model):
    id: IdString
    description: str


class SetDestinationAzureRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"azure"})
    id: IdString
    azure: AzureDestination | None


class SetDestinationS3Request(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"s3"})
    id: IdString
    s3: S3Destination | None


class SetDestinationAuthorizationServerRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"authorization_server"})
    id: IdString
    authorization_server: AuthorizationServer | None = Field(
        validation_alias="authorizationServer", serialization_alias="authorizationServer"
    )


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/remote-object-storage/v1"

INFO = ApiInfo(
    id="remote-object-storage-config",
    name="Remote object storage",
    family=Family.DCA,
    discovery=(DcaDiscovery("remote-object-storage", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/remote-object-storage-api/",),
    errors={
        5: ErrorCode(
            "Validation error. Occurs for example when more than one destination type is given when adding a destination.",
            "invalid_argument",
        )
    },
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=RemoteObjectStorage, access="admin", effect="read"
    )
    get_failover = Operation(
        INFO,
        "get_failover",
        DcaBinding("GET", f"{ROOT}/failover"),
        result=FailoverConfiguration | None,
        access="admin",
        effect="read",
    )
    set_failover = Operation(
        INFO,
        "set_failover",
        DcaBinding("PATCH", f"{ROOT}/failover", body="value", body_field="failover"),
        params=SetFailoverRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_destinations = Operation(
        INFO,
        "list_destinations",
        DcaBinding("GET", f"{ROOT}/destinations"),
        result=list[Destination],
        access="operator",
        effect="read",
    )
    get_destination = Operation(
        INFO,
        "get_destination",
        DcaBinding("GET", f"{ROOT}/destinations/{{id}}"),
        params=DestinationIdRequest,
        result=Destination,
        access="operator",
        effect="read",
    )
    add_destination = Operation(
        INFO,
        "add_destination",
        DcaBinding("POST", f"{ROOT}/destinations", body="object"),
        params=AddDestinationRequest,
        access="admin",
        effect="write",
        write="create",
    )
    update_destination = Operation(
        INFO,
        "update_destination",
        DcaBinding("PATCH", f"{ROOT}/destinations/{{id}}", body="object"),
        params=UpdateDestinationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_destination = Operation(
        INFO,
        "remove_destination",
        DcaBinding("DELETE", f"{ROOT}/destinations/{{id}}"),
        params=DestinationIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_destination_description = Operation(
        INFO,
        "set_destination_description",
        DcaBinding("PATCH", f"{ROOT}/destinations/{{id}}/description", body="value", body_field="description"),
        params=SetDestinationDescriptionRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_destination_azure = Operation(
        INFO,
        "set_destination_azure",
        DcaBinding("PATCH", f"{ROOT}/destinations/{{id}}/azure", body="value", body_field="azure"),
        params=SetDestinationAzureRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_destination_s3 = Operation(
        INFO,
        "set_destination_s3",
        DcaBinding("PATCH", f"{ROOT}/destinations/{{id}}/s3", body="value", body_field="s3"),
        params=SetDestinationS3Request,
        access="admin",
        effect="write",
        write="replace",
    )
    set_destination_authorization_server = Operation(
        INFO,
        "set_destination_authorization_server",
        DcaBinding(
            "PATCH", f"{ROOT}/destinations/{{id}}/authorizationServer", body="value", body_field="authorizationServer"
        ),
        params=SetDestinationAuthorizationServerRequest,
        access="admin",
        effect="write",
        write="replace",
    )


# ---------------------------------------------------------------------------
# API classes


class RemoteObjectStorageApi(SyncApi):
    """Remote object storage (``remote-object-storage-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> RemoteObjectStorage:
        """The failover configuration and all destinations. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_failover(self, *, request_options: RequestOptions | None = None) -> FailoverConfiguration | None:
        """The failover configuration; None when failover is disabled. Access: admin."""
        return self._run(OPS.get_failover, None, {}, request_options)

    @overload
    def set_failover(
        self, request: SetFailoverRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_failover(
        self, failover: FailoverConfiguration | None, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_failover(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the failover configuration, or disable failover with None.

        Only the given fields change. Pass ``None`` to disable failover (objects that fail to upload are
        then not stored locally).

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetFailoverRequest):
            kwargs = {**dict(zip(("failover",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_failover, request, kwargs, request_options)

    def list_destinations(self, *, request_options: RequestOptions | None = None) -> list[Destination]:
        """List the destinations. Access: operator."""
        return self._run(OPS.list_destinations, None, {}, request_options)

    def get_destination(self, id: IdString, *, request_options: RequestOptions | None = None) -> Destination:
        """One destination. Access: operator."""
        return self._run(OPS.get_destination, None, {"id": id}, request_options)

    @overload
    def add_destination(
        self, request: AddDestinationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_destination(
        self,
        /,
        *,
        id: IdString,
        description: str | MISSING = MISSING,
        authorization_server: AuthorizationServer | MISSING = MISSING,
        azure: AzureDestination | MISSING = MISSING,
        s3: S3Destination | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_destination(
        self,
        request: AddDestinationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a destination. Give at most one of azure and s3. Access: admin."""
        self._run(OPS.add_destination, request, kwargs, request_options)

    @overload
    def update_destination(
        self, request: UpdateDestinationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_destination(
        self,
        /,
        *,
        id: IdString,
        description: str | MISSING = MISSING,
        authorization_server: AuthorizationServer | MISSING = MISSING,
        azure: AzureDestination | MISSING = MISSING,
        s3: S3Destination | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_destination(
        self,
        request: UpdateDestinationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update properties of a destination; only the given ones change.

        Documented by the "Update a storage destination" use case (PATCH on the destination); the API
        definition lists only per-property SET.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_destination, request, kwargs, request_options)

    def remove_destination(self, id: IdString, *, request_options: RequestOptions | None = None) -> None:
        """Remove a destination (objects held in failover for it are removed too). Access: admin."""
        self._run(OPS.remove_destination, None, {"id": id}, request_options)

    def set_destination_description(
        self, id: IdString, description: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Replace the description of a destination.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_destination_description, None, {"id": id, "description": description}, request_options)

    @overload
    def set_destination_azure(
        self, request: SetDestinationAzureRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_destination_azure(
        self, id: IdString, azure: AzureDestination | None, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_destination_azure(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the Azure settings of a destination (None removes them).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDestinationAzureRequest):
            kwargs = {**dict(zip(("id", "azure"), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_destination_azure, request, kwargs, request_options)

    @overload
    def set_destination_s3(
        self, request: SetDestinationS3Request, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_destination_s3(
        self, id: IdString, s3: S3Destination | None, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_destination_s3(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the S3 settings of a destination (None removes them).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDestinationS3Request):
            kwargs = {**dict(zip(("id", "s3"), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_destination_s3, request, kwargs, request_options)

    @overload
    def set_destination_authorization_server(
        self, request: SetDestinationAuthorizationServerRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_destination_authorization_server(
        self,
        id: IdString,
        authorization_server: AuthorizationServer | None,
        /,
        *,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_destination_authorization_server(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the authorization server of a destination (None removes it).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDestinationAuthorizationServerRequest):
            kwargs = {**dict(zip(("id", "authorization_server"), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_destination_authorization_server, request, kwargs, request_options)


class AsyncRemoteObjectStorageApi(AsyncApi):
    """Remote object storage (``remote-object-storage-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> RemoteObjectStorage:
        """The failover configuration and all destinations. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_failover(self, *, request_options: RequestOptions | None = None) -> FailoverConfiguration | None:
        """The failover configuration; None when failover is disabled. Access: admin."""
        return await self._run(OPS.get_failover, None, {}, request_options)

    @overload
    async def set_failover(
        self, request: SetFailoverRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_failover(
        self, failover: FailoverConfiguration | None, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_failover(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the failover configuration, or disable failover with None.

        Only the given fields change. Pass ``None`` to disable failover (objects that fail to upload are
        then not stored locally).

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetFailoverRequest):
            kwargs = {**dict(zip(("failover",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_failover, request, kwargs, request_options)

    async def list_destinations(self, *, request_options: RequestOptions | None = None) -> list[Destination]:
        """List the destinations. Access: operator."""
        return await self._run(OPS.list_destinations, None, {}, request_options)

    async def get_destination(self, id: IdString, *, request_options: RequestOptions | None = None) -> Destination:
        """One destination. Access: operator."""
        return await self._run(OPS.get_destination, None, {"id": id}, request_options)

    @overload
    async def add_destination(
        self, request: AddDestinationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_destination(
        self,
        /,
        *,
        id: IdString,
        description: str | MISSING = MISSING,
        authorization_server: AuthorizationServer | MISSING = MISSING,
        azure: AzureDestination | MISSING = MISSING,
        s3: S3Destination | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_destination(
        self,
        request: AddDestinationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a destination. Give at most one of azure and s3. Access: admin."""
        await self._run(OPS.add_destination, request, kwargs, request_options)

    @overload
    async def update_destination(
        self, request: UpdateDestinationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_destination(
        self,
        /,
        *,
        id: IdString,
        description: str | MISSING = MISSING,
        authorization_server: AuthorizationServer | MISSING = MISSING,
        azure: AzureDestination | MISSING = MISSING,
        s3: S3Destination | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_destination(
        self,
        request: UpdateDestinationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update properties of a destination; only the given ones change.

        Documented by the "Update a storage destination" use case (PATCH on the destination); the API
        definition lists only per-property SET.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_destination, request, kwargs, request_options)

    async def remove_destination(self, id: IdString, *, request_options: RequestOptions | None = None) -> None:
        """Remove a destination (objects held in failover for it are removed too). Access: admin."""
        await self._run(OPS.remove_destination, None, {"id": id}, request_options)

    async def set_destination_description(
        self, id: IdString, description: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Replace the description of a destination.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_destination_description, None, {"id": id, "description": description}, request_options)

    @overload
    async def set_destination_azure(
        self, request: SetDestinationAzureRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_destination_azure(
        self, id: IdString, azure: AzureDestination | None, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_destination_azure(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the Azure settings of a destination (None removes them).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDestinationAzureRequest):
            kwargs = {**dict(zip(("id", "azure"), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_destination_azure, request, kwargs, request_options)

    @overload
    async def set_destination_s3(
        self, request: SetDestinationS3Request, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_destination_s3(
        self, id: IdString, s3: S3Destination | None, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_destination_s3(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the S3 settings of a destination (None removes them).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDestinationS3Request):
            kwargs = {**dict(zip(("id", "s3"), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_destination_s3, request, kwargs, request_options)

    @overload
    async def set_destination_authorization_server(
        self, request: SetDestinationAuthorizationServerRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_destination_authorization_server(
        self,
        id: IdString,
        authorization_server: AuthorizationServer | None,
        /,
        *,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_destination_authorization_server(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the authorization server of a destination (None removes it).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDestinationAuthorizationServerRequest):
            kwargs = {**dict(zip(("id", "authorization_server"), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_destination_authorization_server, request, kwargs, request_options)
