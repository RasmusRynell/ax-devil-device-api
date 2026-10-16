"""Model rules: strict construction, lenient responses, wire form, and repr."""

from __future__ import annotations

from typing import ClassVar, Literal

import pytest
from pydantic import Field, ValidationError

from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, parse_result
from ax_devil_device_api.apis.mqtt_client import ClientStatus
from ax_devil_device_api.errors import ResponseFormatError


class Server(Model):
    host: str
    alpn_protocol: str | None = Field(default=None, validation_alias="alpnProtocol", serialization_alias="alpnProtocol")


class Config(Model):
    server: Server | None = None
    protocol: Literal["tcp", "ssl"] | None = None


class Wire(Model):
    __nullable__: ClassVar[frozenset[str]] = frozenset({"keep_alive"})

    client_id: str = Field(validation_alias="clientId", serialization_alias="clientId")
    keep_alive: int | None = Field(default=None, validation_alias="keepAlive", serialization_alias="keepAlive")
    note: str | None = None


CONFIG_OP = Operation(ApiInfo(id="test-api", name="Test API", family=Family.JSONRPC), "get", binding=object(), result=Config)
STATUS_OP = Operation(ApiInfo(id="test-api", name="Test API", family=Family.JSONRPC), "status", binding=object(), result=ClientStatus)


def test_unknown_field_rejected_at_construction() -> None:
    with pytest.raises(ValidationError, match="unexpected field"):
        Server(host="broker", bogus=1)  # type: ignore[call-arg]


def test_unknown_nested_field_rejected_at_construction() -> None:
    with pytest.raises(ValidationError, match="bogus"):
        Config(server={"host": "broker", "bogus": 1})  # type: ignore[arg-type]


def test_alias_and_name_both_accepted_at_construction() -> None:
    assert Server(host="broker", alpnProtocol="h2").alpn_protocol == "h2"  # type: ignore[call-arg]
    assert Server(host="broker", alpn_protocol="h2").alpn_protocol == "h2"


def test_response_ignores_unknown_fields_top_level_and_nested() -> None:
    data = {"server": {"host": "broker", "futureKnob": True}, "newTopLevel": 1}

    result = parse_result(CONFIG_OP, data)

    assert isinstance(result, Config)
    assert result.server is not None and result.server.host == "broker"
    # Unknown fields are dropped, not kept, so they never reach the wire.
    assert result.to_wire() == {"server": {"host": "broker"}}


def test_response_shape_mismatch_is_response_format_error() -> None:
    with pytest.raises(ResponseFormatError):
        parse_result(CONFIG_OP, {"server": {"alpnProtocol": "h2"}})  # host is required


def test_missing_required_response_field_is_response_format_error() -> None:
    with pytest.raises(ResponseFormatError, match="connectionStatus"):
        parse_result(STATUS_OP, {"status": {"state": "active"}})


def test_unset_optional_fields_are_none() -> None:
    config = Config()
    assert config.server is None and config.protocol is None
    assert config.model_fields_set == set()


def test_unknown_enum_value_tolerated_in_response() -> None:
    result = parse_result(STATUS_OP, {"status": {"state": "active", "connectionStatus": "reconnecting"}})

    assert result.status.connection_status == "reconnecting"
    assert result.status.state == "active"


def test_unknown_enum_value_tolerated_in_optional_response_field() -> None:
    result = parse_result(CONFIG_OP, {"protocol": "quic"})

    assert result.protocol == "quic"


def test_invalid_enum_value_rejected_at_construction() -> None:
    with pytest.raises(ValidationError):
        Config(protocol="quic")  # type: ignore[arg-type]


def test_wrong_type_still_rejected_in_response() -> None:
    with pytest.raises(ResponseFormatError):
        parse_result(CONFIG_OP, {"server": "not-an-object"})


def test_explicit_none_rejected_for_non_nullable_field() -> None:
    with pytest.raises(ValidationError, match="cannot be null"):
        Wire(client_id="cam1", note=None)


def test_explicit_none_rejected_by_wire_name_too() -> None:
    with pytest.raises(ValidationError, match="cannot be null"):
        Server(host="broker", alpnProtocol=None)  # type: ignore[call-arg]


def test_explicit_none_allowed_and_serialized_for_nullable_field() -> None:
    wire = Wire(client_id="cam1", keep_alive=None)

    assert "keep_alive" in wire.model_fields_set
    assert wire.to_wire() == {"clientId": "cam1", "keepAlive": None}


def test_null_in_response_is_accepted_for_any_optional_field() -> None:
    result = parse_result(CONFIG_OP, {"protocol": None, "server": None})

    assert result.protocol is None and result.server is None


def test_to_wire_omits_unset_fields_and_uses_aliases() -> None:
    assert Wire(client_id="cam1").to_wire() == {"clientId": "cam1"}
    assert Wire(client_id="cam1", note="hi", keep_alive=30).to_wire() == {
        "clientId": "cam1",
        "keepAlive": 30,
        "note": "hi",
    }


def test_to_wire_uses_aliases_in_nested_models() -> None:
    config = Config(server=Server(host="broker", alpn_protocol="h2"))
    assert config.to_wire() == {"server": {"host": "broker", "alpnProtocol": "h2"}}


def test_set_fields_returns_only_explicitly_set_attributes() -> None:
    assert Wire(client_id="cam1", note="x").set_fields() == {"client_id": "cam1", "note": "x"}


def test_repr_hides_unset_fields() -> None:
    text = repr(Wire(client_id="cam1"))
    assert "client_id='cam1'" in text
    assert "keep_alive" not in text
    assert "note" not in text


def test_repr_shows_explicit_none() -> None:
    assert "keep_alive=None" in repr(Wire(client_id="cam1", keep_alive=None))


def test_const_discriminator_stays_strict_in_responses() -> None:
    from pydantic import TypeAdapter

    from ax_devil_device_api._protocols.base import RESPONSE_CONTEXT
    from ax_devil_device_api.apis.axis_audio_manager_pro import (
        AudioSession,
        HttpAudioSession,
        RtpAudioSession,
        SipAudioSession,
    )

    adapter = TypeAdapter(AudioSession)
    context = {RESPONSE_CONTEXT: True}
    for tag, cls in (("HTTP", HttpAudioSession), ("RTP", RtpAudioSession), ("SIP", SipAudioSession)):
        parsed = adapter.validate_python({"type": tag, "id": "s1", "targets": ["t"]}, context=context)
        assert type(parsed) is cls
    with pytest.raises(ValidationError):
        HttpAudioSession.model_validate({"type": "RTP", "id": "s1", "targets": ["t"]}, context=context)
    with pytest.raises(ValidationError):
        adapter.validate_python({"type": "FUTURE", "id": "s1", "targets": ["t"]}, context=context)


def test_unavailable_power_status_sentinel_parses_but_other_integers_do_not() -> None:
    from ax_devil_device_api._protocols.base import RESPONSE_CONTEXT
    from ax_devil_device_api.apis.power_settings import Capabilities

    context = {RESPONSE_CONTEXT: True}
    for value in (True, False, -1):
        assert Capabilities.model_validate({"powerStatusSupport": value}, context=context).power_status_support == value
    with pytest.raises(ValidationError):
        Capabilities.model_validate({"powerStatusSupport": 5}, context=context)
