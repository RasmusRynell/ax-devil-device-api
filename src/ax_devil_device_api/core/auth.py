import re
from typing import Callable, Optional

import requests
from requests import Response as RequestsResponse
from requests.auth import AuthBase, HTTPBasicAuth, HTTPDigestAuth
from requests.utils import parse_dict_header

from ..utils.errors import AuthenticationError
from .config import AuthMethod, DeviceConfig
from .debug import emit_request_debug_info
from .endpoints import TransportEndpoint


class _NoAuth(AuthBase):
    """Prevent a session-level auth handler from adding Authorization."""

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers.pop("Authorization", None)
        return request


class _PreemptiveDigestAuth(HTTPDigestAuth):
    """Use a previously received Digest challenge on the next request."""

    def __init__(self, username: str, password: str, challenge: str) -> None:
        super().__init__(username, password)
        self._challenge = challenge

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        # AUTO already made the challenge request, so prime Requests' auth
        # object and send the authenticated retry directly.
        self.init_per_thread_state()
        self._thread_local.chal = parse_dict_header(self._challenge)
        self._thread_local.last_nonce = self._thread_local.chal.get("nonce", "")
        self._thread_local.nonce_count = 0
        return super().__call__(request)


class AuthHandler:
    """Handle device authentication and cache only verified auth methods."""

    _AUTH_SCHEME_RE = re.compile(r"(?i)(?<![A-Za-z0-9_-])(basic|digest)(?=\s|$)")

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config
        self._detected_method: Optional[AuthMethod] = None
        self._auth_object: Optional[AuthBase] = None

    def authenticate_request(
        self,
        session: requests.Session,
        request_func: Callable[[Optional[AuthBase]], RequestsResponse],
    ) -> RequestsResponse:
        """Send a request using configured or challenge-selected authentication."""
        if not self.config.username or not self.config.password:
            raise AuthenticationError(
                "username_password_required", "Username and password are required"
            )

        if self._auth_object is not None:
            response = request_func(self._auth_object)
            if response.status_code != 401:
                return response
            self._clear_cached_auth(session)

        if self.config.auth_method != AuthMethod.AUTO:
            challenge_response = request_func(None)
            if challenge_response.status_code != 401:
                return challenge_response
            challenge = self._challenge_for_method(
                challenge_response, self.config.auth_method
            )
            if challenge is None:
                raise AuthenticationError(
                    "authentication_failed",
                    f"Device did not advertise {self.config.auth_method.value} authentication",
                )
            auth_object = self._create_auth(self.config.auth_method, challenge)
            response = request_func(auth_object)
            if response.status_code == 401:
                raise AuthenticationError(
                    "authentication_failed",
                    f"Authentication failed using {self.config.auth_method.value}",
                )
            if self._is_accepted_success(response):
                self._cache_auth(auth_object, self.config.auth_method, session)
            return response

        # Do not send Basic credentials before the device has advertised an
        # authentication challenge. This matters especially for HTTP.
        challenge_response = request_func(None)
        if challenge_response.status_code != 401:
            return challenge_response

        challenges = self._advertised_challenges(challenge_response)
        if not challenges:
            raise AuthenticationError(
                "authentication_failed",
                "Device returned HTTP 401 without a supported Basic or Digest challenge",
            )

        for method, challenge in challenges:
            auth_object = self._create_auth(method, challenge)
            response = request_func(auth_object)
            if response.status_code == 401:
                response.close()
                continue

            # A 403/5xx response is an endpoint or server failure, not proof
            # that the selected credentials are valid.
            if self._is_accepted_success(response):
                self._cache_auth(auth_object, method, session)
            return response

        raise AuthenticationError(
            "authentication_failed", "Failed to authenticate with any advertised method"
        )

    def _advertised_challenges(
        self, response: RequestsResponse
    ) -> list[tuple[AuthMethod, str]]:
        """Extract supported auth challenges, preferring Digest when offered."""
        header = response.headers.get("WWW-Authenticate", "")
        matches = list(self._AUTH_SCHEME_RE.finditer(header))
        challenges: list[tuple[AuthMethod, str]] = []

        for index, match in enumerate(matches):
            method = AuthMethod(match.group(1).lower())
            end = (
                matches[index + 1].start() if index + 1 < len(matches) else len(header)
            )
            challenge = header[match.end() : end].strip(" ,")
            challenges.append((method, challenge))

        # Digest avoids sending a reusable password in clear text when both
        # schemes are advertised. Keep one challenge per method.
        selected: list[tuple[AuthMethod, str]] = []
        for method in (AuthMethod.DIGEST, AuthMethod.BASIC):
            selected.extend(
                challenge for challenge in challenges if challenge[0] == method
            )
        return selected

    @staticmethod
    def _is_accepted_success(response: RequestsResponse) -> bool:
        """Return whether a 2xx response proves that authentication worked."""
        return 200 <= response.status_code < 300

    def _challenge_for_method(
        self, response: RequestsResponse, method: AuthMethod
    ) -> Optional[str]:
        """Return the advertised challenge for one explicitly selected method."""
        return next(
            (
                challenge
                for advertised_method, challenge in self._advertised_challenges(
                    response
                )
                if advertised_method == method
            ),
            None,
        )

    def _clear_cached_auth(self, session: requests.Session) -> None:
        """Forget a cached auth method after a rejected authenticated request."""
        self._auth_object = None
        self._detected_method = None
        session.auth = None

    def _cache_auth(
        self, auth_obj: AuthBase, method: AuthMethod, session: requests.Session
    ) -> None:
        """Cache an auth method after a successful authenticated response."""
        self._auth_object = auth_obj
        self._detected_method = method
        session.auth = auth_obj

    def _create_auth(
        self, method: AuthMethod, challenge: Optional[str] = None
    ) -> AuthBase:
        """Create an auth object for a configured or advertised method."""
        if method == AuthMethod.BASIC:
            return HTTPBasicAuth(self.config.username, self.config.password)
        if method == AuthMethod.DIGEST:
            if challenge:
                return _PreemptiveDigestAuth(
                    self.config.username, self.config.password, challenge
                )
            return HTTPDigestAuth(self.config.username, self.config.password)
        raise AuthenticationError(
            "unsupported_auth_method", f"Unsupported authentication method: {method}"
        )

    def send_request(
        self,
        session: requests.Session,
        endpoint: TransportEndpoint,
        headers: dict,
        kwargs: dict,
    ) -> requests.Response:
        """Send a request while preserving its URL, headers, and body on retries."""
        params = kwargs.get("params")
        request_kwargs = {
            key: value for key, value in kwargs.items() if key != "params"
        }
        body = request_kwargs.get("data")
        body_position: Optional[int] = None
        if body is not None and hasattr(body, "tell") and hasattr(body, "seek"):
            try:
                body_position = body.tell()
            except (OSError, ValueError):
                body_position = None
        if body is not None and not self._is_replayable_body(body, body_position):
            raise AuthenticationError(
                "non_replayable_body",
                "Authentication challenge requires a rewindable request body",
            )

        def make_request(auth: Optional[AuthBase]) -> requests.Response:
            """Perform one attempt with a fresh request argument mapping."""
            if body_position is not None:
                try:
                    body.seek(body_position)
                except (OSError, ValueError):
                    pass

            url = endpoint.build_url(self.config.get_base_url(), params)
            request_args = {
                **request_kwargs,
                "method": endpoint.method,
                "url": url,
                "headers": dict(headers),
                "timeout": self.config.timeout,
                "auth": auth if auth is not None else _NoAuth(),
                "verify": self.config.verify_ssl,
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

            return session.request(**request_args)

        return self.authenticate_request(session, make_request)

    @staticmethod
    def _is_replayable_body(body: object, body_position: Optional[int]) -> bool:
        """Return whether Requests can send the body again after a challenge."""
        if isinstance(body, (bytes, bytearray, memoryview, str, dict, list, tuple)):
            return True
        return body_position is not None
