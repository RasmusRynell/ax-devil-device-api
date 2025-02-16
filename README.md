# ax-devil-device-api

A Python library for interacting with Axis device APIs. Provides a type-safe interface with tools for device management, configuration, and integration. Makes device interactions predictable and easier to debug.

## Important Disclaimer

This project is an independent, community-driven implementation and is **not** affiliated with or endorsed by Axis Communications AB. For official APIs and development resources, please refer to:
- [Axis Developer Community](https://www.axis.com/en-us/developer)

This library is provided "as is" without any guarantees regarding compatibility with future Axis firmware updates.

## Features

- **Device Management**: Core device operations and configuration
- **Network Configuration**: Network settings and connectivity management
- **Media Handling**: Media streaming and snapshot capabilities
- **MQTT Integration**: MQTT protocol support for device communication
- **Geolocation**: Location and positioning features
- **Analytics**: MQTT-based analytics data handling

## Installation

```bash
pip install ax-devil-device-api
```

## Quick Start

```python
from ax_devil_device_api import Client, CameraConfig

# Create a client with HTTPS (recommended)
config = CameraConfig.https("192.168.1.10", "admin", "password")
client = Client(config)

# Get device information
device_info = client.device.get_info()
if device_info.success:
    print(f"Model: {device_info.data.model}")
    print(f"Serial: {device_info.data.serial}")
    print(f"Firmware: {device_info.data.firmware_version}")
```

## CLI Tools

The package includes several command-line tools for common operations:

```bash
# Get device information
ax-devil-device-api-device info --host 192.168.1.10 --username admin --password secret

# List analytics and check MQTT status
ax-devil-device-api-analytics-mqtt list --host 192.168.1.10 --username admin --password secret
ax-devil-device-api-mqtt-client status --host 192.168.1.10 --username admin --password secret

# Capture media
ax-devil-device-api-media capture --host 192.168.1.10 --username admin --password secret --output image.jpg

# Get and set geocoordinates
ax-devil-device-api-geocoordinates location get --host 192.168.1.10 --username admin --password secret
ax-devil-device-api-geocoordinates orientation set 2.5 180 --host 192.168.1.10 --username admin --password secret
```

## Key Features

### Type-Safe API
- Comprehensive type hints throughout the codebase
- Clear error handling with typed responses
- IDE-friendly development experience

### Security First
- HTTPS support with certificate validation
- Secure authentication handling
- Protection against common security issues

### Modular Design
- Clean separation of concerns
- Extensible architecture
- Easy to add new features

### Robust Error Handling
- Detailed error information
- Transport-level error isolation
- Feature-specific error types

## Documentation

For detailed documentation, see the `docs/` directory:
- [Current Architecture](docs/CURRENT_ARCHITECTURE.md)
- [Feature Development Guide](docs/FEATURE_DEVELOPMENT.md)
- [Vision and Philosophy](docs/VISION.md)

## Development

```bash
# Setup development environment
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests (requires camera)
pytest -v

## License

MIT License - See LICENSE file for details.