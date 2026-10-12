"""Intermediate model: what the renderer needs, derived and checked from a spec."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldDef:
    py: str
    wire: str
    ann: str
    """Annotation inside the model (without ``| None`` for optional fields; see ``required``)."""
    sig: str
    """Type in method signatures (no constraints; ``Mapping`` for dicts)."""
    required: bool
    nullable: bool = False
    kwargs: list[str] = field(default_factory=list)
    """Constraint arguments for ``Field(...)``."""
    default: str | None = None
    """Python literal for a non-``None`` default (empty containers only)."""
    doc: str | None = None
    schema: dict[str, Any] = field(default_factory=dict)
    style: str | None = None
    xml: Any = None
    has_model: bool = False
    model_name: str | None = None
    """Name of the model type this field holds (directly or as list items), if any."""

    @property
    def is_mapping(self) -> bool:
        return self.sig.startswith("Mapping[")


@dataclass
class RoundTrip:
    from_name: str
    set_values: dict[str, Any]
    """Python field name -> value."""
    op_id: str


@dataclass
class TypeDef:
    name: str
    kind: str
    """``model`` or ``alias``."""
    doc: str | None = None
    fields: list[FieldDef] = field(default_factory=list)
    alias_expr: str = ""
    nullable: list[str] = field(default_factory=list)
    masked: list[str] = field(default_factory=list)
    read_only: list[str] = field(default_factory=list)
    schema: dict[str, Any] = field(default_factory=dict)
    round_trip: RoundTrip | None = None

    def by_wire(self, wire: str) -> FieldDef | None:
        return next((f for f in self.fields if f.wire == wire), None)

    def by_py(self, py: str) -> FieldDef | None:
        return next((f for f in self.fields if f.py == py), None)


@dataclass
class Applic:
    path: str
    since: tuple[int, int]
    value: Any = None


@dataclass
class OpDef:
    id: str
    summary: str
    description: str | None
    access: str
    effect: str
    write: str | None
    since: tuple[int, int] | None
    support: str
    binding: dict[str, Any]
    params: TypeDef | None
    result: str | None
    """Result type expression, or ``None`` for no result."""
    result_model: TypeDef | None
    errors: dict[Any, dict[str, Any]]
    applicability: list[Applic]
    positional: list[str]
    overloaded: bool
    mapping_args: list[str]
    round_trip: RoundTrip | None
    params_field: str | None = None
    """jsonrpc: the single request field sent as the whole ``params``."""
    reply_map: str | None = None
    """Rendered ``XmlMap(...)`` for cgi xml replies."""


@dataclass
class ApiDef:
    id: str
    name: str
    summary: str
    section: str
    family: str
    module: str
    class_name: str
    docs: list[str]
    access: str
    discovery: list[tuple[str, Any]]
    binding: dict[str, Any]
    errors: dict[Any, dict[str, Any]]
    types: list[TypeDef]
    ops: list[OpDef]
    source: str
    support: str = "docs-only"
