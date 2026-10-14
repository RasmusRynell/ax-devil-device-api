"""Every public numeric input rejects bool, float (for counts), inf, nan, negatives and (where invalid) zero."""

from __future__ import annotations

import io
from collections.abc import Callable
from typing import Any

import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.options import Heartbeat, RequestOptions, RetryPolicy
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
