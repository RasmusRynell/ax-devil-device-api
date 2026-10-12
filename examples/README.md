# Examples

| File | Scenario | Shows | Status |
|---|---|---|---|
| `01_fleet_mqtt_rollout.py` | Configure MQTT + analytics publishing on 50 cameras concurrently | async, per-device error classification incl. `AccessDenied` | runs today |
| `02_parameter_drift.py` | Compare `param.cgi` values to a baseline, fix drift | sync, classic CGI, dry run | runs today |
| `03_version_aware_thermal.py` | Thermal isotherms on a mixed-firmware fleet | `supports()` → `SupportResult`, field-level version gating, fallback | target |
| `04_stream_server_report.py` | Download large server reports to disk | streaming results, per-call timeout, progress from headers | target |
| `05_event_watch.py` | Watch I/O and PTZ events on several cameras | WebSocket sessions, backoff, isolated failures, gap reporting | target |
| `06_debugging_and_lab_setups.py` | Bench camera over HTTP with request logging | logging, `on_request`/`on_response`, error fields, local validation, identity, capabilities | runs today |
| `07_long_running_service.py` | Monitor cameras for weeks | one long-lived `AsyncDevice` per camera, health checks, firmware-change detection, credential rotation | runs today |
| `08_clone_configuration.py` | Copy MQTT + publishers from a reference camera | safe read-modify-write: masked secrets, replace semantics, request objects | runs today |
| `09_testing_your_code.py` | Unit-test your own code without a camera | `testing.MockCamera`, sync and async | runs today |

"Target" examples use APIs that the generator will produce from `specs/`; their names and fields come from the spec files, but they do not run yet.

All examples read credentials from `CAM_USER` and `CAM_PASS`.
