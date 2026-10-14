"""A StreamResult has one iterator: next() followed by more iteration continues, and the response is released only
on exhaustion, close() or leaving the context."""

from __future__ import annotations

import gc
from contextlib import AsyncExitStack, ExitStack
from typing import Any

import pytest

from ax_devil_device_api._runtime.driver import AsyncStreamResult, StreamResult
from ax_devil_device_api._streams import LinesDecoder

CHUNKS = [b"one\ntwo\n", b"three\n", b"four\nfive\n"]


def _sync() -> tuple[StreamResult[str], list[str]]:
    events: list[str] = []
    stack = ExitStack()
    stack.callback(events.append, "released")
    return StreamResult(None, iter(CHUNKS), LinesDecoder(), stack), events  # type: ignore[arg-type]


async def _achunks() -> Any:
    for chunk in CHUNKS:
        yield chunk


def _async() -> tuple[AsyncStreamResult[str], list[str]]:
    events: list[str] = []
    stack = AsyncExitStack()
    stack.callback(events.append, "released")
    return AsyncStreamResult(None, _achunks(), LinesDecoder(), stack), events  # type: ignore[arg-type]


def test_next_then_continued_iteration_keeps_the_response_open_and_continues() -> None:
    stream, events = _sync()
    assert next(iter(stream)) == "one"
    gc.collect()
    assert events == []  # the temporary iterator of the old implementation would have released it here
    assert list(stream) == ["two", "three", "four", "five"]
    assert events == ["released"]  # released on exhaustion, once


def test_close_releases_midway_and_ends_the_iteration() -> None:
    stream, events = _sync()
    assert next(stream) == "one"
    stream.close()
    stream.close()
    assert events == ["released"]
    with pytest.raises((StopIteration, ValueError, RuntimeError)):
        next(stream)


def test_context_exit_releases_an_unfinished_stream() -> None:
    stream, events = _sync()
    with stream:
        assert next(iter(stream)) == "one"
        assert events == []
    assert events == ["released"]


def test_untouched_stream_is_released_by_close_and_then_empty() -> None:
    stream, events = _sync()
    stream.close()
    assert events == ["released"] and list(stream) == []


@pytest.mark.anyio
async def test_async_next_then_continued_iteration_keeps_the_response_open_and_continues() -> None:
    stream, events = _async()
    assert await anext(aiter(stream)) == "one"
    gc.collect()
    assert events == []
    assert [item async for item in stream] == ["two", "three", "four", "five"]
    assert events == ["released"]


@pytest.mark.anyio
async def test_async_close_and_context_exit_release_the_response() -> None:
    stream, events = _async()
    assert await anext(stream) == "one"
    await stream.aclose()
    await stream.aclose()
    assert events == ["released"]
    stream, events = _async()
    async with stream:
        assert await anext(aiter(stream)) == "one"
        assert events == []
    assert events == ["released"]
