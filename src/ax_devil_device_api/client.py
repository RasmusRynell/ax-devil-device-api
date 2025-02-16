"""Main client interface for the ax-devil-device-api package."""

from typing import Optional
from ax_devil_device_api.core.client import CameraClient
from ax_devil_device_api.core.config import CameraConfig
from ax_devil_device_api.features.device import DeviceClient
from ax_devil_device_api.features.network import NetworkClient
from ax_devil_device_api.features.media import MediaClient
from ax_devil_device_api.features.geocoordinates import GeoCoordinatesClient
from ax_devil_device_api.features.mqtt_client import MqttClient
from ax_devil_device_api.features.analytics_mqtt import AnalyticsMqttClient

class Client:
    """Main client interface for Axis cameras.
    
    This is the primary entry point for interacting with Axis cameras.
    It provides access to all features through a unified interface and
    handles lazy loading of feature clients.
    
    Example:
        ```python
        from ax_devil_device_api import Client, CameraConfig
        
        # Create a client
        config = CameraConfig.https("camera.local", "user", "pass")
        client = Client(config)
        
        # Access features
        info = client.device.get_info()
        ```
    """
    
    def __init__(self, config: CameraConfig) -> None:
        """Initialize with camera configuration."""
        self._core = CameraClient(config)
        
        # Lazy-loaded feature clients
        self._device: Optional[DeviceClient] = None
        self._network: Optional[NetworkClient] = None
        self._media: Optional[MediaClient] = None
        self._geocoordinates: Optional[GeoCoordinatesClient] = None
        self._mqtt_client: Optional[MqttClient] = None
        self._analytics_mqtt: Optional[AnalyticsMqttClient] = None
    
    @property
    def device(self) -> DeviceClient:
        """Access device operations."""
        if not self._device:
            self._device = DeviceClient(self._core)
        return self._device
    
    @property
    def network(self) -> NetworkClient:
        """Access network operations."""
        if not self._network:
            self._network = NetworkClient(self._core)
        return self._network

    @property
    def media(self) -> MediaClient:
        """Access media operations."""
        if not self._media:
            self._media = MediaClient(self._core)
        return self._media

    @property
    def geocoordinates(self) -> GeoCoordinatesClient:
        """Access geographic coordinates and orientation operations."""
        if not self._geocoordinates:
            self._geocoordinates = GeoCoordinatesClient(self._core)
        return self._geocoordinates

    @property
    def mqtt_client(self) -> MqttClient:
        """Access MQTT client operations."""
        if not self._mqtt_client:
            self._mqtt_client = MqttClient(self._core)
        return self._mqtt_client

    @property
    def analytics_mqtt(self) -> AnalyticsMqttClient:
        """Access analytics MQTT operations."""
        if not self._analytics_mqtt:
            self._analytics_mqtt = AnalyticsMqttClient(self._core)
        return self._analytics_mqtt
