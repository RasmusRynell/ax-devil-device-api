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
