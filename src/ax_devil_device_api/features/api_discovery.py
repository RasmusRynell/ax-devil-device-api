from dataclasses import dataclass
from typing import Optional, Dict, List

from .base import AxisFeatureClient
from ..core.types import FeatureResponse
from ..core.endpoints import CameraEndpoint
from ..utils.errors import FeatureError


@dataclass
class DiscoveredAPI:
    """Represents a single API.

    Attributes:
        name: Name of the API (e.g. 'analytics-mqtt')
        version: Version identifier (e.g. 'v1')
        state: API state (e.g. 'beta')
        version_string: Full version string (e.g. '1.0.0-beta.1')
    """
    name: str
    version: str
    state: str
    version_string: str
    
    # URLs for various resources
    _urls: Dict[str, str]
    
    # Cache for loaded resources
    _documentation: Optional[str] = None
    _documentation_html: Optional[str] = None
    _model: Optional[Dict] = None
    _openapi: Optional[Dict] = None
    
    # Reference to client for making requests
    _client: Optional['DiscoveryClient'] = None
    
    @classmethod
    def from_discovery_data(cls, name: str, version: str, data: Dict) -> 'DiscoveredAPI':
        """Create an API instance from discovery response data."""
        return cls(
            name=name,
            version=version,
            state=data.get('state', 'unknown'),
            version_string=data.get('version', 'unknown'),
            _urls={
                'doc': data.get('doc'),
                'doc_html': data.get('doc_html'),
                'model': data.get('model'),
                'rest_api': data.get('rest_api'),
                'rest_openapi': data.get('rest_openapi'),
                'rest_ui': data.get('rest_ui')
            }
        )
    
    def _ensure_client(self) -> None:
        """Ensure we have a client instance for making requests."""
        if not self._client:
            raise RuntimeError("API instance not properly initialized with client")
    
    def get_documentation(self) -> FeatureResponse[str]:
        """Get the API's markdown documentation.
        
        Makes a request only on first access, then caches the result.
        """
        self._ensure_client()
        
        if self._documentation is not None:
            return FeatureResponse.ok(self._documentation)
            
        doc_url = self._urls.get('doc')
        if not doc_url:
            return FeatureResponse.create_error(FeatureError(
                "missing_documentation",
                f"No documentation URL available for {self.name} {self.version}"
            ))
            
        response = self._client.request(
            CameraEndpoint("GET", doc_url),
            headers={"Accept": "text/markdown"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "doc_fetch_failed",
                f"Failed to fetch documentation: HTTP {response.raw_response.status_code}"
            ))
            
        self._documentation = response.raw_response.text
        return FeatureResponse.ok(self._documentation)
    
    def get_model(self) -> FeatureResponse[Dict]:
        """Get the API's JSON model.
        
        Makes a request only on first access, then caches the result.
        """
        self._ensure_client()
        
        if self._model is not None:
            return FeatureResponse.ok(self._model)
            
        model_url = self._urls.get('model')
        if not model_url:
            return FeatureResponse.create_error(FeatureError(
                "missing_model",
                f"No model URL available for {self.name} {self.version}"
            ))
            
        response = self._client.request(
            CameraEndpoint("GET", model_url),
            headers={"Accept": "application/json"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "model_fetch_failed",
                f"Failed to fetch model: HTTP {response.raw_response.status_code}"
            ))
            
        try:
            self._model = response.raw_response.json()
            return FeatureResponse.ok(self._model)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "model_parse_failed",
                f"Failed to parse model JSON: {str(e)}"
            ))
    
    def get_documentation_html(self) -> FeatureResponse[str]:
        """Get the API's HTML documentation.
        
        Makes a request only on first access, then caches the result.
        """
        self._ensure_client()
        
        if self._documentation_html is not None:
            return FeatureResponse.ok(self._documentation_html)
            
        doc_url = self._urls.get('doc_html')
        if not doc_url:
            return FeatureResponse.create_error(FeatureError(
                "missing_documentation_html",
                f"No HTML documentation URL available for {self.name} {self.version}"
            ))
            
        response = self._client.request(
            CameraEndpoint("GET", doc_url),
            headers={"Accept": "text/html"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "doc_html_fetch_failed",
                f"Failed to fetch HTML documentation: HTTP {response.raw_response.status_code}"
            ))
            
        self._documentation_html = response.raw_response.text
        return FeatureResponse.ok(self._documentation_html)

    def get_openapi_spec(self) -> FeatureResponse[Dict]:
        """Get the API's OpenAPI specification.
        
        Makes a request only on first access, then caches the result.
        """
        self._ensure_client()
        
        if self._openapi is not None:
            return FeatureResponse.ok(self._openapi)
            
        openapi_url = self._urls.get('rest_openapi')
        if not openapi_url:
            return FeatureResponse.create_error(FeatureError(
                "missing_openapi",
                f"No OpenAPI spec URL available for {self.name} {self.version}"
            ))
            
        response = self._client.request(
            CameraEndpoint("GET", openapi_url),
            headers={"Accept": "application/json"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        if response.raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "openapi_fetch_failed",
                f"Failed to fetch OpenAPI spec: HTTP {response.raw_response.status_code}"
            ))
            
        try:
            self._openapi = response.raw_response.json()
            return FeatureResponse.ok(self._openapi)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "openapi_parse_failed",
                f"Failed to parse OpenAPI JSON: {str(e)}"
            ))

    @property
    def rest_api_url(self) -> str:
        """Get the base URL for REST API endpoints."""
        return self._urls.get('rest_api') or 'No REST API available'
    
    @property
    def rest_ui_url(self) -> str:
        """Get the URL for the Swagger UI."""
        return self._urls.get('rest_ui') or 'No REST UI available'


@dataclass
class DiscoveredAPICollection:
    """Collection of all available APIs and their endpoints.
    
    This is the root structure returned by the discovery endpoint.
    Provides easy access to APIs by name and version.
    
    Attributes:
        apis: Dictionary of APIs by name and version
        raw_data: Original response data for future parsing
    """
    apis: Dict[str, Dict[str, DiscoveredAPI]]
    raw_data: Dict
    
    @classmethod
    def from_response(cls, data: Dict, client: 'DiscoveryClient') -> 'DiscoveredAPICollection':
        """Create APICollection from discovery response data."""
        apis = {}
        
        # Parse the nested API structure
        for api_name, versions in data.get('apis', {}).items():
            apis[api_name] = {}
            for version, api_data in versions.items():
                api = DiscoveredAPI.from_discovery_data(api_name, version, api_data)
                api._client = client  # Inject client for making requests
                apis[api_name][version] = api
        
        return cls(apis=apis, raw_data=data)
    
    def get_api(self, name: str, version: str = None) -> Optional[DiscoveredAPI]:
        """Get a specific API by name and optionally version.
        
        If version is not specified, returns the latest version.
        """
        if name not in self.apis:
            return None
            
        if version:
            return self.apis[name].get(version)
            
        # If no version specified, try to get latest
        versions = sorted(self.apis[name].keys())
        return self.apis[name][versions[-1]] if versions else None
    
    def get_all_apis(self) -> List[DiscoveredAPI]:
        """Get all APIs as a flat list."""
        return [
            api
            for versions in self.apis.values()
            for api in versions.values()
        ]
    
    def get_apis_by_name(self, name: str) -> List[DiscoveredAPI]:
        """Get all versions of a specific API."""
        return list(self.apis.get(name, {}).values())


class DiscoveryClient(AxisFeatureClient[DiscoveredAPICollection]):
    """Client for API discovery operations.
    
    Provides access to the device's API discovery endpoint and helps manage
    API documentation and resources.
    """
    
    DISCOVER_ENDPOINT = CameraEndpoint("GET", "/config/discover")
    
    def discover(self) -> FeatureResponse[DiscoveredAPICollection]:
        """Get information about available APIs.
        
        Returns:
            FeatureResponse containing DiscoveredAPICollection with discovered APIs
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
            return FeatureResponse.ok(DiscoveredAPICollection.from_response(data, self))
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_error",
                f"Failed to parse discovery response: {str(e)}"
            )) 