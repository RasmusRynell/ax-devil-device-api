"""Sync and async transports over httpx, with exception mapping."""

from __future__ import annotations

import asyncio
import base64
import secrets
import ssl
import threading
from collections.abc import AsyncIterable, AsyncIterator, Iterator
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import asynccontextmanager, contextmanager
from dataclasses import replace
from typing import Any
from urllib.parse import quote_plus, urlencode

import httpx
from httpx_ws import AsyncWebSocketSession, WebSocketSession

from .. import errors
from . import debug
from .auth import AxisAuth
from .config import ConnectionConfig
from .multipart import encode_multipart
from .options import Heartbeat
from .types import FormBody, Headers, JsonBody, MultipartBody, RawBody, Request, Response

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
    return errors.PoolTimeout(f"no free request slot to the device within {timeout:g} s")


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


def map_error(error: httpx.TransportError) -> errors.TransportError:
    """Translate an httpx transport exception into the library's hierarchy."""
    where = _where(error)
    if isinstance(error, httpx.ConnectTimeout):
        return errors.ConnectTimeout(f"connect timed out{where}")
    if isinstance(error, httpx.WriteTimeout):
        return errors.WriteTimeout(f"timed out sending the request{where}")
    if isinstance(error, httpx.PoolTimeout):
        return errors.PoolTimeout(f"no free connection to the device{where}")
    if isinstance(error, httpx.TimeoutException):
        return errors.ReadTimeout(f"timed out waiting for the device{where}")
    message = f"{str(error) or type(error).__name__}{where}"
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
        chunk = await asyncio.wrap_future(future)
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
        self._client = httpx.Client(transport=transport, **_client_args(config))
        self._client.headers.pop("Accept", None)  # Accept is set only when a request asks for it

    def _send(self, request: Request, *, stream: bool) -> httpx.Response:
        probe = _preflight_request(request) if self._auth.uses_password else None
        if probe is not None:
            _emit(self.config, probe)
            reply = self._send_once(probe, stream=False)
            if not reply.is_success or self._auth.needs_verification:
                raise _preflight_failure(reply.status_code)
        return self._send_once(request, stream=stream)

    def _send_once(self, request: Request, *, stream: bool) -> httpx.Response:
        opened: list[Any] = []
        try:
            return self._client.send(
                _build(self._client, request, self.config.base_path, opened),
                auth=self._auth.for_request(request.auth, request.replayable),
                stream=stream,
            )
        except httpx.TransportError as error:
            raise map_error(error) from error
        finally:
            for iterator in opened:
                _close(iterator)

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
                    try:
                        raw.read()
                    except httpx.TransportError as error:
                        raise map_error(error) from error
                    yield _response(raw, request, raw.content), iter(())
                else:
                    yield _response(raw, request, b""), self._chunks(raw)
            finally:
                raw.close()

    @contextmanager
    def open_ws(self, request: Request, heartbeat: Heartbeat) -> Iterator[tuple[Response, WebSocketSession]]:
        """Perform a WebSocket handshake and yield ``(handshake response, httpx-ws session)``.

        Authentication is the same flow as for any request (Digest preferred, no
        Basic before a challenge). Raises ``UpgradeRefused`` for any non-101 answer.
        Holds one stream slot until the context exits.
        """
        _emit(self.config, request)
        with _slot(self._stream_slots, _slot_timeout(self.config, request)):
            raw = self._send(_ws_request(request), stream=True)
            try:
                if raw.status_code != 101:
                    try:
                        raw.read()
                    except httpx.TransportError as error:
                        raise map_error(error) from error
                    raise UpgradeRefused(_response(raw, request, raw.content))
                session = WebSocketSession(
                    raw.extensions["network_stream"],
                    max_message_size_bytes=MAX_WS_MESSAGE_BYTES,
                    queue_size=WS_QUEUE_SIZE,
                    keepalive_ping_interval_seconds=heartbeat.interval,
                    keepalive_ping_timeout_seconds=heartbeat.timeout,
                    response=raw,
                )
                with session:
                    yield _response(raw, request, b""), session
            finally:
                raw.close()

    @staticmethod
    def _chunks(raw: httpx.Response) -> Iterator[bytes]:
        try:
            yield from raw.iter_bytes()
        except httpx.TransportError as error:
            raise map_error(error) from error

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
        self._client = httpx.AsyncClient(transport=transport, **_client_args(config))
        self._client.headers.pop("Accept", None)

    def _semaphores(self) -> tuple[asyncio.Semaphore, asyncio.Semaphore]:
        if self._slots is None or self._stream_slots is None:
            self._slots = asyncio.Semaphore(self.config.max_concurrency)
            self._stream_slots = asyncio.Semaphore(self.config.max_streams)
        return self._slots, self._stream_slots

    async def _send(self, request: Request, *, stream: bool) -> httpx.Response:
        probe = _preflight_request(request) if self._auth.uses_password else None
        if probe is not None:
            _emit(self.config, probe)
            reply = await self._send_once(probe, stream=False)
            if not reply.is_success or self._auth.needs_verification:
                raise _preflight_failure(reply.status_code)
        return await self._send_once(request, stream=stream)

    async def _send_once(self, request: Request, *, stream: bool) -> httpx.Response:
        opened: list[Any] = []
        try:
            return await self._client.send(
                _build(self._client, request, self.config.base_path, opened),
                auth=self._auth.for_request(request.auth, request.replayable),
                stream=stream,
            )
        except httpx.TransportError as error:
            raise map_error(error) from error
        finally:
            for iterator in reversed(opened):
                if hasattr(iterator, "aclose"):
                    await iterator.aclose()
                else:
                    _close(iterator)

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
                    try:
                        await raw.aread()
                    except httpx.TransportError as error:
                        raise map_error(error) from error
                    yield _response(raw, request, raw.content), _empty()
                else:
                    yield _response(raw, request, b""), self._chunks(raw)
            finally:
                await raw.aclose()

    @asynccontextmanager
    async def open_ws(self, request: Request, heartbeat: Heartbeat) -> AsyncIterator[tuple[Response, AsyncWebSocketSession]]:
        """Async counterpart of ``SyncTransport.open_ws``.

        Exceptions raised in the body are unwrapped from the ``ExceptionGroup``
        that httpx-ws's task group would put them in.
        """
        _emit(self.config, request)
        _, stream_slots = self._semaphores()
        async with _aslot(stream_slots, _slot_timeout(self.config, request)):
            raw = await self._send(_ws_request(request), stream=True)
            try:
                if raw.status_code != 101:
                    try:
                        await raw.aread()
                    except httpx.TransportError as error:
                        raise map_error(error) from error
                    raise UpgradeRefused(_response(raw, request, raw.content))
                session = AsyncWebSocketSession(
                    raw.extensions["network_stream"],
                    max_message_size_bytes=MAX_WS_MESSAGE_BYTES,
                    queue_size=WS_QUEUE_SIZE,
                    keepalive_ping_interval_seconds=heartbeat.interval,
                    keepalive_ping_timeout_seconds=heartbeat.timeout,
                    response=raw,
                )
                try:
                    async with session:
                        yield _response(raw, request, b""), session
                except BaseExceptionGroup as group:
                    if len(group.exceptions) == 1:
                        raise group.exceptions[0] from None
                    raise
            finally:
                await raw.aclose()

    @staticmethod
    async def _chunks(raw: httpx.Response) -> AsyncIterator[bytes]:
        try:
            async for chunk in raw.aiter_bytes():
                yield chunk
        except httpx.TransportError as error:
            raise map_error(error) from error

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()


async def _empty() -> AsyncIterator[bytes]:
    return
    yield b""
