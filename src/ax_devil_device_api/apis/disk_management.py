# GENERATED from specs/apis/network-video/disk-management.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List, format, check, repair, mount, unmount and lock disks (SD cards and network shares), follow their jobs, and read capabilities and health.

Docs: https://developer.axis.com/vapix/network-video/edge-storage-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap, XmlStatusError
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DiskStatus = Literal["disconnected", "connected", "OK", "failed", "no passphrase", "wrong passphrase", "not encrypted"]
CleanupPolicy = Literal["none", "fifo"]


class Disk(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID."""
    name: str
    """User-friendly disk name (storage parameter FriendlyName)."""
    total_size: int = Field(validation_alias="totalsize", serialization_alias="totalsize")
    """Total disk size in kilobytes."""
    free_size: int = Field(validation_alias="freesize", serialization_alias="freesize")
    """Free disk size in kilobytes."""
    cleanup_level: int | None = Field(
        default=None, validation_alias="cleanuplevel", serialization_alias="cleanuplevel", ge=0, le=99
    )
    """Cleanup level in percent of the total disk space. Obsolete from AXIS OS 5.50."""
    cleanup_max_age: int | None = Field(
        default=None, validation_alias="cleanupmaxage", serialization_alias="cleanupmaxage", ge=0, le=7000
    )
    """Days that unlocked recordings are kept. Recordings are deleted earlier if the disk becomes full."""
    cleanup_policy: CleanupPolicy | None = Field(
        default=None, validation_alias="cleanuppolicy", serialization_alias="cleanuppolicy"
    )
    locked: bool
    """The disk is locked (reported as yes or no)."""
    full: bool
    """The disk is full (reported as yes or no)."""
    readonly: bool
    """The disk is read-only (reported as yes or no)."""
    file_system: str | None = Field(default=None, validation_alias="filesystem", serialization_alias="filesystem")
    """File system of the disk, for example ext4, vfat or cifs."""
    status: DiskStatus
    group: str = Field(pattern="^S[0-9]+$")
    """The parameter group Storage.S# that defines the disk."""
    required_file_system: str | None = Field(
        default=None, validation_alias="requiredfilesystem", serialization_alias="requiredfilesystem"
    )
    """The file system set as required file system; none if not set."""
    disk_encryption_enabled: bool | None = Field(
        default=None, validation_alias="diskencryptionenabled", serialization_alias="diskencryptionenabled"
    )
    """Disk encryption is enabled (reported as true or false)."""
    disk_encrypted: bool | None = Field(
        default=None, validation_alias="diskencrypted", serialization_alias="diskencrypted"
    )
    """The disk content is encrypted. Only true once encryption is enabled and the disk has been mounted and formatted."""


class DiskList(Model):
    number_of_disks: int | None = Field(
        default=None, validation_alias="numberofdisks", serialization_alias="numberofdisks"
    )
    """Number of disks in the reply."""
    disks: list[Disk] | None = None


class JobStarted(Model):
    job_id: int = Field(validation_alias="jobid", serialization_alias="jobid")
    """ID of the started job. Pass it to get_job_progress."""
    disk_id: str | None = Field(default=None, validation_alias="diskid", serialization_alias="diskid")
    action: str | None = None
    """The requested action: format, checkdisk, repair, mount or unmount."""


class JobProgress(Model):
    """A job that failed raises an error; description then carries the device message."""

    job_id: int = Field(validation_alias="jobid", serialization_alias="jobid")
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    action: str
    """format, checkdisk, repair, mount, unmount or N/A."""
    progress: int = Field(ge=0, le=100)
    """Percent done."""
    description: str | None = None
    """Description of the result."""


class FileSystem(Model):
    name: str
    """File system name, for example ext4 or vfat."""
    nicename: str | None = None
    """Descriptive name of the file system."""
    required_fs_supported: bool | None = Field(
        default=None, validation_alias="requiredfssupported", serialization_alias="requiredfssupported"
    )
    """The file system can be used as required file system."""


class DiskCapabilities(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    required_fs_supported: bool | None = Field(
        default=None, validation_alias="requiredfssupported", serialization_alias="requiredfssupported"
    )
    """The disk supports required file system."""
    encryption_supported: bool | None = Field(
        default=None, validation_alias="encryptionsupported", serialization_alias="encryptionsupported"
    )
    """The disk supports disk encryption."""
    filesystems: list[FileSystem] | None = None
    """The file systems the disk can be formatted with."""


class DiskHealth(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    wear: int
    """Percent of the expected life span that has passed; it can exceed 100. A negative value means the disk is not an Axis SD card or the value is unavailable: -1 not supported, -2 an error occurred, -3 the disk is not present."""
    temperature: int | None = None
    """Disk temperature in Kelvin (315 K is 42 C). From AXIS OS 9.50."""
    overall_health: int | None = Field(
        default=None, validation_alias="overallhealth", serialization_alias="overallhealth", ge=0, le=1
    )
    """Overall health: 0 = FAIL, 1 = PASSED. From AXIS OS 9.50."""


class DiskHealthList(Model):
    disks: list[DiskHealth] | None = None


class ListDisksRequest(Model):
    disk_id: str | None = Field(default=None, validation_alias="diskid", serialization_alias="diskid")
    """all lists every disk; otherwise comma-separated Disk IDs of the disks to list."""


class FormatDiskRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk to format."""
    filesystem: Literal["ext4", "vfat", "cifs"] | None = None
    """File system to format with; the disk's choices come from get_capabilities. Default: the file system already on the disk. cifs formats a network share and removes all data this product recorded to it."""


class CheckDiskRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk to check."""


class RepairDiskRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk to repair."""


class MountDiskRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk to mount."""


class UnmountDiskRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk to unmount."""


class GetJobProgressRequest(Model):
    job_id: int = Field(validation_alias="jobid", serialization_alias="jobid")
    """The ID of the job to check."""
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk the job runs on."""


class LockDiskRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""


class UnlockDiskRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""


class GetCapabilitiesRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/disks/list.cgi"

INFO = ApiInfo(
    id="disk-management",
    name="Disk management API (Edge storage)",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.LocalStorage.LocalStorage", "yes"),
        ParamDiscovery("Properties.LocalStorage.Version", "1.00"),
    ),
    requires_firmware="5.40",
    docs=("https://developer.axis.com/vapix/network-video/edge-storage-api/",),
)


class OPS:
    list_disks = Operation(
        INFO,
        "list_disks",
        CgiBinding(
            PATH,
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("numberofdisks"),
                        XmlField(
                            "disks",
                            source="path",
                            name="disk",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("diskid"),
                                    XmlField("name"),
                                    XmlField("totalsize"),
                                    XmlField("freesize"),
                                    XmlField("cleanuplevel"),
                                    XmlField("cleanupmaxage"),
                                    XmlField("cleanuppolicy"),
                                    XmlField("locked"),
                                    XmlField("full"),
                                    XmlField("readonly"),
                                    XmlField("filesystem"),
                                    XmlField("status"),
                                    XmlField("group"),
                                    XmlField("requiredfilesystem"),
                                    XmlField("diskencryptionenabled"),
                                    XmlField("diskencrypted"),
                                )
                            ),
                        ),
                    ),
                    root="disks",
                )
            ),
        ),
        params=ListDisksRequest,
        result=DiskList,
        access="operator",
        effect="read",
    )
    format_disk = Operation(
        INFO,
        "format_disk",
        CgiBinding(
            "/axis-cgi/disks/format.cgi",
            args=(CgiArg("disk_id", wire="diskid"), CgiArg("filesystem")),
            reply=Xml(
                map=XmlMap(fields=(XmlField("jobid"), XmlField("diskid"), XmlField("action")), root="job"),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="description"),
            ),
        ),
        params=FormatDiskRequest,
        result=JobStarted,
        access="admin",
        effect="action",
    )
    check_disk = Operation(
        INFO,
        "check_disk",
        CgiBinding(
            "/axis-cgi/disks/checkdisk.cgi",
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("jobid"), XmlField("diskid"), XmlField("action")), root="job"),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="description"),
            ),
        ),
        params=CheckDiskRequest,
        result=JobStarted,
        access="operator",
        effect="action",
    )
    repair_disk = Operation(
        INFO,
        "repair_disk",
        CgiBinding(
            "/axis-cgi/disks/repair.cgi",
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("jobid"), XmlField("diskid"), XmlField("action")), root="job"),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="description"),
            ),
        ),
        params=RepairDiskRequest,
        result=JobStarted,
        access="admin",
        effect="action",
    )
    mount_disk = Operation(
        INFO,
        "mount_disk",
        CgiBinding(
            "/axis-cgi/disks/mount.cgi",
            fixed_query=(("action", "mount"),),
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("jobid"), XmlField("diskid"), XmlField("action")), root="job"),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="description"),
            ),
        ),
        params=MountDiskRequest,
        result=JobStarted,
        access="admin",
        effect="action",
    )
    unmount_disk = Operation(
        INFO,
        "unmount_disk",
        CgiBinding(
            "/axis-cgi/disks/mount.cgi",
            fixed_query=(("action", "unmount"),),
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("jobid"), XmlField("diskid"), XmlField("action")), root="job"),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="description"),
            ),
        ),
        params=UnmountDiskRequest,
        result=JobStarted,
        access="admin",
        effect="action",
    )
    get_job_progress = Operation(
        INFO,
        "get_job_progress",
        CgiBinding(
            "/axis-cgi/disks/job.cgi",
            args=(CgiArg("job_id", wire="jobid"), CgiArg("disk_id", wire="diskid")),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("jobid"),
                        XmlField("diskid"),
                        XmlField("action"),
                        XmlField("progress"),
                        XmlField("description"),
                    ),
                    root="job",
                ),
                status_error=XmlStatusError(attribute="result", value="ERROR", message="description"),
            ),
        ),
        params=GetJobProgressRequest,
        result=JobProgress,
        access="operator",
        effect="read",
    )
    lock_disk = Operation(
        INFO,
        "lock_disk",
        CgiBinding(
            "/axis-cgi/disks/lock.cgi",
            fixed_query=(("action", "lock"),),
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(status_error=XmlStatusError(attribute="result", value="ERROR", message="description")),
        ),
        params=LockDiskRequest,
        access="admin",
        effect="action",
    )
    unlock_disk = Operation(
        INFO,
        "unlock_disk",
        CgiBinding(
            "/axis-cgi/disks/lock.cgi",
            fixed_query=(("action", "unlock"),),
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(status_error=XmlStatusError(attribute="result", value="ERROR", message="description")),
        ),
        params=UnlockDiskRequest,
        access="admin",
        effect="action",
    )
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        CgiBinding(
            "/axis-cgi/disks/getcapabilities.cgi",
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("diskid"),
                        XmlField("requiredfssupported"),
                        XmlField("encryptionsupported"),
                        XmlField(
                            "filesystems",
                            source="path",
                            name="filesystems/filesystem",
                            many=True,
                            nested=XmlMap(
                                fields=(XmlField("name"), XmlField("nicename"), XmlField("requiredfssupported"))
                            ),
                        ),
                    ),
                    root="disk",
                )
            ),
        ),
        params=GetCapabilitiesRequest,
        result=DiskCapabilities,
        access="operator",
        effect="read",
    )
    get_health = Operation(
        INFO,
        "get_health",
        CgiBinding(
            "/axis-cgi/disks/gethealth.cgi",
            reply=Xml(
                error_elements=("GeneralError",),
                map=XmlMap(
                    fields=(
                        XmlField(
                            "disks",
                            source="path",
                            name="HealthStatus",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("diskid"),
                                    XmlField("wear"),
                                    XmlField("temperature"),
                                    XmlField("overallhealth"),
                                )
                            ),
                        ),
                    ),
                    root="HealthStatusSuccess",
                ),
            ),
        ),
        result=DiskHealthList,
        access="operator",
        effect="read",
        errors={10: ErrorCode("An error occurred while processing the request.", "internal")},
    )


# ---------------------------------------------------------------------------
# API classes


class DiskManagementApi(SyncApi):
    """Disk management API (Edge storage) (``disk-management``)."""

    INFO = INFO

    def list_disks(
        self, disk_id: str | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> DiskList:
        """List the available disks (formatted, mounted and ready) and their status.

        Access: operator.
        """
        return self._run(OPS.list_disks, None, {"disk_id": disk_id}, request_options)

    def format_disk(
        self,
        disk_id: str,
        *,
        filesystem: Literal["ext4", "vfat", "cifs"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> JobStarted:
        """Format a disk and start a job.

        SD cards can be formatted with ext4 (recommended) or vfat. Formatting removes all data on the disk.
        If a required file system is set, the disk is formatted automatically when mounted; if disk
        encryption is enabled, the disk is encrypted when formatted.

        Access: admin.
        """
        return self._run(OPS.format_disk, None, {"disk_id": disk_id, "filesystem": filesystem}, request_options)

    def check_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Check the integrity of the file system and start a job.

        Only SD cards formatted with ext4 can be checked. The request fails if the disk is mounted or if
        encryption is enabled without a valid passphrase. If an error is found, try repair_disk.

        Access: operator.
        """
        return self._run(OPS.check_disk, None, {"disk_id": disk_id}, request_options)

    def repair_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Repair the file system and start a job.

        Repairing may lose data. Only SD cards formatted with ext4 can be repaired. The request fails if the
        disk is mounted or if encryption is enabled without a valid passphrase.

        Access: admin.
        """
        return self._run(OPS.repair_disk, None, {"disk_id": disk_id}, request_options)

    def mount_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Mount a disk and start a job.

        Mounting is automatic when an SD card is inserted, when a network share is bound and at boot. A
        manual mount is only needed after an unmount that was not followed by an automatic remount.

        Access: admin.
        """
        return self._run(OPS.mount_disk, None, {"disk_id": disk_id}, request_options)

    def unmount_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Unmount a disk and start a job.

        Unmount SD cards before ejecting them, to prevent corrupted recordings. An unmounted disk is
        unavailable to the system.

        Access: admin.
        """
        return self._run(OPS.unmount_disk, None, {"disk_id": disk_id}, request_options)

    def get_job_progress(
        self, job_id: int, disk_id: str, *, request_options: RequestOptions | None = None
    ) -> JobProgress:
        """Check the progress of a format, check disk, repair, mount or unmount job.

        Call it repeatedly until the job is done.

        Access: operator.
        """
        return self._run(OPS.get_job_progress, None, {"job_id": job_id, "disk_id": disk_id}, request_options)

    def lock_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Lock a disk.

        A locked disk cannot be formatted or written to. Active recordings stop and saved recordings cannot
        be removed.

        Access: admin.
        """
        self._run(OPS.lock_disk, None, {"disk_id": disk_id}, request_options)

    def unlock_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Unlock a disk. Access: admin."""
        self._run(OPS.unlock_disk, None, {"disk_id": disk_id}, request_options)

    def get_capabilities(self, disk_id: str, *, request_options: RequestOptions | None = None) -> DiskCapabilities:
        """List what a disk supports: formattable file systems, required file system and encryption.

        Access: operator.
        """
        return self._run(OPS.get_capabilities, None, {"disk_id": disk_id}, request_options)

    def get_health(self, *, request_options: RequestOptions | None = None) -> DiskHealthList:
        """List the health status (wear level, temperature, overall health) of all disks.

        Requires AXIS OS 7.20 or later.

        Access: operator.
        """
        return self._run(OPS.get_health, None, {}, request_options)


class AsyncDiskManagementApi(AsyncApi):
    """Disk management API (Edge storage) (``disk-management``)."""

    INFO = INFO

    async def list_disks(
        self, disk_id: str | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> DiskList:
        """List the available disks (formatted, mounted and ready) and their status.

        Access: operator.
        """
        return await self._run(OPS.list_disks, None, {"disk_id": disk_id}, request_options)

    async def format_disk(
        self,
        disk_id: str,
        *,
        filesystem: Literal["ext4", "vfat", "cifs"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> JobStarted:
        """Format a disk and start a job.

        SD cards can be formatted with ext4 (recommended) or vfat. Formatting removes all data on the disk.
        If a required file system is set, the disk is formatted automatically when mounted; if disk
        encryption is enabled, the disk is encrypted when formatted.

        Access: admin.
        """
        return await self._run(OPS.format_disk, None, {"disk_id": disk_id, "filesystem": filesystem}, request_options)

    async def check_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Check the integrity of the file system and start a job.

        Only SD cards formatted with ext4 can be checked. The request fails if the disk is mounted or if
        encryption is enabled without a valid passphrase. If an error is found, try repair_disk.

        Access: operator.
        """
        return await self._run(OPS.check_disk, None, {"disk_id": disk_id}, request_options)

    async def repair_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Repair the file system and start a job.

        Repairing may lose data. Only SD cards formatted with ext4 can be repaired. The request fails if the
        disk is mounted or if encryption is enabled without a valid passphrase.

        Access: admin.
        """
        return await self._run(OPS.repair_disk, None, {"disk_id": disk_id}, request_options)

    async def mount_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Mount a disk and start a job.

        Mounting is automatic when an SD card is inserted, when a network share is bound and at boot. A
        manual mount is only needed after an unmount that was not followed by an automatic remount.

        Access: admin.
        """
        return await self._run(OPS.mount_disk, None, {"disk_id": disk_id}, request_options)

    async def unmount_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> JobStarted:
        """Unmount a disk and start a job.

        Unmount SD cards before ejecting them, to prevent corrupted recordings. An unmounted disk is
        unavailable to the system.

        Access: admin.
        """
        return await self._run(OPS.unmount_disk, None, {"disk_id": disk_id}, request_options)

    async def get_job_progress(
        self, job_id: int, disk_id: str, *, request_options: RequestOptions | None = None
    ) -> JobProgress:
        """Check the progress of a format, check disk, repair, mount or unmount job.

        Call it repeatedly until the job is done.

        Access: operator.
        """
        return await self._run(OPS.get_job_progress, None, {"job_id": job_id, "disk_id": disk_id}, request_options)

    async def lock_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Lock a disk.

        A locked disk cannot be formatted or written to. Active recordings stop and saved recordings cannot
        be removed.

        Access: admin.
        """
        await self._run(OPS.lock_disk, None, {"disk_id": disk_id}, request_options)

    async def unlock_disk(self, disk_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Unlock a disk. Access: admin."""
        await self._run(OPS.unlock_disk, None, {"disk_id": disk_id}, request_options)

    async def get_capabilities(
        self, disk_id: str, *, request_options: RequestOptions | None = None
    ) -> DiskCapabilities:
        """List what a disk supports: formattable file systems, required file system and encryption.

        Access: operator.
        """
        return await self._run(OPS.get_capabilities, None, {"disk_id": disk_id}, request_options)

    async def get_health(self, *, request_options: RequestOptions | None = None) -> DiskHealthList:
        """List the health status (wear level, temperature, overall health) of all disks.

        Requires AXIS OS 7.20 or later.

        Access: operator.
        """
        return await self._run(OPS.get_health, None, {}, request_options)
