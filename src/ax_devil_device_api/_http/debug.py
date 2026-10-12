"""Redacted request descriptions for the ``on_request`` debug hook."""

from __future__ import annotations

import json
import re
import ssl
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .config import RequestHook, Verify
from .types import FormBody, JsonBody, MultipartBody, RawBody, Request

_REDACTED = "<redacted>"
_SECRET_KEY_RE = re.compile(
    r"(?:pass(?:word)?|passwd|pwd|secret|token|api[-_]?key|access[-_]?key|private[-_]?key|authorization|credential|client[-_]?secret|cookie)",
    re.IGNORECASE,
)
_SECRET_TEXT_RE = re.compile(
    r"(?i)(\b(?:password|passwd|pwd|secret|token|api[-_]?key|access[-_]?key|private[-_]?key|authorization|credential|client[-_]?secret)\b\s*[:=]\s*)([^,\s}]+)|\b(Bearer)\s+([^,\s}]+)"
)


def _is_secret_key(key: Any) -> bool:
    """Return whether a mapping key commonly identifies a secret."""
    return bool(_SECRET_KEY_RE.search(str(key)))


def redact_url(url: str) -> str:
    """Redact credentials and secret query parameters from a URL."""
    try:
        parts = urlsplit(url)
        hostname = parts.hostname or ""
        port = parts.port
    except (TypeError, ValueError):
        return _REDACTED
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    netloc = hostname
    if parts.username is not None:
        netloc = f"{_REDACTED}@{netloc}"
    if port is not None:
        netloc = f"{netloc}:{port}"
    query = [
        (key, _REDACTED if _is_secret_key(key) else value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit((parts.scheme, netloc, parts.path, urlencode(query), parts.fragment))


def serialize(value: Any, key: Any = None) -> Any:
    """Convert a value to JSON-safe output, recursively redacting secrets."""
    if _is_secret_key(key):
        return _REDACTED
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return _SECRET_TEXT_RE.sub(lambda m: f"{m.group(1) or m.group(3)}{_REDACTED}", value)
        if isinstance(decoded, (dict, list)):
            return json.dumps(serialize(decoded, key))
        return value
    if isinstance(value, bytes):
        return serialize(value.decode("utf-8", errors="replace"), key)
    if isinstance(value, dict):
        return {str(k): serialize(v, k) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize(item, key) for item in value]
    return str(value)


def _pairs(pairs: tuple[tuple[str, str], ...]) -> list[list[Any]]:
    return [[k, serialize(v, k)] for k, v in pairs]


def _body(body: Any) -> Any:
    if body is None:
        return None
    if isinstance(body, JsonBody):
        return serialize(body.value)
    if isinstance(body, FormBody):
        return _pairs(body.fields)
    if isinstance(body, MultipartBody):
        return {
            "fields": _pairs(body.fields),
            "files": [{"name": f.name, "filename": f.filename, "size": f.length} for f in body.files],
        }
    if isinstance(body, RawBody):
        if isinstance(body.content, bytes):
            return f"<{len(body.content)} bytes {body.content_type}>"
        return f"<stream {body.content_type}>"
    return _REDACTED


def emit_request(hook: RequestHook | None, request: Request, url: str, timeout: float, verify: Verify) -> None:
    """Call ``hook`` with a redacted description of ``request``. No-op without a hook."""
    if hook is None:
        return
    hook(
        {
            "request": {
                "method": request.method,
                "url": redact_url(url),
                "headers": {
                    str(k): _REDACTED if _is_secret_key(k) else serialize(v, k) for k, v in request.headers
                },
                "query": _pairs(request.query),
                "body": _body(request.body),
            },
            "settings": {
                "timeout": timeout,
                "ssl_verify": "<ssl.SSLContext>" if isinstance(verify, ssl.SSLContext) else verify,
            },
        }
    )
