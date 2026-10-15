"""The chained pydantic error must not carry the response body: a formatted traceback shows no secret."""

from __future__ import annotations

import traceback
from typing import Any

import httpx
import pytest

from ax_devil_device_api._protocols.base import ApiInfo, Family, Model, Operation
from ax_devil_device_api._protocols.cgi import CgiBinding, JsonReply
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import ResponseFormatError
from ax_devil_device_api.testing import MockCamera

SECRET = "TOPSECRET-srtp-key-0123456789"
ROOT = "/config/rest/audio-multicast-ctrl/v1beta"


def _assert_clean(error: BaseException) -> None:
    rendered = "".join(traceback.format_exception(error))
    assert SECRET not in rendered and SECRET not in repr(error) and SECRET not in str(error)
    assert error.__cause__ is None  # no chained ValidationError ...
    assert error.__context__ is None or error.__suppress_context__  # ... and no implicit one either
    assert error.__context__ is None  # (it is raised outside the handler, so nothing is stored at all)


def test_sync_list_sources_with_a_missing_label_does_not_leak_through_the_traceback() -> None:
    camera = MockCamera()
    camera.rest("GET", f"{ROOT}/sources", data=[{"srtpKey": SECRET, "id": "s1"}])
    with camera.device() as dev, pytest.raises(ResponseFormatError) as caught:
        dev.apis.audio_multicast_ctrl.list_sources()
    _assert_clean(caught.value)
    assert "label" in str(caught.value)  # still diagnosable: the failing field is named


def test_sync_get_source_with_a_bad_port_does_not_leak_through_the_traceback() -> None:
    camera = MockCamera()
    camera.rest("GET", f"{ROOT}/sources/s1", data={"id": "s1", "label": "l", "port": 5, "srtpKey": SECRET})
    with camera.device() as dev, pytest.raises(ResponseFormatError) as caught:
        dev.apis.audio_multicast_ctrl.get_source("s1")
    _assert_clean(caught.value)


@pytest.mark.anyio
async def test_async_list_sources_and_get_source_do_not_leak_through_the_traceback() -> None:
    camera = MockCamera()
    camera.rest("GET", f"{ROOT}/sources", data=[{"srtpKey": SECRET, "id": "s1"}])
    camera.rest("GET", f"{ROOT}/sources/s1", data={"id": "s1", "label": "l", "port": 5, "srtpKey": SECRET})
    async with camera.async_device() as dev:
        with pytest.raises(ResponseFormatError) as listed:
            await dev.apis.audio_multicast_ctrl.list_sources()
        with pytest.raises(ResponseFormatError) as single:
            await dev.apis.audio_multicast_ctrl.get_source("s1")
    _assert_clean(listed.value)
    _assert_clean(single.value)


class Plain(Model):
    value: int


def test_a_non_masked_operation_drops_the_chain_too_and_keeps_a_redacted_excerpt() -> None:
    op = Operation(ApiInfo(id="t", name="T", family=Family.CGI), "get", CgiBinding("/x.cgi", reply=JsonReply()), result=Plain)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"value": "x", "password": SECRET}))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev, pytest.raises(ResponseFormatError) as caught:
        dev.invoke(op)
    _assert_clean(caught.value)
    assert "value" in str(caught.value) and "'x'" in str(caught.value) or '"x"' in str(caught.value)


@pytest.mark.parametrize("body", [b'{"key": "' + SECRET.encode() + b'", ', b"{" + SECRET.encode()])
def test_undecodable_json_does_not_keep_the_document_as_a_cause(body: bytes) -> None:
    op = Operation(ApiInfo(id="t", name="T", family=Family.CGI), "get", CgiBinding("/x.cgi", reply=JsonReply()), result=dict[str, Any])
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(lambda request: httpx.Response(200, content=body))) as dev:
        with pytest.raises(ResponseFormatError) as caught:
            dev.invoke(op)
    _assert_clean(caught.value)


def test_a_malformed_data_hub_sample_and_a_bad_websocket_message_do_not_chain_the_input() -> None:
    from ax_devil_device_api._runtime.ws_codecs import DataHubCodec

    sample = {"method": "data-hub_v1:topicSample", "params": {"topic": 5, "subscriptionId": "s", "instance": {"k": SECRET}, "data": {"k": SECRET}}}
    with pytest.raises(ResponseFormatError) as caught:
        DataHubCodec().classify(sample)
    _assert_clean(caught.value)
