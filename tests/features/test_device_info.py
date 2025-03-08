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
        assert restart.is_success, f"Failed to restart device: {restart.error}"
        
        # Wait for device to actually go down (max 30 seconds)
        max_down_attempts = 6
        for attempt in range(max_down_attempts):
            try:
                health = client.device.check_health()
                if not health.is_success:
                    break
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
                if health.is_success:
                    break
            except:
                pass
            time.sleep(5)
        else:
            pytest.fail(f"Device did not come back online after {max_up_attempts * 5} seconds")
        
        # Verify device is fully healthy
        final_health = client.device.check_health()
        assert final_health.is_success, "Device is not healthy after restart" 