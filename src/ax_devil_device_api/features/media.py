from dataclasses import dataclass
from typing import Optional, Dict
from .base import AxisFeatureClient
from ..core.types import TransportResponse, FeatureResponse
from ..core.endpoints import DeviceEndpoint
from ..utils.errors import FeatureError

@dataclass
class MediaConfig:
    """Media capture configuration.
    
    Attributes:
        resolution: Image resolution in WxH format (e.g., "1920x1080")
        compression: JPEG compression level (1-100)
        camera_head: Camera head identifier for multi-sensor devices
        rotation: Image rotation in degrees (0, 90, 180, or 270)
    """
    resolution: Optional[str] = None
    compression: Optional[int] = None
    camera_head: Optional[int] = None
    rotation: Optional[int] = None

    def validate(self) -> Optional[str]:
        """Validate configuration parameters.
        
        Returns:
            Error message if validation fails, None if valid.
        """
        if self.compression is not None:
            if not isinstance(self.compression, int) or not (1 <= self.compression <= 100):
                return "Compression must be an integer between 1 and 100"
                
        if self.rotation is not None:
            if self.rotation not in (0, 90, 180, 270):
                return "Rotation must be 0, 90, 180, or 270 degrees"
                
        return None

    def to_params(self) -> Dict[str, str]:
        """Convert configuration to request parameters."""
        params = {}
        if self.resolution:
            params["resolution"] = self.resolution
        if self.compression is not None:
            params["compression"] = str(self.compression)
        if self.camera_head is not None:
            params["camera"] = str(self.camera_head)
        if self.rotation is not None:
            params["rotation"] = str(self.rotation)
        return params

class MediaClient(AxisFeatureClient):
    """Client for camera media operations.
    
    Provides functionality for:
    - Capturing JPEG snapshots
    - Configuring media parameters
    - Retrieving media capabilities
    """
    
    # Endpoint definitions
    SNAPSHOT_ENDPOINT = DeviceEndpoint("GET", "/axis-cgi/jpg/image.cgi")
    
    def get_snapshot(self, config: Optional[MediaConfig] = None) -> FeatureResponse[bytes]:
        """Capture a JPEG snapshot from the camera.
        
        Args:
            config: Optional media configuration parameters
            
        Returns:
            FeatureResponse containing the image data on success
        """
        params = {}
        if config:
            # Validate configuration
            error = config.validate()
            if error:
                return FeatureResponse.create_error(FeatureError(
                    "invalid_config",
                    error
                ))
            params = config.to_params()
            
        response = self.request(
            self.SNAPSHOT_ENDPOINT,
            params=params,
            headers={"Accept": "image/jpeg"}
        )
        
        if not response.is_transport_success:
            return FeatureResponse.from_transport(response)
            
        raw_response = response.raw_response
        if raw_response.status_code != 200:
            return FeatureResponse.create_error(FeatureError(
                "snapshot_failed",
                f"Failed to capture snapshot: HTTP {raw_response.status_code}"
            ))
            
        try:
            return FeatureResponse.ok(raw_response.content)
        except Exception as e:
            return FeatureResponse.create_error(FeatureError(
                "parse_error",
                f"Failed to process snapshot data: {str(e)}"
            )) 