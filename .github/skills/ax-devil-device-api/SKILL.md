---
name: ax-devil-device-api
description: 'Use the ax-devil-device-api Python package (1.0 rewrite, httpx and pydantic) to talk to Axis cameras over VAPIX. Use when asked to write or review Python code with Device or AsyncDevice, configure the MQTT client or analytics MQTT publishers, read or update param.cgi parameters, check what an Axis device supports (identity, capabilities, API versions), handle device errors, retry or time out calls, or unit-test camera code with MockCamera. There is no CLI yet.'
---

# ax-devil-device-api

Python client for Axis devices (VAPIX). Sync (`Device`) and async (`AsyncDevice`) share one code base.

**Package**: `ax-devil-device-api`. Python 3.11+. Runtime dependencies: `httpx`, `pydantic`.
**CLI**: none yet (planned). Do not suggest `ax-devil-device-api <command>`; write Python instead.
**Status**: the runtime and three APIs exist: `mqtt_client`, `analytics_mqtt`, `parameter_management`. Other VAPIX APIs, WebSocket event sessions and the CLI are planned. For anything else, say it is not covered yet rather than inventing a method; `dev.invoke(...)` only runs operations that exist as descriptors.

## Before writing code that talks to a device

Get concrete values for host, username and password. Check the environment the examples use (`CAM_USER`, `CAM_PASS`), and ask the user for what is missing. Do not guess IP addresses or credentials.

HTTPS is the default. A plain-HTTP device needs `Device(host, scheme="http", allow_http=True, ...)`; only do that when the user says the device is on a trusted bench network. A device with a private CA needs `verify="/path/ca.pem"`.

## References

- [Python API reference](./references/python-api.md): construction, calling APIs, request objects, errors, retries, capabilities, testing.

In the repository: `docs/design.md` (architecture and decisions), `examples/README.md` (nine scenarios; says which run today), `src/ax_devil_device_api/apis/` (the available APIs).

## Quick start

```python
from ax_devil_device_api import Device

with Device("192.0.2.10", credentials=("root", "pass")) as dev:
    print(dev.identity().model, dev.identity().firmware_version)
    status = dev.apis.mqtt_client.get_client_status()
    print(status.status.state, status.status.connection_status)
```

Async is the same with `AsyncDevice`, `async with`, and `await` on every call (`await dev.apis.mqtt_client.get_client_status()`).

## Key concepts

- **One long-lived device per camera.** Creating a `Device` does no I/O. It owns the connection pool, the verified credential and cached device facts. Do not create one per call. Fleets are plain application code with one device per camera (`examples/01_fleet_mqtt_rollout.py`).
- **`dev.apis.<name>`** gives an API object: `mqtt_client`, `analytics_mqtt`, `parameter_management`. Methods take keyword arguments or one typed request object, and always accept `request_options=`.
- **Models** are pydantic classes. Unset fields are not sent; unknown fields in device responses are ignored; typos in your own arguments raise `pydantic.ValidationError` before anything is sent.
- **Writes can replace whole configurations.** Read the docstring: `configure_client` replaces the entire MQTT configuration. Use `ConfigureClientRequest.from_current(...)` to edit and write back safely (it never writes the masked password back).
- **Errors** all derive from `ax_devil_device_api.errors.DeviceError`. Catch `AccessDenied` / `Unavailable` for the common categories.
- **No automatic support checks.** Call `dev.supports(ApiClass)` yourself; a call to an API the device lacks raises `NotSupported` from version negotiation or an `HttpError`/`ApiError`.

## Quick decision guide

| Task | Use |
|---|---|
| Model, serial number, firmware; health check | `dev.identity()` / `dev.identity(refresh=True)` |
| Does this camera offer an API? | `dev.supports(MqttClientApi)` returns a `SupportResult` (truthy only for YES) |
| What does the camera advertise? | `dev.capabilities()` |
| MQTT client config, status, activate | `dev.apis.mqtt_client` |
| Publish analytics data over MQTT | `dev.apis.analytics_mqtt` |
| Read or change `param.cgi` parameters | `dev.apis.parameter_management` |
| Per-call timeout or retry policy | `request_options=RequestOptions(timeout=..., retry=...)` |
| Forget cached facts after a reboot or firmware upgrade | `dev.refresh()` |
| Test your own code without a camera | `ax_devil_device_api.testing.MockCamera` |
| Run an operation by descriptor | `dev.invoke(mqtt_client.OPS.get_client_status)` |

## Examples

`examples/` has runnable scenarios: `01` fleet MQTT rollout (async), `02` parameter drift, `06` debugging and lab setups, `07` long-running service, `08` clone configuration, `09` testing with `MockCamera`. Examples `03`, `04` and `05` use APIs that are not generated yet and do not run.
