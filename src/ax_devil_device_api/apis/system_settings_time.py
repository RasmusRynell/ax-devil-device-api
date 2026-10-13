# GENERATED from specs/apis/network-video/system-settings-time.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Get or set the time zone and time synchronisation through the Time, Time.DST and Time.NTP parameter groups (legacy; no longer updated, see the Time API).

Docs: https://developer.axis.com/vapix/network-video/system-settings/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SetTimeSettingsRequest(Model):
    obtain_from_dhcp: bool | None = Field(
        default=None, validation_alias="Time.ObtainFromDHCP", serialization_alias="Time.ObtainFromDHCP"
    )
    """Whether local or remote NTP servers may be provided by a DHCP server. The default is yes."""
    sync_source: Literal["PC", "NTP", "None"] | None = Field(
        default=None, validation_alias="Time.SyncSource", serialization_alias="Time.SyncSource"
    )
    """The source to synchronise the time with: ``PC`` the connected PC, ``NTP`` an NTP server, ``None`` set manually. Product and release dependent."""
    posix_time_zone: str | None = Field(
        default=None, validation_alias="Time.POSIXTimeZone", serialization_alias="Time.POSIXTimeZone"
    )
    """POSIX TZ rule string (IEEE Std 1003.1-2004, chapter 8.3), with or without daylight saving time."""
    dst_enabled: bool | None = Field(
        default=None, validation_alias="Time.DST.Enabled", serialization_alias="Time.DST.Enabled"
    )
    """Enable or disable daylight saving time. The default is no."""
    ntp_server: str | None = Field(
        default=None, validation_alias="Time.NTP.Server", serialization_alias="Time.NTP.Server"
    )
    """The IP address or host name of the NTP server. The default is 0.0.0.0."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="system-settings-time",
    name="System date and time (param.cgi Time groups)",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    status="deprecated",
    requires_firmware="5.00",
    docs=("https://developer.axis.com/vapix/network-video/system-settings/",),
)


class OPS:
    get_time_settings = Operation(
        INFO,
        "get_time_settings",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"), ("group", "Time")),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        result=dict[str, str],
        access="admin",
        effect="read",
    )
    set_time_settings = Operation(
        INFO,
        "set_time_settings",
        CgiBinding(
            PATH,
            fixed_query=(("action", "update"),),
            args=(
                CgiArg("obtain_from_dhcp", wire="Time.ObtainFromDHCP", style="axis_bool"),
                CgiArg("sync_source", wire="Time.SyncSource"),
                CgiArg("posix_time_zone", wire="Time.POSIXTimeZone"),
                CgiArg("dst_enabled", wire="Time.DST.Enabled", style="axis_bool"),
                CgiArg("ntp_server", wire="Time.NTP.Server"),
            ),
            reply=TextOk(),
        ),
        params=SetTimeSettingsRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SystemSettingsTimeApi(SyncApi):
    """System date and time (param.cgi Time groups) (``system-settings-time``)."""

    INFO = INFO

    def get_time_settings(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the Time, Time.DST and Time.NTP parameters as ``{"Time.POSIXTimeZone": "GMT0BST,M3.5.0/1,M10.5.0"}``.

        Operators can read only ``Time.POSIXTimeZone`` and ``Time.DST.Enabled``.

        Access: admin.
        """
        return self._run(OPS.get_time_settings, None, {}, request_options)

    @overload
    def set_time_settings(
        self, request: SetTimeSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_time_settings(
        self,
        /,
        *,
        obtain_from_dhcp: bool | MISSING = MISSING,
        sync_source: Literal["PC", "NTP", "None"] | MISSING = MISSING,
        posix_time_zone: str | MISSING = MISSING,
        dst_enabled: bool | MISSING = MISSING,
        ntp_server: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_time_settings(
        self,
        request: SetTimeSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the time zone and how the time is synchronised.

        Only the given parameters change. ``posix_time_zone`` is a POSIX TZ rule string
        ``<name><offset>[<dst name>[<dst offset>[,<start rule>,<stop rule>]]]``, for example
        ``GMT0BST,M3.5.0/1,M10.5.0`` (standard time ``GMT``, daylight saving time ``BST`` one hour ahead,
        from the last Sunday in March 01:00 to the last Sunday in October 02:00). A name is 3 to 6
        characters. The ``:`` prefixed format is not allowed.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_time_settings, request, kwargs, request_options)


class AsyncSystemSettingsTimeApi(AsyncApi):
    """System date and time (param.cgi Time groups) (``system-settings-time``)."""

    INFO = INFO

    async def get_time_settings(self, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read the Time, Time.DST and Time.NTP parameters as ``{"Time.POSIXTimeZone": "GMT0BST,M3.5.0/1,M10.5.0"}``.

        Operators can read only ``Time.POSIXTimeZone`` and ``Time.DST.Enabled``.

        Access: admin.
        """
        return await self._run(OPS.get_time_settings, None, {}, request_options)

    @overload
    async def set_time_settings(
        self, request: SetTimeSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_time_settings(
        self,
        /,
        *,
        obtain_from_dhcp: bool | MISSING = MISSING,
        sync_source: Literal["PC", "NTP", "None"] | MISSING = MISSING,
        posix_time_zone: str | MISSING = MISSING,
        dst_enabled: bool | MISSING = MISSING,
        ntp_server: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_time_settings(
        self,
        request: SetTimeSettingsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the time zone and how the time is synchronised.

        Only the given parameters change. ``posix_time_zone`` is a POSIX TZ rule string
        ``<name><offset>[<dst name>[<dst offset>[,<start rule>,<stop rule>]]]``, for example
        ``GMT0BST,M3.5.0/1,M10.5.0`` (standard time ``GMT``, daylight saving time ``BST`` one hour ahead,
        from the last Sunday in March 01:00 to the last Sunday in October 02:00). A name is 3 to 6
        characters. The ``:`` prefixed format is not allowed.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_time_settings, request, kwargs, request_options)
