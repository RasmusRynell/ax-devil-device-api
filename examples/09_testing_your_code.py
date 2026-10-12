"""Unit-test your own camera code without a camera, using ``MockCamera``.

``MockCamera`` answers the routes you register, records every request, and
plugs into ``Device``/``AsyncDevice`` in place of the network. Run with
``pytest 09_testing_your_code.py``.

Status: runs today.
"""

import httpx
import pytest

from ax_devil_device_api import Device
from ax_devil_device_api.errors import AccessDenied
from ax_devil_device_api.testing import MockCamera

MQTT = "/axis-cgi/mqtt/client.cgi"


# --- the application code under test -----------------------------------------


def ensure_mqtt_connected(dev: Device) -> str:
    """Activate the MQTT client if needed; return a status line for a dashboard."""
    status = dev.apis.mqtt_client.get_client_status()
    if status.status.state == "inactive":
        dev.apis.mqtt_client.activate_client()
        return "activated"
    return status.status.connection_status


# --- tests -------------------------------------------------------------------


def status(state: str, connection: str) -> dict:
    return {"status": {"state": state, "connectionStatus": connection}}


def test_inactive_client_is_activated() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=status("inactive", "disconnected"))
    camera.jsonrpc(MQTT, "activateClient", data={})

    with camera.device() as dev:
        assert ensure_mqtt_connected(dev) == "activated"

    assert len(camera.calls("activateClient")) == 1


def test_active_client_is_left_alone() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=status("active", "connected"))

    with camera.device() as dev:
        assert ensure_mqtt_connected(dev) == "connected"

    assert camera.calls("activateClient") == []


def test_viewer_account_is_reported() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", error=(2105, "Authorization failure"))

    with camera.device() as dev, pytest.raises(AccessDenied):
        ensure_mqtt_connected(dev)


def test_camera_that_refuses_connections_is_retried_once() -> None:
    camera = MockCamera()
    camera.jsonrpc(MQTT, "getClientStatus", data=status("active", "connected"))
    camera.fail(MQTT, httpx.ConnectError, times=1)  # e.g. still booting

    with camera.device() as dev:
        assert ensure_mqtt_connected(dev) == "connected"
