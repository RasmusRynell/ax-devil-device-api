"""Regression tests for the protocol, codegen and model review threads (PR #2)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from pydantic import ValidationError

from ax_devil_device_api._http.debug import redact_url, serialize
from ax_devil_device_api._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, parse_result
from ax_devil_device_api._protocols.cgi import _text_errors
from ax_devil_device_api._protocols.dca import DcaBinding, _build
from ax_devil_device_api._protocols.soap import SoapBinding, build_envelope
from ax_devil_device_api.apis import airqualitymodbus, mqtt_client, remote_object_storage
from ax_devil_device_api.apis.camera_pairing import OPS as PAIRING
from ax_devil_device_api.apis.mqtt_client import ClientConfig, ConfigureClientRequest, Server
from ax_devil_device_api.apis.network_diagnostics import OPS as DIAGNOSTICS
from ax_devil_device_api.apis.remote_object_storage import (
    AddDestinationRequest,
    AzureDestination,
    Destination,
    S3Destination,
)
from ax_devil_device_api.apis.stream_profiles import ProfileName
from ax_devil_device_api.errors import ApiError, ApiUnavailable, ResponseFormatError
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"
DESTINATIONS = "/config/rest/remote-object-storage/v1/destinations"
ROS = "/config/rest/remote-object-storage/v1"


def _hook(camera: MockCamera, call: Any) -> str:
    events: list[dict[str, Any]] = []
    with camera.device(on_request=events.append) as dev:
        call(dev)
    return json.dumps(events)


# -- 4. WebSocket session token is a secret query key --------------------------------------------


def test_wssession_query_key_is_redacted() -> None:
    url = redact_url("wss://cam/vapix/ws-data-stream?wssession=LIVE-TOKEN&sources=events")
    assert "LIVE-TOKEN" not in url and "sources=events" in url
    assert "LIVE-TOKEN" not in json.dumps(serialize({"wssession": "LIVE-TOKEN"}))


# -- 5. masked storage credentials ---------------------------------------------------------------


def test_azure_masked_credentials_are_redacted_in_hooks() -> None:
    camera = MockCamera()
    camera.rest("PUT", f"{DESTINATIONS}/d1", status=200)
    camera.rest("PATCH", f"{DESTINATIONS}/d1", status=200)
    camera.rest("POST", DESTINATIONS, status=201)
    azure = AzureDestination(sas="SAS-SECRET", shared_key="SHARED-SECRET")
    text = _hook(camera, lambda dev: dev.apis.remote_object_storage.add_destination(id="d1", azure=azure))
    assert "SAS-SECRET" not in text and "SHARED-SECRET" not in text


# -- 6. scalar DCA bodies of secret fields (D9) -------------------------------------------------


def test_scalar_secret_bodies_are_marked_sensitive() -> None:
    from ax_devil_device_api.apis.oidcsetup import OPS as OIDC
    from ax_devil_device_api.apis.ssh_config import OPS as SSH

    assert SSH.set_user_password.binding.sensitive is True
    assert OIDC.set_client_secret.binding.sensitive is True
    assert PAIRING.get_camera_pairing_status.binding.sensitive is False  # type: ignore[attr-defined]


def test_ssh_password_body_is_redacted_in_hooks() -> None:
    camera = MockCamera()
    camera.rest("PATCH", "/config/rest/ssh/v2/users/bob/password")
    text = _hook(camera, lambda dev: dev.apis.ssh_config.set_user_password("bob", "PLAIN-SECRET"))
    assert "PLAIN-SECRET" not in text and "<redacted>" in text


def test_non_secret_scalar_body_stays_visible() -> None:
    camera = MockCamera()
    camera.rest("PATCH", "/config/rest/ssh/v2/users/bob/comment")
    text = _hook(camera, lambda dev: dev.apis.ssh_config.set_user_comment("bob", "Bobby"))
    assert "Bobby" in text


# -- 11. constraints on scalar results ----------------------------------------------------------


def test_scalar_result_keeps_its_constraints() -> None:
    assert parse_result(DIAGNOSTICS.tcp_retransmissions, 3) == 3
    with pytest.raises(ResponseFormatError):
        parse_result(DIAGNOSTICS.tcp_retransmissions, -1)


# -- 12. colliding API class names are aliased in the namespace (fixed in the df06292 range) -----


def test_namespace_aliases_colliding_class_names() -> None:
    text = (Path(mqtt_client.__file__).parent / "__init__.py").read_text()
    assert "NetworkSettingsApi as NetworkSettingsApi_network_settings" in text
    assert "NetworkSettingsApi as NetworkSettingsApi_network_settings_api" in text


# -- 13. nested masked fields never survive a round trip (fixed in 6f525f5) ---------------------


def test_from_current_drops_nested_masked_fields() -> None:
    destination = Destination.model_validate(
        {
            "id": "d1",
            "description": "x",
            "azure": {"sas": "*****", "sharedKey": "*****", "container": "c"},
            "s3": {"accessKeyId": "*****", "secretAccessKey": "*****", "sessionToken": "*****", "bucket": "b"},
        },
        context={"ax_devil_response": True},
    )
    wire = AddDestinationRequest.from_current(destination).to_wire()
    assert "*****" not in json.dumps(wire)


# -- 14 / 56 / D5. unknown enum values survive a round trip, user input stays strict -------------

FUTURE = {"server": {"host": "broker", "protocol": "quic"}, "clientId": "cam1"}


def _future_config() -> ClientConfig:
    return ClientConfig.model_validate(FUTURE, context={"ax_devil_response": True})


def test_from_current_carries_unknown_enum_values() -> None:
    request = ConfigureClientRequest.from_current(_future_config())
    assert request.server is not None and request.server.protocol == "quic"
    assert request.to_wire()["server"]["protocol"] == "quic"


def test_unknown_enum_round_trip_is_sent_but_edits_stay_strict() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "configureClient")
    request = ConfigureClientRequest.from_current(_future_config())
    with camera.device() as dev:
        dev.apis.mqtt_client.configure_client(request)  # the device's own value passes revalidation
        sent = camera.calls("configureClient")[-1].json
        assert isinstance(sent, dict) and sent["params"]["server"]["protocol"] == "quic"
        assert request.server is not None
        request.server.protocol = "typo"  # type: ignore[assignment]
        with pytest.raises(ValidationError):
            dev.apis.mqtt_client.configure_client(request)


def test_user_constructed_requests_reject_unknown_enum_values() -> None:
    with pytest.raises(ValidationError):
        Server(host="b", protocol="quic")  # type: ignore[arg-type]


# -- 16. surplus positional arguments of overloaded methods -------------------------------------


def test_overloaded_method_rejects_surplus_positional_arguments() -> None:
    camera = MockCamera()
    camera.rest("PATCH", f"{ROS}/failover")
    with camera.device() as dev:
        api = dev.apis.remote_object_storage
        with pytest.raises(TypeError, match="at most 1 positional"):
            api.set_failover(None, "accidental")  # type: ignore[call-overload]
        assert not [r for r in camera.requests if r.path.endswith("/failover")]
        api.set_failover(None)
        assert [r for r in camera.requests if r.path.endswith("/failover")]


# -- 17 / D8. masked fields are masked in repr, nested too --------------------------------------


def test_masked_fields_are_masked_in_repr() -> None:
    azure = AzureDestination(shared_key="SECRET", sas="TOKEN")
    assert "SECRET" not in repr(azure) and "TOKEN" not in repr(azure) and "shared_key=" in repr(azure)
    parent = AddDestinationRequest(id="d", s3=S3Destination(secret_access_key="S3-SECRET"), azure=azure)
    assert "S3-SECRET" not in repr(parent) and "S3-SECRET" not in str(parent) and "SECRET" not in repr([parent])
    assert azure.shared_key == "SECRET"  # only the rendering is masked


# -- 18. scalar results tolerate unknown enum values --------------------------------------------


def test_scalar_enum_result_tolerates_new_values() -> None:
    op = PAIRING.get_camera_pairing_status
    assert parse_result(op, "PAIRED") == "PAIRED"
    assert parse_result(op, "QUARANTINED") == "QUARANTINED"
    with pytest.raises(ResponseFormatError):
        parse_result(op, 7)
    with pytest.raises(ResponseFormatError):
        parse_result(op, None)


# -- 19. ranged error codes ---------------------------------------------------------------------

RANGES = ApiInfo(
    id="t",
    name="T",
    family=Family.CGI,
    errors={"9000-9999": ErrorCode("License", "unavailable"), 9001: ErrorCode("Exact"), "100 - 199": ErrorCode("Low")},
)
RANGE_OP = Operation(RANGES, "op", binding=None)


def test_error_code_ranges() -> None:
    assert RANGE_OP.error_code(9500).description == "License"  # type: ignore[union-attr]
    assert RANGE_OP.error_code("9500").description == "License"  # type: ignore[union-attr]
    assert RANGE_OP.error_code(9001).description == "Exact"  # type: ignore[union-attr]
    assert RANGE_OP.error_code(150).description == "Low"  # type: ignore[union-attr]
    assert RANGE_OP.error_code(10000) is None
    assert RANGE_OP.error_code(None) is None


def test_ranged_license_error_is_unavailable() -> None:
    from ax_devil_device_api._protocols.base import api_error

    assert isinstance(api_error(RANGE_OP, 9500, "no license", http_status=200, details=None), ApiUnavailable)


# -- 20. only a whole-body comment is an error ---------------------------------------------------


def test_comment_prefix_with_data_is_not_an_error() -> None:
    op = Operation(RANGES, "op", binding=None)
    _text_errors(op, "<!-- build info -->\nready")  # no error
    with pytest.raises(ApiError, match="camera not found"):
        _text_errors(op, "<!-- camera not found -->\n")


# -- 21. path placeholders resolve through wire aliases (fixed in the df06292 range) -------------


def test_dca_placeholder_resolves_wire_alias() -> None:
    op = airqualitymodbus.OPS.get_configuration
    params = airqualitymodbus.ConfigurationSensorIdRequest(sensor_id="12")  # type: ignore[arg-type]
    request = _build(op, params)  # type: ignore[arg-type]
    assert request.path.endswith("/configurations/12")


# -- 22. cached versions are dropped on every API's own unsupported-version error -----------------


def test_unsupported_version_code_2000_invalidates_cached_versions() -> None:
    from ax_devil_device_api.apis.stream_profiles import OPS as PROFILES

    assert PROFILES.list.api.errors[2000].kind == "unsupported"  # type: ignore[attr-defined]
    camera = MockCamera()
    path = PROFILES.list.binding.path  # type: ignore[attr-defined]
    camera.jsonrpc(path, "list", error=(2000, "Unsupported version"))
    with camera.device() as dev:
        with pytest.raises(ApiError):
            dev.apis.stream_profiles.list(stream_profile_name=[ProfileName(name="p")])
        with pytest.raises(ApiError):
            dev.apis.stream_profiles.list(stream_profile_name=[ProfileName(name="p")])
    assert len(camera.calls("getSupportedVersions")) == 2  # negotiated again after the rejection


# -- 23. JSON-RPC null / missing data is validated, not replaced by {} --------------------------


def test_missing_jsonrpc_result_data_is_a_format_error() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus")  # data: {} (the mock default)
    camera.route(
        "POST",
        MQTT,
        lambda request: httpx.Response(200, json={"apiVersion": "1.0", "method": "getClientStatus", "data": None}),
        accepts=lambda recorded: isinstance(recorded.json, dict) and recorded.json.get("method") == "getClientStatus",
    )
    with camera.device() as dev, pytest.raises(ResponseFormatError):
        dev.apis.mqtt_client.get_client_status()


# -- 24. explicit None of an x-nullable SOAP element is an empty element --------------------------


def test_soap_explicit_null_is_an_empty_element() -> None:
    binding = SoapBinding("a", "SetSchedule", "urn:s")
    xml = build_envelope(binding, {"Name": "x", "ExceptionScheduleDefinition": None}).decode()
    assert "<ExceptionScheduleDefinition></ExceptionScheduleDefinition>" in xml
    assert "<Name>x</Name>" in xml


# -- 54 / D4. request objects are revalidated at send time ---------------------------------------


def test_edited_request_objects_are_revalidated() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "configureClient")
    request = ConfigureClientRequest(server=Server(host="b", protocol="ssl"), client_id="c")
    with camera.device() as dev:
        edited = request.model_copy(update={"server": Server.model_construct(host="b", protocol="nope")})
        with pytest.raises(ValidationError):
            dev.apis.mqtt_client.configure_client(edited)
        assert not camera.calls("configureClient")
        request.client_id = None  # type: ignore[assignment]  # assignment is not validated, sending is
        with pytest.raises(ValidationError):
            dev.apis.mqtt_client.configure_client(request)
        request.client_id = "c"
        dev.apis.mqtt_client.configure_client(request)
        assert len(camera.calls("configureClient")) == 1


def test_revalidation_keeps_explicit_nulls_and_set_fields() -> None:
    request = remote_object_storage.SetFailoverRequest(failover=None)
    again = request.revalidated()
    assert again.to_wire() == {"failover": None}


# -- 55. data_sources arrives wrapped in an object ---------------------------------------------


def test_list_data_sources_unwraps_the_collection() -> None:
    camera = MockCamera()
    camera.rest("GET", "/config/rest/analytics-mqtt/v1/data_sources", data={"data_sources": [{"key": "com.axis.a#1"}]})
    with camera.device() as dev:
        sources = dev.apis.analytics_mqtt.list_data_sources()
    assert [s.key for s in sources.data_sources] == ["com.axis.a#1"]


# -- D11. slash-preserving path placeholders and dot segments -----------------------------------

_NESTED = ApiInfo(id="t", name="T", family=Family.DCA)


class _Key(Model):
    key: str


def _nested_op(style: str) -> Operation[DcaBinding]:
    binding = DcaBinding("GET", "/r/{key}/x", key_styles=(("key", style),))  # type: ignore[arg-type]
    return Operation(_NESTED, "get", binding=binding, params=_Key)


@pytest.mark.parametrize(
    ("style", "value", "path"),
    [("path", "a/b c", "/r/a/b%20c/x"), ("segment", "a/b", "/r/a%2Fb/x"), ("dots_to_slashes", "a.b", "/r/a/b/x")],
)
def test_key_styles(style: str, value: str, path: str) -> None:
    assert _build(_nested_op(style), _Key(key=value)).path == path


@pytest.mark.parametrize("value", ["a/../b", "../b", "a//b", "/a", "a/", "a/."])
def test_path_style_rejects_dot_and_empty_segments(value: str) -> None:
    with pytest.raises(ValueError, match="not a valid path segment"):
        _build(_nested_op("path"), _Key(key=value))


@pytest.mark.parametrize("style", ["segment", "dots_to_slashes"])
def test_other_styles_reject_dot_segments(style: str) -> None:
    with pytest.raises(ValueError, match="not a valid path segment"):
        _build(_nested_op(style), _Key(key=".." if style == "segment" else "a..b"))


def test_documented_version_not_supported_codes_are_unsupported() -> None:
    from ax_devil_device_api.apis.axis_object_analytics import OPS as OBJECT_ANALYTICS
    from ax_devil_device_api.apis.basic_device_info import OPS as BASIC
    from ax_devil_device_api.apis.network_settings_api import OPS as NETWORK

    for code, ops in ((2003, BASIC), (4001, NETWORK), (2000, OBJECT_ANALYTICS)):
        api = next(op for op in vars(ops).values() if hasattr(op, "api")).api
        assert api.errors[code].kind == "unsupported"


def test_every_jsonrpc_spec_marks_version_errors_unsupported() -> None:
    import re

    import yaml

    root = Path(__file__).resolve().parents[2] / "specs" / "apis"
    pattern = re.compile(r"version.{0,40}(not supported|unsupported|isn.t supported)|unsupported.{0,20}version", re.I)
    bad = []
    for path in sorted(root.glob("*/*.yaml")):
        spec = yaml.safe_load(path.read_text())
        if spec.get("family") != "jsonrpc":
            continue
        for code, entry in (spec.get("errors") or {}).items():
            if pattern.search(entry.get("description", "")) and entry.get("kind") != "unsupported":
                bad.append((path.name, code))
    assert not bad


def test_emptied_list_is_rejected_at_send_time() -> None:
    from ax_devil_device_api.apis.ptz import CenterRequest

    request = CenterRequest(center=[1, 2])
    request.center.clear()
    with pytest.raises(ValidationError):
        request.revalidated()
