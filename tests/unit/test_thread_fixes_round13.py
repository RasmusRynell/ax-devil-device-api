"""close() on a dead connection is a no-op that records a network end; an empty multipart boundary is a ResponseFormatError."""

from __future__ import annotations

import time
from typing import Any

import anyio
import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime import ws
from ax_devil_device_api._streams import MixedReplaceDecoder, boundary_of
from ax_devil_device_api.errors import ResponseFormatError

QUICK = Heartbeat(None)
RAW = ws.SessionSpec("audio", "/audio")


def _cause(dev: Any) -> str:
    records = [r for rs in dev._ledger._open.values() for r in rs]  # noqa: SLF001
    folded = dev._ledger._folded  # noqa: SLF001
    assert not records and folded  # the session ended and was folded
    return "folded"


def test_close_after_a_network_drop_does_not_raise() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(RAW, heartbeat=QUICK) as session:
            camera.sockets[0].network_error()
            time.sleep(0.3)
            session.close()
            session.close()  # twice is fine
        assert _cause(dev)
        with dev.connect_session(RAW, heartbeat=QUICK) as again:
            assert again.gap is not None


@pytest.mark.anyio
async def test_async_close_after_a_network_drop() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(RAW, heartbeat=QUICK) as session:
            camera.sockets[0].network_error()
            await anyio.sleep(0.3)
            await session.close()


@pytest.mark.parametrize("content_type", ['multipart/x-mixed-replace; boundary=""', "multipart/x-mixed-replace; boundary=", "multipart/x-mixed-replace"])
def test_empty_or_missing_boundary_is_a_response_format_error(content_type: str) -> None:
    assert boundary_of(content_type) is None


def test_decoder_rejects_an_empty_boundary_with_the_library_error() -> None:
    for boundary in ("", "--", '""'.strip('"')):
        with pytest.raises(ResponseFormatError):
            MixedReplaceDecoder(boundary)


def test_local_close_honors_a_remote_close_the_transport_already_stamped(monkeypatch: pytest.MonkeyPatch) -> None:
    from ax_devil_device_api._http import transport as transport_module

    now = [1000.0]
    monkeypatch.setattr(transport_module, "_clock", lambda: now[0])
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        dev._ledger.now = lambda: now[0]  # noqa: SLF001
        with dev.connect_session(RAW, heartbeat=QUICK) as session:
            now[0] = 1010.0
            camera.sockets[0].push_bytes(b"d")
            assert session.receive(timeout=5) == b"d"
            now[0] = 1020.0
            setattr(session._raw.connection, "remote_close", (1011, 1020.0))  # noqa: SLF001 - stamped, reader not flagged yet
            now[0] = 1100.0
            session.close()
        now[0] = 1200.0
        with dev.connect_session(RAW, heartbeat=QUICK) as again:
            assert again.gap is not None and again.gap.start.timestamp() == 1010.0
