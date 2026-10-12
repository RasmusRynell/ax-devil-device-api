"""Declarative XML-to-data mapping for classic CGI replies.

Generated code describes where each field of a result model lives in the
XML reply; ``extract`` turns the parsed document into plain data that the
result model then validates. Element and attribute names are matched by
local name, so namespaces never matter.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class XmlField:
    """Where one model field comes from, relative to the element of its model.

    - ``attribute``: the attribute ``name`` (the default for scalars).
    - ``text``: the element's own text.
    - ``child``: the text of the first child element ``name``.
    - ``path``: elements at a ``/``-separated path of local names; with
      ``many`` every match becomes a list item. ``nested`` maps each match
      to an object; without it the match's text is used.
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
            message = (_attr(element, rule.message) if rule.message else None) or f"{local(element.tag)} failed"
            code = _attr(element, rule.code) if rule.code else None
            return code, message
    return None
