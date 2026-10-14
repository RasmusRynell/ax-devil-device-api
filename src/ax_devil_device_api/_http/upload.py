"""File content accepted by upload operations.

Every generated upload argument has the type ``UploadSource``:

- ``bytes`` (or ``bytearray``/``memoryview``): the content itself.
- a ``pathlib.Path`` (any ``os.PathLike``): read lazily in chunks when the request is sent.
  A ``str`` is not accepted: it is ambiguous between a path and text.
- ``Upload(stream, size)``: a binary stream (``read(n) -> bytes``) with the number of bytes to send.

The file name sent to the device is the path's name, ``Upload.filename``, or the spec's default.
Content up to ``INLINE_LIMIT`` bytes is read into memory, so the request can be replayed after
an authentication challenge. Larger content is streamed with a ``Content-Length`` header (some
device CGIs reject chunked bodies). A streamed body cannot be replayed, so the transport first
sends a cheap authenticated GET (``usergroup.cgi``) to verify the credentials, then streams.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Annotated, Any, BinaryIO

from pydantic import PlainValidator

from .._validate import non_negative_int
from .types import DeferredContent, FilePart, check_header_text

CHUNK_SIZE = 64 * 1024
INLINE_LIMIT = 8 * 1024 * 1024
"""Largest upload read into memory (and so replayable) instead of streamed."""


@dataclass(eq=False)
class Upload:
    """A binary stream and the number of bytes to send from it.

    ``size`` must be exact: the request declares it as the content length.
    The stream is read once, from its current position (small uploads are then kept in memory, so repeating a failed call is safe).
    """

    stream: BinaryIO
    size: int
    filename: str | None = None
    content_type: str | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    """Held while the stream is read (in a worker thread for async calls): a cancelled call cannot stop a read that
    is running, so a retry waits for it and then reuses the buffer instead of reading the one-shot stream twice."""
    _failure: Exception | None = field(default=None, init=False, repr=False)
    _buffer: bytes | None = field(default=None, init=False, repr=False)
    """Content of a small upload, kept after the first read: the stream is one-shot, so a call that failed before
    the body was sent (no free slot, a failing hook, a connection error) can be repeated with the same source."""

    def __post_init__(self) -> None:
        non_negative_int("Upload size", self.size)
        if self.filename is not None:
            check_header_text("Upload filename", self.filename)
        if self.content_type is not None:
            check_header_text("Upload content_type", self.content_type)

    def _buffered(self) -> bytes:
        """The whole content of a small upload, read once under the lock and kept; a failed read stays failed."""
        with self._lock:
            if self._buffer is None:
                if self._failure is not None:
                    raise ValueError(f"the upload stream already failed and cannot be read again: {self._failure}") from self._failure
                try:
                    self._buffer = b"".join(_read_exactly(self.stream, self.size))
                except Exception as error:
                    self._failure = error
                    raise
            return self._buffer


@dataclass(frozen=True)
class UploadSpec:
    """How one upload argument is sent: the params ``field``, the multipart ``part`` name
    (default: the field's wire name), and the file name and content type used when the
    value itself carries none (``bytes``)."""

    field: str
    part: str | None = None
    filename: str | None = None
    content_type: str | None = None


def _validate(value: Any) -> Any:
    if isinstance(value, (bytes, Upload)):
        return value
    if isinstance(value, (bytearray, memoryview)):
        return bytes(value)
    if isinstance(value, os.PathLike):
        return value
    if isinstance(value, str):
        raise ValueError("pass file content as bytes, a pathlib.Path or an Upload; a str is ambiguous")
    raise ValueError(f"expected bytes, a path or an Upload, got {type(value).__name__}")


if TYPE_CHECKING:
    UploadSource = bytes | os.PathLike[str] | Upload
else:
    UploadSource = Annotated[Any, PlainValidator(_validate)]


class _PathChunks:
    """Chunks of a file, opened when iteration starts and closed when it ends."""

    def __init__(self, path: os.PathLike[str], size: int) -> None:
        self._path, self._size = path, size

    def __iter__(self) -> Iterator[bytes]:
        with open(self._path, "rb") as handle:
            yield from _read_exactly(handle, self._size)


class _StreamChunks:
    def __init__(self, stream: BinaryIO, size: int) -> None:
        self._stream, self._size = stream, size

    def __iter__(self) -> Iterator[bytes]:
        return _read_exactly(self._stream, self._size)


def _read_exactly(stream: BinaryIO, size: int) -> Iterator[bytes]:
    remaining = size
    while remaining:
        chunk = stream.read(min(CHUNK_SIZE, remaining))
        if not chunk:
            raise ValueError(f"upload stream ended {remaining} bytes before its declared size of {size}")
        remaining -= len(chunk)
        yield chunk


def resolve_upload(value: UploadSource, *, filename: str | None, content_type: str | None) -> tuple[bytes | _PathChunks | _StreamChunks, int, str | None, str | None]:
    """``(content, size, filename, content_type)`` of an upload argument; given names win over the defaults.

    Blocking: it stats and reads files and streams. Flows use ``deferred_upload`` instead.
    """
    name, ctype = _names(value, filename, content_type)
    content, size = _load(value)
    return content, size, name, ctype


def _names(value: UploadSource, filename: str | None, content_type: str | None) -> tuple[str | None, str | None]:
    """File name and content type of an upload argument (no I/O)."""
    if isinstance(value, bytes):
        return filename, content_type
    if isinstance(value, Upload):
        return value.filename or filename, value.content_type or content_type
    return os.path.basename(os.fspath(value)) or filename, content_type


def _load(value: UploadSource) -> tuple[bytes | _PathChunks | _StreamChunks, int]:
    if isinstance(value, bytes):
        return value, len(value)
    if isinstance(value, Upload):
        if value.size <= INLINE_LIMIT:
            return value._buffered(), value.size
        return _StreamChunks(value.stream, value.size), value.size
    path = os.fspath(value)
    size = os.stat(path).st_size
    if size <= INLINE_LIMIT:
        with open(path, "rb") as handle:
            return b"".join(_read_exactly(handle, size)), size
    return _PathChunks(value, size), size


def deferred_upload(
    value: UploadSource, *, filename: str | None, content_type: str | None,
) -> tuple[bytes | DeferredContent, str | None, str | None]:
    """``(content, filename, content_type)`` without touching the file or stream.

    ``bytes`` are returned as they are. Anything else becomes a ``DeferredContent`` that the driver
    reads just before sending (off the event loop for async calls), so building a request never blocks.
    """
    name, ctype = _names(value, filename, content_type)
    if isinstance(value, bytes):
        return value, name, ctype
    return DeferredContent(lambda: _load(value)), name, ctype


def file_part(
    part: str, value: UploadSource, *, filename: str | None = None, content_type: str | None = None,
) -> FilePart:
    """A multipart file part for an upload argument; its content is read when the request is sent."""
    content, name, ctype = deferred_upload(value, filename=filename, content_type=content_type)
    return FilePart(part, name or part, content, ctype or "application/octet-stream", size=len(content) if isinstance(content, bytes) else None)
