# ax-devil-device-api Python API Reference

**Install**: `pip install ax-devil-device-api` (or `uv pip install ax-devil-device-api`)

Public exports from `ax_devil_device_api`:

- `Client` — Main entry point, provides access to all feature clients
- `DeviceConfig` — Connection configuration

## DeviceConfig

```python
from ax_devil_device_api import DeviceConfig

# HTTPS (default — self-signed certs, verify_ssl=False)
config = DeviceConfig.https(host="<device-ip>", username="<user>", password="<pass>")

# HTTP (explicit insecure opt-in)
config = DeviceConfig.http(host="<device-ip>", username="<user>", password="<pass>")
```

- `verify_ssl=True` is not implemented yet — always use `False` (default).
- `config.get_base_url()` returns `"https://<host>"` or `"http://<host>"`.

## Client

Use as a context manager for proper session cleanup. Feature clients are lazy-loaded via properties.

```python
from ax_devil_device_api import Client, DeviceConfig

config = DeviceConfig.https(host="<device-ip>", username="<user>", password="<pass>")

with Client(config) as client:
    info = client.device.get_info()
    snapshot = client.media.get_snapshot()
```

### Available feature clients

| Property | Feature area |
|----------|-------------|
| `client.device` | Device info, health, restart |
| `client.network` | Network interface details |
| `client.media` | Snapshots |
| `client.mqtt_client` | MQTT client configure/activate/deactivate |
| `client.analytics_mqtt` | Analytics MQTT publishers and data sources |
| `client.analytics_metadata` | Metadata producer management |
| `client.discovery` | API discovery |
| `client.feature_flags` | Feature flag get/set |
| `client.geocoordinates` | Location and orientation |
| `client.ssh` | SSH user management |
| `client.device_debug` | Debug reports, traces, ping |
| `client.data_transformation` | jq expression-based data transforms |
| `client.systemready` | Device readiness check (no auth needed) |

### Client methods

- `client.close()` — Close session (called automatically by context manager).
- `client.clear_session()` — Reset cookies/connection state.
- `client.new_session()` — Context manager for a temporary fresh session.

## Feature Clients — Quick Reference

Each feature client has methods matching the CLI subcommands. Use your IDE autocomplete or `help()` to explore.

### DeviceInfoClient (`client.device`)

```python
client.device.get_info() -> dict             # Model, firmware, serial
client.device.get_info_detailed() -> dict     # Extended raw parameters
client.device.get_info_no_auth() -> dict      # Basic info without credentials (basicdeviceinfo.cgi)
client.device.get_info_auth() -> dict         # Full info with credentials (basicdeviceinfo.cgi)
client.device.check_health() -> bool          # Health check
client.device.restart() -> bool               # Restart device
```

### NetworkClient (`client.network`)

```python
client.network.get_network_info() -> dict   # Network interface parameters
```

### MediaClient (`client.media`)

```python
client.media.get_snapshot(
    resolution="1920x1080",   # Optional
    compression=50,           # Optional (0-100)
    camera_head=1,            # Optional (multi-sensor devices)
) -> bytes                    # JPEG image data
```

### MqttClient (`client.mqtt_client`)

```python
client.mqtt_client.configure(
    host="<broker-ip>",
    port=1883,                        # Default
    username=None,                    # Optional broker auth
    password=None,                    # Optional broker auth
    protocol="tcp",                   # "tcp" or "ssl"
    keep_alive_interval=60,           # Seconds
    client_id="client1",
    clean_session=True,
    auto_reconnect=True,
    device_topic_prefix=None,         # Optional topic prefix
)
client.mqtt_client.activate() -> dict       # Start MQTT client
client.mqtt_client.deactivate() -> dict     # Stop MQTT client
client.mqtt_client.get_state() -> dict      # {"status": {...}, "config": {...}}
client.mqtt_client.set_state(state) -> dict # Set state (same shape as get_state)
```

### AnalyticsMqttClient (`client.analytics_mqtt`)

```python
client.analytics_mqtt.get_data_sources() -> list[dict]
client.analytics_mqtt.list_publishers() -> list[dict]
client.analytics_mqtt.create_publisher(
    id, data_source_key, mqtt_topic,
    qos=0, retain=False, use_topic_prefix=False,
)
client.analytics_mqtt.remove_publisher(publisher_id)
```

### AnalyticsMetadataClient (`client.analytics_metadata`)

```python
client.analytics_metadata.list_producers() -> list
client.analytics_metadata.set_enabled_producers(producers)
client.analytics_metadata.get_supported_metadata(producer_names) -> list
client.analytics_metadata.get_supported_versions() -> list[str]
```

### FeatureFlagClient (`client.feature_flags`)

```python
client.feature_flags.list_all() -> list[dict]
client.feature_flags.get_flags(["flag1", "flag2"]) -> dict
client.feature_flags.set_flags({"flag1": True, "flag2": False}) -> dict
```

### GeoCoordinatesClient (`client.geocoordinates`)

```python
client.geocoordinates.get_location() -> dict
client.geocoordinates.set_location(latitude=57.7, longitude=12.0) -> bool
client.geocoordinates.get_orientation() -> dict    # heading, tilt, roll, installation_height
client.geocoordinates.set_orientation({"heading": 45, "tilt": 5, "roll": 0, "installation_height": 3.0}) -> bool
client.geocoordinates.apply_settings() -> bool
```

### SSHClient (`client.ssh`)

```python
client.ssh.get_users() -> list[dict]
client.ssh.add_user("myuser", "mypass", comment="Service account")
client.ssh.get_user("myuser") -> dict
client.ssh.modify_user("myuser", password="newpass")
client.ssh.remove_user("myuser")
```

### DiscoveryClient (`client.discovery`)

```python
collection = client.discovery.discover()

# DiscoveredAPICollection methods
apis = collection.get_all_apis()              # All discovered APIs (flat list)
api = collection.get_api("api-name")          # Latest version of a specific API
api = collection.get_api("api-name", "v1")    # Specific version
versions = collection.get_apis_by_name("api-name")  # All versions of an API

# DiscoveredAPI properties and methods
api.rest_api_url                              # REST API endpoint URL
api.rest_ui_url                               # Swagger UI URL
api.get_documentation() -> str                # Markdown documentation
api.get_documentation_html() -> str           # HTML documentation
api.get_model() -> dict                       # JSON model
api.get_openapi_spec() -> dict                # OpenAPI specification
```

### DataTransformationClient (`client.data_transformation`)

```python
client.data_transformation.get_available_topics() -> list[dict]
client.data_transformation.list_transforms() -> list[dict]
client.data_transformation.create_transform(input_topic, output_topic, jq_expression)
client.data_transformation.remove_transform(output_topic)
```

### DeviceDebugClient (`client.device_debug`)

```python
client.device_debug.download_server_report() -> bytes
client.device_debug.download_crash_report() -> bytes
client.device_debug.download_network_trace(duration=30, interface=None) -> bytes
client.device_debug.collect_core_dump() -> bytes
client.device_debug.ping_test("example.com") -> str
client.device_debug.port_open_test("10.0.0.1", 8080) -> str
```

### SystemReadyClient (`client.systemready`)

```python
client.systemready.systemready(timeout=20) -> dict
client.systemready.get_supported_versions() -> list[str]
```

## Typical Python Workflows

### Get device info

```python
from ax_devil_device_api import Client, DeviceConfig

config = DeviceConfig.https(host="<device-ip>", username="<user>", password="<pass>")
with Client(config) as client:
    print(client.device.get_info())
```

### Take a snapshot and save to file

```python
with Client(config) as client:
    jpeg = client.media.get_snapshot(resolution="1280x720")
    with open("snapshot.jpg", "wb") as f:
        f.write(jpeg)
```

### Set up analytics MQTT publishing

```python
with Client(config) as client:
    # Configure broker and activate
    client.mqtt_client.configure(host="<broker-ip>", port=1883)
    client.mqtt_client.activate()

    # Find available sources
    sources = client.analytics_mqtt.get_data_sources()

    # Create a publisher
    client.analytics_mqtt.create_publisher(
        id="my-pub",
        data_source_key=sources[0]["key"],
        mqtt_topic="my/analytics/topic",
    )
```

### Check if device is ready (no auth)

```python
config = DeviceConfig.https(host="<device-ip>", username="", password="")
with Client(config) as client:
    result = client.systemready.systemready(timeout=30)
    print(result)
```
