"""A fake WebSocket camera for unit tests: no sockets, no threads of its own.

``FakeWsCamera.transport()`` / ``.async_transport()`` return httpx transports that
answer the handshake with ``101`` and a fake network stream (httpcore's
``NetworkStream`` interface). A wsproto *server* connection sits behind the
stream, so httpx-ws talks real WebSocket frames to it.
"""

from __future__ import annotations

import asyncio
import json
import queue
from collections.abc import Callable
from typing import Any

import httpcore
import httpx
import wsproto
import wsproto.connection
import wsproto.events

_NETWORK_ERROR = b"<network error>"
"""Queued on a stream to make its next ``read`` raise ``httpcore.ReadError`` (a connection that failed)."""

Handler = Callable[["FakeSocket", Any], None]


class FakeSocket:
    """Server side of one connection."""

    def __init__(self, emit: Callable[[bytes], None], handler: Handler | None) -> None:
        self.conn = wsproto.connection.Connection(wsproto.ConnectionType.SERVER)
        self._emit = emit
        self.handler = handler
        self.received: list[Any] = []
        self.pings = 0
        self.answer_pings = True
        self.closed_by_client: int | None = None
        self.close_frames = 0

    # -- called by the stream
    def feed(self, data: bytes) -> None:
        self.conn.receive_data(data)
        for event in self.conn.events():
            if isinstance(event, wsproto.events.Ping):
                self.pings += 1
                if self.answer_pings:
                    self._emit(self.conn.send(event.response()))
            elif isinstance(event, wsproto.events.TextMessage):
                message = json.loads(event.data)
                self.received.append(message)
                if self.handler is not None:
                    self.handler(self, message)
            elif isinstance(event, wsproto.events.BytesMessage):
                self.received.append(bytes(event.data))
            elif isinstance(event, wsproto.events.CloseConnection):
                self.closed_by_client = event.code
                self.close_frames += 1
                if self.conn.state == wsproto.connection.ConnectionState.REMOTE_CLOSING:
                    self._emit(self.conn.send(event.response()))

    # -- used by tests
    def push(self, message: Any) -> None:
        self._emit(self.conn.send(wsproto.events.TextMessage(json.dumps(message))))

    def push_bytes(self, data: bytes) -> None:
        self._emit(self.conn.send(wsproto.events.BytesMessage(data)))

    def push_fragments(self, *parts: str | bytes) -> None:
        """One message split over several frames (text or binary)."""
        event = wsproto.events.TextMessage if isinstance(parts[0], str) else wsproto.events.BytesMessage
        for index, part in enumerate(parts):
            self._emit(self.conn.send(event(part, message_finished=index == len(parts) - 1)))  # pyright: ignore[reportArgumentType]

    def close(self, code: int = 1000, reason: str = "") -> None:
        self._emit(self.conn.send(wsproto.events.CloseConnection(code, reason)))

    def network_error(self) -> None:
        """The connection fails: the reader gets a read error."""
        self._emit(_NETWORK_ERROR)

    def drop(self) -> None:
        """End of stream without a close frame."""
        self._emit(b"")


class SyncStream:
    def __init__(self, handler: Handler | None) -> None:
        self._out: queue.Queue[bytes] = queue.Queue()
        self.socket = FakeSocket(self._out.put, handler)
        self.closed = False

    def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        if self.closed:
            return b""
        data = self._out.get()
        if data is _NETWORK_ERROR:
            raise httpcore.ReadError("connection failed")
        return data

    def write(self, buffer: bytes, timeout: float | None = None) -> None:
        self.socket.feed(buffer)

    def close(self) -> None:
        self.closed = True
        self._out.put(b"")

    def get_extra_info(self, info: str) -> Any:
        return None


class AsyncStream:
    def __init__(self, handler: Handler | None) -> None:
        self._out: asyncio.Queue[bytes] = asyncio.Queue()
        self.socket = FakeSocket(self._out.put_nowait, handler)
        self.closed = False

    async def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        if self.closed:
            return b""
        data = await self._out.get()
        if data is _NETWORK_ERROR:
            raise httpcore.ReadError("connection failed")
        return data

    async def write(self, buffer: bytes, timeout: float | None = None) -> None:
        self.socket.feed(buffer)

    async def aclose(self) -> None:
        self.closed = True
        self._out.put_nowait(b"")

    def get_extra_info(self, info: str) -> Any:
        return None


DIGEST = 'Digest realm="AXIS_TEST", nonce="abc123", qop="auth", algorithm=MD5'


class FakeWsCamera:
    """Answers WebSocket handshakes and records every HTTP request it sees."""

    def __init__(self, *, handler: Handler | None = None, digest: bool = False, token_digest: bool = False, refuse: int | None = None) -> None:
        self.handler = handler
        self.digest = digest
        self.token_digest = token_digest
        self.refuse = refuse
        self.requests: list[httpx.Request] = []
        self.authorization: list[str | None] = []
        """The Authorization header of each request as it arrived."""
        self.sockets: list[FakeSocket] = []
        self.streams: list[SyncStream | AsyncStream] = []
        self.token = "1331901001644832701"
        self._async = False

    def _answer(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        self.authorization.append(request.headers.get("authorization"))
        if request.url.path == "/axis-cgi/wssession.cgi":
            if self.token_digest and "authorization" not in request.headers:
                return httpx.Response(401, headers={"WWW-Authenticate": DIGEST}, text="unauthorized")
            return httpx.Response(200, text=self.token + "\n")
        if self.digest and "authorization" not in request.headers:
            return httpx.Response(401, headers={"WWW-Authenticate": DIGEST}, text="unauthorized")
        if self.refuse is not None:
            return httpx.Response(self.refuse, text="refused")
        assert request.headers["upgrade"] == "websocket" and request.headers["sec-websocket-version"] == "13"
        stream: SyncStream | AsyncStream = AsyncStream(self.handler) if self._async else SyncStream(self.handler)
        self.streams.append(stream)
        self.sockets.append(stream.socket)
        return httpx.Response(101, headers={"Upgrade": "websocket"}, extensions={"network_stream": stream})

    def transport(self) -> httpx.MockTransport:
        self._async = False
        return httpx.MockTransport(self._answer)

    def async_transport(self) -> httpx.MockTransport:
        self._async = True
        return httpx.MockTransport(self._answer)

    @property
    def ws_requests(self) -> list[httpx.Request]:
        return [r for r in self.requests if r.headers.get("upgrade") == "websocket"]


def events_handler(socket: FakeSocket, message: Any) -> None:
    """Event-stream server: acknowledges ``events:configure``."""
    if message.get("method") == "events:configure":
        socket.push({"apiVersion": "1.0", "context": message["context"], "method": "events:configure", "data": {}})


def notify(topic: str = "tns1:Device/tnsaxis:IO/VirtualPort", **data: str) -> dict[str, Any]:
    return {
        "apiVersion": "1.0",
        "method": "events:notify",
        "params": {"notification": {"timestamp": 1639385866198, "topic": topic, "message": {"source": {"port": "1"}, "key": {}, "data": data}}},
    }
