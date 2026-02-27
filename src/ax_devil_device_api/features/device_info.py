import requests
from typing import Any, Dict
from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


def get_device_info_from_params(params: Dict[str, str]) -> Dict[str, Any]:
    """Create device info dictionary from parameter dictionary.
    
    Args:
        params: Dictionary of device parameters
        
    Returns:
        Dictionary containing device information with fields:
        - model: Device model name (e.g., "AXIS Q1656")
        - product_type: Type of device (e.g., "Box Camera") 
        - product_number: Short product number (e.g., "Q1656")
        - serial_number: Unique serial number
        - hardware_id: Hardware identifier
        - firmware_version: Current firmware version
        - build_date: Firmware build date
        - ptz_support: List of supported PTZ modes
        - analytics_support: Whether analytics are supported
    """
    def get_param(key: str, default: str = "unknown") -> str:
        return params.get(f"root.{key}", params.get(key, default))

    ptz_modes = get_param("Properties.PTZ.DriverModeList", "").split(",")
    ptz_support = [mode.strip() for mode in ptz_modes if mode.strip()]
    
    analytics_support = any(
        key for key in params.keys() 
        if "analytics" in key.lower() or "objectdetection" in key.lower()
    )
    
    return {
        "model": get_param("Brand.ProdShortName"),
        "product_type": get_param("Brand.ProdType"),
        "product_number": get_param("Brand.ProdNbr"),
        "serial_number": get_param("Properties.System.SerialNumber"),
        "hardware_id": get_param("Properties.System.HardwareID"),
        "firmware_version": get_param("Properties.Firmware.Version"),
        "build_date": get_param("Properties.Firmware.BuildDate"),
        "ptz_support": ptz_support,
        "analytics_support": analytics_support,
        "metadata_support": get_param("Properties.API.Metadata.Metadata") == "yes",
        "Onvif Replay Extention": get_param("Properties.API.Onvif.ReplayExtension") == "yes",
    }
    

class DeviceInfoClient(FeatureClient):
    """Client for basic device operations."""
    
    BASIC_DEVICE_INFO_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/basicdeviceinfo.cgi")
    PARAMS_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/param.cgi")
    RESTART_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/restart.cgi")
    
    def _parse_param_response(self, response: requests.Response) -> Dict[str, str]:
        """Parse raw parameter response into dictionary.
        
        Common functionality for parsing param.cgi responses into key-value pairs.
        Used by multiple feature modules that need to get device parameters.
        """
            
        if response.status_code != 200:
            raise FeatureError(
                "invalid_response",
                f"Invalid parameter response: HTTP {response.status_code}"
            )
            
        lines = response.text.strip().split('\n')
        params = dict(line.split('=', 1) for line in lines if '=' in line)
        return params

    def get_info(self) -> Dict[str, Any]:
        """Get basic device information."""
        return get_device_info_from_params(self.get_info_detailed())

    def get_info_detailed(self) -> Dict[str, Any]:
        """Get detailed device information"""

        param_groups = ["Properties", "Brand"]
        params = {}
        
        for group in param_groups:
            response = self.request(
                self.PARAMS_ENDPOINT,
                params={"action": "list", "group": group},
                headers={"Accept": "text/plain"}
            )
            
            parsed = self._parse_param_response(response)
            if not parsed:
                raise FeatureError(
                    "fetch_failed",
                    f"Failed to get {group} parameters",
                    details={"group": group}
                )
            
            params.update(parsed)

        return params

    def restart(self) -> bool:
        """Restart the device."""
        response = self.request(self.RESTART_ENDPOINT)
        
        if response.status_code != 200:
            raise FeatureError(
                "restart_failed",
                f"Restart failed: HTTP {response.status_code}"
            )
            
        return True
        
    def check_health(self) -> bool:
        """Check if the device is responsive."""
        response = self.request(
            self.PARAMS_ENDPOINT,
            params={"action": "list", "group": "Network"},
            headers={"Accept": "text/plain"}
        )
        
        if response.status_code != 200:
            raise FeatureError(
                "health_check_failed",
                f"Health check failed: HTTP {response.status_code}"
            )
            
        return True

    def _get_basic_device_info(self, method: str, *, authenticated: bool = True) -> Dict[str, Any]:
        """Fetch device info via basicdeviceinfo.cgi.

        Args:
            method: The VAPIX JSON-RPC method name
                (e.g. "getAllUnrestrictedProperties" or "getAllProperties").
            authenticated: If False the request bypasses the auth handler.
        """
        request_fn = self.request if authenticated else self.request_no_auth
        response = request_fn(
            self.BASIC_DEVICE_INFO_ENDPOINT,
            headers={"Accept": "application/json"},
            json={"apiVersion": "1.3", "method": method},
        )

        if response.status_code != 200:
            raise FeatureError(
                "fetch_failed",
                f"Failed to get basic device info: HTTP {response.status_code}",
            )

        data = response.json().get("data", {}).get("propertyList", {})
        if not data:
            raise FeatureError(
                "fetch_failed",
                "No device information found in response",
            )
        return data

    def get_info_no_auth(self) -> Dict[str, Any]:
        """Get device info without authentication using basicdeviceinfo.cgi."""
        return self._get_basic_device_info("getAllUnrestrictedProperties", authenticated=False)

    def get_info_auth(self) -> Dict[str, Any]:
        """Get device info with authentication using basicdeviceinfo.cgi."""
        return self._get_basic_device_info("getAllProperties")

