"""Correlated WebSocket messages always resolve their waiter; capability values are plain data; identity values are text."""

from __future__ import annotations

import copy
import dataclasses
import pickle
from typing import Any

import anyio
import pytest
from ws_fake import FakeSocket, FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device, Support
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._protocols.base import ApiDiscovery, ApiInfo, Family
from ax_devil_device_api._runtime.capabilities import Advertised, decide_support
from ax_devil_device_api._runtime.ws import DATA_HUB, EVENTS
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventsCodec
from ax_devil_device_api.apis.scene_profile import SceneProfileApi
from ax_devil_device_api.errors import ResponseFormatError
from ax_devil_device_api.testing import MockCamera

QUICK = Heartbeat(None)
DISCOVERY = "/axis-cgi/apidiscovery.cgi"


# -- 1: a correlated message with neither result nor error ---------------------------------------------------------------


def test_the_codecs_raise_for_a_correlated_message_with_neither_result_nor_error() -> None:
    with pytest.raises(ResponseFormatError):
        EventsCodec().classify({"apiVersion": "1.0", "context": "ax-1"})
    with pytest.raises(ResponseFormatError):
        DataHubCodec().classify({"jsonrpc": "2.0", "id": "ax-1"})
    assert EventsCodec().classify({"apiVersion": "1.0"}) is None  # not correlated: still ignorable
    assert DataHubCodec().classify({"jsonrpc": "2.0"}) is None


def _empty_events(socket: FakeSocket, message: Any) -> None:
    socket.push({"apiVersion": "1.0", "context": message["context"], "method": message["method"]})


def _empty_hub(socket: FakeSocket, message: Any) -> None:
    socket.push({"jsonrpc": "2.0", "id": message["id"]})


@pytest.mark.parametrize(("spec", "handler"), [(EVENTS, _empty_events), (DATA_HUB, _empty_hub)], ids=["events", "datahub"])
def test_sync_request_completes_at_once_for_an_empty_reply(spec: Any, handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(spec, heartbeat=QUICK) as session:
            with pytest.raises(ResponseFormatError):  # not a ReadTimeout after the full timeout
                session.request("m", {}, timeout=5)


@pytest.mark.anyio
@pytest.mark.parametrize(("spec", "handler"), [(EVENTS, _empty_events), (DATA_HUB, _empty_hub)], ids=["events", "datahub"])
async def test_async_request_completes_at_once_for_an_empty_reply(spec: Any, handler: Any) -> None:
    camera = FakeWsCamera(handler=handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(spec, heartbeat=QUICK) as session:
            with anyio.fail_after(4), pytest.raises(ResponseFormatError):
                await session.request("m", {}, timeout=5)


# -- 2: Capabilities holds plain data -------------------------------------------------------------------------------------


def _populated() -> Any:
    camera = MockCamera()
    camera.jsonrpc(
        DISCOVERY, "getApiList", data={"apiList": [{"id": "mqtt-client", "version": "1.0"}, {"id": "mqtt-client", "version": "2.0"}, {"id": "x"}]}
    )
    camera.dca_apis({"analytics-mqtt": ["v1"]})
    with camera.device() as dev:
        return dev.capabilities()


def test_capabilities_survive_asdict_copy_deepcopy_and_pickle() -> None:
    caps = _populated()
    plain = dataclasses.asdict(caps)
    assert plain["classic_apis"]["mqtt-client"] == "1.0, 2.0"  # text stays text
    assert plain["classic_versions"]["mqtt-client"] == {"versions": ("1.0", "2.0"), "problems": ()}
    assert "classic_apis[x]" in plain["errors"]
    for clone in (copy.copy(caps), copy.deepcopy(caps), pickle.loads(pickle.dumps(caps))):
        assert clone.classic_versions == caps.classic_versions and clone.classic_apis == caps.classic_apis
        assert clone.dca_apis == caps.dca_apis and clone.errors == caps.errors
    assert isinstance(caps.classic_versions["mqtt-client"], Advertised) and type(caps.classic_apis["mqtt-client"]) is str  # type: ignore[index]


def test_no_str_tuple_or_int_subclass_values_remain_in_capabilities() -> None:
    caps = _populated()
    values: list[Any] = [*(caps.classic_apis or {}).values(), *(caps.dca_apis or {}).values(), *caps.errors.values()]
    values += [caps.firmware, caps.observed_at]
    for value in values:
        assert type(value) in (str, frozenset, type(None), type(caps.observed_at)), type(value)


# -- 3: an unreadable apiList entry makes absence unknown ------------------------------------------------------------------


def test_an_absent_api_is_unknown_when_an_entry_without_a_readable_id_exists() -> None:
    camera = MockCamera()
    camera.jsonrpc(DISCOVERY, "getApiList", data={"apiList": [{"version": "1.0"}, {"id": "present", "version": "1.0"}]})
    classic = ApiInfo(id="absent", name="a", family=Family.JSONRPC, major=1, discovery=(ApiDiscovery("absent"),))
    present = ApiInfo(id="present", name="p", family=Family.JSONRPC, major=1, discovery=(ApiDiscovery("present"),))
    wrong_major = ApiInfo(id="present", name="p", family=Family.JSONRPC, major=2, discovery=(ApiDiscovery("present"),))
    with camera.device() as dev:
        caps = dev.capabilities()
    assert decide_support(classic, caps).status is Support.UNKNOWN  # the broken entry could have been it
    assert decide_support(present, caps).status is Support.YES
    assert decide_support(wrong_major, caps).status is Support.NO  # a well-formed match still decides


def test_an_absent_api_is_a_definitive_no_when_every_entry_is_readable() -> None:
    camera = MockCamera()
    camera.jsonrpc(DISCOVERY, "getApiList", data={"apiList": [{"id": "present", "version": "1.0"}]})
    classic = ApiInfo(id="absent", name="a", family=Family.JSONRPC, major=1, discovery=(ApiDiscovery("absent"),))
    with camera.device() as dev:
        assert decide_support(classic, dev.capabilities()).status is Support.NO


# -- 4: identity values must be text -------------------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [None, {"a": 1}, 13, 1.5, True, ["x"]])
def test_identity_with_a_non_text_value_is_a_response_format_error_and_caches_nothing(bad: Any) -> None:
    camera = MockCamera()
    camera.jsonrpc("/axis-cgi/basicdeviceinfo.cgi", "getAllProperties", data={"propertyList": {"Version": bad, "ProdNbr": "Q1"}})
    with camera.device() as dev:
        with pytest.raises(ResponseFormatError):
            dev.identity()
        assert dev._state.get("identity") is None  # noqa: SLF001 - nothing cached


def test_a_numeric_firmware_never_satisfies_a_firmware_prerequisite() -> None:
    camera = MockCamera()
    camera.jsonrpc("/axis-cgi/basicdeviceinfo.cgi", "getAllProperties", data={"propertyList": {"Version": 13}})
    camera.api_list({})
    camera.cgi("/axis-cgi/param.cgi", text="root.Properties.API.HTTP.Version=3\n")
    with camera.device() as dev:
        result = dev.supports(SceneProfileApi)  # needs firmware 6.25
    assert result.status is Support.UNKNOWN  # not YES: the firmware could not be read


def test_a_malformed_refresh_keeps_the_cached_identity_and_facts() -> None:
    camera = MockCamera()
    camera.identity(firmware="11.0.0")
    camera.api_list({"mqtt-client": "1.0"})
    with camera.device() as dev:
        assert dev.identity().firmware_version == "11.0.0"
        dev.capabilities()
        assert dev._state.get("classic_apis") is not None  # noqa: SLF001
        camera._routes.clear()  # noqa: SLF001 - the camera now answers the identity request with a malformed list
        camera.jsonrpc("/axis-cgi/basicdeviceinfo.cgi", "getAllProperties", data={"propertyList": {"Version": None}})
        with pytest.raises(ResponseFormatError):
            dev.identity(refresh=True)
        assert dev.identity().firmware_version == "11.0.0"  # the earlier identity stays
        assert dev._state.get("classic_apis") is not None  # noqa: SLF001 - and no cached fact was cleared
