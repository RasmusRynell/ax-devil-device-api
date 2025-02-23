"""Tests for device-related features."""

import time
import pytest

class TestDeviceInfoFeature:
    """Test suite for device feature."""
    
    def test_get_info(self, client):
        """Test device info retrieval."""
        info = client.device.get_info()
        assert info.is_success, f"Failed to get device info: {info.error}"
        self._verify_device_info(info)
        
    def _verify_device_info(self, info):
        """Helper to verify device info response."""
        assert info.data.model, "Model should not be empty"
        assert info.data.product_number, "Product number should not be empty"
        assert info.data.product_type, "Product type should not be empty"
        assert info.data.serial_number, "Serial number should not be empty"
        assert info.data.hardware_id, "Hardware ID should not be empty"
        assert info.data.firmware_version, "Firmware version should not be empty"
        assert info.data.build_date, "Build date should not be empty"
        assert isinstance(info.data.ptz_support, list), "PTZ support should be a list"
        assert isinstance(info.data.analytics_support, bool), "Analytics support should be a boolean"
    
    @pytest.mark.skip_health_check
    def test_health_check(self, client):
        """Test device health check."""
        health = client.device.check_health()
        assert health.is_success, f"Health check failed: {health.error}"
    
    @pytest.mark.restart
    @pytest.mark.skip_health_check
    def test_restart(self, client):
        """Test device restart functionality.
        
        Note: This test is skipped by default as it's potentially disruptive.
        To run this test, use: pytest -v tests/ --run-restart
        """
        # Send restart command
        restart = client.device.restart()
        assert restart.is_success, f"Failed to restart device: {restart.error}"
        
        # Wait for device to actually go down (max 30 seconds)
        max_down_attempts = 6
        for attempt in range(max_down_attempts):
            try:
                health = client.device.check_health()
                if not health.is_success:  # Device is down!
                    break
            except:  # Network errors also indicate device is down
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