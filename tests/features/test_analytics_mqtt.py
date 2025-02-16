"""Tests for analytics MQTT operations."""

import pytest
from ax_devil_device_api.features.analytics_mqtt import PublisherConfig, AnalyticsMqttClient
from ax_devil_device_api.utils.errors import FeatureError

KNOWN_DATA_SOURCE_KEY = "com.axis.analytics_scene_description.v0.beta#1"

class TestPublisherConfig:
    """Test suite for publisher configuration."""
    
    def test_validation_valid(self):
        """Test validation with valid configuration."""
        valid_configs = [
            PublisherConfig(
                id="test1",
                data_source_key="source1",
                mqtt_topic="topic/test"
            ),
            PublisherConfig(
                id="test2",
                data_source_key="source2",
                mqtt_topic="topic/test",
                qos=2,
                retain=True,
                use_topic_prefix=True
            )
        ]
        for config in valid_configs:
            assert config.validate() is None
            
    def test_validation_invalid(self):
        """Test validation with invalid configurations."""
        invalid_configs = [
            (
                PublisherConfig(
                    id="",
                    data_source_key="source1",
                    mqtt_topic="topic/test"
                ),
                "Publisher ID is required"
            ),
            (
                PublisherConfig(
                    id="test1",
                    data_source_key="",
                    mqtt_topic="topic/test"
                ),
                "Data source key is required"
            ),
            (
                PublisherConfig(
                    id="test1",
                    data_source_key="source1",
                    mqtt_topic=""
                ),
                "MQTT topic is required"
            ),
            (
                PublisherConfig(
                    id="test1",
                    data_source_key="source1",
                    mqtt_topic="topic/test",
                    qos=3
                ),
                "QoS must be 0, 1, or 2"
            )
        ]
        for config, expected_error in invalid_configs:
            error = config.validate()
            assert error is not None
            assert expected_error in error
            
    def test_to_payload(self):
        """Test conversion to API payload."""
        config = PublisherConfig(
            id="test1",
            data_source_key="source1",
            mqtt_topic="topic/test",
            qos=1,
            retain=False,
            use_topic_prefix=False
        )
        payload = config.to_payload()
        assert payload == {
            "data": {
                "id": "test1",
                "data_source_key": "source1",
                "mqtt_topic": "topic/test",
                "qos": 1,
                "retain": False,
                "use_topic_prefix": False
            }
        }

    def test_from_response(self):
        """Test creation from API response."""
        response_data = {
                "id": "test1",
                "data_source_key": KNOWN_DATA_SOURCE_KEY,
                "mqtt_topic": "topic/test",
                "qos": 1,
                "retain": True,
                "use_topic_prefix": True
            }
        config = PublisherConfig.from_response(response_data)
        assert config.id == "test1"
        assert config.data_source_key == KNOWN_DATA_SOURCE_KEY
        assert config.mqtt_topic == "topic/test"
        assert config.qos == 1
        assert config.retain is True
        assert config.use_topic_prefix is True

class TestAnalyticsMqttClient:
    """Test suite for analytics MQTT client."""
    
    def test_get_data_sources_success(self, client):
        """Test successful data sources retrieval."""
        response = client.analytics_mqtt.get_data_sources()
        assert response.success, f"Failed to get data sources: {response.error}"
        assert isinstance(response.data, list)
        
    def test_list_publishers_success(self, client):
        """Test successful publishers listing."""
        response = client.analytics_mqtt.list_publishers()
        assert response.success, f"Failed to list publishers: {response.error}"
        assert isinstance(response.data, list)
        for publisher in response.data:
            assert isinstance(publisher, PublisherConfig)
            
    def test_create_publisher_success(self, client):
        """Test successful publisher creation."""
        # Remove any existing publisher with this id
        client.analytics_mqtt.remove_publisher("test_create")

        config = PublisherConfig(
            id="test_create",
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic"
        )
        response = client.analytics_mqtt.create_publisher(config)
        assert response.success, f"Failed to create publisher: {response.error}"
        assert isinstance(response.data, PublisherConfig)
        assert response.data.id == config.id
        assert response.data.data_source_key == config.data_source_key
        assert response.data.mqtt_topic == config.mqtt_topic
        
        # Cleanup
        client.analytics_mqtt.remove_publisher(config.id)
        
    def test_create_publisher_invalid_config(self, client):
        """Test publisher creation with invalid config."""
        config = PublisherConfig(
            id="",  # Invalid: empty ID
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic"
        )
        response = client.analytics_mqtt.create_publisher(config)
        assert not response.success
        assert response.error.code == "invalid_config"
        assert "Publisher ID is required" in response.error.message

        # remove the publisher
        client.analytics_mqtt.remove_publisher(config.id)
        
    def test_remove_publisher_success(self, client):
        """Test successful publisher removal."""
        # First create a publisher
        config = PublisherConfig(
            id="test_remove",
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic"
        )
        create_response = client.analytics_mqtt.create_publisher(config)
        assert create_response.success, f"Failed to create test publisher: {create_response.error}"
        
        # Then remove it
        response = client.analytics_mqtt.remove_publisher(config.id)
        assert response.success, f"Failed to remove publisher: {response.error}"
        assert response.data is True
        
        # Verify it's gone
        list_response = client.analytics_mqtt.list_publishers()
        assert list_response.success
        assert not any(p.id == config.id for p in list_response.data)
        
    def test_remove_publisher_invalid_id(self, client):
        """Test publisher removal with invalid ID."""
        response = client.analytics_mqtt.remove_publisher("")
        assert not response.success
        assert response.error.code == "invalid_id"
        assert "Publisher ID is required" in response.error.message 