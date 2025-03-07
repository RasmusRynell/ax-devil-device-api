from typing import Callable, TypeVar
import requests
from requests.exceptions import SSLError, ConnectionError
from .config import Protocol, DeviceConfig
from ..utils.errors import SecurityError, NetworkError

T = TypeVar('T')

class ProtocolHandler:
    """Handles protocol-specific connection logic."""

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config

    def get_ssl_kwargs(self) -> dict:
        """Build SSL-related kwargs for requests."""
        ssl_kwargs = {}
        
        # Always set verify=False for HTTPS
        if self.config.protocol.is_secure:
            ssl_kwargs["verify"] = False
            
        return ssl_kwargs

    def execute_request(self, request_func: Callable[..., requests.Response]) -> requests.Response:
        """
        Execute a request with appropriate protocol handling.
        For HTTPS, always uses insecure mode (verify=False).
        """
        try:
            ssl_kwargs = self.get_ssl_kwargs() if self.config.protocol.is_secure else {}
            
            # If verify_ssl=True was set, the DeviceConfig.__post_init__ should have already
            # raised an error, but we'll check again just to be safe
            if self.config.protocol.is_secure and self.config.verify_ssl:
                raise SecurityError(
                    "ssl_not_implemented",
                    "Secure SSL verification is not implemented. Use verify_ssl=False for insecure connections."
                )
                
            return request_func(**ssl_kwargs)

        except SSLError as e:
            raise SecurityError("ssl_error", "SSL error occurred", str(e))

        except ConnectionError as e:
            error_code = "connection_refused" if "Connection refused" in str(e) else "connection_error"
            raise NetworkError(error_code, "Connection error", str(e))
