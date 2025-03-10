# ax-devil-device-api

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Hints](https://img.shields.io/badge/Type%20Hints-Strict-brightgreen.svg)](https://www.python.org/dev/peps/pep-0484/)

A Python library for interacting with Axis device APIs. Provides a type-safe interface with tools for device management, configuration, and integration.

</div>

---

## 📋 Contents

- [Feature Overview](#-feature-overview)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Disclaimer](#-disclaimer)
- [License](#-license)

---

## 🔍 Feature Overview

<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>Description</th>
      <th align="center">Python API</th>
      <th align="center">CLI Tool</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>📱 Device Information</b></td>
      <td>Get device details, check health status, and restart device</td>
      <td align="center"><code>client.device</code></td>
      <td align="center"><a href="#device-info-cli">ax-devil-device-api-device-info</a></td>
    </tr>
    <tr>
      <td><b>🔧 Device Debugging</b></td>
      <td>Download server reports, crash reports, and run diagnostics</td>
      <td align="center"><code>client.device_debug</code></td>
      <td align="center"><a href="#device-debug-cli">ax-devil-device-api-device-debug</a></td>
    </tr>
    <tr>
      <td><b>📷 Media Operations</b></td>
      <td>Capture snapshots from device cameras</td>
      <td align="center"><code>client.media</code></td>
      <td align="center"><a href="#media-cli">ax-devil-device-api-media</a></td>
    </tr>
    <tr>
      <td><b>🔐 SSH Management</b></td>
      <td>Add, list, modify, and remove SSH users</td>
      <td align="center"><code>client.ssh</code></td>
      <td align="center"><a href="#ssh-cli">ax-devil-device-api-ssh</a></td>
    </tr>
    <tr>
      <td><b>📡 MQTT Client</b></td>
      <td>Configure, activate, deactivate, and check MQTT client status</td>
      <td align="center"><code>client.mqtt_client</code></td>
      <td align="center"><a href="#mqtt-client-cli">ax-devil-device-api-mqtt-client</a></td>
    </tr>
    <tr>
      <td><b>📊 Analytics MQTT</b></td>
      <td>Manage analytics data sources and publishers for MQTT</td>
      <td align="center"><code>client.analytics_mqtt</code></td>
      <td align="center"><a href="#analytics-mqtt-cli">ax-devil-device-api-analytics-mqtt</a></td>
    </tr>
    <tr>
      <td><b>🔎 API Discovery</b></td>
      <td>List and inspect available APIs on the device</td>
      <td align="center"><code>client.discovery</code></td>
      <td align="center"><a href="#api-discovery-cli">ax-devil-device-api-discovery</a></td>
    </tr>
    <tr>
      <td><b>🌍 Geocoordinates</b></td>
      <td>Get and set device location and orientation</td>
      <td align="center"><code>client.geocoordinates</code></td>
      <td align="center"><a href="#geocoordinates-cli">ax-devil-device-api-geocoordinates</a></td>
    </tr>
    <tr>
      <td><b>🚩 Feature Flags</b></td>
      <td>List, get, and set device feature flags</td>
      <td align="center"><code>client.feature_flags</code></td>
      <td align="center"><a href="#feature-flags-cli">ax-devil-device-api-feature-flags</a></td>
    </tr>
    <tr>
      <td><b>🌐 Network</b></td>
      <td>Get network interface information</td>
      <td align="center"><code>client.network</code></td>
      <td align="center"><a href="#network-cli">ax-devil-device-api-network</a></td>
    </tr>
  </tbody>
</table>

---

## 🚀 Quick Start

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

---

## 💻 Usage Examples

### Python API Usage

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
    device_info = client.mqtt_client.get_state()
    print(json.dumps(device_info, indent=4))
finally:
    client.close()  # Always close the client when done
```

### CLI Usage Examples

<details open>
<summary><a name="device-info-cli"></a><b>📱 Device Information</b></summary>
<p>

```bash
# Get device information
ax-devil-device-api-device-info --device-ip 192.168.1.10 --username admin --password secret info

# Check device health
ax-devil-device-api-device-info --device-ip 192.168.1.10 --username admin --password secret health

# Restart device
ax-devil-device-api-device-info --device-ip 192.168.1.10 --username admin --password secret restart
```
</p>
</details>

<details>
<summary><a name="device-debug-cli"></a><b>🔧 Device Debugging</b></summary>
<p>

```bash
# Download server report
ax-devil-device-api-device-debug --device-ip 192.168.1.10 --username admin --password secret download_server_report report.tar.gz

# Download crash report
ax-devil-device-api-device-debug --device-ip 192.168.1.10 --username admin --password secret download_crash_report crash.tar.gz
```
</p>
</details>

<details>
<summary><a name="media-cli"></a><b>📷 Media Operations</b></summary>
<p>

```bash
# Capture snapshot
ax-devil-device-api-media --device-ip 192.168.1.10 --username admin --password secret --output image.jpg snapshot
```
</p>
</details>

<details>
<summary><a name="ssh-cli"></a><b>🔐 SSH Management</b></summary>
<p>

```bash
# List SSH users
ax-devil-device-api-ssh --device-ip 192.168.1.10 --username admin --password secret list

# Add SSH user
ax-devil-device-api-ssh --device-ip 192.168.1.10 --username admin --password secret add new-user password123

# Remove SSH user
ax-devil-device-api-ssh --device-ip 192.168.1.10 --username admin --password secret remove user123
```
</p>
</details>

<details>
<summary><a name="mqtt-client-cli"></a><b>📡 MQTT Client</b></summary>
<p>

```bash
# Activate MQTT client
ax-devil-device-api-mqtt-client --device-ip 192.168.1.10 --username admin --password secret activate

# Deactivate MQTT client
ax-devil-device-api-mqtt-client --device-ip 192.168.1.10 --username admin --password secret deactivate
```
</p>
</details>

<details>
<summary><a name="analytics-mqtt-cli"></a><b>📊 Analytics MQTT</b></summary>
<p>

```bash
# List available analytics data sources
ax-devil-device-api-analytics-mqtt --device-ip 192.168.1.10 --username admin --password secret sources

# List configured publishers
ax-devil-device-api-analytics-mqtt --device-ip 192.168.1.10 --username admin --password secret list
```
</p>
</details>

<details>
<summary><a name="api-discovery-cli"></a><b>🔎 API Discovery</b></summary>
<p>

```bash
# List available APIs
ax-devil-device-api-discovery --device-ip 192.168.1.10 --username admin --password secret list

# Get API info
ax-devil-device-api-discovery --device-ip 192.168.1.10 --username admin --password secret info vapix
```
</p>
</details>

<details>
<summary><a name="geocoordinates-cli"></a><b>🌍 Geocoordinates</b></summary>
<p>

```bash
# Get current location coordinates
ax-devil-device-api-geocoordinates --device-ip 192.168.1.10 --username admin --password secret location get

# Set location coordinates
ax-devil-device-api-geocoordinates --device-ip 192.168.1.10 --username admin --password secret location set 59.3293 18.0686
```
</p>
</details>

<details>
<summary><a name="feature-flags-cli"></a><b>🚩 Feature Flags</b></summary>
<p>

```bash
# List all feature flags
ax-devil-device-api-feature-flags --device-ip 192.168.1.10 --username admin --password secret list

# Set feature flags
ax-devil-device-api-feature-flags --device-ip 192.168.1.10 --username admin --password secret set feature_name=true
```
</p>
</details>

<details>
<summary><a name="network-cli"></a><b>🌐 Network</b></summary>
<p>

```bash
# Get network interface information
ax-devil-device-api-network --device-ip 192.168.1.10 --username admin --password secret info
```
</p>
</details>

> **Note:** For more CLI examples, check the [examples directory](src/ax_devil_device_api/examples) in the source code.

---

## ⚠️ Disclaimer

This project is an independent, community-driven implementation and is **not** affiliated with or endorsed by Axis Communications AB. For official APIs and development resources, please refer to [Axis Developer Community](https://www.axis.com/en-us/developer).

## 📄 License

MIT License - See LICENSE file for details.
