"""Base classes for feature modules."""

from typing import Dict, TypeVar, Generic
from ..core.client import FeatureClientABC
from ..core.types import TransportResponse, FeatureResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError

T = TypeVar('T')

class FeatureClient(FeatureClientABC, Generic[T]):
    """Base class for device feature clients.
    
    Provides common functionality used across feature modules:
    - Parameter parsing
    - Error handling
    - Response formatting
    """
    
    def _parse_param_response(self, response: TransportResponse) -> FeatureResponse[Dict[str, str]]:
        """Parse raw parameter response into dictionary.
        
        Common functionality for parsing param.cgi responses into key-value pairs.
        Used by multiple feature modules that need to get device parameters.
        """
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        raw_response = response.raw_response
        if raw_response.status_code != 200:
            return FeatureResponse(error=FeatureError(
                "invalid_response",
                f"Invalid parameter response: HTTP {raw_response.status_code}"
            ))
            
        try:
            lines = raw_response.text.strip().split('\n')
            params = dict(line.split('=', 1) for line in lines if '=' in line)
            return FeatureResponse.ok(params)
        except Exception as e:
            return FeatureResponse(error=FeatureError(
                "parse_error",
                f"Failed to parse parameters: {str(e)}"
            ))
