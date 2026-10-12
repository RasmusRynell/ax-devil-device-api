"""Transport-neutral request and response values.

These types know HTTP, nothing about VAPIX. Protocol flows build ``Request``
values and parse ``Response`` values without doing I/O.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

AuthPolicy = Literal["required", "anonymous", "if_challenged"]
"""How a request authenticates.

- ``required``: anonymous first; on a challenge authenticate (Digest preferred).
  A verified credential is sent pre-emptively on later requests.
- ``anonymous``: never send credentials.
- ``if_challenged``: like ``required`` but never sends a pre-emptive credential,
  so devices that allow anonymous access are used anonymously.
"""


@dataclass(frozen=True)
class JsonBody:
    """JSON request body; sets ``Content-Type: application/json``."""

    value: Any
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

    content: bytes | Iterable[bytes] | AsyncIterable[bytes]
    content_type: str

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
    device CGIs do not accept.
    """

    name: str
    filename: str
    content: bytes | Iterable[bytes]
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
    query: tuple[tuple[str, str], ...] = ()
    body: Body | None = None
    accept: str | None = None
    headers: tuple[tuple[str, str], ...] = ()
    auth: AuthPolicy = "required"
    timeout: float | None = None
    stream: bool = False

    def __post_init__(self) -> None:
        if not self.path.startswith("/"):
            raise ValueError(f"Request path must be absolute: {self.path!r}")
        if "?" in self.path:
            raise ValueError(f"Request path must not contain a query; use query=: {self.path!r}")

    @property
    def replayable(self) -> bool:
        return self.body is None or self.body.replayable


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
        return self.content.decode(charset, errors="replace")

    def excerpt(self, limit: int = 200) -> str:
        text = self.text.strip()
        return text if len(text) <= limit else text[:limit] + "…"


Query = Mapping[str, str] | Iterable[tuple[str, str]]


def query_items(query: Query | None) -> tuple[tuple[str, str], ...]:
    """Normalize a mapping or pair list into the ``Request.query`` form."""
    if query is None:
        return ()
    if isinstance(query, Mapping):
        return tuple((str(k), str(v)) for k, v in query.items())
    return tuple((str(k), str(v)) for k, v in query)
