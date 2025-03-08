"""Tests for feature flag operations."""

import pytest
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
        assert isinstance(list_response, list)
        assert len(list_response) > 0, "No feature flags found on device"
        
        # Take the first flag for testing
        test_flag = list_response[0]
        original_value = test_flag.get("value")
        new_value = not original_value
        
        try:
            # Set the flag to a new value
            set_response = client.feature_flags.set_flags({test_flag.get("name"): new_value})
            assert set_response == "Success"
            
            # Verify the change
            get_response = client.feature_flags.get_flags([test_flag.get("name")])
            assert get_response, f"Failed to get flag: {get_response.error}"
            assert isinstance(get_response, dict)
            assert test_flag.get("name") in get_response
            assert get_response[test_flag.get("name")] == new_value
            
        finally:
            # Restore original value
            restore_response = client.feature_flags.set_flags({test_flag.get("name"): original_value})
            assert restore_response == "Success"
    
    @pytest.mark.unit
    def test_get_flags_empty(self, client):
        """Test error handling for empty flag names."""
        with pytest.raises(FeatureError) as exc_info:
            client.feature_flags.get_flags([])
        assert exc_info.value.code == "invalid_request"
        assert "No flag names" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_set_flags_empty(self, client):
        """Test error handling for empty flag values."""
        with pytest.raises(FeatureError) as exc_info:
            client.feature_flags.set_flags({})
        assert exc_info.value.code == "invalid_request"
        assert "No flag values" in str(exc_info.value)
    
    @pytest.mark.integration
    def test_get_supported_versions(self, client):
        """Test retrieving supported API versions."""
        response = client.feature_flags.get_supported_versions()
        assert response
        assert isinstance(response, list)
        assert all(isinstance(version, str) for version in response)
        assert "1.0" in response  # API version 1.0 should be supported
