"""Transport-neutral request and response values.

These types know HTTP, nothing about VAPIX. Protocol flows build ``Request``
values and parse ``Response`` values without doing I/O.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Literal

from ..errors import ResponseFormatError

AuthPolicy = Literal["required", "anonymous", "if_challenged"]
"""How a request authenticates.

- ``required``: anonymous first; on a challenge authenticate (Digest preferred).
  A verified credential is sent pre-emptively on later requests.
- ``anonymous``: never send credentials.
- ``if_challenged``: like ``required`` but never sends a pre-emptive credential,
  so devices that allow anonymous access are used anonymously.
"""


class DeferredContent:
    """Upload content whose reading is postponed until the driver sends the request.

    The flows are sans-IO, so they cannot read files or streams themselves. They hand over this
    marker instead; the driver calls ``resolve_deferred`` (in a worker thread for async calls, so
    no blocking read runs on the event loop) before the request reaches the transport.
    ``load`` returns ``(content, size)``: ``bytes`` (replayable) or a chunk iterable (one-shot).
    """

    __slots__ = ("_load",)

    def __init__(self, load: Callable[[], tuple[bytes | Iterable[bytes], int]]) -> None:
        self._load = load

    def resolve(self) -> tuple[bytes | Iterable[bytes], int]:
        return self._load()


@dataclass(frozen=True)
class JsonBody:
    """JSON request body; sets ``Content-Type: application/json``.

    ``sensitive`` marks a body that is a secret as a whole (a scalar DCA/REST value such as a password): debug
    hooks see every leaf redacted, whatever the keys are called.
    """

    value: Any
    sensitive: bool = False
    replayable: bool = field(default=True, init=False)


@dataclass(frozen=True)
class FormBody:
    """URL-encoded form body; sets ``Content-Type: application/x-www-form-urlencoded``."""

    fields: tuple[tuple[str, str], ...]
    replayable: bool = field(default=True, init=False)


@dataclass(frozen=True)
class RawBody:
    """Opaque body with an explicit content type.

    ``bytes`` content is replayable. An iterable of chunks is sent as a
    stream and is not replayable: it cannot be re-sent after an
    authentication challenge.
    """

    content: bytes | Iterable[bytes] | AsyncIterable[bytes] | DeferredContent
    content_type: str
    size: int | None = None
    """Byte count of a streamed ``content``; with it the request gets a ``Content-Length`` header."""

    @property
    def replayable(self) -> bool:
        return isinstance(self.content, bytes)


@dataclass(frozen=True)
class FilePart:
    """One file in a multipart body.

    ``content`` is ``bytes`` (replayable) or an iterable of chunks for large
    files such as firmware images (one-shot, so the body is not replayable).
    ``size`` is the total byte count of an iterable; with it the request gets
    a ``Content-Length`` instead of chunked transfer encoding, which some
    device CGIs do not accept. Without a ``filename`` the part is a plain
    field with a content type (a JSON part).
    """

    name: str
    filename: str | None
    content: bytes | Iterable[bytes] | DeferredContent
    content_type: str = "application/octet-stream"
    size: int | None = None

    @property
    def length(self) -> int | None:
        return len(self.content) if isinstance(self.content, bytes) else self.size


@dataclass(frozen=True)
class MultipartBody:
    """``multipart/form-data`` body: text fields first, then files, in the given order.

    Encoded by ``_http.multipart.encode_multipart``. ``boundary`` is generated
    unless given (tests, reproducible requests).
    """

    fields: tuple[tuple[str, str], ...] = ()
    files: tuple[FilePart, ...] = ()
    boundary: str | None = None

    @property
    def replayable(self) -> bool:
        return all(isinstance(f.content, bytes) for f in self.files)


Body = JsonBody | FormBody | RawBody | MultipartBody


@dataclass(frozen=True)
class Request:
    """One HTTP request to the device.

    Headers are derived, never defaulted: the body type decides
    ``Content-Type`` and ``accept`` decides ``Accept``. ``headers`` holds only
    extra headers a protocol genuinely needs.
    """

    method: str
    path: str
    query: tuple[tuple[str, str | None], ...] = ()
    """Query arguments; a ``None`` value sends the bare key (``?live-sum.json``)."""
    body: Body | None = None
    accept: str | None = None
    headers: tuple[tuple[str, str], ...] = ()
    auth: AuthPolicy = "required"
    timeout: float | None = None
    stream: bool = False
    masked: frozenset[str] = frozenset()
    """Wire names (``x-masked`` fields of this operation, nested ones too; ``{placeholder}`` templates allowed) that
    debug hooks redact in this request's record only."""

    def __post_init__(self) -> None:
        if not self.path.startswith("/"):
            raise ValueError(f"Request path must be absolute: {self.path!r}")
        if "?" in self.path:
            raise ValueError(f"Request path must not contain a query; use query=: {self.path!r}")

    @property
    def replayable(self) -> bool:
        return self.body is None or self.body.replayable


def has_deferred(request: Request) -> bool:
    """Whether ``request`` still carries upload content that has to be read (see ``DeferredContent``)."""
    body = request.body
    if isinstance(body, RawBody):
        return isinstance(body.content, DeferredContent)
    if isinstance(body, MultipartBody):
        return any(isinstance(part.content, DeferredContent) for part in body.files)
    return False


def resolve_deferred(request: Request) -> Request:
    """``request`` with every ``DeferredContent`` read. Blocking: async callers run it in a thread."""
    body = request.body
    if isinstance(body, RawBody) and isinstance(body.content, DeferredContent):
        content, size = body.content.resolve()
        return replace(request, body=replace(body, content=content, size=size))
    if isinstance(body, MultipartBody) and any(isinstance(part.content, DeferredContent) for part in body.files):
        files = []
        for part in body.files:
            if isinstance(part.content, DeferredContent):
                content, size = part.content.resolve()
                part = replace(part, content=content, size=size)
            files.append(part)
        return replace(request, body=replace(body, files=tuple(files)))
    return request


class Headers(Mapping[str, str]):
    """Immutable, case-insensitive header mapping.

    Repeated headers are joined with ``", "`` as in RFC 9110, except that the
    raw list stays available in ``items_raw`` (``WWW-Authenticate`` may repeat).
    """

    __slots__ = ("_items", "_map")

    def __init__(self, items: Iterable[tuple[str, str]] = ()) -> None:
        self._items = tuple((k, v) for k, v in items)
        merged: dict[str, str] = {}
        for key, value in self._items:
            lower = key.lower()
            merged[lower] = f"{merged[lower]}, {value}" if lower in merged else value
        self._map = merged

    def __getitem__(self, key: str) -> str:
        return self._map[key.lower()]

    def __iter__(self):
        return iter(self._map)

    def __len__(self) -> int:
        return len(self._map)

    def get_all(self, key: str) -> list[str]:
        lower = key.lower()
        return [v for k, v in self._items if k.lower() == lower]

    @property
    def items_raw(self) -> tuple[tuple[str, str], ...]:
        return self._items

    def __repr__(self) -> str:
        return f"Headers({list(self._items)!r})"


@dataclass(frozen=True)
class Response:
    """One HTTP response.

    For a ``stream=True`` request whose status is 2xx, ``content`` is empty and
    the body is delivered through the driver's stream result. For any other
    status the driver reads the full body first, so protocols can parse errors.
    """

    status: int
    headers: Headers
    content: bytes
    request: Request

    @property
    def media_type(self) -> str:
        return self.headers.get("content-type", "").split(";", 1)[0].strip().lower()

    @property
    def text(self) -> str:
        charset = "utf-8"
        for part in self.headers.get("content-type", "").split(";")[1:]:
            key, _, value = part.strip().partition("=")
            if key.lower() == "charset" and value:
                charset = value.strip('"')
        try:
            return self.content.decode(charset, errors="replace")
        except (LookupError, UnicodeError):
            # An unknown (or non-text) charset label is a malformed response, not a programming error.
            raise ResponseFormatError(
                "http", f"{self.request.method} {self.request.path}", f"unsupported response charset {charset!r}"
            ) from None

    def excerpt(self, limit: int = 200) -> str:
        """The start of the body for error messages; never raises (an unusable charset falls back to UTF-8)."""
        try:
            text = self.text
        except ResponseFormatError:
            text = self.content.decode("utf-8", errors="replace")
        text = text.strip()
        return text if len(text) <= limit else text[:limit] + "…"


Query = Mapping[str, str] | Iterable[tuple[str, str]]


def query_items(query: Query | None) -> tuple[tuple[str, str], ...]:
    """Normalize a mapping or pair list into the ``Request.query`` form."""
    if query is None:
        return ()
    if isinstance(query, Mapping):
        return tuple((str(k), str(v)) for k, v in query.items())
    return tuple((str(k), str(v)) for k, v in query)
