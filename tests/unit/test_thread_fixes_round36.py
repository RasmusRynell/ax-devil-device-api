"""A union branch accepts a value only if the value satisfies that branch's strict kind rules."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ax_devil_device_api.apis.fence_guard import Filter


@pytest.mark.parametrize("data", [True, [True], [1, True], 2.5, [2.5]])
def test_union_of_list_and_int_rejects_bool_in_either_branch(data: object) -> None:
    with pytest.raises(ValidationError):
        Filter(type="timeShortLivedLimit", data=data)  # type: ignore[arg-type]


@pytest.mark.parametrize("data", [3, [5, 5], "4"])
def test_correct_values_are_still_accepted(data: object) -> None:
    assert Filter.model_validate({"type": "timeShortLivedLimit", "data": data}).data in (3, [5, 5], 4)
