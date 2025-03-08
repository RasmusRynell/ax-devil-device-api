"""Tests for device info CLI."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from ax_devil_device_api.examples.device_info_cli import cli
from ax_devil_device_api.utils.errors import FeatureError, NetworkError, AuthenticationError


# Mock device info data
class MockDeviceInfo:
    def __init__(self):
        self.model = "AXIS Q1615 Mk III"
        self.serial_number = "ACCC12345678"
        self.firmware_version = "10.9.0"
        self.hardware_id = "12345"
        self.device_name = "Test Camera"
        self.mac_address = "00:40:8C:12:34:56"
        self.ip_address = "192.168.0.90"


class TestDeviceInfoCli:
    """Test suite for Device Info CLI."""

    @pytest.fixture
    def runner(self):
        """Fixture for CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Fixture for mock client."""
        mock = MagicMock()
        
        mock_info_response = MagicMock()
        mock_info_response.is_success = True
        mock_info_response.data = MockDeviceInfo()
        mock.device.get_info.return_value = mock_info_response
        
        mock_health_response = MagicMock()
        mock_health_response.is_success = True
        mock_health_response.data = True
        mock.device.check_health.return_value = mock_health_response
        
        mock_restart_response = MagicMock()
        mock_restart_response.is_success = True
        mock_restart_response.data = True
        mock.device.restart.return_value = mock_restart_response
        
        return mock

    @pytest.mark.unit
    @pytest.mark.basic_operation
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_get_info(self, mock_create_client, runner, mock_client):
        """Test get info command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "info"])
        
        assert result.exit_code == 0
        assert "Device Information:" in result.output
        assert "model: AXIS Q1615 Mk III" in result.output
        assert "serial_number: ACCC12345678" in result.output
        assert "firmware_version: 10.9.0" in result.output
        assert "hardware_id: 12345" in result.output
        assert "device_name: Test Camera" in result.output
        assert "mac_address: 00:40:8C:12:34:56" in result.output
        assert "ip_address: 192.168.0.90" in result.output
        
        mock_client.device.get_info.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.error
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_get_info_error(self, mock_create_client, runner, mock_client):
        """Test get info command with error."""
        error = FeatureError("DEVICE_INFO_ERROR", "Failed to get device info", {"error": "Internal error"})
        mock_info_response = MagicMock()
        mock_info_response.is_success = False
        mock_info_response.error = error
        mock_client.device.get_info.return_value = mock_info_response
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "info"])
        
        assert "Failed to get device info" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @pytest.mark.basic_operation
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_check_health(self, mock_create_client, runner, mock_client):
        """Test health check command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "health"])
        
        assert result.exit_code == 0
        assert "Device is healthy!" in result.output
        
        mock_client.device.check_health.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.error
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_check_health_error(self, mock_create_client, runner, mock_client):
        """Test health check command with error."""
        error = FeatureError("HEALTH_CHECK_ERROR", "Failed to check device health", {"error": "Internal error"})
        mock_health_response = MagicMock()
        mock_health_response.is_success = False
        mock_health_response.error = error
        mock_client.device.check_health.return_value = mock_health_response
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "health"])
        
        assert "Failed to check device health" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    @patch("ax_devil_device_api.examples.device_info_cli.click.confirm")
    def test_restart_with_confirmation(self, mock_confirm, mock_create_client, runner, mock_client):
        """Test restart command with confirmation."""
        mock_confirm.return_value = True
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "restart"])
        
        assert result.exit_code == 0
        assert "Device restart initiated" in result.output
        
        mock_client.device.restart.assert_called_once()
        mock_confirm.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    @patch("ax_devil_device_api.examples.device_info_cli.click.confirm")
    def test_restart_cancelled(self, mock_confirm, mock_create_client, runner, mock_client):
        """Test restart command with cancelled confirmation."""
        mock_confirm.return_value = False
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "restart"])
        
        assert result.exit_code == 0
        assert "Restart cancelled" in result.output
        
        mock_client.device.restart.assert_not_called()
        mock_confirm.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_restart_with_force(self, mock_create_client, runner, mock_client):
        """Test restart command with force flag."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "restart", "--force"])
        
        assert result.exit_code == 0
        assert "Device restart initiated" in result.output
        
        mock_client.device.restart.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.error
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_restart_error(self, mock_create_client, runner, mock_client):
        """Test restart command with error."""
        error = FeatureError("RESTART_ERROR", "Failed to restart device", {"error": "Internal error"})
        mock_restart_response = MagicMock()
        mock_restart_response.is_success = False
        mock_restart_response.error = error
        mock_client.device.restart.return_value = mock_restart_response
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "restart", "--force"])
        
        assert "Failed to restart device" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @pytest.mark.error
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_exception_handling(self, mock_create_client, runner):
        """Test exception handling in commands."""
        mock_client = MagicMock()
        mock_client.device.get_info.side_effect = Exception("Unexpected error")
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "info"])
        
        assert "Unexpected error" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @pytest.mark.transport
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_network_error(self, mock_create_client, runner):
        """Test network error handling."""
        mock_client = MagicMock()
        mock_client.device.get_info.side_effect = NetworkError("NETWORK_ERROR", 
                                                              "Failed to connect to device", 
                                                              {"host": "192.168.0.90", "port": 80})
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "info"])
        
        assert "NETWORK_ERROR" in result.output
        assert "Failed to connect to device" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @pytest.mark.auth
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_authentication_error(self, mock_create_client, runner):
        """Test authentication error handling."""
        mock_client = MagicMock()
        mock_client.device.get_info.side_effect = AuthenticationError("AUTH_ERROR", 
                                                                     "Invalid credentials", 
                                                                     {"status_code": 401})
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "info"])
        
        assert "AUTH_ERROR" in result.output
        assert "Invalid credentials" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @pytest.mark.http
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_with_http_protocol(self, mock_create_client, runner, mock_client):
        """Test using HTTP protocol."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "--protocol", "http", 
            "info"
        ])
        
        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        args = mock_create_client.call_args[1]
        assert args["protocol"] == "http"

    @pytest.mark.unit
    @pytest.mark.https
    @patch("ax_devil_device_api.examples.device_info_cli.create_client")
    def test_with_https_protocol(self, mock_create_client, runner, mock_client):
        """Test using HTTPS protocol."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        # Call the CLI with the --no-verify-ssl flag
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "--protocol", "https", 
            "--no-verify-ssl",
            "info"
        ])
        
        assert result.exit_code == 0
        
        # Verify create_client was called
        mock_create_client.assert_called_once()
        
        # Get the keyword arguments passed to create_client
        call_kwargs = mock_create_client.call_args[1]
        
        # Verify the protocol is https
        assert call_kwargs["protocol"] == "https"
        
        # Verify no_verify_ssl is in the kwargs
        assert "no_verify_ssl" in call_kwargs
        
        # Test a different scenario without the flag to ensure the test is valid
        mock_create_client.reset_mock()
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "--protocol", "https",
            "info"
        ])
        
        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        
        # Get the keyword arguments for the second call
        call_kwargs_2 = mock_create_client.call_args[1]
        
        # Verify the protocol is still https
        assert call_kwargs_2["protocol"] == "https"
        
        # Verify no_verify_ssl is still in the kwargs
        assert "no_verify_ssl" in call_kwargs_2
        
        # The key test: the value should be different between the two calls
        assert call_kwargs["no_verify_ssl"] != call_kwargs_2["no_verify_ssl"]
