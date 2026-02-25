"""Tests for device-related features."""

import time
import pytest

class TestDeviceInfoFeature:
    """Test suite for device feature."""
    
    @pytest.mark.integration
    def test_get_info(self, client):
        """Test device info retrieval."""
        info = client.device.get_info()
        assert info.get("model"), "Model should not be empty"
        assert info.get("product_number"), "Product number should not be empty"
        assert info.get("product_type"), "Product type should not be empty"
        assert info.get("serial_number"), "Serial number should not be empty"
        assert info.get("hardware_id"), "Hardware ID should not be empty"
        assert info.get("firmware_version"), "Firmware version should not be empty"
        assert info.get("build_date"), "Build date should not be empty"
        assert isinstance(info.get("ptz_support"), list), "PTZ support should be a list"
        assert isinstance(info.get("analytics_support"), bool), "Analytics support should be a boolean"
        assert isinstance(info.get("metadata_support"), bool), "Metadata support should be a boolean"
        assert isinstance(info.get("Onvif Replay Extention"), bool), "Onvif Replay Extension support should be a boolean"

    @pytest.mark.integration
    def test_get_info_no_auth(self, client):
        """Test unauthenticated device info retrieval via basicdeviceinfo.cgi."""
        info = client.device.get_info_no_auth()
        assert isinstance(info, dict), "Response should be a dictionary"
        assert len(info) > 0, "Response should contain at least one property"

    @pytest.mark.integration
    def test_get_info_auth(self, client):
        """Test authenticated device info retrieval via basicdeviceinfo.cgi."""
        info = client.device.get_info_auth()
        assert isinstance(info, dict), "Response should be a dictionary"
        assert len(info) > 0, "Response should contain at least one property"

    @pytest.mark.integration
    def test_get_info_auth_has_more_than_no_auth(self, client):
        """Authenticated info should return at least as many properties as unauthenticated."""
        no_auth_info = client.device.get_info_no_auth()
        auth_info = client.device.get_info_auth()
        assert len(auth_info) >= len(no_auth_info), (
            "Authenticated response should have at least as many properties as unauthenticated"
        )
    
    @pytest.mark.skip_health_check
    @pytest.mark.integration
    def test_health_check(self, client):
        """Test device health check."""
        health = client.device.check_health()
        assert health, "Health check should be successful"
    
    @pytest.mark.restart
    @pytest.mark.slow
    @pytest.mark.skip_health_check
    def test_restart(self, client):
        """Test device restart functionality.
        
        Note: This test is skipped by default as it's potentially disruptive.
        To run this test, use: pytest -v tests/ --run-restart
        """
        restart = client.device.restart()
        
        # Wait for device to actually go down (max 30 seconds)
        max_down_attempts = 6
        for attempt in range(max_down_attempts):
            try:
                health = client.device.check_health()
            except:
                break
            time.sleep(5)
        else:
            pytest.fail("Device did not go down after restart command")
            
        # Now wait for device to come back (max 60 seconds)
        max_up_attempts = 12
        for attempt in range(max_up_attempts):
            try:
                health = client.device.check_health()
            except:
                pass
            time.sleep(5)
        else:
            pytest.fail(f"Device did not come back online after {max_up_attempts * 5} seconds")
        
        # Verify device is fully healthy
        final_health = client.device.check_health()