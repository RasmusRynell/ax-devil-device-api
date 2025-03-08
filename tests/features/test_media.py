"""Tests for media operations."""

import pytest

from ax_devil_device_api.utils.errors import FeatureError

class TestMediaFeature:
    """Test suite for media feature."""
    
    @pytest.mark.integration
    def test_get_snapshot_default(self, client):
        """Test snapshot capture with default settings."""
        response = client.media.get_snapshot(
            resolution="1920x1080",
            compression=0,
            rotation=0,
            camera_head=0
        )
        self._verify_snapshot_data(response)
        
    @pytest.mark.integration
    def test_get_snapshot_with_config(self, client):
        """Test snapshot capture with custom configuration."""
        response = client.media.get_snapshot(
            resolution="1280x720",
            compression=75,
            rotation=0,
            camera_head=0
        )
        self._verify_snapshot_data(response)
        
    @pytest.mark.unit
    def test_invalid_compression(self, client):
        """Test error handling for invalid compression value."""
        with pytest.raises(FeatureError) as e:
            client.media.get_snapshot(resolution="1920x1080", compression=101, rotation=0, camera_head=0)
        assert e.value.code == "invalid_parameter"
        assert "Compression" in e.value.message
        
    @pytest.mark.unit
    def test_invalid_rotation(self, client):
        """Test error handling for invalid rotation value."""
        with pytest.raises(FeatureError) as e:
            client.media.get_snapshot(resolution="1920x1080", compression=0, rotation=45, camera_head=0)
        assert e.value.code == "invalid_parameter"
        assert "Rotation" in e.value.message
        
    def _verify_snapshot_data(self, data):
        """Helper to verify snapshot response data."""
        assert isinstance(data, bytes), "Snapshot data should be bytes"
        assert len(data) > 0, "Snapshot data should not be empty"
        
        # Basic JPEG header check (FF D8)
        assert data[:2] == b'\xFF\xD8', "Data should start with JPEG header"
        # Basic JPEG footer check (FF D9)
        assert data[-2:] == b'\xFF\xD9', "Data should end with JPEG footer" 