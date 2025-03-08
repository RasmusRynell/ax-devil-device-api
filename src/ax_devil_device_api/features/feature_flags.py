"""Feature flag management functionality."""

from typing import Dict, List, Optional
from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError

class FeatureFlagClient(FeatureClient):
    """Client for feature flag operations.
    
    Provides functionality for:
    - Setting feature flag values
    - Retrieving feature flag states
    - Listing all available feature flags
    - Getting supported API versions
    """
    
    FEATURE_FLAG_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/featureflag.cgi")
    JSON_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def _make_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the feature flag API.
        
        Args:
            method: API method to call
            params: Optional parameters for the request
            
        Returns:
            JSON response or error
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
        

        if response.status_code != 200:
            raise FeatureError(
                "request_failed",
                f"Request failed: HTTP {response.status_code}"
            )
            
        json_response = response.json()
        
        if "error" in json_response:
            error = json_response["error"]
            raise FeatureError(
                "api_error",
                error.get("message", "Unknown API error")
            )
        
        return json_response.get("data")

    def set_flags(self, flag_values: Dict[str, bool]) -> Dict:
        """Set values for multiple feature flags.
        
        Args:
            flag_values: Dictionary mapping flag names to desired boolean values
            
        Returns:
            JSON response indicating success/failure
        """
        if not flag_values:
            raise FeatureError(
                "invalid_request",
                "No flag values provided"
            )
            
        response = self._make_request("set", {"flagValues": flag_values})
        return response.get("result")

    def get_flags(self, names: List[str]) -> Dict:
        """Get current values of specified feature flags.
        
        Args:
            names: List of feature flag names to retrieve
            
        Returns:
            Dictionary of flag names to values
        """
        if not names:
            raise FeatureError(
                "invalid_request",
                "No flag names provided"
            )
            
        response_json = self._make_request("get", {"names": names})
        return response_json.get("flagValues")

    def list_all(self) -> List[dict]:
        """List all available feature flags with metadata.
        
        Returns:
            Dictionary of feature flag configurations
        """
        response = self._make_request("listAll")
        return response.get("flags")

    def get_supported_versions(self) -> List[str]:
        """Get list of supported API versions.
        
        Returns:
            List of version strings
        """
        response_json = self._make_request("getSupportedVersions")
        return response_json.get("apiVersions")
