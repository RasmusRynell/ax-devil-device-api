# GENERATED from specs/apis/network-video/recording-storage-limit.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Get and set how much disk space the product may use for recordings on each disk.

Docs: https://developer.axis.com/vapix/network-video/edge-storage-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

SchemaVersion = Annotated[int, Field(ge=1)]


class SchemaVersionInfo(Model):
    version_number: str = Field(validation_alias="versionNumber", serialization_alias="versionNumber")
    """Schema version in the form [major].[minor]."""
    deprecated: bool | None = None
    """When true the schema version is deprecated and should not be used."""


class SchemaVersions(Model):
    versions: list[SchemaVersionInfo] | None = None


class StorageLimit(Model):
    diskid: str
    """The disk ID."""
    size: int = Field(ge=0)
    """The recording storage limit in kilobytes. 0 means the limit is disabled."""
    used_space: int | None = Field(default=None, validation_alias="usedSpace", serialization_alias="usedSpace", ge=0)
    """Space already used by recording data, in kilobytes."""


class StorageLimits(Model):
    limits: list[StorageLimit] | None = None


class GetLimitRequest(Model):
    schemaversion: SchemaVersion
    diskid: str | None = None
    """The disk ID. If omitted, the limits of all disks are returned."""


class SetLimitRequest(Model):
    schemaversion: SchemaVersion
    diskid: str
    """The ID of the disk to limit."""
    size: int = Field(ge=0)
    """The limit in kilobytes. 0 disables the limit; otherwise the minimum is 1048576 kB (1 GB)."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/record/storage/schemaversions.cgi"

INFO = ApiInfo(
    id="recording-storage-limit",
    name="Recording storage limit API (Edge storage)",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.LocalStorage.StorageLimit", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/edge-storage-api/",),
    errors={
        10: ErrorCode("Error while processing the request.", "internal"),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
        110: ErrorCode("Disk not found.", "not_found"),
        120: ErrorCode("Invalid size value.", "invalid_argument"),
        130: ErrorCode("Supplied size is less than the minimum allowed limit.", "invalid_argument"),
    },
)


class OPS:
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            PATH,
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "versions",
                            source="path",
                            name="SchemaVersion",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("versionNumber", source="child", name="VersionNumber"),
                                    XmlField("deprecated", source="child", name="Deprecated"),
                                )
                            ),
                        ),
                    ),
                    root="SchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="operator",
        effect="read",
    )
    get_limit = Operation(
        INFO,
        "get_limit",
        CgiBinding(
            "/axis-cgi/record/storage/getlimit.cgi",
            args=(CgiArg("schemaversion"), CgiArg("diskid")),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "limits",
                            source="path",
                            name="StorageLimit",
                            many=True,
                            nested=XmlMap(
                                fields=(XmlField("diskid"), XmlField("size"), XmlField("usedSpace", name="usedspace"))
                            ),
                        ),
                    ),
                    root="GetStorageLimitsResponse",
                )
            ),
        ),
        params=GetLimitRequest,
        result=StorageLimits,
        access="operator",
        effect="read",
    )
    set_limit = Operation(
        INFO,
        "set_limit",
        CgiBinding(
            "/axis-cgi/record/storage/setlimit.cgi",
            args=(CgiArg("schemaversion"), CgiArg("diskid"), CgiArg("size")),
            reply=Xml(),
        ),
        params=SetLimitRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class RecordingStorageLimitApi(SyncApi):
    """Recording storage limit API (Edge storage) (``recording-storage-limit``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def get_limit(
        self,
        schemaversion: SchemaVersion,
        *,
        diskid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StorageLimits:
        """Retrieve the recording storage limit and used space per disk. Access: operator."""
        return self._run(OPS.get_limit, None, {"schemaversion": schemaversion, "diskid": diskid}, request_options)

    def set_limit(
        self, *, schemaversion: SchemaVersion, diskid: str, size: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the recording storage limit, the disk space this product may use, for a disk.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_limit, None, {"schemaversion": schemaversion, "diskid": diskid, "size": size}, request_options
        )


class AsyncRecordingStorageLimitApi(AsyncApi):
    """Recording storage limit API (Edge storage) (``recording-storage-limit``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def get_limit(
        self,
        schemaversion: SchemaVersion,
        *,
        diskid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StorageLimits:
        """Retrieve the recording storage limit and used space per disk. Access: operator."""
        return await self._run(OPS.get_limit, None, {"schemaversion": schemaversion, "diskid": diskid}, request_options)

    async def set_limit(
        self, *, schemaversion: SchemaVersion, diskid: str, size: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the recording storage limit, the disk space this product may use, for a disk.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_limit, None, {"schemaversion": schemaversion, "diskid": diskid, "size": size}, request_options
        )
