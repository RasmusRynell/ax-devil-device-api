# ax-devil-device-api

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Hints](https://img.shields.io/badge/Type%20Hints-Strict-brightgreen.svg)](https://www.python.org/dev/peps/pep-0484/)

A Python library for interacting with Axis device APIs. Provides a type-safe interface with tools for device management, configuration, and integration.

See also: [ax-devil-mqtt](https://github.com/rasmusrynell/ax-devil-mqtt) for using MQTT with an Axis device.

</div>

---

## 📋 Contents

- [Feature Overview](#-feature-overview)
- [Quick Start](#-quick-start)
- [Development Setup](#-development-setup)
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
      <td align="center"><a href="#device-operations">ax-devil-device-api device</a></td>
    </tr>
    <tr>
      <td><b>🔧 Device Debugging</b></td>
      <td>Download server reports, crash reports, and run diagnostics</td>
      <td align="center"><code>client.device_debug</code></td>
      <td align="center"><a href="#device-debugging">ax-devil-device-api debug</a></td>
    </tr>
    <tr>
      <td><b>📷 Media Operations</b></td>
      <td>Capture snapshots from device cameras</td>
      <td align="center"><code>client.media</code></td>
      <td align="center"><a href="#media-operations">ax-devil-device-api media</a></td>
    </tr>
    <tr>
      <td><b>🔐 SSH Management</b></td>
      <td>Add, list, modify, and remove SSH users</td>
      <td align="center"><code>client.ssh</code></td>
      <td align="center"><a href="#ssh-management">ax-devil-device-api ssh</a></td>
    </tr>
    <tr>
      <td><b>📡 MQTT Client</b></td>
      <td>Configure, activate, deactivate, and check MQTT client status</td>
      <td align="center"><code>client.mqtt_client</code></td>
      <td align="center"><a href="#mqtt-client">ax-devil-device-api mqtt</a></td>
    </tr>
    <tr>
      <td><b>📊 Analytics MQTT</b></td>
      <td>Manage analytics data sources and publishers for MQTT</td>
      <td align="center"><code>client.analytics_mqtt</code></td>
      <td align="center"><a href="#analytics-mqtt">ax-devil-device-api analytics</a></td>
    </tr>
    <tr>
      <td><b>🔎 API Discovery</b></td>
      <td>List and inspect available APIs on the device</td>
      <td align="center"><code>client.discovery</code></td>
      <td align="center"><a href="#api-discovery">ax-devil-device-api discovery</a></td>
    </tr>
    <tr>
      <td><b>🌍 Geocoordinates</b></td>
      <td>Get and set device location and orientation</td>
      <td align="center"><code>client.geocoordinates</code></td>
      <td align="center"><a href="#geocoordinates">ax-devil-device-api geocoordinates</a></td>
    </tr>
    <tr>
      <td><b>🚩 Feature Flags</b></td>
      <td>List, get, and set device feature flags</td>
      <td align="center"><code>client.feature_flags</code></td>
      <td align="center"><a href="#feature-flags">ax-devil-device-api features</a></td>
    </tr>
    <tr>
      <td><b>🌐 Network</b></td>
      <td>Get network interface information</td>
      <td align="center"><code>client.network</code></td>
      <td align="center"><a href="#network-operations">ax-devil-device-api network</a></td>
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

## 🛠️ Development Setup

- Create and activate a virtual environment.
- Install the package with development extras (dev dependencies now live in `pyproject.toml`): `pip install -e ".[dev]"`
- Run the test suite with `pytest` (use `pytest --cov` for coverage).

---

## 💻 Usage Examples

### Python API Usage

```python
import json
from ax_devil_device_api import Client, DeviceConfig

# Initialize client (recommended way using context manager)
config = DeviceConfig.https("192.168.1.81", "root", "pass", verify_ssl=False)
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

#### 🎯 New Unified CLI (Recommended)

The project now provides a unified CLI with organized subcommands:

```bash
# Main help - shows all available subcommands
ax-devil-device-api --help

# Check version
ax-devil-device-api --version

# Set common parameters as environment variables for convenience
export AX_DEVIL_TARGET_ADDR=192.168.1.10
export AX_DEVIL_TARGET_USER=admin
export AX_DEVIL_TARGET_PASS=secret
```

<details open>
<summary><a name="device-operations"></a><b>📱 Device Operations</b></summary>
<p>

```bash
# Get device information
ax-devil-device-api device info

# Check device health
ax-devil-device-api device health

# Restart device (with confirmation)
ax-devil-device-api device restart

# Force restart without confirmation
ax-devil-device-api device restart --force
```
</p>
</details>

<details>
<summary><a name="device-debugging"></a><b>🔧 Device Debugging</b></summary>
<p>

```bash
# Download server report
ax-devil-device-api debug download-server-report report.tar.gz

# Download crash report
ax-devil-device-api debug download-crash-report crash.tar.gz

# Run ping test
ax-devil-device-api debug ping-test google.com
```
</p>
</details>

<details>
<summary><a name="media-operations"></a><b>📷 Media Operations</b></summary>
<p>

```bash
# Capture snapshot
ax-devil-device-api media snapshot --output image.jpg

# With custom resolution
ax-devil-device-api media snapshot --resolution 1920x1080 --output snapshot.jpg
```
</p>
</details>

<details>
<summary><a name="ssh-management"></a><b>🔐 SSH Management</b></summary>
<p>

```bash
# List SSH users
ax-devil-device-api ssh list

# Add SSH user
ax-devil-device-api ssh add new-user password123 --comment "John Doe"

# Remove SSH user
ax-devil-device-api-ssh --device-ip 192.168.1.10 --device-username admin --device-password secret remove user123
```
</p>
</details>

<details>
<summary><a name="mqtt-client-cli"></a><b>📡 MQTT Client</b></summary>
<p>

```bash
# Activate MQTT client
ax-devil-device-api-mqtt-client --device-ip 192.168.1.10 --device-username admin --device-password secret activate

# Deactivate MQTT client
ax-devil-device-api-mqtt-client --device-ip 192.168.1.10 --device-username admin --device-password secret deactivate
```
</p>
</details>

<details>
<summary><a name="analytics-mqtt-cli"></a><b>📊 Analytics MQTT</b></summary>
<p>

```bash
# List available analytics data sources
ax-devil-device-api-analytics-mqtt --device-ip 192.168.1.10 --device-username admin --device-password secret sources

# List configured publishers
ax-devil-device-api-analytics-mqtt --device-ip 192.168.1.10 --device-username admin --device-password secret list
```
</p>
</details>

<details>
<summary><a name="api-discovery-cli"></a><b>🔎 API Discovery</b></summary>
<p>

```bash
# List available APIs
ax-devil-device-api-discovery --device-ip 192.168.1.10 --device-username admin --device-password secret list

# Get API info
ax-devil-device-api-discovery --device-ip 192.168.1.10 --device-username admin --device-password secret info vapix
```
</p>
</details>

<details>
<summary><a name="geocoordinates"></a><b>🌍 Geocoordinates</b></summary>
<p>

```bash
# Get current location coordinates
ax-devil-device-api geocoordinates location get

# Set location coordinates (latitude, longitude)
ax-devil-device-api geocoordinates location set 59.3293 18.0686

# Apply pending location changes
ax-devil-device-api geocoordinates location apply

# Get device orientation
ax-devil-device-api geocoordinates orientation get

# Set device orientation (pan, tilt, roll)
ax-devil-device-api geocoordinates orientation set 45 30 0
```
</p>
</details>

<details>
<summary><a name="feature-flags"></a><b>🚩 Feature Flags</b></summary>
<p>

```bash
# List all feature flags
ax-devil-device-api features list

# Get specific feature flag values
ax-devil-device-api features get flag1 flag2

# Set feature flags
ax-devil-device-api features set flag1=true flag2=false
```
</p>
</details>

<details>
<summary><a name="network-operations"></a><b>🌐 Network Operations</b></summary>
<p>

```bash
# Get network interface information
ax-devil-device-api network info

# Get info for specific interface
ax-devil-device-api network info --interface eth0
```
</p>
</details>

> **Note:** All CLI commands support the `--help` flag to see available options and parameters.
>
> **Breaking Change in v1.0:** The old individual commands (e.g., `ax-devil-device-api-device-info`) have been removed. Please use the new unified CLI structure shown above.

---

## ⚠️ Disclaimer

This project is an independent, community-driven implementation and is **not** affiliated with or endorsed by Axis Communications AB. For official APIs and development resources, please refer to [Axis Developer Community](https://www.axis.com/en-us/developer).

## 📄 License

MIT License - See LICENSE file for details.
