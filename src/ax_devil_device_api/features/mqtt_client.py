"""MQTT client feature for managing broker configuration and client lifecycle on a device."""

import json
import requests

from typing import Dict, Any, Optional, ClassVar
from .base import FeatureClient
from ..core.types import FeatureResponse
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError

class MqttClient(FeatureClient):
    """Client for managing MQTT operations."""
    
    API_VERSION: ClassVar[str] = "1.0"
    MQTT_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/mqtt/client.cgi")

    def _parse_mqtt_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse and validate MQTT API response."""
        if response.status_code != 200:
            raise FeatureError(
                "mqtt_error",
                f"MQTT operation failed: HTTP {response.status_code}",
                details={"response": response.text}
            )
        return json.loads(response.text).get("data")

    def _make_mqtt_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make MQTT API request with optional parameters."""
        payload = {
            "apiVersion": self.API_VERSION,
            "method": method
        }
        if params:
            payload["params"] = params
            
        response = self.request(
            self.MQTT_ENDPOINT,
            data=json.dumps(payload),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        
        return self._parse_mqtt_response(response)

    def activate(self) -> Dict[str, Any]:
        """Start MQTT client."""
        return self._make_mqtt_request("activateClient")

    def deactivate(self) -> Dict[str, Any]:
        """Stop MQTT client."""
        return self._make_mqtt_request("deactivateClient")

    def configure(self,  host: str,
                         port: int = 1883,
                         username: Optional[str] = None,
                         password: Optional[str] = None,
                         use_tls: bool = False,
                         keep_alive_interval: int = 60,
                         client_id: str = "client1",
                         clean_session: bool = True,
                         auto_reconnect: bool = True,
                         device_topic_prefix: Optional[str] = None):
        """Configure MQTT broker settings."""
        payload = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "useTLS": use_tls,
            "keepAliveInterval": keep_alive_interval,
            "clientId": client_id,
            "cleanSession": clean_session,
            "autoReconnect": auto_reconnect,
            "deviceTopicPrefix": device_topic_prefix
        }
        _ = self._make_mqtt_request("configureClient", payload)

    def get_status(self) -> Dict[str, Any]:
        """Get MQTT connection status."""
        return self._make_mqtt_request("getClientStatus").get("status")
    
    def get_config(self) -> Dict[str, Any]:
        """Get MQTT configuration."""
        return self._make_mqtt_request("getClientStatus").get("config")
