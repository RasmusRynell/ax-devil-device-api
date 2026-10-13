"""Connection configuration."""

from __future__ import annotations

import math
import ssl
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from typing import Any, Literal
from urllib.parse import urlsplit, urlunsplit

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

    def __repr__(self) -> str:
        return f"Credentials(username={self.username!r}, password=<redacted>)"


@dataclass(frozen=True)
class BearerToken:
    """An OAuth/OIDC access token sent as ``Authorization: Bearer``.

    ``token`` may be a callable returning the current token; it is called for
    every request, and once more after a 401 so a refreshed token can be used.
    """

    token: str | Callable[[], str]

    def current(self) -> str:
        return self.token() if callable(self.token) else self.token

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
        if not self.host or any(c in self.host for c in "/?#@ "):
            raise ConfigurationError(f"Invalid host: {self.host!r}")
        if self.scheme not in ("https", "http"):
            raise ConfigurationError(f"Invalid scheme: {self.scheme!r}")
        if self.scheme == "http" and not self.allow_http:
            raise ConfigurationError("HTTP sends credentials and data unencrypted; pass allow_http=True to use it")
        if self.port is not None and not (0 < self.port < 65536):
            raise ConfigurationError(f"Invalid port: {self.port}")
        if self.base_path and (not self.base_path.startswith("/") or self.base_path.endswith("/") or "?" in self.base_path or "#" in self.base_path):
            raise ConfigurationError("base_path must start with '/', not end with '/', and contain no query or fragment")
        if self.base_path and unsafe_path(self.base_path, strict=True):
            raise ConfigurationError("base_path must not contain '.', '..', empty segments or backslashes (also percent-encoded)")
        if not 0 < self.timeout < math.inf:
            raise ConfigurationError("timeout must be positive and finite")
        if self.max_concurrency < 1 or self.max_streams < 1:
            raise ConfigurationError("max_concurrency and max_streams must be at least 1")
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
        host = f"[{self.host}]" if ":" in self.host and not self.host.startswith("[") else self.host
        default_port = 443 if self.scheme == "https" else 80
        port = f":{self.port}" if self.port is not None and self.port != default_port else ""
        return f"{self.scheme}://{host}{port}"
