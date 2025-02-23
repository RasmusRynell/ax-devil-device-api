from typing import Callable, TypeVar, Any
import requests
import hashlib
import ssl
import socket
from requests.exceptions import SSLError, ConnectionError
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context
from .config import Protocol, DeviceConfig
from .types import TransportResponse
from ..utils.errors import SecurityError, NetworkError

T = TypeVar('T')

class AxisSSLAdapter(HTTPAdapter):
    """Custom SSL Adapter that verifies cert chain but not hostname."""
    
    def __init__(self, ca_cert_path: str = None):
        self.ca_cert_path = ca_cert_path
        super().__init__()

    def init_poolmanager(self, connections, maxsize, block=False):
        context = create_urllib3_context()
        context.load_verify_locations(cafile=self.ca_cert_path)
        context.check_hostname = False
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            assert_hostname=False  # Disable hostname verification at the urllib3 level
        )

def get_cert_fingerprint(cert_der: bytes) -> str:
    """Calculate SHA256 fingerprint of certificate."""
    return f"SHA256:{hashlib.sha256(cert_der).hexdigest()}"

def fetch_server_cert(host: str, port: int, timeout: float = 5.0) -> bytes:
    """
    Securely fetch the server certificate using a dedicated SSL connection.
    A timeout is set to avoid indefinite blocking.
    """
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            return ssock.getpeercert(binary_form=True)

class ProtocolHandler:
    """Handles protocol-specific connection logic."""

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config

    def get_ssl_kwargs(self) -> dict:
        """Build SSL-related kwargs for requests."""
        ssl_kwargs = {}

        if self.config.ssl.verify:
            if self.config.ssl.ca_cert_path:
                # When using a custom CA cert, we need to verify against it
                ssl_kwargs["verify"] = self.config.ssl.ca_cert_path
                # Create a session with our custom adapter
                session = requests.Session()
                session.mount('https://', AxisSSLAdapter(self.config.ssl.ca_cert_path))
                ssl_kwargs["session"] = session
            else:
                ssl_kwargs["verify"] = True
        else:
            ssl_kwargs["verify"] = False

        if self.config.ssl.client_cert_path:
            ssl_kwargs["cert"] = (
                (self.config.ssl.client_cert_path, self.config.ssl.client_key_path)
                if self.config.ssl.client_key_path else self.config.ssl.client_cert_path
            )

        return ssl_kwargs

    def execute_request(self, request_func: Callable[..., requests.Response]) -> TransportResponse:
        """
        Execute a request with appropriate protocol handling, including
        SSL configuration and certificate pinning.
        """
        try:
            ssl_kwargs = self.get_ssl_kwargs() if self.config.protocol.is_secure and self.config.ssl else {}
            session = ssl_kwargs.pop("session", None)

            # Certificate Pinning: Securely fetch the certificate and verify its fingerprint.
            if self.config.ssl:
                if self.config.ssl.expected_fingerprint:
                    parsed_url = urlparse(self.config.get_base_url())
                    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
                    cert = fetch_server_cert(parsed_url.hostname, port)
                    actual = get_cert_fingerprint(cert)
                    if actual != self.config.ssl.expected_fingerprint:
                        return TransportResponse.create_from_error(SecurityError(
                            "cert_fingerprint_mismatch",
                            f"Certificate fingerprint mismatch. Expected: {self.config.ssl.expected_fingerprint}, Got: {actual}"
                        ))

            if session:
                # If we have a custom session (for SSL verification), use it
                def session_request(**kwargs):
                    return session.request(
                        kwargs.pop("method"),
                        kwargs.pop("url"),
                        **kwargs
                    )
                response = request_func(session_request, **ssl_kwargs)
            else:
                # Otherwise use the normal request function
                response = request_func(**ssl_kwargs)

            return TransportResponse.create_from_response(response)

        except SSLError as e:
            error_code = "ssl_verification_failed" if "CERTIFICATE_VERIFY_FAILED" in str(e) else "ssl_error"
            return TransportResponse.create_from_error(SecurityError(error_code, str(e)))

        except ConnectionError as e:
            error_code = "connection_refused" if "Connection refused" in str(e) else "connection_error"
            return TransportResponse.create_from_error(NetworkError(error_code, str(e)))
