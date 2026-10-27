"""D18: an operation whose request or result can carry name/value-pair models handles secrets (a parameter named
``password`` carries its value in ``Value``), so no device error text reaches the exception."""

from __future__ import annotations

import traceback
from typing import Any

import httpx
import pytest
from pydantic import Field

from ax_devil_device_api._protocols.base import (
    ApiInfo,
    Family,
    Model,
    Operation,
    has_parameter_pairs,
    has_secret_fields,
)
from ax_devil_device_api._protocols.soap import SoapBinding
from ax_devil_device_api.apis.action_service import (
    OPS,
    ActionParameter,
    ActionParameters,
    NewRecipientConfiguration,
)
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import ApiError, DeviceError
from ax_devil_device_api.testing import MockCamera

SECRET = "hunter2-SENTINEL"


def _fault(text: str) -> str:
    return (
        '<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope"><env:Body><env:Fault><env:Code><env:Value>env:Sender</env:Value>'
        f'</env:Code><env:Reason><env:Text xml:lang="en">{text}</env:Text></env:Reason><env:Detail>{text}</env:Detail></env:Fault></env:Body></env:Envelope>'
    )


def _everything(error: BaseException) -> str:
    return "\n".join([str(error), repr(error), repr(getattr(error, "details", None)), repr(vars(error)), "".join(traceback.format_exception(error))])


def test_the_operation_is_secret_bearing_now_but_a_plain_one_is_not() -> None:
    assert has_secret_fields(OPS.add_recipient_configuration)
    assert not has_secret_fields(OPS.remove_recipient_configuration)  # no pair models, no masked fields


def test_a_soap_fault_echoing_a_parameter_value_leaks_nothing_on_add_recipient_configuration() -> None:
    camera = MockCamera()
    camera.route("POST", "/vapix/services", lambda _: httpx.Response(500, text=_fault(f"invalid parameter password={SECRET} (value {SECRET})")))
    recipient = NewRecipientConfiguration(
        name="r", template_token="t", parameters=ActionParameters(parameter=[ActionParameter(name="password", value=SECRET)])
    )
    with camera.device() as dev, pytest.raises(DeviceError) as caught:
        dev.apis.action_service.add_recipient_configuration(new_recipient_configuration=recipient)
    assert isinstance(caught.value, ApiError) and "device message omitted" in str(caught.value)
    assert SECRET not in _everything(caught.value)


def test_a_fault_echoing_a_value_that_is_not_a_name_value_pair_pattern_is_omitted_too() -> None:
    # The value is not next to a secret-looking text in the fault: only the static rule can protect it.
    camera = MockCamera()
    camera.route("POST", "/vapix/services", lambda _: httpx.Response(500, text=_fault(f"rejected {SECRET}")))
    recipient = NewRecipientConfiguration(
        name="r", template_token="t", parameters=ActionParameters(parameter=[ActionParameter(name="pw", value=SECRET)])
    )
    with camera.device() as dev, pytest.raises(DeviceError) as caught:
        dev.apis.action_service.add_recipient_configuration(new_recipient_configuration=recipient)
    assert SECRET not in _everything(caught.value)


class PlainParams(Model):
    count: int | None = None
    label: str | None = None


def _soap_op(params: Any) -> Operation[Any]:
    return Operation(ApiInfo(id="t", name="T", family=Family.SOAP), "act", SoapBinding("a", "Act", "urn:x"), result=None, params=params)


def test_an_operation_without_pair_models_or_masked_fields_keeps_its_fault_text() -> None:
    op = _soap_op(PlainParams)
    assert not has_secret_fields(op)
    transport = httpx.MockTransport(lambda request: httpx.Response(500, text=_fault("camera is busy")))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev, pytest.raises(ApiError) as caught:
        dev.invoke(op, count=1)
    assert "camera is busy" in caught.value.message


class Pair(Model):
    name: str = Field(validation_alias="@Name", serialization_alias="@Name")
    value: str = Field(validation_alias="@Value", serialization_alias="@Value")


class Keyed(Model):
    key: str
    value: str


class NameOnly(Model):
    name: str
    comment: str | None = None


class Holder(Model):
    items: list[Pair] | None = None


@pytest.mark.parametrize(
    ("tp", "expected"),
    [
        (Pair, True), (Keyed, True), (Holder, True), (list[Pair], True), (dict[str, Pair], True), (Pair | None, True),
        (NameOnly, False), (PlainParams, False), (int, False), (list[int], False), (None, False),
    ],
)
def test_has_parameter_pairs_finds_pair_models_at_any_depth(tp: Any, expected: bool) -> None:
    assert has_parameter_pairs(tp) is expected
