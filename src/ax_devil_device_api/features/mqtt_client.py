"""MQTT client feature for managing broker configuration and client lifecycle on a device."""

import json
import requests

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, ClassVar, Tuple, Union
from .base import FeatureClient
from ..core.types import FeatureResponse
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError

@dataclass
class BrokerConfig:
    """MQTT broker configuration settings."""
    host: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = False
    keep_alive_interval: int = 60
    client_id: str = "client1"
    clean_session: bool = True
    auto_reconnect: bool = True
    device_topic_prefix: Optional[str] = None
    
    def validate(self) -> Optional[str]:
        """Validate configuration values."""
        if not self.host:
            return "Broker host is required"
        if not isinstance(self.port, int) or self.port < 1 or self.port > 65535:
            return "Port must be between 1 and 65535"
        if self.keep_alive_interval < 1:
            return "Keep alive interval must be positive"
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "use_tls": self.use_tls,
            "keep_alive_interval": self.keep_alive_interval,
            "client_id": self.client_id,
            "clean_session": self.clean_session,
            "auto_reconnect": self.auto_reconnect,
            "device_topic_prefix": self.device_topic_prefix
        }
    
    def to_payload(self) -> Dict[str, Any]:
        """Convert configuration to API payload."""
        payload = {
            "server": {
                "protocol": "tcp",
                "host": self.host,
                "port": self.port,
            },
            "keepAliveInterval": self.keep_alive_interval,
            "clientId": self.client_id,
            "cleanSession": self.clean_session,
            "autoReconnect": self.auto_reconnect
        }
        if self.username:
            payload["username"] = self.username
        if self.password:
            payload["password"] = self.password
        if self.device_topic_prefix:
            payload["deviceTopicPrefix"] = self.device_topic_prefix
        return payload

    @classmethod
    def create_from_response(cls, data: Dict[str, Any]) -> 'BrokerConfig':
        """Create broker config from API response data."""
        config = data.get("config")
        server = config.get("server")
        return cls(
            host=server.get("host", ""),
            port=server.get("port", 1883),
            keep_alive_interval=config.get("keepAliveInterval", 60),
            client_id=config.get("clientId", "client1"),
            clean_session=config.get("cleanSession", True),
            auto_reconnect=config.get("autoReconnect", True),
            device_topic_prefix=config.get("deviceTopicPrefix"),
            use_tls=server.get("protocol", "tcp").lower() == "ssl"
        )

@dataclass
class MqttStatus:
    """MQTT client status with connection details and error information."""
    # Valid status values
    STATUS_CONNECTED: ClassVar[str] = "connected"
    STATUS_CONNECTING: ClassVar[str] = "connecting"
    STATUS_DISCONNECTED: ClassVar[str] = "disconnected"
    STATUS_INACTIVE: ClassVar[str] = "inactive"
    STATUS_ERROR: ClassVar[str] = "error"
    STATUS_UNKNOWN: ClassVar[str] = "unknown"
    
    VALID_STATUSES: ClassVar[set[str]] = {
        STATUS_CONNECTED, STATUS_CONNECTING, STATUS_DISCONNECTED,
        STATUS_INACTIVE, STATUS_ERROR, STATUS_UNKNOWN
    }
    
    # State values
    STATE_ACTIVE: ClassVar[str] = "active"
    STATE_INACTIVE: ClassVar[str] = "inactive"
    STATE_ERROR: ClassVar[str] = "error"
    
    status: str
    state: str
    connected_to: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    config: Optional[BrokerConfig] = None

    def __post_init__(self):
        """Validate status value."""
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status value: {self.status}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status,
            "state": self.state,
            "connected_to": self.connected_to,
            "error": self.error,
            "config": self.config.to_dict() if self.config else None
        }

    @classmethod
    def create_from_response(cls, data: Dict[str, Any]) -> 'MqttStatus':
        """Create status instance from API response data. Raises ValueError if status is invalid."""
        status_data = data.get("data").get("status")
        
        # Map API status to our status enum
        connection_status = status_data.get("connectionStatus", cls.STATUS_UNKNOWN).lower()
        if connection_status not in cls.VALID_STATUSES:
            connection_status = cls.STATUS_UNKNOWN
            
        # Get state and create connected_to if connected
        state = status_data.get("state", cls.STATE_INACTIVE).lower()
        connected_to = None
        if connection_status == cls.STATUS_CONNECTED:
            config = data.get("data").get("config").get("server")
            if config:
                connected_to = {
                    "host": config.get("host"),
                    "port": config.get("port")
                }
        
        # Create broker config if available
        config = None
        if "config" in data.get("data"):
            config = BrokerConfig.create_from_response(data.get("data"))
            
        return cls(
            status=connection_status,
            state=state,
            connected_to=connected_to,
            config=config
        )

class MqttClient(FeatureClient):
    """Client for managing MQTT operations."""
    
    API_VERSION: ClassVar[str] = "1.0"
    MQTT_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/mqtt/client.cgi")

    def _parse_mqtt_response(self, response: requests.Response) -> FeatureResponse[Dict[str, Any]]:
        """Parse and validate MQTT API response."""
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "mqtt_error",
                f"MQTT operation failed: HTTP {response.status_code}",
                details={"response": response.text}
            ))
            
        try:
            data = json.loads(response.text)
            return FeatureResponse.ok(data)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_error",
                f"Failed to parse MQTT response: {str(e)}",
                details={"response": response.text}
            ))

    def _make_mqtt_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> FeatureResponse[Dict[str, Any]]:
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

    def activate(self) -> FeatureResponse[Dict[str, Any]]:
        """Start MQTT client."""
        return self._make_mqtt_request("activateClient")

    def deactivate(self) -> FeatureResponse[Dict[str, Any]]:
        """Stop MQTT client."""
        return self._make_mqtt_request("deactivateClient")

    def configure(self, config: BrokerConfig) -> FeatureResponse[Dict[str, Any]]:
        """Configure MQTT broker settings. Raises FeatureError if config is invalid."""
        error = config.validate()
        if error:
            return FeatureResponse.create_error(FeatureError(
                "invalid_config",
                f"Invalid broker configuration: {error}"
            ))
            
        return self._make_mqtt_request("configureClient", config.to_payload())

    def get_status(self) -> FeatureResponse[MqttStatus]:
        """Get MQTT connection status. Raises FeatureError if response parsing fails."""
        response = self._make_mqtt_request("getClientStatus")
        if not response.is_success:
            return FeatureResponse.create_error(response.error)
            
        try:
            status = MqttStatus.create_from_response(response.data)
            return FeatureResponse.ok(status)  # Return the MqttStatus object
        except ValueError as e:
            return FeatureResponse.create_error(FeatureError(
                "invalid_status",
                f"Invalid status value in response: {str(e)}"
            ))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "status_parse_error",
                f"Failed to parse status response: {str(e)}"
            ))