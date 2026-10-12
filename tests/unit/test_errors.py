"""Error classification: categories, kinds, and descriptions."""

from __future__ import annotations

import pytest

from ax_devil_device_api.errors import (
    AccessDenied,
    ApiAccessDenied,
    ApiError,
    AuthError,
    HttpAccessDenied,
    HttpError,
    HttpUnavailable,
    NotSupported,
    Unavailable,
)
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"
PARAM = "/axis-cgi/param.cgi"


def test_http_403_is_http_access_denied() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="Forbidden", status=403)

    with camera.device() as dev, pytest.raises(HttpAccessDenied) as caught:
        dev.apis.parameter_management.list()

    assert isinstance(caught.value, AccessDenied) and isinstance(caught.value, HttpError)
    assert caught.value.status == 403
    assert (caught.value.api, caught.value.operation) == ("parameter-management", "list")
    assert "viewer" in str(caught.value)


def test_http_503_is_http_unavailable() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="starting", status=503)

    with camera.device() as dev, pytest.raises(HttpUnavailable) as caught:
        dev.apis.parameter_management.list()

    assert isinstance(caught.value, Unavailable) and isinstance(caught.value, HttpError)
    assert caught.value.status == 503


def test_http_401_without_credentials_is_auth_error() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="Unauthorized", status=401)

    with camera.device(credentials=None) as dev, pytest.raises(AuthError, match="no usable credentials"):
        dev.apis.parameter_management.list()


def test_http_404_is_not_supported() -> None:
    camera = MockCamera()

    with camera.device() as dev, pytest.raises(NotSupported, match="404"):
        dev.apis.parameter_management.list()


def test_http_500_is_plain_http_error() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="boom", status=500)

    with camera.device() as dev, pytest.raises(HttpError) as caught:
        dev.apis.parameter_management.list()

    assert type(caught.value) is HttpError


def test_jsonrpc_2105_is_api_access_denied() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(2105, "not allowed"))

    with camera.device() as dev, pytest.raises(ApiAccessDenied) as caught:
        dev.apis.mqtt_client.activate_client()

    error = caught.value
    assert isinstance(error, AccessDenied) and isinstance(error, ApiError)
    assert (error.code, error.kind, error.message) == (2105, "access_denied", "not allowed")
    assert error.description == "Authorization failure"


@pytest.mark.parametrize(
    ("code", "kind", "description"),
    [
        (2104, "invalid_argument", "Invalid parameter value specified"),
        (2102, "unsupported", "Method not supported"),
        (1100, "internal", "Internal error"),
    ],
)
def test_api_error_kind_and_description_come_from_documented_codes(code: int, kind: str, description: str) -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(code, "device says no"))

    with camera.device() as dev, pytest.raises(ApiError) as caught:
        dev.apis.mqtt_client.activate_client()

    assert type(caught.value) is ApiError
    assert (caught.value.kind, caught.value.description) == (kind, description)
    assert caught.value.http_status == 200
    assert str(code) in str(caught.value) and description in str(caught.value)


def test_undocumented_api_error_code_has_no_kind() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(9999, "weird"))

    with camera.device() as dev, pytest.raises(ApiError) as caught:
        dev.apis.mqtt_client.activate_client()

    assert (caught.value.kind, caught.value.description, caught.value.code) == (None, None, 9999)


def test_undocumented_code_with_http_403_is_access_denied() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(9999, "weird"), status=403)

    with camera.device() as dev, pytest.raises(ApiAccessDenied) as caught:
        dev.apis.mqtt_client.activate_client()

    assert caught.value.kind == "access_denied" and caught.value.http_status == 403


def test_dca_error_envelope_is_api_error() -> None:
    camera = MockCamera()
    camera.rest("GET", "/config/rest/analytics-mqtt/v1/publishers", error=(2002, "bad"), status=400)

    with camera.device() as dev, pytest.raises(ApiError) as caught:
        dev.apis.analytics_mqtt.list_publishers()

    assert (caught.value.code, caught.value.http_status) == (2002, 400)


def test_cgi_text_error_is_api_error() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="# Error: Request failed\n")

    with camera.device() as dev, pytest.raises(ApiError, match="Error: Request failed"):
        dev.apis.parameter_management.list()


@pytest.mark.anyio
async def test_async_errors_are_classified_the_same() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(2105, "no"))
    camera.cgi(PARAM, status=503)

    async with camera.async_device() as dev:
        with pytest.raises(ApiAccessDenied):
            await dev.apis.mqtt_client.activate_client()
        with pytest.raises(HttpUnavailable):
            await dev.apis.parameter_management.list()
