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

import json
import re
from typing import Any, Literal

ErrorKind = Literal["access_denied", "unavailable", "invalid_argument", "not_found", "unsupported", "internal"]
"""Normalized meaning of a device error code, from the spec's error tables."""


_CONTROL = re.compile("[\x00-\x1f\x7f-\x9f\u2028\u2029]")
_ESCAPES = {"\n": "\\n", "\r": "\\r", "\t": "\\t"}
DISPLAY_LIMIT = 2000
"""Longest text an exception shows for one human-facing field or for the whole message."""


def _escape(match: re.Match[str]) -> str:
    char = match.group()
    return _ESCAPES.get(char) or (f"\\x{ord(char):02x}" if ord(char) < 256 else f"\\u{ord(char):04x}")


def display_text(value: Any, limit: int = DISPLAY_LIMIT) -> str:
    """THE way text that may come from a device is shown by an exception (message, code, reason, close reason, content
    type, validation location, discovery diagnostics).

    Three steps, in this order: the request-hook redactor (secret-named pairs such as ``password=...``, URL
    credentials), control and newline characters escaped (``\\r\\n``: a device cannot forge a log line), and a length
    bound. Applying it again changes nothing, so composed messages can be shown safely.
    """
    from ._http.debug import serialize  # imported late: that package imports this one

    try:
        shown = serialize(value)
        shown = shown if isinstance(shown, str) else json.dumps(shown, default=str)
    except (TypeError, ValueError, RecursionError):
        return "<unprintable>"
    shown = _CONTROL.sub(_escape, shown)
    return shown if len(shown) <= limit else shown[: max(limit - 1, 0)] + "…"


_DETAILS_ITEMS = 100
_DETAILS_DEPTH = 8


def _bounded(value: Any, depth: int) -> Any:
    if depth > _DETAILS_DEPTH:
        return "<nested too deeply>"
    if isinstance(value, str):
        return _CONTROL.sub(_escape, value) if len(value) <= DISPLAY_LIMIT else _CONTROL.sub(_escape, value[: DISPLAY_LIMIT - 1]) + "…"
    if isinstance(value, dict):
        items = list(value.items())
        shown = {display_text(str(key), 200): _bounded(item, depth + 1) for key, item in items[:_DETAILS_ITEMS]}  # a key is text too
        if len(items) > _DETAILS_ITEMS:
            shown["…"] = f"{len(items) - _DETAILS_ITEMS} more"
        return shown
    if isinstance(value, list):
        listed = [_bounded(item, depth + 1) for item in value[:_DETAILS_ITEMS]]
        if len(value) > _DETAILS_ITEMS:
            listed.append(f"… {len(value) - _DETAILS_ITEMS} more")
        return listed
    return value


def sanitize_details(value: Any) -> Any:
    """The ``details`` an exception keeps: the structure of what the device sent, with secret-named values and URL
    credentials redacted, control characters escaped in every string and key, and the size bounded. Idempotent."""
    from ._http.debug import serialize

    if value is None or isinstance(value, (bool, int, float)):
        return value
    try:
        return _bounded(serialize(value), 0)
    except (TypeError, ValueError, RecursionError):
        return "<unprintable>"


class DeviceError(Exception):
    """Base class for all errors raised by this library.

    This class owns how an error is shown: every string it is built from, and the whole text, go through
    :func:`display_text`, so ``str()``, ``repr()`` and a traceback never repeat a secret, a URL credential or a control
    character, whatever a subclass or a device put into it. Raw values live on attributes meant for matching (``code``,
    ``status``), never in the text.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*(display_text(arg) if isinstance(arg, str) else arg for arg in args))

    def __str__(self) -> str:
        return display_text(super().__str__())

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join(repr(display_text(arg)) for arg in self.args)})"


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
        self.reason = display_text(reason, 300)
        super().__init__(f"session closed by the device (code {code}{': ' + self.reason if self.reason else ''})")


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
        self.body_excerpt = display_text(body_excerpt, 1000)
        self.api = None if api is None else display_text(api, 100)  # a stable label, never a path or URL
        self.operation = None if operation is None else display_text(operation, 100)
        where = f"{self.api}.{self.operation}: " if self.api and self.operation else ""
        text = f"{where}HTTP {status}"
        if detail:
            text += f" ({display_text(detail, 500)})"
        if self.body_excerpt:
            text += f": {self.body_excerpt}"
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
        self.api = display_text(api, 100)  # a stable label (api.operation), never a path or URL
        self.operation = display_text(operation, 100)
        self.code = code  # raw, for matching; the text below shows it through display_text
        self.message = display_text(message, 1000)
        self.description = None if description is None else display_text(description, 1000)
        self.kind = kind
        self.http_status = http_status
        self.details = sanitize_details(details)
        where = f"{self.api}.{self.operation}: "
        text = where + (f"error {display_text(str(code), 100)}: {self.message}" if code is not None else self.message)
        if self.description and self.description != self.message:
            text += f" ({self.description})"
        super().__init__(text)


class ApiAccessDenied(ApiError, AccessDenied):
    """An API error code documented as an authorization failure."""


class ApiUnavailable(ApiError, Unavailable):
    """An API error code documented as busy or temporarily unavailable."""


class ResponseFormatError(DeviceError):
    """The response could not be parsed into the documented shape."""

    def __init__(self, api: str, operation: str, reason: str) -> None:
        self.api = display_text(api, 100)  # a stable label, never a path or URL
        self.operation = display_text(operation, 100)
        self.reason = display_text(reason, 1000)
        super().__init__(f"{self.api}.{self.operation}: {self.reason}")


class NotSupported(DeviceError):
    """The device lacks the API, version, or feature required for the call.

    ``required`` names the version needed when the cause is a version gate.
    """

    def __init__(self, api: str, operation: str | None, reason: str, *, required: str | None = None) -> None:
        self.api = display_text(api, 100)  # a stable label, never a path or URL
        self.operation = None if operation is None else display_text(operation, 100)
        self.reason = display_text(reason, 1000)
        self.required = None if required is None else display_text(required, 100)
        where = f"{self.api}.{self.operation}" if self.operation else self.api
        super().__init__(f"{where}: {self.reason}")
