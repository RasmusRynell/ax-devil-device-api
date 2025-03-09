"""Tests for MQTT client operations."""

from typing import Any, Dict
import pytest

@pytest.fixture
def valid_broker_config():
    """Fixture for valid broker configuration."""
    return {
        "host": "mqtt.example.com",
        "port": 1883,
        "username": "testuser",
        "password": "testpass",
        "keep_alive_interval": 60
    }

class TestMqttClientFeature:
    """Test suite for MQTT client operations."""
    
    @pytest.mark.integration
    def test_get_status(self, client):
        """Test retrieving MQTT client status."""
        response = client.mqtt_client.get_status()
        self._verify_status_response(response)
    
    @pytest.mark.integration
    def test_configure_broker(self, client, valid_broker_config):
        """Test configuring MQTT broker."""
        client.mqtt_client.configure(valid_broker_config)
    
    @pytest.mark.integration
    def test_client_lifecycle(self, client, valid_broker_config):
        """Test the complete MQTT client lifecycle."""
        client.mqtt_client.configure(valid_broker_config)
        client.mqtt_client.activate()
        
        status_response = client.mqtt_client.get_status()
        self._verify_status_response(status_response)
        assert status_response.get("state") == "active", \
            "Client should be in active state after activation"
        
        client.mqtt_client.deactivate()
        
        status_response = client.mqtt_client.get_status()
        self._verify_status_response(status_response)
        assert status_response.get("state") == "inactive", \
            "Client should be in inactive state after deactivation"
    
    @pytest.mark.integration
    def test_get_config(self, client):
        """Test retrieving MQTT client configuration."""
        _ = client.mqtt_client.get_config()

    def _verify_status_response(self, status: Dict[str, Any]):
        """Helper to verify status response structure."""
        assert isinstance(status, Dict), "Status should be Dict instance"
        assert status.get("state") in [
            "active",
            "inactive",
            "error"
        ], "Invalid state value"
        if status.get("status") == "CONNECTED":
            assert status.get("connected_to") is not None, "Connected status should include broker info"
            assert "host" in status.get("connected_to"), "Broker info missing host"
            assert "port" in status.get("connected_to"), "Broker info missing port"
            assert isinstance(status.get("connected_to").get("port"), int), "Port should be integer" 
