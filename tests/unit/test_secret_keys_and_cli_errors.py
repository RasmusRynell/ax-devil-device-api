"""D19 follow-ups: mapping KEYS are redacted like values, and the CLI prints only display forms of errors."""

from __future__ import annotations

import io
import json
from typing import Any

import pytest

from ax_devil_device_api import cli
from ax_devil_device_api._http.debug import serialize
from ax_devil_device_api._runtime.capabilities import Support, SupportResult
from ax_devil_device_api.errors import ApiError, display_text, sanitize_details

NASTY = ["password=hunter2", "rtsp://u:p@h/x"]
FORBIDDEN = ["hunter2", "u:p@"]


@pytest.mark.parametrize("key", NASTY)
def test_serialize_redacts_a_secret_in_a_mapping_key(key: str) -> None:
    shown = json.dumps(serialize({key: "invalid"}))
    assert not any(bad in shown for bad in FORBIDDEN)
    assert len(serialize({key: "invalid"})) == 1


def test_a_key_that_is_a_secret_pair_redacts_its_value_too() -> None:
    assert list(serialize({"password=hunter2": "also-secret"}).values()) == ["<redacted>"]


@pytest.mark.parametrize("key", NASTY)
def test_keys_are_redacted_at_every_depth(key: str) -> None:
    value = {"a": [{"b": {key: "x", "ok": "fine"}}]}
    shown = json.dumps(sanitize_details(value))
    assert not any(bad in shown for bad in FORBIDDEN) and '"ok": "fine"' in shown
    nested_json = json.dumps({"x": {key: "y"}})
    assert not any(bad in json.dumps(serialize(nested_json)) for bad in FORBIDDEN)


def test_keys_that_collapse_to_the_same_text_are_kept_apart() -> None:
    shown = serialize({"password=a": "1", "password=b": "2", "password=c": "3"})
    assert len(shown) == 3 and all(not v.startswith("1") for v in shown.values())
    assert sanitize_details({"password=a": 1, "password=b": 2}).keys() != {"password=<redacted>"}
    assert len(sanitize_details({"password=a": 1, "password=b": 2})) == 2


def test_ordinary_keys_and_values_are_unchanged() -> None:
    assert sanitize_details({"id": 1, "name": "front door", "tags": ["a", "b"]}) == {"id": 1, "name": "front door", "tags": ["a", "b"]}


def test_idempotent() -> None:
    once = sanitize_details({"password=hunter2": "x", "password=other": "y"})
    assert sanitize_details(once) == once


# --- the CLI prints display forms only --------------------------------------------------------------------------------------------


class StubDevice:
    def __init__(self, error: Exception | None = None, results: Any = None) -> None:
        self.error = error
        self.results = results

    def __enter__(self) -> StubDevice:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def invoke(self, op: Any, **params: Any) -> Any:
        assert self.error is not None
        raise self.error

    def supports_many(self, apis: Any) -> Any:
        return {api: self.results for api in apis}


def run(monkeypatch: pytest.MonkeyPatch, device: Any, *argv: str) -> tuple[int, str, str]:
    monkeypatch.setattr(cli, "make_device", lambda args: device)
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(list(argv), out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def _no_secrets(*texts: str) -> None:
    for text in texts:
        assert not any(bad in text for bad in FORBIDDEN), text


@pytest.mark.parametrize("nasty", NASTY)
def test_api_error_fields_never_reach_cli_output(monkeypatch: pytest.MonkeyPatch, nasty: str) -> None:
    error = ApiError(
        nasty, nasty, nasty, f"failed {nasty}", description=nasty, kind=None, http_status=400, details={nasty: nasty, "k": nasty}
    )
    code, out, err = run(monkeypatch, StubDevice(error), "call", "mqtt_client", "get_client_status")
    assert code == 1
    _no_secrets(out, err)
    payload = json.loads(err.splitlines()[-1])["error"]
    assert payload["type"] == "ApiError" and payload["code"] == display_text(nasty, 100)


def test_an_integer_code_is_kept_as_an_integer(monkeypatch: pytest.MonkeyPatch) -> None:
    error = ApiError("mqtt-client", "get_client_status", 2104, "bad value", http_status=400)
    _, _, err = run(monkeypatch, StubDevice(error), "call", "mqtt_client", "get_client_status")
    assert json.loads(err.splitlines()[-1])["error"]["code"] == 2104


@pytest.mark.parametrize("nasty", NASTY)
def test_probe_errors_and_reasons_never_reach_supported_output(monkeypatch: pytest.MonkeyPatch, nasty: str) -> None:
    unknown = SupportResult(Support.UNKNOWN, f"incomplete {nasty}", (f"classic API discovery failed: ConnectionFailed: {nasty}",))
    yes = SupportResult(Support.YES, f"listed {nasty}", (f"probe failed {nasty}",))
    for results, argv in ((unknown, ["supported"]), (unknown, ["apis", "--supported"]), (yes, ["supported"]), (yes, ["apis", "--supported"])):
        code, out, err = run(monkeypatch, StubDevice(results=results), *argv)
        assert code in (0, 1)
        _no_secrets(out, err)


def test_summary_probe_errors_are_shown_through_the_display_form(monkeypatch: pytest.MonkeyPatch) -> None:
    class Summary:
        def to_dict(self) -> dict[str, Any]:
            return {"model": "X", "probe_errors": {"applications": "password=hunter2 failed", "services": "rtsp://u:p@h/x"}}

    monkeypatch.setattr(cli, "device_summary", lambda dev: Summary())
    code, out, err = run(monkeypatch, StubDevice(), "summary")
    assert code == 0
    _no_secrets(out, err)
    assert json.loads(out)["model"] == "X"


@pytest.mark.parametrize("exc", [ValueError("bad value password=hunter2"), TypeError("rtsp://u:p@h/x"), OSError("password=hunter2")])
def test_local_error_messages_are_redacted_too(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    code, out, err = run(monkeypatch, StubDevice(exc), "call", "mqtt_client", "get_client_status")
    assert code in (1, 2)
    _no_secrets(out, err)


def test_missing_values_stay_json_null_not_the_text_null(monkeypatch: pytest.MonkeyPatch) -> None:
    undocumented = ApiError("mqtt-client", "get_client_status", None, "something failed", kind=None, http_status=500)
    code, out, err = run(monkeypatch, StubDevice(undocumented), "call", "mqtt_client", "get_client_status")
    payload = json.loads(err.splitlines()[-1])["error"]
    assert code == 1 and payload["code"] is None and payload["kind"] is None
    assert payload["api"] == "mqtt-client" and payload["operation"] == "get_client_status" and payload["message"]
    assert '"null"' not in err


def test_text_values_are_still_shown_and_integers_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    documented = ApiError("mqtt-client", "get_client_status", 2104, "bad value", kind="invalid_argument", http_status=400)
    _, _, err = run(monkeypatch, StubDevice(documented), "call", "mqtt_client", "get_client_status")
    payload = json.loads(err.splitlines()[-1])["error"]
    assert payload["code"] == 2104 and payload["kind"] == "invalid_argument"
    string_code = ApiError("mqtt-client", "get_client_status", "E-7", "bad value", http_status=400)
    _, _, err = run(monkeypatch, StubDevice(string_code), "call", "mqtt_client", "get_client_status")
    assert json.loads(err.splitlines()[-1])["error"]["code"] == "E-7"
