"""Main client interface for the ax-devil-device-api package."""

from typing import Optional, ContextManager
from contextlib import contextmanager
import warnings
from ax_devil_device_api.core.client import DeviceClient
from ax_devil_device_api.core.config import DeviceConfig
from ax_devil_device_api.features.device_info import DeviceInfoClient
from ax_devil_device_api.features.network import NetworkClient
from ax_devil_device_api.features.media import MediaClient
from ax_devil_device_api.features.geocoordinates import GeoCoordinatesClient
from ax_devil_device_api.features.mqtt_client import MqttClient
from ax_devil_device_api.features.analytics_mqtt import AnalyticsMqttClient
from ax_devil_device_api.features.api_discovery import DiscoveryClient

class Client:
    """Main client interface for a device.
    
    This is the primary entry point for interacting with a device.
    It provides access to all features through a unified interface and
    handles lazy loading of feature clients.
    
    The client maintains a persistent HTTP session for optimal performance
    and resource usage. The session handles connection pooling, cookie
    persistence, and SSL session reuse automatically.
    
    Warning:
        Always use the client as a context manager or explicitly call close()
        when done. While the session will eventually be cleaned up by Python's
        garbage collector, not closing it properly may temporarily:
        - Leave connections open on the device
        - Hold network resources longer than necessary
        - Impact connection pooling for other operations
    
    Example:
        ```python
        from ax_devil_device_api import Client, DeviceConfig
        
        # Create a client
        config = DeviceConfig.https("device-ip", "user", "pass")
        
        # Using as context manager (recommended)
        with Client(config) as client:
            info = client.device.get_info()
            
            # Use a fresh session for sensitive operations
            with client.new_session():
                client.device.restart()
        
        # Or manually managing the client (not recommended)
        client = Client(config)
        try:
            info = client.device.get_info()
            
            # Clear session if needed
            client.clear_session()
            client.device.restart()
        finally:
            client.close()
        ```
    """
    
    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self._core = DeviceClient(config)
        self._closed = False
        
        # Lazy-loaded feature clients
        self._device: Optional[DeviceInfoClient] = None
        self._network: Optional[NetworkClient] = None
        self._media: Optional[MediaClient] = None
        self._geocoordinates: Optional[GeoCoordinatesClient] = None
        self._mqtt_client: Optional[MqttClient] = None
        self._analytics_mqtt: Optional[AnalyticsMqttClient] = None
        self._discovery: Optional[DiscoveryClient] = None
    
    def __del__(self):
        """Attempt to clean up if user forgets to close.
        
        Note: This is a safety net, not a guarantee. Always use
        context manager or explicit close() for proper cleanup.
        """
        if not self._closed:
            warnings.warn(
                "Client was not properly closed. Please use 'with' statement or call close()",
                ResourceWarning,
                stacklevel=2
            )
            try:
                self.close()
            except:
                # Suppress errors during interpreter shutdown
                pass
    
    def __enter__(self) -> 'Client':
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and cleanup resources."""
        self.close()
    
    def close(self) -> None:
        """Close the client and cleanup resources.
        
        This method should be called when the client is no longer needed
        to ensure proper cleanup of network resources. It's recommended
        to use the client as a context manager instead of calling this
        directly.
        """
        if not self._closed and hasattr(self, '_core'):
            self._core._session.close()
            self._closed = True
    
    @contextmanager
    def new_session(self) -> ContextManager['Client']:
        """Create a temporary new session.
        
        This is useful for operations that need a clean session state,
        such as sensitive operations or when you want to ensure no
        previous session state affects the requests.
        
        Example:
            ```python
            with client.new_session():
                # These operations will use a fresh session
                client.device.restart()
            # Back to the original session
            ```
        """
        with self._core.new_session():
            yield self
    
    def clear_session(self) -> None:
        """Clear and reset the current session.
        
        This is useful when you want to clear any stored cookies
        or connection state without creating a new session.
        """
        self._core.clear_session()
    
    @property
    def device(self) -> DeviceInfoClient:
        """Access device operations."""
        if not self._device:
            self._device = DeviceInfoClient(self._core)
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

    @property
    def discovery(self) -> DiscoveryClient:
        """Access API discovery operations."""
        if not self._discovery:
            self._discovery = DiscoveryClient(self._core)
        return self._discovery
