from typing import Callable, TypeVar, Any
import requests
import hashlib
from requests.exceptions import SSLError, ConnectionError
from .config import Protocol, CameraConfig
from .types import TransportResponse
from ..utils.errors import SecurityError, NetworkError

T = TypeVar('T')

def get_cert_fingerprint(cert_der: bytes) -> str:
    """Calculate SHA256 fingerprint of certificate."""
    return f"SHA256:{hashlib.sha256(cert_der).hexdigest()}"

class ProtocolHandler:
    """Handles protocol-specific connection logic."""

    def __init__(self, config: CameraConfig) -> None:
        """Initialize with camera configuration."""
        self.config = config

    def execute_request(self, request_func: Callable[..., requests.Response]) -> TransportResponse:
        """Execute a request with appropriate protocol handling."""

        try:
            # Configure SSL verification
            if self.config.protocol.is_secure and self.config.ssl:
                ssl_kwargs = {}
                
                # Basic verification
                if self.config.ssl.verify:
                    ssl_kwargs["verify"] = True
                    if self.config.ssl.ca_cert_path:
                        ssl_kwargs["verify"] = self.config.ssl.ca_cert_path
                else:
                    ssl_kwargs["verify"] = False
                
                # Client certificate
                if self.config.ssl.client_cert_path:
                    if self.config.ssl.client_key_path:
                        ssl_kwargs["cert"] = (self.config.ssl.client_cert_path, 
                                        self.config.ssl.client_key_path)
                    else:
                        ssl_kwargs["cert"] = self.config.ssl.client_cert_path
                
                # Certificate pinning
                if self.config.ssl.expected_fingerprint:
                    response = requests.get(f"{self.config.get_base_url()}/", 
                                         verify=False, 
                                         cert=ssl_kwargs.get("cert"))
                    if response.raw.connection.sock:
                        cert = response.raw.connection.sock.getpeercert(binary_form=True)
                        actual = get_cert_fingerprint(cert)
                        if actual != self.config.ssl.expected_fingerprint:
                            return TransportResponse.from_error(SecurityError(
                                "cert_fingerprint_mismatch",
                                f"Certificate fingerprint mismatch. Expected: {self.config.ssl.expected_fingerprint}, Got: {actual}"
                            ))
                
                response = request_func(**ssl_kwargs)
            else:
                response = request_func()
            
            return TransportResponse.from_response(response)
            
        except SSLError as e:
            if self.config.protocol == Protocol.HTTPS:
                if "CERTIFICATE_VERIFY_FAILED" in str(e):
                    return TransportResponse.from_error(SecurityError(
                        "ssl_verification_failed",
                        "SSL certificate verification failed"
                    ))
                return TransportResponse.from_error(SecurityError(
                    "ssl_error",
                    str(e)
                ))
            return TransportResponse.from_error(SecurityError(
                "protocol_error",
                f"SSL error with non-HTTPS protocol: {str(e)}"
            ))

        except ConnectionError as e:
            if "Connection refused" in str(e):
                return TransportResponse.from_error(NetworkError(
                    "connection_refused",
                    "Connection refused by remote host"
                ))
            return TransportResponse.from_error(NetworkError(
                "connection_error",
                str(e)
            ))
