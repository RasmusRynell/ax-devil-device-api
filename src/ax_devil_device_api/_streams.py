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
DEFAULT_MAX_LINE_BYTES = 1024 * 1024
"""Longest line a lines decoder accepts; a stream without newlines would otherwise buffer without bound."""


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
        self._undecided = False
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
                for candidate in _HEADERS_END:  # whichever terminator comes first ends the headers, not the first listed
                    found = buf.find(candidate)
                    if found >= 0 and (end < 0 or found < end):
                        end, terminator = found, candidate
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
        found = self._find_boundary(buf)
        if found is None:  # no complete boundary line yet
            if not self._undecided and len(buf) > self._max + len(self._delimiter) + 2:  # a partial delimiter may be buffered after the body
                raise ResponseFormatError(self._api, "stream", f"part exceeds the {self._max} byte limit")
            return False, None
        body_end, consumed = found
        if body_end > self._max:
            raise ResponseFormatError(self._api, "stream", f"part exceeds the {self._max} byte limit")
        body = bytes(buf[:body_end])
        del buf[:consumed]  # keep the delimiter for the preamble step
        self._state = "preamble"
        return True, Part(self._headers, body)

    def _find_boundary(self, buf: bytearray) -> tuple[int, int] | None:
        """``(end of the part body, bytes to drop before the delimiter)`` of the next real boundary line, or ``None``.

        A real boundary is a line break, the delimiter, and then ``--``, or optional blanks and a line end. The same
        bytes inside the content (``\\r\\n--<boundary>x``) do not end the part. If the bytes after a candidate have
        not arrived yet, scanning resumes at that candidate with the next chunk.
        """
        delimiter, width = self._delimiter, len(self._delimiter)
        start = self._scanned
        self._undecided = False
        while True:
            pos = buf.find(b"\n" + delimiter, start)
            if pos < 0:
                self._scanned = max(0, len(buf) - width - 1)
                return None
            verdict = self._boundary_suffix(buf, pos + 1 + width)
            if verdict is None and len(buf) - pos > 1024:
                verdict = False  # endless blanks after the delimiter: not a boundary line
            if verdict is None:  # undecided: wait for more data
                if (pos - 1 if pos > 0 and buf[pos - 1] == 13 else pos) > self._max:
                    raise ResponseFormatError(self._api, "stream", f"part exceeds the {self._max} byte limit")
                self._scanned = pos
                self._undecided = True  # a candidate waits for its suffix; its position was checked against the limit
                return None
            if verdict:
                body_end = pos - 1 if pos > 0 and buf[pos - 1] == 13 else pos
                return body_end, pos + 1
            start = pos + 1

    @staticmethod
    def _boundary_suffix(buf: bytearray, at: int) -> bool | None:
        """Whether what follows the delimiter ends a boundary line (``None``: not enough data to tell)."""
        if buf[at : at + 2] == b"--":
            return True
        if len(buf) - at < 2 and buf[at : at + 1] in (b"", b"-"):
            return None
        index = at
        while index < len(buf) and buf[index] in b" \t":
            index += 1
        if index >= len(buf):
            return None
        if buf[index] == 10:
            return True
        if buf[index] == 13:
            return True if index + 1 < len(buf) and buf[index + 1] == 10 else (None if index + 1 >= len(buf) else False)
        return False


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

    def __init__(self, encoding: str = "utf-8", *, api: str = "stream", max_line_bytes: int = DEFAULT_MAX_LINE_BYTES) -> None:
        self._encoding = encoding
        self._api = api
        self._max = max_line_bytes
        self._buffer = b""

    def _too_long(self) -> ResponseFormatError:
        return ResponseFormatError(self._api, "stream", f"a line exceeds {self._max} bytes; the stream has no line breaks")

    def feed(self, chunk: bytes) -> list[str]:
        self._buffer += chunk
        *lines, self._buffer = self._buffer.split(b"\n")
        if len(self._buffer) > self._max or any(len(line) > self._max for line in lines):
            self._buffer = b""
            raise self._too_long()
        return [line.rstrip(b"\r").decode(self._encoding, errors="replace") for line in lines]

    def close(self) -> list[str]:
        rest, self._buffer = self._buffer, b""
        return [rest.rstrip(b"\r").decode(self._encoding, errors="replace")] if rest else []


class MultipartLinesDecoder:
    """Lines of a ``multipart/x-mixed-replace`` text stream: every part body is split into lines.

    Boundaries and part headers are consumed, so only the text of the parts is returned. Blank lines
    are dropped: a part without content is the device's keep-alive, not an item.
    """

    def __init__(
        self, parts: MixedReplaceDecoder, encoding: str = "utf-8", *, api: str = "stream", max_line_bytes: int = DEFAULT_MAX_LINE_BYTES
    ) -> None:
        self._parts = parts
        self._encoding = encoding
        self._api = api
        self._max = max_line_bytes

    def _lines(self, parts: list[Part]) -> list[str]:
        out: list[str] = []
        for part in parts:
            # Split the raw bytes on LF (like LinesDecoder), never on Unicode separators such as U+2028 / U+0085,
            # and enforce the limit on bytes, before decoding.
            for raw in part.body.split(b"\n"):
                raw = raw.removesuffix(b"\r")
                if len(raw) > self._max:
                    raise ResponseFormatError(self._api, "stream", f"a line exceeds {self._max} bytes")
                line = raw.decode(self._encoding, errors="replace")
                if line.strip():
                    out.append(line)
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


def decoder_for(
    codec: object, response: Response, *, api: str = "stream", max_line_bytes: int = DEFAULT_MAX_LINE_BYTES
) -> StreamDecoder[object]:
    """Decoder for a streamed answer, chosen by a ``Stream`` reply codec (``decoder`` and ``encoding`` attributes).

    Anything without a ``decoder`` attribute gets the raw bytes.
    """
    kind = getattr(codec, "decoder", "bytes")
    if kind == "mjpeg":
        return mjpeg_decoder(response, api=api)
    if kind == "lines":
        encoding = getattr(codec, "encoding", "utf-8")
        content_type = response.headers.get("content-type", "")
        if content_type.split(";", 1)[0].strip().lower().startswith("multipart/"):
            # chosen by media type: a missing or empty boundary is then rejected, not read as plain lines
            return MultipartLinesDecoder(
                MixedReplaceDecoder.for_response(response, api=api), encoding, api=api, max_line_bytes=max_line_bytes
            )
        return LinesDecoder(encoding, api=api, max_line_bytes=max_line_bytes)
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

