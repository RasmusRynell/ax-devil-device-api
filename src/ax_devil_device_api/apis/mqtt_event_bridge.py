# GENERATED from specs/apis/network-video/event-mqtt-bridge.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Bridge Event Service events and MQTT: publish selected device events to the broker and convert subscribed MQTT messages into events.

Docs: https://developer.axis.com/vapix/network-video/mqtt-event-bridge/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Qos = Literal[0, 1, 2]
Retain = Literal["none", "property", "all"]
TopicPrefix = Literal["default", "custom"]


class EventFilter(Model):
    """Selects events to publish."""

    topic_filter: str = Field(validation_alias="topicFilter", serialization_alias="topicFilter")
    """A subscription filter for the Event system, based on ONVIF "Concrete topic expressions"."""
    qos: Qos | None = None
    """QoS policy used when publishing events from this filter. Default 0."""
    retain: Retain | None = None
    """Retain policy used when publishing events from this filter. Default none."""


class EventPublicationConfig(Model):
    """Event publication settings, as reported by the device."""

    topic_prefix: TopicPrefix | None = Field(
        default=None, validation_alias="topicPrefix", serialization_alias="topicPrefix"
    )
    """Controls the topic prefix."""
    custom_topic_prefix: str | None = Field(
        default=None, validation_alias="customTopicPrefix", serialization_alias="customTopicPrefix"
    )
    """The custom topic prefix. Required if topicPrefix is custom."""
    append_event_topic: bool | None = Field(
        default=None, validation_alias="appendEventTopic", serialization_alias="appendEventTopic"
    )
    """Append the topic of the event to the prefix. Default true. (The docs type column says String; the description and examples use a boolean.) Default: True."""
    include_topic_namespaces: bool | None = Field(
        default=None, validation_alias="includeTopicNamespaces", serialization_alias="includeTopicNamespaces"
    )
    """Include ONVIF topic namespaces in the MQTT message topic. Default true. Default: True."""
    include_serial_number_in_payload: bool | None = Field(
        default=None,
        validation_alias="includeSerialNumberInPayload",
        serialization_alias="includeSerialNumberInPayload",
    )
    """Include the serial number in the payload message. Default false. Default: False."""
    event_filter_list: list[EventFilter] | None = Field(
        default=None, validation_alias="eventFilterList", serialization_alias="eventFilterList"
    )
    """Filters applied to messages from the Event system. A message that matches several filters is published several times."""


class ConfigureEventPublicationRequest(Model):
    """Arguments of configure_event_publication. Replaces the event publication configuration."""

    topic_prefix: TopicPrefix | None = Field(
        default=None, validation_alias="topicPrefix", serialization_alias="topicPrefix"
    )
    """Controls the topic prefix."""
    custom_topic_prefix: str | None = Field(
        default=None, validation_alias="customTopicPrefix", serialization_alias="customTopicPrefix"
    )
    """The custom topic prefix. Required if topicPrefix is custom."""
    append_event_topic: bool | None = Field(
        default=None, validation_alias="appendEventTopic", serialization_alias="appendEventTopic"
    )
    """Append the topic of the event to the prefix. Default true. (The docs type column says String; the description and examples use a boolean.) Default: True."""
    include_topic_namespaces: bool | None = Field(
        default=None, validation_alias="includeTopicNamespaces", serialization_alias="includeTopicNamespaces"
    )
    """Include ONVIF topic namespaces in the MQTT message topic. Default true. Default: True."""
    include_serial_number_in_payload: bool | None = Field(
        default=None,
        validation_alias="includeSerialNumberInPayload",
        serialization_alias="includeSerialNumberInPayload",
    )
    """Include the serial number in the payload message. Default false. Default: False."""
    event_filter_list: list[EventFilter] = Field(
        validation_alias="eventFilterList", serialization_alias="eventFilterList"
    )
    """Filters applied to messages from the Event system. A message that matches several filters is published several times."""

    @classmethod
    def from_current(cls, config: EventPublicationConfig) -> ConfigureEventPublicationRequest:
        """A request that rewrites ``config`` unchanged: copy it, edit fields, send it back."""
        data = config.request_data()
        missing = [name for name in ("event_filter_list",) if name not in data]
        if missing:
            raise ValueError(f"the current value has no {', '.join(missing)} to keep")
        return cls.from_response_data(data)


class EventPublicationConfigResult(Model):
    event_publication_config: EventPublicationConfig = Field(
        validation_alias="eventPublicationConfig", serialization_alias="eventPublicationConfig"
    )
    """All options used for event publishing."""


class MqttFilter(Model):
    """Selects incoming MQTT messages to convert to events."""

    topic_filter: str = Field(validation_alias="topicFilter", serialization_alias="topicFilter")
    """An MQTT subscription topic filter used with the external broker. + and # are only allowed for stateless conversions (isStateData false)."""
    use_device_topic_prefix: bool | None = Field(
        default=None, validation_alias="useDeviceTopicPrefix", serialization_alias="useDeviceTopicPrefix"
    )
    """Prefix topicFilter with the device topic prefix of the MQTT client configuration. Default false. Default: False."""
    qos: Qos | None = None
    """MQTT subscription QoS used with the external broker. Default 0."""
    is_state_data: bool | None = Field(default=None, validation_alias="isStateData", serialization_alias="isStateData")
    """If true, matching messages are converted to stateful (property) events; otherwise to stateless events. Default false. Default: False."""


class ConfigureMqttSubscriptionRequest(Model):
    """Arguments of configure_mqtt_subscription. Replaces the subscription configuration."""

    mqtt_filter_list: list[MqttFilter] = Field(validation_alias="mqttFilterList", serialization_alias="mqttFilterList")
    """MQTT topic filters used to subscribe to the external broker. Matching messages are converted to internal events."""

    @classmethod
    def from_current(cls, config: MqttSubscriptionConfig) -> ConfigureMqttSubscriptionRequest:
        """A request that rewrites ``config`` unchanged: copy it, edit fields, send it back."""
        data = config.request_data()
        missing = [name for name in ("mqtt_filter_list",) if name not in data]
        if missing:
            raise ValueError(f"the current value has no {', '.join(missing)} to keep")
        return cls.from_response_data(data)


class MqttSubscriptionConfig(Model):
    mqtt_filter_list: list[MqttFilter] | None = Field(
        default=None, validation_alias="mqttFilterList", serialization_alias="mqttFilterList"
    )


class MqttSubscriptionConfigResult(Model):
    mqtt_subscription_config: MqttSubscriptionConfig = Field(
        validation_alias="mqttSubscriptionConfig", serialization_alias="mqttSubscriptionConfig"
    )
    """All subscription options."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/mqtt/event.cgi"

INFO = ApiInfo(
    id="event-mqtt-bridge",
    name="MQTT Event Bridge",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0), ApiVersion(1, 1)),
    discovery=(ApiDiscovery("event-mqtt-bridge"),),
    docs=("https://developer.axis.com/vapix/network-video/mqtt-event-bridge/",),
    errors={
        1100: ErrorCode("Internal error.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON format.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing or invalid.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failure.", "access_denied"),
        2106: ErrorCode("Request size too large.", "invalid_argument"),
    },
)


class OPS:
    configure_event_publication = Operation(
        INFO,
        "configure_event_publication",
        JsonRpcBinding("configureEventPublication", PATH),
        params=ConfigureEventPublicationRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    get_event_publication_config = Operation(
        INFO,
        "get_event_publication_config",
        JsonRpcBinding("getEventPublicationConfig", PATH),
        result=EventPublicationConfigResult,
        access="admin",
        effect="read",
    )
    configure_mqtt_subscription = Operation(
        INFO,
        "configure_mqtt_subscription",
        JsonRpcBinding("configureMqttSubscription", PATH),
        params=ConfigureMqttSubscriptionRequest,
        access="admin",
        effect="write",
        since=ApiVersion(1, 1),
        write="replace",
    )
    get_mqtt_subscription_config = Operation(
        INFO,
        "get_mqtt_subscription_config",
        JsonRpcBinding("getMqttSubscriptionConfig", PATH),
        result=MqttSubscriptionConfigResult,
        access="admin",
        effect="read",
        since=ApiVersion(1, 1),
    )


# ---------------------------------------------------------------------------
# API classes


class MqttEventBridgeApi(SyncApi):
    """MQTT Event Bridge (``event-mqtt-bridge``, version 1)."""

    INFO = INFO

    @overload
    def configure_event_publication(
        self, request: ConfigureEventPublicationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def configure_event_publication(
        self,
        /,
        *,
        topic_prefix: TopicPrefix | MISSING = MISSING,
        custom_topic_prefix: str | MISSING = MISSING,
        append_event_topic: bool | MISSING = MISSING,
        include_topic_namespaces: bool | MISSING = MISSING,
        include_serial_number_in_payload: bool | MISSING = MISSING,
        event_filter_list: list[EventFilter],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def configure_event_publication(
        self,
        request: ConfigureEventPublicationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Select the events to publish to the MQTT broker.

        Event publication is only enabled once filters are set. Filters apply to topics only; payload
        filtering is not possible.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.configure_event_publication, request, kwargs, request_options)

    def get_event_publication_config(
        self, *, request_options: RequestOptions | None = None
    ) -> EventPublicationConfigResult:
        """Return the event publication configuration. Access: admin."""
        return self._run(OPS.get_event_publication_config, None, {}, request_options)

    @overload
    def configure_mqtt_subscription(
        self, request: ConfigureMqttSubscriptionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def configure_mqtt_subscription(
        self, /, *, mqtt_filter_list: list[MqttFilter], request_options: RequestOptions | None = None
    ) -> None: ...
    def configure_mqtt_subscription(
        self,
        request: ConfigureMqttSubscriptionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the MQTT subscription: incoming MQTT messages converted to events.

        A subscription is required to enable MQTT message to event conversion. Messages published by other
        clients on the same broker can be consumed within the platform.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.configure_mqtt_subscription, request, kwargs, request_options)

    def get_mqtt_subscription_config(
        self, *, request_options: RequestOptions | None = None
    ) -> MqttSubscriptionConfigResult:
        """Return the MQTT subscription configuration. Access: admin."""
        return self._run(OPS.get_mqtt_subscription_config, None, {}, request_options)


class AsyncMqttEventBridgeApi(AsyncApi):
    """MQTT Event Bridge (``event-mqtt-bridge``, version 1)."""

    INFO = INFO

    @overload
    async def configure_event_publication(
        self, request: ConfigureEventPublicationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def configure_event_publication(
        self,
        /,
        *,
        topic_prefix: TopicPrefix | MISSING = MISSING,
        custom_topic_prefix: str | MISSING = MISSING,
        append_event_topic: bool | MISSING = MISSING,
        include_topic_namespaces: bool | MISSING = MISSING,
        include_serial_number_in_payload: bool | MISSING = MISSING,
        event_filter_list: list[EventFilter],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def configure_event_publication(
        self,
        request: ConfigureEventPublicationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Select the events to publish to the MQTT broker.

        Event publication is only enabled once filters are set. Filters apply to topics only; payload
        filtering is not possible.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.configure_event_publication, request, kwargs, request_options)

    async def get_event_publication_config(
        self, *, request_options: RequestOptions | None = None
    ) -> EventPublicationConfigResult:
        """Return the event publication configuration. Access: admin."""
        return await self._run(OPS.get_event_publication_config, None, {}, request_options)

    @overload
    async def configure_mqtt_subscription(
        self, request: ConfigureMqttSubscriptionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def configure_mqtt_subscription(
        self, /, *, mqtt_filter_list: list[MqttFilter], request_options: RequestOptions | None = None
    ) -> None: ...
    async def configure_mqtt_subscription(
        self,
        request: ConfigureMqttSubscriptionRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the MQTT subscription: incoming MQTT messages converted to events.

        A subscription is required to enable MQTT message to event conversion. Messages published by other
        clients on the same broker can be consumed within the platform.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.configure_mqtt_subscription, request, kwargs, request_options)

    async def get_mqtt_subscription_config(
        self, *, request_options: RequestOptions | None = None
    ) -> MqttSubscriptionConfigResult:
        """Return the MQTT subscription configuration. Access: admin."""
        return await self._run(OPS.get_mqtt_subscription_config, None, {}, request_options)
