"""Helpers for the spec-example contract tests: request building, fake device, comparisons."""

from __future__ import annotations

import json
import re
import string
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from types import UnionType
from typing import Any, get_origin
from urllib.parse import parse_qsl

import httpx


@dataclass
class Part:
    """One part of a received ``multipart/form-data`` body."""

    name: str
    filename: str | None
    content_type: str | None
    content: bytes

    @property
    def is_file(self) -> bool:
        """A file or typed part (an upload or a JSON part), as opposed to a plain text field."""
        return self.filename is not None or self.content_type is not None


def parse_multipart(content_type: str, raw: bytes) -> tuple[Part, ...]:
    """The parts of a ``multipart/form-data`` body, in order."""
    match = re.search(r'boundary="?([^";]+)"?', content_type)
    assert match, f"no multipart boundary in {content_type!r}"
    delimiter = b"--" + match.group(1).encode()
    parts: list[Part] = []
    for chunk in raw.split(delimiter)[1:]:
        if chunk.startswith(b"--"):
            break
        head, _, content = chunk.removeprefix(b"\r\n").partition(b"\r\n\r\n")
        headers = {}
        for line in head.decode("utf-8").split("\r\n"):
            key, _, value = line.partition(":")
            headers[key.strip().lower()] = value.strip()
        disposition = headers.get("content-disposition", "")
        name = re.search(r'\bname="([^"]*)"', disposition)
        filename = re.search(r'\bfilename="([^"]*)"', disposition)
        parts.append(Part(name.group(1) if name else "", filename.group(1) if filename else None, headers.get("content-type"), content.removesuffix(b"\r\n")))
    return tuple(parts)


@dataclass
class Sent:
    method: str
    path: str
    query: dict[str, str]
    json: Any
    form: dict[str, str] | None
    raw: bytes = b""
    pairs: tuple[tuple[str, str], ...] = ()
    content_type: str = ""
    rawquery: str = ""
    parts: tuple["Part", ...] = ()


@dataclass
class Fake:
    """A transport that records the operation's request and answers with the documented response."""

    handler: Any
    calls: list[Sent] = field(default_factory=list)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        ctype = request.headers.get("content-type", "")
        body: Any = None
        form = None
        parts: tuple[Part, ...] = ()
        if request.content:
            if "multipart/form-data" in ctype:
                parts = parse_multipart(ctype, request.content)
                form = {p.name: p.content.decode("utf-8") for p in parts if not p.is_file}
            elif "json" in ctype:
                body = json.loads(request.content)
            elif "x-www-form-urlencoded" in ctype:
                form = dict(parse_qsl(request.content.decode(), keep_blank_values=True))
        sent = Sent(
            request.method, request.url.path, dict(request.url.params.items()), body, form, request.content,
            tuple(request.url.params.multi_items()), ctype, request.url.query.decode("ascii"), parts,
        )
        response = self.handler(sent)
        if response is None:
            return httpx.Response(404, text="unexpected request")
        self.calls.append(sent)
        return response


# -- request model construction ------------------------------------------------


def is_stream_reply(binding: dict) -> bool:
    """Whether a cgi binding streams its reply (``reply: stream`` or ``reply: {stream: ...}``)."""
    reply = binding.get("reply")
    return reply == "stream" or (isinstance(reply, dict) and "stream" in reply)


def example_kind(binding: dict) -> str | None:
    """``session``, ``rtsp`` or ``stream`` for operations that do not make a plain request/response exchange."""
    if "session" in binding:
        return "session"
    if "rtsp" in binding:
        return "rtsp"
    return "stream" if is_stream_reply(binding) else None


def build_jsonrpc(op, request: dict) -> Any:
    params = request.get("params")
    field = getattr(op.binding, "params_field", None)
    if field is not None and op.params is not None:
        # Array or free-form params: the whole value is one wrapped field.
        info = op.params.model_fields[field]
        return op.params.model_validate({info.serialization_alias or field: params})
    params = params or {}
    if op.params is None:
        assert not params, f"{op.id} takes no params but example has {params}"
        return None
    return op.params.model_validate(params)


def _template_regex(template: str, multi: frozenset[str] = frozenset()) -> tuple[re.Pattern[str], list[str]]:
    """Regex for a path template. Placeholders in ``multi`` may span several segments."""
    names: list[str] = []
    out = ""
    for literal, name, _, _ in string.Formatter().parse(template):
        out += re.escape(literal)
        if name:
            names.append(name)
            out += "(.+)" if name in multi else "([^/]+)"
    return re.compile(out + "$"), names


def dca_relative(spec_root: str, binding_path: str) -> str:
    return binding_path[len(spec_root):] if binding_path.startswith(spec_root) else binding_path


def build_dca(op, request: dict, root: str) -> tuple[Any, str]:
    """Return (model, expected absolute path)."""
    template = op.binding.path
    rel = dca_relative(root, template)
    given = request.get("path")
    values: dict[str, str] = {}
    if given is None:
        path = template
    else:
        candidate = given if given.startswith(root) else root + given
        styles = dict(getattr(op.binding, "key_styles", ()) or ())
        dotted = frozenset(n for n, s in styles.items() if s == "dots_to_slashes")
        pattern, names = _template_regex(template, dotted)
        match = pattern.match(candidate)
        assert match, f"example path {given!r} does not match template {rel!r}"
        from urllib.parse import unquote

        values = {}
        for n, v in zip(names, match.groups()):
            # dots_to_slashes: the key is written as nested segments, the model holds the dotted key.
            values[n] = ".".join(unquote(s) for s in v.split("/")) if n in dotted else unquote(v)
        path = candidate
    raw_body = request.get("body")
    # {"data": <value>}: the value may be any JSON type (string, number, boolean, array, null).
    body = raw_body.get("data") if isinstance(raw_body, dict) and "data" in raw_body else {}
    if op.binding.body == "value" and op.binding.body_field:
        # Property setters: the whole {"data": value} is one field.
        from ax_devil_device_api._protocols.dca import _field_for

        name = _field_for(op.params, op.binding.body_field) if op.params else None
        field = op.params.model_fields[name] if op.params and name else None
        wire_name = (field.serialization_alias if field else None) or op.binding.body_field
        data = {**values, wire_name: body}
    else:
        data = {**values, **(body if isinstance(body, dict) else {})}
    if op.params is None:
        assert not data
        return None, path
    return op.params.model_validate(data), path


def _numeric(value: Any) -> Any:
    """Numbers and booleans spelled as text, for models whose fields are int, float or bool enums."""
    if isinstance(value, list):
        return [_numeric(v) for v in value]
    if isinstance(value, str):
        if re.fullmatch(r"[+-]?\d+", value):
            return int(value)
        if re.fullmatch(r"[+-]?\d+\.\d+", value):
            return float(value)
        if value in ("true", "false"):
            return value == "true"
    return value


def build_cgi(op, request: dict) -> tuple[Any, dict[str, str]]:
    """Return (model, expected full argument dict including fixed ones).

    The model gets the example's own values (YAML integers stay integers, so
    integer enums validate); when text does not validate, numbers and booleans
    spelled as text are converted and the model is built again.
    """
    binding = op.binding
    fixed = dict(binding.fixed_query)
    raw = {**(request.get("query") or {}), **(request.get("form") or {})}

    def text(v: Any) -> str:
        if isinstance(v, float):
            from ax_devil_device_api._protocols.cgi import _scalar

            return _scalar(v)  # minimal decimal form: 20.0 is sent as 20
        return "true" if v is True else "false" if v is False else str(v)

    args = {str(k): v for k, v in raw.items()}
    # Fixed bare keys (``?live-sum.json``) may be listed in the example with a null value; they arrive as ``""``.
    for key, value in list(binding.url_query) + list(fixed.items()):
        given = args.pop(key, value)
        assert (given is None and value is None) or text(given) == value, f"example changes fixed argument {key}"
    expected = {**{k: v or "" for k, v in (*binding.url_query, *fixed.items())}, **{k: text(v) for k, v in args.items()}}
    for arg in binding.args:
        if arg.style == "flag" and (arg.wire or arg.field) in args:
            expected[arg.wire or arg.field] = ""  # a flag is a bare key
    data: dict[str, Any] = dict(upload_values(op, request))
    if op.params is None:
        return None, expected
    remaining = dict(args)
    spread = None
    for arg in binding.args:
        if arg.style == "spread":
            spread = arg
            continue
        wire = arg.wire or arg.field
        if wire not in remaining:
            continue
        value = remaining.pop(wire)
        if arg.style == "csv":
            data[arg.field] = list(value) if isinstance(value, list) else text(value).split(",")
        elif arg.style == "axis_bool":
            assert text(value) in ("yes", "no"), value
            data[arg.field] = text(value) == "yes"
        elif arg.style == "flag":
            data[arg.field] = bool(value)
        else:
            data[arg.field] = value
    if remaining:
        assert spread is not None, f"unknown arguments {sorted(remaining)}"
        data[spread.field] = {k: text(v) for k, v in remaining.items()}
    spread_field = getattr(spread, "field", None)
    # Per field: the example's own value, then numbers/booleans spelled as text, then text.
    stage = {k: 0 for k in data}

    def variant(key: str) -> Any:
        v = data[key]
        if key == spread_field:
            return v
        return [v, _numeric(v), v if isinstance(v, (list, dict)) else text(v)][stage[key]]

    from pydantic import ValidationError

    while True:
        try:
            return op.params.model_validate({k: variant(k) for k in data}), expected
        except ValidationError as error:
            bumped = False
            for item in error.errors():
                key = next((k for k in data if item["loc"] and (item["loc"][0] == k or item["loc"][0] in (arg.wire for arg in binding.args if arg.field == k))), None)
                if key is not None and stage[key] < 2 and key != spread_field:
                    stage[key] += 1
                    bumped = True
            if not bumped:
                raise


def _payload(value: Any) -> bytes:
    """Bytes of an example body or part content: text as UTF-8, other JSON values as compact JSON."""
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    return json.dumps(value, separators=(",", ":")).encode("utf-8")


def _part_content(part: dict) -> bytes | None:
    """Bytes an example part describes (``content``, ``content_base64`` or ``size`` filler), if it says any."""
    if "content_base64" in part:
        import base64

        return base64.b64decode(part["content_base64"])
    if "content" in part:
        return _payload(part["content"])
    if "size" in part:
        return b"x" * int(part["size"])
    return None


def upload_values(op, request: dict) -> dict[str, Any]:
    """Values of the upload arguments (and the raw body argument) an example describes, keyed by field name.

    ``request.parts`` feeds the multipart upload arguments (matched by part name, which defaults
    to the field's wire name); ``request.body`` feeds the raw body argument of ``encoding: body``.
    """
    binding = op.binding
    values: dict[str, Any] = {}
    if getattr(binding, "encoding", None) == "multipart":
        by_name = {p["name"]: p for p in request.get("parts") or []}
        for spec in binding.uploads:
            part = by_name.get(spec.part or spec.field)
            if part is not None:
                values[spec.field] = _part_content(part) or b"data"
    elif getattr(binding, "encoding", None) == "body" and "body" in request:
        field = binding.body_field
        is_upload = any(u.field == field for u in binding.uploads)
        values[field] = _payload(request["body"]) if is_upload else request["body"]
    return values


def check_sent_body(op, request: dict, sent: Sent) -> None:
    """Compare a raw body or multipart upload with the example's ``body`` / ``parts``."""
    binding = op.binding
    if getattr(binding, "encoding", None) == "body" and "body" in request:
        expected_type = request.get("content_type") or binding.content_type
        media = sent.content_type.split(";", 1)[0].strip().lower()
        if expected_type is not None:
            assert media == expected_type.split(";", 1)[0].strip().lower(), f"content type {media!r}, expected {expected_type!r}"
        compare_body(media, request["body"], sent.raw)
    if getattr(binding, "encoding", None) == "multipart" and "parts" in request:
        got = [p for p in sent.parts if p.is_file]
        want = request["parts"]
        assert [p.name for p in got] == [p["name"] for p in want], f"parts {[p.name for p in got]}, expected {[p['name'] for p in want]}"
        for part, expected in zip(got, want):
            if "filename" in expected:
                assert part.filename == expected["filename"], f"part {part.name}: filename {part.filename!r}"
            if "content_type" in expected:
                assert part.content_type == expected["content_type"], f"part {part.name}: content type {part.content_type!r}"
            content = _part_content(expected)
            if content is not None:
                assert part.content == content, f"part {part.name}: content differs"
    if "query" in request and "form" in request:
        # Mixed placement: query arguments are in the URL, form arguments in the body.
        for key in request["query"]:
            assert key in sent.query or key in sent.rawquery.replace("=", "&").split("&"), f"{key} should be in the URL"
        for key in request["form"]:
            assert sent.form is not None and key in sent.form and key not in sent.query, f"{key} should be in the body only"
    for key, value in list(op.binding.url_query) + list(request.get("query", {}).items()):
        if value is None and key in sent.rawquery:
            assert not re.search(rf"(?:^|&){re.escape(key)}=", sent.rawquery), f"bare key {key} was sent with a value"


def compare_body(media: str, expected: Any, raw: bytes) -> None:
    """XML structurally, JSON as JSON, text without surrounding whitespace, anything else as bytes."""
    if "xml" in media:
        want = ET.fromstring(expected if isinstance(expected, (str, bytes)) else str(expected))
        assert soap_canonical(ET.fromstring(raw)) == soap_canonical(want), "XML body differs"
    elif "json" in media:
        want = json.loads(expected) if isinstance(expected, (str, bytes)) else expected
        assert json.loads(raw) == want, "JSON body differs"
    elif media.startswith("text/"):
        assert raw.decode("utf-8").strip() == _payload(expected).decode("utf-8").strip(), "text body differs"
    else:
        assert raw == _payload(expected), "body differs"


# -- service_json ----------------------------------------------------------------


def build_service_json(op, request: dict) -> Any:
    params = request.get("params") or {}
    if op.params is None:
        assert not params, f"{op.id} takes no params but example has {params}"
        return None
    return op.params.model_validate(params)


def service_json_fault(error: dict) -> dict:
    """The fault object a device sends for a documented ``{code, message}`` error."""
    code = str(error.get("code"))
    if code.startswith("env:") or ":" not in code:
        top, sub = code, None
    else:
        top, sub = "env:Sender", code
    return {
        "Fault": "env:Sender",
        "FaultCode": top,
        "FaultSubCode": sub,
        "FaultReason": error.get("message", "fault"),
        "FaultMsg": error.get("message"),
    }


# -- soap ------------------------------------------------------------------------

ENV_NS = "http://www.w3.org/2003/05/soap-envelope"


def _clark(name: str, default_ns: str, namespaces: dict[str, str]) -> str:
    """``prefix:Local`` resolves through the binding's prefix map, a bare name takes the default namespace."""
    if ":" in name:
        prefix, local = name.split(":", 1)
        uri = namespaces.get(prefix)
        if uri is not None:
            return f"{{{uri}}}{local}"
        return f"{{{default_ns}}}{local}"
    return f"{{{default_ns}}}{name}"


def _soap_text(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _fill(element: ET.Element, value: Any, default_ns: str, namespaces: dict[str, str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.startswith("@"):
                # A prefixed attribute is in that prefix's namespace; an unprefixed one has no namespace.
                prefix, sep, local = key[1:].partition(":")
                uri = namespaces.get(prefix) if sep else None
                element.set(f"{{{uri}}}{local}" if uri else key[1:], _soap_text(item))
            else:
                for entry in item if isinstance(item, list) else [item]:
                    if entry is None:
                        continue
                    child = ET.SubElement(element, _clark(key, default_ns, namespaces))
                    _fill(child, entry, default_ns, namespaces)
    elif value is not None:
        element.text = _soap_text(value)


def soap_expected_from_params(binding, params: dict | None) -> ET.Element:
    namespaces = dict(getattr(binding, "namespaces", None) or {})
    root = ET.Element(_clark(binding.element, binding.namespace, namespaces))
    _fill(root, params or {}, binding.namespace, namespaces)
    return root


def soap_body_element(xml: str | bytes) -> ET.Element:
    """The first element inside ``Body`` of an envelope, or the element itself when it is not an envelope."""
    root = ET.fromstring(xml)
    if root.tag == f"{{{ENV_NS}}}Envelope":
        body = next(c for c in root if c.tag == f"{{{ENV_NS}}}Body")
        return next(iter(body))
    return root


def soap_canonical(element: ET.Element) -> Any:
    """Namespace-aware, whitespace-insensitive form; sibling order matters only among equal names."""
    children = [soap_canonical(c) for c in element]
    children.sort(key=lambda c: c[0])  # stable: keeps document order inside one name
    return (element.tag, tuple(sorted(element.attrib.items())), (element.text or "").strip(), tuple(children))


def soap_wrap(text: str) -> str:
    """A documented reply as a full envelope (examples may show just the reply element or fault)."""
    text = re.sub(r"\A\s*<\?xml[^>]*\?>", "", text).strip()
    if re.match(r"<(?:\w+:)?Envelope\b", text):
        return text
    # Prefixes the documented fragment uses but does not declare (``env:``, ``ter:``) would not parse.
    prefixes = set(re.findall(r"</?(\w+):", text)) | set(re.findall(r"\s(\w+):\w+=", text))
    prefixes -= {"xml", "xmlns", "env"}
    declared = set(re.findall(r"xmlns:(\w+)=", text))
    extra = "".join(f' xmlns:{p}="urn:undeclared:{p}"' for p in sorted(prefixes - declared))
    return f'<env:Envelope xmlns:env="{ENV_NS}"{extra}><env:Body>{text}</env:Body></env:Envelope>'


def soap_fault_xml(error: dict) -> str:
    code = str(error.get("code"))
    message = escape_xml(str(error.get("message", "fault")))
    top, sub = ("env:Sender", code) if ":" in code and not code.startswith("env:") else (code, None)
    subcode = f"<env:Subcode><env:Value>{escape_xml(sub)}</env:Value></env:Subcode>" if sub else ""
    return (
        f"<env:Fault><env:Code><env:Value>{escape_xml(top)}</env:Value>{subcode}</env:Code>"
        f'<env:Reason><env:Text xml:lang="en">{message}</env:Text></env:Reason></env:Fault>'
    )


def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def soap_documented_fault(response: dict | None) -> dict | None:
    """``{"code": .., "any_of": [..]}`` for a fault reply: an explicit ``error`` or a Fault element in ``text``."""
    if not response:
        return None
    error = response.get("error")
    if isinstance(error, dict):
        return error
    text = response.get("text")
    if not text:
        return None
    try:
        body = soap_body_element(soap_wrap(str(text)))
    except (ET.ParseError, StopIteration):
        return None
    if body.tag != f"{{{ENV_NS}}}Fault":
        return None
    values = [(v.text or "").strip() for v in body.iter(f"{{{ENV_NS}}}Value")]
    text_el = next(body.iter(f"{{{ENV_NS}}}Text"), None)
    return {"any_of": values, "message": (text_el.text or "").strip() if text_el is not None else None}


def soap_response_body(response: dict | None) -> tuple[int, str]:
    response = response or {}
    error = response.get("error")
    if isinstance(error, dict) and not response.get("text"):
        return response.get("status", 500), soap_wrap(soap_fault_xml(error))
    text = response.get("text")
    if text is None:
        return response.get("status", 200), soap_wrap("<Empty/>")
    status = response.get("status", 500 if soap_documented_fault(response) else 200)
    return status, soap_wrap(str(text))


def build_soap(op, request: dict) -> tuple[Any, ET.Element]:
    """Return (model, expected request element). ``request.body`` (XML) wins over ``request.params``."""
    params = request.get("params") or {}
    if op.params is None:
        assert not params, f"{op.id} takes no params but example has {params}"
        model = None
    else:
        model = op.params.model_validate(params)
    if request.get("body"):
        expected = soap_body_element(soap_wrap(str(request["body"])))
    else:
        expected = soap_expected_from_params(op.binding, params)
    return model, expected


# -- rest ------------------------------------------------------------------------


def build_rest(op, request: dict, root: str) -> tuple[Any, str, dict[str, list[str]], Any]:
    """Return (model, expected path, expected query, expected JSON body)."""
    binding = op.binding
    template = binding.path
    given = request.get("path")
    values: dict[str, str] = {}
    if given is None:
        path = template
    else:
        candidate = given if given.startswith(root) else root + given
        pattern, names = _template_regex(template)
        match = pattern.match(candidate)
        assert match, f"example path {given!r} does not match template {template!r}"
        from urllib.parse import unquote

        values = {n: unquote(v) for n, v in zip(names, match.groups())}
        path = candidate
    query = {str(k): v for k, v in (request.get("query") or {}).items()}
    raw_body = request.get("body")
    fields = dict(binding.query)
    data: dict[str, Any] = dict(values)
    for field_name, wire in fields.items():
        if wire in query:
            data[field_name] = query[wire]
    if binding.body == "object" and isinstance(raw_body, dict):
        data.update(raw_body)
    elif binding.body == "value" and binding.body_field:
        from ax_devil_device_api._protocols.dca import _field_for

        name = _field_for(op.params, binding.body_field) if op.params else None
        info = op.params.model_fields[name] if op.params and name else None
        data[(info.serialization_alias if info else None) or binding.body_field] = raw_body
    expected_query = {k: [_soap_text(x) for x in (v if isinstance(v, list) else [v])] for k, v in query.items()}
    expected_body = raw_body if binding.body != "object" or raw_body is not None else {}
    if binding.body == "none":
        expected_body = None
    if op.params is None:
        assert not data
        return None, path, expected_query, expected_body
    from pydantic import ValidationError

    try:
        model = op.params.model_validate(data)
    except ValidationError:
        model = op.params.model_validate({k: _numeric(v) if k in fields else v for k, v in data.items()})
    return model, path, expected_query, expected_body


# -- documented error replies ----------------------------------------------------

_ERROR_TEXT = (
    re.compile(r"\A\s*(?:#\s*)?(?:Error|Request failed)\b", re.IGNORECASE),
    re.compile(r"^\s*#\s*(?:Error|Request failed)\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\A\s*<!--.*-->\s*\Z", re.DOTALL),
    re.compile(r"<(?:\w+:)?GeneralError\b"),
    re.compile(r"""<error\s[^>]*\btype=["']"""),
    re.compile(r"""\bresult=["']ERROR["']""", re.IGNORECASE),
)


def cgi_documented_error(response: dict | None) -> dict | None:
    """The error a cgi example documents, as ``{"code": ..., "message": ...}`` (either may be missing).

    An explicit ``response: {error: {code, message}}`` wins. Otherwise a text reply that
    has one of the known failure shapes (``Error:``, ``# Error``, ``<!-- ... -->``,
    ``GeneralError``, ``<error type=..>``, ``result="ERROR"``) is an expected error.
    A code is only expected when the reply carries one, so these checks do not
    mirror the runtime's parsing.
    """
    if not response:
        return None
    if isinstance(response.get("error"), dict):
        return response["error"]
    text = str(response.get("text", ""))
    if not any(pattern.search(text) for pattern in _ERROR_TEXT):
        if response.get("status", 200) >= 400:
            return {"http_status": response["status"]}  # a bare HTTP failure: HttpError, not ApiError
        return None
    code = None
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if re.fullmatch(r"Error:\s*\d+", first):
        code = int(first.split(":", 1)[1])
    else:
        match = re.search(r"<(?:\w+:)?ErrorCode>\s*(\d+)\s*<", text)
        if match:
            code = int(match.group(1))
    return {"code": code} if code is not None else {}


# -- result checking ------------------------------------------------------------


def check_response_only(op, family: str, response: dict) -> None:
    """Validate a documented response against the result model without building a request."""
    from ax_devil_device_api._protocols.base import parse_result

    if family == "jsonrpc":
        data = response.get("data", {})
    elif family == "dca":
        body = response.get("body")
        data = body.get("data") if isinstance(body, dict) else None
    elif family == "service_json":
        data = response.get("data", {})
    elif family == "rest":
        data = response.get("body")
    else:
        raise AssertionError(f"{family}: response-only validation is not supported")
    check_result(op, parse_result(op, data) if op.result is not None else None)


def check_result(op, result: Any) -> None:
    expected = op.result
    if expected is None:
        assert result is None
        return
    cls = get_origin(expected) or expected
    if isinstance(cls, type) and cls is not UnionType:
        assert isinstance(result, cls), f"{op.id}: expected {expected}, got {type(result)}"
    else:
        # Literal, Annotated and union aliases: the value must validate as the result type.
        from ax_devil_device_api._protocols.base import RESPONSE_CONTEXT, adapter

        adapter(expected).validate_python(result, context={RESPONSE_CONTEXT: True})
