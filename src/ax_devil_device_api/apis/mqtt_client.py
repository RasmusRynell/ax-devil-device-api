# GENERATED from specs/apis/network-video/mqtt-client.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure, activate and query the device's MQTT client.

Docs: https://developer.axis.com/vapix/network-video/mqtt-client-api/
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Protocol = Literal["tcp", "ssl", "ws", "wss"]


class Server(Model):
    """Broker address and transport."""

    host: str
    """The broker location, i.e. the hostname or IP address."""
    protocol: Protocol | None = None
    """``tcp``, ``ssl``, ``ws`` (WebSocket) or ``wss`` (WebSocket Secure)."""
    port: int | None = None
    """Defaults per protocol: tcp 1883, ssl 8883, ws 80, wss 443."""
    basepath: str | None = None
    """URL path suffix, used only for ``ws`` and ``wss``. Default empty."""
    alpn_protocol: str | None = Field(
        default=None, validation_alias="alpnProtocol", serialization_alias="alpnProtocol", max_length=255
    )
    """ALPN protocol for ``ssl`` or ``wss``; empty disables ALPN."""


class AnnouncementMessage(Model):
    """Last-will, connect or disconnect message options."""

    use_default: bool | None = Field(default=None, validation_alias="useDefault", serialization_alias="useDefault")
    """Use the default message. When false, topic, message, retain and qos are required."""
    topic: str | None = None
    message: str | None = None
    retain: bool | None = None
    qos: Literal[0, 1, 2] | None = None


class Ssl(Model):
    """TLS options; only for ``ssl`` and ``wss`` connections."""

    validate_server_cert: bool | None = Field(
        default=None, validation_alias="validateServerCert", serialization_alias="validateServerCert"
    )
    client_cert_id: str | None = Field(
        default=None, validation_alias="clientCertID", serialization_alias="clientCertID"
    )
    ca_cert_id: str | None = Field(default=None, validation_alias="CACertID", serialization_alias="CACertID")


class ClientConfig(Model):
    """MQTT client settings as reported by the device. The password is masked."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"password"})
    server: Server
    client_id: str | None = Field(default=None, validation_alias="clientId", serialization_alias="clientId")
    http_proxy: str | None = Field(default=None, validation_alias="httpProxy", serialization_alias="httpProxy")
    https_proxy: str | None = Field(default=None, validation_alias="httpsProxy", serialization_alias="httpsProxy")
    username: str | None = None
    password: str | None = None
    """Always masked (``*****``) by the device; never write it back."""
    keep_alive_interval: int | None = Field(
        default=None, validation_alias="keepAliveInterval", serialization_alias="keepAliveInterval"
    )
    connect_timeout: int | None = Field(
        default=None, validation_alias="connectTimeout", serialization_alias="connectTimeout"
    )
    clean_session: bool | None = Field(
        default=None, validation_alias="cleanSession", serialization_alias="cleanSession"
    )
    auto_reconnect: bool | None = Field(
        default=None, validation_alias="autoReconnect", serialization_alias="autoReconnect"
    )
    device_topic_prefix: str | None = Field(
        default=None, validation_alias="deviceTopicPrefix", serialization_alias="deviceTopicPrefix"
    )
    last_will_testament: AnnouncementMessage | None = Field(
        default=None, validation_alias="lastWillTestament", serialization_alias="lastWillTestament"
    )
    connect_message: AnnouncementMessage | None = Field(
        default=None, validation_alias="connectMessage", serialization_alias="connectMessage"
    )
    disconnect_message: AnnouncementMessage | None = Field(
        default=None, validation_alias="disconnectMessage", serialization_alias="disconnectMessage"
    )
    ssl: Ssl | None = None


class Status(Model):
    state: Literal["active", "inactive"]
    connection_status: Literal["connected", "disconnected"] = Field(
        validation_alias="connectionStatus", serialization_alias="connectionStatus"
    )


class ClientStatus(Model):
    status: Status
    config: ClientConfig | None = None


class ConfigureClientRequest(Model):
    """Arguments of ``configure_client``. Replaces the whole client configuration."""

    server: Server
    client_id: str = Field(validation_alias="clientId", serialization_alias="clientId")
    http_proxy: str | None = Field(
        default=None, validation_alias="httpProxy", serialization_alias="httpProxy", max_length=255
    )
    https_proxy: str | None = Field(
        default=None, validation_alias="httpsProxy", serialization_alias="httpsProxy", max_length=255
    )
    username: str | None = None
    password: str | None = None
    keep_existing_password: bool | None = Field(
        default=None, validation_alias="keepExistingPassword", serialization_alias="keepExistingPassword"
    )
    """Keep the stored password and ignore ``password``."""
    keep_alive_interval: int | None = Field(
        default=None, validation_alias="keepAliveInterval", serialization_alias="keepAliveInterval"
    )
    connect_timeout: int | None = Field(
        default=None, validation_alias="connectTimeout", serialization_alias="connectTimeout"
    )
    clean_session: bool | None = Field(
        default=None, validation_alias="cleanSession", serialization_alias="cleanSession"
    )
    auto_reconnect: bool | None = Field(
        default=None, validation_alias="autoReconnect", serialization_alias="autoReconnect"
    )
    device_topic_prefix: str | None = Field(
        default=None, validation_alias="deviceTopicPrefix", serialization_alias="deviceTopicPrefix"
    )
    last_will_testament: AnnouncementMessage | None = Field(
        default=None, validation_alias="lastWillTestament", serialization_alias="lastWillTestament"
    )
    connect_message: AnnouncementMessage | None = Field(
        default=None, validation_alias="connectMessage", serialization_alias="connectMessage"
    )
    disconnect_message: AnnouncementMessage | None = Field(
        default=None, validation_alias="disconnectMessage", serialization_alias="disconnectMessage"
    )
    ssl: Ssl | None = None

    @classmethod
    def from_current(cls, config: ClientConfig) -> ConfigureClientRequest:
        """A request that rewrites ``config`` unchanged: copy it, edit fields, send it back.

        Masked and read-only fields are dropped and ``keep_existing_password`` is set, so stored secrets
        survive the round trip.

        Masked secrets (``password``) are never copied, at any depth; set a new value on the request when
        the device needs one.
        """
        data = config.request_data()
        missing = [name for name in ("client_id",) if name not in data]
        if missing:
            raise ValueError(f"the current value has no {', '.join(missing)} to keep")
        return cls(**data, keep_existing_password=True)


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/mqtt/client.cgi"

INFO = ApiInfo(
    id="mqtt-client",
    name="MQTT client API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("mqtt-client"),),
    docs=("https://developer.axis.com/vapix/network-video/mqtt-client-api/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON format", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing or invalid", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        2105: ErrorCode("Authorization failure", "access_denied"),
        2106: ErrorCode("Request size too large", "invalid_argument"),
    },
)


class OPS:
    configure_client = Operation(
        INFO,
        "configure_client",
        JsonRpcBinding("configureClient", PATH),
        params=ConfigureClientRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    activate_client = Operation(
        INFO, "activate_client", JsonRpcBinding("activateClient", PATH), access="admin", effect="action"
    )
    deactivate_client = Operation(
        INFO, "deactivate_client", JsonRpcBinding("deactivateClient", PATH), access="admin", effect="action"
    )
    get_client_status = Operation(
        INFO,
        "get_client_status",
        JsonRpcBinding("getClientStatus", PATH),
        result=ClientStatus,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class MqttClientApi(SyncApi):
    """MQTT client API (``mqtt-client``, version 1)."""

    INFO = INFO

    @overload
    def configure_client(
        self, request: ConfigureClientRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def configure_client(
        self,
        /,
        *,
        server: Server,
        client_id: str,
        http_proxy: str | MISSING = MISSING,
        https_proxy: str | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        keep_existing_password: bool | MISSING = MISSING,
        keep_alive_interval: int | MISSING = MISSING,
        connect_timeout: int | MISSING = MISSING,
        clean_session: bool | MISSING = MISSING,
        auto_reconnect: bool | MISSING = MISSING,
        device_topic_prefix: str | MISSING = MISSING,
        last_will_testament: AnnouncementMessage | MISSING = MISSING,
        connect_message: AnnouncementMessage | MISSING = MISSING,
        disconnect_message: AnnouncementMessage | MISSING = MISSING,
        ssl: Ssl | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def configure_client(
        self,
        request: ConfigureClientRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the MQTT client: broker, security, protocol settings, LWT, announcements.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.configure_client, request, kwargs, request_options)

    def activate_client(self, *, request_options: RequestOptions | None = None) -> None:
        """Activate the MQTT client; it stays active across reboots. Access: admin."""
        self._run(OPS.activate_client, None, {}, request_options)

    def deactivate_client(self, *, request_options: RequestOptions | None = None) -> None:
        """Deactivate the MQTT client. Access: admin."""
        self._run(OPS.deactivate_client, None, {}, request_options)

    def get_client_status(self, *, request_options: RequestOptions | None = None) -> ClientStatus:
        """Client state, connection status and configuration. Access: admin."""
        return self._run(OPS.get_client_status, None, {}, request_options)


class AsyncMqttClientApi(AsyncApi):
    """MQTT client API (``mqtt-client``, version 1)."""

    INFO = INFO

    @overload
    async def configure_client(
        self, request: ConfigureClientRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def configure_client(
        self,
        /,
        *,
        server: Server,
        client_id: str,
        http_proxy: str | MISSING = MISSING,
        https_proxy: str | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        keep_existing_password: bool | MISSING = MISSING,
        keep_alive_interval: int | MISSING = MISSING,
        connect_timeout: int | MISSING = MISSING,
        clean_session: bool | MISSING = MISSING,
        auto_reconnect: bool | MISSING = MISSING,
        device_topic_prefix: str | MISSING = MISSING,
        last_will_testament: AnnouncementMessage | MISSING = MISSING,
        connect_message: AnnouncementMessage | MISSING = MISSING,
        disconnect_message: AnnouncementMessage | MISSING = MISSING,
        ssl: Ssl | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def configure_client(
        self,
        request: ConfigureClientRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the MQTT client: broker, security, protocol settings, LWT, announcements.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.configure_client, request, kwargs, request_options)

    async def activate_client(self, *, request_options: RequestOptions | None = None) -> None:
        """Activate the MQTT client; it stays active across reboots. Access: admin."""
        await self._run(OPS.activate_client, None, {}, request_options)

    async def deactivate_client(self, *, request_options: RequestOptions | None = None) -> None:
        """Deactivate the MQTT client. Access: admin."""
        await self._run(OPS.deactivate_client, None, {}, request_options)

    async def get_client_status(self, *, request_options: RequestOptions | None = None) -> ClientStatus:
        """Client state, connection status and configuration. Access: admin."""
        return await self._run(OPS.get_client_status, None, {}, request_options)
