"""Analytics MQTT feature for managing analytics data publishers.

This module implements Layer 2 functionality for analytics MQTT operations,
providing a clean interface for managing analytics data publishers while
handling data normalization and error abstraction.
"""

from typing import Any, ClassVar
from urllib.parse import quote

import requests

from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


class AnalyticsMqttClient(FeatureClient):
    """Client for analytics MQTT operations.

    Provides functionality for:
    - Managing analytics data publishers
    - Retrieving available data sources
    - Configuring MQTT publishing settings
    """

    # API version and endpoints
    API_PATH_VERSION: ClassVar[str] = "v1"
    BASE_PATH: ClassVar[str] = f"/config/rest/analytics-mqtt/{API_PATH_VERSION}"

    # Endpoint definitions
    DATA_SOURCES_ENDPOINT = TransportEndpoint("GET", f"{BASE_PATH}/data_sources")
    PUBLISHERS_ENDPOINT = TransportEndpoint("GET", f"{BASE_PATH}/publishers")
    CREATE_PUBLISHER_ENDPOINT = TransportEndpoint("POST", f"{BASE_PATH}/publishers")
    REMOVE_PUBLISHER_ENDPOINT = TransportEndpoint(
        "DELETE", f"{BASE_PATH}/publishers/{{id}}"
    )

    # Common headers
    JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

    def _json_request_wrapper(self, endpoint: TransportEndpoint, **kwargs) -> Any:
        """Wrapper for request method to handle JSON parsing and error checking."""
        response = self.request(endpoint, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise FeatureError(
                "request_failed",
                f"Analytics MQTT request failed with HTTP {response.status_code}",
            ) from error
        if not response.content:
            return None
        try:
            json_response = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response", "Analytics MQTT returned invalid JSON"
            ) from error

        if not isinstance(json_response, dict):
            raise FeatureError(
                "invalid_response", "Analytics MQTT response must be a JSON object"
            )

        if json_response.get("status") != "success":
            error = json_response.get("error", "Unknown error")
            message = (
                error.get("message", "Unknown error")
                if isinstance(error, dict)
                else str(error)
            )
            raise FeatureError("invalid_response", message)
        return json_response.get("data")

    def get_data_sources(self) -> list[dict]:
        """Get available analytics data sources.

        Returns:
            List of data sources
        """
        data = self._json_request_wrapper(self.DATA_SOURCES_ENDPOINT)
        if isinstance(data, dict):
            data = data.get("data_sources", data.get("dataSources"))
        if not isinstance(data, list):
            raise FeatureError(
                "invalid_response", "Analytics MQTT data sources must be an array"
            )
        if not all(isinstance(item, dict) for item in data):
            raise FeatureError(
                "invalid_response", "Analytics MQTT data source entries must be objects"
            )
        return data

    def list_publishers(self) -> list[dict]:
        """List configured MQTT publishers.

        Returns:
            List of publisher configurations
        """
        data = self._json_request_wrapper(self.PUBLISHERS_ENDPOINT)
        if isinstance(data, dict):
            data = data.get("publishers")
        if not isinstance(data, list):
            raise FeatureError(
                "invalid_response", "Analytics MQTT publishers must be an array"
            )
        if not all(isinstance(item, dict) for item in data):
            raise FeatureError(
                "invalid_response",
                "Analytics MQTT publishers must contain only objects",
            )
        return data

    def create_publisher(
        self,
        id: str,
        data_source_key: str,
        mqtt_topic: str,
        qos: int = 0,
        retain: bool = False,
        use_topic_prefix: bool = False,
    ) -> Any:
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
        if qos not in {0, 1, 2}:
            raise FeatureError("invalid_parameter", "qos must be between 0 and 2")

        return self._json_request_wrapper(
            self.CREATE_PUBLISHER_ENDPOINT,
            json={
                "data": {
                    "id": id,
                    "data_source_key": data_source_key,
                    "mqtt_topic": mqtt_topic,
                    "qos": qos,
                    "retain": retain,
                    "use_topic_prefix": use_topic_prefix,
                }
            },
            headers=self.JSON_HEADERS,
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
        encoded_id = quote(publisher_id, safe="")

        endpoint = TransportEndpoint(
            self.REMOVE_PUBLISHER_ENDPOINT.method,
            self.REMOVE_PUBLISHER_ENDPOINT.path.format(id=encoded_id),
        )

        self._json_request_wrapper(endpoint, headers=self.JSON_HEADERS)
