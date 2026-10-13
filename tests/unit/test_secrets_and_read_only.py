"""Credential redaction in request hooks, masked/read-only handling and 503 mapping."""

from __future__ import annotations

import io
import json
from typing import Any

import httpx
import pytest
from pydantic import ValidationError

from ax_devil_device_api import cli
from ax_devil_device_api._http.debug import serialize
from ax_devil_device_api.apis.axis_audio_manager_pro import HttpAudioSession
from ax_devil_device_api.apis.remote_object_storage import (
    AddDestinationRequest,
    AzureDestination,
    Destination,
    S3Destination,
)
from ax_devil_device_api.errors import ApiUnavailable
from ax_devil_device_api.testing import MockCamera

DESTINATIONS = "/config/rest/remote-object-storage/v1/destinations"


def _azure() -> AzureDestination:
    return AzureDestination(account_name="acc", shared_key="SHAREDKEY==", sas="?sig=SASTOKEN", url="https://u:urlpw@h/c")


def test_request_hook_redacts_azure_keys_and_url_credentials() -> None:
    camera = MockCamera()
    camera.rest("POST", DESTINATIONS, status=201)
    events: list[dict[str, Any]] = []
    with camera.device(on_request=events.append) as dev:
        dev.apis.remote_object_storage.add_destination(id="d1", description="x", azure=_azure())
    text = json.dumps(events)
    for secret in ("SHAREDKEY==", "SASTOKEN", "urlpw"):
        assert secret not in text, secret
    assert "acc" in text


def test_request_hook_redacts_s3_and_embedded_urls_in_nested_strings() -> None:
    s3 = S3Destination(access_key_id="AKIA", secret_access_key="S3SECRET", session_token="SESSTOK")
    camera = MockCamera()
    camera.rest("POST", DESTINATIONS, status=201)
    events: list[dict[str, Any]] = []
    with camera.device(on_request=events.append) as dev:
        dev.apis.remote_object_storage.add_destination(id="d1", description="rtsp://root:rtsppw@10.0.0.1/x", s3=s3)
    text = json.dumps(events)
    for secret in ("S3SECRET", "SESSTOK", "rtsppw"):
        assert secret not in text, secret


def test_serialize_redacts_urls_in_plain_and_nested_strings() -> None:
    out = serialize({"proxy": "http://user:pw@proxy:3128", "list": ["rtsp://a:b@h/p?x=1"], "t": "see rtsp://a:b@h/p now"})
    text = json.dumps(out)
    assert "pw" not in text and ":b@" not in text
    assert "proxy:3128" in text


def test_validation_error_hides_input_values() -> None:
    with pytest.raises(ValidationError) as info:
        AddDestinationRequest(id="d", description="x", azure={"shared_key": 5, "bogus": "S3CRET"})  # type: ignore[arg-type]
    assert "S3CRET" not in str(info.value)


def test_cli_validation_error_hides_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    camera = MockCamera()
    monkeypatch.setattr(cli, "make_device", lambda args: camera.device())
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(
        ["--host", "cam", "call", "user_management", "add_user", "user=test", "pwd=s3cret", "grp=users"], out=out, err=err
    )
    assert code == 2
    assert "s3cret" not in err.getvalue()


def test_from_current_drops_nested_masked_secrets() -> None:
    destination = Destination.model_validate(
        {"id": "d", "description": "x", "azure": {"accountName": "a", "sharedKey": "*****", "sas": "*****", "url": "u"}},
        context={"ax_devil_response": True},
    )
    wire = AddDestinationRequest.from_current(destination).to_wire()
    assert wire == {"id": "d", "description": "x", "azure": {"accountName": "a", "url": "u"}}


def test_supplied_read_only_fields_are_not_sent() -> None:
    session = HttpAudioSession(type="HTTP", targets=["zone1"], id="server-assigned-id")
    assert "id" not in session.to_wire()
    camera = MockCamera()
    camera.route("POST", "/api/v1.2/audioSessions", lambda _: httpx.Response(200, json={"type": "HTTP", "id": "x", "targets": ["zone1"]}))
    with camera.device() as dev:
        dev.apis.axis_audio_manager_pro.create_audio_session(body=session)
    assert all("server-assigned-id" not in json.dumps(r.json) for r in camera.requests if r.method == "POST")


def test_http_503_with_error_envelope_is_unavailable() -> None:
    camera = MockCamera()
    camera.rest("GET", DESTINATIONS + "/d1", error=(100, "busy"), status=503)
    with camera.device() as dev:
        with pytest.raises(ApiUnavailable) as info:
            dev.apis.remote_object_storage.get_destination("d1")
    assert info.value.code == 100 and "busy" in str(info.value)
