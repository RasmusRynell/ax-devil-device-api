# GENERATED from specs/apis/physical-access-control/schedule-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The Schedule service manages schedules for use by other services.

Docs: https://developer.axis.com/vapix/physical-access-control/schedule-service/
"""

from __future__ import annotations

from typing import Any, ClassVar, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ReferenceToken = str


class ServiceCapabilities(Model):
    """What the schedule service supports."""

    component: Any | None = Field(default=None, validation_alias="Component", serialization_alias="Component")
    """The iCalendar components supported; `VEVENT` must be supported. The docs do not give the encoding (string or list)."""
    set_schedule: bool | None = Field(default=None, validation_alias="SetSchedule", serialization_alias="SetSchedule")
    """If the SetSchedule operation is supported."""
    get_schedule: bool | None = Field(default=None, validation_alias="GetSchedule", serialization_alias="GetSchedule")
    """If the GetSchedule operation is supported."""
    remove_schedule: bool | None = Field(
        default=None, validation_alias="RemoveSchedule", serialization_alias="RemoveSchedule"
    )
    """If the RemoveSchedule operation is supported."""
    schedule_active: bool | None = Field(
        default=None, validation_alias="ScheduleActive", serialization_alias="ScheduleActive"
    )
    """If the ScheduleActive operation is supported."""
    event_support: bool | None = Field(
        default=None, validation_alias="EventSupport", serialization_alias="EventSupport"
    )
    """If the service supports sending events."""


class Attribute(Model):
    """A typed name and value pair."""

    type: str | None = None
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")


class ScheduleInfo(Model):
    """Summary of a schedule."""

    token: ReferenceToken
    """A service-unique identifier of the schedule."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Short name of the schedule."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Detailed description of the schedule."""


class Schedule(Model):
    """A schedule as returned by the device. The definitions are in iCalendar syntax (RFC 5545, a subset), with only local time. A definition with a DTEND in its VEVENT is an interval schedule; one without is a pulse schedule."""

    token: ReferenceToken
    """A service-unique identifier of the schedule."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Short name of the schedule."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Detailed description of the schedule."""
    schedule_definition: str | None = Field(
        default=None, validation_alias="ScheduleDefinition", serialization_alias="ScheduleDefinition"
    )
    """When the schedule is active, in iCalendar syntax."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes of the schedule."""
    exception_schedule_definition: str | None = Field(
        default=None, validation_alias="ExceptionScheduleDefinition", serialization_alias="ExceptionScheduleDefinition"
    )
    """When the schedule is in exception, in iCalendar syntax. Exceptions are subtracted from the schedule definition, so the schedule is never active while in exception."""


class ScheduleInput(Model):
    """A schedule to add or update."""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"exception_schedule_definition"})
    token: ReferenceToken | None = None
    """Token of the schedule to update. If empty or absent the device generates a token and adds a new schedule."""
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Short name of the schedule."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Detailed description of the schedule."""
    schedule_definition: str = Field(validation_alias="ScheduleDefinition", serialization_alias="ScheduleDefinition")
    """When the schedule is active, in iCalendar syntax (VCALENDAR with VEVENT). Local time only."""
    attribute: list[Attribute] | None = Field(
        default=None, validation_alias="Attribute", serialization_alias="Attribute"
    )
    """Attributes of the schedule."""
    exception_schedule_definition: str | None = Field(
        default=None, validation_alias="ExceptionScheduleDefinition", serialization_alias="ExceptionScheduleDefinition"
    )
    """When the schedule is in exception, in iCalendar syntax."""


class ScheduleStatus(Model):
    """Status of one schedule."""

    token: ReferenceToken = Field(validation_alias="Token", serialization_alias="Token")
    """Schedule token."""
    active: bool = Field(validation_alias="Active", serialization_alias="Active")
    """Whether the schedule is active now. Never true while Exception is true."""
    exception: bool = Field(validation_alias="Exception", serialization_alias="Exception")
    """Whether the schedule is in exception now."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities of the service."""


class ListRequest(Model):
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of entries to return. If absent, or higher than the device supports, the device decides."""
    start_reference: str | None = Field(
        default=None, validation_alias="StartReference", serialization_alias="StartReference"
    )
    """Start returning entries from this reference. If absent, start from the beginning."""


class TokensRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the schedules."""


class ScheduleInfoList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    schedule_info: list[ScheduleInfo] | None = Field(
        default=None, validation_alias="ScheduleInfo", serialization_alias="ScheduleInfo"
    )


class ScheduleInfos(Model):
    schedule_info: list[ScheduleInfo] | None = Field(
        default=None, validation_alias="ScheduleInfo", serialization_alias="ScheduleInfo"
    )


class ScheduleList(Model):
    next_start_reference: str | None = Field(
        default=None, validation_alias="NextStartReference", serialization_alias="NextStartReference"
    )
    """StartReference to use in the next call to get the following items. Absent when there are no more items."""
    schedule: list[Schedule] | None = Field(default=None, validation_alias="Schedule", serialization_alias="Schedule")


class Schedules(Model):
    schedule: list[Schedule] | None = Field(default=None, validation_alias="Schedule", serialization_alias="Schedule")


class SetScheduleRequest(Model):
    schedule: list[ScheduleInput] = Field(validation_alias="Schedule", serialization_alias="Schedule", min_length=1)
    """The schedules to add or update."""


class TokenList(Model):
    token: list[ReferenceToken] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the schedules that were set."""


class ScheduleActiveRequest(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"local_time", "utc_time"})
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the schedules to check."""
    local_time: str | None = Field(default=None, validation_alias="LocalTime", serialization_alias="LocalTime")
    """Local time (xs:dateTime) to check against. If absent it is deduced from the device time zone and UtcTime if given, otherwise the device's current local time."""
    utc_time: str | None = Field(default=None, validation_alias="UtcTime", serialization_alias="UtcTime")
    """UTC time (xs:dateTime) to check against. If absent it is deduced from the device time zone and LocalTime if given, otherwise the device's current UTC time."""


class ScheduleActiveResult(Model):
    active: bool = Field(validation_alias="Active", serialization_alias="Active")
    """True if any of the schedules is active at the time and there is no exception."""
    exception: bool = Field(validation_alias="Exception", serialization_alias="Exception")
    """True if any of the schedules has an exception at the time."""


class ScheduleStatusReportResult(Model):
    status: list[ScheduleStatus] | None = Field(default=None, validation_alias="Status", serialization_alias="Status")


class ScheduleStatusReportRequest(Model):
    token: list[ReferenceToken] = Field(validation_alias="Token", serialization_alias="Token", min_length=1)
    """Tokens of the schedules to report on."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/schedule"

INFO = ApiInfo(
    id="schedule-service",
    name="Schedule service",
    family=Family.SERVICE_JSON,
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/schedule-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/event-logger-service/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
        "https://developer.axis.com/vapix/physical-access-control/system-integration-examples/",
    ),
    errors={"ter:InvalidArgs": ErrorCode("Invalid argument", "invalid_argument")},
)


class OPS:
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "axsch:GetServiceCapabilities"),
        result=GetServiceCapabilitiesResult,
        access="anonymous",
        effect="read",
    )
    get_schedule_info_list = Operation(
        INFO,
        "get_schedule_info_list",
        ServiceJsonBinding(PATH, "axsch:GetScheduleInfoList"),
        params=ListRequest,
        result=ScheduleInfoList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning.", "invalid_argument"
            )
        },
    )
    get_schedule_info = Operation(
        INFO,
        "get_schedule_info",
        ServiceJsonBinding(PATH, "axsch:GetScheduleInfo"),
        params=TokensRequest,
        result=ScheduleInfos,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    get_schedule_list = Operation(
        INFO,
        "get_schedule_list",
        ServiceJsonBinding(PATH, "axsch:GetScheduleList"),
        params=ListRequest,
        result=ScheduleList,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartReference": ErrorCode(
                "StartReference is invalid or has timed out; start again from the beginning.", "invalid_argument"
            )
        },
    )
    get_schedule = Operation(
        INFO,
        "get_schedule",
        ServiceJsonBinding(PATH, "axsch:GetSchedule"),
        params=TokensRequest,
        result=Schedules,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability.", "invalid_argument"
            )
        },
    )
    set_schedule = Operation(
        INFO,
        "set_schedule",
        ServiceJsonBinding(PATH, "axsch:SetSchedule"),
        params=SetScheduleRequest,
        result=TokenList,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:InvalidScheduleFault": ErrorCode("The schedule definition is invalid.", "invalid_argument")},
    )
    remove_schedule = Operation(
        INFO,
        "remove_schedule",
        ServiceJsonBinding(PATH, "axsch:RemoveSchedule"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("Schedule not found.", "not_found")},
    )
    schedule_active = Operation(
        INFO,
        "schedule_active",
        ServiceJsonBinding(PATH, "axsch:ScheduleActive"),
        params=ScheduleActiveRequest,
        result=ScheduleActiveResult,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("Schedule not found.", "not_found")},
    )
    schedule_status_report = Operation(
        INFO,
        "schedule_status_report",
        ServiceJsonBinding(PATH, "axsch:ScheduleStatusReport"),
        params=ScheduleStatusReportRequest,
        result=ScheduleStatusReportResult,
        access="admin",
        effect="read",
        errors={
            "ter:TooManyItems": ErrorCode(
                "Too many items were requested; see the MaxLimit capability.", "invalid_argument"
            )
        },
    )


# ---------------------------------------------------------------------------
# API classes


class ScheduleServiceApi(SyncApi):
    """Schedule service (``schedule-service``)."""

    INFO = INFO

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the schedule service. Access: anonymous."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def get_schedule_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ScheduleInfoList:
        """List the summaries of all schedules.

        Pages through the schedules. Pass the returned `NextStartReference` as `StartReference` in the next
        call and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return self._run(
            OPS.get_schedule_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_schedule_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> ScheduleInfos:
        """Get the summaries of the schedules with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_schedule_info, None, {"token": token}, request_options)

    def get_schedule_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ScheduleList:
        """List all schedules with their definitions.

        Pages through the schedules. Pass the returned `NextStartReference` as `StartReference` in the next
        call and never reuse a reference. The system has default schedules, such as `standard_office_hours`,
        which can be removed.

        Access: admin.
        """
        return self._run(
            OPS.get_schedule_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    def get_schedule(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> Schedules:
        """Get the schedules with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return self._run(OPS.get_schedule, None, {"token": token}, request_options)

    @overload
    def set_schedule(
        self, request: SetScheduleRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    def set_schedule(
        self, /, *, schedule: list[ScheduleInput], request_options: RequestOptions | None = None
    ) -> TokenList: ...
    def set_schedule(
        self,
        request: SetScheduleRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Add or update schedules.

        A schedule whose token exists is updated, any other is added, and a schedule without a token gets
        one generated by the device. The tokens are returned.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.set_schedule, request, kwargs, request_options)

    def remove_schedule(self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None) -> None:
        """Remove the schedules with the given tokens.

        Removing an active interval schedule sends a Schedule/Interval event with Active and Exception
        false.

        Access: admin.
        """
        self._run(OPS.remove_schedule, None, {"token": token}, request_options)

    def schedule_active(
        self,
        *,
        token: list[ReferenceToken],
        local_time: str | None | MISSING = MISSING,
        utc_time: str | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ScheduleActiveResult:
        """Check whether any of the schedules is active at a given or the current time.

        Several schedules are combined as "any schedule active and no exception". If any schedule has a
        matching exception, the result is `Active` false and `Exception` true. Without `LocalTime` and
        `UtcTime` the device's current time is used; with one of them the other is deduced from the device
        time zone.

        Access: admin.
        """
        return self._run(
            OPS.schedule_active, None, {"token": token, "local_time": local_time, "utc_time": utc_time}, request_options
        )

    def schedule_status_report(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> ScheduleStatusReportResult:
        """Get the status of the given schedules. Access: admin."""
        return self._run(OPS.schedule_status_report, None, {"token": token}, request_options)


class AsyncScheduleServiceApi(AsyncApi):
    """Schedule service (``schedule-service``)."""

    INFO = INFO

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the schedule service. Access: anonymous."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def get_schedule_info_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ScheduleInfoList:
        """List the summaries of all schedules.

        Pages through the schedules. Pass the returned `NextStartReference` as `StartReference` in the next
        call and never reuse a reference. The device may return fewer items than `Limit`.

        Access: admin.
        """
        return await self._run(
            OPS.get_schedule_info_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_schedule_info(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> ScheduleInfos:
        """Get the summaries of the schedules with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_schedule_info, None, {"token": token}, request_options)

    async def get_schedule_list(
        self,
        *,
        limit: int | MISSING = MISSING,
        start_reference: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ScheduleList:
        """List all schedules with their definitions.

        Pages through the schedules. Pass the returned `NextStartReference` as `StartReference` in the next
        call and never reuse a reference. The system has default schedules, such as `standard_office_hours`,
        which can be removed.

        Access: admin.
        """
        return await self._run(
            OPS.get_schedule_list, None, {"limit": limit, "start_reference": start_reference}, request_options
        )

    async def get_schedule(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> Schedules:
        """Get the schedules with the given tokens.

        The device ignores tokens it cannot resolve and may return an empty list.

        Access: admin.
        """
        return await self._run(OPS.get_schedule, None, {"token": token}, request_options)

    @overload
    async def set_schedule(
        self, request: SetScheduleRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    async def set_schedule(
        self, /, *, schedule: list[ScheduleInput], request_options: RequestOptions | None = None
    ) -> TokenList: ...
    async def set_schedule(
        self,
        request: SetScheduleRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Add or update schedules.

        A schedule whose token exists is updated, any other is added, and a schedule without a token gets
        one generated by the device. The tokens are returned.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.set_schedule, request, kwargs, request_options)

    async def remove_schedule(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> None:
        """Remove the schedules with the given tokens.

        Removing an active interval schedule sends a Schedule/Interval event with Active and Exception
        false.

        Access: admin.
        """
        await self._run(OPS.remove_schedule, None, {"token": token}, request_options)

    async def schedule_active(
        self,
        *,
        token: list[ReferenceToken],
        local_time: str | None | MISSING = MISSING,
        utc_time: str | None | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> ScheduleActiveResult:
        """Check whether any of the schedules is active at a given or the current time.

        Several schedules are combined as "any schedule active and no exception". If any schedule has a
        matching exception, the result is `Active` false and `Exception` true. Without `LocalTime` and
        `UtcTime` the device's current time is used; with one of them the other is deduced from the device
        time zone.

        Access: admin.
        """
        return await self._run(
            OPS.schedule_active, None, {"token": token, "local_time": local_time, "utc_time": utc_time}, request_options
        )

    async def schedule_status_report(
        self, *, token: list[ReferenceToken], request_options: RequestOptions | None = None
    ) -> ScheduleStatusReportResult:
        """Get the status of the given schedules. Access: admin."""
        return await self._run(OPS.schedule_status_report, None, {"token": token}, request_options)
