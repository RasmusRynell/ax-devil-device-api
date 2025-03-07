"""Tests for analytics MQTT operations."""

import pytest
from ax_devil_device_api.features.analytics_mqtt import PublisherConfig, AnalyticsMqttClient, DataSource
from ax_devil_device_api.utils.errors import FeatureError

KNOWN_DATA_SOURCE_KEY = "com.axis.analytics_scene_description.v0.beta#1"

class TestPublisherConfig:
    """Test suite for publisher configuration."""
            
    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_create_from_response(self):
        """Test creation from API response."""
        response_data = {
                "id": "test1",
                "data_source_key": KNOWN_DATA_SOURCE_KEY,
                "mqtt_topic": "topic/test",
                "qos": 1,
                "retain": True,
                "use_topic_prefix": True
            }
        config = PublisherConfig.create_from_response(response_data)
        assert config.id == "test1"
        assert config.data_source_key == KNOWN_DATA_SOURCE_KEY
        assert config.mqtt_topic == "topic/test"
        assert config.qos == 1
        assert config.retain is True
        assert config.use_topic_prefix is True

class TestAnalyticsMqttClient:
    """Test suite for analytics MQTT client."""
    
    @pytest.mark.integration
    def test_get_data_sources_success(self, client):
        """Test successful data sources retrieval."""
        response = client.analytics_mqtt.get_data_sources()
        assert isinstance(response, list)
        for data_source in response:
            assert isinstance(data_source, DataSource)
        
    @pytest.mark.integration
    def test_list_publishers_success(self, client):
        """Test successful publishers listing."""
        response = client.analytics_mqtt.list_publishers()
        assert isinstance(response, list)
        for publisher in response:
            assert isinstance(publisher, PublisherConfig)
            
    @pytest.mark.integration
    def test_create_publisher_success(self, client):
        """Test successful publisher creation."""
        # Remove any existing publisher with this id
        if "test_create" in [p.id for p in client.analytics_mqtt.list_publishers()]:
            client.analytics_mqtt.remove_publisher("test_create")

        config = PublisherConfig(
            id="test_create",
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic"
        )
        response = client.analytics_mqtt.create_publisher(config)
        assert isinstance(response, PublisherConfig)
        assert response.id == config.id
        assert response.data_source_key == config.data_source_key
        assert response.mqtt_topic == config.mqtt_topic
        
        # Cleanup
        client.analytics_mqtt.remove_publisher(config.id)
        
    @pytest.mark.integration
    def test_create_publisher_invalid_config(self, client):
        """Test publisher creation with invalid config."""
        config = PublisherConfig(
            id="",  # Invalid: empty ID
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic"
        )
        with pytest.raises(FeatureError) as e:
            response = client.analytics_mqtt.create_publisher(config)
        assert e.value.code == "request_failed"

        # remove the publisher if it was created
        if "test_create" in [p.id for p in client.analytics_mqtt.list_publishers()]:
            client.analytics_mqtt.remove_publisher("test_create")
        
    @pytest.mark.integration
    def test_remove_publisher_success(self, client):
        """Test successful publisher removal."""
        # First create a publisher
        config = PublisherConfig(
            id="test_remove",
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic"
        )

        # remove the publisher if it has already been created
        if "test_remove" in [p.id for p in client.analytics_mqtt.list_publishers()]:
            client.analytics_mqtt.remove_publisher("test_remove")

        create_response = client.analytics_mqtt.create_publisher(config)
        
        response = client.analytics_mqtt.remove_publisher(config.id)
        assert response is True
        
        # Verify it's gone
        list_response = client.analytics_mqtt.list_publishers()
        assert not any(p.id == config.id for p in list_response)
        
    @pytest.mark.integration
    def test_remove_publisher_invalid_id(self, client):
        """Test publisher removal with invalid ID."""
        with pytest.raises(FeatureError) as e:
            response = client.analytics_mqtt.remove_publisher("")
        assert e.value.code == "invalid_id"
        assert "Publisher ID is required" in e.value.message 