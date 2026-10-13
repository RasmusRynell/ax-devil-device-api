"""A service that watches cameras for weeks: one long-lived Device per camera.

The normal way to use the library in a UI or service is to create one
``AsyncDevice`` per camera when the camera is added and keep it until the
camera is removed. The device object keeps the connection pool, the verified
credential and the negotiated API versions, so routine calls cost one round
trip. It copes with the camera's lifecycle by itself:

- Idle connections the camera dropped are reopened on the next call.
- A request that never reached the camera (refused, connect timeout) is retried.
- After a reboot the credential is re-negotiated on the first 401.
- After a firmware upgrade, cached API versions are dropped as soon as the
  camera rejects one, or when ``identity(refresh=True)`` sees new firmware.

What stays the application's job: how often to poll, how long to back off,
and replacing the Device when the camera's address or password changes.
"""

import asyncio
import os
from dataclasses import dataclass, field

from ax_devil_device_api import AsyncDevice
from ax_devil_device_api.errors import AccessDenied, AuthError, DeviceError, TransportError, Unavailable

POLL = 30  # seconds


@dataclass
class Camera:
    host: str
    device: AsyncDevice
    online: bool = False
    firmware: str | None = None
    mqtt: str = "?"
    errors: list[str] = field(default_factory=list)
    busy: asyncio.Lock = field(default_factory=asyncio.Lock)
    """Held while polling, so the Device is never closed under a running poll."""


class Monitor:
    def __init__(self, username: str, password: str) -> None:
        self._credentials = (username, password)
        self.cameras: dict[str, Camera] = {}

    def add(self, host: str) -> None:
        self.cameras[host] = Camera(host, AsyncDevice(host, credentials=self._credentials))

    async def change_password(self, host: str, password: str) -> None:
        """Credentials are part of a Device's identity: replace the Device, don't mutate it."""
        old = self.cameras[host]
        self.cameras[host] = Camera(host, AsyncDevice(host, credentials=(self._credentials[0], password)))
        async with old.busy:  # let a running poll finish first
            await old.device.aclose()

    async def remove(self, host: str) -> None:
        cam = self.cameras.pop(host)
        async with cam.busy:
            await cam.device.aclose()

    async def poll(self, cam: Camera) -> None:
        async with cam.busy:
            await self._poll(cam)

    async def _poll(self, cam: Camera) -> None:
        try:
            identity = await cam.device.identity(refresh=True)  # cheap health check; detects firmware changes
            if cam.firmware and cam.firmware != identity.firmware_version:
                print(f"{cam.host}: firmware {cam.firmware} -> {identity.firmware_version}")
            cam.firmware = identity.firmware_version
            status = await cam.device.apis.mqtt_client.get_client_status()
            cam.mqtt = status.status.connection_status
            cam.online = True
        except (TransportError, Unavailable) as e:  # offline or rebooting: keep the Device, try again later
            cam.online = False
            cam.errors.append(type(e).__name__)
        except (AuthError, AccessDenied) as e:  # needs a human: wrong password or a viewer account
            cam.online = False
            cam.errors.append(str(e))
        except DeviceError as e:
            cam.errors.append(str(e))

    async def run(self) -> None:
        while True:
            await asyncio.gather(*(self.poll(c) for c in list(self.cameras.values())))
            for cam in self.cameras.values():
                state = "online " if cam.online else "OFFLINE"
                print(f"{cam.host:<14} {state} fw={cam.firmware} mqtt={cam.mqtt} {cam.errors[-1:] or ''}")
            await asyncio.sleep(POLL)


async def main() -> None:
    monitor = Monitor(os.environ["CAM_USER"], os.environ["CAM_PASS"])
    for host in ["10.20.0.11", "10.20.0.12", "10.20.0.13"]:
        monitor.add(host)
    try:
        await monitor.run()
    finally:
        for host in list(monitor.cameras):
            await monitor.remove(host)


if __name__ == "__main__":
    asyncio.run(main())
