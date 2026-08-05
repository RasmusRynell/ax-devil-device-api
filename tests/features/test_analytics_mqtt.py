"""Tests for analytics MQTT operations."""

import pytest
from unittest.mock import Mock

from src.ax_devil_device_api.features.analytics_mqtt import AnalyticsMqttClient
from src.ax_devil_device_api.utils.errors import FeatureError

KNOWN_DATA_SOURCE_KEY = "com.axis.scene.frame.v1#1"


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
        if "test_create" in [
            p.get("id") for p in client.analytics_mqtt.list_publishers()
        ]:
            client.analytics_mqtt.remove_publisher("test_create")

        response = client.analytics_mqtt.create_publisher(
            id="test_create",
            data_source_key=KNOWN_DATA_SOURCE_KEY,
            mqtt_topic="test/topic",
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

    @pytest.fixture
    def api_client(self):
        return AnalyticsMqttClient(Mock())

    def test_released_v1_and_official_data_sources_shape(self, api_client):
        response = Mock()
        response.content = b"{}"
        response.json.return_value = {
            "status": "success",
            "data": {"data_sources": [{"key": "source"}]},
        }
        response.raise_for_status = Mock()
        api_client.request = Mock(return_value=response)

        assert api_client.get_data_sources() == [{"key": "source"}]
        assert "/analytics-mqtt/v1/" in api_client.DATA_SOURCES_ENDPOINT.path

    def test_mutation_accepts_success_without_data(self, api_client):
        response = Mock()
        response.content = b"{}"
        response.json.return_value = {"status": "success"}
        response.raise_for_status = Mock()
        api_client.request = Mock(return_value=response)

        assert api_client.create_publisher("id", "source", "topic") is None

    @pytest.mark.parametrize("status_code", [200, 201, 204])
    def test_mutations_accept_valid_success_statuses(self, api_client, status_code):
        response = Mock(status_code=status_code, content=b"")
        response.raise_for_status = Mock()
        api_client.request = Mock(return_value=response)

        api_client.create_publisher("id", "source", "topic")
        api_client.remove_publisher("id")

    @pytest.mark.parametrize("method", ["create_publisher", "remove_publisher"])
    def test_mutations_reject_json_api_errors(self, api_client, method):
        response = Mock(status_code=200, content=b"{}")
        response.raise_for_status = Mock()
        response.json.return_value = {
            "status": "error",
            "error": {"code": "invalid", "message": "bad request"},
        }
        api_client.request = Mock(return_value=response)

        if method == "create_publisher":

            def call():
                api_client.create_publisher("id", "source", "topic")
        else:

            def call():
                api_client.remove_publisher("id")

        with pytest.raises(FeatureError, match="bad request"):
            call()

    def test_mutation_rejects_malformed_json(self, api_client):
        response = Mock(status_code=200, content=b"not-json")
        response.raise_for_status = Mock()
        response.json.side_effect = ValueError("bad json")
        api_client.request = Mock(return_value=response)

        with pytest.raises(FeatureError, match="invalid JSON"):
            api_client.create_publisher("id", "source", "topic")

    @pytest.mark.parametrize("data", [None, {}, ["bad"], [{"key": "ok"}, "bad"]])
    def test_list_data_sources_rejects_malformed_envelopes(self, api_client, data):
        response = Mock(status_code=200, content=b"{}")
        response.raise_for_status = Mock()
        response.json.return_value = {"status": "success", "data": data}
        api_client.request = Mock(return_value=response)

        with pytest.raises(FeatureError, match="data source"):
            api_client.get_data_sources()

    @pytest.mark.parametrize("data", [None, {}, ["bad"]])
    def test_list_publishers_rejects_malformed_envelopes(self, api_client, data):
        response = Mock(status_code=200, content=b"{}")
        response.raise_for_status = Mock()
        response.json.return_value = {"status": "success", "data": data}
        api_client.request = Mock(return_value=response)

        with pytest.raises(FeatureError, match="publishers"):
            api_client.list_publishers()

    def test_create_publisher_uses_official_request_envelope(self, api_client):
        response = Mock(status_code=200, content=b'{"status":"success"}')
        response.json.return_value = {"status": "success"}
        api_client.request = Mock(return_value=response)

        api_client.create_publisher("pub", "source#1", "analytics/topic", 1, True, True)

        assert api_client.request.call_args.kwargs["json"] == {
            "data": {
                "id": "pub",
                "data_source_key": "source#1",
                "mqtt_topic": "analytics/topic",
                "qos": 1,
                "retain": True,
                "use_topic_prefix": True,
            }
        }

    def test_remove_publisher_uses_encoded_single_id_path(self, api_client):
        response = Mock(status_code=204, content=b"")
        api_client.request = Mock(return_value=response)

        api_client.remove_publisher("publisher/id")

        endpoint = api_client.request.call_args.args[0]
        assert endpoint.path.endswith("/publishers/publisher%2Fid")
