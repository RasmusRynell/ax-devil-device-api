"""Tests for API discovery CLI."""

import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, ANY
from ax_devil_device_api.examples.api_discovery_cli import cli
from ax_devil_device_api.utils.errors import FeatureError

# Mock API data
class MockApi:
    def __init__(self, name, version, state="released", version_string=None):
        self.name = name
        self.version = version
        self.state = state
        self.version_string = version_string or f"v{version}"
        self.rest_api_url = f"/api/{name}/{version}"
        self.rest_ui_url = f"/api/{name}/{version}/ui"
        self._urls = {
            'doc': f"/api/{name}/{version}/doc",
            'doc_html': f"/api/{name}/{version}/doc-html",
            'model': f"/api/{name}/{version}/model",
            'rest_openapi': f"/api/{name}/{version}/openapi"
        }
    
    def get_documentation(self):
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.data = "# Markdown Documentation\n\nThis is the API documentation."
        return mock_response.data
    
    def get_documentation_html(self):
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.data = "<html>HTML Documentation</html>"
        return mock_response.data
    
    def get_model(self):
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.data = {"model": "data"}
        return mock_response.data
    
    def get_openapi_spec(self):
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.data = {"openapi": "3.0.0"}
        return mock_response.data

# Mock APIs collection
class MockApis:
    def __init__(self, apis):
        self.apis = apis
    
    def get_all_apis(self):
        return self.apis
    
    def get_api(self, name, version=None):
        if version:
            for api in self.apis:
                if api.name == name and api.version == version:
                    return api
            return None
        
        # Return latest version if no specific version requested
        matching_apis = [api for api in self.apis if api.name == name]
        if not matching_apis:
            return None
        
        # Sort by version and return the latest
        return sorted(matching_apis, key=lambda x: x.version, reverse=True)[0]
    
    def get_apis_by_name(self, name):
        return [api for api in self.apis if api.name == name]

# Test data
MOCK_APIS = [
    MockApi("analytics", "1.0"),
    MockApi("analytics", "2.0"),
    MockApi("events", "1.0", state="beta"),
    MockApi("discovery", "1.0")
]

class TestApiDiscoveryCli:
    """Test suite for API Discovery CLI."""

    @pytest.fixture
    def runner(self):
        """Fixture for CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Fixture for mock client."""
        mock = MagicMock()
        mock.discovery = MagicMock()
        mock.discovery.discover = MagicMock(return_value=MockApis(MOCK_APIS))
        return mock

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_list_apis(self, mock_create_client, runner, mock_client):
        """Test list APIs command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "list"])
        
        assert result.exit_code == 0
        assert "Found 4 APIs:" in result.output
        assert "analytics 1.0" in result.output
        assert "analytics 2.0" in result.output
        assert "events 1.0" in result.output
        assert "discovery 1.0" in result.output
        
        mock_client.discovery.discover.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_list_apis_error(self, mock_create_client, runner, mock_client):
        """Test list APIs command with error."""
        error = FeatureError("Failed to discover APIs", 500, {"error": "Internal error"})
        mock_client.discovery.discover.side_effect = error
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, ["--device-ip", "192.168.0.90", "list"])
        
        assert "Failed to discover APIs" in result.output
        assert "Error" in result.output or "ERROR" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_get_api_info(self, mock_create_client, runner, mock_client):
        """Test get API info command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "analytics"
        ])
        
        assert result.exit_code == 0
        assert "API: analytics 2.0" in result.output  # Should get latest version
        assert "State: released" in result.output
        assert "Version: v2.0" in result.output
        
        mock_client.discovery.discover.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_get_api_info_with_version(self, mock_create_client, runner, mock_client):
        """Test get API info command with specific version."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "analytics", "--version", "1.0"
        ])
        
        assert result.exit_code == 0
        assert "API: analytics 1.0" in result.output
        assert "State: released" in result.output
        assert "Version: v1.0" in result.output
        
        mock_client.discovery.discover.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_get_api_info_not_found(self, mock_create_client, runner, mock_client):
        """Test get API info command for non-existent API."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "nonexistent"
        ], catch_exceptions=False)
        
        assert "Error: API nonexistent not found" in result.output
        
        mock_client.discovery.discover.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_get_api_info_version_not_found(self, mock_create_client, runner, mock_client):
        """Test get API info command for non-existent API version."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "analytics", "--version", "3.0"
        ], catch_exceptions=False)
        
        assert "Error: API analytics version 3.0 not found" in result.output
        
        mock_client.discovery.discover.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    @patch("ax_devil_device_api.examples.api_discovery_cli.webbrowser.open")
    def test_get_api_info_with_docs_md(self, mock_webbrowser, mock_create_client, runner, mock_client):
        """Test get API info command with docs-md option."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "analytics", "--docs-md"
        ])
        
        assert result.exit_code == 0
        assert "Markdown Documentation:" in result.output
        assert "Opening in browser..." in result.output
        
        mock_webbrowser.assert_called_once()
        url_arg = mock_webbrowser.call_args[0][0]
        assert "https://192.168.0.90/api/analytics/2.0/doc" in url_arg

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_get_api_info_with_docs_md_raw(self, mock_create_client, runner, mock_client):
        """Test get API info command with docs-md-raw option."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "analytics", "--docs-md-raw"
        ])
        
        assert result.exit_code == 0
        assert "Markdown Documentation:" in result.output
        assert "Fetching content:" in result.output
        assert "# Markdown Documentation" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_get_api_info_with_docs_md_link(self, mock_create_client, runner, mock_client):
        """Test get API info command with docs-md-link option."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "analytics", "--docs-md-link"
        ])
        
        assert result.exit_code == 0
        assert "Markdown Documentation:" in result.output
        assert "URL:" in result.output
        assert "https://192.168.0.90/api/analytics/2.0/doc" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_get_api_info_with_model_raw(self, mock_create_client, runner, mock_client):
        """Test get API info command with model-raw option."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "info", "analytics", "--model-raw"
        ])
        
        assert result.exit_code == 0
        assert "API Model:" in result.output
        assert "Fetching content:" in result.output
        assert "model" in result.output
        assert "data" in result.output

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_list_versions(self, mock_create_client, runner, mock_client):
        """Test list versions command."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "versions", "analytics"
        ])
        
        assert result.exit_code == 0
        assert "Found 2 versions of analytics:" in result.output
        assert "1.0 (v1.0)" in result.output
        assert "2.0 (v2.0)" in result.output
        assert "State: released" in result.output
        
        mock_client.discovery.discover.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_list_versions_not_found(self, mock_create_client, runner, mock_client):
        """Test list versions command for non-existent API."""
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "versions", "nonexistent"
        ], catch_exceptions=False)
        
        assert "Error: API nonexistent not found" in result.output
        
        mock_client.discovery.discover.assert_called_once()

    @pytest.mark.unit
    @patch("ax_devil_device_api.examples.api_discovery_cli.create_client")
    def test_list_versions_error(self, mock_create_client, runner, mock_client):
        """Test list versions command with error."""
        error = FeatureError("Failed to discover APIs", 500, {"error": "Internal error"})
        mock_client.discovery.discover.side_effect = error
        mock_create_client.return_value.__enter__.return_value = mock_client
        
        result = runner.invoke(cli, [
            "--device-ip", "192.168.0.90", 
            "versions", "analytics"
        ])
        
        assert "Failed to discover APIs" in result.output
        assert "Error" in result.output or "ERROR" in result.output 