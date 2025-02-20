"""Tests for device-related features."""

import time
import pytest

class TestDeviceInfoFeature:
    """Test suite for device feature."""
    
    def test_get_info(self, client):
        """Test device info retrieval."""
        info = client.device.get_info()
        assert info.success, f"Failed to get device info: {info.error}"
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
        """Test camera health check."""
        health = client.device.check_health()
        assert health.success, f"Health check failed: {health.error}"
    
    @pytest.mark.restart
    @pytest.mark.skip_health_check
    def test_restart(self, client):
        """Test camera restart functionality.
        
        Note: This test is skipped by default as it's potentially disruptive.
        To run this test, use: pytest -v tests/ --run-restart
        """
        # Send restart command
        restart = client.device.restart()
        assert restart.success, f"Failed to restart camera: {restart.error}"
        
        # Wait for camera to actually go down (max 30 seconds)
        max_down_attempts = 6
        for attempt in range(max_down_attempts):
            try:
                health = client.device.check_health()
                if not health.success:  # Camera is down!
                    break
            except:  # Network errors also indicate camera is down
                break
            time.sleep(5)
        else:
            pytest.fail("Camera did not go down after restart command")
            
        # Now wait for camera to come back (max 60 seconds)
        max_up_attempts = 12
        for attempt in range(max_up_attempts):
            try:
                health = client.device.check_health()
                if health.success:
                    break
            except:
                pass
            time.sleep(5)
        else:
            pytest.fail(f"Camera did not come back online after {max_up_attempts * 5} seconds")
        
        # Verify camera is fully healthy
        final_health = client.device.check_health()
        assert final_health.success, "Camera is not healthy after restart" 