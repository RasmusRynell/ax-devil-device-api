"""cgi path arguments, templated names, raw bodies, multipart uploads, mixed placement and bare keys.

Each feature is generated from a fixture spec and called through ``Device`` over ``httpx.MockTransport``.
"""

from __future__ import annotations

import io
import json
from email.parser import BytesParser
from email.policy import HTTP
from pathlib import Path
from typing import Any

import httpx
import pytest
from test_bindings import base_spec, build, device, generate, load_module

from ax_devil_device_api.device import Device
from codegen.loader import SpecError, validate


def parts(request: httpx.Request) -> list[tuple[str | None, str | None, str, bytes]]:
    message = BytesParser(policy=HTTP).parsebytes(b"Content-Type: " + request.headers["content-type"].encode() + b"\r\n\r\n" + request.content)
    return [
        (p.get_param("name", header="content-disposition"), p.get_filename(), p.get_content_type(), p.get_payload(decode=True))  # type: ignore[misc]
        for p in message.iter_parts()
    ]


def run(spec: dict[str, Any], call: Any, reply: httpx.Response | None = None, *, anonymous: bool = False) -> list[httpx.Request]:
    module = load_module(spec)
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return reply or httpx.Response(200, text="OK")

    dev = Device("cam", transport=httpx.MockTransport(handler)) if anonymous else device(handler)
    with dev:
        call(dev.api(module.DemoApi))
    return seen


# -- path arguments and templated names ------------------------------------------------

CGI_NAMES = base_spec(
    "cgi",
    {"path": "/axis-cgi/param.cgi"},
    {
        "get_list": {
            "summary": "Get a list.", "effect": "read",
            "binding": {"path": "/local/app/{list_name}.cgi", "reply": "text"},
            "params": {"type": "object", "required": ["list_name"], "properties": {"list_name": {"type": "string"}}},
            "result": {"type": "string"},
        },
        "get_image": {
            "summary": "Get one image source.", "effect": "read",
            "binding": {"query": {"action": "list"}, "reply": {"text_kv": {"strip_prefix": "root.Image.I{n}."}}},
            "params": {"type": "object", "required": ["n"], "properties": {"n": {"type": "integer"}}},
            "result": {"$ref": "#/types/Image"},
        },
        "get_image_full": {
            "summary": "Get one image source with full names.", "effect": "read",
            "binding": {"query": {"action": "list"}, "reply": {"text_kv": {"strip_prefix": "root."}}},
            "params": {"type": "object", "required": ["n"], "properties": {"n": {"type": "integer"}}},
            "result": {"$ref": "#/types/FullImage"},
        },
        "set_image": {
            "summary": "Rename an image source.", "effect": "write",
            "binding": {"query": {"action": "update"}, "reply": "text_ok"},
            "params": {"type": "object", "required": ["n", "Image.I{n}.Name"], "properties": {
                "n": {"type": "integer"},
                "Image.I{n}.Name": {"type": "string", "x-python-name": "name"},
                "Image.I{n}.Rotation": {"type": "integer", "x-python-name": "rotation"},
            }},
        },
    },
    types={
        "Image": {"type": "object", "properties": {"Name": {"type": "string"}}},
        "FullImage": {"type": "object", "properties": {"Image.I{n}.Name": {"type": "string", "x-python-name": "name"}}},
    },
)  # fmt: skip


def test_cgi_path_argument_is_positional_quoted_and_not_sent() -> None:
    (request,) = run(CGI_NAMES, lambda api: api.get_list("block list"))
    assert request.url.raw_path == b"/local/app/block%20list.cgi"
    with pytest.raises(ValueError, match="not a valid path"):
        run(base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "binding": {"path": "/a/{p}/b"}, "params": CGI_NAMES["operations"]["get_list"]["params"] | {"properties": {"p": {"type": "string"}}, "required": ["p"]}}}), lambda api: api.g(".."))


def test_cgi_templated_argument_names_are_filled_from_the_index() -> None:
    (request,) = run(CGI_NAMES, lambda api: api.set_image(2, name="Front", rotation=90))
    assert request.url.params.multi_items() == [("action", "update"), ("Image.I2.Name", "Front"), ("Image.I2.Rotation", "90")]
    assert "Image.I{n}" in generate(CGI_NAMES)


def test_cgi_templated_reply_prefix_and_names() -> None:
    reply = httpx.Response(200, text="root.Image.I3.Name=Lobby\n")
    module = load_module(CGI_NAMES)
    with device(lambda request: reply) as dev:
        api = dev.api(module.DemoApi)
        assert api.get_image(3).name == "Lobby"
        assert api.get_image_full(3).name == "Lobby"


def test_templates_must_name_required_arguments() -> None:
    bad = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "params": {"type": "object", "properties": {"A{m}": {"type": "string", "x-python-name": "a"}}}}})
    with pytest.raises(SpecError, match="not an argument"):
        build(bad)
    optional = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "params": {"type": "object", "properties": {"m": {"type": "integer"}, "A{m}": {"type": "string", "x-python-name": "a"}}}}})
    with pytest.raises(SpecError, match="must be required"):
        build(optional)


# -- raw bodies -------------------------------------------------------------------------

BODY_SPEC = base_spec(
    "cgi",
    {"path": "/local/app/config.cgi"},
    {
        "set_xml": {
            "summary": "Send XML.", "effect": "write",
            "binding": {"method": "POST", "encoding": "body", "content_type": "application/xml", "query": {"action": "set"}, "reply": "text_ok"},
            "params": {"type": "object", "required": ["config"], "properties": {"config": {"type": "string", "x-in": "body"}, "dry_run": {"type": "boolean"}}},
        },
        "set_json": {
            "summary": "Send JSON.", "effect": "write",
            "binding": {"method": "POST", "encoding": "body", "content_type": "application/json", "reply": "text_ok"},
            "params": {"type": "object", "required": ["settings"], "properties": {"settings": {"type": "object", "properties": {"angle": {"type": "integer"}}, "x-name": "Settings", "x-in": "body"}}},
        },
        "upload_driver": {
            "summary": "Upload a driver.", "effect": "write",
            "binding": {"method": "POST", "encoding": "body", "content_type": "application/octet-stream", "reply": "text_ok"},
            "params": {"type": "object", "required": ["driver"], "properties": {"driver": {"type": "string", "format": "binary", "x-in": "body", "x-upload": True}}},
        },
    },
)  # fmt: skip


def test_raw_body_xml_with_query_arguments() -> None:
    (request,) = run(BODY_SPEC, lambda api: api.set_xml(config="<a>é</a>", dry_run=True))
    assert request.method == "POST" and request.headers["content-type"] == "application/xml"
    assert request.content == "<a>é</a>".encode() and request.url.params.multi_items() == [("action", "set"), ("dry_run", "true")]


def test_raw_body_json_from_a_model() -> None:
    module = load_module(BODY_SPEC)
    (request,) = run(BODY_SPEC, lambda api: api.set_json(settings={"angle": 5}))
    assert json.loads(request.content) == {"angle": 5} and request.headers["content-type"] == "application/json"
    assert module.Settings(angle=1).angle == 1


def test_raw_body_upload_streams_with_content_length(tmp_path: Path) -> None:
    from ax_devil_device_api._http.upload import Upload

    data = bytes(range(256)) * 600
    path = tmp_path / "driver.bin"
    path.write_bytes(data)
    for source in (data, path, Upload(io.BytesIO(data), len(data))):
        (request,) = run(BODY_SPEC, lambda api, source=source: api.upload_driver(driver=source), anonymous=True)
        assert request.read() == data and request.headers["content-length"] == str(len(data))
        assert request.headers["content-type"] == "application/octet-stream"


def test_large_uploads_are_streamed_and_small_ones_replayable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from ax_devil_device_api._http import upload

    path = tmp_path / "big.bin"
    path.write_bytes(b"x" * 1000)
    seen: list[bool] = []
    module = load_module(BODY_SPEC)
    op = module.OPS.upload_driver
    from ax_devil_device_api._protocols.cgi import _build

    for limit in (10, 10_000):
        monkeypatch.setattr(upload, "INLINE_LIMIT", limit)
        from ax_devil_device_api._http.types import resolve_deferred

        request = resolve_deferred(_build(op, module.UploadDriverRequest(driver=path), {}))
        seen.append(request.replayable)
        if limit == 10:
            assert b"".join(request.body.content) == b"x" * 1000 and request.body.size == 1000  # type: ignore[union-attr]
    assert seen == [False, True]


def test_raw_body_needs_exactly_one_body_argument() -> None:
    spec = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "binding": {"method": "POST", "encoding": "body", "content_type": "text/plain"}, "params": {"type": "object", "properties": {"a": {"type": "string"}}}}})
    with pytest.raises(SpecError, match="exactly one argument with x-in: body"):
        build(spec)


# -- multipart uploads ------------------------------------------------------------------

MULTIPART_SPEC = base_spec(
    "cgi",
    {"path": "/axis-cgi/mediaclip.cgi"},
    {
        "upload_clip": {
            "summary": "Upload a clip.", "effect": "write",
            "binding": {"method": "POST", "encoding": "multipart", "url_query": {"action": "upload", "media": "audio"}, "reply": "text_ok"},
            "params": {"type": "object", "required": ["clip"], "properties": {
                "clip": {"type": "string", "format": "binary", "x-upload": {"part": "file", "content_type": "audio/basic", "filename": "clip.au"}},
                "name": {"type": "string", "x-in": "query"},
                "note": {"type": "string"},
            }},
        },
    },
)  # fmt: skip


def test_multipart_upload_of_bytes_path_and_stream(tmp_path: Path) -> None:
    from ax_devil_device_api._http.upload import Upload

    data = b"\x00\x01clip\r\n--"
    path = tmp_path / "ding.wav"
    path.write_bytes(data)
    cases = [(data, "clip.au", "audio/basic"), (path, "ding.wav", "audio/basic"),
             (Upload(io.BytesIO(data), len(data), "x.au", "audio/x-au"), "x.au", "audio/x-au")]  # fmt: skip
    for source, filename, content_type in cases:
        (request,) = run(MULTIPART_SPEC, lambda api, source=source: api.upload_clip(clip=source, name="Ding", note="hi"))
        assert request.url.params.multi_items() == [("action", "upload"), ("media", "audio"), ("name", "Ding")]
        assert parts(request) == [("note", None, "text/plain", b"hi"), ("file", filename, content_type, data)]
        assert request.headers["content-length"] == str(len(request.content))


def test_upload_rejects_text_and_short_streams() -> None:
    from pydantic import ValidationError

    from ax_devil_device_api._http.upload import Upload

    with pytest.raises(ValidationError, match="ambiguous"):
        run(MULTIPART_SPEC, lambda api: api.upload_clip(clip="/tmp/file.au"))
    with pytest.raises(ValueError, match="before its declared size"):
        run(MULTIPART_SPEC, lambda api: api.upload_clip(clip=Upload(io.BytesIO(b"ab"), 5)))


def test_upload_argument_stays_out_of_reprs() -> None:
    module = load_module(MULTIPART_SPEC)
    assert "secret" not in repr(module.UploadClipRequest(clip=b"secret"))


def test_multipart_checks() -> None:
    no_upload = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "binding": {"method": "POST", "encoding": "multipart"}, "params": {"type": "object", "properties": {"a": {"type": "string"}}}}})
    with pytest.raises(SpecError, match="at least one x-upload"):
        build(no_upload)
    get = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "binding": {"encoding": "multipart"}, "params": {"type": "object", "properties": {"f": {"type": "string", "x-upload": True}}}}})
    with pytest.raises(SpecError, match="method POST"):
        build(get)
    stray = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "params": {"type": "object", "properties": {"f": {"type": "string", "x-upload": True}}}}})
    with pytest.raises(SpecError, match="encoding multipart"):
        build(stray)


# -- JSON-RPC multipart -----------------------------------------------------------------


def jsonrpc_spec() -> dict[str, Any]:
    params = {"type": "object", "required": ["image"], "properties": {
        "scaleToResolution": {"type": "boolean"},
        "image": {"type": "string", "format": "binary", "x-upload": {"part": "image", "content_type": "image/bmp"}},
    }}  # fmt: skip
    return base_spec(
        "jsonrpc",
        {"path": "/axis-cgi/manage.cgi", "major": 1, "versions": ["1.0"], "negotiation": {"fixed": "1.0"}},
        {
            "upload_overlay": {
                "summary": "Upload an overlay image.", "effect": "write",
                "binding": {"method": "uploadOverlayImage", "path": "/axis-cgi/uploadoverlayimage.cgi", "multipart": {"json_part": "json"}},
                "params": params, "result": {"type": "object", "properties": {"path": {"type": "string"}}},
            },
            "upload_radar": {
                "summary": "Upload a radar map.", "effect": "write",
                "binding": {"method": "uploadRadarImage", "path": "/axis-cgi/radar/uploadradarimage.cgi", "multipart": {}},
                "params": {"type": "object", "required": ["image"], "properties": {"image": params["properties"]["image"]}},
            },
        },
    )


def test_jsonrpc_multipart_envelope_part_and_file_part() -> None:
    reply = httpx.Response(200, json={"apiVersion": "1.0", "method": "uploadOverlayImage", "data": {"path": "/etc/overlays/a.ovl"}})
    module = load_module(jsonrpc_spec())
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return reply

    with device(handler) as dev:
        result = dev.api(module.DemoApi).upload_overlay(image=b"BM..", scale_to_resolution=True)
    assert result.path == "/etc/overlays/a.ovl"
    (request,) = seen
    assert request.url.path == "/axis-cgi/uploadoverlayimage.cgi"
    (json_part, image_part) = parts(request)
    assert json_part[0] == "json" and json_part[1] is None and json_part[2] == "application/json"
    assert json.loads(json_part[3]) == {"apiVersion": "1.0", "method": "uploadOverlayImage", "params": {"scaleToResolution": True}}
    assert image_part == ("image", "image", "image/bmp", b"BM..")


def test_jsonrpc_multipart_without_json_part() -> None:
    reply = httpx.Response(200, json={"apiVersion": "1.0", "method": "uploadRadarImage", "data": {}})
    module = load_module(jsonrpc_spec())
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return reply

    with device(handler) as dev:
        dev.api(module.DemoApi).upload_radar(image=b"\x89PNG")
    assert parts(seen[0]) == [("image", "image", "image/bmp", b"\x89PNG")]


def test_jsonrpc_upload_needs_multipart_binding() -> None:
    spec = jsonrpc_spec()
    del spec["operations"]["upload_radar"]["binding"]["multipart"]
    with pytest.raises(SpecError, match="binding.multipart"):
        build(spec)


# -- mixed placement and bare keys -------------------------------------------------------

MIXED_SPEC = base_spec(
    "cgi",
    {"path": "/local/tvpc/.apioperator"},
    {
        "set_params": {
            "summary": "Set parameters.", "effect": "write",
            "binding": {"method": "POST", "encoding": "form", "url_query": {"setparams": None}, "query": {"v": "1"}, "reply": "text_ok"},
            "params": {"type": "object", "properties": {
                "date": {"type": "string", "x-in": "query"},
                "values": {"type": "object", "additionalProperties": {"type": "string"}},
            }},
        },
        "live": {
            "summary": "Live data.", "effect": "read",
            "binding": {"query": {"live-sum.json": None}, "reply": "json"},
            "params": {"type": "object", "properties": {"export-cnt": {"type": "boolean", "x-style": "flag", "x-python-name": "export"}, "date": {"type": "string"}}},
            "result": {"type": "object", "additionalProperties": True},
        },
    },
)  # fmt: skip


def test_mixed_query_and_form_arguments() -> None:
    (request,) = run(MIXED_SPEC, lambda api: api.set_params(date="2024", values={"Counter.Height": "280"}))
    assert str(request.url).endswith("/local/tvpc/.apioperator?setparams&date=2024")
    assert request.headers["content-type"] == "application/x-www-form-urlencoded"
    assert request.content == b"v=1&Counter.Height=280"


def test_bare_query_keys_are_sent_without_equals_sign() -> None:
    (request,) = run(MIXED_SPEC, lambda api: api.live(export=True, date="20240101"), httpx.Response(200, json={}))
    assert request.url.query == b"live-sum.json&export-cnt&date=20240101"
    (request,) = run(MIXED_SPEC, lambda api: api.live(export=False), httpx.Response(200, json={}))
    assert request.url.query == b"live-sum.json"


def test_bare_keys_cannot_go_in_a_body() -> None:
    spec = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "binding": {"method": "POST", "encoding": "form", "query": {"k": None}}}})
    with pytest.raises(SpecError, match="url_query"):
        build(spec)


def test_x_in_must_match_the_encoding() -> None:
    spec = base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "params": {"type": "object", "properties": {"a": {"type": "string", "x-in": "form"}}}}})
    with pytest.raises(SpecError, match="x-in: form"):
        build(spec)


# -- text_lines and generated typing ----------------------------------------------------


def test_text_lines_reply() -> None:
    spec = base_spec("cgi", {"path": "/x.cgi"}, {"presets": {
        "summary": "List presets.", "effect": "read", "binding": {"reply": {"text_lines": {"skip": 1}}},
        "result": {"type": "array", "items": {"type": "string"}},
    }})  # fmt: skip
    module = load_module(spec)
    with device(lambda request: httpx.Response(200, text="Preset Positions for camera 1\npresetposno1=Home\n\npresetposno2=Door\n")) as dev:
        assert dev.api(module.DemoApi).presets() == ["presetposno1=Home", "presetposno2=Door"]
    with device(lambda request: httpx.Response(200, text="Error: 2")) as dev:
        from ax_devil_device_api.errors import ApiError

        with pytest.raises(ApiError):
            dev.api(module.DemoApi).presets()


def test_optional_mapping_arguments_use_a_typed_args_dict() -> None:
    spec = base_spec("jsonrpc", {"path": "/x.cgi", "major": 1, "negotiation": {"fixed": "1.0"}}, {"set_x": {
        "summary": "x", "effect": "write", "binding": {"method": "setX"},
        "params": {"type": "object", "required": ["force"], "properties": {"force": {"type": "boolean"}, "parameters": {"type": "object", "additionalProperties": {"type": "string"}}}},
    }})  # fmt: skip
    assert "args: dict[str, Any] = " in generate(spec)


def test_schema_accepts_the_new_keys() -> None:
    assert validate(MULTIPART_SPEC) == [] and validate(BODY_SPEC) == [] and validate(MIXED_SPEC) == []
