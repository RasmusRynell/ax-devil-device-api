"""service_json, SOAP and REST protocols: requests, replies, faults, error mapping, sync and async."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any

import httpx
import pytest

from ax_devil_device_api._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation
from ax_devil_device_api._protocols.rest import RestBinding
from ax_devil_device_api._protocols.service_json import ServiceJsonBinding
from ax_devil_device_api._protocols.soap import SoapBinding
from ax_devil_device_api._protocols.xmlmap import XmlField, XmlMap
from ax_devil_device_api.device import AsyncDevice, Device
from ax_devil_device_api.errors import (
    ApiAccessDenied,
    ApiError,
    ApiUnavailable,
    AuthError,
    HttpAccessDenied,
    HttpError,
    NotSupported,
    ResponseFormatError,
)

ENV = "http://www.w3.org/2003/05/soap-envelope"


def info(family: Family, errors: dict[Any, ErrorCode] | None = None) -> ApiInfo:
    return ApiInfo(id="t", name="T", family=family, errors=errors or {})


def connect(handler: Any) -> Device:
    return Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler))


def connect_async(handler: Any) -> AsyncDevice:
    return AsyncDevice("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler))


class Recorder:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.response

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]


# ---------------------------------------------------------------------------
# service_json


class SpeakerArgs(Model):
    volume: int | None = None
    mode: str | None = None


class SpeakerResult(Model):
    result_code: int
    message: str | None = None


SJ_INFO = info(
    Family.SERVICE_JSON,
    {
        "axast:DeviceNotCalibrated": ErrorCode("Not calibrated", "unavailable"),
        "ter:InvalidArgVal": ErrorCode("Invalid value"),
    },
)
SJ_BINDING = ServiceJsonBinding("/vapix/axast", "axast:PerformSpeakerTest")
SJ_OP = Operation(SJ_INFO, "perform", binding=SJ_BINDING, params=SpeakerArgs, result=SpeakerResult)
SJ_ACTION = Operation(SJ_INFO, "action", binding=SJ_BINDING)


def fault(sub: str | None, code: str = "ter:Action", msg: str | None = None, reason: str = "Reason") -> dict[str, Any]:
    return {"Fault": "env:Receiver", "FaultCode": code, "FaultSubCode": sub, "FaultReason": reason, "FaultMsg": msg}


def test_service_json_request_and_bare_response() -> None:
    rec = Recorder(httpx.Response(200, json={"result_code": 3, "message": "ok", "extra": 1}))
    with connect(rec) as dev:
        result = dev.invoke(SJ_OP, volume=10)
    assert isinstance(result, SpeakerResult)
    assert (result.result_code, result.message) == (3, "ok")
    assert rec.last.method == "POST"
    assert rec.last.url.path == "/vapix/axast"
    assert json.loads(rec.last.content) == {"axast:PerformSpeakerTest": {"volume": 10}}


def test_service_json_no_params_sends_empty_object_and_empty_reply_ok() -> None:
    rec = Recorder(httpx.Response(200, content=b""))
    with connect(rec) as dev:
        assert dev.invoke(SJ_ACTION) is None
    assert json.loads(rec.last.content) == {"axast:PerformSpeakerTest": {}}


def test_service_json_fault_keyed_by_subcode() -> None:
    rec = Recorder(httpx.Response(400, json=fault("axast:DeviceNotCalibrated", msg=None, reason="needs calibration")))
    with connect(rec) as dev, pytest.raises(ApiError) as caught:
        dev.invoke(SJ_OP)
    error = caught.value
    assert isinstance(error, ApiUnavailable)
    assert error.code == "axast:DeviceNotCalibrated"
    assert error.kind == "unavailable"
    assert error.description == "Not calibrated"
    assert error.http_status == 400
    assert "needs calibration" in str(error)
    assert error.details["FaultCode"] == "ter:Action"


def test_service_json_null_subcode_falls_back_to_fault_code() -> None:
    rec = Recorder(httpx.Response(400, json=fault(None, code="ter:InvalidArgVal", msg="Volume should be <= 100")))
    with connect(rec) as dev, pytest.raises(ApiError) as caught:
        dev.invoke(SJ_OP)
    assert caught.value.code == "ter:InvalidArgVal"
    assert caught.value.description == "Invalid value"
    assert "Volume should be <= 100" in str(caught.value)


def test_service_json_unknown_code_and_fault_with_200() -> None:
    rec = Recorder(httpx.Response(200, json=fault("x:Weird", msg="boom")))
    with connect(rec) as dev, pytest.raises(ApiError) as caught:
        dev.invoke(SJ_OP)
    assert caught.value.code == "x:Weird"
    assert caught.value.description is None


def test_service_json_http_errors_without_fault_body() -> None:
    with connect(Recorder(httpx.Response(500, text="oops"))) as dev, pytest.raises(HttpError):
        dev.invoke(SJ_OP)
    with connect(Recorder(httpx.Response(403, text="no"))) as dev, pytest.raises(HttpAccessDenied):
        dev.invoke(SJ_OP)


def test_service_json_bad_reply_shapes() -> None:
    with connect(Recorder(httpx.Response(200, text="not json"))) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(SJ_OP)
    with connect(Recorder(httpx.Response(200, json={"message": "missing required"}))) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(SJ_OP)


@pytest.mark.anyio
async def test_service_json_async() -> None:
    rec = Recorder(httpx.Response(200, json={"result_code": 1}))
    async with connect_async(rec) as dev:
        result = await dev.invoke(SJ_OP, mode="a")
    assert result.result_code == 1
    assert json.loads(rec.last.content) == {"axast:PerformSpeakerTest": {"mode": "a"}}

    async with connect_async(Recorder(httpx.Response(400, json=fault("axast:DeviceNotCalibrated")))) as dev:
        with pytest.raises(ApiUnavailable):
            await dev.invoke(SJ_OP)


# ---------------------------------------------------------------------------
# soap


class Item(Model):
    name: str
    count: int | None = None


class Topics(Model):
    title: str
    items: list[Item]


class FilterArgs(Model):
    topic: str | None = None
    enabled: bool | None = None
    tags: list[str] | None = None


NS = "http://www.axis.com/vapix/ws/event1"
SOAP_MAP = XmlMap(
    fields=(
        XmlField("title", "child", "Title"),
        XmlField(
            "items",
            "path",
            "Items/Item",
            many=True,
            nested=XmlMap((XmlField("name", "child"), XmlField("count", "child"))),
        ),
    ),
)
SOAP_INFO = info(
    Family.SOAP,
    {"ter:InvalidArgs": ErrorCode("Bad args"), "ter:ActionNotSupported": ErrorCode("Unsupported", "unavailable")},
)
SOAP_BINDING = SoapBinding(f"{NS}/GetEventInstances", "GetEventInstances", NS, reply=SOAP_MAP)
SOAP_OP = Operation(SOAP_INFO, "get", binding=SOAP_BINDING, params=FilterArgs, result=Topics)
SOAP_ACTION = Operation(SOAP_INFO, "act", binding=SoapBinding("a", "Act", NS), params=FilterArgs)


def envelope(inner: str) -> str:
    return f'<?xml version="1.0"?><env:Envelope xmlns:env="{ENV}"><env:Body>{inner}</env:Body></env:Envelope>'


def soap_fault(*subcodes: str, code: str = "env:Sender", reason: str = "Invalid argument") -> str:
    sub = ""
    for value in reversed(subcodes):
        sub = f"<env:Subcode><env:Value>{value}</env:Value>{sub}</env:Subcode>"
    return envelope(
        f'<env:Fault><env:Code><env:Value>{code}</env:Value>{sub}</env:Code>'
        f'<env:Reason><env:Text xml:lang="en">{reason}</env:Text></env:Reason></env:Fault>'
    )


REPLY = envelope(
    f'<tev:GetEventInstancesResponse xmlns:tev="{NS}"><tev:Title>Tree</tev:Title>'
    "<tev:Items><tev:Item><tev:name>a</tev:name><tev:count>2</tev:count></tev:Item>"
    "<tev:Item><tev:name>b</tev:name></tev:Item></tev:Items></tev:GetEventInstancesResponse>"
)


def test_soap_request_envelope() -> None:
    rec = Recorder(httpx.Response(200, text=REPLY))
    with connect(rec) as dev:
        dev.invoke(SOAP_OP, topic="a<b&c", enabled=True, tags=["x", "y"])
    request = rec.last
    assert request.method == "POST"
    assert request.url.path == "/vapix/services"
    content_type = request.headers["content-type"]
    assert content_type.startswith("application/soap+xml")
    assert f'action="{NS}/GetEventInstances"' in content_type
    root = ET.fromstring(request.content)
    assert root.tag == f"{{{ENV}}}Envelope"
    (body,) = list(root)
    (element,) = list(body)
    assert element.tag == f"{{{NS}}}GetEventInstances"
    assert [(c.tag, c.text) for c in element] == [
        (f"{{{NS}}}topic", "a<b&c"),
        (f"{{{NS}}}enabled", "true"),
        (f"{{{NS}}}tags", "x"),
        (f"{{{NS}}}tags", "y"),
    ]


def test_soap_empty_params_request_element() -> None:
    rec = Recorder(httpx.Response(200, text=envelope("<Done/>")))
    with connect(rec) as dev:
        assert dev.invoke(SOAP_ACTION) is None
    (element,) = list(list(ET.fromstring(rec.last.content))[0])
    assert element.tag == f"{{{NS}}}Act"
    assert len(element) == 0


def test_soap_reply_parsed_through_xml_map() -> None:
    with connect(Recorder(httpx.Response(200, text=REPLY))) as dev:
        result = dev.invoke(SOAP_OP)
    assert result.title == "Tree"
    assert [(i.name, i.count) for i in result.items] == [("a", 2), ("b", None)]


def test_soap_fault_keyed_by_subcode() -> None:
    rec = Recorder(httpx.Response(400, text=soap_fault("ter:InvalidArgs", reason="Bad topic")))
    with connect(rec) as dev, pytest.raises(ApiError) as caught:
        dev.invoke(SOAP_OP)
    error = caught.value
    assert error.code == "ter:InvalidArgs"
    assert error.description == "Bad args"
    assert error.http_status == 400
    assert "Bad topic" in str(error)


def test_soap_nested_subcode_prefers_documented_then_innermost() -> None:
    with connect(Recorder(httpx.Response(500, text=soap_fault("ter:ActionNotSupported", "ter:Deep")))) as dev:
        with pytest.raises(ApiUnavailable) as caught:
            dev.invoke(SOAP_OP)
    assert caught.value.code == "ter:ActionNotSupported"

    with connect(Recorder(httpx.Response(500, text=soap_fault("x:Outer", "x:Inner")))) as dev:
        with pytest.raises(ApiError) as caught2:
            dev.invoke(SOAP_OP)
    assert caught2.value.code == "x:Inner"


def test_soap_fault_without_subcode_uses_code() -> None:
    with connect(Recorder(httpx.Response(500, text=soap_fault(code="env:Receiver")))) as dev:
        with pytest.raises(ApiError) as caught:
            dev.invoke(SOAP_OP)
    assert caught.value.code == "env:Receiver"


def test_soap_non_soap_failures() -> None:
    with connect(Recorder(httpx.Response(503, text="busy"))) as dev, pytest.raises(HttpError):
        dev.invoke(SOAP_OP)
    with connect(Recorder(httpx.Response(401))) as dev, pytest.raises(AuthError):
        dev.invoke(SOAP_OP)
    with connect(Recorder(httpx.Response(200, text="<html/>"))) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(SOAP_OP)
    with connect(Recorder(httpx.Response(200, text=envelope("")))) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(SOAP_OP)


def test_soap_missing_required_field_is_format_error() -> None:
    reply = envelope(f'<r xmlns="{NS}"><Items/></r>')
    with connect(Recorder(httpx.Response(200, text=reply))) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(SOAP_OP)


@pytest.mark.anyio
async def test_soap_async() -> None:
    async with connect_async(Recorder(httpx.Response(200, text=REPLY))) as dev:
        result = await dev.invoke(SOAP_OP, topic="t")
    assert result.title == "Tree"
    async with connect_async(Recorder(httpx.Response(400, text=soap_fault("ter:InvalidArgs")))) as dev:
        with pytest.raises(ApiError) as caught:
            await dev.invoke(SOAP_OP)
    assert caught.value.code == "ter:InvalidArgs"


# ---------------------------------------------------------------------------
# rest


class Thing(Model):
    id: str
    size: int | None = None


class ThingArgs(Model):
    id: str | None = None
    size: int | None = None
    verbose: bool | None = None
    labels: list[str] | None = None


REST_INFO = info(Family.REST, {404: ErrorCode("Thing missing"), 429: ErrorCode("Busy", "unavailable")})
REST_GET = Operation(
    REST_INFO,
    "get",
    binding=RestBinding("GET", "/api/things/{id}", query=(("verbose", "verbose"), ("labels", "label"))),
    params=ThingArgs,
    result=Thing,
)
REST_PUT = Operation(
    REST_INFO, "put", binding=RestBinding("PUT", "/api/things/{id}", body="object"), params=ThingArgs, result=Thing
)
REST_POST_EMPTY = Operation(REST_INFO, "reset", binding=RestBinding("POST", "/api/reset", body="object"))
REST_DELETE = Operation(REST_INFO, "delete", binding=RestBinding("DELETE", "/api/things/{id}"), params=ThingArgs)
REST_VALUE = Operation(
    REST_INFO, "size", binding=RestBinding("PUT", "/api/size", body="value", body_field="size"), params=ThingArgs
)


def test_rest_get_with_path_and_query_and_bare_response() -> None:
    rec = Recorder(httpx.Response(200, json={"id": "a/b", "size": 4, "extra": True}))
    with connect(rec) as dev:
        thing = dev.invoke(REST_GET, id="a/b", verbose=True, labels=["x", "y"])
    assert thing.size == 4
    assert rec.last.method == "GET"
    assert rec.last.url.raw_path.decode().startswith("/api/things/a%2Fb?")
    assert rec.last.url.params.get_list("label") == ["x", "y"]
    assert rec.last.url.params["verbose"] == "true"
    assert not rec.last.content


def test_rest_body_excludes_path_and_query_fields() -> None:
    rec = Recorder(httpx.Response(200, json={"id": "a"}))
    with connect(rec) as dev:
        dev.invoke(REST_PUT, id="a", size=9)
    assert rec.last.method == "PUT"
    assert rec.last.url.path == "/api/things/a"
    assert json.loads(rec.last.content) == {"size": 9}


def test_rest_empty_object_body_and_empty_reply() -> None:
    rec = Recorder(httpx.Response(204))
    with connect(rec) as dev:
        assert dev.invoke(REST_POST_EMPTY) is None
        assert dev.invoke(REST_DELETE, id="a") is None
    assert rec.requests[0].content == b"{}"
    assert rec.requests[1].method == "DELETE"


def test_rest_value_body() -> None:
    rec = Recorder(httpx.Response(200))
    with connect(rec) as dev:
        dev.invoke(REST_VALUE, size=7)
    assert json.loads(rec.last.content) == 7


def test_rest_missing_path_param() -> None:
    with connect(Recorder(httpx.Response(200, json={"id": "a"}))) as dev, pytest.raises(TypeError):
        dev.invoke(REST_GET)
    with connect(Recorder(httpx.Response(200, json={"id": "a"}))) as dev, pytest.raises(ValueError):
        dev.invoke(REST_GET, id="..")


def test_rest_documented_status_maps_to_api_error() -> None:
    with connect(Recorder(httpx.Response(429, text="slow down"))) as dev, pytest.raises(ApiUnavailable) as caught:
        dev.invoke(REST_GET, id="a")
    assert caught.value.code == 429
    assert caught.value.description == "Busy"
    assert caught.value.http_status == 429

    with connect(Recorder(httpx.Response(404, text="nope"))) as dev, pytest.raises(ApiError) as caught2:
        dev.invoke(REST_GET, id="a")
    assert caught2.value.description == "Thing missing"
    assert not isinstance(caught2.value, NotSupported)


def test_rest_undocumented_statuses_use_http_errors() -> None:
    with connect(Recorder(httpx.Response(500, text="x"))) as dev, pytest.raises(HttpError):
        dev.invoke(REST_GET, id="a")
    with connect(Recorder(httpx.Response(403, text="x"))) as dev, pytest.raises(HttpAccessDenied):
        dev.invoke(REST_PUT, id="a")
    with connect(Recorder(httpx.Response(401))) as dev, pytest.raises(AuthError):
        dev.invoke(REST_GET, id="a")


def test_rest_403_documented_as_access_denied() -> None:
    op = Operation(
        info(Family.REST, {403: ErrorCode("Forbidden", "access_denied")}),
        "get",
        binding=RestBinding("GET", "/x"),
        result=Thing,
    )
    with connect(Recorder(httpx.Response(403, text="x"))) as dev, pytest.raises(ApiAccessDenied):
        dev.invoke(op)


def test_rest_bad_reply() -> None:
    with connect(Recorder(httpx.Response(200, text="<xml/>"))) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(REST_GET, id="a")
    with connect(Recorder(httpx.Response(200, json={"size": 1}))) as dev, pytest.raises(ResponseFormatError):
        dev.invoke(REST_GET, id="a")


@pytest.mark.anyio
async def test_rest_async() -> None:
    rec = Recorder(httpx.Response(200, json={"id": "a", "size": 2}))
    async with connect_async(rec) as dev:
        thing = await dev.invoke(REST_PUT, id="a", size=2)
    assert thing.size == 2
    assert json.loads(rec.last.content) == {"size": 2}
    async with connect_async(Recorder(httpx.Response(404))) as dev:
        with pytest.raises(ApiError):
            await dev.invoke(REST_GET, id="a")
