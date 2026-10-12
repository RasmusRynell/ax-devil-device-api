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
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any, BinaryIO

from pydantic import PlainValidator

from .types import FilePart

CHUNK_SIZE = 64 * 1024
INLINE_LIMIT = 8 * 1024 * 1024
"""Largest upload read into memory (and so replayable) instead of streamed."""


@dataclass(eq=False)
class Upload:
    """A binary stream and the number of bytes to send from it.

    ``size`` must be exact: the request declares it as the content length.
    The stream is read once, from its current position.
    """

    stream: BinaryIO
    size: int
    filename: str | None = None
    content_type: str | None = None

    def __post_init__(self) -> None:
        if self.size < 0:
            raise ValueError("Upload size cannot be negative")


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
    """``(content, size, filename, content_type)`` of an upload argument; given names win over the defaults."""
    if isinstance(value, bytes):
        return value, len(value), filename, content_type
    if isinstance(value, Upload):
        name, ctype = value.filename or filename, value.content_type or content_type
        if value.size <= INLINE_LIMIT:
            return b"".join(_read_exactly(value.stream, value.size)), value.size, name, ctype
        return _StreamChunks(value.stream, value.size), value.size, name, ctype
    path = os.fspath(value)
    size = os.stat(path).st_size
    name = os.path.basename(path) or filename
    if size <= INLINE_LIMIT:
        with open(path, "rb") as handle:
            return b"".join(_read_exactly(handle, size)), size, name, content_type
    return _PathChunks(value, size), size, name, content_type


def file_part(
    part: str, value: UploadSource, *, filename: str | None = None, content_type: str | None = None,
) -> FilePart:
    """A multipart file part for an upload argument (always with its size)."""
    content, size, name, ctype = resolve_upload(value, filename=filename, content_type=content_type)
    return FilePart(part, name or part, content, ctype or "application/octet-stream", size=size)
