"""Tests for geocoordinates operations."""

import pytest
from ax_devil_device_api.features.geocoordinates import GeoCoordinatesParser
from ax_devil_device_api.utils.errors import FeatureError

class TestGeoCoordinatesLocation:
    """Test suite for geocoordinates location features."""
    
    @pytest.mark.integration
    def test_get_location_success(self, client):
        """Test successful location retrieval."""
        location = client.geocoordinates.get_location()
        assert isinstance(location, dict)
        assert "is_valid" in location
        assert "latitude" in location
        assert "longitude" in location
        
    @pytest.mark.integration
    def test_set_location_success(self, client):
        """Test successful location update."""
        initial = client.geocoordinates.get_location()
        
        # Set new location
        result = client.geocoordinates.set_location(latitude=45.0, longitude=90.0)
        assert result is True
        
        # Verify the update
        updated_location = client.geocoordinates.get_location()
        assert updated_location["latitude"] == 45.0
        assert updated_location["longitude"] == 90.0
        
        # Reset to initial state
        client.geocoordinates.set_location(
            latitude=initial["latitude"],
            longitude=initial["longitude"]
        )
            
    @pytest.mark.unit
    def test_location_info_from_params(self):
        """Test location dict creation from parameters."""
        params = {
            "Geolocation.Latitude": "45.0",
            "Geolocation.Longitude": "90.0"
        }
        info = GeoCoordinatesParser.location_from_params(params)
        assert info["latitude"] == 45.0
        assert info["longitude"] == 90.0
        
        # Test with missing parameters
        with pytest.raises(ValueError):
            GeoCoordinatesParser.location_from_params({})

class TestGeoCoordinatesOrientation:
    """Test suite for geocoordinates orientation features."""
    
    @pytest.mark.integration
    def test_get_orientation_success(self, client):
        """Test successful orientation retrieval."""
        orientation = client.geocoordinates.get_orientation()
        assert isinstance(orientation, dict)
        assert "is_valid" in orientation
        assert "heading" in orientation
        assert "tilt" in orientation
        assert "roll" in orientation
        assert "installation_height" in orientation
            
    @pytest.mark.integration
    def test_set_orientation_success(self, client):
        """Test successful orientation update."""
        # Get initial state
        initial = client.geocoordinates.get_orientation()
        
        # Set new orientation
        orientation = {
            "heading": 180.0,
            "tilt": 45.0,
            "roll": 0.0,
            "installation_height": 2.5
        }
        result = client.geocoordinates.set_orientation(orientation)
        assert result is True
        
        # Verify the update
        updated_orientation = client.geocoordinates.get_orientation()
        assert updated_orientation["heading"] == 180.0
        assert updated_orientation["tilt"] == 45.0
        assert updated_orientation["roll"] == 0.0
        assert updated_orientation["installation_height"] == 2.5
        
        # Reset to initial state
        client.geocoordinates.set_orientation(initial)
        
    @pytest.mark.integration
    def test_set_orientation_partial(self, client):
        """Test partial orientation update."""
        # Get initial state
        initial = client.geocoordinates.get_orientation()
        
        # Set only heading
        orientation = {"heading": 90.0}
        result = client.geocoordinates.set_orientation(orientation)
        assert result is True
        
        # Verify update - heading changed, others unchanged
        updated_orientation = client.geocoordinates.get_orientation()
        assert updated_orientation["heading"] == 90.0
        assert updated_orientation["tilt"] == initial["tilt"]
        assert updated_orientation["roll"] == initial["roll"]
        assert updated_orientation["installation_height"] == initial["installation_height"]
            
        # Reset to initial state
        client.geocoordinates.set_orientation(initial)
            
    @pytest.mark.unit
    def test_orientation_info_from_params(self):
        """Test orientation dict creation from parameters."""
        params = {
            "GeoOrientation.Heading": "180.0",
            "GeoOrientation.Tilt": "45.0",
            "GeoOrientation.Roll": "0.0",
            "GeoOrientation.InstallationHeight": "2.5"
        }
        info = GeoCoordinatesParser.orientation_from_params(params)
        assert info["heading"] == 180.0
        assert info["tilt"] == 45.0
        assert info["roll"] == 0.0
        assert info["installation_height"] == 2.5
        
        # Test with missing parameters (should be None)
        empty_info = GeoCoordinatesParser.orientation_from_params({})
        assert empty_info["heading"] is None
        assert empty_info["tilt"] is None
        assert empty_info["roll"] is None
        assert empty_info["installation_height"] is None
        
    @pytest.mark.integration
    def test_apply_settings_success(self, client):
        """Test successful settings application."""
        # Get initial state
        initial = client.geocoordinates.get_orientation()
        
        # Set new orientation
        orientation = {"heading": 270.0}
        client.geocoordinates.set_orientation(orientation)
        
        # Apply settings
        result = client.geocoordinates.apply_settings()
        assert result is True
        
        # Verify changes were applied
        updated_orientation = client.geocoordinates.get_orientation()
        assert updated_orientation["heading"] == 270.0
        
        # Reset to initial state
        client.geocoordinates.set_orientation(initial)
        client.geocoordinates.apply_settings()
        
    @pytest.mark.integration
    def test_error_handling(self, client, monkeypatch):
        """Test error handling with invalid requests."""
        # Test invalid URL
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "<Error><ErrorCode>NotFound</ErrorCode><ErrorDescription>Resource not found</ErrorDescription></Error>"
        
        # Patch the request method to return our mock
        monkeypatch.setattr(client.geocoordinates, "request", lambda *args, **kwargs: mock_response)
        
        # Test that FeatureError is raised
        with pytest.raises(FeatureError) as excinfo:
            client.geocoordinates.get_location()
        assert "HTTP 404" in str(excinfo.value) 