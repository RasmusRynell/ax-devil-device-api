"""Device error text never reaches the exception of an operation that handles secrets (result OR request); other
operations get it redacted. The raw text is used only for the code/kind lookup."""

from __future__ import annotations

import traceback
from typing import Any

import httpx
import pytest

from ax_devil_device_api._protocols.base import (
    ApiInfo,
    ErrorCode,
    Family,
    Model,
    Operation,
    api_error,
    error_text,
    has_secret_fields,
)
from ax_devil_device_api._protocols.cgi import CgiBinding, Text
from ax_devil_device_api._protocols.soap import SoapBinding
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import AccessDenied, ApiError, AuthError, DeviceError
from ax_devil_device_api.testing import MockCamera

SENTINEL = "SENTINEL-SECRET-VALUE"
ROOT = "/config/rest/audio-multicast-ctrl/v1beta"


def _clean(error: BaseException) -> None:
    rendered = "".join(traceback.format_exception(error))
    assert SENTINEL not in str(error) and SENTINEL not in repr(error) and SENTINEL not in rendered
    assert SENTINEL not in repr(getattr(error, "details", None))


class Secret(Model):
    __masked__ = frozenset({"key"})  # type: ignore[assignment]
    key: str | None = None


class Plain(Model):
    value: int | None = None


class SendsKey(Model):
    __masked__ = frozenset({"key"})  # type: ignore[assignment]
    key: str


def _info(family: Family, **errors: ErrorCode) -> ApiInfo:
    return ApiInfo(id="t", name="T", family=family, errors={7: ErrorCode("documented seven", "invalid_argument"), **errors})  # type: ignore[arg-type]


def _invoke(op: Operation[Any], response: httpx.Response, **kwargs: Any) -> DeviceError:
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(lambda request: response)) as dev:
        with pytest.raises(DeviceError) as caught:
            dev.invoke(op, **kwargs)
    return caught.value


# -- the repro from the comment: a real DCA operation ---------------------------------------------------------------------


def test_dca_400_message_of_get_source_is_omitted_but_code_and_kind_stay() -> None:
    camera = MockCamera()
    camera.rest("GET", f"{ROOT}/sources/s1", error=(7, f"bad {SENTINEL}"), status=400)
    with camera.device() as dev, pytest.raises(ApiError) as caught:
        dev.apis.audio_multicast_ctrl.get_source("s1")
    error = caught.value
    _clean(error)
    assert error.code == 7 and error.http_status == 400 and "device message omitted" in error.message


@pytest.mark.anyio
async def test_the_same_through_the_async_path() -> None:
    camera = MockCamera()
    camera.rest("GET", f"{ROOT}/sources/s1", error=(7, f"bad {SENTINEL}"), status=400)
    async with camera.async_device() as dev:
        with pytest.raises(ApiError) as caught:
            await dev.apis.audio_multicast_ctrl.get_source("s1")
    _clean(caught.value)
    assert caught.value.code == 7


# -- a request that carries a secret --------------------------------------------------------------------------------------


def test_set_source_srtp_key_handles_a_secret_even_though_its_result_is_none() -> None:
    from ax_devil_device_api.apis.audio_multicast_ctrl import OPS

    assert has_secret_fields(OPS.set_source_srtp_key) and OPS.set_source_srtp_key.result is None


@pytest.mark.parametrize("status", [500, 400, 409])
def test_a_500_echoing_the_key_leaks_nothing_from_set_source_srtp_key(status: int) -> None:
    camera = MockCamera()
    camera.route("PATCH", f"{ROOT}/sources/s1/srtpKey", lambda _: httpx.Response(status, json={"status": "error", "error": {"code": 7, "message": f"bad key {SENTINEL}"}}))
    with camera.device() as dev, pytest.raises(DeviceError) as caught:
        dev.apis.audio_multicast_ctrl.set_source_srtp_key("s1", srtp_key=SENTINEL)
    _clean(caught.value)


def test_a_plain_text_500_echoing_the_key_leaks_nothing_from_set_source_srtp_key() -> None:
    camera = MockCamera()
    camera.route("PATCH", f"{ROOT}/sources/s1/srtpKey", lambda _: httpx.Response(500, text=f"failed to set {SENTINEL}"))
    with camera.device() as dev, pytest.raises(DeviceError) as caught:
        dev.apis.audio_multicast_ctrl.set_source_srtp_key("s1", srtp_key=SENTINEL)
    _clean(caught.value)


# -- CGI text errors, SOAP faults, 401 -------------------------------------------------------------------------------------

CGI_TEXTS = [f"Error: bad {SENTINEL}", f"# Error: bad {SENTINEL}", f"<!-- bad {SENTINEL} -->", f"Error:\nbad {SENTINEL}"]


@pytest.mark.parametrize("text", CGI_TEXTS)
def test_cgi_text_errors_of_a_masked_operation_leak_nothing(text: str) -> None:
    op = Operation(_info(Family.CGI), "get", CgiBinding("/x.cgi", reply=Text()), result=Secret)
    error = _invoke(op, httpx.Response(200, text=text))
    assert isinstance(error, ApiError)
    _clean(error)


def test_cgi_text_errors_of_a_non_masked_operation_keep_the_message_redacted() -> None:
    op = Operation(_info(Family.CGI), "get", CgiBinding("/x.cgi", reply=Text()), result=Plain)
    error = _invoke(op, httpx.Response(200, text="Error: bad password=hunter2 at https://u:pw@h/x"))
    assert "bad" in str(error) and "hunter2" not in str(error) and "pw@" not in str(error)


def test_a_soap_fault_of_a_masked_operation_leaks_nothing() -> None:
    op = Operation(_info(Family.SOAP), "act", SoapBinding("a", "Act", "urn:x"), result=None, params=SendsKey)
    body = (
        '<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope"><env:Body><env:Fault><env:Code><env:Value>env:Sender</env:Value>'
        f'<env:Subcode><env:Value>7</env:Value></env:Subcode></env:Code><env:Reason><env:Text xml:lang="en">bad {SENTINEL}</env:Text>'
        "</env:Reason></env:Fault></env:Body></env:Envelope>"
    )
    error = _invoke(op, httpx.Response(500, text=body), key=SENTINEL)
    _clean(error)


def test_a_401_on_a_masked_operation_keeps_the_category_without_the_text() -> None:
    op = Operation(_info(Family.CGI), "get", object(), result=Secret)
    error = api_error(op, 7, f"denied {SENTINEL}", http_status=401, details=None)
    assert isinstance(error, AuthError)
    _clean(error)
    forbidden = api_error(op, 7, f"denied {SENTINEL}", http_status=403, details=None)
    assert isinstance(forbidden, AccessDenied)
    _clean(forbidden)


def test_the_helper_itself() -> None:
    secret_op = Operation(_info(Family.CGI), "get", object(), result=Secret)
    plain_op = Operation(_info(Family.CGI), "get", object(), result=Plain)
    assert "omitted" in error_text(secret_op, f"x {SENTINEL}") and SENTINEL not in error_text(secret_op, SENTINEL)
    assert "password" in error_text(plain_op, "password=hunter2") and "hunter2" not in error_text(plain_op, "password=hunter2")
