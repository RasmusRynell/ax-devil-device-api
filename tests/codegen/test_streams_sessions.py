"""Streams, WebSocket sessions, RTSP URLs and prefixed SOAP names: spec -> generated module -> runtime.

Each feature gets a small fixture spec, generated and executed as a member of the ``apis`` package,
then called through ``Device`` / ``AsyncDevice`` over fake transports.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "unit"))  # ws_fake

from codegen.build import build_api
from codegen.loader import LoadedSpec, SpecError, validate
from codegen.output import render_surface
from codegen.render import signatures
from test_bindings import base_spec, build, generate, load_module
from ws_fake import FakeWsCamera, events_handler, notify

from ax_devil_device_api import AsyncDevice, Device, EventFilter, Heartbeat, MediaStream, Part, RtspUrl, errors

QUICK = Heartbeat(None)

# -- HTTP streams ------------------------------------------------------------------

STREAM_SPEC = base_spec(
    "cgi",
    {"path": "/axis-cgi/mjpg/video.cgi"},
    {
        "mjpeg": {
            "summary": "Motion JPEG.", "effect": "read",
            "binding": {"reply": {"stream": {"decoder": "mjpeg"}}},
            "params": {"type": "object", "properties": {"fps": {"type": "integer"}, "resolution": {"type": "string"}}},
        },
        "monitor": {
            "summary": "Watch ports.", "effect": "read",
            "binding": {"path": "/axis-cgi/io/port.cgi", "query": {"monitor": "all"}, "reply": {"stream": {"decoder": "lines"}}},
        },
        "download": {"summary": "Raw bytes.", "effect": "read", "binding": {"path": "/axis-cgi/media.cgi", "reply": "stream"}},
    },
)  # fmt: skip


def frame(body: bytes) -> bytes:
    return b"--b\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n%s\r\n" % (len(body), body)


def stream_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/axis-cgi/mjpg/video.cgi":
        assert request.url.params["fps"] == "5"
        data = frame(b"\xff\xd8one") + frame(b"\xff\xd8two") + b"--b--\r\n"
        return httpx.Response(200, content=data, headers={"Content-Type": "multipart/x-mixed-replace; boundary=b"})
    if request.url.path == "/axis-cgi/io/port.cgi":
        assert request.url.params["monitor"] == "all"
        return httpx.Response(200, content=b"0=active\r\n1=inactive\n2=active")
    if request.url.path == "/axis-cgi/media.cgi":
        return httpx.Response(200, content=b"\x00\x01\x02")
    return httpx.Response(404)


def test_stream_replies_render_binding_and_return_types() -> None:
    code = generate(STREAM_SPEC)
    assert "reply=Stream(" in code and code.count("stream=True") == 3
    assert "Stream('mjpeg')" in code or 'Stream("mjpeg")' in code
    assert "-> StreamResult[Part]" in code and "-> AsyncStreamResult[Part]" in code
    assert "-> StreamResult[str]" in code and "-> AsyncStreamResult[bytes]" in code
    assert "async def mjpeg" in code
    surface = render_surface([build(STREAM_SPEC)])
    assert "DemoApi.mjpeg(self, *, fps: int | MISSING = MISSING, resolution: str | MISSING = MISSING, " in surface
    assert "AsyncDemoApi.monitor(self, *, request_options: RequestOptions | None = None) -> AsyncStreamResult[str]" in surface


def test_stream_operations_have_no_result() -> None:
    spec = base_spec(
        "cgi", {"path": "/x"},
        {"go": {"summary": "x", "binding": {"reply": {"stream": {}}}, "result": {"type": "string"}}},
    )  # fmt: skip
    with pytest.raises(SpecError, match="no `result`"):
        build(spec)
    bad = base_spec("cgi", {"path": "/x"}, {"go": {"summary": "x", "binding": {"reply": {"stream": {"decoder": "nope"}}}}})
    assert validate(bad)  # the schema rejects unknown decoders


def test_streams_end_to_end_sync() -> None:
    module = load_module(STREAM_SPEC)
    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(stream_handler)) as dev:
        api = dev.api(module.DemoApi)
        with api.mjpeg(fps=5) as stream:
            parts = list(stream)
        assert [p.body for p in parts] == [b"\xff\xd8one", b"\xff\xd8two"] and all(isinstance(p, Part) for p in parts)
        with api.monitor() as lines:
            assert list(lines) == ["0=active", "1=inactive", "2=active"]
        with api.download() as raw:
            assert b"".join(raw) == b"\x00\x01\x02"


@pytest.mark.anyio
async def test_streams_end_to_end_async() -> None:
    module = load_module(STREAM_SPEC)
    async with AsyncDevice("cam", credentials=("u", "p"), transport=httpx.MockTransport(stream_handler)) as dev:
        api = dev.api(module.AsyncDemoApi)
        async with await api.mjpeg(fps=5) as stream:
            bodies = [p.body async for p in stream]
        assert bodies == [b"\xff\xd8one", b"\xff\xd8two"]
        async with await api.monitor() as lines:
            assert [line async for line in lines] == ["0=active", "1=inactive", "2=active"]


def test_stream_error_status_raises_before_streaming() -> None:
    module = load_module(STREAM_SPEC)
    transport = httpx.MockTransport(lambda request: httpx.Response(503, text="busy"))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev, pytest.raises(errors.HttpUnavailable):
        dev.api(module.DemoApi).download()


def test_mjpeg_decoder_rejects_a_plain_image() -> None:
    module = load_module(STREAM_SPEC)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=b"jpeg", headers={"Content-Type": "image/jpeg"}))
    with Device("cam", credentials=("u", "p"), transport=transport) as dev, pytest.raises(errors.ResponseFormatError):
        dev.api(module.DemoApi).mjpeg()


# -- WebSocket sessions ------------------------------------------------------------

WS_SPEC = base_spec(
    "ws",
    {},
    {
        "connect": {
            "summary": "Stream events.", "effect": "read",
            "binding": {"session": {"path": "/vapix/ws-data-stream", "query": {"sources": "events"}, "codec": "events"}},
        },
        "connect_hub": {
            "summary": "Data hub.", "effect": "read",
            "binding": {"session": {"path": "/vapix/ws/v1", "query": {"apis": "data-hub"}, "codec": "datahub"}},
        },
        "connect_audio": {"summary": "Raw audio.", "effect": "read", "binding": {"session": {"path": "/vapix/audio"}}},
        "audio_session": {
            "summary": "Audio of one session.", "effect": "read",
            "binding": {"session": {"path": "/api/v1.2/audioSessions/{audioSessionId}/ws/recv"}},
            "params": {"type": "object", "required": ["audioSessionId"], "properties": {"audioSessionId": {"type": "string"}}},
        },
    },
)  # fmt: skip


def test_session_operations_render_spec_and_signatures() -> None:
    code = generate(WS_SPEC)
    assert "class SESSIONS:" in code and "EventsCodec()" in code and "setup=events_setup" in code
    assert "PATH =" not in code
    assert "    def connect(" in code and "async def connect" not in code  # async API returns the context manager
    assert "-> AbstractAsyncContextManager[AsyncSession]" in code and "-> AbstractContextManager[Session]" in code
    surface = render_surface([build(WS_SPEC)])
    assert (
        "demo.DemoApi.connect(self, event_filter_list: Sequence[EventFilter | Mapping[str, str]] | None = None, *, "
        "heartbeat: Heartbeat = DEFAULT_HEARTBEAT, use_token: bool = False, request_options: RequestOptions | None = None) "
        "-> AbstractContextManager[Session]" in surface
    )
    assert "connect_audio(self, *, heartbeat" in surface
    (sig,), _ = signatures(build(WS_SPEC).ops[1])
    assert sig.args[0].startswith("subscriptions:")


def test_session_path_placeholders_become_arguments() -> None:
    assert "audio_session_id: str, *, heartbeat" in render_surface([build(WS_SPEC)])
    module = load_module(WS_SPEC)
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.api(module.DemoApi).audio_session("a/b 1", heartbeat=QUICK) as session:
            camera.sockets[0].push_bytes(b"\x01")
            assert session.receive(2) == b"\x01"
        with pytest.raises(TypeError):
            dev.api(module.DemoApi).audio_session()  # type: ignore[call-arg]
    assert camera.ws_requests[0].url.raw_path.startswith(b"/api/v1.2/audioSessions/a%2Fb%201/ws/recv")


def test_session_spec_errors() -> None:
    def spec(binding: dict[str, Any], **op: Any) -> dict[str, Any]:
        return base_spec("ws", {}, {"connect": {"summary": "x", "binding": binding, **op}})

    with pytest.raises(SpecError, match="no `result`"):
        build(spec({"session": {"path": "/x"}}, result={"type": "string"}))
    with pytest.raises(SpecError, match="exactly the"):
        build(spec({"session": {"path": "/x"}}, params={"type": "object", "properties": {"a": {"type": "string"}}}))
    with pytest.raises(SpecError, match="raw session"):
        build(spec({"session": {"path": "/x", "setup": "events"}}))
    with pytest.raises(SpecError, match="start with"):
        build(spec({"session": {"path": "x"}}))
    mixed = base_spec("ws", {}, {"go": {"summary": "x", "binding": {"rtsp": {}}}})
    assert validate(mixed)  # the schema allows only session bindings in a ws API
    with pytest.raises(SpecError, match="need binding.session"):
        build(base_spec("ws", {}, {"go": {"summary": "x"}}))
    clash = base_spec("ws", {}, {"connect": {"summary": "x", "binding": {"session": {"path": "/x", "codec": "events"}}}},
                      types={"EventFilter": {"type": "object", "properties": {"a": {"type": "string"}}}})  # fmt: skip
    api = build(clash)  # the type is renamed, not rejected (see test_reserved_type_names_are_renamed)
    assert [t.name for t in api.types] == ["EventFilterType"]


def test_events_connect_end_to_end_sync() -> None:
    module = load_module(WS_SPEC)
    camera = FakeWsCamera(handler=events_handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        api = dev.api(module.DemoApi)
        filters = [EventFilter(topic_filter="tns1:Device/tnsaxis:IO/VirtualPort"), {"contentFilter": "boolean(//x)"}]
        with api.connect(filters, heartbeat=QUICK) as session:
            camera.sockets[0].push(notify(state="1"))
            camera.sockets[0].close()
            topics = [e.topic for e in session.notifications()]
    assert topics == ["tns1:Device/tnsaxis:IO/VirtualPort"]
    configure = camera.sockets[0].received[0]
    assert configure["params"]["eventFilterList"] == [
        {"topicFilter": "tns1:Device/tnsaxis:IO/VirtualPort"}, {"contentFilter": "boolean(//x)"},
    ]  # fmt: skip
    handshake = camera.ws_requests[0]
    assert handshake.url.path == "/vapix/ws-data-stream" and handshake.url.params["sources"] == "events"


def test_events_connect_without_filters_and_raw_session() -> None:
    module = load_module(WS_SPEC)
    camera = FakeWsCamera(handler=events_handler)
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        api = dev.api(module.DemoApi)
        with api.connect(heartbeat=QUICK):
            pass
        assert camera.sockets[0].received == []  # no filters, no events:configure
        with api.connect_audio(heartbeat=QUICK) as session:
            camera.sockets[1].push_bytes(b"\x01\x02")
            assert session.receive(2) == b"\x01\x02"
    assert camera.ws_requests[1].url.path == "/vapix/audio"


@pytest.mark.anyio
async def test_events_connect_end_to_end_async() -> None:
    module = load_module(WS_SPEC)
    camera = FakeWsCamera(handler=events_handler)
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        api = dev.api(module.AsyncDemoApi)
        async with api.connect([EventFilter(topic_filter="t")], heartbeat=QUICK) as session:
            camera.sockets[0].push(notify(state="0"))
            camera.sockets[0].close()
            topics = [e.topic async for e in session.notifications()]
    assert topics == ["tns1:Device/tnsaxis:IO/VirtualPort"]
    assert camera.sockets[0].received[0]["params"]["eventFilterList"] == [{"topicFilter": "t"}]


def test_datahub_connect_sends_subscriptions() -> None:
    module = load_module(WS_SPEC)

    def handler(socket: Any, message: Any) -> None:
        socket.push({"jsonrpc": "2.0", "id": message["id"], "result": {}})

    camera = FakeWsCamera(handler=handler)
    subs = [{"subscriptionId": "s1", "filters": [{"topic": "t"}]}]
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.api(module.DemoApi).connect_hub(subs, heartbeat=QUICK):
            pass
    sent = camera.sockets[0].received[0]
    assert sent["method"] == "data-hub_v1:subscribe" and sent["params"]["subscriptionId"] == "s1"


# -- RTSP --------------------------------------------------------------------------

RTSP_SPEC = base_spec(
    "rtsp",
    {},
    {
        "stream": {
            "summary": "Live stream.", "effect": "read",
            "binding": {"rtsp": {"query": {"videocodec": "h264"}}},
            "params": {"type": "object", "properties": {
                "resolution": {"type": "string"}, "audio": {"type": "boolean"}, "fps": {"type": "integer"},
                "mode": {"enum": ["a", "b"]}, "tags": {"type": "array", "items": {"type": "string"}},
            }},
        },
        "events": {
            "summary": "Events only.", "effect": "read",
            "binding": {"rtsp": {"path": "/axis-media/ssm/media.amp", "port": 8554, "query": {"event": "on"}}},
            "params": {"type": "object", "required": ["eventtopic"], "properties": {"eventtopic": {"type": "string"}}},
            "positional": ["eventtopic"],
        },
    },
)  # fmt: skip


def test_rtsp_operations_build_urls_without_io() -> None:
    module = load_module(RTSP_SPEC)

    def refuse(request: httpx.Request) -> httpx.Response:
        raise AssertionError("an RTSP operation must not make a request")

    with Device("cam.local", credentials=("viewer", "p@ss"), transport=httpx.MockTransport(refuse)) as dev:
        api = dev.api(module.DemoApi)
        url = api.stream(resolution="1280x720", audio=False, fps=15, mode="b", tags=["x", "y"])
        assert isinstance(url, RtspUrl)
        assert str(url) == (
            "rtsp://cam.local:554/axis-media/media.amp?videocodec=h264&resolution=1280x720&audio=0&fps=15&mode=b&tags=x,y"
        )
        assert str(api.stream()) == "rtsp://cam.local:554/axis-media/media.amp?videocodec=h264"
        with_creds = api.events("tns1:Device/Casing", include_credentials=True)
        assert str(with_creds) == "rtsp://viewer:p%40ss@cam.local:8554/axis-media/ssm/media.amp?event=on&eventtopic=tns1:Device/Casing"
        assert "p%40ss" not in repr(with_creds) and "p@ss" not in with_creds.safe
        assert api.events("t", port=554).port == 554
        with pytest.raises(Exception):
            api.stream(bogus=1)  # type: ignore[call-arg]
        assert str(dev.rtsp_url(MediaStream(videocodec="h264"))).startswith("rtsp://cam.local:554/")


@pytest.mark.anyio
async def test_rtsp_operations_on_the_async_api_are_plain_calls() -> None:
    module = load_module(RTSP_SPEC)
    async with AsyncDevice("cam.local", credentials=("u", "p"), transport=httpx.MockTransport(lambda r: httpx.Response(404))) as dev:
        url = dev.api(module.AsyncDemoApi).stream(fps=5)
        assert url.safe.endswith("videocodec=h264&fps=5")


def test_rtsp_in_a_cgi_api_and_error_cases() -> None:
    mixed = base_spec(
        "cgi", {"path": "/axis-cgi/x.cgi"},
        {"live": {"summary": "x", "binding": {"rtsp": {}}, "params": {"type": "object", "properties": {"camera": {"type": "integer"}}}}},
    )  # fmt: skip
    assert "RtspBinding()" in generate(mixed)
    reserved = base_spec(
        "rtsp", {},
        {"go": {"summary": "x", "binding": {"rtsp": {}}, "params": {"type": "object", "properties": {"port": {"type": "integer"}}}}},
    )  # fmt: skip
    with pytest.raises(SpecError, match="reserved for RTSP"):
        build(reserved)
    nested = base_spec(
        "rtsp", {},
        {"go": {"summary": "x", "binding": {"rtsp": {}}, "params": {"type": "object", "properties": {
            "a": {"type": "object", "x-name": "A", "properties": {"b": {"type": "string"}}}}}}},
    )  # fmt: skip
    with pytest.raises(SpecError, match="scalar"):
        build(nested)
    with pytest.raises(SpecError, match="no `result`"):
        build(base_spec("rtsp", {}, {"go": {"summary": "x", "binding": {"rtsp": {}}, "result": {"type": "string"}}}))


# -- SOAP namespaces ---------------------------------------------------------------

NS = "http://www.axis.com/vapix/ws/certificates"
ACERT = "http://www.axis.com/vapix/ws/cert"
SOAP_NS_SPEC = base_spec(
    "soap",
    {"namespace": NS, "namespaces": {"acert": ACERT}},
    {
        "create": {
            "summary": "Create.", "effect": "write",
            "binding": {"action": f"{NS}/Create", "element": "Create"},
            "params": {"type": "object", "required": ["acert:Id"], "properties": {
                "acert:Id": {"type": "string"},
                "@acert:flag": {"type": "boolean"},
                "Subject": {"type": "object", "x-name": "CreateSubject", "properties": {"acert:CN": {"type": "string"}}},
            }},
            "result": {"$ref": "#/types/Created"},
        },
        "ping": {
            "summary": "Ping.", "effect": "action",
            "binding": {"action": f"{NS}/Ping", "element": "Ping", "namespaces": {"p": "urn:p"}},
            "params": {"type": "object", "properties": {"p:Name": {"type": "string"}}},
        },
    },
    types={"Created": {"type": "object", "required": ["acert:Id"], "properties": {
        "acert:Id": {"type": "string"}, "Size": {"type": "integer"}, "Note": {"type": "string"}}}},
)  # fmt: skip


def test_soap_prefixed_names_python_names_and_binding() -> None:
    api = build(SOAP_NS_SPEC)
    request = next(t for t in api.types if t.name == "CreateRequest")
    assert [(f.py, f.wire) for f in request.fields] == [("id", "acert:Id"), ("flag", "@acert:flag"), ("subject", "Subject")]
    code = generate(SOAP_NS_SPEC)
    assert f"namespaces=(('acert', '{ACERT}'),)" in code.replace('"', "'")
    assert 'XmlField("acert:Id", source="child", name="Id")' in code
    assert "'p', 'urn:p'" in code.replace('"', "'") and "'acert', " in code.replace('"', "'")  # operation namespaces are merged


def test_soap_undeclared_prefix_is_rejected() -> None:
    spec = base_spec(
        "soap", {"namespace": NS},
        {"go": {"summary": "x", "binding": {"action": "a", "element": "E"},
                "params": {"type": "object", "properties": {"zz:Id": {"type": "string"}}}}},
    )  # fmt: skip
    with pytest.raises(SpecError, match="declare them in binding.namespaces"):
        build(spec)
    reserved = base_spec("soap", {"namespace": NS, "namespaces": {"env": "urn:x"}},
                         {"go": {"summary": "x", "binding": {"action": "a", "element": "E"}}})  # fmt: skip
    with pytest.raises(SpecError, match="reserved namespace prefix"):
        build(reserved)


def test_soap_prefixed_end_to_end() -> None:
    module = load_module(SOAP_NS_SPEC)
    seen: list[httpx.Request] = []
    env = "http://www.w3.org/2003/05/soap-envelope"

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if b"<Ping" in request.content:
            return httpx.Response(200, content=f'<s:Envelope xmlns:s="{env}"><s:Body><PingResponse/></s:Body></s:Envelope>')
        body = (
            f'<s:Envelope xmlns:s="{env}" xmlns:c="{ACERT}"><s:Body><x:CreateResponse xmlns:x="{NS}">'
            "<c:Id>cert1</c:Id><x:Size></x:Size><x:Note></x:Note></x:CreateResponse></s:Body></s:Envelope>"
        )
        return httpx.Response(200, content=body)

    with Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler)) as dev:
        api = dev.api(module.DemoApi)
        created = api.create(id="cert1", flag=True, subject={"acert:CN": "me"})
        text = seen[0].content.decode()
        assert f'<Create xmlns="{NS}" xmlns:acert="{ACERT}" xmlns:p="urn:p"' not in text  # ping's prefix is not on create
        assert f'xmlns="{NS}" xmlns:acert="{ACERT}"' in text and 'acert:flag="true"' in text
        assert "<acert:Id>cert1</acert:Id>" in text and "<Subject><acert:CN>me</acert:CN></Subject>" in text
        # empty elements are pruned for fields that cannot hold ""; strings keep them
        assert created.id == "cert1" and created.size is None and created.note == ""
        api.ping(name="n")
        assert 'xmlns:p="urn:p"' in seen[1].content.decode() and "<p:Name>n</p:Name>" in seen[1].content.decode()
