from typing import Any, Callable, Optional


def _serialize_debug_value(value: Any) -> Any:
    """Convert request values into JSON-serializable debug output."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    if isinstance(value, dict):
        return {str(key): _serialize_debug_value(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_serialize_debug_value(item) for item in value]

    return str(value)


def emit_request_debug_info(
    callback: Optional[Callable[[dict], None]],
    *,
    method: str,
    url: str,
    headers: dict,
    timeout: float,
    verify_ssl: bool,
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
                "url": url,
                "headers": _serialize_debug_value(headers),
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