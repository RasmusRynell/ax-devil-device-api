"""Redacted request descriptions for the ``on_request`` debug hook."""

from __future__ import annotations

import json
import re
import ssl
from contextvars import ContextVar
from functools import lru_cache
from typing import Any
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

from .config import RequestHook, Verify
from .types import FormBody, JsonBody, MultipartBody, RawBody, Request

_REDACTED = "<redacted>"
# Key / header / element / attribute names that identify a secret (matched as substrings, case-insensitive).
_SECRET_KEY_RE = re.compile(
    r"(?:pass(?:word)?|passwd|pwd|secret|token|api[-_]?key|access[-_]?key|private[-_]?key|authorization|credential"
    r"|client[-_]?secret|cookie|shared[-_]?key|account[-_]?key|session[-_]?token|storage[-_]?key|sas[-_]?token"
    r"|secret[-_]?access|authentication[-_]?key)",
    re.IGNORECASE,
)
_SECRET_EXACT = {
    "sas", "sig", "psk", "signature", "sastoken", "sas_token", "wssession",
    "pin", "puk", "oldpin", "newpin", "confirmpin", "simpin", "pincode", "oldpuk", "newpuk", "simpuk", "pukcode",
    "passphrase", "passcode", "community", "apikey", "otp",
}
# Short or common words that only count as a whole name segment (``sim_pin``, ``SimPIN``, ``pin-code``), never
# as a substring: ``spinning`` and ``community_center_id`` must not match.
_SECRET_SEGMENTS = frozenset({"pin", "puk", "psk", "community", "passphrase", "passcode", "otp"})
_SEGMENT_SPLIT_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")
# Headers whose whole value is dropped by name (no content parsing). Any name matching the secret set is dropped too.
_SENSITIVE_HEADERS = frozenset({"authorization", "proxy-authorization", "cookie", "set-cookie"})
_TOKEN_RE = re.compile(r"[A-Za-z0-9_.\-]+")
_AUTHORITY_END = re.compile(r"[/?#\s]")
_WHITESPACE = re.compile(r"\s")
_SEGMENT_RE = re.compile(r"[^&\r\n]+")
_MAX_DECODE_LAYERS = 4
_MAX_DEPTH = 32


_Masks = tuple[frozenset[str], tuple["re.Pattern[str]", ...]]
_request_masked: ContextVar[_Masks] = ContextVar("ax_request_masked", default=(frozenset(), ()))
# Spec-masked (``x-masked``) wire names of the request being described: lower-cased exact names and templates.
_TEMPLATE_RE = re.compile(r"\{[^}]*\}")


def _masks(names: Any) -> _Masks:
    exact: set[str] = set()
    templates: list[re.Pattern[str]] = []
    for name in names:
        text = str(name).lower()
        if "{" in text:
            pattern = ".+".join(re.escape(part) for part in _TEMPLATE_RE.split(text))
            templates.append(re.compile(pattern, re.DOTALL))
        else:
            exact.add(text)
    return frozenset(exact), tuple(templates)


def _is_secret_key(key: Any) -> bool:
    """Return whether a mapping key, header, element or attribute name identifies a secret."""
    text = str(key)
    if _name_is_secret(text):
        return True
    exact, templates = _request_masked.get()
    if not exact and not templates:
        return False
    lowered = text.lower()
    return lowered in exact or any(t.fullmatch(lowered) for t in templates)


@lru_cache(maxsize=4096)
def _name_is_secret(text: str) -> bool:
    """Cached name test: the same few names recur in every record and in repeated free-text tokens."""
    lowered = text.lower()
    if _SECRET_KEY_RE.search(text) or lowered in _SECRET_EXACT:
        return True
    return any(segment.lower() in _SECRET_SEGMENTS for segment in _SEGMENT_SPLIT_RE.findall(text))


def is_secret_name(name: str) -> bool:
    """Whether ``name`` (a wire or Python field name) identifies a secret; used by codegen to mark sensitive bodies."""
    return _is_secret_key(name)


def _text_has_secret_name(text: str) -> bool:
    """Whether free text names a secret (substring match, or a whole token that names a secret)."""
    if _SECRET_KEY_RE.search(text):
        return True
    return any(_is_secret_key(token) for token in _TOKEN_RE.findall(text))


def _scrub_userinfo(text: str) -> str:
    """Redact URL userinfo (``scheme://user:pass@host``).

    Every ``://`` is a candidate on its own (overlapping ones included). The userinfo runs to the last ``@`` before
    the next ``/ ? #`` or whitespace, so quotes, commas and the like belong to it. One forward scan, linear.
    """
    pos = text.find("://")
    if pos < 0:
        return text
    out: list[str] = []
    done = 0
    n = len(text)
    while pos >= 0:
        start = pos + 3
        match = _AUTHORITY_END.search(text, start)
        end = match.start() if match else n
        at = text.rfind("@", start, end)
        if at >= 0 and text[start:at] != _REDACTED and start >= done:
            out.append(text[done:start])
            out.append(_REDACTED)
            done = at
        pos = text.find("://", start)
    out.append(text[done:])
    return "".join(out)


def _scrub_pairs(text: str) -> str:
    """Redact the value of ``name=value`` pairs once the text before the ``=`` names a secret.

    Pairs are split into segments on ``&`` and newlines; within a segment, after the first secret name every value is
    redacted (``Cookie: sid=x; other=y``). A value runs to whitespace, or to the closing quote when quoted. Markup
    characters are ordinary value characters.
    """
    if "=" not in text:
        return text
    out: list[str] = []
    done = 0
    for seg in _SEGMENT_RE.finditer(text):
        s, e = seg.span()
        scanned = s
        armed = False
        eq = text.find("=", s, e)
        while eq >= 0:
            if not armed and _text_has_secret_name(text[scanned:eq]):
                armed = True
            end = eq + 1
            if armed:
                v = end
                while v < e and text[v] in " \t":
                    v += 1
                if v < e and text[v] in "\"'":
                    close = text.find(text[v], v + 1, e)
                    end = e if close < 0 else close + 1
                else:
                    ws = _WHITESPACE.search(text, v, e)
                    end = ws.start() if ws else e
                if end > v and text[v:end] != _REDACTED:
                    out.append(text[done:v])
                    out.append(_REDACTED)
                    done = end
            scanned = end
            eq = text.find("=", end, e)
    out.append(text[done:])
    return "".join(out)


def _scrub_plain(text: str) -> str:
    # Userinfo first: a password may contain ``=`` or ``&``, which the keyed-pair scan would split.
    return _scrub_pairs(_scrub_userinfo(text))


def _scrub_text(text: str) -> str:
    """Redact credentials in free text, looking through percent-encoding layers; fail closed past the layer limit."""
    if not text:
        return text
    current = text
    found = False
    layers = 0
    while True:
        redacted = _scrub_plain(current)
        if redacted != current:
            current, found = redacted, True
        decoded = unquote(current)
        if decoded == current:
            break
        if layers >= _MAX_DECODE_LAYERS:
            return _REDACTED
        current = decoded
        layers += 1
    return current if found else text


def redact_url(url: str) -> str:
    """Redact URL userinfo, secret query parameters and credentials inside the path, query values and fragment."""
    try:
        parts = urlsplit(url)
        hostname = parts.hostname or ""
        port = parts.port
    except (TypeError, ValueError):
        return _REDACTED
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    netloc = hostname
    if parts.username is not None or "@" in parts.netloc:
        netloc = f"{_REDACTED}@{netloc}"
    if port is not None:
        netloc = f"{netloc}:{port}"
    query = [
        (_scrub_text(key), _REDACTED if _is_secret_key(key) else _scrub_text(value))
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit(
        (parts.scheme, netloc, _scrub_text(parts.path), urlencode(query), _scrub_text(parts.fragment))
    )


_NAME_KEYS = frozenset({"name", "key"})


def _local(key: Any) -> str:
    """Key without a leading ``@`` and any ``prefix:``, lower-cased (``@Name``, ``tt:Name`` -> ``name``)."""
    return str(key).lstrip("@").rsplit(":", 1)[-1].lower()


def serialize(value: Any, key: Any = None, _depth: int = 0) -> Any:
    """Convert a value to JSON-safe output, recursively redacting secrets."""
    if _is_secret_key(key):
        return _REDACTED
    if _depth > _MAX_DEPTH:
        return _REDACTED
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except RecursionError:
            return _REDACTED
        except (TypeError, ValueError):
            return _scrub_text(value)
        if isinstance(decoded, (dict, list, str)):
            return json.dumps(serialize(decoded, key, _depth + 1))
        return value
    if isinstance(value, bytes):
        return serialize(value.decode("utf-8", errors="replace"), key, _depth + 1)
    if isinstance(value, dict):
        # ``{"name": "password", "value": ...}``: a secret-named parameter hides its value.
        param = any(_local(k) in _NAME_KEYS and isinstance(v, str) and _text_has_secret_name(v) for k, v in value.items())
        shown: dict[str, Any] = {}
        for k, v in value.items():
            name = str(k)
            safe = _scrub_text(name)  # a device-controlled key such as "password=hunter2" is text like any other
            if safe != name:
                item: Any = _REDACTED  # the key carried a secret, so what it labels is not shown either
            elif param and _local(k) == "value":
                item = _REDACTED
            else:
                item = serialize(v, k, _depth + 1)
            unique, number = safe, 1
            while unique in shown:  # two keys can collapse to the same redacted text: keep both entries
                number += 1
                unique = f"{safe} ({number})"
            shown[unique] = item
        return shown
    if isinstance(value, (list, tuple, set)):
        return [serialize(item, key, _depth + 1) for item in value]
    return str(value)


def _pairs(pairs: tuple[tuple[str, Any], ...]) -> list[list[Any]]:
    return [[k, serialize(v, k)] for k, v in pairs]


def _redact_leaves(value: Any) -> Any:
    """Replace every value of a sensitive body (the keys, like ``data``, are not secret)."""
    if isinstance(value, dict):
        return {str(k): _redact_leaves(v) for k, v in value.items()}
    return _REDACTED


def _body(body: Any) -> Any:
    if body is None:
        return None
    if isinstance(body, JsonBody):
        if body.sensitive:
            return _redact_leaves(body.value)
        return serialize(body.value)
    if isinstance(body, FormBody):
        return _pairs(body.fields)
    if isinstance(body, MultipartBody):
        return {
            "fields": _pairs(body.fields),
            "files": [
                {"name": _scrub_text(f.name), "filename": _scrub_text(f.filename or ""), "size": f.length}
                for f in body.files
            ],
        }
    if isinstance(body, RawBody):
        if isinstance(body.content, bytes):
            return f"<{len(body.content)} bytes {_scrub_text(body.content_type)}>"
        return f"<stream {_scrub_text(body.content_type)}>"
    return _REDACTED


def emit_request(hook: RequestHook | None, request: Request, url: str, timeout: float, verify: Verify) -> None:
    """Call ``hook`` with a redacted description of ``request``. No-op without a hook."""
    if hook is None:
        return
    token = _request_masked.set(_masks(request.masked))
    try:
        record = _record(request, url, timeout, verify)
    finally:
        _request_masked.reset(token)
    hook(record)


def _record(request: Request, url: str, timeout: float, verify: Verify) -> dict[str, Any]:
    return (
        {
            "request": {
                "method": request.method,
                "url": redact_url(url),
                "headers": {
                    str(k): _REDACTED if str(k).lower() in _SENSITIVE_HEADERS or _is_secret_key(k) else serialize(v, k)
                    for k, v in request.headers
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
