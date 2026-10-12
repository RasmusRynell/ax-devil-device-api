"""XML reply mappings (cgi): render ``XmlMap``/``XmlField`` descriptors from result types."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .loader import SpecError
from .model import FieldDef, OpDef, TypeDef
from .naming import pascal_case  # noqa: F401

if TYPE_CHECKING:
    from .build import Builder


def reply_kind(binding: dict) -> tuple[str, dict]:
    reply = binding.get("reply", "text")
    if isinstance(reply, str):
        return reply, {}
    ((kind, options),) = reply.items()
    return kind, options or {}


def _field_code(b: Builder, f: FieldDef, stack: tuple[str, ...]) -> str:
    x = f.xml
    schema = b.norm(f.schema)
    is_array = _is_array(b, schema)
    source, name, many, nested = "attribute", None, False, None
    if x == "text":
        source = "text"
    elif isinstance(x, dict):
        if "child" in x:
            source, name = "child", x["child"]
        elif "path" in x:
            source, name = "path", x["path"]
        elif "attribute" in x:
            name = x["attribute"]
    elif x is None and (is_array or f.model_name):
        source, name = "path", f.wire
    if source == "path":
        many = is_array
        if f.model_name:
            nested = b.defs[f.model_name]
    parts = [repr(f.wire)]
    if source != "attribute":
        parts.append(f"source={source!r}")
    if name is not None and name != f.wire:
        parts.append(f"name={name!r}")
    if many:
        parts.append("many=True")
    if nested is not None:
        if nested.name in stack:
            raise SpecError(f"x-xml mapping of {nested.name} is recursive")
        parts.append(f"nested={map_code(b, nested, stack + (nested.name,))}")
    return f"XmlField({', '.join(parts)})"


def _is_array(b: Builder, schema: dict) -> bool:
    schema = b.norm(schema)
    if "$ref" in schema:
        return _is_array(b, b.raw_types[b.ref_name(schema["$ref"])])
    return schema.get("type") == "array"


def map_code(b: Builder, td: TypeDef, stack: tuple[str, ...], top: bool = False) -> str:
    fields = ", ".join(_field_code(b, f, stack) for f in td.fields)
    tup = f"({fields},)" if len(td.fields) == 1 else f"({fields})"
    root = ""
    x = td.schema.get("x-xml")
    if top and isinstance(x, dict) and x.get("root"):
        root = f", root={x['root']!r}"
    return f"XmlMap(fields={tup}{root})"


def attach_xml_maps(b: Builder, ops: list[OpDef]) -> None:
    for op in ops:
        kind, _ = reply_kind(op.binding)
        if kind == "xml" and op.result_model is not None:
            op.reply_map = map_code(b, op.result_model, (op.result_model.name,), top=True)
