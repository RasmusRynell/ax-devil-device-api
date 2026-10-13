# Examples

| File | Scenario | Shows |
|---|---|---|
| `01_fleet_mqtt_rollout.py` | Configure MQTT + analytics publishing on 50 cameras concurrently | async, per-device error classification incl. `AccessDenied` |
| `02_parameter_drift.py` | Compare `param.cgi` values to a baseline, fix drift | sync, classic CGI, dry run |
| `03_version_aware_thermal.py` | Thermal isotherms on a mixed-firmware fleet | `supports()` → `SupportResult`, field-level version gating, fallback |
| `04_record_clips.py` | Record a video clip from each camera straight to disk | streaming results, per-call timeout, early exit, partial files |
| `05_event_watch.py` | Watch I/O and PTZ events on several cameras | WebSocket sessions, backoff, isolated failures, gap reporting |
| `06_debugging_and_lab_setups.py` | Bench camera over HTTP with request logging | logging, `on_request`/`on_response`, error fields, local validation, identity, capabilities |
| `07_long_running_service.py` | Monitor cameras for weeks | one long-lived `AsyncDevice` per camera, health checks, firmware-change detection, credential rotation |
| `08_clone_configuration.py` | Copy MQTT + publishers from a reference camera | safe read-modify-write: masked secrets, replace semantics, request objects |
| `09_testing_your_code.py` | Unit-test your own code without a camera | `testing.MockCamera`, sync and async |

All examples use the generated APIs and read credentials from `CAM_USER` and `CAM_PASS` (`08` also reads `BROKER_PASS`). `tests/examples/test_example_scripts.py` imports each script and runs it against a `MockCamera` (or a fake WebSocket camera for `05`), so the examples cannot drift from the library; no real network is used.
