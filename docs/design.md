# ax-devil-device-api 1.0 design

Status: implemented. The runtime, the spec format and generator (`codegen/`), 208 generated API modules (`src/ax_devil_device_api/apis/`), the protocol families below, WebSocket sessions, streams, uploads, RTSP URLs, the hand-written `features/` layer and the `ax-devil` command line all exist and are covered by tests. Not done: live conformance against real devices (no operation is `verified` yet), import-linter enforcement of the layer rules, and the external doc monitor. Replaces the 0.x code entirely; no backwards compatibility. Items marked *(planned)* do not exist in the repository; everything else describes code in this repository.

## 1. Goals

- Cover every VAPIX API, including several major versions of the same API, in one consistent style.
- Support sync and async from the same code base.
- Make the library mostly generated from a machine-readable spec, so a doc-watching agent can keep it current by editing specs only.
- Keep the 0.x security properties: HTTPS by default, explicit HTTP opt-in, no Basic credentials before a challenge, Digest preferred, secrets redacted in debug output.

Non-goals: RTP/media decoding (hand RTSP URLs to a media library), ONVIF coverage beyond what VAPIX pages document, Python < 3.11.

Scope statements:

- RTSP: the client builds RTSP URLs only. RTSP session commands (`OPTIONS`, `DESCRIBE`, `SETUP`, `GET_PARAMETER`, `SET_PARAMETER`) and RTSP-over-HTTP are out of scope.
- Unsupported WebSocket and audio formats: the Google JSON WebSocket codec, STOMP, binary audio formats and decoding of multipart audio. Operations that need them are not generated; the spec records each as a `BLOCKED(<reason>)` entry in `provenance.open_questions`, so the gap stays visible and can be revisited.
- `service_json` is preferred over SOAP: when a service is documented in both forms, the spec carries only the JSON form. SOAP is used for services that have no JSON binding.

## 2. Architecture

```
VAPIX docs ──monitor (external, not in this repo)──▶ specs/apis/<section>/<id>.yaml   doc-derived; the agent edits only these
                                                      specs/schema.json                  JSON Schema of the format
                                                      specs/patches/<id>.yaml            device-verified corrections (supported by codegen; none committed yet)
                                                │ apply patches + schema validation
                                                ▼
                                        codegen/  (dev-only, deterministic: python -m codegen validate | generate | check)
                                                │
                ┌───────────────────────────────┼───────────────────────────────┐
                ▼                               ▼                               ▼
 src/ax_devil_device_api/apis/        tests/contract/                    docs/api_surface.txt
   <module>.py, __init__.py             runs the examples of the specs      committed public-API snapshot
   GENERATED                            against the generated modules       (its diff shows every rename)
                │ calls
                ▼
 src/ax_devil_device_api/
   __init__.py  public exports (Device, AsyncDevice, credentials, RequestOptions, RetryPolicy, Heartbeat, Upload, sessions, SupportResult, ...)
   device.py    Device / AsyncDevice (identity, capabilities, supports, invoke, connect_session, rtsp_url, apis)
   errors.py    exception hierarchy
   testing.py   MockCamera
   rtsp.py      RtspUrl, MediaStream, RTSP URL building (pure)
   _streams.py  stream decoders (bytes, mjpeg parts, lines)
   _http/       types (Request, Response, bodies), config, options, auth (AxisAuth), transport (sync/async, httpx), upload, multipart, debug
   _protocols/  base (Model, Operation, ApiInfo, flows), state (DeviceState), xmlmap, and one module per family:
                jsonrpc, dca, cgi, service_json, soap, rest   (sans-IO call flows)
   _runtime/    driver (sync/async flow drivers, stream results, retries), capabilities (identity, probes, support),
                ws (sessions), ws_codecs (message codecs)
   features/    hand-written convenience built only on generated APIs: snapshot, device summary, API registry
   cli/         argparse command line `ax-devil`: generic `call`, `apis` and `ops` driven by the generated modules,
                plus `snapshot`, `summary` and `supported`
```

The 0.x code (`client.py`, `clis/`, `core/`, `utils/` and the old `features/`) is gone and is not part of this design.

Layer rules (an import-linter contract to enforce them in CI is *planned*; today they hold by convention):

1. `_http` knows HTTP and auth, nothing about VAPIX.
2. `_protocols` know VAPIX families, nothing about specific APIs, and never do I/O.
3. `apis` (generated) contain models, operation descriptors and thin methods. No logic. Never edited by hand: CI runs `python -m codegen check`, which regenerates and fails on any difference.
4. `features` and `cli` use only the public API of `apis` and `device`. The CLI additionally reads the operation descriptors of the generated modules to list and call operations.

When a generated method is wrong, the fix goes into a spec or patch. When a whole family behaves wrongly, the fix goes into its protocol module.

`_runtime` sits between: it runs flows over transports, implements the device-level probes and the WebSocket sessions. `Device` composes `_http`, `_protocols` and `_runtime`.

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

### Streaming

A request with `stream=True` must be the last request a flow yields. For a 2xx response the flow receives an empty-content `Response` and returns a `StreamDecoder` (`feed(chunk)` / `close()`). For any other status the transport reads the whole body first, so the flow can parse the error and raise. The driver wraps the open httpx response and the decoder in a managed result: `StreamResult` (sync context manager, iterable) or `AsyncStreamResult` (async context manager, async iterable), both in `_runtime/driver.py`; `.response` gives status and headers. Leaving the context or cancelling the task closes the httpx response. Streaming operations return these managers, never data. A spec selects the decoder (`_streams.py`): `bytes` (raw chunks), `mjpeg` (`multipart/x-mixed-replace` parts as `Part`, one JPEG each) or `lines` (text lines; on a `multipart/x-mixed-replace` or `multipart/mixed` answer, such as the I/O port monitor, the lines of the part bodies, with boundaries, part headers and blank keep-alive lines dropped).

```python
with dev.apis.media_stream.get_media_stream(container="mp4") as stream:          # sync
    for chunk in stream: f.write(chunk)
async with adev.apis.media_stream.get_media_stream(container="mp4") as stream:   # async
    async for chunk in stream: await f.write(chunk)
```

### Sessions (WebSocket)

Sessions (event streaming, Device Data Hub, the audio and intercom WebSockets) are not request/response flows. A generated `connect(...)` returns a `Session` (sync context manager) or `AsyncSession` (async context manager) from `_runtime/ws.py`, with `send(message)`, `receive(timeout)`, `request(method, params)`, iteration over received messages and `notifications()` for parsed ones. The socket loop is `httpx-ws`'s (sync and async). Sans-IO code is limited to session setup (the optional `wssession.cgi` token, `use_token=True`), the message codecs (`_runtime/ws_codecs.py`: `events`, `datahub`, `raw`) and the setup requests (`events:configure`, `data-hub_v1:subscribe`). `Device.connect_session(SessionSpec, ...)` is the lower-level entry point the generated methods call. The contract:

- Heartbeat. The WebSocket APIs document no application-level heartbeat, so liveness is a ping-based heartbeat: every `Heartbeat.interval` seconds (default 20) the client sends a WebSocket ping, and if no pong arrives within `Heartbeat.timeout` (default 20) the session ends with `ConnectionFailed`. `Heartbeat(None)` turns pings off; a silent half-open connection is then never noticed. Silence alone is never an error, because idle event streams are normal. Pass `heartbeat=` to `connect`.
- Ending. The device closing with code 1000 or 1001, or the application leaving the `with` block, is a normal end: iteration stops and `receive()` raises `SessionClosed`. Anything else (network error, ping timeout, other close code) raises a `TransportError`.
- Reading. Every read (`receive`, `notifications()`, `request`) goes through one dispatcher with one reader at a time (a lock-free hand-over in async, a condition variable in sync). Whoever reads a frame routes it: the reply to a registered request goes to that request (its id is registered *before* it is sent, so a reply cannot be missed or taken by another reader); every other frame (notifications, unmatched replies, plain frames) goes to the queue that `receive()` and `notifications()` drain, in arrival order. Requests are therefore multiplexed: several may be outstanding, from different tasks or threads, next to a notification iterator. Timeouts count the time spent waiting for the reader; a timed-out or cancelled request just unregisters; a close or failure is raised to every pending request and reader (the stored error, once). `receive(timeout=0)` polls the buffer without waiting. A request's timeout is the caller's total budget: it bounds the wait for the reply, and in async also the send itself (`anyio.fail_after` with what is left; a timeout mid-send ends the session as a `network` failure with `ReadTimeout`, since a half-written frame leaves the connection unusable). A sync send is bounded by the transport write timeout (the device timeout, supplied to every WebSocket write; a stalled write is a `ConnectionFailed`) and by the heartbeat, because a blocking socket write cannot be interrupted safely mid-frame. The queue of unread messages holds at most `WS_QUEUE_SIZE` (512) entries: when it is full (a request is waiting for its reply while notifications flood in, or the app reads slowly) the OLDEST message is dropped and reading goes on, so a reply is always dispatched and the session never deadlocks. Drops are counted in the read-only `dropped_notifications` attribute and logged as one warning per overflow episode (the next one starts after the queue drains below the limit).
- Gaps. Events are not replayed. The device keeps one record per session (key = endpoint and query): when it opened, the last data frame it received (its last evidence of liveness), and a *termination* `(cause, code, time)` that is set once, by whichever layer sees the end first: the transport (a close frame is stamped when it arrives, before the reader hands it on), the reader's termination (checked whenever another session opens, a session closes or sends, even if the app never read the end), `receive`, `send`, `close()` or leaving the `with` block. The causes are `normal_remote` (close 1000/1001), `local_close`, `abnormal_remote` (any other code), `network`, `oversize` (the 8 MiB limit) and `send_failure`; a later observer never changes a recorded termination, and leaving the `with` block records `local_close` at that moment only if nothing was recorded. A session was covered until its termination time for `normal_remote` and `local_close`, and until its last data frame for every other cause. `session.gap = Gap(start, end)` is *computed* when a session opens, never stored: `None` for the first session of a key and while another session for the key is still live (coverage is continuous); otherwise `start` is the latest coverage end of the earlier sessions and `end` is the new session's opening time. So the order in which overlapping sessions are finalized does not matter, and finished records are folded into one number per key. The ledger is lock-protected because the sync reader runs in its own thread. Reconnect policy and resynchronising after a gap are the application's (see `examples/05_event_watch.py`).
- A session holds one of the device's stream slots (`max_streams`) until the `with` block ends. It authenticates in the handshake (Digest or Bearer) unless `use_token=True`; then the handshake is sent without an `Authorization` header (`auth="anonymous"`) and only the `wssession` token authenticates it. `RequestOptions.timeout` applies to the token request, the handshake and the setup requests (`events:configure`, `data-hub_v1:subscribe`), and is the default for later `session.request()` calls. Fragmented messages (text or binary) are reassembled before decoding, up to 8 MiB counted in bytes (UTF-8 for text). The limit is enforced per wsproto event, while the message is still being received, so an unfinished message cannot buffer without bound; past it the transport is closed with a real close frame, code 1009, and the receive raises `ResponseFormatError`; later `send`/`receive` raise `SessionClosed` (code 1009) and the context exit sends no second close. `subscriptions` (Data Hub) and `event_filter_list` (events) are validated before anything is sent: each subscription mapping against the generated `Subscription` schema (wire names are serialized), each filter mapping against `topicFilter`/`contentFilter`; a bad one raises `ValidationError`/`ValueError` locally. The session enters the gap ledger only after its setup requests succeed, so a failed setup leaves earlier gap data intact. Path parameters (`SessionSpec.bind`) are percent-encoded as one segment each; `.` and `..` are rejected with `ValueError`. Event-session error codes 2105 and 2106 raise `ApiAccessDenied` (an `AccessDenied`), like the Data Hub.
- In-session requests (`events:configure`, `data-hub_v1:listTopics`) are not operations; call `session.request(method, params)`.

### Uploads

Every upload argument (cgi and jsonrpc, multipart or raw body) is an `UploadSource`: `bytes`, a `pathlib.Path`, or `Upload(stream, size, filename=None, content_type=None)`. A plain `str` is rejected as ambiguous. Requests always carry `Content-Length`. Content up to 8 MiB (`INLINE_LIMIT` in `_http/upload.py`) is read into memory, so the body is replayable after an authentication challenge. Larger content is streamed and therefore not replayable. When the credentials are a password and the operation sends credentials from the first request (`auth: required`, the default), the transport always first sends an authenticated preflight `GET /axis-cgi/usergroup.cgi` (read-only, answered for any role, same Digest realm as the other CGIs) and only then the body, so the body is sent once with a credential that was just verified (a nonce that expired or a device that rebooted since the last request is renewed by the preflight, never by the body). A Digest 401 with `stale=true` only refreshes the nonce: it does not demote the verified credential, and if a concurrent request does demote it between the preflight and the body, the preflight is repeated once before the body is signed (the body is never sent twice). A pool timeout (no free concurrency slot) happens before the request is built, so it is retried even for a one-shot upload, which is still sent once. A transport failure of the preflight itself is judged as the replayable read-only GET it is (the body behind it was never touched), so the normal retry rules apply to it and the body is still sent at most once; a failure while sending the body is never retried. If the preflight does not answer 2xx (or leaves the credentials unverified) the call raises `AuthError` without sending the body, even when verified credentials were cached. Small and large uploads are read only when the request is sent, never while it is built. A small `Upload` keeps its bytes after the first read, so repeating a call that failed before the body was sent (no free slot, a raising hook, a connection error) with the same source sends the data again instead of an empty body; the read runs under a per-`Upload` lock, so a cancelled async call whose worker thread is still reading cannot overlap with an immediate retry (the retry waits in a thread, then reuses the buffer; a read that failed stays failed with a clear error); a large one-shot stream that was partly consumed fails with a clear error. REST keys its error maps by HTTP status, so a status the operation documents becomes that `ApiError`. CGI maps may mix API codes (which arrive in a 200 envelope) with statuses, so on the HTTP-status path CGI consults the map only for 404 (a documented 404 `not_found` wins over the generic `NotSupported`); every other status, 5xx included, uses the generic mapping (Focus Recall's code 503 'Unknown index' does not turn an HTTP 503 into `not_found`). 401 and 403 always keep `AuthError` / `AccessDenied`. The same rule holds for an API error envelope in every protocol: the HTTP status decides the category when it fixes one (401 `AuthError`, 403 `AccessDenied`, 503 `Unavailable`, with the documented code, description and kind kept on the exception), and the documented `kind` picks the class only for 2xx envelopes, 404, other 4xx and 5xx other than 503 (SOAP sends every fault as 500). A 401 the spec documents as an API error (add_user before an admin exists) stays that `ApiError`. The other protocols (dca, jsonrpc, soap, service-json) key their maps by API error codes, so an HTTP status never matches a map entry (decoder code 403 is 'unsupported protocol', yet an HTTP 403 stays access denied). Error details are built from a safe text decode (an unknown response charset falls back to UTF-8), so error reporting itself never fails. `host` is a name or IP only (colons just in IPv6 literals; no whitespace or control characters; non-ASCII only if it IDNA-encodes; RTSP URLs and the proxy host use the same rule); `host:port` raises `ConfigurationError` pointing at `port`, and an invalid URL from httpx is a `ConfigurationError` too. Cancelling an async upload while a worker-thread read is in progress propagates `CancelledError`; the source is closed as soon as that read returns. Operations with `auth: if_challenged` or `anonymous` are not primed. CR, LF and NUL are rejected (`ConfigurationError`) in every value that reaches a header: part names, file names and content types of `Upload` and multipart parts, raw body content types, `Request.headers` and `accept`; quotes and backslashes in part and file names are escaped. The file name and content type of a part come from `Upload`, then `x-upload`, then the part name / `application/octet-stream`; for raw-body CGIs an argument marked `x-in: content_type` sets the Content-Type per call and wins over all of these.

### Headers, transports, auth

- Headers are derived, not defaulted. `JsonBody` sets `Content-Type: application/json`; no body means no `Content-Type`. `accept` is set only when the request specifies it (the transport removes httpx's default `Accept`). This removes all header-removal machinery from 0.x.
- `SyncTransport` / `AsyncTransport` wrap `httpx.Client` / `httpx.AsyncClient`, map httpx exceptions to `TransportError` subclasses (setting `request_sent`), and expose `send(Request) -> Response` and `open_stream(Request)`, a context manager yielding `(Response, chunks)`. `base_path` is prepended to every request path. An injected httpx transport (`Device(transport=...)`) replaces the network, which is what `MockCamera` uses.
- Concurrency limits are enforced in the transport: one semaphore for requests in flight (`max_concurrency`) and one for open streams and sessions (`max_streams`). Both are `threading.BoundedSemaphore` in the sync transport; the async transport creates its `asyncio.Semaphore`s lazily inside the running loop. A stream holds its slot until its context exits. Waiting for a slot counts against the request's timeout (`RequestOptions.timeout`, else the device timeout); when it runs out the call raises `PoolTimeout` without sending anything. In `AsyncDevice`, no blocking read runs on the event loop: flows never read uploads themselves, they hand the driver a deferred source (`DeferredContent`), and the driver reads it (stat, open, `stream.read`) in a worker thread before sending; large bodies are then streamed through worker-thread reads as well.
- `AxisAuth` owns the auth state of one device and builds an `httpx.Auth` flow per request (`for_request(policy, replayable)`). It is our own flow, not httpx's `DigestAuth`, which caches a challenge before the authenticated retry has succeeded. One flow serves both transports:
  - `required`: use the *verified* credential pre-emptively if there is one; otherwise send without credentials and on 401 pick Digest if offered, otherwise Basic. Never send Basic before a challenge.
  - Two auth states: *candidate* (built from a challenge, used for the retry) and *verified* (promoted only after an authenticated 2xx). Only verified state is used pre-emptively on later requests. Digest state holds the challenge and a nonce counter, so later requests take one round trip; a 401 demotes it, and `stale=true` gets one more attempt with the fresh challenge.
  - State updates are a single swap of an immutable state object under a `threading.Lock` (never held across an await).
  - `anonymous`: never adds credentials. `if_challenged`: like `required` but never pre-emptive, so a device that allows anonymous access is used anonymously (classic API discovery needs this).
  - A request with `replayable=False` (one-shot bodies: iterators, open files, uploads over 8 MiB) is never retried: if it would need a challenge round trip (no verified state, or a 401 after being sent with verified state), it fails with `AuthError` and the caller must re-supply the body. To avoid that for password credentials, the transport sends the preflight described under "Uploads" before such a body, every time. Replayable bodies and Bearer credentials need no preflight.
  - `BearerToken` (static string or callable) is sent on every `required` request; with `if_challenged` it is sent only after a 401 that carries a `WWW-Authenticate` challenge (one-shot bodies cannot be probed and get the token up front). A callable is called for every request and once more after a 401 (if the body is replayable); a second 401 raises `AuthError`. `ConnectionConfig` rejects Bearer over HTTP.
- `ConnectionConfig` is frozen and validated at construction; its fields are listed in section 6. `Credentials` redacts the password in `repr`; `_http/debug.py` redacts secrets in `on_request` records structurally and fails closed. Raw request bodies (SOAP, XML, octet-stream, streams, any non-JSON non-form body) and multipart file contents are never logged, only content type and size. Sensitive headers (`Authorization`, `Proxy-Authorization`, `Cookie`, `Set-Cookie`, any secret-named header) are dropped by name, whole value, with no parsing. Structured data (query/form/multipart text fields, JSON and structured SOAP params at any depth, including JSON-encoded strings) is redacted by key against the secret-name set (key patterns, Azure `sharedKey`/`sas`, session tokens, the SIM PIN/PUK, passphrase, `psk`, SNMP `community` and `apikey` names (matched as exact names or whole camelCase/snake_case segments, never as substrings, so `spinning` is not a secret), `AuthenticationKey` (substring, so templated names like `Port.I0.AuthenticationKey` match), the WebSocket handshake key `wssession`, and the generic name patterns, which are global); the fields a spec marks `x-masked` are redacted per operation, not by a process-wide name registry: when a call is driven, the operation's request model yields its masked wire names (aliases, nested models and `{placeholder}` templates included, `Model.masked_wire_names()`), they travel with the `Request` (`Request.masked`) and apply to that request's record only, so a field named `key`, `code`, `config` or `certificate` is redacted on the operations that mask it and shown on an unrelated operation that uses the same name; a sensitive key's value is redacted wholesale. A scalar `value` body (`{"data": "<secret>"}` for DCA, a bare value for REST) of a field that is `x-masked` or has a secret-looking name is marked `sensitive` by the generator (`DcaBinding.sensitive`, `JsonBody.sensitive`): every leaf of that body is redacted, whatever the key is called. A `{name, value}` pair (keys compared case-insensitively after stripping a leading `@` and any `prefix:`; name key `Name` or `Key`) hides `value` when the name is a secret name. Every other string gets two linear scans only: URL userinfo (every `://` independently; userinfo runs to the last `@` before `/ ? #` or whitespace, becoming `scheme://<redacted>@host`) and keyed `name=value` pairs (once the text before an `=` in a `&`/newline segment names a secret, the values after it are redacted; a value runs to whitespace or the closing quote; markup characters are ordinary). Percent-encoding is decoded layer by layer (up to 4); a value that still changes after that is replaced by `<redacted>`. Documented limits: no XML or markup parsing of string values (`<Password>x</Password>` inside a string is not detected), no `Basic`/`Bearer` heuristics in free text, no `name: value` or prose secrets without `=`, an unquoted `=` value ends at whitespace, URL passwords containing unencoded `/ ? #` or whitespace, and secrets in unkeyed free text under non-secret names.
- The per-device concurrency limits (section 6) and the error classes (section 7) are applied here; the retry loop is in the driver (section 7).

## 4. Protocols: sans-IO call flows

Every finite call is a generator that yields `Request`s and receives `Response`s, the same pattern as `httpx.Auth.auth_flow`. A small sync driver and a small async driver (`_runtime/driver.py`: `run_sync`, `run_async`) run any flow, wrap streaming results (section 3) and apply the retry policy (section 7), so no protocol logic exists twice.

```python
CallFlow = Generator[Request, Response, T]

# one flow function per binding type, registered with register_binding(); flow_for(op, params, state) dispatches
def flow(op: Operation[B], params: Model | None, state: DeviceState) -> CallFlow[Any]: ...
```

`Operation` (in `_protocols/base.py`) carries `api: ApiInfo`, `id`, `binding` (family-specific wire data), `params` model type, `result` type, `access`, `effect`, `since`, `write`, `applicability`, `errors` and `support`. The binding type selects the protocol. `Family` is an enum of the families; each protocol module registers its binding type.

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

`select_version(advertised, major, known_versions)` is pure and not cached; it returns `None` when the device offers no version of the class's major, which becomes `NotSupported`. On a JSON-RPC error 2100 (version not supported), any error the API documents as `kind: unsupported` (for example 2000 in `stream_profiles` and the `*_guard` APIs), or a 404 from an endpoint that negotiated before, the flow calls `state.forget_advertised_versions(key)` and re-raises.

`DeviceState` (`_protocols/state.py`) caches only facts about the device (advertised versions per endpoint, discovery probe results, identity), never per-class selections. Selection is a pure function of those facts and the calling class's major version, so a v1 and a v2 class for the same API cannot interfere. Concurrency control is by tokens:

- `token(key)` is taken before the I/O that produces a fact; `set(key, value, token)` stores it only if neither `clear()` nor `forget(key)` happened since. A probe that was in flight when its fact was invalidated cannot put the stale fact back.
- `set_or_clear(key, value, token, stale)` compares, optionally clears everything, and stores in one atomic step (used to drop all facts when `identity()` reports different firmware).
- `forget(key)` drops one fact and invalidates its outstanding tokens; `clear()` drops everything. All checks run under one `threading.Lock` that is never held across I/O or an `await`.
- `Device.refresh()` calls `clear()`.

Negotiation is a per-API strategy on the JSON-RPC binding: `GetSupportedVersions(key, auth)` (version list under `data[key]`), `FixedVersion(version)` (API has no negotiation; the spec states the version) and `NoVersion()` (no `apiVersion` field). A strategy based on `api_discovery` (version from `getApiList`) is *planned*.

### Protocol families

| Family | Module | Owns |
|---|---|---|
| JSON-RPC CGI (`jsonrpc`) | `jsonrpc` | `{apiVersion, method, params}` envelope (`params` or top-level placement); `getSupportedVersions` / fixed / no-version negotiation; `{error:{code,message}}` → `ApiError` (body first, then status); multipart uploads with a JSON part |
| Device Configuration REST (`dca`) | `dca` | `/config/rest/<api>/<ver>/…` path templates with percent-encoded path parameters; `{data}` request body; `{status, data}` / `{status:"error", error}`; entity get/set/add/remove/actions |
| Classic CGI (`cgi`) | `cgi` | query/form/multipart/raw-body encoding with per-argument placement, `yes/no` booleans, CSV lists, spread mappings, templated names, uploads; reply codecs `TextOk`, `TextKv`, `Text`, text lines, `Xml` (element mapping), `Binary` (media type and signature checks), `JsonReply`; `# Error:` / `# Request failed:` and XML error detection; stream replies. The generic `param.cgi` operations (`list`, `update`, `add`, `remove`) are ordinary `cgi` operations (`apis/parameter_management.py`). |
| VAPIX JSON service (`service_json`) | `service_json` | `POST /vapix/<svc>` with `{"<prefix>:<Op>": {...}}`; the bare reply message; JSON faults (`FaultCode` / `FaultSubCode`) → `ApiError` keyed by the subcode |
| SOAP (`soap`) | `soap`, `xmlmap` | SOAP 1.2 envelope and faults over `POST /vapix/services`, for services without a JSON form; request elements from `params` (`@name` attributes, `#text` for the text of an element that also has attributes), replies read with the same XML mapping as `cgi`, or returned as the raw reply element with `result: {x-xml: true}` |
| Plain REST (`rest`) | `rest` | non-framework REST APIs (AXIS Audio Manager Edge/Pro): path templates, JSON bodies, errors keyed by HTTP status |
| WebSocket sessions (`ws`, or session operations in any family) | `_runtime/ws`, `_runtime/ws_codecs` | handshake path and query, optional `wssession.cgi` token, ping heartbeat, setup requests and message codecs; see "Sessions" in section 3 |
| Streams (a reply mode of `cgi`) | `_streams`, `_runtime/driver` | decoders `bytes`, `mjpeg`, `lines` and the managed `StreamResult`; see "Streaming" in section 3 |
| RTSP URLs (`rtsp`, or operations in any family) | `rtsp` | URL building only: an `RtspUrl` with query arguments from the operation's params (booleans `1`/`0`, arrays comma-joined) and optional credentials in the URL (`include_credentials`). No network call. `Device.rtsp_url(MediaStream(...))` is the hand-written builder for `media.amp` parameters. |

`Family` also has a `param` member; it names the discovery kind for `param.cgi` properties, not a call family.

Families have documented exceptions (for example `capture-mode` puts arguments at the top level of the JSON-RPC envelope; some JSON-RPC APIs have no `getSupportedVersions`; classic CGIs accept XML or form request bodies). Bindings therefore carry declarative knobs, never code: envelope placement of arguments (`params` object or top level), negotiation strategy, per-operation endpoint override, request codec and content type (`json`, `form`, `query`, `xml`, `multipart`, `raw`), and response codec. An exception that the knobs cannot express is a protocol change and needs a human.

## 5. Generated code

One module per API spec (major version), containing models, an operation table and two classes. The format of the specs is in [spec-format.md](spec-format.md); this section describes the output. `python -m codegen generate` writes `src/ax_devil_device_api/apis/<module>.py`, `apis/__init__.py` and `docs/api_surface.txt`; `python -m codegen check` fails if any of them differs from a fresh generation. Each generated file starts with a "GENERATED, do not edit" header. An excerpt (`apis/mqtt_client.py`, from `specs/apis/network-video/mqtt-client.yaml`):

```python
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
- Responses ignore unknown fields and keep enum values newer than the generated `Literal` (new firmware may add both). Construction in Python rejects unknown fields and invalid enum values. Result types and fields tolerate new enum values the same way at any depth: scalars, lists, mappings (`dict[str, Literal]`), unions and combinations of them, and keep their top-level constraints (`minimum`, `pattern`, ...). `repr` and `str` render masked (`x-masked`) fields as `'*****'`, nested models included; the value itself stays readable on the attribute. A `const` field is not an enum: it generates `Annotated[Literal[...], CONST]` and stays strict in responses, so union variants are told apart by their discriminator.
- Public numeric inputs (connection, retry, request and heartbeat settings, upload size, RTSP and media stream parameters, numeric CLI flags) go through the shared validators in `_validate.py`: counts must be real `int`s, durations finite numbers, `bool` is always rejected, and the error is a `ConfigurationError` naming the setting.
- Request validation rejects NaN and infinite floats at any depth (JSON cannot carry them); responses are not affected.
- A request object passed to a method is revalidated at send time under the strict request rules, so edits made after construction (assignment, `model_copy(update=...)`) raise `ValidationError` locally. `from_current` is the one exception to "strict": it carries enum values newer than the generated code through from the device's response, remembers exactly those values, and send-time revalidation accepts them and no others (a typo is still rejected). The carried values are keyed by (model class, field, value), so a value seen in one place is not accepted in another field or in a same-named field of another model. Keyword arguments are revalidated like request objects: the completed params model is revalidated before sending, so a pre-built nested model edited after construction raises locally too.
- Wire names are `validation_alias`/`serialization_alias`, never `alias`, so type checkers show the Python names in constructors.
- Method signatures use `pydantic.MISSING` (re-exported as `ax_devil_device_api.MISSING`) as the "not given" default for flattened keyword arguments. It never appears in models or results.

Methods:

- Every method that makes a request takes `request_options: RequestOptions | None` (timeout, retry policy for this call). RTSP URL builders make no request and take none.
- Signature rule (deterministic, so the generator can apply it): an operation whose params include a nested model, or more than four fields, gets two overloads: flattened keyword arguments, or one positional `*Request` object (passing both, or more positional values than `positional` names, is a `TypeError`). Smaller operations, such as `parameter_management.update(parameters)` or `get_publisher(id)`, get one plain signature: path keys and the main argument positional, the rest keyword-only.
- Required read-only fields (`x-read-only` plus `required`) are required in responses only: a response without one raises `ResponseFormatError`, while the request model leaves it out (`None` on a model you build, never sent). In the models this is the `not_sent` default and `__response_required__`.
- Writes declare `write`: `replace` (fields left out return to defaults), `patch`, `create` or `delete`, shown in the docstring.
- Where a read result can be written back, the request model gets `from_current(result)`. It drops fields the device masks or that are read-only (from the spec), and sets "keep existing" flags where the API has them (MQTT `keepExistingPassword`). Blind round trips must never write a masked `*****` back: masked and read-only fields are dropped through nested models and lists, and a secret the creation call needs must be set on the request afterwards (the docstring names the masked paths). Read-only fields are omitted from every request at any depth even when supplied (`__read_only__`, applied by `to_wire`). Models hide input values in validation errors (`hide_input_in_errors`), so secrets never appear in them.
- Raw-body CGI operations can take the Content-Type per call through an `x-in: content_type` argument (for example `transmit_audio(audio, content_type="audio/G726-32")`).
- Streaming operations return a `StreamResult[T]` / `AsyncStreamResult[T]`, session operations a `Session` / `AsyncSession` context manager, RTSP operations an `RtspUrl` (section 3 and the families table).

Descriptors and naming:

- `Model`, `Operation`, `ApiInfo` and `ApiVersion` are runtime types in `_protocols/base.py`; the generator only emits data and signatures.
- One class per major version. The unsuffixed name (`mqtt_client`) is permanently the first major version generated; later incompatible majors get `_v2`, `_v3`. Regeneration never changes what an existing name means. DCA path versions map the same way.
- Python names are derived deterministically from spec ids and wire names, with an explicit collision rule and `x-python-name` overrides; `docs/api_surface.txt` makes every rename visible in review.
- Version applicability is finer than per operation. `since` (and `until`/`deprecated`) can sit on an operation, a parameter, a nested field or an enum value. Before sending, `check_applicability` rejects any *set* argument, field or enum value newer than the negotiated version with `NotSupported` (`.required` names the version). The spec's `requires` block is carried into `ApiInfo` (`requires_firmware`, `requires_application`, and the lifecycle `status`). `Device.supports()` answers `NO` when the firmware is known and older than `requires_firmware` (dotted numbers compared component by component), whether discovery matched, found nothing or was incomplete (a discovery `NO` stays `NO` when the firmware is unknown), and `UNKNOWN` when the firmware cannot be read (the identity is fetched once and cached, only for APIs that declare a minimum). `requires_application` is free text and informational; it is not checked.
- Each operation declares its `effect`: `read`, `write`, `action`, or `unknown`. It cannot be inferred from the HTTP method, because classic CGIs change state with GET. Retries and live tests depend on it; the generator warns on `unknown`.
- Error tables carry a `kind` per code (`access_denied`, `unavailable`, `invalid_argument`, `not_found`, `unsupported`, `internal`), which selects the error class (section 7); `kind` is optional on an `ErrorCode`.
- `apis/__init__.py` is generated: `Apis` / `AsyncApis` namespaces with one lazy, cached property per API, exposed as `device.apis`. `device.api(ApiClass)` returns the cached instance of one class.
- Support status is tracked per operation (`Operation.support`): `verified` (a live test passed, recording model and firmware), `docs-only` (every operation today), or `known-broken`. Recording `verified` from live runs is *planned*.

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
- cached facts are invalidated on evidence: JSON-RPC error 2100 (version not supported), an API's documented `unsupported` error, or a 404 from an endpoint that negotiated before, and `identity(refresh=True)` reporting different firmware. Not on timeouts.

Host or credential changes mean a new `Device`. Health checks are explicit (`identity(refresh=True)`); there are no background threads. Reconnect and backoff policy for whole sessions stays in the application.

Sharing. A sync `Device` may be shared between threads; an `AsyncDevice` between tasks of one event loop. Closing or reconfiguring concurrently with calls is not supported. Discovery probes and identity are coalesced per key with a lock (one in flight at a time). `DeviceState` uses generation tokens (section 4): a fact computed before `refresh()` is never stored after it. Cancelling a call releases its connection and concurrency slot; it does not undo a request the device already received.

Concurrency. Each device limits requests in flight (`max_concurrency`, default 4) and open streams and sessions (`max_streams`, default 2) separately, so a long download never blocks control calls such as PTZ. No fleet object: one `Device` per camera; fleets are application code (see `examples/01`).

Capabilities and discovery. `capabilities()` runs three probes (concurrently on `AsyncDevice`): classic `apidiscovery.cgi` (`if_challenged`), `/config/discover`, and the `param.cgi` `Properties.API` group. Two more probes run only when an API's discovery asks for them, because they need an administrator account: the installed ACAP applications (`/axis-cgi/applications/list.cgi`) and the web services listed by the Entry service (`GetServices` on `/vapix/services`). Successful probes are cached until invalidated; failed ones are reported in `Capabilities.errors` and retried on the next call. An API declares how it is recognised through an ordered list of discovery entries (spec-format.md, "Discovery entries"), and `supports(api)` returns an immutable `SupportResult(status, reason, errors, observed_at)`:

| Discovery kind | Listed when |
|---|---|
| `api_discovery` | `apidiscovery.cgi` lists the id (a different major version gives `NO`) |
| `dca` | `/config/discover` lists the API and path version |
| `param` | a `param.cgi` property exists, equals a value, or compares `>=` as a dotted number. Properties in `Properties.API` come from the capabilities probe; any other property gets its own lazy `properties:<name>` probe (one `param.cgi` list per declared property, cached, `Capabilities.property_groups` records what was queried; a leading `root.` is stripped). Scopes are merged independently, so a failed `Properties.API` probe does not discard a scope that worked, and each property is judged only against the probe that covers it. `capabilities()` stays lazy: it never runs property probes itself, but includes scoped results cached by earlier `supports()` calls, so `decide_support(api.INFO, capabilities())` agrees with `supports(api)`. A never-queried property is `UNKNOWN`, a queried and absent one is `NO`; an `ApiError` containing "getting param in group" counts as `NO`, any other error as `UNKNOWN` |
| `acap` | an application with that name (case-insensitive) is installed; running is not required |
| `service` | the Entry service lists the web service namespace (AXIS OS 5.60 and later); used for SOAP and service JSON APIs that API discovery does not list |

The first entry that matches gives `YES`. `NO` only when every probe that would list the API succeeded and none listed it (or a different major version was listed); `UNKNOWN` when a relevant probe failed or the API declares no discovery. Calls do not check support automatically; version negotiation raises `NotSupported` when it matters.

Configuration (`Device(host, *, ...)` keyword arguments, validated into a frozen `ConnectionConfig`; `Device.from_config` takes a ready one). `scheme` (default `https`), `port`, `base_path` (reverse proxy or VMS prefix; starts with `/`, no trailing `/`, no query or fragment, and no `.`, `..`, empty segments, trailing separators or backslashes at any percent-decoding layer (checked up to four layers, failing closed), so `%2f`, `%5c`, `%252e%252e` and the like cannot make normalisation leave the prefix; `Request` and RTSP paths reject dot segments and backslashes the same way), `proxy` (an `http`, `https` or `socks5` URL with a host; userinfo is redacted in `repr`) (a proxy failing the tunnel is `ConnectionFailed` with `request_sent=False`; a proxy together with the injected `transport` is a `ConfigurationError`, because httpx would route around the transport; SOCKS needs the `socks` extra), `verify` (bool, CA bundle path, or `SSLContext`) (a missing, unreadable or malformed CA bundle raises `ConfigurationError` naming the path when the transport is built; request-time TLS failures stay `TlsError`), `credentials` (`Credentials`, a `(user, password)` tuple, or `BearerToken` with a static or refreshing token), `timeout` (default 10 s; positive and finite, as is `RequestOptions.timeout`, where `None` keeps the device timeout and there is no way to disable timeouts), `retry`, `allow_http` (required for `scheme="http"`), `max_concurrency`, `max_streams`, `on_request`, `on_response`, and the low-level `transport` (an httpx transport).

Observability. Standard `logging` at DEBUG on the `ax_devil_device_api` logger (one line per request attempt), `on_request` (redacted request), `on_response` (structured record per attempt: api, operation, method, path, status, error, duration_ms, attempt); every attempt gets a record, including ones that fail with `AuthError` or any other library error, which are never retried). A response whose `Content-Type` names an unknown charset raises `ResponseFormatError` (error excerpts fall back to UTF-8). OpenTelemetry can instrument the underlying httpx client.

Testing. `ax_devil_device_api.testing.MockCamera` answers identity, API discovery, Device Configuration discovery, JSON-RPC (`getSupportedVersions` is answered automatically), REST and CGI routes (`identity`, `api_list`, `dca_apis`, `jsonrpc`, `rest`, `cgi`, `route` for raw httpx handlers), injects transport failures (`fail`), records requests (`requests`, `calls(method)`) and hands out `device()` / `async_device()`, so users can test their own code without hardware. Unmatched requests get 404. `Device(transport=...)` remains the low-level seam. WebSocket sessions are tested with a fake network stream behind the same transport seam (`tests/unit/ws_fake.py`). See `examples/09_testing_your_code.py`.

## 7. Errors

```
DeviceError
├── ConfigurationError
├── TransportError (.request_sent)
│   ├── RequestTimeout: ConnectTimeout*, ReadTimeout, WriteTimeout, PoolTimeout*
│   ├── TlsError*
│   └── ConnectionFailed            (* = request never sent; always safe to retry)
├── SessionClosed(code, reason)     a WebSocket session ended normally; raised by receive()/request() only
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
└── Unavailable                     category: catch both 503 and documented busy codes (an HTTP 503 API error envelope without a documented kind is also unavailable)
```

Errors without a code. Some classic CGIs report a failure only as text (`Error: account user name.` with HTTP 200). A spec's error table can match such a message with `message` (the whole text) or `message_prefix` (its start); whitespace is collapsed, a trailing full stop is ignored and the match is case-sensitive. The raised `ApiError` has `code=None` and takes `kind` and `description` from the entry; an unmatched failure is still an `ApiError` carrying the message. Message matching applies wherever the runtime has a message (cgi plain-text and JSON error replies, SOAP faults, JSON-RPC errors).

HTTP 401. A 401 is an `AuthError`, raised before the body is read. The one exception is an operation with `auth: if_challenged` (sent without credentials first): a 401 without a `WWW-Authenticate` challenge is not a request for credentials but an answer of the API, so it reaches the CGI decoder and typically becomes an `ApiAccessDenied` or a matched message error (`pwdgrp.cgi` before the first administrator exists). A 401 with a challenge, and every 401 of an operation that sends credentials from the start, stays an `AuthError`.

Retries (`RetryPolicy`, per device, overridable per call through `RequestOptions(retry=...)`; `NO_RETRY` disables them): requests that were never sent are retried for every operation (default 2 attempts in total, backoff 0.2 s doubling up to 5 s). Read timeouts and dropped connections are retried only with `retry_reads=True` and only for `effect: read` with a replayable body. Writes and actions are never resent after the request may have arrived; HTTP and API errors are never retried. Opening a stream follows the same rules (unsent failures are retried, within the attempt budget); once a stream's response has started it is never restarted, and sessions are never restarted. `backoff` and `max_backoff` must not be negative.

## 8. Specs, patches and the generator

The spec format is documented in [spec-format.md](spec-format.md) (one YAML file per API and major version, maps keyed by id, wire names in the spec and Python names derived, nothing implicit about effects, write semantics or masked fields). The JSON Schema is `specs/schema.json`. The generator is `codegen/`:

- `python -m codegen validate`: every spec against the schema, after patches.
- `python -m codegen generate [--only ID ...] [--all]`: write `apis/*.py`, `apis/__init__.py` and `docs/api_surface.txt`. A full run also deletes generated modules no spec produces any more; `--only` never deletes. Specs whose `provenance.curated` is not true are skipped unless `--all` is given.
- `python -m codegen check`: regenerate in memory and fail if the committed outputs differ. CI runs this.
- `codegen/migrate_v1.py` and `migrate_streams.py` are the one-off migrations that produced the first specs from the 0.x corpus.

Patches live in `specs/patches/<id>.yaml` and come in two kinds. The loader and applier (`codegen/patches.py`) exist; no patch has been committed yet because none has been verified on a device.

- **Corrections** apply to every device: the docs are wrong. Each is an explicit operation (RFC 6902 style: `add`, `replace`, `remove` at a JSON Pointer path) (array indices follow RFC 6902: canonical non-negative integers, `<=` the length for `add`, `<` the length otherwise, `-` only for `add`; anything else is a spec error) with an `expect` field holding the value or hash the patch was written against, plus `evidence` (model, firmware, date, what was observed). RFC 7396 merge patches are not used because they cannot set an explicit `null` and replace arrays wholesale.
- **Variants** apply only to matching devices: `when: {firmware: "<12.0", model: "Q1656*"}`, then the same operation list. A variant is meant to become descriptor data checked at runtime against the device's identity, never a universal change: a field missing on one camera is a variant, not a correction. The loader currently ignores variants with a warning (*generator support planned*).

When the base spec changes under a patch, applying the patch compares each operation's `expect` with the current base value, so `validate`, `generate` and `check` all fail with a `PatchError`. A mismatch is a conflict that needs a human. Ancestor-path conflict detection (a patch on `/operations/foo/params/bar` when `/operations/foo` was replaced) is *planned*; today such a patch fails because its path no longer exists.

For DCA APIs, importing the device-served `openapi.json` / model to report differences from the spec (`codegen import-dca --device <host>`) is *planned*. The device is more authoritative than the docs.

## 9. Features and CLI

`features/` is hand-written convenience built only on generated APIs and the public `Device` runtime (layer rule 4):

- `snapshot(dev, **options)` / `async_snapshot`: one JPEG via the generated `video_streaming.get_jpeg`.
- `device_summary(dev)` / `async_device_summary`: identity plus discovery results as a `DeviceSummary` (failed probes are listed, not raised).
- `api_support(dev)` / `supported_apis(dev)` (and async variants): `SupportResult` for every generated API, or the names the device positively offers. All results come from one capability snapshot (`Device.supports_many`), so a failing probe runs once, not once per API.
- `load_all()`, `load_api(name)`, `api_names()` (`features/registry.py`): the generated API modules as `ApiEntry` values (name, `ApiInfo`, operations, sync and async classes).

`cli/` is the `ax-devil` command (argparse, no extra dependencies; entry point `ax_devil_device_api.cli:main`). Output is JSON on stdout, errors are JSON on stderr with exit code 1 (device or OS error) or 2 (usage or invalid parameters). Connection options (`--host`, `--user`, `--password`, `--port`, `--http`, `--insecure`, `--ca-bundle`, `--base-path`, `--timeout`) default to `$AX_DEVIL_HOST`, `$AX_DEVIL_USER` / `$CAM_USER` and `$AX_DEVIL_PASSWORD` / `$CAM_PASS`. Commands:

| Command | Needs a device | What it does |
|---|---|---|
| `apis` | no (`--supported`: yes) | list generated APIs with family and operation count |
| `ops <api>` | no | list an API's operations, access level, effect and parameters |
| `call <api> <op> [key=value ...]` | yes | run any operation; values are parsed as JSON, else strings; `--json` for an object or `@file`; binary results and streams go to `--output FILE` (`-` is stdout, refused on a terminal; created or truncated even when the stream is empty or `--limit 0`; the decoder of the stream operation decides whether it is binary); `--limit N` stops a stream |
| `snapshot` | yes | write a JPEG to `--output` or raw to stdout |
| `summary` | yes | `device_summary` as JSON |
| `supported` | yes | `SupportResult` of every generated API |

Because `apis`, `ops` and `call` read the generated modules, a new spec is available on the command line as soon as it is generated; there is no hand-written command per API.

## 10. Tests

All run with `uv run pytest`; `uv run pyright` type-checks `src` and `tests`.

1. Unit tests (`tests/unit/`): `_http` (transport, auth including the 0.x security cases, retries, uploads and the upload preflight), the protocol families, the driver, capabilities and support decisions, version selection, models and error mapping, streams and decoders, WebSocket sessions against a fake network stream, RTSP URLs, `MockCamera`, features, the CLI, and round trips through reference APIs. Async tests use `anyio`.
2. Contract tests (`tests/contract/`): every `examples` entry of every spec is run through the generated module over fake transports. The built request must match the documented request, and the documented response must parse into the result model (or raise the documented error). Streams, sessions and RTSP URL builders have their own example conventions (spec-format.md).
3. Codegen tests (`tests/codegen/`): bindings, rendering, staleness checks, migrations, and the behaviours added with the runtime pass: message-matched errors, required read-only fields, `x-in: content_type`, SOAP `#text` and raw results, `{n}` placeholders in fixed `query` / `url_query` values, upload and cgi contract examples.
4. Example tests (`tests/examples/`): each script in `examples/` is imported and run against a `MockCamera` or fake WebSocket camera, so the examples cannot rot. No real network.

Planned: live conformance (`pytest -m live --device …`) runs `effect: read` operations of APIs that `supports()` reports as `YES`; `unknown`-effect operations are skipped. Results are recorded per operation with model and firmware and feed the support status in section 5. Failures become correction or variant patches.

CI (`.github/workflows/publish.yml`, Python 3.11 to 3.13): `uv sync --locked`, `python -m codegen check`, `ruff check .`, `pyright`, `pytest`; a tag builds and publishes. Planned: schema validation as its own step and import-linter.

## 11. Maintenance loop

1. An external monitor (not in this repository) detects changed doc pages and lists the specs citing them.
2. The agent edits `specs/apis/**` by hand, citing source anchors, then runs `python -m codegen generate` and commits the regenerated outputs (`apis/`, `docs/api_surface.txt`) in the same PR.
3. CI runs `codegen check` (regenerating must reproduce the committed outputs exactly, which catches hand edits to generated files), ruff, pyright and the tests, including the contract tests of the changed examples.
4. The PR shows the spec diff and the `docs/api_surface.txt` diff. Patch conflicts block merging.

The agent's hand edits are limited to `specs/apis/**`; everything else it commits is generator output. A change needing a new family, binding knob, codec or envelope behaviour is escalated to a human; the agent never edits `_http`, `_protocols`, `_runtime` or `codegen`.

## 12. Status and remaining work

Done: `_http`, `errors`, `Device`/`AsyncDevice`, sync and async drivers, the `jsonrpc`, `dca`, `cgi`, `service_json`, `soap` and `rest` protocols, capabilities and support checks (including ACAP and Entry service discovery), streams, uploads, WebSocket sessions, RTSP URL builders, `testing.MockCamera`, the spec format, `codegen`, generated modules for all curated specs, contract tests, `features/`, the CLI.

Remaining:

1. Live conformance runs against real devices and recording `verified` support.
2. `specs/patches/` content from those runs, and variant handling in the generator.
3. `import-linter` contract for the layer rules.
4. A JSON-RPC negotiation strategy based on `api_discovery`.
5. The unsupported items listed under Scope statements (`BLOCKED` entries in the specs). The SOAP-related ones are resolved (`action_service.add_action_rule` and `event_service.get_event_instances`, using `#text` and raw reply elements).
6. Build an SSLContext from a string `verify` path internally before httpx drops string support.

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
| Session liveness | Ping-based `Heartbeat` (the APIs define no application heartbeat); silence alone is never an error; `Heartbeat(None)` disables it. |
| Observability | stdlib logging + `on_request` + `on_response`. |
| User testing | `testing.MockCamera` on top of transport injection. |
| Auth and routing | `BearerToken`, `base_path`, `proxy`; ACAP routes are ordinary absolute paths under the base path. |
| Uploads | One argument type, `UploadSource` (`bytes`, `Path` or `Upload(stream, size)`), for cgi and jsonrpc; always sent with `Content-Length`; content up to 8 MiB is read into memory so it stays replayable; larger content is streamed and, being non-replayable, is preceded by a credential-priming `GET /axis-cgi/usergroup.cgi`. |
| CGI argument placement | `encoding` query/form/multipart/body plus per-argument `x-in` (`query`, `form`, `body`, `content_type`); `{name}` placeholders in paths and wire names are filled from required scalar arguments; bare query keys are `null` values; fixed `query` / `url_query` values may contain `{name}` placeholders filled from required scalar arguments. |
| RTSP | URLs only; no RTSP client, no session commands, no RTSP-over-HTTP. |
| Service APIs | `service_json` over SOAP when both exist; discovery of service APIs through the Entry service namespace list. |
| CLI | argparse, JSON output, generic `call` driven by the generated modules; hand-written commands only for `snapshot`, `summary`, `supported`. |

## 14. Dependencies

Tooling is `uv` (`uv sync`, `uv run pytest`, `uv run pyright`). Python 3.11+ (3.10 reached end of life in October 2026).

- Runtime: `httpx`, `httpx-ws` (WebSocket sessions), `pydantic>=2`.
- Dev group: `pytest`, `anyio`, `pyright`, `ruff`, `pyyaml`, `jsonschema`, `types-pyyaml` (generator, schema validation and contract tests).
- The CLI uses only the standard library (`argparse`).
