"""Tests for the systemready feature."""

import pytest

from src.ax_devil_device_api.features.systemready import SystemReadyClient


class TestSystemReadyFeature:
    """Test suite for the systemready feature."""

    @pytest.mark.integration
    def test_systemready(self, client):
        """Test systemready on a real device."""
        data = client.systemready.systemready(timeout=20)
        assert isinstance(data, dict)
        assert data.get("systemready") in ("yes", "no")
        assert "bootid" in data

    @pytest.mark.integration
    def test_get_supported_versions(self, client):
        """Test getSupportedVersions on a real device."""
        versions = client.systemready.get_supported_versions()
        assert isinstance(versions, list)
        assert len(versions) > 0
        assert all(isinstance(v, str) for v in versions)
