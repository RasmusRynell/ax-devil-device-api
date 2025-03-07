"""Tests for feature flag operations."""

import pytest
from ax_devil_device_api.features.feature_flags import FeatureFlag
from ax_devil_device_api.utils.errors import FeatureError


class TestFeatureFlagFeature:
    """Test suite for feature flag feature."""
    
    @pytest.mark.integration
    def test_list_and_modify_flags(self, client):
        """Test listing and modifying feature flags.
        
        This test:
        1. Lists all available flags
        2. Takes one flag and saves its original value
        3. Sets the flag to the opposite value
        4. Verifies the change
        5. Restores the original value
        """
        # First, list all flags
        list_response = client.feature_flags.list_all()
        assert list_response.is_success, f"Failed to list flags: {list_response.error}"
        assert isinstance(list_response.data, list)
        assert len(list_response.data) > 0, "No feature flags found on device"
        
        # Take the first flag for testing
        test_flag = list_response.data[0]
        original_value = test_flag.value
        new_value = not original_value
        
        try:
            # Set the flag to a new value
            set_response = client.feature_flags.set_flags({test_flag.name: new_value})
            assert set_response.is_success, f"Failed to set flag: {set_response.error}"
            
            # Verify the change
            get_response = client.feature_flags.get_flags([test_flag.name])
            assert get_response.is_success, f"Failed to get flag: {get_response.error}"
            assert isinstance(get_response.data, dict)
            assert test_flag.name in get_response.data
            assert get_response.data[test_flag.name] == new_value
            
        finally:
            # Restore original value
            restore_response = client.feature_flags.set_flags({test_flag.name: original_value})
            assert restore_response.is_success, f"Failed to restore flag: {restore_response.error}"
    
    @pytest.mark.integration
    def test_get_flags_empty(self, client):
        """Test error handling for empty flag names."""
        response = client.feature_flags.get_flags([])
        assert not response.is_success
        assert response.error.code == "invalid_request"
        assert "No flag names" in response.error.message
    
    @pytest.mark.integration
    def test_set_flags_empty(self, client):
        """Test error handling for empty flag values."""
        response = client.feature_flags.set_flags({})
        assert not response.is_success
        assert response.error.code == "invalid_request"
        assert "No flag values" in response.error.message
    
    @pytest.mark.integration
    def test_get_supported_versions(self, client):
        """Test retrieving supported API versions."""
        response = client.feature_flags.get_supported_versions()
        assert response.is_success, f"Failed to get versions: {response.error}"
        assert isinstance(response.data, list)
        assert all(isinstance(version, str) for version in response.data)
        assert "1.0" in response.data  # API version 1.0 should be supported
    
    @pytest.mark.unit
    def test_feature_flag_from_response(self):
        """Test FeatureFlag.from_response constructor."""
        data = {
            "name": "test.flag",
            "value": True,
            "defaultValue": False,
            "description": "Test flag description"
        }
        flag = FeatureFlag.from_response(data)
        assert flag.name == "test.flag"
        assert flag.value is True
        assert flag.default_value is False
        assert flag.description == "Test flag description"
        
        # Test with minimal data
        minimal_data = {
            "name": "minimal.flag",
            "value": False
        }
        flag = FeatureFlag.from_response(minimal_data)
        assert flag.name == "minimal.flag"
        assert flag.value is False
        assert flag.default_value is False  # Default value
        assert flag.description is None  # Optional field 