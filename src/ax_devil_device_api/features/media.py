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
    
    def get_snapshot(
        self,
        resolution: str | None = None,
        compression: int | None = None,
        camera_head: int | None = None,
    ) -> bytes:
        """Capture a JPEG snapshot from the camera.
        
        Args:
            resolution: Optional image resolution in WxH format
            compression: Optional JPEG compression level between 0 and 100
            camera_head: Optional camera head identifier for multi-sensor devices
            
        Returns:
            bytes containing the image data on success
        """
        if compression is not None and not isinstance(compression, int):
            raise FeatureError(
                "invalid_parameter", 
                "Compression must be an integer between 0 and 100"
            )
            
        if compression is not None and not (0 <= compression <= 100):
            raise FeatureError(
                "invalid_parameter",
                "Compression must be between 0 and 100"
            )
            
        params = {}
        if resolution is not None:
            params["resolution"] = resolution
        if compression is not None:
            params["compression"] = compression
        if camera_head is not None:
            params["camera"] = camera_head

        response = self.request(
            self.SNAPSHOT_ENDPOINT,
            params=params or None,
            headers={"Accept": "image/jpeg"}
        )
            
        if response.status_code != 200:
            raise FeatureError(
                "snapshot_failed",
                f"Failed to capture snapshot: HTTP {response.status_code}, {response.text}"
            )
            
        return response.content