"""Base classes for feature modules."""

from typing import Any, Generic, TypeVar

import requests

from ..core.endpoints import TransportEndpoint
from ..core.transport_client import TransportClient
from ..utils.errors import FeatureError

T = TypeVar("T")


class FeatureClient(Generic[T]):
    """Base class for device feature clients.

    Provides common functionality used across feature modules:
    - Parameter parsing
    - Error handling
    - Response formatting
    """

    def __init__(self, device_client: TransportClient) -> None:
        """Initialize with device client instance."""
        self.device = device_client

    def request(self, endpoint: TransportEndpoint, **kwargs) -> requests.Response:
        """Make a request to the device API."""
        return self.device.request(endpoint, **kwargs)

    def request_no_auth(
        self, endpoint: TransportEndpoint, **kwargs
    ) -> requests.Response:
        """Make an unauthenticated request to the device API."""
        return self.device.request_no_auth(endpoint, **kwargs)

    def request_after_challenge(
        self,
        endpoint: TransportEndpoint,
        challenge_response: requests.Response,
        **kwargs,
    ) -> requests.Response:
        """Make one authenticated request using a received challenge."""
        return self.device.request_after_challenge(
            endpoint, challenge_response, **kwargs
        )

    @staticmethod
    def parse_json_api_response(
        response: requests.Response, operation: str, expected_method: str
    ) -> dict[str, Any]:
        """Validate a successful JSON API response and its method envelope."""
        if response.status_code != 200:
            raise FeatureError(
                "request_failed", f"{operation} failed: HTTP {response.status_code}"
            )
        try:
            payload = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response", f"{operation} response is not valid JSON"
            ) from error
        if not isinstance(payload, dict):
            raise FeatureError(
                "invalid_response", f"{operation} response is not an object"
            )
        if "error" in payload:
            error = payload["error"]
            if not isinstance(error, dict):
                raise FeatureError(
                    "api_error", f"{operation} returned a malformed error"
                )
            raise FeatureError(
                "api_error",
                str(error.get("message", "Unknown API error")),
                details=error,
            )
        if payload.get("method") != expected_method:
            raise FeatureError(
                "invalid_response",
                f"{operation} response has unexpected method; expected {expected_method}",
            )
        return payload
