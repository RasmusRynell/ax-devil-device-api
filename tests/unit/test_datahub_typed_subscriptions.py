"""The generated Data Hub connect() accepts Subscription objects as well as mappings (pyright checks these calls)."""

from __future__ import annotations

from typing import Any

from ws_fake import FakeSocket, FakeWsCamera

from ax_devil_device_api import Device
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api.apis.device_data_hub_ws import Filter, Subscription


def _handler(socket: FakeSocket, message: Any) -> None:
    socket.push({"jsonrpc": "2.0", "id": message["id"], "result": {"subscriptionId": message["params"]["subscriptionId"]}})


def test_connect_takes_subscription_objects_and_mappings_together() -> None:
    camera = FakeWsCamera(handler=_handler)
    dev = Device("cam.test", credentials=("root", "pass"), transport=camera.transport())
    typed = Subscription(subscription_id="s1", filters=[Filter(topics=["t1"])])
    with dev.apis.device_data_hub_ws.connect([typed, {"subscriptionId": "s2", "filters": [{"topics": ["t2"]}]}], heartbeat=Heartbeat(None)):
        pass
    sent = [m for m in camera.sockets[0].received if m.get("method") == "data-hub_v1:subscribe"]
    assert [m["params"]["subscriptionId"] for m in sent] == ["s1", "s2"]
