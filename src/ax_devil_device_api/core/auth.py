import re
from collections.abc import Callable

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

    def __init__(self, headers_to_remove: frozenset[str] = frozenset()) -> None:
        self._headers_to_remove = headers_to_remove

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers.pop("Authorization", None)
        _remove_headers(request, self._headers_to_remove)
        return request


class _HeaderRemovingAuth(AuthBase):
    """Apply authentication, then remove headers from the prepared request."""

    def __init__(self, auth: AuthBase, headers_to_remove: frozenset[str]) -> None:
        self._auth = auth
        self._headers_to_remove = headers_to_remove

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request = self._auth(request)
        _remove_headers(request, self._headers_to_remove)
        return request


def _remove_headers(
    request: requests.PreparedRequest, headers_to_remove: frozenset[str]
) -> None:
    """Remove headers case-insensitively from a prepared Requests request."""
    for key in list(request.headers):
        if key.lower() in headers_to_remove:
            del request.headers[key]


class _OneShotDigestAuth(AuthBase):
    """Attach one Digest header without installing Requests' 401 retry hook."""

    def __init__(self, username: str, password: str, challenge: str) -> None:
        self._digest_auth = HTTPDigestAuth(username, password)
        self._challenge = _parse_supported_digest_challenge(challenge)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Build the Authorization header from the received challenge."""
        digest_auth = self._digest_auth
        digest_auth.init_per_thread_state()
        digest_auth._thread_local.chal = self._challenge
        digest_auth._thread_local.last_nonce = ""
        digest_auth._thread_local.nonce_count = 0
        authorization = digest_auth.build_digest_header(request.method, request.url)
        if authorization is None:
            raise AuthenticationError(
                "unsupported_digest_challenge",
                "Device advertised an unsupported Digest challenge",
            )
        request.headers["Authorization"] = authorization
        return request


class AuthHandler:
    """Handle device authentication and cache only verified auth methods."""

    _AUTH_TOKEN_RE = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+")

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self.config = config
        self._detected_method: AuthMethod | None = None
        self._auth_object: AuthBase | None = None

    def authenticate_request(
        self,
        session: requests.Session,
        request_func: Callable[[AuthBase | None], RequestsResponse],
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
                self._cache_auth_if_reusable(
                    auth_object, self.config.auth_method, session
                )
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
                self._cache_auth_if_reusable(auth_object, method, session)
            return response

        raise AuthenticationError(
            "authentication_failed", "Failed to authenticate with any advertised method"
        )

    def _advertised_challenges(
        self, response: RequestsResponse
    ) -> list[tuple[AuthMethod, str]]:
        """Extract supported auth challenges, preferring Digest when offered."""
        header = response.headers.get("WWW-Authenticate", "")
        matches = self._find_challenge_boundaries(header)
        challenges: list[tuple[AuthMethod, str]] = []

        for index, (method_name, start, _) in enumerate(matches):
            if method_name.lower() not in {
                AuthMethod.BASIC.value,
                AuthMethod.DIGEST.value,
            }:
                continue
            method = AuthMethod(method_name.lower())
            end = matches[index + 1][1] if index + 1 < len(matches) else len(header)
            challenge = header[start + len(method_name) : end].strip(" ,")
            challenges.append((method, challenge))

        # Digest avoids sending a reusable password in clear text when both
        # schemes are advertised. Keep one challenge per method.
        selected: list[tuple[AuthMethod, str]] = []
        for method in (AuthMethod.DIGEST, AuthMethod.BASIC):
            selected.extend(
                challenge for challenge in challenges if challenge[0] == method
            )
        return selected

    @classmethod
    def _find_challenge_boundaries(cls, header: str) -> list[tuple[str, int, int]]:
        """Find scheme tokens only at actual challenge boundaries."""
        boundaries: list[tuple[str, int, int]] = []
        in_quotes = False
        escaped = False
        for index, character in enumerate(header + ","):
            if escaped:
                escaped = False
                continue
            if in_quotes and character == "\\":
                escaped = True
                continue
            if character == '"':
                in_quotes = not in_quotes
                continue
            if in_quotes or character != ",":
                continue
            start = index + 1
            while start < len(header) and header[start].isspace():
                start += 1
            token = cls._AUTH_TOKEN_RE.match(header, start)
            if token is not None and (
                token.end() == len(header) or header[token.end()].isspace()
            ):
                boundaries.append((token.group(), start, token.end()))

        if in_quotes:
            return []
        token = cls._AUTH_TOKEN_RE.match(header)
        if token is not None and (
            token.end() == len(header) or header[token.end()].isspace()
        ):
            boundaries.insert(0, (token.group(), 0, token.end()))
        return boundaries

    @staticmethod
    def _is_accepted_success(response: RequestsResponse) -> bool:
        """Return whether a 2xx response proves that authentication worked."""
        return 200 <= response.status_code < 300

    def _challenge_for_method(
        self, response: RequestsResponse, method: AuthMethod
    ) -> str | None:
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

    def reset_session_state(self, *sessions: requests.Session) -> None:
        """Clear cached authentication when transport session state changes."""
        self._auth_object = None
        self._detected_method = None
        for session in sessions:
            session.auth = None

    def _cache_auth(
        self, auth_obj: AuthBase, method: AuthMethod, session: requests.Session
    ) -> None:
        """Cache an auth method after a successful authenticated response."""
        self._auth_object = auth_obj
        self._detected_method = method
        session.auth = auth_obj

    def _cache_auth_if_reusable(
        self, auth_obj: AuthBase, method: AuthMethod, session: requests.Session
    ) -> None:
        """Cache only authentication objects that are safe to reuse."""
        if method == AuthMethod.DIGEST and isinstance(auth_obj, _OneShotDigestAuth):
            self._clear_cached_auth(session)
            return
        self._cache_auth(auth_obj, method, session)

    def _create_auth(
        self, method: AuthMethod, challenge: str | None = None
    ) -> AuthBase:
        """Create an auth object for a configured or advertised method."""
        if method == AuthMethod.BASIC:
            return HTTPBasicAuth(self.config.username, self.config.password)
        if method == AuthMethod.DIGEST:
            if challenge:
                return _OneShotDigestAuth(
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
        headers_to_remove: frozenset[str] = frozenset(),
    ) -> requests.Response:
        """Send a request while preserving its URL, headers, and body on retries."""
        request_func = self._make_request_func(
            session, endpoint, headers, kwargs, headers_to_remove
        )
        return self.authenticate_request(session, request_func)

    def send_request_after_challenge(
        self,
        session: requests.Session,
        endpoint: TransportEndpoint,
        headers: dict,
        kwargs: dict,
        challenge_response: RequestsResponse,
        headers_to_remove: frozenset[str] = frozenset(),
    ) -> requests.Response:
        """Send exactly one authenticated request using an existing challenge."""
        if not self.config.username or not self.config.password:
            raise AuthenticationError(
                "username_password_required", "Username and password are required"
            )
        if challenge_response.status_code != 401:
            raise AuthenticationError(
                "authentication_failed",
                "Authenticated retry requires an HTTP 401 challenge response",
            )

        challenges = self._advertised_challenges(challenge_response)
        if not challenges:
            raise AuthenticationError(
                "authentication_failed",
                "Device returned HTTP 401 without a supported Basic or Digest challenge",
            )

        if self.config.auth_method == AuthMethod.AUTO:
            method, challenge = challenges[0]
        else:
            method = self.config.auth_method
            challenge = self._challenge_for_method(challenge_response, method)
            if challenge is None:
                raise AuthenticationError(
                    "authentication_failed",
                    f"Device did not advertise {method.value} authentication",
                )
        auth_object = self._create_auth(method, challenge)
        response = self._make_request_func(
            session, endpoint, headers, kwargs, headers_to_remove
        )(auth_object)
        if self._is_accepted_success(response):
            self._cache_auth_if_reusable(auth_object, method, session)
        return response

    def _make_request_func(
        self,
        session: requests.Session,
        endpoint: TransportEndpoint,
        headers: dict,
        kwargs: dict,
        headers_to_remove: frozenset[str],
    ) -> Callable[[AuthBase | None], RequestsResponse]:
        """Build a one-attempt request function for the configured transport."""
        params = kwargs.get("params")
        timeout = kwargs.get("timeout", self.config.timeout)
        request_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"params", "timeout"}
        }
        body = request_kwargs.get("data")
        body_position: int | None = None
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

        def make_request(auth: AuthBase | None) -> requests.Response:
            """Perform one attempt with a fresh request argument mapping."""
            if body_position is not None:
                try:
                    body.seek(body_position)
                except (OSError, ValueError):
                    pass

            url = endpoint.build_url(self.config.get_base_url(), params)
            request_auth = auth if auth is not None else _NoAuth()
            if headers_to_remove:
                request_auth = _HeaderRemovingAuth(request_auth, headers_to_remove)

            request_args = {
                **request_kwargs,
                "method": endpoint.method,
                "url": url,
                "headers": dict(headers),
                "timeout": timeout,
                "auth": request_auth,
                "verify": self.config.verify_ssl,
            }

            emit_request_debug_info(
                self.config.debug_request_callback,
                method=endpoint.method,
                url=url,
                headers=headers,
                timeout=timeout,
                verify_ssl=self.config.verify_ssl,
                params=params,
                json_body=kwargs.get("json"),
                data=kwargs.get("data"),
            )

            return session.request(**request_args)

        return make_request

    @staticmethod
    def _is_replayable_body(body: object, body_position: int | None) -> bool:
        """Return whether Requests can send the body again after a challenge."""
        if isinstance(body, (bytes, bytearray, memoryview, str, dict, list, tuple)):
            return True
        return body_position is not None


def _parse_supported_digest_challenge(challenge: str) -> dict[str, str]:
    """Validate the Digest policy supported by Requests and Axis devices."""
    try:
        parameters = parse_dict_header(challenge)
    except (TypeError, ValueError) as error:
        raise AuthenticationError(
            "invalid_digest_challenge", "Device returned a malformed Digest challenge"
        ) from error

    realm = parameters.get("realm")
    nonce = parameters.get("nonce")
    if (
        not isinstance(realm, str)
        or not realm
        or not isinstance(nonce, str)
        or not nonce
    ):
        raise AuthenticationError(
            "invalid_digest_challenge",
            "Device returned a Digest challenge without a valid realm and nonce",
        )

    algorithm = parameters.get("algorithm", "MD5")
    if not isinstance(algorithm, str) or algorithm.upper() not in {
        "MD5",
        "MD5-SESS",
        "SHA",
        "SHA-256",
        "SHA-512",
    }:
        raise AuthenticationError(
            "unsupported_digest_challenge",
            "Device advertised an unsupported Digest algorithm",
        )

    qop = parameters.get("qop")
    if qop is not None and (
        not isinstance(qop, str)
        or "auth" not in {value.strip().lower() for value in qop.split(",")}
    ):
        raise AuthenticationError(
            "unsupported_digest_challenge",
            "Device advertised an unsupported Digest quality of protection",
        )

    return {key: value for key, value in parameters.items() if isinstance(value, str)}
