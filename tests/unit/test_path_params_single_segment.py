"""A path parameter that is not declared multi-segment can never carry a separator, whatever its encoding."""

from __future__ import annotations

from typing import Any

import pytest

from ax_devil_device_api._protocols import cgi, dca, rest
from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation
from ax_devil_device_api._runtime import ws

PAYLOADS = ["a/b", "a\\b", "a%2Fb", "a%2fb", "a%252Fb", "a%5Cb", "/", "\\"]


class _Key(Model):
    key: str


def _op(family: Family, binding: Any) -> Operation[Any]:
    return Operation(ApiInfo(id="t", name="T", family=family), "get", binding=binding, params=_Key)


def _dca(style: str | None) -> Operation[Any]:
    styles = (("key", style),) if style else ()
    return _op(Family.DCA, dca.DcaBinding("GET", "/r/{key}/x", key_styles=styles))  # type: ignore[arg-type]


def _build_dca(op: Operation[Any], value: str) -> Any:
    return dca._build(op, _Key(key=value))


def _build_rest(value: str) -> Any:
    op = _op(Family.REST, rest.RestBinding("GET", "/r/{key}/x"))
    return rest._build(op, _Key(key=value))


def _build_cgi(value: str) -> Any:
    op = _op(Family.CGI, cgi.CgiBinding("/r/{key}/x.cgi"))
    return cgi._build(op, _Key(key=value), {"key": value})


def _bind_ws(value: str) -> Any:
    return ws.SessionSpec("t", "/r/{key}/ws").bind({"key": value})


BINDERS = {
    "dca": lambda v: _build_dca(_dca(None), v),
    "dca-segment": lambda v: _build_dca(_dca("segment"), v),
    "dca-dots": lambda v: _build_dca(_dca("dots_to_slashes"), v),
    "rest": _build_rest,
    "cgi": _build_cgi,
    "ws": _bind_ws,
}


@pytest.mark.parametrize("payload", PAYLOADS[:2] + ["/", "\\", "a/b/c"])
@pytest.mark.parametrize("binder", sorted(BINDERS))
def test_single_segment_params_reject_separators(binder: str, payload: str) -> None:
    with pytest.raises(ValueError, match="single path segment"):
        BINDERS[binder](payload)


@pytest.mark.parametrize("payload", ["a%2Fb", "a%2fb", "a%252Fb"])
@pytest.mark.parametrize("binder", sorted(BINDERS))
def test_already_encoded_separators_are_encoded_again_not_decoded(binder: str, payload: str) -> None:
    """Values arrive raw: a literal '%2F' is text and becomes '%252F', never a separator."""
    built = BINDERS[binder](payload)
    path = built if isinstance(built, str) else getattr(built, "path", None) or built.path
    assert "%25" in path and "/" not in path.split("/r/", 1)[1].split("/", 1)[0]


def test_multi_segment_params_still_allow_slashes_but_not_backslashes() -> None:
    op = _dca("path")
    assert _build_dca(op, "a/b c").path == "/r/a/b%20c/x"
    with pytest.raises(ValueError, match="single path segment"):
        _build_dca(op, "a\\b")
    with pytest.raises(ValueError, match="not a valid path segment"):
        _build_dca(op, "a/../b")


def test_ordinary_values_are_unchanged() -> None:
    assert _build_dca(_dca(None), "a b").path == "/r/a%20b/x"
    assert _build_rest("a b").path == "/r/a%20b/x"
    assert _bind_ws("a b").path == "/r/a%20b/ws"


@pytest.mark.parametrize("binder", [b for b in sorted(BINDERS) if b != "ws"])
def test_an_encoded_backslash_in_a_value_fails_closed_in_the_request_path(binder: str) -> None:
    with pytest.raises(ValueError, match="backslashes"):
        BINDERS[binder]("a%5Cb")
