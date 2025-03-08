"""Tests for device debug CLI."""

import pytest
import io
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, mock_open
from ax_devil_device_api.examples.device_debug_cli import cli
from ax_devil_device_api.utils.errors import FeatureError


class TestDeviceDebugCli:
    """Test suite for Device Debug CLI."""

    @pytest.fixture
    def runner(self):
        """Fixture for CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Fixture for mock client."""
        mock = MagicMock()
        mock.device_debug = MagicMock()
        mock.device_debug.download_server_report = MagicMock(return_value=b"server report data")
        mock.device_debug.download_crash_report = MagicMock(return_value=b"crash report data")
        mock.device_debug.download_network_trace = MagicMock(return_value=b"network trace data")
        mock.device_debug.ping_test = MagicMock(return_value="Ping test results")
        mock.device_debug.port_open_test = MagicMock(return_value="Port test results")
        mock.device_debug.collect_core_dump = MagicMock(return_value=b"core dump data")
        return mock

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_server_report(self, mock_file, mock_create_client, runner, mock_client):
        """Test download server report command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "download-server-report", "report.tar.gz"])
        
        assert result.exit_code == 0
        assert "Server report saved to report.tar.gz" in result.output
        
        mock_client.device_debug.download_server_report.assert_called_once()
        mock_file.assert_called_once_with("report.tar.gz", "wb")
        mock_file().write.assert_called_once_with(b"server report data")

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_crash_report(self, mock_file, mock_create_client, runner, mock_client):
        """Test download crash report command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "download-crash-report", "crash.tar.gz"])
        
        assert result.exit_code == 0
        assert "Crash report saved to crash.tar.gz" in result.output
        
        mock_client.device_debug.download_crash_report.assert_called_once()
        mock_file.assert_called_once_with("crash.tar.gz", "wb")
        mock_file().write.assert_called_once_with(b"crash report data")

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_network_trace(self, mock_file, mock_create_client, runner, mock_client):
        """Test download network trace command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "download-network-trace", 
            "trace.pcap",
            "--duration", "60",
            "--interface", "eth0"
        ])
        
        assert result.exit_code == 0
        assert "Network trace saved to trace.pcap" in result.output
        
        mock_client.device_debug.download_network_trace.assert_called_once_with(duration=60, interface="eth0")
        mock_file.assert_called_once_with("trace.pcap", "wb")
        mock_file().write.assert_called_once_with(b"network trace data")

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    def test_ping_test(self, mock_create_client, runner, mock_client):
        """Test ping test command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "ping-test", "8.8.8.8"])
        
        assert result.exit_code == 0
        assert "Ping test results" in result.output
        
        mock_client.device_debug.ping_test.assert_called_once_with("8.8.8.8")

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    def test_port_open_test(self, mock_create_client, runner, mock_client):
        """Test port open test command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "port-open-test", "example.com", "443"])
        
        assert result.exit_code == 0
        assert "Port test results" in result.output
        
        mock_client.device_debug.port_open_test.assert_called_once_with("example.com", 443)

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    @patch("builtins.open", new_callable=mock_open)
    def test_collect_core_dump(self, mock_file, mock_create_client, runner, mock_client):
        """Test collect core dump command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "collect-core-dump", "core.dump"])
        
        assert result.exit_code == 0
        assert "Core dump saved to core.dump" in result.output
        
        mock_client.device_debug.collect_core_dump.assert_called_once()
        mock_file.assert_called_once_with("core.dump", "wb")
        mock_file().write.assert_called_once_with(b"core dump data")

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    @patch("builtins.open")
    def test_download_server_report_file_error(self, mock_file, mock_create_client, runner, mock_client):
        """Test download server report with file error."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        mock_file.side_effect = IOError("Permission denied")
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "download-server-report", "/invalid/path/report.tar.gz"])
        
        assert "Error saving file: Permission denied" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    def test_download_server_report_api_error(self, mock_create_client, runner, mock_client):
        """Test download server report with API error."""
        error = FeatureError("Failed to download server report", 500, {"error": "Internal server error"})
        mock_client.device_debug.download_server_report.side_effect = error
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "download-server-report", "report.tar.gz"])
        
        assert isinstance(result.exception, FeatureError)
        assert "Failed to download server report" in str(result.exception)

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_debug_cli.create_client")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_network_trace_default_params(self, mock_file, mock_create_client, runner, mock_client):
        """Test download network trace with default parameters."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "download-network-trace", "trace.pcap"])
        
        assert result.exit_code == 0
        assert "Network trace saved to trace.pcap" in result.output
        mock_client.device_debug.download_network_trace.assert_called_once_with(duration=30, interface=None)
        mock_file.assert_called_once_with("trace.pcap", "wb")
        mock_file().write.assert_called_once_with(b"network trace data") 