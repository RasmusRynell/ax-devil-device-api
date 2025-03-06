import json
from ax_devil_device_api import Client, DeviceConfig

# Initialize client (recommended way using context manager)
config = DeviceConfig.https("192.168.1.81", "root", "fusion", verify_ssl=True)
with Client(config) as client:
    device_info = client.device.get_info()
    if not device_info.is_success:
        raise device_info.error
    print(json.dumps(device_info.data.to_dict(), indent=4))

# Alternative: Manual resource management (not recommended)
client = Client(config)
try:
    device_info = client.mqtt_client.get_status()
    if not device_info.is_success:
        raise device_info.error
    print(json.dumps(device_info.data.to_dict(), indent=4))
finally:
    client.close()  # Always close the client when done