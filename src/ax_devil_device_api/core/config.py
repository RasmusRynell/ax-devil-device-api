from dataclasses import dataclass
from enum import Enum
from typing import Optional
from ..utils.errors import ConfigurationError


class AuthMethod(Enum):
    """Authentication methods supported by the camera."""
    AUTO = "auto"
    BASIC = "basic"
    DIGEST = "digest"


class Protocol(Enum):
    """Connection protocol."""
    HTTPS = "https"
    HTTP = "http"

    @property
    def default_port(self) -> int:
        """Get the default port for this protocol."""
        return 443 if self == Protocol.HTTPS else 80

    @property
    def is_secure(self) -> bool:
        """Whether this is a secure protocol."""
        return self == Protocol.HTTPS


@dataclass
class SSLConfig:
    """SSL/TLS configuration.
    
    Attributes:
        verify: Whether to verify SSL certificates
        ca_cert_path: Path to custom CA certificate bundle
        client_cert_path: Path to client certificate for mutual TLS
        client_key_path: Path to client private key
        expected_fingerprint: Expected certificate fingerprint for pinning
    """
    verify: bool = True
    ca_cert_path: Optional[str] = None
    client_cert_path: Optional[str] = None
    client_key_path: Optional[str] = None
    expected_fingerprint: Optional[str] = None


@dataclass
class CameraConfig:
    """Camera connection configuration.

    Common usage:
        # For HTTPS cameras with CA-signed certificate:
        config = CameraConfig.https("camera.local", "user", "pass")

        # For HTTPS cameras with self-signed certificate (development only):
        config = CameraConfig.https("camera.local", "user", "pass", verify_ssl=False)
        
        # For HTTPS cameras with custom CA certificate:
        config = CameraConfig.https("camera.local", "user", "pass", ca_cert="/path/to/ca.crt")
        
        # For HTTPS cameras with certificate pinning:
        config = CameraConfig.https("camera.local", "user", "pass", cert_fingerprint="SHA256:...")
    """
    host: str
    username: str
    password: str
    protocol: Protocol = Protocol.HTTPS
    port: Optional[int] = None
    auth_method: AuthMethod = AuthMethod.AUTO
    timeout: float = 10.0
    ssl: Optional[SSLConfig] = None
    allow_insecure: bool = False

    def __post_init__(self) -> None:
        """Validate configuration."""

        if self.port is None:
            self.port = self.protocol.default_port

        if self.ssl is None and self.protocol.is_secure:
            self.ssl = SSLConfig()

        if self.port is not None and not (0 < self.port < 65536):
            raise ConfigurationError(f"Invalid port number: {self.port}")

        if self.protocol == Protocol.HTTP and not self.allow_insecure:
            raise ConfigurationError(
                "HTTP protocol requested but allow_insecure=False. "
                "Use CameraConfig.http() to explicitly allow HTTP."
            )

        if self.protocol == Protocol.HTTPS and not self.ssl.verify:
            import warnings
            import urllib3
            warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

    @classmethod
    def http(cls, host: str, username: str, password: str, port: Optional[int] = None) -> 'CameraConfig':
        """Create configuration for HTTP-only camera."""
        return cls(
            host=host,
            username=username,
            password=password,
            protocol=Protocol.HTTP,
            port=port,
            allow_insecure=True
        )

    @classmethod
    def https(cls, host: str, username: str, password: str, *, 
              verify_ssl: bool = True, 
              port: Optional[int] = None,
              ca_cert: Optional[str] = None,
              cert_fingerprint: Optional[str] = None,
              client_cert: Optional[str] = None,
              client_key: Optional[str] = None) -> 'CameraConfig':
        """Create configuration for HTTPS camera.
        
        Args:
            host: Camera hostname or IP
            username: Authentication username
            password: Authentication password
            verify_ssl: Whether to verify SSL certificates
            port: Optional custom port (default: 443)
            ca_cert: Path to custom CA certificate bundle
            cert_fingerprint: Expected certificate fingerprint for pinning
            client_cert: Path to client certificate for mutual TLS
            client_key: Path to client private key
        """
        return cls(
            host=host,
            username=username,
            password=password,
            protocol=Protocol.HTTPS,
            port=port,
            ssl=SSLConfig(
                verify=verify_ssl,
                ca_cert_path=ca_cert,
                expected_fingerprint=cert_fingerprint,
                client_cert_path=client_cert,
                client_key_path=client_key
            )
        )

    def get_base_url(self) -> str:
        """Get the base URL for the camera."""
        port_part = f":{self.port}" if self.port not in (80, 443) else ""
        return f"{self.protocol.value}://{self.host}{port_part}"
