"""Numeric text from the device is converted only when it is a bounded run of ASCII digits; anything else is not a number
(and never a ValueError from int())."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

import pytest

from ax_devil_device_api import Support
from ax_devil_device_api._protocols.base import (
    ApiInfo,
    ApiVersion,
    Family,
    Model,
    Operation,
    api_error,
    ascii_int,
    parse_result,
)
from ax_devil_device_api._protocols.cgi import CgiBinding, Text, _numeric_or_text
from ax_devil_device_api._runtime.capabilities import Capabilities, _version_key, decide_support, firmware_key
from ax_devil_device_api.errors import DeviceError, ResponseFormatError

HUGE = "9" * 5000
ODD = ["²", "²³", "٣", "1²", "", " ", "-5", "+5", "1.5", "0x10"]


def test_ascii_int_accepts_bounded_ascii_digits_only() -> None:
    assert ascii_int("0") == 0 and ascii_int(" 42 ") == 42 and ascii_int("9" * 18) == int("9" * 18)
    for text in (HUGE, "9" * 19, *ODD):
        assert ascii_int(text) is None, text


def _op() -> Operation[Any]:
    return Operation(ApiInfo(id="t", name="T", family=Family.CGI), "op", CgiBinding("/x.cgi", reply=Text()), result=None)


@pytest.mark.parametrize("status", [None, 200, 401, 403, 500, 503])
@pytest.mark.parametrize("code", [HUGE, HUGE + "x", *ODD, "5-" + HUGE])
def test_api_error_with_a_non_numeric_or_huge_text_code_stays_in_the_hierarchy(code: str, status: int | None) -> None:
    error = api_error(_op(), code, "message", http_status=status, details=None)
    assert isinstance(error, DeviceError)


def test_helpers_and_version_parsers_do_not_raise_on_huge_or_unicode_digits() -> None:
    for text in (HUGE, f"{HUGE}.1", f"1.{HUGE}", "².³"):
        assert _version_key(text) is None or isinstance(_version_key(text), tuple)
        assert firmware_key(text) is None or isinstance(firmware_key(text), tuple)
        with pytest.raises(ValueError, match="major.minor"):
            ApiVersion.parse(text)
    assert _numeric_or_text(HUGE) == HUGE and _numeric_or_text("0") == 0 and _numeric_or_text(None) is None and _numeric_or_text("") == ""


def test_decide_support_with_a_huge_firmware_is_a_library_answer() -> None:
    from ax_devil_device_api._protocols.base import ParamDiscovery

    info = ApiInfo(id="x", name="x", family=Family.CGI, requires_firmware="10.0", discovery=(ParamDiscovery("Properties.API.A.B", "1", ">="),))
    for firmware in (HUGE, f"10.{HUGE}", "².³"):
        caps = Capabilities(None, None, {"Properties.API.A.B": HUGE}, {}, datetime.now(UTC), firmware=firmware)
        assert decide_support(info, caps).status in (Support.UNKNOWN, Support.NO, Support.YES)


class _Flag(Model):
    mode: Literal[0, 1] | None = None


def test_a_huge_numeric_text_for_a_literal_int_field_is_a_format_error_not_a_value_error() -> None:
    op = Operation(ApiInfo(id="t", name="T", family=Family.CGI), "op", object(), result=_Flag)
    for text in (HUGE, "²"):
        try:
            parse_result(op, {"mode": text})
        except ResponseFormatError:
            pass
