<p align="center">
  <img src="./resources/ax-devil-banner.png" alt="ax-devil banner" width="100%"/>
</p>

# ax-devil-device-api

Typed, synchronous and asynchronous Python client for the VAPIX APIs of Axis devices.

The API modules are generated from a machine-readable spec of the VAPIX documentation. The generation pipeline is still in progress. Today three reference APIs exist (`mqtt_client`, `analytics_mqtt`, `parameter_management`), plus device identity and capability discovery.

See also [ax-devil-mqtt](https://github.com/rasmusrynell/ax-devil-mqtt) and [ax-devil-rtsp](https://github.com/rasmusrynell/ax-devil-rtsp).

> **Status: pre-release rewrite (1.0.0.dev0).** This is a complete rewrite of the 0.x library, with no backwards compatibility: the old `Client`, `DeviceConfig` and CLI are gone. The code has not yet been validated against real cameras. Expect breaking changes.

## Install

Requires Python 3.11+.

```bash
uv add ax-devil-device-api --prerelease=allow
# or
pip install --pre ax-devil-device-api
```

## Quick start

Synchronous:

```python
from ax_devil_device_api import Device

with Device("192.168.0.90", credentials=("root", "pass")) as dev:
    status = dev.apis.mqtt_client.get_client_status()
    print(status.status.state, status.status.connection_status)

    params = dev.apis.parameter_management.list(["Brand.ProdNbr"])
    print(params)  # {"Brand.ProdNbr": "..."}

    print(dev.identity())  # model, serial number, firmware version, ...
```

Asynchronous:

```python
import asyncio
from ax_devil_device_api import AsyncDevice

async def main() -> None:
    async with AsyncDevice("192.168.0.90", credentials=("root", "pass")) as dev:
        status = await dev.apis.mqtt_client.get_client_status()
        print(status.status.state)
        print(await dev.identity())

asyncio.run(main())
```

HTTPS is the default. Plain HTTP must be enabled explicitly (see [Configuration](#configuration)).

## Core concepts

### One long-lived Device per camera

Creating a `Device` does no I/O. It owns the connection pool, the verified credential and cached device facts, and it copes with dropped connections, reboots and firmware changes. Create it once, keep it for the life of your script or service, and close it when done. A sync `Device` may be shared between threads; an `AsyncDevice` between tasks of one event loop. Fleets are plain application code: one `Device` per camera.

### APIs

Every API is an attribute of `dev.apis`; sync and async have the same names.

```python
dev.apis.mqtt_client.get_client_status()
await adev.apis.mqtt_client.get_client_status()
```

### Arguments and per-call options

Pass keyword arguments, or a typed request object. Every method also accepts `request_options`.

```python
from ax_devil_device_api import RequestOptions, RetryPolicy
from ax_devil_device_api.apis.mqtt_client import ConfigureClientRequest, Server

mqtt = dev.apis.mqtt_client
mqtt.configure_client(server=Server(host="broker.example", port=8883, protocol="ssl"), client_id="cam-1")
mqtt.configure_client(ConfigureClientRequest(server=Server(host="broker.example"), client_id="cam-1"))

mqtt.get_client_status(request_options=RequestOptions(timeout=30, retry=RetryPolicy(attempts=3, retry_reads=True)))
```

Invalid arguments are rejected locally, before any request is sent (see example 06).

### Safe read-modify-write

Devices mask secrets such as passwords when you read a configuration, and `configure_client` replaces the whole configuration. `from_current` turns a read result into a write request that drops masked fields and keeps the stored secret.

```python
current = mqtt.get_client_status().config
request = ConfigureClientRequest.from_current(current)
request.keep_alive_interval = 60
mqtt.configure_client(request)
```

### Errors

All errors derive from `DeviceError` (`ax_devil_device_api.errors`):

| Error | Meaning |
|---|---|
| `ConfigurationError` | Invalid host, port, base path, HTTP without opt-in, and similar. Raised locally. |
| `TransportError` | Network failure. `.request_sent` says whether the request may have reached the camera. Subclasses cover timeouts by phase, TLS errors and failed connections. |
| `AuthError` | Wrong credentials, or a 401 with none configured. |
| `HttpError` | Non-success HTTP status (`.status`, `.body_excerpt`). |
| `ApiError` | Documented API error (`.code`, `.kind`, `.description`, `.http_status`). |
| `ResponseFormatError` | The device answered with something unexpected. |
| `NotSupported` | The device does not offer the API or version. |
| `AccessDenied`, `Unavailable` | Categories: catching them covers both the HTTP status (403, 503) and the documented API error codes. |

```python
from ax_devil_device_api.errors import AccessDenied, TransportError, Unavailable

try:
    dev.apis.mqtt_client.activate_client()
except AccessDenied:
    print("this account is not an admin")
except Unavailable:
    print("camera busy, try later")
except TransportError as e:
    print("network problem; request sent:", e.request_sent)
```

### Identity and capabilities

```python
dev.identity()                    # DeviceIdentity: model, serial_number, firmware_version, ... (cached)
dev.identity(refresh=True)        # also works as a health check
dev.capabilities()                # what the device lists in its API discovery endpoints
result = dev.supports(dev.apis.mqtt_client)
print(result.status, result.reason)  # Support.YES, NO or UNKNOWN
```

`NO` is returned only when a discovery probe that would list the API succeeded and did not list it. If the probes failed, the answer is `UNKNOWN`, and failed probes are listed in `capabilities().errors`. Calls do not check support automatically.

### Retries

Requests that were never sent (connect, TLS and pool-timeout failures) are retried for every operation (default 2 attempts, exponential backoff). Read timeouts and dropped connections are retried only with `retry_reads=True` and only for reads. Writes are never resent once they may have arrived, HTTP and API errors are never retried, and streams are never restarted. Set the policy per device with `retry=` or per call with `request_options`; `NO_RETRY` disables retries.

### Configuration

```python
from ax_devil_device_api import BearerToken, Device

dev = Device(
    "cam7",
    credentials=BearerToken(get_token),   # or ("user", "pass") / Credentials(...); token may be a callable
    base_path="/vms/cam7",                # reverse proxy or VMS prefix
    proxy="http://proxy.local:3128",
    verify="/etc/ssl/axis-ca.pem",        # True, False, CA bundle path or ssl.SSLContext
    timeout=10.0,
    max_concurrency=4,                    # requests in flight per device
    max_streams=2,                        # open streams per device, counted separately
)
```

Plain HTTP (for a lab bench) needs `scheme="http", allow_http=True`. Bearer tokens are refused over HTTP. Digest authentication is preferred, and Basic credentials are never sent before the camera challenges.

### Logging and hooks

```python
import logging
logging.getLogger("ax_devil_device_api").setLevel(logging.DEBUG)  # one line per request attempt

Device(
    "cam",
    credentials=("root", "pass"),
    on_request=lambda info: print(info["request"]),   # redacted: secrets become <redacted>
    on_response=lambda info: print(info["api"], info["operation"], info["status"], info["duration_ms"]),
)
```

`on_response` receives one record per attempt: `api`, `operation`, `method`, `path`, `status`, `error`, `duration_ms`, `attempt`.

### Testing your code

`MockCamera` answers the routes you register, records every request, and plugs into `Device` and `AsyncDevice` in place of the network.

```python
from ax_devil_device_api.testing import MockCamera

def test_status() -> None:
    camera = MockCamera()
    camera.jsonrpc(
        "/axis-cgi/mqtt/client.cgi",
        "getClientStatus",
        data={"status": {"state": "active", "connectionStatus": "connected"}},
    )
    with camera.device() as dev:
        assert dev.apis.mqtt_client.get_client_status().status.state == "active"
    assert len(camera.calls("getClientStatus")) == 1
```

It also offers `identity()`, `api_list()`, `dca_apis()`, `rest()`, `cgi()`, `fail()` and `async_device()`.

## Examples

Scenario-driven scripts in [`examples/`](examples/README.md). All read credentials from `CAM_USER` and `CAM_PASS`. "Target" examples use APIs the generator will produce; they do not run yet.

| File | Scenario | Status |
|---|---|---|
| `01_fleet_mqtt_rollout.py` | Configure MQTT and analytics publishing on 50 cameras concurrently | runs today |
| `02_parameter_drift.py` | Compare `param.cgi` values to a baseline and fix drift | runs today |
| `03_version_aware_thermal.py` | Thermal isotherms on a mixed-firmware fleet | target |
| `04_stream_server_report.py` | Download large server reports to disk | target |
| `05_event_watch.py` | Watch I/O and PTZ events over WebSocket on several cameras | target |
| `06_debugging_and_lab_setups.py` | Bench camera over HTTP with request logging and error inspection | runs today |
| `07_long_running_service.py` | Monitor cameras for weeks with one `AsyncDevice` each | runs today |
| `08_clone_configuration.py` | Copy MQTT and publishers from a reference camera | runs today |
| `09_testing_your_code.py` | Unit-test your own code with `MockCamera` | runs today |

## Design

See [docs/design.md](docs/design.md) for the architecture, spec format, error model, and the decisions log.

## Development

```bash
uv sync
uv run pytest
uv run pyright
uv build
```

## License

MIT. See [LICENSE](LICENSE).
