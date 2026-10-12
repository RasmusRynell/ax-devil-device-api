"""Classic CGI conversion in codegen/migrate_v1.py (synthetic v1 input, no corpus needed)."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from codegen import migrate_v1 as m
from codegen.build import build_api
from codegen.loader import LoadedSpec, validate

XML_REPLY = (
    '<PositionResponse SchemaVersion="1.0"><Success><GetSuccess><Location><Lat>51.0</Lat></Location>'
    "<Text>hi</Text></GetSuccess></Success></PositionResponse>"
)


def v1_cgi(*ops: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "demo-cgi",
        "name": "Demo CGI",
        "summary": "Demo.",
        "status": "released",
        "styles": ["cgi_query"],
        "python": {"module": "demo_cgi", "class_name": "DemoCgiApi"},
        "auth": {"default_access_level": "operator"},
        "sources": [{"url": "https://example.test/doc"}],
        "operations": list(ops),
    }


def op(op_id: str, path: str = "/axis-cgi/demo.cgi", **kw: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": op_id, "name": op_id, "kind": "http_endpoint", "summary": op_id,
        "http": {"method": "GET", "path": path}, "params": [], "response": {"format": "text"},
    }
    out.update(kw)
    return out


def convert(v1: dict[str, Any]):
    doc, notes = m.convert_cgi(copy.deepcopy(v1), "network-video", {"all_modules": set()})
    return doc, notes


def spec_errors(doc: dict[str, Any]) -> None:
    api = build_api(LoadedSpec(Path("specs/apis/network-video/demo-cgi.yaml"), doc))
    assert api.ops
    validate(doc)


def test_query_params_reply_codecs_and_effects() -> None:
    v1 = v1_cgi(
        op("get_things", params=[{"name": "group", "in": "query", "type": "string", "required": True}],
           http={"method": "GET", "path": "/axis-cgi/demo.cgi", "fixed_query": {"action": "list"}},
           response={"format": "text_kv"}),
        op("set_thing", http={"method": "GET", "path": "/axis-cgi/other.cgi"},
           params=[{"name": "enabled", "in": "query", "type": "boolean", "description": "yes or no"}],
           response={"format": "text"},
           examples=[{"title": "ok", "request": {"raw": "GET /axis-cgi/other.cgi?enabled=yes"},
                      "response": {"raw": "OK"}}]),
        op("download_file", response={"format": "binary", "content_type": "image/jpeg"}),
    )
    doc, _ = convert(v1)
    assert doc["family"] == "cgi" and doc["access"] == "operator"
    ops = doc["operations"]
    assert ops["get_things"]["effect"] == "read"
    assert ops["get_things"]["binding"]["query"] == {"action": "list"}
    assert ops["get_things"]["binding"]["reply"] == "text_kv"
    assert ops["get_things"]["params"]["required"] == ["group"]
    assert ops["set_thing"]["binding"]["path"] == "/axis-cgi/other.cgi"
    assert ops["set_thing"]["binding"]["reply"] == "text_ok"
    assert ops["set_thing"]["params"]["properties"]["enabled"]["x-style"] == "axis_bool"
    assert ops["set_thing"]["examples"][0]["request"] == {"query": {"enabled": "yes"}}
    assert ops["download_file"]["binding"]["reply"] == {"binary": {"media_types": ["image/jpeg"]}}
    assert doc["binding"] == {"path": "/axis-cgi/demo.cgi"}
    assert doc["provenance"]["curated"] is False
    spec_errors(doc)


def test_form_encoding_for_post_with_form_params() -> None:
    v1 = v1_cgi(op("update_things", http={"method": "POST", "path": "/axis-cgi/demo.cgi"},
                   params=[{"name": "a", "in": "form", "type": "string"}]))
    doc, _ = convert(v1)
    binding = doc["operations"]["update_things"]["binding"]
    assert binding["method"] == "POST" and binding["encoding"] == "form"
    assert doc["operations"]["update_things"]["write"] == "patch"


@pytest.mark.parametrize(
    "bad",
    [
        {"http": {"method": "POST", "path": "/x.cgi", "request_content_type": "application/xml"}},
        {"params": [{"name": "k", "in": "path", "type": "string"}]},
        {"params": [{"name": "f", "in": "multipart", "type": "binary"}]},
        {"kind": "rtsp_request"},
    ],
)
def test_unsupported_operations_are_skipped_with_a_note(bad: dict[str, Any]) -> None:
    doc, notes = convert(v1_cgi(op("get_ok"), op("get_bad", **bad)))
    assert list(doc["operations"]) == ["get_ok"]
    assert any(k == "op-skipped" and "get_bad" in d for k, d in notes.items)


def test_api_without_expressible_operations_is_not_written() -> None:
    doc, _ = convert(v1_cgi(op("get_bad", kind="stream")))
    assert doc is None


def test_xml_result_is_mapped_from_the_sample_reply() -> None:
    schema = {"type": "object", "properties": {
        "Location": {"type": "object", "properties": {"Lat": {"type": "string"}}},
        "Text": {"type": "string"},
    }}
    v1 = v1_cgi(op("get_position", response={"format": "xml", "schema": schema},
                   examples=[{"title": "x", "response": {"raw": XML_REPLY}}]))
    doc, _ = convert(v1)
    result = doc["operations"]["get_position"]["result"]
    typ = doc["types"][result["$ref"].rsplit("/", 1)[-1]]
    assert typ["x-xml"] == {"root": "Success/GetSuccess"}
    assert typ["properties"]["Text"]["x-xml"] == {"child": "Text"}
    assert typ["properties"]["Location"]["properties"]["Lat"]["x-xml"] == {"child": "Lat"}
    spec_errors(doc)


def test_xml_without_schema_returns_the_raw_element() -> None:
    doc, notes = convert(v1_cgi(op("get_raw", response={"format": "xml"})))
    assert doc["operations"]["get_raw"]["result"] == {"x-xml": True}
    assert any(k == "xml-unmapped" for k, _ in notes.items)


def test_xml_error_rules_come_from_sample_replies() -> None:
    err = '<root><job result="ERROR" description="boom"/></root>'
    err2 = "<Error><SetError><ErrorCode>1</ErrorCode></SetError></Error>"
    doc, _ = convert(v1_cgi(op("do_it", response={"format": "xml"}, examples=[
        {"title": "e", "response": {"raw": err}}, {"title": "e2", "response": {"raw": err2}}])))
    xml = doc["operations"]["do_it"]["binding"]["reply"]["xml"]
    assert xml["status_error"] == {"attribute": "result", "value": "ERROR", "message": "description"}
    assert {"Error", "SetError", "GeneralError"} <= set(xml["error_elements"])


def test_effect_inference_covers_common_cgi_names() -> None:
    assert m.cgi_effect("list_disks", "GET") == ("read", None)
    assert m.cgi_effect("export_csv", "GET") == ("read", None)
    assert m.cgi_effect("remove_share", "GET") == ("write", "delete")
    assert m.cgi_effect("restart", "GET")[0] == "action"
    assert m.cgi_effect("zzz", "GET") == (None, None)


def test_existing_curated_spec_is_not_overwritten(tmp_path: Path) -> None:
    out = tmp_path / "network-video"
    out.mkdir()
    (out / "demo-cgi.yaml").write_text("provenance:\n  curated: true\n")
    src = tmp_path / "src" / "network-video"
    src.mkdir(parents=True)
    import yaml

    (src / "demo-cgi.yaml").write_text(yaml.safe_dump(v1_cgi(op("get_ok"))))
    assert m.main(["--src", str(tmp_path / "src"), "--out", str(tmp_path)]) == 0
    assert (out / "demo-cgi.yaml").read_text() == "provenance:\n  curated: true\n"


# -- service JSON, SOAP and REST ---------------------------------------------------------


def v1_service(styles: list[str], *ops: dict[str, Any], **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": "demo-svc", "name": "Demo service", "summary": "Demo.", "status": "released", "styles": styles,
        "python": {"module": "demo_svc", "class_name": "DemoSvcApi"}, "auth": {"default_access_level": "viewer"},
        "sources": [{"url": "https://example.test/doc"}], "operations": list(ops),
    }  # fmt: skip
    out.update(extra)
    return out


def json_op(op_id: str, name: str, path: str = "/vapix/demo", **kw: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": op_id, "name": name, "kind": "soap_operation", "summary": op_id,
        "http": {"method": "POST", "path": path}, "soap": {"input_element": name}, "params": [],
        "response": {"format": "json"},
    }  # fmt: skip
    out.update(kw)
    return out


def generates(doc: dict[str, Any]):
    api = build_api(LoadedSpec(Path("specs/apis/network-video/demo-svc.yaml"), doc))
    assert validate(doc) == []
    return api


def test_classification_of_non_cgi_specs() -> None:
    soap_op = json_op("get_x", "ax:GetX", path="/vapix/services")
    assert m.classify_v1_family(v1_service(["soap"], soap_op)) == "soap"
    assert m.classify_v1_family(v1_service(["soap", "other"], json_op("get_x", "ax:GetX"))) == "service_json"
    rest = {"id": "get_x", "kind": "http_endpoint", "http": {"method": "PATCH", "path": "/api/v1/x/{id}"}}
    assert m.classify_v1_family(v1_service(["other"], rest)) == "rest"
    assert m.classify_v1_family(v1_service(["websocket"], json_op("get_x", "ax:GetX"))) is None
    assert m.classify_v1_family(v1_service(["rtsp", "soap"], soap_op)) is None
    stream = {"id": "s", "kind": "stream", "http": {"path": "/axis-cgi/media.cgi"}}
    assert m.classify_v1_family(v1_service(["http_stream"], stream)) is None


def test_service_json_conversion() -> None:
    v1 = v1_service(
        ["soap", "other"],
        json_op("get_door_info", "tdc:GetDoorInfo",
                params=[{"name": "Token", "in": "soap_body", "type": "array", "items": {"type": "string"}, "required": True}],
                response={"format": "json", "schema": {"type": "object", "properties": {"DoorInfo": {"type": "array", "items": {"type": "string"}}}}},
                errors=[{"code": "env:Sender/ter:InvalidArgs/ter:TooManyItems", "scope": "operation", "description": "Too many items."}],
                examples=[{"title": "ok", "request": {"body": {"tdc:GetDoorInfo": {"Token": ["a"]}}}, "response": {"body": {"DoorInfo": []}}}]),
        json_op("lock_door", "tdc:LockDoor"),
        json_op("ws", "x:Ws", path="/vapix/demo/other"),
        {"id": "stream", "kind": "ws_message", "name": "s", "http": {"method": "GET", "path": "/x"}},
        discovery=[{"method": "param_property", "property": 'Properties.API.Demo.Version="1.2"', "notes": "1.2 and later."}],
    )  # fmt: skip
    doc, notes = m.convert_service(copy.deepcopy(v1), "network-video", {}, "service_json")
    assert doc["family"] == "service_json" and doc["binding"] == {"path": "/vapix/demo"}
    assert doc["discovery"] == [{"param": {"name": "Properties.API.Demo.Version", "value": "1.2", "compare": ">="}}]
    assert list(doc["operations"]) == ["get_door_info", "lock_door"]
    op = doc["operations"]["get_door_info"]
    assert op["binding"] == {"operation": "tdc:GetDoorInfo"} and op["effect"] == "read"
    assert op["errors"] == {"ter:TooManyItems": {"description": "Too many items.", "kind": "invalid_argument"}}
    assert op["examples"][0]["request"] == {"params": {"Token": ["a"]}}
    assert doc["operations"]["lock_door"]["effect"] == "action"
    kinds = [k for k, _ in notes.items]
    assert kinds.count("op-skipped") == 2  # other path, websocket kind
    assert doc["provenance"]["curated"] is False
    generates(doc)


def test_soap_conversion_uses_prefix_namespaces_and_local_names() -> None:
    def soap_op(op_id: str, element: str, **kw: Any) -> dict[str, Any]:
        out = json_op(op_id, element, path="/vapix/services")
        out["soap"] = {"input_element": element, "soap_action": f"http://x.test/a/{element.split(':')[1]}"}
        out["response"] = {"format": "xml", "schema": {"type": "object", "properties": {"wstop:TopicSet": {"type": "object"}, "Count": {"type": "integer"}}}}
        out.update(kw)
        return out

    v1 = v1_service(
        ["soap"],
        soap_op("get_things", "a:GetThings"),
        soap_op("get_other", "b:GetOther", soap={"input_element": "b:GetOther"}),
        soap={"endpoint": "/vapix/services", "namespaces": {"a": "http://x.test/a", "b": "http://x.test/b"}},
    )  # fmt: skip
    doc, notes = m.convert_service(copy.deepcopy(v1), "network-video", {}, "soap")
    assert doc["family"] == "soap" and doc["binding"]["namespace"] in ("http://x.test/a", "http://x.test/b")
    ops = doc["operations"]
    other = ops["get_things"] if doc["binding"]["namespace"] == "http://x.test/b" else ops["get_other"]
    assert other["binding"]["namespace"] in ("http://x.test/a", "http://x.test/b")
    assert ops["get_other"]["binding"]["action"] == "http://x.test/b/GetOther"  # derived, flagged
    assert ops["get_things"]["binding"]["element"] == "GetThings"
    assert set(ops["get_things"]["result"]["properties"]) == {"TopicSet", "Count"}
    assert "type" not in ops["get_things"]["result"]["properties"]["TopicSet"]  # open element
    assert any(k == "soap-action-inferred" for k, _ in notes.items)
    generates(doc)


def test_rest_conversion() -> None:
    def rest_op(op_id: str, method: str, path: str, params: list[dict[str, Any]], **kw: Any) -> dict[str, Any]:
        out = {"id": op_id, "name": f"{method} {path}", "kind": "http_endpoint", "summary": op_id,
               "http": {"method": method, "path": path}, "params": params, "response": {"format": "none"}}  # fmt: skip
        out.update(kw)
        return out

    ident = {"name": "itemId", "in": "path", "type": "string", "required": True}
    v1 = v1_service(
        ["other"],
        rest_op("list_items", "GET", "/api/v1.1/items", [],
                response={"format": "json", "schema": {"type": "array", "items": {"type": "string"}}}),
        rest_op("update_item", "PATCH", "/api/v1.1/items/{itemId}",
                [ident, {"name": "enabled", "in": "json_body", "type": "boolean", "required": True}]),
        rest_op("create_item", "POST", "/api/v1.2/items", [{"name": "body", "in": "json_body", "type": "object", "required": True, "schema": {"type": "object", "properties": {"a": {"type": "string"}}}}],
                errors=[{"code": 400, "http_status": 400, "scope": "operation"}, {"code": 401, "http_status": 401, "scope": "operation"}]),
        rest_op("search", "GET", "/api/v1.1/search", [{"name": "q", "in": "query", "type": "string"}]),
        rest_op("socket", "GET", "/api/v1.1/socket", [], kind="ws_message"),
    )  # fmt: skip
    doc, notes = m.convert_rest(copy.deepcopy(v1), "network-video", {})
    assert doc["family"] == "rest" and doc["binding"] == {"root": "/api"}
    ops = doc["operations"]
    assert "socket" not in ops
    assert ops["list_items"]["binding"] == {"method": "GET", "path": "/v1.1/items"}
    assert ops["list_items"]["result"] == {"type": "array", "items": {"type": "string"}}
    assert ops["update_item"]["binding"] == {"method": "PATCH", "path": "/v1.1/items/{itemId}", "body": "object"}
    assert ops["update_item"]["effect"] == "write" and ops["update_item"]["write"] == "patch"
    assert ops["update_item"]["params"]["required"] == ["itemId", "enabled"]
    assert ops["create_item"]["binding"]["body"] == "value" and ops["create_item"]["binding"]["body_field"] == "body"
    assert ops["create_item"]["errors"] == {400: {"description": "Bad Request", "kind": "invalid_argument"}}  # 401 is dropped
    assert ops["search"]["binding"] == {"method": "GET", "path": "/v1.1/search", "query": ["q"]}
    assert any(k == "versioned-paths" for k, _ in notes.items)
    generates(doc)


def test_main_routes_new_families_and_never_overwrites_existing_files(tmp_path: Path) -> None:
    import yaml

    src = tmp_path / "src" / "network-video"
    src.mkdir(parents=True)
    (src / "demo-svc.yaml").write_text(yaml.safe_dump(v1_service(["soap", "other"], json_op("get_x", "ax:GetX"))))
    out = tmp_path / "out"
    assert m.main(["--src", str(tmp_path / "src"), "--out", str(out)]) == 0
    written = (out / "network-video" / "demo-svc.yaml").read_text()
    assert "family: service_json" in written
    (out / "network-video" / "demo-svc.yaml").write_text("edited\n")
    assert m.main(["--src", str(tmp_path / "src"), "--out", str(out)]) == 0
    assert (out / "network-video" / "demo-svc.yaml").read_text() == "edited\n"
    assert m.main(["--src", str(tmp_path / "src"), "--out", str(out), "--overwrite"]) == 0
    assert "family: service_json" in (out / "network-video" / "demo-svc.yaml").read_text()
