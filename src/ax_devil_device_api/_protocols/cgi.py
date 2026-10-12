"""Classic CGI APIs (``/axis-cgi/*.cgi`` with query or form arguments).

These APIs have no common envelope. The binding declares how each argument
is encoded and which codec reads the reply; the codecs here also detect the
plain-text error conventions (``# Error: ...``, ``# Request failed: ...``)
that classic CGIs return with HTTP 200.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

from ..errors import ResponseFormatError
from .._http.types import AuthPolicy, FormBody, Request, Response
from .base import BytesDecoder, CallFlow, Model, Operation, api_error, check_applicability, http_error, parse_result, register_binding
from .state import DeviceState

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
    """

    field: str
    wire: str | None = None
    style: Literal["plain", "csv", "axis_bool", "spread"] = "plain"


def _scalar(value: Any) -> str:
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _encode_args(op: Operation[CgiBinding], params: Model | None) -> list[tuple[str, str]]:
    binding = op.binding
    items = list(binding.fixed_query)
    if params is None:
        return items
    set_fields = params.model_fields_set
    for arg in binding.args:
        if arg.field not in set_fields:
            continue
        value = getattr(params, arg.field)
        if value is None:
            continue
        wire = arg.wire or arg.field
        if arg.style == "spread":
            if not isinstance(value, Mapping):
                raise TypeError(f"{op.api.id}.{op.id}: {arg.field} must be a mapping")
            items.extend((str(k), _scalar(v)) for k, v in value.items())
        elif arg.style == "csv":
            values = value if isinstance(value, (list, tuple)) else [value]
            items.append((wire, ",".join(_scalar(v) for v in values)))
        elif arg.style == "axis_bool":
            items.append((wire, "yes" if value else "no"))
        else:
            items.append((wire, _scalar(value)))
    return items


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
    """XML document; returns the root ``xml.etree.ElementTree.Element``.

    ``error_elements`` are local element names whose presence anywhere in the
    document means failure (e.g. ``GeneralError``).
    """

    error_elements: tuple[str, ...] = ("GeneralError",)


@dataclass(frozen=True)
class Binary:
    """Opaque bytes. Optional checks on media type and leading file signature."""

    media_types: tuple[str, ...] = ()
    signatures: tuple[bytes, ...] = ()


@dataclass(frozen=True)
class JsonReply:
    """A JSON document without a VAPIX envelope."""


Codec = TextOk | TextKv | Text | Xml | Binary | JsonReply

_TEXT_ERROR_PREFIXES = ("# Error", "# Request failed")


@dataclass(frozen=True)
class CgiBinding:
    """Wire binding of one classic CGI operation."""

    path: str
    method: Literal["GET", "POST"] = "GET"
    fixed_query: tuple[tuple[str, str], ...] = ()
    """Fixed arguments, such as ``action=list`` on ``action``-multiplexed CGIs."""
    args: tuple[CgiArg, ...] = ()
    encoding: Literal["query", "form"] = "query"
    """``form`` sends every argument (fixed ones included) as a POST form body."""
    reply: Codec = Text()
    accept: str | None = None
    stream: bool = False
    """Stream the body; the operation returns a stream result of ``bytes`` chunks."""
    auth: AuthPolicy = "required"
    timeout: float | None = None


def _text_errors(op: Operation[Any], text: str) -> None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    errors = [line for line in lines if line.startswith(_TEXT_ERROR_PREFIXES)]
    if errors:
        message = "; ".join(line.lstrip("#").strip() for line in errors)
        raise api_error(op, None, message, http_status=None, details=text)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _decode(op: Operation[CgiBinding], response: Response) -> Any:
    codec = op.binding.reply
    if not 200 <= response.status < 300:
        if not isinstance(codec, Binary) and response.status not in (401, 403, 404):
            _text_errors(op, response.text)
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
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as error:
            _text_errors(op, text)
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
        return root

    _text_errors(op, text)
    if isinstance(codec, TextOk):
        if text.strip() != "OK":
            raise ResponseFormatError(op.api.id, op.id, f"expected 'OK', got {response.excerpt(80)!r}")
        return None
    if isinstance(codec, TextKv):
        result: dict[str, str] = {}
        for line in text.splitlines():
            if not line.strip():
                continue
            key, sep, value = line.partition("=")
            if not sep:
                raise ResponseFormatError(op.api.id, op.id, f"expected key=value lines, got {line[:80]!r}")
            key = key.strip()
            if codec.strip_prefix and key.startswith(codec.strip_prefix):
                key = key[len(codec.strip_prefix):]
            result[key] = value
        return result
    if isinstance(codec, JsonReply):
        try:
            return json.loads(response.content)
        except ValueError as error:
            raise ResponseFormatError(op.api.id, op.id, "response is not valid JSON") from error
    return text


def flow(op: Operation[CgiBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    binding = op.binding
    check_applicability(op, params, None)
    items = tuple(_encode_args(op, params))
    if binding.encoding == "form":
        request = Request(binding.method, binding.path, body=FormBody(items), accept=binding.accept,
                          auth=binding.auth, timeout=binding.timeout, stream=binding.stream)
    else:
        request = Request(binding.method, binding.path, query=items, accept=binding.accept,
                          auth=binding.auth, timeout=binding.timeout, stream=binding.stream)
    response = yield request

    if binding.stream:
        if not 200 <= response.status < 300:
            _decode(op, response)  # raises
        return BytesDecoder()

    data = _decode(op, response)
    if op.result is None:
        return None
    if op.result is ET.Element or op.result is bytes:
        return data
    return parse_result(op, data)


register_binding(CgiBinding, flow)
