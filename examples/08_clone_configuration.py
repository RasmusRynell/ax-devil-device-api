"""Copy MQTT and analytics publishing setup from a reference camera to others.

Read-modify-write is where client libraries usually hurt people. Two traps
are handled here:

- Secrets are masked in what the camera returns (the MQTT password reads as
  ``*****``). ``ConfigureClientRequest.from_current`` drops masked fields and
  asks the camera to keep its stored password instead of overwriting it with
  asterisks. On a *different* camera there is no stored password, so the real
  one must be supplied.
- ``configure_client`` replaces the whole configuration (fields left out go
  back to defaults), so changes start from the full current configuration.

Status: runs today.

    python 08_clone_configuration.py 10.20.0.10 10.20.0.11 10.20.0.12
"""

import os
import sys

from ax_devil_device_api import Device
from ax_devil_device_api.apis.analytics_mqtt import AddPublisherRequest
from ax_devil_device_api.apis.mqtt_client import ConfigureClientRequest
from ax_devil_device_api.errors import DeviceError

CREDENTIALS = (os.environ["CAM_USER"], os.environ["CAM_PASS"])
BROKER_PASSWORD = os.environ["BROKER_PASS"]


def main(reference: str, targets: list[str]) -> None:
    with Device(reference, credentials=CREDENTIALS) as ref:
        config = ref.apis.mqtt_client.get_client_status().config
        if config is None:
            raise SystemExit(f"{reference} has no MQTT configuration")
        publishers = ref.apis.analytics_mqtt.list_publishers()

        # Same camera, one change: keep everything else, including the stored password.
        tweak = ConfigureClientRequest.from_current(config).model_copy(update={"keep_alive_interval": 15})
        ref.apis.mqtt_client.configure_client(tweak)

    # Other cameras: same settings, but the password has to be provided explicitly.
    template = ConfigureClientRequest.from_current(config).model_copy(
        update={"password": BROKER_PASSWORD, "keep_existing_password": False}
    )
    for host in targets:
        try:
            with Device(host, credentials=CREDENTIALS) as dev:
                client_id = f"cam-{host.replace('.', '-')}"  # client ids must be unique per broker
                dev.apis.mqtt_client.configure_client(template.model_copy(update={"client_id": client_id}))
                existing = {p.id for p in dev.apis.analytics_mqtt.list_publishers()}
                for publisher in publishers:
                    if publisher.id not in existing:
                        dev.apis.analytics_mqtt.add_publisher(AddPublisherRequest.from_current(publisher))
                dev.apis.mqtt_client.activate_client()
                print(f"{host}: cloned {len(publishers)} publisher(s)")
        except DeviceError as e:
            print(f"{host}: failed: {e}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
