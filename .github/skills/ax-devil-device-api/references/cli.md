# ax-devil-device-api CLI Reference

Entry point: `ax-devil-device-api`

**Install** (if `which ax-devil-device-api` returns nothing):
```bash
uv tool install ax-devil-device-api
```

**Full help for any command:**
```bash
ax-devil-device-api --help
ax-devil-device-api <command> --help
ax-devil-device-api <command> <subcommand> --help
```

## Environment Variables

The CLI reads these when the corresponding flag is not supplied:

| Variable | CLI flag fallback |
|----------|-------------------|
| `AX_DEVIL_TARGET_ADDR` | `--device-ip` / `-a` |
| `AX_DEVIL_TARGET_USER` | `--device-username` / `-u` |
| `AX_DEVIL_TARGET_PASS` | `--device-password` / `-p` |
| `AX_DEVIL_MQTT_BROKER_ADDR` | `mqtt configure --broker-address` / `-b` |
| `AX_DEVIL_MQTT_BROKER_PASS` | `mqtt configure --broker-password` / `-W` |

## Global Options

| Flag | Short | Env var | Description |
|------|-------|---------|-------------|
| `--device-ip` | `-a` | `AX_DEVIL_TARGET_ADDR` | Device IP or hostname |
| `--device-username` | `-u` | `AX_DEVIL_TARGET_USER` | Device username |
| `--device-password` | `-p` | `AX_DEVIL_TARGET_PASS` | Device password |
| `--protocol` | — | — | `http` or `https` (default: `https`) |
| `--port` | — | — | Override default port |
| `--no-verify-ssl` | — | — | Skip SSL verification |
| `--debug` | — | — | Show outgoing request details |

## Commands Overview

### `device` — Device info, health, restart

```bash
ax-devil-device-api device info              # Model, firmware, serial number
ax-devil-device-api device info-detailed     # Extended parameters
ax-devil-device-api device info-no-auth      # Basic info without credentials (basicdeviceinfo.cgi)
ax-devil-device-api device info-auth         # Auth-required info (basicdeviceinfo.cgi)
ax-devil-device-api device health            # Is the device responsive?
ax-devil-device-api device restart --force   # Restart (prompts unless --force)
```

### `media` — Snapshots

```bash
ax-devil-device-api media snapshot -o snapshot.jpg
ax-devil-device-api media snapshot --resolution 1920x1080 --compression 50 --device 1
```

### `network` — Network info

```bash
ax-devil-device-api network info                         # Default interface (eth0)
ax-devil-device-api network info --interface eth1         # Specific interface
```

### `mqtt` — Device MQTT client configuration

Configures the MQTT client **on the device** (broker address, credentials, activate/deactivate).

```bash
ax-devil-device-api mqtt status              # Current MQTT state
ax-devil-device-api mqtt config              # Current MQTT config
ax-devil-device-api mqtt configure --broker-address <ip> --broker-port 1883
ax-devil-device-api mqtt configure -b <ip> -P 1883 -U <user> -W <pass> --keep-alive 60 --use-tls
ax-devil-device-api mqtt activate
ax-devil-device-api mqtt deactivate
```

`configure` options: `--broker-address`/`-b` (required, env `AX_DEVIL_MQTT_BROKER_ADDR`), `--broker-port`/`-P` (default 1883), `--broker-username`/`-U`, `--broker-password`/`-W` (env `AX_DEVIL_MQTT_BROKER_PASS`), `--keep-alive` (default 60), `--use-tls`.

### `analytics` — Analytics MQTT publishers

Manages analytics data publishers on the device. Use `sources` to discover what the device can publish.

```bash
ax-devil-device-api analytics sources        # List available data sources
ax-devil-device-api analytics list           # List existing publishers
ax-devil-device-api analytics create <id> <source> <topic> [--qos 0] [--retain] [--use-topic-prefix] [--force]
ax-devil-device-api analytics remove <id> [--force]
```

### `analytics-metadata` — Metadata producer configuration

Enable/disable analytics metadata producers on specific channels.

```bash
ax-devil-device-api analytics-metadata list [--format table|json]
ax-devil-device-api analytics-metadata versions [--format table|json]
ax-devil-device-api analytics-metadata enable <producer> --channel 1 --channel 2
ax-devil-device-api analytics-metadata disable <producer> --channel 1
ax-devil-device-api analytics-metadata sample <producer1> [<producer2> ...] --format xml|json [-o output.xml]
```

`sample` format default is `xml`.

### `features` — Feature flags

```bash
ax-devil-device-api features list                         # All flags with values
ax-devil-device-api features get <flag1> <flag2>          # Specific flags
ax-devil-device-api features set <flag>=true --force      # Set flag values
```

### `geocoordinates` — Location and orientation

```bash
ax-devil-device-api geocoordinates location get
ax-devil-device-api geocoordinates location set <lat> <lon>
ax-devil-device-api geocoordinates location apply
ax-devil-device-api geocoordinates orientation get
ax-devil-device-api geocoordinates orientation set --heading 45 --tilt 5 --roll 0 --height 3.0
ax-devil-device-api geocoordinates orientation apply
```

`orientation set` requires at least one of: `--heading`, `--tilt`, `--roll`, `--height`.

### `discovery` — API discovery

List and inspect APIs available on the device.

```bash
ax-devil-device-api discovery list
ax-devil-device-api discovery info <api-name> [--version <v>]
ax-devil-device-api discovery versions <api-name>
```

`discovery info` supports flags to access specific resources: `--docs-md`, `--docs-html`, `--model`, `--rest-api`, `--rest-openapi`, `--rest-ui`. Each has `-raw` (print content) and `-link` (print URL) variants.

### `ssh` — SSH user management

```bash
ax-devil-device-api ssh list
ax-devil-device-api ssh add <user> <password> --comment "Service account"
ax-devil-device-api ssh show <user>
ax-devil-device-api ssh modify <user> --password <new-pass> --comment <new-comment>
ax-devil-device-api ssh remove <user>
```

### `data-transformation` — jq-based data transforms

Create transforms that apply jq expressions to analytics data topics.

```bash
ax-devil-device-api data-transformation topics           # Available input topics
ax-devil-device-api data-transformation list             # Current transforms
ax-devil-device-api data-transformation create <input-topic> <output-topic> '<jq-expr>'
ax-devil-device-api data-transformation remove <output-topic> [--force]
```

### `systemready` — Device readiness (no auth required)

```bash
ax-devil-device-api systemready check                    # No credentials needed (default timeout: 20s)
ax-devil-device-api systemready check -t 30              # Custom timeout
ax-devil-device-api systemready versions
```

### `debug` — Diagnostics and reports

```bash
ax-devil-device-api debug download-server-report report.tar.gz
ax-devil-device-api debug download-crash-report crash.tar.gz
ax-devil-device-api debug download-network-trace trace.pcap --duration 30 [--interface eth0]
ax-devil-device-api debug collect-core-dump coredump.bin
ax-devil-device-api debug ping-test example.com
ax-devil-device-api debug port-open-test <address> <port>
```

## Typical CLI Workflows

### Quick health check

```bash
ax-devil-device-api device health
```

### Take a snapshot from the device

```bash
ax-devil-device-api media snapshot -o /tmp/snap.jpg
```

### Set up analytics MQTT publishing

```bash
# 1. See what analytics the device offers
ax-devil-device-api analytics sources

# 2. Configure MQTT broker on device
ax-devil-device-api mqtt configure --broker-address <broker-ip> --broker-port 1883
ax-devil-device-api mqtt activate

# 3. Create a publisher
ax-devil-device-api analytics create my-pub com.axis.analytics_scene_description.v0.beta#1 my/topic
```

### Enable a metadata producer

```bash
ax-devil-device-api analytics-metadata list
ax-devil-device-api analytics-metadata enable <producer-name> --channel 1
```
