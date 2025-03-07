"""Tests for geocoordinates operations."""

import pytest
from ax_devil_device_api.features.geocoordinates import GeoCoordinatesLocation, GeoCoordinatesOrientation, GeoCoordinatesClient
from ax_devil_device_api.utils.errors import FeatureError

class TestGeoCoordinatesLocation:
    """Test suite for geocoordinates location features."""
    
    @pytest.mark.integration
    def test_get_location_success(self, client):
        """Test successful location retrieval."""
        response = client.geocoordinates.get_location()
        assert response.is_success, f"Failed to get location: {response.error}"
        assert isinstance(response.data, GeoCoordinatesLocation)
        # Note: We don't validate ranges, we trust the device's response
        assert response.data.is_valid is not None
        
    @pytest.mark.integration
    def test_set_location_success(self, client):
        """Test successful location update."""
        # Get initial state
        initial = client.geocoordinates.get_location()
        assert initial.is_success, "Failed to get initial location"
        
        # Set new location
        response = client.geocoordinates.set_location(latitude=45.0, longitude=90.0)
        assert response.is_success, f"Failed to set location: {response.error}"
        assert response.data is True
        
        # Verify the update
        get_response = client.geocoordinates.get_location()
        assert get_response.is_success, "Failed to get updated location"
        assert get_response.data.latitude == 45.0
        assert get_response.data.longitude == 90.0
        
        # Reset to initial state
        if initial.is_success:
            client.geocoordinates.set_location(
                latitude=initial.data.latitude,
                longitude=initial.data.longitude
            )
            
    @pytest.mark.unit
    def test_location_info_from_params(self):
        """Test GeoCoordinatesLocation creation from parameters."""
        params = {
            "Geolocation.Latitude": "45.0",
            "Geolocation.Longitude": "90.0"
        }
        info = GeoCoordinatesLocation.from_params(params)
        assert info.latitude == 45.0
        assert info.longitude == 90.0
        
        # Test with missing parameters
        with pytest.raises(ValueError):
            GeoCoordinatesLocation.from_params({})

class TestGeoCoordinatesOrientation:
    """Test suite for geocoordinates orientation features."""
    
    @pytest.mark.integration
    def test_get_orientation_success(self, client):
        """Test successful orientation retrieval."""
        response = client.geocoordinates.get_orientation()
        assert response.is_success, f"Failed to get orientation: {response.error}"
        assert isinstance(response.data, GeoCoordinatesOrientation)
        assert response.data.is_valid is not None
            
    @pytest.mark.integration
    def test_set_orientation_success(self, client):
        """Test successful orientation update."""
        # Get initial state
        initial = client.geocoordinates.get_orientation()
        assert initial.is_success, "Failed to get initial orientation"
        
        # Set new orientation
        orientation = GeoCoordinatesOrientation(
            heading=180.0,
            tilt=45.0,
            roll=0.0,
            installation_height=2.5
        )
        response = client.geocoordinates.set_orientation(orientation)
        assert response.is_success, f"Failed to set orientation: {response.error}"
        assert response.data is True
        
        # Verify the update
        get_response = client.geocoordinates.get_orientation()
        assert get_response.is_success, "Failed to get updated orientation"
        assert get_response.data.heading == 180.0
        assert get_response.data.tilt == 45.0
        assert get_response.data.roll == 0.0
        assert get_response.data.installation_height == 2.5
        
        # Reset to initial state
        if initial.is_success:
            client.geocoordinates.set_orientation(initial.data)
        
    @pytest.mark.integration
    def test_set_orientation_partial(self, client):
        """Test partial orientation update."""
        # Get initial state
        initial = client.geocoordinates.get_orientation()
        assert initial.is_success, "Failed to get initial orientation"
        
        # Set only heading
        orientation = GeoCoordinatesOrientation(heading=90.0)
        response = client.geocoordinates.set_orientation(orientation)
        assert response.is_success, f"Failed to set partial orientation: {response.error}"
        
        # Verify update - heading changed, others unchanged
        get_response = client.geocoordinates.get_orientation()
        assert get_response.is_success, "Failed to get updated orientation"
        assert get_response.data.heading == 90.0
        if initial.is_success:
            assert get_response.data.tilt == initial.data.tilt
            assert get_response.data.roll == initial.data.roll
            assert get_response.data.installation_height == initial.data.installation_height
            
        # Reset to initial state
        if initial.is_success:
            client.geocoordinates.set_orientation(initial.data)
            
    @pytest.mark.unit
    def test_orientation_info_from_params(self):
        """Test GeoCoordinatesOrientation creation from parameters."""
        params = {
            "GeoOrientation.Heading": "180.0",
            "GeoOrientation.Tilt": "45.0",
            "GeoOrientation.Roll": "0.0",
            "GeoOrientation.InstallationHeight": "2.5"
        }
        info = GeoCoordinatesOrientation.from_params(params)
        assert info.heading == 180.0
        assert info.tilt == 45.0
        assert info.roll == 0.0
        assert info.installation_height == 2.5
        
        # Test with missing parameters (should be None)
        empty_info = GeoCoordinatesOrientation.from_params({})
        assert empty_info.heading is None
        assert empty_info.tilt is None
        assert empty_info.roll is None
        assert empty_info.installation_height is None
        
    @pytest.mark.integration
    def test_apply_settings_success(self, client):
        """Test successful settings application."""
        # Get initial state
        initial = client.geocoordinates.get_orientation()
        assert initial.is_success, "Failed to get initial orientation"
        
        # Set new orientation
        orientation = GeoCoordinatesOrientation(heading=270.0)
        set_response = client.geocoordinates.set_orientation(orientation)
        assert set_response.is_success, "Failed to set orientation"
        
        # Apply settings
        response = client.geocoordinates.apply_settings()
        assert response.is_success, f"Failed to apply settings: {response.error}"
        assert response.data is True
        
        # Verify changes were applied
        get_response = client.geocoordinates.get_orientation()
        assert get_response.is_success, "Failed to get updated orientation"
        assert get_response.data.heading == 270.0
        
        # Reset to initial state
        if initial.is_success:
            client.geocoordinates.set_orientation(initial.data)
            client.geocoordinates.apply_settings() 