"""service_json, soap and rest bindings, discovery rendering and optional wrapped params.

Each family also gets an end-to-end test: a small fixture spec is generated, the module is executed
and its API class is called through ``Device`` over ``httpx.MockTransport``.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Any

import httpx
import pytest

from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import ApiError, ApiUnavailable
from codegen.build import build_api
from codegen.loader import LoadedSpec, SpecError, validate
from codegen.output import format_python
from codegen.render import render_module, signatures


def base_spec(family: str, binding: dict[str, Any], operations: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {
        "format": 2, "id": "demo", "name": "Demo", "summary": "A demo.", "section": "network-video",
        "family": family, "python": {"module": "demo", "class": "Demo"}, "access": "viewer",
        "binding": binding, "operations": operations, **extra,
    }  # fmt: skip


def build(spec: dict[str, Any]):
    assert validate(spec) == []
    return build_api(LoadedSpec(Path("specs/apis/demo.yaml"), spec))


def generate(spec: dict[str, Any]) -> str:
    return format_python(render_module(build(spec)), "src/ax_devil_device_api/apis/demo.py")


_counter = 0


def load_module(spec: dict[str, Any]) -> types.ModuleType:
    """Execute the generated module as a member of the ``apis`` package."""
    global _counter
    _counter += 1
    name = f"ax_devil_device_api.apis._fixture_{_counter}"
    module = types.ModuleType(name)
    module.__package__ = "ax_devil_device_api.apis"
    sys.modules[name] = module
    exec(compile(generate(spec), name, "exec"), module.__dict__)  # noqa: S102
    return module


def device(handler: Any) -> Device:
    return Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler))


# -- service_json ------------------------------------------------------------------

SJ_SPEC = base_spec(
    "service_json",
    {"path": "/vapix/axast"},
    {
        "perform_speaker_test": {
            "summary": "Run a speaker test.", "effect": "action",
            "binding": {"operation": "axast:PerformSpeakerTest"},
            "params": {"type": "object", "properties": {"volume": {"type": "integer"}}},
            "result": {"$ref": "#/types/TestResult"},
        },
        "stop": {"summary": "Stop.", "effect": "action", "binding": {"operation": "axast:Stop", "path": "/vapix/other"}},
    },
    types={"TestResult": {"type": "object", "required": ["resultCode"], "properties": {"resultCode": {"type": "integer"}}}},
    errors={"axast:DeviceNotCalibrated": {"description": "Not calibrated", "kind": "unavailable"}},
)


def test_service_json_renders_binding_and_errors() -> None:
    code = generate(SJ_SPEC)
    assert 'ServiceJsonBinding(PATH, "axast:PerformSpeakerTest")' in code
    assert 'ServiceJsonBinding("/vapix/other", "axast:Stop")' in code
    assert "family=Family.SERVICE_JSON" in code
    assert '"axast:DeviceNotCalibrated": ErrorCode(' in code


def test_service_json_needs_operation() -> None:
    spec = base_spec("service_json", {"path": "/vapix/x"}, {"go": {"summary": "x", "binding": {}}})
    assert validate(spec)  # the schema requires binding.operation


def test_service_json_end_to_end() -> None:
    module = load_module(SJ_SPEC)
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if json.loads(request.content).get("axast:Stop") is not None:
            return httpx.Response(
                400, json={"Fault": "env:Receiver", "FaultCode": "ter:Action", "FaultSubCode": "axast:DeviceNotCalibrated",
                           "FaultReason": "calibrate first", "FaultMsg": None},
            )  # fmt: skip
        return httpx.Response(200, json={"resultCode": 7})

    with device(handler) as dev:
        api = dev.api(module.DemoApi)
        result = api.perform_speaker_test(volume=5)
        assert result.result_code == 7
        assert seen[0].url.path == "/vapix/axast"
        assert json.loads(seen[0].content) == {"axast:PerformSpeakerTest": {"volume": 5}}
        with pytest.raises(ApiUnavailable) as caught:
            api.stop()
        assert caught.value.code == "axast:DeviceNotCalibrated"
        assert seen[1].url.path == "/vapix/other"


# -- soap --------------------------------------------------------------------------

NS = "http://www.axis.com/vapix/ws/demo1"
SOAP_SPEC = base_spec(
    "soap",
    {"namespace": NS},
    {
        "get_things": {
            "summary": "List things.", "effect": "read",
            "binding": {"action": f"{NS}/GetThings", "element": "GetThings"},
            "params": {"type": "object", "properties": {"Filter": {"type": "string"}, "@token": {"type": "string"}}},
            "result": {"$ref": "#/types/Things"},
        },
        "reset": {
            "summary": "Reset.", "effect": "action",
            "binding": {"action": f"{NS}/Reset", "element": "Reset"},
            "errors": {"ter:Failed": {"description": "Failed", "kind": "unavailable"}},
        },
    },
    types={
        "Thing": {"type": "object", "properties": {"token": {"type": "string"}, "Name": {"type": "string"},
                                                  "size": {"type": "integer", "x-xml": {"attribute": "size"}}}},
        "Things": {"type": "object", "required": ["Count"], "properties": {
            "Count": {"type": "integer"},
            "Thing": {"type": "array", "items": {"$ref": "#/types/Thing"}},
        }},
    },
)  # fmt: skip


def test_soap_renders_binding_with_child_default_and_attribute_names() -> None:
    api = build(SOAP_SPEC)
    request = next(t for t in api.types if t.name == "GetThingsRequest")
    assert [(f.py, f.wire) for f in request.fields] == [("filter", "Filter"), ("token", "@token")]
    code = generate(SOAP_SPEC)
    assert "SoapBinding(" in code and f'"{NS}/GetThings",\n            "GetThings",\n            "{NS}",' in code
    # scalars of a soap reply are child elements unless x-xml says otherwise
    assert 'XmlField("Count", source="child")' in code
    assert 'XmlField("size")' in code
    assert "path=" not in code  # the default /vapix/services path is not repeated


def test_soap_requires_namespace_and_object_result() -> None:
    op = {"summary": "x", "binding": {"action": "a", "element": "E"}}
    with pytest.raises(SpecError, match="namespace"):
        build(base_spec("soap", {}, {"go": op}))
    bad = {**op, "result": {"type": "string"}}
    with pytest.raises(SpecError, match="object type"):
        build(base_spec("soap", {"namespace": NS}, {"go": bad}))


def test_soap_end_to_end() -> None:
    module = load_module(SOAP_SPEC)
    seen: list[httpx.Request] = []
    env = "http://www.w3.org/2003/05/soap-envelope"

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if b"<Reset" in request.content:
            body = (
                f'<Envelope xmlns="{env}"><Body><Fault><Code><Value>env:Receiver</Value><Subcode><Value>ter:Failed</Value>'
                "</Subcode></Code><Reason><Text>nope</Text></Reason></Fault></Body></Envelope>"
            )
            return httpx.Response(500, content=body)
        body = (
            f'<s:Envelope xmlns:s="{env}"><s:Body><t:GetThingsResponse xmlns:t="{NS}"><t:Count>2</t:Count>'
            '<t:Thing size="3"><t:token>a</t:token><t:Name>One</t:Name></t:Thing>'
            '<t:Thing size="4"><t:token>b</t:token></t:Thing></t:GetThingsResponse></s:Body></s:Envelope>'
        )
        return httpx.Response(200, content=body)

    with device(handler) as dev:
        api = dev.api(module.DemoApi)
        result = api.get_things(filter="x", token="t1")
        assert result.count == 2
        assert [(t.token, t.name, t.size) for t in result.thing] == [("a", "One", 3), ("b", None, 4)]
        request = seen[0]
        assert request.url.path == "/vapix/services"
        assert f'action="{NS}/GetThings"' in request.headers["content-type"]
        assert f'<GetThings token="t1" xmlns="{NS}"><Filter>x</Filter>' in request.content.decode()
        with pytest.raises(ApiUnavailable) as caught:
            api.reset()
        assert caught.value.code == "ter:Failed"


# -- rest --------------------------------------------------------------------------

REST_SPEC = base_spec(
    "rest",
    {"root": "/vapix/things"},
    {
        "get_thing": {
            "summary": "Get one.", "effect": "read",
            "binding": {"method": "GET", "path": "/{id}", "query": ["detail"]},
            "params": {"type": "object", "required": ["id"],
                       "properties": {"id": {"type": "string"}, "detail": {"type": "boolean"}}},
            "result": {"$ref": "#/types/Thing"},
            "errors": {404: {"description": "Missing", "kind": "not_found"}},
        },
        "create_thing": {
            "summary": "Create.", "effect": "write", "write": "create",
            "binding": {"method": "POST", "body": "object"},
            "params": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}},
            "result": {"$ref": "#/types/Thing"},
        },
        "set_tags": {
            "summary": "Replace tags.", "effect": "write", "write": "replace",
            "binding": {"method": "PUT", "path": "/{id}/tags", "body": "value", "body_field": "tags"},
            "params": {"type": "object", "required": ["id", "tags"],
                       "properties": {"id": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}},
        },
    },
    types={"Thing": {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}, "name": {"type": "string"}}}},
)  # fmt: skip


def test_rest_renders_binding_and_positional_path_keys() -> None:
    code = generate(REST_SPEC)
    assert 'ROOT = "/vapix/things"' in code
    assert 'RestBinding("GET", f"{ROOT}/{{id}}", query=(("detail", "detail"),))' in code
    assert 'RestBinding("POST", ROOT, body="object")' in code
    assert 'body="value", body_field="tags"' in code
    api = build(REST_SPEC)
    assert api.ops[0].positional == ["id"]
    (sig,), _ = signatures(api.ops[0])
    assert sig.args[0] == "id: str"


def test_rest_binding_checks() -> None:
    def rest(binding: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any]:
        op = {"summary": "x", "binding": binding}
        if params:
            op["params"] = params
        return base_spec("rest", {"root": "/r"}, {"go": op})

    with pytest.raises(SpecError, match="'id'"):
        build(rest({"method": "GET", "path": "/{id}"}, {"type": "object", "properties": {"x": {"type": "string"}}}))
    with pytest.raises(SpecError, match="must be a required"):
        build(rest({"method": "GET", "path": "/{id}"}, {"type": "object", "properties": {"id": {"type": "string"}}}))
    with pytest.raises(SpecError, match="body_field"):
        build(rest({"method": "PUT", "body": "value"}, {"type": "object", "properties": {"x": {"type": "string"}}}))


def test_rest_end_to_end() -> None:
    module = load_module(REST_SPEC)
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.endswith("/missing"):
            return httpx.Response(404, text="no such thing")
        if request.method == "PUT":
            return httpx.Response(204)
        return httpx.Response(200, json={"id": "a b", "name": "n"})

    with device(handler) as dev:
        api = dev.api(module.DemoApi)
        thing = api.get_thing("a b", detail=True)
        assert thing.id == "a b"
        assert seen[0].url.raw_path == b"/vapix/things/a%20b?detail=true"
        api.create_thing(name="n")
        assert json.loads(seen[1].content) == {"name": "n"}
        api.set_tags("a", tags=["x", "y"])
        assert seen[2].method == "PUT" and json.loads(seen[2].content) == ["x", "y"]
        with pytest.raises(ApiError) as caught:
            api.get_thing("missing")
        assert caught.value.code == 404


# -- discovery ---------------------------------------------------------------------


def test_discovery_compare_and_acap_render() -> None:
    spec = base_spec("cgi", {"path": "/axis-cgi/x.cgi"}, {})
    spec["discovery"] = [
        {"param": {"name": "Properties.A.Version", "value": "1.20", "compare": ">="}},
        {"param": {"name": "Properties.B", "value": "3", "compare": "=="}},
        {"param": {"name": "Properties.C"}},
        {"acap": {"name": "loiteringguard"}},
        {"service": {"namespace": "http://www.axis.com/vapix/ws/light"}},
    ]
    code = generate(spec)
    assert 'ParamDiscovery("Properties.A.Version", "1.20", ">=")' in code
    assert 'ParamDiscovery("Properties.B", "3")' in code
    assert 'ParamDiscovery("Properties.C")' in code
    assert 'AcapDiscovery("loiteringguard")' in code
    assert 'ServiceDiscovery("http://www.axis.com/vapix/ws/light")' in code
    assert "import" in code and "AcapDiscovery," in code


def test_discovery_compare_needs_value() -> None:
    spec = base_spec("cgi", {"path": "/axis-cgi/x.cgi"}, {}, discovery=[{"param": {"name": "P", "compare": ">="}}])
    with pytest.raises(SpecError, match="needs a value"):
        generate(spec)


# -- optional wrapped params ---------------------------------------------------------

JR = {"path": "/axis-cgi/x.cgi", "major": 1, "negotiation": {"fixed": "1.0"}}


def jsonrpc_with(optional: bool) -> dict[str, Any]:
    params: dict[str, Any] = {"type": "array", "items": {"type": "string"}, "x-arg-name": "ports"}
    if optional:
        params["x-arg-optional"] = True
    return base_spec("jsonrpc", JR, {"get_ports": {"summary": "x", "effect": "read", "binding": {"method": "getPorts"}, "params": params}})


def test_wrapped_params_are_required_by_default_and_optional_on_request() -> None:
    required = build(jsonrpc_with(False)).ops[0]
    optional = build(jsonrpc_with(True)).ops[0]
    (sig,), _ = signatures(required)
    assert sig.args[0] == "ports: list[str]"
    (sig,), _ = signatures(optional)
    assert sig.args[:2] == ["ports: list[str] | MISSING = MISSING", "*"]
    assert optional.params_field == "ports"
    assert "ports: list[str] | None = None" in generate(jsonrpc_with(True))


def test_optional_wrapped_params_omit_params_on_the_wire() -> None:
    module = load_module(jsonrpc_with(True))
    bodies: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        bodies.append(body)
        return httpx.Response(200, json={"apiVersion": "1.0", "method": "getPorts", "data": {}})

    with device(handler) as dev:
        api = dev.api(module.DemoApi)
        api.get_ports()
        api.get_ports(["a"])
    assert "params" not in bodies[0]
    assert bodies[1]["params"] == ["a"]


def test_x_arg_optional_only_for_wrapped_params() -> None:
    spec = base_spec(
        "jsonrpc", JR,
        {"go": {"summary": "x", "binding": {"method": "go"},
                "params": {"type": "object", "x-arg-optional": True, "properties": {"a": {"type": "string"}}}}},
    )  # fmt: skip
    with pytest.raises(SpecError, match="x-arg-optional"):
        build(spec)


# -- reserved type names and write docstrings --------------------------------------


def test_reserved_type_names_are_renamed_deterministically() -> None:
    obj = {"type": "object", "properties": {"a": {"type": "string"}}}
    spec = base_spec(
        "jsonrpc", JR,
        {
            "get_it": {
                "summary": "x", "effect": "read", "binding": {"method": "getIt"},
                "params": {"$ref": "#/types/Model"},
                "result": {"$ref": "#/types/DemoApi"},
                "round_trip": {"from": "DemoApi", "set": {}},
            },
        },
        types={"Model": obj, "DemoApi": obj, "ModelType": obj, "Text": {"type": "string"}},
    )
    api = build(spec)
    assert sorted(t.name for t in api.types) == ["DemoApiType", "ModelType", "ModelTypeType", "TextType"]
    code = generate(spec)
    assert code == generate(spec)  # deterministic
    module = load_module(spec)
    assert module.ModelTypeType.__mro__[1] is module.Model  # the runtime base class keeps its name
    assert issubclass(module.DemoApiType, module.Model) and module.DemoApi is not module.DemoApiType
    request = module.ModelTypeType(a="x")
    assert request.to_wire() == {"a": "x"}


def _patch_op(params: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return base_spec("jsonrpc", JR, {"set_it": {"summary": "Set it.", "effect": "write", "write": "patch", "binding": {"method": "setIt"}, "params": params, **extra}})


def test_patch_docstring_names_fields_for_flat_params_and_entries_for_lists_of_models() -> None:
    flat = generate(_patch_op({"type": "object", "properties": {"a": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}}))
    assert "Changes only the fields given." in flat
    entries = generate(_patch_op({
        "type": "object",
        "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {"token": {"type": "string"}}}}},
    }))
    assert "Changes only the fields given." not in entries
    assert "Changes only the entries given; entries that do not exist yet may be created." in entries
