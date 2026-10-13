"""``x-in: content_type``: the Content-Type of a raw body (``encoding: body``) chosen per call."""

from __future__ import annotations

import io
from typing import Any

import pytest
from test_bindings import base_spec, build
from test_upload_bindings import run

from codegen.loader import SpecError

SPEC = base_spec(
    "cgi",
    {"path": "/axis-cgi/audio/transmit.cgi"},
    {
        "transmit": {
            "summary": "Transmit audio.", "effect": "action",
            "binding": {"method": "POST", "encoding": "body", "reply": "text_ok"},
            "params": {"type": "object", "required": ["audio"], "properties": {
                "audio": {"type": "string", "format": "binary", "x-in": "body", "x-upload": {"content_type": "audio/basic"}},
                "content_type": {"type": "string", "enum": ["audio/basic", "audio/G726-32"], "x-in": "content_type"},
                "audiodeviceid": {"type": "string"},
            }},
        },
        "send_text": {
            "summary": "Send text.", "effect": "write",
            "binding": {"method": "POST", "encoding": "body", "content_type": "text/plain", "reply": "text_ok"},
            "params": {"type": "object", "required": ["body"], "properties": {
                "body": {"type": "string", "x-in": "body"},
                "mime": {"type": "string", "x-in": "content_type"},
            }},
        },
    },
)  # fmt: skip


def types(call: Any) -> list[tuple[str, bytes, list[tuple[str, str]]]]:
    (request,) = run(SPEC, call)
    return [(request.headers["content-type"], request.read(), request.url.params.multi_items())]


def test_default_is_the_upload_content_type() -> None:
    assert types(lambda api: api.transmit(audio=b"AU")) == [("audio/basic", b"AU", [])]


def test_the_argument_sets_the_content_type_and_is_not_sent_as_a_query_argument() -> None:
    result = types(lambda api: api.transmit(audio=b"AU", content_type="audio/G726-32", audiodeviceid="d1"))
    assert result == [("audio/G726-32", b"AU", [("audiodeviceid", "d1")])]


def test_the_argument_wins_over_an_upload_content_type() -> None:
    from ax_devil_device_api._http.upload import Upload

    def upload() -> Upload:
        return Upload(io.BytesIO(b"AU"), 2, content_type="audio/opus")  # a stream is read once

    assert types(lambda api: api.transmit(audio=upload()))[0][0] == "audio/opus"
    assert types(lambda api: api.transmit(audio=upload(), content_type="audio/basic"))[0][0] == "audio/basic"


def test_the_argument_wins_over_the_binding_content_type() -> None:
    assert types(lambda api: api.send_text(body="hi"))[0][0] == "text/plain"
    assert types(lambda api: api.send_text(body="hi", mime="text/csv"))[0][0] == "text/csv"


def test_values_outside_the_enum_are_rejected() -> None:
    with pytest.raises(ValueError):
        run(SPEC, lambda api: api.transmit(audio=b"AU", content_type="audio/x-unknown"))


def spec_with(binding: dict[str, Any], properties: dict[str, Any]) -> dict[str, Any]:
    return base_spec("cgi", {"path": "/x.cgi"}, {"g": {"summary": "x", "binding": binding, "params": {"type": "object", "properties": properties}}})


def test_needs_the_body_encoding() -> None:
    with pytest.raises(SpecError, match="x-in: content_type, which needs binding.encoding body"):
        build(spec_with({"method": "POST", "encoding": "form"}, {"c": {"type": "string", "x-in": "content_type"}}))


def test_at_most_one_and_strings_only() -> None:
    body = {"b": {"type": "string", "x-in": "body"}}
    binding = {"method": "POST", "encoding": "body", "content_type": "text/plain"}
    with pytest.raises(SpecError, match="at most one"):
        build(spec_with(binding, {**body, "c": {"type": "string", "x-in": "content_type"}, "d": {"type": "string", "x-in": "content_type"}}))
    with pytest.raises(SpecError, match="must be a string"):
        build(spec_with(binding, {**body, "c": {"type": "integer", "x-in": "content_type"}}))
