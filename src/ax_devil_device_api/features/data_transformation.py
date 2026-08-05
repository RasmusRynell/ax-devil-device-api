"""Axis data transformation configuration client."""

from typing import Any, ClassVar
from urllib.parse import quote

import requests

from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


class DataTransformationClient(FeatureClient):
    """Client for data transformation operations.

    Manages data transforms that apply jq expressions to transform
    data from an input topic to an output topic.
    """

    # API version and endpoints
    API_VERSION: ClassVar[str] = "v1beta"
    BASE_PATH: ClassVar[str] = "/config/rest/data-transformation/v1beta"

    # Endpoint definitions
    AVAILABLE_TOPICS_ENDPOINT = TransportEndpoint(
        "GET", f"{BASE_PATH}/availableTopics/topics"
    )
    TRANSFORMS_ENDPOINT = TransportEndpoint("GET", f"{BASE_PATH}/transforms")
    CREATE_TRANSFORM_ENDPOINT = TransportEndpoint("POST", f"{BASE_PATH}/transforms")
    REMOVE_TRANSFORM_ENDPOINT = TransportEndpoint(
        "DELETE", f"{BASE_PATH}/transforms/{{id}}"
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
                f"Data transformation request failed with HTTP {response.status_code}",
            ) from error
        if not response.content:
            return None
        try:
            json_response = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response", "Data transformation returned invalid JSON"
            ) from error

        if not isinstance(json_response, dict):
            raise FeatureError(
                "invalid_response", "Data transformation response must be a JSON object"
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

    def get_available_topics(self) -> list[dict]:
        """Get available topics.

        Returns:
            List of topics
        """
        data = self._json_request_wrapper(self.AVAILABLE_TOPICS_ENDPOINT)
        if isinstance(data, dict):
            data = data.get("topics")
        if not isinstance(data, list):
            raise FeatureError(
                "invalid_response", "Data transformation topics must be an array"
            )
        if not all(isinstance(item, dict) for item in data):
            raise FeatureError(
                "invalid_response", "Data transformation topic entries must be objects"
            )
        return data

    def list_transforms(self) -> list[dict]:
        """List configured transforms.

        Returns:
            List of transform configurations
        """
        data = self._json_request_wrapper(self.TRANSFORMS_ENDPOINT)
        if isinstance(data, dict):
            data = data.get("transforms")
        if not isinstance(data, list):
            raise FeatureError(
                "invalid_response", "Data transformation transforms must be an array"
            )
        if not all(isinstance(item, dict) for item in data):
            raise FeatureError(
                "invalid_response", "Data transformation entries must be objects"
            )
        return data

    def create_transform(
        self, input_topic: str, output_topic: str, jq_expression: str
    ) -> None:
        """Create new transform.

        Args:
            input_topic: Input topic
            output_topic: Output topic
            jq_expression: JQ expression to apply
        """

        self._json_request_wrapper(
            self.CREATE_TRANSFORM_ENDPOINT,
            json={
                "data": {
                    "inputTopic": input_topic,
                    "jqExpression": jq_expression,
                    "outputTopic": output_topic,
                }
            },
            headers=self.JSON_HEADERS,
        )

    def remove_transform(self, output_topic: str) -> None:
        """Delete a transform by output topic.

        Args:
            output_topic: Output topic of transform to remove
        """
        if not output_topic:
            raise FeatureError("invalid_id", "Output topic is required")

        # The API maps dotted topic components to URL path segments.
        encoded_id = "/".join(
            quote(component, safe="") for component in output_topic.split(".")
        )

        endpoint = TransportEndpoint(
            self.REMOVE_TRANSFORM_ENDPOINT.method,
            self.REMOVE_TRANSFORM_ENDPOINT.path.format(id=encoded_id),
        )

        self._json_request_wrapper(endpoint, headers=self.JSON_HEADERS)
