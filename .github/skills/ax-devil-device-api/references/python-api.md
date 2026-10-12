# ax-devil-device-api Python API reference

Everything here exists in `src/ax_devil_device_api/`. Anything not listed is not implemented yet (other VAPIX APIs, WebSocket sessions, CLI).

Public exports from `ax_devil_device_api`: `Device`, `AsyncDevice`, `Credentials`, `BearerToken`, `RequestOptions`, `RetryPolicy`, `NO_RETRY`, `Capabilities`, `DeviceIdentity`, `Support`, `SupportResult`, `MISSING`. Errors live in `ax_devil_device_api.errors`; test helpers in `ax_devil_device_api.testing`; API modules in `ax_devil_device_api.apis.<name>`.

## Device and AsyncDevice

```python
from ax_devil_device_api import AsyncDevice, BearerToken, Device

dev = Device("192.0.2.10", credentials=("root", "pass"))      # no I/O at construction
dev.close()                                                   # or: with Device(...) as dev:

async with AsyncDevice("10.0.0.1", credentials=BearerToken(get_token), base_path="/vms/cam7") as dev: ...
```

Keyword arguments: `credentials` (`Credentials`, a `(user, password)` tuple, or `BearerToken`), `scheme="https"`, `port`, `base_path` (starts with `/`, no trailing `/`), `verify` (`True`, `False`, a CA bundle path, or an `ssl.SSLContext`), `proxy`, `timeout=10.0`, `allow_http=False`, `max_concurrency=4`, `max_streams=2`, `retry` (`RetryPolicy`), `on_request`, `on_response`, `transport` (an httpx transport; used by `MockCamera`). Invalid values raise `ConfigurationError` at construction. `scheme="http"` requires `allow_http=True`; a `BearerToken` is rejected over HTTP. `Device.from_config(ConnectionConfig)` takes a ready config.

Authentication: Digest is preferred and Basic is used only after the device challenges. A `BearerToken` takes a string or a callable that returns the current token (called per request and once more after a 401).

Methods:

| Method | Returns |
|---|---|
| `dev.apis.<name>` | API object (sync or async, matching the device) |
| `dev.api(ApiClass)` | the cached API object for a class, e.g. `dev.api(MqttClientApi)` |
| `dev.invoke(op, request=None, /, *, request_options=None, **kwargs)` | result of any operation descriptor, e.g. `mqtt_client.OPS.get_client_status` |
| `dev.identity(refresh=False)` | `DeviceIdentity` (cached; `refresh=True` re-asks and works as a health check; new firmware drops all cached facts) |
| `dev.capabilities()` | `Capabilities` from three discovery probes; failed probes are reported in `.errors`, not raised |
| `dev.supports(api)` | `SupportResult` for an API class or object |
| `dev.refresh()` | forget all cached device facts (after a reboot or firmware upgrade) |

For `AsyncDevice` the methods that do I/O (`invoke`, `identity`, `capabilities`, `supports`, every API method) are coroutines, and closing is `await dev.aclose()` or `async with`.

A sync `Device` may be shared between threads; an `AsyncDevice` between tasks of one event loop. Do not close or reconfigure while calls are running. `max_concurrency` limits requests in flight and `max_streams` open streams, separately.

## Identity, capabilities, support

```python
from ax_devil_device_api import Support
from ax_devil_device_api.apis.mqtt_client import MqttClientApi

ident = dev.identity()            # .model, .product_number, .full_name, .serial_number,
                                  # .firmware_version, .hardware_id, .architecture, .properties
result = dev.supports(MqttClientApi)
if result:                        # truthy only for Support.YES
    ...
elif result.status is Support.UNKNOWN:
    print(result.reason, result.errors)   # probes failed; do not conclude "not supported"
```

`SupportResult` fields: `status` (`Support.YES`/`NO`/`UNKNOWN`), `reason`, `errors`, `observed_at`. `NO` is returned only when a probe that would list the API succeeded and did not list it (or listed another major version). `Capabilities` fields: `classic_apis`, `dca_apis`, `properties` (each `None` when its probe failed), `errors`, `observed_at`. Calls do not check support automatically.

## Available APIs

| Attribute | Module | Family | Operations |
|---|---|---|---|
| `dev.apis.mqtt_client` | `apis.mqtt_client` | JSON-RPC | `configure_client`, `activate_client`, `deactivate_client`, `get_client_status` |
| `dev.apis.analytics_mqtt` | `apis.analytics_mqtt` | Device Configuration REST | `get_all`, `list_data_sources`, `get_data_source(key)`, `list_publishers`, `get_publisher(id)`, `add_publisher`, `remove_publisher(id)` |
| `dev.apis.parameter_management` | `apis.parameter_management` | classic `param.cgi` | `list`, `list_definitions`, `update`, `add`, `remove` |

Each module also holds the models, `INFO` (static API description) and `OPS` (operation descriptors with `effect`, `access`, `write`). The class names are `MqttClientApi`/`AsyncMqttClientApi`, `AnalyticsMqttApi`/`AsyncAnalyticsMqttApi`, `ParameterManagementApi`/`AsyncParameterManagementApi`. Method docstrings state the access level, whether a write replaces the whole configuration, and the version requirements. Operation `support` is `docs-only` for all three: none has been verified on hardware.

## Calling methods: keywords or a request object

Every method takes `request_options=`. Methods with arguments accept either flattened keyword arguments or one positional request object, never both (`TypeError`).

```python
from ax_devil_device_api.apis.mqtt_client import ConfigureClientRequest, Server

dev.apis.mqtt_client.configure_client(
    server=Server(host="broker.example.com", protocol="ssl"), client_id="cam-7", username="u", password="p",
)
req = ConfigureClientRequest(server=Server(host="broker.example.com"), client_id="cam-7")
dev.apis.mqtt_client.configure_client(req)
```

- Unset fields are not sent. `pydantic.MISSING` (also `ax_devil_device_api.MISSING`) is the "not given" default in method signatures; do not use it in models.
- Arguments are validated locally: a typo or invalid value raises `pydantic.ValidationError` before any request.
- Responses ignore unknown fields and keep enum values newer than the `Literal`.
- Version-gated fields: setting a field newer than the negotiated API version raises `NotSupported` before sending (`.required` names the version).

Safe read-modify-write (replace semantics, masked secrets):

```python
status = dev.apis.mqtt_client.get_client_status()
if status.config is not None:
    req = ConfigureClientRequest.from_current(status.config)   # drops the masked password, sets keep_existing_password
    req = req.model_copy(update={"keep_alive_interval": 60})
    dev.apis.mqtt_client.configure_client(req)
```

`AddPublisherRequest.from_current(publisher)` (in `apis.analytics_mqtt`) recreates a publisher, for example on another camera. See `examples/08_clone_configuration.py` for the full flow.

Parameters:

```python
values = dev.apis.parameter_management.list(group=["Image.I0.Appearance.*"])   # dict[str, str], "root." removed
dev.apis.parameter_management.update({"Image.I0.Appearance.Resolution": "1920x1080"})
```

## Request options and retries

```python
from ax_devil_device_api import NO_RETRY, RequestOptions, RetryPolicy

dev.apis.parameter_management.list(request_options=RequestOptions(timeout=60))
dev.apis.mqtt_client.get_client_status(request_options=RequestOptions(retry=RetryPolicy(attempts=3, retry_reads=True)))
```

`RequestOptions(timeout, retry)` applies to one call. `RetryPolicy(attempts=2, retry_unsent=True, retry_reads=False, backoff=0.2, max_backoff=5.0)`: requests that never reached the device are retried for every operation; with `retry_reads=True` read operations are also retried after timeouts or dropped connections; writes and actions are never resent once they may have arrived; HTTP and API errors are never retried. `NO_RETRY` disables retries.

## Errors

All derive from `DeviceError` (`ax_devil_device_api.errors`).

```
DeviceError
 ConfigurationError
 TransportError (.request_sent)
   RequestTimeout: ConnectTimeout, ReadTimeout, WriteTimeout, PoolTimeout
   TlsError, ConnectionFailed
 AuthError
 HttpError (.status, .body_excerpt)  -> HttpAccessDenied (403), HttpUnavailable (503)
 ApiError (.api, .operation, .code, .message, .description, .kind, .http_status, .details)
   -> ApiAccessDenied, ApiUnavailable
 ResponseFormatError (.api, .operation, .reason)
 NotSupported (.api, .operation, .reason, .required)
 AccessDenied, Unavailable   categories; HttpAccessDenied/ApiAccessDenied and HttpUnavailable/ApiUnavailable also inherit these
```

```python
from ax_devil_device_api.errors import AccessDenied, DeviceError, NotSupported, Unavailable

try:
    dev.apis.mqtt_client.activate_client()
except AccessDenied: ...      # 403 or a documented authorization-failure code
except Unavailable: ...       # 503 or a documented busy code
except NotSupported as e: print(e.reason, e.required)
except DeviceError as e: print(e)
```

## Observability

`on_request(record)` receives a redacted description of each outgoing request; `on_response(record)` receives one dict per attempt with `api`, `operation`, `method`, `path`, `status`, `error`, `duration_ms`, `attempt`. The `ax_devil_device_api` logger logs one DEBUG line per request attempt. Secrets are redacted. See `examples/06_debugging_and_lab_setups.py`.

## Testing your code with MockCamera

```python
from ax_devil_device_api.testing import MockCamera

camera = MockCamera()
camera.identity(model="AXIS Q1656", firmware="11.9.0", serial="ACCC8E")
camera.jsonrpc("/axis-cgi/mqtt/client.cgi", "getClientStatus",
               data={"status": {"state": "active", "connectionStatus": "connected"}})
with camera.device() as dev:           # or camera.async_device()
    assert dev.apis.mqtt_client.get_client_status().status.state == "active"
assert camera.calls("getClientStatus")
```

Registration: `identity(...)`, `api_list({id: version})`, `dca_apis({name: [versions]})`, `jsonrpc(path, method, data=..., error=(code, message), status=200, versions=None)` (`getSupportedVersions` is answered automatically), `rest(method, path, data=..., error=...)`, `cgi(path, text=..., match=..., content_type=..., status=..., method=...)`, `route(method, path, handler)` for a raw httpx handler, `fail(path, httpx_error_class, times=None)` to inject transport failures. A later registration for the same route overrides earlier ones; unmatched requests get 404. Paths are matched as the device sees them, so include `base_path` if you set one. Inspect `camera.requests` (`RecordedRequest`: `method`, `path`, `query`, `json`, `form`). `camera.device(host="camera.test", **kwargs)` defaults to credentials `("root", "pass")`. See `examples/09_testing_your_code.py`.

## Not available yet

Other VAPIX APIs (media, network, SSH, PTZ, events, ...), streaming downloads, WebSocket event sessions and the command-line interface are planned. The old 0.x `Client`, `DeviceConfig` and feature clients no longer exist.
