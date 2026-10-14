"""The terminal outcome is published once under a lock; the gap ledger forgets finished keys beyond a cap."""

from __future__ import annotations

import threading

from ws_fake import FakeWsCamera

from ax_devil_device_api import Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime.ws import EVENTS, SessionLedger
from ax_devil_device_api.errors import ConnectionFailed, SessionClosed

QUICK = Heartbeat(None)


def test_racing_reader_and_closer_publish_exactly_one_outcome() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=64) as dev:
        for _ in range(60):
            with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
                core = session._core  # noqa: SLF001
                barrier = threading.Barrier(3)
                got: list[BaseException] = []

                def reader() -> None:
                    barrier.wait()
                    got.append(core.fail_with(ConnectionFailed("lost")))

                def closer() -> None:
                    barrier.wait()
                    got.append(core.publish_outcome(SessionClosed(1000, "closed")))  # type: ignore[arg-type]

                def other() -> None:
                    barrier.wait()
                    got.append(core.on_network_error())

                threads = [threading.Thread(target=fn) for fn in (reader, closer, other)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(5)
                stored = core.closed if core.closed is not None else core.failure
                assert stored is not None and len(got) == 3
                assert all(outcome is stored for outcome in got)  # every caller got the one winning exception
                assert (core.closed is None) != (core.failure is None)  # and only one of the two slots was set


def test_ledger_caps_finished_keys_and_never_evicts_an_open_session() -> None:
    now = [100.0]
    ledger = SessionLedger(clock=lambda: now[0], max_folded=3)
    first, _ = ledger.open("a", lambda: None)
    for key in ("b", "c", "d", "e"):
        record, _ = ledger.open(key, lambda: None)
        now[0] += 1
        ledger.end(record)
    assert len(ledger._folded) <= 3  # noqa: SLF001
    ledger.end(first)  # "a" was open the whole time and is folded last: it is remembered
    _, gap = ledger.open("a", lambda: None)
    assert gap is not None
    _, evicted = ledger.open("b", lambda: None)
    assert evicted is None  # the oldest finished key was forgotten: unknown, reported like a first connect
    _, remembered = ledger.open("e", lambda: None)
    assert remembered is not None
