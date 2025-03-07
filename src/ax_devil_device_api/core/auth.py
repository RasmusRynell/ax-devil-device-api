from typing import Optional, Callable
from requests import Response as RequestsResponse
from requests.auth import HTTPBasicAuth, HTTPDigestAuth, AuthBase
from .config import DeviceConfig, AuthMethod
from ..utils.errors import AuthenticationError
import requests
from .endpoints import TransportEndpoint

class AuthHandler:
    """Handles authentication for device requests, ensuring auth is detected only once per session."""

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config
        self._detected_method: Optional[AuthMethod] = None
        self._auth_object: Optional[AuthBase] = None  # Cache the auth object

    def authenticate_request(
        self, 
        session: requests.Session, 
        request_func: Callable[[AuthBase], RequestsResponse]
    ) -> RequestsResponse:
        """
        Authenticate the request by detecting and storing a working auth method.
        This is only done **once per session**, and future requests reuse the detected method.
        """
        if not self.config.username or not self.config.password:
            raise AuthenticationError("username_password_required", "Username and password are required")

        # If we've already determined a valid authentication method, use it directly
        if self._auth_object:
            return request_func(self._auth_object)

        # If cookies exist, assume authentication is still valid and attempt a request
        if session.cookies:
            response = request_func(None)
            if response.status_code != 401:
                return response

        # If a specific method is forced or cookies are not enough, test only that
        if self.config.auth_method != AuthMethod.AUTO:
            auth_obj = self._create_auth(self.config.auth_method)
            response = request_func(auth_obj)
            if response.status_code == 401:
                raise AuthenticationError(
                    "authentication_failed",
                    f"Authentication failed using {self.config.auth_method}"
                )
            self._cache_auth(auth_obj, self.config.auth_method, session)
            return response

        # Auto-detect authentication: Try Basic, then Digest
        for method in [AuthMethod.BASIC, AuthMethod.DIGEST]:
            auth_obj = self._create_auth(method)
            response = request_func(auth_obj)
            if response.status_code != 401:
                self._cache_auth(auth_obj, method, session)
                return response


        raise AuthenticationError("authentication_failed", "Failed to authenticate with any method")

    def _cache_auth(self, auth_obj: AuthBase, method: AuthMethod, session: requests.Session):
        """Cache the authentication method for future requests."""
        self._auth_object = auth_obj
        self._detected_method = method
        session.auth = auth_obj

    def _create_auth(self, method: AuthMethod) -> AuthBase:
        """Create and return an auth object for the specified method."""
        if method == AuthMethod.BASIC:
            return HTTPBasicAuth(self.config.username, self.config.password)
        elif method == AuthMethod.DIGEST:
            return HTTPDigestAuth(self.config.username, self.config.password)
        else:
            raise AuthenticationError("unsupported_auth_method", f"Unsupported authentication method: {method}")

    def send_request(
        self, 
        session: requests.Session, 
        endpoint: TransportEndpoint, 
        headers: dict, 
        kwargs: dict
    ) -> requests.Response:
        """
        Send an authenticated request to the endpoint.

        This method ensures the **first call detects authentication**, and future calls
        reuse the cached authentication method.
        """
        def make_request(auth: Optional[AuthBase]) -> requests.Response:
            """Perform a request using the provided authentication."""

            request_args = {
                "method": endpoint.method,
                "url": endpoint.build_url(self.config.get_base_url(), kwargs.get("params")),
                "headers": headers,
                "timeout": self.config.timeout,
                "auth": auth,  # Auth will be None if cookies are enough
                "verify": self.config.verify_ssl,
                **kwargs
            }
            return session.request(**request_args)

        return self.authenticate_request(session, make_request)
