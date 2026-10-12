# GENERATED from specs/apis/network-video/disk-properties.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure disk properties: required file system (autoformat), disk encryption and passphrase, cleanup max age and policy, and disk alert levels.

Docs: https://developer.axis.com/vapix/network-video/edge-storage-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class AlertLevels(Model):
    wear: int | None = Field(default=None, validation_alias="Wear", serialization_alias="Wear", ge=0)
    """Wear level that triggers a storage alert event."""
    temperature: int | None = Field(
        default=None, validation_alias="Temperature", serialization_alias="Temperature", ge=0
    )
    """Disk temperature in Kelvin that triggers a storage alert event."""


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version as major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """A deprecated schema version should not be used."""


class SchemaVersions(Model):
    versions: list[SchemaVersion] | None = None


class SetRequiredFileSystemRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""
    file_system: Literal["none", "ext4"] = Field(validation_alias="filesystem", serialization_alias="filesystem")
    """The required file system; none disables the function. Check what the disk supports with get_capabilities in the disk-management API."""


class EnableDiskEncryptionRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk to encrypt."""
    passphrase: str = Field(max_length=512)
    """The passphrase to encrypt with. At most 512 bytes."""


class DisableDiskEncryptionRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""


class ChangeDiskPassphraseRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""
    new_passphrase: str = Field(validation_alias="newpassphrase", serialization_alias="newpassphrase", max_length=512)
    """The new passphrase. At most 512 bytes."""
    old_passphrase: str = Field(validation_alias="oldpassphrase", serialization_alias="oldpassphrase")
    """The current passphrase."""


class SetCleanupMaxAgeRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""
    max_age: int = Field(validation_alias="maxage", serialization_alias="maxage", ge=0, le=7000)
    """Days that unlocked recordings are kept on the disk. Only used when the cleanup policy is fifo. Recordings are deleted earlier when free space is low."""


class SetCleanupPolicyRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""
    cleanup_policy: Literal["fifo", "none"] = Field(
        validation_alias="cleanuppolicy", serialization_alias="cleanuppolicy"
    )
    """fifo deletes recordings automatically according to the cleanup max age. none leaves deletion to the user. Recordings are deleted anyway when free space is low."""


class SetDiskAlertLevelsRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""
    wear: int | None = Field(default=None, ge=0)
    """Wear level that triggers a storage alert event."""
    temperature: int | None = Field(default=None, ge=0)
    """Disk temperature in Kelvin that triggers a storage alert event."""


class GetDiskAlertLevelsRequest(Model):
    disk_id: str = Field(validation_alias="diskid", serialization_alias="diskid")
    """The Disk ID of the disk."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/disks/properties/setrequiredfs.cgi"

INFO = ApiInfo(
    id="disk-properties",
    name="Disk properties API (Edge storage)",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.LocalStorage.RequiredFileSystem", "yes"),
        ParamDiscovery("Properties.LocalStorage.DiskEncryption", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/edge-storage-api/",),
)


class OPS:
    set_required_file_system = Operation(
        INFO,
        "set_required_file_system",
        CgiBinding(
            "/axis-cgi/disks/properties/setrequiredfs.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("disk_id", wire="diskid"), CgiArg("file_system", wire="filesystem")),
            reply=Xml(),
        ),
        params=SetRequiredFileSystemRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            30: ErrorCode("Specified file system is not supported.", "unsupported"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
        },
    )
    enable_disk_encryption = Operation(
        INFO,
        "enable_disk_encryption",
        CgiBinding(
            "/axis-cgi/disks/properties/enablediskencryption.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("disk_id", wire="diskid"), CgiArg("passphrase")),
            reply=Xml(),
        ),
        params=EnableDiskEncryptionRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            50: ErrorCode("Invalid disk ID.", "invalid_argument"),
            100: ErrorCode("The disk does not support disk encryption.", "unsupported"),
            110: ErrorCode("Invalid passphrase.", "invalid_argument"),
            140: ErrorCode("Encryption is already enabled."),
            160: ErrorCode("The disk is mounted. Encryption can only be enabled/disabled when the disk is unmounted."),
        },
    )
    disable_disk_encryption = Operation(
        INFO,
        "disable_disk_encryption",
        CgiBinding(
            "/axis-cgi/disks/properties/disablediskencryption.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(),
        ),
        params=DisableDiskEncryptionRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            50: ErrorCode("Invalid disk ID.", "invalid_argument"),
            100: ErrorCode("The disk does not support disk encryption.", "unsupported"),
            160: ErrorCode("The disk is mounted. Encryption can only be enabled/disabled when the disk is unmounted."),
        },
    )
    change_disk_passphrase = Operation(
        INFO,
        "change_disk_passphrase",
        CgiBinding(
            "/axis-cgi/disks/properties/changediskpassphrase.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(
                CgiArg("disk_id", wire="diskid"),
                CgiArg("new_passphrase", wire="newpassphrase"),
                CgiArg("old_passphrase", wire="oldpassphrase"),
            ),
            reply=Xml(),
        ),
        params=ChangeDiskPassphraseRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            50: ErrorCode("Invalid disk ID.", "invalid_argument"),
            100: ErrorCode("The disk does not support disk encryption.", "unsupported"),
            120: ErrorCode("Invalid new passphrase.", "invalid_argument"),
            130: ErrorCode("The oldpassphrase does not match the existing passphrase.", "invalid_argument"),
            150: ErrorCode("The disk is unmounted. Passphrase can only be changed when the disk is mounted."),
        },
    )
    set_cleanup_max_age = Operation(
        INFO,
        "set_cleanup_max_age",
        CgiBinding(
            "/axis-cgi/disks/properties/setcleanupmaxage.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("disk_id", wire="diskid"), CgiArg("max_age", wire="maxage")),
            reply=Xml(),
        ),
        params=SetCleanupMaxAgeRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            50: ErrorCode("Invalid disk ID.", "invalid_argument"),
        },
    )
    set_cleanup_policy = Operation(
        INFO,
        "set_cleanup_policy",
        CgiBinding(
            "/axis-cgi/disks/properties/setcleanuppolicy.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("disk_id", wire="diskid"), CgiArg("cleanup_policy", wire="cleanuppolicy")),
            reply=Xml(),
        ),
        params=SetCleanupPolicyRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            50: ErrorCode("Invalid disk ID.", "invalid_argument"),
        },
    )
    set_disk_alert_levels = Operation(
        INFO,
        "set_disk_alert_levels",
        CgiBinding(
            "/axis-cgi/disks/properties/setdiskalertlevels.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("disk_id", wire="diskid"), CgiArg("wear"), CgiArg("temperature")),
            reply=Xml(),
        ),
        params=SetDiskAlertLevelsRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            50: ErrorCode("Invalid disk ID.", "invalid_argument"),
        },
    )
    get_disk_alert_levels = Operation(
        INFO,
        "get_disk_alert_levels",
        CgiBinding(
            "/axis-cgi/disks/properties/getdiskalertlevels.cgi",
            fixed_query=(("schemaversion", "1"),),
            args=(CgiArg("disk_id", wire="diskid"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("Wear"), XmlField("Temperature")), root="Success/GetAlertLevelsSuccess/AlertLevels"
                )
            ),
        ),
        params=GetDiskAlertLevelsRequest,
        result=AlertLevels,
        access="operator",
        effect="read",
        errors={
            10: ErrorCode("Error while processing the request.", "internal"),
            20: ErrorCode("Invalid request.", "invalid_argument"),
            40: ErrorCode("Specified version is not supported.", "unsupported"),
            50: ErrorCode("Invalid disk ID.", "invalid_argument"),
        },
    )
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            "/axis-cgi/disks/properties/schemaversions.cgi",
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
                    root="Success/SchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class DiskPropertiesApi(SyncApi):
    """Disk properties API (Edge storage) (``disk-properties``)."""

    INFO = INFO

    def set_required_file_system(
        self, disk_id: str, file_system: Literal["none", "ext4"], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the required file system, or disable it with none.

        Each mounted SD card that uses another file system, or whose file system cannot be determined, is
        formatted automatically and its data is lost. A locked card is not reformatted; an unlocked one is
        formatted the next time it is mounted. Setting it while a card is mounted reformats the card when it
        is remounted. Called autoformat in the web interface.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_required_file_system, None, {"disk_id": disk_id, "file_system": file_system}, request_options)

    def enable_disk_encryption(
        self, disk_id: str, passphrase: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable disk encryption.

        The disk must be unmounted. Format and mount it afterwards to encrypt the content.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.enable_disk_encryption, None, {"disk_id": disk_id, "passphrase": passphrase}, request_options)

    def disable_disk_encryption(self, disk_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Disable disk encryption.

        The disk must be unmounted. Format and mount it afterwards; formatting removes the recordings.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.disable_disk_encryption, None, {"disk_id": disk_id}, request_options)

    def change_disk_passphrase(
        self, disk_id: str, *, new_passphrase: str, old_passphrase: str, request_options: RequestOptions | None = None
    ) -> None:
        """Change the disk encryption passphrase.

        The disk must be mounted. Ongoing recordings are not disrupted.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.change_disk_passphrase,
            None,
            {"disk_id": disk_id, "new_passphrase": new_passphrase, "old_passphrase": old_passphrase},
            request_options,
        )

    def set_cleanup_max_age(self, disk_id: str, max_age: int, *, request_options: RequestOptions | None = None) -> None:
        """Set the cleanup max age of a disk. Changes only the fields given. Access: admin."""
        self._run(OPS.set_cleanup_max_age, None, {"disk_id": disk_id, "max_age": max_age}, request_options)

    def set_cleanup_policy(
        self, disk_id: str, cleanup_policy: Literal["fifo", "none"], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the cleanup policy of a disk. Changes only the fields given. Access: admin."""
        self._run(OPS.set_cleanup_policy, None, {"disk_id": disk_id, "cleanup_policy": cleanup_policy}, request_options)

    def set_disk_alert_levels(
        self,
        disk_id: str,
        *,
        wear: int | MISSING = MISSING,
        temperature: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the levels at which a disk raises the storage alert event.

        The event is sent once with the alert property True when any property reaches its level, and again
        with False once all are below their levels.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_disk_alert_levels,
            None,
            {"disk_id": disk_id, "wear": wear, "temperature": temperature},
            request_options,
        )

    def get_disk_alert_levels(self, disk_id: str, *, request_options: RequestOptions | None = None) -> AlertLevels:
        """Get the alert levels of a disk. Access: operator."""
        return self._run(OPS.get_disk_alert_levels, None, {"disk_id": disk_id}, request_options)

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the supported XML schema versions of the Disk properties API and whether they are deprecated.

        Access: operator.
        """
        return self._run(OPS.get_schema_versions, None, {}, request_options)


class AsyncDiskPropertiesApi(AsyncApi):
    """Disk properties API (Edge storage) (``disk-properties``)."""

    INFO = INFO

    async def set_required_file_system(
        self, disk_id: str, file_system: Literal["none", "ext4"], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the required file system, or disable it with none.

        Each mounted SD card that uses another file system, or whose file system cannot be determined, is
        formatted automatically and its data is lost. A locked card is not reformatted; an unlocked one is
        formatted the next time it is mounted. Setting it while a card is mounted reformats the card when it
        is remounted. Called autoformat in the web interface.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_required_file_system, None, {"disk_id": disk_id, "file_system": file_system}, request_options
        )

    async def enable_disk_encryption(
        self, disk_id: str, passphrase: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable disk encryption.

        The disk must be unmounted. Format and mount it afterwards to encrypt the content.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.enable_disk_encryption, None, {"disk_id": disk_id, "passphrase": passphrase}, request_options
        )

    async def disable_disk_encryption(self, disk_id: str, *, request_options: RequestOptions | None = None) -> None:
        """Disable disk encryption.

        The disk must be unmounted. Format and mount it afterwards; formatting removes the recordings.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.disable_disk_encryption, None, {"disk_id": disk_id}, request_options)

    async def change_disk_passphrase(
        self, disk_id: str, *, new_passphrase: str, old_passphrase: str, request_options: RequestOptions | None = None
    ) -> None:
        """Change the disk encryption passphrase.

        The disk must be mounted. Ongoing recordings are not disrupted.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.change_disk_passphrase,
            None,
            {"disk_id": disk_id, "new_passphrase": new_passphrase, "old_passphrase": old_passphrase},
            request_options,
        )

    async def set_cleanup_max_age(
        self, disk_id: str, max_age: int, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the cleanup max age of a disk. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_cleanup_max_age, None, {"disk_id": disk_id, "max_age": max_age}, request_options)

    async def set_cleanup_policy(
        self, disk_id: str, cleanup_policy: Literal["fifo", "none"], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the cleanup policy of a disk. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_cleanup_policy, None, {"disk_id": disk_id, "cleanup_policy": cleanup_policy}, request_options
        )

    async def set_disk_alert_levels(
        self,
        disk_id: str,
        *,
        wear: int | MISSING = MISSING,
        temperature: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the levels at which a disk raises the storage alert event.

        The event is sent once with the alert property True when any property reaches its level, and again
        with False once all are below their levels.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_disk_alert_levels,
            None,
            {"disk_id": disk_id, "wear": wear, "temperature": temperature},
            request_options,
        )

    async def get_disk_alert_levels(
        self, disk_id: str, *, request_options: RequestOptions | None = None
    ) -> AlertLevels:
        """Get the alert levels of a disk. Access: operator."""
        return await self._run(OPS.get_disk_alert_levels, None, {"disk_id": disk_id}, request_options)

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the supported XML schema versions of the Disk properties API and whether they are deprecated.

        Access: operator.
        """
        return await self._run(OPS.get_schema_versions, None, {}, request_options)
