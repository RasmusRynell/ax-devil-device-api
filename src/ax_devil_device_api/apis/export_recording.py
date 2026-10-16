# GENERATED from specs/apis/network-video/export-recording.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Export an edge storage recording, whole or in part, as a single Matroska file (optionally in an AES-256 encrypted ZIP) or to an external USB disk.

Docs: https://developer.axis.com/vapix/network-video/edge-storage-api/
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Stream, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from .._runtime.driver import AsyncStreamResult, StreamResult
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version as major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """A deprecated schema version should not be used."""


class SchemaVersions(Model):
    versions: list[SchemaVersion] | None = None


class ExportEncryption(Model):
    encryption_format: str | None = Field(
        default=None, validation_alias="EncryptionFormat", serialization_alias="EncryptionFormat"
    )
    """A supported encryption format, for example zip-aes256."""


class ExportCapability(Model):
    export_format: str = Field(validation_alias="ExportFormat", serialization_alias="ExportFormat")
    """A supported media format, for example matroska."""
    encryptions: list[ExportEncryption] | None = Field(
        default=None, validation_alias="ExportEncryption", serialization_alias="ExportEncryption"
    )
    """Encryption formats available for the media format (API version 1.2)."""


class ExportCapabilities(Model):
    capabilities: list[ExportCapability] | None = None


class ExportProperties(Model):
    recording_id: str = Field(validation_alias="RecordingId", serialization_alias="RecordingId")
    export_format: str = Field(validation_alias="ExportFormat", serialization_alias="ExportFormat")
    """Media format."""
    encryption_format: str | None = Field(
        default=None, validation_alias="EncryptionFormat", serialization_alias="EncryptionFormat"
    )
    """Encryption format, when one was requested."""
    estimated_file_size: int = Field(validation_alias="EstimatedFileSize", serialization_alias="EstimatedFileSize")
    """Estimated file size in kilobytes; -1 when it cannot be estimated."""
    start_time: str = Field(validation_alias="Starttime", serialization_alias="Starttime")
    """Start time (UTC ISO 8601). It is set to the preceding key frame closest to the requested start time."""
    stop_time: str = Field(validation_alias="Stoptime", serialization_alias="Stoptime")
    """Stop time (UTC ISO 8601)."""


class ExportToExternalJob(Model):
    job_id: int = Field(validation_alias="JobId", serialization_alias="JobId")
    """Job ID to follow with get_job_status."""
    file_path: str | None = Field(default=None, validation_alias="FilePath", serialization_alias="FilePath")
    """Path of the exported file on the external disk."""


class JobStatus(Model):
    """A failed job raises an error with the code and description from the device."""

    status: Literal["In Progress", "Done"] = Field(validation_alias="Status", serialization_alias="Status")
    progress: int | None = Field(
        default=None, validation_alias="Progress", serialization_alias="Progress", ge=-1, le=100
    )
    """Percent done; -1 when unknown."""


class GetPropertiesRequest(Model):
    recording_id: str = Field(validation_alias="recordingid", serialization_alias="recordingid")
    """The Recording ID of the recording."""
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """Disk ID of the disk where the recording is stored."""
    start_time: str | None = Field(default=None, validation_alias="starttime", serialization_alias="starttime")
    """UTC ISO 8601 combined date and time. Use it for a part of a recording. Omitted: the recording's beginning."""
    stop_time: str | None = Field(default=None, validation_alias="stoptime", serialization_alias="stoptime")
    """UTC ISO 8601 combined date and time. Use it for a part of a recording. Omitted: the time of the request for an ongoing recording, the recording end for a finished one."""
    export_format: str | None = Field(default=None, validation_alias="exportformat", serialization_alias="exportformat")
    """The media format the recording should be exported to."""
    encryption_format: str | None = Field(
        default=None, validation_alias="encryptionformat", serialization_alias="encryptionformat"
    )
    """The encryption format of the export."""


class ExportRecordingRequest(Model):
    __masked__: ClassVar[frozenset[str]] = frozenset({"password"})
    recording_id: str = Field(validation_alias="recordingid", serialization_alias="recordingid")
    """The Recording ID of the recording."""
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """Disk ID of the disk where the recording is stored."""
    export_format: str = Field(validation_alias="exportformat", serialization_alias="exportformat")
    """Media format to export to, for example matroska. get_capabilities lists the supported formats."""
    start_time: str | None = Field(default=None, validation_alias="starttime", serialization_alias="starttime")
    """UTC ISO 8601 combined date and time. Start of the part to export. It should match a key frame (use the start time from get_properties); otherwise the closest preceding key frame is used. Omitted: the recording's beginning. A start time outside the recording gives a best-effort result."""
    stop_time: str | None = Field(default=None, validation_alias="stoptime", serialization_alias="stoptime")
    """UTC ISO 8601 combined date and time. End of the part to export. Omitted: the time of the request for an ongoing recording, the recording end for a finished one."""
    filename: str | None = None
    """Name of the exported file, UTF-8 encoded, without extension (it is added automatically)."""
    password: str | None = Field(default=None, max_length=512)
    """Password protection of the exported file. Keep it under 100 characters, as some applications cannot open longer ones; at most 512 bytes. Needs encryption_format."""
    encryption_format: str | None = Field(
        default=None, validation_alias="encryptionformat", serialization_alias="encryptionformat"
    )
    """Encryption format, for example zip-aes256 (API version 1.2). Required when a password is set; a password must be set to use it."""


class ExportToExternalRequest(Model):
    __masked__: ClassVar[frozenset[str]] = frozenset({"password"})
    recording_id: str = Field(validation_alias="recordingid", serialization_alias="recordingid")
    """The Recording ID of the recording."""
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """Disk ID of the disk where the recording is stored."""
    external_disk_id: Literal["USB_DISK"] = Field(
        validation_alias="externaldiskid", serialization_alias="externaldiskid"
    )
    """The disk to export to."""
    export_format: str = Field(validation_alias="exportformat", serialization_alias="exportformat")
    """Media format to export to, for example matroska. get_capabilities lists the supported formats."""
    start_time: str | None = Field(default=None, validation_alias="starttime", serialization_alias="starttime")
    """UTC ISO 8601 combined date and time. Start of the part to export. It should match a key frame (use the start time from get_properties); otherwise the closest preceding key frame is used. Omitted: the recording's beginning. A start time outside the recording gives a best-effort result."""
    stop_time: str | None = Field(default=None, validation_alias="stoptime", serialization_alias="stoptime")
    """UTC ISO 8601 combined date and time. End of the part to export. Omitted: the time of the request for an ongoing recording, the recording end for a finished one."""
    file_path: str | None = Field(default=None, validation_alias="filepath", serialization_alias="filepath")
    """Path and file name of the exported file on the external disk. Missing directories are created; '..' is not allowed. Omitted: a default name at the disk root."""
    password: str | None = Field(default=None, max_length=512)
    """Password protection of the exported file. Keep it under 100 characters, as some applications cannot open longer ones; at most 512 bytes. Needs encryption_format."""
    encryption_format: str | None = Field(
        default=None, validation_alias="encryptionformat", serialization_alias="encryptionformat"
    )
    """Encryption format, for example zip-aes256 (API version 1.2). Required when a password is set; a password must be set to use it."""


class GetJobStatusRequest(Model):
    job_id: int = Field(validation_alias="jobid", serialization_alias="jobid")
    """The job to return the status for."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/record/export/schemaversions.cgi"

INFO = ApiInfo(
    id="export-recording",
    name="Export recording API (Edge storage)",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.LocalStorage.ExportRecording", "yes"),),
    requires_firmware="5.60",
    docs=("https://developer.axis.com/vapix/network-video/edge-storage-api/",),
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
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        CgiBinding(
            "/axis-cgi/record/export/capabilities.cgi",
            fixed_query=(("schemaversion", "1"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "capabilities",
                            source="path",
                            name="ExportCapabilities",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("ExportFormat"),
                                    XmlField(
                                        "ExportEncryption",
                                        source="path",
                                        many=True,
                                        nested=XmlMap(fields=(XmlField("EncryptionFormat"),)),
                                    ),
                                )
                            ),
                        ),
                    ),
                    root="CapabilitiesSuccess",
                )
            ),
        ),
        result=ExportCapabilities,
        access="viewer",
        effect="read",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )
    get_properties = Operation(
        INFO,
        "get_properties",
        CgiBinding(
            "/axis-cgi/record/export/properties.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(
                CgiArg("recording_id", wire="recordingid"),
                CgiArg("disk_id", wire="diskid"),
                CgiArg("start_time", wire="starttime"),
                CgiArg("stop_time", wire="stoptime"),
                CgiArg("export_format", wire="exportformat"),
                CgiArg("encryption_format", wire="encryptionformat"),
            ),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("RecordingId"),
                        XmlField("ExportFormat"),
                        XmlField("EncryptionFormat"),
                        XmlField("EstimatedFileSize"),
                        XmlField("Starttime"),
                        XmlField("Stoptime"),
                    ),
                    root="PropertiesSuccess/ExportProperties",
                )
            ),
        ),
        params=GetPropertiesRequest,
        result=ExportProperties,
        access="viewer",
        effect="read",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            110: ErrorCode("Recording not found.", "not_found"),
            120: ErrorCode("Invalid start time.", "invalid_argument"),
            130: ErrorCode("Invalid stop time.", "invalid_argument"),
            140: ErrorCode("Invalid start time. The requested start time is after the stop time.", "invalid_argument"),
            150: ErrorCode(
                "Invalid start time. The requested start time is after the recording's stop time.", "invalid_argument"
            ),
            160: ErrorCode(
                "Invalid stop time. The requested stop time is before the recording's start time.", "invalid_argument"
            ),
            170: ErrorCode("Invalid export format.", "invalid_argument"),
            180: ErrorCode("Requested export format is not compatible with the media type.", "invalid_argument"),
            250: ErrorCode("Invalid encryption format.", "invalid_argument"),
            280: ErrorCode(
                "Requested encryption format is not compatible with requested export format.", "invalid_argument"
            ),
        },
    )
    export_recording = Operation(
        INFO,
        "export_recording",
        CgiBinding(
            "/axis-cgi/record/export/exportrecording.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(
                CgiArg("recording_id", wire="recordingid"),
                CgiArg("disk_id", wire="diskid"),
                CgiArg("export_format", wire="exportformat"),
                CgiArg("start_time", wire="starttime"),
                CgiArg("stop_time", wire="stoptime"),
                CgiArg("filename"),
                CgiArg("password"),
                CgiArg("encryption_format", wire="encryptionformat"),
            ),
            reply=Stream(media_types=("video/x-matroska", "application/zip")),
            stream=True,
        ),
        params=ExportRecordingRequest,
        access="viewer",
        effect="read",
    )
    export_to_external = Operation(
        INFO,
        "export_to_external",
        CgiBinding(
            "/axis-cgi/record/export/exporttoexternal.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(
                CgiArg("recording_id", wire="recordingid"),
                CgiArg("disk_id", wire="diskid"),
                CgiArg("external_disk_id", wire="externaldiskid"),
                CgiArg("export_format", wire="exportformat"),
                CgiArg("start_time", wire="starttime"),
                CgiArg("stop_time", wire="stoptime"),
                CgiArg("file_path", wire="filepath"),
                CgiArg("password"),
                CgiArg("encryption_format", wire="encryptionformat"),
            ),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("JobId"), XmlField("FilePath")), root="ExportToExternalSuccess/ExportToExternal"
                )
            ),
        ),
        params=ExportToExternalRequest,
        result=ExportToExternalJob,
        access="viewer",
        effect="action",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            200: ErrorCode("Invalid external disk.", "invalid_argument"),
            210: ErrorCode("Unusable external disk.", "unavailable"),
            220: ErrorCode("Maximum number of jobs reached.", "unavailable"),
            230: ErrorCode("Invalid file path.", "invalid_argument"),
            240: ErrorCode("Invalid password.", "invalid_argument"),
            250: ErrorCode("Invalid encryption format.", "invalid_argument"),
            260: ErrorCode("Password not set.", "invalid_argument"),
            270: ErrorCode("Encryption format not set.", "invalid_argument"),
            280: ErrorCode(
                "Requested encryption format is not compatible with requested export format.", "invalid_argument"
            ),
        },
    )
    get_job_status = Operation(
        INFO,
        "get_job_status",
        CgiBinding(
            "/axis-cgi/record/export/getjobstatus.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("job_id", wire="jobid"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("Status"), XmlField("Progress")), root="GetJobStatusSuccess/JobStatus")
            ),
        ),
        params=GetJobStatusRequest,
        result=JobStatus,
        access="viewer",
        effect="read",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            190: ErrorCode("Job not found.", "not_found"),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class ExportRecordingApi(SyncApi):
    """Export recording API (Edge storage) (``export-recording``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the supported XML schema versions. Access: viewer."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> ExportCapabilities:
        """List the export capabilities (media formats and encryption formats). Access: viewer."""
        return self._run(OPS.get_capabilities, None, {}, request_options)

    @overload
    def get_properties(
        self, request: GetPropertiesRequest, /, *, request_options: RequestOptions | None = None
    ) -> ExportProperties: ...
    @overload
    def get_properties(
        self,
        recording_id: str,
        disk_id: str,
        /,
        *,
        start_time: str | MISSING = MISSING,
        stop_time: str | MISSING = MISSING,
        export_format: str | MISSING = MISSING,
        encryption_format: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ExportProperties: ...
    def get_properties(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ExportProperties:
        """Get the export properties of a recording: proper start time, stop time and estimated size.

        Request the properties before exporting. The returned start time is the preceding key frame closest
        to the requested start time.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, GetPropertiesRequest):
            kwargs = bind_positional(OPS.get_properties, ("recording_id", "disk_id"), (request, *args), kwargs)
            request = None
        return self._run(OPS.get_properties, request, kwargs, request_options)

    @overload
    def export_recording(
        self, request: ExportRecordingRequest, /, *, request_options: RequestOptions | None = None
    ) -> StreamResult[bytes]: ...
    @overload
    def export_recording(
        self,
        recording_id: str,
        disk_id: str,
        export_format: str,
        /,
        *,
        start_time: str | MISSING = MISSING,
        stop_time: str | MISSING = MISSING,
        filename: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        encryption_format: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StreamResult[bytes]: ...
    def export_recording(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> StreamResult[bytes]:
        """Export a recording, or part of one, as a single file; returns the file as a stream of byte chunks (exports can be gigabytes, so write them as they arrive).

        The file is Matroska (video/x-matroska), or a ZIP archive (application/zip) when a password is set.
        The device names the file from the start and stop times unless filename is given, and gives
        encrypted ZIP files without a name a random XXXXXX.zip name; the name is not part of the result.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ExportRecordingRequest):
            kwargs = bind_positional(
                OPS.export_recording, ("recording_id", "disk_id", "export_format"), (request, *args), kwargs
            )
            request = None
        return self._run(OPS.export_recording, request, kwargs, request_options)

    @overload
    def export_to_external(
        self, request: ExportToExternalRequest, /, *, request_options: RequestOptions | None = None
    ) -> ExportToExternalJob: ...
    @overload
    def export_to_external(
        self,
        recording_id: str,
        disk_id: str,
        external_disk_id: Literal["USB_DISK"],
        export_format: str,
        /,
        *,
        start_time: str | MISSING = MISSING,
        stop_time: str | MISSING = MISSING,
        file_path: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        encryption_format: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ExportToExternalJob: ...
    def export_to_external(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ExportToExternalJob:
        """Export a recording to an external disk (USB) and return the job.

        Available from API version 1.1. Only one export to an external disk can run at a time.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ExportToExternalRequest):
            kwargs = bind_positional(
                OPS.export_to_external,
                ("recording_id", "disk_id", "external_disk_id", "export_format"),
                (request, *args),
                kwargs,
            )
            request = None
        return self._run(OPS.export_to_external, request, kwargs, request_options)

    def get_job_status(self, job_id: int, *, request_options: RequestOptions | None = None) -> JobStatus:
        """Get the status of an export-to-external job (ongoing jobs and the last five completed).

        Available from API version 1.1.

        Access: viewer.
        """
        return self._run(OPS.get_job_status, None, {"job_id": job_id}, request_options)


class AsyncExportRecordingApi(AsyncApi):
    """Export recording API (Edge storage) (``export-recording``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the supported XML schema versions. Access: viewer."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> ExportCapabilities:
        """List the export capabilities (media formats and encryption formats). Access: viewer."""
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    @overload
    async def get_properties(
        self, request: GetPropertiesRequest, /, *, request_options: RequestOptions | None = None
    ) -> ExportProperties: ...
    @overload
    async def get_properties(
        self,
        recording_id: str,
        disk_id: str,
        /,
        *,
        start_time: str | MISSING = MISSING,
        stop_time: str | MISSING = MISSING,
        export_format: str | MISSING = MISSING,
        encryption_format: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ExportProperties: ...
    async def get_properties(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ExportProperties:
        """Get the export properties of a recording: proper start time, stop time and estimated size.

        Request the properties before exporting. The returned start time is the preceding key frame closest
        to the requested start time.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, GetPropertiesRequest):
            kwargs = bind_positional(OPS.get_properties, ("recording_id", "disk_id"), (request, *args), kwargs)
            request = None
        return await self._run(OPS.get_properties, request, kwargs, request_options)

    @overload
    async def export_recording(
        self, request: ExportRecordingRequest, /, *, request_options: RequestOptions | None = None
    ) -> AsyncStreamResult[bytes]: ...
    @overload
    async def export_recording(
        self,
        recording_id: str,
        disk_id: str,
        export_format: str,
        /,
        *,
        start_time: str | MISSING = MISSING,
        stop_time: str | MISSING = MISSING,
        filename: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        encryption_format: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AsyncStreamResult[bytes]: ...
    async def export_recording(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> AsyncStreamResult[bytes]:
        """Export a recording, or part of one, as a single file; returns the file as a stream of byte chunks (exports can be gigabytes, so write them as they arrive).

        The file is Matroska (video/x-matroska), or a ZIP archive (application/zip) when a password is set.
        The device names the file from the start and stop times unless filename is given, and gives
        encrypted ZIP files without a name a random XXXXXX.zip name; the name is not part of the result.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ExportRecordingRequest):
            kwargs = bind_positional(
                OPS.export_recording, ("recording_id", "disk_id", "export_format"), (request, *args), kwargs
            )
            request = None
        return await self._run(OPS.export_recording, request, kwargs, request_options)

    @overload
    async def export_to_external(
        self, request: ExportToExternalRequest, /, *, request_options: RequestOptions | None = None
    ) -> ExportToExternalJob: ...
    @overload
    async def export_to_external(
        self,
        recording_id: str,
        disk_id: str,
        external_disk_id: Literal["USB_DISK"],
        export_format: str,
        /,
        *,
        start_time: str | MISSING = MISSING,
        stop_time: str | MISSING = MISSING,
        file_path: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        encryption_format: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ExportToExternalJob: ...
    async def export_to_external(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> ExportToExternalJob:
        """Export a recording to an external disk (USB) and return the job.

        Available from API version 1.1. Only one export to an external disk can run at a time.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, ExportToExternalRequest):
            kwargs = bind_positional(
                OPS.export_to_external,
                ("recording_id", "disk_id", "external_disk_id", "export_format"),
                (request, *args),
                kwargs,
            )
            request = None
        return await self._run(OPS.export_to_external, request, kwargs, request_options)

    async def get_job_status(self, job_id: int, *, request_options: RequestOptions | None = None) -> JobStatus:
        """Get the status of an export-to-external job (ongoing jobs and the last five completed).

        Available from API version 1.1.

        Access: viewer.
        """
        return await self._run(OPS.get_job_status, None, {"job_id": job_id}, request_options)
