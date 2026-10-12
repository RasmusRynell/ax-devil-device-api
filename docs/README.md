# Documentation

| File | Contents |
|---|---|
| [design.md](design.md) | Architecture and design of ax-devil-device-api 1.0: layers, HTTP and auth, sans-IO protocols, generated API shape, `Device`, errors, spec format, tests, build order. Parts not built yet are marked *planned*. |
| [../examples/](../examples/README.md) | Nine scenario scripts (fleet rollout, parameter drift, long-running service, testing with `MockCamera`, ...). The README there says which run today and which are targets. |

The decisions that shaped the public API (connection lifetime, retries, request shapes, errors, capabilities, testing) are in [section 13 of design.md](design.md#13-decisions-log).

Development uses `uv`: `uv sync`, `uv run pytest`, `uv run pyright`.
