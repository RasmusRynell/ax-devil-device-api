from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from codegen.build import build_api
from codegen.cli import main
from codegen.loader import LoadedSpec, SpecError, validate
from codegen.naming import NamingError, field_name, pascal_case, snake_case
from codegen.patches import PatchError, apply_patch
from codegen.render import render_module, signatures


def make_spec(family: str = "cgi", **overrides: Any) -> dict[str, Any]:
    spec: dict[str, Any] = {
        "format": 2,
        "id": "demo",
        "name": "Demo",
        "summary": "A demo.",
        "section": "network-video",
        "family": family,
        "python": {"module": "demo", "class": "Demo"},
        "access": "viewer",
        "binding": {"cgi": {"path": "/axis-cgi/demo.cgi"}}.get(family, {}),
        "operations": {},
    }
    if family == "cgi":
        spec["binding"] = {"path": "/axis-cgi/demo.cgi"}
    spec.update(overrides)
    return spec


def build(spec: dict[str, Any]):
    return build_api(LoadedSpec(Path("specs/apis/demo.yaml"), spec))


# -- naming ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("wire", "expected"),
    [
        ("keepExistingPassword", "keep_existing_password"),
        ("CACertID", "ca_cert_id"),
        ("clientCertID", "client_cert_id"),
        ("alpnProtocol", "alpn_protocol"),
        ("data_source_key", "data_source_key"),
        ("HTTPServer", "http_server"),
        ("class", "class_"),
        ("a-b.c", "a_b_c"),
    ],
)
def test_snake_case(wire: str, expected: str) -> None:
    assert snake_case(wire) == expected


def test_pascal_case_and_overrides() -> None:
    assert pascal_case("list_definitions") == "ListDefinitions"
    assert field_name("whatever", "custom") == "custom"
    assert field_name("json") == "json_"  # would shadow a pydantic attribute
    assert field_name("class") == "class_"
    with pytest.raises(NamingError):
        field_name("json", "copy")


# -- type mapping --------------------------------------------------------------


def test_type_mapping_and_aliases() -> None:
    spec = make_spec(
        types={
            "Key": {"type": "string", "minLength": 3, "pattern": "^a"},
            "Mode": {"enum": ["a", "b"]},
            "Thing": {
                "type": "object",
                "required": ["Key"],
                "x-nullable": ["note"],
                "x-masked": ["secret"],
                "properties": {
                    "Key": {"$ref": "#/types/Key"},
                    "note": {"type": "string"},
                    "secret": {"type": "string"},
                    "mode": {"$ref": "#/types/Mode"},
                    "tags": {"type": "array", "items": {"type": "integer"}, "default": []},
                    "labels": {"type": "object", "additionalProperties": {"type": "string"}},
                    "level": {"type": "integer", "minimum": 1, "maximum": 5},
                },
            },
        }
    )
    api = build(spec)
    types = {t.name: t for t in api.types}
    assert types["Key"].alias_expr == "Annotated[str, Field(min_length=3, pattern='^a')]"
    assert types["Mode"].alias_expr == 'Literal[\'a\', \'b\']'
    fields = {f.py: f for f in types["Thing"].fields}
    assert fields["key"].wire == "Key" and fields["key"].required
    assert fields["tags"].ann == "list[int]" and fields["tags"].default == "[]"
    assert fields["labels"].ann == "dict[str, str]" and fields["labels"].sig == "Mapping[str, str]"
    assert fields["level"].kwargs == ["ge=1", "le=5"]
    assert types["Thing"].nullable == ["note"]
    assert types["Thing"].masked == ["secret"]
    code = render_module(api)
    assert '__nullable__: ClassVar[frozenset[str]] = frozenset({"note"})' in code or "'note'" in code


def test_inline_params_naming_and_shared_x_name() -> None:
    shared = {"type": "object", "x-name": "IdRequest", "required": ["id"], "properties": {"id": {"type": "string"}}}
    ops = {
        "get_it": {"summary": "x", "effect": "read", "binding": {"method": "GET", "path": "/a/{id}"}, "params": shared},
        "drop_it": {"summary": "x", "effect": "write", "binding": {"method": "DELETE", "path": "/a/{id}"}, "params": shared},
        "make_it": {
            "summary": "x",
            "effect": "write",
            "binding": {"method": "POST", "path": "/a"},
            "params": {"type": "object", "properties": {"name": {"type": "string"}}},
        },
    }
    api = build(make_spec("dca", binding={"root": "/config/rest/x/v1"}, operations=ops))
    names = [t.name for t in api.types]
    assert names.count("IdRequest") == 1 and "MakeItRequest" in names
    clash = {**ops, "other": {**ops["get_it"], "params": {**shared, "required": []}}}
    with pytest.raises(SpecError, match="IdRequest"):
        build(make_spec("dca", binding={"root": "/config/rest/x/v1"}, operations=clash))


# -- signature rule ------------------------------------------------------------


def _op(params: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {"summary": "x", "effect": "read", "binding": {"method": "GET", "path": "/x"}, "params": params, **extra}


def props(n: int) -> dict[str, Any]:
    return {f"p{i}": {"type": "string"} for i in range(n)}


def test_small_operation_gets_one_signature_with_positional_then_keyword_only() -> None:
    params = {"type": "object", "required": ["a"], "properties": props(3) | {"a": {"type": "string"}}}
    api = build(make_spec(operations={"go": _op(params, positional=["a", "p0"])}))
    (op,) = api.ops
    assert not op.overloaded
    (sig,), impl = signatures(op)
    assert impl is None
    assert sig.args[:3] == ["a: str", "p0: str | MISSING = MISSING", "*"]
    assert sig.args[-1].startswith("request_options")


def test_more_than_four_fields_or_nested_model_gets_overloads() -> None:
    big = build(make_spec(operations={"go": _op({"type": "object", "properties": props(5)})}))
    assert big.ops[0].overloaded
    nested = {"type": "object", "properties": {"inner": {"type": "object", "properties": {"x": {"type": "string"}}}}}
    api = build(make_spec(operations={"go": _op(nested)}))
    assert api.ops[0].overloaded
    overloads, impl = signatures(api.ops[0])
    assert len(overloads) == 2 and impl is not None
    four = build(make_spec(operations={"go": _op({"type": "object", "properties": props(4)})}))
    assert not four.ops[0].overloaded


def test_dca_path_keys_are_positional() -> None:
    params = {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}, "q": {"type": "string"}}}
    spec = make_spec("dca", binding={"root": "/r"}, operations={"get": _op(params)})
    spec["operations"]["get"]["binding"]["path"] = "/items/{id}"
    api = build(spec)
    assert api.ops[0].positional == ["id"]
    (sig,), _ = signatures(api.ops[0])
    assert sig.args[0] == "id: str" and sig.args[1] == "*"


def test_required_positional_after_optional_is_rejected() -> None:
    params = {"type": "object", "required": ["b"], "properties": {"a": {"type": "string"}, "b": {"type": "string"}}}
    with pytest.raises(SpecError, match="follows an optional"):
        build(make_spec(operations={"go": _op(params, positional=["a", "b"])}))


# -- patches -------------------------------------------------------------------


def test_patch_ops_apply_and_do_not_mutate_input() -> None:
    base = {"a": {"b": [1, 2]}, "c": "x"}
    ops = [
        {"op": "replace", "path": "/c", "value": "y", "expect": "x"},
        {"op": "add", "path": "/a/b/-", "value": 3},
        {"op": "remove", "path": "/a/b/0", "expect": 1},
        {"op": "add", "path": "/n~1s", "value": True},
    ]
    out = apply_patch(base, ops)
    assert out == {"a": {"b": [2, 3]}, "c": "y", "n/s": True}
    assert base == {"a": {"b": [1, 2]}, "c": "x"}


def test_patch_expect_mismatch_fails_loudly() -> None:
    with pytest.raises(PatchError, match="expected 'old'"):
        apply_patch({"c": "new"}, [{"op": "replace", "path": "/c", "value": "z", "expect": "old"}])
    with pytest.raises(PatchError, match="does not exist"):
        apply_patch({"c": 1}, [{"op": "replace", "path": "/zzz", "value": 1}])


# -- schema --------------------------------------------------------------------


def test_schema_catches_typos() -> None:
    good = make_spec(operations={"go": {"summary": "x", "effect": "read", "binding": {"method": "GET"}}})
    assert validate(good) == []
    assert validate({**good, "famly": "cgi"})
    bad_op = make_spec(operations={"go": {"summary": "x", "efect": "read"}})
    assert validate(bad_op)
    assert validate({**good, "x-note": 1}) == []
    stray = make_spec(types={"T": {"type": "object", "properties": {"a": {"type": "string", "oops": 1}}}})
    assert validate(stray)


# -- xml mapping ---------------------------------------------------------------


def test_xml_mapping_is_rendered_from_result_types() -> None:
    spec = make_spec(
        types={
            "Item": {
                "type": "object",
                "properties": {
                    "profile": {"type": "integer"},
                    "note": {"type": "string", "x-xml": "text"},
                    "label": {"type": "string", "x-xml": {"child": "Label"}},
                },
            },
            "Items": {
                "type": "object",
                "x-xml": {"root": "items"},
                "properties": {
                    "items": {"type": "array", "items": {"$ref": "#/types/Item"}, "x-xml": {"path": "item"}},
                },
            },
        },
        operations={
            "list_items": {
                "summary": "x",
                "effect": "read",
                "binding": {"reply": {"xml": {"status_error": {"attribute": "result", "value": "ERROR", "message": "errormsg"}}}},
                "result": {"$ref": "#/types/Items"},
            },
            "raw": {"summary": "x", "effect": "read", "binding": {"reply": "xml"}, "result": {"x-xml": True}},
        },
    )
    assert validate(spec) == []
    code = render_module(build(spec))
    assert 'XmlField("note", source="text")' in code.replace("'", '"')
    assert 'source="child", name="Label"' in code.replace("'", '"')
    assert 'many=True' in code and 'root="items"' in code.replace("'", '"')
    assert "XmlStatusError(" in code
    assert "result=ET.Element" in code


# -- golden ----------------------------------------------------------------------


def test_committed_generated_files_are_up_to_date() -> None:
    assert main(["check"]) == 0


def test_jsonrpc_array_params_are_wrapped_in_a_single_positional_field() -> None:
    spec = make_spec(
        "jsonrpc",
        binding={"path": "/axis-cgi/x.cgi", "major": 1, "versions": ["1.0"]},
        types={"Item": {"type": "object", "properties": {"a": {"type": "string"}}}},
        operations={
            "set_items": {
                "summary": "x",
                "effect": "write",
                "binding": {"method": "setItems"},
                "params": {"type": "array", "items": {"$ref": "#/types/Item"}, "x-arg-name": "items"},
            },
            "set_map": {
                "summary": "x",
                "effect": "write",
                "binding": {"method": "setMap"},
                "params": {"type": "object", "additionalProperties": {"type": "string"}},
            },
        },
    )
    assert validate(spec) == []
    api = build(spec)
    items, mapping = api.ops
    assert items.params_field == "items" and items.positional == ["items"] and not items.overloaded
    assert mapping.params_field == "params" and mapping.params.fields[0].is_mapping
    code = render_module(api)
    assert "params_field='items'" in code.replace('"', "'")
