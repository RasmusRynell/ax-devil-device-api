"""Tests for analytics MQTT CLI."""

import pytest
import time
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from ax_devil_device_api.examples.analytics_mqtt_cli import cli
from ax_devil_device_api.features.analytics_mqtt import PublisherConfig, DataSource
from ax_devil_device_api.utils.errors import FeatureError

# Test data
MOCK_SOURCES = [
    DataSource(key="source1"),
    DataSource(key="source2")
]

MOCK_PUBLISHERS = [
    PublisherConfig(
        id="pub1",
        data_source_key="source1",
        mqtt_topic="topic/test1",
        qos=0,
        retain=False,
        use_topic_prefix=False
    ),
    PublisherConfig(
        id="pub2",
        data_source_key="source2",
        mqtt_topic="topic/test2",
        qos=1,
        retain=True,
        use_topic_prefix=True
    )
]

class TestAnalyticsMqttCli:
    """Test suite for Analytics MQTT CLI."""

    @pytest.fixture
    def runner(self):
        """Fixture for CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Fixture for mock client."""
        mock = MagicMock()
        # Setup analytics_mqtt attribute with necessary methods
        mock.analytics_mqtt = MagicMock()
        mock.analytics_mqtt.get_data_sources = MagicMock(return_value=MOCK_SOURCES)
        mock.analytics_mqtt.list_publishers = MagicMock(return_value=MOCK_PUBLISHERS)
        mock.analytics_mqtt.create_publisher = MagicMock(return_value=MOCK_PUBLISHERS[0])
        mock.analytics_mqtt.remove_publisher = MagicMock()
        return mock

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    def test_list_sources(self, mock_create_client, runner, mock_client):
        """Test list sources command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "sources"])
        
        assert result.exit_code == 0
        assert "Available Analytics Data Sources:" in result.output
        assert "source1" in result.output
        assert "source2" in result.output
        
        mock_client.analytics_mqtt.get_data_sources.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    def test_list_publishers(self, mock_create_client, runner, mock_client):
        """Test list publishers command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "list"])
        
        assert result.exit_code == 0
        assert "Configured Publishers:" in result.output
        assert "pub1" in result.output
        assert "pub2" in result.output
        assert "topic/test1" in result.output
        assert "topic/test2" in result.output
        
        mock_client.analytics_mqtt.list_publishers.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    def test_create_publisher(self, mock_create_client, runner, mock_client):
        """Test create publisher command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "create", "test-id", "source1", "topic/test",
                "--qos", "1",
                "--retain",
                "--use-topic-prefix",
                "--force" # Use --force to skip confirmation
            ]
        )
        
        assert result.exit_code == 0
        assert "Publisher created successfully" in result.output
        
        mock_client.analytics_mqtt.create_publisher.assert_called_once()
        args, kwargs = mock_client.analytics_mqtt.create_publisher.call_args
        config = args[0]
        assert config.id == "test-id"
        assert config.data_source_key == "source1"
        assert config.mqtt_topic == "topic/test"
        assert config.qos == 1
        assert config.retain is True
        assert config.use_topic_prefix is True

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    def test_create_publisher_error(self, mock_create_client, runner, mock_client):
        """Test create publisher with error."""
        # Set up the error to be raised
        error = FeatureError("Invalid configuration", 400, {"error": "Invalid data source"})
        mock_client.analytics_mqtt.create_publisher.side_effect = error
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        # We're testing that the CLI handles the error and displays it to the user
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "create", "test-id", "invalid-source", "topic/test",
                "--force"
            ]
        )
        
        # The CLI should display the error message to the user
        assert "Invalid configuration" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    def test_remove_publisher(self, mock_create_client, runner, mock_client):
        """Test remove publisher command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "remove", "pub1",
                "--force" # Use --force to skip confirmation
            ]
        )
        
        assert result.exit_code == 0
        assert "removed successfully" in result.output
        
        mock_client.analytics_mqtt.remove_publisher.assert_called_once_with("pub1")

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    def test_remove_publisher_error(self, mock_create_client, runner, mock_client):
        """Test remove publisher with error."""
        # Set up the error to be raised
        error = FeatureError("Publisher not found", 404, {"error": "No such publisher"})
        mock_client.analytics_mqtt.remove_publisher.side_effect = error
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        # We're testing that the CLI handles the error and displays it to the user
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "remove", "nonexistent",
                "--force"
            ]
        )
        
        # The CLI should display the error message to the user
        assert "Publisher not found" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    @patch("click.confirm")
    def test_create_publisher_confirmation(self, mock_confirm, mock_create_client, runner, mock_client):
        """Test create publisher command with confirmation."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        mock_confirm.return_value = True
        
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "create", "test-id", "source1", "topic/test"
            ]
        )
        
        assert result.exit_code == 0
        mock_confirm.assert_called_once()
        mock_client.analytics_mqtt.create_publisher.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    @patch("click.confirm")
    def test_create_publisher_cancelled(self, mock_confirm, mock_create_client, runner, mock_client):
        """Test create publisher command with cancelled confirmation."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        mock_confirm.return_value = False
        
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "create", "test-id", "source1", "topic/test"
            ]
        )
        
        assert result.exit_code == 0
        assert "Operation cancelled" in result.output
        mock_confirm.assert_called_once()
        mock_client.analytics_mqtt.create_publisher.assert_not_called()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    @patch("click.confirm")
    def test_remove_publisher_confirmation(self, mock_confirm, mock_create_client, runner, mock_client):
        """Test remove publisher command with confirmation."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        mock_confirm.return_value = True
        
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "remove", "pub1"
            ]
        )
        
        assert result.exit_code == 0
        mock_confirm.assert_called_once()
        mock_client.analytics_mqtt.remove_publisher.assert_called_once_with("pub1")

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.analytics_mqtt_cli.create_client")
    @patch("click.confirm")
    def test_remove_publisher_cancelled(self, mock_confirm, mock_create_client, runner, mock_client):
        """Test remove publisher command with cancelled confirmation."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        mock_confirm.return_value = False
        
        result = runner.invoke(
            cli, 
            [
                "--device-ip", "192.168.0.90", 
                "remove", "pub1"
            ]
        )
        
        assert result.exit_code == 0
        assert "Operation cancelled" in result.output
        mock_confirm.assert_called_once()
        mock_client.analytics_mqtt.remove_publisher.assert_not_called() 