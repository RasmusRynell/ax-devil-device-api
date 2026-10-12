"""Build the intermediate model (``ApiDef``) from a validated spec."""

from __future__ import annotations

import json
import re
from typing import Any

from .loader import LoadedSpec, SpecError
from .model import Applic, ApiDef, FieldDef, OpDef, RoundTrip, TypeDef
from .naming import RESERVED_ARG_NAMES, NamingError, field_name, pascal_case, snake_case

SUPPORTED_FAMILIES = ("jsonrpc", "dca", "cgi")

# Names the generated module imports or defines itself.
RESERVED_MODULE_NAMES = frozenset(
    {
        "Annotated", "Any", "ClassVar", "Literal", "overload", "Mapping", "MISSING", "Field", "ET", "builtins",
        "RequestOptions", "ApiDiscovery", "ApiInfo", "ApiVersion", "Applicability", "DcaDiscovery", "ErrorCode",
        "Family", "Model", "Operation", "ParamDiscovery", "JsonRpcBinding", "GetSupportedVersions", "FixedVersion",
        "NoVersion", "DcaBinding", "CgiArg", "CgiBinding", "Text", "TextKv", "TextOk", "Xml", "Binary", "JsonReply",
        "XmlMap", "XmlField", "XmlStatusError", "AsyncApi", "SyncApi", "INFO", "OPS", "PATH", "ROOT",
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


def clean(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    out = " ".join(text.split())
    return out or None


def py_literal(value: Any) -> str:
    if isinstance(value, str) and "\\" in value and '"' not in value and not value.endswith("\\") and "\n" not in value:
        return f'r"{value}"'
    return repr(value)


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
        if name in RESERVED_MODULE_NAMES:
            raise SpecError(f"type name {name!r} collides with a name used by generated modules; rename it")

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
                py = field_name(wire, prop.get("x-python-name"))
            except NamingError as error:
                raise SpecError(f"{name}: {error}") from error
            if py in seen:
                raise SpecError(f"{name}: {wire!r} and {seen[py]!r} both become {py!r}; set x-python-name on one")
            seen[py] = wire
            nest = name + pascal_case(py)
            ann = self.expr(prop, nest, constraints=False)
            sig = "Mapping[" + ann[5:] if ann.startswith("dict[") else ann
            default = None
            doc = clean(prop.get("description"))
            if "default" in prop:
                if prop["default"] in ([], {}) and not (wire in required):
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
                    kwargs=self.constraint_kwargs(prop), default=default, doc=doc, schema=prop,
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
        for py in td.nullable:
            fd = td.by_py(py)
            assert fd is not None
            fd.nullable = True
        return td

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
            inner = {k: v for k, v in s.items() if k not in ("x-name", "x-arg-name")}
            wrapper = {
                "type": "object",
                "required": [arg],
                "properties": {arg: inner},
            }
            td = self.define_inline(s.get("x-name") or pascal_case(op_id) + "Request", wrapper)
            field = td.by_wire(arg)
            assert field is not None
            return td, field.py
        if "$ref" in s:
            td = self.define(self.ref_name(s["$ref"]))
            if td is None or td.kind != "model":
                raise SpecError(f"{op_id}: params must be an object type")
            return td, None
        if s.get("type", "object") != "object":
            raise SpecError(f"{op_id}: params must be an object schema")
        s = {**s, "properties": s.get("properties") or {}}
        return self.define_inline(s.get("x-name") or pascal_case(op_id) + "Request", s), None

    def result_info(self, op_id: str, schema: Any) -> tuple[str | None, TypeDef | None]:
        if schema is None:
            return None, None
        s = self.norm(schema)
        if s.get("x-xml") is True:
            return "ET.Element", None
        if "$ref" in s:
            name = self.ref_name(s["$ref"])
            text = self.expr(s, None, constraints=False)
            td = self.defs.get(name)
            return text, td if td is not None and td.kind == "model" else None
        text = self.expr(s, pascal_case(op_id) + "Result", constraints=False)
        td = self.defs.get(text)
        return text, td if td is not None and td.kind == "model" else None

    def build_op(self, op_id: str, op: dict[str, Any], api_access: str, path_keys: list[str]) -> OpDef:
        if not op_id.isidentifier():
            raise SpecError(f"operation id {op_id!r} is not a Python identifier")
        try:
            params, params_field = self.params_type(op_id, op.get("params"))
            result, result_model = self.result_info(op_id, op.get("result"))
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
        overloaded = bool(params) and not params_field and (any(f.has_model for f in fields) or len(fields) > 4)

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
        return OpDef(
            id=op_id, summary=clean(op.get("summary")) or op_id, description=clean(op.get("description")),
            access=op.get("access") or api_access, effect=effect, write=op.get("write"), since=since,
            support=op.get("support") or "docs-only", binding=dict(op.get("binding") or {}), params=params,
            result=result, result_model=result_model, errors=errors, applicability=applicability,
            positional=positional, overloaded=overloaded, args=fields, params_field=params_field, mapping_args=mapping_args, round_trip=round_trip,
        )  # fmt: skip

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


def build_api(spec: LoadedSpec) -> ApiDef:
    data = spec.data
    family = data["family"]
    if family not in SUPPORTED_FAMILIES:
        raise SpecError(f"family {family!r} is not supported by the generator")
    b = Builder(spec)
    for name in b.raw_types:
        b.define(name)
    api_binding = dict(data.get("binding") or {})
    access = data.get("access") or "unknown"
    ops: list[OpDef] = []
    for op_id, raw in (data.get("operations") or {}).items():
        keys: list[str] = []
        if family == "dca":
            keys = dca_path_keys((raw.get("binding") or {}).get("path", ""))
        styles = (raw.get("binding") or {}).get("key_styles") or {}
        for placeholder in styles:
            if placeholder not in keys:
                raise SpecError(f"{op_id}: binding.key_styles names {placeholder!r}, which is not a placeholder of binding.path")
        ops.append(b.build_op(op_id, raw, access, keys))
    if b.unknown_effects:
        spec.warnings.append(f"effect is unknown for {len(b.unknown_effects)} operation(s): {', '.join(b.unknown_effects)}")
    if family == "cgi":
        from .xmlreply import attach_xml_maps

        attach_xml_maps(b, ops)
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
