# ax-devil-device-api

A Python library for interacting with Axis device APIs. Provides a type-safe interface with tools for device management, configuration, and integration.

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
import json
from ax_devil_device_api import Client, DeviceConfig

# Initialize client (recommended way using context manager)
config = DeviceConfig.https("192.168.1.81", "root", "fusion", verify_ssl=False)
with Client(config) as client:
    device_info = client.device.get_info()
    print(json.dumps(device_info, indent=4))

# Alternative: Manual resource management (not recommended)
client = Client(config)
try:
    device_info = client.mqtt_client.get_status()
    print(json.dumps(device_info, indent=4))
finally:
    client.close()  # Always close the client when done
```

### CLI Usage Examples

Get device information
```bash
ax-devil-device-api-device-info --device-ip 192.168.1.10 --username admin --password secret info
```

Capture media
```bash
ax-devil-device-api-media --device-ip 192.168.1.10 --username admin --password secret --output image.jpg capture
```

Get SSH users
```bash
ax-devil-device-api-ssh --device-ip 192.168.1.10 --username admin --password secret list
```

Discover APIs
```bash
ax-devil-device-api-discovery --device-ip 192.168.1.10 --username admin --password secret list
```

And much more!

## Disclaimer

This project is an independent, community-driven implementation and is **not** affiliated with or endorsed by Axis Communications AB. For official APIs and development resources, please refer to [Axis Developer Community](https://www.axis.com/en-us/developer).

## License

MIT License - See LICENSE file for details.