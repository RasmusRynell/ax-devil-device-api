"""Roll out analytics-over-MQTT to a whole fleet of cameras, concurrently.

For every camera: point its MQTT client at the broker, publish the scene
description data source to a per-camera topic, and activate the client.
Each camera's outcome is classified, so one bad camera never stops the rollout.

Status: runs today (mqtt-client and analytics-mqtt are built).
"""

import asyncio
import os

from ax_devil_device_api import AsyncDevice
from ax_devil_device_api.apis.mqtt_client import AnnouncementMessage, Server
from ax_devil_device_api.errors import AccessDenied, ApiError, AuthError, DeviceError, NotSupported, TransportError

BROKER = Server(host="mqtt.example.internal", protocol="ssl", port=8883)
SCENE_SOURCE = "com.axis.analytics_scene_description.v0.beta#1"
CAMERAS = [f"10.20.0.{n}" for n in range(10, 60)]
CREDENTIALS = (os.environ["CAM_USER"], os.environ["CAM_PASS"])


async def provision(host: str) -> str:
    async with AsyncDevice(host, credentials=CREDENTIALS, verify="/etc/ssl/fleet-ca.pem") as dev:
        mqtt = dev.apis.mqtt_client
        await mqtt.configure_client(
            server=BROKER,
            client_id=f"cam-{host}",
            keep_alive_interval=30,
            last_will_testament=AnnouncementMessage(use_default=True),
        )

        analytics = dev.apis.analytics_mqtt
        existing = {p.id for p in await analytics.list_publishers()}
        if "scene" not in existing:
            await analytics.add_publisher(
                id="scene",
                data_source_key=SCENE_SOURCE,
                mqtt_topic=f"fleet/{host.replace('.', '_')}/scene",
                qos=1,
            )

        await mqtt.activate_client()
        status = await mqtt.get_client_status()
        return f"ok ({status.status.connection_status})"


async def safe_provision(host: str) -> tuple[str, str]:
    try:
        return host, await provision(host)
    except NotSupported as e:
        return host, f"skipped: {e.reason}"  # old firmware, API missing
    except AuthError:
        return host, "wrong credentials"
    except AccessDenied:
        return host, "account lacks admin rights"
    except ApiError as e:
        return host, f"device refused: {e.code} {e.description or e.message}"
    except TransportError as e:
        return host, f"unreachable: {type(e).__name__}"
    except DeviceError as e:  # anything else from the library; never abort the whole rollout
        return host, f"failed: {e}"


async def main() -> None:
    # Each AsyncDevice already limits requests per camera (max_concurrency=4 by default);
    # the semaphore here limits how many cameras are worked on at once.
    limit = asyncio.Semaphore(16)

    async def bounded(host: str) -> tuple[str, str]:
        async with limit:
            return await safe_provision(host)

    results = await asyncio.gather(*(bounded(h) for h in CAMERAS))
    for host, outcome in sorted(results):
        print(f"{host:<14} {outcome}")


if __name__ == "__main__":
    asyncio.run(main())
