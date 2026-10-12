# GENERATED from specs/apis/device-configuration/recording-group-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Create, update, delete and retrieve recording groups, which hold the configuration for recordings stored on remote object storage.

Docs: https://developer.axis.com/vapix/device-configuration/recording-group/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ContainerFormat = Literal["matroska", "mp4", "cmaf", "none", "tar"]
HexadecimalEncryptionKey128Bit = Annotated[str, Field(pattern=r"^([a-fA-F0-9]{32}|\*\*\*)$")]
Uuid = Annotated[
    str,
    Field(
        min_length=36,
        max_length=36,
        pattern="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    ),
]


class ContentEncryption(Model):
    """Fixed-key encryption: only the given key is used to encrypt recordings."""

    key: HexadecimalEncryptionKey128Bit | None = None
    key_id: Uuid | None = Field(default=None, validation_alias="keyId", serialization_alias="keyId")


PositiveInteger = Annotated[int, Field(ge=0)]


class TargetAndMax(Model):
    """A type for holding a target and max positive integer values."""

    max: PositiveInteger | None = None
    target: PositiveInteger | None = None


IdString = Annotated[str, Field(min_length=1, max_length=50, pattern="^[a-zA-Z0-9_-]+$")]


class DataProducerOptions(Model):
    """Contains the data options to use for recording. The possible producers and their configuration can be retrieved from the Recording Data Producer Registry."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"data_duration", "data_size", "producer_configuration"})
    data_duration: TargetAndMax | None = Field(
        default=None, validation_alias="dataDuration", serialization_alias="dataDuration"
    )
    """The target and max duration in seconds of data items stored in the archive. Only applicable when `containerFormat` is `tar`."""
    data_size: TargetAndMax | None = Field(default=None, validation_alias="dataSize", serialization_alias="dataSize")
    """The target and max size in bytes of data items stored in the archive. Only applicable when `containerFormat` is `tar`."""
    producer_configuration: Any | None = Field(
        default=None, validation_alias="producerConfiguration", serialization_alias="producerConfiguration"
    )
    """The producer specific configuration (free-form JSON)."""
    producer_id: IdString = Field(validation_alias="producerId", serialization_alias="producerId")
    """The id of the recording data producer to use."""


class RemoteObjectStorage(Model):
    """Describes a remote object storage such as an Azure or Amazon S3 cloud server."""

    id: IdString | None = None
    postfix: str | None = None
    prefix: str | None = None


class Destination(Model):
    """The destination to save recordings to."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"remote_object_storage"})
    remote_object_storage: RemoteObjectStorage | None = Field(
        default=None, validation_alias="remoteObjectStorage", serialization_alias="remoteObjectStorage"
    )


DestinationsArray = Annotated[list[Destination], Field(min_length=1, max_length=1)]
StringArray = list[str]


class PublicKey(Model):
    """Type for storing a public key and its id."""

    key: str | None = None
    key_id: Uuid | None = Field(default=None, validation_alias="keyId", serialization_alias="keyId")


PublicKeysArray = list[PublicKey]


class KeyEncryption(Model):
    """Rotating-key encryption: generated keys are encrypted for the given certificates and public keys (RSA only)."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"certificate_ids", "public_keys"})
    certificate_ids: StringArray | None = Field(
        default=None, validation_alias="certificateIds", serialization_alias="certificateIds"
    )
    key_rotation_duration: PositiveInteger | None = Field(
        default=None, validation_alias="keyRotationDuration", serialization_alias="keyRotationDuration"
    )
    public_keys: PublicKeysArray | None = Field(
        default=None, validation_alias="publicKeys", serialization_alias="publicKeys"
    )


ProtectionSchemeEnum = Literal["CENC"]


class Encryption(Model):
    """Encryption method and parameters. Set exactly one of contentEncryption (fixed key) or keyEncryption (rotating key); omit encryption entirely for no encryption. Only cmaf recordings can be encrypted."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"content_encryption", "key_encryption"})
    content_encryption: ContentEncryption | None = Field(
        default=None, validation_alias="contentEncryption", serialization_alias="contentEncryption"
    )
    key_encryption: KeyEncryption | None = Field(
        default=None, validation_alias="keyEncryption", serialization_alias="keyEncryption"
    )
    protection_scheme: ProtectionSchemeEnum | None = Field(
        default=None, validation_alias="protectionScheme", serialization_alias="protectionScheme"
    )


ObjectAttributeKeyString = Annotated[str, Field(min_length=1, max_length=200, pattern="^[a-zA-Z][a-zA-Z0-9_]*$")]
ObjectAttributeValueString = Annotated[str, Field(min_length=0, max_length=200, pattern=r"^[^\x00-\x1F\x7F]*$")]


class ObjectAttribute(Model):
    """A key-value pair."""

    key: ObjectAttributeKeyString
    """The key string."""
    value: ObjectAttributeValueString
    """The value string."""


ObjectAttributes = Annotated[list[ObjectAttribute], Field(max_length=3)]


class RecordingGroup(Model):
    """A recording group: configuration for the recordings that belong to it."""

    __nullable__: ClassVar[frozenset[str]] = frozenset(
        {
            "container_format",
            "data_producer_options",
            "description",
            "encryption",
            "max_retention_time",
            "nice_name",
            "object_attributes",
            "post_duration",
            "pre_duration",
            "segment_duration",
            "segment_size",
            "span_duration",
            "stream_options",
        }
    )
    id: IdString
    """ID for the recording group."""
    destinations: DestinationsArray
    """Remote object storage destinations array. The recordings in this group will be stored on all destinations in this field if possible."""
    container_format: ContainerFormat | None = Field(
        default=None, validation_alias="containerFormat", serialization_alias="containerFormat"
    )
    """The output format of the recordings. Default: matroska."""
    data_producer_options: DataProducerOptions | None = Field(
        default=None, validation_alias="dataProducerOptions", serialization_alias="dataProducerOptions"
    )
    """Options for recording data from the specified producer. This option cannot be used together with streamOptions, only one of them can be set."""
    description: str | None = None
    """Description for the recording group."""
    encryption: Encryption | None = None
    """The encryption options to use for encrypting recording segments. Default: no encryption."""
    max_retention_time: PositiveInteger | None = Field(
        default=None, validation_alias="maxRetentionTime", serialization_alias="maxRetentionTime"
    )
    """Max number of hours the recordings in the group will be stored for. Default: 0 (unlimited)."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """User friendly name for the recording group."""
    object_attributes: ObjectAttributes | None = Field(
        default=None, validation_alias="objectAttributes", serialization_alias="objectAttributes"
    )
    """Optional, fixed, extra attributes to set on stored objects."""
    post_duration: PositiveInteger | None = Field(
        default=None, validation_alias="postDuration", serialization_alias="postDuration"
    )
    """Post-trigger time in milliseconds. Default: 0."""
    pre_duration: PositiveInteger | None = Field(
        default=None, validation_alias="preDuration", serialization_alias="preDuration"
    )
    """Pre-trigger time in milliseconds. Default: 0."""
    segment_duration: TargetAndMax | None = Field(
        default=None, validation_alias="segmentDuration", serialization_alias="segmentDuration"
    )
    """The segment (recording files) duration in seconds. Target value may not be reached depending on segmentSize. Default: target/max = 15/30."""
    segment_size: TargetAndMax | None = Field(
        default=None, validation_alias="segmentSize", serialization_alias="segmentSize"
    )
    """The target/max segment size in bytes. Target value may not be reached depending on segmentDuration. Default: target/max = 15728640/26214400 (15MiB/25MiB)."""
    span_duration: PositiveInteger | None = Field(
        default=None, validation_alias="spanDuration", serialization_alias="spanDuration"
    )
    """The span duration in seconds. A recording is logically made up of one or more spans. Default: 3600."""
    stream_options: str | None = Field(
        default=None, validation_alias="streamOptions", serialization_alias="streamOptions"
    )
    """The stream options to use for recordings in the group. This option can't be used together with `dataProducerOptions`, only one of them can be set."""


class RecordingGroupTree(Model):
    """The whole API tree."""

    recording_groups: list[RecordingGroup] = Field(
        default=[], validation_alias="recordingGroups", serialization_alias="recordingGroups"
    )


class AddRecordingGroupRequest(Model):
    """Arguments of ``add_recording_group``."""

    destinations: DestinationsArray
    """Remote object storage destinations array. The recordings in this group will be stored on all destinations in this field if possible."""
    id: IdString | None = None
    """ID for the recording group."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    """User friendly name for the recording group."""
    description: str | None = None
    """Description for the recording group."""
    max_retention_time: PositiveInteger | None = Field(
        default=None, validation_alias="maxRetentionTime", serialization_alias="maxRetentionTime"
    )
    """Max number of hours the recordings in the group will be stored for. Default: 0 (unlimited)."""
    container_format: ContainerFormat | None = Field(
        default=None, validation_alias="containerFormat", serialization_alias="containerFormat"
    )
    """The output format of the recordings. Default: matroska."""
    span_duration: PositiveInteger | None = Field(
        default=None, validation_alias="spanDuration", serialization_alias="spanDuration"
    )
    """The span duration in seconds. A recording is logically made up of one or more spans. Default: 3600."""
    segment_duration: TargetAndMax | None = Field(
        default=None, validation_alias="segmentDuration", serialization_alias="segmentDuration"
    )
    """The segment (recording files) duration in seconds. Target value may not be reached depending on segmentSize. Default: target/max = 15/30."""
    segment_size: TargetAndMax | None = Field(
        default=None, validation_alias="segmentSize", serialization_alias="segmentSize"
    )
    """The target/max segment size in bytes. Target value may not be reached depending on segmentDuration. Default: target/max = 15728640/26214400 (15MiB/25MiB)."""
    pre_duration: PositiveInteger | None = Field(
        default=None, validation_alias="preDuration", serialization_alias="preDuration"
    )
    """Pre-trigger time in milliseconds. Default: 0."""
    post_duration: PositiveInteger | None = Field(
        default=None, validation_alias="postDuration", serialization_alias="postDuration"
    )
    """Post-trigger time in milliseconds. Default: 0."""
    stream_options: str | None = Field(
        default=None, validation_alias="streamOptions", serialization_alias="streamOptions"
    )
    """The stream options to use for recordings in the group. This option can't be used together with `dataProducerOptions`, only one of them can be set."""
    encryption: Encryption | None = None
    """The encryption options to use for encrypting recording segments. Default: no encryption."""
    data_producer_options: DataProducerOptions | None = Field(
        default=None, validation_alias="dataProducerOptions", serialization_alias="dataProducerOptions"
    )
    """Options for recording data from the specified producer. This option cannot be used together with streamOptions, only one of them can be set."""
    object_attributes: ObjectAttributes | None = Field(
        default=None, validation_alias="objectAttributes", serialization_alias="objectAttributes"
    )
    """Optional, fixed, extra attributes to set on stored objects."""

    @classmethod
    def from_current(cls, group: RecordingGroup) -> AddRecordingGroupRequest:
        """A request that rewrites ``group`` unchanged: copy it, edit fields, send it back."""
        data = group.request_data()
        return cls(**data)


class RecordingGroupIdRequest(Model):
    id: IdString


class SetRecordingGroupDataProducerOptionsRequest(Model):
    data_producer_options: DataProducerOptions = Field(
        validation_alias="dataProducerOptions", serialization_alias="dataProducerOptions"
    )
    id: IdString


class SetRecordingGroupObjectAttributesRequest(Model):
    object_attributes: ObjectAttributes = Field(
        validation_alias="objectAttributes", serialization_alias="objectAttributes"
    )
    id: IdString


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/recording-group/v2"

INFO = ApiInfo(
    id="recording-group-config",
    name="Recording group API",
    family=Family.DCA,
    discovery=(DcaDiscovery("recording-group", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/recording-group/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=RecordingGroupTree, access="admin", effect="read"
    )
    list_recording_groups = Operation(
        INFO,
        "list_recording_groups",
        DcaBinding("GET", f"{ROOT}/recordingGroups"),
        result=list[RecordingGroup],
        access="admin",
        effect="read",
    )
    get_recording_group = Operation(
        INFO,
        "get_recording_group",
        DcaBinding("GET", f"{ROOT}/recordingGroups/{{id}}"),
        params=RecordingGroupIdRequest,
        result=RecordingGroup,
        access="admin",
        effect="read",
    )
    add_recording_group = Operation(
        INFO,
        "add_recording_group",
        DcaBinding("POST", f"{ROOT}/recordingGroups", body="object"),
        params=AddRecordingGroupRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_recording_group = Operation(
        INFO,
        "remove_recording_group",
        DcaBinding("DELETE", f"{ROOT}/recordingGroups/{{id}}"),
        params=RecordingGroupIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_recording_group_data_producer_options = Operation(
        INFO,
        "set_recording_group_data_producer_options",
        DcaBinding(
            "PATCH",
            f"{ROOT}/recordingGroups/{{id}}/dataProducerOptions",
            body="value",
            body_field="dataProducerOptions",
        ),
        params=SetRecordingGroupDataProducerOptionsRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_recording_group_object_attributes = Operation(
        INFO,
        "set_recording_group_object_attributes",
        DcaBinding(
            "PATCH", f"{ROOT}/recordingGroups/{{id}}/objectAttributes", body="value", body_field="objectAttributes"
        ),
        params=SetRecordingGroupObjectAttributesRequest,
        access="admin",
        effect="write",
        write="replace",
    )


# ---------------------------------------------------------------------------
# API classes


class RecordingGroupConfigApi(SyncApi):
    """Recording group API (``recording-group-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> RecordingGroupTree:
        """The whole API tree (all recording groups). Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_recording_groups(self, *, request_options: RequestOptions | None = None) -> list[RecordingGroup]:
        """List the recording groups. Access: admin."""
        return self._run(OPS.list_recording_groups, None, {}, request_options)

    def get_recording_group(self, id: IdString, *, request_options: RequestOptions | None = None) -> RecordingGroup:
        """Get one recording group. Access: admin."""
        return self._run(OPS.get_recording_group, None, {"id": id}, request_options)

    @overload
    def add_recording_group(
        self, request: AddRecordingGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_recording_group(
        self,
        /,
        *,
        destinations: DestinationsArray,
        id: IdString | MISSING = MISSING,
        nice_name: str | MISSING = MISSING,
        description: str | MISSING = MISSING,
        max_retention_time: PositiveInteger | MISSING = MISSING,
        container_format: ContainerFormat | MISSING = MISSING,
        span_duration: PositiveInteger | MISSING = MISSING,
        segment_duration: TargetAndMax | MISSING = MISSING,
        segment_size: TargetAndMax | MISSING = MISSING,
        pre_duration: PositiveInteger | MISSING = MISSING,
        post_duration: PositiveInteger | MISSING = MISSING,
        stream_options: str | MISSING = MISSING,
        encryption: Encryption | MISSING = MISSING,
        data_producer_options: DataProducerOptions | MISSING = MISSING,
        object_attributes: ObjectAttributes | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_recording_group(
        self,
        request: AddRecordingGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a recording group. Only destinations is required; the device generates an id when none is given.

        Access: admin.
        """
        self._run(OPS.add_recording_group, request, kwargs, request_options)

    def remove_recording_group(self, id: IdString, *, request_options: RequestOptions | None = None) -> None:
        """Delete a recording group. Access: admin."""
        self._run(OPS.remove_recording_group, None, {"id": id}, request_options)

    @overload
    def set_recording_group_data_producer_options(
        self, request: SetRecordingGroupDataProducerOptionsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_recording_group_data_producer_options(
        self,
        id: IdString,
        data_producer_options: DataProducerOptions,
        /,
        *,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_recording_group_data_producer_options(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the data producer options of a recording group.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRecordingGroupDataProducerOptionsRequest):
            kwargs = {**dict(zip(("id", "data_producer_options"), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_recording_group_data_producer_options, request, kwargs, request_options)

    @overload
    def set_recording_group_object_attributes(
        self, request: SetRecordingGroupObjectAttributesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_recording_group_object_attributes(
        self, id: IdString, object_attributes: ObjectAttributes, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_recording_group_object_attributes(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the object attributes of a recording group.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRecordingGroupObjectAttributesRequest):
            kwargs = {**dict(zip(("id", "object_attributes"), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_recording_group_object_attributes, request, kwargs, request_options)


class AsyncRecordingGroupConfigApi(AsyncApi):
    """Recording group API (``recording-group-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> RecordingGroupTree:
        """The whole API tree (all recording groups). Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_recording_groups(self, *, request_options: RequestOptions | None = None) -> list[RecordingGroup]:
        """List the recording groups. Access: admin."""
        return await self._run(OPS.list_recording_groups, None, {}, request_options)

    async def get_recording_group(
        self, id: IdString, *, request_options: RequestOptions | None = None
    ) -> RecordingGroup:
        """Get one recording group. Access: admin."""
        return await self._run(OPS.get_recording_group, None, {"id": id}, request_options)

    @overload
    async def add_recording_group(
        self, request: AddRecordingGroupRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_recording_group(
        self,
        /,
        *,
        destinations: DestinationsArray,
        id: IdString | MISSING = MISSING,
        nice_name: str | MISSING = MISSING,
        description: str | MISSING = MISSING,
        max_retention_time: PositiveInteger | MISSING = MISSING,
        container_format: ContainerFormat | MISSING = MISSING,
        span_duration: PositiveInteger | MISSING = MISSING,
        segment_duration: TargetAndMax | MISSING = MISSING,
        segment_size: TargetAndMax | MISSING = MISSING,
        pre_duration: PositiveInteger | MISSING = MISSING,
        post_duration: PositiveInteger | MISSING = MISSING,
        stream_options: str | MISSING = MISSING,
        encryption: Encryption | MISSING = MISSING,
        data_producer_options: DataProducerOptions | MISSING = MISSING,
        object_attributes: ObjectAttributes | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_recording_group(
        self,
        request: AddRecordingGroupRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a recording group. Only destinations is required; the device generates an id when none is given.

        Access: admin.
        """
        await self._run(OPS.add_recording_group, request, kwargs, request_options)

    async def remove_recording_group(self, id: IdString, *, request_options: RequestOptions | None = None) -> None:
        """Delete a recording group. Access: admin."""
        await self._run(OPS.remove_recording_group, None, {"id": id}, request_options)

    @overload
    async def set_recording_group_data_producer_options(
        self, request: SetRecordingGroupDataProducerOptionsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_recording_group_data_producer_options(
        self,
        id: IdString,
        data_producer_options: DataProducerOptions,
        /,
        *,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_recording_group_data_producer_options(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the data producer options of a recording group.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRecordingGroupDataProducerOptionsRequest):
            kwargs = {**dict(zip(("id", "data_producer_options"), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_recording_group_data_producer_options, request, kwargs, request_options)

    @overload
    async def set_recording_group_object_attributes(
        self, request: SetRecordingGroupObjectAttributesRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_recording_group_object_attributes(
        self, id: IdString, object_attributes: ObjectAttributes, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_recording_group_object_attributes(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Replace the object attributes of a recording group.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRecordingGroupObjectAttributesRequest):
            kwargs = {**dict(zip(("id", "object_attributes"), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_recording_group_object_attributes, request, kwargs, request_options)
