"""Request-side validation messages name the kind and the location of a rejected value, never the value itself."""

from __future__ import annotations

import io
import json
import traceback
from typing import Any, Literal

import pytest
from pydantic import ValidationError

from ax_devil_device_api import cli
from ax_devil_device_api._protocols.base import Model
from ax_devil_device_api.testing import MockCamera

SECRET = "hunter2-SENTINEL"


class Inner(Model):
    __masked__ = frozenset({"token"})  # type: ignore[assignment]
    token: str | None = None
    count: int | None = None


class Params(Model):
    __masked__ = frozenset({"password", "keys", "secrets", "nested"})  # type: ignore[assignment]
    password: str | None = None
    keys: list[str] | None = None
    secrets: dict[str, str] | None = None
    nested: Inner | None = None
    # not masked
    number: int | None = None
    ratio: float | None = None
    flag: bool | None = None
    names: list[int] | None = None
    table: dict[str, int] | None = None
    mode: Literal["a", "b"] | None = None
    label: str | None = None


HOSTILE: list[Any] = [
    {"secret": SECRET}, [SECRET], [[SECRET]], {"a": {"b": [SECRET]}}, (SECRET,), {SECRET}, SECRET, 1.5, True, b"x" + SECRET.encode(),
    [{"token": SECRET}], [1, SECRET],
]
# A mapping KEY or an unknown field NAME is part of the location the message reports (``secrets.user``, "unexpected
# field(s): pwd"): the caller chose it as a name, and naming it is how a typo is found. Values are never shown.
FIELDS = ["password", "keys", "secrets", "nested", "number", "ratio", "flag", "names", "table", "mode", "label"]


def _everything(error: BaseException) -> list[str]:
    texts = [str(error), repr(error), repr(error.args), "".join(traceback.format_exception(error))]
    link: BaseException | None = error
    while link is not None:
        texts += [repr(link), str(link)]
        link = link.__cause__ or link.__context__
    return texts


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("value", HOSTILE, ids=lambda v: type(v).__name__ + str(v)[:12].replace(SECRET, "S"))
def test_a_rejected_request_value_is_never_in_the_error(field: str, value: Any) -> None:
    try:
        Params(**{field: value})
    except ValidationError as error:
        for text in _everything(error):
            assert SECRET not in text, (field, text)
        assert SECRET not in json.dumps([{k: v for k, v in item.items() if k not in ("input", "ctx")} for item in error.errors()], default=str)
    except Exception as error:  # noqa: BLE001 - anything that is not a validation error is raised without the value too
        for text in _everything(error):
            assert SECRET not in text, (field, text)


def test_the_messages_name_kind_and_location() -> None:
    with pytest.raises(ValidationError) as caught:
        Params(password={"secret": SECRET})  # type: ignore[arg-type]
    text = str(caught.value)
    assert "password" in text and "got an object" in text and "input_value" not in text
    with pytest.raises(ValidationError) as caught:
        Params(number=[SECRET])  # type: ignore[arg-type]
    assert "number" in str(caught.value) and "got a list" in str(caught.value)
    with pytest.raises(ValidationError) as caught:
        Params(flag=SECRET)  # type: ignore[arg-type]
    assert "got text" in str(caught.value)
    with pytest.raises(ValidationError) as caught:
        Params(number=2.5)  # type: ignore[arg-type]
    assert "whole number" in str(caught.value) and "2.5" not in str(caught.value)


def test_the_cli_validation_output_has_the_same_form(monkeypatch: pytest.MonkeyPatch) -> None:
    camera = MockCamera()
    monkeypatch.setattr(cli, "make_device", lambda args: camera.device())
    for argument in (f'pwd={{"secret":"{SECRET}"}}', f'pwd=["{SECRET}"]'):
        out, err = io.StringIO(), io.StringIO()
        code = cli.main(["call", "user_management", "add_user", "user=test", argument, "grp=users"], out=out, err=err)
        assert code == 2
        assert SECRET not in err.getvalue() and SECRET not in out.getvalue()
        assert "pwd" in err.getvalue() and "expected a single value" in err.getvalue()
