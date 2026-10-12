# GENERATED from specs/apis/physical-access-control/event-logger-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The event logger service is used for event logging and management of events and alarms.

Docs: https://developer.axis.com/vapix/physical-access-control/event-logger-service/
"""

from __future__ import annotations

from typing import Any, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class FilterKeyValue(Model):
    """A key and value to match events or alarms against. Leave out the value to match the key alone."""

    key: str = Field(validation_alias="Key", serialization_alias="Key")
    """Key to match, for example `topic0`, `topic1`, `topic2` for the event topic levels or the name of an event data item."""
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    """Value to match. Absent to match every event that has the key."""


class FilterSet(Model):
    """A group of key-value pairs that must all match."""

    filters: list[FilterKeyValue] | None = Field(
        default=None, validation_alias="Filters", serialization_alias="Filters"
    )


class FetchedEventKeyValue(Model):
    """A key and value of a logged event."""

    key: str | None = Field(default=None, validation_alias="Key", serialization_alias="Key")
    value: str | None = Field(default=None, validation_alias="Value", serialization_alias="Value")
    tags: list[str] | None = Field(default=None, validation_alias="Tags", serialization_alias="Tags")
    """Tags such as `onvif-source`, `onvif-data` or `wstype:pt:ReferenceToken`."""


class FetchedEvent(Model):
    """A logged event or alarm."""

    rowid: int | None = None
    """Row id in the log; pass the last one as `RowID` to fetch the next page."""
    token: str | None = None
    """Token of the event; the token of an alarm is what `remove_logged_alarm` takes."""
    uuid: str | None = Field(default=None, validation_alias="UUID", serialization_alias="UUID")
    """UUID of the producing device."""
    utc_time: str | None = Field(default=None, validation_alias="UtcTime", serialization_alias="UtcTime")
    """When the event was logged (ISO 8601, UTC)."""
    key_values: list[FetchedEventKeyValue] | None = Field(
        default=None, validation_alias="KeyValues", serialization_alias="KeyValues"
    )
    """The event's data."""
    tags: list[str] | None = Field(default=None, validation_alias="Tags", serialization_alias="Tags")


class FetchLogRequest(Model):
    start: str | None = Field(default=None, validation_alias="Start", serialization_alias="Start")
    """Start of the time interval (ISO 8601, for example `2012-11-27T00:00:00`). If absent, year 0 is assumed."""
    stop: str | None = Field(default=None, validation_alias="Stop", serialization_alias="Stop")
    """End of the time interval (ISO 8601). If absent there is no upper limit."""
    filters: list[FilterKeyValue] | None = Field(
        default=None, validation_alias="Filters", serialization_alias="Filters"
    )
    """Key-value pairs that returned items must match."""
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of items to return. One call returns at most 1000 items."""
    row_id: int | None = Field(default=None, validation_alias="RowID", serialization_alias="RowID")
    """Continue after this row id: the rowid of the last item of the previous response when More was true."""
    descending: bool | None = Field(default=None, validation_alias="Descending", serialization_alias="Descending")
    """Sort in descending order. The default is ascending. Default: False."""


class FetchLog2Request(Model):
    start: str | None = Field(default=None, validation_alias="Start", serialization_alias="Start")
    """Start of the time interval (ISO 8601, for example `2012-11-27T00:00:00`). If absent, year 0 is assumed."""
    stop: str | None = Field(default=None, validation_alias="Stop", serialization_alias="Stop")
    """End of the time interval (ISO 8601). If absent there is no upper limit."""
    filters: list[FilterKeyValue] | None = Field(
        default=None, validation_alias="Filters", serialization_alias="Filters"
    )
    """Key-value pairs that returned items must match."""
    filter_sets: list[FilterSet] | None = Field(
        default=None, validation_alias="FilterSets", serialization_alias="FilterSets"
    )
    """Groups of filters combined with logical OR; the filters within a group must all match."""
    limit: int | None = Field(default=None, validation_alias="Limit", serialization_alias="Limit")
    """Maximum number of items to return. One call returns at most 1000 items."""
    row_id: int | None = Field(default=None, validation_alias="RowID", serialization_alias="RowID")
    """Continue after this row id: the rowid of the last item of the previous response when More was true."""
    descending: bool | None = Field(default=None, validation_alias="Descending", serialization_alias="Descending")
    """Sort in descending order. The default is ascending. Default: False."""


class FetchEventsResult(Model):
    event: list[FetchedEvent] | None = Field(default=None, validation_alias="Event", serialization_alias="Event")
    """The events."""
    more: bool = Field(validation_alias="More", serialization_alias="More")
    """True if more items match than were returned; fetch the rest with RowID."""


class FetchAlarmsResult(Model):
    alarm: list[FetchedEvent] | None = Field(default=None, validation_alias="Alarm", serialization_alias="Alarm")
    """The alarms."""
    more: bool = Field(validation_alias="More", serialization_alias="More")
    """True if more items match than were returned; fetch the rest with RowID."""


class TokensRequest(Model):
    token: list[str] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens to remove."""


class TokenList(Model):
    token: list[str] | None = Field(default=None, validation_alias="Token", serialization_alias="Token")
    """Tokens of the created or updated filters."""


class IgnoreFilter(Model):
    """A filter for events that are not stored in the event log. An event matches when it has all the key-value pairs and comes from one of the devices in UUIDs."""

    token: str | None = None
    """Token of the filter. Allocated by the device when absent in a set request."""
    key_values: list[FilterKeyValue] | None = Field(
        default=None, validation_alias="KeyValues", serialization_alias="KeyValues"
    )
    """The key-value pairs an event must have."""
    uui_ds: list[str] | None = Field(default=None, validation_alias="UUIDs", serialization_alias="UUIDs")
    """UUIDs of the door controllers the filter applies to. Empty or absent applies to all."""


class AlarmFilter(Model):
    """A filter for events that become alarms. It overrides ignore filters."""

    token: str | None = None
    """Token of the filter. Allocated by the device when absent in a set request."""
    key_values: list[FilterKeyValue] | None = Field(
        default=None, validation_alias="KeyValues", serialization_alias="KeyValues"
    )
    """The key-value pairs an event must have."""
    uui_ds: list[str] | None = Field(default=None, validation_alias="UUIDs", serialization_alias="UUIDs")
    """UUIDs of the door controllers the filter applies to. Empty or absent applies to all."""


class SetIgnoreFilterRequest(Model):
    filter: list[IgnoreFilter] | None = Field(default=None, validation_alias="Filter", serialization_alias="Filter")


class IgnoreFilterList(Model):
    filter: list[IgnoreFilter] | None = Field(default=None, validation_alias="Filter", serialization_alias="Filter")


class SetAlarmFilterRequest(Model):
    filter: list[AlarmFilter] | None = Field(default=None, validation_alias="Filter", serialization_alias="Filter")


class AlarmFilterList(Model):
    filter: list[AlarmFilter] | None = Field(default=None, validation_alias="Filter", serialization_alias="Filter")


class ServiceCapabilities(Model):
    """Optional functionality of the event logger config service. Static during device operation."""

    enable_global_events: bool | None = Field(
        default=None, validation_alias="EnableGlobalEvents", serialization_alias="EnableGlobalEvents"
    )
    """True if the operations to enable and disable global event distribution are supported."""


class GetServiceCapabilitiesResult(Model):
    capabilities: ServiceCapabilities = Field(validation_alias="Capabilities", serialization_alias="Capabilities")
    """The capabilities."""


class EventDistributionConfig(Model):
    """The current event distribution configuration."""

    global_distribution_enabled: bool | None = Field(
        default=None, validation_alias="GlobalDistributionEnabled", serialization_alias="GlobalDistributionEnabled"
    )
    """True if events are distributed among all door controllers in the network."""


class EventDistributionConfigResult(Model):
    event_distribution_config: list[EventDistributionConfig] | None = Field(
        default=None, validation_alias="EventDistributionConfig", serialization_alias="EventDistributionConfig"
    )


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/eventlogger"

INFO = ApiInfo(
    id="event-logger-service",
    name="Event logger service",
    family=Family.SERVICE_JSON,
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/event-logger-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/access-control-service/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
    ),
    errors={"ter:InvalidArgVal": ErrorCode("Invalid argument value", "invalid_argument")},
)


class OPS:
    fetch_events = Operation(
        INFO,
        "fetch_events",
        ServiceJsonBinding(PATH, "axlog:FetchEvents"),
        params=FetchLogRequest,
        result=FetchEventsResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartTime": ErrorCode("Invalid start time.", "invalid_argument"),
            "ter:InvalidStopTime": ErrorCode("Invalid stop time.", "invalid_argument"),
        },
    )
    fetch_events2 = Operation(
        INFO,
        "fetch_events2",
        ServiceJsonBinding(PATH, "axlog:FetchEvents2"),
        params=FetchLog2Request,
        result=FetchEventsResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartTime": ErrorCode("Invalid start time.", "invalid_argument"),
            "ter:InvalidStopTime": ErrorCode("Invalid stop time.", "invalid_argument"),
        },
    )
    fetch_alarms = Operation(
        INFO,
        "fetch_alarms",
        ServiceJsonBinding(PATH, "axlog:FetchAlarms"),
        params=FetchLogRequest,
        result=FetchAlarmsResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartTime": ErrorCode("Invalid start time.", "invalid_argument"),
            "ter:InvalidStopTime": ErrorCode("Invalid stop time.", "invalid_argument"),
        },
    )
    fetch_alarms2 = Operation(
        INFO,
        "fetch_alarms2",
        ServiceJsonBinding(PATH, "axlog:FetchAlarms2"),
        params=FetchLog2Request,
        result=FetchAlarmsResult,
        access="admin",
        effect="read",
        errors={
            "ter:InvalidStartTime": ErrorCode("Invalid start time.", "invalid_argument"),
            "ter:InvalidStopTime": ErrorCode("Invalid stop time.", "invalid_argument"),
        },
    )
    remove_logged_alarm = Operation(
        INFO,
        "remove_logged_alarm",
        ServiceJsonBinding(PATH, "axlog:RemoveLoggedAlarm"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("Alarm not found.", "not_found")},
    )
    set_ignore_filter = Operation(
        INFO,
        "set_ignore_filter",
        ServiceJsonBinding(PATH, "axloc:SetIgnoreFilter"),
        params=SetIgnoreFilterRequest,
        result=TokenList,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:NotFound": ErrorCode("Filter not found.", "not_found")},
    )
    remove_ignore_filter = Operation(
        INFO,
        "remove_ignore_filter",
        ServiceJsonBinding(PATH, "axloc:RemoveIgnoreFilter"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("Filter not found.", "not_found")},
    )
    get_ignore_filter_list = Operation(
        INFO,
        "get_ignore_filter_list",
        ServiceJsonBinding(PATH, "axloc:GetIgnoreFilterList"),
        result=IgnoreFilterList,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("Filter not found.", "not_found")},
    )
    set_alarm_filter = Operation(
        INFO,
        "set_alarm_filter",
        ServiceJsonBinding(PATH, "axloc:SetAlarmFilter"),
        params=SetAlarmFilterRequest,
        result=TokenList,
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:NotFound": ErrorCode("Filter not found.", "not_found")},
    )
    remove_alarm_filter = Operation(
        INFO,
        "remove_alarm_filter",
        ServiceJsonBinding(PATH, "axloc:RemoveAlarmFilter"),
        params=TokensRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={"ter:NotFound": ErrorCode("Filter not found.", "not_found")},
    )
    get_alarm_filter_list = Operation(
        INFO,
        "get_alarm_filter_list",
        ServiceJsonBinding(PATH, "axloc:GetAlarmFilterList"),
        result=AlarmFilterList,
        access="admin",
        effect="read",
        errors={"ter:NotFound": ErrorCode("Filter not found.", "not_found")},
    )
    get_service_capabilities = Operation(
        INFO,
        "get_service_capabilities",
        ServiceJsonBinding(PATH, "axloc:GetServiceCapabilities"),
        result=GetServiceCapabilitiesResult,
        access="anonymous",
        effect="read",
    )
    enable_global_distribution = Operation(
        INFO,
        "enable_global_distribution",
        ServiceJsonBinding(PATH, "axloc:EnableGlobalDistribution"),
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:NotSupported": ErrorCode("The operation is not supported.", "unsupported")},
    )
    disable_global_distribution = Operation(
        INFO,
        "disable_global_distribution",
        ServiceJsonBinding(PATH, "axloc:DisableGlobalDistribution"),
        access="admin",
        effect="write",
        write="patch",
        errors={"ter:NotSupported": ErrorCode("The operation is not supported.", "unsupported")},
    )
    get_event_distribution_config = Operation(
        INFO,
        "get_event_distribution_config",
        ServiceJsonBinding(PATH, "axloc:GetEventDistributionConfig"),
        result=EventDistributionConfigResult,
        access="admin",
        effect="read",
        errors={"ter:NotSupported": ErrorCode("The operation is not supported.", "unsupported")},
    )


# ---------------------------------------------------------------------------
# API classes


class EventLoggerServiceApi(SyncApi):
    """Event logger service (``event-logger-service``)."""

    INFO = INFO

    @overload
    def fetch_events(
        self, request: FetchLogRequest, /, *, request_options: RequestOptions | None = None
    ) -> FetchEventsResult: ...
    @overload
    def fetch_events(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchEventsResult: ...
    def fetch_events(
        self, request: FetchLogRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> FetchEventsResult:
        """Fetch logged events that match the filters.

        The event log holds at most 30000 events and one call returns at most 1000. When `More` is true,
        call again with `RowID` set to the rowid of the last event returned. With global event distribution
        enabled (firmware 1.20 and later) events from every door controller in the network can be fetched.

        Access: admin.
        """
        return self._run(OPS.fetch_events, request, kwargs, request_options)

    @overload
    def fetch_events2(
        self, request: FetchLog2Request, /, *, request_options: RequestOptions | None = None
    ) -> FetchEventsResult: ...
    @overload
    def fetch_events2(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        filter_sets: list[FilterSet] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchEventsResult: ...
    def fetch_events2(
        self,
        request: FetchLog2Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> FetchEventsResult:
        """Fetch logged events that match the filters or any of the filter sets.

        Like fetch_events, with `FilterSets` in addition. The filters in one set must all match and the sets
        are combined with logical OR.

        Access: admin.
        """
        return self._run(OPS.fetch_events2, request, kwargs, request_options)

    @overload
    def fetch_alarms(
        self, request: FetchLogRequest, /, *, request_options: RequestOptions | None = None
    ) -> FetchAlarmsResult: ...
    @overload
    def fetch_alarms(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchAlarmsResult: ...
    def fetch_alarms(
        self, request: FetchLogRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> FetchAlarmsResult:
        """Fetch logged alarms that match the filters.

        Takes the same parameters as fetch_events. The alarm list holds at most 200 alarms, so the default
        limit of 1000 returns all of them in one call. An alarm is acknowledged by removing it with
        remove_logged_alarm.

        Access: admin.
        """
        return self._run(OPS.fetch_alarms, request, kwargs, request_options)

    @overload
    def fetch_alarms2(
        self, request: FetchLog2Request, /, *, request_options: RequestOptions | None = None
    ) -> FetchAlarmsResult: ...
    @overload
    def fetch_alarms2(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        filter_sets: list[FilterSet] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchAlarmsResult: ...
    def fetch_alarms2(
        self,
        request: FetchLog2Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> FetchAlarmsResult:
        """Fetch logged alarms that match the filters or any of the filter sets.

        Like fetch_alarms, with `FilterSets` in addition, as fetch_events2 does for events.

        Access: admin.
        """
        return self._run(OPS.fetch_alarms2, request, kwargs, request_options)

    def remove_logged_alarm(
        self, *, token: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Acknowledge alarms by removing them from the alarm list.

        The alarms stay in the event log.

        Access: admin.
        """
        self._run(OPS.remove_logged_alarm, None, {"token": token}, request_options)

    @overload
    def set_ignore_filter(
        self, request: SetIgnoreFilterRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    def set_ignore_filter(
        self, /, *, filter: list[IgnoreFilter] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    def set_ignore_filter(
        self,
        request: SetIgnoreFilterRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Create or update ignore filters.

        A filter whose token exists is updated; any other is created. Events that match an ignore filter are
        not stored, unless they also match an alarm filter.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.set_ignore_filter, request, kwargs, request_options)

    def remove_ignore_filter(
        self, *, token: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove ignore filters. Access: admin."""
        self._run(OPS.remove_ignore_filter, None, {"token": token}, request_options)

    def get_ignore_filter_list(self, *, request_options: RequestOptions | None = None) -> IgnoreFilterList:
        """List all ignore filters. Access: admin."""
        return self._run(OPS.get_ignore_filter_list, None, {}, request_options)

    @overload
    def set_alarm_filter(
        self, request: SetAlarmFilterRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    def set_alarm_filter(
        self, /, *, filter: list[AlarmFilter] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    def set_alarm_filter(
        self,
        request: SetAlarmFilterRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Create or update alarm filters.

        A filter whose token exists is updated; any other is created. An event that matches an alarm filter
        is stored as an alarm as well as an event, even if it matches an ignore filter.

        Changes only the fields given. Access: admin.
        """
        return self._run(OPS.set_alarm_filter, request, kwargs, request_options)

    def remove_alarm_filter(
        self, *, token: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove alarm filters. Access: admin."""
        self._run(OPS.remove_alarm_filter, None, {"token": token}, request_options)

    def get_alarm_filter_list(self, *, request_options: RequestOptions | None = None) -> AlarmFilterList:
        """List all alarm filters. Access: admin."""
        return self._run(OPS.get_alarm_filter_list, None, {}, request_options)

    def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the event logger config service. Access: anonymous."""
        return self._run(OPS.get_service_capabilities, None, {}, request_options)

    def enable_global_distribution(self, *, request_options: RequestOptions | None = None) -> None:
        """Enable global distribution of events among all connected door controllers.

        Enabled by default, from firmware 1.20.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.enable_global_distribution, None, {}, request_options)

    def disable_global_distribution(self, *, request_options: RequestOptions | None = None) -> None:
        """Disable global distribution of events among all connected door controllers.

        Logged events and alarms are then no longer replicated to the other door controllers.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.disable_global_distribution, None, {}, request_options)

    def get_event_distribution_config(
        self, *, request_options: RequestOptions | None = None
    ) -> EventDistributionConfigResult:
        """Get the current event distribution configuration. Access: admin."""
        return self._run(OPS.get_event_distribution_config, None, {}, request_options)


class AsyncEventLoggerServiceApi(AsyncApi):
    """Event logger service (``event-logger-service``)."""

    INFO = INFO

    @overload
    async def fetch_events(
        self, request: FetchLogRequest, /, *, request_options: RequestOptions | None = None
    ) -> FetchEventsResult: ...
    @overload
    async def fetch_events(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchEventsResult: ...
    async def fetch_events(
        self, request: FetchLogRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> FetchEventsResult:
        """Fetch logged events that match the filters.

        The event log holds at most 30000 events and one call returns at most 1000. When `More` is true,
        call again with `RowID` set to the rowid of the last event returned. With global event distribution
        enabled (firmware 1.20 and later) events from every door controller in the network can be fetched.

        Access: admin.
        """
        return await self._run(OPS.fetch_events, request, kwargs, request_options)

    @overload
    async def fetch_events2(
        self, request: FetchLog2Request, /, *, request_options: RequestOptions | None = None
    ) -> FetchEventsResult: ...
    @overload
    async def fetch_events2(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        filter_sets: list[FilterSet] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchEventsResult: ...
    async def fetch_events2(
        self,
        request: FetchLog2Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> FetchEventsResult:
        """Fetch logged events that match the filters or any of the filter sets.

        Like fetch_events, with `FilterSets` in addition. The filters in one set must all match and the sets
        are combined with logical OR.

        Access: admin.
        """
        return await self._run(OPS.fetch_events2, request, kwargs, request_options)

    @overload
    async def fetch_alarms(
        self, request: FetchLogRequest, /, *, request_options: RequestOptions | None = None
    ) -> FetchAlarmsResult: ...
    @overload
    async def fetch_alarms(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchAlarmsResult: ...
    async def fetch_alarms(
        self, request: FetchLogRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> FetchAlarmsResult:
        """Fetch logged alarms that match the filters.

        Takes the same parameters as fetch_events. The alarm list holds at most 200 alarms, so the default
        limit of 1000 returns all of them in one call. An alarm is acknowledged by removing it with
        remove_logged_alarm.

        Access: admin.
        """
        return await self._run(OPS.fetch_alarms, request, kwargs, request_options)

    @overload
    async def fetch_alarms2(
        self, request: FetchLog2Request, /, *, request_options: RequestOptions | None = None
    ) -> FetchAlarmsResult: ...
    @overload
    async def fetch_alarms2(
        self,
        /,
        *,
        start: str | MISSING = MISSING,
        stop: str | MISSING = MISSING,
        filters: list[FilterKeyValue] | MISSING = MISSING,
        filter_sets: list[FilterSet] | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        row_id: int | MISSING = MISSING,
        descending: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> FetchAlarmsResult: ...
    async def fetch_alarms2(
        self,
        request: FetchLog2Request | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> FetchAlarmsResult:
        """Fetch logged alarms that match the filters or any of the filter sets.

        Like fetch_alarms, with `FilterSets` in addition, as fetch_events2 does for events.

        Access: admin.
        """
        return await self._run(OPS.fetch_alarms2, request, kwargs, request_options)

    async def remove_logged_alarm(
        self, *, token: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Acknowledge alarms by removing them from the alarm list.

        The alarms stay in the event log.

        Access: admin.
        """
        await self._run(OPS.remove_logged_alarm, None, {"token": token}, request_options)

    @overload
    async def set_ignore_filter(
        self, request: SetIgnoreFilterRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    async def set_ignore_filter(
        self, /, *, filter: list[IgnoreFilter] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    async def set_ignore_filter(
        self,
        request: SetIgnoreFilterRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Create or update ignore filters.

        A filter whose token exists is updated; any other is created. Events that match an ignore filter are
        not stored, unless they also match an alarm filter.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.set_ignore_filter, request, kwargs, request_options)

    async def remove_ignore_filter(
        self, *, token: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove ignore filters. Access: admin."""
        await self._run(OPS.remove_ignore_filter, None, {"token": token}, request_options)

    async def get_ignore_filter_list(self, *, request_options: RequestOptions | None = None) -> IgnoreFilterList:
        """List all ignore filters. Access: admin."""
        return await self._run(OPS.get_ignore_filter_list, None, {}, request_options)

    @overload
    async def set_alarm_filter(
        self, request: SetAlarmFilterRequest, /, *, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    @overload
    async def set_alarm_filter(
        self, /, *, filter: list[AlarmFilter] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> TokenList: ...
    async def set_alarm_filter(
        self,
        request: SetAlarmFilterRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TokenList:
        """Create or update alarm filters.

        A filter whose token exists is updated; any other is created. An event that matches an alarm filter
        is stored as an alarm as well as an event, even if it matches an ignore filter.

        Changes only the fields given. Access: admin.
        """
        return await self._run(OPS.set_alarm_filter, request, kwargs, request_options)

    async def remove_alarm_filter(
        self, *, token: list[str] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove alarm filters. Access: admin."""
        await self._run(OPS.remove_alarm_filter, None, {"token": token}, request_options)

    async def get_alarm_filter_list(self, *, request_options: RequestOptions | None = None) -> AlarmFilterList:
        """List all alarm filters. Access: admin."""
        return await self._run(OPS.get_alarm_filter_list, None, {}, request_options)

    async def get_service_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> GetServiceCapabilitiesResult:
        """Get the capabilities of the event logger config service. Access: anonymous."""
        return await self._run(OPS.get_service_capabilities, None, {}, request_options)

    async def enable_global_distribution(self, *, request_options: RequestOptions | None = None) -> None:
        """Enable global distribution of events among all connected door controllers.

        Enabled by default, from firmware 1.20.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.enable_global_distribution, None, {}, request_options)

    async def disable_global_distribution(self, *, request_options: RequestOptions | None = None) -> None:
        """Disable global distribution of events among all connected door controllers.

        Logged events and alarms are then no longer replicated to the other door controllers.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.disable_global_distribution, None, {}, request_options)

    async def get_event_distribution_config(
        self, *, request_options: RequestOptions | None = None
    ) -> EventDistributionConfigResult:
        """Get the current event distribution configuration. Access: admin."""
        return await self._run(OPS.get_event_distribution_config, None, {}, request_options)
