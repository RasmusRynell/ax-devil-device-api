"""Async capability probes are bounded by max_concurrency, so a probe's timeout starts when it can be sent."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from ax_devil_device_api import AsyncDevice


@pytest.mark.anyio
async def test_probe_fan_out_does_not_turn_slot_waits_into_pool_timeouts() -> None:
    async def slow(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.3)
        return httpx.Response(404, text="nope")

    async with AsyncDevice(
        "cam.test", credentials=("root", "pass"), transport=httpx.MockTransport(slow), timeout=0.5, max_concurrency=2
    ) as dev:
        extra = ("applications", "services", *(f"properties:Prop{n}.Version" for n in range(6)))
        caps = await dev._collect(extra)  # noqa: SLF001
    assert len(caps.errors) == 3 + len(extra)  # every probe was sent and failed on its own 404
    assert not [name for name, text in caps.errors.items() if "PoolTimeout" in text], caps.errors
