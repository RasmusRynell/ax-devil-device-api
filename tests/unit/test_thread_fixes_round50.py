"""Short-circuit only on pre-send failures; gap coverage per setup; unrelated documents are not empty listings."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from ws_fake import FakeSocket, FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device, Support
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._protocols.base import AcapDiscovery, ApiInfo, DcaDiscovery, Family, ServiceDiscovery
from ax_devil_device_api._runtime.capabilities import decide_support
from ax_devil_device_api._runtime.ws import DATA_HUB, EVENTS
from ax_devil_device_api._runtime.ws_codecs import EventFilter
from ax_devil_device_api.testing import MockCamera

QUICK = Heartbeat(None)
DISCOVERY = "/axis-cgi/apidiscovery.cgi"


def _requests(camera: MockCamera, path: str) -> int:
    return sum(1 for r in camera.requests if r.path == path)


# -- 1: only a failure before anything was sent says the device is out of reach --------------------------------------------


def test_sync_a_reset_after_the_request_was_sent_fails_only_that_probe() -> None:
    camera = MockCamera()
    camera.fail(DISCOVERY, httpx.ReadError)  # the request left; the connection then broke
    camera.dca_apis({"analytics-mqtt": ["v1"]})
    camera.cgi("/axis-cgi/param.cgi", text="root.Properties.API.HTTP.Version=3\n")
    with camera.device() as dev:
        caps = dev.capabilities()
    assert "classic_apis" in caps.errors and "skipped" not in caps.errors["classic_apis"]
    assert caps.dca_apis == {"analytics-mqtt": frozenset({"v1"})}  # the later probes ran
    assert caps.properties is not None and "dca_apis" not in caps.errors and "properties" not in caps.errors


def test_sync_a_refusal_before_sending_still_short_circuits() -> None:
    camera = MockCamera()
    camera.fail(DISCOVERY, httpx.ConnectError)
    camera.dca_apis({"analytics-mqtt": ["v1"]})
    with camera.device() as dev:
        caps = dev.capabilities()
    assert "skipped" in caps.errors["dca_apis"] and "skipped" in caps.errors["properties"]
    assert _requests(camera, "/config/discover") == 0  # not even asked


@pytest.mark.anyio
async def test_async_a_reset_after_send_fails_only_that_probe_and_a_refusal_short_circuits() -> None:
    camera = MockCamera()
    camera.fail(DISCOVERY, httpx.ReadError)
    camera.dca_apis({"analytics-mqtt": ["v1"]})
    camera.cgi("/axis-cgi/param.cgi", text="root.Properties.API.HTTP.Version=3\n")
    async with camera.async_device() as dev:
        caps = await dev.capabilities()
    assert caps.dca_apis == {"analytics-mqtt": frozenset({"v1"})} and caps.properties is not None
    refused = MockCamera()
    refused.fail(DISCOVERY, httpx.ConnectError)
    refused.dca_apis({"analytics-mqtt": ["v1"]})
    async with refused.async_device(max_concurrency=1) as dev:  # probes run one after another
        caps = await dev.capabilities()
    assert "skipped" in caps.errors["dca_apis"] and _requests(refused, "/config/discover") == 0


# -- 2: the gap ledger key includes the setup ----------------------------------------------------------------------------------


def _hub_handler(socket: FakeSocket, message: Any) -> None:
    if message.get("method", "").startswith("data-hub_v1:"):
        socket.push({"jsonrpc": "2.0", "id": message["id"], "result": {}})


def _events_handler(socket: FakeSocket, message: Any) -> None:
    socket.push({"apiVersion": "1.0", "context": message["context"], "method": message["method"], "data": {}})


def _gaps(spec: Any, handler: Any, option: str, a: Any, b: Any) -> dict[str, bool]:
    camera = FakeWsCamera(handler=handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), max_streams=4) as dev:
        with dev.connect_session(spec, heartbeat=QUICK, **{option: a}):
            pass
        with dev.connect_session(spec, heartbeat=QUICK, **{option: b}) as other:
            other_gap = other.gap is not None
        with dev.connect_session(spec, heartbeat=QUICK, **{option: a}) as same:
            same_gap = same.gap is not None
    return {"different": other_gap, "identical": same_gap}


def test_events_sessions_with_different_filters_do_not_share_coverage() -> None:
    a = [EventFilter(topic_filter="tns1:A")]
    b = [{"topicFilter": "tns1:B"}]
    result = _gaps(EVENTS, _events_handler, "event_filter_list", a, b)
    assert result == {"different": False, "identical": True}  # B has no history; A's own history is kept


def test_events_filters_that_are_the_same_in_another_spelling_share_coverage() -> None:
    result = _gaps(EVENTS, _events_handler, "event_filter_list", [EventFilter(topic_filter="tns1:A")], [{"topicFilter": "tns1:A"}])
    assert result == {"different": True, "identical": True}


def test_data_hub_sessions_with_different_subscriptions_do_not_share_coverage() -> None:
    a = [{"subscriptionId": "s", "filters": [{"topics": ["topic.a"]}]}]
    b = [{"subscriptionId": "s", "filters": [{"topics": ["topic.b"]}]}]
    assert _gaps(DATA_HUB, _hub_handler, "subscriptions", a, b) == {"different": False, "identical": True}
    same_but_reordered_keys = [{"filters": [{"topics": ["topic.a"]}], "subscriptionId": "s"}]
    assert _gaps(DATA_HUB, _hub_handler, "subscriptions", a, same_but_reordered_keys) == {"different": True, "identical": True}


@pytest.mark.anyio
async def test_async_events_sessions_with_different_filters_do_not_share_coverage() -> None:
    camera = FakeWsCamera(handler=_events_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport(), max_streams=4) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=[{"topicFilter": "A"}]):
            pass
        async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=[{"topicFilter": "B"}]) as other:
            assert other.gap is None
        async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=[{"topicFilter": "A"}]) as same:
            assert same.gap is not None


# -- 3: an unrelated document is not an empty listing -----------------------------------------------------------------------------

ACAP = ApiInfo(id="a", name="a", family=Family.CGI, discovery=(AcapDiscovery("a"),))
SERVICE = ApiInfo(id="a", name="a", family=Family.SOAP, discovery=(ServiceDiscovery("urn:a"),))


@pytest.mark.parametrize("body", [b"<html/>", b"<html><body>Login</body></html>", b"<replies/>", b"<Envelope/>"])
def test_an_unrelated_applications_document_is_unknown_and_uncached(body: bytes) -> None:
    camera = MockCamera()
    camera.cgi("/axis-cgi/applications/list.cgi", text=body, content_type="text/xml")
    with camera.device() as dev:
        caps = dev._collect(("applications",))  # noqa: SLF001
        assert decide_support(ACAP, caps).status is Support.UNKNOWN
        assert dev._state.get("applications") is None  # noqa: SLF001


def test_an_empty_but_genuine_applications_reply_is_a_definitive_empty_list() -> None:
    camera = MockCamera()
    camera.cgi("/axis-cgi/applications/list.cgi", text=b'<reply result="ok"/>', content_type="text/xml")
    with camera.device() as dev:
        caps = dev._collect(("applications",))  # noqa: SLF001
        assert decide_support(ACAP, caps).status is Support.NO  # genuinely nothing installed
        assert dev._state.get("applications") is not None  # noqa: SLF001


@pytest.mark.parametrize("body", [b"<html/>", b"<reply/>", b"<html><Service><Namespace>urn:a</Namespace></Service></html>"])
def test_an_unrelated_services_document_is_unknown_and_uncached(body: bytes) -> None:
    camera = MockCamera()
    camera.route("POST", "/vapix/services", lambda _: httpx.Response(200, content=body))
    with camera.device() as dev:
        caps = dev._collect(("services",))  # noqa: SLF001
        assert decide_support(SERVICE, caps).status is Support.UNKNOWN
        assert dev._state.get("services") is None  # noqa: SLF001


@pytest.mark.parametrize("payload", [{"other": 1}, [], "x", {"apis": None}, {"apis": []}])
def test_a_wrong_shape_discovery_document_is_unknown_and_uncached(payload: Any) -> None:
    dca = ApiInfo(id="a", name="a", family=Family.DCA, discovery=(DcaDiscovery("a", "v1"),))
    camera = MockCamera()
    camera.route("GET", "/config/discover", lambda _: httpx.Response(200, json=payload))
    with camera.device() as dev:
        caps = dev.capabilities()
        assert decide_support(dca, caps).status is Support.UNKNOWN
        assert dev._state.get("dca_apis") is None  # noqa: SLF001


@pytest.mark.parametrize("data", [{"other": 1}, [], "x", {"apiList": None}, {"apiList": {}}])
def test_a_wrong_shape_api_list_is_unknown_and_uncached(data: Any) -> None:
    from ax_devil_device_api._protocols.base import ApiDiscovery

    classic = ApiInfo(id="a", name="a", family=Family.JSONRPC, major=1, discovery=(ApiDiscovery("a"),))
    camera = MockCamera()
    camera.jsonrpc(DISCOVERY, "getApiList", data=data)
    with camera.device() as dev:
        caps = dev.capabilities()
        assert decide_support(classic, caps).status is Support.UNKNOWN
        assert dev._state.get("classic_apis") is None  # noqa: SLF001
