"""Gap ledger matrix: every way a session can end x how the end is noticed x single/overlapping sessions x sync/async.

One injected clock drives both the ledger and the transport's frame stamps. Timeline (seconds):

    1000 A opens   1005 B opens (overlap only)   1010 A gets data   1015 B gets data
    1020 the end happens on A   1090 B closes locally (overlap only)
    1100/1110 A is finalized and B exits (order depends on the case)   1200 C opens: its gap is the answer
"""

from __future__ import annotations

import time
from typing import Any

import anyio
import pytest
import wsproto.utilities
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http import transport as transport_module
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime import ws
from ax_devil_device_api.errors import ConnectionFailed, ResponseFormatError, SessionClosed

QUICK = Heartbeat(None)
RAW = ws.SessionSpec("audio", "/audio")
MIB = 1024 * 1024

CAUSES = ["normal_remote", "abnormal_1011", "network_error", "oversize_1009", "local_close", "send_failure"]
MODES = ["read", "unread_close", "unread_exit", "unread_reaped"]
TOPOLOGIES = ["single", "overlap_AB", "overlap_BA"]


def _valid(cause: str, mode: str) -> bool:
    if cause == "local_close":
        return mode in ("read", "unread_exit")  # read = an explicit close(); nothing remote to leave unread
    if cause == "send_failure":
        return mode == "read"  # the failure is only observed by the failing send
    return True


CASES = [(c, m, t) for c in CAUSES for m in MODES for t in TOPOLOGIES if _valid(c, m)]
IDS = ["-".join(c) for c in CASES]


def _trigger(cause: str, socket: Any) -> None:
    if cause == "normal_remote":
        socket.close(1000)
    elif cause == "abnormal_1011":
        socket.close(1011)
    elif cause == "network_error":
        socket.network_error()
    elif cause == "oversize_1009":
        socket.push_fragments(b"\x00" * (5 * MIB), b"\x00" * (5 * MIB))


EXPECTED_ERROR = {
    "normal_remote": SessionClosed,
    "abnormal_1011": ConnectionFailed,
    "network_error": ConnectionFailed,
    "oversize_1009": ResponseFormatError,
    "send_failure": SessionClosed,
}


def _expected_start(cause: str, topology: str, a_finalized_at: float) -> float:
    # oversize: the first fragment (within the limit) arrived at 1020, so that is the last evidence of liveness
    own = {"normal_remote": 1020.0, "oversize_1009": 1020.0, "local_close": a_finalized_at}.get(cause, 1010.0)
    return max(own, 1090.0) if topology != "single" else own


def _break_send(session: Any) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise wsproto.utilities.LocalProtocolError("connection is closed")

    session._raw.send_bytes = fail  # noqa: SLF001


def _setup(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    now = [1000.0]
    monkeypatch.setattr(transport_module, "_clock", lambda: now[0])
    return now


@pytest.mark.parametrize(("cause", "mode", "topology"), CASES, ids=IDS)
def test_sync_matrix(monkeypatch: pytest.MonkeyPatch, cause: str, mode: str, topology: str) -> None:
    now = _setup(monkeypatch)
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=4) as dev:
        dev._ledger.now = lambda: now[0]  # noqa: SLF001
        cm_a = dev.connect_session(RAW, heartbeat=QUICK)
        a = cm_a.__enter__()
        cm_b = None
        b: Any = None
        if topology != "single":
            now[0] = 1005.0
            cm_b = dev.connect_session(RAW, heartbeat=QUICK)
            b = cm_b.__enter__()
            assert b.gap is None  # A is live: coverage is continuous
        now[0] = 1010.0
        camera.sockets[0].push_bytes(b"d")
        assert a.receive(timeout=5) == b"d"
        if cm_b is not None:
            now[0] = 1015.0
            camera.sockets[1].push_bytes(b"d")
            assert b.receive(timeout=5) == b"d"
        now[0] = 1020.0
        _trigger(cause, camera.sockets[0])
        time.sleep(0.4)  # the reader sees it now
        if cm_b is not None:
            now[0] = 1090.0
            b.close()

        finalized_at = {"single": 1100.0, "overlap_AB": 1100.0, "overlap_BA": 1110.0}[topology]

        def finalize_a(at: float, *, exit_context: bool = True) -> None:
            now[0] = at
            if mode == "read":
                if cause == "local_close":
                    a.close()
                else:
                    if cause == "send_failure":
                        _break_send(a)
                    with pytest.raises(EXPECTED_ERROR[cause]):
                        a.send(b"x") if cause == "send_failure" else a.receive(timeout=5)
            elif mode == "unread_close":
                a.close()
            if exit_context:
                cm_a.__exit__(None, None, None)

        def finalize_b(at: float) -> None:
            now[0] = at
            assert cm_b is not None
            cm_b.__exit__(None, None, None)

        if mode == "unread_reaped":
            if topology == "overlap_BA":
                finalize_b(1100.0)
        elif topology == "overlap_BA":
            finalize_b(1100.0)
            finalize_a(finalized_at)
        else:
            finalize_a(1100.0)
            if cm_b is not None:
                finalize_b(1110.0)

        now[0] = 1200.0
        with dev.connect_session(RAW, heartbeat=QUICK) as c:
            assert c.gap is not None
            assert c.gap.start.timestamp() == _expected_start(cause, topology, finalized_at)
            assert c.gap.end.timestamp() == 1200.0
            now[0] = 1210.0
        if mode == "unread_reaped":
            cm_a.__exit__(None, None, None)
            if topology == "overlap_AB":
                finalize_b(1220.0)


class _AsyncB:
    """The overlapping session B runs in its own task, so it can end in any order relative to A (anyio scopes nest)."""

    def __init__(self, dev: AsyncDevice) -> None:
        self.dev = dev
        self.opened, self.received, self.closed, self.exited = (anyio.Event() for _ in range(4))
        self.cmd_receive, self.cmd_close, self.cmd_exit = (anyio.Event() for _ in range(3))
        self.gap: Any = "unset"

    async def run(self) -> None:
        async with self.dev.connect_session(RAW, heartbeat=QUICK) as b:
            self.gap = b.gap
            self.opened.set()
            await self.cmd_receive.wait()
            await b.receive(timeout=5)
            self.received.set()
            await self.cmd_close.wait()
            await b.close()
            self.closed.set()
            await self.cmd_exit.wait()
        self.exited.set()


@pytest.mark.anyio
@pytest.mark.parametrize(("cause", "mode", "topology"), CASES, ids=IDS)
async def test_async_matrix(monkeypatch: pytest.MonkeyPatch, cause: str, mode: str, topology: str) -> None:
    now = _setup(monkeypatch)
    camera = FakeWsCamera()
    async with (
        AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport(), max_streams=4) as dev,
        anyio.create_task_group() as tg,
    ):
        dev._ledger.now = lambda: now[0]  # noqa: SLF001
        cm_a = dev.connect_session(RAW, heartbeat=QUICK)
        a = await cm_a.__aenter__()
        b = _AsyncB(dev) if topology != "single" else None
        if b is not None:
            now[0] = 1005.0
            tg.start_soon(b.run)
            await b.opened.wait()
            assert b.gap is None  # A is live: coverage is continuous
        now[0] = 1010.0
        camera.sockets[0].push_bytes(b"d")
        assert await a.receive(timeout=5) == b"d"
        if b is not None:
            now[0] = 1015.0
            camera.sockets[1].push_bytes(b"d")
            b.cmd_receive.set()
            await b.received.wait()
        now[0] = 1020.0
        _trigger(cause, camera.sockets[0])
        await anyio.sleep(0.4)
        if b is not None:
            now[0] = 1090.0
            b.cmd_close.set()
            await b.closed.wait()

        finalized_at = {"single": 1100.0, "overlap_AB": 1100.0, "overlap_BA": 1110.0}[topology]

        async def finalize_a(at: float) -> None:
            now[0] = at
            if mode == "read":
                if cause == "local_close":
                    await a.close()
                else:
                    if cause == "send_failure":
                        _break_async_send(a)
                    with pytest.raises(EXPECTED_ERROR[cause]):
                        if cause == "send_failure":
                            await a.send(b"x")
                        else:
                            await a.receive(timeout=5)
            elif mode == "unread_close":
                await a.close()
            await cm_a.__aexit__(None, None, None)

        async def finalize_b(at: float) -> None:
            now[0] = at
            assert b is not None
            b.cmd_exit.set()
            await b.exited.wait()

        if mode == "unread_reaped":
            if topology == "overlap_BA":
                await finalize_b(1100.0)
        elif topology == "overlap_BA":
            await finalize_b(1100.0)
            await finalize_a(finalized_at)
        else:
            await finalize_a(1100.0)
            if b is not None:
                await finalize_b(1110.0)

        now[0] = 1200.0
        async with dev.connect_session(RAW, heartbeat=QUICK) as c:
            assert c.gap is not None
            assert c.gap.start.timestamp() == _expected_start(cause, topology, finalized_at)
            assert c.gap.end.timestamp() == 1200.0
            now[0] = 1210.0
        if mode == "unread_reaped":
            await cm_a.__aexit__(None, None, None)
            if topology == "overlap_AB":
                await finalize_b(1220.0)


def _break_async_send(session: Any) -> None:
    async def fail(*args: Any, **kwargs: Any) -> None:
        raise wsproto.utilities.LocalProtocolError("connection is closed")

    session._raw.send_bytes = fail  # noqa: SLF001


# -- round 12 regressions ------------------------------------------------------------------------


def test_round12_unread_failure_then_close_keeps_the_gap(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unread 1011 followed by close() or context exit must not erase the gap."""
    now = _setup(monkeypatch)
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=4) as dev:
        dev._ledger.now = lambda: now[0]  # noqa: SLF001
        with dev.connect_session(RAW, heartbeat=QUICK) as a:
            now[0] = 1010.0
            camera.sockets[0].push_bytes(b"d")
            a.receive(timeout=5)
            now[0] = 1020.0
            camera.sockets[0].close(1011)
            time.sleep(0.3)
            now[0] = 1100.0
            a.close()
        now[0] = 1200.0
        with dev.connect_session(RAW, heartbeat=QUICK) as again:
            assert again.gap is not None and again.gap.start.timestamp() == 1010.0


def test_round12_overlapping_stale_finalization_does_not_rewind(monkeypatch: pytest.MonkeyPatch) -> None:
    """A (old) is finalized after B (newer) ended later: the newer coverage must stay."""
    now = _setup(monkeypatch)
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=4) as dev:
        dev._ledger.now = lambda: now[0]  # noqa: SLF001
        cm_a = dev.connect_session(RAW, heartbeat=QUICK)
        cm_a.__enter__()
        now[0] = 1005.0
        cm_b = dev.connect_session(RAW, heartbeat=QUICK)
        cm_b.__enter__()
        now[0] = 1500.0
        cm_b.__exit__(None, None, None)  # B ended at 1500 ...
        now[0] = 1600.0
        cm_a.__exit__(None, None, None)  # ... then A, a stale session, is finalized at 1600
        now[0] = 1700.0
        with dev.connect_session(RAW, heartbeat=QUICK) as c:
            assert c.gap is not None and c.gap.start.timestamp() == 1600.0
