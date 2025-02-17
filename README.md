# ax-devil-device-api

A Python library for interacting with Axis device APIs. Provides a type-safe interface with tools for device management, configuration, and integration.

## Important Disclaimer

This project is an independent, community-driven implementation and is **not** affiliated with or endorsed by Axis Communications AB. For official APIs and development resources, please refer to:
- [Axis Developer Community](https://www.axis.com/en-us/developer)

## Features

- Type-safe API with comprehensive error handling
- Device management and configuration
- Network and connectivity management
- Media streaming and snapshot capabilities
- MQTT protocol support
- Geolocation and analytics features

## Installation

```bash
pip install ax-devil-device-api
```

## Quick Start

```python
from ax_devil_device_api import Client, CameraConfig

# Initialize client
config = CameraConfig.https("192.168.1.10", "admin", "password")
client = Client(config)

# Get device information
device_info = client.device.get_info()
if device_info.success:
    print(f"Model: {device_info.data.model}")
    print(f"Serial: {device_info.data.serial}")
```

## CLI Usage

```bash
# Get device information
ax-devil-device-api-device --camera-ip 192.168.1.10 --username admin --password secret info

# Capture media
ax-devil-device-api-media --camera-ip 192.168.1.10 --username admin --password secret --output image.jpg capture
```


## License

MIT License - See LICENSE file for details.