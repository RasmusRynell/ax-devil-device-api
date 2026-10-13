"""D14: spec-masked names are redacted per operation, never process-wide; name patterns stay global."""

from __future__ import annotations

import json
from typing import Any

import pytest

from ax_devil_device_api._http.debug import emit_request
from ax_devil_device_api._http.types import FormBody, JsonBody, Request
from ax_devil_device_api._runtime.driver import Call
from ax_devil_device_api.apis import cert_est, certificate_management, serial_port


def record(request: Request) -> str:
    events: list[dict[str, Any]] = []
    emit_request(events.append, request, "https://cam/x", 5.0, True)
    return json.dumps(events)


def prepared(op: Any, request: Request) -> Request:
    return Call(op=op).prepare(request)


@pytest.mark.parametrize("name", ["key", "code", "config", "certificate"])
def test_masked_name_is_redacted_only_on_the_request_that_masks_it(name: str) -> None:
    secret = "S3CR3T-value"
    masking = Request("POST", "/a", body=JsonBody({name: secret}), query=((name, secret),), masked=frozenset({name}))
    other = Request("POST", "/b", body=JsonBody({name: "visible"}), query=((name, "visible"),))
    assert secret not in record(masking)
    assert record(masking).count("<redacted>") >= 2
    assert "visible" in record(other)
    # the earlier masking request left no process-wide state behind
    assert secret in record(Request("POST", "/c", body=FormBody(((name, secret),))))


def test_masked_names_cover_nested_and_form_fields() -> None:
    request = Request(
        "POST", "/a", body=JsonBody({"outer": {"Key": "NESTED"}, "list": [{"key": "IN-LIST"}]}), masked=frozenset({"key"})
    )
    text = record(request)
    assert "NESTED" not in text and "IN-LIST" not in text


def test_load_pkcs12_certificate_is_redacted_but_the_cert_est_public_certificate_is_not() -> None:
    pkcs = prepared(
        certificate_management.OPS.load_pkcs12,
        Request("POST", "/p", body=JsonBody({"Pkcs12": {"acert:Id": "i", "acert:Certificate": "PFX-BYTES", "acert:Password": "pw"}})),
    )
    text = record(pkcs)
    assert "PFX-BYTES" not in text and "pw" not in text
    est = prepared(
        cert_est.OPS.set_profile_certificate,
        Request("PATCH", "/e", body=JsonBody({"data": "PUBLIC-CERT"})),
    )
    assert "PUBLIC-CERT" in record(est)


def test_templated_masked_name_matches_the_filled_in_name() -> None:
    op = serial_port.OPS.set_remote_port
    request = prepared(op, Request("GET", "/s", query=(("RemotePort.R3.AuthenticationKey", "KEYVALUE"), ("x", "plain"))))
    text = record(request)
    assert "KEYVALUE" not in text and "plain" in text


def test_authentication_key_pattern_is_global() -> None:
    text = record(Request("GET", "/s", query=(("Port.I0.AuthenticationKey", "KEYVALUE"),)))
    assert "KEYVALUE" not in text
