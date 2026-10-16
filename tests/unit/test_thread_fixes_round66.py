"""A malformed body is never chained: JSONDecodeError.doc and the XML parse errors hold the response, so the discovery and
identity probes and the decoders raise their library error outside the handler. Message, str, repr, the whole
__cause__/__context__ chain and the traceback are free of the body."""

from __future__ import annotations

import traceback
from typing import Any

import httpx
import pytest

from ax_devil_device_api._protocols.base import ApiInfo, Family, Operation
from ax_devil_device_api._protocols.cgi import CgiBinding, Xml
from ax_devil_device_api._runtime.capabilities import applications_flow, dca_apis_flow, services_flow
from ax_devil_device_api._runtime.driver import run_sync
from ax_devil_device_api.device import Device
from ax_devil_device_api.errors import DeviceError
from ax_devil_device_api.testing import MockCamera

SENTINEL = "SENTINEL-HUNTER2-BODY"


def _links(error: BaseException) -> list[BaseException]:
    found: list[BaseException] = []
    pending = [error]
    while pending:
        current = pending.pop()
        if any(current is seen for seen in found):
            continue
        found.append(current)
        pending += [link for link in (current.__cause__, current.__context__) if link is not None]
    return found


def assert_no_body(error: BaseException) -> None:
    assert error.__cause__ is None and error.__context__ is None, [type(link).__name__ for link in _links(error)]
    texts = [str(error), repr(error), "".join(traceback.format_exception(error))]
    for link in _links(error):
        texts += [repr(link), str(link), repr(link.args), repr(getattr(link, "doc", ""))]
    for text in texts:
        assert SENTINEL not in text, text[:200]


def _device(body: bytes, content_type: str = "application/json", status: int = 200) -> Device:
    transport = httpx.MockTransport(lambda request: httpx.Response(status, content=body, headers={"content-type": content_type}))
    return Device("cam", credentials=("u", "p"), transport=transport)


JSON_BODIES = [f'{{"password":"{SENTINEL}"'.encode(), f"{SENTINEL} not json".encode(), f'{{"apis": {{"a": {SENTINEL}}}}}'.encode()]
XML_BODIES = [f'<reply password="{SENTINEL}"'.encode(), f"<a>{SENTINEL}</b>".encode(), f"<?xml version='1.0' encoding='{SENTINEL}'?><a/>".encode()]


@pytest.mark.parametrize("body", JSON_BODIES, ids=lambda b: b[:12].decode())
def test_malformed_discovery_json_is_not_chained(body: bytes) -> None:
    with _device(body) as dev, pytest.raises(DeviceError) as caught:
        run_sync(dev._transport, dca_apis_flow(dev._state))  # noqa: SLF001
    assert_no_body(caught.value)


@pytest.mark.parametrize("body", XML_BODIES, ids=lambda b: b[:12].decode())
@pytest.mark.parametrize("flow", [applications_flow, services_flow], ids=lambda f: f.__name__)
def test_malformed_discovery_xml_is_not_chained(flow: Any, body: bytes) -> None:
    with _device(body, "text/xml") as dev, pytest.raises(DeviceError) as caught:
        run_sync(dev._transport, flow(dev._state))  # noqa: SLF001
    assert_no_body(caught.value)


def test_the_probe_errors_in_capabilities_hold_no_body() -> None:
    camera = MockCamera()
    camera.route("GET", "/config/discover", lambda _: httpx.Response(200, content=JSON_BODIES[0]))
    camera.route("POST", "/axis-cgi/applications/list.cgi", lambda _: httpx.Response(200, content=XML_BODIES[0]))
    with camera.device() as dev:
        caps = dev.capabilities()
        dev._collect(("applications",))  # noqa: SLF001
        caps = dev.capabilities()
    assert caps.errors and all(SENTINEL not in text for text in caps.errors.values())


@pytest.mark.parametrize("body", JSON_BODIES, ids=lambda b: b[:12].decode())
def test_malformed_identity_and_version_replies_are_not_chained(body: bytes) -> None:
    camera = MockCamera()
    camera.route("POST", "/axis-cgi/basicdeviceinfo.cgi", lambda _: httpx.Response(200, content=body, headers={"content-type": "application/json"}))
    with camera.device() as dev, pytest.raises(DeviceError) as caught:
        dev.identity()
    assert_no_body(caught.value)


@pytest.mark.parametrize("body", XML_BODIES, ids=lambda b: b[:12].decode())
def test_a_cgi_xml_reply_that_does_not_parse_is_not_chained(body: bytes) -> None:
    op = Operation(ApiInfo(id="t", name="T", family=Family.CGI), "get", CgiBinding("/x.cgi", reply=Xml()), result=None)
    with _device(body, "text/xml") as dev, pytest.raises(DeviceError) as caught:
        dev.invoke(op)
    assert_no_body(caught.value)
