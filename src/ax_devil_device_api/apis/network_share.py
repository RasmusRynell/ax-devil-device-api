# GENERATED from specs/apis/network-video/network-share.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Add, list, modify, remove, bind, unbind and test CIFS/SMB network shares used as edge storage.

Docs: https://developer.axis.com/vapix/network-video/edge-storage-api/
"""

from __future__ import annotations

from typing import Annotated, Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models

XmlSchemaVersion = Annotated[str, Field(pattern=r"^[0-9]+(\.[0-9]+)?$")]


class NetworkShareEntry(Model):
    """One network share."""

    nice_name: str = Field(validation_alias="NiceName", serialization_alias="NiceName")
    """User-friendly name of the share."""
    share_id: str = Field(validation_alias="ShareId", serialization_alias="ShareId")
    """Share ID."""
    address: str = Field(validation_alias="Address", serialization_alias="Address")
    """Network address (IPv4 address or host name) of the storage device."""
    share: str = Field(validation_alias="Share", serialization_alias="Share")
    """Name of the share on the storage device."""
    user: str | None = Field(default=None, validation_alias="User", serialization_alias="User")
    """User name for a user on the share."""
    disk_id: str | None = Field(default=None, validation_alias="DiskId", serialization_alias="DiskId")
    """Disk ID of the disk the share is bound to. Absent when the share is unbound."""


class NetworkShareList(Model):
    number_of_shares: int = Field(validation_alias="NumberOfShares", serialization_alias="NumberOfShares", ge=0)
    """Number of network shares."""
    shares: list[NetworkShareEntry] | None = Field(
        default=None, validation_alias="NetworkShare", serialization_alias="NetworkShare"
    )


class AddedShare(Model):
    share_id: str = Field(validation_alias="ShareId", serialization_alias="ShareId")
    """Share ID of the added share."""


class BoundShare(Model):
    disk_id: str = Field(validation_alias="DiskId", serialization_alias="DiskId")
    """Disk ID of the disk the share was bound to."""


class StartedTest(Model):
    job_id: str = Field(validation_alias="JobId", serialization_alias="JobId")
    """Job ID to pass to ``get_job_progress``."""


class JobProgress(Model):
    """Progress of a test job. ``progress`` is absent when the job has finished successfully; a job that finished with errors raises an API error with the job's error code."""

    progress: int | None = Field(
        default=None, validation_alias="Progress", serialization_alias="Progress", ge=0, le=100
    )
    """Progress of the job in percent."""


class SchemaVersionInfo(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version (major.minor)."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersionInfo] = Field(
        validation_alias="SchemaVersion", serialization_alias="SchemaVersion"
    )


class ListSharesRequest(Model):
    schemaversion: XmlSchemaVersion | None = None
    shareid: str
    """``all`` or comma-separated Share IDs of the shares to list."""


class AddShareRequest(Model):
    schemaversion: XmlSchemaVersion | None = None
    nicename: str
    """User-friendly name for the share."""
    address: str
    """IPv4 address or host name of the storage device."""
    share: str
    """Name of the share on the storage device."""
    shareid: str | None = Field(default=None, pattern="^[A-Za-z0-9-]+$")
    """Unique Share ID. Assigned by the product when omitted."""
    user: str | None = None
    """User name for a user on the share."""
    password: str | None = Field(default=None, validation_alias="pass", serialization_alias="pass")
    """Password for the user."""


class RemoveShareRequest(Model):
    schemaversion: XmlSchemaVersion | None = None
    shareid: str
    """Comma-separated Share IDs of the shares to remove."""


class ModifyShareRequest(Model):
    schemaversion: XmlSchemaVersion | None = None
    shareid: str
    """Share ID of the network share to modify."""
    nicename: str | None = None
    """User-friendly name for the share."""
    address: str | None = None
    """IPv4 address or host name of the storage device."""
    share: str | None = None
    """Name of the share on the storage device."""
    user: str | None = None
    """User name for a user on the share."""
    password: str | None = Field(default=None, validation_alias="pass", serialization_alias="pass")
    """Password for the user."""


class BindShareRequest(Model):
    schemaversion: XmlSchemaVersion | None = None
    shareid: str
    """Share ID of the network share to bind."""
    automaticmount: bool | None = None
    """Mount the disk automatically after binding. The device default is yes. Default: True."""


class UnbindShareRequest(Model):
    schemaversion: XmlSchemaVersion | None = None
    shareid: str
    """Share ID of the network share to unbind."""


class TestShareRequest(Model):
    schemaversion: XmlSchemaVersion | None = None
    address: str | None = None
    """IPv4 address or host name of the storage device."""
    share: str | None = None
    """Name of the share on the storage device."""
    user: str | None = None
    """User name for a user on the share."""
    password: str | None = Field(default=None, validation_alias="pass", serialization_alias="pass")
    """Password for the user."""
    shareid: str | None = None
    """Share ID to take unspecified values from."""


class GetJobProgressRequest(Model):
    schemaversion: XmlSchemaVersion
    jobid: str
    """Job ID returned by ``test_share``."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/disks/networkshare/list.cgi"

INFO = ApiInfo(
    id="network-share",
    name="Network share API",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.NetworkShare.NetworkShare", "yes"),
        ParamDiscovery("Properties.NetworkShare.CIFS", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/edge-storage-api/",),
    errors={
        10: ErrorCode("Error while processing the request.", "internal"),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
    },
)


class OPS:
    list_shares = Operation(
        INFO,
        "list_shares",
        CgiBinding(
            PATH,
            args=(CgiArg("schemaversion"), CgiArg("shareid")),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("NumberOfShares"),
                        XmlField(
                            "NetworkShare",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("NiceName"),
                                    XmlField("ShareId"),
                                    XmlField("Address"),
                                    XmlField("Share"),
                                    XmlField("User"),
                                    XmlField("DiskId"),
                                )
                            ),
                        ),
                    ),
                    root="ListSuccess/NetworkShares",
                )
            ),
        ),
        params=ListSharesRequest,
        result=NetworkShareList,
        access="operator",
        effect="read",
    )
    add_share = Operation(
        INFO,
        "add_share",
        CgiBinding(
            "/axis-cgi/disks/networkshare/add.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("nicename"),
                CgiArg("address"),
                CgiArg("share"),
                CgiArg("shareid"),
                CgiArg("user"),
                CgiArg("password", wire="pass"),
            ),
            reply=Xml(map=XmlMap(fields=(XmlField("ShareId"),), root="AddSuccess")),
        ),
        params=AddShareRequest,
        result=AddedShare,
        access="admin",
        effect="write",
        write="create",
        errors={
            200: ErrorCode("Invalid ShareId.", "invalid_argument"),
            210: ErrorCode("The ShareId is not unique.", "invalid_argument"),
            220: ErrorCode("The NiceName is not unique.", "invalid_argument"),
            230: ErrorCode("Maximum number of network shares is already reached. No more shares can be added."),
        },
    )
    remove_share = Operation(
        INFO,
        "remove_share",
        CgiBinding(
            "/axis-cgi/disks/networkshare/remove.cgi", args=(CgiArg("schemaversion"), CgiArg("shareid")), reply=Xml()
        ),
        params=RemoveShareRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={500: ErrorCode("The network share is bound and can't be removed. Unbind it first.")},
    )
    modify_share = Operation(
        INFO,
        "modify_share",
        CgiBinding(
            "/axis-cgi/disks/networkshare/modify.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("shareid"),
                CgiArg("nicename"),
                CgiArg("address"),
                CgiArg("share"),
                CgiArg("user"),
                CgiArg("password", wire="pass"),
            ),
            reply=Xml(),
        ),
        params=ModifyShareRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            600: ErrorCode("The network share is bound and can't be modified. Unbind it first."),
            610: ErrorCode("The new ShareId is not unique.", "invalid_argument"),
            620: ErrorCode("The NiceName is not unique.", "invalid_argument"),
        },
    )
    bind_share = Operation(
        INFO,
        "bind_share",
        CgiBinding(
            "/axis-cgi/disks/networkshare/bind.cgi",
            args=(CgiArg("schemaversion"), CgiArg("shareid"), CgiArg("automaticmount", style="axis_bool")),
            reply=Xml(map=XmlMap(fields=(XmlField("DiskId"),), root="BindSuccess")),
        ),
        params=BindShareRequest,
        result=BoundShare,
        access="operator",
        effect="action",
        errors={
            300: ErrorCode("No available disk. Check if another network share is already bound."),
            310: ErrorCode("The network share is already bound to a disk."),
        },
    )
    unbind_share = Operation(
        INFO,
        "unbind_share",
        CgiBinding(
            "/axis-cgi/disks/networkshare/unbind.cgi", args=(CgiArg("schemaversion"), CgiArg("shareid")), reply=Xml()
        ),
        params=UnbindShareRequest,
        access="operator",
        effect="action",
        errors={
            400: ErrorCode(
                "The network share is mounted and can't be unbound. Unmount it with the disk management API."
            )
        },
    )
    test_share = Operation(
        INFO,
        "test_share",
        CgiBinding(
            "/axis-cgi/disks/networkshare/test.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("address"),
                CgiArg("share"),
                CgiArg("user"),
                CgiArg("password", wire="pass"),
                CgiArg("shareid"),
            ),
            reply=Xml(map=XmlMap(fields=(XmlField("JobId"),), root="TestSuccess")),
        ),
        params=TestShareRequest,
        result=StartedTest,
        access="operator",
        effect="action",
        errors={
            700: ErrorCode("No such hostname.", "not_found"),
            710: ErrorCode("Error while mounting network share."),
            720: ErrorCode("Internal error while mounting network share.", "internal"),
            730: ErrorCode("Too many tests or jobs started, wait for some to finish.", "unavailable"),
            740: ErrorCode("Problem writing to the share."),
            750: ErrorCode("Problem reading data written to the share."),
            760: ErrorCode("Problem connecting to the share."),
        },
    )
    get_job_progress = Operation(
        INFO,
        "get_job_progress",
        CgiBinding(
            "/axis-cgi/disks/networkshare/job.cgi",
            args=(CgiArg("schemaversion"), CgiArg("jobid")),
            reply=Xml(map=XmlMap(fields=(XmlField("Progress", source="child"),), root="JobSuccess")),
        ),
        params=GetJobProgressRequest,
        result=JobProgress,
        access="operator",
        effect="read",
        errors={
            700: ErrorCode("No such hostname.", "not_found"),
            710: ErrorCode("Error while mounting network share."),
            720: ErrorCode("Internal error while mounting network share.", "internal"),
            730: ErrorCode("Too many tests or jobs started, wait for some to finish.", "unavailable"),
            740: ErrorCode("Problem writing to the share."),
            750: ErrorCode("Problem reading data written to the share."),
            760: ErrorCode("Problem connecting to the share."),
        },
    )
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            "/axis-cgi/disks/networkshare/schemaversions.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "SchemaVersion",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("VersionNumber", source="child"),
                                    XmlField("Deprecated", source="child"),
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


# ---------------------------------------------------------------------------
# API classes


class NetworkShareApi(SyncApi):
    """Network share API (``network-share``)."""

    INFO = INFO

    def list_shares(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> NetworkShareList:
        """List network shares and their parameters. Access: operator."""
        return self._run(OPS.list_shares, None, {"schemaversion": schemaversion, "shareid": shareid}, request_options)

    @overload
    def add_share(
        self, request: AddShareRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddedShare: ...
    @overload
    def add_share(
        self,
        /,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        nicename: str,
        address: str,
        share: str,
        shareid: str | MISSING = MISSING,
        user: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedShare: ...
    def add_share(
        self, request: AddShareRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AddedShare:
        """Add a network share (NAS or other CIFS/SMB server). Access: admin."""
        return self._run(OPS.add_share, request, kwargs, request_options)

    def remove_share(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Remove network shares. They must be unbound first. Access: admin."""
        self._run(OPS.remove_share, None, {"schemaversion": schemaversion, "shareid": shareid}, request_options)

    @overload
    def modify_share(
        self, request: ModifyShareRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def modify_share(
        self,
        shareid: str,
        /,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        nicename: str | MISSING = MISSING,
        address: str | MISSING = MISSING,
        share: str | MISSING = MISSING,
        user: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def modify_share(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Modify a network share.

        ``nicename`` can always be changed. To change the other parameters the share must be unbound first.
        Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ModifyShareRequest):
            kwargs = bind_positional(OPS.modify_share, ("shareid",), (request, *args), kwargs)
            request = None
        self._run(OPS.modify_share, request, kwargs, request_options)

    def bind_share(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        automaticmount: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> BoundShare:
        """Bind a network share to a disk and return the Disk ID.

        The Disk ID is used with the disk management and recording APIs.

        Access: operator.
        """
        return self._run(
            OPS.bind_share,
            None,
            {"schemaversion": schemaversion, "shareid": shareid, "automaticmount": automaticmount},
            request_options,
        )

    def unbind_share(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Unbind a network share so it can be modified or removed. Access: operator."""
        self._run(OPS.unbind_share, None, {"schemaversion": schemaversion, "shareid": shareid}, request_options)

    @overload
    def test_share(
        self, request: TestShareRequest, /, *, request_options: RequestOptions | None = None
    ) -> StartedTest: ...
    @overload
    def test_share(
        self,
        /,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        address: str | MISSING = MISSING,
        share: str | MISSING = MISSING,
        user: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        shareid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartedTest: ...
    def test_share(
        self,
        request: TestShareRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> StartedTest:
        """Start a job that tests whether a network share can be used as storage.

        The given parameters are only used for the test and are not stored. ``shareid`` can replace some or
        all of address, share, user and password; arguments given together with it override the stored
        values. Poll the returned job with ``get_job_progress``.

        Access: operator.
        """
        return self._run(OPS.test_share, request, kwargs, request_options)

    def get_job_progress(
        self, schemaversion: XmlSchemaVersion, jobid: str, *, request_options: RequestOptions | None = None
    ) -> JobProgress:
        """Check the progress of a network share test job.

        Typically polled until the job is done.

        Access: operator.
        """
        return self._run(OPS.get_job_progress, None, {"schemaversion": schemaversion, "jobid": jobid}, request_options)

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the supported XML schema versions and whether they are deprecated. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)


class AsyncNetworkShareApi(AsyncApi):
    """Network share API (``network-share``)."""

    INFO = INFO

    async def list_shares(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> NetworkShareList:
        """List network shares and their parameters. Access: operator."""
        return await self._run(
            OPS.list_shares, None, {"schemaversion": schemaversion, "shareid": shareid}, request_options
        )

    @overload
    async def add_share(
        self, request: AddShareRequest, /, *, request_options: RequestOptions | None = None
    ) -> AddedShare: ...
    @overload
    async def add_share(
        self,
        /,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        nicename: str,
        address: str,
        share: str,
        shareid: str | MISSING = MISSING,
        user: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedShare: ...
    async def add_share(
        self, request: AddShareRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AddedShare:
        """Add a network share (NAS or other CIFS/SMB server). Access: admin."""
        return await self._run(OPS.add_share, request, kwargs, request_options)

    async def remove_share(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Remove network shares. They must be unbound first. Access: admin."""
        await self._run(OPS.remove_share, None, {"schemaversion": schemaversion, "shareid": shareid}, request_options)

    @overload
    async def modify_share(
        self, request: ModifyShareRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def modify_share(
        self,
        shareid: str,
        /,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        nicename: str | MISSING = MISSING,
        address: str | MISSING = MISSING,
        share: str | MISSING = MISSING,
        user: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def modify_share(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Modify a network share.

        ``nicename`` can always be changed. To change the other parameters the share must be unbound first.
        Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ModifyShareRequest):
            kwargs = bind_positional(OPS.modify_share, ("shareid",), (request, *args), kwargs)
            request = None
        await self._run(OPS.modify_share, request, kwargs, request_options)

    async def bind_share(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        automaticmount: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> BoundShare:
        """Bind a network share to a disk and return the Disk ID.

        The Disk ID is used with the disk management and recording APIs.

        Access: operator.
        """
        return await self._run(
            OPS.bind_share,
            None,
            {"schemaversion": schemaversion, "shareid": shareid, "automaticmount": automaticmount},
            request_options,
        )

    async def unbind_share(
        self,
        shareid: str,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Unbind a network share so it can be modified or removed. Access: operator."""
        await self._run(OPS.unbind_share, None, {"schemaversion": schemaversion, "shareid": shareid}, request_options)

    @overload
    async def test_share(
        self, request: TestShareRequest, /, *, request_options: RequestOptions | None = None
    ) -> StartedTest: ...
    @overload
    async def test_share(
        self,
        /,
        *,
        schemaversion: XmlSchemaVersion | MISSING = MISSING,
        address: str | MISSING = MISSING,
        share: str | MISSING = MISSING,
        user: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        shareid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartedTest: ...
    async def test_share(
        self,
        request: TestShareRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> StartedTest:
        """Start a job that tests whether a network share can be used as storage.

        The given parameters are only used for the test and are not stored. ``shareid`` can replace some or
        all of address, share, user and password; arguments given together with it override the stored
        values. Poll the returned job with ``get_job_progress``.

        Access: operator.
        """
        return await self._run(OPS.test_share, request, kwargs, request_options)

    async def get_job_progress(
        self, schemaversion: XmlSchemaVersion, jobid: str, *, request_options: RequestOptions | None = None
    ) -> JobProgress:
        """Check the progress of a network share test job.

        Typically polled until the job is done.

        Access: operator.
        """
        return await self._run(
            OPS.get_job_progress, None, {"schemaversion": schemaversion, "jobid": jobid}, request_options
        )

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the supported XML schema versions and whether they are deprecated. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)
