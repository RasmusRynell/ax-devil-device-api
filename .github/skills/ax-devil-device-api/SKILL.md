---
name: ax-devil-device-api
description: 'Use the ax-devil-device-api package (CLI and Python API) to interact with Axis cameras over HTTPS. Use when asked to "get device info", "take snapshot", "restart device", "configure MQTT", "manage SSH users", "list analytics sources", "create publisher", "set feature flags", "check device health", "discover APIs", "set geocoordinates", "data transformation", "systemready", or write Python code using Client/DeviceConfig to control an Axis device.'
---

# ax-devil-device-api

Python package and CLI for configuring Axis devices via their HTTPS APIs.

**Package**: `ax-devil-device-api` (PyPI)
**Depends on**: `requests`, `click`, `rich`

## Prerequisites — MUST do before any command

1. **Ensure the CLI is installed.** Run `which ax-devil-device-api`. If not found, install it:
   ```bash
   uv tool install ax-devil-device-api
   ```
2. **Resolve credentials.** Before running any command or writing code that talks to a device, you MUST have concrete values for the required parameters. Follow this procedure:
   - Check env vars: `echo $AX_DEVIL_TARGET_ADDR $AX_DEVIL_TARGET_USER $AX_DEVIL_TARGET_PASS`
   - If any required value is missing or empty, **ASK the user** — do NOT guess or use placeholder IPs.
   - The only exception is `systemready check` which needs only the device IP (no auth).

## References

Load only the reference you need:

- **[CLI Reference](./references/cli.md)** — All subcommands grouped by feature area, with examples
- **[Python API Reference](./references/python-api.md)** — `Client`, `DeviceConfig`, feature clients, and Python workflows

## Environment Variables

The CLI reads these when the corresponding flag is not supplied:

| Variable | CLI flag fallback |
|----------|-------------------|
| `AX_DEVIL_TARGET_ADDR` | `--device-ip` / `-a` |
| `AX_DEVIL_TARGET_USER` | `--device-username` / `-u` |
| `AX_DEVIL_TARGET_PASS` | `--device-password` / `-p` |
| `AX_DEVIL_MQTT_BROKER_ADDR` | `--broker-address` / `-b` (mqtt configure) |
| `AX_DEVIL_MQTT_BROKER_PASS` | `--broker-password` / `-W` (mqtt configure) |

## Quick Decision Guide

| Task | CLI command | Python property |
|------|-------------|-----------------|
| Get device info / health / restart | `device` | `client.device` |
| Take a snapshot | `media snapshot` | `client.media` |
| Network info | `network info` | `client.network` |
| Configure/activate MQTT on device | `mqtt` | `client.mqtt_client` |
| List analytics sources / publishers | `analytics` | `client.analytics_mqtt` |
| Manage metadata producers | `analytics-metadata` | `client.analytics_metadata` |
| Get/set feature flags | `features` | `client.feature_flags` |
| Manage SSH users | `ssh` | `client.ssh` |
| Set geocoordinates / orientation | `geocoordinates` | `client.geocoordinates` |
| Discover device APIs | `discovery` | `client.discovery` |
| Data transforms (jq expressions) | `data-transformation` | `client.data_transformation` |
| Check device readiness (no auth) | `systemready check` | `client.systemready` |
| Debug: reports, traces, ping | `debug` | `client.device_debug` |

**Tip**: Run `ax-devil-device-api <command> --help` for full details on any command.

## Key Concepts

- **DeviceConfig**: Connection config. Use `DeviceConfig.https(...)` (default) or `DeviceConfig.http(...)` (insecure, explicit opt-in). SSL verification is not yet implemented — always `verify_ssl=False`.
- **Client**: Main entry point. Lazy-loads feature clients via properties. Use as context manager for proper cleanup.
- **CLI global options**: `-a/--device-ip`, `-u/--device-username`, `-p/--device-password`, `--protocol`, `--port`, `--no-verify-ssl`, `--debug`.
