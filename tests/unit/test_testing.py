"""MockCamera itself: routing, recording, failures, and sync/async devices."""

from __future__ import annotations

import httpx
import pytest

from ax_devil_device_api.errors import ConnectionFailed, NotSupported
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"
STATUS = {"status": {"state": "active", "connectionStatus": "connected"}}


def get(camera: MockCamera, method: str, path: str, **kwargs) -> httpx.Response:
    with httpx.Client(transport=httpx.MockTransport(camera._handle), base_url="https://cam") as client:
        return client.request(method, path, **kwargs)


def test_jsonrpc_answers_method_and_negotiation_automatically() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=STATUS)

    with camera.device() as dev:
        status = dev.apis.mqtt_client.get_client_status()

    assert status.status.state == "active"
    assert len(camera.calls("getSupportedVersions")) == 1
    assert camera.calls("getClientStatus")[0].json == {"apiVersion": "1.0", "method": "getClientStatus"}


def test_jsonrpc_versions_keyword_overrides_advertised_versions() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", versions=("1.0", "1.4"))

    with camera.device() as dev:
        dev.apis.mqtt_client.activate_client()
        assert [str(v) for v in dev._state.advertised_versions(f"jsonrpc:{MQTT}") or ()] == ["1.0", "1.4"]


def test_jsonrpc_explicit_versions_registration_is_not_overridden_by_later_methods() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getSupportedVersions", data={"apiVersions": ["1.0", "1.2"]})
    camera.jsonrpc(MQTT, "activateClient")

    response = get(camera, "POST", MQTT, json={"method": "getSupportedVersions"})

    assert response.json()["data"]["apiVersions"] == ["1.0", "1.2"]


def test_jsonrpc_error_and_status_keywords() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient", error=(2105, "nope"), status=403)

    response = get(camera, "POST", MQTT, json={"method": "activateClient"})

    assert response.status_code == 403
    assert response.json()["error"] == {"code": 2105, "message": "nope"}


def test_later_registration_overrides_earlier() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data={"v": 1})
    camera.jsonrpc(MQTT, "getClientStatus", data={"v": 2})

    assert get(camera, "POST", MQTT, json={"method": "getClientStatus"}).json()["data"] == {"v": 2}


def test_unmatched_request_is_404_and_recorded() -> None:
    camera = MockCamera()

    response = get(camera, "GET", "/nothing", params={"a": "1"})

    assert response.status_code == 404
    assert [(r.method, r.path, r.query) for r in camera.requests] == [("GET", "/nothing", {"a": "1"})]


def test_jsonrpc_for_other_method_is_not_matched() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient")

    assert get(camera, "POST", MQTT, json={"method": "other"}).status_code == 404


def test_rest_success_error_and_status() -> None:
    camera = MockCamera()
    camera.rest("GET", "/config/rest/x/v1/a", data=[1, 2])
    camera.rest("POST", "/config/rest/x/v1/a", status=201)
    camera.rest("DELETE", "/config/rest/x/v1/a/1", error=(2002, "bad"))

    assert get(camera, "GET", "/config/rest/x/v1/a").json() == {"status": "success", "data": [1, 2]}
    created = get(camera, "POST", "/config/rest/x/v1/a", json={"data": {}})
    assert created.status_code == 201 and created.json() == {"status": "success"}
    failed = get(camera, "DELETE", "/config/rest/x/v1/a/1")
    assert failed.status_code == 400
    assert failed.json() == {"status": "error", "error": {"code": 2002, "message": "bad"}}


def test_cgi_match_is_subset_of_query_or_form_arguments() -> None:
    camera = MockCamera()
    camera.cgi("/axis-cgi/param.cgi", text="list-reply", match={"action": "list"})
    camera.cgi("/axis-cgi/param.cgi", text="update-reply", match={"action": "update"}, content_type="text/x-test")

    listed = get(camera, "GET", "/axis-cgi/param.cgi", params={"action": "list", "group": "A"})
    updated = get(camera, "POST", "/axis-cgi/param.cgi", data={"action": "update", "x": "1"})

    assert listed.text == "list-reply"
    assert updated.text == "update-reply" and updated.headers["content-type"] == "text/x-test"
    assert get(camera, "GET", "/axis-cgi/param.cgi", params={"action": "remove"}).status_code == 404
    assert camera.requests[1].form == {"action": "update", "x": "1"}
    assert camera.requests[0].query == {"action": "list", "group": "A"}


def test_cgi_status_and_method_filter() -> None:
    camera = MockCamera()
    camera.cgi("/c.cgi", text="denied", status=403, method="POST")

    assert get(camera, "POST", "/c.cgi").status_code == 403
    assert get(camera, "GET", "/c.cgi").status_code == 404


def test_route_escape_hatch_gets_raw_request() -> None:
    camera = MockCamera()
    camera.route("GET", "/custom", lambda request: httpx.Response(202, text=request.url.query.decode()))

    response = get(camera, "GET", "/custom", params={"q": "1"})

    assert (response.status_code, response.text) == (202, "q=1")


def test_fail_raises_for_every_request_or_times() -> None:
    camera = MockCamera()
    camera.cgi("/a")
    camera.fail("/a", httpx.ConnectError, times=1)

    with pytest.raises(httpx.ConnectError):
        get(camera, "GET", "/a")
    assert get(camera, "GET", "/a").status_code == 200
    assert len(camera.requests) == 2

    camera.fail("/b", httpx.ReadTimeout)
    for _ in range(3):
        with pytest.raises(httpx.ReadTimeout):
            get(camera, "GET", "/b")


def test_identity_answers_basic_device_info() -> None:
    camera = MockCamera()
    camera.identity(model="AXIS Q1656", firmware="11.9.0", serial="ACCC8E", ProdNbr="Q1656")

    with camera.device() as dev:
        identity = dev.identity()

    assert (identity.model, identity.firmware_version, identity.serial_number, identity.product_number) == (
        "AXIS Q1656", "11.9.0", "ACCC8E", "Q1656",
    )


def test_api_list_and_dca_apis_shapes() -> None:
    camera = MockCamera()
    camera.api_list({"mqtt-client": "1.3"})
    camera.dca_apis({"analytics-mqtt": ["v1", "v2beta"]})

    discover = get(camera, "GET", "/config/discover").json()
    listing = get(camera, "POST", "/axis-cgi/apidiscovery.cgi", json={"method": "getApiList"}).json()

    assert discover["apis"]["analytics-mqtt"]["v1"] == {"state": "released", "version": "1.0.0"}
    assert discover["framework_version"] == "1.0.0"
    assert [(a["id"], a["version"]) for a in listing["data"]["apiList"]] == [("mqtt-client", "1.3")]


def test_device_defaults_and_forwarded_kwargs() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient")

    with camera.device(timeout=3.0, base_path="") as dev:
        assert dev.config.timeout == 3.0
        assert dev.config.credentials is not None and dev.config.credentials.username == "root"  # type: ignore[union-attr]
        dev.apis.mqtt_client.activate_client()


def test_device_without_matching_route_raises_not_supported() -> None:
    camera = MockCamera()
    with camera.device() as dev, pytest.raises(NotSupported):
        dev.apis.mqtt_client.activate_client()


def test_device_credentials_can_be_disabled() -> None:
    assert MockCamera().device(credentials=None).config.credentials is None


def test_failures_surface_as_library_errors() -> None:
    camera = MockCamera()
    camera.fail(MQTT, httpx.ReadError)
    with camera.device() as dev, pytest.raises(ConnectionFailed):
        dev.apis.mqtt_client.activate_client()


def test_calls_filters_by_jsonrpc_method() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "activateClient")
    camera.jsonrpc(MQTT, "deactivateClient")
    with camera.device() as dev:
        dev.apis.mqtt_client.activate_client()
        dev.apis.mqtt_client.deactivate_client()
        dev.apis.mqtt_client.deactivate_client()

    assert len(camera.calls("activateClient")) == 1
    assert len(camera.calls("deactivateClient")) == 2


@pytest.mark.anyio
async def test_async_device_uses_same_camera() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=STATUS)
    camera.identity(firmware="11.9.0")

    async with camera.async_device() as dev:
        status = await dev.apis.mqtt_client.get_client_status()
        identity = await dev.identity()

    assert status.status.connection_status == "connected"
    assert identity.firmware_version == "11.9.0"
    assert len(camera.calls("getClientStatus")) == 1
