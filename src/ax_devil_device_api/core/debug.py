import json
import re
from typing import Any, Callable, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


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


def _redact_url(url: str) -> str:
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
    return urlunsplit(
        (parts.scheme, netloc, parts.path, urlencode(query), parts.fragment)
    )


def _serialize_debug_value(value: Any, key: Any = None) -> Any:
    """Convert request values to JSON-safe output while recursively redacting secrets."""
    if _is_secret_key(key):
        return _REDACTED

    if value is None or isinstance(value, (int, float, bool)):
        return value

    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return _SECRET_TEXT_RE.sub(
                lambda match: f"{match.group(1) or match.group(3)}{_REDACTED}",
                value,
            )
        if isinstance(decoded, (dict, list)):
            redacted = _serialize_debug_value(decoded, key)
            return json.dumps(redacted)
        return value

    if isinstance(value, bytes):
        return _serialize_debug_value(value.decode("utf-8", errors="replace"), key)

    if isinstance(value, dict):
        return {
            str(item_key): _serialize_debug_value(item, item_key)
            for item_key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_serialize_debug_value(item, key) for item in value]

    return str(value)


def _serialize_headers(headers: Any) -> Any:
    """Serialize headers and redact authentication or secret header values."""
    if not isinstance(headers, dict):
        return _serialize_debug_value(headers)
    return {
        str(key): _REDACTED
        if _is_secret_key(key)
        else _serialize_debug_value(value, key)
        for key, value in headers.items()
    }


def emit_request_debug_info(
    callback: Optional[Callable[[dict], None]],
    *,
    method: str,
    url: str,
    headers: dict,
    timeout: float,
    verify_ssl: bool | str,
    params: Any = None,
    json_body: Any = None,
    data: Any = None,
) -> None:
    """Send a normalized outgoing-request payload to the configured debug callback."""
    if callback is None:
        return

    callback(
        {
            "request": {
                "method": method,
                "url": _redact_url(url),
                "headers": _serialize_headers(headers),
                "params": _serialize_debug_value(params),
                "json": _serialize_debug_value(json_body),
                "data": _serialize_debug_value(data),
            },
            "settings": {
                "timeout": timeout,
                "ssl_verify": verify_ssl,
            },
        }
    )
