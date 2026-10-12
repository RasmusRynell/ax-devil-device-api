"""The contract harness itself: DCA request building for dotted keys and non-object bodies."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

from pydantic import Field

from ax_devil_device_api._protocols.base import Model
from ax_devil_device_api._protocols.dca import DcaBinding

def _load_harness():
    path = Path(__file__).resolve().parents[1] / "contract" / "_harness.py"
    spec = importlib.util.spec_from_file_location("contract_harness", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


h = _load_harness()


class _Topic(Model):
    topic: str


class _SetName(Model):
    id: str
    display_name: str = Field(validation_alias="displayName", serialization_alias="displayName")


def test_build_dca_dots_to_slashes_key_is_dotted_in_the_model() -> None:
    binding = DcaBinding("GET", "/config/rest/x/v1/topics/{topic}", key_styles=(("topic", "dots_to_slashes"),))
    op = SimpleNamespace(binding=binding, params=_Topic)
    model, path = h.build_dca(op, {"path": "/topics/com/axis/topic"}, "/config/rest/x/v1")
    assert model.topic == "com.axis.topic"
    assert path == "/config/rest/x/v1/topics/com/axis/topic"


def test_build_dca_value_body_takes_any_json_type() -> None:
    binding = DcaBinding("PATCH", "/r/{id}/displayName", body="value", body_field="displayName")
    op = SimpleNamespace(binding=binding, params=_SetName)
    model, _ = h.build_dca(op, {"path": "/r/7/displayName", "body": {"data": "Lobby"}}, "/r")
    assert (model.id, model.display_name) == ("7", "Lobby")
