"""
ax-devil-device-api: Axis Device Management API

A comprehensive Python library that provides a unified interface for Axis network devices,
focusing on device-level operations and configuration management. The library emphasizes:

- Type safety and robust error handling
- Secure communication with HTTPS support
- Modular design for easy feature extension
- Comprehensive device management capabilities

Key Features:
    - Device Management: Core device operations and configuration
    - Network Configuration: Network settings and connectivity
    - Media Handling: Streaming and snapshot capabilities
    - MQTT Integration: Protocol support for device communication
    - Geolocation: Location and positioning features
    - Analytics: MQTT-based analytics data handling

Example:
    ```python
    from ax_devil_device_api import Client, DeviceConfig
    
    # Create a client with HTTPS (recommended)
    config = DeviceConfig.https("device-ip", "user", "pass")
    client = Client(config)
    
    # Get device information
    info = client.device.get_info()
    if info.success:
        print(f"Model: {info.data.model}")
        print(f"Firmware: {info.data.firmware_version}")
    ```

For detailed documentation, see the project's README.md and docs/ directory.
"""

__version__ = "0.1.0"

from .core.config import DeviceConfig
from .client import Client

__all__ = [
    # Main interface
    'Client',
    'DeviceConfig',
] 