"""Lab and debugging setups: request logging, plain HTTP, and inspecting errors.

- Standard ``logging`` at DEBUG on the ``ax_devil_device_api`` logger shows
  every request with status, duration and retry attempt.
- ``on_request`` receives a redacted description of every outgoing request
  (passwords and tokens are replaced with ``<redacted>``).
- ``on_response`` receives one structured record per request attempt, for
  metrics or tracing.
- Plain HTTP must be enabled explicitly with ``allow_http=True``.
- Errors carry structured fields, not just a message.

Status: runs today.
"""

import json
import logging

from ax_devil_device_api import Device
from ax_devil_device_api.apis.mqtt_client import Server
from ax_devil_device_api.errors import AccessDenied, ApiError, ConfigurationError, HttpError

logging.basicConfig(level=logging.WARNING)
logging.getLogger("ax_devil_device_api").setLevel(logging.DEBUG)


def log_request(info: dict) -> None:
    print(">>>", json.dumps(info["request"], indent=2))


def record_metrics(info: dict) -> None:
    print(f"<<< {info['api']}.{info['operation']}: {info['status'] or info['error']} in {info['duration_ms']} ms")


# A factory-fresh camera on a lab bench, HTTP only.
try:
    Device("192.168.0.90", credentials=("root", "pass"), scheme="http")
except ConfigurationError as e:
    print(f"refused as expected: {e}")

with Device(
    "192.168.0.90",
    credentials=("root", "pass"),
    scheme="http",
    allow_http=True,
    on_request=log_request,
    on_response=record_metrics,
) as dev:
    mqtt = dev.apis.mqtt_client

    # The password appears as "<redacted>" in the logged request body.
    try:
        mqtt.configure_client(
            server=Server(host="lab-broker", port=70000),  # invalid port: the device decides
            client_id="bench",
            password="hunter2",
        )
    except AccessDenied:
        print("this account is not an admin")
    except ApiError as e:
        print(f"api error {e.code} ({e.kind}): {e.message}")
        print(f"  documented meaning: {e.description}")  # from the spec's error table
        print(f"  http status: {e.http_status}, raw: {e.details}")
    except HttpError as e:
        print(f"http {e.status}: {e.body_excerpt}")

    # Mistakes fail locally, before any request is sent.
    for mistake in (lambda: Server(host="lab-broker", prot="tcp"), lambda: Server(host="lab-broker", port=None)):
        try:
            mistake()
        except ValueError as e:
            print(f"caught locally: {e.errors()[0]['msg']}")

    # Who is this, and what does it support?
    print(dev.identity())
    caps = dev.capabilities()
    print(f"{len(caps.classic_apis or {})} classic APIs, {len(caps.dca_apis or {})} configuration APIs, failed probes: {caps.errors}")
