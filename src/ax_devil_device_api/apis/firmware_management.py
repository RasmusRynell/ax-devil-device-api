# GENERATED from specs/apis/network-video/firmware-management.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Firmware status, upgrade, commit, rollback, purge, factory default and reboot.

Docs: https://developer.axis.com/vapix/network-video/firmware-management-api/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._http.upload import UploadSource, UploadSpec
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding, JsonRpcMultipart
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

PendingCommit = Literal["started"]


class FirmwareStatus(Model):
    """Firmware status of the product."""

    active_firmware_version: str = Field(
        validation_alias="activeFirmwareVersion", serialization_alias="activeFirmwareVersion"
    )
    """Current firmware version."""
    active_firmware_part: str = Field(validation_alias="activeFirmwarePart", serialization_alias="activeFirmwarePart")
    """Current firmware part number."""
    inactive_firmware_version: str | None = Field(
        default=None, validation_alias="inactiveFirmwareVersion", serialization_alias="inactiveFirmwareVersion"
    )
    """Inactive firmware version. Only present if an inactive firmware exists; UNKNOWN if it does not support the automatic rollback parameters."""
    is_committed: bool | None = Field(default=None, validation_alias="isCommited", serialization_alias="isCommited")
    """True if the current firmware is committed; false if it is uncommitted and will roll back on reboot. Only present if an inactive firmware exists. (Spelled isCommited on the wire.)"""
    pending_commit: PendingCommit | None = Field(
        default=None, validation_alias="pendingCommit", serialization_alias="pendingCommit"
    )
    """Pending automatic commit. Only present if the active firmware is uncommitted and an automatic commit is pending."""
    time_to_rollback: int | None = Field(
        default=None, validation_alias="timeToRollback", serialization_alias="timeToRollback"
    )
    """Seconds left to the automatic rollback. Only present if the active firmware is uncommitted and an automatic rollback is pending."""
    last_upgrade_at: str | None = Field(
        default=None, validation_alias="lastUpgradeAt", serialization_alias="lastUpgradeAt"
    )
    """Date and time of the upgrade. Only present if an inactive firmware exists."""


class FirmwareVersion(Model):
    firmware_version: str = Field(validation_alias="firmwareVersion", serialization_alias="firmwareVersion")
    """The firmware version."""


UpgradeFactoryDefaultMode = Literal["none", "soft", "hard"]
AutoCommit = Literal["never", "boot", "started", "default"]


class UpgradeRequest(Model):
    """Arguments of ``upgrade``. The request is multipart: the JSON message (the options below) first, then the firmware file."""

    file: UploadSource = Field(exclude=True, repr=False)
    """The firmware image (.bin)."""
    factory_default_mode: UpgradeFactoryDefaultMode | None = Field(
        default=None, validation_alias="factoryDefaultMode", serialization_alias="factoryDefaultMode"
    )
    auto_commit: AutoCommit | None = Field(
        default=None, validation_alias="autoCommit", serialization_alias="autoCommit"
    )
    auto_rollback: str | None = Field(
        default=None,
        validation_alias="autoRollback",
        serialization_alias="autoRollback",
        pattern="^(never|default|[0-9]+)$",
    )
    """When the new firmware is rolled back automatically. never: no automatic rollback (a rollback still happens on a major fault or power loss before commit). A number: minutes after boot until the rollback unless committed. default: never unless autoCommit is also default, then a rollback after 10 minutes. Ignored if the new firmware does not support automatic rollback."""


FactoryDefaultMode = Literal["soft", "hard"]


class FactoryDefaultRequest(Model):
    factory_default_mode: FactoryDefaultMode | None = Field(
        default=None, validation_alias="factoryDefaultMode", serialization_alias="factoryDefaultMode"
    )


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/firmwaremanagement.cgi"

INFO = ApiInfo(
    id="firmware-management",
    name="Firmware management API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("fwmgr"),),
    docs=("https://developer.axis.com/vapix/network-video/firmware-management-api/",),
    errors={
        400: ErrorCode("Message could not be parsed or contains unknown parameters or values.", "invalid_argument"),
        405: ErrorCode("Unknown method in request.", "unsupported"),
        417: ErrorCode("API version not compatible.", "unsupported"),
        423: ErrorCode("System is busy with another firmware management request.", "unavailable"),
        500: ErrorCode("Unexpected internal error.", "internal"),
    },
)


class OPS:
    status = Operation(
        INFO, "status", JsonRpcBinding("status", PATH), result=FirmwareStatus, access="admin", effect="read"
    )
    upgrade = Operation(
        INFO,
        "upgrade",
        JsonRpcBinding(
            "upgrade",
            PATH,
            multipart=JsonRpcMultipart(
                json_part="json",
                uploads=(
                    UploadSpec("file", part="file", filename="firmware.bin", content_type="application/octet-stream"),
                ),
            ),
        ),
        params=UpgradeRequest,
        result=FirmwareVersion,
        access="admin",
        effect="action",
        errors={
            409: ErrorCode("Upgrade without factory default not allowed to an older firmware version.", "unsupported"),
            410: ErrorCode("Upgrade failed due to firmware version revoked.", "unsupported"),
            412: ErrorCode("Upgrade not allowed due to active firmware is uncommitted.", "unavailable"),
            415: ErrorCode("Upgrade failed due to invalid image.", "invalid_argument"),
            421: ErrorCode("Upgrade failed due to image not matching device.", "invalid_argument"),
            422: ErrorCode("Upgrade failed due to image missing a mandatory digital signature.", "invalid_argument"),
            424: ErrorCode(
                "Upgrade failed due to image referencing an unknown custom firmware certificate.", "invalid_argument"
            ),
        },
    )
    commit = Operation(
        INFO, "commit", JsonRpcBinding("commit", PATH), result=FirmwareVersion, access="admin", effect="action"
    )
    rollback = Operation(
        INFO,
        "rollback",
        JsonRpcBinding("rollback", PATH),
        access="admin",
        effect="action",
        errors={404: ErrorCode("No old firmware exists to rollback to.", "not_found")},
    )
    purge = Operation(
        INFO,
        "purge",
        JsonRpcBinding("purge", PATH),
        access="admin",
        effect="action",
        errors={412: ErrorCode("Active firmware is not committed.", "unavailable")},
    )
    factory_default = Operation(
        INFO,
        "factory_default",
        JsonRpcBinding("factoryDefault", PATH),
        params=FactoryDefaultRequest,
        access="admin",
        effect="action",
    )
    stop_auto = Operation(INFO, "stop_auto", JsonRpcBinding("stopAuto", PATH), access="admin", effect="action")
    reboot = Operation(INFO, "reboot", JsonRpcBinding("reboot", PATH), access="admin", effect="action")


# ---------------------------------------------------------------------------
# API classes


class FirmwareManagementApi(SyncApi):
    """Firmware management API (``firmware-management``, version 1)."""

    INFO = INFO

    def status(self, *, request_options: RequestOptions | None = None) -> FirmwareStatus:
        """Retrieve the firmware status of the product. Access: admin."""
        return self._run(OPS.status, None, {}, request_options)

    def upgrade(
        self,
        *,
        file: UploadSource,
        factory_default_mode: UpgradeFactoryDefaultMode | MISSING = MISSING,
        auto_commit: AutoCommit | MISSING = MISSING,
        auto_rollback: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FirmwareVersion:
        """Upgrade the firmware; the product reboots as part of this method.

        Only allowed if the current firmware is committed. Any inactive firmware is purged when an upgrade
        starts, even if the upgrade fails, so a rollback to it is no longer possible. Downgrading requires
        factoryDefaultMode hard. The request is multipart: the JSON message in the first part, the firmware
        image (.bin) in the second.

        Access: admin.
        """
        return self._run(
            OPS.upgrade,
            None,
            {
                "file": file,
                "factory_default_mode": factory_default_mode,
                "auto_commit": auto_commit,
                "auto_rollback": auto_rollback,
            },
            request_options,
        )

    def commit(self, *, request_options: RequestOptions | None = None) -> FirmwareVersion:
        """Commit the current firmware and stop a pending automatic rollback.

        Does nothing if the firmware is already committed.

        Access: admin.
        """
        return self._run(OPS.commit, None, {}, request_options)

    def rollback(self, *, request_options: RequestOptions | None = None) -> None:
        """Roll back the firmware and configuration to the state before the most recent upgrade; the product reboots.

        Only the most recent upgrade can be rolled back; applications and their data are not rolled back.
        Works whether or not the active firmware is committed. Not available after a purge or a factory
        default.

        Access: admin.
        """
        self._run(OPS.rollback, None, {}, request_options)

    def purge(self, *, request_options: RequestOptions | None = None) -> None:
        """Purge the previous firmware to prevent a rollback.

        Only possible when the current firmware is committed and no upgrade is in progress. A rollback is no
        longer possible afterwards.

        Access: admin.
        """
        self._run(OPS.purge, None, {}, request_options)

    def factory_default(
        self,
        *,
        factory_default_mode: FactoryDefaultMode | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Reset the parameters to factory defaults; the product reboots.

        Applications and ACAPs are removed or restored to pre-installed versions. If the current firmware is
        committed, any inactive or pending firmware is purged. If it is not committed and no automatic
        rollback is pending, the current firmware is committed and the inactive firmware purged. Replaces
        factorydefault.cgi and hardfactorydefault.cgi.

        Access: admin.
        """
        self._run(OPS.factory_default, None, {"factory_default_mode": factory_default_mode}, request_options)

    def stop_auto(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop the pending automatic rollback timer.

        Does not commit the firmware.

        Access: admin.
        """
        self._run(OPS.stop_auto, None, {}, request_options)

    def reboot(self, *, request_options: RequestOptions | None = None) -> None:
        """Reboot using the active firmware.

        The firmware does not roll back even if it is uncommitted; a pending automatic rollback stays
        pending. Replaces restart.cgi.

        Access: admin.
        """
        self._run(OPS.reboot, None, {}, request_options)


class AsyncFirmwareManagementApi(AsyncApi):
    """Firmware management API (``firmware-management``, version 1)."""

    INFO = INFO

    async def status(self, *, request_options: RequestOptions | None = None) -> FirmwareStatus:
        """Retrieve the firmware status of the product. Access: admin."""
        return await self._run(OPS.status, None, {}, request_options)

    async def upgrade(
        self,
        *,
        file: UploadSource,
        factory_default_mode: UpgradeFactoryDefaultMode | MISSING = MISSING,
        auto_commit: AutoCommit | MISSING = MISSING,
        auto_rollback: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FirmwareVersion:
        """Upgrade the firmware; the product reboots as part of this method.

        Only allowed if the current firmware is committed. Any inactive firmware is purged when an upgrade
        starts, even if the upgrade fails, so a rollback to it is no longer possible. Downgrading requires
        factoryDefaultMode hard. The request is multipart: the JSON message in the first part, the firmware
        image (.bin) in the second.

        Access: admin.
        """
        return await self._run(
            OPS.upgrade,
            None,
            {
                "file": file,
                "factory_default_mode": factory_default_mode,
                "auto_commit": auto_commit,
                "auto_rollback": auto_rollback,
            },
            request_options,
        )

    async def commit(self, *, request_options: RequestOptions | None = None) -> FirmwareVersion:
        """Commit the current firmware and stop a pending automatic rollback.

        Does nothing if the firmware is already committed.

        Access: admin.
        """
        return await self._run(OPS.commit, None, {}, request_options)

    async def rollback(self, *, request_options: RequestOptions | None = None) -> None:
        """Roll back the firmware and configuration to the state before the most recent upgrade; the product reboots.

        Only the most recent upgrade can be rolled back; applications and their data are not rolled back.
        Works whether or not the active firmware is committed. Not available after a purge or a factory
        default.

        Access: admin.
        """
        await self._run(OPS.rollback, None, {}, request_options)

    async def purge(self, *, request_options: RequestOptions | None = None) -> None:
        """Purge the previous firmware to prevent a rollback.

        Only possible when the current firmware is committed and no upgrade is in progress. A rollback is no
        longer possible afterwards.

        Access: admin.
        """
        await self._run(OPS.purge, None, {}, request_options)

    async def factory_default(
        self,
        *,
        factory_default_mode: FactoryDefaultMode | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Reset the parameters to factory defaults; the product reboots.

        Applications and ACAPs are removed or restored to pre-installed versions. If the current firmware is
        committed, any inactive or pending firmware is purged. If it is not committed and no automatic
        rollback is pending, the current firmware is committed and the inactive firmware purged. Replaces
        factorydefault.cgi and hardfactorydefault.cgi.

        Access: admin.
        """
        await self._run(OPS.factory_default, None, {"factory_default_mode": factory_default_mode}, request_options)

    async def stop_auto(self, *, request_options: RequestOptions | None = None) -> None:
        """Stop the pending automatic rollback timer.

        Does not commit the firmware.

        Access: admin.
        """
        await self._run(OPS.stop_auto, None, {}, request_options)

    async def reboot(self, *, request_options: RequestOptions | None = None) -> None:
        """Reboot using the active firmware.

        The firmware does not roll back even if it is uncommitted; a pending automatic rollback stays
        pending. Replaces restart.cgi.

        Access: admin.
        """
        await self._run(OPS.reboot, None, {}, request_options)
