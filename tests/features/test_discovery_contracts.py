"""Deterministic contracts for both Axis discovery families."""

from unittest.mock import Mock

import pytest

from src.ax_devil_device_api.clis.api_discovery_cli import show_api_info
from src.ax_devil_device_api.features.api_discovery import (
    ClassicAPIDiscoveryClient,
    DiscoveredAPI,
    DiscoveryClient,
)
from src.ax_devil_device_api.utils.errors import FeatureError


def response(payload, status=200):
    result = Mock(status_code=status)
    result.json.return_value = payload
    return result


def test_classic_get_api_list_contract():
    device = Mock()
    device.request_no_auth.return_value = response(
        {
            "apiVersion": "1.0",
            "context": "x",
            "method": "getApiList",
            "data": {"apiList": []},
        }
    )
    result = ClassicAPIDiscoveryClient(device).get_api_list(
        api_id="foo", version="2.0", context="x"
    )
    assert result.apis == ()
    endpoint, kwargs = (
        device.request_no_auth.call_args.args[0],
        device.request_no_auth.call_args.kwargs,
    )
    assert (endpoint.method, endpoint.path) == ("POST", "/axis-cgi/apidiscovery.cgi")
    assert kwargs["json"] == {
        "apiVersion": "1.0",
        "context": "x",
        "method": "getApiList",
        "params": {"id": "foo", "version": "2.0"},
    }


def test_classic_discovery_is_anonymous_by_default():
    device = Mock()
    device.request_no_auth.return_value = response(
        {
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        }
    )
    assert ClassicAPIDiscoveryClient(device).get_supported_versions() == ("1.0",)
    device.request_no_auth.assert_called_once()
    device.request.assert_not_called()
    assert device.request_no_auth.call_args.kwargs["json"] == {
        "method": "getSupportedVersions"
    }


def test_classic_discovery_uses_auth_only_for_documented_challenge_response():
    device = Mock()
    anonymous = response({}, status=401)
    anonymous.headers = {"WWW-Authenticate": 'Digest realm="Device API"'}
    authenticated = response(
        {
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        }
    )
    device.request_no_auth.return_value = anonymous
    device.request_after_challenge.return_value = authenticated
    assert ClassicAPIDiscoveryClient(device).get_supported_versions() == ("1.0",)
    anonymous_endpoint = device.request_no_auth.call_args.args[0]
    assert (anonymous_endpoint.method, anonymous_endpoint.path) == (
        "POST",
        "/axis-cgi/apidiscovery.cgi",
    )
    assert device.request_no_auth.call_args.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "json": {"method": "getSupportedVersions"},
    }
    device.request_after_challenge.assert_called_once()
    authenticated_endpoint = device.request_after_challenge.call_args.args[0]
    assert (authenticated_endpoint.method, authenticated_endpoint.path) == (
        "POST",
        "/axis-cgi/apidiscovery.cgi",
    )
    assert device.request_after_challenge.call_args.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "json": {"method": "getSupportedVersions"},
    }


@pytest.mark.parametrize("status", ["released", "alpha", "beta", "deprecated"])
def test_classic_status_accepts_only_documented_values(status):
    device = Mock()
    device.request_no_auth.return_value = response(
        {
            "apiVersion": "1.0",
            "method": "getApiList",
            "data": {"apiList": [{"id": "foo", "version": "1.0", "status": status}]},
        }
    )
    assert ClassicAPIDiscoveryClient(device).get_api_list().apis[0].status == status


@pytest.mark.parametrize("status", ["Released", "preview", "unknown", ""])
def test_classic_status_rejects_undocumented_values(status):
    device = Mock()
    device.request_no_auth.return_value = response(
        {
            "apiVersion": "1.0",
            "method": "getApiList",
            "data": {"apiList": [{"id": "foo", "version": "1.0", "status": status}]},
        }
    )
    with pytest.raises(FeatureError, match="Invalid classic API status"):
        ClassicAPIDiscoveryClient(device).get_api_list()


@pytest.mark.parametrize(
    "header",
    [
        'NotBasic realm="Device API"',
        'Bearer realm="Device API", NotDigest realm="Other API"',
    ],
)
def test_classic_discovery_rejects_lookalike_auth_challenges(header):
    device = Mock()
    unauthorized = response({}, status=401)
    unauthorized.headers = {"WWW-Authenticate": header}
    device.request_no_auth.return_value = unauthorized

    with pytest.raises(FeatureError, match="HTTP 401"):
        ClassicAPIDiscoveryClient(device).get_supported_versions()
    device.request.assert_not_called()


def test_classic_discovery_handles_combined_supported_challenges():
    device = Mock()
    anonymous = response({}, status=401)
    anonymous.headers = {
        "WWW-Authenticate": 'Bearer realm="Other", Digest realm="Device API", Basic realm="Device API"'
    }
    authenticated = response(
        {
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        }
    )
    device.request_no_auth.return_value = anonymous
    device.request_after_challenge.return_value = authenticated

    assert ClassicAPIDiscoveryClient(device).get_supported_versions() == ("1.0",)
    device.request_after_challenge.assert_called_once()


def test_classic_discovery_does_not_retry_non_challenge_401():
    device = Mock()
    device.request_no_auth.return_value = response({}, status=401)

    with pytest.raises(FeatureError, match="HTTP 401"):
        ClassicAPIDiscoveryClient(device).get_supported_versions()
    device.request.assert_not_called()


def test_classic_discovery_retries_authenticated_request_once():
    device = Mock()
    anonymous = response({}, status=401)
    anonymous.headers = {"WWW-Authenticate": 'Basic realm="Device API"'}
    authenticated = response({}, status=401)
    device.request_no_auth.return_value = anonymous
    device.request_after_challenge.return_value = authenticated

    with pytest.raises(FeatureError, match="HTTP 401"):
        ClassicAPIDiscoveryClient(device).get_supported_versions()
    device.request_after_challenge.assert_called_once()
    endpoint = device.request_after_challenge.call_args.args[0]
    assert (endpoint.method, endpoint.path) == (
        "POST",
        "/axis-cgi/apidiscovery.cgi",
    )
    assert device.request_after_challenge.call_args.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "json": {"method": "getSupportedVersions"},
    }


@pytest.mark.parametrize("field", ["docLink", "name"])
def test_classic_optional_fields_must_be_strings(field):
    device = Mock()
    device.request_no_auth.return_value = response(
        {
            "apiVersion": "1.0",
            "method": "getApiList",
            "data": {
                "apiList": [
                    {"id": "foo", "version": "1.0", "status": "released", field: 1}
                ]
            },
        }
    )
    with pytest.raises(FeatureError):
        ClassicAPIDiscoveryClient(device).get_api_list()


def test_classic_application_error_is_normalized():
    device = Mock()
    device.request_no_auth.return_value = response(
        {"error": {"code": 42, "message": "bad request"}}
    )
    with pytest.raises(FeatureError, match="bad request"):
        ClassicAPIDiscoveryClient(device).get_api_list()


def test_device_configuration_route_and_semantic_selection():
    device = Mock()
    device.request.return_value = response(
        {
            "framework_version": "1.0.0",
            "apis": {
                "foo": {
                    "v1": {"state": "beta", "version": "1.0.0-beta.2"},
                    "v2": {"state": "released", "version": "1.0.0"},
                }
            },
        }
    )
    result = DiscoveryClient(device).discover()
    assert result.get_api("foo").version_string == "1.0.0"
    endpoint = device.request.call_args.args[0]
    assert (endpoint.method, endpoint.path) == ("GET", "/config/discover")


def test_device_configuration_http_error_is_normalized():
    device = Mock()
    device.request.return_value = response({}, status=404)
    with pytest.raises(FeatureError, match="HTTP 404"):
        DiscoveryClient(device).discover()


def test_device_configuration_http_error_preserves_official_error_object():
    device = Mock()
    error = {
        "code": "invalid_request",
        "message": "Request was not accepted",
        "details": {"field": "version"},
    }
    device.request.return_value = response(
        {"status": "error", "error": error}, status=400
    )

    with pytest.raises(FeatureError) as exc_info:
        DiscoveryClient(device).discover()

    assert exc_info.value.code == "invalid_request"
    assert exc_info.value.message == "Request was not accepted"
    assert exc_info.value.details == error


@pytest.mark.parametrize("payload", [ValueError("invalid json"), ["not an object"]])
def test_device_configuration_malformed_http_error_is_normalized(payload):
    device = Mock()
    failed_response = response(payload, status=500)
    if isinstance(payload, Exception):
        failed_response.json.side_effect = payload
    device.request.return_value = failed_response

    with pytest.raises(FeatureError, match="HTTP 500") as exc_info:
        DiscoveryClient(device).discover()

    assert exc_info.value.code == "discovery_failed"


def test_dca_malformed_nested_mapping_is_feature_error():
    device = Mock()
    device.request.return_value = response(
        {"framework_version": "1.0.0", "apis": {"foo": ["not-a-version-map"]}}
    )
    with pytest.raises(FeatureError):
        DiscoveryClient(device).discover()


def test_dca_latest_requires_released_version():
    device = Mock()
    device.request.return_value = response(
        {
            "framework_version": "1.0.0",
            "apis": {
                "foo": {
                    "v1": {"state": "alpha", "version": "2.0.0-alpha.1"},
                    "v2": {"state": "beta", "version": "9.0.0-beta.1"},
                }
            },
        }
    )
    collection = DiscoveryClient(device).discover()
    with pytest.raises(FeatureError, match="no released version"):
        collection.get_api("foo")


def test_dca_latest_selects_highest_released_semver():
    device = Mock()
    device.request.return_value = response(
        {
            "framework_version": "1.0.0",
            "apis": {
                "foo": {
                    "v1": {"state": "released", "version": "1.2.0"},
                    "v2": {"state": "released", "version": "2.0.0"},
                    "v3": {"state": "beta", "version": "9.0.0-beta.1"},
                }
            },
        }
    )
    assert DiscoveryClient(device).discover().get_api("foo").version_string == "2.0.0"


@pytest.mark.parametrize(
    ("state", "version"),
    [("released", "12.7.11"), ("alpha", "12.0.0-alpha.3"), ("beta", "12.0.0-beta.4")],
)
def test_dca_accepts_official_state_version_forms(state, version):
    api = DiscoveredAPI.from_discovery_data(
        "foo", "v1", {"state": state, "version": version}
    )
    assert (api.state, api.version_string) == (state, version)


@pytest.mark.parametrize(
    ("state", "version"),
    [
        ("released", "12.0.0-beta.1"),
        ("released", "12.0.0-alpha.1"),
        ("alpha", "12.1.0-alpha.1"),
        ("alpha", "12.0.0-beta.1"),
        ("beta", "12.1.0-beta.1"),
        ("beta", "12.0.0-alpha.1"),
        ("deprecated", "12.0.0"),
    ],
)
def test_dca_rejects_state_version_mismatches(state, version):
    with pytest.raises(
        FeatureError, match="invalid form|Invalid Device Configuration API state"
    ):
        DiscoveredAPI.from_discovery_data(
            "foo", "v1", {"state": state, "version": version}
        )


def test_dca_resource_caches_are_per_api_and_route_exactly():
    device = Mock()
    ui_response = response({}, status=200)
    ui_response.text = ""
    device.request.side_effect = [
        response(
            {
                "framework_version": "1.0.0",
                "apis": {
                    "foo": {
                        "v1": {
                            "state": "released",
                            "version": "1.0.0",
                            "model": "/model.json",
                            "rest_openapi": "/openapi.json",
                            "rest_ui": "/swagger-ui/",
                        },
                        "v2": {
                            "state": "released",
                            "version": "2.0.0",
                            "model": "/model.json",
                            "rest_openapi": "/openapi.json",
                            "rest_ui": "/swagger-ui/",
                        },
                    }
                },
            }
        ),
        response({"model": True}),
        response({"model": False}),
        response({"openapi": "3.0.0"}),
        ui_response,
    ]
    collection = DiscoveryClient(device).discover()
    api = collection.get_api("foo", "v1")
    other_api = collection.get_api("foo", "v2")
    assert api.get_model() == api.get_model() == {"model": True}
    assert other_api.get_model() == {"model": False}
    assert api.get_openapi_spec() == api.get_openapi_spec() == {"openapi": "3.0.0"}
    assert api.get_rest_ui() == ""
    calls = [call.args[0].path for call in device.request.call_args_list]
    assert calls == [
        "/config/discover",
        "/model.json",
        "/model.json",
        "/openapi.json",
        "/swagger-ui/",
    ]


def test_rest_ui_raw_uses_rest_ui_resource(capsys):
    api = Mock()
    api.name = "foo"
    api.version = "v1"
    api.state = "released"
    api.version_string = "1.0.0"
    api._urls = {"rest_ui": "/swagger-ui/"}
    api.rest_ui_url = "/swagger-ui/"
    api.get_rest_ui.return_value = "<html>swagger</html>"
    context = Mock(obj={"protocol": "https", "device_ip": "camera", "port": None})

    show_api_info(
        api,
        context,
        docs_md=False,
        docs_md_raw=False,
        docs_md_link=False,
        docs_html=False,
        docs_html_raw=False,
        docs_html_link=False,
        model=False,
        model_raw=False,
        model_link=False,
        rest_api=False,
        rest_api_raw=False,
        rest_api_link=False,
        rest_openapi=False,
        rest_openapi_raw=False,
        rest_openapi_link=False,
        rest_ui=False,
        rest_ui_raw=True,
        rest_ui_link=False,
    )

    assert "<html>swagger</html>" in capsys.readouterr().out
    api.get_rest_ui.assert_called_once()
    api.get_documentation_html.assert_not_called()


def test_discovery_link_requires_optional_url():
    api = Mock()
    api.name = "foo"
    api.version = "v1"
    api.state = "released"
    api.version_string = "1.0.0"
    api._urls = {"doc": None}
    context = Mock(obj={"protocol": "https", "device_ip": "camera", "port": None})

    with pytest.raises(FeatureError, match="No Markdown Documentation URL available"):
        show_api_info(
            api,
            context,
            docs_md=False,
            docs_md_raw=False,
            docs_md_link=True,
            docs_html=False,
            docs_html_raw=False,
            docs_html_link=False,
            model=False,
            model_raw=False,
            model_link=False,
            rest_api=False,
            rest_api_raw=False,
            rest_api_link=False,
            rest_openapi=False,
            rest_openapi_raw=False,
            rest_openapi_link=False,
            rest_ui=False,
            rest_ui_raw=False,
            rest_ui_link=False,
        )
