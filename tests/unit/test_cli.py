"""CLI: generic call, listings and hand-written commands, against MockCamera."""

from __future__ import annotations

import io
import json

import pytest

from ax_devil_device_api import cli
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"


def run(monkeypatch: pytest.MonkeyPatch, camera: MockCamera | None, *argv: str) -> tuple[int, str, str]:
    if camera is not None:
        monkeypatch.setattr(cli, "make_device", lambda args: camera.device())
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(list(argv), out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def test_call_prints_json(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.jsonrpc(MQTT, "getClientStatus", data={"status": {"state": "active", "connectionStatus": "connected"}})
    code, out, _ = run(monkeypatch, cam, "call", "mqtt_client", "get_client_status")
    assert code == 0
    assert json.loads(out)["status"]["state"] == "active"


def test_call_parses_key_value_and_json_args(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.jsonrpc(MQTT, "configureClient")
    code, out, _ = run(
        monkeypatch, cam, "call", "mqtt_client", "configure_client",
        "client_id=cam-1", "--json", '{"server": {"host": "broker.example"}}',
    )
    assert code == 0 and json.loads(out) is None
    body = cam.calls("configureClient")[0].json
    assert body is not None
    params = body["params"]
    assert params["clientId"] == "cam-1" and params["server"]["host"] == "broker.example"


def test_call_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    code, _, err = run(monkeypatch, cam, "call", "nope", "x")
    assert code == 2 and "unknown API" in err
    code, _, err = run(monkeypatch, cam, "call", "mqtt_client", "nope")
    assert code == 2 and "unknown operation" in err
    code, _, err = run(monkeypatch, cam, "call", "mqtt_client", "configure_client", "bogus=1")
    assert code == 2 and "InvalidParameters" in err


def test_device_error_is_json_on_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.jsonrpc(MQTT, "getClientStatus", error=(2105, "denied"))
    code, _, err = run(monkeypatch, cam, "call", "mqtt_client", "get_client_status")
    assert code == 1
    assert json.loads(err)["error"]["code"] == 2105


def test_apis_and_ops_need_no_device(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out, _ = run(monkeypatch, None, "apis")
    assert code == 0 and "mqtt_client" in {a["name"] for a in json.loads(out)}
    code, out, _ = run(monkeypatch, None, "ops", "mqtt_client")
    assert code == 0 and "get_client_status" in {o["name"] for o in json.loads(out)}


def test_summary_and_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.identity(model="AXIS X", firmware="11.0.0")
    cam.api_list({"mqtt-client": "1.0"})
    code, out, _ = run(monkeypatch, cam, "summary")
    assert code == 0 and json.loads(out)["model"] == "AXIS X"
    code, out, _ = run(monkeypatch, cam, "supported")
    assert code == 0 and json.loads(out)["mqtt_client"]["status"] == "yes"


def test_missing_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AX_DEVIL_HOST", raising=False)
    code, _, err = run(monkeypatch, None, "summary")
    assert code == 2 and "no device" in err


def test_make_device_options(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CAM_USER", "root")
    monkeypatch.setenv("CAM_PASS", "pw")
    args = cli.build_parser().parse_args(["--host", "10.0.0.1", "--http", "-k", "--port", "8080", "summary"])
    dev = cli.make_device(args)
    assert dev.config.scheme == "http" and dev.config.verify is False and dev.config.port == 8080
    assert dev.config.credentials is not None


def test_snapshot_writes_file(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    cam = MockCamera()
    cam.cgi("/axis-cgi/jpg/image.cgi", text=b"\xff\xd8jpeg", content_type="image/jpeg")
    target = tmp_path / "s.jpg"
    code, out, _ = run(monkeypatch, cam, "snapshot", "-o", str(target), "--resolution", "320x240", "--camera", "2")
    assert code == 0 and out == ""
    assert target.read_bytes() == b"\xff\xd8jpeg"
    assert [r for r in cam.requests if r.path.endswith("image.cgi")][-1].query == {"resolution": "320x240", "camera": "2"}


def test_snapshot_stdout_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.cgi("/axis-cgi/jpg/image.cgi", text=b"\xff\xd8jpeg", content_type="image/jpeg")
    monkeypatch.setattr(cli, "make_device", lambda args: cam.device())
    raw = io.BytesIO()
    out = io.TextIOWrapper(raw, write_through=True)
    assert cli.main(["snapshot"], out=out, err=io.StringIO()) == 0
    assert raw.getvalue() == b"\xff\xd8jpeg"


def test_snapshot_invalid_option(monkeypatch: pytest.MonkeyPatch) -> None:
    code, _, err = run(monkeypatch, MockCamera(), "snapshot", "--compression", "500", "-o", "/dev/null")
    assert code == 2 and "InvalidParameters" in err


def test_argument_errors_are_json_on_injected_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    for argv in ([], ["--bogus"], ["call"], ["snapshot", "--color", "7"]):
        code, out, err = run(monkeypatch, None, *argv)
        assert code == 2 and out == ""
        assert json.loads(err)["error"]["type"] == "UsageError"


def test_snapshot_refuses_terminal_before_writing(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.cgi("/axis-cgi/jpg/image.cgi", text=b"\xff\xd8jpeg", content_type="image/jpeg")
    monkeypatch.setattr(cli, "make_device", lambda args: cam.device())

    class Tty(io.BytesIO):
        def isatty(self) -> bool:
            return True

    raw = Tty()
    out = io.TextIOWrapper(raw, write_through=True)
    err = io.StringIO()
    assert cli.main(["snapshot"], out=out, err=err) == 2
    assert raw.getvalue() == b"" and "terminal" in err.getvalue()


def test_call_rtsp_operation_prints_url_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    code, out, _ = run(monkeypatch, cam, "call", "video_streaming_rtsp", "describe_url", "videocodec=h264")
    assert code == 0
    url = json.loads(out)["url"]
    assert url.startswith("rtsp://") and "videocodec=h264" in url and "@" not in url
    assert cam.requests == []


def test_call_empty_binary_stream_truncates_output(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    cam = MockCamera()
    cam.cgi("/axis-cgi/media.cgi", text=b"", content_type="video/x-matroska")
    target = tmp_path / "out.mkv"
    target.write_bytes(b"stale")
    code, out, _ = run(monkeypatch, cam, "call", "media_stream", "get_media_stream", "-o", str(target))
    assert code == 0 and out == ""
    assert target.read_bytes() == b""


def test_call_binary_stream_limit_zero_creates_output(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    cam = MockCamera()
    cam.cgi("/axis-cgi/media.cgi", text=b"data", content_type="video/x-matroska")
    target = tmp_path / "out.mkv"
    code, _, _ = run(monkeypatch, cam, "call", "media_stream", "get_media_stream", "-o", str(target), "--limit", "0")
    assert code == 0 and target.read_bytes() == b""


def test_call_binary_stream_without_output_is_an_error_even_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.cgi("/axis-cgi/media.cgi", text=b"", content_type="video/x-matroska")
    code, _, err = run(monkeypatch, cam, "call", "media_stream", "get_media_stream")
    assert code == 2 and "--output" in err
