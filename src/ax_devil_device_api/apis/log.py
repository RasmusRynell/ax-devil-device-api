# GENERATED from specs/apis/device-configuration/log-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Turn persistent log storage on and off, clear the persistent log and write messages into the system log.

Docs: https://developer.axis.com/vapix/device-configuration/log-api/
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

LogMsg = Annotated[str, Field(min_length=0, max_length=4096)]
LogSeverity = Annotated[int, Field(ge=0, le=7)]


class WriteMessageRequest(Model):
    """The message to be logged, it contains the severity level of the message and the message itself."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"severity"})
    msg: LogMsg
    """Text that provides information of the event"""
    severity: LogSeverity | None = None
    """Severity level of this message, default value is 6 meaning "Informational" level"""


class Persistent(Model):
    """Status of saving logs to the persistent storage"""

    enabled: bool
    """Whether it is enabled to save logs to the persistent storage. enabled is a property in the log.v1.persistent entity that is able to switch the log saving to the persistent storage on and off."""


class Log(Model):
    """The whole API tree."""

    persistent: Persistent | None = None


class SetPersistentEnabledRequest(Model):
    enabled: bool
    """Whether it is enabled to save logs to the persistent storage. enabled is a property in the log.v1.persistent entity that is able to switch the log saving to the persistent storage on and off."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/log/v1"

INFO = ApiInfo(
    id="log-config",
    name="Log API",
    family=Family.DCA,
    discovery=(DcaDiscovery("log", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/log-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Log, access="viewer", effect="read")
    write_message = Operation(
        INFO,
        "write_message",
        DcaBinding("POST", f"{ROOT}/writeMessage", body="object"),
        params=WriteMessageRequest,
        access="admin",
        effect="action",
    )
    get_persistent = Operation(
        INFO,
        "get_persistent",
        DcaBinding("GET", f"{ROOT}/persistent"),
        result=Persistent,
        access="viewer",
        effect="read",
    )
    get_persistent_enabled = Operation(
        INFO,
        "get_persistent_enabled",
        DcaBinding("GET", f"{ROOT}/persistent/enabled"),
        result=bool,
        access="viewer",
        effect="read",
    )
    set_persistent_enabled = Operation(
        INFO,
        "set_persistent_enabled",
        DcaBinding("PATCH", f"{ROOT}/persistent/enabled", body="value", body_field="enabled"),
        params=SetPersistentEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    clear_log = Operation(
        INFO,
        "clear_log",
        DcaBinding("POST", f"{ROOT}/persistent/clearLog", body="object"),
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class LogApi(SyncApi):
    """Log API (``log-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Log:
        """All data of the Log API. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    def write_message(
        self,
        *,
        msg: LogMsg,
        severity: LogSeverity | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Write a log message to the system log with the given severity.

        Avoid writing many large messages in a short time; that can overflow the storage.

        Access: admin.
        """
        self._run(OPS.write_message, None, {"msg": msg, "severity": severity}, request_options)

    def get_persistent(self, *, request_options: RequestOptions | None = None) -> Persistent:
        """Get the persistent log storage status. Access: viewer."""
        return self._run(OPS.get_persistent, None, {}, request_options)

    def get_persistent_enabled(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether logs are saved to the persistent storage. Access: viewer."""
        return self._run(OPS.get_persistent_enabled, None, {}, request_options)

    def set_persistent_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn saving of logs to the persistent storage on or off. The persistent storage fills up while it is on; clear it with clear_log.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_persistent_enabled, None, {"enabled": enabled}, request_options)

    def clear_log(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear log file storing all logs. Access: admin."""
        self._run(OPS.clear_log, None, {}, request_options)


class AsyncLogApi(AsyncApi):
    """Log API (``log-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Log:
        """All data of the Log API. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def write_message(
        self,
        *,
        msg: LogMsg,
        severity: LogSeverity | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Write a log message to the system log with the given severity.

        Avoid writing many large messages in a short time; that can overflow the storage.

        Access: admin.
        """
        await self._run(OPS.write_message, None, {"msg": msg, "severity": severity}, request_options)

    async def get_persistent(self, *, request_options: RequestOptions | None = None) -> Persistent:
        """Get the persistent log storage status. Access: viewer."""
        return await self._run(OPS.get_persistent, None, {}, request_options)

    async def get_persistent_enabled(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether logs are saved to the persistent storage. Access: viewer."""
        return await self._run(OPS.get_persistent_enabled, None, {}, request_options)

    async def set_persistent_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Turn saving of logs to the persistent storage on or off. The persistent storage fills up while it is on; clear it with clear_log.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_persistent_enabled, None, {"enabled": enabled}, request_options)

    async def clear_log(self, *, request_options: RequestOptions | None = None) -> None:
        """Clear log file storing all logs. Access: admin."""
        await self._run(OPS.clear_log, None, {}, request_options)
