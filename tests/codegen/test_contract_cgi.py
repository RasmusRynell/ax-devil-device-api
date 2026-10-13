"""Contract harness: cgi examples with path placeholders and templated argument names."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))  # tests/ -> the contract package

from contract._runner import run_example
from test_bindings import base_spec, load_module
from test_contract_examples import op


def run(spec: dict[str, Any], op_id: str, index: int = 0) -> None:
    module = load_module(spec)
    run_example(spec, module.OPS, op_id, spec["operations"][op_id]["examples"][index])


SPEC = base_spec(
    "cgi",
    {"path": "/axis-cgi/param.cgi"},
    {
        "get_cfg": op(
            {"path": "/local/app/{endpoint}.cgi", "reply": "text"},
            [
                {"title": "path", "request": {"path": "/local/app/cloud2.cgi"}, "response": {"text": "x"}},
                {"title": "endpoint outside the enum", "request": {"path": "/local/app/other.cgi"}},
                {"title": "no path", "request": {"query": {}}},
            ],
            params={"type": "object", "required": ["endpoint"], "properties": {"endpoint": {"type": "string", "enum": ["cloud", "cloud2", "cloud3"]}}},
            result={"type": "string"},
        ),
        "set_rate": op(
            {"query": {"action": "update"}, "reply": "text_ok"},
            [
                {"title": "index from the names", "request": {"query": {"root.Image.I2.RateControl.Mode": "mbr", "root.Image.I2.RateControl.MaxBitrate": "1000"}}, "response": {"text": "OK"}},
                {"title": "indexes disagree", "request": {"query": {"root.Image.I1.RateControl.Mode": "mbr", "root.Image.I2.RateControl.MaxBitrate": "1000"}}},
            ],
            effect="write", write="patch",
            params={"type": "object", "required": ["n"], "properties": {
                "n": {"type": "integer"},
                "root.Image.I{n}.RateControl.Mode": {"type": "string", "x-python-name": "mode"},
                "root.Image.I{n}.RateControl.MaxBitrate": {"type": "integer", "x-python-name": "max_bitrate"},
            }},
            positional=["n"],
        ),
    },
)  # fmt: skip


def test_path_placeholder_is_filled_from_the_example_path() -> None:
    run(SPEC, "get_cfg", 0)


def test_path_that_does_not_match_the_template_fails() -> None:
    with pytest.raises(AssertionError, match="does not match"):
        module = load_module(SPEC)
        run_example(SPEC, module.OPS, "get_cfg", {"request": {"path": "/elsewhere/cloud.cgi"}})


def test_path_value_outside_the_enum_fails() -> None:
    with pytest.raises(Exception, match="enum|literal"):
        run(SPEC, "get_cfg", 1)


def test_templated_placeholder_path_needs_an_example_path() -> None:
    with pytest.raises(AssertionError, match="request.path"):
        run(SPEC, "get_cfg", 2)


def test_templated_names_map_to_the_index_argument() -> None:
    run(SPEC, "set_rate", 0)


def test_templated_names_with_different_indexes_fail() -> None:
    with pytest.raises(AssertionError, match="another argument says"):
        run(SPEC, "set_rate", 1)
