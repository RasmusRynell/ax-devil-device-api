"""Deterministic Python names derived from wire names and spec ids."""

from __future__ import annotations

import keyword
import re

from pydantic import BaseModel

from ax_devil_device_api._protocols.base import Model

_BOUNDARY_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
_BOUNDARY_2 = re.compile(r"([a-z0-9])([A-Z])")
_NON_IDENT = re.compile(r"[^0-9a-zA-Z_]+")

# Names a model field or method argument must not take.
RESERVED_FIELD_NAMES = frozenset(dir(BaseModel)) | frozenset(dir(Model)) | {"model_config"}
RESERVED_ARG_NAMES = frozenset({"self", "request_options"})


class NamingError(ValueError):
    pass


def snake_case(wire: str) -> str:
    """``keepExistingPassword`` -> ``keep_existing_password``; ``CACertID`` -> ``ca_cert_id``."""
    text = _NON_IDENT.sub("_", wire)
    text = _BOUNDARY_1.sub(r"\1_\2", text)
    text = _BOUNDARY_2.sub(r"\1_\2", text)
    text = re.sub(r"_+", "_", text).strip("_").lower()
    if not text:
        raise NamingError(f"cannot derive a Python name from {wire!r}")
    if text[0].isdigit():
        text = "_" + text
    if keyword.iskeyword(text):
        text += "_"
    return text


def pascal_case(text: str) -> str:
    """``list_definitions`` -> ``ListDefinitions``; keeps existing capitals (``getAll`` -> ``GetAll``)."""
    parts = [p for p in _NON_IDENT.sub("_", text).split("_") if p]
    return "".join(p[0].upper() + p[1:] for p in parts)


def field_name(wire: str, override: str | None = None) -> str:
    name = override or snake_case(wire)
    if not name.isidentifier() or keyword.iskeyword(name):
        raise NamingError(f"{name!r} (from {wire!r}) is not a usable Python name; set x-python-name")
    if name in RESERVED_FIELD_NAMES or name in RESERVED_ARG_NAMES:
        if override:
            raise NamingError(f"x-python-name {override!r} for {wire!r} is reserved")
        name += "_"
    return name


def last_word(type_name: str) -> str:
    """``ClientConfig`` -> ``config`` (parameter name of ``from_current``)."""
    words = re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", type_name)
    return snake_case(words[-1]) if words else "value"
