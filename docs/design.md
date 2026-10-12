# ax-devil-device-api 1.0 design

Status: the runtime is implemented; the spec/generator pipeline, the remaining protocol families, the CLI and live conformance are planned. Replaces the 0.x code entirely; no backwards compatibility. Items marked *(planned)* do not exist in the repository yet; everything else describes code in `src/`.

## 1. Goals

- Cover every VAPIX API, including several major versions of the same API, in one consistent style.
- Support sync and async from the same code base.
- Make the library mostly generated from a machine-readable spec, so a doc-watching agent can keep it current by editing specs only.
- Keep the 0.x security properties: HTTPS by default, explicit HTTP opt-in, no Basic credentials before a challenge, Digest preferred, secrets redacted in debug output.

Non-goals: RTP/media decoding (hand RTSP URLs to a media library), ONVIF coverage beyond what VAPIX pages document, Python < 3.11.

## 2. Architecture

```
VAPIX docs ──monitor (external repo)──▶ specs/apis/**/*.yaml     (planned) doc-derived; the agent edits only these
                                        specs/patches/*.yaml     (planned) device-verified corrections; human-owned
                                                │ apply patches + schema validation
                                                ▼
                                        codegen/  (planned, dev-only, deterministic)
                                                │
                ┌───────────────────────────────┼───────────────────────────────┐
                ▼                               ▼                               ▼
 src/ax_devil_device_api/apis/        tests/contract/  (planned,        docs/api_surface.txt (planned,
   <module>.py                          from spec examples)               committed public-API snapshot)
   hand-written today (3 reference modules); GENERATED later
                │ calls
                ▼
 src/ax_devil_device_api/
   __init__.py  public exports (Device, AsyncDevice, credentials, RequestOptions, RetryPolicy, SupportResult, ...)
   device.py    Device / AsyncDevice (identity, capabilities, supports, invoke, apis)
   errors.py    exception hierarchy
   testing.py   MockCamera
   _http/       types (Request, Response, bodies), config, options, auth (AxisAuth), transport (sync/async, httpx), debug
   _protocols/  base (Model, Operation, ApiInfo, flows), state (DeviceState), jsonrpc, dca, cgi   sans-IO
                planned modules: param (typed groups), service_json, soap, rest, ws, rtsp
   _runtime/    driver (sync/async flow drivers, stream results, retries), capabilities (identity, probes, support)
   features/    (planned) hand-written convenience built only on generated APIs
   cli/         (planned) generic `call` command from specs + hand-written commands
```

The 0.x code (`client.py`, `cli.py`, `clis/`, `core/`, `features/`, `utils/`) is being removed and is not part of this design.

Layer rules (the import-linter contract that enforces them in CI is *planned*; today they hold by convention):

1. `_http` knows HTTP and auth, nothing about VAPIX.
2. `_protocols` know VAPIX families, nothing about specific APIs, and never do I/O.
3. `apis` (generated) contain models, operation descriptors and thin methods. No logic. Never edited by hand once the generator exists (*planned*: CI regenerates and fails on a diff); the three current modules are hand-written targets for it.
4. `features` and `cli` use only the public API of `apis` and `device`.

When a generated method is wrong, the fix goes into a spec or patch. When a whole family behaves wrongly, the fix goes into its protocol module.

`_runtime` sits between: it runs flows over transports and implements the device-level probes. `Device` composes `_http`, `_protocols` and `_runtime`.

## 3. HTTP layer (`_http`)

```python
AuthPolicy = Literal["required", "anonymous", "if_challenged"]

@dataclass(frozen=True)
class Request:
    method: str                     # "GET", "POST", ...
    path: str                       # absolute path, no query (validated); base_path is added by the transport
    query: tuple[tuple[str, str], ...] = ()
    body: JsonBody | FormBody | RawBody | MultipartBody | None = None
    accept: str | None = None
    headers: tuple[tuple[str, str], ...] = ()   # extra headers a protocol genuinely needs
    auth: AuthPolicy = "required"
    timeout: float | None = None    # None = device default
    stream: bool = False            # see "Streaming" below
    # property: replayable -> False for one-shot bodies (iterators, open files)

@dataclass(frozen=True)
class Response:
    status: int
    headers: Headers                # immutable, case-insensitive; get_all() / items_raw keep repeated headers
    content: bytes                  # empty for a 2xx stream=True response
    request: Request
    # helpers: media_type, text, excerpt()
```

Bodies: `JsonBody`, `FormBody`, `RawBody` (bytes are replayable, an iterable of chunks is not), `MultipartBody` with `FilePart`s.

Streaming. A request with `stream=True` must be the last request a flow yields. For a 2xx response the flow receives an empty-content `Response` and returns a `StreamDecoder` (`feed(chunk)` / `close()`; `BytesDecoder` passes raw bytes through). For any other status the transport reads the whole body first, so the flow can parse the error and raise. The driver wraps the open httpx response and the decoder in a managed result: `StreamResult` (sync context manager, iterable) or `AsyncStreamResult` (async context manager, async iterable), both in `_runtime/driver.py`. Leaving the context or cancelling the task closes the httpx response. Streaming operations return these managers, never data. The shape below is the contract; no streaming API is generated yet, so the method name is illustrative:

```python
with dev.apis.debug.download_core_dump() as stream:   # sync (planned API)
    for chunk in stream: f.write(chunk)
async with dev.apis.debug.download_core_dump() as stream:   # async (planned API)
    async for chunk in stream: await f.write(chunk)
```

Sessions (WebSocket event and Device Data Hub streams) are *planned*. They are not request/response flows and will have their own contract: a `Session` / `AsyncSession` context manager with `send(message)` and iteration over received messages, built on `httpx-ws` (sync and async; not a dependency yet). Sans-IO code is limited to session setup (the `wssession.cgi` token flow) and message codecs; the socket loop is per driver.

- Headers are derived, not defaulted. `JsonBody` sets `Content-Type: application/json`; no body means no `Content-Type`. `accept` is set only when the request specifies it (the transport removes httpx's default `Accept`). This removes all header-removal machinery from 0.x.
- `SyncTransport` / `AsyncTransport` wrap `httpx.Client` / `httpx.AsyncClient`, map httpx exceptions to `TransportError` subclasses (setting `request_sent`), and expose `send(Request) -> Response` and `open_stream(Request)`, a context manager yielding `(Response, chunks)`. `base_path` is prepended to every request path. An injected httpx transport (`Device(transport=...)`) replaces the network, which is what `MockCamera` uses.
- Concurrency limits are enforced in the transport: one semaphore for requests in flight (`max_concurrency`) and one for open streams (`max_streams`). Both are `threading.BoundedSemaphore` in the sync transport; the async transport creates its `asyncio.Semaphore`s lazily inside the running loop. A stream holds its slot until its context exits.
- `AxisAuth` owns the auth state of one device and builds an `httpx.Auth` flow per request (`for_request(policy, replayable)`). It is our own flow, not httpx's `DigestAuth`, which caches a challenge before the authenticated retry has succeeded. One flow serves both transports:
  - `required`: use the *verified* credential pre-emptively if there is one; otherwise send without credentials and on 401 pick Digest if offered, otherwise Basic. Never send Basic before a challenge.
  - Two auth states: *candidate* (built from a challenge, used for the retry) and *verified* (promoted only after an authenticated 2xx). Only verified state is used pre-emptively on later requests. Digest state holds the challenge and a nonce counter, so later requests take one round trip; a 401 demotes it, and `stale=true` gets one more attempt with the fresh challenge.
  - State updates are a single swap of an immutable state object under a `threading.Lock` (never held across an await).
  - `anonymous`: never adds credentials. `if_challenged`: like `required` but never pre-emptive, so a device that allows anonymous access is used anonymously (classic API discovery needs this).
  - A request with `replayable=False` is never retried: if it would need a challenge round trip (no verified state, or a 401 after being sent with verified state), it fails with `AuthError` and the caller must re-supply the body.
  - `BearerToken` (static string or callable) is sent on every non-anonymous request. A callable is called for every request and once more after a 401 (if the body is replayable); a second 401 raises `AuthError`. `ConnectionConfig` rejects Bearer over HTTP.
- `ConnectionConfig` is frozen and validated at construction; its fields are listed in section 6. `Credentials` redacts the password in `repr`; `_http/debug.py` redacts secrets in `on_request` records.
- The per-device concurrency limits (section 6) and the error classes (section 7) are applied here; the retry loop is in the driver (section 7).

## 4. Protocols: sans-IO call flows

Every finite call is a generator that yields `Request`s and receives `Response`s, the same pattern as `httpx.Auth.auth_flow`. A small sync driver and a small async driver (`_runtime/driver.py`: `run_sync`, `run_async`) run any flow, wrap streaming results (section 3) and apply the retry policy (section 7), so no protocol logic exists twice.

```python
CallFlow = Generator[Request, Response, T]

# one flow function per binding type, registered with register_binding(); flow_for(op, params, state) dispatches
def flow(op: Operation[B], params: Model | None, state: DeviceState) -> CallFlow[Any]: ...
```

`Operation` (in `_protocols/base.py`) carries `api: ApiInfo`, `id`, `binding` (family-specific wire data), `params` model type, `result` type, `access`, `effect`, `since`, `write`, `applicability`, `errors` and `support`. The binding type selects the protocol. `Family` is an enum of all planned families; only the bindings of implemented protocols are registered.

Prerequisites such as version negotiation are steps inside the flow. Results are cached in `DeviceState`, so they cost a round trip only once per device. The JSON-RPC flow, simplified:

```python
def flow(op, params, state):                                   # _protocols/jsonrpc.py
    version = yield from _version(op, state)                   # may yield getSupportedVersions
    check_applicability(op, params, version)                   # NotSupported before sending (section 5)
    response = yield Request("POST", binding.path, body=JsonBody(envelope(version, params)), ...)
    payload = _decode(op, response)                            # body first (error object), then status
    return parse_result(op, payload.get("data"))

def _advertised(op, state):
    cached = state.advertised_versions(key)                    # key = "jsonrpc:<path>"
    if cached is not None: return cached
    token = state.versions_token(key)                          # taken before the I/O
    response = yield Request("POST", path, body=JsonBody({"method": "getSupportedVersions"}), ...)
    versions = parse(response)
    state.set_advertised_versions(key, versions, token)        # dropped if the fact was invalidated meanwhile
    return versions
```

`select_version(advertised, major, known_versions)` is pure and not cached; it returns `None` when the device offers no version of the class's major, which becomes `NotSupported`. On a JSON-RPC error 2100 (version not supported) or a 404 from an endpoint that negotiated before, the flow calls `state.forget_advertised_versions(key)` and re-raises.

`DeviceState` (`_protocols/state.py`) caches only facts about the device (advertised versions per endpoint, discovery probe results, identity), never per-class selections. Selection is a pure function of those facts and the calling class's major version, so a v1 and a v2 class for the same API cannot interfere. Concurrency control is by tokens:

- `token(key)` is taken before the I/O that produces a fact; `set(key, value, token)` stores it only if neither `clear()` nor `forget(key)` happened since. A probe that was in flight when its fact was invalidated cannot put the stale fact back.
- `set_or_clear(key, value, token, stale)` compares, optionally clears everything, and stores in one atomic step (used to drop all facts when `identity()` reports different firmware).
- `forget(key)` drops one fact and invalidates its outstanding tokens; `clear()` drops everything. All checks run under one `threading.Lock` that is never held across I/O or an `await`.
- `Device.refresh()` calls `clear()`.

Negotiation is a per-API strategy on the JSON-RPC binding: `GetSupportedVersions(key, auth)` (version list under `data[key]`), `FixedVersion(version)` (API has no negotiation; the spec states the version) and `NoVersion()` (no `apiVersion` field). A strategy based on `api_discovery` (version from `getApiList`) is *planned*.

Families and what each protocol owns:

| Family | Module | Status | Owns |
|---|---|---|---|
| JSON-RPC CGI | `jsonrpc` | implemented | `{apiVersion, method, params}` envelope (`params` or top-level placement); `getSupportedVersions` / fixed / no-version negotiation; `{error:{code,message}}` → `ApiError` (body first, then status) |
| Device Configuration REST | `dca` | implemented | `/config/rest/<api>/<ver>/…` path templates with percent-encoded path parameters; `{data}` request body; `{status, data}` / `{status:"error", error}`; entity get/set/add/remove/actions |
| Classic CGI | `cgi` | implemented | query/form encoding, `yes/no` booleans, CSV lists, spread mappings; reply codecs `TextOk`, `TextKv`, `Text`, `Xml` (element mapping), `Binary` (media type and signature checks), `JsonReply`; `# Error:` / `# Request failed:` and XML error detection; optional streaming |
| param.cgi typed groups | `param` | planned | typed parameter-group access used by generated group accessors. The generic `list` / `update` / `add` / `remove` operations already work through `cgi` (`apis/parameter_management.py`) |
| VAPIX JSON service | `service_json` | planned | `POST /vapix/<svc>` with `{"<prefix>:<Op>": {...}}`; JSON fault mapping |
| SOAP | `soap` | planned | SOAP 1.2 envelope and faults for the few SOAP-only services |
| Plain REST | `rest` | planned | non-framework REST APIs (AXIS Audio Manager Edge/Pro): path templates, JSON bodies, HTTP status errors |
| WebSocket | `ws` | planned | `wssession.cgi` token and message codecs; sockets via the session contract (section 3) |
| RTSP | `rtsp` | planned | URL building only |

Families have documented exceptions (for example `capture-mode` puts arguments at the top level of the JSON-RPC envelope; some JSON-RPC APIs have no `getSupportedVersions`; classic CGIs accept XML or form request bodies). Bindings therefore carry declarative knobs, never code: envelope placement of arguments (`params` object or top level), negotiation strategy, per-operation endpoint override, request codec and content type (`json`, `form`, `query`, `xml`, `multipart`, `raw`), and response codec. An exception that the knobs cannot express is a protocol change and needs a human.

## 5. Generated code

One module per API spec (major version), containing models, an operation table and two classes. `src/ax_devil_device_api/apis/mqtt_client.py` (JSON-RPC), `analytics_mqtt.py` (Device Configuration) and `parameter_management.py` (classic CGI) exist today as hand-written reference output; the generator (*planned*) must reproduce them exactly. They still carry a "GENERATED, do not edit" header, which is the intended end state.

```python
# apis/mqtt_client.py — will be GENERATED from specs/apis/network-video/mqtt-client.yaml. Do not edit.
class Server(Model):
    host: str
    protocol: Literal["tcp", "ssl", "ws", "wss"] | None = None
    alpn_protocol: str | None = Field(default=None, validation_alias="alpnProtocol", serialization_alias="alpnProtocol")

class ConfigureClientRequest(Model):
    server: Server
    client_id: str = Field(validation_alias="clientId", serialization_alias="clientId")
    ...
    @classmethod
    def from_current(cls, config: ClientConfig) -> ConfigureClientRequest: ...   # safe round trip

INFO = ApiInfo(id="mqtt-client", name="MQTT client API", family=Family.JSONRPC, major=1, known_versions=(ApiVersion(1, 0),),
               discovery=(ApiDiscovery("mqtt-client"),), errors={2105: ErrorCode("Authorization failure", "access_denied"), ...})

class OPS:
    configure_client = Operation(INFO, "configure_client", JsonRpcBinding("configureClient", PATH),
                                 params=ConfigureClientRequest, access="admin", effect="write", write="replace")

class MqttClientApi(SyncApi):
    @overload
    def configure_client(self, request: ConfigureClientRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def configure_client(self, /, *, server: Server, client_id: str, port: int | MISSING = MISSING, ...,
                         request_options: RequestOptions | None = None) -> None: ...
    def configure_client(self, request=None, /, *, request_options=None, **kwargs) -> None:
        """Configure the MQTT client ... Replaces the whole configuration ... Access: admin."""
        self._run(OPS.configure_client, request, kwargs, request_options)

class AsyncMqttClientApi(AsyncApi): ...   # same, async
```

Models:

- One `Model` class serves requests and responses. Optional fields are `X | None = None`; the model records which fields were set, and only set fields are sent (`exclude_unset`). So omission, null and server defaults stay distinct without a sentinel in user-facing types:
  - not set: not sent;
  - set to `None`: sent as `null`, allowed only for fields listed in `__nullable__` (rejected at construction otherwise);
  - documented server defaults go in docstrings, never into Python defaults.
- Fields the device always returns are required. A response missing one raises `ResponseFormatError`.
- Responses ignore unknown fields and keep enum values newer than the generated `Literal` (new firmware may add both). Construction in Python rejects unknown fields and invalid enum values.
- Wire names are `validation_alias`/`serialization_alias`, never `alias`, so type checkers show the Python names in constructors.
- Method signatures use `pydantic.MISSING` (re-exported as `ax_devil_device_api.MISSING`) as the "not given" default for flattened keyword arguments. It never appears in models or results.

Methods:

- Every method takes `request_options: RequestOptions | None` (timeout, retry policy for this call).
- Signature rule (deterministic, so the generator can apply it): an operation whose params include a nested model, or more than four fields, gets two overloads: flattened keyword arguments, or one positional `*Request` object (passing both is a `TypeError`). Smaller operations, such as `parameter_management.update(parameters)` or `get_publisher(id)`, get one plain signature: path keys and the main argument positional, the rest keyword-only.
- Writes declare `write`: `replace` (fields left out return to defaults), `patch`, `create` or `delete`, shown in the docstring.
- Where a read result can be written back, the request model gets `from_current(result)`. It drops fields the device masks or that are read-only (from the spec), and sets "keep existing" flags where the API has them (MQTT `keepExistingPassword`). Blind round trips must never write a masked `*****` back.

Descriptors and naming:

- `Model`, `Operation`, `ApiInfo` and `ApiVersion` are runtime types in `_protocols/base.py`; the generator only emits data and signatures.
- One class per major version. The unsuffixed name (`mqtt_client`) is permanently the first major version generated; later incompatible majors get `_v2`, `_v3`. Regeneration never changes what an existing name means. DCA path versions map the same way.
- Python names are derived deterministically from spec ids and wire names, with an explicit collision rule and `x-python-name` overrides; `docs/api_surface.txt` (*planned*) makes every rename visible.
- Version applicability is finer than per operation. `since` (and `until`/`deprecated`) can sit on an operation, a parameter, a nested field or an enum value. Before sending, `check_applicability` rejects any *set* argument, field or enum value newer than the negotiated version with `NotSupported` (`.required` names the version). Requirements on AXIS OS firmware or an installed ACAP application are separate fields, checked against capabilities when known.
- Each operation declares its `effect`: `read`, `write`, `action`, or `unknown`. It cannot be inferred from the HTTP method, because classic CGIs change state with GET. Retries and live tests depend on it; the generator warns on `unknown`.
- Error tables carry a `kind` per code (`access_denied`, `unavailable`, `invalid_argument`, `not_found`, `unsupported`, `internal`), which selects the error class (section 7); `kind` is optional on an `ErrorCode`.
- `apis/__init__.py` is to be generated too; today it is hand-written: `Apis` / `AsyncApis` namespaces with one lazy, cached property per API, exposed as `device.apis`. `device.api(ApiClass)` returns the cached instance of one class.
- Support status is tracked per operation (`Operation.support`): `verified` (a live test passed, recording model and firmware), `docs-only` (all three reference APIs today), or `known-broken`. Recording `verified` from live runs is *planned*.

## 6. Device

```python
dev = Device("10.0.0.1", credentials=("root", "pass"))            # no I/O; like httpx.Client
dev.apis.mqtt_client.get_client_status()
dev.identity()                                                     # model, serial, firmware (cached)
dev.supports(MqttClientApi)                                        # SupportResult(YES/NO/UNKNOWN, reason, errors)
dev.invoke(mqtt_client.OPS.get_client_status)                      # any operation by descriptor
dev.close()                                                        # or: with Device(...) as dev

async with AsyncDevice("10.0.0.1", credentials=BearerToken(get_token), base_path="/vms/cam7") as dev: ...
```

Lifetime. One long-lived `Device` per camera is the intended use, for a script or for a service running for weeks. Creating one does no I/O. It owns the connection pool, the verified credential and the cached device facts. It handles the camera's lifecycle itself:

- idle connections the camera dropped are reopened on the next call;
- requests that never reached the camera are retried (section 7, `RetryPolicy`);
- after a reboot the credential is re-negotiated on the first 401;
- cached facts are invalidated on evidence: JSON-RPC error 2100 (version not supported) or a 404 from an endpoint that negotiated before, and `identity(refresh=True)` reporting different firmware. Not on timeouts.

Host or credential changes mean a new `Device`. Health checks are explicit (`identity(refresh=True)`); there are no background threads. Reconnect and backoff policy for whole sessions stays in the application.

Sharing. A sync `Device` may be shared between threads; an `AsyncDevice` between tasks of one event loop. Closing or reconfiguring concurrently with calls is not supported. Discovery probes and identity are coalesced per key with a lock (one in flight at a time). `DeviceState` uses generation tokens (section 4): a fact computed before `refresh()` is never stored after it. Cancelling a call releases its connection and concurrency slot; it does not undo a request the device already received.

Concurrency. Each device limits requests in flight (`max_concurrency`, default 4) and open streams (`max_streams`, default 2) separately, so a long download never blocks control calls such as PTZ. No fleet object: one `Device` per camera; fleets are application code (see `examples/01`).

Capabilities. `capabilities()` runs three probes (concurrently on `AsyncDevice`): classic `apidiscovery.cgi` (`if_challenged`), `/config/discover`, and the `param.cgi` `Properties.API` group. Successful probes are cached until invalidated; failed ones are reported in `Capabilities.errors` and retried on the next call. `supports(api)` returns an immutable `SupportResult(status, reason, errors, observed_at)`: `NO` only when a probe that would list the API succeeded and did not list it (or listed a different major version), `UNKNOWN` when the relevant probes failed. Calls do not check support automatically; version negotiation raises `NotSupported` when it matters.

Configuration (`Device(host, *, ...)` keyword arguments, validated into a frozen `ConnectionConfig`; `Device.from_config` takes a ready one). `scheme` (default `https`), `port`, `base_path` (reverse proxy or VMS prefix; starts with `/`, no trailing `/`), `proxy`, `verify` (bool, CA bundle path, or `SSLContext`), `credentials` (`Credentials`, a `(user, password)` tuple, or `BearerToken` with a static or refreshing token), `timeout` (default 10 s), `retry`, `allow_http` (required for `scheme="http"`), `max_concurrency`, `max_streams`, `on_request`, `on_response`, and the low-level `transport` (an httpx transport).

Observability. Standard `logging` at DEBUG on the `ax_devil_device_api` logger (one line per request attempt), `on_request` (redacted request), `on_response` (structured record per attempt: api, operation, method, path, status, error, duration_ms, attempt). OpenTelemetry can instrument the underlying httpx client.

Testing. `ax_devil_device_api.testing.MockCamera` answers identity, API discovery, Device Configuration discovery, JSON-RPC (`getSupportedVersions` is answered automatically), REST and CGI routes (`identity`, `api_list`, `dca_apis`, `jsonrpc`, `rest`, `cgi`, `route` for raw httpx handlers), injects transport failures (`fail`), records requests (`requests`, `calls(method)`) and hands out `device()` / `async_device()`, so users can test their own code without hardware. Unmatched requests get 404. `Device(transport=...)` remains the low-level seam. See `examples/09_testing_your_code.py`.

## 7. Errors

```
DeviceError
├── ConfigurationError
├── TransportError (.request_sent)
│   ├── RequestTimeout: ConnectTimeout*, ReadTimeout, WriteTimeout, PoolTimeout*
│   ├── TlsError*
│   └── ConnectionFailed            (* = request never sent; always safe to retry)
├── AuthError                       (wrong credentials, or 401 with none configured)
├── HttpError(status, body_excerpt)
│   ├── HttpAccessDenied            (403)        also an AccessDenied
│   └── HttpUnavailable             (503)        also an Unavailable
├── ApiError(api, operation, code, message, description, kind, http_status, details)
│   ├── ApiAccessDenied             (kind access_denied)
│   └── ApiUnavailable              (kind unavailable)
├── ResponseFormatError(api, operation, reason)
├── NotSupported(api, operation, reason, required)
├── AccessDenied                    category: catch both 403 and documented auth-failure codes
└── Unavailable                     category: catch both 503 and documented busy codes
```

Retries (`RetryPolicy`, per device, overridable per call through `RequestOptions(retry=...)`; `NO_RETRY` disables them): requests that were never sent are retried for every operation (default 2 attempts in total, backoff 0.2 s doubling up to 5 s). Read timeouts and dropped connections are retried only with `retry_reads=True` and only for `effect: read` with a replayable body. Writes and actions are never resent after the request may have arrived; HTTP and API errors are never retried; streams are never restarted.

## 8. Spec format v2 (owned by this repo; planned)

Nothing in this section exists yet: there is no `specs/` directory, `codegen/` or schema in the repository.

The v1 corpus in `vapix_spec` is converted once by `codegen/migrate_v1.py` and then v1 is dropped. v2 changes, driven by the generator and by `SCHEMA_GAPS.md`:

- `family` is an explicit enum (the table in section 4); no inference from `styles`.
- Family binding at API level (`jsonrpc: {path, majors}`, `dca: {api, path_version}`, `cgi: {path}`); operations carry only what differs. Multiple bindings per operation are allowed (`bindings: [...]`) for JSON-service/SOAP pairs; the generator uses the first supported one.
- Collections are maps keyed by id (`operations`, `types`, `errors`, `params` for query-style operations), not lists. This keeps diffs and patch paths stable.
- JSON-RPC and service params are a JSON Schema for the `params` object; results are a JSON Schema for `data`. No flattened dotted parameter lists.
- Classic CGI params keep a per-parameter list with `format` (`axis-boolean`, `csv`, …); responses declare `format` and, for XML, an `xml` mapping.
- Python names are derived deterministically (snake_case of wire names); `x-python-name` only resolves clashes.
- `x-*` keys allowed everywhere; ignored by the generator unless documented.
- `sources[]` with content hashes and `provenance` stay as in v1; they drive change monitoring.

Patches live in `specs/patches/<id>.yaml` and come in two kinds:

- **Corrections** apply to every device: the docs are wrong. Each is an explicit operation (RFC 6902 style: `add`, `replace`, `remove` at a JSON Pointer path) with an `expect` field holding the value or hash the patch was written against, plus `evidence` (model, firmware, date, what was observed). RFC 7396 merge patches are not used because they cannot set an explicit `null` and replace arrays wholesale.
- **Variants** apply only to matching devices: `when: {firmware: "<12.0", model: "Q1656*"}`, then the same operation list. The generator turns variants into descriptor data checked at runtime against the device's identity, never into a universal change. A field missing on one camera becomes a variant, not a correction.

When the base spec changes under a patch, `codegen check` compares each operation's `expect` with the new base value and also checks ancestor paths (a patch on `/operations/foo/params/bar` conflicts if `/operations/foo` was replaced). A mismatch is a conflict that needs a human.

For DCA APIs, `codegen import-dca --device <host>` fetches the device-served `openapi.json` / model and reports differences from the spec. The device is more authoritative than the docs.

## 9. Tests

Done:

1. Unit tests under `tests/unit/` (264 tests, run with `uv run pytest`): `_http` (transport, auth including the 0.x security cases, retries), the `jsonrpc`, `dca` and `cgi` protocols, the driver, capabilities and support decisions, version selection, models and error mapping, `MockCamera`, and round trips through the three reference APIs. Async tests use `anyio`; `uv run pyright` type-checks the package.

Planned:

2. Contract tests generated from spec examples: the built request matches the documented request, and the documented response parses into the result model (or raises the documented error).
3. Live conformance (`pytest -m live --device …`) runs `effect: read` operations of APIs that `supports()` reports as `YES`; `unknown`-effect operations are skipped. Results are recorded per operation with model and firmware and feed the support status in section 5. Failures become correction or variant patches.

Planned CI: schema validation, `codegen check` (regenerate, diff must be empty), contract tests, import-linter, type check of generated code. Today CI-relevant checks are `uv run pytest` and `uv run pyright`.

## 10. Maintenance loop (planned)

1. External monitor detects changed doc pages and lists the specs citing them.
2. The agent edits `specs/apis/**` by hand, citing source anchors, then runs `codegen generate` and commits the regenerated outputs (`apis/`, contract tests, `docs/api_surface.txt`) in the same PR.
3. CI validates the specs, runs `codegen check` (regenerating must reproduce the committed outputs exactly, which catches hand edits to generated files), and runs the contract tests.
4. The PR shows the spec diff and the `docs/api_surface.txt` diff. Patch conflicts block merging.

The agent's hand edits are limited to `specs/apis/**`; everything else it commits is generator output. A change needing a new family, binding knob or envelope behaviour is escalated to a human; the agent never edits `_http`, `protocols` or `codegen`.

## 11. Build order

Done:

1. `_http`, `errors`, `Device`/`AsyncDevice`, sync and async drivers, `jsonrpc`, `dca` and `cgi` protocols, capabilities and support checks, `testing.MockCamera`.
2. Hand-written target output for `mqtt-client`, `analytics-mqtt-config` and `parameter-management`; ergonomics settled in `examples/`.

Next:

3. Spec v2 schema and `migrate_v1.py`; generator reproduces the three hand-written modules exactly; contract test generation.
4. Generate all JSON-RPC and DCA APIs.
5. `param` typed groups, more XML mapping, remaining classic CGI APIs.
6. Hand-written `features/` and the new CLI (`cli/`).
7. Live conformance runs against real devices.
8. `service_json`, `soap`, `rest`, `ws` (with `httpx-ws`), `rtsp`.

## 12. Dependencies

Tooling is `uv` (`uv sync`, `uv run pytest`, `uv run pyright`). Python 3.11+ (3.10 reached end of life in October 2026).

- Runtime today: `httpx`, `pydantic>=2`.
- Dev group today: `pytest`, `anyio`, `pyright`.
- Planned runtime additions: `httpx-ws` (WebSocket sessions), `click` and `rich` (CLI).
- Planned dev additions: `pyyaml`, `jsonschema`, `import-linter` (generator and CI).

## 13. Decisions log

Settled on 2026-10-12 after an API-shape review (Codex `gpt-6-astra` and Claude Fable, reviewing `examples/`):

| Topic | Decision |
|---|---|
| Connection lifetime | One long-lived `Device` per camera; no I/O at construction; invalidate cached facts on evidence, not on timeouts. |
| Entry point | `Device(host, ...)` constructor (like `httpx.Client`), not `Device.connect`. |
| Fleets | No fleet object; per-device concurrency limits, streams counted separately. |
| Retries | Unsent requests retried by default for every operation; read retries opt-in; writes never resent. |
| Response models | No sentinel in results: required fields, `X | None` for optional ones. |
| Request shape | Flattened keyword arguments or a typed `*Request` object (overloads); `request_options` on every method. |
| Round trips | Separate read and write models plus `from_current()`, which drops masked/read-only fields. |
| Major versions | Unsuffixed name is the first major forever; later majors get `_v2`. |
| Errors | `AccessDenied` and `Unavailable` categories; timeouts by phase; `request_sent` flag; error `kind` from spec tables. |
| Capabilities | `SupportResult` object; `identity()` as cached profile and health check; no automatic support checks before calls. |
| Event sessions | `connect(event_filter_list=...)` in one step; sessions report gaps after reconnects; reconnect policy is the application's. |
| Observability | stdlib logging + `on_request` + `on_response`. |
| User testing | `testing.MockCamera` on top of transport injection. |
| Auth and routing | `BearerToken`, `base_path`, `proxy`; ACAP routes are ordinary absolute paths under the base path. |

