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


def _soap_op(binding):
    return SimpleNamespace(
        binding=binding, params=None, id="Op", api=SimpleNamespace(id="x"), error_code=lambda code, message=None: None
    )


def test_soap_expected_matches_runtime_envelope_ignoring_whitespace_and_order() -> None:
    from ax_devil_device_api._protocols.soap import SoapBinding, build_envelope

    binding = SoapBinding("urn:a", "Get", "urn:ns")
    sent = build_envelope(binding, {"@token": "t", "A": "1", "B": [True, False]})
    expected = h.soap_expected_from_params(binding, {"B": [True, False], "A": 1, "@token": "t"})
    assert h.soap_canonical(h.soap_body_element(sent)) == h.soap_canonical(expected)
    other = h.soap_expected_from_params(binding, {"@token": "t", "A": "2", "B": [True, False]})
    assert h.soap_canonical(h.soap_body_element(sent)) != h.soap_canonical(other)


def test_soap_prefixed_names_resolve_through_binding_namespaces() -> None:
    binding = SimpleNamespace(element="Get", namespace="urn:ns", namespaces={"tt": "urn:tt"})
    expected = h.soap_expected_from_params(binding, {"tt:Token": "1", "Plain": "2"})
    xml = '<Get xmlns="urn:ns" xmlns:t="urn:tt">\n <t:Token> 1 </t:Token><Plain>2</Plain></Get>'
    assert h.soap_canonical(h.soap_body_element(xml)) == h.soap_canonical(expected)


def test_soap_documented_fault_round_trips_through_the_runtime_decoder() -> None:
    import pytest

    from ax_devil_device_api._protocols.soap import SoapBinding, _decode
    from ax_devil_device_api.errors import ApiError

    fault = {"code": "ter:InvalidArgs", "message": "bad"}
    status, body = h.soap_response_body({"error": fault})
    response = SimpleNamespace(status=status, content=body.encode())
    with pytest.raises(ApiError) as caught:
        _decode(_soap_op(SoapBinding("a", "E", "n")), response)  # type: ignore[arg-type]
    assert caught.value.code == "ter:InvalidArgs" and "bad" in str(caught.value)
    documented = h.soap_documented_fault({"text": h.soap_fault_xml(fault)})
    assert documented is not None and "ter:InvalidArgs" in documented["any_of"]


def test_service_json_fault_uses_the_subcode_as_the_key() -> None:
    from ax_devil_device_api._protocols.service_json import fault_of

    fault = h.service_json_fault({"code": "axast:DeviceNotCalibrated", "message": "m"})
    assert fault_of(fault) is not None and fault["FaultSubCode"] == "axast:DeviceNotCalibrated"
    assert h.service_json_fault({"code": "env:Sender", "message": "m"})["FaultSubCode"] is None


def test_build_rest_splits_path_query_and_body() -> None:
    from ax_devil_device_api._protocols.rest import RestBinding

    class _Params(Model):
        volume_id: str
        filter: str | None = None
        level: int | None = None

    binding = RestBinding("PATCH", "/api/v1/vols/{volume_id}", body="object", query=(("filter", "filter"),))
    op = SimpleNamespace(binding=binding, params=_Params)
    model, path, query, body = h.build_rest(
        op, {"path": "/vols/7", "query": {"filter": "a"}, "body": {"level": 3}}, "/api/v1"
    )
    assert (model.volume_id, model.filter, model.level) == ("7", "a", 3)
    assert path == "/api/v1/vols/7" and query == {"filter": ["a"]} and body == {"level": 3}
