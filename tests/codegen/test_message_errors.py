"""Message-keyed errors in the spec error model."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from test_bindings import base_spec, build, device, generate, load_module

from codegen.loader import SpecError, validate
from ax_devil_device_api.errors import ApiAccessDenied, ApiError

ERRORS = {
    "bad_name": {"description": "Bad name", "kind": "invalid_argument", "message": "account user name."},
    "malformed": {"description": "Malformed", "message_prefix": "malformed action operation,"},
    "no_admin": {"description": "No admin", "kind": "access_denied", "message": "initial admin user must be created first."},
}


def spec_with(errors: dict[str, Any]) -> dict[str, Any]:
    return base_spec(
        "cgi", {"path": "/axis-cgi/demo.cgi"},
        {"go": {"summary": "Go.", "effect": "read", "binding": {"reply": "text"}, "result": {"type": "string"}}},
        errors=errors,
    )


def test_message_errors_are_rendered() -> None:
    code = generate(spec_with(ERRORS))
    assert '"bad_name": ErrorCode("Bad name", "invalid_argument", message="account user name.")' in code
    assert '"malformed": ErrorCode("Malformed", message_prefix="malformed action operation,")' in code


def test_message_and_prefix_together_are_rejected() -> None:
    with pytest.raises(SpecError, match="both message and message_prefix"):
        build(spec_with({"x": {"description": "d", "message": "a", "message_prefix": "b"}}))


def test_empty_message_is_rejected_by_the_schema() -> None:
    assert validate(spec_with({"x": {"description": "d", "message": ""}}))


def test_message_errors_end_to_end() -> None:
    module = load_module(spec_with(ERRORS))
    reply = ["Error: account user name."]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=reply[0])

    with device(handler) as dev:
        api = dev.api(module.DemoApi)
        with pytest.raises(ApiError) as caught:
            api.go()
        assert caught.value.kind == "invalid_argument" and caught.value.code is None
        reply[0] = "Error: malformed action operation, add."
        with pytest.raises(ApiError) as caught:
            api.go()
        assert caught.value.description == "Malformed"
        reply[0] = "Error: initial admin user must be created first."
        with pytest.raises(ApiAccessDenied):
            api.go()
