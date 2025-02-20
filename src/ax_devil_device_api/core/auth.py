from typing import Optional, Callable, Any
from requests import Response as RequestsResponse
from requests.auth import HTTPBasicAuth, HTTPDigestAuth, AuthBase
from .config import DeviceConfig, AuthMethod
from ..utils.errors import AuthenticationError


class AuthHandler:
    """Handles authentication for device requests."""

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config
        self._detected_method: Optional[AuthMethod] = None

    def authenticate_request(self, request_func) -> RequestsResponse:
        """Handle authentication for a request, including retries and method detection.

        Args:
            request_func: Function that takes an auth object and returns a response

        Returns:
            The authenticated response

        Raises:
            AuthenticationError: If authentication fails
        """
        if not self.config.username or not self.config.password:
            raise AuthenticationError("Username and password are required")

        # For explicit auth methods, just try once
        if self.config.auth_method != AuthMethod.AUTO:
            response = request_func(self._create_auth(self.config.auth_method))
            if response.status_code == 401:
                raise AuthenticationError(
                    f"Authentication failed using {self.config.auth_method}")
            return response

        # For auto auth, try each method once, caching the successful method
        if self._detected_method is None or self._detected_method == AuthMethod.BASIC:
            response = request_func(self._create_auth(AuthMethod.BASIC))
            if response.status_code != 401:
                self._detected_method = AuthMethod.BASIC
                return response

        if self._detected_method is None or self._detected_method == AuthMethod.DIGEST:
            response = request_func(self._create_auth(AuthMethod.DIGEST))
            if response.status_code != 401:
                self._detected_method = AuthMethod.DIGEST
                return response

        raise AuthenticationError("Failed to authenticate with any method")

    def _create_auth(self, method: AuthMethod) -> AuthBase:
        """Create an auth object for the specified method."""
        if method == AuthMethod.BASIC:
            return HTTPBasicAuth(self.config.username, self.config.password)
        elif method == AuthMethod.DIGEST:
            return HTTPDigestAuth(self.config.username, self.config.password)
        else:
            raise AuthenticationError(
                f"Unsupported authentication method: {method}")
