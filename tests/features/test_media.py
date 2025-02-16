"""Tests for media operations."""

import pytest
from ax_devil_device_api.features.media import MediaConfig
from ax_devil_device_api.utils.errors import FeatureError

class TestMediaFeature:
    """Test suite for media feature."""
    
    def test_get_snapshot_default(self, client):
        """Test snapshot capture with default settings."""
        response = client.media.get_snapshot()
        assert response.success, f"Failed to get snapshot: {response.error}"
        self._verify_snapshot_data(response.data)
        
    def test_get_snapshot_with_config(self, client):
        """Test snapshot capture with custom configuration."""
        config = MediaConfig(
            resolution="1280x720",
            compression=75,
            rotation=0
        )
        response = client.media.get_snapshot(config)
        assert response.success, f"Failed to get snapshot: {response.error}"
        self._verify_snapshot_data(response.data)
        
    def test_invalid_compression(self, client):
        """Test error handling for invalid compression value."""
        config = MediaConfig(compression=101)  # Invalid: > 100
        response = client.media.get_snapshot(config)
        assert not response.success
        assert response.error.code == "invalid_config"
        assert "Compression" in response.error.message
        
    def test_invalid_rotation(self, client):
        """Test error handling for invalid rotation value."""
        config = MediaConfig(rotation=45)  # Invalid: not 0/90/180/270
        response = client.media.get_snapshot(config)
        assert not response.success
        assert response.error.code == "invalid_config"
        assert "Rotation" in response.error.message
        
    def test_mediaconfig_validation(self):
        """Test MediaConfig validation logic."""
        # Valid configurations
        valid_configs = [
            MediaConfig(),  # Default values
            MediaConfig(resolution="1920x1080"),
            MediaConfig(compression=1),
            MediaConfig(compression=100),
            MediaConfig(rotation=0),
            MediaConfig(rotation=90),
            MediaConfig(rotation=180),
            MediaConfig(rotation=270),
            MediaConfig(camera_head=1)
        ]
        for config in valid_configs:
            assert config.validate() is None, f"Valid config failed validation: {config}"
            
        # Invalid configurations
        invalid_configs = [
            (MediaConfig(compression=0), "Compression"),
            (MediaConfig(compression=101), "Compression"),
            (MediaConfig(rotation=45), "Rotation"),
            (MediaConfig(rotation=360), "Rotation")
        ]
        for config, expected_error in invalid_configs:
            error = config.validate()
            assert error is not None, f"Invalid config passed validation: {config}"
            assert expected_error in error
            
    def test_mediaconfig_to_params(self):
        """Test MediaConfig parameter conversion."""
        config = MediaConfig(
            resolution="1280x720",
            compression=75,
            camera_head=1,
            rotation=90
        )
        params = config.to_params()
        
        assert params["resolution"] == "1280x720"
        assert params["compression"] == "75"
        assert params["camera"] == "1"
        assert params["rotation"] == "90"
        
        # Test partial configuration
        partial_config = MediaConfig(resolution="640x480")
        params = partial_config.to_params()
        assert len(params) == 1
        assert params["resolution"] == "640x480"
        
    def _verify_snapshot_data(self, data):
        """Helper to verify snapshot response data."""
        assert isinstance(data, bytes), "Snapshot data should be bytes"
        assert len(data) > 0, "Snapshot data should not be empty"
        
        # Basic JPEG header check (FF D8)
        assert data[:2] == b'\xFF\xD8', "Data should start with JPEG header"
        # Basic JPEG footer check (FF D9)
        assert data[-2:] == b'\xFF\xD9', "Data should end with JPEG footer" 