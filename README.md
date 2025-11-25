# ax-devil-device-api

<div align="center">

Python package and CLI for configuring Axis devices via their HTTPS APIs: device info and health, snapshots, network details, MQTT clients, analytics publishers, API discovery, SSH users and more.

See also [ax-devil-mqtt](https://github.com/rasmusrynell/ax-devil-mqtt) and [ax-devil-rtsp](https://github.com/rasmusrynell/ax-devil-rtsp) for related tools.

</div>

---

## Install

```bash
pip install ax-devil-device-api
```

## Configure (optional)

Set environment variables to avoid repeating credentials and broker details:

- `AX_DEVIL_TARGET_ADDR` – Device IP or hostname
- `AX_DEVIL_TARGET_USER` – Device username
- `AX_DEVIL_TARGET_PASS` – Device password
- `AX_DEVIL_MQTT_BROKER_ADDR` – MQTT broker address
- `AX_DEVIL_MQTT_BROKER_PASS` – MQTT broker password
- `AX_DEVIL_USAGE_CLI` – Set to `unsafe` to allow `--no-verify-ssl` without prompts (defaults to `safe`)

---

## Capabilities

- Device info & health – model/firmware, health, restart; CLI `device`; Python `client.device`
- Network – interface details; CLI `network info`; Python `client.network`
- Media – snapshots with resolution/compression; CLI `media snapshot`; Python `client.media`
- MQTT client – configure/activate/deactivate/status/config; CLI `mqtt`; Python `client.mqtt_client`
- Analytics MQTT publishers – list/create/remove; CLI `analytics`; Python `client.analytics_mqtt`
- Analytics metadata producers – list/enable/disable/sample/versions; CLI `analytics-metadata`; Python `client.analytics_metadata`
- API discovery – list APIs, inspect docs/models/openapi; CLI `discovery`; Python `client.discovery`
- Feature flags – list/get/set; CLI `features`; Python `client.feature_flags`
- Geocoordinates – location/orientation get/set/apply; CLI `geocoordinates`; Python `client.geocoordinates`
- SSH users – add/list/show/modify/remove; CLI `ssh`; Python `client.ssh`
- Debug – server/crash reports, network traces, pings, port checks, core dumps; CLI `debug`; Python `client.device_debug`

---

## CLI

`ax-devil-device-api --help` lists all subcommands. Global options: `--device-ip/-a`, `--device-username/-u`, `--device-password/-p`, `--protocol [http|https]`, `--port`, and `--no-verify-ssl`.

Common flows:

- Device checks and restart:

```bash
ax-devil-device-api device info \
  --device-ip <device-ip> \
  --device-username <username> \
  --device-password <password>

ax-devil-device-api device health
ax-devil-device-api device restart --force
```

- Capture a snapshot:

```bash
ax-devil-device-api media snapshot \
  --device-ip <device-ip> \
  --device-username <username> \
  --device-password <password> \
  --resolution 1920x1080 \
  --output snapshot.jpg
```

- Configure and inspect the device MQTT client:

```bash
ax-devil-device-api mqtt configure \
  --device-ip <device-ip> \
  --device-username <username> \
  --device-password <password> \
  --broker-address <broker-ip> \
  --broker-port 1883 \
  --use-tls

ax-devil-device-api mqtt status
ax-devil-device-api mqtt config
```

- Network and geocoordinates:

```bash
ax-devil-device-api network info

ax-devil-device-api geocoordinates location set 59.3293 18.0686
ax-devil-device-api geocoordinates orientation set --heading 45 --tilt 5
ax-devil-device-api geocoordinates orientation apply
```

- Manage analytics publishers:

```bash
ax-devil-device-api analytics sources
ax-devil-device-api analytics create pub-1 "com.axis.analytics_scene_description.v0.beta#1" "axis/events" --qos 1 --retain
ax-devil-device-api analytics list
ax-devil-device-api analytics remove pub-1
```

- Manage analytics metadata producers:

```bash
ax-devil-device-api analytics-metadata list
ax-devil-device-api analytics-metadata enable metadata-producer --channel 1 --channel 2
ax-devil-device-api analytics-metadata sample metadata-producer --format json
```

- Feature flags:

```bash
ax-devil-device-api features list
ax-devil-device-api features get my_flag other_flag
ax-devil-device-api features set my_flag=true other_flag=false --force
```

- Inspect APIs exposed by the device:

```bash
ax-devil-device-api discovery list
ax-devil-device-api discovery info analytics-mqtt --docs-html-link
```

- Manage SSH users or collect diagnostics:

```bash
ax-devil-device-api ssh add new-user password123 --comment "Service account"
ax-devil-device-api ssh list
ax-devil-device-api ssh modify new-user --password new-pass
ax-devil-device-api debug download-server-report report.tar.gz
ax-devil-device-api debug download-crash-report crash.tar.gz
ax-devil-device-api debug ping-test example.com
```

---

## Python API

```python
import json
from ax_devil_device_api import Client, DeviceConfig

config = DeviceConfig.https(
    host="192.168.1.81",
    username="root",
    password="pass",
    verify_ssl=False,  # leave True in production
)

with Client(config) as client:
    info = client.device.get_info()
    print(json.dumps(info, indent=2))

    snapshot = client.media.get_snapshot(resolution="1280x720")
    mqtt_state = client.mqtt_client.get_state()
```

---

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

---

## Disclaimer

This project is an independent, community-driven implementation and is **not** affiliated with or endorsed by Axis Communications AB. For official APIs and development resources, see the [Axis Developer Community](https://www.axis.com/en-us/developer).

## License

MIT License - see [LICENSE](LICENSE) for details.
