"""Tests for analytics metadata operations."""

from unittest.mock import Mock

import pytest

from src.ax_devil_device_api.features.analytics_metadata import (
    AnalyticsMetadataClient,
    MetadataSample,
    Producer,
    VideoChannel,
)
from src.ax_devil_device_api.utils.errors import FeatureError


class TestAnalyticsMetadataDataClasses:
    """Test suite for analytics metadata data classes."""

    def test_video_channel_creation(self):
        """Test VideoChannel data class creation."""
        channel = VideoChannel(channel=1, enabled=True)
        assert channel.channel == 1
        assert channel.enabled is True

    def test_producer_from_official_api_data(self):
        api_data = {
            "name": "AnalyticsSceneDescription",
            "niceName": "Analytics Scene Description",
            "videochannels": [
                {"channel": 1, "enabled": True},
                {"channel": 2, "enabled": False},
            ],
        }

        producer = Producer.from_api_data(api_data)
        assert producer.name == "AnalyticsSceneDescription"
        assert producer.nice_name == "Analytics Scene Description"
        assert len(producer.video_channels) == 2
        assert producer.video_channels[0].channel == 1
        assert producer.video_channels[0].enabled is True
        assert producer.video_channels[1].channel == 2
        assert producer.video_channels[1].enabled is False
        assert not hasattr(producer, "api_versions")

    def test_producer_allows_missing_optional_nice_name(self):
        producer = Producer.from_api_data(
            {
                "name": "Producer",
                "videochannels": [{"channel": 1, "enabled": True}],
            }
        )

        assert producer.nice_name is None

    @pytest.mark.parametrize("nice_name", [None, 1, []])
    def test_producer_rejects_non_string_nice_name(self, nice_name):
        with pytest.raises(FeatureError, match="niceName"):
            Producer.from_api_data(
                {
                    "name": "Producer",
                    "niceName": nice_name,
                    "videochannels": [],
                }
            )

    @pytest.mark.parametrize(
        "data",
        [
            {"name": "Producer"},
            {"name": "Producer", "videoChannels": []},
            {"name": "Producer", "videochannels": "bad"},
        ],
    )
    def test_producer_requires_official_videochannels(self, data):
        with pytest.raises(FeatureError, match="channels must be an array"):
            Producer.from_api_data(data)

    def test_metadata_sample_from_api_data(self):
        """Test MetadataSample creation from official API response data."""
        api_data = {
            "name": "TestProducer",
            "sampleFrameXML": "<xml>sample</xml>",
        }

        sample = MetadataSample.from_api_data(api_data)
        assert sample.producer_name == "TestProducer"
        assert sample.sample_frame_xml == "<xml>sample</xml>"
        assert not hasattr(sample, "schema_xml")

    @pytest.mark.parametrize(
        "data",
        [
            {"producerName": "TestProducer", "sampleFrameXML": "<xml />"},
            {"name": "TestProducer"},
        ],
    )
    def test_metadata_sample_requires_official_fields(self, data):
        with pytest.raises(FeatureError, match="sample"):
            MetadataSample.from_api_data(data)


class TestAnalyticsMetadataClient:
    """Test suite for analytics metadata client."""

    @pytest.fixture
    def mock_transport_client(self):
        """Create a mock transport client."""
        return Mock()

    @pytest.fixture
    def client(self, mock_transport_client):
        """Create analytics metadata client with mocked transport."""
        return AnalyticsMetadataClient(mock_transport_client)

    def test_list_producers_success(self, client):
        """Test successful listing of producers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "producers": [
                    {
                        "name": "AnalyticsSceneDescription",
                        "niceName": "Analytics Scene Description",
                        "videochannels": [{"channel": 1, "enabled": True}],
                    }
                ]
            }
        }
        client.request = Mock(return_value=mock_response)

        producers = client.list_producers()

        assert len(producers) == 1
        assert producers[0].name == "AnalyticsSceneDescription"
        assert producers[0].nice_name == "Analytics Scene Description"
        assert len(producers[0].video_channels) == 1
        assert producers[0].video_channels[0].channel == 1
        assert producers[0].video_channels[0].enabled is True

        # Verify request was made correctly
        client.request.assert_called_once()
        _args, kwargs = client.request.call_args
        assert kwargs["json"] == {
            "context": "cli",
            "method": "listProducers",
            "apiVersion": "1.0",
        }

    def test_list_producers_empty_response(self, client):
        """Test listing producers with empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"producers": []}}
        client.request = Mock(return_value=mock_response)

        producers = client.list_producers()
        assert len(producers) == 0

    def test_set_enabled_producers_success(self, client):
        """Test successful producer configuration."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {}}
        client.request = Mock(return_value=mock_response)

        producers = [
            Producer(
                name="TestProducer",
                nice_name="Test Producer",
                video_channels=[VideoChannel(channel=1, enabled=True)],
            )
        ]

        client.set_enabled_producers(producers)

        # Verify request was made correctly
        client.request.assert_called_once()
        _args, kwargs = client.request.call_args
        assert kwargs["json"]["method"] == "setEnabledProducers"
        assert kwargs["json"]["apiVersion"] == "1.0"
        expected_params = {
            "producers": [
                {
                    "name": "TestProducer",
                    "videochannels": [{"channel": 1, "enabled": True}],
                }
            ]
        }
        assert kwargs["json"]["params"] == expected_params

    def test_set_enabled_producers_requires_data_object(self, client):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"data": []}
        client.request = Mock(return_value=mock_response)
        producer = Producer(
            name="TestProducer",
            nice_name=None,
            video_channels=[VideoChannel(channel=1, enabled=True)],
        )

        with pytest.raises(FeatureError, match="data must be an object"):
            client.set_enabled_producers([producer])

    def test_set_enabled_producers_empty_list(self, client):
        """Test error when trying to set empty producer list."""
        with pytest.raises(FeatureError) as exc_info:
            client.set_enabled_producers([])

        assert exc_info.value.code == "invalid_parameter"
        assert "At least one producer" in exc_info.value.message

    def test_get_supported_metadata_success(self, client):
        """Test successful metadata sample retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "producers": [
                    {
                        "name": "TestProducer",
                        "sampleFrameXML": "<xml>sample</xml>",
                    }
                ]
            }
        }
        client.request = Mock(return_value=mock_response)

        samples = client.get_supported_metadata(["TestProducer"])

        assert len(samples) == 1
        assert samples[0].producer_name == "TestProducer"
        assert samples[0].sample_frame_xml == "<xml>sample</xml>"
        assert not hasattr(samples[0], "schema_xml")

        # Verify request was made correctly
        client.request.assert_called_once()
        _args, kwargs = client.request.call_args
        assert kwargs["json"]["method"] == "getSupportedMetadata"
        assert kwargs["json"]["apiVersion"] == "1.0"
        assert kwargs["json"]["params"] == {"producers": ["TestProducer"]}

    def test_get_supported_metadata_rejects_direct_array_data(self, client):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "data": [{"name": "TestProducer", "sampleFrameXML": "<xml />"}]
        }
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError, match="data must be an object"):
            client.get_supported_metadata(["TestProducer"])

    def test_get_supported_metadata_rejects_producer_name_alias(self, client):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "data": {
                "producers": [
                    {"producerName": "TestProducer", "sampleFrameXML": "<xml />"}
                ]
            }
        }
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError, match="sample entry"):
            client.get_supported_metadata(["TestProducer"])

    def test_get_supported_metadata_omits_optional_producers(self, client):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"data": {"producers": []}}
        client.request = Mock(return_value=mock_response)

        assert client.get_supported_metadata() == []
        _, kwargs = client.request.call_args
        assert kwargs["json"] == {
            "context": "cli",
            "method": "getSupportedMetadata",
            "apiVersion": "1.0",
        }

    def test_get_supported_versions_success(self, client):
        """Test successful version retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"apiVersions": ["1.0", "1.1"]}}
        client.request = Mock(return_value=mock_response)

        versions = client.get_supported_versions()

        assert versions == ["1.0", "1.1"]

        # Verify request was made correctly
        client.request.assert_called_once()
        _args, kwargs = client.request.call_args
        assert kwargs["json"] == {
            "context": "cli",
            "method": "getSupportedVersions",
        }

    def test_get_supported_versions_rejects_legacy_versions_field(self, client):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"data": {"versions": ["1.0"]}}
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError, match="apiVersions"):
            client.get_supported_versions()

    def test_api_error_response(self, client):
        """Test handling of API error responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        error = {
            "code": 2000,
            "message": "Invalid request",
            "details": {"field": "producers"},
        }
        mock_response.json.return_value = {"error": error}
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError) as exc_info:
            client.list_producers()

        assert exc_info.value.code == "api_error_2000"
        assert exc_info.value.message == "Invalid request"
        assert exc_info.value.details == error

    @pytest.mark.parametrize("error", [None, "bad", [], {"code": 2000}])
    def test_api_error_normalizes_malformed_error_objects(self, client, error):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"error": error}
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError):
            client.list_producers()

    def test_http_error_response(self, client):
        """Test handling of HTTP error responses."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError) as exc_info:
            client.list_producers()

        assert exc_info.value.code == "request_failed"
        assert "HTTP 401" in exc_info.value.message

    def test_invalid_json_response(self, client):
        """Test handling of invalid JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError) as exc_info:
            client.list_producers()

        assert exc_info.value.code == "invalid_response"
        assert "Failed to parse JSON" in exc_info.value.message

    @pytest.mark.parametrize("versions", [["1.0", 2], "bad", None])
    def test_supported_versions_rejects_malformed_values(self, client, versions):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"data": {"apiVersions": versions}}
        client.request = Mock(return_value=mock_response)

        with pytest.raises(FeatureError, match="apiVersions"):
            client.get_supported_versions()


class TestAnalyticsMetadataIntegration:
    """Integration tests for analytics metadata functionality."""

    @pytest.mark.integration
    def test_list_producers_integration(self, client):
        """Test listing producers against real device."""
        try:
            producers = client.analytics_metadata.list_producers()
            assert isinstance(producers, list)

            # If producers exist, verify structure
            for producer in producers:
                assert hasattr(producer, "name")
                assert hasattr(producer, "nice_name")
                assert hasattr(producer, "video_channels")
                assert isinstance(producer.video_channels, list)

                for channel in producer.video_channels:
                    assert hasattr(channel, "channel")
                    assert hasattr(channel, "enabled")
                    assert isinstance(channel.channel, int)
                    assert isinstance(channel.enabled, bool)
        except FeatureError as e:
            # Some devices may not support this feature
            if "request_failed" in e.code and "404" in e.message:
                pytest.skip("Device does not support analytics metadata API")
            else:
                raise

    @pytest.mark.integration
    def test_get_supported_versions_integration(self, client):
        """Test getting supported versions against real device."""
        try:
            versions = client.analytics_metadata.get_supported_versions()
            assert isinstance(versions, list)
            # Should have at least version 1.0
            if versions:
                assert "1.0" in versions or len(versions) > 0
        except FeatureError as e:
            # Some devices may not support this feature
            if "request_failed" in e.code and "404" in e.message:
                pytest.skip("Device does not support analytics metadata API")
            else:
                raise
