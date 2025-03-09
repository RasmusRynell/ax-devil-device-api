import requests
from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from .base import FeatureClient
from ..core.types import FeatureResponse
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError

class NetworkClient(FeatureClient):
    """Client for network configuration operations."""
    
    # Endpoint definitions
    PARAMS_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/param.cgi")
    
    def _parse_param_response(self, response: requests.Response) -> Dict[str, str]:
        """Parse raw parameter response into dictionary."""
        if response.status_code != 200:
            raise FeatureError(
                "invalid_response",
                f"Invalid parameter response: HTTP {response.status_code}"
            )
            
        try:
            lines = response.text.strip().split('\n')
            return dict(line.split('=', 1) for line in lines if '=' in line)
        except Exception as e:
            raise FeatureError(
                "parse_error",
                f"Failed to parse parameters: {str(e)}"
            )

    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information."""
        response = self.request(
            self.PARAMS_ENDPOINT,
            params={"action": "list", "group": "Network"},
            headers={"Accept": "text/plain"}
        )
        
        return self._parse_param_response(response)
