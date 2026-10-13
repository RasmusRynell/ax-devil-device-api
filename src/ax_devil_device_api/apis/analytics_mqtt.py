# GENERATED from specs/apis/device-configuration/analytics-mqtt-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Publish analytics data sources to MQTT topics through the device's MQTT client.

Docs: https://developer.axis.com/vapix/device-configuration/analytics-mqtt/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DataSourceKey = Annotated[str, Field(min_length=3, max_length=128)]
PublisherId = Annotated[str, Field(min_length=1, max_length=128)]
MqttTopic = Annotated[str, Field(min_length=1, max_length=128, pattern="^([a-zA-Z0-9_-]+)(/[a-zA-Z0-9_-]+)*$")]
Qos = Literal[0, 1, 2]


class DataSource(Model):
    """An analytics data source that can be published."""

    key: DataSourceKey


class DataSources(Model):
    """The data sources that can be published (the ``data`` member of the list response)."""

    data_sources: list[DataSource]


class Publisher(Model):
    """A configured publisher of one data source to one MQTT topic."""

    id: PublisherId
    data_source_key: DataSourceKey
    mqtt_topic: MqttTopic
    qos: Qos | None = None
    retain: bool | None = None
    use_topic_prefix: bool | None = None
    """Prefix the topic with the device topic prefix configured in the MQTT client."""


class AnalyticsMqtt(Model):
    """The whole API tree."""

    data_sources: list[DataSource] = []
    publishers: list[Publisher] = []


class AddPublisherRequest(Model):
    """Arguments of ``add_publisher``."""

    id: PublisherId
    data_source_key: DataSourceKey
    mqtt_topic: MqttTopic
    qos: Qos | None = None
    retain: bool | None = None
    use_topic_prefix: bool | None = None

    @classmethod
    def from_current(cls, publisher: Publisher) -> AddPublisherRequest:
        """A request that rewrites ``publisher`` unchanged: copy it, edit fields, send it back."""
        data = publisher.request_data()
        return cls.from_response_data(data)


class DataSourceKeyRequest(Model):
    key: DataSourceKey


class PublisherIdRequest(Model):
    id: PublisherId


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/analytics-mqtt/v1"

INFO = ApiInfo(
    id="analytics-mqtt-config",
    name="Analytics MQTT",
    family=Family.DCA,
    discovery=(DcaDiscovery("analytics-mqtt", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/analytics-mqtt/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=AnalyticsMqtt, access="admin", effect="read")
    list_data_sources = Operation(
        INFO,
        "list_data_sources",
        DcaBinding("GET", f"{ROOT}/data_sources"),
        result=DataSources,
        access="admin",
        effect="read",
    )
    get_data_source = Operation(
        INFO,
        "get_data_source",
        DcaBinding("GET", f"{ROOT}/data_sources/{{key}}"),
        params=DataSourceKeyRequest,
        result=DataSource,
        access="admin",
        effect="read",
    )
    list_publishers = Operation(
        INFO,
        "list_publishers",
        DcaBinding("GET", f"{ROOT}/publishers"),
        result=list[Publisher],
        access="admin",
        effect="read",
    )
    get_publisher = Operation(
        INFO,
        "get_publisher",
        DcaBinding("GET", f"{ROOT}/publishers/{{id}}"),
        params=PublisherIdRequest,
        result=Publisher,
        access="admin",
        effect="read",
    )
    add_publisher = Operation(
        INFO,
        "add_publisher",
        DcaBinding("POST", f"{ROOT}/publishers", body="object"),
        params=AddPublisherRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_publisher = Operation(
        INFO,
        "remove_publisher",
        DcaBinding("DELETE", f"{ROOT}/publishers/{{id}}"),
        params=PublisherIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class AnalyticsMqttApi(SyncApi):
    """Analytics MQTT (``analytics-mqtt-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> AnalyticsMqtt:
        """All data sources and publishers. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_data_sources(self, *, request_options: RequestOptions | None = None) -> DataSources:
        """Data sources that can be published. Access: admin."""
        return self._run(OPS.list_data_sources, None, {}, request_options)

    def get_data_source(self, key: DataSourceKey, *, request_options: RequestOptions | None = None) -> DataSource:
        """One data source. Access: admin."""
        return self._run(OPS.get_data_source, None, {"key": key}, request_options)

    def list_publishers(self, *, request_options: RequestOptions | None = None) -> list[Publisher]:
        """Configured publishers. Access: admin."""
        return self._run(OPS.list_publishers, None, {}, request_options)

    def get_publisher(self, id: PublisherId, *, request_options: RequestOptions | None = None) -> Publisher:
        """One publisher. Access: admin."""
        return self._run(OPS.get_publisher, None, {"id": id}, request_options)

    @overload
    def add_publisher(
        self, request: AddPublisherRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def add_publisher(
        self,
        /,
        *,
        id: PublisherId,
        data_source_key: DataSourceKey,
        mqtt_topic: MqttTopic,
        qos: Qos | MISSING = MISSING,
        retain: bool | MISSING = MISSING,
        use_topic_prefix: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_publisher(
        self,
        request: AddPublisherRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a publisher. Access: admin."""
        self._run(OPS.add_publisher, request, kwargs, request_options)

    def remove_publisher(self, id: PublisherId, *, request_options: RequestOptions | None = None) -> None:
        """Delete a publisher. Access: admin."""
        self._run(OPS.remove_publisher, None, {"id": id}, request_options)


class AsyncAnalyticsMqttApi(AsyncApi):
    """Analytics MQTT (``analytics-mqtt-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> AnalyticsMqtt:
        """All data sources and publishers. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_data_sources(self, *, request_options: RequestOptions | None = None) -> DataSources:
        """Data sources that can be published. Access: admin."""
        return await self._run(OPS.list_data_sources, None, {}, request_options)

    async def get_data_source(self, key: DataSourceKey, *, request_options: RequestOptions | None = None) -> DataSource:
        """One data source. Access: admin."""
        return await self._run(OPS.get_data_source, None, {"key": key}, request_options)

    async def list_publishers(self, *, request_options: RequestOptions | None = None) -> list[Publisher]:
        """Configured publishers. Access: admin."""
        return await self._run(OPS.list_publishers, None, {}, request_options)

    async def get_publisher(self, id: PublisherId, *, request_options: RequestOptions | None = None) -> Publisher:
        """One publisher. Access: admin."""
        return await self._run(OPS.get_publisher, None, {"id": id}, request_options)

    @overload
    async def add_publisher(
        self, request: AddPublisherRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_publisher(
        self,
        /,
        *,
        id: PublisherId,
        data_source_key: DataSourceKey,
        mqtt_topic: MqttTopic,
        qos: Qos | MISSING = MISSING,
        retain: bool | MISSING = MISSING,
        use_topic_prefix: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_publisher(
        self,
        request: AddPublisherRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a publisher. Access: admin."""
        await self._run(OPS.add_publisher, request, kwargs, request_options)

    async def remove_publisher(self, id: PublisherId, *, request_options: RequestOptions | None = None) -> None:
        """Delete a publisher. Access: admin."""
        await self._run(OPS.remove_publisher, None, {"id": id}, request_options)
