"""Tests for MQTT client operations."""

from typing import Any, Dict
import pytest

@pytest.fixture
def valid_broker_config():
    """Fixture for valid broker configuration."""
    return 

class TestMqttClientFeature:
    """Test suite for MQTT client operations."""
    
    @pytest.mark.integration
    def test_get_status(self, client):
        """Test retrieving MQTT client status."""
        response = client.mqtt_client.get_status()
        self._verify_status_status_and_config(response)
    
    @pytest.mark.integration
    def test_configure_broker(self, client):
        """Test configuring MQTT broker."""
        client.mqtt_client.configure(
            host="mqtt.example.com",
            port=1883,
            username="testuser",
            password="testpass",
            keep_alive_interval=60
        )
    
    @pytest.mark.integration
    def test_client_lifecycle(self, client):
        """Test the complete MQTT client lifecycle."""
        client.mqtt_client.configure(
            host="mqtt.example.com",
            port=1883,
            username="testuser",
            password="testpass",
            keep_alive_interval=60
        )
        client.mqtt_client.activate()
        
        status_response = client.mqtt_client.get_status()
        self._verify_status_status_and_config(status_response)
        assert status_response.get("status").get("state") == "active", \
            "Client should be in active state after activation"
        
        client.mqtt_client.deactivate()
        
        status_response = client.mqtt_client.get_status()
        self._verify_status_status_and_config(status_response)
        assert status_response.get("status").get("state") == "inactive", \
            "Client should be in inactive state after deactivation"

    def _verify_status_status_and_config(self, data: Dict[str, Any]):
        """Helper to verify status response structure."""
        assert isinstance(data, Dict), "Status should be Dict instance"
        status = data.get("status")
        config = data.get("config")
        assert status.get("state") in [
            "active",
            "inactive",
            "error"
        ], "Invalid state value"
        assert "host" in config.get("server"), "Broker info missing host"
