"""Read-modify-write helpers and the request-object calling convention."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ax_devil_device_api.apis import mqtt_client
from ax_devil_device_api.apis.analytics_mqtt import AddPublisherRequest, Publisher
from ax_devil_device_api.apis.mqtt_client import ClientConfig, ConfigureClientRequest, Server
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"
PUBLISHERS = "/config/rest/analytics-mqtt/v1/publishers"

CURRENT = {
    "status": {"state": "active", "connectionStatus": "reconnecting"},
    "config": {
        "server": {"host": "broker", "protocol": "ssl"},
        "clientId": "cam1",
        "username": "u",
        "password": "*****",
        "keepAliveInterval": 30,
        "futureField": 1,
    },
}


def test_from_current_drops_masked_password_and_keeps_existing() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=CURRENT)
    with camera.device() as dev:
        config = dev.apis.mqtt_client.get_client_status().config

    assert config is not None and config.password == "*****"
    request = ConfigureClientRequest.from_current(config)

    assert request.password is None and "password" not in request.model_fields_set
    assert request.keep_existing_password is True
    assert request.to_wire() == {
        "server": {"host": "broker", "protocol": "ssl"},
        "clientId": "cam1",
        "username": "u",
        "keepAliveInterval": 30,
        "keepExistingPassword": True,
    }


def test_from_current_requires_client_id() -> None:
    with pytest.raises(ValueError, match="client_id"):
        ConfigureClientRequest.from_current(ClientConfig(server=Server(host="b")))


def test_edit_and_send_back_round_trip() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=CURRENT)
    camera.jsonrpc(MQTT, "configureClient")
    with camera.device() as dev:
        config = dev.apis.mqtt_client.get_client_status().config
        assert config is not None
        edited = ConfigureClientRequest.from_current(config).model_copy(update={"keep_alive_interval": 60})
        dev.apis.mqtt_client.configure_client(edited)

    [call] = camera.calls("configureClient")
    assert call.json["params"]["keepAliveInterval"] == 60
    assert call.json["params"]["keepExistingPassword"] is True
    assert "password" not in call.json["params"]


def test_configure_client_accepts_request_object_and_kwargs_equally() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "configureClient")
    request = ConfigureClientRequest(server=Server(host="b"), client_id="c", keep_alive_interval=5)
    with camera.device() as dev:
        dev.apis.mqtt_client.configure_client(request)
        dev.apis.mqtt_client.configure_client(server=Server(host="b"), client_id="c", keep_alive_interval=5)

    first, second = camera.calls("configureClient")
    assert first.json == second.json


def test_request_and_kwargs_together_is_type_error() -> None:
    camera = MockCamera()
    request = ConfigureClientRequest(server=Server(host="b"), client_id="c")
    with camera.device() as dev, pytest.raises(TypeError, match="either a request object or keyword"):
        dev.apis.mqtt_client.configure_client(request, client_id="x")  # type: ignore[call-overload]

    assert camera.requests == []


def test_wrong_request_type_is_type_error() -> None:
    camera = MockCamera()
    wrong = AddPublisherRequest(id="p", data_source_key="tns1:Foo", mqtt_topic="a")
    with camera.device() as dev, pytest.raises(TypeError, match="expects ConfigureClientRequest, got AddPublisherRequest"):
        dev.apis.mqtt_client.configure_client(wrong)  # type: ignore[call-overload]

    assert camera.requests == []


def test_request_for_operation_without_params_is_type_error() -> None:
    camera = MockCamera()
    with camera.device() as dev, pytest.raises(TypeError, match="takes no arguments"):
        dev.invoke(mqtt_client.OPS.activate_client, bogus=1)


def test_invalid_kwargs_fail_before_anything_is_sent() -> None:
    camera = MockCamera()
    with camera.device() as dev, pytest.raises(ValidationError):
        dev.apis.mqtt_client.configure_client(server=Server(host="b"), client_id="c", nope=1)  # type: ignore[call-overload]

    assert camera.requests == []


def test_add_publisher_from_current_round_trips() -> None:
    camera = MockCamera()
    camera.rest("GET", f"{PUBLISHERS}/p1", data={"id": "p1", "data_source_key": "tns1:Foo", "mqtt_topic": "a/b", "qos": 1})
    camera.rest("POST", PUBLISHERS, status=201)
    with camera.device() as dev:
        publisher = dev.apis.analytics_mqtt.get_publisher("p1")
        assert isinstance(publisher, Publisher)
        request = AddPublisherRequest.from_current(publisher)
        dev.apis.analytics_mqtt.add_publisher(request)

    assert request.to_wire() == {"id": "p1", "data_source_key": "tns1:Foo", "mqtt_topic": "a/b", "qos": 1}
    post = next(r for r in camera.requests if r.method == "POST")
    assert post.json == {"data": request.to_wire()}


def test_invoke_runs_operation_by_descriptor() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=CURRENT)
    camera.jsonrpc(MQTT, "configureClient")
    with camera.device() as dev:
        status = dev.invoke(mqtt_client.OPS.get_client_status)
        dev.invoke(mqtt_client.OPS.configure_client, server=Server(host="b"), client_id="c")
        dev.invoke(
            mqtt_client.OPS.configure_client, ConfigureClientRequest(server=Server(host="b"), client_id="d")
        )

    assert status.status.state == "active"
    assert [c.json["params"]["clientId"] for c in camera.calls("configureClient")] == ["c", "d"]


@pytest.mark.anyio
async def test_async_request_object_and_invoke() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=CURRENT)
    camera.jsonrpc(MQTT, "configureClient")
    async with camera.async_device() as dev:
        status = await dev.invoke(mqtt_client.OPS.get_client_status)
        assert status.config is not None
        await dev.apis.mqtt_client.configure_client(ConfigureClientRequest.from_current(status.config))
        with pytest.raises(TypeError):
            await dev.apis.mqtt_client.configure_client(
                ConfigureClientRequest.from_current(status.config), client_id="x"  # type: ignore[call-overload]
            )

    assert len(camera.calls("configureClient")) == 1
