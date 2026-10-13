"""Contract harness: multipart uploads (cgi and JSON-RPC) with documented file names and envelope parts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))  # tests/ -> the contract package

from test_bindings import base_spec, load_module
from test_upload_bindings import jsonrpc_spec

from contract._runner import run_example


def run(spec: dict[str, Any], op_id: str, example: dict[str, Any]) -> None:
    module = load_module(spec)
    run_example(spec, module.OPS, op_id, example)


CGI = base_spec(
    "cgi",
    {"path": "/axis-cgi/clip.cgi"},
    {
        "upload_clip": {
            "summary": "Upload a clip.", "effect": "write",
            "binding": {"method": "POST", "encoding": "multipart", "url_query": {"action": "upload"}, "reply": "text_ok"},
            "params": {"type": "object", "required": ["clip"], "properties": {
                "clip": {"type": "string", "format": "binary", "x-upload": {"part": "file", "content_type": "audio/basic"}},
            }},
        },
    },
)  # fmt: skip


def clip_example(**part: Any) -> dict[str, Any]:
    return {
        "request": {"query": {"action": "upload"}, "parts": [{"name": "file", "content": "RIFF", **part}]},
        "response": {"text": "OK"},
    }


def test_documented_file_name_other_than_the_part_name_is_sent() -> None:
    run(CGI, "upload_clip", clip_example(filename="clip.wav", content_type="audio/basic"))


def test_without_a_documented_file_name_the_part_name_is_the_default() -> None:
    run(CGI, "upload_clip", clip_example(filename="file"))


def test_wrong_documented_content_type_still_fails() -> None:
    with pytest.raises(AssertionError, match="content type"):
        run(CGI, "upload_clip", clip_example(filename="clip.wav", content_type="audio/x-wav"))


def test_jsonrpc_multipart_example_checks_envelope_and_file() -> None:
    spec = jsonrpc_spec()
    example = {
        "request": {"params": {"scaleToResolution": True}, "parts": [{"name": "image", "filename": "a.bmp", "content_type": "image/bmp", "content": "BM"}]},
        "response": {"data": {"path": "/etc/overlays/a.ovl"}},
    }
    run(spec, "upload_overlay", example)


def test_jsonrpc_multipart_example_without_parts_gets_filler() -> None:
    run(jsonrpc_spec(), "upload_overlay", {"request": {"params": {}}, "response": {"error": {"code": 1000, "message": "bad"}}})


def test_jsonrpc_multipart_envelope_params_are_compared() -> None:
    spec = jsonrpc_spec()
    module = load_module(spec)
    example = {"request": {"params": {"scaleToResolution": True}}, "response": {"data": {"path": "x"}}}
    # The model gets what the example says; a different expectation must fail.
    run_example(spec, module.OPS, "upload_overlay", example)
    wrong = {**example, "request": {"params": {"scaleToResolution": True}, "parts": [{"name": "other"}]}}
    with pytest.raises(AssertionError, match="parts"):
        run_example(spec, module.OPS, "upload_overlay", wrong)


def test_jsonrpc_upload_without_envelope_part() -> None:
    spec = jsonrpc_spec()
    module = load_module(spec)
    run_example(spec, module.OPS, "upload_radar", {"request": {"params": {}}, "response": {"data": {}}})
