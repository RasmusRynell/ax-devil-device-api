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
    assert code == 0 and json.loads(out)["apis"]["mqtt_client"]["status"] == "yes"


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


def test_call_output_dash_writes_binary_to_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.cgi("/axis-cgi/media.cgi", text=b"data", content_type="video/x-matroska")
    monkeypatch.setattr(cli, "make_device", lambda args: cam.device())
    raw = io.BytesIO()
    out = io.TextIOWrapper(raw, write_through=True)
    assert cli.main(["call", "media_stream", "get_media_stream", "-o", "-"], out=out, err=io.StringIO()) == 0
    assert raw.getvalue() == b"data"


def test_call_output_dash_refuses_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.cgi("/axis-cgi/media.cgi", text=b"data", content_type="video/x-matroska")
    monkeypatch.setattr(cli, "make_device", lambda args: cam.device())

    class Tty(io.BytesIO):
        def isatty(self) -> bool:
            return True

    raw = Tty()
    out = io.TextIOWrapper(raw, write_through=True)
    err = io.StringIO()
    assert cli.main(["call", "media_stream", "get_media_stream", "-o", "-"], out=out, err=err) == 2
    assert raw.getvalue() == b"" and "terminal" in err.getvalue()


def test_local_value_error_is_json_invalid_parameters_not_a_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    code, _, err = run(monkeypatch, MockCamera(), "call", "analytics_mqtt", "remove_publisher", "id=.")
    assert code == 2 and "Traceback" not in err
    error = json.loads(err.splitlines()[-1])["error"]
    assert error["type"] == "InvalidParameters" and error["message"]


def test_configuration_error_keeps_the_library_error_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(["--host", "camera.local:8443", "--user", "u", "--password", "p", "call", "mqtt_client", "get_client_status"], out=out, err=err)
    error = json.loads(err.getvalue().splitlines()[-1])["error"]
    assert code == 1 and error["type"] == "ConfigurationError" and "port" in error["message"]


def test_explicit_empty_password_is_kept_not_replaced_by_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CAM_USER", "envuser")
    monkeypatch.setenv("CAM_PASS", "envpass")
    args = cli.build_parser().parse_args(["--host", "10.0.0.1", "--user", "root", "--password", "", "summary"])
    dev = cli.make_device(args)
    assert dev.config.credentials is not None
    assert (dev.config.credentials.username, dev.config.credentials.password) == ("root", "")  # type: ignore[union-attr]


def test_empty_password_without_environment_is_not_a_missing_password(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("AX_DEVIL_USER", "CAM_USER", "AX_DEVIL_PASSWORD", "CAM_PASS"):
        monkeypatch.delenv(name, raising=False)
    args = cli.build_parser().parse_args(["--host", "10.0.0.1", "--user", "root", "--password", "", "summary"])
    assert cli.make_device(args).config.credentials is not None


def test_user_without_any_password_still_asks_for_both(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("AX_DEVIL_USER", "CAM_USER", "AX_DEVIL_PASSWORD", "CAM_PASS"):
        monkeypatch.delenv(name, raising=False)
    args = cli.build_parser().parse_args(["--host", "10.0.0.1", "--user", "root", "summary"])
    with pytest.raises(cli.CliError, match="both"):
        cli.make_device(args)


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["call", "mqtt_client", "get_client_status", "--json", ""], "not valid JSON"),
        (["call", "mqtt_client", "get_client_status", "--json", "@"], "file name"),
        (["--host", "", "summary"], "--host must not be empty"),
        (["--host", "cam", "--user", "", "summary"], "--user must not be empty"),
        (["--host", "cam", "--ca-bundle", "", "summary"], "--ca-bundle must not be empty"),
        (["call", "mqtt_client", "get_client_status", "-o", ""], "--output must not be empty"),
        (["snapshot", "-o", ""], "--output must not be empty"),
        (["snapshot", "--resolution", ""], "--resolution must not be empty"),
        (["snapshot", "--camera", ""], "--camera must not be empty"),
    ],
)
def test_empty_cli_values_are_usage_errors_not_absent_options(monkeypatch: pytest.MonkeyPatch, argv: list[str], message: str) -> None:
    for name in ("AX_DEVIL_HOST", "AX_DEVIL_USER", "CAM_USER", "AX_DEVIL_PASSWORD", "CAM_PASS"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AX_DEVIL_HOST", "cam")
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(argv, out=out, err=err)
    assert code == 2 and "Traceback" not in err.getvalue()
    assert message in json.loads(err.getvalue().splitlines()[-1])["error"]["message"]


def test_explicit_empty_host_does_not_fall_back_to_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AX_DEVIL_HOST", "envhost")
    args = cli.build_parser().parse_args(["--host", "other", "summary"])
    assert cli.make_device(args).config.host == "other"


# --- --output behaves the same for every kind of result ------------------------------------------------------------------------

PORT_CGI = "/axis-cgi/io/port.cgi"


def _monitor(monkeypatch: pytest.MonkeyPatch, text: str, *extra: str) -> tuple[int, str, str]:
    cam = MockCamera()
    cam.cgi(PORT_CGI, text=text)
    return run(monkeypatch, cam, "call", "io_port", "monitor_ports", "monitor=[1]", *extra)


def test_line_stream_goes_to_the_output_file(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    target = tmp_path / "events.log"
    code, out, err = _monitor(monkeypatch, "1=active\n2=inactive\n", "--output", str(target))
    assert code == 0, err
    assert out == ""
    lines = target.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line) for line in lines] == ["1=active", "2=inactive"]


def test_empty_line_stream_still_creates_and_truncates_the_output_file(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    target = tmp_path / "events.log"
    target.write_text("stale content\n")
    code, out, err = _monitor(monkeypatch, "", "--output", str(target))
    assert code == 0, err
    assert out == "" and target.read_text() == ""
    fresh = tmp_path / "new.log"
    assert _monitor(monkeypatch, "", "--output", str(fresh))[0] == 0 and fresh.exists()


def test_dash_output_means_stdout_for_a_line_stream(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    code, out, err = _monitor(monkeypatch, "1=active\n", "--output", "-")
    assert code == 0, err
    assert [json.loads(line) for line in out.splitlines()] == ["1=active"]
    assert not list(tmp_path.iterdir())


def test_line_stream_without_output_still_prints_to_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out, _ = _monitor(monkeypatch, "1=active\n")
    assert code == 0 and [json.loads(line) for line in out.splitlines()] == ["1=active"]


def test_json_result_goes_to_the_output_file_too(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    cam = MockCamera()
    cam.jsonrpc(MQTT, "getClientStatus", data={"status": {"state": "active", "connectionStatus": "connected"}})
    target = tmp_path / "result.json"
    code, out, err = run(monkeypatch, cam, "call", "mqtt_client", "get_client_status", "-o", str(target))
    assert code == 0, err
    assert out == "" and json.loads(target.read_text(encoding="utf-8")) is not None
    code, out, _ = run(monkeypatch, cam, "call", "mqtt_client", "get_client_status", "-o", "-")
    assert code == 0 and json.loads(out) is not None
