from unittest.mock import Mock

import pytest

from src.ax_devil_device_api.features.device_debug import DeviceDebugClient
from src.ax_devil_device_api.utils.errors import FeatureError


def make_response(
    *,
    content: bytes = b"PK\x03\x04report",
    status_code: int = 200,
    content_type: str | None = None,
    text: str = "ok",
) -> Mock:
    """Build a deterministic diagnostic response for unit tests."""
    result = Mock(status_code=status_code, content=content, text=text)
    result.headers = {} if content_type is None else {"Content-Type": content_type}
    return result


def test_download_server_report_preserves_compatibility_default():
    """The Python API keeps its image-inclusive compatibility default."""
    transport = Mock()
    transport.request.return_value = make_response(content_type="application/zip")

    result = DeviceDebugClient(transport).download_server_report()

    assert result.startswith(b"PK")
    args, request = transport.request.call_args
    endpoint = args[0]
    assert endpoint.path == "/axis-cgi/serverreport.cgi"
    assert request["params"] == {"mode": "zip_with_image"}
    assert request["headers"] == {
        "Content-Type": None,
        "Accept-Encoding": "identity",
    }


def test_download_server_report_accepts_portable_zip_mode():
    """The portable ZIP mode remains available explicitly."""
    transport = Mock()
    transport.request.return_value = make_response(content_type="application/zip")

    DeviceDebugClient(transport).download_server_report(mode="zip")

    assert transport.request.call_args.kwargs["params"] == {"mode": "zip"}


@pytest.mark.parametrize("mode", ["tar", "", None, True])
def test_download_server_report_rejects_unsupported_modes(mode):
    """Only the two documented server report archive modes are accepted."""
    with pytest.raises(FeatureError, match="zip"):
        DeviceDebugClient(Mock()).download_server_report(mode=mode)


def test_download_crash_report_accepts_gzip_signature():
    """Crash reports accept gzip bytes without requiring a response media type."""
    transport = Mock()
    payload = b"\x1f\x8b\x08crash"
    transport.request.return_value = make_response(content=payload)

    assert DeviceDebugClient(transport).download_crash_report() == payload


def test_download_network_trace_accepts_classic_pcap_signature():
    """Network traces accept classic PCAP bytes without a strict media type."""
    transport = Mock()
    payload = b"\xd4\xc3\xb2\xa1pcap"
    transport.request.return_value = make_response(content=payload)

    assert DeviceDebugClient(transport).download_network_trace() == payload


@pytest.mark.parametrize(
    ("method", "content_type", "content"),
    [
        ("download_server_report", "application/zip", b""),
        ("download_server_report", "application/zip", b"not a zip"),
        ("download_server_report", "application/octet-stream", b"PK\x03\x04data"),
        ("download_crash_report", None, b""),
        ("download_crash_report", None, b"not gzip"),
        ("download_network_trace", None, b""),
        ("download_network_trace", None, b"not pcap"),
    ],
)
def test_downloads_reject_empty_or_invalid_payloads(method, content_type, content):
    """Successful HTTP responses still need the expected binary signature."""
    transport = Mock()
    transport.request.return_value = make_response(
        content=content, content_type=content_type
    )

    with pytest.raises(FeatureError):
        getattr(DeviceDebugClient(transport), method)()


@pytest.mark.parametrize("status_code", [400, 404, 500])
@pytest.mark.parametrize(
    "method",
    ["download_server_report", "download_crash_report", "download_network_trace"],
)
def test_downloads_preserve_operation_specific_http_errors(method, status_code):
    """HTTP failures retain each diagnostics operation's existing error code."""
    transport = Mock()
    transport.request.return_value = make_response(status_code=status_code)

    with pytest.raises(FeatureError) as error:
        getattr(DeviceDebugClient(transport), method)()

    expected_code = (
        "network_trace_error"
        if method == "download_network_trace"
        else f"{method}_error"
    )
    assert error.value.code == expected_code


def test_download_network_trace_uses_documented_parameters_and_timeout():
    """Network capture includes pcapdump, duration, interface, and capture time."""
    transport = Mock()
    transport.request.return_value = make_response(content=b"\x0a\x0d\x0d\x0apcap")

    DeviceDebugClient(transport).download_network_trace(duration=12, interface="eth0")

    args, request = transport.request.call_args
    endpoint = args[0]
    assert endpoint.path == "/axis-cgi/debug/debug.tgz?cmd=pcapdump"
    assert request["params"] == {"duration": 12, "interface": "eth0"}
    assert request["timeout"] == DeviceDebugClient.DOWNLOAD_TIMEOUT + 12
    assert request["headers"] == {
        "Content-Type": None,
        "Accept-Encoding": "identity",
    }


@pytest.mark.parametrize("duration", [0, -1, True, 1.5, "1"])
def test_download_network_trace_requires_positive_integer_duration(duration):
    """Capture duration rejects zero, negative, bool, and non-integer values."""
    with pytest.raises(FeatureError, match="positive integer"):
        DeviceDebugClient(Mock()).download_network_trace(duration=duration)


@pytest.mark.parametrize("interface", ["", "   ", 1, True, [], {}])
def test_download_network_trace_requires_nonempty_string_interface(interface):
    """An explicitly supplied network interface must be a nonempty string."""
    with pytest.raises(FeatureError, match="nonempty string"):
        DeviceDebugClient(Mock()).download_network_trace(interface=interface)


def test_download_crash_report_preserves_requests_decoded_content():
    """Crash downloads request identity encoding to preserve gzip artifact bytes."""
    transport = Mock()
    payload = b"\x1f\x8b\x08crash"
    response = make_response(content=payload)
    response.headers["Content-Encoding"] = "gzip"
    transport.request.return_value = response

    assert DeviceDebugClient(transport).download_crash_report() == payload
    assert transport.request.call_args.kwargs["headers"] == {
        "Content-Type": None,
        "Accept-Encoding": "identity",
    }


def test_ping_test_returns_raw_text_without_json_accept_header():
    """Ping output is returned unchanged and is not advertised as JSON."""
    transport = Mock()
    transport.request.return_value = make_response(
        content=b"ignored", text="raw ping\n"
    )

    assert DeviceDebugClient(transport).ping_test(" example.com ") == "raw ping\n"
    assert transport.request.call_args.kwargs["headers"] == {"Accept": None}


@pytest.mark.parametrize("target", ["", "   ", None, 123])
def test_ping_test_requires_nonempty_string_target(target):
    """Ping targets must be nonempty strings."""
    with pytest.raises(FeatureError):
        DeviceDebugClient(Mock()).ping_test(target)


@pytest.mark.parametrize("port", [0, -1, 65536, True, False, 80.0, "80"])
def test_port_open_test_requires_valid_tcp_port(port):
    """TCP port validation excludes bool and values outside the valid range."""
    with pytest.raises(FeatureError, match="between 1 and 65535"):
        DeviceDebugClient(Mock()).port_open_test("example.com", port)


def test_port_open_test_returns_raw_text():
    """TCP test output is returned as raw text."""
    transport = Mock()
    transport.request.return_value = make_response(content=b"ignored", text="open\n")

    assert DeviceDebugClient(transport).port_open_test("example.com", 443) == "open\n"
    assert transport.request.call_args.kwargs["headers"] == {"Accept": None}


@pytest.mark.parametrize("target", ["", "   ", None, 123])
def test_port_open_test_requires_nonempty_string_address(target):
    """TCP targets must be nonempty strings."""
    with pytest.raises(FeatureError):
        DeviceDebugClient(Mock()).port_open_test(target, 443)


@pytest.mark.integration
@pytest.mark.slow
def test_download_server_report(client):
    """Test downloading the server report returns binary data."""
    result = client.device_debug.download_server_report()
    assert isinstance(result, bytes), "Expected binary data for server report"


@pytest.mark.integration
@pytest.mark.slow
def test_download_crash_report(client):
    """Test downloading the crash report returns binary data."""
    result = client.device_debug.download_crash_report()
    assert isinstance(result, bytes), "Expected binary data for crash report"


@pytest.mark.integration
@pytest.mark.slow
def test_download_network_trace(client):
    """Test downloading network trace returns binary data."""
    # Test with default parameters
    result = client.device_debug.download_network_trace()
    assert isinstance(result, bytes), "Expected binary data for network trace"


@pytest.mark.integration
def test_ping_test_valid(client):
    """Test ping test with a valid target returns text."""
    result = client.device_debug.ping_test("8.8.8.8")
    assert isinstance(result, str), "Expected text data for ping test"


@pytest.mark.unit
def test_ping_test_invalid(client):
    """Test ping test with empty target returns error."""
    with pytest.raises(FeatureError):
        client.device_debug.ping_test("")


@pytest.mark.integration
def test_port_open_test_valid(client):
    """Test port open test with valid inputs returns text."""
    result = client.device_debug.port_open_test("8.8.8.8", 53)
    assert isinstance(result, str), "Expected text data for port open test"


@pytest.mark.unit
def test_port_open_test_invalid(client):
    """Test port open test with invalid inputs returns error."""
    with pytest.raises(FeatureError):
        client.device_debug.port_open_test("", 53)
