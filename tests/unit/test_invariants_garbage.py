"""Invariant tests I1 and I2 (a device sending garbage is a device fault, handled by CLASS).

I1: device data never escapes as a non-library exception: only ``DeviceError`` subclasses come out of any decoder.
I2: unparseable discovery data never yields a definitive, cached NO: it gives UNKNOWN, uncached.

Each decoder and probe is fed a fixed set of garbage shapes: null, wrong scalar types, objects where scalars are
expected, arrays where objects are expected, empty and binary bodies, and deep nesting.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ax_devil_device_api import Device, Support
from ax_devil_device_api._protocols.base import (
    AcapDiscovery,
    ApiDiscovery,
    ApiInfo,
    ApiVersion,
    DcaDiscovery,
    Family,
    Model,
    Operation,
    ServiceDiscovery,
)
from ax_devil_device_api._protocols.cgi import CgiBinding, JsonReply, Text, TextKv, Xml
from ax_devil_device_api._protocols.dca import DcaBinding
from ax_devil_device_api._protocols.jsonrpc import FixedVersion, JsonRpcBinding
from ax_devil_device_api._protocols.rest import RestBinding
from ax_devil_device_api._protocols.service_json import ServiceJsonBinding
from ax_devil_device_api._protocols.soap import SoapBinding
from ax_devil_device_api._protocols.xmlmap import XmlField, XmlMap
from ax_devil_device_api._runtime.capabilities import decide_support
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventsCodec
from ax_devil_device_api.errors import DeviceError
from ax_devil_device_api.testing import MockCamera

DEEP = 5000
NESTED_JSON = b"[" * DEEP + b"]" * DEEP
NESTED_OBJECT = b'{"a":' * DEEP + b"1" + b"}" * DEEP
NESTED_XML = b"<a>" * DEEP + b"</a>" * DEEP

JSON_GARBAGE: list[bytes] = [
    b"", b"null", b"5", b"1.5", b"true", b'"x"', b"[]", b"[null]", b"{}", b"\xff\xfe\x00", b"NaN", b"{",
    b"No camera specified (ex. camera=1)", b"just words", b"=", b"a=b=c", b"(x=1)", b"image width=wide\nimage height=",
    b'{"error":null}', b'{"error":5}', b'{"error":"x"}', b'{"error":[]}', b'{"error":{}}',
    b'{"error":{"code":{},"message":{}}}', b'{"error":{"code":[],"message":null}}', b'{"error":{"code":1.5}}',
    b'{"error":{"code":true,"message":"m"}}', b'{"error":{"code":7,"message":["m"]}}',
    b'{"error":{"code":1,"message":"m","details":{"subCode":{}}}}',
    b'{"errors":[null]}', b'{"errors":[5]}', b'{"errors":[{"code":{}}]}', b'{"errors":[{"code":[1],"message":{}}]}',
    b'{"status":"error"}', b'{"status":"error","error":7}', b'{"status":"error","error":{"code":[1]}}',
    b'{"status":"success","data":null}', b'{"data":5}', b'{"data":[null]}',
    b'{"Fault":{},"FaultCode":{}}', b'{"Fault":1,"FaultCode":[],"FaultSubCode":{"a":1}}',
    b'{"Fault":"x","FaultCode":"c","FaultReason":{},"FaultMsg":[]}',
    b'{"data":{"a":{"b":{"c":[null,{"d":[]}]}}}}', NESTED_JSON, NESTED_OBJECT,
    b'{"x":' + b"9" * 5000 + b"}", b'{"x":1e999}', b'{"x":"NaN"}',
]
XML_GARBAGE: list[bytes] = [
    b"", b"<a/>", b"<a", b"text", b"\xff\xfe", b"<?xml version='1.0' encoding='nope'?><a/>", NESTED_XML,
    b"<Envelope xmlns='http://www.w3.org/2003/05/soap-envelope'><Body><Fault/></Body></Envelope>",
    b"<Envelope xmlns='http://www.w3.org/2003/05/soap-envelope'><Body><Fault><Code><Value/></Code></Fault></Body></Envelope>",
    b"<Envelope xmlns='http://www.w3.org/2003/05/soap-envelope'><Body><Fault><Code><Subcode><Subcode/></Subcode></Code>"
    b"<Reason><Text/></Reason></Fault></Body></Envelope>",
    b"<Envelope xmlns='http://www.w3.org/2003/05/soap-envelope'><Body><R><x><y/></x><x>1</x><x>a</x></R></Body></Envelope>",
    b"<r><i>1</i><i>x</i><i/></r>", b"<r a='1' b=''><c>2</c></r>",
]
STATUSES = (200, 401, 403, 404, 500, 503)


class Item(Model):
    n: int | None = None
    s: str | None = None
    f: float | None = None
    flag: bool | None = None
    tags: list[str] | None = None
    nested: dict[str, int] | None = None


def _info(family: Family) -> ApiInfo:
    return ApiInfo(id="t", name="T", family=family, major=1 if family is Family.JSONRPC else None)


ITEM_MAP = XmlMap(
    (
        XmlField("n", "child", "i"),
        XmlField("s", "attribute", "a"),
        XmlField("tags", "path", "r/i", many=True),
        XmlField("nested", "path", "r/c", many=True, nested=XmlMap((XmlField("x", "child"), XmlField("y", "attribute")))),
    )
)


def _ops() -> dict[str, Operation[Any]]:
    return {
        "jsonrpc": Operation(_info(Family.JSONRPC), "op", JsonRpcBinding("m", "/rpc", negotiation=FixedVersion(ApiVersion(1, 0))), result=Item),
        "jsonrpc-list": Operation(_info(Family.JSONRPC), "op", JsonRpcBinding("m", "/rpc", negotiation=FixedVersion(ApiVersion(1, 0))), result=list[Item]),
        "dca": Operation(_info(Family.DCA), "op", DcaBinding("GET", "/config/x"), result=Item),
        "rest": Operation(_info(Family.REST), "op", RestBinding("GET", "/x"), result=Item),
        "cgi-json": Operation(_info(Family.CGI), "op", CgiBinding("/x.cgi", reply=JsonReply()), result=Item),
        "cgi-dict": Operation(_info(Family.CGI), "op", CgiBinding("/x.cgi", reply=JsonReply()), result=dict[str, Any]),
        "cgi-text": Operation(_info(Family.CGI), "op", CgiBinding("/x.cgi", reply=Text()), result=str),
        "cgi-kv": Operation(_info(Family.CGI), "op", CgiBinding("/x.cgi", reply=TextKv()), result=Item),
        "cgi-xml": Operation(_info(Family.CGI), "op", CgiBinding("/x.cgi", reply=Xml()), result=None),
        "cgi-xml-map": Operation(_info(Family.CGI), "op", CgiBinding("/x.cgi", reply=Xml(map=ITEM_MAP)), result=Item),
        "soap-map": Operation(_info(Family.SOAP), "op", SoapBinding("a", "Act", "urn:x", reply=ITEM_MAP), result=Item),
        "service-json": Operation(_info(Family.SERVICE_JSON), "op", ServiceJsonBinding("/vapix/x", "ns:Op"), result=Item),
        "soap": Operation(_info(Family.SOAP), "op", SoapBinding("a", "Act", "urn:x"), result=None),
    }


def _drive(op: Operation[Any], body: bytes, status: int) -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(status, content=body))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev:
        try:
            dev.invoke(op)
        except DeviceError:
            pass  # a library error is the expected outcome for garbage


@pytest.mark.parametrize("name", list(_ops()))
def test_i1_protocol_decoders_raise_only_library_errors(name: str) -> None:
    op = _ops()[name]
    escaped: list[str] = []
    for body in [*JSON_GARBAGE, *XML_GARBAGE]:
        for status in STATUSES:
            try:
                _drive(op, body, status)
            except Exception as error:  # noqa: BLE001 - anything but a DeviceError is the failure
                escaped.append(f"{status} {body[:40]!r}: {type(error).__name__}: {str(error)[:80]}")
    assert not escaped, "\n".join(escaped[:15])


# -- WebSocket codecs ----------------------------------------------------------------------------------------------------

DEEP_DICT: dict[str, Any] = {}
_cursor = DEEP_DICT
for _ in range(500):
    _cursor["a"] = {}
    _cursor = _cursor["a"]

WS_GARBAGE: list[Any] = [
    None, 5, 1.5, True, "x", [], [None], {}, {"method": None}, {"method": 5}, {"method": []}, {"id": {}}, {"id": []},
    {"id": 1}, {"id": 1, "method": None}, {"context": 5}, {"context": {}}, {"context": "c"}, {"error": 5}, {"error": {}},
    {"id": "1", "error": {"code": {}, "message": []}}, {"context": "c", "error": {"code": 1.5, "message": "m"}},
    {"context": "c", "data": None}, {"id": "1", "result": None}, {"method": "events:notify"},
    {"method": "events:notify", "params": 5}, {"method": "events:notify", "params": {"notification": []}},
    {"method": "events:notify", "params": {"notification": {"topic": {}, "message": []}}},
    {"method": "events:notify", "params": {"notification": {"topic": "t", "message": {"source": 5}}}},
    {"method": "events:notify", "params": {"notification": {"topic": "t", "message": {}, "timestamp": 1e999}}},
    {"method": "events:notify", "params": {"notification": {"topic": "t", "message": {}, "timestamp": {}}}},
    {"method": "data-hub_v1:topicSample"}, {"method": "data-hub_v1:topicSample", "params": []},
    {"method": "data-hub_v1:topicSample", "params": {"topic": {}, "subscriptionId": [], "instance": 1, "data": None}},
    {"method": "data-hub_v1:topicSample", "params": {"topic": "t", "subscriptionId": "s", "instance": {}, "data": {}, "timestamp": 5}},
    {"method": "data-hub_v1:topicSample", "params": {"topic": "t", "subscriptionId": "s", "instance": {}, "data": {}, "timestamp": {}, "isHistorical": {}}},
    DEEP_DICT,
]


@pytest.mark.parametrize("codec", [EventsCodec(), DataHubCodec()], ids=["events", "datahub"])
def test_i1_websocket_codecs_raise_only_library_errors(codec: Any) -> None:
    escaped: list[str] = []
    for message in WS_GARBAGE:
        for call in (codec.classify, codec.correlation_id):
            try:
                call(message)
            except DeviceError:
                pass
            except Exception as error:  # noqa: BLE001
                escaped.append(f"{call.__name__}({str(message)[:50]}): {type(error).__name__}")
    assert not escaped, "\n".join(escaped[:15])


def test_a_null_method_with_a_correlated_id_is_a_response_shaped_message() -> None:
    from ax_devil_device_api.errors import ResponseFormatError

    with pytest.raises(ResponseFormatError):
        DataHubCodec().classify({"jsonrpc": "2.0", "id": "1", "method": None})
    with pytest.raises(ResponseFormatError):
        EventsCodec().classify({"context": "c", "method": None})


# -- capability probes (I1 and I2) ----------------------------------------------------------------------------------------

DISCOVERY = "/axis-cgi/apidiscovery.cgi"
CLASSIC = ApiInfo(id="a", name="a", family=Family.JSONRPC, major=1, discovery=(ApiDiscovery("a"),))
DCA = ApiInfo(id="a", name="a", family=Family.DCA, discovery=(DcaDiscovery("a", "v1"),))
ACAP = ApiInfo(id="a", name="a", family=Family.CGI, discovery=(AcapDiscovery("a"),))
SERVICE = ApiInfo(id="a", name="a", family=Family.SOAP, discovery=(ServiceDiscovery("urn:a"),))

CLASSIC_LISTS: list[Any] = [
    None, 5, "x", {}, [None], [5], ["x"], [[]], [{}], [{"id": None}], [{"id": {}, "version": []}],
    [{"id": "a"}], [{"id": "a", "version": None}], [{"id": "a", "version": 1}], [{"id": "a", "version": ""}],
    [{"id": "a", "version": "garbage"}], [{"id": "a", "version": "1"}], [{"id": "a", "version": "1.0.0"}],
    [{"id": ["a"], "version": "1.0"}], [{"version": "1.0"}], [{"id": "b", "version": "1.0"}, {"id": 5}],
]


def _status(camera: MockCamera, info: ApiInfo, key: str) -> tuple[Support, bool]:
    """Support for ``info`` after the probes ran, and whether the probe result was cached as definitive."""
    with camera.device() as dev:
        caps = dev.capabilities()
        result = decide_support(info, caps)
        return result.status, dev._state.get(key) is not None  # noqa: SLF001


@pytest.mark.parametrize("entries", CLASSIC_LISTS, ids=[repr(e)[:40] for e in CLASSIC_LISTS])
def test_i2_garbage_classic_discovery_is_never_a_cached_definitive_no(entries: Any) -> None:
    camera = MockCamera()
    camera.jsonrpc(DISCOVERY, "getApiList", data={"apiList": entries})
    status, cached = _status(camera, CLASSIC, "classic_apis")
    assert status is not Support.NO, "garbage must be UNKNOWN, never a definitive NO"
    assert not cached, "garbage must not be cached"


DCA_LISTS: list[Any] = [
    None, [], "x", 5, {"a": None}, {"a": []}, {"a": 5}, {"a": "v1"}, {"a": ["v1"]}, {"a": True},
    # the versions of an API are metadata objects; a null / list / string / number version is not a statement of support
    {"a": {"v1": None}}, {"a": {"v1": []}}, {"a": {"v1": "x"}}, {"a": {"v1": 5}}, {"a": {"v1": True}},
    {"a": {"v1": {}, "v2": None}}, {"a": {"v2": None}},
]


@pytest.mark.parametrize("apis", DCA_LISTS, ids=[repr(a)[:40] for a in DCA_LISTS])
def test_i2_garbage_dca_discovery_is_never_a_cached_definitive_no(apis: Any) -> None:
    camera = MockCamera()
    camera.route("GET", "/config/discover", lambda _: httpx.Response(200, json={"apis": apis}))
    status, cached = _status(camera, DCA, "dca_apis")
    assert status is not Support.NO and not cached
    assert status is not Support.YES, "a version that is not a metadata object is not a statement that the API is there"


def test_a_well_formed_dca_listing_is_yes_and_cached() -> None:
    camera = MockCamera()
    camera.route("GET", "/config/discover", lambda _: httpx.Response(200, json={"apis": {"a": {"v1": {}, "v2": {"x": 1}}}}))
    status, cached = _status(camera, DCA, "dca_apis")
    assert status is Support.YES and cached


APPLICATIONS = [b"", b"<a", b"text", b"\xff", b"<reply result='error'/>", b"<reply><application/></reply>",
                b"<reply><application Name=''/></reply>", b"<reply><application Version='1'/></reply>",
                b"<html/>", b"<html><body><application Name='a'/></body></html>", b"<replies/>", b"<reply><x/></reply><reply/>"]


@pytest.mark.parametrize("body", APPLICATIONS, ids=[repr(b)[:30] for b in APPLICATIONS])
def test_i2_garbage_application_list_is_never_a_cached_definitive_no(body: bytes) -> None:
    camera = MockCamera()
    camera.cgi("/axis-cgi/applications/list.cgi", text=body, content_type="text/xml")
    camera.api_list({})
    with camera.device() as dev:
        caps = dev._collect(("applications",))  # noqa: SLF001
        assert decide_support(ACAP, caps).status is not Support.NO
        assert dev._state.get("applications") is None  # noqa: SLF001


SERVICES = [b"", b"<a", b"text", b"\xff", b"<html/>", b"<html><Service><Namespace>urn:b</Namespace></Service></html>",
            b"<reply/>", b"<Envelope><Body><Service/></Body></Envelope>",
            b"<Envelope><Body><Service><XAddr>u</XAddr></Service></Body></Envelope>",
            b"<Envelope><Body><Service><Namespace>urn:b</Namespace><XAddr>u</XAddr></Service><Service/></Body></Envelope>",
            b"<Envelope><Body><Service><Namespace> </Namespace></Service></Body></Envelope>", NESTED_XML]


@pytest.mark.parametrize("body", SERVICES, ids=[repr(b)[:30] for b in SERVICES])
def test_i2_garbage_service_list_is_never_a_cached_definitive_no(body: bytes) -> None:
    camera = MockCamera()
    camera.route("POST", "/vapix/services", lambda _: httpx.Response(200, content=body))
    with camera.device() as dev:
        caps = dev._collect(("services",))  # noqa: SLF001
        assert decide_support(SERVICE, caps).status is not Support.NO
        assert dev._state.get("services") is None  # noqa: SLF001


IDENTITY = [None, 5, "x", [], {}, {"propertyList": None}, {"propertyList": []}, {"propertyList": "x"},
            {"propertyList": {"Version": None}}, {"propertyList": {"Version": {}}}, {"propertyList": {"Version": 13}}]


@pytest.mark.parametrize("data", IDENTITY, ids=[repr(d)[:40] for d in IDENTITY])
def test_i1_garbage_identity_raises_only_library_errors_and_caches_nothing(data: Any) -> None:
    camera = MockCamera()
    camera.jsonrpc("/axis-cgi/basicdeviceinfo.cgi", "getAllProperties", data=data)
    with camera.device() as dev:
        try:
            dev.identity()
        except DeviceError:
            pass
        assert dev._state.get("identity") is None or data == {"propertyList": {}}  # noqa: SLF001


@pytest.mark.parametrize("body", [b"", b"x", b"=", b"a=b=c", b"\xff", b"root.Properties.API.HTTP.Version=" + b"9" * 5000, b"\n" * 5000])
def test_i1_garbage_property_list_raises_only_library_errors(body: bytes) -> None:
    camera = MockCamera()
    camera.cgi("/axis-cgi/param.cgi", text=body)
    camera.api_list({})
    with camera.device() as dev:
        dev.capabilities()  # probe failures are recorded, never raised
        dev.capabilities()


STREAM_GARBAGE: list[bytes] = [
    b"", b"\x00" * 100, b"--b", b"--b\r\n", b"--b\r\nContent-Length: x\r\n\r\n", b"--b\r\nContent-Length: -5\r\n\r\nabc",
    b"--b\r\nContent-Length: 99999999999999999999\r\n\r\n", b"--b\r\n:::\r\n\r\nbody\r\n--b--", b"--b\n\n\n\n\n--b--", b"\xff\xfe" * 50,
    b"--b\r\nContent-Type: " + b"x" * 70000 + b"\r\n\r\n", b"--b--", b"\r\n" * 1000,
]


@pytest.mark.parametrize("chunk", [None, 1, 7])
def test_i1_stream_decoders_raise_only_library_errors(chunk: int | None) -> None:
    from ax_devil_device_api._streams import LinesDecoder, MixedReplaceDecoder, MultipartLinesDecoder

    escaped: list[str] = []
    for data in STREAM_GARBAGE:
        pieces = [data] if chunk is None else [data[i : i + chunk] for i in range(0, len(data), chunk)]
        for make in (
            lambda: MixedReplaceDecoder("b"),
            lambda: LinesDecoder(),
            lambda: MultipartLinesDecoder(MixedReplaceDecoder("b")),
        ):
            decoder = make()
            try:
                for piece in pieces:
                    decoder.feed(piece)
                decoder.close()
            except DeviceError:
                pass
            except Exception as error:  # noqa: BLE001
                escaped.append(f"{type(decoder).__name__} {data[:30]!r}: {type(error).__name__}")
    assert not escaped, "\n".join(escaped[:10])
