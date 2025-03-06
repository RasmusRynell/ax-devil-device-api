"""Feature flag management functionality."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .base import FeatureClient
from ..core.types import TransportResponse, FeatureResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError


@dataclass
class FeatureFlag:
    """Represents a feature flag configuration.
    
    Attributes:
        name: Unique identifier of the feature flag
        value: Current value of the flag (True/False)
        default_value: Default value of the flag
        description: Optional description of the flag's purpose
    """
    name: str
    value: bool
    default_value: bool = False
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the FeatureFlag to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "default_value": self.default_value,
            "description": self.description
        }

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> 'FeatureFlag':
        """Create instance from API response data."""
        return cls(
            name=data['name'],
            value=data['value'],
            default_value=data.get('defaultValue', False),
            description=data.get('description')
        )


class FeatureFlagClient(FeatureClient[FeatureFlag]):
    """Client for feature flag operations.
    
    Provides functionality for:
    - Setting feature flag values
    - Retrieving feature flag states
    - Listing all available feature flags
    - Getting supported API versions
    """
    
    FEATURE_FLAG_ENDPOINT = DeviceEndpoint("POST", "/axis-cgi/featureflag.cgi")
    JSON_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def _make_request(self, method: str, params: Optional[Dict] = None) -> FeatureResponse[Dict]:
        """Make a request to the feature flag API.
        
        Args:
            method: API method to call
            params: Optional parameters for the request
            
        Returns:
            FeatureResponse containing parsed JSON response or error
        """
        payload = {
            "apiVersion": "1.0",
            "method": method
        }
        if params:
            payload["params"] = params
            
        response = self.request(
            self.FEATURE_FLAG_ENDPOINT,
            json=payload,
            headers=self.JSON_HEADERS
        )
        
        if not response.is_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "request_failed",
                f"Request failed: HTTP {response.raw_response.status_code}"
            ))
            
        json_response = response.raw_response.json()
        
        # Check for API error response
        if "error" in json_response:
            error = json_response["error"]
            return FeatureResponse.create_error(FeatureError(
                "api_error",
                error.get("message", "Unknown API error")
            ))
        
        return FeatureResponse.ok(json_response.get("data", {}))

    def set_flags(self, flag_values: Dict[str, bool]) -> FeatureResponse[bool]:
        """Set values for multiple feature flags.
        
        Args:
            flag_values: Dictionary mapping flag names to desired boolean values
            
        Returns:
            FeatureResponse indicating success/failure
        """
        if not flag_values:
            return FeatureResponse.create_error(FeatureError(
                "invalid_request",
                "No flag values provided"
            ))
            
        response = self._make_request("set", {"flagValues": flag_values})
        if not response.is_success:
            return FeatureResponse.create_error(response.error)
            
        return FeatureResponse.ok(True)

    def get_flags(self, names: List[str]) -> FeatureResponse[Dict[str, bool]]:
        """Get current values of specified feature flags.
        
        Args:
            names: List of feature flag names to retrieve
            
        Returns:
            FeatureResponse containing dictionary of flag names to values
        """
        if not names:
            return FeatureResponse.create_error(FeatureError(
                "invalid_request",
                "No flag names provided"
            ))
            
        response = self._make_request("get", {"names": names})
        if not response.is_success:
            return FeatureResponse.create_error(response.error)
            
        return FeatureResponse.ok(response.data.get("flagValues", {}))

    def list_all(self) -> FeatureResponse[List[FeatureFlag]]:
        """List all available feature flags with metadata.
        
        Returns:
            FeatureResponse containing list of feature flag configurations
        """
        response = self._make_request("listAll")
        if not response.is_success:
            return FeatureResponse.create_error(response.error)
            
        flags = [FeatureFlag.from_response(flag) for flag in response.data.get("flags", [])]
        return FeatureResponse.ok(flags)

    def get_supported_versions(self) -> FeatureResponse[List[str]]:
        """Get list of supported API versions.
        
        Returns:
            FeatureResponse containing list of version strings
        """
        response = self._make_request("getSupportedVersions")
        if not response.is_success:
            return FeatureResponse.create_error(response.error)
            
        return FeatureResponse.ok(response.data.get("apiVersions", []))
