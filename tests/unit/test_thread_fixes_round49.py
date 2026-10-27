"""HTTP error statuses never put a secret-bearing body into the exception (message, repr, details, traceback)."""

from __future__ import annotations

import ast
import traceback

import httpx
import pytest
from test_error_body_guard import _reads_body

from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation, redact_text
from ax_devil_device_api._protocols.cgi import CgiBinding, Text
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import AccessDenied, ApiError, DeviceError, HttpError, Unavailable
from ax_devil_device_api.testing import MockCamera

SECRET = "TOPSECRET-srtp-key-0123456789"
PATH = "/config/rest/audio-multicast-ctrl/v1beta/sources/s1"
BODY = f'{{"error":"backend unavailable","srtpKey":"{SECRET}"}}'


def _clean(error: BaseException) -> None:
    assert SECRET not in str(error) and SECRET not in repr(error)
    assert SECRET not in "".join(traceback.format_exception(error))
    assert SECRET not in repr(getattr(error, "details", None)) and SECRET not in repr(getattr(error, "body_excerpt", ""))


def _camera(status: int) -> MockCamera:
    camera = MockCamera()
    camera.route("GET", PATH, lambda _: httpx.Response(status, text=BODY, headers={"content-type": "application/json"}))
    return camera


@pytest.mark.parametrize(("status", "kind"), [(503, Unavailable), (403, AccessDenied), (500, HttpError), (502, HttpError), (409, HttpError)])
def test_sync_http_errors_of_a_secret_returning_operation_leak_nothing(status: int, kind: type) -> None:
    with _camera(status).device() as dev, pytest.raises(DeviceError) as caught:
        dev.apis.audio_multicast_ctrl.get_source("s1")
    assert isinstance(caught.value, kind)  # the exception category is unchanged
    _clean(caught.value)
    assert "body omitted" in str(caught.value) and str(status) in str(caught.value)


@pytest.mark.anyio
@pytest.mark.parametrize("status", [503, 403, 500])
async def test_async_http_errors_of_a_secret_returning_operation_leak_nothing(status: int) -> None:
    async with _camera(status).async_device() as dev:
        with pytest.raises(DeviceError) as caught:
            await dev.apis.audio_multicast_ctrl.get_source("s1")
    _clean(caught.value)


class Plain(Model):
    value: int


def test_a_non_masked_operation_still_gets_a_redacted_excerpt() -> None:
    op = Operation(ApiInfo(id="t", name="T", family=Family.CGI), "get", CgiBinding("/x.cgi", reply=Text()), result=Plain)
    body = '{"error":"backend unavailable","password":"hunter2","url":"https://u:pw@h/x"}'
    for status in (503, 403, 500):
        transport = httpx.MockTransport(lambda request, status=status: httpx.Response(status, text=body))
        with Device("cam", credentials=("u", "p"), transport=transport) as dev, pytest.raises(DeviceError) as caught:
            dev.invoke(op)
        message = str(caught.value)
        assert "backend unavailable" in message  # diagnosable
        assert "hunter2" not in message and "pw@" not in message  # and redacted


def test_documented_error_details_of_a_secret_operation_are_omitted() -> None:
    camera = MockCamera()
    camera.rest("GET", PATH, error=(7, f"bad {SECRET}"), status=400)  # an envelope error object
    with camera.device() as dev, pytest.raises(ApiError) as caught:
        dev.apis.audio_multicast_ctrl.get_source("s1")
    assert SECRET not in repr(caught.value.details)


def test_the_generic_redactor_is_bounded_and_redacts() -> None:
    shown = redact_text("password=hunter2 " + "x" * 500)
    assert "hunter2" not in shown and len(shown) <= 201


def test_the_guard_flags_a_bypass() -> None:
    assert _reads_body(ast.parse("HttpError(status, response.excerpt())", mode="eval").body.args[1])  # type: ignore[attr-defined]
    assert not _reads_body(ast.parse("body_excerpt(op, response.safe_text)", mode="eval").body)
