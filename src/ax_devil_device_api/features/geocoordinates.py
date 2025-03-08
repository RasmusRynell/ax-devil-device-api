"""Geographic coordinates and orientation features for a device."""

import xml.etree.ElementTree as ET
import requests
from typing import Optional, Dict, Tuple, TypeVar, cast, Union, Any, Callable
from .base import FeatureClient
from ..core.types import FeatureResponse
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError

T = TypeVar('T', bound=Union[Dict[str, Any], bool])
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
    
    def _handle_response(self, response: requests.Response, 
                         parser_func: Callable[[str], T]) -> FeatureResponse[T]:
        """Handle common response processing pattern."""
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "invalid_response", f"HTTP {response.status_code}"
            ))
            
        try:
            if parser_func is bool:
                return FeatureResponse.ok(True)
            return FeatureResponse.ok(cast(T, parser_func(response.text)))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_error", f"Failed to parse response: {e}"
            ))
    
    def _check_xml_response_for_success(self, response: requests.Response, 
                                       error_code: str) -> FeatureResponse[bool]:
        """Check XML response for success or error elements."""
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                error_code, f"HTTP {response.status_code}"
            ))
            
        try:
            root = parse_xml(response.text)
            error = root.find(".//Error")
            if error is not None:
                error_code_val = xml_value(error, "ErrorCode") or "Unknown"
                error_desc = xml_value(error, "ErrorDescription") or ""
                return FeatureResponse.create_error(FeatureError(
                    error_code, f"API error: {error_code_val} - {error_desc}"
                ))
                
            if root.find(".//Success") is None:
                return FeatureResponse.create_error(FeatureError(
                    error_code, "No success confirmation in response"
                ))
                
            return FeatureResponse.ok(True)
            
        except ValueError as e:
            return FeatureResponse.create_error(FeatureError(
                "invalid_response", f"Failed to parse response: {e}"
            ))
    
    def _handle_request_error(self, e: Exception, error_code: str) -> FeatureResponse[bool]:
        """Handle common request error pattern."""
        return FeatureResponse.create_error(FeatureError(
            error_code, f"Request failed: {e}"
        ))
        
    def get_location(self) -> FeatureResponse[LocationDict]:
        """Get current device location."""
        response = self.request(
            self.LOCATION_GET_ENDPOINT,
            headers={"Accept": "text/xml"}
        )
        return self._handle_response(response, GeoCoordinatesParser.location_from_xml)
            
    def set_location(self, latitude: float, longitude: float) -> FeatureResponse[bool]:
        """Set device location."""
        try:
            lat_str, lng_str = format_iso6709_coordinate(latitude, longitude)
            response = self.request(
                self.LOCATION_SET_ENDPOINT,
                params={"lat": lat_str, "lng": lng_str},
                headers={"Accept": "text/xml"}
            )
            return self._check_xml_response_for_success(response, "set_failed")
        except Exception as e:
            return self._handle_request_error(e, "set_failed")
            
    def get_orientation(self) -> FeatureResponse[OrientationDict]:
        """Get current device orientation."""
        response = self.request(
            self.ORIENTATION_ENDPOINT,
            params={"action": "get"},
            headers={"Accept": "text/xml"}
        )
        return self._handle_response(response, GeoCoordinatesParser.orientation_from_xml)
            
    def set_orientation(self, orientation: OrientationDict) -> FeatureResponse[bool]:
        """Set device orientation."""
        try:
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
            return self._check_xml_response_for_success(response, "set_failed")
        except Exception as e:
            return self._handle_request_error(e, "set_failed")
        
    def apply_settings(self) -> FeatureResponse[bool]:
        """Apply pending orientation settings."""
        response = self.request(
            self.ORIENTATION_ENDPOINT,
            params={"action": "set", "auto_update_once": "true"}
        )
        
        if response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "apply_failed", f"Failed to apply settings: HTTP {response.status_code}"
            ))

        return FeatureResponse.ok(True)