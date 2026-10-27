---
name: ax-devil-device-api
description: 'Use the ax-devil-device-api Python package and its `ax-devil-device-api` command (1.0 rewrite, httpx and pydantic) to talk to Axis devices over VAPIX. Use when asked to write or review Python code with Device or AsyncDevice, call any generated VAPIX API (MQTT, parameters, PTZ, media, events, audio, ...), read or update param.cgi parameters, stream media or events, upload files, build RTSP URLs, check what a device supports (identity, capabilities, API versions), handle device errors, retry or time out calls, unit-test camera code with MockCamera, run the ax-devil-device-api CLI, or maintain the specs and generated code (specs/apis, codegen).'
---

# ax-devil-device-api

Python client for Axis devices (VAPIX). Sync (`Device`) and async (`AsyncDevice`) share one code base. Almost all of it is generated from YAML specs.

**Package**: `ax-devil-device-api`. Python 3.11+. Runtime dependencies: `httpx`, `httpx-ws`, `pydantic`.
**CLI**: `ax-devil-device-api` (argparse, JSON output). `ax-devil-device-api apis`, `ax-devil-device-api ops <api>`, `ax-devil-device-api call <api> <op> key=value`, `snapshot`, `summary`, `supported`. The old 0.x subcommands no longer exist.
**Status**: pre-release rewrite. 208 generated APIs (`dev.apis.<name>`) over the families jsonrpc, dca, cgi, service_json, soap, rest, WebSocket sessions, streams and RTSP URLs. Every operation is `docs-only`: written from the documentation, not yet verified on hardware. Say so when a user depends on one, and never invent a method: list what exists with `ax-devil-device-api apis` / `ax-devil-device-api ops <api>` or `docs/api_surface.txt`.

## Before writing code that talks to a device

Get concrete values for host, username and password. Check the environment the examples use (`CAM_USER`, `CAM_PASS`; the CLI also reads `AX_DEVIL_HOST`, `AX_DEVIL_USER`, `AX_DEVIL_PASSWORD`), and ask the user for what is missing. Do not guess IP addresses or credentials.

HTTPS is the default. A plain-HTTP device needs `Device(host, scheme="http", allow_http=True, ...)`; only do that when the user says the device is on a trusted bench network. A device with a private CA needs `verify="/path/ca.pem"` (CLI: `--ca-bundle`; `--insecure` disables verification).

## References

- [Python API reference](./references/python-api.md): construction, calling APIs, request objects, streams, sessions, uploads, RTSP, errors, retries, capabilities, features, CLI, testing, and the spec and codegen workflow.

In the repository: `README.md`, `docs/design.md` (architecture and decisions), `docs/spec-format.md` (spec format), `docs/api_surface.txt` (every generated name and signature), `examples/README.md` (nine scenarios, each run by `tests/examples/`), `src/ax_devil_device_api/apis/` (generated, never edit).

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
- **`dev.apis.<name>`** gives an API object. Names are the snake_case spec module names; later incompatible major versions get `_v2`. Methods take keyword arguments or one typed request object (never both), and always accept `request_options=`.
- **Models** are pydantic classes. Unset fields are not sent; unknown fields in device responses are ignored; typos in your own arguments raise `pydantic.ValidationError` before anything is sent.
- **Writes can replace whole configurations.** Read the docstring (`write: replace` semantics, access level). Use `ConfigureClientRequest.from_current(...)`-style helpers to edit and write back safely (they never write a masked password back).
- **Streams, sessions and RTSP URLs are not plain return values.** Stream methods return a `StreamResult` (use `with`), session `connect(...)` methods a `Session` (use `with`), RTSP methods an `RtspUrl` (no network call).
- **Errors** all derive from `ax_devil_device_api.errors.DeviceError`. Catch `AccessDenied` / `Unavailable` for the common categories.
- **No automatic support checks.** Call `dev.supports(ApiClass)` yourself; a call to an API the device lacks raises `NotSupported` from version negotiation or an `HttpError`/`ApiError`.
- **Out of scope:** RTSP session commands (`OPTIONS`, `DESCRIBE`, `SETUP`, `GET_PARAMETER`, `SET_PARAMETER`) and RTSP-over-HTTP, the Google JSON WebSocket codec, STOMP, binary audio formats, multipart audio decoding. Operations that need them are `BLOCKED` notes in the specs, not methods.

## Quick decision guide

| Task | Use |
|---|---|
| Which APIs / operations exist? | `ax-devil-device-api apis`, `ax-devil-device-api ops <api>`, `docs/api_surface.txt` |
| Model, serial number, firmware; health check | `dev.identity()` / `dev.identity(refresh=True)` |
| Does this camera offer an API? | `dev.supports(MqttClientApi)` returns a `SupportResult` (truthy only for YES); `ax-devil-device-api supported` for all (JSON `{"apis", "errors"}`; exit 1 when discovery cannot reach the device) |
| What does the camera advertise? | `dev.capabilities()`, `features.device_summary(dev)` |
| One JPEG | `features.snapshot(dev, resolution="640x480")` or `ax-devil-device-api snapshot -o img.jpg` |
| Download or watch a long body | a stream operation, e.g. `with dev.apis.media_stream.get_media_stream(container="mp4") as s:` |
| Live events over WebSocket | `with dev.apis.event_streaming_ws.connect([EventFilter(...)]) as session:` |
| Upload a file | pass `bytes`, a `Path` or `Upload(stream, size)` to the upload argument |
| RTSP URL | `dev.rtsp_url(MediaStream(...))` or a generated `*_url` method; hand it to a media library |
| Read or change `param.cgi` parameters | `dev.apis.parameter_management` |
| Run any operation from a shell | `ax-devil-device-api call <api> <op> key=value` |
| Per-call timeout or retry policy | `request_options=RequestOptions(timeout=..., retry=...)` |
| Forget cached facts after a reboot or firmware upgrade | `dev.refresh()` |
| Test your own code without a camera | `ax_devil_device_api.testing.MockCamera` |
| Run an operation by descriptor | `dev.invoke(mqtt_client.OPS.get_client_status)` |

## Changing the library

- A wrong or missing API method is a **spec** problem: edit `specs/apis/<section>/<id>.yaml` (format: `docs/spec-format.md`), then `uv run python -m codegen validate`, `uv run python -m codegen generate`, and commit the regenerated `src/ax_devil_device_api/apis/` and `docs/api_surface.txt` in the same change. Never edit generated files by hand: `uv run python -m codegen check` (also run in CI) fails on any difference.
- Device-verified corrections go in `specs/patches/<id>.yaml`, not in the doc-derived spec.
- Behaviour that a spec binding cannot express (a new codec, envelope or family behaviour) is a change to `_protocols/`, `_runtime/` or `codegen/` and needs a human decision; do not work around it in a spec.
- Checks before finishing: `uv run python -m codegen check`, `uv run ruff check .`, `uv run pyright`, `uv run pytest` (unit, contract tests that run every spec example, codegen tests, and `tests/examples/` which runs each `examples/` script against a fake camera). Keep `examples/` working: they are tests.

## Examples

`examples/` has nine runnable scenarios: `01` fleet MQTT rollout (async), `02` parameter drift, `03` version-aware thermal settings, `04` recording clips with streams, `05` event watch over WebSocket, `06` debugging and lab setups, `07` long-running service, `08` clone configuration, `09` testing with `MockCamera`.
