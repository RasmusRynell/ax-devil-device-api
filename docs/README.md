# Documentation

| File | Contents |
|---|---|
| [design.md](design.md) | Architecture of ax-devil-device-api 1.0: layers, HTTP and auth, protocol families (cgi, jsonrpc, dca, service_json, soap, rest), streams, uploads, WebSocket sessions and the heartbeat contract, RTSP URLs, generated API shape, `Device`, capabilities and discovery, errors, the generator and patches, features and CLI, tests, decisions log. Parts not built yet are marked *planned*. |
| [spec-format.md](spec-format.md) | The YAML spec format that the generator turns into API modules: top level, discovery entries, bindings per family, CGI arguments and uploads, XML replies, errors, types, operations, examples. |
| [api_surface.txt](api_surface.txt) | Generated snapshot of every public name and signature of the generated APIs. Do not edit; `python -m codegen generate` rewrites it. |
| [../examples/](../examples/README.md) | Nine scenario scripts (fleet rollout, parameter drift, version-aware calls, clip recording, event watch, long-running service, testing with `MockCamera`, ...), each run against a fake camera by `tests/examples/`. |

The decisions that shaped the public API (connection lifetime, retries, request shapes, errors, capabilities, sessions, testing) are in [section 13 of design.md](design.md#13-decisions-log).

Development uses `uv`: `uv sync --locked`, `uv run python -m codegen check`, `uv run ruff check .`, `uv run pyright`, `uv run pytest`.
