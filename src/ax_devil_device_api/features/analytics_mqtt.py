"""Analytics MQTT feature for managing analytics data publishers.

This module implements Layer 2 functionality for analytics MQTT operations,
providing a clean interface for managing analytics data publishers while
handling data normalization and error abstraction.
"""

import requests
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, ClassVar, Generic, TypeVar
from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from urllib.parse import quote

T = TypeVar('T')

@dataclass
class DataSource:
    """Analytics data source information.
    
    Attributes:
        key: Unique identifier for the data source
    """
    key: str

    @classmethod
    def create_from_response(cls, data: Dict[str, Any]) -> 'DataSource':
        """Create instance from API response data."""
        return cls(
            key=data.get("key")
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
    def create_from_response(cls, data: Dict[str, Any]) -> 'PublisherConfig':
        """Create publisher config from API response data."""
        return cls(
            id=data.get("id"),
            data_source_key=data.get("data_source_key"),
            mqtt_topic=data.get("mqtt_topic"),
            qos=data.get("qos"),
            retain=data.get("retain"),
            use_topic_prefix=data.get("use_topic_prefix")
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
    DATA_SOURCES_ENDPOINT = TransportEndpoint("GET", f"{BASE_PATH}/data_sources")
    PUBLISHERS_ENDPOINT = TransportEndpoint("GET", f"{BASE_PATH}/publishers")
    CREATE_PUBLISHER_ENDPOINT = TransportEndpoint("POST", f"{BASE_PATH}/publishers")
    REMOVE_PUBLISHER_ENDPOINT = TransportEndpoint("DELETE", f"{BASE_PATH}/publishers/{{id}}")

    # Common headers
    JSON_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def _json_request_wrapper(self, endpoint: TransportEndpoint, **kwargs) -> Dict[str, Any]:
        """Wrapper for request method to handle JSON parsing and error checking."""
        response = self.request(endpoint, **kwargs)
        
        json_response = response.json()

        if json_response.get("status") != "success":
            raise FeatureError("request_failed", json_response.get("error", "Unknown error"))
        if "data" not in json_response:
            raise FeatureError("parse_failed", "No data found in response")
        print("TEST5")
        response.raise_for_status()
        return json_response.get("data")


    def get_data_sources(self) -> List[DataSource]:
        """Get available analytics data sources.
        
        Returns:
            List of data sources
        """
        data_sources = self._json_request_wrapper(self.DATA_SOURCES_ENDPOINT)
        return [DataSource.create_from_response(source) for source in data_sources]

    def list_publishers(self) -> List[PublisherConfig]:
        """List configured MQTT publishers.
        
        Returns:
            List of publisher configurations
        """
        publishers = self._json_request_wrapper(self.PUBLISHERS_ENDPOINT)
        return [PublisherConfig.create_from_response(p) for p in publishers]

    def create_publisher(self, config: PublisherConfig) -> PublisherConfig:
        """Create new MQTT publisher.
        
        Args:
            config: Publisher configuration
            
        Returns:
            Created publisher configuration
        """
        print("TEST6")
        response = self._json_request_wrapper(
            self.CREATE_PUBLISHER_ENDPOINT,
            json=config.to_payload(),
            headers=self.JSON_HEADERS
        )
        print("TEST7")
        return PublisherConfig.create_from_response(response)

    def remove_publisher(self, publisher_id: str) -> bool:
        """Delete MQTT publisher by ID.
        
        Args:
            publisher_id: ID of publisher to remove
            
        Returns:
            True if publisher was removed, False otherwise
        """
        if not publisher_id:
            raise FeatureError("invalid_id", "Publisher ID is required")
            
        # URL encode the publisher ID to handle special characters, including '/'
        encoded_id = quote(publisher_id, safe='')

        endpoint = TransportEndpoint(
            self.REMOVE_PUBLISHER_ENDPOINT.method,
            self.REMOVE_PUBLISHER_ENDPOINT.path.format(id=encoded_id)
        )

        response = self.request(
            endpoint, 
            headers=self.JSON_HEADERS
        )
        response.raise_for_status()
        return True
