"""Geographic coordinates and orientation features for a device."""

import xml.etree.ElementTree as ET
import requests
from typing import Optional, Dict, Tuple, Any
from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError

LocationDict = Dict[str, Any]
OrientationDict = Dict[str, Any]


def parse_xml(xml_text: str, xpath: str = None) -> Optional[ET.Element]:
    """Parse XML text and optionally find an element by xpath."""
    try:
        root = ET.fromstring(xml_text)
        return root.find(xpath) if xpath else root
    except (ET.ParseError, AttributeError) as e:
        raise ValueError(f"Invalid XML format: {e}")

def xml_value(element: Optional[ET.Element], path: str) -> Optional[str]:
    """Extract text value from XML element."""
    if element is None:
        return None
    found = element.find(path)
    return found.text if found is not None else None

def xml_bool(element: Optional[ET.Element], path: str) -> bool:
    """Extract boolean value from XML element."""
    value = xml_value(element, path)
    return value is not None and value.lower() == "true"

def try_float(val: Optional[str]) -> Optional[float]:
    """Convert string to float, returning None if invalid."""
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None

def format_iso6709_coordinate(latitude: float, longitude: float) -> Tuple[str, str]:
    """Format coordinates according to ISO 6709 standard."""
    def format_coord(value: float, width: int) -> str:
        sign = "+" if value >= 0 else "-"
        abs_val = abs(value)
        degrees = int(abs_val)
        fraction = abs_val - degrees
        return f"{sign}{degrees:0{width}d}.{int(fraction * 1000000):06d}"
    
    return format_coord(latitude, 2), format_coord(longitude, 3)

def parse_iso6709_coordinate(coord_str: str) -> float:
    """Parse an ISO 6709 coordinate string to float."""
    if not coord_str or len(coord_str) < 2:
        raise ValueError("Empty or invalid coordinate string")
        
    coord_str = coord_str.strip()
    sign = -1 if coord_str[0] == '-' else 1
    value = float(coord_str[1:] if coord_str[0] in '+-' else coord_str)
    return sign * value

class GeoCoordinatesParser:
    """Parser for geo coordinates data."""
    
    @staticmethod
    def location_from_params(params: Dict[str, str]) -> LocationDict:
        """Create location dict from parameter dictionary."""
        lat_str = params.get('Geolocation.Latitude')
        lng_str = params.get('Geolocation.Longitude')
        
        if not lat_str or not lng_str:
            raise ValueError("Missing required location parameters")
            
        try:
            return {
                "latitude": float(lat_str),
                "longitude": float(lng_str),
                "is_valid": True
            }
        except ValueError as e:
            raise ValueError(f"Invalid coordinate format: {e}")

    @staticmethod
    def location_from_xml(xml_text: str) -> LocationDict:
        """Create location dict from XML response."""
        root = parse_xml(xml_text)
        location = root.find(".//Location")
        
        if location is None:
            raise ValueError("Missing Location element")
            
        lat = parse_iso6709_coordinate(xml_value(location, "Lat") or "")
        lng = parse_iso6709_coordinate(xml_value(location, "Lng") or "")
        
        return {
            "latitude": lat,
            "longitude": lng,
            "is_valid": xml_bool(root, ".//ValidPosition")
        }
    
    @staticmethod
    def orientation_from_params(params: Dict[str, str]) -> OrientationDict:
        """Create orientation dict from parameter dictionary."""
        heading = try_float(params.get('GeoOrientation.Heading'))
        return {
            "heading": heading,
            "tilt": try_float(params.get('GeoOrientation.Tilt')),
            "roll": try_float(params.get('GeoOrientation.Roll')),
            "installation_height": try_float(params.get('GeoOrientation.InstallationHeight')),
            "is_valid": bool(heading)
        }

    @staticmethod
    def orientation_from_xml(xml_text: str) -> OrientationDict:
        """Create orientation dict from XML response."""
        success = parse_xml(xml_text, ".//GetSuccess")
        
        if success is None:
            return {"is_valid": False}
            
        return {
            "heading": try_float(xml_value(success, "Heading")),
            "tilt": try_float(xml_value(success, "Tilt")),
            "roll": try_float(xml_value(success, "Roll")),
            "installation_height": try_float(xml_value(success, "InstallationHeight")),
            "is_valid": xml_bool(success, "ValidHeading")
        }

class GeoCoordinatesClient(FeatureClient):
    """Client for device geocoordinates and orientation features."""
    
    LOCATION_GET_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/geolocation/get.cgi")
    LOCATION_SET_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/geolocation/set.cgi")
    ORIENTATION_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/geoorientation/geoorientation.cgi")
    
    def _check_xml_success(self, response: requests.Response, error_code: str) -> bool:
        """Check XML response for success or error elements."""
        if response.status_code != 200:
            raise FeatureError(error_code, f"HTTP {response.status_code}")
            
        root = parse_xml(response.text)
        error = root.find(".//Error")
        if error is not None:
            error_code_val = xml_value(error, "ErrorCode") or "Unknown"
            error_desc = xml_value(error, "ErrorDescription") or ""
            raise FeatureError(error_code, f"API error: {error_code_val} - {error_desc}")
            
        if root.find(".//Success") is None:
            raise FeatureError(error_code, "No success confirmation in response")
            
        return True
        
    def get_location(self) -> LocationDict:
        """Get current device location."""
        response = self.request(
            self.LOCATION_GET_ENDPOINT,
            headers={"Accept": "text/xml"}
        )
        
        if response.status_code != 200:
            raise FeatureError("invalid_response", f"HTTP {response.status_code}")
            
        try:
            return GeoCoordinatesParser.location_from_xml(response.text)
        except ValueError as e:
            raise FeatureError("parse_error", f"Failed to parse response: {e}")
            
    def set_location(self, latitude: float, longitude: float) -> bool:
        """Set device location."""
        lat_str, lng_str = format_iso6709_coordinate(latitude, longitude)
        response = self.request(
            self.LOCATION_SET_ENDPOINT,
            params={"lat": lat_str, "lng": lng_str},
            headers={"Accept": "text/xml"}
        )
        return self._check_xml_success(response, "set_failed")
            
    def get_orientation(self) -> OrientationDict:
        """Get current device orientation."""
        response = self.request(
            self.ORIENTATION_ENDPOINT,
            params={"action": "get"},
            headers={"Accept": "text/xml"}
        )
        
        if response.status_code != 200:
            raise FeatureError("invalid_response", f"HTTP {response.status_code}")
            
        try:
            return GeoCoordinatesParser.orientation_from_xml(response.text)
        except ValueError as e:
            raise FeatureError("parse_error", f"Failed to parse response: {e}")
            
    def set_orientation(self, orientation: OrientationDict) -> bool:
        """Set device orientation."""
        params = {"action": "set"}
        param_mapping = {
            "heading": "heading",
            "tilt": "tilt", 
            "roll": "roll",
            "installation_height": "inst_height"
        }
        
        params.update({
            param: str(orientation[key]) 
            for key, param in param_mapping.items() 
            if orientation.get(key) is not None
        })
            
        response = self.request(self.ORIENTATION_ENDPOINT, params=params)
        return self._check_xml_success(response, "set_failed")
        
    def apply_settings(self) -> bool:
        """Apply pending orientation settings."""
        response = self.request(
            self.ORIENTATION_ENDPOINT,
            params={"action": "set", "auto_update_once": "true"}
        )
        
        if response.status_code != 200:
            raise FeatureError("apply_failed", f"HTTP {response.status_code}")
            
        return True