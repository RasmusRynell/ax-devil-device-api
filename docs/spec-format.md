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
family: jsonrpc                  # jsonrpc | dca | cgi | service_json | soap | rest | ws | rtsp
status: released                 # released | beta | alpha | deprecated
python:
  module: mqtt_client            # file and dev.apis attribute; unsuffixed = first major, later majors _v2
  class: MqttClient              # -> MqttClientApi and AsyncMqttClientApi; a trailing `Api` is dropped (warning)
docs: [https://developer.axis.com/vapix/network-video/mqtt-client-api/]
access: admin                    # default access level for operations
discovery:                       # how Device.supports() recognizes the API; tried in order
  - api_discovery: mqtt-client
  - dca: {api: analytics-mqtt, version: v1}
  - param: {name: Properties.API.HTTP.Version, value: "3"}
  - param: {name: Properties.EmbeddedDevelopment.Version, value: "1.20", compare: ">="}
  - acap: {name: loiteringguard}
requires: {firmware: "11.5", application: null}   # optional
binding: {...}                   # family-specific, below
errors: {...}                    # API-wide error codes, below
types: {...}                     # named schemas, below
operations: {...}                # below
sources: [...]                   # doc pages, with content hashes (change monitoring)
provenance: {...}                # completeness, open questions, verification
```

### Discovery entries

- `api_discovery: <id>`: listed by API discovery (`apidiscovery.cgi`).
- `dca: {api, version}`: listed by `/config/discover`.
- `param: {name, value, compare}`: a `param.cgi` property. Without `value` the property only has to exist. `compare` is `"=="` (default) or `">="`; `">="` compares dotted numbers component by component (`1.20` >= `1.9`), and a value that is not a dotted number never matches.
- `acap: {name}`: an ACAP application whose `Name` attribute (case-insensitive) appears in `/axis-cgi/applications/list.cgi`. Installed is enough; the application need not be running. The list needs an administrator account, so without one the answer is `UNKNOWN`, not `NO`.

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
                                                              # a dotted key as nested segments (a.b -> a/b); default `segment`
```

`cgi`:

```yaml
binding:
  path: /axis-cgi/param.cgi
# operation:
  binding:
    method: GET                       # GET | POST
    query: {action: list}             # fixed arguments
    encoding: query                   # query | form (form sends every argument in a POST body)
    accept: text/plain
    reply: {text_kv: {strip_prefix: "root."}}   # text_ok | text | text_kv | xml | binary | json
    stream: false
```

Reply codecs: `text_ok` (body must be `OK`), `text`, `text_kv` (`key=value` lines; optional `strip_prefix`), `xml` (optional `error_elements`), `binary` (optional `media_types`, `signatures` as hex strings), `json`.

Every binding may set `auth` (`required`, `anonymous`, `if_challenged`) and `timeout` (seconds).

## XML replies (cgi)

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

## Errors

```yaml
errors:
  2104: {description: Invalid parameter value specified, kind: invalid_argument}
  2105: {description: Authorization failure, kind: access_denied}
```

`kind` is one of `access_denied`, `unavailable`, `invalid_argument`, `not_found`, `unsupported`, `internal`. It selects the error class at runtime, so set it whenever the meaning is clear. Operations may add their own `errors`.

## Types

Named schemas, using a JSON Schema subset: `type`, `properties`, `required`, `items`, `enum`, `const`, `additionalProperties`, `minimum`, `maximum`, `minLength`, `maxLength`, `pattern`, `minItems`, `maxItems`, `default`, `description`, `since`, `$ref: "#/types/Name"`, `oneOf`.

- An `object` type becomes a `Model` class. Other types become type aliases (`Annotated[str, Field(...)]`, `Literal[...]`).
- `required` lists the fields that must be present. In request models they are required arguments. In response models a missing one raises `ResponseFormatError`, so list only what the device always returns.
- Optional fields become `X | None = None`.
- Extensions:
  - `x-nullable: [field, ...]`: may be sent as explicit `null`.
  - `x-masked: [field, ...]`: masked by the device in responses (for example `*****`); dropped by round trips.
  - `x-read-only: [field, ...]`: present in responses, never sent. When a request type is shared with the response, read-only fields stay on the model but are not method arguments.
  - `x-python-name` on a property: overrides the derived name.
  - `x-style` on a property (cgi only): `plain`, `csv`, `axis_bool`, `spread`.

- `pattern` must work in pydantic's regex engine: lookaheads and lookbehinds (`(?=`, `(?!`, `(?<=`, `(?<!`) are rejected by `codegen validate`.
- `minItems`/`maxItems` on arrays become `Field(min_length=..., max_length=...)` (a point pair is an array of two numbers with both set to 2).
- `since: "1.9"` on a property (mainly result fields): the field was added in that API version. It is always generated optional (`X | None = None`, whatever `required` says) and its attribute docstring ends with "Available from API version 1.9.". The runtime does not drop it on older devices; the field is `None` when the device does not return it.

Enums are `Literal`s. Responses tolerate new values of the same type, and requests reject them.

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

Request model naming: when `params` is inline, the generator names it `<OperationInPascalCase>Request`, unless `x-name` gives a name. Several operations may share one inline shape through the same `x-name`, for example `PublisherIdRequest` for `get_publisher` and `remove_publisher`. Named params types should follow the same convention.

JSON-RPC `params` that are not an object (an array, or a free-form map with only `additionalProperties`) are wrapped: the generator makes a request model with one required field named by `x-arg-name` on the params schema (default `params`) holding that schema, sets `JsonRpcBinding(params_field=...)` so its value is sent as the whole `params`, and makes it the one positional argument.

Results:

- `result: {x-xml: true}` returns the parsed XML root element (`xml.etree.ElementTree.Element`) until the spec maps the XML to a model.
- `result: {type: string}` and `result: {format: binary}` return the decoded text and the raw bytes.

Signature rule:

- An operation whose params include a nested model, or more than four fields, gets two overloads: keyword arguments, or one positional request object.
- Smaller operations get one plain signature. `positional` names the arguments taken positionally (DCA path keys are positional by default), and the rest are keyword-only.
- On an overloaded operation, `positional` makes those arguments positional in the keyword overload (`set_x(value, /, *, ...)`); the request-object form is unchanged. DCA path keys are not positional by default there.
- A `x-nullable` field accepts an explicit `None` in the signature.
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
