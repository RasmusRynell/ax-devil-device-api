"""Axis data transformation configuration client."""

from typing import Any, ClassVar, List
from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from urllib.parse import quote

class DataTransformationClient(FeatureClient):
    """Client for data transformation operations.

    Manages data transforms that apply jq expressions to transform
    data from an input topic to an output topic.
    """
    
    # API version and endpoints
    API_VERSION: ClassVar[str] = "v0alpha"
    BASE_PATH: ClassVar[str] = "/config/rest/data-transformation/v0alpha"
    
    # Endpoint definitions
    AVAILABLE_TOPICS_ENDPOINT = TransportEndpoint("GET", f"{BASE_PATH}/availableTopics/topics")
    TRANSFORMS_ENDPOINT = TransportEndpoint("GET", f"{BASE_PATH}/transforms")
    CREATE_TRANSFORM_ENDPOINT = TransportEndpoint("POST", f"{BASE_PATH}/transforms")
    REMOVE_TRANSFORM_ENDPOINT = TransportEndpoint("DELETE", f"{BASE_PATH}/transforms/{{id}}")

    # Common headers
    JSON_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def _json_request_wrapper(self, endpoint: TransportEndpoint, **kwargs) -> Any:
        """Wrapper for request method to handle JSON parsing and error checking."""
        response = self.request(endpoint, **kwargs)
        
        json_response = response.json()

        if json_response.get("status") != "success":
            raise FeatureError("invalid_response", json_response.get("error", "Unknown error"))
        if "data" not in json_response:
            raise FeatureError("parse_failed", "No data found in response")
        
        response.raise_for_status()

        return json_response.get("data")

    def get_available_topics(self) -> List[dict]:
        """Get available topics.
        
        Returns:
            List of topics
        """
        return self._json_request_wrapper(self.AVAILABLE_TOPICS_ENDPOINT)

    def list_transforms(self) -> List[dict]:
        """List configured transforms.
        
        Returns:
            List of transform configurations
        """
        return self._json_request_wrapper(self.TRANSFORMS_ENDPOINT)

    def create_transform(self, 
                         input_topic: str,
                         output_topic: str,
                         jq_expression: str) -> None:
        """Create new transform.
        
        Args:
            input_topic: Input topic
            output_topic: Output topic
            jq_expression: JQ expression to apply
        """

        self._json_request_wrapper(
            self.CREATE_TRANSFORM_ENDPOINT,
            json={"data": {
                "inputTopic": input_topic,
                "jqExpression": jq_expression,
                "outputTopic": output_topic
            }},
            headers=self.JSON_HEADERS
        )

    def remove_transform(self, output_topic: str) -> None:
        """Delete a transform by output topic.
        
        Args:
            output_topic: Output topic of transform to remove
        """
        if not output_topic:
            raise FeatureError("invalid_id", "Output topic is required")
            
        # URL encode the output topic to handle special characters, including '/'
        encoded_id = quote(output_topic, safe='')

        endpoint = TransportEndpoint(
            self.REMOVE_TRANSFORM_ENDPOINT.method,
            self.REMOVE_TRANSFORM_ENDPOINT.path.format(id=encoded_id)
        )

        response = self.request(
            endpoint, 
            headers=self.JSON_HEADERS
        )
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("status") != "success":
            raise FeatureError("request_failed", json_response.get("error", "Unknown error"))
