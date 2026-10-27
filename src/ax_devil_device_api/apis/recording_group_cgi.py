# GENERATED from specs/apis/network-video/recording-group.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Create, update, delete and list recording groups (continuous recording sets with shared storage, retention time and stream options) through the classic XML CGIs.

Docs: https://developer.axis.com/vapix/network-video/recording-group/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class RecordingGroup(Model):
    """One recording group (the attributes of a RecordingGroup element)."""

    recording_group_id: str = Field(validation_alias="RecordingGroupId", serialization_alias="RecordingGroupId")
    """The name of the recording group."""
    nice_name: str | None = Field(default=None, validation_alias="NiceName", serialization_alias="NiceName")
    """The user friendly name of the recording group."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """A description of the recording group."""
    retention_time: int | None = Field(
        default=None, validation_alias="RetentionTime", serialization_alias="RetentionTime"
    )
    """Maximum number of hours a recording is saved. Zero means indefinite."""
    disk_id: str | None = Field(default=None, validation_alias="DiskId", serialization_alias="DiskId")
    """The storage used for recordings in the group."""
    stream_options: str | None = Field(
        default=None, validation_alias="StreamOptions", serialization_alias="StreamOptions"
    )
    """The stream options used for the group."""
    pre_duration: int | None = Field(default=None, validation_alias="PreDuration", serialization_alias="PreDuration")
    """Pre-trigger time in milliseconds."""
    post_duration: int | None = Field(default=None, validation_alias="PostDuration", serialization_alias="PostDuration")
    """Post-trigger time in milliseconds."""


class RecordingGroups(Model):
    recording_group: list[RecordingGroup] | None = Field(
        default=None, validation_alias="RecordingGroup", serialization_alias="RecordingGroup"
    )


class CreatedRecordingGroup(Model):
    recording_group_id: str = Field(validation_alias="RecordingGroupId", serialization_alias="RecordingGroupId")
    """The name of the created recording group."""


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """The schema version in the form major.minor, e.g. 1.0."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class CreateRecordingGroupRequest(Model):
    schemaversion: int
    """Specifies the major XML schema that should be used."""
    recordinggroupid: str | None = Field(default=None, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    """Id of the recording group. Generated if not provided. Valid characters a-z, A-Z, 0-9, _, -; max 50 characters."""
    description: str | None = None
    """Description of the recording group."""
    nicename: str | None = None
    """A user friendly name of the recording group."""
    retentiontime: int | None = Field(default=None, ge=0)
    """Maximum number of hours that recordings in this group are stored. 0 means unlimited."""
    diskid: str | None = None
    """The name of the storage that should be used. Cannot be changed after creation."""
    streamoptions: str | None = None
    """The stream options used when recording in the group, e.g. resolution=1920x1080&device=AABBCCDDEE."""
    preduration: int | None = None
    """Pre-trigger time in milliseconds: the time included from immediately before a recording is started."""
    postduration: int | None = None
    """Post-trigger time in milliseconds: the time included from immediately after a recording is stopped."""


class UpdateRecordingGroupRequest(Model):
    schemaversion: int
    """Specifies the major XML schema that should be used."""
    recordinggroupid: str
    """The recording group ID that should be updated."""
    description: str | None = None
    """Description of the recording group."""
    nicename: str | None = None
    """A user friendly name of the recording group."""
    retentiontime: int | None = Field(default=None, ge=0)
    """Maximum number of hours that recordings in this group are stored. 0 means unlimited. Affects all existing and future recordings of the group."""
    streamoptions: str | None = None
    """The stream options used when recording in the group."""
    preduration: int | None = None
    """Pre-trigger time in milliseconds."""
    postduration: int | None = None
    """Post-trigger time in milliseconds."""


class DeleteRecordingGroupRequest(Model):
    schemaversion: int
    """Specifies the major XML schema that should be used."""
    recordinggroupid: str
    """The recording group ID that should be deleted."""


class ListRecordingGroupsRequest(Model):
    schemaversion: int
    """Specifies the major XML schema that should be used."""
    recordinggroupid: str | None = None
    """The recording group ID that should be listed. All available groups are listed unless specified."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/record/recording_group/schemaversions.cgi"

INFO = ApiInfo(
    id="recording-group",
    name="Recording group (CGI)",
    family=Family.CGI,
    discovery=(ApiDiscovery("recording-group"),),
    docs=("https://developer.axis.com/vapix/network-video/recording-group/",),
    errors={
        10: ErrorCode("An error occurred while processing the request."),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version not supported.", "unsupported"),
        110: ErrorCode("Recording group not found.", "not_found"),
        120: ErrorCode("Max number of recording groups reached.", "unavailable"),
        130: ErrorCode("Invalid stream options.", "invalid_argument"),
        140: ErrorCode("Recording group in use.", "unavailable"),
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
        access="viewer",
        effect="read",
    )
    create_recording_group = Operation(
        INFO,
        "create_recording_group",
        CgiBinding(
            "/axis-cgi/record/recording_group/create.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("recordinggroupid"),
                CgiArg("description"),
                CgiArg("nicename"),
                CgiArg("retentiontime"),
                CgiArg("diskid"),
                CgiArg("streamoptions"),
                CgiArg("preduration"),
                CgiArg("postduration"),
            ),
            reply=Xml(map=XmlMap(fields=(XmlField("RecordingGroupId"),), root="CreateSuccess")),
        ),
        params=CreateRecordingGroupRequest,
        result=CreatedRecordingGroup,
        access="operator",
        effect="write",
        write="create",
    )
    update_recording_group = Operation(
        INFO,
        "update_recording_group",
        CgiBinding(
            "/axis-cgi/record/recording_group/update.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("recordinggroupid"),
                CgiArg("description"),
                CgiArg("nicename"),
                CgiArg("retentiontime"),
                CgiArg("streamoptions"),
                CgiArg("preduration"),
                CgiArg("postduration"),
            ),
            reply=Xml(),
        ),
        params=UpdateRecordingGroupRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    delete_recording_group = Operation(
        INFO,
        "delete_recording_group",
        CgiBinding(
            "/axis-cgi/record/recording_group/delete.cgi",
            args=(CgiArg("schemaversion"), CgiArg("recordinggroupid")),
            reply=Xml(),
        ),
        params=DeleteRecordingGroupRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    list_recording_groups = Operation(
        INFO,
        "list_recording_groups",
        CgiBinding(
            "/axis-cgi/record/recording_group/list.cgi",
            args=(CgiArg("schemaversion"), CgiArg("recordinggroupid")),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "RecordingGroup",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("RecordingGroupId"),
                                    XmlField("NiceName"),
                                    XmlField("Description"),
                                    XmlField("RetentionTime"),
                                    XmlField("DiskId"),
                                    XmlField("StreamOptions"),
                                    XmlField("PreDuration"),
                                    XmlField("PostDuration"),
                                )
                            ),
                        ),
                    ),
                    root="ListSuccess",
                )
            ),
        ),
        params=ListRecordingGroupsRequest,
        result=RecordingGroups,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RecordingGroupCgiApi(SyncApi):
    """Recording group (CGI) (``recording-group``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve a list of supported schema versions and whether they are deprecated.

        Access: viewer.
        """
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    @overload
    def create_recording_group(
        self, request: CreateRecordingGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> CreatedRecordingGroup: ...
    @overload
    def create_recording_group(
        self,
        /,
        *,
        schemaversion: int,
        recordinggroupid: str | MISSING = MISSING,
        description: str | MISSING = MISSING,
        nicename: str | MISSING = MISSING,
        retentiontime: int | MISSING = MISSING,
        diskid: str | MISSING = MISSING,
        streamoptions: str | MISSING = MISSING,
        preduration: int | MISSING = MISSING,
        postduration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> CreatedRecordingGroup: ...
    def create_recording_group(
        self,
        request: CreateRecordingGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> CreatedRecordingGroup:
        """Create a new recording group.

        An error is returned when the maximum number of recording groups is reached.

        Access: operator.
        """
        return self._run(OPS.create_recording_group, request, kwargs, request_options)

    @overload
    def update_recording_group(
        self, request: UpdateRecordingGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_recording_group(
        self,
        /,
        *,
        schemaversion: int,
        recordinggroupid: str,
        description: str | MISSING = MISSING,
        nicename: str | MISSING = MISSING,
        retentiontime: int | MISSING = MISSING,
        streamoptions: str | MISSING = MISSING,
        preduration: int | MISSING = MISSING,
        postduration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_recording_group(
        self,
        request: UpdateRecordingGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a recording group.

        Only the given fields change. Updating the stream options during an ongoing recording restarts the
        recording group.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.update_recording_group, request, kwargs, request_options)

    def delete_recording_group(
        self, *, schemaversion: int, recordinggroupid: str, request_options: RequestOptions | None = None
    ) -> None:
        """Delete a recording group and all of its recordings (only if no recording actions are configured to it).

        Access: operator.
        """
        self._run(
            OPS.delete_recording_group,
            None,
            {"schemaversion": schemaversion, "recordinggroupid": recordinggroupid},
            request_options,
        )

    def list_recording_groups(
        self,
        *,
        schemaversion: int,
        recordinggroupid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordingGroups:
        """Retrieve list information for one or all recording groups. Access: viewer."""
        return self._run(
            OPS.list_recording_groups,
            None,
            {"schemaversion": schemaversion, "recordinggroupid": recordinggroupid},
            request_options,
        )


class AsyncRecordingGroupCgiApi(AsyncApi):
    """Recording group (CGI) (``recording-group``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve a list of supported schema versions and whether they are deprecated.

        Access: viewer.
        """
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    @overload
    async def create_recording_group(
        self, request: CreateRecordingGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> CreatedRecordingGroup: ...
    @overload
    async def create_recording_group(
        self,
        /,
        *,
        schemaversion: int,
        recordinggroupid: str | MISSING = MISSING,
        description: str | MISSING = MISSING,
        nicename: str | MISSING = MISSING,
        retentiontime: int | MISSING = MISSING,
        diskid: str | MISSING = MISSING,
        streamoptions: str | MISSING = MISSING,
        preduration: int | MISSING = MISSING,
        postduration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> CreatedRecordingGroup: ...
    async def create_recording_group(
        self,
        request: CreateRecordingGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> CreatedRecordingGroup:
        """Create a new recording group.

        An error is returned when the maximum number of recording groups is reached.

        Access: operator.
        """
        return await self._run(OPS.create_recording_group, request, kwargs, request_options)

    @overload
    async def update_recording_group(
        self, request: UpdateRecordingGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_recording_group(
        self,
        /,
        *,
        schemaversion: int,
        recordinggroupid: str,
        description: str | MISSING = MISSING,
        nicename: str | MISSING = MISSING,
        retentiontime: int | MISSING = MISSING,
        streamoptions: str | MISSING = MISSING,
        preduration: int | MISSING = MISSING,
        postduration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_recording_group(
        self,
        request: UpdateRecordingGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Update a recording group.

        Only the given fields change. Updating the stream options during an ongoing recording restarts the
        recording group.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.update_recording_group, request, kwargs, request_options)

    async def delete_recording_group(
        self, *, schemaversion: int, recordinggroupid: str, request_options: RequestOptions | None = None
    ) -> None:
        """Delete a recording group and all of its recordings (only if no recording actions are configured to it).

        Access: operator.
        """
        await self._run(
            OPS.delete_recording_group,
            None,
            {"schemaversion": schemaversion, "recordinggroupid": recordinggroupid},
            request_options,
        )

    async def list_recording_groups(
        self,
        *,
        schemaversion: int,
        recordinggroupid: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> RecordingGroups:
        """Retrieve list information for one or all recording groups. Access: viewer."""
        return await self._run(
            OPS.list_recording_groups,
            None,
            {"schemaversion": schemaversion, "recordinggroupid": recordinggroupid},
            request_options,
        )
