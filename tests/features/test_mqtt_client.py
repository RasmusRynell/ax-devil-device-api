"""Tests for MQTT client operations."""

from typing import Any, Dict
from unittest.mock import Mock

import pytest

from src.ax_devil_device_api.features.mqtt_client import MqttClient
from src.ax_devil_device_api.utils.errors import FeatureError


@pytest.fixture
def valid_broker_config():
    """Fixture for valid broker configuration."""
    return


class TestMqttClientFeature:
    """Test suite for MQTT client operations."""

    @pytest.mark.integration
    def test_get_state(self, client):
        """Test retrieving MQTT client status."""
        response = client.mqtt_client.get_state()
        self._verify_status_status_and_config(response)

    @pytest.mark.integration
    def test_configure_broker(self, client):
        """Test configuring MQTT broker."""
        client.mqtt_client.configure(
            host="mqtt.example.com",
            port=1883,
            username="testuser",
            password="testpass",
            keep_alive_interval=60,
        )

    @pytest.mark.integration
    def test_client_lifecycle(self, client):
        """Test the complete MQTT client lifecycle."""
        client.mqtt_client.configure(
            host="mqtt.example.com",
            port=1883,
            username="testuser",
            password="testpass",
            keep_alive_interval=60,
        )
        client.mqtt_client.activate()

        status_response = client.mqtt_client.get_state()
        self._verify_status_status_and_config(status_response)
        assert status_response.get("status").get("state") == "active", (
            "Client should be in active state after activation"
        )

        client.mqtt_client.deactivate()

        status_response = client.mqtt_client.get_state()
        self._verify_status_status_and_config(status_response)
        assert status_response.get("status").get("state") == "inactive", (
            "Client should be in inactive state after deactivation"
        )

    def _verify_status_status_and_config(self, data: Dict[str, Any]):
        """Helper to verify status response structure."""
        assert isinstance(data, Dict), "Status should be Dict instance"
        status = data.get("status")
        config = data.get("config")
        assert status.get("state") in ["active", "inactive", "error"], (
            "Invalid state value"
        )
        assert "host" in config.get("server"), "Broker info missing host"

    @pytest.fixture
    def api_client(self):
        return MqttClient(Mock())

    def test_configure_maps_tls_and_omits_optional_strings(self, api_client):
        api_client.request = Mock(return_value=self._response({"data": {}}))

        api_client.configure("broker", use_tls=True)

        payload = api_client.request.call_args.kwargs["data"]
        assert '"protocol": "ssl"' in payload
        assert '"username"' not in payload
        assert '"password"' not in payload

    def test_set_state_uses_lifecycle_methods(self, api_client):
        api_client.activate = Mock(return_value={})

        api_client.set_state({"status": {"state": "active"}})

        api_client.activate.assert_called_once_with()

    def test_set_state_rejects_configuration_shape_without_state(self, api_client):
        with pytest.raises(FeatureError, match="state must be"):
            api_client.set_state({"config": {}})

    @pytest.mark.parametrize("port", [0, 65536])
    def test_configure_rejects_invalid_port(self, api_client, port):
        with pytest.raises(FeatureError, match="port must be"):
            api_client.configure("broker", port=port)

    def test_configure_rejects_negative_keepalive(self, api_client):
        with pytest.raises(FeatureError, match="keep_alive_interval"):
            api_client.configure("broker", keep_alive_interval=-1)

    @pytest.mark.parametrize("protocol", ["tcp", "ssl", "ws", "wss"])
    def test_configure_accepts_official_protocols(self, api_client, protocol):
        api_client.request = Mock(return_value=self._response({"data": {}}))

        api_client.configure("broker", protocol=protocol)

        assert (
            api_client.request.call_args.kwargs["data"].find(
                f'"protocol": "{protocol}"'
            )
            >= 0
        )

    def test_configure_rejects_non_official_protocol(self, api_client):
        with pytest.raises(FeatureError, match="protocol must be"):
            api_client.configure("broker", protocol="mqtt")

    @pytest.mark.parametrize("protocol", ["ws", "wss"])
    def test_configure_rejects_tls_flag_with_websocket_protocol(
        self, api_client, protocol
    ):
        with pytest.raises(FeatureError, match="only be combined"):
            api_client.configure("broker", protocol=protocol, use_tls=True)

    @staticmethod
    def _response(data):
        response = Mock()
        response.status_code = 200
        response.json.return_value = data
        return response
