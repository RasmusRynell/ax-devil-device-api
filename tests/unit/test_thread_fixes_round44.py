"""Discovery lists: every advertised version counts; malformed entries (classic apiList and /config/discover share one
rule) make the affected API unknown, are recorded, and keep the probe from being cached."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ax_devil_device_api import Support
from ax_devil_device_api._protocols.base import ApiDiscovery, ApiInfo, DcaDiscovery, Family
from ax_devil_device_api._runtime.capabilities import decide_support
from ax_devil_device_api.testing import MockCamera

DISCOVERY = "/axis-cgi/apidiscovery.cgi"
CLASSIC = ApiInfo(id="mqtt-client", name="m", family=Family.JSONRPC, major=1, discovery=(ApiDiscovery("mqtt-client"),))
OTHER = ApiInfo(id="other", name="o", family=Family.JSONRPC, major=1, discovery=(ApiDiscovery("other"),))
DCA = ApiInfo(id="analytics-mqtt", name="a", family=Family.DCA, discovery=(DcaDiscovery("analytics-mqtt", "v1"),))
DCA_OTHER = ApiInfo(id="other", name="o", family=Family.DCA, discovery=(DcaDiscovery("other", "v1"),))


def _classic(entries: list[Any]) -> MockCamera:
    camera = MockCamera()
    camera.jsonrpc(DISCOVERY, "getApiList", data={"apiList": entries})
    return camera


def _calls(camera: MockCamera, path: str) -> int:
    return sum(1 for request in camera.requests if request.path == path)


# -- U: several advertised versions ----------------------------------------------------------------------------------


@pytest.mark.parametrize("versions", [["1.0", "2.0"], ["2.0", "1.0"], ["2.0", "1.0", "3.1"]])
def test_any_advertised_version_that_fits_the_major_answers_yes(versions: list[str]) -> None:
    camera = _classic([{"id": "mqtt-client", "version": v} for v in versions])
    with camera.device() as dev:
        caps = dev.capabilities()
    result = decide_support(CLASSIC, caps)
    assert result.status is Support.YES and "1.0" in result.reason


def test_only_other_majors_advertised_is_a_definitive_no() -> None:
    camera = _classic([{"id": "mqtt-client", "version": "2.0"}, {"id": "mqtt-client", "version": "3.0"}])
    with camera.device() as dev:
        result = decide_support(CLASSIC, dev.capabilities())
    assert result.status is Support.NO and "2.0" in result.reason and "3.0" in result.reason


# -- V: malformed classic entries ---------------------------------------------------------------------------------------

MALFORMED_READABLE = [
    {"id": "mqtt-client"},
    {"id": "mqtt-client", "version": 1.0},
    {"id": "mqtt-client", "version": ""},
    {"id": "mqtt-client", "version": None},
]
MALFORMED_UNREADABLE = [{"version": "1.0"}, {"id": 5, "version": "1.0"}, {"id": "", "version": "1.0"}, "text", 7, None, ["x"]]


@pytest.mark.parametrize("bad", MALFORMED_READABLE)
def test_a_malformed_classic_entry_with_a_readable_id_makes_that_api_unknown(bad: Any) -> None:
    camera = _classic([bad, {"id": "other", "version": "1.2"}])
    with camera.device() as dev:
        caps = dev.capabilities()
        first = _calls(camera, DISCOVERY)
        dev.capabilities()
        assert _calls(camera, DISCOVERY) == first + 1  # not cached as definitive: asked again
    assert "classic_apis[mqtt-client]" in caps.errors
    unknown = decide_support(CLASSIC, caps)
    assert unknown.status is Support.UNKNOWN and unknown.errors  # never a definitive NO
    assert decide_support(OTHER, caps).status is Support.YES  # the well-formed entry still counts


@pytest.mark.parametrize("bad", MALFORMED_UNREADABLE, ids=[repr(b) for b in MALFORMED_UNREADABLE])
def test_an_unreadable_classic_entry_is_recorded_and_not_cached(bad: Any) -> None:
    camera = _classic([bad, {"id": "other", "version": "1.2"}])
    with camera.device() as dev:
        caps = dev.capabilities()
        first = _calls(camera, DISCOVERY)
        dev.capabilities()
        assert _calls(camera, DISCOVERY) == first + 1
    assert any(key.startswith("classic_apis[<entry") for key in caps.errors)
    assert decide_support(OTHER, caps).status is Support.YES


def test_a_well_formed_classic_list_is_cached() -> None:
    camera = _classic([{"id": "mqtt-client", "version": "1.0"}])
    with camera.device() as dev:
        dev.capabilities()
        first = _calls(camera, DISCOVERY)
        dev.capabilities()
        assert _calls(camera, DISCOVERY) == first


# -- the same rule on /config/discover ----------------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [["v1"], "v1", None, 5, True])
def test_a_malformed_dca_entry_follows_the_same_rule(bad: Any) -> None:
    camera = MockCamera()
    camera.route("GET", "/config/discover", lambda _: httpx.Response(200, json={"apis": {"analytics-mqtt": bad, "other": {"v1": {}}}}))
    with camera.device() as dev:
        caps = dev.capabilities()
        first = _calls(camera, "/config/discover")
        dev.capabilities()
        assert _calls(camera, "/config/discover") == first + 1
    assert "dca_apis[analytics-mqtt]" in caps.errors
    assert decide_support(DCA, caps).status is Support.UNKNOWN
    assert decide_support(DCA_OTHER, caps).status is Support.YES
