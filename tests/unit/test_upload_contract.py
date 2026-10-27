"""Contract-harness support for raw bodies, multipart uploads, mixed placement and bare keys."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

from ax_devil_device_api._http.upload import UploadSource, UploadSpec
from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation
from ax_devil_device_api._protocols.cgi import CgiArg, CgiBinding
from ax_devil_device_api.device import Device


def _load():
    path = Path(__file__).resolve().parents[1] / "contract" / "_harness.py"
    spec = importlib.util.spec_from_file_location("contract_harness_up", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


h = _load()
INFO = ApiInfo(id="t", name="T", family=Family.CGI)


class Clip(Model):
    clip: UploadSource
    name: str | None = None
    note: str | None = None


class Raw(Model):
    data: UploadSource
    name: str | None = None


def multipart_op() -> Operation[Any]:
    binding = CgiBinding(
        "/up.cgi", "POST", url_query=(("action", "upload"),), encoding="multipart",
        args=(CgiArg("name", place="query"), CgiArg("note", place="form")),
        uploads=(UploadSpec("clip", part="file", filename="clip.wav", content_type="audio/basic"),),
    )
    return Operation(INFO, "upload", binding, params=Clip)


def body_op(content_type: str = "text/xml") -> Operation[Any]:
    binding = CgiBinding(
        "/put.cgi", "POST", fixed_query=(("live-sum.json", None),), encoding="body", content_type=content_type,
        args=(CgiArg("name"),), body_field="data", uploads=(UploadSpec("data"),),
    )
    return Operation(INFO, "put", binding, params=Raw)


def run(op: Operation[Any], request: dict) -> Any:
    model, expected = h.build_cgi(op, request)
    fake = h.Fake(lambda sent: httpx.Response(200, text="OK"))
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(fake)) as dev:
        dev.invoke(op, model)
    (sent,) = fake.calls
    assert {**sent.query, **(sent.form or {})} == expected
    h.check_sent_body(op, request, sent)
    return sent


def test_multipart_parts_and_mixed_placement() -> None:
    request = {
        "query": {"name": "n"}, "form": {"note": "hi"},
        "parts": [{"name": "file", "filename": "clip.wav", "content_type": "audio/basic", "content": "RIFF"}],
    }
    sent = run(multipart_op(), request)
    assert [p.name for p in sent.parts if p.is_file] == ["file"] and sent.form == {"note": "hi"}
    assert sent.query == {"action": "upload", "name": "n"}


@pytest.mark.parametrize(
    "change",
    [{"filename": "other.wav"}, {"content_type": "audio/x"}, {"content": "RIFX"}, {"name": "zip"}],
)
def test_multipart_mismatch_is_detected(change: dict) -> None:
    part = {"name": "file", "filename": "clip.wav", "content_type": "audio/basic", "content": "RIFF"}
    request = {"query": {"name": "n"}, "parts": [part]}
    model, _ = h.build_cgi(multipart_op(), request)
    fake = h.Fake(lambda sent: httpx.Response(200, text="OK"))
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(fake)) as dev:
        dev.invoke(multipart_op(), model)
    with pytest.raises(AssertionError):
        h.check_sent_body(multipart_op(), {**request, "parts": [{**part, **change}]}, fake.calls[0])


def test_size_only_part_is_filled_and_measured() -> None:
    sent = run(multipart_op(), {"parts": [{"name": "file", "size": 1000}]})
    assert len(sent.parts[0].content) == 1000


def test_xml_body_compares_structurally_and_bare_key_stays_bare() -> None:
    body = '<a  x="1"><b>t</b></a>'
    sent = run(body_op(), {"query": {"name": "n", "live-sum.json": None}, "body": body, "content_type": "text/xml"})
    assert sent.rawquery.startswith("live-sum.json&") and sent.content_type == "text/xml"
    model, _ = h.build_cgi(body_op(), {"body": "<a/>"})
    fake = h.Fake(lambda sent: httpx.Response(200, text="OK"))
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(fake)) as dev:
        dev.invoke(body_op(), model)
    with pytest.raises(AssertionError, match="XML"):
        h.check_sent_body(body_op(), {"body": "<a><c/></a>"}, fake.calls[0])
    h.check_sent_body(body_op(), {"body": "<a />"}, fake.calls[0])


def test_json_body_and_wrong_content_type() -> None:
    run(body_op("application/json"), {"body": {"k": [1, 2]}})
    model, _ = h.build_cgi(body_op("application/json"), {"body": {"k": 1}})
    fake = h.Fake(lambda sent: httpx.Response(200, text="OK"))
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(fake)) as dev:
        dev.invoke(body_op("application/json"), model)
    with pytest.raises(AssertionError, match="JSON"):
        h.check_sent_body(body_op("application/json"), {"body": {"k": 2}}, fake.calls[0])
    with pytest.raises(AssertionError, match="content type"):
        h.check_sent_body(body_op("application/json"), {"body": {"k": 1}, "content_type": "text/plain"}, fake.calls[0])


def test_binary_body_is_compared_as_bytes() -> None:
    run(body_op("application/octet-stream"), {"body": "raw text"})
