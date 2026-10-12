"""React to camera events in real time over WebSocket, across several cameras.

Opens one event session per camera, subscribes to I/O port changes and
PTZ-ready notifications, and prints them as they arrive.

Each camera is watched independently: a camera that drops is reconnected
with backoff, and a camera that fails permanently (wrong password, no
event API) is reported and left alone, without affecting the others.
Events that happen while a session is down are lost; the session reports
the gap so the application can resynchronize (e.g. re-read port states).

Status: target. WebSocket sessions and ``event_streaming_ws`` are not built yet;
the message names and filter fields come from
specs/apis/network-video/event-streaming-over-websocket.yaml.
"""

import asyncio
import os

from ax_devil_device_api import AsyncDevice
from ax_devil_device_api.apis.event_streaming_ws import EventFilter
from ax_devil_device_api.errors import AccessDenied, AuthError, NotSupported, TransportError, Unavailable

CREDENTIALS = (os.environ["CAM_USER"], os.environ["CAM_PASS"])

FILTERS = [
    EventFilter(topic_filter="tns1:Device/tnsaxis:IO/Port"),
    EventFilter(topic_filter="tns1:PTZController/tnsaxis:PTZReady"),
]


async def watch(host: str) -> None:
    backoff = 1.0
    async with AsyncDevice(host, credentials=CREDENTIALS) as dev:
        while True:
            try:
                async with dev.apis.event_streaming_ws.connect(event_filter_list=FILTERS) as session:
                    if session.gap:  # reconnected: anything between session.gap.start and now was missed
                        print(f"{host}: reconnected after {session.gap.duration:.0f} s; resynchronizing")
                    backoff = 1.0
                    async for event in session.notifications():
                        if event.topic.endswith("IO/Port") and event.data.get("state") == "1":
                            print(f"{host}: input {event.source.get('port')} active at {event.timestamp}")
                        elif event.topic.endswith("PTZReady"):
                            print(f"{host}: PTZ ready={event.data.get('ready')}")
                # The device closed the session normally (e.g. reboot): reconnect after a pause too.
            except (AuthError, AccessDenied, NotSupported) as e:
                print(f"{host}: giving up: {e}")  # retrying will not help
                return
            except (TransportError, Unavailable) as e:
                print(f"{host}: connection lost ({type(e).__name__})")
            print(f"{host}: reconnecting in {backoff:.0f} s")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def main() -> None:
    hosts = ["10.20.0.11", "10.20.0.12", "10.20.0.13"]
    # gather (not TaskGroup): one camera's failure must not cancel the others.
    results = await asyncio.gather(*(watch(h) for h in hosts), return_exceptions=True)
    for host, result in zip(hosts, results):
        if isinstance(result, Exception):
            print(f"{host}: watcher crashed: {result!r}")


if __name__ == "__main__":
    asyncio.run(main())
