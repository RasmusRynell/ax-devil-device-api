"""Redacted request descriptions for the ``on_request`` debug hook."""

from __future__ import annotations

import json
import re
import ssl
from typing import Any
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

from .config import RequestHook, Verify
from .types import FormBody, JsonBody, MultipartBody, RawBody, Request

_REDACTED = "<redacted>"
# Key / header / element / attribute names that identify a secret (matched as substrings, case-insensitive).
_SECRET_KEY_RE = re.compile(
    r"(?:pass(?:word)?|passwd|pwd|secret|token|api[-_]?key|access[-_]?key|private[-_]?key|authorization|credential"
    r"|client[-_]?secret|cookie|shared[-_]?key|account[-_]?key|session[-_]?token|storage[-_]?key|sas[-_]?token"
    r"|secret[-_]?access)",
    re.IGNORECASE,
)
_SECRET_EXACT = {"sas", "sig", "psk", "signature", "sastoken", "sas_token"}
# Headers whose whole value is dropped by name (no content parsing). Any name matching the secret set is dropped too.
_SENSITIVE_HEADERS = frozenset({"authorization", "proxy-authorization", "cookie", "set-cookie"})
_extra_secret_names: set[str] = set()
_TOKEN_RE = re.compile(r"[A-Za-z0-9_.\-]+")
_AUTHORITY_END = re.compile(r"[/?#\s\"'<>]")
_SEGMENT_RE = re.compile(r"[^&\r\n]+")
_ATTR_RE = re.compile(r"""([^\s=/"'<>]+)(\s*=\s*)("[^"]*"|'[^']*'|[^\s"'>]+)""")
_NAME_RE = re.compile(r"[^\s/>]+")
_MAX_DECODE_LAYERS = 4
_MAX_DEPTH = 32


def register_secret_names(names: Any) -> None:
    """Treat these wire names (from ``x-masked`` in the specs) as secrets everywhere in request records."""
    _extra_secret_names.update(str(n).lower() for n in names)


def _is_secret_key(key: Any) -> bool:
    """Return whether a mapping key, header, element or attribute name identifies a secret."""
    text = str(key)
    lowered = text.lower()
    return bool(_SECRET_KEY_RE.search(text) or lowered in _SECRET_EXACT or lowered in _extra_secret_names)


def _is_secret_local(name: str) -> bool:
    return _is_secret_key(name.rsplit(":", 1)[-1])


def _text_has_secret_name(text: str) -> bool:
    """Whether free text names a secret (substring match, or an exact/registered whole token)."""
    if _SECRET_KEY_RE.search(text):
        return True
    return any(t.lower() in _SECRET_EXACT or t.lower() in _extra_secret_names for t in _TOKEN_RE.findall(text))


def _scrub_userinfo(text: str) -> str:
    """Replace URL userinfo (``scheme://user:pass@host``) found by a linear scan for ``://``."""
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
        if at >= 0 and text[start:at] != _REDACTED:
            out.append(text[done:start])
            out.append(_REDACTED)
            done = at
        pos = text.find("://", max(end, start))
    out.append(text[done:])
    return "".join(out)


def _scrub_pairs(text: str) -> str:
    """Redact everything after ``=`` once the text before it names a secret (``a=1&password=x``, ``Cookie: sid=x``)."""
    if "=" not in text:
        return text
    out: list[str] = []
    done = 0
    for seg in _SEGMENT_RE.finditer(text):
        s, e = seg.span()
        scanned = s
        eq = text.find("=", s, e)
        while eq >= 0:
            if _text_has_secret_name(text[scanned:eq]):
                value = text[eq + 1 : e]
                if value and value != _REDACTED:
                    out.append(text[done : eq + 1])
                    out.append(_REDACTED)
                    done = e
                break
            scanned = eq + 1
            eq = text.find("=", eq + 1, e)
    out.append(text[done:])
    return "".join(out)


def _scrub_plain(text: str) -> str:
    return _scrub_userinfo(_scrub_pairs(text))


def _tag_end(text: str, start: int) -> int:
    """Index of the ``>`` closing the tag opened at ``start`` (quote-aware), or -1."""
    i = start + 1
    n = len(text)
    while i < n:
        gt = text.find(">", i)
        if gt < 0:
            return -1
        quote = -1
        for q in ('"', "'"):
            k = text.find(q, i, gt)
            if k >= 0 and (quote < 0 or k < quote):
                quote = k
        if quote < 0:
            return gt
        close = text.find(text[quote], quote + 1)
        if close < 0:
            return gt
        i = close + 1
    return -1


_NAME_KEYS = frozenset({"name", "key"})


def _scrub_tag(interior: str) -> tuple[str, str, bool, bool, bool]:
    """Return (scrubbed interior, local name, is_end_tag, is_self_closing, names_a_secret_parameter)."""
    closing = interior.startswith("/")
    selfclose = interior.rstrip().endswith("/")
    m = _NAME_RE.match(interior[1:] if closing else interior)
    name = m.group(0).rsplit(":", 1)[-1] if m else ""
    attrs = list(_ATTR_RE.finditer(interior))
    # ``<Parameter Name="Password" Value="x"/>``: a secret-named parameter hides its value attribute and content.
    param = not closing and any(
        a.group(1).rsplit(":", 1)[-1].lower() in _NAME_KEYS and _text_has_secret_name(a.group(3).strip("\"'"))
        for a in attrs
    )

    def attr(match: re.Match[str]) -> str:
        key, eq, value = match.groups()
        quote = value[0] if value[0] in "\"'" else ""
        inner = value[1:-1] if quote else value
        local = key.rsplit(":", 1)[-1]
        hide = _is_secret_local(key) or (param and local.lower() == "value")
        return f"{key}{eq}{quote}{_REDACTED if hide else _scrub_plain(inner)}{quote}"

    return _ATTR_RE.sub(attr, interior), name, closing, selfclose, param


def _scrub_markup(text: str) -> str:
    """Redact XML/SOAP: values of secret-named elements (text, CDATA, children) and attributes, else plain scrub."""
    out: list[str] = []
    i = 0
    n = len(text)
    skip = 0  # nesting depth inside a secret element
    while i < n:
        lt = text.find("<", i)
        if lt < 0:
            if not skip:
                out.append(_scrub_plain(text[i:]))
            break
        if lt > i and not skip:
            out.append(_scrub_plain(text[i:lt]))
        if text.startswith("<![CDATA[", lt):
            close = text.find("]]>", lt)
            end = n if close < 0 else close + 3
            if not skip:
                body = text[lt + 9 : end - 3 if close >= 0 else end]
                out.append(f"<![CDATA[{_scrub_plain(body)}" + ("]]>" if close >= 0 else ""))
            i = end
            continue
        nxt = text[lt + 1 : lt + 2]
        if not (nxt.isalpha() or nxt in ("/", "!", "?", "_", ":")):
            if not skip:
                out.append("<")
            i = lt + 1
            continue
        gt = _tag_end(text, lt)
        if gt < 0:
            if not skip:
                out.append(_scrub_plain(text[lt:]))
            break
        interior = text[lt + 1 : gt]
        if nxt in ("!", "?"):
            if not skip:
                out.append(f"<{_scrub_plain(interior)}>")
            i = gt + 1
            continue
        scrubbed, name, closing, selfclose, param = _scrub_tag(interior)
        if skip:
            if closing:
                skip -= 1
                if not skip:
                    out.append(f"<{scrubbed}>")
            elif not selfclose:
                skip += 1
        else:
            out.append(f"<{scrubbed}>")
            if not closing and not selfclose and (param or _is_secret_key(name)):
                out.append(_REDACTED)
                skip = 1
        i = gt + 1
    return "".join(out)


def _scrub_one(text: str) -> str:
    if "<" in text and ">" in text:
        return _scrub_markup(text)
    return _scrub_plain(text)


def _scrub_text(text: str) -> str:
    """Redact credentials in free text, looking through percent-encoding layers; fail closed past the layer limit."""
    if not text:
        return text
    current = text
    found = False
    layers = 0
    while True:
        redacted = _scrub_one(current)
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
        param = any(
            str(k).lower() in _NAME_KEYS and isinstance(v, str) and _text_has_secret_name(v) for k, v in value.items()
        )
        return {
            str(k): _REDACTED if param and str(k).lower() == "value" else serialize(v, k, _depth + 1)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [serialize(item, key, _depth + 1) for item in value]
    return str(value)


def _pairs(pairs: tuple[tuple[str, Any], ...]) -> list[list[Any]]:
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
            "files": [
                {"name": _scrub_text(f.name), "filename": _scrub_text(f.filename or ""), "size": f.length}
                for f in body.files
            ],
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
