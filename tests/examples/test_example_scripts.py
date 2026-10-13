"""Run every script in ``examples/`` against fake devices, so the examples cannot rot.

No network is used. ``Device`` and ``AsyncDevice`` are replaced (in the package
namespace the examples import from) by factories that hand out devices wired to
a ``MockCamera`` or a ``FakeWsCamera`` chosen by host name.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx
import pytest

import ax_devil_device_api
from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api.testing import MockCamera

sys.path.insert(0, str(Path(__file__).parents[1] / "unit"))
from ws_fake import FakeWsCamera, events_handler, notify  # noqa: E402

EXAMPLES = Path(__file__).parents[2] / "examples"

MQTT = "/axis-cgi/mqtt/client.cgi"
PUBLISHERS = "/config/rest/analytics-mqtt/v1/publishers"
PARAM = "/axis-cgi/param.cgi"
STATUS_ACTIVE = {"status": {"state": "active", "connectionStatus": "connected"}}
CONFIG = {
    "server": {"host": "broker.example", "protocol": "ssl", "port": 8883},
    "clientId": "ref",
    "username": "user",
    "password": "*****",
    "keepAliveInterval": 30,
}


class Fleet:
    """Maps host names to fake cameras and builds the devices the examples ask for."""

    def __init__(self) -> None:
        self.cameras: dict[str, MockCamera] = {}
        self.ws: dict[str, FakeWsCamera] = {}

    def add(self, host: str, camera: MockCamera | None = None) -> MockCamera:
        self.cameras[host] = camera or MockCamera()
        return self.cameras[host]

    def device(self, host: str, **kwargs: Any) -> Device:
        if host in self.ws:
            kwargs.pop("credentials", None)
            return Device(host, credentials=("root", "pass"), transport=self.ws[host].transport(), **kwargs)
        return self.cameras[host].device(host, **kwargs)

    def async_device(self, host: str, **kwargs: Any) -> AsyncDevice:
        if host in self.ws:
            kwargs.pop("credentials", None)
            return AsyncDevice(host, credentials=("root", "pass"), transport=self.ws[host].async_transport(), **kwargs)
        return self.cameras[host].async_device(host, **kwargs)


@pytest.fixture
def fleet(monkeypatch: pytest.MonkeyPatch) -> Fleet:
    fleet = Fleet()
    monkeypatch.setattr(ax_devil_device_api, "Device", fleet.device)
    monkeypatch.setattr(ax_devil_device_api, "AsyncDevice", fleet.async_device)
    monkeypatch.setenv("CAM_USER", "root")
    monkeypatch.setenv("CAM_PASS", "pass")
    monkeypatch.setenv("BROKER_PASS", "broker-secret")
    return fleet


@pytest.fixture
def load(fleet: Fleet) -> Iterator[Callable[[str], ModuleType]]:
    loaded: list[str] = []

    def _load(prefix: str) -> ModuleType:
        [path] = EXAMPLES.glob(f"{prefix}_*.py")
        name = f"example_{prefix}"
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        loaded.append(name)
        spec.loader.exec_module(module)
        return module

    yield _load
    for name in loaded:
        sys.modules.pop(name, None)


def test_every_example_is_covered() -> None:
    covered = {"01", "02", "03", "04", "05", "06", "07", "08", "09"}
    assert {p.name[:2] for p in EXAMPLES.glob("[0-9][0-9]_*.py")} == covered


class StopLoop(Exception):
    """Raised by a fake ``asyncio.sleep`` to end an example's endless loop."""


# -- 01 fleet rollout ----------------------------------------------------------


def test_01_fleet_rollout_classifies_each_camera(
    fleet: Fleet, load: Callable[[str], ModuleType], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("01")
    good = fleet.add("10.0.0.1")
    good.jsonrpc(MQTT, "configureClient")
    good.rest("GET", PUBLISHERS, data=[])
    good.rest("POST", PUBLISHERS, status=201)
    good.jsonrpc(MQTT, "activateClient")
    good.jsonrpc(MQTT, "getClientStatus", data=STATUS_ACTIVE)
    viewer = fleet.add("10.0.0.2")
    viewer.jsonrpc(MQTT, "configureClient", error=(2105, "Authorization failure"))
    monkeypatch.setattr(example, "CAMERAS", ["10.0.0.1", "10.0.0.2"])

    asyncio.run(example.main())

    out = capsys.readouterr().out
    assert "10.0.0.1" in out and "ok (connected)" in out
    assert "account lacks admin rights" in out
    [configure] = good.calls("configureClient")
    assert configure.json is not None and configure.json["params"]["clientId"] == "cam-10.0.0.1"
    [publisher] = [r for r in good.requests if r.method == "POST" and r.path == PUBLISHERS]
    assert publisher.json is not None
    assert viewer.calls("activateClient") == []


# -- 02 parameter drift --------------------------------------------------------


def test_02_parameter_drift_dry_run_and_apply(
    fleet: Fleet, load: Callable[[str], ModuleType], monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("02")
    camera = fleet.add("10.0.0.3")
    camera.cgi(PARAM, text="root.Network.Bonjour.Enabled=yes\nroot.Network.Bonjour.FriendlyName=cam\n", match={"action": "list"})
    camera.cgi(PARAM, text="OK", match={"action": "update"})
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"Network.Bonjour.Enabled": "no", "Network.Bonjour.FriendlyName": "cam", "Network.Nope": "x"}))

    def updates() -> list[Any]:
        return [r for r in camera.requests if "update" in (r.query.get("action"), (r.form or {}).get("action"))]

    monkeypatch.setattr(sys, "argv", ["02", "10.0.0.3", str(baseline)])
    example.main()
    out = capsys.readouterr().out
    assert "Network.Bonjour.Enabled: 'yes' -> 'no'" in out and "do not exist" in out
    assert updates() == []

    monkeypatch.setattr(sys, "argv", ["02", "10.0.0.3", str(baseline), "--apply"])
    example.main()
    assert "applied 1 change(s)" in capsys.readouterr().out
    [update] = updates()
    assert {**update.query, **(update.form or {})}["Network.Bonjour.Enabled"] == "no"


# -- 03 version-aware thermal ----------------------------------------------------

THERMO = "/axis-cgi/thermometry.cgi"


def thermal_camera(fleet: Fleet, host: str, versions: list[str]) -> MockCamera:
    camera = fleet.add(host)
    camera.api_list({"thermometry": versions[-1]})
    camera.jsonrpc(THERMO, "getSupportedVersions", data={"apiVersions": versions})
    camera.jsonrpc(
        THERMO,
        "getConfigurationCapabilities",
        data={
            "currentTemperatureScale": "celsius",
            "minTemperature": -40,
            "maxTemperature": 550,
            "maxNumberOfAreas": 5,
            "maxNumberOfVertices": 8,
            "maxDelayTime": 600,
            "defaultDelayTime": 0,
            "maxNameLength": 20,
        },
    )
    camera.jsonrpc(THERMO, "setIsothermLevels")
    return camera


def test_03_thermal_uses_floor_when_supported_and_falls_back_when_not(
    fleet: Fleet, load: Callable[[str], ModuleType], capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("03")
    new = thermal_camera(fleet, "10.0.0.4", ["1.0", "1.1", "1.2"])
    old = thermal_camera(fleet, "10.0.0.5", ["1.0", "1.1"])

    example.set_levels("10.0.0.4", low=20, middle=45, high=80, floor=5)
    example.set_levels("10.0.0.5", low=20, middle=45, high=80, floor=5)

    [call] = new.calls("setIsothermLevels")
    assert call.json is not None and call.json["params"]["min"] == 5
    [fallback] = old.calls("setIsothermLevels")
    assert fallback.json is not None and "min" not in fallback.json["params"]
    assert "setting levels without a floor" in capsys.readouterr().out


def test_03_thermal_skips_cameras_without_the_api(
    fleet: Fleet, load: Callable[[str], ModuleType], capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("03")
    camera = fleet.add("10.0.0.6")
    camera.api_list({"mqtt-client": "1.0"})
    camera.dca_apis({})
    camera.cgi(PARAM, text="")

    example.set_levels("10.0.0.6", low=20, middle=45, high=80, floor=5)

    assert "not a thermal camera" in capsys.readouterr().out
    assert camera.calls("setIsothermLevels") == []


# -- 04 recording a clip -----------------------------------------------------------


def test_04_clip_is_streamed_to_disk(
    fleet: Fleet, load: Callable[[str], ModuleType], monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("04")
    monkeypatch.setattr(example, "OUT", tmp_path / "clips")
    monkeypatch.setattr(example, "CLIP_BYTES", 1000)
    camera = fleet.add("10.0.0.7")
    camera.cgi("/axis-cgi/media.cgi", text=b"\x00" * 5000, content_type="video/mp4")
    broken = fleet.add("10.0.0.8")
    broken.cgi("/axis-cgi/media.cgi", text="nope", status=403)

    example.main(["10.0.0.7", "10.0.0.8"])

    clip = tmp_path / "clips" / "10.0.0.7.mp4"
    assert clip.exists() and clip.stat().st_size >= 1000
    assert not list((tmp_path / "clips").glob("*.part"))
    assert not (tmp_path / "clips" / "10.0.0.8.mp4").exists()
    out = capsys.readouterr().out
    assert "video/mp4" in out and "10.0.0.8: failed" in out
    assert camera.requests[0].query["container"] == "mp4"


# -- 05 event watch ----------------------------------------------------------------


def test_05_event_watch_prints_events_and_reconnects(
    fleet: Fleet, load: Callable[[str], ModuleType], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("05")

    def on_message(socket: Any, message: Any) -> None:
        events_handler(socket, message)
        if message.get("method") == "events:configure":
            socket.push(notify("tns1:Device/tnsaxis:IO/Port", state="1"))
            socket.push(notify("tns1:PTZController/tnsaxis:PTZReady", ready="1"))
            socket.close()  # normal end: the example reconnects after a pause

    camera = FakeWsCamera(handler=on_message)
    fleet.ws["10.0.0.9"] = camera
    sleeps: list[float] = []
    real_sleep = asyncio.sleep

    async def fake_sleep(seconds: float) -> None:
        if seconds != 1.0 and seconds != 2.0:  # not the example's reconnect pause (the library backs off too)
            return await real_sleep(0)
        sleeps.append(seconds)
        if len(sleeps) == 2:
            raise StopLoop

    monkeypatch.setattr(example.asyncio, "sleep", fake_sleep)

    with pytest.raises(StopLoop):
        asyncio.run(example.watch("10.0.0.9"))

    out = capsys.readouterr().out
    assert "input 1 active" in out and "PTZ ready=1" in out
    assert "reconnected after" in out  # the second session reports the gap
    assert len(camera.ws_requests) == 2


def test_05_event_watch_gives_up_on_refused_access(
    fleet: Fleet, load: Callable[[str], ModuleType], capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("05")
    fleet.ws["10.0.0.10"] = FakeWsCamera(refuse=403)

    asyncio.run(example.watch("10.0.0.10"))

    assert "giving up" in capsys.readouterr().out


# -- 06 debugging ---------------------------------------------------------------------


def test_06_debugging_shows_redacted_requests_and_error_fields(
    fleet: Fleet, load: Callable[[str], ModuleType], capsys: pytest.CaptureFixture[str]
) -> None:
    camera = fleet.add("192.168.0.90")
    camera.jsonrpc(MQTT, "configureClient", error=(2104, "Invalid parameter value specified"))
    camera.identity(model="AXIS Q1656", firmware="11.9.0", serial="ACCC8E000001")
    camera.api_list({"mqtt-client": "1.0"})
    camera.dca_apis({"analytics-mqtt": ["v1"]})
    camera.cgi(PARAM, text="")

    load("06")

    out = capsys.readouterr().out
    assert "refused as expected" in out
    assert "<redacted>" in out and "hunter2" not in out
    assert "api error 2104" in out
    assert "caught locally" in out
    assert "1 classic APIs, 1 configuration APIs" in out


# -- 07 long-running service --------------------------------------------------------------


def test_07_monitor_polls_and_survives_failures(
    fleet: Fleet, load: Callable[[str], ModuleType], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("07")
    up = fleet.add("10.0.1.1")
    up.identity(model="AXIS M3068", firmware="11.9.0")
    up.jsonrpc(MQTT, "getClientStatus", data=STATUS_ACTIVE)
    down = fleet.add("10.0.1.2")
    down.identity()
    down.fail("/axis-cgi/basicdeviceinfo.cgi", httpx.ConnectError)
    sleeps: list[float] = []

    real_sleep = asyncio.sleep

    async def fake_sleep(seconds: float) -> None:
        if seconds != example.POLL:  # the library's own retry backoff keeps running
            return await real_sleep(0)
        sleeps.append(seconds)
        raise StopLoop

    monkeypatch.setattr(example.asyncio, "sleep", fake_sleep)

    async def run() -> None:
        monitor = example.Monitor("root", "pass")
        monitor.add("10.0.1.1")
        monitor.add("10.0.1.2")
        try:
            with pytest.raises(StopLoop):
                await monitor.run()
            await monitor.change_password("10.0.1.1", "new-pass")
        finally:
            for host in list(monitor.cameras):
                await monitor.remove(host)

    asyncio.run(run())

    out = capsys.readouterr().out
    assert "online" in out and "fw=11.9.0" in out and "mqtt=connected" in out
    assert "OFFLINE" in out
    assert sleeps == [example.POLL]


# -- 08 clone configuration -----------------------------------------------------------------


def test_08_clone_keeps_reference_password_and_supplies_one_for_targets(
    fleet: Fleet, load: Callable[[str], ModuleType], capsys: pytest.CaptureFixture[str]
) -> None:
    example = load("08")
    reference = fleet.add("10.0.2.1")
    reference.jsonrpc(MQTT, "getClientStatus", data={**STATUS_ACTIVE, "config": CONFIG})
    reference.jsonrpc(MQTT, "configureClient")
    reference.rest("GET", PUBLISHERS, data=[{"id": "scene", "data_source_key": "tns1:Foo", "mqtt_topic": "a/b", "qos": 1}])
    target = fleet.add("10.0.2.2")
    target.rest("GET", PUBLISHERS, data=[])
    target.rest("POST", PUBLISHERS, status=201)
    target.jsonrpc(MQTT, "configureClient")
    target.jsonrpc(MQTT, "activateClient")

    example.main("10.0.2.1", ["10.0.2.2"])

    [tweak] = reference.calls("configureClient")
    assert tweak.json is not None
    assert tweak.json["params"]["keepAliveInterval"] == 15 and tweak.json["params"]["keepExistingPassword"] is True
    assert "password" not in tweak.json["params"]
    [clone] = target.calls("configureClient")
    assert clone.json is not None
    assert clone.json["params"]["password"] == "broker-secret" and clone.json["params"]["clientId"] == "cam-10-0-2-2"
    assert len(target.calls("activateClient")) == 1
    assert [r for r in target.requests if r.method == "POST" and r.path == PUBLISHERS]
    assert "cloned 1 publisher(s)" in capsys.readouterr().out


# -- 09 testing your code ---------------------------------------------------------------------


def test_09_example_tests_pass(load: Callable[[str], ModuleType]) -> None:
    example = load("09")
    example.test_inactive_client_is_activated()
    example.test_active_client_is_left_alone()
    example.test_viewer_account_is_reported()
    example.test_camera_that_refuses_connections_is_retried_once()
