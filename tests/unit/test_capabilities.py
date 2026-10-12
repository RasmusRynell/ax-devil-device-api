"""Support decisions, probe caching, identity, and cache invalidation."""

from __future__ import annotations

import httpx
import pytest

from ax_devil_device_api import Support
from ax_devil_device_api._protocols.base import ApiVersion
from ax_devil_device_api._protocols.state import DeviceState
from ax_devil_device_api.apis.analytics_mqtt import AnalyticsMqttApi
from ax_devil_device_api.apis.mqtt_client import AsyncMqttClientApi, MqttClientApi
from ax_devil_device_api.apis.parameter_management import ParameterManagementApi
from ax_devil_device_api.errors import ApiError
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"
DISCOVERY = "/axis-cgi/apidiscovery.cgi"
PARAM = "/axis-cgi/param.cgi"
VERSIONS_KEY = f"jsonrpc:{MQTT}"


def count(camera: MockCamera, path: str) -> int:
    return sum(1 for r in camera.requests if r.path == path)


# -- supports -----------------------------------------------------------------


def test_supports_yes_via_classic_discovery() -> None:
    camera = MockCamera()
    camera.api_list({"mqtt-client": "1.3"})

    with camera.device() as dev:
        result = dev.supports(MqttClientApi)

    assert result.status is Support.YES and bool(result)
    assert "mqtt-client 1.3" in result.reason
    assert result.errors == ()


def test_supports_accepts_api_instance() -> None:
    camera = MockCamera()
    camera.api_list({"mqtt-client": "1.0"})

    with camera.device() as dev:
        assert dev.supports(dev.apis.mqtt_client)


def test_supports_no_when_probe_succeeds_and_api_not_listed() -> None:
    camera = MockCamera()
    camera.api_list({"something-else": "1.0"})

    with camera.device() as dev:
        result = dev.supports(MqttClientApi)

    assert result.status is Support.NO and not result
    assert result.errors == ()


def test_supports_no_when_device_lists_other_major_version() -> None:
    camera = MockCamera()
    camera.api_list({"mqtt-client": "2.0"})

    with camera.device() as dev:
        result = dev.supports(MqttClientApi)

    assert result.status is Support.NO
    assert "2.0" in result.reason and "1.x" in result.reason


def test_supports_unknown_when_probe_fails_and_reports_errors() -> None:
    camera = MockCamera()  # apidiscovery.cgi answers 404

    with camera.device() as dev:
        result = dev.supports(MqttClientApi)

    assert result.status is Support.UNKNOWN and not result
    assert len(result.errors) == 1 and "classic API discovery failed" in result.errors[0]
    assert "NotSupported" in result.errors[0]


def test_failed_probe_is_retried_while_successful_probe_is_cached() -> None:
    camera = MockCamera()
    camera.dca_apis({"analytics-mqtt": ["v1"]})

    with camera.device() as dev:
        first = dev.capabilities()
        assert first.dca_apis == {"analytics-mqtt": frozenset({"v1"})}
        assert set(first.errors) == {"classic_apis", "properties"}
        assert first.classic_apis is None and first.properties is None

        camera.api_list({"mqtt-client": "1.3"})
        second = dev.capabilities()

    assert second.classic_apis == {"mqtt-client": "1.3"}
    assert set(second.errors) == {"properties"}
    assert count(camera, "/config/discover") == 1
    assert count(camera, DISCOVERY) == 2
    assert count(camera, PARAM) == 2


def test_successful_probes_are_cached_across_supports_calls() -> None:
    camera = MockCamera()
    camera.api_list({"mqtt-client": "1.0"})
    camera.dca_apis({"analytics-mqtt": ["v1"]})
    camera.cgi(PARAM, text="root.Properties.API.HTTP.Version=3\n")

    with camera.device() as dev:
        results = [dev.supports(c) for c in (MqttClientApi, AnalyticsMqttApi, ParameterManagementApi)]
        dev.supports(MqttClientApi)

    assert [r.status for r in results] == [Support.YES] * 3
    assert count(camera, DISCOVERY) == count(camera, "/config/discover") == count(camera, PARAM) == 1


def test_param_discovery_matches_property_value() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="root.Properties.API.HTTP.Version=3\nroot.Properties.API.Metadata.Metadata=yes\n",
               match={"action": "list"})

    with camera.device() as dev:
        assert dev.supports(ParameterManagementApi).status is Support.YES
        assert dev.capabilities().properties == {"Properties.API.HTTP.Version": "3", "Properties.API.Metadata.Metadata": "yes"}

    [listing] = [r for r in camera.requests if r.path == PARAM]
    assert listing.query == {"action": "list", "group": "Properties.API"}


def test_param_discovery_value_mismatch_is_no() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="root.Properties.API.HTTP.Version=2\n")

    with camera.device() as dev:
        assert dev.supports(ParameterManagementApi).status is Support.NO


def test_dca_discovery_yes_and_no() -> None:
    camera = MockCamera()
    camera.dca_apis({"analytics-mqtt": ["v1"]})
    with camera.device() as dev:
        assert dev.supports(AnalyticsMqttApi).status is Support.YES

    camera = MockCamera()
    camera.dca_apis({"analytics-mqtt": ["v2beta"], "other": ["v1"]})
    with camera.device() as dev:
        result = dev.supports(AnalyticsMqttApi)
    assert result.status is Support.NO


def test_dca_discovery_unknown_when_endpoint_missing() -> None:
    camera = MockCamera()
    camera.rest("GET", "/config/discover", status=503)
    with camera.device() as dev:
        result = dev.supports(AnalyticsMqttApi)

    assert result.status is Support.UNKNOWN
    assert "Device Configuration discovery failed" in result.errors[0] and "HttpUnavailable" in result.errors[0]


@pytest.mark.anyio
async def test_async_capabilities_and_supports() -> None:
    camera = MockCamera()
    camera.api_list({"mqtt-client": "1.3"})
    camera.dca_apis({"analytics-mqtt": ["v1"]})

    async with camera.async_device() as dev:
        caps = await dev.capabilities()
        assert caps.classic_apis == {"mqtt-client": "1.3"}
        assert set(caps.errors) == {"properties"}
        assert (await dev.supports(AsyncMqttClientApi)).status is Support.YES
        assert (await dev.supports(dev.apis.mqtt_client)).status is Support.YES

    assert count(camera, DISCOVERY) == 1


@pytest.mark.anyio
async def test_async_supports_unknown_then_retried() -> None:
    camera = MockCamera()
    async with camera.async_device() as dev:
        assert (await dev.supports(AsyncMqttClientApi)).status is Support.UNKNOWN
        camera.api_list({"mqtt-client": "1.0"})
        assert (await dev.supports(AsyncMqttClientApi)).status is Support.YES


# -- identity -----------------------------------------------------------------


def test_identity_is_cached() -> None:
    camera = MockCamera()
    camera.identity(model="AXIS Q1656", firmware="11.9.0", serial="ACCC8E")

    with camera.device() as dev:
        first = dev.identity()
        second = dev.identity()

    assert first is second
    assert (first.model, first.firmware_version, first.serial_number) == ("AXIS Q1656", "11.9.0", "ACCC8E")
    assert len(camera.calls("getAllProperties")) == 1


def test_identity_refresh_asks_device_again() -> None:
    camera = MockCamera()
    camera.identity(firmware="11.9.0")
    with camera.device() as dev:
        dev.identity()
        dev.identity(refresh=True)

    assert len(camera.calls("getAllProperties")) == 2


def test_identity_refresh_with_changed_firmware_clears_cached_facts() -> None:
    camera = MockCamera()
    camera.identity(firmware="11.9.0")
    camera.jsonrpc(MQTT, "activateClient")
    camera.api_list({"mqtt-client": "1.0"})

    with camera.device() as dev:
        dev.identity()
        dev.apis.mqtt_client.activate_client()
        dev.capabilities()
        assert dev._state.advertised_versions(VERSIONS_KEY) is not None
        assert dev._state.get("classic_apis") is not None

        camera.identity(firmware="12.1.0")
        assert dev.identity(refresh=True).firmware_version == "12.1.0"

        assert dev._state.advertised_versions(VERSIONS_KEY) is None
        assert dev._state.get("classic_apis") is None
        assert dev.identity().firmware_version == "12.1.0"  # the new identity itself is kept
        dev.apis.mqtt_client.activate_client()

    assert len(camera.calls("getSupportedVersions")) == 3  # basic info, mqtt, then mqtt again


def test_identity_refresh_with_same_firmware_keeps_cached_facts() -> None:
    camera = MockCamera()
    camera.identity(firmware="11.9.0")
    camera.jsonrpc(MQTT, "activateClient")

    with camera.device() as dev:
        dev.identity()
        dev.apis.mqtt_client.activate_client()
        dev.identity(refresh=True)
        assert dev._state.advertised_versions(VERSIONS_KEY) is not None


def test_refresh_forgets_identity_and_facts() -> None:
    camera = MockCamera()
    camera.identity()
    camera.api_list({"mqtt-client": "1.0"})
    with camera.device() as dev:
        dev.identity()
        dev.capabilities()
        dev.refresh()
        assert dev._state.get("identity") is None and dev._state.get("classic_apis") is None
        dev.identity()

    assert len(camera.calls("getAllProperties")) == 2


@pytest.mark.anyio
async def test_async_identity_cached_and_firmware_change_clears() -> None:
    camera = MockCamera()
    camera.identity(firmware="11.9.0")
    camera.jsonrpc(MQTT, "activateClient")
    async with camera.async_device() as dev:
        assert (await dev.identity()) is (await dev.identity())
        await dev.apis.mqtt_client.activate_client()
        camera.identity(firmware="12.0.0")
        await dev.identity(refresh=True)
        assert dev._state.advertised_versions(VERSIONS_KEY) is None

    assert len(camera.calls("getAllProperties")) == 2


# -- state generation ---------------------------------------------------------


def test_value_computed_before_clear_is_not_stored_after() -> None:
    state = DeviceState()
    token = state.token("identity")
    version_token = state.versions_token("jsonrpc:/x")

    state.clear()

    assert state.set("identity", "stale", token) is False
    assert state.get("identity") is None
    state.set_advertised_versions("jsonrpc:/x", (ApiVersion(1, 0),), version_token)
    assert state.advertised_versions("jsonrpc:/x") is None


def test_value_computed_in_current_generation_is_stored() -> None:
    state = DeviceState()
    state.clear()
    token = state.token("k")
    version_token = state.versions_token("e")

    assert state.set("k", 1, token) is True
    state.set_advertised_versions("e", (ApiVersion(1, 0),), version_token)

    assert state.get("k") == 1
    assert state.advertised_versions("e") == (ApiVersion(1, 0),)


def test_clear_drops_everything_and_invalidates_outstanding_tokens() -> None:
    state = DeviceState()
    state.set("k", 1, state.token("k"))
    state.set_advertised_versions("e", (ApiVersion(1, 0),), state.versions_token("e"))
    outstanding = state.token("k")

    state.clear()

    assert state.get("k") is None and state.advertised_versions("e") is None
    assert state.set("k", 2, outstanding) is False
    assert state.get("k") is None


def test_forget_advertised_versions_drops_only_that_endpoint() -> None:
    state = DeviceState()
    for endpoint in ("a", "b"):
        state.set_advertised_versions(endpoint, (ApiVersion(1, 0),), state.versions_token(endpoint))

    state.forget_advertised_versions("a")

    assert state.advertised_versions("a") is None and state.advertised_versions("b") is not None


def test_refresh_during_probe_discards_the_probe_result() -> None:
    camera = MockCamera()
    with camera.device() as dev:
        def discovery(request: httpx.Request) -> httpx.Response:
            dev.refresh()  # the cache is cleared while this probe is in flight
            return httpx.Response(200, json={"method": "getApiList", "data": {"apiList": [{"id": "mqtt-client", "version": "1.0"}]}})

        camera.route("POST", DISCOVERY, discovery)
        dev.capabilities()
        assert dev._state.get("classic_apis") is None  # stale result was not stored

        camera.api_list({"mqtt-client": "1.0"})
        assert dev.capabilities().classic_apis == {"mqtt-client": "1.0"}


# -- JSON-RPC version errors --------------------------------------------------


def test_jsonrpc_error_2100_forgets_cached_versions_and_renegotiates() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(2100, "version not supported"))

    with camera.device() as dev:
        with pytest.raises(ApiError) as caught:
            dev.apis.mqtt_client.activate_client()
        assert caught.value.kind == "unsupported"
        assert dev._state.advertised_versions(VERSIONS_KEY) is None

        camera.jsonrpc(MQTT, "activateClient")
        dev.apis.mqtt_client.activate_client()

    assert len(camera.calls("getSupportedVersions")) == 2


def test_other_api_errors_keep_cached_versions() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(2104, "bad"))

    with camera.device() as dev, pytest.raises(ApiError):
        dev.apis.mqtt_client.activate_client()
    assert len(camera.calls("getSupportedVersions")) == 1


def test_endpoint_disappearing_forgets_cached_versions() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient")
    camera.jsonrpc(MQTT, "deactivateClient")

    with camera.device() as dev:
        dev.apis.mqtt_client.activate_client()
        assert dev._state.advertised_versions(VERSIONS_KEY) is not None
        camera.route("POST", MQTT, lambda request: httpx.Response(404))
        with pytest.raises(Exception, match="404"):
            dev.apis.mqtt_client.deactivate_client()
        assert dev._state.advertised_versions(VERSIONS_KEY) is None


# -- base_path ----------------------------------------------------------------


def test_base_path_prefixes_every_request() -> None:
    prefix = "/vms/cam7"
    camera = MockCamera()
    camera.jsonrpc(prefix + MQTT, "activateClient")
    camera.api_list({"mqtt-client": "1.0"})  # registered unprefixed: must not be hit
    camera.cgi(prefix + PARAM, text="root.Properties.API.HTTP.Version=3\n")
    camera.rest("GET", prefix + "/config/rest/analytics-mqtt/v1/publishers", data=[])

    with camera.device(base_path=prefix) as dev:
        dev.apis.mqtt_client.activate_client()
        dev.apis.parameter_management.list()
        dev.apis.analytics_mqtt.list_publishers()
        assert dev.supports(MqttClientApi).status is Support.UNKNOWN  # prefixed discovery paths are unregistered

    assert camera.requests and all(r.path.startswith(prefix + "/") for r in camera.requests)
