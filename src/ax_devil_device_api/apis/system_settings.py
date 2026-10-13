# GENERATED from specs/apis/network-video/system-settings.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Legacy system maintenance CGIs - factory default, hard factory default, restart, server report and the system and access logs.

Docs: https://developer.axis.com/vapix/network-video/system-settings/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._http.upload import UploadSource, UploadSpec
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import Binary, CgiArg, CgiBinding, Text
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ServerReportRequest(Model):
    mode: Literal["tar_all", "text", "zip", "zip_with_image"] | None = None
    """The server report presentation mode. ``tar_all``: all log files (system log, access log, audit log, etc) as a .tar file; ``text``: the report as text; ``zip``: the report as a .zip file; ``zip_with_image``: the report together with a snapshot image taken using the Image Appearance settings as a single .zip file. ``zip_with_image`` and ``tar_all`` are only available on products with application support. Default: 'text'."""


class SystemLogRequest(Model):
    text: str | None = Field(default=None, pattern="^[A-Za-z0-9]+$")
    """Only log entries that contain this text are returned. Available on AXIS OS 11.11.45 and later."""


class FirmwareUpgradeRequest(Model):
    firmware: UploadSource = Field(exclude=True, repr=False)
    """The AXIS OS file, as bytes, a Path or an Upload(stream, size)."""
    type: Literal["normal", "factorydefault"] | None = None
    """The upgrade type: normal (restore old settings) or factorydefault (all parameters set to defaults). Default: 'normal'."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/factorydefault.cgi"

INFO = ApiInfo(
    id="system-settings",
    name="System settings",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    docs=("https://developer.axis.com/vapix/network-video/system-settings/",),
)


class OPS:
    factory_default = Operation(
        INFO, "factory_default", CgiBinding(PATH, reply=Text()), access="admin", effect="action"
    )
    hard_factory_default = Operation(
        INFO,
        "hard_factory_default",
        CgiBinding("/axis-cgi/hardfactorydefault.cgi", reply=Text()),
        access="admin",
        effect="action",
    )
    restart = Operation(
        INFO, "restart", CgiBinding("/axis-cgi/restart.cgi", reply=Text()), access="admin", effect="action"
    )
    server_report = Operation(
        INFO,
        "server_report",
        CgiBinding("/axis-cgi/serverreport.cgi", args=(CgiArg("mode"),), reply=Binary()),
        params=ServerReportRequest,
        result=bytes,
        access="admin",
        effect="read",
    )
    system_log = Operation(
        INFO,
        "system_log",
        CgiBinding("/axis-cgi/systemlog.cgi", args=(CgiArg("text"),), reply=Text()),
        params=SystemLogRequest,
        result=str,
        access="admin",
        effect="read",
    )
    access_log = Operation(
        INFO,
        "access_log",
        CgiBinding("/axis-cgi/accesslog.cgi", reply=Text()),
        result=str,
        access="admin",
        effect="read",
    )
    firmware_upgrade = Operation(
        INFO,
        "firmware_upgrade",
        CgiBinding(
            "/axis-cgi/firmwareupgrade.cgi",
            method="POST",
            encoding="multipart",
            args=(CgiArg("type", place="query"),),
            uploads=(UploadSpec("firmware", part="file", content_type="application/octet-stream"),),
            reply=Text(),
        ),
        params=FirmwareUpgradeRequest,
        result=str,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class SystemSettingsApi(SyncApi):
    """System settings (``system-settings``)."""

    INFO = INFO

    def factory_default(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset to factory default except network/IP settings, system time and IEEE 802.1X; the product restarts.

        All settings are set to their factory default values except the boot protocol
        (``Network.BootProto``), the static IP address (``Network.IPAddress``), the default router
        (``Network.DefaultRouter``), the subnet mask (``Network.SubnetMask``), the broadcast IP address
        (``Network.Broadcast``), the system time and the IEEE 802.1X settings. Since these are not reset the
        product can be accessed on the same address (important with NAT routers). The product is restarted.
        Superseded by ``factoryDefault`` in the Firmware management API.

        Access: admin.
        """
        self._run(OPS.factory_default, None, {}, request_options)

    def hard_factory_default(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset all settings, including the IP addresses, to factory default; the product restarts.

        Superseded by ``factoryDefault`` in the Firmware management API.

        Access: admin.
        """
        self._run(OPS.hard_factory_default, None, {}, request_options)

    def restart(self, *, request_options: RequestOptions | None = None) -> None:
        """Restart the Axis product.

        Superseded by ``reboot`` in the Firmware management API.

        Access: admin.
        """
        self._run(OPS.restart, None, {}, request_options)

    def server_report(
        self,
        *,
        mode: Literal["tar_all", "text", "zip", "zip_with_image"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes:
        """Generate and return a server report (product information, parameter settings and system logs) as bytes.

        Useful as input when requesting support. The body is text for ``mode=text`` (the default), and a
        ``.zip`` or ``.tar`` file for the other modes.

        Access: admin.
        """
        return self._run(OPS.server_report, None, {"mode": mode}, request_options)

    def system_log(self, *, text: str | MISSING = MISSING, request_options: RequestOptions | None = None) -> str:
        """Retrieve the system log (the level of detail is set by the ``Log.System`` group).

        Access: admin.
        """
        return self._run(OPS.system_log, None, {"text": text}, request_options)

    def access_log(self, *, request_options: RequestOptions | None = None) -> str:
        """Retrieve the client access log (the level of detail is set by the ``Log.Access`` group).

        Access: admin.
        """
        return self._run(OPS.access_log, None, {}, request_options)

    def firmware_upgrade(
        self,
        firmware: UploadSource,
        *,
        type: Literal["normal", "factorydefault"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Upgrade the AXIS OS from an uploaded firmware file; the product restarts automatically.

        Superseded by ``upgrade`` in the Firmware management API. ``type=normal`` upgrades and restores the
        old settings, ``factorydefault`` sets all parameters to their default values. The docs do not show a
        success reply.

        Access: admin.
        """
        return self._run(OPS.firmware_upgrade, None, {"firmware": firmware, "type": type}, request_options)


class AsyncSystemSettingsApi(AsyncApi):
    """System settings (``system-settings``)."""

    INFO = INFO

    async def factory_default(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset to factory default except network/IP settings, system time and IEEE 802.1X; the product restarts.

        All settings are set to their factory default values except the boot protocol
        (``Network.BootProto``), the static IP address (``Network.IPAddress``), the default router
        (``Network.DefaultRouter``), the subnet mask (``Network.SubnetMask``), the broadcast IP address
        (``Network.Broadcast``), the system time and the IEEE 802.1X settings. Since these are not reset the
        product can be accessed on the same address (important with NAT routers). The product is restarted.
        Superseded by ``factoryDefault`` in the Firmware management API.

        Access: admin.
        """
        await self._run(OPS.factory_default, None, {}, request_options)

    async def hard_factory_default(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset all settings, including the IP addresses, to factory default; the product restarts.

        Superseded by ``factoryDefault`` in the Firmware management API.

        Access: admin.
        """
        await self._run(OPS.hard_factory_default, None, {}, request_options)

    async def restart(self, *, request_options: RequestOptions | None = None) -> None:
        """Restart the Axis product.

        Superseded by ``reboot`` in the Firmware management API.

        Access: admin.
        """
        await self._run(OPS.restart, None, {}, request_options)

    async def server_report(
        self,
        *,
        mode: Literal["tar_all", "text", "zip", "zip_with_image"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> bytes:
        """Generate and return a server report (product information, parameter settings and system logs) as bytes.

        Useful as input when requesting support. The body is text for ``mode=text`` (the default), and a
        ``.zip`` or ``.tar`` file for the other modes.

        Access: admin.
        """
        return await self._run(OPS.server_report, None, {"mode": mode}, request_options)

    async def system_log(self, *, text: str | MISSING = MISSING, request_options: RequestOptions | None = None) -> str:
        """Retrieve the system log (the level of detail is set by the ``Log.System`` group).

        Access: admin.
        """
        return await self._run(OPS.system_log, None, {"text": text}, request_options)

    async def access_log(self, *, request_options: RequestOptions | None = None) -> str:
        """Retrieve the client access log (the level of detail is set by the ``Log.Access`` group).

        Access: admin.
        """
        return await self._run(OPS.access_log, None, {}, request_options)

    async def firmware_upgrade(
        self,
        firmware: UploadSource,
        *,
        type: Literal["normal", "factorydefault"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Upgrade the AXIS OS from an uploaded firmware file; the product restarts automatically.

        Superseded by ``upgrade`` in the Firmware management API. ``type=normal`` upgrades and restores the
        old settings, ``factorydefault`` sets all parameters to their default values. The docs do not show a
        success reply.

        Access: admin.
        """
        return await self._run(OPS.firmware_upgrade, None, {"firmware": firmware, "type": type}, request_options)
