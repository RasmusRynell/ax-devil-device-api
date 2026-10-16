"""The request kind rules (bool is not a number, a boolean field takes real bools, no fractions for integers) hold at
every depth of a field's shape."""

from __future__ import annotations

from typing import Any, Literal

import pytest
from pydantic import ValidationError

from ax_devil_device_api._protocols.base import RESPONSE_CONTEXT, Model


class Inner(Model):
    count: int
    on: bool | None = None


class Shapes(Model):
    flags: dict[str, bool] | None = None
    rows: list[dict[str, int]] | None = None
    series: dict[str, list[int]] | None = None
    maybe: int | None = None
    either: int | str | None = None
    pair: tuple[int, bool] | None = None
    many: tuple[float, ...] | None = None
    choice: Literal[0, 1] | None = None
    nested: Inner | None = None
    nested_list: list[Inner] | None = None
    tags: set[int] | None = None


CASES: list[tuple[str, list[Any], Any]] = [
    ("flags", [{"flag": 1}, {"flag": 2.5}, {"flag": "true"}], {"flag": True}),
    ("rows", [[{"a": True}], [{"a": 2.5}]], [{"a": 1}, {"b": 2.0}]),
    ("series", [{"a": [1, True]}, {"a": [1.5]}], {"a": [1, 2]}),
    ("maybe", [True, 2.5], 3),
    ("either", [True, 2.5], 3),
    ("pair", [(1, 1), (True, True), (1.5, True), (2, 0)], (1, True)),
    ("many", [(1.0, True), (True,)], (1.0, 2)),
    ("choice", [True, False], 1),
    ("nested", [{"count": True}, {"count": 2.5}, {"count": 1, "on": 1}], {"count": 1, "on": True}),
    ("nested_list", [[{"count": 1}, {"count": True}], [{"count": 1, "on": 0}]], [{"count": 1}]),
    ("tags", [{True}, {2.5}], {1, 2}),
]


@pytest.mark.parametrize(("field", "bad", "good"), CASES, ids=[c[0] for c in CASES])
def test_kind_rules_hold_at_every_depth(field: str, bad: list[Any], good: Any) -> None:
    for value in bad:
        with pytest.raises(ValidationError):
            Shapes(**{field: value})
    assert getattr(Shapes(**{field: good}), field) is not None


def test_union_of_int_and_str_still_accepts_text_and_numbers() -> None:
    assert Shapes(either="abc").either == "abc"
    assert Shapes(either="2").either in ("2", 2)
    assert Shapes.model_validate({"either": 2.0}).either in (2, 2.0)


def test_numeric_text_is_still_accepted_where_numbers_are_expected() -> None:
    assert Shapes.model_validate({"maybe": "3"}).maybe == 3
    assert Shapes.model_validate({"series": {"a": ["1", 2]}}).series == {"a": [1, 2]}


def test_responses_stay_lenient_at_depth() -> None:
    parsed = Shapes.model_validate({"flags": {"x": 1}, "rows": [{"a": True}]}, context={RESPONSE_CONTEXT: True})
    assert parsed.flags == {"x": True} and parsed.rows == [{"a": 1}]
