"""Review round 9 (HTTP/driver): hook records on every failure, off-loop upload reads, charsets, secret names."""

from __future__ import annotations

import asyncio
import io
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from ax_devil_device_api._http.debug import is_secret_name, serialize
from ax_devil_device_api._http.types import FilePart, Headers, MultipartBody, RawBody, Request, Response
from ax_devil_device_api._http.upload import Upload, deferred_upload, file_part
from ax_devil_device_api._protocols.base import BytesDecoder, CallFlow
from ax_devil_device_api._runtime.driver import Call, run_async, run_sync
from ax_devil_device_api.errors import AuthError, ResponseFormatError

# --- #7: one on_response record per attempt, whatever the failure ------------------------------------------------


class Failing:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def send(self, request: Request) -> Response:
        raise self.error

    @contextmanager
    def open_stream(self, request: Request) -> Iterator[Any]:
        raise self.error
        yield  # pragma: no cover


class AFailing:
    def __init__(self, error: Exception) -> None:
        self.error = error

    async def send(self, request: Request) -> Response:
        raise self.error

    def open_stream(self, request: Request) -> Any:
        error = self.error

        class _Ctx:
            async def __aenter__(self) -> Any:
                raise error

            async def __aexit__(self, *exc: object) -> None:
                return None

        return _Ctx()


def one_request() -> CallFlow[bytes]:
    response = yield Request("GET", "/x")
    return response.content


def one_stream() -> CallFlow[BytesDecoder]:
    yield Request("GET", "/x", stream=True)
    return BytesDecoder()


@pytest.mark.parametrize("flow", [one_request, one_stream])
def test_auth_error_emits_one_response_record_sync(flow: Any) -> None:
    records: list[dict[str, Any]] = []
    call = Call(label=("api", "op"), on_response=records.append)
    with pytest.raises(AuthError):
        run_sync(Failing(AuthError("nope")), flow(), call)  # type: ignore[arg-type]
    assert [(r["status"], r["error"], r["attempt"]) for r in records] == [(None, "AuthError", 1)]


@pytest.mark.anyio
@pytest.mark.parametrize("flow", [one_request, one_stream])
async def test_auth_error_emits_one_response_record_async(flow: Any) -> None:
    records: list[dict[str, Any]] = []
    call = Call(label=("api", "op"), on_response=records.append)
    with pytest.raises(AuthError):
        await run_async(AFailing(AuthError("nope")), flow(), call)  # type: ignore[arg-type]
    assert [(r["status"], r["error"], r["attempt"]) for r in records] == [(None, "AuthError", 1)]


# --- #9: no blocking upload read on the event loop ---------------------------------------------------------------


class ThreadRecordingStream(io.BytesIO):
    def __init__(self, data: bytes) -> None:
        super().__init__(data)
        self.threads: set[int] = set()

    def read(self, size: int | None = -1) -> bytes:
        self.threads.add(threading.get_ident())
        return super().read(size)


class Recorder:
    def __init__(self) -> None:
        self.requests: list[Request] = []

    async def send(self, request: Request) -> Response:
        self.requests.append(request)
        return Response(200, Headers(()), b"", request)

    def open_stream(self, request: Request) -> Any:
        raise NotImplementedError


class SyncRecorder:
    def __init__(self) -> None:
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        return Response(200, Headers(()), b"", request)

    def open_stream(self, request: Request) -> Any:
        raise NotImplementedError


def multipart_flow(part: FilePart) -> CallFlow[None]:
    yield Request("POST", "/up", body=MultipartBody((), (part,)))


def raw_flow(upload: Upload) -> CallFlow[None]:
    content, _, _ = deferred_upload(upload, filename=None, content_type=None)
    yield Request("POST", "/up", body=RawBody(content, "application/octet-stream"))


def test_building_a_request_reads_nothing() -> None:
    stream = ThreadRecordingStream(b"abc")
    file_part("f", Upload(stream, 3))
    assert stream.threads == set() and stream.tell() == 0


@pytest.mark.anyio
async def test_small_async_upload_stream_is_read_off_the_event_loop() -> None:
    stream = ThreadRecordingStream(b"abcdef")
    transport = Recorder()
    await run_async(transport, multipart_flow(file_part("f", Upload(stream, 6))), Call())
    assert stream.threads and threading.get_ident() not in stream.threads
    body = transport.requests[0].body
    assert isinstance(body, MultipartBody) and body.files[0].content == b"abcdef" and body.replayable


@pytest.mark.anyio
async def test_small_async_upload_path_and_raw_body_are_read_off_the_event_loop(tmp_path: Path) -> None:
    (tmp_path / "f.bin").write_bytes(b"xyz")
    transport = Recorder()
    await run_async(transport, multipart_flow(file_part("f", tmp_path / "f.bin")), Call())
    stream = ThreadRecordingStream(b"12345")
    await run_async(transport, raw_flow(Upload(stream, 5)), Call())
    assert stream.threads and threading.get_ident() not in stream.threads
    raw = transport.requests[1].body
    assert isinstance(raw, RawBody) and raw.content == b"12345" and raw.size == 5
    first = transport.requests[0].body
    assert isinstance(first, MultipartBody) and first.files[0].content == b"xyz"


def test_small_sync_upload_is_resolved_before_sending(tmp_path: Path) -> None:
    path = tmp_path / "f.bin"
    path.write_bytes(b"abc")
    transport = SyncRecorder()
    run_sync(transport, multipart_flow(file_part("f", path)), Call())
    assert transport.requests[0].replayable


@pytest.mark.anyio
async def test_async_upload_read_error_surfaces_from_the_call(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        await run_async(Recorder(), multipart_flow(file_part("f", tmp_path / "missing")), Call())
    await asyncio.sleep(0)


# --- #10: unknown charset ----------------------------------------------------------------------------------------


def _response(content_type: str, content: bytes = b"hi") -> Response:
    return Response(200, Headers([("Content-Type", content_type)]), content, Request("GET", "/x"))


def test_unknown_charset_is_a_response_format_error() -> None:
    with pytest.raises(ResponseFormatError, match="charset"):
        _response("text/plain; charset=nonsense-9").text


def test_non_text_codec_is_a_response_format_error() -> None:
    with pytest.raises(ResponseFormatError):
        _response("text/plain; charset=rot13").text


def test_excerpt_never_raises_on_an_unknown_charset() -> None:
    assert _response("text/plain; charset=nonsense-9", b"hello").excerpt() == "hello"


def test_known_charset_still_decodes() -> None:
    assert _response("text/plain; charset=latin-1", "é".encode("latin-1")).text == "é"


# --- #15: SIM PIN/PUK and related secret names -------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    ["pin", "puk", "oldPin", "newPin", "oldpin", "newpuk", "SimPIN", "sim_pin", "pin-code", "verifySimPin", "PUK",
     "passphrase", "wpaPassphrase", "psk", "preSharedKey", "community", "snmp_community", "apiKey", "api_key",
     "apikey", "AuthenticationKey", "Port.I0.AuthenticationKey", "authentication_key", "secret", "clientSecret", "token", "refreshToken"],
)
def test_secret_names(name: str) -> None:
    assert is_secret_name(name)
    assert serialize({name: "1234"}) == {name: "<redacted>"}


@pytest.mark.parametrize(
    "name",
    ["spinning", "pinned", "mapping", "pinch", "opinion", "ping", "timestamp", "keyboard", "Pingable", "ShippingCode",
     "stoppingDistance"],
)
def test_names_that_merely_contain_pin_are_not_secrets(name: str) -> None:
    assert not is_secret_name(name)


# --- dot segments in user-supplied URL paths -----------------------------------------------------------------------


@pytest.mark.parametrize(
    "base_path",
    ["/vms/camera/../admin", "/a/./b", "/..", "/a/%2e%2e/b", "/a/%2E%2e", "/a/%252e%252e/b", "/a//b", "/a\\..\\b", "/a/..%2f",
     "/vms/%2f/cam", "/vms/%252f/cam", "/vms/%5c/cam", "/vms/%255c/cam", "/vms/%2F%2fcam", "/vms%2f", "/vms/cam%2f",
     "/a/%25252e%25252e/b", "/a/%2525252e"],
)
def test_base_path_rejects_dot_and_empty_segments(base_path: str) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api.errors import ConfigurationError

    with pytest.raises(ConfigurationError):
        ConnectionConfig("cam", base_path=base_path)


@pytest.mark.parametrize("base_path", ["", "/vms/camera-1", "/a.b/c..d", "/v1.2/x"])
def test_ordinary_base_paths_are_kept(base_path: str) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig

    assert ConnectionConfig("cam", base_path=base_path).base_path == base_path


@pytest.mark.parametrize("path", ["/a/../b", "/a/%2e%2e/b", "/a/./b", "/a/%5c/b", "/a/%255c/b", "/a/%252e%252e/b"])
def test_request_and_rtsp_paths_reject_dot_segments(path: str) -> None:
    from ax_devil_device_api.errors import ConfigurationError
    from ax_devil_device_api.rtsp import build_rtsp_url

    with pytest.raises(ValueError):
        Request("GET", path)
    with pytest.raises(ConfigurationError):
        build_rtsp_url("cam", path=path)
