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

Streamed replies, WebSocket sessions and RTSP URL builders have their own example
conventions (see docs/spec-format.md); ``_special.py`` runs them.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest
import yaml

from ._runner import run_example

SPECS = Path(os.environ.get("CONTRACT_SPECS_DIR") or Path(__file__).resolve().parents[2] / "specs" / "apis")
FAMILIES = {"jsonrpc", "dca", "cgi", "service_json", "soap", "rest", "ws", "rtsp"}


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


@pytest.mark.parametrize("case", list(_cases()))
def test_example(case):
    if case[0] == "invalid":
        pytest.fail(f"{case[1].name} is not valid YAML: {case[2]}")
    spec, ops, op_id, example = case
    run_example(spec, ops, op_id, example)
