"""Base classes for feature modules."""

from typing import Generic, TypeVar

import requests

from ..core.endpoints import TransportEndpoint
from ..core.transport_client import TransportClient

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
