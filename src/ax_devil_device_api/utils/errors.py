from typing import Optional, Dict, Any

class BaseError(Exception):
    """Base exception for all ax-devil-device-api errors."""
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def __str__(self):
        return f"\ncode: {self.code}\nmessage: {self.message}\ndetails: {self.details}"

class AuthenticationError(BaseError):
    """Authentication related errors."""
    pass

class ConfigurationError(BaseError):
    """Configuration related errors."""
    pass

class NetworkError(BaseError):
    """Network communication errors."""
    pass

class SecurityError(BaseError):
    """Security-related errors like SSL/TLS issues."""
    pass

class FeatureError(BaseError):
    """Feature-specific errors."""
    pass
