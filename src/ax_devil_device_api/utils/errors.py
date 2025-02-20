from typing import Optional, Dict, Any

class BaseError(Exception):
    """Base exception for all ax-devil-device-api errors."""
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details or {}

class AuthenticationError(BaseError):
    """Authentication related errors."""
    pass

class ConfigurationError(BaseError):
    """Configuration related errors."""
    pass

class NetworkError(BaseError):
    """Network communication errors."""
    def __init__(self, code: str, message: str = None):
        super().__init__(code, message)

class SecurityError(BaseError):
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

class FeatureError(BaseError):
    """Feature-specific errors."""
    pass
