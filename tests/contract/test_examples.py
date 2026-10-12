"""Contract tests: every documented example in specs/apis/**/*.yaml against the generated modules.

One test per (spec id, operation id, example index). An example may carry
``x-contract``:

- ``skip: "reason"``: the example is skipped.
- ``template: true``: the example is a syntax template (placeholders instead of
  values). The runtime still runs it, but only the method and path are compared
  with the example, and an example whose placeholder values do not validate
  against the models is skipped instead of failing. Examples that do validate
  are still run through the runtime.

Examples without a request (response-only) for operations with required
arguments validate just the response against the result model.
"""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
import yaml

from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import ApiError, HttpError

from . import _harness as h

SPECS = Path(os.environ.get("CONTRACT_SPECS_DIR") or Path(__file__).resolve().parents[2] / "specs" / "apis")
FAMILIES = {"jsonrpc", "dca", "cgi", "service_json", "soap", "rest"}


def _cases():
    for path in sorted(SPECS.rglob("*.yaml")):
        try:
            spec = yaml.safe_load(path.read_text())
        except yaml.YAMLError as error:
            yield pytest.param(("invalid", path, error), id=f"{path.stem}::invalid-yaml")
            continue
        sid = spec.get("id", path.stem)
        family = spec.get("family")
        if family not in FAMILIES:
            yield pytest.param(None, id=f"{sid}::*", marks=pytest.mark.skip(reason=f"{sid}: family {family!r} not covered"))
            continue
        try:
            module = importlib.import_module(f"ax_devil_device_api.apis.{spec['python']['module']}")
            ops = module.OPS
        except Exception as error:  # noqa: BLE001
            reason = f"{sid}: cannot import module ({type(error).__name__}: {error})"
            yield pytest.param(None, id=f"{sid}::*", marks=pytest.mark.skip(reason=reason))
            continue
        for op_id, op_spec in (spec.get("operations") or {}).items():
            binding = op_spec.get("binding") or {}
            if "session" in binding or "rtsp" in binding or h.is_stream_reply(binding):
                continue  # sessions, RTSP URLs and streamed bodies make no request/response exchange to compare
            for index, example in enumerate(op_spec.get("examples") or []):
                yield pytest.param((spec, ops, op_id, example), id=f"{sid}::{op_id}::{index}")


def _jsonrpc_response(spec, op, example, sent: h.Sent):
    response = example.get("response")
    method = sent.json.get("method") if isinstance(sent.json, dict) else None
    if method == "getSupportedVersions":
        negotiation = spec["binding"].get("negotiation") or {}
        key = ((negotiation.get("get_supported_versions") or {}) if isinstance(negotiation, dict) else {}).get("key", "apiVersions")
        return httpx.Response(200, json={"apiVersion": "1.0", "method": method, "data": {key: spec["binding"]["versions"]}})
    if method != op.binding.method:
        return None
    body: dict[str, Any] = {"apiVersion": spec["binding"]["versions"][-1], "method": method}
    status = 200
    if response is None:
        body["data"] = {}
    else:
        status = response.get("status", 200)
        if "error" in response:
            body["error"] = response["error"]
        else:
            body["data"] = response.get("data", {})
    return httpx.Response(status, json=body)


def _dca_response(example, sent):
    response = example.get("response") or {"status": 200, "body": {"status": "success"}}
    return httpx.Response(response.get("status", 200), json=response.get("body", {}))


def _cgi_response(example, sent):
    response = example.get("response") or {"status": 200, "text": "OK"}
    ctype = response.get("content_type") or response.get("content-type") or "text/plain"
    return httpx.Response(response.get("status", 200), content=str(response.get("text", "")).encode(), headers={"content-type": ctype})


def _service_json_response(spec, op, example, sent):
    if not isinstance(sent.json, dict) or list(sent.json) != [op.binding.operation]:
        return None
    response = example.get("response") or {}
    if isinstance(response.get("error"), dict):
        return httpx.Response(response.get("status", 400), json=h.service_json_fault(response["error"]))
    if "data" not in response:
        return httpx.Response(response.get("status", 200), content=b"")
    return httpx.Response(response.get("status", 200), json=response["data"])


def _soap_response(example, sent):
    status, body = h.soap_response_body(example.get("response"))
    return httpx.Response(status, content=body.encode(), headers={"content-type": "application/soap+xml; charset=utf-8"})


def _rest_response(example, sent):
    response = example.get("response") or {}
    body = response.get("body")
    status = response.get("status", 200)
    if body is None:
        return httpx.Response(status, content=str(response.get("text", "")).encode())
    return httpx.Response(status, json=body)


def _expected_error(family: str, response: dict | None, op=None):
    if not response:
        return None
    if family == "service_json":
        return response.get("error") if isinstance(response.get("error"), dict) else None
    if family == "soap":
        return h.soap_documented_fault(response)
    if family == "rest":
        status = response.get("status", 200)
        if status < 400:
            return None
        if status != 401 and op is not None and op.error_code(status) is not None:
            return {"code": status, "message": None}
        return {"http_status": status}
    if family == "jsonrpc":
        return response.get("error")
    if family == "dca":
        body = response.get("body")
        return body.get("error") if isinstance(body, dict) and body.get("status") == "error" else None
    return h.cgi_documented_error(response)


@pytest.mark.parametrize("case", list(_cases()))
def test_example(case):
    if case[0] == "invalid":
        pytest.fail(f"{case[1].name} is not valid YAML: {case[2]}")
    spec, ops, op_id, example = case
    marker = example.get("x-contract") or {}
    skip = marker.get("skip")
    if skip:
        pytest.skip(skip)
    template = bool(marker.get("template"))
    family = spec["family"]
    op = getattr(ops, op_id)
    request = example.get("request")
    response = example.get("response")

    model: Any = None
    expected_path = op.binding.path
    expected_args: dict[str, str] = {}
    expected_xml: Any = None
    expected_query: dict[str, list[str]] = {}
    expected_body: Any = None
    if request is not None:
        try:
            if family == "jsonrpc":
                model = h.build_jsonrpc(op, request)
            elif family == "dca":
                model, expected_path = h.build_dca(op, request, spec["binding"]["root"])
            elif family == "service_json":
                model = h.build_service_json(op, request)
            elif family == "soap":
                model, expected_xml = h.build_soap(op, request)
            elif family == "rest":
                model, expected_path, expected_query, expected_body = h.build_rest(op, request, spec["binding"].get("root", ""))
            else:
                model, expected_args = h.build_cgi(op, request)
        except Exception as error:  # noqa: BLE001
            if template:
                pytest.skip(f"template example: request placeholders do not validate ({type(error).__name__})")
            raise
    elif op.params is not None:
        try:
            model = op.params.model_validate({})
        except Exception:  # noqa: BLE001
            # Required arguments and no request in the example: check the response alone.
            if response is None or _expected_error(family, response) is not None or family not in ("jsonrpc", "dca", "service_json", "rest"):
                pytest.skip("response-only example, the operation needs arguments and the response cannot be checked alone")
            try:
                h.check_response_only(op, family, response)
            except Exception as error:  # noqa: BLE001
                if template:
                    pytest.skip(f"template example: response placeholders do not validate ({type(error).__name__})")
                raise
            return

    def handler(sent: h.Sent):
        if family == "jsonrpc":
            return _jsonrpc_response(spec, op, example, sent)
        if family == "dca":
            return _dca_response(example, sent)
        if family == "service_json":
            return _service_json_response(spec, op, example, sent)
        if family == "soap":
            return _soap_response(example, sent)
        if family == "rest":
            return _rest_response(example, sent)
        return _cgi_response(example, sent)

    fake = h.Fake(handler)
    dev = Device("camera.test", credentials=("root", "pass"), transport=httpx.MockTransport(fake))
    error = _expected_error(family, response, op)
    try:
        if error is not None and "http_status" in error:
            with pytest.raises(HttpError) as http_caught:
                dev.invoke(op, model)
            assert http_caught.value.status == error["http_status"]
        elif error is not None:
            with pytest.raises(ApiError) as caught:
                dev.invoke(op, model)
            expected_code = error.get("code", error.get("errorCode", error.get("id")))
            if "any_of" in error:  # a documented fault: the code is one of its subcodes or its code value
                allowed = list(cast("list[Any]", error["any_of"]))
                assert caught.value.code in allowed, f"code {caught.value.code!r} not in {allowed}"
                if expected_code is not None:
                    assert caught.value.code == expected_code
            elif family != "cgi" or expected_code is not None:
                assert caught.value.code == expected_code
            if family in ("cgi", "service_json", "soap", "rest") and error.get("message"):
                assert str(error["message"]) in str(caught.value)
        elif response is None:
            try:
                dev.invoke(op, model)
            except ApiError:
                raise
            except Exception:  # noqa: BLE001  (request-only: the placeholder reply may not fit the result type)
                pass
        else:
            try:
                result = dev.invoke(op, model)
                h.check_result(op, result)
            except Exception as error:  # noqa: BLE001
                if template and not isinstance(error, ApiError):
                    pytest.skip(f"template example: response placeholders do not validate ({type(error).__name__})")
                raise
    finally:
        dev.close()

    # Request side
    if request is None:
        return
    calls = [c for c in fake.calls if not (family == "jsonrpc" and isinstance(c.json, dict) and c.json.get("method") == "getSupportedVersions")]
    assert len(calls) == 1, f"expected one request, got {len(calls)}"
    sent = calls[0]
    if template:
        # Placeholder values are not compared with what was sent; method and path still are.
        if family == "jsonrpc":
            assert sent.path == op.binding.path and sent.json["method"] == op.binding.method
        elif family == "service_json":
            assert sent.path == op.binding.path and list(sent.json) == [op.binding.operation]
        elif family == "soap":
            assert sent.path == op.binding.path
            assert h.soap_body_element(sent.raw).tag == h.soap_canonical(expected_xml)[0]
        elif family == "rest":
            assert sent.method == op.binding.method and sent.path == expected_path
        elif family == "dca":
            assert sent.method == op.binding.method and sent.path == expected_path
        else:
            assert sent.method == op.binding.method and sent.path == op.binding.path
        return
    if family == "jsonrpc":
        assert sent.path == op.binding.path
        assert sent.json["method"] == op.binding.method
        if getattr(op.binding, "params_placement", "params") == "top_level":
            # Arguments sit next to apiVersion/method in the envelope.
            sent_args = {k: v for k, v in sent.json.items() if k not in ("apiVersion", "method", "context")}
            assert sent_args == (request.get("params") or {})
        else:
            assert sent.json.get("params", {}) == (request.get("params") if request.get("params") is not None else {})
    elif family == "dca":
        assert sent.method == op.binding.method
        assert sent.path == expected_path
        body = request.get("body")
        if body == {} and sent.json == {"data": {}}:
            # Docs show an empty object for argument-less actions; the runtime sends {"data": {}}.
            body = sent.json
        assert sent.json == (json.loads(json.dumps(body)) if body is not None else None)
    elif family == "service_json":
        assert sent.path == op.binding.path
        assert sent.json == {op.binding.operation: json.loads(json.dumps(request.get("params") or {}))}
    elif family == "soap":
        assert sent.method == "POST" and sent.path == op.binding.path
        assert h.soap_canonical(h.soap_body_element(sent.raw)) == h.soap_canonical(expected_xml)
    elif family == "rest":
        assert sent.method == op.binding.method
        assert sent.path == expected_path
        got: dict[str, list[str]] = {}
        for k, v in sent.pairs:
            got.setdefault(k, []).append(v)
        assert got == expected_query
        assert sent.json == (json.loads(json.dumps(expected_body)) if expected_body is not None else None)
    else:
        assert sent.method == op.binding.method
        assert sent.path == op.binding.path
        assert {**sent.query, **(sent.form or {})} == expected_args
        if "form" in request:
            assert sent.form is not None
        h.check_sent_body(op, request, sent)
