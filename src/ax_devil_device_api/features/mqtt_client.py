"""MQTT client feature for broker configuration and client lifecycle."""

import json
from typing import Any, ClassVar

import requests

from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


class MqttClient(FeatureClient):
    """Client for managing MQTT operations."""

    API_VERSION: ClassVar[str] = "1.0"
    MQTT_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/mqtt/client.cgi")

    def _parse_mqtt_response(self, response: requests.Response) -> dict[str, Any]:
        """Parse and validate MQTT API response."""
        if response.status_code != 200:
            raise FeatureError(
                "mqtt_error",
                f"MQTT operation failed: HTTP {response.status_code}",
            )

        try:
            json_response = response.json()
        except ValueError as error:
            raise FeatureError(
                "mqtt_error", "MQTT operation returned invalid JSON"
            ) from error
        if not isinstance(json_response, dict):
            raise FeatureError(
                "mqtt_error", "MQTT operation response must be a JSON object"
            )
        if "error" in json_response:
            error = json_response["error"]
            message = (
                error.get("message", "Unknown error")
                if isinstance(error, dict)
                else str(error)
            )
            raise FeatureError("mqtt_error", message)
        return json_response.get("data") or {}

    def _make_mqtt_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make MQTT API request with optional parameters."""
        payload = {"apiVersion": self.API_VERSION, "method": method}
        if params:
            payload["params"] = params

        response = self.request(
            self.MQTT_ENDPOINT,
            data=json.dumps(payload),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

        return self._parse_mqtt_response(response)

    def activate(self) -> dict[str, Any]:
        """Start MQTT client."""
        return self._make_mqtt_request("activateClient")

    def deactivate(self) -> dict[str, Any]:
        """Stop MQTT client."""
        return self._make_mqtt_request("deactivateClient")

    def configure(
        self,
        host: str,
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
        protocol: str = "tcp",
        keep_alive_interval: int = 60,
        client_id: str = "client1",
        clean_session: bool = True,
        auto_reconnect: bool = True,
        device_topic_prefix: str | None = None,
        use_tls: bool | None = None,
    ) -> dict[str, Any]:
        """Configure MQTT broker settings."""

        if not 1 <= port <= 65535:
            raise FeatureError("invalid_parameter", "port must be between 1 and 65535")
        if keep_alive_interval < 0:
            raise FeatureError(
                "invalid_parameter", "keep_alive_interval must be nonnegative"
            )

        if use_tls is not None and protocol not in {"tcp", "ssl"}:
            raise FeatureError(
                "invalid_parameter",
                "use_tls can only be combined with protocol 'tcp' or 'ssl'",
            )
        if use_tls is not None:
            protocol = "ssl" if use_tls else "tcp"
        if protocol not in {"tcp", "ssl", "ws", "wss"}:
            raise FeatureError(
                "invalid_parameter", "protocol must be 'tcp', 'ssl', 'ws', or 'wss'"
            )

        payload = {
            "server": {"host": host, "port": port, "protocol": protocol},
            "keepAliveInterval": keep_alive_interval,
            "clientId": client_id,
            "cleanSession": clean_session,
            "autoReconnect": auto_reconnect,
        }
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        if device_topic_prefix:
            payload["deviceTopicPrefix"] = device_topic_prefix
        return self._make_mqtt_request("configureClient", payload)

    def get_state(self) -> dict[str, Any]:
        """Get MQTT connection status."""
        return self._make_mqtt_request("getClientStatus")

    def set_state(self, state: str | dict[str, Any]) -> dict[str, Any]:
        """Set the client lifecycle state to ``active`` or ``inactive``."""
        requested_state = state
        if isinstance(state, dict):
            requested_state = state.get("status", {}).get("state")
        if requested_state == "active":
            return self.activate()
        if requested_state == "inactive":
            return self.deactivate()
        raise FeatureError("invalid_state", "state must be 'active' or 'inactive'")
