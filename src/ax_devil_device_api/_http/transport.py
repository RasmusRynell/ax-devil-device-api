"""Sync and async transports over httpx, with exception mapping."""

from __future__ import annotations

import asyncio
import base64
import inspect
import secrets
import ssl
import threading
import time
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Iterable, Iterator
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import asynccontextmanager, contextmanager
from dataclasses import replace
from typing import Any
from urllib.parse import quote_plus, urlencode

import httpcore
import httpx
import wsproto.events
from httpx_ws import AsyncWebSocketSession, WebSocketSession

from .. import errors
from .._validate import positive_int
from . import debug
from .auth import AxisAuth
from .config import BearerToken, ConnectionConfig, Credentials
from .multipart import encode_multipart
from .options import Heartbeat
from .types import DeferredContent, FormBody, Headers, JsonBody, MultipartBody, RawBody, Request, Response, has_deferred

USER_AGENT = "ax-devil-device-api/1.0"

PREFLIGHT_PATH = "/axis-cgi/usergroup.cgi"
"""Authenticated GET used to verify credentials before a body that cannot be replayed.

Present on every Axis device, read-only, answered for any role (it reports the caller's own
user and groups) and served from the same Digest realm as the other ``/axis-cgi`` CGIs, so the
verified credential it leaves behind is the one the upload then uses.
"""


def _slot_timeout(config: ConnectionConfig, request: Request) -> float:
    return request.timeout if request.timeout is not None else config.timeout


def _pool_timeout(timeout: float) -> errors.PoolTimeout:
    error = errors.PoolTimeout(f"no free request slot to the device within {timeout:g} s")
    error.body_untouched = True  # raised before the request was built: a one-shot body is still intact
    return error


@contextmanager
def _slot(semaphore: threading.BoundedSemaphore, timeout: float) -> Iterator[None]:
    """Hold a concurrency slot; waiting for it counts against the request timeout."""
    if not semaphore.acquire(timeout=timeout):
        raise _pool_timeout(timeout)
    try:
        yield
    finally:
        semaphore.release()


@asynccontextmanager
async def _aslot(semaphore: asyncio.Semaphore, timeout: float) -> AsyncIterator[None]:
    try:
        await asyncio.wait_for(semaphore.acquire(), timeout)
    except TimeoutError:
        raise _pool_timeout(timeout) from None
    try:
        yield
    finally:
        semaphore.release()


def _check_proxy_with_transport(config: ConnectionConfig, transport: object | None) -> None:
    if transport is not None and config.proxy is not None:
        raise errors.ConfigurationError(
            "proxy cannot be combined with an injected transport: httpx would route requests around the "
            "transport. Configure the proxy on that transport instead, or drop one of the two"
        )


def _client_error(error: Exception, config: ConnectionConfig | None = None) -> errors.ConfigurationError:
    if isinstance(error, OSError):
        verify = config.verify if config is not None else None
        # The CA wording only when the error is about the verify path (or the SSL layer rejecting its contents);
        # anything else (an SSLKEYLOGFILE that cannot be opened, say) is reported as it is, filename included.
        about_bundle = isinstance(verify, str) and (isinstance(error, ssl.SSLError) or error.filename in (None, verify))
        if about_bundle:
            return errors.ConfigurationError(f"cannot load the CA bundle {verify!r} given as verify: {error}")
        return errors.ConfigurationError(f"could not build the HTTP client: {error}")
    if isinstance(error, ImportError):
        return errors.ConfigurationError("SOCKS proxy support requires: pip install 'ax-devil-device-api[socks]'")
    return _invalid_url(error)


def _invalid_url(error: Exception) -> errors.ConfigurationError:
    return errors.ConfigurationError(f"the device address, proxy or request path does not make a valid URL: {error}")


def _preflight_request(request: Request) -> Request | None:
    """The preflight for ``request``, or ``None`` when it needs none."""
    if request.replayable or request.auth != "required":
        return None
    return Request("GET", PREFLIGHT_PATH, timeout=request.timeout)


def _preflight_failure(status: int) -> errors.AuthError:
    return errors.AuthError(
        f"authentication failed: could not verify the credentials before sending a body that "
        f"cannot be replayed (HTTP {status} from {PREFLIGHT_PATH})"
    )


def _scrub(text: str, secrets: Iterable[str]) -> str:
    """``text`` without any of the credential values (three characters or more: shorter ones would mangle the text)."""
    for secret in sorted({s for s in secrets if len(s) >= 3}, key=len, reverse=True):
        text = text.replace(secret, "<redacted>")
    return text


def _request_secrets(config: ConnectionConfig, request: Request) -> tuple[str, ...]:
    """Every credential value this request carries: the configured password or token, and secret-named or masked
    query and header values (a wssession token, an export password)."""
    found: list[str] = []
    credentials = config.credentials
    if isinstance(credentials, Credentials):
        found.append(credentials.password)
    elif isinstance(credentials, BearerToken):
        found.append(credentials.recent() or "")
    for name, value in (*request.query, *request.headers):
        if value and (str(name).lower() in request.masked or debug.is_secret_name(str(name))):
            found.append(str(value))
    return tuple(found)


def map_error(error: httpx.TransportError, secrets: Iterable[str] = ()) -> errors.TransportError:
    """Translate an httpx transport exception into the library's hierarchy.

    The diagnostic copied from the exception is scrubbed of ``secrets`` (the credentials of the transport) on top of the
    display redaction every library error applies: a header-parsing failure can quote the header it rejected.
    """
    where = _where(error)
    # The library error is raised OUTSIDE the except block that caught ``error`` and chains nothing: the httpx exception
    # holds the request (its Authorization header, a password in the query) and must not be reachable from the error.
    # What diagnoses the failure is kept as text: the exception's class name and its own message (errno, TLS reason).
    own = _scrub(str(error), secrets)
    named = f"{type(error).__name__}: {own}" if own else type(error).__name__
    if isinstance(error, httpx.ConnectTimeout):
        return errors.ConnectTimeout(f"connect timed out{where} [{named}]")
    if isinstance(error, httpx.WriteTimeout):
        return errors.WriteTimeout(f"timed out sending the request{where} [{named}]")
    if isinstance(error, httpx.PoolTimeout):
        return errors.PoolTimeout(f"no free connection to the device{where} [{named}]")
    if isinstance(error, httpx.TimeoutException):
        return errors.ReadTimeout(f"timed out waiting for the device{where} [{named}]")
    message = f"{named}{where}"
    if isinstance(error, httpx.ProxyError):
        # The proxy refused or failed the tunnel: nothing reached the device.
        return errors.ConnectionFailed(message, request_sent=False)
    if isinstance(error, httpx.ConnectError):
        if _is_tls(error):
            return errors.TlsError(message)
        return errors.ConnectionFailed(message, request_sent=False)
    return errors.ConnectionFailed(message, request_sent=True)


def _where(error: httpx.TransportError) -> str:
    try:
        request = error.request
    except RuntimeError:
        return ""
    return f" ({request.method} {request.url.copy_with(query=None)})"


def _is_tls(error: BaseException) -> bool:
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, ssl.SSLError) or "certificate verify" in str(current).lower():
            return True
        current = current.__cause__ or current.__context__
    return False


_DONE = object()


class _ThreadReads:
    """Async view of a blocking chunk iterator; every read runs in a worker thread, off the event loop.

    A cancelled caller cannot stop a read that is already running, and a generator cannot be closed
    while it runs. ``aclose`` therefore never touches a running iterator: it closes it from the worker
    thread as soon as the in-flight read returns, so cancellation propagates and the source is still
    closed (a library-owned file does not stay open).
    """

    def __init__(self, chunks: Iterator[bytes]) -> None:
        self._chunks = chunks
        self._executor: ThreadPoolExecutor | None = None
        self._pending: Future[Any] | None = None
        self._closed = False
        self._lock = threading.Lock()

    def __aiter__(self) -> _ThreadReads:
        return self

    async def __anext__(self) -> bytes:
        if self._closed:
            raise StopAsyncIteration
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ax-upload-read")
        future = self._executor.submit(next, self._chunks, _DONE)
        self._pending = future
        chunk: Any = await asyncio.wrap_future(future)
        if chunk is _DONE:
            raise StopAsyncIteration
        return chunk

    async def aclose(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            pending = self._pending
            if pending is not None and not pending.done():
                pending.add_done_callback(lambda _: self._finish())
                return
        self._finish()

    def _finish(self) -> None:
        try:
            _close(self._chunks)
        finally:
            if self._executor is not None:
                self._executor.shutdown(wait=False)


def _aiter(chunks: Iterator[bytes]) -> _ThreadReads:
    return _ThreadReads(chunks)


def _closing(chunks: Iterator[bytes]) -> Iterator[bytes]:
    try:
        yield from chunks
    finally:
        _close(chunks)


def _close(iterator: object) -> None:
    close = getattr(iterator, "close", None)
    if callable(close):
        close()


class UpgradeRefused(Exception):
    """The device answered a WebSocket handshake with something other than 101."""

    def __init__(self, response: Response) -> None:
        super().__init__(f"WebSocket upgrade refused: HTTP {response.status}")
        self.response = response


MAX_WS_MESSAGE_BYTES = 8 * 1024 * 1024
WS_QUEUE_SIZE = 512
"""How many unread messages the session layer keeps (it also has a byte budget, see ``_runtime/ws.py``)."""
WS_UPSTREAM_QUEUE_SIZE = positive_int("WS_UPSTREAM_QUEUE_SIZE", 16)
"""httpx-ws's own ``queue_size``: complete messages its reader may hold before the session layer takes them. Small on
purpose (a message can be 8 MiB): a full queue blocks that reader, which is TCP backpressure; the session layer's
byte-accounted queue is the real bound."""
LIMIT_CLOSE_CODE = 1009
LIMIT_CLOSE_REASON = "message too big (ax-devil limit)"
"""Close code and reason of the synthetic close the size guard injects."""


class _SizeGuard:
    """Wraps httpx-ws's wsproto connection so a message is cut off while it is still being received.

    httpx-ws buffers the fragments of an unfinished message without any limit (its
    ``max_message_size_bytes`` is only the read size). Counting UTF-8 bytes per wsproto event here,
    before the fragments are aggregated, turns an over-limit message into a close event
    (``LIMIT_CLOSE_CODE``), which the session layer reports as a ``ResponseFormatError``.
    """

    def __init__(self, inner: Any, limit: int) -> None:
        self._inner = inner
        self._limit = limit
        self._size = 0
        self.stopped = False
        """Set when the session is closing: no further events are handed to httpx-ws's reader, so its blocking
        ``put`` on the (small) queue can never be reached again."""
        self.last_frame: float | None = None
        """Arrival time of the last data frame."""
        self.remote_close: tuple[int, float] | None = None
        """``(code, arrival time)`` of the close frame the device sent. Recorded here, in the reader, before the
        session layer sees the event, so the time is that of the frame however late it is consumed."""

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def events(self) -> Iterator[Any]:
        for event in self._inner.events():
            if self.stopped:
                return  # closing: frames still in this read are dropped, not queued
            if isinstance(event, wsproto.events.Message):
                data = event.data
                self._size += len(data.encode("utf-8")) if isinstance(data, str) else len(data)
                if self._size > self._limit:
                    self._size = 0
                    yield wsproto.events.CloseConnection(LIMIT_CLOSE_CODE, LIMIT_CLOSE_REASON)
                    return
                self.last_frame = _clock()  # only frames within the limit count as evidence of liveness
                if event.message_finished:
                    self._size = 0
            if isinstance(event, wsproto.events.CloseConnection) and self.remote_close is None:
                self.remote_close = (event.code, _clock())
            yield event


def _clock() -> float:
    return time.time()


class _WatchedStream:
    """Wraps the network stream of a session to remember that a write failed.

    httpx-ws swallows a ``WriteError`` while closing, and sets its own ``_should_close`` before it writes, so neither
    tells the session layer that its close did not reach the device. This does.
    """

    def __init__(self, inner: Any, write_timeout: float | None = None) -> None:
        self._inner = inner
        self._write_timeout = write_timeout
        self.write_failed = False
        self._unfinished = 0

    @property
    def write_in_flight(self) -> bool:
        """A write was started and has neither finished nor failed: cancelling it leaves a partly written frame."""
        return self._unfinished > 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def write(self, *args: Any, **kwargs: Any) -> Any:
        if self._write_timeout is not None and len(args) < 2:
            kwargs.setdefault("timeout", self._write_timeout)  # httpx-ws writes without one; a blocked peer must not hang
        self._unfinished += 1
        try:
            result = self._inner.write(*args, **kwargs)
        except httpcore.WriteTimeout as error:
            self._unfinished -= 1
            self.write_failed = True
            raise httpcore.WriteError(str(error)) from error  # a stalled write is a broken connection (and close() copes)
        except Exception:  # not BaseException: a write cancelled by closing the session is not a failure
            self._unfinished -= 1
            self.write_failed = True
            raise
        if inspect.isawaitable(result):
            return self._awaited(result)
        self._unfinished -= 1
        return result

    async def _awaited(self, awaitable: Any) -> Any:
        try:
            result = await awaitable
            self._unfinished -= 1
            return result
        except httpcore.WriteTimeout as error:
            self._unfinished -= 1
            self.write_failed = True
            raise httpcore.WriteError(str(error)) from error
        except Exception:  # not BaseException: a write cancelled by closing the session is not a failure
            self._unfinished -= 1
            self.write_failed = True
            raise


def _guard(session: Any, write_timeout: float | None = None) -> None:
    session.connection = _SizeGuard(session.connection, MAX_WS_MESSAGE_BYTES)
    session.stream = _WatchedStream(session.stream, write_timeout)


def _ws_request(request: Request) -> Request:
    """Add the RFC 6455 handshake headers (the key is random per attempt)."""
    key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
    handshake = (
        ("Connection", "Upgrade"),
        ("Upgrade", "websocket"),
        ("Sec-WebSocket-Key", key),
        ("Sec-WebSocket-Version", "13"),
    )
    return replace(request, headers=request.headers + handshake)


def _build(
    client: httpx.Client | httpx.AsyncClient, request: Request, base_path: str, opened: list[Any] | None = None,
) -> httpx.Request:
    """Build the httpx request; headers are derived from the body, never defaulted.

    Lazy body iterators (which may own open files) are appended to ``opened`` so the
    caller can close them once the send is over, however it ended.
    """
    if has_deferred(request):
        raise TypeError("upload content is still deferred; the driver reads it (resolve_deferred) before sending")
    track = opened if opened is not None else []
    headers: list[tuple[str, str]] = []
    if request.accept is not None:
        headers.append(("Accept", request.accept))
    headers.extend(request.headers)
    kwargs: dict[str, Any] = {}
    body = request.body
    if isinstance(body, JsonBody):
        kwargs["json"] = body.value
    elif isinstance(body, FormBody):
        kwargs["content"] = urlencode(body.fields).encode("ascii")
        headers.append(("Content-Type", "application/x-www-form-urlencoded"))
    elif isinstance(body, RawBody):
        content = body.content
        assert not isinstance(content, DeferredContent)  # has_deferred() above
        if not isinstance(content, (bytes, AsyncIterable)):
            content = _aiter(iter(content)) if isinstance(client, httpx.AsyncClient) else _closing(iter(content))
        if not isinstance(content, bytes):
            track.append(content)
        kwargs["content"] = content
        headers.append(("Content-Type", body.content_type))
        if body.size is not None and not isinstance(body.content, bytes):
            headers.append(("Content-Length", str(body.size)))
    elif isinstance(body, MultipartBody):
        encoded = encode_multipart(body)
        headers.append(("Content-Type", encoded.content_type))
        if isinstance(encoded.content, bytes):
            kwargs["content"] = encoded.content
        else:
            # httpx's async client needs an async iterable; the sync one a sync iterable.
            # The async wrapper owns closing the iterator (deferred while a worker read is in flight).
            kwargs["content"] = _aiter(encoded.content) if isinstance(client, httpx.AsyncClient) else encoded.content
            track.append(kwargs["content"])
            if encoded.length is not None:
                headers.append(("Content-Length", str(encoded.length)))
    if request.timeout is not None:
        kwargs["timeout"] = request.timeout
    url = base_path + request.path
    params: list[tuple[str, Any]] | None = None
    if any(value is None for _, value in request.query):
        # httpx always writes `key=`; bare keys (`?live-sum.json`) are written by hand, in order.
        url += "?" + "&".join(
            quote_plus(key) if value is None else str(httpx.QueryParams([(key, value)])) for key, value in request.query
        )
    else:
        params = [(key, value) for key, value in request.query if value is not None] or None
    return client.build_request(
        request.method,
        url,
        params=params,
        headers=headers,
        **kwargs,
    )


def _response(raw: httpx.Response, request: Request, content: bytes) -> Response:
    return Response(raw.status_code, Headers(raw.headers.multi_items()), content, request)


def _observe_probe(
    config: ConnectionConfig, probe: Request, status: int | None, error: BaseException | None, started: float, attempt: int
) -> None:
    """The ``on_response`` record of a credentials preflight: its own request, so its failure is not the upload's."""
    if config.on_response is None:
        return
    config.on_response(
        {
            "api": "device-auth",
            "operation": "preflight",
            "method": probe.method,
            "path": probe.path,
            "status": status,
            "error": type(error).__name__ if error is not None else None,
            "duration_ms": round((time.monotonic() - started) * 1000, 1),
            "attempt": attempt,
        }
    )


def _emit(config: ConnectionConfig, request: Request) -> None:
    timeout = request.timeout if request.timeout is not None else config.timeout
    debug.emit_request(config.on_request, request, config.base_url + config.base_path + request.path, timeout, config.verify)


def _client_args(config: ConnectionConfig) -> dict[str, Any]:
    args: dict[str, Any] = {
        "base_url": config.base_url,
        "verify": config.verify,
        "timeout": config.timeout,
        "follow_redirects": False,
        "headers": {"User-Agent": USER_AGENT},
        "limits": httpx.Limits(
            max_connections=config.max_concurrency + config.max_streams,
            max_keepalive_connections=config.max_concurrency,
        ),
    }
    if config.proxy is not None:
        args["proxy"] = config.proxy
    return args


class SyncTransport:
    """Blocking transport for one device."""

    def __init__(self, config: ConnectionConfig, *, transport: httpx.BaseTransport | None = None) -> None:
        self.config = config
        self._auth = AxisAuth(config.credentials)
        self._slots = threading.BoundedSemaphore(config.max_concurrency)
        self._stream_slots = threading.BoundedSemaphore(config.max_streams)
        _check_proxy_with_transport(config, transport)
        try:
            self._client = httpx.Client(transport=transport, **_client_args(config))
        except (httpx.InvalidURL, ValueError, ImportError, OSError) as error:
            raise _client_error(error, config) from error
        self._client.headers.pop("Accept", None)  # Accept is set only when a request asks for it

    def _send(self, request: Request, *, stream: bool) -> httpx.Response:
        probe = _preflight_request(request) if self._auth.uses_password else None
        for attempt in range(2 if probe is not None else 1):
            if probe is not None:
                _emit(self.config, probe)
                started = time.monotonic()
                try:
                    reply = self._send_once(probe, stream=False)
                except Exception as error:
                    if isinstance(error, errors.TransportError):
                        error.during_preflight = True
                    _observe_probe(self.config, probe, None, error, started, attempt + 1)
                    raise
                if not reply.is_success or self._auth.needs_verification:
                    failure = _preflight_failure(reply.status_code)
                    _observe_probe(self.config, probe, reply.status_code, failure, started, attempt + 1)
                    raise failure
                _observe_probe(self.config, probe, reply.status_code, None, started, attempt + 1)
            try:
                return self._send_once(request, stream=stream)
            except errors.AuthError as error:
                # A concurrent request demoted the verified credential after the preflight and before this body
                # was signed: nothing was sent yet, so verify once more. A failure after the body went out is final.
                if attempt == 0 and probe is not None and getattr(error, "body_untouched", False):
                    continue
                raise
        raise AssertionError("unreachable")  # pragma: no cover

    def _send_once(self, request: Request, *, stream: bool) -> httpx.Response:
        opened: list[Any] = []
        failure: Exception | None = None
        try:
            return self._client.send(
                _build(self._client, request, self.config.base_path, opened),
                auth=self._auth.for_request(request.auth, request.replayable),
                stream=stream,
            )
        except httpx.InvalidURL as error:
            failure = _invalid_url(error)
        except UnicodeEncodeError:
            # Safety net: headers are checked as ASCII when built; this is whatever slipped through (a value from the device
            # echoed into a header, say). Never echoes it.
            failure = errors.ConfigurationError("a request header cannot be encoded: non-ASCII characters")
        except httpx.TransportError as error:
            failure = map_error(error, _request_secrets(self.config, request))
        finally:
            for iterator in opened:
                _close(iterator)
        raise failure  # outside the handler: no __cause__ or __context__ reaches the httpx exception and its request

    def send(self, request: Request) -> Response:
        """Send ``request`` and return the fully read response."""
        _emit(self.config, request)
        with _slot(self._slots, _slot_timeout(self.config, request)):
            raw = self._send(request, stream=False)
            return _response(raw, request, raw.content)

    @contextmanager
    def open_stream(self, request: Request) -> Iterator[tuple[Response, Iterator[bytes]]]:
        """Yield ``(response, chunks)``; non-2xx responses carry the whole body and no chunks.

        Holds one stream slot until the context exits.
        """
        _emit(self.config, request)
        with _slot(self._stream_slots, _slot_timeout(self.config, request)):
            raw = self._send(request, stream=True)
            try:
                if not raw.is_success:
                    failure: errors.TransportError | None = None
                    try:
                        raw.read()
                    except httpx.TransportError as error:
                        failure = map_error(error, _request_secrets(self.config, request))
                    if failure is not None:
                        raise failure
                    yield _response(raw, request, raw.content), iter(())
                else:
                    yield _response(raw, request, b""), self._chunks(raw, request)
            finally:
                raw.close()

    @contextmanager
    def open_ws(
        self, request: Request, heartbeat: Heartbeat, before_send: Callable[[], Request] | None = None
    ) -> Iterator[tuple[Response, WebSocketSession]]:
        """Perform a WebSocket handshake and yield ``(handshake response, httpx-ws session)``.

        Authentication is the same flow as for any request (Digest preferred, no
        Basic before a challenge). Raises ``UpgradeRefused`` for any non-101 answer.
        Holds one stream slot until the context exits.

        ``before_send`` runs once the stream slot is held and returns the request to send (``request`` still decides how
        long to wait for the slot). A short-lived credential in the request, such as the 15 second ``wssession`` token,
        is fetched there, so waiting for a busy slot cannot use it up.
        """
        if before_send is None:
            _emit(self.config, request)
        with _slot(self._stream_slots, _slot_timeout(self.config, request)):
            if before_send is not None:
                request = before_send()
                _emit(self.config, request)
            raw = self._send(_ws_request(request), stream=True)
            try:
                if raw.status_code != 101:
                    failure: errors.TransportError | None = None
                    try:
                        raw.read()
                    except httpx.TransportError as error:
                        failure = map_error(error, _request_secrets(self.config, request))
                    if failure is not None:
                        raise failure
                    raise UpgradeRefused(_response(raw, request, raw.content))
                session = WebSocketSession(
                    raw.extensions["network_stream"],
                    max_message_size_bytes=MAX_WS_MESSAGE_BYTES,
                    queue_size=WS_UPSTREAM_QUEUE_SIZE,
                    keepalive_ping_interval_seconds=heartbeat.interval,
                    keepalive_ping_timeout_seconds=heartbeat.timeout,
                    response=raw,
                )
                _guard(session, self.config.timeout)
                with session:
                    yield _response(raw, request, b""), session
            finally:
                raw.close()

    def _chunks(self, raw: httpx.Response, request: Request) -> Iterator[bytes]:
        failure: errors.TransportError | None = None
        try:
            yield from raw.iter_bytes()
        except httpx.TransportError as error:
            failure = map_error(error, _request_secrets(self.config, request))
        if failure is not None:
            raise failure

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SyncTransport:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncTransport:
    """Asyncio transport for one device."""

    def __init__(self, config: ConnectionConfig, *, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.config = config
        self._auth = AxisAuth(config.credentials)
        self._slots: asyncio.Semaphore | None = None  # created on first use, inside a running loop
        self._stream_slots: asyncio.Semaphore | None = None
        _check_proxy_with_transport(config, transport)
        try:
            self._client = httpx.AsyncClient(transport=transport, **_client_args(config))
        except (httpx.InvalidURL, ValueError, ImportError, OSError) as error:
            raise _client_error(error, config) from error
        self._client.headers.pop("Accept", None)

    def _semaphores(self) -> tuple[asyncio.Semaphore, asyncio.Semaphore]:
        if self._slots is None or self._stream_slots is None:
            self._slots = asyncio.Semaphore(self.config.max_concurrency)
            self._stream_slots = asyncio.Semaphore(self.config.max_streams)
        return self._slots, self._stream_slots

    async def _send(self, request: Request, *, stream: bool) -> httpx.Response:
        probe = _preflight_request(request) if self._auth.uses_password else None
        for attempt in range(2 if probe is not None else 1):
            if probe is not None:
                _emit(self.config, probe)
                started = time.monotonic()
                try:
                    reply = await self._send_once(probe, stream=False)
                except Exception as error:
                    if isinstance(error, errors.TransportError):
                        error.during_preflight = True
                    _observe_probe(self.config, probe, None, error, started, attempt + 1)
                    raise
                if not reply.is_success or self._auth.needs_verification:
                    failure = _preflight_failure(reply.status_code)
                    _observe_probe(self.config, probe, reply.status_code, failure, started, attempt + 1)
                    raise failure
                _observe_probe(self.config, probe, reply.status_code, None, started, attempt + 1)
            try:
                return await self._send_once(request, stream=stream)
            except errors.AuthError as error:
                # A concurrent request demoted the verified credential after the preflight and before this body
                # was signed: nothing was sent yet, so verify once more. A failure after the body went out is final.
                if attempt == 0 and probe is not None and getattr(error, "body_untouched", False):
                    continue
                raise
        raise AssertionError("unreachable")  # pragma: no cover

    async def _send_once(self, request: Request, *, stream: bool) -> httpx.Response:
        opened: list[Any] = []
        failure: Exception | None = None
        try:
            return await self._client.send(
                _build(self._client, request, self.config.base_path, opened),
                auth=self._auth.for_request(request.auth, request.replayable),
                stream=stream,
            )
        except httpx.InvalidURL as error:
            failure = _invalid_url(error)
        except UnicodeEncodeError:
            # Safety net: headers are checked as ASCII when built; this is whatever slipped through (a value from the device
            # echoed into a header, say). Never echoes it.
            failure = errors.ConfigurationError("a request header cannot be encoded: non-ASCII characters")
        except httpx.TransportError as error:
            failure = map_error(error, _request_secrets(self.config, request))
        finally:
            for iterator in reversed(opened):
                if hasattr(iterator, "aclose"):
                    await iterator.aclose()
                else:
                    _close(iterator)
        raise failure  # outside the handler: no __cause__ or __context__ reaches the httpx exception and its request

    async def send(self, request: Request) -> Response:
        """Send ``request`` and return the fully read response."""
        _emit(self.config, request)
        slots, _ = self._semaphores()
        async with _aslot(slots, _slot_timeout(self.config, request)):
            raw = await self._send(request, stream=False)
            return _response(raw, request, raw.content)

    @asynccontextmanager
    async def open_stream(self, request: Request) -> AsyncIterator[tuple[Response, AsyncIterator[bytes]]]:
        """Yield ``(response, chunks)``; non-2xx responses carry the whole body and no chunks.

        Holds one stream slot until the context exits.
        """
        _emit(self.config, request)
        _, stream_slots = self._semaphores()
        async with _aslot(stream_slots, _slot_timeout(self.config, request)):
            raw = await self._send(request, stream=True)
            try:
                if not raw.is_success:
                    failure: errors.TransportError | None = None
                    try:
                        await raw.aread()
                    except httpx.TransportError as error:
                        failure = map_error(error, _request_secrets(self.config, request))
                    if failure is not None:
                        raise failure
                    yield _response(raw, request, raw.content), _empty()
                else:
                    yield _response(raw, request, b""), self._chunks(raw, request)
            finally:
                await raw.aclose()

    @asynccontextmanager
    async def open_ws(
        self, request: Request, heartbeat: Heartbeat, before_send: Callable[[], Awaitable[Request]] | None = None
    ) -> AsyncIterator[tuple[Response, AsyncWebSocketSession]]:
        """Async counterpart of ``SyncTransport.open_ws`` (``before_send`` is awaited once the stream slot is held).

        Exceptions raised in the body are unwrapped from the ``ExceptionGroup``
        that httpx-ws's task group would put them in.
        """
        if before_send is None:
            _emit(self.config, request)
        _, stream_slots = self._semaphores()
        async with _aslot(stream_slots, _slot_timeout(self.config, request)):
            if before_send is not None:
                request = await before_send()
                _emit(self.config, request)
            raw = await self._send(_ws_request(request), stream=True)
            try:
                if raw.status_code != 101:
                    failure: errors.TransportError | None = None
                    try:
                        await raw.aread()
                    except httpx.TransportError as error:
                        failure = map_error(error, _request_secrets(self.config, request))
                    if failure is not None:
                        raise failure
                    raise UpgradeRefused(_response(raw, request, raw.content))
                session = AsyncWebSocketSession(
                    raw.extensions["network_stream"],
                    max_message_size_bytes=MAX_WS_MESSAGE_BYTES,
                    queue_size=WS_UPSTREAM_QUEUE_SIZE,
                    keepalive_ping_interval_seconds=heartbeat.interval,
                    keepalive_ping_timeout_seconds=heartbeat.timeout,
                    response=raw,
                )
                _guard(session, self.config.timeout)
                try:
                    async with session:
                        yield _response(raw, request, b""), session
                except BaseExceptionGroup as group:
                    if len(group.exceptions) == 1:
                        raise group.exceptions[0] from None
                    raise
            finally:
                await raw.aclose()

    async def _chunks(self, raw: httpx.Response, request: Request) -> AsyncIterator[bytes]:
        failure: errors.TransportError | None = None
        try:
            async for chunk in raw.aiter_bytes():
                yield chunk
        except httpx.TransportError as error:
            failure = map_error(error, _request_secrets(self.config, request))
        if failure is not None:
            raise failure

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()


async def _empty() -> AsyncIterator[bytes]:
    return
    yield b""
