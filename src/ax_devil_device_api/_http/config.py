"""Connection configuration."""

from __future__ import annotations

import ipaddress
import ssl
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from typing import Any, Literal
from urllib.parse import urlsplit, urlunsplit

from .._validate import boolean, bounded_int, header_safe_secret, positive_finite, positive_int, text
from ..errors import ConfigurationError
from .options import RetryPolicy
from .types import unsafe_path


def _redact_userinfo(url: str) -> str:
    """``url`` with any ``user:password@`` part replaced by ``<redacted>@``."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return "<redacted>"
    if "@" not in parts.netloc:
        return url
    return urlunsplit(parts._replace(netloc="<redacted>@" + parts.netloc.rpartition("@")[2]))


@dataclass(frozen=True)
class Credentials:
    """Username and password; the device's challenge decides Digest or Basic."""

    username: str
    password: str

    def __post_init__(self) -> None:
        # A password read from an unset environment variable is None: refuse it instead of sending "None".
        # Axis user names are ASCII, and a header cannot carry anything else (httpx would fail inside the send).
        # Passwords may be any text: Digest and Basic encode them as UTF-8.
        header_safe_secret("username", text("username", self.username), ascii_only=True)
        header_safe_secret("password", text("password", self.password, allow_empty=True), inner_space=True)

    @classmethod
    def from_pair(cls, pair: Any) -> Credentials:
        """``Credentials`` from the ``(username, password)`` tuple form."""
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ConfigurationError("credentials given as a tuple must be (username, password)")
        return cls(*pair)

    def __repr__(self) -> str:
        return f"Credentials(username={self.username!r}, password=<redacted>)"


@dataclass(frozen=True)
class BearerToken:
    """An OAuth/OIDC access token sent as ``Authorization: Bearer``.

    ``token`` may be a callable returning the current token; it is called for
    every request, and once more after a 401 so a refreshed token can be used.
    """

    token: str | Callable[[], str]

    def __post_init__(self) -> None:
        if not callable(self.token):
            header_safe_secret("bearer token", text("token", self.token), ascii_only=True)

    def current(self) -> str:
        token = self.token() if callable(self.token) else self.token
        token = header_safe_secret("bearer token", text("token", token), ascii_only=True)  # checked at every use, callable providers included
        object.__setattr__(self, "_last", token)  # remembered only so error text can be scrubbed of it
        return token

    def recent(self) -> str | None:
        """The token last sent (or the static one): what a diagnostic must not repeat."""
        return self.token if isinstance(self.token, str) else self.__dict__.get("_last")

    def __repr__(self) -> str:
        return "BearerToken(<redacted>)"


Auth = Credentials | BearerToken

Scheme = Literal["https", "http"]
Verify = bool | str | ssl.SSLContext
"""``True`` (system CAs), ``False`` (no verification), a CA bundle path, or an SSL context."""

RequestHook = Callable[[dict[str, Any]], None]
"""Receives a redacted description of every outgoing request (debug aid)."""

ResponseHook = Callable[[dict[str, Any]], None]
"""Receives one record per completed or failed request attempt:
``{api, operation, method, path, status, error, duration_ms, attempt}``."""


def check_host(host: str) -> None:
    """Raise ``ConfigurationError`` unless ``host`` is a name or IP address (colons only in an IPv6 literal)."""
    if not isinstance(host, str) or not host or any(c in host for c in "/?#@\\"):
        raise ConfigurationError(f"Invalid host: {host!r}")
    if any(c.isspace() or unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp") for c in host):
        raise ConfigurationError(f"Invalid host: {host!r}; whitespace and control characters are not allowed")
    if not host.isascii():
        try:
            host.encode("idna")
        except UnicodeError:
            raise ConfigurationError(f"Invalid host: {host!r}; not a valid internationalised host name") from None
    if ":" in host and not _is_ipv6(host):
        raise ConfigurationError(
            f"Invalid host: {host!r}; a host name or IP address only. Pass the port with port=... (or --port)"
        )


def _check_proxy(proxy: str) -> None:
    # urlsplit silently drops tabs and newlines, so look for them first.
    if any(c.isspace() or unicodedata.category(c) in ("Cc", "Cf") for c in proxy):
        raise ConfigurationError("Invalid proxy URL: whitespace and control characters are not allowed")
    try:
        parts = urlsplit(proxy)
        hostname = parts.hostname
        parts.port  # noqa: B018  (validates the port)
    except ValueError as error:
        raise ConfigurationError(f"Invalid proxy URL: {error}") from error
    if hostname:
        check_host(hostname)
    if parts.scheme not in ("http", "https", "socks5", "socks5h") or not hostname:
        raise ConfigurationError(
            "Invalid proxy URL: it needs a scheme (http, https or socks5) and a host, "
            "for example proxy='http://proxy.local:8080'"
        )


def url_host(host: str) -> str:
    """``host`` as the authority of a URL: IPv6 literals in brackets, with a zone id's ``%`` encoded as ``%25`` (RFC 6874),
    and an internationalised name in its IDNA (``xn--``) form, which is what resolvers and media clients understand."""
    if ":" not in host:
        if host.isascii():
            return host
        try:
            return host.encode("idna").decode("ascii")
        except UnicodeError:
            raise ConfigurationError(f"Invalid host: {host!r}; not a valid internationalised host name") from None
    inner = host[1:-1] if host.startswith("[") and host.endswith("]") else host
    return f"[{inner.replace('%', '%25')}]"


def _is_ipv6(host: str) -> bool:
    """Whether ``host`` is an IPv6 literal, with or without brackets (a zone id is allowed)."""
    inner = host[1:-1] if host.startswith("[") and host.endswith("]") else host
    try:
        ipaddress.IPv6Address(inner)
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class ConnectionConfig:
    """Everything needed to reach one device. Immutable once created."""

    host: str
    credentials: Auth | None = None
    scheme: Scheme = "https"
    port: int | None = None
    base_path: str = ""
    """Prefix for every request path, for devices reached through a reverse proxy or VMS."""
    verify: Verify = True
    proxy: str | None = None
    timeout: float = 10.0
    allow_http: bool = False
    max_concurrency: int = 4
    """Requests in flight to this device at once (excluding streams). Cameras are small computers."""
    max_streams: int = 2
    """Open streaming responses to this device at once; counted separately so downloads never block control calls."""
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    on_request: RequestHook | None = None
    on_response: ResponseHook | None = None

    def __post_init__(self) -> None:
        check_host(self.host)
        if self.credentials is not None and not isinstance(self.credentials, (Credentials, BearerToken)):
            raise ConfigurationError(
                f"credentials must be None, Credentials(user, password) or BearerToken(...), got {type(self.credentials).__name__}"
            )
        boolean("allow_http", self.allow_http)
        if self.retry is None:
            object.__setattr__(self, "retry", RetryPolicy())  # None keeps the default policy
        elif not isinstance(self.retry, RetryPolicy):
            raise ConfigurationError(f"retry must be a RetryPolicy or None, got {self.retry!r}")
        if self.scheme not in ("https", "http"):
            raise ConfigurationError(f"Invalid scheme: {self.scheme!r}")
        if self.proxy is not None:
            _check_proxy(self.proxy)
        if self.scheme == "http" and not self.allow_http:
            raise ConfigurationError("HTTP sends credentials and data unencrypted; pass allow_http=True to use it")
        if self.port is not None:
            bounded_int("port", self.port, 1, 65535)
        if self.base_path and (not self.base_path.startswith("/") or self.base_path.endswith("/") or "?" in self.base_path or "#" in self.base_path):
            raise ConfigurationError("base_path must start with '/', not end with '/', and contain no query or fragment")
        if self.base_path and unsafe_path(self.base_path, strict=True):
            raise ConfigurationError("base_path must not contain '.', '..', empty segments or backslashes (also percent-encoded)")
        positive_finite("timeout", self.timeout)
        positive_int("max_concurrency", self.max_concurrency)
        positive_int("max_streams", self.max_streams)
        if not isinstance(self.verify, (bool, str, ssl.SSLContext)):
            raise ConfigurationError("verify must be a bool, a CA bundle path, or an ssl.SSLContext")
        if isinstance(self.credentials, BearerToken) and self.scheme == "http":
            raise ConfigurationError("Bearer tokens are sent in clear text over HTTP; use HTTPS")

    def __repr__(self) -> str:
        parts = []
        for f in fields(self):
            value = getattr(self, f.name)
            if f.name == "proxy" and value is not None:
                value = _redact_userinfo(value)
            parts.append(f"{f.name}={value!r}")
        return f"ConnectionConfig({', '.join(parts)})"

    @property
    def base_url(self) -> str:
        """Scheme, host and port; ``base_path`` is applied separately to request paths."""
        host = url_host(self.host)
        default_port = 443 if self.scheme == "https" else 80
        port = f":{self.port}" if self.port is not None and self.port != default_port else ""
        return f"{self.scheme}://{host}{port}"
