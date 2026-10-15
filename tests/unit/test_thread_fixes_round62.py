"""A version the device reports in a form this client cannot read is UNKNOWN (never a mismatch), uncached, with a
diagnostic; a later readable value is probed again and gives YES."""

from __future__ import annotations

import httpx
import pytest

from ax_devil_device_api import Support
from ax_devil_device_api._protocols.base import ApiInfo, DcaDiscovery, Family
from ax_devil_device_api._runtime.capabilities import readable_version
from ax_devil_device_api.apis.audio_control_service import AudioControlServiceApi
from ax_devil_device_api.apis.heartbeat import AsyncHeartbeatApi, HeartbeatApi
from ax_devil_device_api.testing import MockCamera

PARAM = "/axis-cgi/param.cgi"
UNREADABLE = ["²", "１.０", "١.٠", "garbage", "", " ", "1..0", "1.0.", ".1", "1.0-beta", "9" * 5000, "².³", "1,0"]


def _properties(camera: MockCamera, **values: str) -> None:
    text = "".join(f"root.Properties.API.{name}.Version={value}\n" for name, value in values.items())
    camera.cgi(PARAM, text=text)


def test_readable_version_is_ascii_dotted_numbers_only() -> None:
    for good in ("1", "1.0", "1.20", "10.12.213", " 2.0 "):
        assert readable_version(good), good
    for bad in UNREADABLE:
        assert not readable_version(bad), bad


@pytest.mark.parametrize("value", UNREADABLE, ids=lambda v: repr(v)[:14])
def test_an_unreadable_version_property_is_unknown_uncached_and_a_later_value_is_probed_again(value: str) -> None:
    camera = MockCamera()
    _properties(camera, Heartbeat=value)
    with camera.device() as dev:
        result = dev.supports(HeartbeatApi)
        assert result.status is Support.UNKNOWN and any("Heartbeat.Version" in error and "readable version" in error for error in result.errors)
        assert dev._state.get("properties") is None  # noqa: SLF001 - not cached
        _properties(camera, Heartbeat="1.0")
        assert dev.supports(HeartbeatApi).status is Support.YES  # re-probed
        assert dev._state.get("properties") is not None  # noqa: SLF001 - now cached


@pytest.mark.parametrize("value", ["²", "garbage", "３"], ids=repr)
def test_an_unreadable_equality_version_is_unknown_not_no(value: str) -> None:
    camera = MockCamera()
    _properties(camera, AudioControl=value)
    with camera.device() as dev:
        assert dev.supports(AudioControlServiceApi).status is Support.UNKNOWN
        _properties(camera, AudioControl="1.0")
        assert dev.supports(AudioControlServiceApi).status is Support.YES


def test_a_readable_but_different_version_is_still_no() -> None:
    camera = MockCamera()
    _properties(camera, AudioControl="2.0")
    with camera.device() as dev:
        assert dev.supports(AudioControlServiceApi).status is Support.NO


@pytest.mark.anyio
@pytest.mark.parametrize("value", ["²", "garbage"], ids=repr)
async def test_async_an_unreadable_version_property_is_unknown_and_re_probed(value: str) -> None:
    camera = MockCamera()
    _properties(camera, Heartbeat=value)
    async with camera.async_device() as dev:
        assert (await dev.supports(AsyncHeartbeatApi)).status is Support.UNKNOWN
        _properties(camera, Heartbeat="1.0")
        assert (await dev.supports(AsyncHeartbeatApi)).status is Support.YES


# -- Device Configuration discovery: the version names ----------------------------------------------------------------------


@pytest.mark.parametrize("name", ["²", "ｖ１", "garbage", "v", "V1", "v1 ", ""], ids=repr)
def test_an_unreadable_dca_version_name_is_unknown_and_not_cached(name: str) -> None:
    from ax_devil_device_api._runtime.capabilities import decide_support

    info = ApiInfo(id="a", name="a", family=Family.DCA, discovery=(DcaDiscovery("a", "v1"),))
    camera = MockCamera()
    camera.route("GET", "/config/discover", lambda _: httpx.Response(200, json={"apis": {"a": {name: {}}}}))
    with camera.device() as dev:
        caps = dev.capabilities()
        assert decide_support(info, caps).status is Support.UNKNOWN and caps.errors.get("dca_apis[a]")
        assert dev._state.get("dca_apis") is None  # noqa: SLF001
        camera.dca_apis({"a": ["v1"]})
        assert decide_support(info, dev.capabilities()).status is Support.YES


def test_readable_dca_version_names_are_accepted() -> None:
    from ax_devil_device_api._runtime.capabilities import decide_support

    info = ApiInfo(id="a", name="a", family=Family.DCA, discovery=(DcaDiscovery("a", "v2beta"),))
    camera = MockCamera()
    camera.dca_apis({"a": ["v1", "v2beta", "v1alpha1"]})
    with camera.device() as dev:
        assert decide_support(info, dev.capabilities()).status is Support.YES


# -- identity: an unreadable firmware is not cached ----------------------------------------------------------------------


def test_an_unreadable_firmware_is_not_cached_and_a_later_value_is_read() -> None:
    camera = MockCamera()
    camera.identity(firmware="².³")
    with camera.device() as dev:
        assert dev.identity().firmware_version == "².³"
        assert dev._state.get("identity") is None  # noqa: SLF001
        camera.identity(firmware="11.9.0")
        assert dev.identity().firmware_version == "11.9.0"
        assert dev._state.get("identity") is not None  # noqa: SLF001


# -- round 40: firmware must be a well-formed dotted version; cacheability never depends on a property's name -------------

from ax_devil_device_api._runtime.capabilities import firmware_key  # noqa: E402
from ax_devil_device_api.apis.geolocation import AsyncGeolocationApi, GeolocationApi  # noqa: E402
from ax_devil_device_api.apis.osdi import AsyncOnScreenDirectionalIndicatorApi, OnScreenDirectionalIndicatorApi  # noqa: E402

BAD_FIRMWARE = ["1..0", "1.0.", ".1", "", "  ", "\t", "².³", "１.０", "garbage", "-1", "1,0", "9" * 5000 + ".0", "v11.9"]


def test_firmware_key_needs_a_well_formed_dotted_version() -> None:
    assert firmware_key("11.9.0") == (11, 9, 0) and firmware_key(" 9.80.1.1 ") == (9, 80, 1, 1) and firmware_key("11.5") == (11, 5)
    assert firmware_key("11.9.0-beta") == (11, 9, 0) and firmware_key("10.12 (build 4)") == (10, 12)
    for bad in BAD_FIRMWARE:
        assert firmware_key(bad) is None, bad


def _geo(camera: MockCamera, firmware: str) -> None:
    camera.identity(firmware=firmware)
    camera.cgi(PARAM, text="root.Properties.Geolocation.Geolocation=yes\nroot.Properties.Geolocation.Version=0.01\n")


@pytest.mark.parametrize("firmware", BAD_FIRMWARE, ids=lambda v: repr(v)[:14])
def test_an_unreadable_firmware_gates_to_unknown_uncached_and_a_correction_is_read(firmware: str) -> None:
    camera = MockCamera()
    _geo(camera, firmware)
    with camera.device() as dev:
        result = dev.supports(GeolocationApi)
        assert result.status is Support.UNKNOWN, result
        assert dev._state.get("identity") is None  # noqa: SLF001
        _geo(camera, "11.9.0")
        assert dev.supports(GeolocationApi).status is Support.YES
        assert dev._state.get("identity") is not None  # noqa: SLF001


@pytest.mark.anyio
@pytest.mark.parametrize("firmware", ["1..0", "", "  "], ids=repr)
async def test_async_an_unreadable_firmware_is_unknown_and_re_read(firmware: str) -> None:
    camera = MockCamera()
    _geo(camera, firmware)
    async with camera.async_device() as dev:
        assert (await dev.supports(AsyncGeolocationApi)).status is Support.UNKNOWN
        _geo(camera, "11.9.0")
        assert (await dev.supports(AsyncGeolocationApi)).status is Support.YES


def test_a_readable_old_firmware_is_still_no() -> None:
    camera = MockCamera()
    _geo(camera, "6.10.0")
    with camera.device() as dev:
        assert dev.supports(GeolocationApi).status is Support.NO


def test_a_garbage_value_of_a_property_not_named_version_is_unknown_and_re_probed() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="root.PTZ.Locator.L0.MaxZones=garbage\n")
    with camera.device() as dev:
        result = dev.supports(OnScreenDirectionalIndicatorApi)
        assert result.status is Support.UNKNOWN and any("MaxZones" in error for error in result.errors)
        camera.cgi(PARAM, text="root.PTZ.Locator.L0.MaxZones=8\n")
        assert dev.supports(OnScreenDirectionalIndicatorApi).status is Support.YES


@pytest.mark.anyio
async def test_async_a_garbage_value_of_a_property_not_named_version_is_re_probed() -> None:
    camera = MockCamera()
    camera.cgi(PARAM, text="root.PTZ.Locator.L0.MaxZones=garbage\n")
    async with camera.async_device() as dev:
        assert (await dev.supports(AsyncOnScreenDirectionalIndicatorApi)).status is Support.UNKNOWN
        camera.cgi(PARAM, text="root.PTZ.Locator.L0.MaxZones=8\n")
        assert (await dev.supports(AsyncOnScreenDirectionalIndicatorApi)).status is Support.YES
