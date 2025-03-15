"""Tests for analytics MQTT operations."""

import pytest
from src.ax_devil_device_api.utils.errors import FeatureError

KNOWN_DATA_SOURCE_KEY = "com.axis.analytics_scene_description.v0.beta#1"

class TestAnalyticsMqttClient:
    """Test suite for analytics MQTT client."""
    
    @pytest.mark.integration
    def test_get_data_sources_success(self, client):
        """Test successful data sources retrieval."""
        try:
            response = client.analytics_mqtt.get_data_sources()
        except FeatureError as e:
            print(e)
            raise e

        assert isinstance(response, list)
        
    @pytest.mark.integration
    def test_list_publishers_success(self, client):
        """Test successful publishers listing."""
        response = client.analytics_mqtt.list_publishers()
        assert isinstance(response, list)
            
    @pytest.mark.integration
    def test_create_and_remove_publisher_success(self, client):
        """Test successful publisher creation and removal."""
        # Remove any existing publisher with this id
        if "test_create" in [p.get("id") for p in client.analytics_mqtt.list_publishers()]:
            client.analytics_mqtt.remove_publisher("test_create")

        response = client.analytics_mqtt.create_publisher(
            id="test_create",
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic"
        )
        assert response is None
        
        # Cleanup
        client.analytics_mqtt.remove_publisher("test_create")
        
    @pytest.mark.unit
    def test_remove_publisher_invalid_id(self, client):
        """Test publisher removal with invalid ID."""
        with pytest.raises(FeatureError) as e:
            client.analytics_mqtt.remove_publisher("")
        assert e.value.code == "invalid_id"
        assert "Publisher ID is required" in e.value.message 