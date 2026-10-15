"""``call <api> <op> param=@path`` sends a file for upload parameters; other parameters never interpret ``@``."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from ax_devil_device_api import Device, cli
from ax_devil_device_api._http.upload import is_upload_field
from ax_devil_device_api.testing import MockCamera

UPLOAD = "/axis-cgi/applications/upload.cgi"


def run(monkeypatch: pytest.MonkeyPatch, cam: MockCamera, *argv: str) -> tuple[int, str, str]:
    monkeypatch.setattr(cli, "make_device", lambda args: cam.device())
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(list(argv), out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def test_upload_application_sends_the_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    package = tmp_path / "app.eap"
    package.write_bytes(b"PACKAGE-BYTES")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, text="OK")

    monkeypatch.setattr(cli, "make_device", lambda args: Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler)))
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(["call", "application_api", "upload_application", f"package=@{package}"], out=out, err=err)
    assert code == 0, err.getvalue()
    upload = next(r for r in seen if r.url.path == UPLOAD)
    assert b"PACKAGE-BYTES" in upload.content and b'filename="app.eap"' in upload.content


def test_a_missing_file_is_a_usage_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    code, _, err = run(monkeypatch, MockCamera(), "call", "application_api", "upload_application", f"package=@{tmp_path / 'nope.eap'}")
    assert code == 2 and "no such file" in json.loads(err.splitlines()[-1])["error"]["message"]


def test_a_bare_at_sign_needs_a_file_name(monkeypatch: pytest.MonkeyPatch) -> None:
    code, _, err = run(monkeypatch, MockCamera(), "call", "application_api", "upload_application", "package=@")
    assert code == 2 and "file name" in err


def test_at_on_a_non_upload_non_text_parameter_is_a_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # --limit-like numeric parameter: pick any operation parameter typed as a number
    op = cli._entry("mqtt_client").operations["configure_client"]
    assert op.params is not None
    numeric = next(
        name
        for name, field in op.params.model_fields.items()
        if not is_upload_field(field) and not cli._accepts_text(field.annotation)
    )
    code, _, err = run(monkeypatch, MockCamera(), "call", "mqtt_client", "configure_client", f"{numeric}=@file")
    assert code == 2 and "'@' is only for file uploads" in err


def test_string_parameters_keep_a_leading_at_as_text() -> None:
    op = cli._entry("mqtt_client").operations["configure_client"]
    assert op.params is not None
    texts = [n for n, f in op.params.model_fields.items() if cli._accepts_text(f.annotation) and not is_upload_field(f)]
    assert texts, "the operation has a text parameter"
    assert cli.parse_params([f"{texts[0]}=@name"], None, op)[texts[0]] == "@name"


def test_ops_marks_upload_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    out, err = io.StringIO(), io.StringIO()
    assert cli.main(["ops", "application_api"], out=out, err=err) == 0
    ops: dict[str, Any] = {o["name"]: o for o in json.loads(out.getvalue())}
    assert any(p["upload"] for p in ops["upload_application"]["parameters"])
    assert not any(p["upload"] for p in ops["list_applications"]["parameters"]) if "list_applications" in ops else True
