"""A value given on the command line never comes back in a usage or parameter error, whatever its kind."""

from __future__ import annotations

import io
import json

import pytest

from ax_devil_device_api import cli
from ax_devil_device_api.testing import MockCamera

SENTINEL = "s3cr3t-sentinel"


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(list(argv), out=out, err=err)
    return code, out.getvalue(), err.getvalue()


CASES = {
    "unrecognized option after the command": ["apis", "--password", SENTINEL],
    "unrecognized option, equals form": ["apis", f"--password={SENTINEL}"],
    "unknown secret-named option": ["--token", SENTINEL, "apis"],
    "unknown secret-named option, equals form": [f"--bearer={SENTINEL}", "apis"],
    "short password option after the command": ["apis", "-p", SENTINEL],
    "extra positional": ["apis", SENTINEL],
    "invalid command choice": [SENTINEL],
    "invalid int value": ["--port", SENTINEL, "apis"],
    "invalid int value, equals form": [f"--port={SENTINEL}", "apis"],
    "invalid float value": ["--timeout", SENTINEL, "apis"],
    "invalid limit": ["call", "mqtt_client", "get_client_status", "--limit", SENTINEL],
    "invalid option choice": ["snapshot", "--color", SENTINEL],
    "ambiguous option": [f"--h={SENTINEL}", "apis"],
    "positional without an equals sign": ["call", "mqtt_client", "get_client_status", SENTINEL],
    "secret key=value pair of an unknown parameter": ["call", "mqtt_client", "get_client_status", f"password={SENTINEL}"],
    "secret key=value pair, unknown api": ["call", "no_such_api", "x", f"password={SENTINEL}"],
    "out of range port": ["--port", f"{SENTINEL}0", "apis"],
}


@pytest.mark.parametrize("argv", CASES.values(), ids=CASES.keys())
def test_the_value_never_reaches_stdout_or_stderr(argv: list[str]) -> None:
    code, out, err = run(*argv)
    assert code != 0
    assert SENTINEL not in out and SENTINEL not in err, err
    assert json.loads(err.splitlines()[-1])["error"]["message"]


def test_the_unrecognized_message_names_options_only() -> None:
    _, _, err = run("apis", "--password", SENTINEL)
    assert "unrecognized arguments: --password <value>" in json.loads(err.splitlines()[-1])["error"]["message"]


def test_the_equals_form_is_elided_too() -> None:
    _, _, err = run("apis", f"--password={SENTINEL}")
    assert "--password=<" in err  # the value is elided (shown as <elided> or <redacted>)


def test_a_missing_argument_is_still_reported() -> None:
    code, _, err = run("--password")
    assert code == 2 and "expected one argument" in err


def test_ordinary_usage_errors_keep_their_useful_text() -> None:
    _, _, err = run("--port", "0", "apis")
    assert "--port must be an integer between 1 and 65535" in err
    _, _, err = run("no_such_command_x")
    assert "invalid choice" in err and "choose from" in err and "no_such_command_x" not in err


def test_parameter_errors_from_a_running_command_do_not_echo_secret_pairs(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    monkeypatch.setattr(cli, "make_device", lambda args: cam.device())
    out, err = io.StringIO(), io.StringIO()
    cli.main(["call", "mqtt_client", "configure_client", f"password={SENTINEL}", f"token={SENTINEL}"], out=out, err=err)
    assert SENTINEL not in out.getvalue() + err.getvalue()


DASH_SECRETS = ["-" + SENTINEL, "--" + SENTINEL, "-" + SENTINEL + "-x", "=" + SENTINEL]

DASH_CASES = {
    "unrecognized, separate value": lambda s: ["apis", "--password", s],
    "unrecognized, equals form": lambda s: ["apis", f"--password={s}"],
    "unknown token option first": lambda s: ["--token", s, "apis"],
    "unknown bearer option, equals form": lambda s: [f"--bearer={s}", "apis"],
    "short option after the command": lambda s: ["apis", "-p", s],
    "invalid port after a password": lambda s: ["--password", s, "--port", "x", "apis"],
    "invalid command after a password": lambda s: ["--password", s, "nosuchcommand"],
    "secret key=value pair": lambda s: ["call", "mqtt_client", "get_client_status", f"password={s}"],
    "secret pair, unknown api": lambda s: ["call", "no_such_api", "x", f"token={s}"],
    "ambiguous option next to a secret": lambda s: ["--password", s, "--h", "apis"],
}


@pytest.mark.parametrize("secret", DASH_SECRETS)
@pytest.mark.parametrize("build", DASH_CASES.values(), ids=DASH_CASES.keys())
def test_dash_prefixed_secret_values_never_reach_the_output(build, secret: str) -> None:  # type: ignore[no-untyped-def]
    code, out, err = run(*build(secret))
    assert code != 0
    assert secret.lstrip("-=") not in out + err, err
    assert json.loads(err.splitlines()[-1])["error"]["message"]
