"""The public ``code`` of an API error: integers and documented text codes unchanged; an unrecognised text code is its
display form, and is not kept at all (a fixed marker in the text) for an operation that handles secret fields."""

from __future__ import annotations

import traceback
from typing import Any

import pytest

from ax_devil_device_api._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, api_error
from ax_devil_device_api._protocols.cgi import CgiBinding, Text
from ax_devil_device_api.errors import ApiError

NASTY = "password=hunter2 rtsp://u:p@h/x\r\nINJECTED-LINE"


class Secret(Model):
    __masked__ = frozenset({"key"})  # type: ignore[assignment]
    key: str | None = None


class Plain(Model):
    value: int | None = None


def _op(result: Any) -> Operation[Any]:
    errors = {"Documented/Code": ErrorCode("a documented text code", "invalid_argument"), 7: ErrorCode("seven", "not_found")}
    info = ApiInfo(id="t", name="T", family=Family.CGI, errors=errors)  # type: ignore[arg-type]
    return Operation(info, "op", CgiBinding("/x.cgi", reply=Text()), result=result)


def _shown(error: BaseException) -> str:
    try:
        raise error
    except BaseException as caught:  # noqa: BLE001
        return "\n".join([str(error), repr(error), repr(vars(error)), "".join(traceback.format_exception(caught))])


def _code(error: BaseException) -> Any:
    assert isinstance(error, ApiError)
    return error.code


@pytest.mark.parametrize("result", [Secret, Plain])
@pytest.mark.parametrize("status", [None, 200, 404, 500])
def test_integer_codes_and_documented_text_codes_are_unchanged(result: Any, status: int | None) -> None:
    op = _op(result)
    assert _code(api_error(op, 7, "m", http_status=status, details=None)) == 7
    assert _code(api_error(op, "Documented/Code", "m", http_status=status, details=None)) == "Documented/Code"
    assert _code(api_error(op, "42", "m", http_status=status, details=None)) == "42"


@pytest.mark.parametrize("status", [None, 200, 404, 500])
def test_an_unrecognised_text_code_of_a_secret_operation_is_not_kept(status: int | None) -> None:
    error = api_error(_op(Secret), NASTY, "m", http_status=status, details=None)
    assert _code(error) is None
    assert "error code omitted" in str(error)
    text = _shown(error)
    for forbidden in ("hunter2", "u:p@", "\r", "\nINJECTED-LINE"):
        assert forbidden not in text


@pytest.mark.parametrize("status", [None, 200, 404, 500])
def test_an_unrecognised_text_code_of_another_operation_is_its_display_form(status: int | None) -> None:
    error = api_error(_op(Plain), NASTY, "m", http_status=status, details=None)
    code = _code(error)
    assert isinstance(code, str) and "INJECTED-LINE" in code and "\\r\\n" in code
    text = _shown(error)
    for forbidden in ("hunter2", "u:p@", "\r", "\nINJECTED-LINE"):
        assert forbidden not in text


def test_matching_used_the_raw_code_before_it_was_shown() -> None:
    error = api_error(_op(Secret), "Documented/Code", "m", http_status=None, details=None)
    assert isinstance(error, ApiError) and error.kind == "invalid_argument" and error.description == "a documented text code"
