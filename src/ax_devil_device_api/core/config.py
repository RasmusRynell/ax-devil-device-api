from dataclasses import dataclass
from enum import Enum
from typing import Optional
from ..utils.errors import ConfigurationError, SecurityError


class AuthMethod(Enum):
    """Authentication methods supported by the device."""
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
class DeviceConfig:
    """Device connection configuration."""
    host: str
    username: str
    password: str
    protocol: Protocol = Protocol.HTTPS
    port: Optional[int] = None
    auth_method: AuthMethod = AuthMethod.AUTO
    timeout: float = 10.0
    verify_ssl: bool = False  # Always False not implemented, set to True will raise an error
    allow_insecure: bool = False

    def __post_init__(self) -> None:
        """Validate configuration."""

        if self.port is None:
            self.port = self.protocol.default_port

        if self.port is not None and not (0 < self.port < 65536):
            raise ConfigurationError("invalid_port", f"Invalid port number: {self.port}")

        if self.protocol == Protocol.HTTP and not self.allow_insecure:
            raise ConfigurationError(
                "http_protocol_requested",
                "HTTP protocol requested but allow_insecure=False. "
                "Use DeviceConfig.http() to explicitly allow HTTP."
            )

        # Always disable SSL verification for HTTPS
        if self.protocol == Protocol.HTTPS:
            if self.verify_ssl:
                raise SecurityError(
                    "ssl_not_implemented",
                    "Secure SSL verification is not implemented. Use verify_ssl=False for insecure connections."
                )
            
            import warnings
            import urllib3
            warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

    @classmethod
    def http(cls, host: str, username: str, password: str, port: Optional[int] = None) -> 'DeviceConfig':
        """Create configuration for HTTP-only device."""
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
              verify_ssl: bool = False, 
              port: Optional[int] = None) -> 'DeviceConfig':
        """Create configuration for HTTPS device."""
        return cls(
            host=host,
            username=username,
            password=password,
            protocol=Protocol.HTTPS,
            port=port,
            verify_ssl=verify_ssl
        )

    def get_base_url(self) -> str:
        """Get the base URL for the device."""
        port_part = f":{self.port}" if self.port not in (80, 443) else ""
        return f"{self.protocol.value}://{self.host}{port_part}"
