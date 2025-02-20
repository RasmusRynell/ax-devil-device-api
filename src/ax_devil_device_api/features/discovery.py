from dataclasses import dataclass
from typing import Optional, Dict, List
from .base import FeatureClient
from ..core.types import TransportResponse, FeatureResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError

@dataclass
class APIEndpoint:
    """Represents a single API endpoint.
    
    Attributes:
        path: Full path to the endpoint
        method: HTTP method (GET, POST, etc)
        description: Optional description of the endpoint
        content_type: Expected content type
    """
    path: str
    method: str
    description: Optional[str] = None
    content_type: Optional[str] = None

class DiscoveredAPI:
    """Represents a single API.



@dataclass
class DiscoveredAPICollection:
    """Collection of all available APIs and their endpoints.
    
    This is the root structure returned by the discovery endpoint.
    It can be extended with additional attributes and methods as needed.
    
    Attributes:
        groups: List of API groups
        raw_data: Original response data for future parsing
    """
    groups: List[DiscoveredAPI]
    raw_data: Dict

    @classmethod
    def from_response(cls, data: Dict) -> 'APICollection':
        """Create APICollection from discovery response data.
        
        This method will be enhanced as we understand more about the response structure.
        For now, it stores the raw data and provides a minimal parsed structure.
        """
        # Start with an empty list of groups - we'll enhance this later
        groups = []
        
        # Store raw data for future parsing when we implement more features
        return cls(groups=groups, raw_data=data)

class DiscoveryClient(FeatureClient[APICollection]):
    """Client for API discovery operations.
    
    Currently focused on the core discovery endpoint, which provides
    information about available APIs and their endpoints.
    
    This client will be extended with additional functionality for specific
    API interactions as we implement more features.
    """
    
    DISCOVER_ENDPOINT = DeviceEndpoint("GET", "/config/discover")
    
    def discover(self) -> FeatureResponse[APICollection]:
        """Get information about available APIs.
        
        Returns:
            FeatureResponse containing APICollection with discovered APIs
        """
        response = self.request(
            self.DISCOVER_ENDPOINT,
            headers={"Accept": "application/json"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "discovery_failed",
                f"Discovery request failed: HTTP {response.raw_response.status_code}"
            ))
            
        try:
            data = response.raw_response.json()
            return FeatureResponse.ok(APICollection.from_response(data))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_error",
                f"Failed to parse discovery response: {str(e)}"
            )) 