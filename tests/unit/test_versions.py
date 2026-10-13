"""Version parsing, negotiation, and applicability rules (no device, no I/O)."""

from __future__ import annotations

from typing import Literal

import pytest

from ax_devil_device_api._protocols.base import (
    ApiInfo,
    ApiVersion,
    Applicability,
    Family,
    Model,
    Operation,
    check_applicability,
    select_version,
)
from ax_devil_device_api.errors import NotSupported

INFO = ApiInfo(id="test-api", name="Test API", family=Family.JSONRPC, major=1)


class Server(Model):
    host: str
    alpn_protocol: str | None = None


class Params(Model):
    server: Server | None = None
    protocol: Literal["tcp", "wss"] | None = None


def operation(*, since: ApiVersion | None = None, applicability: tuple[Applicability, ...] = ()) -> Operation:
    return Operation(INFO, "op", binding=object(), params=Params, since=since, applicability=applicability)


ALPN_SINCE_1_3 = Applicability(path="server.alpn_protocol", since=ApiVersion(1, 3))
WSS_SINCE_1_3 = Applicability(path="protocol", since=ApiVersion(1, 3), value="wss")


# ---------------------------------------------------------------------------
# select_version


@pytest.mark.parametrize(
    ("advertised", "major", "known", "expected"),
    [
        (["1.4", "2.0"], 1, ["1.0"], "1.0"),  # client knows less than the device: use client's max
        (["1.4", "2.0"], 1, ["1.0", "1.6"], "1.4"),  # device is older than the client: use device's max
        (["1.4", "2.0"], 1, [], "1.4"),  # no known versions: use the device's max
        (["1.4", "2.0"], 3, ["1.0"], None),  # nothing advertised for this major version
    ],
)
def test_select_version_picks_lower_of_device_and_client(advertised, major, known, expected) -> None:
    result = select_version(
        [ApiVersion.parse(v) for v in advertised],
        major,
        [ApiVersion.parse(v) for v in known],
    )
    assert (None if result is None else str(result)) == expected


# ---------------------------------------------------------------------------
# ApiVersion


def test_parse_accepts_major_minor() -> None:
    assert ApiVersion.parse("1.2") == ApiVersion(1, 2)
    assert str(ApiVersion.parse(" 2.0 ")) == "2.0"


@pytest.mark.parametrize("text", ["v1", "1", "1.2.3", "1.x"])
def test_parse_rejects_anything_but_major_minor(text: str) -> None:
    with pytest.raises(ValueError, match="major.minor"):
        ApiVersion.parse(text)


def test_minor_versions_compare_numerically() -> None:
    assert ApiVersion(1, 10) > ApiVersion(1, 9)
    assert ApiVersion.parse("1.10") > ApiVersion.parse("1.9")
    assert ApiVersion.parse("2.0") > ApiVersion.parse("1.99")


# ---------------------------------------------------------------------------
# check_applicability


def test_operation_since_rejects_older_device() -> None:
    op = operation(since=ApiVersion(1, 2))
    with pytest.raises(NotSupported, match="requires API version 1.2"):
        check_applicability(op, None, ApiVersion(1, 0))


def test_operation_since_accepts_equal_or_newer_device() -> None:
    op = operation(since=ApiVersion(1, 2))
    check_applicability(op, None, ApiVersion(1, 2))
    check_applicability(op, None, ApiVersion(1, 3))


def test_nested_path_rejected_only_when_that_field_is_set() -> None:
    op = operation(applicability=(ALPN_SINCE_1_3,))
    older = ApiVersion(1, 2)

    # Server is present but alpn_protocol was never set: nothing to reject.
    check_applicability(op, Params(server=Server(host="broker")), older)
    # Params without a server at all: nothing to reject.
    check_applicability(op, Params(), older)

    with pytest.raises(NotSupported, match="server.alpn_protocol requires API version 1.3"):
        check_applicability(op, Params(server=Server(host="broker", alpn_protocol="h2")), older)

    check_applicability(op, Params(server=Server(host="broker", alpn_protocol="h2")), ApiVersion(1, 3))


def test_enum_value_rejected_only_when_it_matches() -> None:
    op = operation(applicability=(WSS_SINCE_1_3,))
    older = ApiVersion(1, 0)

    check_applicability(op, Params(protocol="tcp"), older)

    with pytest.raises(NotSupported, match="protocol='wss' requires API version 1.3"):
        check_applicability(op, Params(protocol="wss"), older)


def test_unknown_version_checks_nothing() -> None:
    op = operation(since=ApiVersion(9, 0), applicability=(ALPN_SINCE_1_3, WSS_SINCE_1_3))
    params = Params(server=Server(host="broker", alpn_protocol="h2"), protocol="wss")
    check_applicability(op, params, None)
