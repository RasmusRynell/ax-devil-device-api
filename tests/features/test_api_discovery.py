"""Tests for API discovery feature."""

import pytest
from ax_devil_device_api.utils.errors import FeatureError

class TestAPIDiscoveryFeature:
    """Test suite for API discovery feature."""
    
    def test_discover(self, client):
        """Test basic API discovery."""
        result = client.discovery.discover()
        assert result.is_success, f"Failed to discover APIs: {result.error}"
        self._verify_discovery_result(result)
    
    def _verify_discovery_result(self, result):
        """Helper to verify discovery response."""
        # Verify collection structure
        assert hasattr(result.data, 'apis'), "Result should have apis attribute"
        assert isinstance(result.data.apis, dict), "APIs should be a dictionary"
        assert len(result.data.apis) > 0, "At least one API should be discovered"
        
        # Get first API for detailed verification
        first_api_name = next(iter(result.data.apis))
        first_api_versions = result.data.apis[first_api_name]
        assert isinstance(first_api_versions, dict), "API versions should be a dictionary"
        
        # Verify API version structure
        first_version = next(iter(first_api_versions.values()))
        assert first_version.name, "API should have a name"
        assert first_version.version, "API should have a version"
        assert first_version.state, "API should have a state"
        assert first_version.version_string, "API should have a version string"
        assert hasattr(first_version, '_urls'), "API should have URLs"
    
    def test_get_api_documentation(self, client):
        """Test fetching API documentation."""
        # First discover APIs
        discovery = client.discovery.discover()
        assert discovery.is_success, "Discovery failed"
        
        # Get first available API
        api = discovery.data.get_all_apis()[0]
        
        # Test markdown documentation
        doc_result = api.get_documentation()
        assert doc_result.is_success, f"Failed to get documentation: {doc_result.error}"
        assert isinstance(doc_result.data, str), "Documentation should be a string"
        assert len(doc_result.data) > 0, "Documentation should not be empty"
        
        # Test caching - second call should use cached data
        cached_result = api.get_documentation()
        assert cached_result.is_success
        assert cached_result.data == doc_result.data
        
        # Test HTML documentation
        html_result = api.get_documentation_html()
        assert html_result.is_success, f"Failed to get HTML documentation: {html_result.error}"
        assert isinstance(html_result.data, str), "HTML documentation should be a string"
        assert len(html_result.data) > 0, "HTML documentation should not be empty"
        
        # Test HTML caching
        cached_html = api.get_documentation_html()
        assert cached_html.is_success
        assert cached_html.data == html_result.data
    
    def test_get_api_model(self, client):
        """Test fetching API model."""
        discovery = client.discovery.discover()
        assert discovery.is_success, "Discovery failed"
        
        api = discovery.data.get_all_apis()[0]
        
        # Test model retrieval
        model_result = api.get_model()
        assert model_result.is_success, f"Failed to get model: {model_result.error}"
        assert isinstance(model_result.data, dict), "Model should be a dictionary"
        self._verify_model_structure(model_result.data)
        
        # Test caching
        cached_model = api.get_model()
        assert cached_model.is_success
        assert cached_model.data == model_result.data
    
    def _verify_model_structure(self, model):
        """Helper to verify model response structure."""
        # Model should have some basic structure
        assert isinstance(model, dict), "Model should be a dictionary"
        # Add more specific model structure checks based on your API model format
    
    def test_get_openapi_spec(self, client):
        """Test fetching OpenAPI specification."""
        discovery = client.discovery.discover()
        assert discovery.is_success, "Discovery failed"
        
        api = discovery.data.get_all_apis()[0]
        
        # Test OpenAPI spec retrieval
        spec_result = api.get_openapi_spec()
        assert spec_result.is_success, f"Failed to get OpenAPI spec: {spec_result.error}"
        assert isinstance(spec_result.data, dict), "OpenAPI spec should be a dictionary"
        self._verify_openapi_structure(spec_result.data)
        
        # Test caching
        cached_spec = api.get_openapi_spec()
        assert cached_spec.is_success
        assert cached_spec.data == spec_result.data
    
    def _verify_openapi_structure(self, spec):
        """Helper to verify OpenAPI spec structure."""
        # Basic OpenAPI structure checks
        assert 'openapi' in spec, "OpenAPI spec should have version"
        assert 'info' in spec, "OpenAPI spec should have info section"
        assert 'paths' in spec, "OpenAPI spec should have paths section"
    
    def test_api_collection_methods(self, client):
        """Test API collection helper methods."""
        discovery = client.discovery.discover()
        assert discovery.is_success, "Discovery failed"
        
        collection = discovery.data
        
        # Test get_all_apis
        all_apis = collection.get_all_apis()
        assert isinstance(all_apis, list), "get_all_apis should return a list"
        assert len(all_apis) > 0, "Should find at least one API"
        
        # Test get_api with specific version
        first_api = all_apis[0]
        found_api = collection.get_api(first_api.name, first_api.version)
        assert found_api is not None, "Should find API by name and version"
        assert found_api.name == first_api.name, "API names should match"
        assert found_api.version == first_api.version, "API versions should match"
        
        # Test get_api with latest version
        latest_api = collection.get_api(first_api.name)
        assert latest_api is not None, "Should find latest API version"
        
        # Test get_apis_by_name
        api_versions = collection.get_apis_by_name(first_api.name)
        assert isinstance(api_versions, list), "get_apis_by_name should return a list"
        assert len(api_versions) > 0, "Should find at least one version"
    
    def test_error_handling(self, client):
        """Test error handling for invalid requests."""
        discovery = client.discovery.discover()
        assert discovery.is_success, "Discovery failed"
        
        collection = discovery.data
        
        # Test non-existent API
        non_existent = collection.get_api("non_existent_api")
        assert non_existent is None, "Should return None for non-existent API"
        
        # Test non-existent version
        first_api = collection.get_all_apis()[0]
        non_existent_version = collection.get_api(first_api.name, "999.999")
        assert non_existent_version is None, "Should return None for non-existent version"
    
    def test_url_properties(self, client):
        """Test REST API and UI URL properties."""
        discovery = client.discovery.discover()
        assert discovery.is_success, "Discovery failed"
        
        api = discovery.data.get_all_apis()[0]
        
        # Test URL properties
        assert isinstance(api.rest_api_url, str), "REST API URL should be a string"
        assert isinstance(api.rest_ui_url, str), "Swagger UI URL should be a string"
        
        # Test default empty string for missing URLs
        api._urls['rest_api'] = None
        api._urls['rest_ui'] = None
        assert api.rest_api_url == 'No REST API available', "Missing REST API URL should return empty string"
        assert api.rest_ui_url == 'No REST UI available', "Missing Swagger UI URL should return empty string"
    
    def test_api_creation_edge_cases(self):
        """Test DiscoveredAPI creation with missing fields."""
        from ax_devil_device_api.features.api_discovery import DiscoveredAPI
        
        # Test with minimal data
        minimal_api = DiscoveredAPI.from_discovery_data("test-api", "v1", {})
        assert minimal_api.state == "unknown", "Missing state should default to 'unknown'"
        assert minimal_api.version_string == "unknown", "Missing version should default to 'unknown'"
        assert all(url is None for url in minimal_api._urls.values()), "Missing URLs should be None"
        
        # Test with partial data
        partial_data = {
            "state": "beta",
            "doc": "/api/doc",
            # version_string missing
        }
        partial_api = DiscoveredAPI.from_discovery_data("test-api", "v1", partial_data)
        assert partial_api.state == "beta"
        assert partial_api.version_string == "unknown"
        assert partial_api._urls["doc"] == "/api/doc"
    
    def test_client_initialization(self, client):
        """Test client initialization checks."""
        discovery = client.discovery.discover()
        assert discovery.is_success, "Discovery failed"
        
        api = discovery.data.get_all_apis()[0]
        
        # Test with uninitialized client
        api._client = None
        with pytest.raises(RuntimeError) as exc_info:
            api.get_documentation()
        assert "not properly initialized" in str(exc_info.value) 