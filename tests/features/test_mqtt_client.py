"""Tests for MQTT client operations."""

import pytest
from ax_devil_device_api.features.mqtt_client import BrokerConfig, MqttStatus
from ax_devil_device_api.utils.errors import FeatureError

@pytest.fixture
def valid_broker_config():
    """Fixture for valid broker configuration."""
    return BrokerConfig(
        host="mqtt.example.com",
        port=1883,
        username="testuser",
        password="testpass",
        keep_alive_interval=60
    )

@pytest.fixture
def mock_connected_response():
    """Fixture for connected status response."""
    return {
        "data": {
            "status": {
                "connectionStatus": "connected",
                "state": "active"
            },
            "config": {
                "server": {
                    "host": "mqtt.example.com",
                    "port": 1883
                }
            }
        }
    }

class TestBrokerConfig:
    """Test suite for broker configuration validation."""
    
    def test_valid_configurations(self):
        """Test various valid broker configurations."""
        valid_configs = [
            BrokerConfig(host="mqtt.example.com"),
            BrokerConfig(host="mqtt.example.com", port=8883, use_tls=True),
            BrokerConfig(
                host="mqtt.example.com",
                username="user",
                password="pass",
                keep_alive_interval=30
            )
        ]
        for config in valid_configs:
            assert config.validate() is None, f"Valid config failed validation: {config}"
    
    @pytest.mark.parametrize("config,expected_error", [
        (BrokerConfig(host=""), "host is required"),
        (BrokerConfig(host="mqtt.example.com", port=0), "Port must be between"),
        (BrokerConfig(host="mqtt.example.com", port=65536), "Port must be between"),
        (BrokerConfig(host="mqtt.example.com", keep_alive_interval=0), 
         "Keep alive interval must be positive")
    ])
    def test_invalid_configurations(self, config, expected_error):
        """Test invalid broker configurations."""
        error = config.validate()
        assert error is not None, f"Invalid config passed validation: {config}"
        assert expected_error in error

class TestMqttStatus:
    """Test suite for MQTT status parsing and validation."""
    
    @pytest.mark.parametrize("status_data,expected", [
        ({
            "data": {
                "status": {
                    "connectionStatus": "connected",
                    "state": "active"
                },
                "config": {
                    "server": {
                        "host": "mqtt.example.com",
                        "port": 1883
                    }
                }
            }
        }, {
            "status": "connected",
            "state": "active",
            "has_config": True,
            "has_connection": True
        }),
        ({
            "data": {
                "status": {
                    "connectionStatus": "disconnected",
                    "state": "inactive"
                }
            }
        }, {
            "status": "disconnected",
            "state": "inactive",
            "has_config": False,
            "has_connection": False
        }),
        ({
            "data": {
                "status": {
                    "connectionStatus": "error",
                    "state": "error"
                }
            }
        }, {
            "status": "error",
            "state": "error",
            "has_config": False,
            "has_connection": False
        })
    ])
    def test_status_parsing(self, status_data, expected):
        """Test parsing of various MQTT status responses."""
        status = MqttStatus.from_response(status_data)
        assert status.status == expected["status"]
        assert status.state == expected["state"]
        assert (status.config is not None) == expected["has_config"]
        assert (status.connected_to is not None) == expected["has_connection"]

    def test_invalid_status_value(self):
        """Test handling of invalid status values."""
        with pytest.raises(ValueError, match="Invalid status value"):
            MqttStatus(
                status="invalid_status",
                state=MqttStatus.STATE_ACTIVE
            )

class TestMqttClientFeature:
    """Test suite for MQTT client operations."""
    
    def test_get_status(self, client):
        """Test MQTT client status retrieval."""
        response = client.mqtt_client.get_status()
        assert response.success, f"Failed to get MQTT status: {response.error}"
        self._verify_status_response(response.data)
    
    def test_configure_broker(self, client, valid_broker_config):
        """Test MQTT broker configuration."""
        response = client.mqtt_client.configure(valid_broker_config)
        assert response.success, f"Failed to configure broker: {response.error}"
    
    def test_client_lifecycle(self, client, valid_broker_config):
        """Test complete client lifecycle: configure -> activate -> deactivate."""
        # Configure
        config_response = client.mqtt_client.configure(valid_broker_config)
        assert config_response.success, f"Failed to configure broker: {config_response.error}"
        
        # Activate and verify
        activate_response = client.mqtt_client.activate()
        assert activate_response.success, f"Failed to activate client: {activate_response.error}"
        
        status_response = client.mqtt_client.get_status()
        assert status_response.success
        assert status_response.data.state == "active", \
            "Client should be in active state after activation"
        
        # Deactivate and verify
        deactivate_response = client.mqtt_client.deactivate()
        assert deactivate_response.success, f"Failed to deactivate client: {deactivate_response.error}"
        
        status_response = client.mqtt_client.get_status()
        assert status_response.success
        assert status_response.data.state == "inactive", \
            "Client should be in inactive state after deactivation"
    
    def _verify_status_response(self, status: MqttStatus):
        """Helper to verify MQTT status response structure."""
        assert isinstance(status, MqttStatus), "Status should be MqttStatus instance"
        assert status.status in MqttStatus.VALID_STATUSES, "Invalid status value"
        assert status.state in [
            MqttStatus.STATE_ACTIVE,
            MqttStatus.STATE_INACTIVE,
            MqttStatus.STATE_ERROR
        ], "Invalid state value"
        
        if status.status == MqttStatus.STATUS_CONNECTED:
            assert status.connected_to is not None, "Connected status should include broker info"
            assert "host" in status.connected_to, "Broker info missing host"
            assert "port" in status.connected_to, "Broker info missing port"
            assert isinstance(status.connected_to["port"], int), "Port should be integer" 