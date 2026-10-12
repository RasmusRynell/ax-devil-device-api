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
