"""Classic CGI APIs (``/axis-cgi/*.cgi`` with query or form arguments).

These APIs have no common envelope. The binding declares how each argument
is encoded and which codec reads the reply; the codecs here also detect the
plain-text error conventions (``# Error: ...``, ``# Request failed: ...``,
``Error: ...``, ``Error:`` followed by a message line)
that classic CGIs return with HTTP 200.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Literal
from urllib.parse import quote

from pydantic_core import to_json

from .._http.types import AuthPolicy, FormBody, MultipartBody, RawBody, Request, Response
from .._http.upload import UploadSpec, deferred_upload, file_part
from ..errors import ResponseFormatError
from .base import CallFlow, Model, Operation, api_error, check_applicability, http_error, parse_result, register_binding
from .state import DeviceState
from .xmlmap import XmlMap, XmlStatusError, extract, is_list_type, prune_empty, status_error

# ---------------------------------------------------------------------------
# Arguments


@dataclass(frozen=True)
class CgiArg:
    """How one params field is sent.

    - ``plain``: ``wire=value``.
    - ``csv``: a list joined with commas.
    - ``axis_bool``: ``True``/``False`` sent as ``yes``/``no``.
    - ``spread``: a mapping whose items are sent as separate ``key=value`` pairs
      (``param.cgi`` ``update``); ``wire`` is ignored.
    - ``flag``: a boolean sent as the bare key ``wire`` (no ``=``) when true, nothing when false.

    ``wire`` may contain ``{name}`` placeholders, filled from the params field ``name``
    (``Image.I{n}.Name``). ``place`` overrides where the argument goes: ``query`` (the URL)
    or ``form`` (the body fields); ``None`` means the encoding's default.
    """

    field: str
    wire: str | None = None
    style: Literal["plain", "csv", "axis_bool", "spread", "flag"] = "plain"
    place: Literal["query", "form"] | None = None


def _scalar(value: Any) -> str:
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value == value and value not in (float("inf"), float("-inf")):
        # Minimal decimal form: 10.0 -> "10", 1e-05 -> "0.00001", 0.5 -> "0.5".
        text = format(Decimal(repr(value)), "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return "0" if text in ("-0", "") else text
    return str(value)


_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def _field_for(params: Model, placeholder: str) -> str | None:
    """The params field a placeholder refers to, by Python name or wire name."""
    fields = type(params).model_fields
    if placeholder in fields:
        return placeholder
    for name, info in fields.items():
        if placeholder in (info.serialization_alias, info.validation_alias, info.alias):
            return name
    return None


def _fill_values(op: Operation[CgiBinding], params: Model | None) -> dict[str, str]:
    """Text of every ``{name}`` placeholder used by the binding's path, argument names and reply prefix."""
    binding = op.binding
    texts = [binding.path, *(a.wire or "" for a in binding.args)]
    texts += [value for _, value in (*binding.url_query, *binding.fixed_query) if value]
    if isinstance(binding.reply, TextKv) and binding.reply.strip_prefix:
        texts.append(binding.reply.strip_prefix)
    names = {name for text in texts for name in _PLACEHOLDER.findall(text)}
    if isinstance(binding.reply, TextKv) and isinstance(op.result, type) and issubclass(op.result, Model):
        for info in op.result.model_fields.values():
            for alias in (info.validation_alias, info.alias):
                if isinstance(alias, str):
                    names.update(_PLACEHOLDER.findall(alias))
    values: dict[str, str] = {}
    for name in sorted(names):
        field = _field_for(params, name) if params is not None else None
        value = getattr(params, field, None) if field is not None else None
        if value is None:
            raise TypeError(f"{op.api.id}.{op.id}: missing argument {name!r} (used in the request's names or path)")
        values[name] = _scalar(value)
    return values


def _fill(template: str, values: Mapping[str, str], *, quoted: bool = False) -> str:
    if "{" not in template:
        return template
    return _PLACEHOLDER.sub(lambda m: quote(values[m.group(1)], safe="") if quoted else values[m.group(1)], template)


def _encode_args(
    op: Operation[CgiBinding], params: Model | None, values: Mapping[str, str] | None = None,
) -> tuple[list[tuple[str, str | None]], list[tuple[str, str | None]]]:
    """``(query, form)`` argument lists: fixed arguments, then the params, each in its place."""
    binding = op.binding
    values = values or {}
    default = "query" if binding.encoding in ("query", "body") else "form"
    query: list[tuple[str, str | None]] = [(k, _fill(v, values) if v else v) for k, v in binding.url_query]
    form: list[tuple[str, str | None]] = []
    (query if default == "query" else form).extend((k, _fill(v, values) if v else v) for k, v in binding.fixed_query)
    if params is None:
        return query, form
    set_fields = params.model_fields_set
    for arg in binding.args:
        if arg.field not in set_fields:
            continue
        value = getattr(params, arg.field)
        if value is None:
            continue
        items = form if (arg.place or default) == "form" else query
        wire = _fill(arg.wire or arg.field, values)
        if arg.style == "spread":
            if not isinstance(value, Mapping):
                raise TypeError(f"{op.api.id}.{op.id}: {arg.field} must be a mapping")
            items.extend((str(k), _scalar(v)) for k, v in value.items())
        elif arg.style == "csv":
            seq = value if isinstance(value, (list, tuple)) else [value]
            items.append((wire, ",".join(_scalar(v) for v in seq)))
        elif arg.style == "axis_bool":
            items.append((wire, "yes" if value else "no"))
        elif arg.style == "flag":
            if value:
                items.append((wire, None))
        else:
            items.append((wire, _scalar(value)))
    return query, form


def _text_pairs(op: Operation[Any], pairs: list[tuple[str, str | None]]) -> tuple[tuple[str, str], ...]:
    for key, value in pairs:
        if value is None:
            raise TypeError(f"{op.api.id}.{op.id}: bare key {key!r} can only be sent in the URL query")
    return tuple((key, value) for key, value in pairs if value is not None)


def _body_bytes(value: Any) -> bytes:
    """A raw request body from ``bytes``, a ``str`` (UTF-8), a model or a JSON-compatible value."""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, Model):
        return to_json(value.to_wire())
    return to_json(value)


# ---------------------------------------------------------------------------
# Response codecs


@dataclass(frozen=True)
class TextOk:
    """Body must be ``OK``; returns ``None``."""


@dataclass(frozen=True)
class TextKv:
    """``key=value`` lines; returns ``dict[str, str]``. ``strip_prefix`` is removed from keys."""

    strip_prefix: str | None = None


@dataclass(frozen=True)
class Text:
    """Plain text; returns ``str`` after error detection."""


@dataclass(frozen=True)
class Xml:
    """XML document.

    Returns the root ``xml.etree.ElementTree.Element``, or, with ``map``, the
    data extracted for the operation's result model. ``error_elements`` are
    local element names whose presence anywhere means failure (e.g.
    ``GeneralError``); ``status_error`` describes attribute-style failures
    such as ``result="ERROR"``.
    """

    error_elements: tuple[str, ...] = ("GeneralError",)
    map: XmlMap | None = None
    status_error: XmlStatusError | None = None


FRAGMENT_ROOT = "fragment"
"""Tag of the synthetic root that wraps a reply with several top-level elements."""

_XML_DECLARATION = re.compile(rb"^\s*<\?xml[^>]*\?>")


def _parse_xml(content: bytes) -> ET.Element:
    """Parse a reply; a sequence of sibling top-level elements is wrapped in a synthetic ``fragment`` root.

    Only a body that really is several elements counts (whitespace, comments and processing
    instructions between them are fine). Leading or trailing text, or a body with no element, is
    not a fragment, so a plain-text error such as ``Error: camera not found`` is never wrapped.
    """
    try:
        return ET.fromstring(content)
    except ET.ParseError as error:
        body = _XML_DECLARATION.sub(b"", content, count=1)
        try:
            root = ET.fromstring(b"<" + FRAGMENT_ROOT.encode() + b">" + body + b"</" + FRAGMENT_ROOT.encode() + b">")
        except ET.ParseError:
            raise error from None
        if len(root) == 0 or (root.text or "").strip() or any((child.tail or "").strip() for child in root):
            raise error from None
        return root


@dataclass(frozen=True)
class Binary:
    """Opaque bytes. Optional checks on media type and leading file signature."""

    media_types: tuple[str, ...] = ()
    signatures: tuple[bytes, ...] = ()


@dataclass(frozen=True)
class JsonReply:
    """A JSON document without a VAPIX envelope."""


@dataclass(frozen=True)
class Stream:
    """The body is streamed, not read: the operation returns a ``StreamResult`` / ``AsyncStreamResult``.

    ``decoder``: ``bytes`` (raw chunks), ``mjpeg`` (``Part`` per frame of a
    ``multipart/x-mixed-replace`` body) or ``lines`` (text lines).
    """

    decoder: Literal["bytes", "mjpeg", "lines"] = "bytes"
    encoding: str = "utf-8"
    """Text encoding for the ``lines`` decoder."""


@dataclass(frozen=True)
class TextLines:
    """Plain text read as lines; returns ``list[str]`` of the non-blank lines, stripped.

    ``skip`` leading (non-blank) lines are dropped, for a fixed header such as
    ``Preset Positions for camera 1``.
    """

    skip: int = 0


Codec = TextOk | TextKv | Text | Xml | Binary | JsonReply | Stream | TextLines

_TEXT_ERROR_PREFIXES = ("# Error", "# Request failed")
_COMMENT_ERROR = re.compile(r"<!--((?:(?!-->).)*)-->", re.DOTALL)


@dataclass(frozen=True)
class CgiBinding:
    """Wire binding of one classic CGI operation."""

    path: str
    method: Literal["GET", "POST"] = "GET"
    fixed_query: tuple[tuple[str, str | None], ...] = ()
    """Fixed arguments, such as ``action=list`` on ``action``-multiplexed CGIs. They go where the
    encoding sends arguments by default (the URL, or the body for ``form`` and ``multipart``).
    A ``None`` value is a bare key (``?live-sum.json``), URL only. A value may contain ``{name}``
    placeholders, filled from the required scalar params field ``name`` (``group=Image.I{n}.RateControl``)."""
    url_query: tuple[tuple[str, str | None], ...] = ()
    """Fixed arguments that always go in the URL, even when the encoding sends arguments in the body."""
    args: tuple[CgiArg, ...] = ()
    encoding: Literal["query", "form", "multipart", "body"] = "query"
    """Where arguments go by default:

    - ``query``: the URL.
    - ``form``: a URL-encoded POST body (fixed ones included).
    - ``multipart``: text parts of a ``multipart/form-data`` body, plus the ``uploads`` files.
    - ``body``: arguments in the URL; the one ``body_field`` is the raw body, sent as ``content_type``.
    """
    content_type: str | None = None
    """Content type of a raw ``body``."""
    body_field: str | None = None
    content_type_field: str | None = None
    """``body`` encoding: the params field whose value, when set, is the Content-Type of this call's body."""
    uploads: tuple[UploadSpec, ...] = ()
    """File arguments: multipart file parts, or the raw body when ``encoding`` is ``body``."""
    reply: Codec = Text()
    accept: str | None = None
    stream: bool = False
    """Stream the body; the operation returns a stream result of ``bytes`` chunks."""
    auth: AuthPolicy = "required"
    timeout: float | None = None


def _text_errors(op: Operation[Any], text: str, http_status: int | None = None) -> None:
    """Raise ``ApiError`` for the documented plain-text failure replies.

    Forms (all returned by the device, usually with HTTP 200):

    - ``# Error: <message>`` / ``# Request failed: <message>`` on any line.
    - ``Error: <code or message>`` as the first non-empty line (application.cgi,
      usergroup/pwdgrp style CGIs).
    - ``Error:`` alone on the first line with the message on the following
      lines (privacymask.cgi, com/ptz.cgi).
    - A body that is one HTML comment, ``<!-- <message> -->`` (imagesize.cgi
      with a ``camera`` argument). Only a whole-body comment counts.
    """
    envelope = _json_error(text)
    if envelope is not None:
        code, message = envelope
        raise api_error(op, code, message, http_status=http_status, details=text)
    comment = _COMMENT_ERROR.fullmatch(text.strip())
    if comment:
        raise api_error(op, None, comment.group(1).strip() or "Error", http_status=http_status, details=text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    errors = [line for line in lines if line.startswith(_TEXT_ERROR_PREFIXES)]
    if errors:
        message = "; ".join(line.lstrip("#").strip() for line in errors)
        raise api_error(op, None, message, http_status=http_status, details=text)
    if lines and lines[0].startswith("Error:"):
        rest = lines[0][len("Error:"):].strip()
        if not rest:
            rest = "; ".join(lines[1:])
        code: int | str | None = None
        if rest.isdigit():
            code = int(rest)
        elif len(lines) == 2 and lines[0] == "Error:" and lines[1].isdigit():
            code = int(lines[1])
        raise api_error(op, code, rest or "Error", http_status=http_status, details=text)


def _json_error(text: Any) -> tuple[int | str | None, str] | None:
    """``(id, message)`` of a ``{"error": {"id": .., "message": ..}}`` envelope, else ``None``.

    Only a document whose single member is ``error`` with an ``id`` or ``message`` counts.
    """
    if isinstance(text, str):
        stripped = text.strip()
        if not stripped.startswith("{"):
            return None
        try:
            text = json.loads(stripped)
        except ValueError:
            return None
    if not (isinstance(text, dict) and list(text) == ["error"] and isinstance(text["error"], dict)):
        return None
    error = text["error"]
    if "id" not in error and "message" not in error:
        return None
    code = error.get("id")
    if isinstance(code, str) and code.strip().isdigit():
        code = int(code)
    if not isinstance(code, (int, str)) or isinstance(code, bool):
        code = None
    message = error.get("message")
    return code, str(message) if message else (f"error {code}" if code is not None else "Error")


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _split_array_values(data: dict[str, Any], model: Any) -> dict[str, Any]:
    """Split comma-separated values, only for fields the result model declares as arrays."""
    if not (isinstance(model, type) and issubclass(model, Model)):
        return data
    arrays = set()
    for name, info in model.model_fields.items():
        if is_list_type(info.annotation):
            arrays.update(k for k in (name, info.alias, info.validation_alias) if isinstance(k, str))
    return {
        key: ([part.strip() for part in value.split(",")] if value else []) if key in arrays and isinstance(value, str) else value
        for key, value in data.items()
    }


def _templated_keys(data: dict[str, Any], model: Any, values: Mapping[str, str] | None) -> dict[str, Any]:
    """Rename reply keys to the result model's templated names (``Image.I1.Name`` -> ``Image.I{n}.Name``)."""
    if not values or not (isinstance(model, type) and issubclass(model, Model)):
        return data
    renames: dict[str, str] = {}
    for info in model.model_fields.values():
        for alias in (info.validation_alias, info.alias):
            if isinstance(alias, str) and "{" in alias:
                renames[_fill(alias, values)] = alias
    return {renames.get(key, key): value for key, value in data.items()} if renames else data


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _decode(op: Operation[CgiBinding], response: Response, values: Mapping[str, str] | None = None) -> Any:
    codec = op.binding.reply
    if not 200 <= response.status < 300:
        # A 401 may carry a plain-text API error (pwdgrp.cgi: "Error: initial admin user must be created first.")
        # when the request was sent without a challenge; any other 401 body is the device's login page.
        if not isinstance(codec, Binary) and (response.status not in (401, 403, 404) or (response.status == 401 and op.binding.auth == "if_challenged")):
            _text_errors(op, response.text, response.status)
        raise http_error(op, response)

    if isinstance(codec, Binary):
        if codec.media_types and response.media_type not in codec.media_types:
            raise ResponseFormatError(op.api.id, op.id, f"unexpected content type {response.media_type!r}")
        if not response.content:
            raise ResponseFormatError(op.api.id, op.id, "empty response body")
        if codec.signatures and not response.content.startswith(codec.signatures):
            raise ResponseFormatError(op.api.id, op.id, "response body has an unexpected file signature")
        return response.content

    text = response.text
    if isinstance(codec, Xml):
        if not response.content.strip() and op.result is None:
            return None
        try:
            root = _parse_xml(response.content)
        except ET.ParseError as error:
            _text_errors(op, text, response.status)
            raise ResponseFormatError(op.api.id, op.id, f"invalid XML: {error}") from error
        for element in root.iter():
            if _local(element.tag) in codec.error_elements:
                code_text = next((e.text for e in element.iter() if _local(e.tag) in ("ErrorCode", "Code")), None)
                message = next((e.text for e in element.iter() if _local(e.tag) in ("ErrorDescription", "Description", "Message")), None)
                code: int | str | None = int(code_text) if code_text and code_text.strip().isdigit() else code_text
                raise api_error(
                    op, code, message or _local(element.tag), http_status=response.status,
                    details=ET.tostring(element, encoding="unicode"),
                )
        if codec.status_error is not None:
            failure = status_error(root, codec.status_error)
            if failure is not None:
                code_text, message = failure
                code = int(code_text) if code_text and code_text.isdigit() else code_text
                raise api_error(op, code, message, http_status=response.status, details=text)
        if codec.map is None:
            return root
        return prune_empty(extract(root, codec.map), op.result)

    _text_errors(op, text, response.status)
    if isinstance(codec, TextOk):
        if text.strip() != "OK":
            raise ResponseFormatError(op.api.id, op.id, f"expected 'OK', got {response.excerpt(80)!r}")
        return None
    if isinstance(codec, TextKv):
        result: dict[str, Any] = {}
        prefix = _fill(codec.strip_prefix, values or {}) if codec.strip_prefix else None
        for line in text.splitlines():
            if not line.strip():
                continue
            key, sep, value = line.partition("=")
            if not sep:
                raise ResponseFormatError(op.api.id, op.id, f"expected key=value lines, got {line[:80]!r}")
            key = key.strip()
            if prefix and key.startswith(prefix):
                key = key[len(prefix):]
            result[key] = _unquote(value.strip())
        return _split_array_values(_templated_keys(result, op.result, values), op.result)
    if isinstance(codec, TextLines):
        return [line.strip() for line in text.splitlines() if line.strip()][codec.skip :]
    if isinstance(codec, JsonReply):
        if not response.content.strip():
            return None
        try:
            return json.loads(response.content)
        except ValueError as error:
            raise ResponseFormatError(op.api.id, op.id, "response is not valid JSON") from error
    return text


def _path(op: Operation[CgiBinding], values: Mapping[str, str]) -> str:
    path = _fill(op.binding.path, values, quoted=True)
    if "{" in op.binding.path and any(segment in (".", "..") for segment in path.split("/")):
        # These would address a different resource after URL normalization.
        raise ValueError(f"{op.api.id}.{op.id}: the path argument gives {path!r}, which is not a valid path")
    return path


def _build(op: Operation[CgiBinding], params: Model | None, values: Mapping[str, str]) -> Request:
    binding = op.binding
    path = _path(op, values)
    query, form = _encode_args(op, params, values)
    body: FormBody | MultipartBody | RawBody | None = None
    if binding.encoding == "form":
        body = FormBody(_text_pairs(op, form))
    elif binding.encoding == "multipart":
        files = []
        for spec in binding.uploads:
            value = getattr(params, spec.field, None) if params is not None else None
            if value is not None:
                files.append(file_part(spec.part or spec.field, value, filename=spec.filename, content_type=spec.content_type))
        body = MultipartBody(_text_pairs(op, form), tuple(files))
    elif binding.encoding == "body":
        assert binding.body_field is not None
        value = getattr(params, binding.body_field, None) if params is not None else None
        # A content type given with the call wins over the upload's and the binding's.
        given = getattr(params, binding.content_type_field, None) if params is not None and binding.content_type_field else None
        if value is not None:
            spec = next((u for u in binding.uploads if u.field == binding.body_field), None)
            if spec is not None:
                content, _, ctype = deferred_upload(value, filename=None, content_type=spec.content_type)
                size = len(content) if isinstance(content, bytes) else None
                body = RawBody(content, given or ctype or binding.content_type or "application/octet-stream", size=size)
            else:
                body = RawBody(_body_bytes(value), given or binding.content_type or "application/octet-stream")
    return Request(
        binding.method, path, query=tuple(query), body=body, accept=binding.accept,
        auth=binding.auth, timeout=binding.timeout, stream=binding.stream,
    )


def flow(op: Operation[CgiBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    binding = op.binding
    check_applicability(op, params, None)
    values = _fill_values(op, params)
    response = yield _build(op, params, values)

    if binding.stream:
        if not 200 <= response.status < 300:
            _decode(op, response, values)  # raises
        from .._streams import decoder_for  # imported here: _streams itself imports this package

        return decoder_for(binding.reply, response, api=op.api.id)

    data = _decode(op, response, values)
    if op.result is None:
        return None
    if op.result is ET.Element or op.result is bytes:
        return data
    return parse_result(op, data)


register_binding(CgiBinding, flow)
