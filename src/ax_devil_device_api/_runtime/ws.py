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
import queue
import threading
import time
from collections import deque
from collections.abc import AsyncIterator, Callable, Iterator, Mapping, Sequence
from contextlib import AsyncExitStack, ExitStack, asynccontextmanager, contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import httpcore
import httpx_ws
import wsproto.events
import wsproto.utilities

from .._http.options import DEFAULT_HEARTBEAT, Heartbeat
from .._http.transport import (
    LIMIT_CLOSE_CODE,
    LIMIT_CLOSE_REASON,
    MAX_WS_MESSAGE_BYTES,
    AsyncTransport,
    SyncTransport,
    UpgradeRefused,
)
from .._http.types import Request, Response
from .._protocols.base import CallFlow
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
            if str(value) in (".", ".."):
                raise ValueError(f"{self.api_id}: path parameter {name!r} must not be {str(value)!r} (dot segments change the endpoint)")
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


@dataclass
class _Track:
    active: int = 0
    last_seen: float = 0.0
    ended_abnormally: bool = False


class SessionLedger:
    """Per-device memory of when each session key last received data. Thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tracks: dict[Any, _Track] = {}
        self._watchers: dict[Any, list[Callable[[], None]]] = {}

    def watch(self, key: Any, check: Callable[[], None]) -> None:
        """Register ``check`` for an active session; it ends the session's tracking if its reader has terminated."""
        with self._lock:
            self._watchers.setdefault(key, []).append(check)

    def unwatch(self, key: Any, check: Callable[[], None]) -> None:
        with self._lock:
            if check in self._watchers.get(key, []):
                self._watchers[key].remove(check)

    def begin(self, key: Any) -> Gap | None:
        with self._lock:
            checks = list(self._watchers.get(key, ()))
        for check in checks:  # a session whose socket died is not "open", even if nobody has read the close yet
            check()
        now = time.time()
        with self._lock:
            track = self._tracks.get(key)
            gap: Gap | None = None
            if track is None:
                track = self._tracks[key] = _Track()
            elif track.active == 0:
                gap = Gap(_utc(track.last_seen), _utc(now))
            track.active += 1
            track.last_seen = now
            return gap

    def touch(self, key: Any) -> None:
        with self._lock:
            track = self._tracks.get(key)
            if track is not None:
                track.last_seen = time.time()

    def end(self, key: Any, *, graceful: bool) -> None:
        """A session ended. Graceful: stamp now. Abnormal: keep the last frame time."""
        with self._lock:
            track = self._tracks.get(key)
            if track is None:
                return
            track.active = max(0, track.active - 1)
            if graceful:
                track.last_seen = time.time()


# ---------------------------------------------------------------------------
# Shared (I/O free) session logic


class _Core:
    def __init__(self, spec: SessionSpec, ledger: SessionLedger, response: Response, default_timeout: float) -> None:
        self.spec = spec
        self.ledger = ledger
        self.response = response
        self.default_timeout = default_timeout
        self.gap: Gap | None = None
        self._begun = False
        self._parts: list[Any] = []
        self._parts_size = 0
        self.pending: deque[Any] = deque()
        self.closed: SessionClosed | None = None
        self.failed = False
        self.overflowed = False
        self._counter = 0
        self._ended = False
        self._reader_over: Callable[[], bool] | None = None

    def begin(self) -> None:
        """Enter the gap ledger. Called once setup has succeeded, so a failed attempt leaves no trace."""
        if not self._begun and not self._ended:
            self._begun = True
            self.gap = self.ledger.begin(self.spec.key)
            self.ledger.watch(self.spec.key, self.check_alive)

    def watch_reader(self, is_over: Callable[[], bool]) -> None:
        """``is_over`` tells whether the socket's background reader has terminated (close frame, network error)."""
        self._reader_over = is_over

    def check_alive(self) -> None:
        """End tracking if the reader terminated, whatever the reason (abnormal: the gap starts at the last frame)."""
        if self._reader_over is not None and not self._ended and self._reader_over():
            self.failed = self.failed or self.closed is None
            self.finish(user_exit_error=None)

    def next_id(self) -> str:
        self._counter += 1
        return f"ax-{self._counter}"

    def decode(self, event: wsproto.events.Event) -> Any:
        """Turn a wsproto message into a Python value; ``None`` for non-message events."""
        if not isinstance(event, (wsproto.events.BytesMessage, wsproto.events.TextMessage)):
            return None
        if self._begun and not self._ended:
            self.ledger.touch(self.spec.key)
        is_text = isinstance(event, wsproto.events.TextMessage)
        self._parts.append(event.data if is_text else bytes(event.data))
        self._parts_size += len(event.data.encode("utf-8")) if is_text else len(event.data)
        if self._parts_size > MAX_WS_MESSAGE_BYTES:
            self._parts.clear()
            self._parts_size = 0
            raise self._too_large()
        if not event.message_finished:
            return None
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
        return json.dumps(message)

    def overflow_closed(self) -> SessionClosed:
        return SessionClosed(LIMIT_CLOSE_CODE, LIMIT_CLOSE_REASON)

    def _too_large(self) -> ResponseFormatError:
        self.failed = True
        self.overflowed = True
        self.finish(user_exit_error=None)  # the session is over: stop gap tracking now, not when the ``with`` block exits
        return ResponseFormatError(self.spec.api_id, "receive", f"message exceeds {MAX_WS_MESSAGE_BYTES} bytes; session closed")

    def on_disconnect(self, error: httpx_ws.WebSocketDisconnect) -> DeviceError:
        if error.code == LIMIT_CLOSE_CODE and error.reason == LIMIT_CLOSE_REASON:
            return self._too_large()
        if error.code in _NORMAL_CLOSE:
            self.closed = SessionClosed(error.code, error.reason)
            self.finish(user_exit_error=None)
            return self.closed
        return self._fail(ConnectionFailed(f"{self.spec.api_id}: device closed the session with code {error.code}: {error.reason}"))

    def on_network_error(self) -> DeviceError:
        return self._fail(ConnectionFailed(f"{self.spec.api_id}: connection lost (network error or heartbeat timeout)"))

    def _fail(self, error: TransportError) -> TransportError:
        self.failed = True
        self.finish(user_exit_error=None)
        return error

    def reply_for(self, message: Any, request_id: str, method: str) -> tuple[bool, Any]:
        """Whether ``message`` answers ``request_id``; raises the API error if it carries one."""
        codec = self.spec.codec
        assert codec is not None
        kind = codec.classify(message)
        if isinstance(kind, Reply) and kind.request_id == request_id:
            if kind.error is not None:
                raise api_error(codec, method, kind.error)
            return True, kind.result
        return False, None

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
        if self._ended:
            return
        self._ended = True
        if not self._begun:
            return
        self.ledger.unwatch(self.spec.key, self.check_alive)
        graceful = not self.failed and (user_exit_error is None or not isinstance(user_exit_error, TransportError))
        self.ledger.end(self.spec.key, graceful=graceful)


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
    token = response.text.strip()
    if response.status != 200 or not token:
        raise refusal_error(spec, response) if response.status != 200 else ResponseFormatError(
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
        core.watch_reader(lambda: getattr(raw, "_should_close").is_set())

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
            self._core.check_alive()
            self._core.finish(user_exit_error=None)  # the connection is closed: stop gap tracking
            raise self._core.closed or SessionClosed() from error
        except (httpx_ws.WebSocketNetworkError, httpcore.WriteError, httpcore.NetworkError) as error:
            raise self._core.on_network_error() from error

    def receive(self, timeout: float | None = None) -> Any:
        """The next message. ``ReadTimeout`` after ``timeout`` seconds; ``SessionClosed`` after a normal end."""
        core = self._core
        if core.pending:
            return core.pending.popleft()
        return self._read(timeout)

    def _read(self, timeout: float | None) -> Any:
        core = self._core
        if core.closed is not None:
            raise core.closed
        if core.overflowed:
            raise core.overflow_closed()
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
            try:
                event = self._raw.receive(remaining)
            except queue.Empty:
                raise ReadTimeout(f"{core.spec.api_id}: no message within {timeout} s") from None
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
            if message is not None:
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
        request_id, message = core.request_message(method, params)
        self.send(message)
        limit = core.default_timeout if timeout is None else timeout
        deadline = time.monotonic() + limit
        skipped: list[Any] = []
        try:
            while True:
                incoming = self._read(max(0.0, deadline - time.monotonic()))
                matched, result = core.reply_for(incoming, request_id, method)
                if matched:
                    return result
                skipped.append(incoming)
        finally:
            core.pending.extend(skipped)

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
        self._raw.close()
        self._core.finish(user_exit_error=None)  # closed: the session no longer counts as active in the gap ledger


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
    if use_token:
        query = (("wssession", run_sync(transport, _token_flow(spec), call)),) + query
    request = call.prepare(Request("GET", spec.path, query=query, auth="anonymous" if use_token else "required"))
    attempt = 1
    stack = ExitStack()
    while True:
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
        call.observe(request, response, None, started, attempt)
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
        core.finish(user_exit_error=error)


# ---------------------------------------------------------------------------
# Async


class AsyncSession:
    """Async counterpart of ``Session``: ``async for`` over messages, ``await`` for the rest."""

    def __init__(self, raw: httpx_ws.AsyncWebSocketSession, core: _Core) -> None:
        self._raw = raw
        self._core = core
        core.watch_reader(lambda: getattr(raw, "_should_close").is_set())

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
            self._core.check_alive()
            self._core.finish(user_exit_error=None)  # the connection is closed: stop gap tracking
            raise self._core.closed or SessionClosed() from error
        except (httpx_ws.WebSocketNetworkError, httpcore.WriteError, httpcore.NetworkError) as error:
            raise self._core.on_network_error() from error

    async def receive(self, timeout: float | None = None) -> Any:
        """The next message. ``ReadTimeout`` after ``timeout`` seconds; ``SessionClosed`` after a normal end."""
        core = self._core
        if core.pending:
            return core.pending.popleft()
        return await self._read(timeout)

    async def _read(self, timeout: float | None) -> Any:
        core = self._core
        if core.closed is not None:
            raise core.closed
        if core.overflowed:
            raise core.overflow_closed()
        loop = asyncio.get_running_loop()
        deadline = None if timeout is None else loop.time() + timeout
        while True:
            remaining = None if deadline is None else max(0.0, deadline - loop.time())
            try:
                event = await self._raw.receive(remaining)
            except TimeoutError:
                raise ReadTimeout(f"{core.spec.api_id}: no message within {timeout} s") from None
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
            if message is not None:
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
        request_id, message = core.request_message(method, params)
        await self.send(message)
        limit = core.default_timeout if timeout is None else timeout
        loop = asyncio.get_running_loop()
        deadline = loop.time() + limit
        skipped: list[Any] = []
        try:
            while True:
                incoming = await self._read(max(0.0, deadline - loop.time()))
                matched, result = core.reply_for(incoming, request_id, method)
                if matched:
                    return result
                skipped.append(incoming)
        finally:
            core.pending.extend(skipped)

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
        await self._raw.close()
        self._core.finish(user_exit_error=None)  # closed: the session no longer counts as active in the gap ledger


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
    if use_token:
        query = (("wssession", await run_async(transport, _token_flow(spec), call)),) + query
    request = call.prepare(Request("GET", spec.path, query=query, auth="anonymous" if use_token else "required"))
    attempt = 1
    stack = AsyncExitStack()
    while True:
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
        call.observe(request, response, None, started, attempt)
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
        core.finish(user_exit_error=error)
