"""Analytics MQTT feature for managing analytics data publishers.

This module implements Layer 2 functionality for analytics MQTT operations,
providing a clean interface for managing analytics data publishers while
handling data normalization and error abstraction.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, ClassVar, Generic, TypeVar
from .base import FeatureClient
from ..core.types import FeatureResponse, TransportResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError
from urllib.parse import quote

T = TypeVar('T')

@dataclass
class DataSource:
    """Analytics data source information.
    
    Attributes:
        key: Unique identifier for the data source
        name: Human-readable name
        description: Optional description of the data source
        type: Type of analytics data
        format: Data format (e.g., "json")
    """
    key: str
    name: str
    description: Optional[str] = None
    format: str = "json"

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> 'DataSource':
        """Create instance from API response data."""
        return cls(
            key=data.get("key", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            format=data.get("format", "json")
        )

@dataclass
class PublisherConfig:
    """MQTT analytics publisher configuration.
    
    Attributes:
        id: Unique identifier for the publisher
        data_source_key: Key identifying the analytics data source
        mqtt_topic: MQTT topic to publish to
        qos: Quality of Service level (0-2)
        retain: Whether to retain messages on the broker
        use_topic_prefix: Whether to use device topic prefix
    """
    id: str
    data_source_key: str
    mqtt_topic: str
    qos: int = 0
    retain: bool = False
    use_topic_prefix: bool = False

    def validate(self) -> Optional[str]:
        """Validate configuration values."""
        if not self.id:
            return "Publisher ID is required"
        if not self.data_source_key:
            return "Data source key is required"
        if not self.mqtt_topic:
            return "MQTT topic is required"
        if not isinstance(self.qos, int) or self.qos not in (0, 1, 2):
            return "QoS must be 0, 1, or 2"
        return None

    def to_payload(self) -> Dict[str, Any]:
        """Convert to API request payload."""
        return {
            "data": {
                "id": self.id,
                "data_source_key": self.data_source_key,
                "mqtt_topic": self.mqtt_topic,
                "qos": self.qos,
                "retain": self.retain,
                "use_topic_prefix": self.use_topic_prefix
            }
        }

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> 'PublisherConfig':
        """Create publisher config from API response data."""
        return cls(
            id=data.get("id", ""),
            data_source_key=data.get("data_source_key", ""),
            mqtt_topic=data.get("mqtt_topic", ""),
            qos=data.get("qos", 0),
            retain=data.get("retain", False),
            use_topic_prefix=data.get("use_topic_prefix", False)
        )

class AnalyticsMqttClient(FeatureClient[PublisherConfig]):
    """Client for analytics MQTT operations.
    
    Provides functionality for:
    - Managing analytics data publishers
    - Retrieving available data sources
    - Configuring MQTT publishing settings
    """
    
    # API version and endpoints
    API_VERSION: ClassVar[str] = "v1beta"
    BASE_PATH: ClassVar[str] = "/config/rest/analytics-mqtt/v1beta"
    
    # Endpoint definitions
    DATA_SOURCES_ENDPOINT = DeviceEndpoint("GET", f"{BASE_PATH}/data_sources")
    PUBLISHERS_ENDPOINT = DeviceEndpoint("GET", f"{BASE_PATH}/publishers")
    CREATE_PUBLISHER_ENDPOINT = DeviceEndpoint("POST", f"{BASE_PATH}/publishers")
    REMOVE_PUBLISHER_ENDPOINT = DeviceEndpoint("DELETE", f"{BASE_PATH}/publishers/{{id}}")

    # Common headers
    JSON_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def get_feature_name(self) -> str:
        """Get feature identifier."""
        return "analytics_mqtt"

    def _parse_json_response(self, response: TransportResponse, expected_type: type[T] = dict) -> FeatureResponse[T]:
        """Parse and validate JSON API response.
        
        Args:
            response: Raw transport response
            expected_type: Expected type of the parsed data
            
        Returns:
            FeatureResponse containing parsed data or error
        """
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
        
        raw_response = response.raw_response
        if not (200 <= raw_response.status_code < 300):
            return FeatureResponse.create_error(FeatureError(
                "request_failed",
                f"Request failed: HTTP {raw_response.status_code}",
                details={"response": raw_response.text}
            ))
            
        try:
            data = response.raw_response.json().get("data")
            if not isinstance(data, expected_type):
                return FeatureResponse.create_error(FeatureError(
                    "invalid_response",
                    f"Expected {expected_type.__name__}, got {type(data).__name__}"
                ))
            return FeatureResponse.ok(data)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_failed",
                f"Failed to parse response: {str(e)}",
                details={"response": raw_response.text}
            ))

    def get_data_sources(self) -> FeatureResponse[List[DataSource]]:
        """Get available analytics data sources.
        
        Returns:
            FeatureResponse containing list of data sources
        """
        response = self.request(
            self.DATA_SOURCES_ENDPOINT,
            headers=self.JSON_HEADERS
        )

        parsed = self._parse_json_response(response, list)
        if not parsed.success:
            return FeatureResponse.create_error(parsed.error)
            
        try:
            sources = [DataSource.from_response(source) for source in parsed.data]
            return FeatureResponse.ok(sources)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_failed",
                f"Failed to parse data sources: {str(e)}"
            ))

    def list_publishers(self) -> FeatureResponse[List[PublisherConfig]]:
        """List configured MQTT publishers.
        
        Returns:
            FeatureResponse containing list of publisher configurations
        """
        response = self.request(
            self.PUBLISHERS_ENDPOINT,
            headers=self.JSON_HEADERS
        )
        
        parsed = self._parse_json_response(response, list)
        if not parsed.success:
            return FeatureResponse.create_error(parsed.error)
            
        try:
            publishers = [PublisherConfig.from_response(p) for p in parsed.data]
            return FeatureResponse.ok(publishers)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_failed",
                f"Failed to parse publishers: {str(e)}"
            ))

    def create_publisher(self, config: PublisherConfig) -> FeatureResponse[PublisherConfig]:
        """Create new MQTT publisher.
        
        Args:
            config: Publisher configuration
            
        Returns:
            FeatureResponse containing created publisher configuration
        """
        error = config.validate()
        if error:
            return FeatureResponse.create_error(FeatureError(
                "invalid_config",
                f"Invalid publisher configuration: {error}"
            ))
            
        response = self.request(
            self.CREATE_PUBLISHER_ENDPOINT,
            json=config.to_payload(),
            headers=self.JSON_HEADERS
        )
        
        parsed = self._parse_json_response(response, dict)
        if not parsed.success:
            return FeatureResponse.create_error(parsed.error)
            
        try:
            return FeatureResponse.ok(PublisherConfig.from_response(parsed.data))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_failed",
                f"Failed to parse created publisher: {str(e)}"
            ))

    def remove_publisher(self, publisher_id: str) -> FeatureResponse[bool]:
        """Delete MQTT publisher by ID.
        
        Args:
            publisher_id: ID of publisher to remove
            
        Returns:
            FeatureResponse indicating success/failure
        """
        if not publisher_id:
            return FeatureResponse.create_error(FeatureError(
                "invalid_id",
                "Publisher ID is required"
            ))
            
        # URL encode the publisher ID to handle special characters, including '/'
        encoded_id = quote(publisher_id, safe='')

        endpoint = DeviceEndpoint(
            self.REMOVE_PUBLISHER_ENDPOINT.method,
            self.REMOVE_PUBLISHER_ENDPOINT.path.format(id=encoded_id)
        )

        response = self.request(
            endpoint, 
            headers=self.JSON_HEADERS
        )
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)

        if not (200 <= response.raw_response.status_code < 300):
            return FeatureResponse.create_error(FeatureError(
                "request_failed",
                f"Failed to remove publisher: HTTP {response.raw_response.status_code}"
            ))
            
        return FeatureResponse.ok(True)