# GENERATED from specs/apis/device-configuration/event-schedules-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage pulse and interval schedules that make the event system send scheduled events.

Docs: https://developer.axis.com/vapix/device-configuration/event-schedules-api/
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ScheduleVariant = Literal["PULSE", "INTERVAL"]


class Schedule(Model):
    """Schedules"""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"schedule_type"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"schedule_type"})
    id: str
    """Unique identifier for a schedule. Automatically generated if not provided during add."""
    name: str
    """Well-known name of the schedule."""
    schedule: str
    """Schedule definition, based on the iCalendar format (DTSTART, optional DTEND, RRULE). The schedule type follows from DTEND."""
    schedule_type: ScheduleVariant = Field(
        default_factory=not_sent, validation_alias="scheduleType", serialization_alias="scheduleType"
    )
    """Type of schedule, either 'Pulse' or 'Interval'. Determined by the schedule definition."""


class EventSchedules(Model):
    """The whole API tree."""

    schedules: list[Schedule] | None = None


class UpdateScheduleRequest(Model):
    """Arguments of ``update_schedule``."""

    id: str
    """Identifier of the schedule to update."""
    name: str | None = None
    """Well-known name of the schedule."""
    schedule: str | None = None
    """Schedule definition, based on the iCalendar format."""


class AddScheduleRequest(Model):
    """Arguments of ``add_schedule``."""

    name: str
    """Well-known name of the schedule."""
    schedule: str
    """Schedule definition, based on the iCalendar format."""
    id: str | None = None
    """Unique identifier for a schedule. Automatically generated if not provided during add."""


class ScheduleIdRequest(Model):
    id: str
    """Identifier of the schedule."""


class SetScheduleNameRequest(Model):
    id: str
    """Identifier of the schedule."""
    name: str
    """Well-known name of the schedule."""


class SetScheduleScheduleRequest(Model):
    id: str
    """Identifier of the schedule."""
    schedule: str
    """Schedule definition, based on the iCalendar format."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/event-schedules/v2"

INFO = ApiInfo(
    id="event-schedules-config",
    name="Event schedules API",
    family=Family.DCA,
    discovery=(DcaDiscovery("event-schedules", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/event-schedules-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=EventSchedules, access="viewer", effect="read")
    list_schedules = Operation(
        INFO,
        "list_schedules",
        DcaBinding("GET", f"{ROOT}/schedules"),
        result=list[Schedule],
        access="viewer",
        effect="read",
    )
    get_schedule = Operation(
        INFO,
        "get_schedule",
        DcaBinding("GET", f"{ROOT}/schedules/{{id}}"),
        params=ScheduleIdRequest,
        result=Schedule,
        access="viewer",
        effect="read",
    )
    update_schedule = Operation(
        INFO,
        "update_schedule",
        DcaBinding("PATCH", f"{ROOT}/schedules/{{id}}", body="object"),
        params=UpdateScheduleRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    add_schedule = Operation(
        INFO,
        "add_schedule",
        DcaBinding("POST", f"{ROOT}/schedules", body="object"),
        params=AddScheduleRequest,
        result=Schedule,
        access="admin",
        effect="write",
        write="create",
    )
    remove_schedule = Operation(
        INFO,
        "remove_schedule",
        DcaBinding("DELETE", f"{ROOT}/schedules/{{id}}"),
        params=ScheduleIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_schedule_name = Operation(
        INFO,
        "set_schedule_name",
        DcaBinding("PATCH", f"{ROOT}/schedules/{{id}}/name", body="value", body_field="name"),
        params=SetScheduleNameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_schedule_schedule = Operation(
        INFO,
        "set_schedule_schedule",
        DcaBinding("PATCH", f"{ROOT}/schedules/{{id}}/schedule", body="value", body_field="schedule"),
        params=SetScheduleScheduleRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class EventSchedulesApi(SyncApi):
    """Event schedules API (``event-schedules-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> EventSchedules:
        """All data of the Event schedules API. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_schedules(self, *, request_options: RequestOptions | None = None) -> list[Schedule]:
        """List the schedules. Access: viewer."""
        return self._run(OPS.list_schedules, None, {}, request_options)

    def get_schedule(self, id: str, *, request_options: RequestOptions | None = None) -> Schedule:
        """Get one schedule. Access: viewer."""
        return self._run(OPS.get_schedule, None, {"id": id}, request_options)

    def update_schedule(
        self,
        id: str,
        *,
        name: str | MISSING = MISSING,
        schedule: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update a schedule. Changes only the fields given. Access: admin."""
        self._run(OPS.update_schedule, None, {"id": id, "name": name, "schedule": schedule}, request_options)

    def add_schedule(
        self, *, name: str, schedule: str, id: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Schedule:
        """Add a schedule. The device generates the id unless one is given. Access: admin."""
        return self._run(OPS.add_schedule, None, {"name": name, "schedule": schedule, "id": id}, request_options)

    def remove_schedule(self, id: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a schedule. Access: admin."""
        self._run(OPS.remove_schedule, None, {"id": id}, request_options)

    def set_schedule_name(self, id: str, *, name: str, request_options: RequestOptions | None = None) -> None:
        """Set the name of a schedule. Changes only the fields given. Access: admin."""
        self._run(OPS.set_schedule_name, None, {"id": id, "name": name}, request_options)

    def set_schedule_schedule(self, id: str, *, schedule: str, request_options: RequestOptions | None = None) -> None:
        """Set the definition (iCalendar text) of a schedule.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_schedule_schedule, None, {"id": id, "schedule": schedule}, request_options)


class AsyncEventSchedulesApi(AsyncApi):
    """Event schedules API (``event-schedules-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> EventSchedules:
        """All data of the Event schedules API. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_schedules(self, *, request_options: RequestOptions | None = None) -> list[Schedule]:
        """List the schedules. Access: viewer."""
        return await self._run(OPS.list_schedules, None, {}, request_options)

    async def get_schedule(self, id: str, *, request_options: RequestOptions | None = None) -> Schedule:
        """Get one schedule. Access: viewer."""
        return await self._run(OPS.get_schedule, None, {"id": id}, request_options)

    async def update_schedule(
        self,
        id: str,
        *,
        name: str | MISSING = MISSING,
        schedule: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update a schedule. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_schedule, None, {"id": id, "name": name, "schedule": schedule}, request_options)

    async def add_schedule(
        self, *, name: str, schedule: str, id: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Schedule:
        """Add a schedule. The device generates the id unless one is given. Access: admin."""
        return await self._run(OPS.add_schedule, None, {"name": name, "schedule": schedule, "id": id}, request_options)

    async def remove_schedule(self, id: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove a schedule. Access: admin."""
        await self._run(OPS.remove_schedule, None, {"id": id}, request_options)

    async def set_schedule_name(self, id: str, *, name: str, request_options: RequestOptions | None = None) -> None:
        """Set the name of a schedule. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_schedule_name, None, {"id": id, "name": name}, request_options)

    async def set_schedule_schedule(
        self, id: str, *, schedule: str, request_options: RequestOptions | None = None
    ) -> None:
        """Set the definition (iCalendar text) of a schedule.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_schedule_schedule, None, {"id": id, "schedule": schedule}, request_options)
