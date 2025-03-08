"""Analytics MQTT feature for managing analytics data publishers.

This module implements Layer 2 functionality for analytics MQTT operations,
providing a clean interface for managing analytics data publishers while
handling data normalization and error abstraction.
"""

from typing import Dict, Any, List, ClassVar
from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from urllib.parse import quote

class AnalyticsMqttClient(FeatureClient):
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
        
        response.raise_for_status()

        return json_response.get("data")


    def get_data_sources(self) -> List[dict]:
        """Get available analytics data sources.
        
        Returns:
            List of data sources
        """
        return self._json_request_wrapper(self.DATA_SOURCES_ENDPOINT)

    def list_publishers(self) -> List[dict]:
        """List configured MQTT publishers.
        
        Returns:
            List of publisher configurations
        """
        return self._json_request_wrapper(self.PUBLISHERS_ENDPOINT)

    def create_publisher(self, 
                         id: str, 
                         data_source_key: str, 
                         mqtt_topic: str, 
                         qos: int = 0, 
                         retain: bool = False, 
                         use_topic_prefix: bool = False) -> None:
        """Create new MQTT publisher.
        
        Args:
            id: Publisher ID
            data_source_key: Data source key
            mqtt_topic: MQTT topic
            qos: Quality of service
            retain: Retain flag
            use_topic_prefix: Use topic prefix
            
        Returns:
            Created publisher configuration
        """

        response = self._json_request_wrapper(
            self.CREATE_PUBLISHER_ENDPOINT,
            json={"data": {
                "id": id,
                "data_source_key": data_source_key,
                "mqtt_topic": mqtt_topic,
                "qos": qos,
                "retain": retain,
                "use_topic_prefix": use_topic_prefix
            }},
            headers=self.JSON_HEADERS
        )

    def remove_publisher(self, publisher_id: str) -> None:
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
        json_response = response.json()
        if json_response.get("status") != "success":
            raise FeatureError("request_failed", json_response.get("error", "Unknown error"))
