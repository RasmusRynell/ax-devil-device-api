from dataclasses import dataclass
from typing import Dict, List
from .base import FeatureClient
from ..core.types import FeatureResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError

@dataclass
class DeviceInfo:
    """Device device information.
    
    Attributes:
        model: Device model name (e.g., "AXIS Q1656")
        product_type: Type of device (e.g., "Box Camera")
        product_number: Short product number (e.g., "Q1656")
        serial_number: Unique serial number
        hardware_id: Hardware identifier
        firmware_version: Current firmware version
        build_date: Firmware build date
        ptz_support: List of supported PTZ modes
        analytics_support: Whether analytics are supported
    """
    # Device identification
    model: str
    product_type: str
    product_number: str
    serial_number: str
    hardware_id: str
    
    # Firmware information
    firmware_version: str
    build_date: str
    
    # Capabilities
    ptz_support: List[str] = None
    analytics_support: bool = False
    
    @classmethod
    def from_params(cls, params: Dict[str, str]) -> 'DeviceInfo':
        """Create instance from parameter dictionary."""
        # Helper function to get params with or without root prefix
        def get_param(key: str, default: str = "unknown") -> str:
            return params.get(f"root.{key}", params.get(key, default))
        
        # Parse PTZ support
        ptz_modes = get_param("Properties.PTZ.DriverModeList", "").split(",")
        ptz_support = [mode.strip() for mode in ptz_modes if mode.strip()]
        
        # Check analytics support (based on presence of analytics parameters)
        analytics_support = any(
            key for key in params.keys() 
            if "analytics" in key.lower() or "objectdetection" in key.lower()
        )
        
        return cls(
            # Device identification
            model=get_param("Brand.ProdShortName"),
            product_type=get_param("Brand.ProdType"),
            product_number=get_param("Brand.ProdNbr"),
            serial_number=get_param("Properties.System.SerialNumber"),
            hardware_id=get_param("Properties.System.HardwareID"),
            
            # Firmware information
            firmware_version=get_param("Properties.Firmware.Version"),
            build_date=get_param("Properties.Firmware.BuildDate"),
            
            # Capabilities
            ptz_support=ptz_support,
            analytics_support=analytics_support
        )

class DeviceInfoClient(FeatureClient[DeviceInfo]):
    """Client for basic device operations."""
    
    # Endpoint definitions
    PARAMS_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/param.cgi")
    RESTART_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/restart.cgi")
    
    def get_info(self) -> FeatureResponse[DeviceInfo]:
        """Get basic device information."""
        # Get required parameter groups
        param_groups = ["Properties", "Brand"]
        params = {}
        
        for group in param_groups:
            response = self.request(
                self.PARAMS_ENDPOINT,
                params={"action": "list", "group": group},
                headers={"Accept": "text/plain"}
            )
            
            parsed = self._parse_param_response(response)
            if not parsed.success:
                return FeatureResponse.create_error(FeatureError(
                    "fetch_failed",
                    f"Failed to get {group} parameters",
                    details={"group": group, "original_error": parsed.error}
                ))
            
            params.update(parsed.data)
        
        try:
            return FeatureResponse.ok(DeviceInfo.from_params(params))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "info_parse_failed",
                "Failed to parse device info",
                details={"error": str(e)}
            ))
            
    def restart(self) -> FeatureResponse[bool]:
        """Restart the device."""
        response = self.request(self.RESTART_ENDPOINT)
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "restart_failed",
                f"Restart failed: HTTP {response.raw_response.status_code}"
            ))
            
        return FeatureResponse.ok(True)
        
    def check_health(self) -> FeatureResponse[bool]:
        """Check if the device is responsive."""
        try:
            response = self.request(
                self.PARAMS_ENDPOINT,
                params={"action": "list", "group": "Network"},
                headers={"Accept": "text/plain"}
            )
            
            # Handle transport-level errors
            if not response.is_transport_success:
                return FeatureResponse.from_transport(response)
                
            # Handle HTTP-level errors
            if response.raw_response.status_code != 200:
                return FeatureResponse.create_error(FeatureError(
                    "health_check_failed",
                    f"Health check failed: HTTP {response.raw_response.status_code}"
                ))
                
            return FeatureResponse.ok(True)
            
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "health_check_error",
                str(e),
                details={"exception": str(e), "type": e.__class__.__name__}
            ))
