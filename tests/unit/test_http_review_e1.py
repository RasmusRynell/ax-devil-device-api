"""Review round 9 (HTTP/driver): hook records on every failure, off-loop upload reads, charsets, secret names."""

from __future__ import annotations

import asyncio
import io
import json
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


@pytest.mark.parametrize("value", [0, -1, 0.0, -0.5, float("inf"), float("nan")])
def test_request_options_reject_non_positive_or_non_finite_timeouts(value: float) -> None:
    from ax_devil_device_api._http.options import RequestOptions

    with pytest.raises(ValueError, match="None"):
        RequestOptions(timeout=value)


def test_request_options_accept_none_and_positive_timeouts() -> None:
    from ax_devil_device_api._http.options import RequestOptions

    assert RequestOptions().timeout is None and RequestOptions(timeout=0.5).timeout == 0.5


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_connection_timeout_and_heartbeat_reject_non_finite_values(value: float) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api._http.options import Heartbeat
    from ax_devil_device_api.errors import ConfigurationError

    with pytest.raises(ConfigurationError):
        ConnectionConfig("cam", timeout=value)
    with pytest.raises(ValueError):
        Heartbeat(timeout=value)
    with pytest.raises(ValueError):
        Heartbeat(interval=value)


# --- NaN / infinity in request payloads ----------------------------------------------------------------------------


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_floats_are_rejected_before_a_json_rpc_request_is_sent(value: float) -> None:
    from pydantic import ValidationError

    from ax_devil_device_api.apis.axis_audio_manager_edge import OffsetVolumeRequest
    from ax_devil_device_api.testing import MockCamera

    camera = MockCamera()
    with camera.device() as dev:
        with pytest.raises(ValidationError, match="NaN"):
            dev.apis.axis_audio_manager_edge.offset_volume("vc1", volume_offset=value)
    with pytest.raises(ValidationError):
        OffsetVolumeRequest(volume_controller_id="vc1", volume_offset=value)


def test_finite_floats_still_validate() -> None:
    from ax_devil_device_api.apis.axis_audio_manager_edge import OffsetVolumeRequest

    assert OffsetVolumeRequest(volume_controller_id="vc1", volume_offset=-2.5).volume_offset == -2.5


# --- a documented HTTP status wins over the generic 404 -> NotSupported mapping ---------------------------------------


def test_documented_404_is_an_api_error_not_not_supported() -> None:
    from ax_devil_device_api._protocols.base import http_error
    from ax_devil_device_api._protocols.cgi import _decode
    from ax_devil_device_api.apis import media_stream
    from ax_devil_device_api.errors import ApiError, NotSupported

    op = media_stream.OPS.get_media_stream
    request = Request("GET", "/axis-media/media.amp")
    response = Response(404, Headers(()), b"not here", request)
    error = http_error(op, response, documented=frozenset({404}))
    assert isinstance(error, ApiError) and error.kind == "not_found" and error.http_status == 404
    with pytest.raises(ApiError):
        _decode(op, response)
    # an operation that documents nothing for the status keeps the generic mapping
    undocumented = media_stream.OPS.get_media_stream
    assert isinstance(http_error(undocumented, Response(418, Headers(()), b"", request)), Exception)
    assert not isinstance(http_error(op, response, documented=frozenset({404})), NotSupported)


# --- a reused one-shot upload source never silently sends an empty body ---------------------------------------------


def _mock_ok() -> Any:
    import httpx

    seen: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.content)
        return httpx.Response(200)

    return httpx.MockTransport(handler), seen


def _upload_flow(upload: Upload) -> CallFlow[int]:
    response = yield Request("POST", "/up", body=MultipartBody((), (file_part("f", upload),)), timeout=0.05)
    return response.status


def test_sync_reused_upload_after_a_failing_hook_or_pool_timeout_sends_the_data() -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api._http.transport import SyncTransport
    from ax_devil_device_api.errors import PoolTimeout

    upload = Upload(io.BytesIO(b"PAYLOAD"), 7)
    mock, seen = _mock_ok()

    def boom(record: dict[str, Any]) -> None:
        raise RuntimeError("hook failed")

    with SyncTransport(ConnectionConfig("cam", on_request=boom, max_concurrency=1), transport=mock) as failing:
        with pytest.raises(RuntimeError):
            run_sync(failing, _upload_flow(upload), Call())
    with SyncTransport(ConnectionConfig("cam", max_concurrency=1), transport=mock) as busy:
        assert busy._slots.acquire()
        with pytest.raises(PoolTimeout):
            run_sync(busy, _upload_flow(upload), Call())
        busy._slots.release()
        assert run_sync(busy, _upload_flow(upload), Call()) == 200
    assert seen and b"PAYLOAD" in seen[-1]


@pytest.mark.anyio
async def test_async_reused_upload_after_a_failing_hook_or_pool_timeout_sends_the_data() -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api._http.transport import AsyncTransport
    from ax_devil_device_api.errors import PoolTimeout

    upload = Upload(io.BytesIO(b"PAYLOAD"), 7)
    mock, seen = _mock_ok()

    def boom(record: dict[str, Any]) -> None:
        raise RuntimeError("hook failed")

    async with AsyncTransport(ConnectionConfig("cam", on_request=boom), transport=mock) as failing:
        with pytest.raises(RuntimeError):
            await run_async(failing, _upload_flow(upload), Call())
    async with AsyncTransport(ConnectionConfig("cam", max_concurrency=1), transport=mock) as busy:
        slots, _ = busy._semaphores()
        await slots.acquire()
        with pytest.raises(PoolTimeout):
            await run_async(busy, _upload_flow(upload), Call())
        slots.release()
        assert await run_async(busy, _upload_flow(upload), Call()) == 200
    assert seen and b"PAYLOAD" in seen[-1]


def test_api_code_keyed_protocols_keep_the_generic_http_mapping() -> None:
    """Decoder code 403 means 'unsupported protocol' in the API, but an HTTP 403 is still access denied."""
    from ax_devil_device_api._protocols.jsonrpc import _decode
    from ax_devil_device_api.apis import decoder
    from ax_devil_device_api.errors import AccessDenied

    op = decoder.OPS.get_capabilities
    assert op.error_code(403) is not None  # the collision this guards against
    response = Response(403, Headers(()), b"forbidden", Request("POST", "/x"))
    with pytest.raises(AccessDenied):
        _decode(op, response)


def test_http_keyed_protocols_use_documented_statuses_except_401_and_403() -> None:
    from ax_devil_device_api._protocols.base import http_error
    from ax_devil_device_api._protocols.rest import _decode
    from ax_devil_device_api.apis import intercom_configuration
    from ax_devil_device_api.errors import AccessDenied, ApiError, AuthError

    op = intercom_configuration.OPS.update_configuration
    request = Request("PATCH", "/x")
    with pytest.raises(ApiError) as info:
        _decode(op, Response(400, Headers(()), b"bad", request))
    assert info.value.kind == "invalid_argument"
    assert isinstance(http_error(op, Response(403, Headers(()), b"", request), documented=True), AccessDenied)
    assert isinstance(http_error(op, Response(401, Headers(()), b"", request), documented=True), AuthError)


# --- error details never fail on an unknown charset ------------------------------------------------------------------


def test_documented_status_with_an_unknown_charset_keeps_its_kind() -> None:
    from ax_devil_device_api._protocols.base import http_error
    from ax_devil_device_api.apis import media_stream
    from ax_devil_device_api.errors import ApiError

    request = Request("GET", "/axis-media/media.amp")
    response = Response(404, Headers([("Content-Type", "text/plain; charset=nonsense-9")]), b"gone", request)
    error = http_error(media_stream.OPS.get_media_stream, response, documented=frozenset({404}))
    assert isinstance(error, ApiError) and error.kind == "not_found" and "gone" in str(error.details)
    assert response.safe_text == "gone"


# --- host must not carry a port ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("host", ["camera.local:8443", "10.0.0.5:80", "cam:", "[bad:host]", "::zz"])
def test_host_with_a_port_is_a_configuration_error(host: str) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api.errors import ConfigurationError

    with pytest.raises(ConfigurationError, match="port"):
        ConnectionConfig(host)


@pytest.mark.parametrize("host", ["2001:db8::1", "[2001:db8::1]", "::1", "fe80::1%eth0", "camera.local"])
def test_ipv6_literals_and_names_are_accepted(host: str) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig

    assert ConnectionConfig(host).host == host


def test_cli_reports_host_with_port_as_json_not_a_traceback() -> None:
    import io

    from ax_devil_device_api.cli import main

    out, err = io.StringIO(), io.StringIO()
    code = main(["--host", "camera.local:8443", "--user", "u", "--password", "p", "call", "mqtt_client", "get_client_status"], out=out, err=err)
    text = err.getvalue()
    assert code != 0 and "Traceback" not in text
    assert "port" in json.loads(text.splitlines()[-1])["error"]["message"]


def test_invalid_url_from_httpx_is_a_configuration_error() -> None:
    import httpx

    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api._http.transport import SyncTransport
    from ax_devil_device_api.errors import ConfigurationError

    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(lambda r: httpx.Response(200))) as t:
        with pytest.raises(ConfigurationError):
            t.send(Request("GET", "/ok\x00x"))


def test_cgi_http_503_is_unavailable_even_when_the_api_has_code_503() -> None:
    """Focus Recall's API code 503 ('Unknown index') arrives in a 200 envelope; an HTTP 503 is still unavailable."""
    from ax_devil_device_api._protocols.cgi import _decode
    from ax_devil_device_api.apis import focus_recall
    from ax_devil_device_api.errors import Unavailable

    op = focus_recall.OPS.add_memory_zone
    assert op.error_code(503) is not None
    with pytest.raises(Unavailable):
        _decode(op, Response(503, Headers(()), b"", Request("GET", "/axis-cgi/opticssetup.cgi")))
