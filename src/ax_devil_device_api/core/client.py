from typing import Any, Dict
import requests
from requests.auth import AuthBase
from abc import ABC, abstractmethod

from .config import CameraConfig
from .auth import AuthHandler
from .protocol import ProtocolHandler
from .types import TransportResponse
from .endpoints import CameraEndpoint
from ..utils.errors import NetworkError, AuthenticationError


class FeatureClient(ABC):
    """Abstract base class for all feature clients."""

    def __init__(self, camera_client: 'CameraClient') -> None:
        """Initialize with camera client instance."""
        self.camera = camera_client

    def request(self, endpoint: CameraEndpoint, **kwargs) -> TransportResponse:
        """Make a request to the camera API."""
        return self.camera.request(endpoint, **kwargs)

class CameraClient:
    """Core client for camera API communication.
    
    This class handles the low-level communication with the camera API,
    including transport, authentication, and protocol handling. It is part
    of Layer 1 (Communications Layer) and should not contain any feature-specific
    code.
    """

    # Transport-level headers that are part of Layer 1's responsibility
    _TRANSPORT_HEADERS = {
        "Accept": "application/json",
        "User-Agent": "ax-devil-device-api/1.0",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate"
    }

    def __init__(self, config: CameraConfig) -> None:
        """Initialize with camera configuration."""
        self.config = config
        self.auth = AuthHandler(config)
        self.protocol = ProtocolHandler(config)

    def request(self, endpoint: CameraEndpoint, **kwargs) -> TransportResponse:
        """Make a raw request to the camera API."""
        url = self.config.get_base_url()
        url = endpoint.build_url(url, kwargs.get("params"))
        
        # Merge transport headers with user headers, letting user headers take precedence
        headers = self._TRANSPORT_HEADERS.copy()
        headers.update(kwargs.pop("headers", {}))

        def make_request(auth: AuthBase, **extra_kwargs) -> requests.Response:
            return requests.request(
                endpoint.method,
                url,
                headers=headers,
                timeout=self.config.timeout,
                auth=auth,
                **kwargs,
                **extra_kwargs
            )

        try:
            # First wrap with protocol handling (SSL, etc)
            wrapped_request = lambda **extra_kwargs: self.auth.authenticate_request(
                lambda auth: make_request(auth, **extra_kwargs)
            )

            return self.protocol.execute_request(wrapped_request)

        except AuthenticationError as e:
            return TransportResponse.from_error(e)
            
        except requests.exceptions.Timeout as e:
            return TransportResponse.from_error(NetworkError(
                "request_timeout",
                f"Request timed out after {self.config.timeout}s"
            ))
            
        except requests.exceptions.RequestException as e:
            return TransportResponse.from_error(NetworkError(
                "request_failed",
                str(e)
            ))
