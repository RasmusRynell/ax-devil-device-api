"""Geographic coordinates and orientation features for a device."""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple, TypeVar, Protocol, cast, Union
import xml.etree.ElementTree as ET
from .base import FeatureClient
from ..core.types import TransportResponse, FeatureResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError

class XMLParseable(Protocol):
    """Protocol for types that can be created from XML."""
    @classmethod
    def from_xml(cls, xml_text: str) -> 'XMLParseable':
        """Create instance from XML text."""
        ...

T = TypeVar('T', bound=Union[XMLParseable, bool])

def safe_float(value: Optional[str]) -> Optional[float]:
    """Safely convert string to float, returning None if invalid."""
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def extract_xml_value(element: Optional[ET.Element], path: str) -> Optional[str]:
    """Safely extract text value from XML element."""
    if element is None:
        return None
    found = element.find(path)
    return found.text if found is not None else None

def extract_xml_bool(element: Optional[ET.Element], path: str) -> bool:
    """Safely extract boolean value from XML element."""
    value = extract_xml_value(element, path)
    return value is not None and value.lower() == "true"

def parse_xml_root(xml_text: str) -> ET.Element:
    """Parse XML text into root element with error handling."""
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {e}")

def format_iso6709_coordinate(latitude: float, longitude: float) -> Tuple[str, str]:
    """Format coordinates according to ISO 6709 standard.
    
    Format:
        Latitude: ±DD.DDDDDD (2 digits before decimal, 6 after)
        Longitude: ±DDD.DDDDDD (3 digits before decimal, 6 after)
    """
    
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

@dataclass
class GeoCoordinatesLocation:
    """Device location information."""
    latitude: float
    longitude: float
    is_valid: bool = False

    @classmethod
    def from_params(cls, params: Dict[str, str]) -> 'GeoCoordinatesLocation':
        """Create instance from parameter dictionary."""
        lat_str = params.get('Geolocation.Latitude')
        lng_str = params.get('Geolocation.Longitude')
        
        if not lat_str or not lng_str:
            raise ValueError("Missing required location parameters")
            
        try:
            latitude = float(lat_str)
            longitude = float(lng_str)
            return cls(latitude=latitude, longitude=longitude, is_valid=True)
        except ValueError as e:
            raise ValueError(f"Invalid coordinate format: {e}")

    @classmethod
    def from_xml(cls, xml_text: str) -> 'GeoCoordinatesLocation':
        """Create instance from XML response."""
        root = parse_xml_root(xml_text)
        location = root.find(".//Location")
        
        if location is None:
            raise ValueError("Missing Location element")
            
        lat = parse_iso6709_coordinate(extract_xml_value(location, "Lat") or "")
        lng = parse_iso6709_coordinate(extract_xml_value(location, "Lng") or "")
        is_valid = extract_xml_bool(root, ".//ValidPosition")
        
        return cls(latitude=lat, longitude=lng, is_valid=is_valid)

@dataclass
class GeoCoordinatesOrientation:
    """Device orientation information."""
    heading: Optional[float] = None
    tilt: Optional[float] = None
    roll: Optional[float] = None
    installation_height: Optional[float] = None
    is_valid: bool = False

    @classmethod
    def from_params(cls, params: Dict[str, str]) -> 'GeoCoordinatesOrientation':
        """Create instance from parameter dictionary."""
        try:
            return cls(
                heading=safe_float(params.get('GeoOrientation.Heading')),
                tilt=safe_float(params.get('GeoOrientation.Tilt')),
                roll=safe_float(params.get('GeoOrientation.Roll')),
                installation_height=safe_float(params.get('GeoOrientation.InstallationHeight')),
                is_valid=bool(params.get('GeoOrientation.Heading'))
            )
        except ValueError as e:
            raise ValueError(f"Invalid orientation values: {e}")

    @classmethod
    def from_xml(cls, xml_text: str) -> 'GeoCoordinatesOrientation':
        """Create instance from XML response."""
        root = parse_xml_root(xml_text)
        success = root.find(".//GetSuccess")
        
        if success is None:
            return cls(is_valid=False)
            
        return cls(
            heading=safe_float(extract_xml_value(success, "Heading")),
            tilt=safe_float(extract_xml_value(success, "Tilt")),
            roll=safe_float(extract_xml_value(success, "Roll")),
            installation_height=safe_float(extract_xml_value(success, "InstallationHeight")),
            is_valid=extract_xml_bool(success, "ValidHeading")
        )

class GeoCoordinatesClient(FeatureClient):
    """Client for device geocoordinates and orientation features."""
    
    LOCATION_GET_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/geolocation/get.cgi")
    LOCATION_SET_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/geolocation/set.cgi")
    ORIENTATION_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/geoorientation/geoorientation.cgi")
    
    def _handle_response(self, response: TransportResponse, parser: type[T]) -> FeatureResponse[T]:
        """Handle common response processing pattern."""
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        raw_response = response.raw_response
        if raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "invalid_response",
                f"Invalid response: HTTP {raw_response.status_code}"
            ))
            
        try:
            if parser is bool:
                return FeatureResponse.ok(True)
            result = parser.from_xml(raw_response.text)
            return FeatureResponse.ok(cast(T, result))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_error",
                f"Failed to parse response: {e}"
            ))
        
    def get_location(self) -> FeatureResponse[GeoCoordinatesLocation]:
        """Get current device location."""
        response = self.request(
            self.LOCATION_GET_ENDPOINT,
            headers={"Accept": "text/xml"}
        )
        return self._handle_response(response, GeoCoordinatesLocation)
            
    def set_location(self, latitude: float, longitude: float) -> FeatureResponse[bool]:
        """Set device location."""
        try:
            lat_str, lng_str = format_iso6709_coordinate(latitude, longitude)
            params = {"lat": lat_str, "lng": lng_str}
            
            response = self.request(
                self.LOCATION_SET_ENDPOINT,
                params=params,
                headers={"Accept": "text/xml"}
            )
            
            if not response.is_transport_success:
                return FeatureResponse.from_transport(response)
                
            raw_response = response.raw_response
            if raw_response.status_code != 200:
                return FeatureResponse.create_error(FeatureError(
                    "set_failed",
                    f"Failed to set location: HTTP {raw_response.status_code}"
                ))
                
            # Check response XML for success/error
            try:
                root = parse_xml_root(raw_response.text)
                error = root.find(".//Error")
                if error is not None:
                    error_code = extract_xml_value(error, "ErrorCode") or "Unknown"
                    error_desc = extract_xml_value(error, "ErrorDescription") or ""
                    return FeatureResponse.create_error(FeatureError(
                        "set_failed",
                        f"API error: {error_code} - {error_desc}"
                    ))
                    
                success = root.find(".//Success")
                if success is None:
                    return FeatureResponse.create_error(FeatureError(
                        "set_failed",
                        "No success confirmation in response"
                    ))
                    
                return FeatureResponse.ok(True)
                
            except ValueError as e:
                return FeatureResponse.create_error(FeatureError(
                    "invalid_response",
                    f"Failed to parse response: {e}"
                ))
            
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "set_failed",
                f"Failed to set location: {e}"
            ))
            
    def get_orientation(self) -> FeatureResponse[GeoCoordinatesOrientation]:
        """Get current device orientation."""
        response = self.request(
            self.ORIENTATION_ENDPOINT,
            params={"action": "get"},
            headers={"Accept": "text/xml"}
        )
        return self._handle_response(response, GeoCoordinatesOrientation)
            
    def set_orientation(self, orientation: GeoCoordinatesOrientation) -> FeatureResponse[bool]:
        """Set device orientation."""
        try:
            params = {"action": "set"}
            if orientation.heading is not None:
                params["heading"] = str(orientation.heading)
            if orientation.tilt is not None:
                params["tilt"] = str(orientation.tilt)
            if orientation.roll is not None:
                params["roll"] = str(orientation.roll)
            if orientation.installation_height is not None:
                params["inst_height"] = str(orientation.installation_height)
                
            response = self.request(self.ORIENTATION_ENDPOINT, params=params)
            
            if not response.is_transport_success:
                return FeatureResponse.from_transport(response)
                
            raw_response = response.raw_response
            if raw_response.status_code != 200:
                return FeatureResponse.create_error(FeatureError(
                    "set_failed",
                    f"Failed to set orientation: HTTP {raw_response.status_code}"
                ))
                
            # Check response XML for success/error
            try:
                root = parse_xml_root(raw_response.text)
                error = root.find(".//Error")
                if error is not None:
                    error_code = extract_xml_value(error, "ErrorCode") or "Unknown"
                    error_desc = extract_xml_value(error, "ErrorDescription") or ""
                    return FeatureResponse.create_error(FeatureError(
                        "set_failed",
                        f"API error: {error_code} - {error_desc}"
                    ))
                    
                success = root.find(".//Success")
                if success is None:
                    return FeatureResponse.create_error(FeatureError(
                        "set_failed",
                        "No success confirmation in response"
                    ))
                    
                return FeatureResponse.ok(True)
                
            except ValueError as e:
                return FeatureResponse.create_error(FeatureError(
                    "invalid_response",
                    f"Failed to parse response: {e}"
                ))
            
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "set_failed",
                f"Failed to set orientation: {e}"
            ))
        
    def apply_settings(self) -> FeatureResponse[bool]:
        """Apply pending orientation settings."""
        response = self.request(
            self.ORIENTATION_ENDPOINT,
            params={"action": "set", "auto_update_once": "true"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "apply_failed",
                f"Failed to apply settings: HTTP {response.raw_response.status_code}"
            ))
            
        return FeatureResponse.ok(True) 