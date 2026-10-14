"""WebSocket sessions: event streams and Device Data Hub.

A session is not a request/response flow. ``connect_session`` (sync) and
``connect_session_async`` open one, run the spec's setup requests
(``events:configure``, ``data-hub_v1:subscribe``) and hand out a ``Session`` /
``AsyncSession``. The socket loop is httpx-ws's; message shapes live in
``ws_codecs`` and are sans-IO. ``Device.connect_session`` is the entry point.

Liveness and gaps (the contract):

- Liveness is a WebSocket ping every ``Heartbeat.interval`` seconds; a missing
  pong ends the session with ``ConnectionFailed``. The APIs have no
  application heartbeat and an idle stream is normal, so silence alone is
  never an error.
- A session ends *normally* when the device closes with code 1000 or 1001
  (iteration stops; ``receive()`` raises ``SessionClosed``), or when the
  application leaves the ``with`` block. Anything else (network error, ping
  timeout, other close code) raises a ``TransportError``.
- Events are not replayed. The device remembers, per session key (endpoint and
  query), when the previous session stopped receiving: the close time for a
  normal end, the last frame received (or the connect time) for an abnormal
  end. A later session for the same key starts with ``session.gap`` set to a
  ``Gap(start, end)``; the first session, and sessions that overlap another
  open one, have ``gap=None``. Reconnect policy is the application's.
"""

from __future__ import annotations

import asyncio
import json
import logging
import queue
import threading
import time
from collections import deque
from collections.abc import AsyncIterator, Callable, Iterator, Mapping, Sequence
from contextlib import AsyncExitStack, ExitStack, asynccontextmanager, contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import quote

import anyio
import httpcore
import httpx_ws
import wsproto.events
import wsproto.utilities

from .._http.options import DEFAULT_HEARTBEAT, Heartbeat
from .._http.transport import (
    LIMIT_CLOSE_CODE,
    LIMIT_CLOSE_REASON,
    MAX_WS_MESSAGE_BYTES,
    WS_QUEUE_SIZE,
    AsyncTransport,
    SyncTransport,
    UpgradeRefused,
)
from .._http.types import Request, Response
from .._protocols.base import CallFlow
from .._validate import optional_non_negative_finite, optional_positive_finite
from ..errors import (
    AuthError,
    ConnectionFailed,
    DeviceError,
    HttpAccessDenied,
    HttpError,
    HttpUnavailable,
    NotSupported,
    ReadTimeout,
    ResponseFormatError,
    SessionClosed,
    TransportError,
)
from .driver import Call, run_async, run_sync
from .ws_codecs import (
    DataHubCodec,
    EventsCodec,
    Notification,
    Reply,
    WsCodec,
    api_error,
    datahub_setup,
    events_setup,
)

_NORMAL_CLOSE = (1000, 1001)

Setup = Callable[[Mapping[str, Any]], Sequence[tuple[str, Mapping[str, Any] | None]]]


# ---------------------------------------------------------------------------
# Description of a session endpoint


@dataclass(frozen=True)
class SessionSpec:
    """What the generated API layer binds to: an endpoint, its codec and its setup."""

    api_id: str
    path: str
    query: tuple[tuple[str, str], ...] = ()
    codec: WsCodec | None = None
    """``None`` for raw sessions (binary audio): frames pass through, JSON is not decoded."""
    setup: Setup | None = None
    """Maps ``connect(**options)`` to requests sent before the session is returned."""
    token_path: str = "/axis-cgi/wssession.cgi"

    @property
    def key(self) -> tuple[Any, ...]:
        return (self.path, tuple(sorted(self.query)))

    def bind(self, values: Mapping[str, Any]) -> SessionSpec:
        """A copy with the ``{name}`` placeholders of ``path`` filled in (percent-encoded, one path segment each)."""
        for name, value in values.items():
            if str(value) in ("", ".", ".."):
                raise ValueError(f"{self.api_id}: {name}={str(value)!r} is not a valid path segment")
        try:
            path = self.path.format(**{name: quote(str(value), safe="") for name, value in values.items()})
        except KeyError as missing:
            raise TypeError(f"{self.api_id}: no value for the path placeholder {missing}") from None
        return replace(self, path=path)


EVENTS = SessionSpec(
    "event-streaming-over-websocket", "/vapix/ws-data-stream", (("sources", "events"),), EventsCodec(), events_setup
)
DATA_HUB = SessionSpec(
    "datahub-streaming-over-websocket", "/vapix/ws/v1", (("apis", "data-hub"),), DataHubCodec(), datahub_setup
)


# ---------------------------------------------------------------------------
# Gaps


@dataclass(frozen=True)
class Gap:
    """Time during which a session for the same endpoint was not receiving."""

    start: datetime
    end: datetime

    @property
    def duration(self) -> float:
        return (self.end - self.start).total_seconds()


def _utc(stamp: float) -> datetime:
    return datetime.fromtimestamp(stamp, tz=UTC)


Cause = Literal["normal_remote", "local_close", "abnormal_remote", "network", "oversize", "send_failure"]
"""Why a session ended: a 1000/1001 close frame, our own close, any other close code, a transport error,
the 8 MiB message limit, or a failed send."""
_COVERED_UNTIL_TERMINATION: tuple[str, ...] = ("normal_remote", "local_close")


@dataclass
class _Record:
    """One session as the ledger knows it."""

    key: Any
    opened_ts: float
    last_frame_ts: float
    """The last data frame received: the last evidence that the session was alive."""
    termination: tuple[Cause, int | None, float] | None = None
    """``(cause, code, ts)``, set once by whichever layer observes the end first."""
    ended: bool = False
    poll: Callable[[], None] | None = None

    def coverage_end(self) -> float:
        """Until when this session is known to have been receiving."""
        if self.termination is not None and self.termination[0] in _COVERED_UNTIL_TERMINATION:
            return self.termination[2]
        return self.last_frame_ts


class SessionLedger:
    """Per-device record of sessions, from which the gap of a new session is *computed*. Thread-safe.

    Nothing is overwritten: each session has its own record, a termination is set once, and the gap of a new
    session for a key is derived from all earlier records, so the order in which sessions are finalized does not
    matter. A new session has no gap while another one for the key is still live (coverage is continuous) and for
    the first connect; otherwise the gap runs from the latest coverage end of the earlier sessions. Finished
    records are folded into one number per key, so memory stays bounded.
    """

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self.now = clock
        self._lock = threading.Lock()
        self._open: dict[Any, list[_Record]] = {}
        self._folded: dict[Any, float] = {}

    def open(self, key: Any, poll: Callable[[], None]) -> tuple[_Record, Gap | None]:
        with self._lock:
            known = list(self._open.get(key, ()))
        for record in known:  # sessions whose socket died but nobody noticed yet terminate here
            if record.termination is None and record.poll is not None:
                record.poll()
        now = self.now()
        with self._lock:
            records = self._open.setdefault(key, [])
            gap: Gap | None = None
            live = any(r.termination is None for r in records)
            if not live and (records or key in self._folded):
                start = max([r.coverage_end() for r in records] + [self._folded.get(key, float("-inf"))])
                gap = Gap(_utc(min(start, now)), _utc(now))
            record = _Record(key, now, now, poll=poll)
            records.append(record)
            return record, gap

    def touch(self, record: _Record, ts: float) -> None:
        with self._lock:
            if not record.ended and record.termination is None:
                record.last_frame_ts = max(record.last_frame_ts, ts)

    def terminate(self, record: _Record, cause: Cause, code: int | None, ts: float) -> None:
        """Record why the session ended; a no-op if a termination is already set."""
        with self._lock:
            if record.termination is None:
                record.termination = (cause, code, ts)

    def end(self, record: _Record) -> None:
        """The session object is finished (the ``with`` block exited). Never invents a time: without a recorded
        termination the session ended by our own close, now."""
        with self._lock:
            if record.ended:
                return
            if record.termination is None:
                record.termination = ("local_close", None, self.now())
            record.ended = True
            records = self._open.get(record.key, [])
            if record in records:
                records.remove(record)
            self._folded[record.key] = max(self._folded.get(record.key, float("-inf")), record.coverage_end())

    # -- inspection (tests, diagnostics) --

    def live(self, key: Any) -> int:
        with self._lock:
            return sum(1 for r in self._open.get(key, ()) if r.termination is None)

    def coverage(self, key: Any) -> float | None:
        """Latest coverage end over the finished and terminated sessions of ``key`` (``None`` if there are none)."""
        with self._lock:
            ends = [r.coverage_end() for r in self._open.get(key, ()) if r.termination is not None]
            if key in self._folded:
                ends.append(self._folded[key])
            return max(ends) if ends else None


# ---------------------------------------------------------------------------
# Shared (I/O free) session logic


_POLL_SLICE = 0.1
"""Longest blocking wait for the transport before the reader looks at the session's terminal state again (a close or
failure published by another thread or task interrupts the owning read within this time)."""

NO_MESSAGE: Any = object()
"""Private marker for "no complete message yet" (control frame, unfinished fragment); never a real message, ``None`` included."""


_log = logging.getLogger(__name__)


class _Slot:
    """The outcome of one outstanding request, filled in by whoever reads its reply."""

    def __init__(self, method: str) -> None:
        self.method = method
        self.done = False
        self.value: Any = None
        self.error: Exception | None = None

    def poll(self) -> Any:
        if not self.done:
            return NO_MESSAGE
        if self.error is not None:
            raise self.error
        return self.value


class _Core:
    def __init__(self, spec: SessionSpec, ledger: SessionLedger, response: Response, default_timeout: float) -> None:
        self.spec = spec
        self.ledger = ledger
        self.response = response
        self.default_timeout = default_timeout
        self.gap: Gap | None = None
        self.record: _Record | None = None
        self._begun = False
        self._parts: list[Any] = []
        self._parts_size = 0
        self.pending: deque[Any] = deque()
        self.dropped = 0
        self._overflowing = False
        self.closed: SessionClosed | None = None
        self.overflowed = False
        self._counter = 0
        self._ended = False
        self._reader_over: Callable[[], bool] | None = None
        self._raw: Any = None
        self.closing = False
        self.failure: TransportError | None = None
        self.local_closed = False

    def begin(self) -> None:
        """Enter the gap ledger. Called once setup has succeeded, so a failed attempt leaves no trace."""
        if not self._begun and not self._ended:
            self._begun = True
            self.record, self.gap = self.ledger.open(self.spec.key, self._poll_reader)
            self._poll_reader()  # the socket may have died during setup

    def watch_reader(self, raw: Any) -> None:
        """Follow the socket's background reader: when it terminated (a private httpx-ws signal)."""
        self._raw = raw
        self._reader_over = lambda: bool(getattr(raw, "_should_close").is_set())  # noqa: B009

    @property
    def _connection(self) -> Any:
        return getattr(self._raw, "connection", None)

    @property
    def remote_close(self) -> tuple[int, float] | None:
        """``(code, arrival time)`` of the device's close frame, as recorded by the transport's connection wrapper."""
        return getattr(self._connection, "remote_close", None)

    @property
    def write_failed(self) -> bool:
        return bool(getattr(getattr(self._raw, "stream", None), "write_failed", False))

    def _frame_time(self) -> float:
        return getattr(self._connection, "last_frame", None) or self.ledger.now()

    def _poll_reader(self) -> None:
        """If the reader terminated, record why (whatever the app has or has not read yet). A no-op once recorded."""
        record = self.record
        if record is None or record.ended or record.termination is not None:
            return
        closed = self.remote_close  # stamped by the transport as the frame arrived, even before the reader flags its end
        if closed is not None:
            self._record(record, "normal_remote" if closed[0] in _NORMAL_CLOSE else "abnormal_remote", closed[0], closed[1])
            return
        if self.write_failed:
            self._record(record, "network", None, None)  # a write that failed: the connection is broken
        elif self.closing:
            return  # the reader flag is our own close's doing, not evidence of anything
        elif self._reader_over is not None and self._reader_over():
            self._record(record, "network", None, None)

    def _record(self, record: _Record, cause: Cause, code: int | None, ts: float | None) -> None:
        seen = getattr(self._connection, "last_frame", None)
        if seen is not None:
            self.ledger.touch(record, seen)
        self.ledger.terminate(record, cause, code, self.ledger.now() if ts is None else ts)

    def closing_now(self) -> None:
        """We are about to close the socket: an end the reader already saw is recorded first."""
        self._poll_reader()
        self.closing = True

    def terminate(self, cause: Cause, code: int | None = None, ts: float | None = None) -> None:
        """Every observer reports the end of the session here; the first report wins."""
        if self.record is None:
            return  # never entered the ledger: a failed setup leaves no trace
        self._poll_reader()  # an end the reader already saw comes first
        self._record(self.record, cause, code, ts)

    def next_id(self) -> str:
        self._counter += 1
        return f"ax-{self._counter}"

    def decode(self, event: wsproto.events.Event) -> Any:
        """Turn a wsproto message into a Python value; ``NO_MESSAGE`` for control frames and unfinished messages.

        A complete JSON ``null`` is a message like any other and decodes to ``None``.
        """
        if not isinstance(event, (wsproto.events.BytesMessage, wsproto.events.TextMessage)):
            return NO_MESSAGE
        if self.record is not None and not self._ended:
            self.ledger.touch(self.record, self._frame_time())
        is_text = isinstance(event, wsproto.events.TextMessage)
        self._parts.append(event.data if is_text else bytes(event.data))
        self._parts_size += len(event.data.encode("utf-8")) if is_text else len(event.data)
        if self._parts_size > MAX_WS_MESSAGE_BYTES:
            self._parts.clear()
            self._parts_size = 0
            raise self._too_large()
        if not event.message_finished:
            return NO_MESSAGE
        parts, self._parts, self._parts_size = self._parts, [], 0
        if not is_text:
            return b"".join(parts)
        text = "".join(parts)
        if self.spec.codec is None:
            return text
        try:
            return json.loads(text)
        except ValueError as error:
            raise ResponseFormatError(self.spec.api_id, "receive", f"invalid JSON message: {error}") from error

    def encode(self, message: Any) -> str | bytes:
        if isinstance(message, (bytes, bytearray)):
            return bytes(message)
        if isinstance(message, str):
            return message
        try:
            return json.dumps(message, allow_nan=False)
        except ValueError as error:  # NaN / infinity: JSON has no representation; nothing is sent
            raise ValueError("NaN and infinity cannot be sent: JSON has no representation for them") from error

    def overflow_closed(self) -> SessionClosed:
        return SessionClosed(LIMIT_CLOSE_CODE, LIMIT_CLOSE_REASON)

    def _too_large(self) -> ResponseFormatError:
        self.overflowed = True
        self.terminate("oversize", LIMIT_CLOSE_CODE)
        return ResponseFormatError(self.spec.api_id, "receive", f"message exceeds {MAX_WS_MESSAGE_BYTES} bytes; session closed")

    def close_locally(self) -> None:
        """Publish our own ``close()`` as the terminal outcome: pending and later reads raise ``SessionClosed``."""
        if self.closed is None and self.failure is None:
            self.closed = SessionClosed(1000, "closed by this client")
            self.local_closed = True

    def on_disconnect(self, error: httpx_ws.WebSocketDisconnect) -> DeviceError:
        if self.local_closed and self.closed is not None:
            return self.closed  # the transport errors that follow our own close are not failures
        if error.code == LIMIT_CLOSE_CODE and error.reason == LIMIT_CLOSE_REASON:
            return self._too_large()
        if error.code in _NORMAL_CLOSE:
            self.closed = SessionClosed(error.code, error.reason)
            self.terminate("normal_remote", error.code)
            return self.closed
        self.terminate("abnormal_remote", error.code)
        return self._fail(ConnectionFailed(f"{self.spec.api_id}: device closed the session with code {error.code}: {error.reason}"))

    def send_refused(self) -> DeviceError:
        """The error for a send the protocol layer refused: the connection is closed.

        A close frame the transport already stamped is mapped like one the app received (a real ``TransportError``
        for an abnormal code); only without any close, or after a normal one, is it ``SessionClosed``.
        """
        if self.closed is not None:
            return self.closed
        if self.failure is not None:
            return self.failure
        stamped = self.remote_close
        if stamped is not None:
            return self.on_disconnect(httpx_ws.WebSocketDisconnect(stamped[0], ""))
        self.terminate("send_failure")
        outcome = SessionClosed()
        self.closed = outcome  # stored (set-once): every current and later read raises it, not only this send
        return outcome

    def on_network_error(self) -> DeviceError:
        if self.local_closed and self.closed is not None:
            return self.closed
        self.terminate("network")
        return self._fail(ConnectionFailed(f"{self.spec.api_id}: connection lost (network error or heartbeat timeout)"))

    def _fail(self, error: TransportError) -> TransportError:
        self.failure = error  # the terminal event is queued once: later reads raise this again
        return error

    def dispatch(self, message: Any, waiters: dict[str, _Slot]) -> None:
        """Route one decoded frame: the reply to a registered request goes to that request, everything else
        (notifications, unmatched replies, other frames) is queued for ``receive()`` / ``notifications()``."""
        codec = self.spec.codec
        kind = codec.classify(message) if codec is not None else None
        if isinstance(kind, Reply) and kind.request_id in waiters:
            slot = waiters[kind.request_id]
            if kind.error is not None and codec is not None:
                slot.error = api_error(codec, slot.method, kind.error)
            else:
                slot.value = kind.result
            slot.done = True
            return
        if len(self.pending) >= WS_QUEUE_SIZE:
            # Nobody is draining the queue (a request is waiting for its reply, or the app is slow): keep the newest,
            # drop the oldest, and keep reading so replies are always dispatched.
            self.pending.popleft()
            self.dropped += 1
            if not self._overflowing:
                self._overflowing = True
                _log.warning(
                    "%s: %d unread messages; dropping the oldest ones (see Session.dropped_notifications)",
                    self.spec.api_id, WS_QUEUE_SIZE,
                )
        self.pending.append(message)

    def take_pending(self) -> Any:
        """The oldest queued message, or ``NO_MESSAGE``."""
        if not self.pending:
            return NO_MESSAGE
        message = self.pending.popleft()
        if len(self.pending) < WS_QUEUE_SIZE:
            self._overflowing = False  # the next overflow is a new episode with its own warning
        return message

    def notification(self, message: Any) -> Notification | None:
        codec = self.spec.codec
        if codec is None:
            return None
        kind = codec.classify(message)
        return kind if isinstance(kind, Notification) else None

    def request_message(self, method: str, params: Mapping[str, Any] | None) -> tuple[str, dict[str, Any]]:
        codec = self.spec.codec
        if codec is None:
            raise TypeError(f"{self.spec.api_id} is a raw session; it has no request/response messages")
        request_id = self.next_id()
        return request_id, codec.encode_request(method, params, request_id)

    def finish(self, *, user_exit_error: BaseException | None) -> None:
        """The session object is done. Only marks it ended: the termination was recorded by whoever saw the end."""
        if self._ended:
            return
        self._ended = True
        if self.record is None:
            return
        self._poll_reader()  # an unread end must not be mistaken for our own close
        self.ledger.end(self.record)


_CLOSE_ERRORS = (httpx_ws.WebSocketNetworkError, httpcore.WriteError, httpcore.NetworkError, wsproto.utilities.LocalProtocolError)
"""What closing an already dead connection can raise: closing it is then a no-op, never an error for the caller."""


def _check_receive_timeout(timeout: float | None) -> None:
    """``receive`` timeouts are finite and 0 or more (0 polls); ``None`` waits as long as the session lives."""
    optional_non_negative_finite("timeout", timeout)


def refusal_error(spec: SessionSpec, response: Response) -> DeviceError:
    """The error for a handshake the device did not accept."""
    status = response.status
    if status == 401:
        return AuthError(f"{spec.api_id}: the device requires authentication and no usable credentials were configured")
    if status == 403:
        return HttpAccessDenied(status, response.excerpt(), api=spec.api_id, operation="connect")
    if status == 503:
        return HttpUnavailable(status, response.excerpt(), api=spec.api_id, operation="connect")
    if status == 404:
        return NotSupported(spec.api_id, None, f"{response.request.path} not found (HTTP 404): the device has no such WebSocket endpoint")
    return HttpError(status, response.excerpt(), api=spec.api_id, operation="connect")


def _setup_requests(spec: SessionSpec, options: Mapping[str, Any]) -> Sequence[tuple[str, Mapping[str, Any] | None]]:
    if spec.setup is not None:
        return spec.setup(options)
    if options:
        raise TypeError(f"{spec.api_id} takes no connect arguments: {sorted(options)}")
    return ()


def _token_flow(spec: SessionSpec) -> CallFlow[str]:
    response = yield Request("GET", spec.token_path, accept="text/plain")
    if response.status != 200:
        raise refusal_error(spec, response)  # judged by status first: an error page is never decoded as a token
    token = response.text.strip()
    if not token:
        raise ResponseFormatError(
            spec.api_id, "wssession", "the device returned an empty session token"
        )
    return token


# ---------------------------------------------------------------------------
# Sync


class Session:
    """A blocking WebSocket session. Obtain it from ``Device.connect_session``.

    Iterating yields every received message (decoded JSON, ``str`` or
    ``bytes``) until the device closes normally. ``notifications()`` yields
    only the codec's parsed notifications. Not safe to read from several
    threads at once; ``send`` may be called from another thread.
    """

    def __init__(self, raw: httpx_ws.WebSocketSession, core: _Core) -> None:
        self._raw = raw
        self._core = core
        self._cond = threading.Condition()
        self._reading = False
        self._waiters: dict[str, _Slot] = {}
        core.watch_reader(raw)

    @property
    def dropped_notifications(self) -> int:
        """Messages dropped (oldest first) because more than ``WS_QUEUE_SIZE`` were waiting unread."""
        return self._core.dropped

    @property
    def gap(self) -> Gap | None:
        """Set if an earlier session for this endpoint ended before this one began (events in between are lost)."""
        return self._core.gap

    @property
    def response(self) -> Response:
        """The handshake response."""
        return self._core.response

    def send(self, message: Any) -> None:
        """Send ``bytes`` as a binary frame, ``str`` as text, anything else as JSON text."""
        if self._core.overflowed:
            raise self._core.overflow_closed()
        data = self._core.encode(message)
        try:
            if isinstance(data, bytes):
                self._raw.send_bytes(data)
            else:
                self._raw.send_text(data)
        except wsproto.utilities.LocalProtocolError as error:
            outcome = self._core.send_refused()
            self._publish()
            raise outcome from error
        except (httpx_ws.WebSocketNetworkError, httpcore.WriteError, httpcore.NetworkError) as error:
            outcome = self._core.on_network_error()
            self._publish()
            raise outcome from error

    def _publish(self) -> None:
        """A terminal outcome is stored on the core: wake every waiter (the reader owner notices within a poll slice)."""
        with self._cond:
            self._cond.notify_all()

    def receive(self, timeout: float | None = None) -> Any:
        """The next message. ``ReadTimeout`` after ``timeout`` seconds; ``SessionClosed`` after a normal end."""
        core = self._core
        _check_receive_timeout(timeout)
        return self._await(core.take_pending, timeout)

    def _await(self, poll: Callable[[], Any], timeout: float | None) -> Any:
        """Wait until ``poll()`` yields something other than ``NO_MESSAGE``.

        Reads go through one reader at a time (``_reading``): whoever finds nobody reading reads the next frame and
        dispatches it (a reply to its request, a notification to the queue, ...); the others wait to be woken.
        An error that ends the session is raised by whichever reader meets it, and wakes the rest, which meet it too.
        """
        core = self._core
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._cond:
            while True:
                found = poll()
                if found is not NO_MESSAGE:
                    return found
                if core.failure is not None:
                    raise core.failure  # terminal state first, before any wait
                if core.closed is not None:
                    raise core.closed
                remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
                if self._reading:
                    if remaining == 0:
                        raise ReadTimeout(f"{core.spec.api_id}: no message within {timeout} s")
                    self._cond.wait(remaining)
                    continue
                self._reading = True
                self._cond.release()
                try:
                    frame = self._read(remaining)
                finally:
                    self._cond.acquire()
                    self._reading = False
                    self._cond.notify_all()
                core.dispatch(frame, self._waiters)
                self._cond.notify_all()

    def _read(self, timeout: float | None) -> Any:
        core = self._core
        if core.closed is not None:
            raise core.closed
        if core.failure is not None:
            raise core.failure
        if core.overflowed:
            raise core.overflow_closed()
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
            try:
                event = self._raw.receive(_POLL_SLICE if remaining is None else min(remaining, _POLL_SLICE))
            except queue.Empty:
                if core.failure is not None:
                    raise core.failure from None
                if core.closed is not None:
                    raise core.closed from None
                if deadline is not None and time.monotonic() >= deadline:
                    raise ReadTimeout(f"{core.spec.api_id}: no message within {timeout} s") from None
                continue
            except httpx_ws.WebSocketDisconnect as error:
                raised = core.on_disconnect(error)
                if core.overflowed:
                    self._abort()
                raise raised from None
            except httpx_ws.WebSocketNetworkError:
                raise core.on_network_error() from None
            try:
                message = core.decode(event)
            except ResponseFormatError:
                if core.overflowed:
                    self._abort()
                raise
            if message is not NO_MESSAGE:
                return message

    def _abort(self) -> None:
        """Close the transport with 1009 after an oversized message (the context exit then sends nothing more)."""
        try:
            self._raw.close(LIMIT_CLOSE_CODE, LIMIT_CLOSE_REASON)
        except (httpx_ws.WebSocketNetworkError, httpcore.WriteError, httpcore.NetworkError, wsproto.utilities.LocalProtocolError):
            pass

    def request(self, method: str, params: Mapping[str, Any] | None = None, *, timeout: float | None = None) -> Any:
        """Send a request and return its result; other messages that arrive meanwhile stay queued for ``receive()``."""
        core = self._core
        if timeout is not None:
            optional_positive_finite("timeout", timeout)  # nothing is sent otherwise
        limit = core.default_timeout if timeout is None else timeout
        deadline = time.monotonic() + limit  # the caller's total budget: registration, sending and waiting
        slot = _Slot(method)
        with self._cond:
            request_id, message = core.request_message(method, params)
            self._waiters[request_id] = slot  # registered before the request is sent, so its reply cannot be missed
        try:
            self.send(message)
            return self._await(slot.poll, max(0.0, deadline - time.monotonic()))
        finally:
            with self._cond:
                self._waiters.pop(request_id, None)

    def __iter__(self) -> Iterator[Any]:
        while True:
            try:
                yield self.receive()
            except SessionClosed:
                return

    def notifications(self) -> Iterator[Any]:
        """Parsed notifications (``EventNotification``, ``TopicSample``); replies and unknown messages are skipped."""
        for message in self:
            found = self._core.notification(message)
            if found is not None:
                yield found.item

    def close(self) -> None:
        self._core.closing_now()  # before the socket closes, so it is not mistaken for a failure
        self._core.close_locally()
        self._publish()  # pending requests and the reader owner see SessionClosed now, not at their timeout
        try:
            self._raw.close()
        except _CLOSE_ERRORS:
            self._core.terminate("network")  # the connection was already dead; closing it again is a no-op
        else:
            self._core.terminate("network" if self._core.write_failed else "local_close")


@contextmanager
def connect_session(
    transport: SyncTransport,
    ledger: SessionLedger,
    call: Call,
    spec: SessionSpec,
    options: Mapping[str, Any],
    *,
    heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
    use_token: bool = False,
) -> Iterator[Session]:
    """Open a session: optional token, handshake (retried when it provably never left), setup requests."""
    setup = _setup_requests(spec, options)
    query = spec.query
    attempt = 1
    stack = ExitStack()
    while True:
        # The token is valid for 15 seconds only: every handshake attempt, a retry included, gets a fresh one.
        attempt_query = (("wssession", run_sync(transport, _token_flow(spec), call)),) + query if use_token else query
        request = call.prepare(Request("GET", spec.path, query=attempt_query, auth="anonymous" if use_token else "required"))
        started = time.monotonic()
        try:
            response, raw = stack.enter_context(transport.open_ws(request, heartbeat))
        except UpgradeRefused as refused:
            call.observe(request, refused.response, None, started, attempt)
            raise refusal_error(spec, refused.response) from None
        except TransportError as error:
            call.observe(request, None, error, started, attempt)
            if not call.should_retry(request, error, attempt):
                raise
            time.sleep(call.retry.delay(attempt))
            attempt += 1
            continue
        except Exception as error:
            call.observe(request, None, error, started, attempt)  # e.g. AuthError: still one record
            raise
        try:
            call.observe(request, response, None, started, attempt)
        except BaseException:
            stack.close()  # a raising hook must not leak the open connection and its stream slot
            raise
        break
    core = _Core(spec, ledger, response, call.timeout if call.timeout is not None else transport.config.timeout)
    session = Session(raw, core)
    error: BaseException | None = None
    try:
        with stack:
            try:
                for method, params in setup:
                    session.request(method, params)
                core.begin()
                yield session
            except BaseException as exc:  # noqa: BLE001 - recorded, re-raised
                error = exc
                raise
            finally:
                # Leaving the context closes the socket next: record that this end is ours (an end already seen wins).
                core.closing_now()  # the socket closes next; finish() records how it ended
    finally:
        core.finish(user_exit_error=error)


# ---------------------------------------------------------------------------
# Async


class AsyncSession:
    """Async counterpart of ``Session``: ``async for`` over messages, ``await`` for the rest."""

    def __init__(self, raw: httpx_ws.AsyncWebSocketSession, core: _Core) -> None:
        self._raw = raw
        self._core = core
        self._reading = False
        self._changed = asyncio.Event()
        self._waiters: dict[str, _Slot] = {}
        core.watch_reader(raw)

    @property
    def dropped_notifications(self) -> int:
        """Messages dropped (oldest first) because more than ``WS_QUEUE_SIZE`` were waiting unread."""
        return self._core.dropped

    @property
    def gap(self) -> Gap | None:
        """Set if an earlier session for this endpoint ended before this one began (events in between are lost)."""
        return self._core.gap

    @property
    def response(self) -> Response:
        """The handshake response."""
        return self._core.response

    async def send(self, message: Any) -> None:
        """Send ``bytes`` as a binary frame, ``str`` as text, anything else as JSON text."""
        if self._core.overflowed:
            raise self._core.overflow_closed()
        data = self._core.encode(message)
        try:
            if isinstance(data, bytes):
                await self._raw.send_bytes(data)
            else:
                await self._raw.send_text(data)
        except wsproto.utilities.LocalProtocolError as error:
            outcome = self._core.send_refused()
            self._wake()
            raise outcome from error
        except (httpx_ws.WebSocketNetworkError, httpcore.WriteError, httpcore.NetworkError) as error:
            outcome = self._core.on_network_error()
            self._wake()
            raise outcome from error

    async def receive(self, timeout: float | None = None) -> Any:
        """The next message. ``ReadTimeout`` after ``timeout`` seconds; ``SessionClosed`` after a normal end."""
        core = self._core
        _check_receive_timeout(timeout)
        return await self._await(core.take_pending, timeout)

    def _wake(self) -> None:
        changed, self._changed = self._changed, asyncio.Event()
        changed.set()

    async def _await(self, poll: Callable[[], Any], timeout: float | None) -> Any:
        """Async counterpart of ``Session._await`` (one reader at a time; the loop is single-threaded, so the
        checks and the hand-over need no lock)."""
        core = self._core
        loop = asyncio.get_running_loop()
        deadline = None if timeout is None else loop.time() + timeout
        while True:
            found = poll()
            if found is not NO_MESSAGE:
                return found
            if core.failure is not None:
                raise core.failure  # terminal state first, before any wait
            if core.closed is not None:
                raise core.closed
            remaining = None if deadline is None else max(0.0, deadline - loop.time())
            if self._reading:
                if remaining == 0:
                    raise ReadTimeout(f"{core.spec.api_id}: no message within {timeout} s")
                changed = self._changed
                try:
                    await asyncio.wait_for(changed.wait(), remaining)
                except TimeoutError:
                    pass  # re-poll once; the deadline check above raises
                continue
            self._reading = True
            try:
                frame = await self._read(remaining)
            finally:
                self._reading = False
                self._wake()
            core.dispatch(frame, self._waiters)
            self._wake()

    async def _next_event(self, remaining: float | None) -> wsproto.events.Event:
        """The next wsproto event. With nothing left to wait (0) the buffer is only looked at, never awaited:
        AnyIO checkpoints before it reads, so ``fail_after(0)`` would time out even with a frame already queued."""
        stream = getattr(self._raw, "_receive_event", None)
        if remaining != 0 or stream is None:
            return await self._raw.receive(remaining)
        try:
            event = stream.receive_nowait()
        except anyio.WouldBlock:
            raise TimeoutError from None
        if isinstance(event, httpx_ws.HTTPXWSException):
            raise event
        if isinstance(event, wsproto.events.CloseConnection):
            raise httpx_ws.WebSocketDisconnect(event.code, event.reason)
        return event

    async def _read(self, timeout: float | None) -> Any:
        core = self._core
        if core.closed is not None:
            raise core.closed
        if core.failure is not None:
            raise core.failure
        if core.overflowed:
            raise core.overflow_closed()
        loop = asyncio.get_running_loop()
        deadline = None if timeout is None else loop.time() + timeout
        while True:
            remaining = None if deadline is None else max(0.0, deadline - loop.time())
            try:
                event = await self._next_event(_POLL_SLICE if remaining is None else min(remaining, _POLL_SLICE))
            except TimeoutError:
                if core.failure is not None:
                    raise core.failure from None
                if core.closed is not None:
                    raise core.closed from None
                if deadline is not None and loop.time() >= deadline:
                    raise ReadTimeout(f"{core.spec.api_id}: no message within {timeout} s") from None
                continue
            except httpx_ws.WebSocketDisconnect as error:
                raised = core.on_disconnect(error)
                if core.overflowed:
                    await self._abort()
                raise raised from None
            except httpx_ws.WebSocketNetworkError:
                raise core.on_network_error() from None
            try:
                message = core.decode(event)
            except ResponseFormatError:
                if core.overflowed:
                    await self._abort()
                raise
            if message is not NO_MESSAGE:
                return message

    async def _abort(self) -> None:
        """Close the transport with 1009 after an oversized message (the context exit then sends nothing more)."""
        try:
            await self._raw.close(LIMIT_CLOSE_CODE, LIMIT_CLOSE_REASON)
        except (httpx_ws.WebSocketNetworkError, httpcore.WriteError, httpcore.NetworkError, wsproto.utilities.LocalProtocolError):
            pass

    async def request(self, method: str, params: Mapping[str, Any] | None = None, *, timeout: float | None = None) -> Any:
        """Send a request and return its result; other messages that arrive meanwhile stay queued for ``receive()``."""
        core = self._core
        if timeout is not None:
            optional_positive_finite("timeout", timeout)
        limit = core.default_timeout if timeout is None else timeout
        deadline = asyncio.get_running_loop().time() + limit  # the caller's total budget
        request_id, message = core.request_message(method, params)
        slot = _Slot(method)
        self._waiters[request_id] = slot  # registered before the request is sent, so its reply cannot be missed
        try:
            await self.send(message)
            return await self._await(slot.poll, max(0.0, deadline - asyncio.get_running_loop().time()))
        finally:
            self._waiters.pop(request_id, None)

    async def __aiter__(self) -> AsyncIterator[Any]:
        while True:
            try:
                yield await self.receive()
            except SessionClosed:
                return

    async def notifications(self) -> AsyncIterator[Any]:
        """Parsed notifications (``EventNotification``, ``TopicSample``); replies and unknown messages are skipped."""
        async for message in self:
            found = self._core.notification(message)
            if found is not None:
                yield found.item

    async def close(self) -> None:
        self._core.closing_now()
        self._core.close_locally()
        self._wake()
        try:
            await self._raw.close()
        except _CLOSE_ERRORS:
            self._core.terminate("network")
        else:
            self._core.terminate("network" if self._core.write_failed else "local_close")


@asynccontextmanager
async def connect_session_async(
    transport: AsyncTransport,
    ledger: SessionLedger,
    call: Call,
    spec: SessionSpec,
    options: Mapping[str, Any],
    *,
    heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
    use_token: bool = False,
) -> AsyncIterator[AsyncSession]:
    """Async counterpart of ``connect_session``."""
    setup = _setup_requests(spec, options)
    query = spec.query
    attempt = 1
    stack = AsyncExitStack()
    while True:
        attempt_query = (("wssession", await run_async(transport, _token_flow(spec), call)),) + query if use_token else query
        request = call.prepare(Request("GET", spec.path, query=attempt_query, auth="anonymous" if use_token else "required"))
        started = time.monotonic()
        try:
            response, raw = await stack.enter_async_context(transport.open_ws(request, heartbeat))
        except UpgradeRefused as refused:
            call.observe(request, refused.response, None, started, attempt)
            raise refusal_error(spec, refused.response) from None
        except TransportError as error:
            call.observe(request, None, error, started, attempt)
            if not call.should_retry(request, error, attempt):
                raise
            await asyncio.sleep(call.retry.delay(attempt))
            attempt += 1
            continue
        except Exception as error:
            call.observe(request, None, error, started, attempt)  # e.g. AuthError: still one record
            raise
        try:
            call.observe(request, response, None, started, attempt)
        except BaseException:
            await stack.aclose()  # a raising hook must not leak the open connection and its stream slot
            raise
        break
    core = _Core(spec, ledger, response, call.timeout if call.timeout is not None else transport.config.timeout)
    session = AsyncSession(raw, core)
    error: BaseException | None = None
    try:
        async with stack:
            try:
                for method, params in setup:
                    await session.request(method, params)
                core.begin()
                yield session
            except BaseException as exc:  # noqa: BLE001 - recorded, re-raised
                error = exc
                raise
            finally:
                # Leaving the context closes the socket next: record that this end is ours (an end already seen wins).
                core.closing_now()  # the socket closes next; finish() records how it ended
    finally:
        core.finish(user_exit_error=error)
