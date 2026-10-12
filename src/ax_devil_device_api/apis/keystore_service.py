# GENERATED from specs/apis/physical-access-control/keystore-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The axkey service implements a keystore.

Docs: https://developer.axis.com/vapix/physical-access-control/keystore-service/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ReferenceToken = str


class EncryptionKey(Model):
    """An encryption key as returned by the device."""

    token: ReferenceToken
    """A service-unique identifier of the encryption key."""
    key: str | None = Field(default=None, validation_alias="Key", serialization_alias="Key", max_length=1024)
    """The cryptographic key. The device never reveals it; responses show `*****`."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the key."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """Extra information about the key."""
    modification_time: str | None = Field(
        default=None, validation_alias="ModificationTime", serialization_alias="ModificationTime"
    )
    """UTC time when the key was last updated. Set by the device; cannot be set with set_encryption_key."""


class EncryptionKeyInput(Model):
    """An encryption key to add or update."""

    token: ReferenceToken
    """A service-unique identifier of the encryption key. An existing token updates that key."""
    key: str = Field(validation_alias="Key", serialization_alias="Key", max_length=1024)
    """The cryptographic key, for example a 16-byte value as 32 hex digits. The known key SCBK-D and the all-zero 16-byte value are rejected."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Name of the key."""
    description: str | None = Field(
        default=None, validation_alias="Description", serialization_alias="Description", max_length=1024
    )
    """Extra information about the key."""


class EncryptionKeyList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    encryption_key: list[EncryptionKey] | None = Field(
        default=None, validation_alias="EncryptionKey", serialization_alias="EncryptionKey"
    )
    """The keys, without key values."""


class SetEncryptionKeyRequest(Model):
    encryption_key: list[EncryptionKeyInput] = Field(
        validation_alias="EncryptionKey", serialization_alias="EncryptionKey", min_length=1
    )
    """The new versions of the encryption keys."""


class TokenList(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the added or updated keys."""


class EncryptionKeys(Model):
    encryption_key: list[EncryptionKey] | None = Field(
        default=None, validation_alias="EncryptionKey", serialization_alias="EncryptionKey"
    )


class TokensRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the encryption keys."""


class GetEncryptionKeyListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If absent, or greater than the device supports, the device decides."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this reference. If absent, start from the beginning."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/axkey"

INFO = ApiInfo(
    id="keystore-service",
    name="Keystore service",
    family=Family.SERVICE_JSON,
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/keystore-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/idpoint-service/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
    ),
)


class OPS:
    get_encryption_key_list = Operation(
        INFO,
        "get_encryption_key_list",
        ServiceJsonBinding(PATH, "axkey:GetEncryptionKeyList"),
        params=GetEncryptionKeyListRequest,
        result=EncryptionKeyList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning.", "invalid_argument"
            )
        },
    )
    set_encryption_key = Operation(
        INFO,
        "set_encryption_key",
        ServiceJsonBinding(PATH, "axkey:SetEncryptionKey"),
        params=SetEncryptionKeyRequest,
        result=TokenList,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:InvalidArgs": ErrorCode("Invalid key value", "invalid_argument")},
    )
    get_encryption_key = Operation(
        INFO,
        "get_encryption_key",
        ServiceJsonBinding(PATH, "axkey:GetEncryptionKey"),
        params=TokensRequest,
        result=EncryptionKeys,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("Encryption key not found", "not_found")},
    )
    remove_encryption_key = Operation(
        INFO,
        "remove_encryption_key",
        ServiceJsonBinding(PATH, "axkey:RemoveEncryptionKey"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("Encryption key not found", "not_found")},
    )


# ---------------------------------------------------------------------------
# API classes


class KeystoreServiceApi(SyncApi):
    """Keystore service (``keystore-service``)."""

    INFO = INFO

    def get_encryption_key_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> EncryptionKeyList:
        """List the encryption keys, without their key values.

        Pages through the keys. Pass the returned `NextStartReference` as `StartReference` in the next call
        and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return self._run(
            OPS.get_encryption_key_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    @overload
    def set_encryption_key(
        self, request: SetEncryptionKeyRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    def set_encryption_key(
        self, /, *, encryption_key: list[EncryptionKeyInput], request_options: RequestOptions | None = None
    ) -> TokenList: ...
    def set_encryption_key(
        self,
        request: SetEncryptionKeyRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Add or update encryption keys.

        Adds the keys, or updates the keys whose token already exists. The modification time is set by the
        device.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.set_encryption_key, request, kwargs, request_options)

    def get_encryption_key(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> EncryptionKeys:
        """Get one or more encryption keys, without their key values. Access: admin."""
        return self._run(OPS.get_encryption_key, None, {"token": token}, request_options)

    def remove_encryption_key(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the encryption keys with the given tokens. Access: admin."""
        self._run(OPS.remove_encryption_key, None, {"token": token}, request_options)


class AsyncKeystoreServiceApi(AsyncApi):
    """Keystore service (``keystore-service``)."""

    INFO = INFO

    async def get_encryption_key_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> EncryptionKeyList:
        """List the encryption keys, without their key values.

        Pages through the keys. Pass the returned `NextStartReference` as `StartReference` in the next call
        and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return await self._run(
            OPS.get_encryption_key_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    @overload
    async def set_encryption_key(
        self, request: SetEncryptionKeyRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    async def set_encryption_key(
        self, /, *, encryption_key: list[EncryptionKeyInput], request_options: RequestOptions | None = None
    ) -> TokenList: ...
    async def set_encryption_key(
        self,
        request: SetEncryptionKeyRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Add or update encryption keys.

        Adds the keys, or updates the keys whose token already exists. The modification time is set by the
        device.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.set_encryption_key, request, kwargs, request_options)

    async def get_encryption_key(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> EncryptionKeys:
        """Get one or more encryption keys, without their key values. Access: admin."""
        return await self._run(OPS.get_encryption_key, None, {"token": token}, request_options)

    async def remove_encryption_key(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the encryption keys with the given tokens. Access: admin."""
        await self._run(OPS.remove_encryption_key, None, {"token": token}, request_options)
