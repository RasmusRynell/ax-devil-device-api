"""Non-finite numbers never reach a parsed result; httpx-ws's own queue is small, and a full one blocks nothing for good."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ax_devil_device_api import Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, parse_result
from ax_devil_device_api._protocols.cgi import CgiBinding, JsonReply
from ax_devil_device_api.errors import ResponseFormatError

QUICK = Heartbeat(None)
INFO = ApiInfo(id="t", name="T", family=Family.CGI)


class Reading(Model):
    value: float
    history: list[float] | None = None
    by_name: dict[str, float] | None = None
    pair: tuple[float, float] | None = None


class Outer(Model):
    reading: Reading


def _op(result: Any) -> Operation[Any]:
    return Operation(INFO, "get", binding=object(), result=result)


@pytest.mark.parametrize("text", ["NaN", "nan", "inf", "-inf", "Infinity", "-Infinity"])
@pytest.mark.parametrize(
    ("result", "shape"),
    [
        (Reading, lambda t: {"value": t}),
        (Reading, lambda t: {"value": 1.0, "history": [1.0, t]}),
        (Reading, lambda t: {"value": 1.0, "by_name": {"a": t}}),
        (Reading, lambda t: {"value": 1.0, "pair": [1.0, t]}),
        (Outer, lambda t: {"reading": {"value": t}}),
        (list[Reading], lambda t: [{"value": 1.0}, {"value": t}]),
        (float, lambda t: t),
        (dict[str, list[float]], lambda t: {"k": [t]}),
    ],
    ids=["field", "list", "dict", "tuple", "nested-model", "list-of-models", "scalar", "dict-of-lists"],
)
def test_text_that_coerces_to_a_non_finite_float_is_a_response_format_error(text: str, result: Any, shape: Any) -> None:
    with pytest.raises(ResponseFormatError, match="NaN or infinite"):
        parse_result(_op(result), shape(text))


def test_finite_numbers_and_numeric_text_still_parse() -> None:
    parsed = parse_result(_op(Reading), {"value": "1.5", "history": [1, "2"], "pair": [0, 1]})
    assert parsed.value == 1.5 and parsed.history == [1.0, 2.0]


def test_a_cgi_json_reply_with_nan_text_is_rejected_end_to_end() -> None:
    op = Operation(INFO, "get", binding=CgiBinding("/x.cgi", reply=JsonReply()), result=Reading)
    handler = lambda request: httpx.Response(200, json={"value": "NaN"})  # noqa: E731
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler)) as dev:
        with pytest.raises(ResponseFormatError):
            dev.invoke(op)
