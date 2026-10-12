"""Contract tests: every documented example in specs/apis/**/*.yaml against the generated modules.

One test per (spec id, operation id, example index). An example may carry
``x-contract: {skip: "reason"}`` to be skipped.
"""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Any

import httpx
import pytest
import yaml

from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import ApiError

from . import _harness as h

SPECS = Path(os.environ.get("CONTRACT_SPECS_DIR") or Path(__file__).resolve().parents[2] / "specs" / "apis")
FAMILIES = {"jsonrpc", "dca", "cgi"}


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
            for index, example in enumerate(op_spec.get("examples") or []):
                yield pytest.param((spec, ops, op_id, example), id=f"{sid}::{op_id}::{index}")


def _jsonrpc_response(spec, op, example, sent: h.Sent):
    response = example.get("response")
    method = sent.json.get("method") if isinstance(sent.json, dict) else None
    if method == "getSupportedVersions":
        return httpx.Response(200, json={"apiVersion": "1.0", "method": method, "data": {"apiVersions": spec["binding"]["versions"]}})
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


def _expected_error(family: str, response: dict | None):
    if not response:
        return None
    if family == "jsonrpc":
        return response.get("error")
    if family == "dca":
        body = response.get("body")
        return body.get("error") if isinstance(body, dict) and body.get("status") == "error" else None
    return None


@pytest.mark.parametrize("case", list(_cases()))
def test_example(case):
    if case[0] == "invalid":
        pytest.fail(f"{case[1].name} is not valid YAML: {case[2]}")
    spec, ops, op_id, example = case
    skip = (example.get("x-contract") or {}).get("skip")
    if skip:
        pytest.skip(skip)
    family = spec["family"]
    op = getattr(ops, op_id)
    request = example.get("request")
    response = example.get("response")

    model: Any = None
    expected_path = op.binding.path
    expected_args: dict[str, str] = {}
    if request is not None:
        if family == "jsonrpc":
            model = h.build_jsonrpc(op, request)
        elif family == "dca":
            model, expected_path = h.build_dca(op, request, spec["binding"]["root"])
        else:
            model, expected_args = h.build_cgi(op, request)
    elif op.params is not None:
        try:
            model = op.params.model_validate({})
        except Exception:  # noqa: BLE001
            pytest.skip("response-only example and the operation needs arguments")

    def handler(sent: h.Sent):
        if family == "jsonrpc":
            return _jsonrpc_response(spec, op, example, sent)
        if family == "dca":
            return _dca_response(example, sent)
        return _cgi_response(example, sent)

    fake = h.Fake(handler)
    dev = Device("camera.test", credentials=("root", "pass"), transport=httpx.MockTransport(fake))
    error = _expected_error(family, response)
    try:
        if error is not None:
            with pytest.raises(ApiError) as caught:
                dev.invoke(op, model)
            assert caught.value.code == error.get("code")
        elif response is None:
            try:
                dev.invoke(op, model)
            except ApiError:
                raise
            except Exception:  # noqa: BLE001  (request-only: the placeholder reply may not fit the result type)
                pass
        else:
            result = dev.invoke(op, model)
            h.check_result(op, result)
    finally:
        dev.close()

    # Request side
    if request is None:
        return
    calls = [c for c in fake.calls if not (family == "jsonrpc" and isinstance(c.json, dict) and c.json.get("method") == "getSupportedVersions")]
    assert len(calls) == 1, f"expected one request, got {len(calls)}"
    sent = calls[0]
    if family == "jsonrpc":
        assert sent.path == op.binding.path
        assert sent.json["method"] == op.binding.method
        assert sent.json.get("params", {}) == (request.get("params") or {})
    elif family == "dca":
        assert sent.method == op.binding.method
        assert sent.path == expected_path
        body = request.get("body")
        assert sent.json == (json.loads(json.dumps(body)) if body is not None else None)
    else:
        assert sent.method == op.binding.method
        assert sent.path == op.binding.path
        assert {**sent.query, **(sent.form or {})} == expected_args
        if "form" in request:
            assert sent.form is not None
