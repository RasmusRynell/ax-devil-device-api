"""A cancelled aclose() still tears the stream down, and a second aclose() is a no-op."""

from __future__ import annotations

from contextlib import AsyncExitStack
from typing import Any

import anyio
import pytest

from ax_devil_device_api._runtime.driver import AsyncStreamResult
from ax_devil_device_api._streams import LinesDecoder


async def _chunks() -> Any:
    yield b"one\n"


@pytest.mark.anyio
async def test_cancelling_aclose_midway_still_closes_the_response_once() -> None:
    events: list[str] = []

    async def teardown() -> None:
        events.append("closing")
        await anyio.sleep(0.2)  # the connection takes a while to close
        events.append("closed")

    stack = AsyncExitStack()
    stack.push_async_callback(teardown)
    stream: AsyncStreamResult[str] = AsyncStreamResult(None, _chunks(), LinesDecoder(), stack)  # type: ignore[arg-type]

    with anyio.move_on_after(0.05) as scope:  # cancelled while the teardown is running
        await stream.aclose()
    assert scope.cancel_called  # the cancellation was still delivered afterwards
    assert events == ["closing", "closed"]  # and the teardown ran to the end
    await stream.aclose()  # a second call does nothing
    assert events == ["closing", "closed"]
    assert [item async for item in stream] == []  # a closed result yields nothing more
