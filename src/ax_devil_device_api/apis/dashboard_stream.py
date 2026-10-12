# GENERATED from specs/apis/device-configuration/dashboard-stream-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the air quality dashboard stream, its display language and dark mode.

Docs: https://developer.axis.com/vapix/device-configuration/environmental-sensor/dashboard-stream-api/
"""

from __future__ import annotations

from typing import Literal

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Language = Literal[
    "cs", "de", "en", "es", "fr", "it", "nl", "pl", "pt", "fi", "sv", "vi", "tr", "ru", "th", "ko", "zh", "zh-TW", "ja"
]


class DashboardStream(Model):
    """The whole API tree."""

    darkmode: bool | None = None
    """Enable or disable dark mode."""
    language: Language | None = None
    """Language display in dashboard stream."""


class SetDarkmodeRequest(Model):
    darkmode: bool
    """Enable or disable dark mode."""


class SetLanguageRequest(Model):
    language: Language
    """Language display in dashboard stream."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/dashboard-stream/v1"

INFO = ApiInfo(
    id="dashboard-stream-config",
    name="Dashboard stream API",
    family=Family.DCA,
    discovery=(DcaDiscovery("dashboard-stream", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/environmental-sensor/dashboard-stream-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=DashboardStream, access="viewer", effect="read"
    )
    get_darkmode = Operation(
        INFO, "get_darkmode", DcaBinding("GET", f"{ROOT}/darkmode"), result=bool, access="viewer", effect="read"
    )
    set_darkmode = Operation(
        INFO,
        "set_darkmode",
        DcaBinding("PATCH", f"{ROOT}/darkmode", body="value", body_field="darkmode"),
        params=SetDarkmodeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_language = Operation(
        INFO, "get_language", DcaBinding("GET", f"{ROOT}/language"), result=Language, access="viewer", effect="read"
    )
    set_language = Operation(
        INFO,
        "set_language",
        DcaBinding("PATCH", f"{ROOT}/language", body="value", body_field="language"),
        params=SetLanguageRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class DashboardStreamApi(SyncApi):
    """Dashboard stream API (``dashboard-stream-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> DashboardStream:
        """Dark mode and language of the dashboard stream. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_darkmode(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether dark mode is enabled. Access: viewer."""
        return self._run(OPS.get_darkmode, None, {}, request_options)

    def set_darkmode(self, *, darkmode: bool, request_options: RequestOptions | None = None) -> None:
        """Enable or disable dark mode. Changes only the fields given. Access: admin."""
        self._run(OPS.set_darkmode, None, {"darkmode": darkmode}, request_options)

    def get_language(self, *, request_options: RequestOptions | None = None) -> Language:
        """The display language of the dashboard stream. Access: viewer."""
        return self._run(OPS.get_language, None, {}, request_options)

    def set_language(self, *, language: Language, request_options: RequestOptions | None = None) -> None:
        """Set the display language of the dashboard stream.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_language, None, {"language": language}, request_options)


class AsyncDashboardStreamApi(AsyncApi):
    """Dashboard stream API (``dashboard-stream-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> DashboardStream:
        """Dark mode and language of the dashboard stream. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_darkmode(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether dark mode is enabled. Access: viewer."""
        return await self._run(OPS.get_darkmode, None, {}, request_options)

    async def set_darkmode(self, *, darkmode: bool, request_options: RequestOptions | None = None) -> None:
        """Enable or disable dark mode. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_darkmode, None, {"darkmode": darkmode}, request_options)

    async def get_language(self, *, request_options: RequestOptions | None = None) -> Language:
        """The display language of the dashboard stream. Access: viewer."""
        return await self._run(OPS.get_language, None, {}, request_options)

    async def set_language(self, *, language: Language, request_options: RequestOptions | None = None) -> None:
        """Set the display language of the dashboard stream.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_language, None, {"language": language}, request_options)
