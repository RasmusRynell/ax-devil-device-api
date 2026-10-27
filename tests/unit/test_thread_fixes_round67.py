"""Request strictness accepts any Mapping / Sequence implementation (the signatures say Mapping[str, Any]), checks the
items with the same strict rules, and sends plain dicts and lists."""

from __future__ import annotations

import collections.abc
import json
from collections import UserDict, UserList
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from pydantic import ValidationError

from ax_devil_device_api._protocols.base import Model
from ax_devil_device_api.apis.intercom_configuration import UpdateConfigurationRequest
from ax_devil_device_api.testing import MockCamera


class Shapes(Model):
    table: Mapping[str, int] | None = None
    names: Sequence[str] | None = None
    free: dict[str, Any] | None = None
    many: list[int] | None = None
    pair: tuple[int, str] | None = None
    flag: bool | None = None


def test_a_userdict_is_accepted_where_a_mapping_is_documented_and_serialized_as_a_dict() -> None:
    request = UpdateConfigurationRequest(image_file=UserDict({"name": "logo.png", "data": UserDict({"a": [1, 2]})}))  # type: ignore[arg-type]
    wire = request.to_wire()
    assert wire == {"imageFile": {"name": "logo.png", "data": {"a": [1, 2]}}}
    json.dumps(wire)  # plain containers all the way down


def test_the_call_reaches_the_device_with_a_userdict() -> None:
    camera = MockCamera()
    camera.route("POST", "/config/rest/intercom-configuration/v1beta", lambda request: __import__("httpx").Response(200, json={"status": "success"}))
    with camera.device() as dev:
        try:
            dev.apis.intercom_configuration.update_configuration(image_file=UserDict({"name": "logo.png"}))
        except Exception as error:  # noqa: BLE001 - whatever the device mock answers, the request must have been built and sent
            assert not isinstance(error, (ValidationError, TypeError)), error
    assert camera.requests, "the request was built and sent"
    assert "logo.png" in json.dumps(camera.requests[-1].json)


def test_other_mapping_and_sequence_implementations_are_accepted() -> None:
    mapping = collections.ChainMap({"a": 1}, {"b": 2})
    shapes = Shapes(table=mapping, names=UserList(["x", "y"]), free=UserDict({"k": UserList([1, 2])}), many=UserList([1, 2]), pair=(1, "a"))  # type: ignore[arg-type]
    wire = shapes.to_wire()
    assert wire["table"] == {"a": 1, "b": 2} and wire["names"] == ["x", "y"] and wire["free"] == {"k": [1, 2]} and wire["many"] == [1, 2]
    assert type(wire["free"]) is dict and type(wire["free"]["k"]) is list
    json.dumps(wire)


def test_a_tuple_is_accepted_for_a_sequence_annotation() -> None:
    assert Shapes(names=("a", "b")).to_wire()["names"] == ["a", "b"]  # type: ignore[arg-type]


def test_the_items_are_checked_with_the_same_strict_rules() -> None:
    with pytest.raises(ValidationError):
        Shapes(table=UserDict({"a": True}))  # type: ignore[arg-type]  # a bool is not a number
    with pytest.raises(ValidationError):
        Shapes(table=UserDict({"a": 1.5}))  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        Shapes(names=UserList(["a", True]))  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        Shapes(many=UserList([1, True]))  # type: ignore[arg-type]


def test_text_and_bytes_are_not_sequences_and_a_mapping_is_not_a_list() -> None:
    for bad in ("abc", b"abc"):
        with pytest.raises(ValidationError):
            Shapes(names=bad)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        Shapes(many=UserDict({"a": 1}))  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        Shapes(table=["a"])  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        Shapes(flag=UserDict())  # type: ignore[arg-type]


def test_non_finite_numbers_in_a_userdict_are_still_refused() -> None:
    with pytest.raises(ValidationError):
        Shapes(free=UserDict({"x": [float("nan")]}))  # type: ignore[arg-type]


def test_the_abstract_types_are_what_the_checks_use() -> None:
    assert isinstance(UserDict(), collections.abc.Mapping) and isinstance(UserList(), collections.abc.Sequence)
