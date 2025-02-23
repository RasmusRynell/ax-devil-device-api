from typing import Any, Dict
import requests
from requests.auth import AuthBase
from abc import ABC, abstractmethod
from contextlib import contextmanager

from .config import DeviceConfig
from .auth import AuthHandler
from .protocol import ProtocolHandler
from .types import TransportResponse
from .endpoints import DeviceEndpoint
from ..utils.errors import NetworkError, AuthenticationError


class FeatureClientABC(ABC):
    """Abstract base class for all feature clients."""

    def __init__(self, device_client: 'DeviceClient') -> None:
        """Initialize with device client instance."""
        self.device = device_client

    def request(self, endpoint: DeviceEndpoint, **kwargs) -> TransportResponse:
        """Make a request to the device API."""
        return self.device.request(endpoint, **kwargs)

class DeviceClient:
    """Core client for device API communication.
    
    This class handles the low-level communication with the device API,
    including transport, authentication, and protocol handling. It is part
    of Layer 1 (Communications Layer) and should not contain any feature-specific
    code.

    Connection Management:
        - Uses requests.Session for connection pooling and cookie persistence
        - Maintains connection pool across requests
        - Automatically manages SSL/TLS session
        - Thread-safe session handling
    """

    # Transport-level headers that are part of Layer 1's responsibility
    _TRANSPORT_HEADERS = {
        "Accept": "application/json",
        "User-Agent": "ax-devil-device-api/1.0",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate"
    }

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config
        self.auth = AuthHandler(config)
        self.protocol = ProtocolHandler(config)
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure a requests Session with proper pooling."""
        session = requests.Session()
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,  # Number of connection pools to cache
            pool_maxsize=100,     # Max connections per pool
            max_retries=0,        # We handle retries at a higher level
            pool_block=False      # Don't block when pool is full
        )
        
        # Mount for both HTTP and HTTPS
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Set default headers
        session.headers.update(self._TRANSPORT_HEADERS)
        
        return session

    def __del__(self):
        """Ensure session is cleaned up."""
        if self._session:
            self._session.close()

    @contextmanager
    def new_session(self):
        """Context manager for creating a temporary new session.
        
        Useful for operations that need a clean session state.
        """
        old_session = self._session
        self._session = self._create_session()
        try:
            yield self
        finally:
            self._session.close()
            self._session = old_session

    def clear_session(self):
        """Clear and reset the current session.
        
        Useful when you want to clear any stored cookies or connection state.
        """
        self._session.close()
        self._session = self._create_session()

    def request(self, endpoint: DeviceEndpoint, **kwargs) -> TransportResponse:
        """Make a request to the device API using the session."""
        url = self.config.get_base_url()
        url = endpoint.build_url(url, kwargs.get("params"))
        
        # Merge transport headers with user headers, letting user headers take precedence
        headers = {}
        headers.update(kwargs.pop("headers", {}))

        def make_request(auth: AuthBase, request_func=None, **extra_kwargs) -> requests.Response:
            request_args = {
                "method": endpoint.method,
                "url": url,
                "headers": headers,
                "timeout": self.config.timeout,
                "auth": auth,
                **kwargs,
                **extra_kwargs
            }
            
            if request_func:
                return request_func(**request_args)
            return self._session.request(**request_args)

        try:
            # Wrap with protocol handling (SSL, etc)
            wrapped_request = lambda request_func=None, **extra_kwargs: self.auth.authenticate_request(
                lambda auth: make_request(auth, request_func, **extra_kwargs)
            )

            return self.protocol.execute_request(wrapped_request)

        except AuthenticationError as e:
            return TransportResponse.create_from_error(e)
            
        except requests.exceptions.Timeout as e:
            return TransportResponse.create_from_error(NetworkError(
                "request_timeout",
                f"Request timed out after {self.config.timeout}s"
            ))
            
        except requests.exceptions.RequestException as e:
            return TransportResponse.create_from_error(NetworkError(
                "request_failed",
                str(e)
            ))
