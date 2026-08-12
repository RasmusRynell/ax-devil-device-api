"""Main client interface for the ax-devil-device-api package."""

import warnings
from contextlib import AbstractContextManager, contextmanager

from .core.config import DeviceConfig
from .core.transport_client import TransportClient
from .features.analytics_metadata import AnalyticsMetadataClient
from .features.analytics_mqtt import AnalyticsMqttClient
from .features.api_discovery import ClassicAPIDiscoveryClient, DiscoveryClient
from .features.data_transformation import DataTransformationClient
from .features.device_debug import DeviceDebugClient
from .features.device_info import DeviceInfoClient
from .features.feature_flags import FeatureFlagClient
from .features.geocoordinates import GeoCoordinatesClient
from .features.media import MediaClient
from .features.mqtt_client import MqttClient
from .features.network import NetworkClient
from .features.ssh import SSHClient
from .features.systemready import SystemReadyClient


class Client:
    """Main client interface for a device.

    Primary entry point for interacting with a device.
    Provides access to all features through a unified interface and handles lazy loading of feature clients.

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
    """

    def __init__(self, config: DeviceConfig) -> None:
        """Initialize with device configuration."""
        self._core = TransportClient(config)
        self._closed = False

        # Lazy-loaded feature clients
        self._device: DeviceInfoClient | None = None
        self._network: NetworkClient | None = None
        self._media: MediaClient | None = None
        self._geocoordinates: GeoCoordinatesClient | None = None
        self._mqtt_client: MqttClient | None = None
        self._analytics_mqtt: AnalyticsMqttClient | None = None
        self._discovery: DiscoveryClient | None = None
        self._classic_discovery: ClassicAPIDiscoveryClient | None = None
        self._feature_flags: FeatureFlagClient | None = None
        self._ssh: SSHClient | None = None
        self._device_debug: DeviceDebugClient | None = None
        self._analytics_metadata: AnalyticsMetadataClient | None = None
        self._data_transformation: DataTransformationClient | None = None
        self._systemready: SystemReadyClient | None = None

    def __del__(self):
        """Attempt to clean up if user forgets to close.

        Note: This is a safety net, not a guarantee. Always use
        context manager or explicit close() for proper cleanup.
        """
        if not self._closed:
            warnings.warn(
                "Client was not properly closed. Please use 'with' statement or call close()",
                ResourceWarning,
                stacklevel=2,
            )
            try:
                self.close()
            except Exception:  # noqa: BLE001, S110 - destructor cleanup boundary
                # Suppress errors during interpreter shutdown
                pass

    def __enter__(self) -> "Client":  # noqa: PYI034 - supports Python 3.10
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
        if not self._closed and hasattr(self, "_core"):
            self._core._session.close()
            self._closed = True

    @contextmanager
    def new_session(self) -> AbstractContextManager["Client"]:
        """Create a temporary session for sensitive operations.

        This context manager creates a new session that will be used
        for all requests within its scope. The session is automatically
        closed when exiting the context.

        Example:
            ```python
            with client.new_session():
                # These operations use a fresh session
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
        """Access device information and management features."""
        if not self._device:
            self._device = DeviceInfoClient(self._core)
        return self._device

    @property
    def network(self) -> NetworkClient:
        """Access network configuration features."""
        if not self._network:
            self._network = NetworkClient(self._core)
        return self._network

    @property
    def media(self) -> MediaClient:
        """Access media streaming and snapshot features."""
        if not self._media:
            self._media = MediaClient(self._core)
        return self._media

    @property
    def geocoordinates(self) -> GeoCoordinatesClient:
        """Access geographic coordinates and orientation features."""
        if not self._geocoordinates:
            self._geocoordinates = GeoCoordinatesClient(self._core)
        return self._geocoordinates

    @property
    def mqtt_client(self) -> MqttClient:
        """Access MQTT client features."""
        if not self._mqtt_client:
            self._mqtt_client = MqttClient(self._core)
        return self._mqtt_client

    @property
    def analytics_mqtt(self) -> AnalyticsMqttClient:
        """Access analytics MQTT features."""
        if not self._analytics_mqtt:
            self._analytics_mqtt = AnalyticsMqttClient(self._core)
        return self._analytics_mqtt

    @property
    def discovery(self) -> DiscoveryClient:
        """Access Device Configuration API discovery."""
        if not self._discovery:
            self._discovery = DiscoveryClient(self._core)
        return self._discovery

    @property
    def classic_discovery(self) -> ClassicAPIDiscoveryClient:
        """Access classic VAPIX API Discovery."""
        if not self._classic_discovery:
            self._classic_discovery = ClassicAPIDiscoveryClient(self._core)
        return self._classic_discovery

    @property
    def feature_flags(self) -> FeatureFlagClient:
        """Access feature flag management features."""
        if not self._feature_flags:
            self._feature_flags = FeatureFlagClient(self._core)
        return self._feature_flags

    @property
    def ssh(self) -> SSHClient:
        """Get the SSH management client."""
        if not self._ssh:
            self._ssh = SSHClient(self._core)
        return self._ssh

    @property
    def device_debug(self) -> DeviceDebugClient:
        """Get the device debug client."""
        if not self._device_debug:
            self._device_debug = DeviceDebugClient(self._core)
        return self._device_debug

    @property
    def analytics_metadata(self) -> AnalyticsMetadataClient:
        """Get the analytics metadata producer configuration client."""
        if not self._analytics_metadata:
            self._analytics_metadata = AnalyticsMetadataClient(self._core)
        return self._analytics_metadata

    @property
    def data_transformation(self) -> DataTransformationClient:
        """Get the data transformation client."""
        if not self._data_transformation:
            self._data_transformation = DataTransformationClient(self._core)
        return self._data_transformation

    @property
    def systemready(self) -> SystemReadyClient:
        """Get the systemready client for checking device readiness."""
        if not self._systemready:
            self._systemready = SystemReadyClient(self._core)
        return self._systemready
