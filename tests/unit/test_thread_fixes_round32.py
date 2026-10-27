"""Request models are strict about booleans and whole numbers; text that spells a number is still accepted."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ax_devil_device_api._protocols.base import Model
from ax_devil_device_api.apis.media_stream import GetMediaStreamRequest


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("compression", True),
        ("compression", False),
        ("compression", 2.5),
        ("rotation", False),
        ("rotation", True),
        ("fps", True),
        ("mirror", True),
    ],
)
def test_bools_and_fractions_are_rejected_for_integer_fields(field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        GetMediaStreamRequest(**{field: value})


@pytest.mark.parametrize(("field", "value", "expected"), [("compression", 2.0, 2), ("compression", "2", 2), ("fps", "25", 25), ("rotation", 90, 90)])
def test_whole_floats_and_numeric_text_are_still_accepted(field: str, value: Any, expected: int) -> None:
    assert getattr(GetMediaStreamRequest(**{field: value}), field) == expected


class Flags(Model):
    enabled: bool | None = None
    level: float | None = None
    levels: list[int] | None = None


@pytest.mark.parametrize("value", [1, 0, "true", "yes", 2.0])
def test_boolean_fields_take_only_real_bools(value: Any) -> None:
    with pytest.raises(ValidationError):
        Flags(enabled=value)
    assert Flags(enabled=True).enabled is True and Flags(enabled=False).enabled is False


def test_number_fields_reject_bool_and_list_items_too() -> None:
    with pytest.raises(ValidationError):
        Flags(level=True)
    with pytest.raises(ValidationError):
        Flags(levels=[1, True])
    assert Flags(level=1.5, levels=[1, 2]).levels == [1, 2]


def test_responses_stay_lenient() -> None:
    from ax_devil_device_api._protocols.base import RESPONSE_CONTEXT

    parsed = Flags.model_validate({"enabled": "true", "level": True, "levels": ["1", 2]}, context={RESPONSE_CONTEXT: True})
    assert parsed.enabled is True and parsed.levels == [1, 2]
