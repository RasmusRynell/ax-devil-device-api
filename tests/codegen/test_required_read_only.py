"""Required read-only fields: enforced on responses, left out of requests."""

from __future__ import annotations

import httpx
import pytest
from test_bindings import base_spec, device, generate, load_module

from ax_devil_device_api.errors import ResponseFormatError

SPEC = base_spec(
    "rest", {"root": "/api"},
    {"create": {
        "summary": "Create.", "effect": "write", "write": "create",
        "binding": {"method": "POST", "path": "/things", "body": "value", "body_field": "body"},
        "params": {"type": "object", "required": ["body"], "properties": {"body": {"$ref": "#/types/Thing"}}},
        "result": {"$ref": "#/types/Thing"},
    }},
    types={"Thing": {"type": "object", "required": ["name", "id"], "x-read-only": ["id"],
                     "properties": {"name": {"type": "string"}, "id": {"type": "string", "minLength": 2}}}},
)  # fmt: skip


def test_rendering() -> None:
    code = generate(SPEC)
    assert '__response_required__: ClassVar[frozenset[str]] = frozenset({"id"})' in code
    assert "id: str = Field(default_factory=not_sent" in code


def test_request_model_needs_no_id_and_never_sends_it() -> None:
    module = load_module(SPEC)
    thing = module.Thing(name="a")
    assert thing.to_wire() == {"name": "a"}
    bodies: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(request.content)
        return httpx.Response(200, json={"name": "a", "id": "t1"})

    with device(handler) as dev:
        result = dev.api(module.DemoApi).create(body=thing)
    assert result.id == "t1" and bodies == [b'{"name":"a"}']


def test_response_without_the_field_is_rejected() -> None:
    module = load_module(SPEC)
    with device(lambda r: httpx.Response(200, json={"name": "a"})) as dev:
        with pytest.raises(ResponseFormatError, match="id"):
            dev.api(module.DemoApi).create(body=module.Thing(name="a"))
