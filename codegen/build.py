"""Build the intermediate model (``ApiDef``) from a validated spec."""

from __future__ import annotations

import json
import re
from typing import Any

from .loader import LoadedSpec, SpecError
from .model import ApiDef, Applic, FieldDef, OpDef, RoundTrip, TypeDef
from .naming import RESERVED_ARG_NAMES, NamingError, field_name, pascal_case, snake_case
from .xmlreply import reply_kind

SUPPORTED_FAMILIES = ("jsonrpc", "dca", "cgi", "service_json", "soap", "rest", "ws", "rtsp")

# WebSocket sessions: codec -> default setup, and the `connect` options each setup takes
# (name, annotation). The setups and codecs live in `_runtime/ws_codecs.py`.
SESSION_CODECS = {"events": "events", "datahub": "datahub", "raw": "none"}
SESSION_SETUPS: dict[str, list[tuple[str, str]]] = {
    "events": [("event_filter_list", "Sequence[EventFilter | Mapping[str, str]] | None = None")],
    "datahub": [("subscriptions", "Sequence[Mapping[str, Any]] | None = None")],
    "none": [],
}
STREAM_DECODERS = ("bytes", "mjpeg", "lines")
RTSP_RESERVED_ARGS = frozenset({"port", "include_credentials"})
# Names the generated module imports only when it uses the feature.
FEATURE_RESERVED = {
    "stream": frozenset({"Stream", "StreamResult", "AsyncStreamResult", "Part"}),
    "session": frozenset(
        {"Session", "AsyncSession", "SessionSpec", "SESSIONS", "Heartbeat", "DEFAULT_HEARTBEAT", "Sequence",
         "AbstractContextManager", "AbstractAsyncContextManager"}
    ),
    "events": frozenset({"EventFilter", "EventsCodec", "events_setup"}),
    "datahub": frozenset({"DataHubCodec", "datahub_setup"}),
    "rtsp": frozenset({"RtspBinding", "RtspUrl"}),
}  # fmt: skip


def op_kind(family: str, binding: dict[str, Any]) -> tuple[str, str | None]:
    """``(kind, stream decoder)`` of an operation from its raw binding: call, stream, session or rtsp."""
    if "session" in binding:
        return "session", None
    if "rtsp" in binding:
        return "rtsp", None
    if family == "cgi" and "reply" in binding:
        kind, options = reply_kind(binding)
        if kind == "stream":
            return "stream", options.get("decoder", "bytes")
    return "call", None


def detect_features(data: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for raw in (data.get("operations") or {}).values():
        binding = raw.get("binding") or {}
        kind, _ = op_kind(data["family"], binding)
        if kind in ("stream", "rtsp"):
            out.add(kind)
        elif kind == "session":
            out.add("session")
            session = binding["session"]
            codec = session.get("codec", "raw")
            setup = session.get("setup") or SESSION_CODECS.get(codec, "none")
            if codec == "events" or setup == "events":
                out.add("events")
            if codec == "datahub" or setup == "datahub":
                out.add("datahub")
    return out

# Names the generated module imports or defines itself.
RESERVED_MODULE_NAMES = frozenset(
    {
        "Annotated", "Any", "ClassVar", "Literal", "overload", "Mapping", "MISSING", "Field", "ET", "builtins",
        "RequestOptions", "ApiDiscovery", "ApiInfo", "ApiVersion", "Applicability", "DcaDiscovery", "ErrorCode",
        "Family", "Model", "Operation", "ParamDiscovery", "JsonRpcBinding", "GetSupportedVersions", "FixedVersion",
        "NoVersion", "DcaBinding", "CgiArg", "CgiBinding", "Text", "TextKv", "TextOk", "Xml", "Binary", "JsonReply",
        "XmlMap", "XmlField", "XmlStatusError", "AsyncApi", "SyncApi", "INFO", "OPS", "PATH", "ROOT",
        "AcapDiscovery", "ServiceDiscovery", "ServiceJsonBinding", "SoapBinding", "RestBinding", "TextLines", "UploadSource", "UploadSpec",
        "JsonRpcMultipart", "not_sent",
    }
)  # fmt: skip
BUILTIN_SHADOWS = ("list", "dict", "set", "tuple", "str", "int", "float", "bool", "bytes", "type", "object")

_CONSTRAINTS = (
    ("minLength", "min_length"),
    ("maxLength", "max_length"),
    ("minItems", "min_length"),
    ("maxItems", "max_length"),
    ("pattern", "pattern"),
    ("minimum", "ge"),
    ("exclusiveMinimum", "gt"),
    ("maximum", "le"),
    ("exclusiveMaximum", "lt"),
    ("multipleOf", "multiple_of"),
)
_SCALARS = {"string": "str", "integer": "int", "number": "float", "boolean": "bool", "null": "None"}


_KIND_RETURNS = {"stream": "stream result", "session": "session context manager", "rtsp": "RtspUrl"}


def clean(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    out = " ".join(text.split())
    return out or None


def py_literal(value: Any) -> str:
    if isinstance(value, str) and "\\" in value and '"' not in value and not value.endswith("\\") and "\n" not in value:
        return f'r"{value}"'
    return repr(value)


def reserved_names(data: dict[str, Any]) -> frozenset[str]:
    """Names a generated module imports or defines itself, which a spec type must not take."""
    cls = data["python"]["class"]
    cls = cls[:-3] if cls.endswith("Api") and len(cls) > 3 else cls
    own = {f"{cls}Api", f"Async{cls}Api"}
    return RESERVED_MODULE_NAMES.union(*(FEATURE_RESERVED[f] for f in detect_features(data)), BUILTIN_SHADOWS, own)


def rename_reserved_types(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Give types whose name clashes with a name of the generated module a new Python name.

    Only the Python class changes (``Text`` -> ``TextType``, ``TextTypeType`` if that is taken as well); the wire is
    unaffected. Applies to ``types`` keys, ``x-name`` values, ``$ref`` targets and ``round_trip.from``.
    Returns the data (a copy when anything was renamed) and the renames, spec name -> Python name.
    """
    reserved = reserved_names(data)
    wanted: set[str] = set(data.get("types") or {})

    def collect(node: Any) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("x-name"), str):
                wanted.add(node["x-name"])
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for v in node:
                collect(v)

    collect(data)
    renames: dict[str, str] = {}
    taken = set(wanted)
    for name in sorted(wanted & reserved):
        new = name + "Type"
        while new in reserved or new in taken:
            new += "Type"
        taken.add(new)
        renames[name] = new
    if not renames:
        return data, {}

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                if k == "$ref" and isinstance(v, str) and v.startswith("#/types/"):
                    v = "#/types/" + renames.get(v[len("#/types/"):], v[len("#/types/"):])
                elif k == "x-name" and isinstance(v, str):
                    v = renames.get(v, v)
                elif k == "round_trip" and isinstance(v, dict) and isinstance(v.get("from"), str):
                    v = {**walk(v), "from": renames.get(v["from"], v["from"])}
                    out[k] = v
                    continue
                out[k] = walk(v)
            return out
        if isinstance(node, list):
            return [walk(v) for v in node]
        return node

    renamed = walk(data)
    if "types" in renamed:
        renamed["types"] = {renames.get(k, k): v for k, v in renamed["types"].items()}
    return renamed, renames


def shape_key(schema: dict[str, Any]) -> str:
    """Identity of a schema for deduplicating shared inline shapes (ignores the top-level description)."""
    return json.dumps({k: v for k, v in schema.items() if k not in ("x-name", "description")}, sort_keys=True, default=str)


def _parse_version(text: str, where: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)", str(text).strip())
    if not match:
        raise SpecError(f"{where}: {text!r} is not a major.minor version")
    return int(match.group(1)), int(match.group(2))


class Builder:
    def __init__(self, spec: LoadedSpec) -> None:
        self.spec = spec
        self.data = spec.data
        self.raw_types: dict[str, Any] = self.data.get("types") or {}
        self.defs: dict[str, TypeDef] = {}
        self.order: list[str] = []
        self._defining: set[str] = set()
        self._inline_keys: dict[str, str] = {}
        self.family: str = self.data["family"]
        self.unknown_effects: list[str] = []
        self.reserved: frozenset[str] = RESERVED_MODULE_NAMES.union(*(FEATURE_RESERVED[f] for f in detect_features(self.data)))

    # -- schema helpers ----------------------------------------------------------

    def ref_name(self, ref: str) -> str:
        match = re.fullmatch(r"#/types/([A-Za-z_][A-Za-z0-9_]*)", ref)
        if not match or match.group(1) not in self.raw_types:
            raise SpecError(f"unresolvable $ref {ref!r}")
        return match.group(1)

    def norm(self, s: Any) -> dict[str, Any]:
        if s is True or s is None:
            return {}
        if not isinstance(s, dict):
            raise SpecError(f"expected a schema object, got {s!r}")
        all_of = s.get("allOf")
        if isinstance(all_of, list) and len(all_of) == 1:
            merged = {k: v for k, v in s.items() if k != "allOf"}
            return self.norm({**all_of[0], **merged})
        return s

    def is_model_schema(self, s: dict[str, Any]) -> bool:
        return "properties" in s and s.get("type", "object") == "object"

    def contains_model(self, s: Any, seen: frozenset[str] = frozenset()) -> bool:
        s = self.norm(s)
        if "$ref" in s:
            name = self.ref_name(s["$ref"])
            if name in seen:
                return False
            return self.contains_model(self.raw_types[name], seen | {name})
        if self.is_model_schema(s):
            return True
        if s.get("type") == "array":
            return self.contains_model(s.get("items"), seen)
        if isinstance(s.get("additionalProperties"), dict):
            return self.contains_model(s["additionalProperties"], seen)
        return any(self.contains_model(m, seen) for m in (s.get("oneOf") or s.get("anyOf") or []))

    def model_name_of(self, s: Any, nest: str) -> str | None:
        s = self.norm(s)
        if "$ref" in s:
            name = self.ref_name(s["$ref"])
            return name if self.is_model_schema(self.norm(self.raw_types[name])) else None
        if self.is_model_schema(s):
            return s.get("x-name") or nest
        if s.get("type") == "array":
            return self.model_name_of(s.get("items"), nest + "Item")
        return None

    def constraint_kwargs(self, s: dict[str, Any]) -> list[str]:
        out = []
        for key, kw in _CONSTRAINTS:
            if key in s:
                out.append(f"{kw}={py_literal(s[key])}")
        return out

    # -- type expressions --------------------------------------------------------

    def expr(self, s: Any, nest: str | None, constraints: bool = True) -> str:
        s = self.norm(s)
        base = self._base(s, nest)
        if constraints:
            kw = self.constraint_kwargs(s)
            if kw:
                return f"Annotated[{base}, Field({', '.join(kw)})]"
        return base

    def _base(self, s: dict[str, Any], nest: str | None) -> str:
        if "$ref" in s:
            name = self.ref_name(s["$ref"])
            self.define(name)
            return name
        if "const" in s:
            return f"Literal[{py_literal(s['const'])}]"
        if "enum" in s:
            return f"Literal[{', '.join(py_literal(v) for v in s['enum'])}]"
        members = s.get("oneOf") or s.get("anyOf")
        if members:
            parts: list[str] = []
            for number, member in enumerate(members, 1):
                text = self.expr(member, f"{nest}{number}" if nest else None)
                if text not in parts:
                    parts.append(text)
            return " | ".join(parts)
        kind = s.get("type")
        if isinstance(kind, list):
            parts = []
            for k in kind:
                text = self._base({**s, "type": k}, nest)
                if text not in parts:
                    parts.append(text)
            return " | ".join(sorted(parts, key=lambda p: p == "None"))
        if kind is None:
            if "properties" in s:
                kind = "object"
            elif "items" in s:
                kind = "array"
            else:
                return "Any"
        if kind == "string":
            return "bytes" if s.get("format") == "binary" else "str"
        if kind in _SCALARS:
            return _SCALARS[kind]
        if kind == "array":
            return f"list[{self.expr(s.get('items'), nest + 'Item' if nest else None)}]"
        if kind == "object":
            if "properties" in s:
                name = s.get("x-name") or nest
                if not name:
                    raise SpecError("an inline object here needs an x-name")
                self.define_inline(name, s)
                return name
            ap = s.get("additionalProperties")
            if isinstance(ap, dict):
                return f"dict[str, {self.expr(ap, nest)}]"
            return "dict[str, Any]"
        raise SpecError(f"unsupported schema type {kind!r}")

    # -- type definitions --------------------------------------------------------

    def check_type_name(self, name: str) -> None:
        if not name.isidentifier():
            raise SpecError(f"type name {name!r} is not a Python identifier")
        if name in self.reserved:
            raise SpecError(f"type name {name!r} collides with a name used by generated modules; set x-name to another name")

    def define(self, name: str) -> TypeDef | None:
        if name in self.defs:
            return self.defs[name]
        if name in self._defining:
            return None
        self.check_type_name(name)
        self._defining.add(name)
        raw = self.norm(self.raw_types[name])
        if self.is_model_schema(raw):
            self._inline_keys[name] = shape_key(raw)
            td = self.build_model(name, raw)
        else:
            td = TypeDef(name, "alias", schema=raw)
            td.alias_expr = self.expr(raw, name)
        self._defining.discard(name)
        self.defs[name] = td
        self.order.append(name)
        return td

    def define_inline(self, name: str, schema: dict[str, Any]) -> TypeDef:
        key = shape_key(schema)
        if name in self.defs or name in self._defining:
            if name in self._inline_keys and self._inline_keys[name] == key:
                return self.defs[name]
            raise SpecError(f"type name {name!r} is defined twice with different shapes; give the inline one an x-name")
        self.check_type_name(name)
        self._inline_keys[name] = key
        self._defining.add(name)
        td = self.build_model(name, schema)
        self._defining.discard(name)
        self.defs[name] = td
        self.order.append(name)
        return td

    def build_model(self, name: str, schema: dict[str, Any]) -> TypeDef:
        td = TypeDef(name, "model", doc=clean(schema.get("description")), schema=schema)
        required = set(schema.get("required") or [])
        props = schema.get("properties") or {}
        missing = sorted(required - set(props))
        if missing:
            raise SpecError(f"{name}: required lists unknown properties {missing}")
        seen: dict[str, str] = {}
        for wire, prop in props.items():
            prop = self.norm(prop)
            try:
                # SOAP names may carry a namespace prefix (acert:Id, @xsi:type); the Python name comes from the local name.
                py = field_name(wire.rsplit(":", 1)[-1] if self.family == "soap" else wire, prop.get("x-python-name"))
            except NamingError as error:
                raise SpecError(f"{name}: {error}") from error
            if py in seen:
                raise SpecError(f"{name}: {wire!r} and {seen[py]!r} both become {py!r}; set x-python-name on one")
            seen[py] = wire
            nest = name + pascal_case(py)
            upload = self.upload_options(name, wire, prop)
            ann = "UploadSource" if upload is not None else self.expr(prop, nest, constraints=False)
            sig = "Mapping[" + ann[5:] if ann.startswith("dict[") else ann
            default = None
            doc = clean(prop.get("description"))
            if "default" in prop:
                if prop["default"] in ([], {}) and wire not in required:
                    default = repr(prop["default"])
                else:
                    note = f"Default: {prop['default']!r}."
                    doc = f"{doc} {note}" if doc else note
            since = _parse_version(prop["since"], f"{name}.{wire}.since") if prop.get("since") else None
            if since:
                note = f"Available from API version {since[0]}.{since[1]}."
                doc = f"{doc} {note}" if doc else note
            td.fields.append(
                FieldDef(
                    py=py, wire=wire, ann=ann, sig=sig, required=wire in required and since is None, since=since,
                    kwargs=["exclude=True", "repr=False"] if upload is not None else self.constraint_kwargs(prop),
                    upload=upload, place=prop.get("x-in"), default=default, doc=doc, schema=prop,
                    style=prop.get("x-style"), xml=prop.get("x-xml"), has_model=self.contains_model(prop),
                    model_name=self.model_name_of(prop, nest),
                )
            )  # fmt: skip

        def names(key: str) -> list[str]:
            out = []
            for item in schema.get(key) or []:
                f = td.by_wire(item) or td.by_py(item)
                if f is None:
                    raise SpecError(f"{name}: {key} names unknown field {item!r}")
                out.append(f.py)
            return sorted(out)

        td.nullable = names("x-nullable")
        td.masked = names("x-masked")
        td.read_only = names("x-read-only")
        for py in td.read_only:
            fd = td.by_py(py)
            assert fd is not None
            fd.read_only = True
        for py in td.nullable:
            fd = td.by_py(py)
            assert fd is not None
            fd.nullable = True
        return td

    def upload_options(self, type_name: str, wire: str, prop: dict[str, Any]) -> dict[str, Any] | None:
        """``x-upload`` of a property as a dict (``true`` means no options), or ``None``."""
        value = prop.get("x-upload")
        if value is None or value is False:
            return None
        if self.family not in ("cgi", "jsonrpc"):
            raise SpecError(f"{type_name}.{wire}: x-upload only applies to cgi and jsonrpc specs")
        return {} if value is True else dict(value)

    # -- operations --------------------------------------------------------------

    def is_wrapped_params(self, s: dict[str, Any]) -> bool:
        """Params that are not an object with properties: an array, a free-form map or a plain alias."""
        if "$ref" in s:
            return not self.is_model_schema(self.norm(self.raw_types[self.ref_name(s["$ref"])]))
        return not (s.get("type", "object") == "object" and ("properties" in s or "additionalProperties" not in s))

    def params_type(self, op_id: str, schema: Any) -> tuple[TypeDef | None, str | None]:
        """The request model and, for wrapped params, the name of its single field."""
        if schema is None:
            return None, None
        s = self.norm(schema)
        if self.family == "jsonrpc" and self.is_wrapped_params(s):
            arg = s.get("x-arg-name", "params")
            inner = {k: v for k, v in s.items() if k not in ("x-name", "x-arg-name", "x-arg-optional")}
            wrapper = {
                "type": "object",
                "required": [] if s.get("x-arg-optional") else [arg],
                "properties": {arg: inner},
            }
            td = self.define_inline(s.get("x-name") or pascal_case(op_id) + "Request", wrapper)
            field = td.by_wire(arg)
            assert field is not None
            return td, field.py
        if s.get("x-arg-optional"):
            raise SpecError(f"{op_id}: x-arg-optional only applies to wrapped jsonrpc params (an array or free-form map)")
        if "$ref" in s:
            td = self.define(self.ref_name(s["$ref"]))
            if td is None or td.kind != "model":
                raise SpecError(f"{op_id}: params must be an object type")
            return td, None
        if s.get("type", "object") != "object":
            raise SpecError(f"{op_id}: params must be an object schema")
        s = {**s, "properties": s.get("properties") or {}}
        return self.define_inline(s.get("x-name") or pascal_case(op_id) + "Request", s), None

    def result_info(self, op_id: str, schema: Any) -> tuple[str | None, TypeDef | None, str | None]:
        """(signature type, result model, validation type if it differs: with the top-level constraints)."""
        if schema is None:
            return None, None, None
        s = self.norm(schema)
        if s.get("x-xml") is True:
            return "ET.Element", None, None
        if "$ref" in s:
            name = self.ref_name(s["$ref"])
            text = self.expr(s, None, constraints=False)
            td = self.defs.get(name)
            return text, td if td is not None and td.kind == "model" else None, None
        nest = pascal_case(op_id) + "Result"
        text = self.expr(s, nest, constraints=False)
        typed = self.expr(s, nest)
        td = self.defs.get(text)
        return text, td if td is not None and td.kind == "model" else None, typed if typed != text else None

    def cgi_keys(
        self, op_id: str, ob: dict[str, Any], params: TypeDef | None, fields: list[FieldDef], result_model: TypeDef | None
    ) -> list[str]:
        """Python names of the arguments that fill ``{name}`` placeholders (never sent as arguments).

        Placeholders are read from the operation's path, its fixed ``query`` / ``url_query`` values, the wire names of its arguments, a ``text_kv``
        ``strip_prefix`` and the wire names of its result fields.
        """
        names: list[str] = []

        def add(text: Any) -> None:
            for name in re.findall(r"\{(\w+)\}", text) if isinstance(text, str) else []:
                if name not in names:
                    names.append(name)

        add(ob.get("path"))
        for fixed in (ob.get("query"), ob.get("url_query")):
            for value in (fixed or {}).values():
                add(value)
        for f in fields:
            add(f.wire)
        reply = ob.get("reply")
        if isinstance(reply, dict) and isinstance(reply.get("text_kv"), dict):
            add(reply["text_kv"].get("strip_prefix"))
        if result_model is not None:
            for f in result_model.fields:
                add(f.wire)
        keys: list[str] = []
        for name in names:
            f = (params.by_py(name) or params.by_wire(name)) if params else None
            if f is None or f not in fields:
                raise SpecError(f"{op_id}: placeholder {{{name}}} is not an argument of the operation")
            if not f.required:
                raise SpecError(f"{op_id}: argument {name!r} fills a placeholder, so it must be required")
            if f.has_model or f.upload is not None or f.sig.startswith(("list[", "Mapping[")) or f.place:
                raise SpecError(f"{op_id}: argument {name!r} fills a placeholder, so it must be a plain scalar (no x-in, no x-upload)")
            if "{" in f.wire:
                raise SpecError(f"{op_id}: argument {name!r} fills a placeholder and cannot have a templated name itself")
            if f.py not in keys:
                keys.append(f.py)
        return keys

    def build_op(self, op_id: str, op: dict[str, Any], api_access: str, path_keys: list[str]) -> OpDef:
        if not op_id.isidentifier():
            raise SpecError(f"operation id {op_id!r} is not a Python identifier")
        try:
            params, params_field = self.params_type(op_id, op.get("params"))
            result, result_model, result_type = self.result_info(op_id, op.get("result"))
        except SpecError as error:
            message = str(error)
            raise SpecError(message if message.startswith(f"{op_id}:") else f"{op_id}: {message}") from None
        effect = op.get("effect") or "unknown"
        if effect == "unknown":
            self.unknown_effects.append(op_id)
        fields = [f for f in params.fields if f.py not in params.read_only] if params else []
        for f in fields:
            if f.py in RESERVED_ARG_NAMES:
                raise SpecError(f"{op_id}: argument {f.py!r} is reserved")
        key_fields: list[str] = []
        if self.family == "cgi":
            key_fields = self.cgi_keys(op_id, op.get("binding") or {}, params, fields, result_model)
            path_keys = key_fields
        kind, stream_decoder = op_kind(self.family, op.get("binding") or {})
        self.check_kind(op_id, op, kind, stream_decoder, params, result, fields)
        overloaded = bool(params) and not params_field and kind != "rtsp" and (any(f.has_model for f in fields) or len(fields) > 4)

        positional: list[str] = []
        if params:
            if overloaded:
                # Only explicit `positional` applies; path keys stay keyword arguments of the kwargs overload.
                wanted = list(op.get("positional") or [])
            else:
                wanted = ([params_field] if params_field else []) + [k for k in path_keys] + [p for p in (op.get("positional") or []) if p not in path_keys]
            for item in wanted:
                f = params.by_py(item) or params.by_wire(item)
                if f is None or f not in fields:
                    raise SpecError(f"{op_id}: positional {item!r} is not an argument")
                if f.py not in positional:
                    positional.append(f.py)
            seen_optional = False
            for item in positional:
                f = params.by_py(item)
                assert f is not None
                if not f.required:
                    seen_optional = True
                elif seen_optional:
                    raise SpecError(f"{op_id}: required positional {item!r} follows an optional one")
        mapping_args = [f.py for f in fields if f.is_mapping]

        round_trip = None
        rt = op.get("round_trip")
        if rt is not None:
            if params is None:
                raise SpecError(f"{op_id}: round_trip needs params")
            source = self.define(rt["from"]) if rt["from"] in self.raw_types else None
            if source is None or source.kind != "model":
                raise SpecError(f"{op_id}: round_trip.from {rt['from']!r} is not an object type")
            values = {}
            for key, value in (rt.get("set") or {}).items():
                f = params.by_wire(key) or params.by_py(key)
                if f is None:
                    raise SpecError(f"{op_id}: round_trip.set names unknown field {key!r}")
                values[f.py] = value
            round_trip = RoundTrip(rt["from"], values, op_id)
            if params.round_trip and (params.round_trip.from_name, params.round_trip.set_values) != (
                round_trip.from_name,
                round_trip.set_values,
            ):
                raise SpecError(f"{op_id}: {params.name} already has a different round_trip")
            params.round_trip = round_trip

        applicability = self.applicability(op_id, op.get("since_fields") or {}, params)
        since = _parse_version(op["since"], f"{op_id}.since") if op.get("since") else None
        errors = {k: dict(v) for k, v in (op.get("errors") or {}).items()}
        check_errors(op_id, errors)
        return OpDef(
            id=op_id, summary=clean(op.get("summary")) or op_id, description=clean(op.get("description")),
            access=op.get("access") or api_access, effect=effect, write=op.get("write"), since=since,
            support=op.get("support") or "docs-only", binding=dict(op.get("binding") or {}), params=params,
            result=result, result_type=result_type, result_model=result_model, errors=errors, applicability=applicability,
            positional=positional, overloaded=overloaded, args=fields, key_fields=key_fields, params_field=params_field, mapping_args=mapping_args, round_trip=round_trip,
            kind=kind, stream_decoder=stream_decoder, session=dict(op["binding"]["session"]) if kind == "session" else None,
            rtsp=dict(op["binding"]["rtsp"]) if kind == "rtsp" else None,
        )  # fmt: skip

    def check_kind(
        self, op_id: str, op: dict[str, Any], kind: str, decoder: str | None, params: TypeDef | None, result: str | None, fields: list[FieldDef]
    ) -> None:
        """Checks for the operation kinds that are not plain request/response calls."""
        if self.family == "ws" and kind != "session":
            raise SpecError(f"{op_id}: operations of a ws API need binding.session")
        if self.family == "rtsp" and kind != "rtsp":
            raise SpecError(f"{op_id}: operations of an rtsp API need binding.rtsp")
        binding = op.get("binding") or {}
        if kind == "call":
            return
        if "session" in binding and "rtsp" in binding:
            raise SpecError(f"{op_id}: binding.session and binding.rtsp cannot be combined")
        if result is not None or op.get("result") is not None:
            raise SpecError(f"{op_id}: {kind} operations have no `result` (they return a {_KIND_RETURNS[kind]})")
        if kind == "stream":
            if decoder not in STREAM_DECODERS:
                raise SpecError(f"{op_id}: stream decoder {decoder!r} is not one of {', '.join(STREAM_DECODERS)}")
            if binding.get("stream") is False:
                raise SpecError(f"{op_id}: a stream reply cannot set stream: false")
        elif kind == "session":
            session = binding["session"]
            if not str(session.get("path", "")).startswith("/"):
                raise SpecError(f"{op_id}: binding.session.path must start with '/'")
            placeholders = re.findall(r"\{(\w+)\}", session["path"])
            if sorted(f.wire for f in fields) != sorted(placeholders):
                raise SpecError(
                    f"{op_id}: session `params` must be exactly the {{placeholders}} of binding.session.path "
                    f"({', '.join(placeholders) or 'none'}); connect options come from the codec/setup"
                )
            for f in fields:
                if not f.required or f.has_model or f.is_mapping:
                    raise SpecError(f"{op_id}: path placeholder {f.wire!r} must be a required scalar params field")
            codec = session.get("codec", "raw")
            if codec not in SESSION_CODECS:
                raise SpecError(f"{op_id}: session codec {codec!r} is not one of {', '.join(SESSION_CODECS)}")
            setup = session.get("setup") or SESSION_CODECS[codec]
            if setup not in SESSION_SETUPS:
                raise SpecError(f"{op_id}: session setup {setup!r} is not one of {', '.join(SESSION_SETUPS)}")
            if setup != "none" and codec == "raw":
                raise SpecError(f"{op_id}: a raw session has no request/response messages, so it cannot have a setup")
            if op.get("positional"):
                raise SpecError(f"{op_id}: session operations have no positional arguments")
        else:  # rtsp
            rtsp = binding["rtsp"]
            if not str(rtsp.get("path", "/")).startswith("/") or "?" in str(rtsp.get("path", "")):
                raise SpecError(f"{op_id}: binding.rtsp.path must start with '/' and have no query")
            for f in fields:
                if f.py in RTSP_RESERVED_ARGS:
                    raise SpecError(f"{op_id}: argument {f.py!r} is reserved for RTSP operations; set x-python-name")
                if f.has_model or f.is_mapping:
                    raise SpecError(f"{op_id}: RTSP argument {f.py!r} must be a scalar or a list of scalars")

    def applicability(self, op_id: str, since_fields: dict[str, str], params: TypeDef | None) -> list[Applic]:
        out = []
        for path, version in since_fields.items():
            where = f"{op_id}.since_fields[{path!r}]"
            if params is None:
                raise SpecError(f"{where}: the operation has no params")
            text, _, value = path.partition("=")
            parts = text.split(".")
            if parts and parts[0] == "params":
                parts = parts[1:]
            if not parts:
                raise SpecError(f"{where}: empty path")
            td: TypeDef | None = params
            names = []
            for i, part in enumerate(parts):
                if td is None:
                    raise SpecError(f"{where}: {part!r} is not inside an object")
                f = td.by_wire(part) or td.by_py(part)
                if f is None:
                    raise SpecError(f"{where}: unknown field {part!r} in {td.name}")
                names.append(f.py)
                td = self.defs.get(f.model_name) if f.model_name else None
            parsed: Any = None
            if value:
                try:
                    parsed = json.loads(value)
                except ValueError:
                    parsed = value
            out.append(Applic(".".join(names), _parse_version(version, where), parsed))
        return out


def dca_path_keys(path: str) -> list[str]:
    return re.findall(r"\{(\w+)\}", path)


def soap_prefixes(td: TypeDef, defs: dict[str, TypeDef], seen: tuple[str, ...] = ()) -> set[str]:
    """Namespace prefixes used by the wire names of ``td`` and the models below it."""
    out: set[str] = set()
    for f in td.fields:
        name = f.wire.lstrip("@")
        if ":" in name:
            out.add(name.split(":", 1)[0])
        if f.model_name and f.model_name in defs and f.model_name not in seen:
            out |= soap_prefixes(defs[f.model_name], defs, seen + (f.model_name,))
    return out


def check_cgi_binding(op: OpDef) -> None:
    """Placement of arguments (query, form, body, file parts) against the binding's encoding."""
    ob = op.binding
    encoding = ob.get("encoding", "query")
    default = "query" if encoding in ("query", "body") else "form"
    keys = set(op.key_fields)
    body_fields = [f for f in op.args if f.place == "body"]
    type_fields = [f for f in op.args if f.place == "content_type"]
    for f in op.args:
        where = f"{op.id}: argument {f.py!r}"
        if f.place == "form" and default != "form":
            raise SpecError(f"{where} has x-in: form, which needs binding.encoding form or multipart")
        if f.place == "content_type":
            if encoding != "body":
                raise SpecError(f"{where} has x-in: content_type, which needs binding.encoding body")
            if f.has_model or f.upload is not None or f.sig.startswith(("list[", "Mapping[")) or f.sig in ("int", "float", "bool"):
                raise SpecError(f"{where}: x-in content_type must be a string (or an enum of strings)")
        if f.place == "body" and encoding != "body":
            raise SpecError(f"{where} has x-in: body, which needs binding.encoding body")
        if f.upload is not None:
            if encoding not in ("multipart", "body"):
                raise SpecError(f"{where} has x-upload, which needs binding.encoding multipart (or body)")
            if f.place != ("body" if encoding == "body" else None):
                raise SpecError(f"{where}: x-upload takes x-in: body with encoding body and no x-in with multipart")
        if f.style == "flag" and (f.place or default) != "query":
            raise SpecError(f"{where}: x-style flag sends a bare key, which only works in the URL query")
        if f.py in keys and f.place:
            raise SpecError(f"{where} fills a placeholder and cannot have x-in")
    if encoding == "multipart":
        if ob.get("method") != "POST":
            raise SpecError(f"{op.id}: multipart operations need binding.method POST")
        if not any(f.upload is not None for f in op.args):
            raise SpecError(f"{op.id}: multipart operations need at least one x-upload argument")
    if encoding == "body":
        if ob.get("method") != "POST":
            raise SpecError(f"{op.id}: encoding body needs binding.method POST")
        if len(body_fields) != 1:
            raise SpecError(f"{op.id}: encoding body needs exactly one argument with x-in: body, found {len(body_fields)}")
        if len(type_fields) > 1:
            raise SpecError(f"{op.id}: at most one argument can have x-in: content_type")
        upload = body_fields[0].upload
        if not ob.get("content_type") and not (upload or {}).get("content_type"):
            raise SpecError(f"{op.id}: encoding body needs binding.content_type")
    elif ob.get("content_type"):
        raise SpecError(f"{op.id}: binding.content_type only applies to encoding body")
    if default == "form" and any(v is None for v in (ob.get("query") or {}).values()):
        raise SpecError(f"{op.id}: a bare query key (null value) cannot be sent in the body; put it in binding.url_query")


def check_jsonrpc_upload(op: OpDef) -> None:
    uploads = [f for f in op.args if f.upload is not None]
    multipart = op.binding.get("multipart")
    if multipart is None:
        if uploads:
            raise SpecError(f"{op.id}: x-upload arguments need binding.multipart")
        return
    if not uploads:
        raise SpecError(f"{op.id}: binding.multipart needs at least one x-upload argument")
    if op.params_field:
        raise SpecError(f"{op.id}: multipart operations cannot use wrapped params")


def check_op_binding(
    family: str, op: OpDef, path_keys: list[str], api_binding: dict[str, Any], defs: dict[str, TypeDef] | None = None
) -> None:
    """Family-specific checks of one operation's binding against its params."""
    ob = op.binding
    if op.kind in ("session", "rtsp"):
        return  # checked when the operation is built; the family's own binding keys do not apply
    if family == "cgi":
        check_cgi_binding(op)
    elif family == "jsonrpc":
        check_jsonrpc_upload(op)
    if family == "service_json":
        if not ob.get("operation"):
            raise SpecError(f"{op.id}: service_json operations need binding.operation")
    elif family == "soap":
        for key in ("action", "element"):
            if not ob.get(key):
                raise SpecError(f"{op.id}: soap operations need binding.{key}")
        if not ob.get("namespace") and not api_binding.get("namespace"):
            raise SpecError(f"{op.id}: soap operations need binding.namespace (or a namespace in the API binding)")
        if op.result is not None and op.result_model is None and op.result != "ET.Element":
            raise SpecError(f"{op.id}: a soap result must be an object type (the reply is read through x-xml) or x-xml: true (the raw reply element)")
        namespaces = {**(api_binding.get("namespaces") or {}), **(ob.get("namespaces") or {})}
        for prefix in namespaces:
            if prefix in ("env", "xml", "xmlns"):
                raise SpecError(f"{op.id}: {prefix!r} is a reserved namespace prefix")
        used = soap_prefixes(op.params, defs or {}) if op.params else set()
        undeclared = sorted(used - set(namespaces))
        if undeclared:
            raise SpecError(f"{op.id}: params use the namespace prefix(es) {', '.join(undeclared)}; declare them in binding.namespaces")
    elif family == "rest":
        if not ob.get("method"):
            raise SpecError(f"{op.id}: rest operations need binding.method")
        path = ob.get("path", "")
        if path and not path.startswith("/"):
            raise SpecError(f"{op.id}: rest binding.path must start with '/'")

        def field(name: str) -> FieldDef:
            f = op.params.by_py(name) or op.params.by_wire(name) if op.params else None
            if f is None:
                raise SpecError(f"{op.id}: binding names {name!r}, which is not a params field")
            return f

        for key in path_keys:
            if not field(key).required:
                raise SpecError(f"{op.id}: path placeholder {key!r} must be a required params field")
        for name in ob.get("query") or []:
            field(name)
        body = ob.get("body", "none")
        if body == "value":
            if not ob.get("body_field"):
                raise SpecError(f"{op.id}: rest body 'value' needs binding.body_field")
            field(ob["body_field"])
        elif ob.get("body_field"):
            raise SpecError(f"{op.id}: binding.body_field only applies to body 'value'")


def check_errors(where: str, errors: dict[Any, dict[str, Any]]) -> None:
    """Message-keyed errors: ``message`` or ``message_prefix`` (not both), under a label that is not a code."""
    for key, entry in errors.items():
        if entry.get("message") and entry.get("message_prefix"):
            raise SpecError(f"{where}: error {key!r} sets both message and message_prefix")


def build_api(spec: LoadedSpec) -> ApiDef:
    family = spec.data["family"]
    if family not in SUPPORTED_FAMILIES:
        raise SpecError(f"family {family!r} is not supported by the generator")
    data, renames = rename_reserved_types(spec.data)
    if renames:
        spec = LoadedSpec(spec.path, data, spec.warnings)
        spec.warnings.append("type(s) renamed because the name is used by the generated module: " + ", ".join(f"{a} -> {b}" for a, b in renames.items()))
    check_errors("errors", data.get("errors") or {})
    b = Builder(spec)
    for name in b.raw_types:
        b.define(name)
    api_binding = dict(data.get("binding") or {})
    access = data.get("access") or "unknown"
    ops: list[OpDef] = []
    for op_id, raw in (data.get("operations") or {}).items():
        keys: list[str] = []
        if family in ("dca", "rest"):
            keys = dca_path_keys((raw.get("binding") or {}).get("path", ""))
        styles = (raw.get("binding") or {}).get("key_styles") or {}
        for placeholder in styles:
            if placeholder not in keys:
                raise SpecError(f"{op_id}: binding.key_styles names {placeholder!r}, which is not a placeholder of binding.path")
        built = b.build_op(op_id, raw, access, keys)
        check_op_binding(family, built, keys, data.get("binding") or {}, b.defs)
        ops.append(built)
    if b.unknown_effects:
        spec.warnings.append(f"effect is unknown for {len(b.unknown_effects)} operation(s): {', '.join(b.unknown_effects)}")
    if family in ("cgi", "soap"):
        from .xmlreply import attach_xml_maps

        attach_xml_maps(b, ops, soap=family == "soap")
    discovery = []
    for entry in data.get("discovery") or []:
        (kind, value), = entry.items()
        discovery.append((kind, value))
    python = data["python"]
    for ident in (python["module"], python["class"]):
        if not ident.isidentifier():
            raise SpecError(f"python.{ident!r} is not an identifier")
    class_name = python["class"]
    if class_name.endswith("Api") and len(class_name) > 3:
        # The generator appends `Api` (and `AsyncApi` prefix); do not double it.
        class_name = class_name[:-3]
        spec.warnings.append(f"python.class {python['class']!r} already ends in 'Api'; using {class_name!r} ({class_name}Api)")
    elif class_name == "Api":
        raise SpecError("python.class 'Api' is not a usable class name")
    return ApiDef(
        id=data["id"], name=data["name"], summary=clean(data.get("summary")) or data["name"], section=data["section"],
        family=family, module=python["module"], class_name=class_name, docs=list(data.get("docs") or []),
        access=access, discovery=discovery, binding=api_binding,
        errors={k: dict(v) for k, v in (data.get("errors") or {}).items()},
        types=[b.defs[n] for n in b.order], ops=ops, source=spec.rel,
    )  # fmt: skip


__all__ = ["build_api", "snake_case", "BUILTIN_SHADOWS", "SUPPORTED_FAMILIES"]
