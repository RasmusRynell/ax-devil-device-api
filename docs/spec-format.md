# Spec format v2

One YAML file per API (per major version) in `specs/apis/<section>/<id>.yaml`. The generator (`codegen/`) turns each file into one module in `src/ax_devil_device_api/apis/`, plus contract tests in `tests/contract/`. The JSON Schema is `specs/schema.json`; every spec must validate.

The format is designed for generation first, and for humans and agents editing it second:

- **Maps keyed by id, not lists**, for stable diffs and patch paths.
- **Wire names in the spec, Python names derived.** Python names are the snake_case form of wire names (`keepExistingPassword` -> `keep_existing_password`). Override with `x-python-name` only to resolve a collision or a keyword.
- **Nothing implicit.** Effects, write semantics, required response fields and masked fields are stated, because they cannot be inferred safely.

The [design document](design.md) explains how the runtime uses each field.

## Top level

```yaml
format: 2
id: mqtt-client                  # stable; the API discovery id where one exists
name: MQTT client API
summary: Configure, activate and query the device's MQTT client.
section: network-video           # docs section; also the directory name
family: jsonrpc                  # jsonrpc | dca | cgi | service_json | soap | rest | ws | rtsp (ws and rtsp: sessions and URLs only)
status: released                 # released | beta | alpha | deprecated
python:
  module: mqtt_client            # file and dev.apis attribute; unsuffixed = first major, later majors _v2
  class: MqttClient              # -> MqttClientApi and AsyncMqttClientApi; a trailing `Api` is dropped (warning)
docs: [https://developer.axis.com/vapix/network-video/mqtt-client-api/]
access: admin                    # default access level for operations
discovery:                       # how Device.supports() recognizes the API; tried in order
  - api_discovery: mqtt-client
  - dca: {api: analytics-mqtt, version: v1}
  - param: {name: Properties.API.HTTP.Version, value: "3"}   # outside Properties.API: probed lazily per property
  - param: {name: Properties.EmbeddedDevelopment.Version, value: "1.20", compare: ">="}
  - acap: {name: loiteringguard}
  - service: {namespace: "http://www.axis.com/vapix/ws/event1"}
requires: {firmware: "11.5", application: null}   # optional: minimum AXIS OS version (enforced by supports()); application is informational
binding: {...}                   # family-specific, below
errors: {...}                    # API-wide error codes, below
types: {...}                     # named schemas, below
operations: {...}                # below
sources: [...]                   # doc pages, with content hashes (change monitoring)
provenance: {...}                # completeness, open questions, verification
```

### Discovery entries

Entries are alternatives (any-of): the first one that matches makes `Device.supports()` answer `YES`. Each entry must therefore identify the API on its own. Do not list a generic prerequisite such as `Properties.API.HTTP.Version=3` next to API-specific entries; it matches every device with VAPIX HTTP v3 and would turn the whole list into "yes". Use such a marker only as the sole entry of a core API that the documentation defines by it.

- `api_discovery: <id>`: listed by API discovery (`apidiscovery.cgi`).
- `dca: {api, version}`: listed by `/config/discover`.
- `param: {name, value, compare}`: a `param.cgi` property. `value` is the decoded value without the surrounding quotes `param.cgi` may add (`yes`, not `"yes"`). Without `value` the property only has to exist. `compare` is `"=="` (default) or `">="`; `">="` compares dotted numbers component by component (`1.20` >= `1.9`), and a value that is not a dotted number never matches.
- `acap: {name}`: an ACAP application whose name appears (the `Name` attribute, read as `name` too, compared case-insensitively) in `/axis-cgi/applications/list.cgi`. Installed is enough; the application need not be running. The list needs an administrator account, so without one the answer is `UNKNOWN`, not `NO`.
- `service: {namespace}`: the web service namespace is listed by the Entry service (`GetServices` on `/vapix/services`, AXIS OS 5.60 and later). Use it for service APIs (SOAP, service JSON) that have no entry in API discovery. The probe runs only when an API asks for it, needs the same account as the service calls and answers `UNKNOWN` when it fails.

## Bindings

The `binding` block holds what all operations share. Operations add or override fields under their own `binding`.

`jsonrpc`:

```yaml
binding:
  path: /axis-cgi/mqtt/client.cgi
  major: 1
  versions: ["1.0", "1.1"]                 # every documented version of this major
  negotiation: {get_supported_versions: {key: apiVersions}}   # or {fixed: "1.0"} or none
  params_placement: params                  # or top_level (arguments merged into the envelope)
# operation:
  binding: {method: configureClient}        # optional: path, auth, timeout
  binding: {method: uploadOverlayImage, path: /axis-cgi/uploadoverlayimage.cgi, multipart: {json_part: json}}
                                            # multipart upload method, see "Uploads" below
```

`dca`:

```yaml
binding:
  root: /config/rest/analytics-mqtt/v1
# operation:
  binding: {method: POST, path: /publishers, body: object}   # path relative to root; {key} placeholders
                                                              # body: none | object | value (+ body_field)
  binding: {method: GET, path: '/topics/{topic}', key_styles: {topic: dots_to_slashes}}
                                                              # key_styles: per placeholder, `dots_to_slashes` writes
                                                              # a dotted key as nested segments (a.b -> a/b); `path` keeps the
                                                              # `/` of a nested path (a/b stays two segments); default `segment`
                                                              # (one encoded segment). Empty, `.` and `..` segments are rejected.
```

`cgi`:

```yaml
binding:
  path: /axis-cgi/param.cgi
# operation:
  binding:
    method: GET                       # GET | POST
    query: {action: list}             # fixed arguments
    encoding: query                   # query | form | multipart | body (see "CGI arguments, bodies and uploads")
    accept: text/plain
    reply: {text_kv: {strip_prefix: "root."}}   # text_ok | text | text_kv | xml | binary | json
    stream: false
```

Reply codecs: `text_ok` (body must be `OK`), `text`, `text_kv` (`key=value` lines; optional `strip_prefix`), `text_lines` (the non-blank lines as `list[str]`; optional `skip`, the number of leading lines to drop), `xml` (optional `error_elements`; a reply with several top-level elements, as in a listing of `<entry .../>` lines, is wrapped in a synthetic `fragment` root; only a body that is a sequence of elements, with at most whitespace, comments or processing instructions between them, is wrapped, so a text error such as `Error: camera not found` is still reported as an error), `binary` (optional `media_types`, `signatures` as hex strings), `json`, `stream` (streamed body, see below).

`text_lines` is for replies that are lists rather than `key=value` maps. The result is `{type: array, items: {type: string}}`; plain-text error detection still applies:

```yaml
binding: {reply: {text_lines: {skip: 1}}}   # skips the header "Preset Positions for camera 1"
result: {type: array, items: {type: string}}   # ["presetposno1=Home", "presetposno2=Door"]
```

`service_json` (Axis service APIs spoken as JSON: `POST /vapix/<service>` with a body of one key, the qualified operation name):

```yaml
binding:
  path: /vapix/axast                         # service endpoint
# operation:
  binding: {operation: "axast:PerformSpeakerTest"}   # the single body key; `path` overrides the endpoint
```

The body is `{"<operation>": {...params...}}` and the reply is the bare message object (an empty body means `{}`). Faults come with HTTP 400 or 500 as `{Fault, FaultCode, FaultSubCode, FaultReason, FaultMsg}`, so `errors` are keyed by that code: `FaultSubCode` when present, otherwise `FaultCode`, as the string the device sends (`axast:DeviceNotCalibrated`, `ter:InvalidArgs`). A documented triple such as `env:Sender/ter:InvalidArgs/ter:TooManyItems` is keyed by its last member, `ter:TooManyItems`. `params` is an object schema (the message fields, wire names as sent), `result` an object type for the reply message. Examples use `request: {params: {...}}` (the value of the single key) and `response: {data: {...}}` or `{error: {code, message}}`.

`soap` (SOAP 1.2 over `POST /vapix/services`):

```yaml
binding:
  namespace: http://www.axis.com/vapix/ws/event1     # default request namespace; `path` defaults to /vapix/services
# operation:
  binding:
    action: http://www.axis.com/vapix/ws/event1/GetEventInstances
    element: GetEventInstances                       # local name of the request element
    namespace: http://www.axis.com/vapix/ws/light    # optional: overrides the API-level namespace
    namespaces: {acert: "http://www.axis.com/vapix/ws/cert"}   # prefix -> URI; merged over the API-level map
```

`params` fields become child elements of the request element, in field order, in the request element's namespace: the property key is the element name (local name, no prefix) unless it is a prefixed name, below. A key starting with `@` is an attribute of its parent (`"@token": {type: string}` -> `token="..."`; the Python name is derived without the `@`, so set `x-python-name` if an element of the same name exists). The key `#text` is the text of its parent, so an element can have attributes and text: `TopicExpression: {"@Dialect": ..., "#text": "tns1:Device//."}` -> `<TopicExpression Dialect="...">tns1:Device//.</TopicExpression>` (the Python name is `text`; set `x-python-name` for a better one). For the same type to be read from a reply, annotate the properties with `x-xml: {attribute: Dialect}` and `x-xml: text`. Scalars are text (`true`/`false` for booleans), arrays repeat the element, nested objects nest. The `result` must be an object type; it is read from the first element inside the SOAP body with the same `x-xml` mapping as XML replies of `cgi` (see below), with one difference: an unannotated scalar property is the text of the child element of that name, not an attribute (use `x-xml: {attribute: name}` for attributes). `x-xml: {root: ...}` on the result type is relative to the reply element (for example `GetEventInstancesResponse`). `result: {x-xml: true}` returns the reply element itself (`xml.etree.ElementTree.Element`), for replies with dynamic content such as the event topic tree of `GetEventInstances`; a fault is still raised as an error. Without a `result` the reply is ignored. Faults are keyed by their subcode strings, innermost first (`ter:InvalidArgs`, then the code value `env:Sender`).

Prefixed names. Some requests mix namespaces (`<acert:Id>` under a request element in another namespace). A property key, or an attribute key after the `@`, may carry a prefix: `acert:Id`, `@acert:flag`. Every prefix must be declared in `binding.namespaces` (API level and operation level, merged); `codegen` rejects undeclared prefixes and the reserved `env`, `xml` and `xmlns`. The request element declares all of them. The Python name comes from the local name (`acert:Id` -> `id`; use `x-python-name` on a clash), and replies are read by local name, so a result property `acert:Id` matches `<Id>` in any namespace. Empty reply elements (`<Size/>`) are dropped for fields that cannot hold an empty string, as for XML replies of `cgi`.

`rest` (plain REST/JSON, no envelope):

```yaml
binding:
  root: /vapix/aam-edge/api                  # prefix of every operation path
# operation:
  binding:
    method: PATCH                            # GET | POST | PUT | PATCH | DELETE
    path: /v1.1/volumeControllers/{volumeControllerId}   # relative to root; {key} placeholders
    body: object                             # none (default) | object | value (+ body_field)
    query: [filter]                          # params fields sent as query arguments when set
```

`{key}` placeholders name required `params` fields and are positional arguments, as in `dca`. `body: object` sends the remaining params as one JSON object, `body: value` with `body_field: body` sends the value of that one field as the whole body. Failures are signalled by the HTTP status, so `errors` are keyed by the integer status (`404: {description: Not found, kind: not_found}`); other failures use the generic HTTP errors, and 401 is always an authentication error.

Every binding may set `auth` (`required`, `anonymous`, `if_challenged`) and `timeout` (seconds). An operation that the docs list as anonymous or pre-authentication (`access: anonymous`) sets `auth: if_challenged`, so no stale credentials are sent first; for a `jsonrpc` API also on the version negotiation (`negotiation: {get_supported_versions: {key: apiVersions, auth: if_challenged}}`) and, when every operation is anonymous, on the API-level `binding`.

### Streamed replies (cgi)

`reply: stream` (or `reply: {stream: {decoder: mjpeg}}`) makes the operation return a `StreamResult` (`AsyncStreamResult` on the async API) instead of a value. The body is not read up front; use the result as a context manager and iterate it. Leaving the `with` block closes the connection. It counts against the device's `max_streams`, not `max_concurrency`.

```yaml
operations:
  mjpeg:
    effect: read
    binding: {path: /axis-cgi/mjpg/video.cgi, reply: {stream: {decoder: mjpeg}}}
    params: {type: object, properties: {resolution: {type: string}, fps: {type: integer}}}
  monitor_ports:
    binding: {path: /axis-cgi/io/port.cgi, query: {monitor: all}, reply: {stream: {decoder: lines, encoding: utf-8}}}
  download:
    binding: {path: /axis-cgi/media.cgi, reply: stream}          # decoder defaults to bytes
```

| `decoder` | Items | Use |
|---|---|---|
| `bytes` (default) | `bytes` chunks | MP4/Matroska/audio, any binary body |
| `mjpeg` | `Part` (`headers`, `body`, `content_type`) | `multipart/x-mixed-replace`, one JPEG per part; a plain `image/jpeg` answer raises `ResponseFormatError` |
| `lines` | `str`, one per line | line-oriented text streams. On a `multipart/x-mixed-replace` (or `multipart/mixed`) answer, such as `port.cgi?monitor=`, the lines of the part bodies are returned: boundaries and part headers are consumed and blank lines (the keep-alive parts) are dropped |

A stream operation has no `result`. It may have `examples` (see "Examples of streams, sessions and RTSP URLs"). Non-2xx answers are errors raised before the result is returned. `effect` is usually `read`. Request bodies of POST streams (audio transmit) belong to the upload bindings.

### WebSocket sessions (`ws`, or any family)

A session operation opens a WebSocket and returns a context manager: `Session` on `Device`-bound APIs (`with dev.apis.x.connect(...) as session:`), `AsyncSession` on `AsyncDevice` (`async with`). It carries the handshake, keep-alive (`heartbeat=`), authentication (`use_token=True` uses `wssession.cgi`) and gap tracking of `Device.connect_session`; see the design document, section 3 ("Sessions"). Use `family: ws` for an API that is only sessions, or put the operation in any other family.

```yaml
family: ws
operations:
  connect:
    summary: Stream events.
    effect: read
    binding:
      session:
        path: /vapix/ws-data-stream
        query: {sources: events}        # fixed handshake query
        codec: events                   # events | datahub | raw (default raw)
        setup: events                   # optional: events | datahub | none; defaults from the codec
```

- `codec` selects the message format in `_runtime/ws_codecs.py`: `events` (event streaming, `events:notify` -> `EventNotification`), `datahub` (Device Data Hub, JSON-RPC 2.0, `TopicSample`) or `raw` (frames pass through; `bytes` stay `bytes`, text stays `str`, no request/response).
- `setup` turns the `connect` arguments into the requests sent right after the handshake and decides what `connect` accepts: `events` adds `event_filter_list: Sequence[EventFilter | Mapping[str, str]] | None` (sends `events:configure` when given), `datahub` adds `subscriptions: Sequence[Mapping[str, Any]] | None` (one `data-hub_v1:subscribe` each; every entry is validated against the spec's `Subscription` type before it is sent), `none` adds nothing. A new codec or setup needs runtime code; escalate rather than inventing one.
- Every `connect` also takes `heartbeat: Heartbeat = DEFAULT_HEARTBEAT`, `use_token: bool = False` and `request_options`.
- A session path may contain `{placeholders}` (`/api/v1.2/audioSessions/{audioSessionId}/ws/recv`). `params` must then be exactly those fields, required scalars; they become the leading arguments of `connect` and are percent-encoded into the path. Otherwise a session operation has no `params`. It has no `result`. `EventFilter`, `Heartbeat`, `Session` and the other names the generated module imports are reserved as type names when it uses sessions. In-session requests (`events:configure`, `data-hub_v1:listTopics`) are not operations; call `session.request(method, params)`.

```python
with dev.apis.event_streaming_ws.connect([EventFilter(topic_filter="tns1:Device/tnsaxis:IO/VirtualPort")]) as session:
    for event in session.notifications():
        ...
```

### RTSP URLs (`rtsp`, or any family)

An RTSP operation builds an `RtspUrl` and makes no request (the library has no RTSP client). It is a plain method on both the sync and the async API. Use `family: rtsp` for an API that is only URLs, or put the operation in a `cgi`/`jsonrpc` API whose docs also describe an RTSP stream.

```yaml
operations:
  stream_with_events:
    summary: Live stream with event metadata.
    effect: read
    binding:
      rtsp:
        path: /axis-media/media.amp     # default
        port: 554                       # default
        query: {event: "on"}            # fixed arguments, first
    params:
      type: object
      required: [eventtopic]
      properties:
        eventtopic: {type: string}
        videocodec: {type: string, enum: [h264, h265]}
        audio: {type: boolean}          # sent as 1/0
    positional: [eventtopic]
```

The set `params` fields become query arguments in field order (wire names as given; booleans as `1`/`0`; arrays joined with commas); only scalars and arrays of scalars are allowed. The method also takes `port: int | None = None` (overrides the binding) and `include_credentials: bool = False` (adds the user name and password from the device's credentials to the URL; a bearer token cannot be used), so `port` and `include_credentials` are reserved argument names for these operations. `str(url)` includes credentials, `url.safe` and `repr(url)` do not. `Device.rtsp_url(MediaStream(...))` remains the hand-written builder for `media.amp` parameters with validation. An RTSP operation has no `result` and no `request_options`. RTSP methods on a stream that must be *driven* (GET_PARAMETER, replay `Range` headers) are out of scope; document them in `description`.

## CGI arguments, bodies and uploads

Every cgi operation sends its params fields as arguments. `encoding` says where they go by default:

| `encoding` | Default place of arguments | Body |
| --- | --- | --- |
| `query` (default) | URL query | none |
| `form` | URL-encoded form body (POST) | the arguments |
| `multipart` | text parts of a `multipart/form-data` body (POST) | the arguments plus the files |
| `body` | URL query | the one `x-in: body` argument, raw (POST) |

Fixed arguments:

```yaml
binding:
  query: {action: list, schemaversion: '1'}   # sent where arguments go by default (the body for form and multipart)
  url_query: {setparams: null}                # always in the URL; a null value is a bare key: ?setparams
```

- A value in `query` or `url_query` may contain `{name}` placeholders, filled from the required scalar params field `name` like the placeholders of names and paths (see "Templated names"): `query: {action: list, group: 'Image.I{n}.RateControl'}` with a required integer `n`. This makes reads of index-named groups typed (`list_rate_control(0)`), together with `strip_prefix: 'root.Image.I{n}.RateControl.'`.
- `schemaversion` is the version of the request and response format that the CGIs of the recording export, disk and similar APIs require (`schemaversion=1`). It is a fixed argument of the binding, not a params field: put it in `query` and the generated method never exposes it.
- A bare key (`?live-sum.json`, `?export-cnt&date=...`; the people counter and queue monitor docs write them this way) is a `null` value in `query` or `url_query`, and a params field with `x-style: flag` (true sends the key, false sends nothing). A key with an empty value (`live-sum.json: ''`) is sent as `live-sum.json=`. Bare keys only go in the URL.

### Where one argument goes: `x-in`

`x-in` on a params property overrides the default place for that argument: `query` (the URL), `form` (a body field; only with `form` or `multipart`), `body` (the raw body; only with `body`) or `content_type` (the Content-Type of the raw body; only with `body`, see "Raw request bodies"). This is how one POST mixes URL arguments and body fields:

```yaml
binding: {method: POST, encoding: form, url_query: {setparams: null}}   # POST /local/tvpc/.apioperator?setparams&date=...
params:
  type: object
  properties:
    date: {type: string, x-in: query}            # in the URL
    values: {type: object, additionalProperties: {type: string}}   # spread into the form body
```

### Path arguments

`{name}` in an operation's `binding.path` is filled from the required scalar params field `name` (Python or wire name), percent-encoded. These arguments are positional (like DCA path keys) and are not sent as query arguments. Use an enum when the path has a closed set of names:

```yaml
get_push_config:
  binding: {path: '/local/fflprapp/{endpoint}.cgi', reply: xml}   # endpoint: cloud | cloud2 | cloud3
  params:
    type: object
    required: [endpoint]
    properties: {endpoint: {type: string, enum: [cloud, cloud2, cloud3]}}
```

### Templated names

A params or result property name may contain `{name}`. It is filled from the required scalar params field `name`, which is then an index argument and is not sent itself:

```yaml
set_image:
  params:
    type: object
    required: [n, 'Image.I{n}.Name']
    properties:
      n: {type: integer}                                             # set_image(2, name="Front")
      'Image.I{n}.Name': {type: string, x-python-name: name}         # sent as Image.I2.Name=Front
get_image:
  binding: {query: {action: list}, reply: {text_kv: {strip_prefix: 'root.Image.I{n}.'}}}   # strip_prefix may use it too
  params: {type: object, required: [n], properties: {n: {type: integer}}}
  result: {$ref: '#/types/Image'}      # fields named Name, Rotation...; or full names like 'Image.I{n}.Name' (text_kv replies)
```

The Python name of a templated property is derived as usual (`Image.I{n}.Name` -> `image_i_n_name`); set `x-python-name` for a readable one. Templated result names work for `text_kv` replies.

### Raw request bodies

`encoding: body` sends one argument, marked `x-in: body`, as the whole POST body with `content_type`. A `string` is sent as UTF-8, `format: binary` as bytes, and an object or array as JSON. The other arguments go in the URL.

The content type can be chosen per call: one optional string argument (usually an enum) marked `x-in: content_type` is not sent as an argument, and its value, when given, becomes the Content-Type of the body. It wins over the `Upload.content_type`, the `x-upload` content type and `binding.content_type`, so `binding.content_type` may be left out when every call has one of these. This is how `transmit_audio(audio, content_type="audio/G726-32")` picks the codec.

```yaml
set_settings:
  binding: {method: POST, encoding: body, content_type: application/xml, reply: text_ok}
  params:
    type: object
    required: [configuration]
    properties: {configuration: {type: string, x-in: body, description: The <configuration> document.}}
```

### Uploads (cgi and jsonrpc)

A params property with `x-upload` is file content. Its generated type is `UploadSource`, and every upload argument in every API accepts the same three things:

- `bytes`: the content.
- a `pathlib.Path`: read from disk when the request is sent. A plain `str` is rejected because it is ambiguous.
- `Upload(stream, size, filename=None, content_type=None)` (from `ax_devil_device_api`): a binary stream and its exact byte count.

The file name of a multipart file part is the path's name for a `Path`; for `bytes` and `Upload` it is `Upload.filename`, then the `filename` of `x-upload`, then the part name. A content type is `Upload.content_type`, then the `content_type` of `x-upload`, then `application/octet-stream`. Requests always carry `Content-Length`. Content up to 8 MiB is read into memory and can be replayed after an authentication challenge. Larger content is streamed and cannot be replayed, so before sending it an operation that sends credentials from the first request (`auth: required`, the default) first verifies them with an authenticated `GET /axis-cgi/usergroup.cgi` every time; if that fails, the call raises `AuthError` without sending the body. Operations with `auth: if_challenged` or `anonymous` are not primed.

```yaml
x-upload: true                    # part name = the property's wire name, application/octet-stream
x-upload: {part: file, filename: clip.au, content_type: audio/basic}   # all optional
```

`multipart` (cgi): files become file parts, other arguments text parts, `x-in: query` arguments and `url_query` go in the URL.

```yaml
upload_clip:
  binding: {method: POST, encoding: multipart, url_query: {action: upload, media: audio}, reply: text_ok}
  params:
    type: object
    required: [clip]
    properties:
      clip: {type: string, format: binary, x-upload: {part: file, content_type: audio/basic}}
      name: {type: string, x-in: query}
```

`body` (cgi): an upload argument with `x-in: body` is the raw body, streamed (for example a driver or a firmware file sent as POST data). Its `x-upload.content_type`, if any, overrides `content_type`.

`multipart` (jsonrpc): the call is a `multipart/form-data` POST. `json_part` names the part that carries the JSON-RPC envelope (`apiVersion`, `method`, `params`, as `application/json`), `params` leaves out the upload arguments, and the files follow as file parts. Leave `json_part` out for CGIs that take only files (the radar image upload); no `apiVersion` is negotiated or sent then.

```yaml
upload_overlay_image:      # overlay image: parts "json" (envelope) and "image" (file)
  binding: {method: uploadOverlayImage, path: /axis-cgi/uploadoverlayimage.cgi, multipart: {json_part: json}}
  params:
    type: object
    required: [image]
    properties:
      scaleToResolution: {type: boolean}
      image: {type: string, format: binary, x-upload: {part: image, content_type: image/bmp}}
upload_radar_image:        # parts: only the file (any part name)
  binding: {method: uploadRadarImage, path: /axis-cgi/radar/uploadradarimage.cgi, multipart: {}}
  params:
    type: object
    required: [image]
    properties: {image: {type: string, format: binary, x-upload: {part: image, content_type: image/png}}}
```

For the siren and light `uploadProfiles` shape (part `request` holds the envelope, part `file` holds a JSON file of profiles), use `json_part: request` and a `file` upload argument with `content_type: application/json`.

## XML replies (cgi, soap)

Most classic CGIs answer in XML. To return a model instead of a raw element, the result type says where each field lives. Names are local names; namespaces are ignored.

```yaml
types:
  ContinuousConfiguration:
    type: object
    properties:
      profile: {type: integer}                    # scalars default to the attribute of the same name
      diskid: {type: string}
      note: {type: string, x-xml: text}           # the element's own text
      label: {type: string, x-xml: {child: Label}}  # text of a child element
  ContinuousConfigurations:
    type: object
    x-xml: {root: continuousrecordingconfigurations}   # top-level type only: path from the document root
    properties:
      configurations:
        type: array
        items: {$ref: "#/types/ContinuousConfiguration"}
        x-xml: {path: continuousrecordingconfiguration}   # every match becomes an item
operations:
  list_continuous_configurations:
    binding:
      reply: {xml: {status_error: {attribute: result, value: ERROR, message: errormsg}}}
    result: {$ref: "#/types/ContinuousConfigurations"}
```

`xml` options:

- `error_elements` (default `[GeneralError]`): presence of the element means failure. Its `ErrorCode`/`ErrorDescription` children become the error code and message.
- `status_error`: an attribute value that means failure, e.g. `result="ERROR"` with the message in `errormsg`. Optionally `code` (the attribute carrying the code) and `path` (where to look).

Without an XML mapping on the result type, the operation returns the root element (`result: {x-xml: true}`).

`x-xml: {path: ...}` is a `/`-separated path of element names below the current element. A last segment `@name` reads that attribute of every matched element instead of the element's text, which is how a list of attribute values is mapped:

```yaml
values:
  type: array
  items: {type: string}
  x-xml: {path: 'Item/@value'}      # <Item value="a"/><Item value="b"/> -> ["a", "b"]; Items without the attribute are skipped
```

An optional array field whose elements are absent from the reply parses to `None` (the device did not report it), not `[]`; a required array stays `[]`. Empty strings (`<PoeClass/>`, `attr=""`) are dropped for fields that cannot hold a string.

## Errors

```yaml
errors:
  2104: {description: Invalid parameter value specified, kind: invalid_argument}
  2105: {description: Authorization failure, kind: access_denied}
```

`kind` is one of `access_denied`, `unavailable`, `invalid_argument`, `not_found`, `unsupported`, `internal`. It selects the error class at runtime, so set it whenever the meaning is clear. Operations may add their own `errors`. A key may also be a range of codes, `"9000-9999": {description: Reserved for license errors, kind: unavailable}`; an exact code wins over a range, and an operation's entry over the API's. A JSON-RPC error with `kind: unsupported` (like 2100, or 2000 where an API documents it so) also drops the cached API versions.

Some APIs report failures only as a message, with no code: classic CGIs answer `Error: account user name.` (HTTP 200). Such an error is matched by its text: give the entry `message` (the whole message) or `message_prefix` (its start, for messages that end with a variable part), and use any label as the key:

```yaml
errors:
  account_user_name: {description: The user name is missing or invalid, kind: invalid_argument, message: account user name.}
  malformed_action: {description: The user name does not fit the action, kind: invalid_argument, message_prefix: 'malformed action operation,'}
```

The match is case-sensitive; whitespace is collapsed and a trailing full stop is ignored on both sides. An entry sets `message` or `message_prefix`, not both. A message entry is only looked up by message (never by its label), the raised `ApiError` has `code=None` and takes `kind` and `description` from the entry, and a failure that matches no entry is still an `ApiError` with the message. Entries with a code are unaffected. Message matching applies wherever the runtime has a message (cgi plain-text and JSON error replies, SOAP faults, JSON-RPC errors).

HTTP 401. A 401 is an authentication failure and raises `AuthError` before the body is read. One exception exists for operations with `auth: if_challenged` (they are sent without credentials first): a 401 that carries no `WWW-Authenticate` challenge is not a request for credentials but an answer of the API, so a cgi operation reads its body for `Error:` lines as usual. `pwdgrp.cgi` uses this before the first administrator exists (`Error: initial admin user must be created first.`, HTTP 401). A 401 with a challenge, and every 401 of an operation that sends credentials from the start, stays an `AuthError`.

## Types

Named schemas, using a JSON Schema subset: `type`, `properties`, `required`, `items`, `enum`, `const`, `additionalProperties`, `minimum`, `maximum`, `minLength`, `maxLength`, `pattern`, `minItems`, `maxItems`, `default`, `description`, `since`, `$ref: "#/types/Name"`, `oneOf`. `const` generates `Annotated[Literal[...], CONST]` and stays strict in responses (unlike `enum`, which tolerates newer values); use `oneOf` with a `const` member for a documented sentinel, for example `oneOf: [{type: boolean}, {const: -1}]`.

- An `object` type becomes a `Model` class. Other types become type aliases (`Annotated[str, Field(...)]`, `Literal[...]`).
- `required` lists the fields that must be present. In request models they are required arguments. In response models a missing one raises `ResponseFormatError`, so list only what the device always returns.
- Optional fields become `X | None = None`.
- Extensions:
  - `x-nullable: [field, ...]`: may be sent as explicit `null` (JSON `null`; an empty element in SOAP).
  - `x-masked: [field, ...]`: masked by the device in responses (for example `*****`); dropped by round trips at any depth (through nested models and lists); also redacted by name in the `on_request` records of that operation only (never in other operations that reuse the name), shown as `'*****'` in `repr`, and, when it is the `body_field` of a `body: value` DCA/REST operation, it marks the body `sensitive` (the same happens for a field whose name looks like a secret, such as `password`), so `on_request` records show only `<redacted>` for that body. Mark every credential field, in request and response types and in inline operation `params`: passwords, passphrases, PINs and PUKs, pre-shared and private keys, SNMP communities, client secrets. A write-only secret is marked as well: dropping it from round trips is correct, because the device never returns it and `from_current` must not copy it.
  - `x-read-only: [field, ...]`: present in responses, never sent: omitted from request serialization at any depth, even when supplied. When a request type is shared with the response, read-only fields stay on the model but are not method arguments. A field that is also in `required` is required in responses only: a response without it raises `ResponseFormatError`, while a request model leaves it out (the attribute is `None` on a model you built yourself; type checkers still see the field type) and never sends it.
  - `x-python-name` on a property: overrides the derived name.
  - `x-style` on a property (cgi only): `plain`, `csv`, `axis_bool`, `spread`, `flag` (a boolean sent as the bare key when true).
  - `x-in` on a property (cgi only): `query`, `form` or `body`, where the argument goes (see "CGI arguments, bodies and uploads").
  - `x-upload` on a property (cgi and jsonrpc): the property is file content (`UploadSource`), sent as a file part or a raw body.

- `pattern` must work in pydantic's regex engine: lookaheads and lookbehinds (`(?=`, `(?!`, `(?<=`, `(?<!`) are rejected by `codegen validate`.
- `minItems`/`maxItems` on arrays become `Field(min_length=..., max_length=...)` (a point pair is an array of two numbers with both set to 2).
- `since: "1.9"` on a property (mainly result fields): the field was added in that API version. It is always generated optional (`X | None = None`, whatever `required` says) and its attribute docstring ends with "Available from API version 1.9.". The runtime does not drop it on older devices; the field is `None` when the device does not return it.

Enums are `Literal`s. Responses tolerate new values of the same type (also inside lists, mappings and unions), and requests reject them.

## Operations

```yaml
operations:
  configure_client:              # id = Python method name
    summary: Configure the MQTT client.
    description: ...             # optional, longer docstring text
    access: admin                # defaults to the API-level access
    effect: write                # read | write | action | unknown
    write: replace               # for effect write: replace | patch | create | delete
    since: "1.0"                 # optional; jsonrpc version gate
    binding: {method: configureClient}
    params:                      # object schema, or {$ref: "#/types/Name"}; omit for no arguments
      $ref: "#/types/ConfigureClientRequest"
    positional: []               # argument names taken positionally (small operations only)
    result: {$ref: "#/types/ClientStatus"}     # omit for no result
    round_trip:                  # optional: generate Request.from_current(result_type)
      from: ClientConfig
      set: {keepExistingPassword: true}
    since_fields: {"params.min": "1.2"}        # field-level version gates (dotted wire paths)
    errors: {...}
    examples:
      - title: Get the MQTT client status
        request: {params: {}}                  # jsonrpc: params; dca: {path, body}; cgi: {query} or {form}
        response: {data: {...}}                # jsonrpc: data or error; dca: status + body; cgi: status + text
        source: https://...#anchor
        x-contract: {template: true}   # optional: the example is a syntax template, not a literal exchange
    support: docs-only           # docs-only | verified | known-broken
```

Example conventions of the contract tests (`tests/contract`). `soap`: `request: {params: {...}}` is compared with the request element built from `params` (namespace-aware, whitespace-insensitive), or `request: {body: "<xml/>"}` (the element, or a full envelope) which wins for the comparison (`params` is still needed when the operation has required arguments, because it drives the call); `response: {text: "<xml/>"}` is the reply element, a Fault or a full envelope, with `status` and `error: {code, message}` as alternatives for a fault. Prefixed names are written as in `params` (`acert:Id`, `@acert:flag`); a prefixed attribute is compared in that prefix's namespace. `cgi` examples of operations with `{placeholders}` in `binding.path` give the path in `request.path` (`/local/fflprapp/cloud.cgi`); the placeholder values are read from it and must satisfy the argument's type. Index arguments of templated names and of templated fixed `query` values (`n` in `root.Image.I{n}.RateControl.Mode`, `group=Image.I{n}.RateControl`) are read from the concrete names and values the example gives, and must agree. `rest`: `request: {path, query, body}` (the path is relative to `binding.root`; `query` values may be lists) and `response: {status, body}` or `{status, text}`.

`cgi` examples with raw bodies, uploads, mixed placement and bare keys:

```yaml
examples:
  - title: Send an XML document      # encoding: body
    request:
      query: {name: x, live-sum.json: null}  # URL arguments; null is a bare key (?live-sum.json)
      body: '<a><b>t</b></a>'                # the raw body: text is UTF-8, a mapping or list is JSON
      content_type: text/xml                 # optional; defaults to binding.content_type
  - title: Upload a clip             # encoding: multipart
    request:
      query: {name: x}               # arguments placed in the URL (x-in: query, url_query)
      form: {note: hi}               # arguments placed in the body (text parts)
      parts:                         # upload parts, in order, matched by part name
        - {name: file, filename: clip.wav, content_type: audio/basic, content: RIFF}   # or content_base64, or size: N
```

A body is compared by its content type: XML structurally (ignoring whitespace and attribute order), JSON as JSON, `text/*` as text without surrounding whitespace, anything else as bytes. For parts, `name` is required and matched in order against the file and typed parts sent (text fields are compared through `form`); `filename`, `content_type` and `content` (or `content_base64`) are compared only when given, and `size: N` stands for N bytes of filler (the length is compared). When `query` and `form` are both given, `query` keys must be in the URL and `form` keys only in the body. Bare keys must be sent without `=`.

A part that names a `filename` is run with an `Upload` carrying that name, because plain bytes carry none (the runtime would send the `x-upload` default or the part name); a `content_type` is compared with what the operation sends. `jsonrpc` operations with `binding.multipart` take the same `request.parts` for their file parts. The JSON envelope part is compared through `request.params` like any JSON-RPC call, and without `parts` the file arguments get filler bytes (the docs often show only the JSON message). For an `encoding: body` operation with an `x-in: content_type` argument, the example's `content_type` is passed as that argument.

### Examples of streams, sessions and RTSP URLs

Streamed `cgi` replies, WebSocket sessions and RTSP URL builders may have `examples`; the contract tests run them through the generated API method with fake transports. An example that cannot be checked (it needs a real device or a codec the fake does not speak) carries `x-contract: {skip: "reason"}`. `x-contract: {template: true}` skips these three kinds as well.

```yaml
# stream (cgi): the request is compared like any cgi request (query, form, body); the response is optional
examples:
  - title: Watch the ports
    request: {query: {monitor: all}}
    response:
      status: 200                       # default 200
      content_type: text/plain          # default: octet-stream, multipart/x-mixed-replace; boundary=b for mjpeg
      text: "0=active\n1=inactive\n"     # the body the fake serves
      items: ["0=active", "1=inactive"] # optional: decoded items. lines: str; bytes: joined and compared as text; mjpeg: each part body as text
# rtsp: the URL the method returns, built for the host camera.test with the credentials root/pass
examples:
  - title: Live stream, no audio       # binding: rtsp: {query: {videocodec: h264}}
    request:
      params: {resolution: 1280x720, audio: false}   # wire names, as in the other families
      port: 8554                                     # optional method arguments
      include_credentials: true
    response: {url: "rtsp://root:pass@camera.test:8554/axis-media/media.amp?videocodec=h264&resolution=1280x720&audio=0"}
# session: a fake WebSocket camera accepts the handshake and acknowledges the setup requests
examples:
  - title: Filtered events
    request:
      params: {audioSessionId: abc}     # path placeholders, wire names (sessions with a placeholder path only)
      connect: {event_filter_list: [{topicFilter: "tns1:Device/tnsaxis:IO/VirtualPort"}]}   # setup arguments (event_filter_list or subscriptions)
      path: /vapix/ws-data-stream       # optional: the expected handshake path, placeholders percent-encoded; default from the binding
      query: {sources: events}          # optional: the expected handshake query; default from the binding
      messages:                         # optional: the JSON messages sent right after the handshake, in order
        - {method: "events:configure", params: {eventFilterList: [{topicFilter: "tns1:Device/tnsaxis:IO/VirtualPort"}]}}
```

Session `messages` are compared as subsets: every key written must match, extra keys the runtime adds (`context`, `id`) are ignored; lists must match exactly. A session example has no `response`.

Request model naming: when `params` is inline, the generator names it `<OperationInPascalCase>Request`, unless `x-name` gives a name. Several operations may share one inline shape through the same `x-name`, for example `PublisherIdRequest` for `get_publisher` and `remove_publisher`. Named params types should follow the same convention.

JSON-RPC `params` that are not an object (an array, or a free-form map with only `additionalProperties`) are wrapped: the generator makes a request model with one required field named by `x-arg-name` on the params schema (default `params`) holding that schema, sets `JsonRpcBinding(params_field=...)` so its value is sent as the whole `params`, and makes it the one positional argument. Add `x-arg-optional: true` to the params schema when the device allows `params` to be left out (for example "without port queries, all ports are returned"): the field becomes optional (`ports: list[PortQuery] | MISSING = MISSING`) and when it is not given no `params` member is sent at all. `x-arg-optional` is only valid on wrapped params.

Results:

- `result: {x-xml: true}` returns the parsed XML root element (`xml.etree.ElementTree.Element`) until the spec maps the XML to a model.
- `result: {type: string}` and `result: {format: binary}` return the decoded text and the raw bytes.

Signature rule:

- An operation whose params include a nested model, or more than four fields, gets two overloads: keyword arguments, or one positional request object.
- Smaller operations get one plain signature. `positional` names the arguments taken positionally (DCA path keys are positional by default), and the rest are keyword-only.
- On an overloaded operation, `positional` makes those arguments positional in the keyword overload (`set_x(value, /, *, ...)`); the request-object form is unchanged. DCA path keys are not positional by default there.
- A `x-nullable` field accepts an explicit `None` in the signature.
- Overloaded methods raise `TypeError` for more positional values than `positional` lists.
- A scalar `result` keeps its constraints (`minimum`, `pattern`, ...) at run time, and tolerates enum values newer than the generated `Literal`; the method's return annotation stays the plain type. A JSON-RPC response whose `data` is `null` or missing is validated as such, so it only passes for a `result` that accepts `None`.
- Every method takes `request_options`.

## Patches

`specs/patches/<id>.yaml` holds corrections and variants (design section 8). The generator applies patches before validation, so a generated module reflects the corrected spec.

## Provenance

```yaml
provenance:
  completeness: complete        # complete | partial | stub
  open_questions: [...]
  migrated_from: v1             # set by codegen/migrate_v1.py
  curated: false                # true once a person or agent reviewed the migrated spec
```
