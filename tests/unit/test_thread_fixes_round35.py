"""Data Hub isHistorical must be a JSON boolean (this supersedes the earlier rejection of the same point)."""

from __future__ import annotations

from typing import Any

import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import DATA_HUB
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, TopicSample
from ax_devil_device_api.errors import ResponseFormatError

QUICK = Heartbeat(None)


def _sample(**extra: Any) -> dict[str, Any]:
    params = {"topic": "t", "subscriptionId": "s", "instance": {}, "data": {}, "timestamp": "2024-01-01T00:00:00Z", **extra}
    return {"jsonrpc": "2.0", "method": "data-hub_v1:topicSample", "params": params}


@pytest.mark.parametrize("bad", ["false", "true", "", 0, 1, None, [], {}])
def test_a_non_boolean_is_historical_is_a_response_format_error(bad: Any) -> None:
    with pytest.raises(ResponseFormatError, match="isHistorical"):
        DataHubCodec().classify(_sample(isHistorical=bad))


@pytest.mark.parametrize(("extra", "expected"), [({"isHistorical": True}, True), ({"isHistorical": False}, False), ({}, False)])
def test_booleans_and_an_absent_flag_behave_as_before(extra: dict[str, Any], expected: bool) -> None:
    note = DataHubCodec().classify(_sample(**extra))
    assert note is not None and isinstance(note.item, TopicSample) and note.item.is_historical is expected  # type: ignore[union-attr]


@pytest.mark.parametrize("field", ["instance", "data"])
@pytest.mark.parametrize("bad", ["missing", None, "text", [], 5])
def test_a_missing_or_non_object_required_field_is_a_response_format_error(field: str, bad: Any) -> None:
    message = _sample()
    if bad == "missing":
        del message["params"][field]
    else:
        message["params"][field] = bad
    with pytest.raises(ResponseFormatError, match=field):
        DataHubCodec().classify(message)


def test_sync_session_reports_the_bad_sample_to_the_consumer_and_stays_usable() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(DATA_HUB, heartbeat=QUICK) as session:
            camera.sockets[0].push(_sample(isHistorical="false"))
            camera.sockets[0].push(_sample(isHistorical=True))
            notes = session.notifications()
            with pytest.raises(ResponseFormatError):
                next(notes)
            assert session.receive(timeout=3)["params"]["isHistorical"] is True  # the session was not broken


@pytest.mark.anyio
async def test_async_session_reports_the_bad_sample_to_the_consumer_and_stays_usable() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(DATA_HUB, heartbeat=QUICK) as session:
            camera.sockets[0].push(_sample(isHistorical=1))
            camera.sockets[0].push(_sample(isHistorical=False))
            notes = session.notifications()
            with pytest.raises(ResponseFormatError):
                await anext(notes)
            assert (await session.receive(timeout=3))["params"]["isHistorical"] is False
