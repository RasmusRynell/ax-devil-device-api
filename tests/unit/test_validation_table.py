"""Every public numeric input rejects bool, float (for counts), inf, nan, negatives and (where invalid) zero."""

from __future__ import annotations

import io
from collections.abc import Callable
from typing import Any

import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.options import Heartbeat, RequestOptions, RetryPolicy
from ax_devil_device_api._http.types import FilePart, MultipartBody
from ax_devil_device_api._http.upload import Upload
from ax_devil_device_api.errors import ConfigurationError
from ax_devil_device_api.rtsp import MediaStream, RtspUrl, build_rtsp_url

NAN, INF = float("nan"), float("inf")

# name -> (constructor taking the value, kind, zero_is_valid)
INPUTS: dict[str, tuple[Callable[[Any], Any], str, bool]] = {
    "ConnectionConfig.timeout": (lambda v: ConnectionConfig("cam", timeout=v), "number", False),
    "ConnectionConfig.max_concurrency": (lambda v: ConnectionConfig("cam", max_concurrency=v), "int", False),
    "ConnectionConfig.max_streams": (lambda v: ConnectionConfig("cam", max_streams=v), "int", False),
    "ConnectionConfig.port": (lambda v: ConnectionConfig("cam", port=v), "int", False),
    "RequestOptions.timeout": (lambda v: RequestOptions(timeout=v), "number", False),
    "RetryPolicy.attempts": (lambda v: RetryPolicy(attempts=v), "int", False),
    "RetryPolicy.backoff": (lambda v: RetryPolicy(backoff=v), "number", True),
    "RetryPolicy.max_backoff": (lambda v: RetryPolicy(max_backoff=v), "number", True),
    "Heartbeat.interval": (lambda v: Heartbeat(interval=v), "number", False),
    "Heartbeat.timeout": (lambda v: Heartbeat(timeout=v), "number", False),
    "Upload.size": (lambda v: Upload(io.BytesIO(b""), v), "int", True),
    "RtspUrl.port": (lambda v: RtspUrl("cam", port=v), "int", False),
    "build_rtsp_url.port": (lambda v: build_rtsp_url("cam", port=v), "int", False),
    "MediaStream.camera": (lambda v: MediaStream(camera=v), "int", False),
    "MediaStream.fps": (lambda v: MediaStream(fps=v), "int", True),
    "MediaStream.compression": (lambda v: MediaStream(compression=v), "int", True),
}

COMMON_BAD = [True, False, NAN, INF, -INF, -1, "2"]
INT_ONLY_BAD = [1.5, 2.0]


def _cases() -> list[Any]:
    cases = []
    for name, (build, kind, zero_ok) in INPUTS.items():
        bad = list(COMMON_BAD) + (INT_ONLY_BAD if kind == "int" else []) + ([] if zero_ok else [0])
        for value in bad:
            cases.append(pytest.param(build, value, id=f"{name}={value!r}"))
    return cases


@pytest.mark.parametrize(("build", "value"), _cases())
def test_invalid_numeric_input_is_rejected(build: Callable[[Any], Any], value: Any) -> None:
    with pytest.raises(ConfigurationError):
        build(value)


@pytest.mark.parametrize("name", sorted(INPUTS))
def test_valid_numeric_input_is_accepted(name: str) -> None:
    build, _, zero_ok = INPUTS[name]
    assert build(1) is not None
    if zero_ok:
        assert build(0) is not None


def test_documented_upper_bounds() -> None:
    for build in (INPUTS["ConnectionConfig.port"][0], INPUTS["RtspUrl.port"][0]):
        assert build(65535) is not None
        with pytest.raises(ConfigurationError):
            build(65536)
    assert MediaStream(compression=100) and MediaStream(camera="quad")
    with pytest.raises(ConfigurationError):
        MediaStream(compression=101)


@pytest.mark.parametrize(
    "argv",
    [
        ["--port", "0", "apis"],
        ["--port", "70000", "apis"],
        ["--port", "1.5", "apis"],
        ["--timeout", "inf", "apis"],
        ["--timeout", "nan", "apis"],
        ["--timeout", "0", "apis"],
        ["call", "mqtt_client", "get_client_status", "--limit", "-1"],
    ],
)
def test_cli_numeric_flags_are_validated(argv: list[str]) -> None:
    import json

    from ax_devil_device_api.cli import main

    out, err = io.StringIO(), io.StringIO()
    code = main(argv, out=out, err=err)
    assert code == 2 and "Traceback" not in err.getvalue()
    assert json.loads(err.getvalue().splitlines()[-1])["error"]["type"] == "UsageError"


# --- boolean inputs accept only True/False --------------------------------------------------------------------------------


def _device(**kw: Any) -> Any:
    from ax_devil_device_api import Device

    return Device("cam", credentials=("u", "p"), **kw)


BOOL_INPUTS: dict[str, tuple[Callable[[Any], Any], bool]] = {
    # name -> (constructor, None is valid)
    "ConnectionConfig.allow_http": (lambda v: ConnectionConfig("cam", scheme="http", allow_http=v), False),
    "Device.allow_http": (lambda v: _device(scheme="http", allow_http=v), False),
    "RetryPolicy.retry_unsent": (lambda v: RetryPolicy(retry_unsent=v), False),
    "RetryPolicy.retry_reads": (lambda v: RetryPolicy(retry_reads=v), False),
    "Device.rtsp_url.include_credentials": (lambda v: _device().rtsp_url(include_credentials=v), False),
    "Device.connect_session.use_token": (lambda v: _device().connect_session(object(), use_token=v), False),  # type: ignore[arg-type]
    **{
        f"MediaStream.{flag}": ((lambda v, flag=flag: MediaStream(**{flag: v})), True)
        for flag in ("audio", "video", "mirror", "color", "squarepixel", "event", "pull")
    },
}


def _bool_cases() -> list[Any]:
    cases = []
    for name, (build, none_ok) in BOOL_INPUTS.items():
        for value in ["false", "true", 0, 1, 2.0, *([] if none_ok else [None])]:
            cases.append(pytest.param(build, value, id=f"{name}={value!r}"))
    return cases


@pytest.mark.parametrize(("build", "value"), _bool_cases())
def test_boolean_inputs_reject_truthy_and_falsy_non_booleans(build: Callable[[Any], Any], value: Any) -> None:
    with pytest.raises(ConfigurationError):
        build(value)


def test_plain_http_needs_a_real_true() -> None:
    assert ConnectionConfig("cam", scheme="http", allow_http=True).allow_http is True
    with pytest.raises(ConfigurationError):
        ConnectionConfig("cam", scheme="http", allow_http=False)


# --- CR/LF/NUL never reach a header ---------------------------------------------------------------------------------------

PAYLOADS = ["text/plain\r\nX-Injected: 1", "a\nb", "a\rb", "a\x00b"]


@pytest.mark.parametrize("payload", PAYLOADS)
def test_multipart_part_fields_reject_header_injection(payload: str) -> None:
    from ax_devil_device_api._http.multipart import encode_multipart

    with pytest.raises(ConfigurationError):
        FilePart("f", None, b"x", content_type=payload)
    with pytest.raises(ConfigurationError):
        FilePart("f", payload, b"x")
    with pytest.raises(ConfigurationError):
        FilePart(payload, "n.bin", b"x")
    with pytest.raises(ConfigurationError):
        encode_multipart(MultipartBody((("field" + payload, "v"),), ()))


@pytest.mark.parametrize("payload", PAYLOADS)
def test_upload_and_request_header_values_reject_header_injection(payload: str) -> None:
    from ax_devil_device_api._http.types import RawBody, Request

    with pytest.raises(ConfigurationError):
        Upload(io.BytesIO(b""), 0, content_type=payload)
    with pytest.raises(ConfigurationError):
        Upload(io.BytesIO(b""), 0, filename=payload)
    with pytest.raises(ConfigurationError):
        RawBody(b"x", payload)
    with pytest.raises(ConfigurationError):
        Request("GET", "/x", headers=(("X-Test", payload),))
    with pytest.raises(ConfigurationError):
        Request("GET", "/x", headers=((payload, "v"),))
    with pytest.raises(ConfigurationError):
        Request("GET", "/x", accept=payload)


def test_quotes_and_backslashes_in_names_are_still_escaped_not_rejected() -> None:
    from ax_devil_device_api._http.multipart import encode_multipart

    encoded = encode_multipart(MultipartBody((), (FilePart('a"b', 'c\\d"e.bin', b"x"),), boundary="B"))
    assert isinstance(encoded.content, bytes) and b'name="a%22b"' in encoded.content
    assert b'filename="c\\\\d%22e.bin"' in encoded.content


# --- every MediaStream field is checked ------------------------------------------------------------------------------------

MEDIA_BAD: dict[str, list[Any]] = {
    "rotation": [True, 90.0, float("nan"), 45, "90", -90, 360],
    "videocodec": [False, 1, "", b"h264"],
    "streamprofile": [0, ""],
    "recordingid": [0, ""],
    "palette": [True, ""],
    "eventtopic": [1, ""],
    "eventcontent": [1, ""],
    "resolution": [1280, True, "1280*720", ""],
    "overlays": [True, 1, "everything"],
    "ptz": [True, "pan"],
    "analytics": [0, "circle"],
    "ptz_pantilt_coordinate_space": [1, "radians"],
    "ptz_zoom_coordinate_space": [1, "degrees"],
    "camera": [True, 1.5, "2", "Quad", 0],
    "extra": ["a=b", (("a", 1),), (("a",),), [("a", "b")]],
}


@pytest.mark.parametrize(
    ("field", "value"), [pytest.param(f, v, id=f"{f}={v!r}") for f, values in MEDIA_BAD.items() for v in values]
)
def test_media_stream_rejects_invalid_field_values(field: str, value: Any) -> None:
    with pytest.raises(ConfigurationError):
        MediaStream(**{field: value})


def test_media_stream_accepts_documented_values() -> None:
    stream = MediaStream(
        videocodec="h264", rotation=90, overlays="all-sync", ptz="position", analytics="box", camera="quad",
        resolution="1280x720", extra=(("x", "y"),), audio=False,
    )
    assert ("rotation", "90") in stream.query() and ("audio", "0") in stream.query()
    assert MediaStream(rotation=0).query() == (("rotation", "0"),)


# --- resolution, credentials and host strictness ---------------------------------------------------------------------------


@pytest.mark.parametrize("resolution", ["640x480\n", "٦٤٠x٤٨٠", "640x480 ", "640X480", "x480", "640x"])
def test_media_stream_resolution_is_strict(resolution: str) -> None:
    with pytest.raises(ConfigurationError):
        MediaStream(resolution=resolution)
    assert MediaStream(resolution="640x480").resolution == "640x480"


@pytest.mark.parametrize("credentials", ["root:pass", ("root", "pass"), 5, {"user": "u"}, object()])
def test_connection_config_credentials_must_be_credentials_or_a_token(credentials: Any) -> None:
    with pytest.raises(ConfigurationError, match="credentials"):
        ConnectionConfig("cam", credentials=credentials)


def test_connection_config_accepts_credentials_token_and_none() -> None:
    from ax_devil_device_api._http.config import BearerToken, Credentials

    ConnectionConfig("cam")
    ConnectionConfig("cam", credentials=Credentials("u", "p"))
    ConnectionConfig("cam", credentials=BearerToken("t"))


@pytest.mark.parametrize(
    "host",
    ["cam\n", "cam\tx", "ca m", "cam\r\nHost: evil", "cam\x00", "cam\x7f", "cam\x85", "cam ", "cam​", "ca\\m", "bad\ud800host"],
)
def test_hosts_reject_whitespace_and_control_characters(host: str) -> None:
    with pytest.raises(ConfigurationError):
        ConnectionConfig(host)
    with pytest.raises(ConfigurationError):
        RtspUrl(host)


def test_hosts_allow_idna_names_and_reject_non_encodable_ones() -> None:
    assert ConnectionConfig("bücher.example").host == "bücher.example"
    with pytest.raises(ConfigurationError):
        ConnectionConfig("a" * 70 + ".exämple")  # label too long for IDNA


@pytest.mark.parametrize("proxy", ["http://proxy.local\n:8080", "http://prox y.local", "http://proxy.local\t", "http://pro\x00xy"])
def test_proxy_rejects_whitespace_and_control_characters(proxy: str) -> None:
    with pytest.raises(ConfigurationError):
        ConnectionConfig("cam", proxy=proxy)


def test_missing_password_credentials_give_a_library_error_not_an_assert() -> None:
    import httpx

    from ax_devil_device_api._http.auth import AxisAuth
    from ax_devil_device_api._http.config import BearerToken
    from ax_devil_device_api.errors import AuthError

    flow = AxisAuth(BearerToken("t")).for_request("required", True)
    request = httpx.Request("GET", "https://cam/x")
    state = type("S", (), {"header": lambda *a: "x"})()
    with pytest.raises(AuthError):
        flow._sign(state, request)  # type: ignore[attr-defined]


# --- credentials must be strings (an unset environment variable is None) -----------------------------------------------------

BAD_TEXT = [None, 5, b"secret", 1.5, True]


def _creds(username: Any, password: Any) -> Any:
    from ax_devil_device_api._http.config import Credentials

    return Credentials(username, password)


def _bearer(token: Any) -> Any:
    from ax_devil_device_api._http.config import BearerToken

    return BearerToken(token)


CREDENTIAL_BUILDERS: dict[str, Callable[[Any], Any]] = {
    "Credentials.username": lambda v: _creds(v, "pw"),
    "Credentials.password": lambda v: _creds("root", v),
    "BearerToken.token": _bearer,
    "Device tuple username": lambda v: _device_with((v, "pw")),
    "Device tuple password": lambda v: _device_with(("root", v)),
    "build_rtsp_url tuple password": lambda v: build_rtsp_url("cam", credentials=("root", v)),
}


def _device_with(pair: Any) -> Any:
    from ax_devil_device_api import Device

    return Device("cam", credentials=pair)


@pytest.mark.parametrize(
    ("build", "value"),
    [pytest.param(b, v, id=f"{n}={v!r}") for n, b in CREDENTIAL_BUILDERS.items() for v in BAD_TEXT],
)
def test_credentials_reject_non_string_values(build: Callable[[Any], Any], value: Any) -> None:
    with pytest.raises(ConfigurationError):
        build(value)


@pytest.mark.parametrize("pair", [("root",), ("a", "b", "c"), "root:pw", ["root", "pw"]])
def test_credentials_tuple_form_needs_exactly_a_pair(pair: Any) -> None:
    with pytest.raises(ConfigurationError):
        _device_with(pair)


def test_empty_password_is_allowed_but_an_empty_username_is_not() -> None:
    assert _creds("root", "").password == ""
    with pytest.raises(ConfigurationError):
        _creds("", "pw")
    assert _device_with(("root", "pw")).config.credentials.username == "root"  # type: ignore[union-attr]


def test_a_bearer_token_callable_must_return_a_string() -> None:
    assert _bearer(lambda: "t").current() == "t"
    with pytest.raises(ConfigurationError):
        _bearer(lambda: None).current()


@pytest.mark.parametrize("retry", [{}, False, 0, "default", RetryPolicy, (2,), 3])
def test_retry_must_be_a_retry_policy_or_none(retry: Any) -> None:
    with pytest.raises(ConfigurationError, match="RetryPolicy"):
        ConnectionConfig("cam", retry=retry)
    with pytest.raises(ConfigurationError, match="RetryPolicy"):
        RequestOptions(retry=retry)


def test_none_retry_keeps_the_default_policy() -> None:
    assert ConnectionConfig("cam", retry=None).retry == RetryPolicy()  # type: ignore[arg-type]
    assert RequestOptions(retry=None).retry is None
    custom = RetryPolicy(attempts=3)
    assert ConnectionConfig("cam", retry=custom).retry is custom and RequestOptions(retry=custom).retry is custom


# --- scoped IPv6 hosts: the zone id's '%' is encoded as '%25' in every URL ------------------------------------------------------


@pytest.mark.parametrize("host", ["fe80::1%eth0", "[fe80::1%eth0]"])
def test_scoped_ipv6_host_is_encoded_in_every_url_builder(host: str) -> None:
    from ax_devil_device_api._http.config import url_host
    from ax_devil_device_api._http.transport import SyncTransport

    assert url_host(host) == "[fe80::1%25eth0]"
    assert ConnectionConfig(host).base_url == "https://[fe80::1%25eth0]"
    assert build_rtsp_url(host).safe.startswith("rtsp://[fe80::1%25eth0]:554/")
    assert str(RtspUrl(host, username="u", password="p")).startswith("rtsp://u:p@[fe80::1%25eth0]:554/")
    assert MediaStream().url(host).safe.startswith("rtsp://[fe80::1%25eth0]:554/")
    transport = SyncTransport(ConnectionConfig(host))
    assert str(transport._client.base_url).startswith("https://[fe80::1%25eth0]")  # the client URL the WS handshake uses too
    transport.close()


def test_plain_hosts_are_not_touched() -> None:
    from ax_devil_device_api._http.config import url_host

    assert url_host("cam.local") == "cam.local" and url_host("2001:db8::1") == "[2001:db8::1]"
    assert build_rtsp_url("2001:db8::1").safe.startswith("rtsp://[2001:db8::1]:554/")


# --- RTSP paths: valid percent escapes survive, stray percent signs are data, a raw '#' is refused -----------------------------


def test_an_escaped_hash_round_trips_exactly() -> None:
    url = RtspUrl("cam", path="/archive%23today")
    assert url.safe == "rtsp://cam:554/archive%23today"
    assert str(url) == "rtsp://cam:554/archive%23today"


@pytest.mark.parametrize(
    ("path", "shown"),
    [
        ("/a%zz", "/a%25zz"),
        ("/100%", "/100%25"),
        ("/a%2", "/a%252"),
        ("/a%20b", "/a%20b"),
        ("/a b", "/a%20b"),
        ("/a%41%2f", "/a%41%2f"),
    ],
)
def test_stray_percent_signs_are_encoded_and_valid_escapes_kept(path: str, shown: str) -> None:
    assert RtspUrl("cam", path=path).safe == f"rtsp://cam:554{shown}"


def test_a_raw_hash_is_still_refused() -> None:
    with pytest.raises(ConfigurationError, match="%23"):
        RtspUrl("cam", path="/archive#today")
