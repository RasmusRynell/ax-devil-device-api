"""Decoders and flow helpers for streamed HTTP bodies (sans-IO).

``StreamDecoder`` implementations plug into the driver's ``StreamResult`` /
``AsyncStreamResult``, which own the connection and close it when the ``with``
block ends:

- ``BytesDecoder`` (in ``_protocols.base``): raw chunks.
- ``LinesDecoder``: text lines (log tails, server-sent text). On a ``multipart`` answer,
  ``MultipartLinesDecoder`` returns the lines of the part bodies instead.
- ``MixedReplaceDecoder``: ``multipart/x-mixed-replace`` (MJPEG, snapshot
  pushes) as ``Part`` values, one per frame.

``stream_flow`` is the generic flow a protocol returns for a streaming
operation: it sends the request with ``stream=True``, turns non-2xx answers
into errors and picks the decoder from the response.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from ._http.types import Headers, Request, Response
from ._protocols.base import BytesDecoder, CallFlow, StreamDecoder
from .errors import ConnectionFailed, ResponseFormatError

DEFAULT_MAX_PART_BYTES = 32 * 1024 * 1024


@dataclass(frozen=True)
class Part:
    """One part of a multipart stream (for MJPEG: one JPEG frame in ``body``)."""

    headers: Headers
    body: bytes

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "").split(";", 1)[0].strip().lower()


def boundary_of(content_type: str) -> str | None:
    """The ``boundary`` parameter of a ``Content-Type`` value, unquoted, or ``None``."""
    for param in content_type.split(";")[1:]:
        key, _, value = param.strip().partition("=")
        if key.strip().lower() == "boundary":
            return value.strip().strip('"').strip() or None  # `boundary=""` is as good as none
    return None


def is_multipart_stream(content_type: str) -> bool:
    return content_type.split(";", 1)[0].strip().lower() in ("multipart/x-mixed-replace", "multipart/mixed")


_HEADERS_END = (b"\r\n\r\n", b"\n\n")


class MixedReplaceDecoder:
    """Incremental parser for ``multipart/x-mixed-replace`` (and ``multipart/mixed``) bodies.

    Uses a part's ``Content-Length`` when present and otherwise scans for the
    next boundary. Tolerates a preamble, bare ``\\n`` line ends, a boundary
    value given with or without the leading ``--``, and a closing
    ``--boundary--``. A body that ends inside a part raises ``ConnectionFailed``.
    """

    def __init__(self, boundary: str, *, api: str = "stream", max_part_bytes: int = DEFAULT_MAX_PART_BYTES) -> None:
        if not boundary or not boundary.strip("-"):
            raise ResponseFormatError(api, "stream", "the multipart boundary is empty")
        self._delimiter = (boundary if boundary.startswith("--") else "--" + boundary).encode("latin-1")
        self._api = api
        self._max = max_part_bytes
        self._buffer = bytearray()
        self._state = "preamble"  # preamble -> headers -> body -> preamble ...
        self._headers = Headers()
        self._length: int | None = None
        self._scanned = 0
        self._done = False

    @classmethod
    def for_response(cls, response: Response, *, api: str = "stream", max_part_bytes: int = DEFAULT_MAX_PART_BYTES) -> MixedReplaceDecoder:
        content_type = response.headers.get("content-type", "")
        boundary = boundary_of(content_type)
        if not is_multipart_stream(content_type) or boundary is None:
            raise ResponseFormatError(api, "stream", f"expected a multipart stream with a boundary, got {content_type!r}")
        return cls(boundary, api=api, max_part_bytes=max_part_bytes)

    def feed(self, chunk: bytes) -> list[Part]:
        if self._done or not chunk:
            return []
        self._buffer += chunk
        parts: list[Part] = []
        while not self._done:
            progressed, part = self._step()
            if part is not None:
                parts.append(part)
            if not progressed:
                break
        return parts

    def close(self) -> list[Part]:
        if self._done or (self._state == "preamble" and not self._buffer.strip()):
            return []
        if self._state == "body" or self._state == "headers":
            raise ConnectionFailed("the stream ended in the middle of a part", request_sent=True)
        return []

    def _step(self) -> tuple[bool, Part | None]:
        """Advance the state machine once: ``(progressed, part)``; ``progressed=False`` means more data is needed."""
        buf = self._buffer
        if self._state == "preamble":
            index = buf.find(self._delimiter)
            if index < 0:
                del buf[: max(0, len(buf) - len(self._delimiter))]  # keep a possible partial delimiter
                return False, None
            after = index + len(self._delimiter)
            if buf[after : after + 2] == b"--":
                self._done = True
                buf.clear()
                return True, None
            line_end = buf.find(b"\n", after)
            if line_end < 0:
                del buf[:index]
                return False, None
            del buf[: line_end + 1]
            self._state = "headers"
            return True, None
        if self._state == "headers":
            end, terminator = -1, b""
            if buf.startswith((b"\r\n", b"\n")):  # a part without headers: blank line right away
                end, terminator = 0, (b"\r\n" if buf.startswith(b"\r\n") else b"\n")
            else:
                for candidate in _HEADERS_END:
                    found = buf.find(candidate)
                    if found >= 0:
                        end, terminator = found, candidate
                        break
            if end < 0:
                if len(buf) > 64 * 1024:
                    raise ResponseFormatError(self._api, "stream", "part headers are too large")
                return False, None
            lines = bytes(buf[:end]).decode("latin-1").splitlines()
            del buf[: end + len(terminator)]
            self._headers = Headers(tuple((k.strip(), v.strip()) for k, _, v in (line.partition(":") for line in lines) if k.strip()))
            self._length = _length(self._headers)
            if self._length is not None and self._length > self._max:
                raise ResponseFormatError(self._api, "stream", f"part of {self._length} bytes exceeds the {self._max} byte limit")
            self._scanned = 0
            self._state = "body"
            return True, None
        # body
        if self._length is not None:
            if len(buf) < self._length:
                return False, None
            body = bytes(buf[: self._length])
            del buf[: self._length]
            self._state = "preamble"
            return True, Part(self._headers, body)
        marker = b"\r\n" + self._delimiter
        index = buf.find(marker, self._scanned)
        width = len(marker)
        if index < 0:
            index = buf.find(b"\n" + self._delimiter, self._scanned)
            width = len(self._delimiter) + 1
        if index < 0:
            if len(buf) > self._max + len(marker):  # a partial delimiter may be buffered after the body
                raise ResponseFormatError(self._api, "stream", f"part exceeds the {self._max} byte limit")
            self._scanned = max(0, len(buf) - len(marker))
            return False, None
        if index > self._max:
            raise ResponseFormatError(self._api, "stream", f"part exceeds the {self._max} byte limit")
        body = bytes(buf[:index])
        del buf[: index + (width - len(self._delimiter))]  # keep the delimiter for the preamble step
        self._state = "preamble"
        return True, Part(self._headers, body)


def _length(headers: Headers) -> int | None:
    value = headers.get("content-length")
    if value is None:
        return None
    try:
        length = int(value)
    except ValueError:
        return None
    return length if length >= 0 else None


class LinesDecoder:
    """Split a text body into lines (without terminators). A final unterminated line is returned on ``close``."""

    def __init__(self, encoding: str = "utf-8") -> None:
        self._encoding = encoding
        self._buffer = b""

    def feed(self, chunk: bytes) -> list[str]:
        self._buffer += chunk
        *lines, self._buffer = self._buffer.split(b"\n")
        return [line.rstrip(b"\r").decode(self._encoding, errors="replace") for line in lines]

    def close(self) -> list[str]:
        rest, self._buffer = self._buffer, b""
        return [rest.rstrip(b"\r").decode(self._encoding, errors="replace")] if rest else []


class MultipartLinesDecoder:
    """Lines of a ``multipart/x-mixed-replace`` text stream: every part body is split into lines.

    Boundaries and part headers are consumed, so only the text of the parts is returned. Blank lines
    are dropped: a part without content is the device's keep-alive, not an item.
    """

    def __init__(self, parts: MixedReplaceDecoder, encoding: str = "utf-8") -> None:
        self._parts = parts
        self._encoding = encoding

    def _lines(self, parts: list[Part]) -> list[str]:
        out: list[str] = []
        for part in parts:
            out.extend(line for line in part.body.decode(self._encoding, errors="replace").splitlines() if line.strip())
        return out

    def feed(self, chunk: bytes) -> list[str]:
        return self._lines(self._parts.feed(chunk))

    def close(self) -> list[str]:
        return self._lines(self._parts.close())


def stream_flow(
    request: Request,
    decoder_for: Callable[[Response], StreamDecoder[object]],
    error_for: Callable[[Response], Exception],
) -> CallFlow[StreamDecoder[object]]:
    """Generic streaming call: send ``request`` with ``stream=True``, return the decoder for a 2xx answer.

    ``error_for`` receives the fully read response for any other status (the
    protocol's own error parsing); ``decoder_for`` receives the 2xx headers.
    """
    response = yield replace(request, stream=True)
    if not 200 <= response.status < 300:
        raise error_for(response)
    return decoder_for(response)


def mjpeg_decoder(response: Response, *, api: str = "stream") -> StreamDecoder[Part]:
    """Decoder for an MJPEG answer; a plain ``image/jpeg`` answer is not a stream and is rejected."""
    return MixedReplaceDecoder.for_response(response, api=api)


def decoder_for(codec: object, response: Response, *, api: str = "stream") -> StreamDecoder[object]:
    """Decoder for a streamed answer, chosen by a ``Stream`` reply codec (``decoder`` and ``encoding`` attributes).

    Anything without a ``decoder`` attribute gets the raw bytes.
    """
    kind = getattr(codec, "decoder", "bytes")
    if kind == "mjpeg":
        return mjpeg_decoder(response, api=api)
    if kind == "lines":
        encoding = getattr(codec, "encoding", "utf-8")
        content_type = response.headers.get("content-type", "")
        if is_multipart_stream(content_type) and boundary_of(content_type) is not None:
            return MultipartLinesDecoder(MixedReplaceDecoder.for_response(response, api=api), encoding)
        return LinesDecoder(encoding)
    if kind == "bytes":
        return BytesDecoder()
    raise ValueError(f"unknown stream decoder {kind!r}")


__all__ = [
    "LinesDecoder",
    "MixedReplaceDecoder",
    "MultipartLinesDecoder",
    "Part",
    "boundary_of",
    "decoder_for",
    "is_multipart_stream",
    "mjpeg_decoder",
    "stream_flow",
]

