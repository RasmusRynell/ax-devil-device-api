"""repr() of a model masks the Value next to a secret-named Name, like the request-hook serializer does."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import Field

from ax_devil_device_api._protocols.base import Model
from ax_devil_device_api.apis.action_service import (
    ActionParameter,
    ActionParameters,
    NewRecipientConfiguration,
    StoredActionParameter,
    StoredActionParameters,
)

SECRET = "hunter2-SENTINEL"


def _recipient(*pairs: tuple[str, str]) -> NewRecipientConfiguration:
    return NewRecipientConfiguration(
        name="r1",
        template_token="tpl",
        parameters=ActionParameters(parameter=[ActionParameter(name=name, value=value) for name, value in pairs]),
    )


def test_repr_of_a_recipient_with_a_secret_parameter_hides_the_value() -> None:
    recipient = _recipient(("host", "10.0.0.1"), ("password", SECRET), ("token", SECRET + "2"), ("user", "root"))
    shown = repr(recipient)
    assert SECRET not in shown and "10.0.0.1" in shown and "root" in shown and "password" in shown
    assert SECRET not in str(recipient) and SECRET not in repr(recipient.parameters)


def test_str_and_rich_repr_hide_it_too() -> None:
    recipient = _recipient(("password", SECRET))
    assert SECRET not in str(recipient) and SECRET not in "".join(str(arg) for arg in recipient.__rich_repr__())


@pytest.mark.parametrize("name", ["password", "Password", "api_key", "secret", "SharedKey", "tt:Password", "authToken"])
def test_the_name_may_be_any_secret_name(name: str) -> None:
    assert SECRET not in repr(ActionParameter(name=name, value=SECRET))


def test_a_plain_parameter_is_shown() -> None:
    assert "10.0.0.1" in repr(ActionParameter(name="host", value="10.0.0.1"))


def test_stored_parameters_with_a_secret_name_are_masked() -> None:
    stored = StoredActionParameters(parameter=[StoredActionParameter(name="password", value=SECRET), StoredActionParameter(name="host", value="h")])
    assert SECRET not in repr(stored) and "'h'" in repr(stored)


class Loose(Model):
    """A model with free-form dict and list fields, as some responses have."""

    parameters: list[dict[str, Any]] | None = Field(default=None, validation_alias="Parameters", serialization_alias="Parameters")
    options: dict[str, Any] | None = None


def test_dicts_and_nested_lists_are_masked_by_the_same_rule() -> None:
    loose = Loose(
        parameters=[{"@Name": "password", "@Value": SECRET}, {"Name": "host", "Value": "h"}, {"tt:Key": "token", "tt:Value": SECRET}],
        options={"nested": [{"name": "passphrase", "value": SECRET}], "api_key": SECRET},
    )
    shown = repr(loose)
    assert SECRET not in shown and "'h'" in shown


def test_the_wire_form_still_carries_the_value() -> None:
    wire = _recipient(("password", SECRET)).to_wire()
    assert SECRET in repr(wire)  # only repr hides it; the request must still send it


# -- keys, depth and parity with the hook serializer -----------------------------------------------------------------------

from ax_devil_device_api._http.debug import DEPTH_LIMIT, MAX_DEPTH, emit_request, serialize  # noqa: E402
from ax_devil_device_api._http.types import JsonBody, Request  # noqa: E402


class Free(Model):
    data: Any = None


def test_a_secret_in_a_mapping_key_is_not_shown_in_a_repr() -> None:
    loose = Loose(options={"password=hunter2-SENTINEL": "invalid", "rtsp://u:SENTINEL-CRED@h/x": 1, "ok": 2})
    shown = repr(loose)
    assert "hunter2" not in shown and "SENTINEL-CRED" not in shown and "'ok': 2" in shown
    nested = Loose(parameters=[{"a": {"password=hunter2-SENTINEL": "x"}}])
    assert "hunter2" not in repr(nested)


@pytest.mark.parametrize("levels", [10, 20, MAX_DEPTH, MAX_DEPTH + 5, 200])
def test_a_password_at_the_bottom_of_a_deep_structure_is_in_neither_the_repr_nor_the_hook_record(levels: int) -> None:
    deep: Any = {"password": SECRET}
    for _ in range(levels):
        deep = {"level": deep}
    loose = Loose(options=deep)
    assert SECRET not in repr(loose) and SECRET not in repr(serialize(deep))
    records: list[dict[str, Any]] = []
    emit_request(records.append, Request("POST", "/x", body=JsonBody(deep)), "https://cam/x", 5.0, True)
    assert SECRET not in repr(records)
    if levels > MAX_DEPTH:
        assert DEPTH_LIMIT in repr(loose) and DEPTH_LIMIT in repr(records)
    # the same goes for a Name / Value pair at the bottom and for lists on the way down
    pair: Any = [{"@Name": "password", "@Value": SECRET}]
    for _ in range(levels):
        pair = [pair, {"x": pair}] if levels < 12 else [pair]
    assert SECRET not in repr(Free(data=pair))


def test_beyond_the_depth_limit_every_caller_gets_the_placeholder() -> None:
    value: Any = "leaf-SENTINEL"
    for _ in range(MAX_DEPTH + 3):
        value = {"k": value}
    assert "leaf-SENTINEL" not in repr(serialize(value)) and DEPTH_LIMIT in repr(serialize(value))
    listed: Any = "leaf-SENTINEL"
    for _ in range(MAX_DEPTH + 3):
        listed = [listed]
    assert "leaf-SENTINEL" not in repr(Free(data=listed)) and DEPTH_LIMIT in repr(Free(data=listed))


PARITY: list[dict[str, Any]] = [
    {"password": SECRET, "ok": 1},
    {"@Name": "password", "@Value": SECRET, "x": "y"},
    {"tt:Key": "authToken", "tt:Value": SECRET},
    {"password=hunter2-SENTINEL": "v", "rtsp://u:p@h/x": "w"},
    {"nested": {"Name": "secret", "Value": SECRET, "other": {"api_key": SECRET}}},
    {"plain": "text", "n": 3, "none": None, "flag": True},
    {"list": [{"name": "passphrase", "value": SECRET}, {"name": "host", "value": "h"}]},
]


@pytest.mark.parametrize("value", PARITY, ids=lambda v: str(sorted(v))[:30])
def test_repr_and_the_hook_serializer_redact_the_same_inputs_identically(value: dict[str, Any]) -> None:
    loose = Loose(options=value)
    (shown,) = [arg for name, arg in loose.__repr_args__() if name == "options"]
    assert shown == serialize(value)
    assert SECRET not in repr(loose) and "hunter2" not in repr(loose)
