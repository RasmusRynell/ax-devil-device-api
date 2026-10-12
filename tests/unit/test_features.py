"""features/: registry, device summary and support overview."""

from __future__ import annotations

import pytest

from ax_devil_device_api import Support
from ax_devil_device_api.features import (
    api_names,
    api_support,
    async_api_support,
    async_device_summary,
    device_summary,
    load_api,
    supported_apis,
)
from ax_devil_device_api.testing import MockCamera


def camera() -> MockCamera:
    cam = MockCamera()
    cam.identity(model="AXIS Q1656", firmware="11.9.1", serial="ABC")
    cam.api_list({"mqtt-client": "1.0"})
    cam.dca_apis({"analytics-mqtt": ["v1"]})
    return cam


def test_registry_describes_generated_modules() -> None:
    assert "mqtt_client" in api_names()
    entry = load_api("mqtt_client")
    assert entry.info.id == "mqtt-client"
    assert "get_client_status" in entry.operations
    assert entry.sync_class.__name__ == "MqttClientApi"
    assert entry.async_class.__name__ == "AsyncMqttClientApi"
    with pytest.raises(KeyError):
        load_api("nope")


def test_device_summary_sync() -> None:
    with camera().device() as dev:
        s = device_summary(dev)
    assert (s.model, s.firmware_version, s.serial_number) == ("AXIS Q1656", "11.9.1", "ABC")
    assert s.classic_apis == {"mqtt-client": "1.0"}
    assert s.dca_apis == {"analytics-mqtt": ("v1",)}
    assert s.to_dict()["observed_at"]


@pytest.mark.anyio
async def test_device_summary_async_matches_sync() -> None:
    async with camera().async_device() as dev:
        s = await async_device_summary(dev)
    assert s.model == "AXIS Q1656" and s.classic_apis == {"mqtt-client": "1.0"}


def test_supported_apis_lists_only_yes() -> None:
    with camera().device() as dev:
        names = supported_apis(dev)
        results = api_support(dev, [load_api("mqtt_client")])
    assert "mqtt_client" in names
    assert results["mqtt_client"].status is Support.YES


@pytest.mark.anyio
async def test_async_api_support() -> None:
    async with camera().async_device() as dev:
        results = await async_api_support(dev, [load_api("mqtt_client")])
    assert results["mqtt_client"].status is Support.YES


JPEG = b"\xff\xd8\xff\xe0fakejpeg\xff\xd9"


def test_snapshot_sync_sends_options() -> None:
    from ax_devil_device_api.features import snapshot

    cam = MockCamera()
    cam.cgi("/axis-cgi/jpg/image.cgi", text=JPEG, content_type="image/jpeg")
    with cam.device() as dev:
        data = snapshot(dev, resolution="640x480", compression=30, rotation=90)
    assert data == JPEG
    query = [r for r in cam.requests if r.path.endswith("image.cgi")][-1].query
    assert query == {"resolution": "640x480", "compression": "30", "rotation": "90"}


@pytest.mark.anyio
async def test_snapshot_async_defaults_send_no_arguments() -> None:
    from ax_devil_device_api.features import async_snapshot

    cam = MockCamera()
    cam.cgi("/axis-cgi/jpg/image.cgi", text=JPEG, content_type="image/jpeg")
    async with cam.async_device() as dev:
        assert await async_snapshot(dev) == JPEG
    assert [r for r in cam.requests if r.path.endswith("image.cgi")][-1].query == {}


def test_snapshot_rejects_invalid_option() -> None:
    from pydantic import ValidationError

    from ax_devil_device_api.features import snapshot

    with camera().device() as dev, pytest.raises(ValidationError):
        snapshot(dev, compression=101)
