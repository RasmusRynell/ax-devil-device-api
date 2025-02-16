"""Tests for network-related features."""

class TestNetworkFeature:
    """Test suite for network feature."""
    
    def test_get_network_info(self, client):
        """Test network interface information retrieval."""
        info = client.network.get_network_info()
        assert info.success, f"Failed to get network info: {info.error}"
        self._verify_network_info(info)
        
    def test_get_network_info_custom_interface(self, client):
        """Test network info retrieval for non-default interface."""
        # Test with a non-existent interface to verify error handling
        info = client.network.get_network_info("eth99")
        
        # Should still succeed but have default/empty values
        assert info.success, f"Network info request failed: {info.error}"
        assert info.data.interface_name == "eth99"
        assert info.data.ip_address == "unknown"
        
    def _verify_network_info(self, info):
        """Helper to verify network info response."""
        assert info.data.interface_name, "Interface name should not be empty"
        
        # Network info validation - relaxed requirements
        # Some cameras might not expose all information or might have different configurations
        assert isinstance(info.data.mac_address, str), "MAC address should be string"
        assert isinstance(info.data.ip_address, str), "IP address should be string"
        assert isinstance(info.data.subnet_mask, str), "Subnet mask should be string"
        assert isinstance(info.data.gateway, str), "Gateway should be string"
        assert isinstance(info.data.dns_servers, list), "DNS servers should be a list"
        assert isinstance(info.data.link_status, bool), "Link status should be boolean"
        
        # If we have non-unknown values, validate their format
        if info.data.mac_address != "unknown":
            # Basic MAC address format check (6 pairs of hex digits)
            assert len(info.data.mac_address.replace(":", "").replace("-", "")) == 12, \
                "MAC address should be 12 hex digits"
                
        if info.data.ip_address != "unknown":
            # Basic IP address format check (4 octets)
            octets = info.data.ip_address.split(".")
            assert len(octets) == 4, "IP address should have 4 octets"
            assert all(o.isdigit() and 0 <= int(o) <= 255 for o in octets), \
                "IP address octets should be 0-255"
        
        # Optional fields with type checking only when present
        if info.data.link_speed is not None:
            assert isinstance(info.data.link_speed, int), "Link speed should be integer"
            assert info.data.link_speed >= 0, "Link speed should be non-negative"
            
        if info.data.duplex_mode:
            assert info.data.duplex_mode.lower() in ("full", "half", "unknown"), \
                "Invalid duplex mode" 