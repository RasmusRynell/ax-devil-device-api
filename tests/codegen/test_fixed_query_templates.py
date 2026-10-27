"""Fixed cgi ``query`` values with ``{n}`` placeholders, filled from the index argument."""

from __future__ import annotations

import httpx
import pytest
from test_bindings import base_spec, build, device, generate, load_module

from codegen.loader import SpecError


def spec(query: dict[str, str], properties: dict | None = None, required: list[str] | None = None, url_query: dict | None = None) -> dict:
    binding = {"query": query, "reply": {"text_kv": {"strip_prefix": "root.Image.I{n}.RateControl."}}}
    if url_query:
        binding["url_query"] = url_query
    return base_spec(
        "cgi", {"path": "/axis-cgi/param.cgi"},
        {"list": {
            "summary": "List.", "effect": "read", "binding": binding,
            "params": {"type": "object", "required": ["n"] if required is None else required,
                       "properties": properties or {"n": {"type": "integer", "minimum": 0}}},
            "result": {"$ref": "#/types/RateControl"},
        }},
        types={"RateControl": {"type": "object", "properties": {"Mode": {"type": "string"}, "MaxBitrate": {"type": "integer"}}}},
    )  # fmt: skip


def test_renders_the_template_unchanged() -> None:
    assert 'fixed_query=(("action", "list"), ("group", "Image.I{n}.RateControl"))' in generate(spec({"action": "list", "group": "Image.I{n}.RateControl"}))


def test_group_and_prefix_are_filled_from_the_index_and_the_read_is_typed() -> None:
    module = load_module(spec({"action": "list", "group": "Image.I{n}.RateControl"}, url_query={"v": "n{n}"}))
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, text="root.Image.I2.RateControl.Mode=mbr\nroot.Image.I2.RateControl.MaxBitrate=1000\n")

    with device(handler) as dev:
        result = dev.api(module.DemoApi).list(2)
    assert dict(seen[0].url.params) == {"v": "n2", "action": "list", "group": "Image.I2.RateControl"}
    assert (result.mode, result.max_bitrate) == ("mbr", 1000)


def test_the_index_is_not_sent_as_an_argument() -> None:
    module = load_module(spec({"group": "Image.I{n}.RateControl"}))
    seen: list[httpx.Request] = []
    with device(lambda r: (seen.append(r), httpx.Response(200, text=""))[1]) as dev:
        dev.api(module.DemoApi).list(0)
    assert "n" not in seen[0].url.params


def test_a_placeholder_without_an_argument_is_rejected() -> None:
    with pytest.raises(SpecError, match=r"placeholder \{n\} is not an argument"):
        build(spec({"group": "Image.I{n}.RateControl"}, properties={"m": {"type": "integer"}}, required=["m"]))


def test_the_index_argument_must_be_required() -> None:
    with pytest.raises(SpecError, match="must be required"):
        build(spec({"group": "Image.I{n}.RateControl"}, required=[]))
