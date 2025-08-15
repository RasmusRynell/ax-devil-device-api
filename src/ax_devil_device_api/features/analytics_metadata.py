"""Axis analytics metadata producer configuration client."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


@dataclass(frozen=True)
class VideoChannel:
    """Represents a video channel configuration for a producer.
    
    Attributes:
        channel: Channel number/identifier
        enabled: Whether the producer is enabled on this channel
    """
    channel: int
    enabled: bool


@dataclass(frozen=True)
class Producer:
    """Represents an analytics metadata producer.
    
    Attributes:
        name: Internal name of the producer
        nice_name: Human-readable name of the producer
        video_channels: List of video channels this producer can operate on
    """
    name: str
    nice_name: str
    video_channels: List[VideoChannel]

    @classmethod
    def from_api_data(cls, data: Dict) -> 'Producer':
        """Create Producer from API response data."""
        channels = [
            VideoChannel(channel=ch['channel'], enabled=ch['enabled'])
            for ch in data.get('videochannels', [])
        ]
        return cls(
            name=data['name'],
            nice_name=data['niceName'],
            video_channels=channels
        )


@dataclass(frozen=True)
class MetadataSample:
    """Represents a metadata sample frame.
    
    Attributes:
        producer_name: Name of the producer that generated this sample
        sample_frame_xml: XML content of the sample frame
        schema_xml: XML schema for the metadata (if available)
    """
    producer_name: str
    sample_frame_xml: str
    schema_xml: Optional[str] = None

    @classmethod
    def from_api_data(cls, producer_name: str, data: Dict) -> 'MetadataSample':
        """Create MetadataSample from API response data."""
        return cls(
            producer_name=producer_name,
            sample_frame_xml=data.get('sampleFrameXML', ''),
            schema_xml=data.get('schemaXML')
        )


class AnalyticsMetadataClient(FeatureClient[List[Producer]]):
    """Client for analytics metadata producer configuration.
    
    Provides functionality for:
    - Listing available metadata producers
    - Enabling/disabling producers on video channels
    - Getting sample metadata frames
    - Checking supported API versions
    """
    
    ANALYTICS_METADATA_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/analyticsmetadataconfig.cgi")
    
    def _make_request(self, method: str, params: Dict = None) -> Dict:
        """Make a JSON-RPC style request to the analytics metadata API."""
        if params is None:
            params = {}
            
        payload = {
            "apiVersion": "1.0",
            "context": "cli", 
            "method": method,
            "params": params
        }
        
        response = self.request(
            self.ANALYTICS_METADATA_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise FeatureError(
                "request_failed",
                f"Analytics metadata request failed: HTTP {response.status_code}, {response.text}"
            )
        
        try:
            result = response.json()
        except ValueError as e:
            raise FeatureError(
                "invalid_response",
                f"Failed to parse JSON response: {e}"
            )
        
        if 'error' in result:
            error = result['error']
            raise FeatureError(
                f"api_error_{error.get('code', 'unknown')}",
                error.get('message', 'Unknown API error')
            )
        
        return result.get('data', {})
    
    def list_producers(self) -> List[Producer]:
        """List all available metadata producers.
        
        Returns:
            List of Producer objects with their channel configurations
        """
        data = self._make_request("listProducers")
        
        producers = []
        for producer_data in data.get('producers', []):
            producers.append(Producer.from_api_data(producer_data))
        
        return producers
    
    def set_enabled_producers(self, producers: List[Producer]) -> None:
        """Enable or disable producers on specific video channels.
        
        Args:
            producers: List of producers with desired channel configurations
        """
        if not producers:
            raise FeatureError(
                "invalid_parameter",
                "At least one producer must be specified"
            )
        
        producer_configs = []
        for producer in producers:
            channels = [
                {"channel": ch.channel, "enabled": ch.enabled}
                for ch in producer.video_channels
            ]
            producer_configs.append({
                "name": producer.name,
                "videochannels": channels
            })
        
        params = {"producers": producer_configs}
        self._make_request("setEnabledProducers", params)
    
    def get_supported_metadata(self, producer_names: List[str]) -> List[MetadataSample]:
        """Get sample metadata frames for specified producers.
        
        Args:
            producer_names: List of producer names to get samples for
            
        Returns:
            List of MetadataSample objects containing sample frames
        """
        if not producer_names:
            raise FeatureError(
                "invalid_parameter", 
                "At least one producer name must be specified"
            )
        
        params = {"producers": producer_names}
        data = self._make_request("getSupportedMetadata", params)
        
        samples = []
        
        # The API response structure might be different than expected
        # Check if it's directly the sample data or nested
        if 'sampleFrameXML' in data:
            # Single producer response
            samples.append(MetadataSample.from_api_data(producer_names[0], data))
        else:
            # Multiple producers or nested structure
            for producer_name in producer_names:
                if producer_name in data and isinstance(data[producer_name], dict):
                    samples.append(MetadataSample.from_api_data(producer_name, data[producer_name]))
                elif isinstance(data, dict) and 'sampleFrameXML' in str(data):
                    # Fallback: try to extract from any dict value
                    for key, value in data.items():
                        if isinstance(value, dict) and 'sampleFrameXML' in value:
                            samples.append(MetadataSample.from_api_data(key, value))
        
        return samples
    
    def get_supported_versions(self) -> List[str]:
        """Get supported API versions.
        
        Returns:
            List of supported version strings
        """
        data = self._make_request("getSupportedVersions")
        
        # The response might contain supported versions directly or in a different structure
        if isinstance(data, list):
            return data
        elif 'supportedVersions' in data:
            return data['supportedVersions']
        elif 'versions' in data:
            return data['versions']
        else:
            # If it's a dict with version keys, return those keys
            if isinstance(data, dict) and all(key.replace('.', '').isdigit() for key in data.keys()):
                return list(data.keys())
        
        return []