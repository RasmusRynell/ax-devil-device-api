from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


class MediaClient(FeatureClient):
    """Client for camera media operations.
    
    Provides functionality for:
    - Capturing JPEG snapshots
    - Configuring media parameters
    - Retrieving media capabilities
    """
    
    # Endpoint definitions
    SNAPSHOT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/jpg/image.cgi")
    
    def get_snapshot(self, resolution: str, compression: int, camera_head: int) -> bytes:
        """Capture a JPEG snapshot from the camera.
        
        Args:
            config: Optional media configuration parameters
            
        Returns:
            bytes containing the image data on success
        """
        if not isinstance(compression, int):
            raise FeatureError(
                "invalid_parameter", 
                "Compression must be an integer between 0 and 100"
            )
            
        if not (0 <= compression <= 100):
            raise FeatureError(
                "invalid_parameter",
                "Compression must be between 0 and 100"
            )
            
        params = {
            "resolution": resolution,
            "compression": compression,
            "camera": camera_head
        }

        response = self.request(
            self.SNAPSHOT_ENDPOINT,
            params=params,
            headers={"Accept": "image/jpeg"}
        )
            
        if response.status_code != 200:
            raise FeatureError(
                "snapshot_failed",
                f"Failed to capture snapshot: HTTP {response.status_code}, {response.text}"
            )
            
        return response.content