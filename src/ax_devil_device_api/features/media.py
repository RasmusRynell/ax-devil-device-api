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
    
    def get_snapshot(self, resolution: str, compression: int, rotation: int, camera_head: int) -> bytes:
        """Capture a JPEG snapshot from the camera.
        
        Args:
            config: Optional media configuration parameters
            
        Returns:
            bytes containing the image data on success
        """
        if not (0 <= compression <= 100):
            raise FeatureError(
                "invalid_parameter",
                "Compression must be between 0 and 100"
            )
        if rotation not in [0, 90, 180, 270]:
            raise FeatureError(
                "invalid_parameter",
                "Rotation must be 0, 90, 180, or 270"
            )
            
        params = {
            "resolution": resolution,
            "compression": compression,
            "rotation": rotation,
            "camera": camera_head
        }

        response = self.request(
            self.SNAPSHOT_ENDPOINT,
            params=params,
            headers={"Accept": "image/jpeg"}
        )
            
        if response.status_code != 200:
            print(response.content)
            raise FeatureError(
                "snapshot_failed",
                f"Failed to capture snapshot: HTTP {response.status_code}"
            )
            
        return response.content