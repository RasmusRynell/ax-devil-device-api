"""``multipart/form-data`` encoding for request bodies.

Pure functions, no I/O. Protocols describe a ``MultipartBody``; the transport
encodes it here. Small bodies become ``bytes``; bodies with iterable file
content (firmware images) are produced lazily and never held in memory.
"""

from __future__ import annotations

import secrets
from collections.abc import Iterator
from dataclasses import dataclass

from .types import DeferredContent, FilePart, MultipartBody


@dataclass(frozen=True)
class EncodedMultipart:
    content_type: str
    content: bytes | Iterator[bytes]
    length: int | None
    """Total body size when known (always for ``bytes``), else ``None``."""

    @property
    def replayable(self) -> bool:
        return isinstance(self.content, bytes)


def new_boundary() -> str:
    return "axdevil-" + secrets.token_hex(16)


def _quote(value: str) -> str:
    """Escape a header parameter value (RFC 7578 section 4.2 / WHATWG form-data rules)."""
    return value.replace("\\", "\\\\").replace('"', "%22").replace("\r", "%0D").replace("\n", "%0A")


def _check_boundary(boundary: str) -> None:
    if not boundary or len(boundary) > 70 or not all(c.isalnum() or c in "'()+_,-./:=?" for c in boundary):
        raise ValueError(f"Invalid multipart boundary: {boundary!r}")


def _field_head(boundary: str, name: str, value: str) -> bytes:
    head = f'--{boundary}\r\nContent-Disposition: form-data; name="{_quote(name)}"\r\n\r\n'
    return head.encode("utf-8") + value.encode("utf-8") + b"\r\n"


def _file_head(boundary: str, part: FilePart) -> bytes:
    filename = "" if part.filename is None else f'; filename="{_quote(part.filename)}"'
    head = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="{_quote(part.name)}"{filename}\r\n'
        f"Content-Type: {part.content_type}\r\n\r\n"
    )
    return head.encode("utf-8")


def encode_multipart(body: MultipartBody) -> EncodedMultipart:
    """Encode ``body``: text fields in order, then each file.

    Content types of text fields are omitted (the default is ``text/plain``).
    Raises ``ValueError`` for a malformed boundary.
    """
    boundary = body.boundary or new_boundary()
    _check_boundary(boundary)
    content_type = f"multipart/form-data; boundary={boundary}"
    closing = f"--{boundary}--\r\n".encode("ascii")
    prefix = b"".join(_field_head(boundary, k, v) for k, v in body.fields)

    if body.replayable:
        pieces = [prefix]
        for part in body.files:
            assert isinstance(part.content, bytes)
            pieces += [_file_head(boundary, part), part.content, b"\r\n"]
        pieces.append(closing)
        data = b"".join(pieces)
        return EncodedMultipart(content_type, data, len(data))

    heads = [_file_head(boundary, part) for part in body.files]
    lengths = [part.length for part in body.files]
    length = None if any(n is None for n in lengths) else (
        len(prefix) + len(closing) + sum(len(h) + 2 + (n or 0) for h, n in zip(heads, lengths))
    )

    def chunks() -> Iterator[bytes]:
        if prefix:
            yield prefix
        for head, part in zip(heads, body.files):
            yield head
            if isinstance(part.content, bytes):
                yield part.content
            else:
                assert not isinstance(part.content, DeferredContent)  # the driver resolves it before sending
                iterator = iter(part.content)
                try:
                    yield from iterator
                finally:
                    close = getattr(iterator, "close", None)
                    if callable(close):
                        close()
            yield b"\r\n"
        yield closing

    return EncodedMultipart(content_type, chunks(), length)
