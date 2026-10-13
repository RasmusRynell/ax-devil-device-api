"""Declarative XML-to-data mapping for classic CGI replies.

Generated code describes where each field of a result model lives in the
XML reply; ``extract`` turns the parsed document into plain data that the
result model then validates. Element and attribute names are matched by
local name, so namespaces never matter.
"""

from __future__ import annotations

import types
import typing
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel


class XmlDeclarationError(ET.ParseError):
    """The XML declaration is unusable (unknown encoding, bad value): not a syntax problem a fragment wrapper could fix."""


def parse_xml(content: bytes | str) -> ET.Element:
    """``ET.fromstring`` with every way a document can be malformed reported as ``ET.ParseError``.

    An XML declaration with an unknown encoding raises ``LookupError`` and a bad declaration or value can raise
    ``ValueError``; neither belongs to the library's error hierarchy, so callers only have to handle one exception.
    """
    try:
        return ET.fromstring(content)
    except (LookupError, ValueError) as error:  # ParseError is a SyntaxError and passes through
        raise XmlDeclarationError(str(error)) from error


@dataclass(frozen=True)
class XmlField:
    """Where one model field comes from, relative to the element of its model.

    - ``attribute``: the attribute ``name`` (the default for scalars).
    - ``text``: the element's own text.
    - ``child``: the text of the first child element ``name``.
    - ``path``: elements at a ``/``-separated path of local names; with
      ``many`` every match becomes a list item. ``nested`` maps each match
      to an object; without it the match's text is used. A last path segment
      ``@name`` reads that attribute of each matched element instead
      (``item/@value`` -> the ``value`` attribute of every ``<item>``);
      elements without the attribute are skipped.
    """

    key: str
    """Wire name of the field in the result model."""
    source: Literal["attribute", "text", "child", "path"] = "attribute"
    name: str | None = None
    """Attribute or child name, or the path; defaults to ``key``."""
    many: bool = False
    nested: XmlMap | None = None


@dataclass(frozen=True)
class XmlMap:
    """How to read one object from an element."""

    fields: tuple[XmlField, ...]
    root: str | None = None
    """For the top-level map only: path from the document root to the element to read."""


@dataclass(frozen=True)
class XmlStatusError:
    """Failure signalled by an attribute, e.g. ``<configure result="ERROR" errormsg="...">``.

    Any element at ``path`` (default: anywhere) whose ``attribute`` equals
    ``value`` is a failure; ``message`` and ``code`` name the attributes that
    carry the details.
    """

    attribute: str = "result"
    value: str = "ERROR"
    message: str | None = "errormsg"
    code: str | None = None
    path: str | None = None


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _attr(element: ET.Element, name: str) -> str | None:
    for key, value in element.attrib.items():
        if local(key) == name:
            return value
    return None


def find_all(element: ET.Element, path: str) -> Iterator[ET.Element]:
    """Elements at a ``/``-separated path of local names (``*`` matches any)."""
    parts = [p for p in path.split("/") if p and p != "."]
    current = [element]
    for part in parts:
        current = [child for node in current for child in node if part == "*" or local(child.tag) == part]
    yield from current


def extract(element: ET.Element, mapping: XmlMap) -> dict[str, Any]:
    """Read the fields described by ``mapping`` from ``element``. Absent fields are left out."""
    if mapping.root:
        found = next(find_all(element, mapping.root), None)
        if found is None:
            return {}
        element = found
    data: dict[str, Any] = {}
    for field in mapping.fields:
        name = field.name or field.key
        if field.source == "attribute":
            value: Any = _attr(element, name)
        elif field.source == "text":
            value = (element.text or "").strip()
        elif field.source == "child":
            child = next(find_all(element, name), None)
            value = None if child is None else (child.text or "").strip()
        else:
            head, _, last = name.rpartition("/")
            if last.startswith("@") and len(last) > 1:
                attr_name = last[1:]
                attrs = [_attr(m, attr_name) for m in find_all(element, head or ".")]
                items = [v.strip() for v in attrs if v is not None]
            else:
                matches = list(find_all(element, name))
                items = [extract(m, field.nested) if field.nested else (m.text or "").strip() for m in matches]
            value = items if field.many else (items[0] if items else None)
        if value is not None:
            data[field.key] = value
    return data


def status_error(root: ET.Element, rule: XmlStatusError) -> tuple[str | None, str] | None:
    """``(code, message)`` of the first element that signals failure, or ``None``."""
    candidates = find_all(root, rule.path) if rule.path else root.iter()
    for element in candidates:
        if _attr(element, rule.attribute) == rule.value:
            child = next((c for c in element if local(c.tag) == "error"), None)
            message = (_attr(element, rule.message) if rule.message else None) or (
                _attr(child, "message") if child is not None else None
            ) or f"{local(element.tag)} failed"
            code = (_attr(element, rule.code) if rule.code else None) or (
                _attr(child, "type") if child is not None else None
            )
            return code, message
    return None


# ---------------------------------------------------------------------------
# Empty values


def _unwrap(annotation: Any) -> Any:
    while get_origin(annotation) is typing.Annotated:
        annotation = get_args(annotation)[0]
    return annotation


def _accepts_empty_string(annotation: Any) -> bool:
    """Whether ``""`` is a meaningful value for the annotation (strings, ``Any``, ``Literal[..., ""]``)."""
    annotation = _unwrap(annotation)
    origin = get_origin(annotation)
    if annotation is str or annotation is Any:
        return True
    if origin is Literal:
        return "" in get_args(annotation)
    if origin in (Union, types.UnionType):
        return any(_accepts_empty_string(a) for a in get_args(annotation))
    return False


def _model_in(annotation: Any) -> type[BaseModel] | None:
    """The model of a model or list-of-models annotation (optionally nullable)."""
    annotation = _unwrap(annotation)
    origin = get_origin(annotation)
    if origin in (Union, types.UnionType):
        for arg in get_args(annotation):
            found = _model_in(arg)
            if found is not None:
                return found
        return None
    if origin is list:
        (item,) = get_args(annotation) or (Any,)
        return _model_in(item)
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation
    return None


def is_list_type(annotation: Any) -> bool:
    annotation = _unwrap(annotation)
    origin = get_origin(annotation)
    if origin is list:
        return True
    if origin in (Union, types.UnionType):
        return any(is_list_type(a) for a in get_args(annotation))
    return False


def prune_empty(data: Any, model: Any) -> Any:
    """Make empty XML values absent where the model cannot use them.

    XML replies carry ``<PoeClass/>`` and ``attr=""`` for "no value". Extraction
    hands them over as ``""``, which would fail int, float, bool and enum fields.
    This drops (recursively, following nested models and lists of models):

    - ``""`` for every field whose type does not accept a string (string
      fields keep ``""``);
    - an empty list for an optional array field (no element means the device
      did not report it, ``None``); a required array stays ``[]``.
    """
    if isinstance(data, list):
        return [prune_empty(item, model) for item in data]
    if not isinstance(data, dict) or not (isinstance(model, type) and issubclass(model, BaseModel)):
        return data
    keys = {}
    for name, info in model.model_fields.items():
        for key in (name, info.alias, info.validation_alias):
            if isinstance(key, str):
                keys[key] = info
    out: dict[str, Any] = {}
    for key, value in data.items():
        info = keys.get(key)
        if info is None:
            out[key] = value
            continue
        if value == "" and not _accepts_empty_string(info.annotation):
            continue
        if value == [] and not info.is_required() and is_list_type(info.annotation):
            continue
        nested = _model_in(info.annotation)
        out[key] = prune_empty(value, nested) if nested is not None else value
    return out
