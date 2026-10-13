"""Exception hierarchy for the device API.

Every exception raised by the library for a device interaction derives from
``DeviceError``. Argument validation errors raised before anything is sent
are ``pydantic.ValidationError`` (a ``ValueError``) or ``ConfigurationError``.

Two cross-cutting categories can be caught regardless of which layer
detected them:

- ``AccessDenied``: the account lacks the required access level
  (HTTP 403, or an API error code documented as an authorization failure).
- ``Unavailable``: the device is temporarily unable to serve the request
  (HTTP 503, or an API error code documented as busy/unavailable).
"""

from __future__ import annotations

from typing import Any, Literal

ErrorKind = Literal["access_denied", "unavailable", "invalid_argument", "not_found", "unsupported", "internal"]
"""Normalized meaning of a device error code, from the spec's error tables."""


class DeviceError(Exception):
    """Base class for all errors raised by this library."""


class ConfigurationError(DeviceError, ValueError):
    """Invalid client configuration, detected before any request is sent."""


# ---------------------------------------------------------------------------
# Categories


class AccessDenied(DeviceError):
    """The account is not allowed to perform the operation."""


class Unavailable(DeviceError):
    """The device is temporarily unable to serve the request (busy, starting up)."""


# ---------------------------------------------------------------------------
# Transport


class TransportError(DeviceError):
    """The request did not produce an HTTP response.

    ``request_sent`` is ``False`` when the failure happened before any byte of
    the request reached the device (connection refused, connect timeout, no
    free connection). Such requests are always safe to retry.
    """

    request_sent: bool = True
    during_preflight: bool = False
    """The failure hit the credentials preflight (a replayable GET), before the upload body was touched."""
    body_untouched: bool = False
    """The failure came before the request was built (no free concurrency slot), so even a one-shot body can be sent again."""

    def __init__(self, message: str, *, request_sent: bool | None = None) -> None:
        super().__init__(message)
        if request_sent is not None:
            self.request_sent = request_sent


class RequestTimeout(TransportError):
    """A timeout in any phase of the request."""


class ConnectTimeout(RequestTimeout):
    """Connecting to the device timed out."""

    request_sent = False


class ReadTimeout(RequestTimeout):
    """The device stopped sending data for longer than the timeout."""


class WriteTimeout(RequestTimeout):
    """Sending the request body to the device timed out."""


class PoolTimeout(RequestTimeout):
    """No connection to the device became free in time (too many concurrent requests)."""

    request_sent = False


class TlsError(TransportError):
    """TLS handshake or certificate verification failed."""

    request_sent = False


class ConnectionFailed(TransportError):
    """Any other connection-level failure (refused, reset, DNS, protocol error)."""


class SessionClosed(DeviceError):
    """A WebSocket session ended normally (close code 1000 or 1001) and has no more messages.

    Raised by ``receive()``/``request()`` only; iterating a session just stops.
    An abnormal end is a ``TransportError`` instead.
    """

    def __init__(self, code: int = 1000, reason: str = "") -> None:
        self.code = code
        self.reason = reason
        super().__init__(f"session closed by the device (code {code}{': ' + reason if reason else ''})")


class AuthError(DeviceError):
    """Authentication failed or could not be attempted safely."""


# ---------------------------------------------------------------------------
# HTTP and API level


class HttpError(DeviceError):
    """The device answered with an HTTP status that the protocol treats as failure."""

    def __init__(
        self,
        status: int,
        body_excerpt: str = "",
        *,
        api: str | None = None,
        operation: str | None = None,
        detail: str | None = None,
    ) -> None:
        self.status = status
        self.body_excerpt = body_excerpt
        self.api = api
        self.operation = operation
        where = f"{api}.{operation}: " if api and operation else ""
        text = f"{where}HTTP {status}"
        if detail:
            text += f" ({detail})"
        if body_excerpt:
            text += f": {body_excerpt}"
        super().__init__(text)


class HttpAccessDenied(HttpError, AccessDenied):
    """HTTP 403."""


class HttpUnavailable(HttpError, Unavailable):
    """HTTP 503."""


class ApiError(DeviceError):
    """The API reported an error in its response envelope."""

    def __init__(
        self,
        api: str,
        operation: str,
        code: int | str | None,
        message: str,
        *,
        description: str | None = None,
        kind: ErrorKind | None = None,
        http_status: int | None = None,
        details: Any = None,
    ) -> None:
        self.api = api
        self.operation = operation
        self.code = code
        self.message = message
        self.description = description
        self.kind = kind
        self.http_status = http_status
        self.details = details
        text = f"{api}.{operation}: " + (f"error {code}: {message}" if code is not None else message)
        if description and description != message:
            text += f" ({description})"
        super().__init__(text)


class ApiAccessDenied(ApiError, AccessDenied):
    """An API error code documented as an authorization failure."""


class ApiUnavailable(ApiError, Unavailable):
    """An API error code documented as busy or temporarily unavailable."""


class ResponseFormatError(DeviceError):
    """The response could not be parsed into the documented shape."""

    def __init__(self, api: str, operation: str, reason: str) -> None:
        self.api = api
        self.operation = operation
        self.reason = reason
        super().__init__(f"{api}.{operation}: {reason}")


class NotSupported(DeviceError):
    """The device lacks the API, version, or feature required for the call.

    ``required`` names the version needed when the cause is a version gate.
    """

    def __init__(self, api: str, operation: str | None, reason: str, *, required: str | None = None) -> None:
        self.api = api
        self.operation = operation
        self.reason = reason
        self.required = required
        where = f"{api}.{operation}" if operation else api
        super().__init__(f"{where}: {reason}")
