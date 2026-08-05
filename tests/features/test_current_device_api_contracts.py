"""Contract tests for the current device-management JSON APIs."""

import pytest

from src.ax_devil_device_api.features.device_info import (
    DeviceInfoClient,
    get_device_info_from_params,
)
from src.ax_devil_device_api.features.network import NetworkClient
from src.ax_devil_device_api.features.systemready import SystemReadyClient
from src.ax_devil_device_api.utils.errors import FeatureError


class FakeResponse:
    """Small response double exposing the requests.Response surface used here."""

    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class RecordingDevice:
    """Feature transport double that records exact endpoint calls."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, endpoint, **kwargs):
        self.calls.append((endpoint.method, endpoint.path, kwargs))
        return self.responses.pop(0)

    def request_no_auth(self, endpoint, **kwargs):
        self.calls.append(("no-auth", endpoint.method, endpoint.path, kwargs))
        return self.responses.pop(0)


def test_basic_device_info_maps_official_properties_to_public_fields():
    params = {
        "Version": "12.7.11",
        "BuildDate": "Aug 04 2026 12:00",
        "Brand": "AXIS",
        "ProdShortName": "AXIS Q3505 Mk II",
        "ProdNbr": "Q3505 Mk II",
        "ProdType": "Network Camera",
        "SerialNumber": "ACCC8EAF8C30",
        "HardwareID": "75E.1",
    }

    assert get_device_info_from_params(params) == {
        "model": "AXIS Q3505 Mk II",
        "product_type": "Network Camera",
        "product_number": "Q3505 Mk II",
        "serial_number": "ACCC8EAF8C30",
        "hardware_id": "75E.1",
        "firmware_version": "12.7.11",
        "build_date": "Aug 04 2026 12:00",
        "ptz_support": [],
        "analytics_support": False,
        "metadata_support": False,
        "Onvif Replay Extention": False,
    }


def test_basic_device_info_discovers_version_and_validates_property_list():
    transport = RecordingDevice(
        [
            FakeResponse(
                {
                    "method": "getSupportedVersions",
                    "data": {"apiVersions": ["1.0", "1.2"]},
                }
            ),
            FakeResponse(
                {
                    "method": "getAllProperties",
                    "data": {"propertyList": {"Brand": "AXIS"}},
                }
            ),
        ]
    )

    info = DeviceInfoClient(transport).get_info_auth()

    assert info == {"Brand": "AXIS"}
    assert transport.calls[0][2]["json"] == {"method": "getSupportedVersions"}
    assert transport.calls[1][2]["json"] == {
        "apiVersion": "1.2",
        "method": "getAllProperties",
    }


@pytest.mark.parametrize("method", [None, "wrong"])
def test_basic_device_info_rejects_method_mismatch(method):
    response = {"data": {"apiVersions": ["1.0"]}}
    if method is not None:
        response["method"] = method

    with pytest.raises(FeatureError, match="unexpected method"):
        DeviceInfoClient(RecordingDevice([FakeResponse(response)])).get_info_auth()


def test_restart_uses_firmware_management_and_does_not_retry():
    transport = RecordingDevice(
        [
            FakeResponse(
                {"method": "getSupportedVersions", "data": {"apiVersions": ["1.0"]}}
            ),
            FakeResponse({"method": "reboot", "data": {}}),
        ]
    )

    assert DeviceInfoClient(transport).restart() is True
    assert transport.calls == [
        (
            "POST",
            "/axis-cgi/firmwaremanagement.cgi",
            {"json": {"method": "getSupportedVersions"}},
        ),
        (
            "POST",
            "/axis-cgi/firmwaremanagement.cgi",
            {"json": {"apiVersion": "1.0", "method": "reboot"}},
        ),
    ]


@pytest.mark.parametrize(
    "responses",
    [
        [FakeResponse({"data": {"apiVersions": ["1.0"]}})],
        [
            FakeResponse(
                {"method": "getSupportedVersions", "data": {"apiVersions": ["1.0"]}}
            ),
            FakeResponse({"method": "wrong", "data": {}}),
        ],
    ],
)
def test_firmware_management_rejects_method_mismatch(responses):
    with pytest.raises(
        FeatureError, match="valid reboot success envelope|unexpected method"
    ):
        DeviceInfoClient(RecordingDevice(responses)).restart()


def test_restart_does_not_send_reboot_after_version_discovery_failure():
    transport = RecordingDevice(
        [FakeResponse({"error": {"code": 417, "message": "Unsupported API version"}})]
    )

    with pytest.raises(FeatureError) as error:
        DeviceInfoClient(transport).restart()

    assert error.value.code == "api_error"
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    "success_payload",
    [
        {"data": {}},
        {"method": "wrong", "data": {}},
        {"method": "reboot", "data": []},
    ],
)
def test_restart_requires_exact_success_envelope(success_payload):
    transport = RecordingDevice(
        [
            FakeResponse(
                {"method": "getSupportedVersions", "data": {"apiVersions": ["1.0"]}}
            ),
            FakeResponse(success_payload),
        ]
    )

    with pytest.raises(FeatureError, match="valid reboot success envelope"):
        DeviceInfoClient(transport).restart()

    assert len(transport.calls) == 2


def test_systemready_rejects_missing_data_member():
    transport = RecordingDevice([FakeResponse({"method": "systemready"})])

    with pytest.raises(FeatureError, match="no data object"):
        SystemReadyClient(transport)._request_no_auth_json(
            {"method": "systemready"}, "systemready"
        )


@pytest.mark.parametrize("method", [None, "wrong"])
def test_network_settings_rejects_version_method_mismatch(method):
    response = {"data": {"supportedVersions": ["1.0"]}}
    if method is not None:
        response["method"] = method

    with pytest.raises(FeatureError, match="unexpected method"):
        NetworkClient(RecordingDevice([FakeResponse(response)])).get_network_info()


def test_network_settings_rejects_operation_method_mismatch():
    transport = RecordingDevice(
        [
            FakeResponse(
                {
                    "method": "getSupportedVersions",
                    "data": {"supportedVersions": ["1.0"]},
                }
            ),
            FakeResponse({"method": "wrong", "data": {}}),
        ]
    )

    with pytest.raises(FeatureError, match="unexpected method"):
        NetworkClient(transport).get_network_info()


@pytest.mark.parametrize("method", [None, "wrong"])
def test_systemready_rejects_readiness_method_mismatch(method):
    response = {"data": {"apiVersions": ["1.0"]}}
    if method is not None:
        response["method"] = method

    with pytest.raises(FeatureError, match="unexpected method"):
        SystemReadyClient(RecordingDevice([FakeResponse(response)])).systemready()


@pytest.mark.parametrize("method", [None, "wrong"])
def test_systemready_rejects_supported_versions_method_mismatch(method):
    response = {"data": {"apiVersions": ["1.0"]}}
    if method is not None:
        response["method"] = method

    with pytest.raises(FeatureError, match="unexpected method"):
        SystemReadyClient(
            RecordingDevice([FakeResponse(response)])
        ).get_supported_versions()


def test_network_info_uses_network_settings_api_and_advertised_version():
    transport = RecordingDevice(
        [
            FakeResponse(
                {
                    "method": "getSupportedVersions",
                    "data": {"supportedVersions": ["1.0", "3.1"]},
                }
            ),
            FakeResponse(
                {"method": "getNetworkInfo", "data": {"system": {}, "devices": []}}
            ),
        ]
    )

    info = NetworkClient(transport).get_network_info()

    assert info == {"system": {}, "devices": []}
    assert transport.calls[1][2]["json"] == {
        "apiVersion": "3.1",
        "method": "getNetworkInfo",
    }


@pytest.mark.parametrize(
    "client_method, responses",
    [
        ("get_info_auth", [FakeResponse(ValueError("bad json"))]),
        ("restart", [FakeResponse({"data": {"apiVersions": []}})]),
    ],
)
def test_device_api_normalizes_malformed_and_unsupported_responses(
    client_method, responses
):
    transport = RecordingDevice(responses)

    with pytest.raises(FeatureError) as error:
        getattr(DeviceInfoClient(transport), client_method)()

    assert error.value.code in {"invalid_response", "unsupported_version"}


def test_health_is_true_only_for_systemready_yes():
    transport = RecordingDevice(
        [
            FakeResponse(
                {
                    "method": "getSupportedVersions",
                    "data": {"apiVersions": ["1.0", "1.2"]},
                }
            ),
            FakeResponse({"method": "systemready", "data": {"systemready": "no"}}),
        ]
    )

    assert DeviceInfoClient(transport).check_health() is False
    assert transport.calls[0][0:3] == ("no-auth", "POST", "/axis-cgi/systemready.cgi")
    assert transport.calls[1][3]["json"] == {
        "apiVersion": "1.2",
        "method": "systemready",
        "params": {"timeout": 20},
    }


def test_systemready_negotiates_version_before_readiness_request():
    transport = RecordingDevice(
        [
            FakeResponse(
                {
                    "method": "getSupportedVersions",
                    "data": {"apiVersions": ["1.0", "1.3"]},
                }
            ),
            FakeResponse({"method": "systemready", "data": {"systemready": "yes"}}),
        ]
    )

    assert SystemReadyClient(transport).systemready() == {"systemready": "yes"}
    assert transport.calls == [
        (
            "no-auth",
            "POST",
            "/axis-cgi/systemready.cgi",
            {
                "json": {"method": "getSupportedVersions"},
                "headers": SystemReadyClient.JSON_HEADERS,
            },
        ),
        (
            "no-auth",
            "POST",
            "/axis-cgi/systemready.cgi",
            {
                "json": {
                    "apiVersion": "1.3",
                    "method": "systemready",
                    "params": {"timeout": 20},
                },
                "headers": SystemReadyClient.JSON_HEADERS,
            },
        ),
    ]


@pytest.mark.parametrize("versions", [[], ["1"], ["one.two"]])
def test_systemready_rejects_empty_or_malformed_versions(versions):
    transport = RecordingDevice(
        [
            FakeResponse(
                {"method": "getSupportedVersions", "data": {"apiVersions": versions}}
            )
        ]
    )

    with pytest.raises(FeatureError, match="valid API versions|malformed API versions"):
        SystemReadyClient(transport).systemready()


@pytest.mark.parametrize(
    "client, operation",
    [
        (DeviceInfoClient, "restart"),
        (NetworkClient, "get_network_info"),
        (SystemReadyClient, "systemready"),
    ],
)
def test_feature_errors_preserve_nested_axis_error_details(client, operation):
    axis_error = {"code": 123, "message": "bad request", "details": {"field": "value"}}
    transport = RecordingDevice([FakeResponse({"error": axis_error})])

    with pytest.raises(FeatureError) as error:
        getattr(client(transport), operation)()

    assert error.value.code == "api_error"
    assert error.value.message == "bad request"
    assert error.value.details == axis_error
