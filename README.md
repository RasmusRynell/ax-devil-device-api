<p align="center">
  <img src="./resources/ax-devil-banner.png" alt="ax-devil banner" width="100%"/>
</p>

# ax-devil-device-api

Typed, synchronous and asynchronous Python client for the VAPIX APIs of Axis devices, with a command line.

The API modules (208 of them, about 1,900 operations) are generated from YAML specs of the VAPIX documentation, so the client covers JSON-RPC, Device Configuration, classic CGI, JSON service, SOAP and plain REST APIs, streams, uploads, WebSocket sessions and RTSP URLs in one consistent style.

See also [ax-devil-mqtt](https://github.com/rasmusrynell/ax-devil-mqtt) and [ax-devil-rtsp](https://github.com/rasmusrynell/ax-devil-rtsp).

> **Status: pre-release rewrite (1.0.0.dev0).** This is a complete rewrite of the 0.x library, with no backwards compatibility: the old `Client`, `DeviceConfig` and CLI are gone. The generated APIs follow the VAPIX documentation and have not yet been validated against real devices (every operation is marked `docs-only`). Expect breaking changes.

## Install

Requires Python 3.11+.

```bash
uv add ax-devil-device-api --prerelease=allow
# or
pip install --pre ax-devil-device-api
```

This also installs the `ax-devil` command. SOCKS proxies (`socks5://...`) need the optional extra: `pip install 'ax-devil-device-api[socks]'`.

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

## Generated APIs

Every API is an attribute of `dev.apis`; sync and async have the same names. The module, class and method names come from the spec (`mqtt-client` becomes `dev.apis.mqtt_client` with `MqttClientApi` / `AsyncMqttClientApi`). Find what exists with the command line or in code:

```bash
ax-devil apis              # all generated APIs with family and operation count
ax-devil ops mqtt_client   # operations, access level, effect and parameters of one API
```

[docs/api_surface.txt](docs/api_surface.txt) lists every public name and signature. Method docstrings state the access level, whether a write replaces the whole configuration and which API version added a field.

### Arguments and per-call options

Pass keyword arguments, or a typed request object. Every method that sends a request also accepts `request_options`.

```python
from ax_devil_device_api import RequestOptions, RetryPolicy
from ax_devil_device_api.apis.mqtt_client import ConfigureClientRequest, Server

mqtt = dev.apis.mqtt_client
mqtt.configure_client(server=Server(host="broker.example", port=8883, protocol="ssl"), client_id="cam-1")
mqtt.configure_client(ConfigureClientRequest(server=Server(host="broker.example"), client_id="cam-1"))

mqtt.get_client_status(request_options=RequestOptions(timeout=30, retry=RetryPolicy(attempts=3, retry_reads=True)))
```

Invalid arguments are rejected locally, before any request is sent. Any operation can also be run by descriptor: `dev.invoke(mqtt_client.OPS.get_client_status)`.

### Safe read-modify-write

Devices mask secrets such as passwords when you read a configuration, and `configure_client` replaces the whole configuration. `from_current` turns a read result into a write request that drops masked fields and keeps the stored secret.

```python
current = mqtt.get_client_status().config
request = ConfigureClientRequest.from_current(current)
request.keep_alive_interval = 60
mqtt.configure_client(request)
```

### Streams

Operations that return a long body return a stream manager (`StreamResult`, or `AsyncStreamResult` on `AsyncDevice`). Use it as a context manager; leaving the block closes the connection. Streams count against `max_streams`, not `max_concurrency`.

```python
with dev.apis.media_stream.get_media_stream(container="mp4") as stream:
    for chunk in stream:           # bytes; MJPEG streams yield Part objects, line streams yield str
        out.write(chunk)
```

### Uploads

Upload arguments take `bytes`, a `pathlib.Path` or `Upload(stream, size)`. Content up to 8 MiB is buffered and can be replayed after an authentication challenge; larger content is streamed after an authenticated `GET /axis-cgi/usergroup.cgi` has verified the credentials.

```python
from pathlib import Path
dev.apis.application_api.upload_application(Path("my_app.eap"))
```

### WebSocket sessions

Event streaming, Device Data Hub and the audio and intercom WebSockets are sessions. A ping-based heartbeat (`Heartbeat`, every 20 s by default) detects dead connections. Events are not replayed: after a reconnect `session.gap` says how long the stream was down. Reconnecting is up to the application (see `examples/05_event_watch.py`).

```python
from ax_devil_device_api import EventFilter

filters = [EventFilter(topic_filter="tns1:Device/tnsaxis:IO/Port")]
with dev.apis.event_streaming_ws.connect(filters) as session:
    for event in session.notifications():
        print(event.topic, event.data)
```

### RTSP URLs

The library builds RTSP URLs and does not speak RTSP: pass the URL to a media library. RTSP session commands (`OPTIONS`, `DESCRIBE`, `SETUP`, `GET_PARAMETER`, `SET_PARAMETER`) and RTSP-over-HTTP are out of scope.

```python
from ax_devil_device_api import MediaStream

url = dev.rtsp_url(MediaStream(videocodec="h264", resolution="1280x720"), include_credentials=True)
print(url.safe)      # rtsp://camera:554/axis-media/media.amp?videocodec=h264&resolution=1280x720
print(str(url))      # same, with user name and password; repr(url) never shows the password
```

### Errors

All errors derive from `DeviceError` (`ax_devil_device_api.errors`):

| Error | Meaning |
|---|---|
| `ConfigurationError` | Invalid host, port, base path, HTTP without opt-in, and similar. Raised locally. |
| `TransportError` | Network failure. `.request_sent` says whether the request may have reached the camera. Subclasses cover timeouts by phase, TLS errors and failed connections. |
| `SessionClosed` | A WebSocket session ended normally (`receive()` and `request()` only). |
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

## Device behaviour

### One long-lived Device per camera

Creating a `Device` does no I/O. It owns the connection pool, the verified credential and cached device facts, and it copes with dropped connections, reboots and firmware changes. Create it once, keep it for the life of your script or service, and close it when done. A sync `Device` may be shared between threads; an `AsyncDevice` between tasks of one event loop. Fleets are plain application code: one `Device` per camera.

### Identity and capabilities

```python
dev.identity()                    # DeviceIdentity: model, serial_number, firmware_version, ... (cached)
dev.identity(refresh=True)        # also works as a health check
dev.capabilities()                # what the device lists in its discovery endpoints
result = dev.supports(dev.apis.mqtt_client)
print(result.status, result.reason)  # Support.YES, NO or UNKNOWN
```

Support is decided from API discovery, Device Configuration discovery, `param.cgi` properties, installed ACAP applications and the web services listed by the Entry service. `NO` is returned only when every probe that would list the API succeeded and none did. If a probe failed, the answer is `UNKNOWN`, and failed probes are listed in `capabilities().errors`. Calls do not check support automatically.

### Retries

Requests that were never sent (connect, TLS and pool-timeout failures) are retried for every operation (default 2 attempts, exponential backoff). Read timeouts and dropped connections are retried only with `retry_reads=True` and only for reads. Writes are never resent once they may have arrived, HTTP and API errors are never retried, and streams and sessions are never restarted. Set the policy per device with `retry=` or per call with `request_options`; `NO_RETRY` disables retries.

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
    max_streams=2,                        # open streams and sessions per device, counted separately
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

## Features

`ax_devil_device_api.features` holds hand-written conveniences built only on the generated APIs. Each has an async twin with an `async_` prefix.

```python
from ax_devil_device_api.features import api_support, device_summary, snapshot, supported_apis

jpeg = snapshot(dev, resolution="640x480")      # bytes
summary = device_summary(dev)                   # identity plus discovery results
names = supported_apis(dev)                     # generated APIs the device positively offers
support = api_support(dev)                      # SupportResult for every generated API
```

## Command line

```bash
ax-devil --help
ax-devil apis                                  # list generated APIs (no device needed)
ax-devil ops mqtt_client                       # operations and parameters of one API (no device needed)

export AX_DEVIL_HOST=192.168.0.90 AX_DEVIL_USER=root AX_DEVIL_PASSWORD=pass
ax-devil summary                               # identity and discovery summary
ax-devil supported                             # {"apis": status of every generated API, "errors": failed probes}; exit 1 if the device cannot be reached
ax-devil call mqtt_client get_client_status
ax-devil call parameter_management list group='["Brand.ProdNbr"]'
ax-devil call media_stream get_media_stream container=mp4 --limit 100 -o clip.mp4
ax-devil call application_api upload_application package=@app.eap   # a file for an upload parameter
ax-devil snapshot --resolution 640x480 -o snapshot.jpg
```

Connection options: `--host`, `--user`, `--password`, `--port`, `--http`, `--insecure`, `--ca-bundle`, `--base-path`, `--timeout`. Host, user and password default to `$AX_DEVIL_HOST`, `$AX_DEVIL_USER` (or `$CAM_USER`) and `$AX_DEVIL_PASSWORD` (or `$CAM_PASS`); prefer the environment to `--password`, which shows up in process lists. Output is JSON on stdout (`call --output FILE` writes JSON results, line streams, RTSP URLs and binary results to a file; `-` is stdout). Errors are JSON on stderr with exit code 1 (device or OS error) or 2 (usage or invalid parameters). `call` parses `key=value` values as JSON and falls back to strings; use `--json '{...}'` or `--json @file` for larger parameter sets. For a parameter typed as an upload source (`ax-devil ops <api>` marks it `"upload": true`), `key=@path` sends that file, with its size and name; any other parameter never interprets a leading `@` (a string keeps it as text, a number or list with one is a usage error). `call` runs any operation of any generated API, so new specs are available on the command line as soon as they are generated.

## Protocol families

| Family | Used for |
|---|---|
| JSON-RPC (`jsonrpc`) | `/axis-cgi/<api>.cgi` APIs with `apiVersion` negotiation |
| Device Configuration (`dca`) | `/config/rest/<api>/<version>` |
| Classic CGI (`cgi`) | query/form/multipart/raw-body CGIs, text, key=value, XML, binary and streamed replies, `param.cgi` |
| VAPIX JSON service (`service_json`) | `POST /vapix/<service>` |
| SOAP (`soap`) | SOAP 1.2 services without a JSON form (the JSON service is preferred when both exist) |
| Plain REST (`rest`) | Audio Manager Edge and Pro |
| WebSocket sessions | event streaming, Device Data Hub, audio and intercom WebSockets |
| Streams | MJPEG, media containers, audio, line-based monitors |
| RTSP URLs | URL building only |

Not supported: RTSP session commands and RTSP-over-HTTP, the Google JSON WebSocket codec, STOMP, binary audio formats and multipart audio decoding. Operations that need them are recorded as `BLOCKED` notes in the spec and are not generated.

## Specs and code generation

One YAML file per API and major version in `specs/apis/<section>/`, validated by `specs/schema.json`, describes models, operations, bindings, errors, version gates and examples. `codegen/` turns them into `src/ax_devil_device_api/apis/*.py` and `docs/api_surface.txt`. Generated files are never edited by hand: fix the spec (or a patch in `specs/patches/`) and regenerate. The contract tests run every example in every spec through the generated code.

```bash
uv run python -m codegen validate    # specs against the schema
uv run python -m codegen generate    # write the generated modules and docs/api_surface.txt
uv run python -m codegen check       # fail if generated files are stale (CI runs this)
```

See [docs/spec-format.md](docs/spec-format.md) for the format and [docs/design.md](docs/design.md) for the architecture, error model and decisions.

## Examples

Scenario-driven scripts in [`examples/`](examples/README.md). All read credentials from `CAM_USER` and `CAM_PASS`, and each is run against a fake camera by `tests/examples/`.

| File | Scenario |
|---|---|
| `01_fleet_mqtt_rollout.py` | Configure MQTT and analytics publishing on 50 cameras concurrently |
| `02_parameter_drift.py` | Compare `param.cgi` values to a baseline and fix drift |
| `03_version_aware_thermal.py` | Thermal isotherms on a mixed-firmware fleet |
| `04_record_clips.py` | Record video clips from many cameras straight to disk |
| `05_event_watch.py` | Watch I/O and PTZ events over WebSocket on several cameras |
| `06_debugging_and_lab_setups.py` | Bench camera over HTTP with request logging and error inspection |
| `07_long_running_service.py` | Monitor cameras for weeks with one `AsyncDevice` each |
| `08_clone_configuration.py` | Copy MQTT and publishers from a reference camera |
| `09_testing_your_code.py` | Unit-test your own code with `MockCamera` |

## Development

```bash
uv sync --locked
uv run python -m codegen check   # generated modules match the specs
uv run ruff check .              # lint (config in pyproject.toml)
uv run pyright                   # type check src and tests
uv run pytest                    # unit, contract, codegen and example tests
uv build
```

No test touches the network. Live conformance against real devices is not implemented yet.

## License

MIT. See [LICENSE](LICENSE).
