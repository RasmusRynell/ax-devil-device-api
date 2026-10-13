"""Tolerant enum pass keeps every other constraint; the httpx-ws signal the session reaping relies on exists."""

from __future__ import annotations

import time
from typing import Annotated, Any, Literal

import pytest
from pydantic import Field, ValidationError
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, parse_result
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api.errors import ResponseFormatError

INFO = ApiInfo(id="t", name="T", family=Family.CGI)
Kind = Literal["a", "b"]


def _op(result: Any) -> Operation[Any]:
    return Operation(INFO, "get", binding=object(), result=result)


def test_unknown_enum_with_a_min_length_violation_is_rejected() -> None:
    op = _op(Annotated[list[Kind], Field(min_length=2)])
    assert parse_result(op, ["new", "a"]) == ["new", "a"]
    with pytest.raises(ResponseFormatError):
        parse_result(op, ["new"])


def test_unknown_enum_with_a_range_or_pattern_violation_is_rejected() -> None:
    op = _op(dict[str, Annotated[list[Kind], Field(max_length=1)]])
    assert parse_result(op, {"x": ["new"]}) == {"x": ["new"]}
    with pytest.raises(ResponseFormatError):
        parse_result(op, {"x": ["new", "a"]})
    nested = _op(Annotated[dict[str, Kind], Field(min_length=1)])
    with pytest.raises(ResponseFormatError):
        parse_result(nested, {})


def test_model_field_unknown_enum_with_length_violation_is_rejected() -> None:
    class Box(Model):
        kinds: list[Kind] = Field(min_length=2)

    assert parse_result(_op(Box), {"kinds": ["new", "a"]}).kinds == ["new", "a"]
    with pytest.raises(ResponseFormatError):
        parse_result(_op(Box), {"kinds": ["new"]})
    with pytest.raises(ValidationError):
        Box.from_response_data({"kinds": ["new"]})


def test_httpx_ws_still_exposes_the_reader_signal_session_reaping_uses() -> None:
    """Reaping dead sessions reads ``_should_close`` of httpx-ws; an upgrade that drops it must fail here, loudly."""
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=Heartbeat(None)) as session:
            signal = session._raw._should_close  # noqa: SLF001
            assert not signal.is_set()
            camera.sockets[0].close()
            deadline = time.monotonic() + 3
            while not signal.is_set() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert signal.is_set()


@pytest.mark.anyio
async def test_httpx_ws_async_session_exposes_the_same_signal() -> None:
    import anyio

    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=Heartbeat(None)) as session:
            signal = session._raw._should_close  # noqa: SLF001
            assert not signal.is_set()
            camera.sockets[0].close()
            with anyio.fail_after(3):
                while not signal.is_set():
                    await anyio.sleep(0.01)
