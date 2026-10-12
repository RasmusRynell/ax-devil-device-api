"""Sync and async transports over httpx, with exception mapping."""

from __future__ import annotations

import asyncio
import ssl
import threading
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any
from urllib.parse import urlencode

import httpx

from .. import errors
from . import debug
from .auth import AxisAuth
from .config import ConnectionConfig
from .types import FormBody, Headers, JsonBody, MultipartBody, RawBody, Request, Response

USER_AGENT = "ax-devil-device-api/1.0"


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


def _build(client: httpx.Client | httpx.AsyncClient, request: Request, base_path: str) -> httpx.Request:
    """Build the httpx request; headers are derived from the body, never defaulted."""
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
        kwargs["content"] = body.content
        headers.append(("Content-Type", body.content_type))
    elif isinstance(body, MultipartBody):
        parts: list[tuple[str, Any]] = [(k, (None, v)) for k, v in body.fields]
        parts += [(f.name, (f.filename, f.content, f.content_type)) for f in body.files]
        kwargs["files"] = parts
    if request.timeout is not None:
        kwargs["timeout"] = request.timeout
    return client.build_request(
        request.method,
        base_path + request.path,
        params=list(request.query) or None,
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
        try:
            return self._client.send(
                _build(self._client, request, self.config.base_path),
                auth=self._auth.for_request(request.auth, request.replayable),
                stream=stream,
            )
        except httpx.TransportError as error:
            raise map_error(error) from error

    def send(self, request: Request) -> Response:
        """Send ``request`` and return the fully read response."""
        _emit(self.config, request)
        with self._slots:
            raw = self._send(request, stream=False)
            return _response(raw, request, raw.content)

    @contextmanager
    def open_stream(self, request: Request) -> Iterator[tuple[Response, Iterator[bytes]]]:
        """Yield ``(response, chunks)``; non-2xx responses carry the whole body and no chunks.

        Holds one stream slot until the context exits.
        """
        _emit(self.config, request)
        with self._stream_slots:
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
        try:
            return await self._client.send(
                _build(self._client, request, self.config.base_path),
                auth=self._auth.for_request(request.auth, request.replayable),
                stream=stream,
            )
        except httpx.TransportError as error:
            raise map_error(error) from error

    async def send(self, request: Request) -> Response:
        """Send ``request`` and return the fully read response."""
        _emit(self.config, request)
        slots, _ = self._semaphores()
        async with slots:
            raw = await self._send(request, stream=False)
            return _response(raw, request, raw.content)

    @asynccontextmanager
    async def open_stream(self, request: Request) -> AsyncIterator[tuple[Response, AsyncIterator[bytes]]]:
        """Yield ``(response, chunks)``; non-2xx responses carry the whole body and no chunks.

        Holds one stream slot until the context exits.
        """
        _emit(self.config, request)
        _, stream_slots = self._semaphores()
        async with stream_slots:
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
