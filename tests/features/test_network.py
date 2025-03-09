"""Tests for network-related features."""
import pytest

class TestNetworkFeature:
    """Test suite for network feature."""
    
    @pytest.mark.integration
    def test_get_network_info(self, client):
        """Test network interface information retrieval."""
        info = client.network.get_network_info()
        assert len(info) > 0, "Network info should not be empty"
