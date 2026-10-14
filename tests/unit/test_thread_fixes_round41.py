"""Non-finite numbers never reach a parsed result; httpx-ws's own queue is small, and a full one blocks nothing for good."""

from __future__ import annotations

import threading
import time
from typing import Any

import anyio
import httpx
import pytest
from ws_fake import FakeWsCamera, notify

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._http.transport import WS_QUEUE_SIZE, WS_UPSTREAM_QUEUE_SIZE
from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, parse_result
from ax_devil_device_api._protocols.cgi import CgiBinding, JsonReply
from ax_devil_device_api._runtime.ws import EVENTS
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


# -- the upstream queue -------------------------------------------------------------------------------------------------

BLOB = "x" * (200 * 1024)
FRAMES = 60


def test_the_upstream_queue_is_small_and_smaller_than_the_session_queue() -> None:
    assert 1 <= WS_UPSTREAM_QUEUE_SIZE <= 16 < WS_QUEUE_SIZE


def test_sync_flood_with_no_consumer_blocks_the_upstream_reader_and_nothing_is_lost() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            for n in range(FRAMES):
                camera.sockets[0].push(notify(f"t/{n}", blob=BLOB))
            time.sleep(0.5)
            assert session._raw._events.qsize() <= WS_UPSTREAM_QUEUE_SIZE  # noqa: SLF001 - the reader is blocked, not buffering
            topics = [session.receive(timeout=10)["params"]["notification"]["topic"] for _ in range(FRAMES)]
            assert topics == [f"t/{n}" for n in range(FRAMES)]  # backpressure, not loss
            assert session.dropped_notifications == 0


def test_sync_context_exit_with_a_full_upstream_queue_does_not_hang() -> None:
    camera = FakeWsCamera()
    finished = threading.Event()

    def scenario() -> None:
        with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
            with dev.connect_session(EVENTS, heartbeat=QUICK):
                for n in range(FRAMES):
                    camera.sockets[0].push(notify(f"t/{n}", blob=BLOB))
                time.sleep(0.4)  # the reader is now blocked on the full queue; nobody reads
        finished.set()

    thread = threading.Thread(target=scenario, daemon=True)
    thread.start()
    assert finished.wait(15), "leaving the session hung on a blocked reader"


def test_sync_request_progresses_while_the_upstream_queue_is_full() -> None:
    camera = FakeWsCamera()

    def handler(socket: Any, message: Any) -> None:
        if message["method"] == "flood":
            for n in range(FRAMES):
                socket.push(notify(f"t/{n}", blob=BLOB))
            socket.push({"apiVersion": "1.0", "context": message["context"], "method": "flood", "data": {"done": True}})

    camera.handler = handler
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            assert session.request("flood", {}, timeout=30) == {"done": True}  # the request drains as it reads


@pytest.mark.anyio
async def test_async_flood_with_no_consumer_is_backpressured_and_nothing_is_lost() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            for n in range(FRAMES):
                camera.sockets[0].push(notify(f"t/{n}", blob=BLOB))
            await anyio.sleep(0.5)
            assert session._raw._receive_event.statistics().current_buffer_used <= WS_UPSTREAM_QUEUE_SIZE  # noqa: SLF001
            topics = [(await session.receive(timeout=10))["params"]["notification"]["topic"] for _ in range(FRAMES)]
            assert topics == [f"t/{n}" for n in range(FRAMES)]
