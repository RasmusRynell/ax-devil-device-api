# ax-devil-device-api

A Python library for interacting with Axis device APIs. Provides a type-safe interface with tools for device management, configuration, and integration.

## Important Disclaimer

This project is an independent, community-driven implementation and is **not** affiliated with or endorsed by Axis Communications AB. For official APIs and development resources, please refer to [Axis Developer Community](https://www.axis.com/en-us/developer).

## Quick Start

### Installation

```bash
pip install ax-devil-device-api
```

### Environment Variables
For an easier experience, you can set the following environment variables:
```bash
export AX_DEVIL_TARGET_ADDR=<device-ip>
export AX_DEVIL_TARGET_USER=<username>
export AX_DEVIL_TARGET_PASS=<password>
export AX_DEVIL_USAGE_CLI="safe" # Set to "unsafe" to skip SSL certificate verification for CLI calls
```

### Example Usage

```python
from ax_devil_device_api import Client, DeviceConfig

# Initialize client (recommended way using context manager)
config = DeviceConfig.https("192.168.1.10", "admin", "password")
with Client(config) as client:
    # Get device information
    device_info = client.device.get_info()
    if device_info.success:
        print(f"Model: {device_info.data.model}")
        print(f"Serial: {device_info.data.serial}")
        
    # Use a fresh session for sensitive operations
    with client.new_session():
        client.device.restart()

# Alternative: Manual resource management (not recommended)
client = Client(config)
try:
    device_info = client.device.get_info()
    if device_info.success:
        print(f"Model: {device_info.data.model}")
finally:
    client.close()  # Always close the client when done
```

### CLI Usage

```bash
# Get device information
ax-devil-device-api-device --device-ip 192.168.1.10 --username admin --password secret info

# Capture media
ax-devil-device-api-media --device-ip 192.168.1.10 --username admin --password secret --output image.jpg capture
```

## License

MIT License - See LICENSE file for details.