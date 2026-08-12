from contextlib import contextmanager

import requests

from ..utils.errors import NetworkError
from .auth import AuthHandler, _NoAuth
from .config import DeviceConfig
from .debug import emit_request_debug_info
from .endpoints import TransportEndpoint


class TransportClient:
    """Core client for device API communication.

    This class handles the low-level communication with the device API,
    including transport, authentication, and protocol handling. It is part
    of Layer 1 (Communications Layer) and should not contain any feature-specific
    code.

    Connection Management:
        - Uses requests.Session for connection pooling and cookie persistence
        - Maintains connection pool across requests
        - Automatically manages SSL/TLS session
        - Thread-safe session handling
    """

    # Transport-level headers that are part of Layer 1's responsibility
    _TRANSPORT_HEADERS = {  # noqa: RUF012 - immutable by convention
        "Accept": "application/json",
        "User-Agent": "ax-devil-device-api/1.0",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate",
    }

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config
        self.auth = AuthHandler(config)
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure a requests Session with proper pooling."""
        session = requests.Session()

        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,  # Number of connection pools to cache
            pool_maxsize=100,  # Max connections per pool
            max_retries=0,  # We handle retries at a higher level
            pool_block=False,  # Don't block when pool is full
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update(self._TRANSPORT_HEADERS)
        return session

    def __del__(self):
        """Ensure session is cleaned up."""
        if self._session:
            self._session.close()

    @contextmanager
    def new_session(self):
        """Context manager for creating a temporary new session.

        Useful for operations that need a clean session state.
        """
        old_session = self._session
        self.auth.reset_session_state(old_session)
        self._session = self._create_session()
        try:
            yield self
        finally:
            new_session = self._session
            new_session.close()
            self._session = old_session
            self.auth.reset_session_state(new_session, old_session)

    def clear_session(self):
        """Clear and reset the current session.

        Useful when you want to clear any stored cookies or connection state.
        """
        old_session = self._session
        old_session.close()
        self._session = self._create_session()
        self.auth.reset_session_state(old_session, self._session)

    def request(self, endpoint: TransportEndpoint, **kwargs) -> requests.Response:
        """Make a request to the device API using the session."""
        headers = {**self._TRANSPORT_HEADERS, **kwargs.pop("headers", {})}

        try:
            return self.auth.send_request(self._session, endpoint, headers, kwargs)

        except requests.exceptions.Timeout:
            raise NetworkError(
                "request_timeout", f"Request timed out after {self.config.timeout}s"
            )

        except requests.exceptions.SSLError as error:
            raise NetworkError(
                "ssl_verification_failed",
                "TLS certificate verification failed",
                str(error),
            ) from error
        except requests.exceptions.RequestException as error:
            raise NetworkError(
                "request_failed",
                "Request failed",
                str(error),
            ) from error

    def request_after_challenge(
        self,
        endpoint: TransportEndpoint,
        challenge_response: requests.Response,
        **kwargs,
    ) -> requests.Response:
        """Make one authenticated request from a previously received challenge."""
        headers = {**self._TRANSPORT_HEADERS, **kwargs.pop("headers", {})}

        try:
            return self.auth.send_request_after_challenge(
                self._session, endpoint, headers, kwargs, challenge_response
            )

        except requests.exceptions.Timeout:
            raise NetworkError(
                "request_timeout", f"Request timed out after {self.config.timeout}s"
            )

        except requests.exceptions.SSLError as error:
            raise NetworkError(
                "ssl_verification_failed",
                "TLS certificate verification failed",
                str(error),
            ) from error
        except requests.exceptions.RequestException as error:
            raise NetworkError(
                "request_failed",
                "Request failed",
                str(error),
            ) from error
        finally:
            challenge_response.close()

    def request_no_auth(
        self, endpoint: TransportEndpoint, **kwargs
    ) -> requests.Response:
        """Make an unauthenticated request to the device API.

        Bypasses the authentication handler, useful for endpoints that
        do not require credentials (e.g. basicdeviceinfo.cgi unrestricted).
        """
        params = kwargs.pop("params", None)
        kwargs.pop("auth", None)
        url = endpoint.build_url(self.config.get_base_url(), params)
        headers = {**self._TRANSPORT_HEADERS, **kwargs.pop("headers", {})}
        headers = {
            key: value
            for key, value in headers.items()
            if key.lower() not in {"authorization", "cookie"}
        }

        emit_request_debug_info(
            self.config.debug_request_callback,
            method=endpoint.method,
            url=url,
            headers=headers,
            timeout=self.config.timeout,
            verify_ssl=self.config.verify_ssl,
            params=params,
            json_body=kwargs.get("json"),
            data=kwargs.get("data"),
        )

        no_auth_session = self._create_session()
        try:
            return no_auth_session.request(
                method=endpoint.method,
                url=url,
                headers=headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                auth=_NoAuth(),
                **kwargs,
            )

        except requests.exceptions.Timeout:
            raise NetworkError(
                "request_timeout",
                f"Request timed out after {self.config.timeout}s",
            )

        except requests.exceptions.SSLError as error:
            raise NetworkError(
                "ssl_verification_failed",
                "TLS certificate verification failed",
                str(error),
            ) from error
        except requests.exceptions.RequestException as error:
            raise NetworkError(
                "request_failed",
                "Request failed",
                str(error),
            ) from error
        finally:
            no_auth_session.close()
