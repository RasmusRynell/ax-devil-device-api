from typing import Optional, Dict, Any

class AxisError(Exception):
    """Base exception for all ax-devil-device-api errors."""
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details or {}

class AuthenticationError(AxisError):
    """Authentication related errors."""
    pass

class ConfigurationError(AxisError):
    """Configuration related errors."""
    pass

class NetworkError(AxisError):
    """Network communication errors."""
    def __init__(self, code: str, message: str = None):
        super().__init__(code, message)

class SecurityError(AxisError):
    """Security-related errors like SSL/TLS issues."""
    def __init__(self, code: str, message: str = None, details: Optional[Dict[str, Any]] = None):
        if message is None:
            message = {
                "ssl_verification_failed": "SSL certificate verification failed",
                "ssl_error": "SSL error occurred",
                "cert_fingerprint_mismatch": "Certificate fingerprint mismatch",
                "protocol_error": "Protocol security error",
            }.get(code, "Security error")
        super().__init__(code, message, details)

class FeatureError(AxisError):
    """Feature-specific errors."""
    pass
