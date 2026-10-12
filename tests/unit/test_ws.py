"""WebSocket sessions over a fake camera: handshake, auth, codecs, heartbeat, gaps, cleanup."""

from __future__ import annotations

import time
from datetime import timezone
from typing import Any

import pytest

from ax_devil_device_api import AsyncDevice, Device, errors
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._runtime import ws
from ax_devil_device_api._runtime.ws import DATA_HUB, EVENTS, Gap, SessionLedger
from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventFilter, EventNotification, EventsCodec, TopicSample
from ws_fake import FakeSocket, FakeWsCamera, events_handler, notify

FILTERS = [
    EventFilter(topic_filter="tns1:PTZController/tnsaxis:PTZReady"),
    EventFilter(topic_filter="tns1:Device/tnsaxis:IO/VirtualPort", content_filter='boolean(//SimpleItem[@Name="port" and @Value="1"])'),
]

QUICK = Heartbeat(None)


def device(camera: FakeWsCamera, **kw: Any) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport(), **kw)


def adevice(camera: FakeWsCamera, **kw: Any) -> AsyncDevice:
    return AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport(), **kw)


# -- codecs (sans-IO) -------------------------------------------------------


def test_events_codec_roundtrip() -> None:
    codec = EventsCodec()
    assert codec.encode_request("events:configure", {"eventFilterList": []}, "c1") == {
        "apiVersion": "1.0", "context": "c1", "method": "events:configure", "params": {"eventFilterList": []},
    }
    reply = codec.classify({"apiVersion": "1.0", "context": "c1", "method": "events:configure", "data": {}})
    assert reply is not None and getattr(reply, "request_id") == "c1"
    note = codec.classify(notify(state="0"))
    assert note is not None
    event = note.item  # type: ignore[union-attr]
    assert isinstance(event, EventNotification)
    assert event.topic.endswith("VirtualPort") and event.source == {"port": "1"} and event.data == {"state": "0"}
    assert event.timestamp is not None and event.timestamp.tzinfo is timezone.utc and event.timestamp.year == 2021
    assert codec.classify({"method": "something:else"}) is None


def test_event_filter_needs_a_filter() -> None:
    with pytest.raises(ValueError):
        EventFilter()


def test_datahub_codec() -> None:
    codec = DataHubCodec()
    assert codec.encode_request("data-hub_v1:listTopics", None, "7") == {
        "jsonrpc": "2.0", "id": "7", "method": "data-hub_v1:listTopics", "params": {},
    }
    sample = codec.classify({
        "jsonrpc": "2.0", "method": "data-hub_v1:topicSample",
        "params": {"subscriptionId": "s1", "topic": "t", "instance": {"k": "v"}, "data": {"x": 1},
                   "timestamp": "2026-03-17T09:39:52.569Z", "isHistorical": True},
    })
    assert sample is not None
    item = sample.item  # type: ignore[union-attr]
    assert isinstance(item, TopicSample) and item.is_historical and item.timestamp is not None and item.timestamp.year == 2026
    error = codec.classify({"jsonrpc": "2.0", "id": "7", "error": {"code": 1200, "message": "No such subscription"}})
    assert error is not None and getattr(error, "error").code == 1200
    assert codec.error_kind(1200) == "not_found" and codec.error_kind(2105) == "access_denied"


# -- sync sessions ----------------------------------------------------------


def test_events_session_configures_and_streams() -> None:
    camera = FakeWsCamera(handler=events_handler)
    with device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS) as session:
            assert session.gap is None
            camera.sockets[0].push(notify(state="1"))
            camera.sockets[0].push(notify("tns1:PTZController/tnsaxis:PTZReady", ready="1"))
            camera.sockets[0].close()
            topics = [e.topic for e in session.notifications()]
    assert topics == ["tns1:Device/tnsaxis:IO/VirtualPort", "tns1:PTZController/tnsaxis:PTZReady"]
    configure = camera.sockets[0].received[0]
    assert configure["method"] == "events:configure" and configure["apiVersion"] == "1.0"
    assert configure["params"]["eventFilterList"][0] == {"topicFilter": "tns1:PTZController/tnsaxis:PTZReady"}
    assert configure["params"]["eventFilterList"][1]["contentFilter"].startswith("boolean(")
    handshake = camera.ws_requests[0]
    assert handshake.url.path == "/vapix/ws-data-stream" and handshake.url.params["sources"] == "events"
    assert handshake.headers["sec-websocket-key"] and "wssession" not in handshake.url.params


def test_no_filters_sends_no_configure() -> None:
    camera = FakeWsCamera(handler=events_handler)
    with device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        session.send({"hello": 1})
        camera.sockets[0].close(1001)
        assert list(session) == []
    assert camera.sockets[0].received == [{"hello": 1}]


def test_unknown_connect_options_are_rejected() -> None:
    camera = FakeWsCamera()
    with device(camera) as dev, pytest.raises(TypeError):
        dev.connect_session(EVENTS, bogus=1).__enter__()
    assert camera.requests == []


def test_digest_authentication_reuses_http_auth() -> None:
    camera = FakeWsCamera(handler=events_handler, digest=True)
    with device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK):
        pass
    assert camera.authorization[0] is None  # nothing before the challenge
    assert camera.authorization[1] is not None and camera.authorization[1].startswith("Digest ")
    assert 'username="root"' in camera.authorization[1]


def test_token_authentication() -> None:
    camera = FakeWsCamera(handler=events_handler)
    with device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK, use_token=True):
        pass
    assert camera.requests[0].url.path == "/axis-cgi/wssession.cgi"
    handshake = camera.ws_requests[0]
    assert handshake.url.params["wssession"] == camera.token and handshake.url.params["sources"] == "events"


@pytest.mark.parametrize(
    ("status", "error"),
    [(401, errors.AuthError), (403, errors.HttpAccessDenied), (404, errors.NotSupported), (503, errors.HttpUnavailable), (500, errors.HttpError)],
)
def test_refused_handshake_maps_to_errors(status: int, error: type[Exception]) -> None:
    camera = FakeWsCamera(refuse=status)
    with device(camera) as dev, pytest.raises(error):
        dev.connect_session(EVENTS).__enter__()


def test_request_keeps_interleaved_notifications() -> None:
    def handler(socket: FakeSocket, message: Any) -> None:
        if message["method"] == "data-hub_v1:listTopics":
            socket.push({"jsonrpc": "2.0", "method": "data-hub_v1:topicSample",
                         "params": {"subscriptionId": "s", "topic": "a", "instance": {}, "data": {}, "timestamp": "2026-01-01T00:00:00Z", "isHistorical": False}})
            socket.push({"jsonrpc": "2.0", "id": message["id"], "result": {"topics": [{"name": "a"}]}})
        elif message["method"] == "data-hub_v1:unsubscribe":
            socket.push({"jsonrpc": "2.0", "id": message["id"], "error": {"code": 1200, "message": "No such subscription"}})

    camera = FakeWsCamera(handler=handler)
    with device(camera) as dev, dev.connect_session(DATA_HUB, heartbeat=QUICK) as session:
        assert session.request("data-hub_v1:listTopics") == {"topics": [{"name": "a"}]}
        sample = next(iter(session.notifications()))
        assert isinstance(sample, TopicSample) and sample.topic == "a"
        with pytest.raises(errors.ApiError) as raised:
            session.request("data-hub_v1:unsubscribe", {"subscriptionId": "x"})
        assert raised.value.code == 1200 and raised.value.kind == "not_found" and raised.value.api == DATA_HUB.api_id
    assert camera.ws_requests[0].url.path == "/vapix/ws/v1" and camera.ws_requests[0].url.params["apis"] == "data-hub"


def test_datahub_subscriptions_on_connect() -> None:
    def handler(socket: FakeSocket, message: Any) -> None:
        socket.push({"jsonrpc": "2.0", "id": message["id"], "result": {"subscriptionId": message["params"]["subscriptionId"]}})

    camera = FakeWsCamera(handler=handler)
    subs = [{"subscriptionId": "s1", "filters": [{"topics": ["t"]}]}]
    with device(camera) as dev, dev.connect_session(DATA_HUB, heartbeat=QUICK, subscriptions=subs):
        pass
    assert camera.sockets[0].received[0]["method"] == "data-hub_v1:subscribe"


def test_receive_timeout_and_binary_frames() -> None:
    camera = FakeWsCamera()
    raw = ws.SessionSpec("audio", "/audio/ws")
    with device(camera) as dev, dev.connect_session(raw, heartbeat=QUICK) as session:
        with pytest.raises(errors.ReadTimeout):
            session.receive(timeout=0.05)
        camera.sockets[0].push_bytes(b"\x00\x01")
        assert session.receive(timeout=2) == b"\x00\x01"
        session.send(b"\x02")
        with pytest.raises(TypeError):
            session.request("x")
    assert camera.sockets[0].received == [b"\x02"]


def test_normal_close_vs_abnormal_close() -> None:
    camera = FakeWsCamera()
    with device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1001, "going away")
            with pytest.raises(errors.SessionClosed) as closed:
                session.receive(timeout=2)
            assert closed.value.code == 1001
            with pytest.raises(errors.SessionClosed):  # stays closed, never blocks
                session.receive(timeout=2)
        with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[1].close(1011, "boom")
            with pytest.raises(errors.ConnectionFailed):
                list(session)


def test_dropped_connection_is_a_transport_error() -> None:
    camera = FakeWsCamera()
    with device(camera) as dev, dev.connect_session(EVENTS, heartbeat=QUICK) as session:
        camera.sockets[0].drop()
        with pytest.raises(errors.TransportError):
            list(session)


def test_heartbeat_pings_and_detects_dead_peer() -> None:
    camera = FakeWsCamera()
    with device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=Heartbeat(0.05, 1.0)) as session:
            time.sleep(0.3)
            assert camera.sockets[0].pings >= 2
            camera.sockets[0].close()
            assert list(session) == []
        with dev.connect_session(EVENTS, heartbeat=Heartbeat(0.05, 0.1)) as session:
            camera.sockets[1].answer_pings = False
            with pytest.raises(errors.ConnectionFailed):
                session.receive(timeout=3)


def test_heartbeat_validation() -> None:
    with pytest.raises(ValueError):
        Heartbeat(0)
    with pytest.raises(ValueError):
        Heartbeat(5, 0)


def test_gap_reported_after_reconnect() -> None:
    camera = FakeWsCamera()
    with device(camera) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK) as first:
            assert first.gap is None
            with dev.connect_session(EVENTS, heartbeat=QUICK) as overlapping:
                assert overlapping.gap is None  # another session is open: nothing was missed
        time.sleep(0.05)
        with dev.connect_session(EVENTS, heartbeat=QUICK) as second:
            assert isinstance(second.gap, Gap)
            assert 0 < second.gap.duration < 5 and second.gap.start < second.gap.end
        with dev.connect_session(DATA_HUB, heartbeat=QUICK) as other:
            assert other.gap is None  # a different endpoint has its own history


def test_stream_slot_released_and_handshake_closed() -> None:
    camera = FakeWsCamera()
    with device(camera, max_streams=1) as dev:
        for _ in range(3):
            with dev.connect_session(EVENTS, heartbeat=QUICK):
                pass
    assert all(s.closed for s in camera.streams)


def test_user_exception_passes_through() -> None:
    camera = FakeWsCamera()
    with device(camera) as dev, pytest.raises(KeyError):
        with dev.connect_session(EVENTS, heartbeat=QUICK):
            raise KeyError("x")
    assert camera.streams[0].closed


def test_on_response_reports_handshake() -> None:
    records: list[dict[str, Any]] = []
    camera = FakeWsCamera()
    with device(camera, on_response=records.append) as dev, dev.connect_session(EVENTS, heartbeat=QUICK):
        pass
    assert records[-1]["path"] == "/vapix/ws-data-stream" and records[-1]["status"] == 101


# -- ledger (clock controlled) ---------------------------------------------


def test_ledger_gap_start_depends_on_how_the_session_ended(monkeypatch: pytest.MonkeyPatch) -> None:
    now = [1000.0]
    monkeypatch.setattr(ws.time, "time", lambda: now[0])
    ledger = SessionLedger()
    assert ledger.begin("k") is None
    now[0] = 1010.0
    ledger.touch("k")  # last frame at 1010
    now[0] = 1030.0
    ledger.end("k", graceful=False)  # lost: the loss was noticed at 1030, but data stopped at 1010
    now[0] = 1100.0
    gap = ledger.begin("k")
    assert gap is not None and gap.start.timestamp() == 1010.0 and gap.duration == 90.0
    now[0] = 1110.0
    ledger.end("k", graceful=True)  # clean exit stamps the close time
    now[0] = 1120.0
    gap = ledger.begin("k")
    assert gap is not None and gap.start.timestamp() == 1110.0 and gap.duration == 10.0


# -- async ------------------------------------------------------------------


@pytest.mark.anyio
async def test_async_events_session() -> None:
    camera = FakeWsCamera(handler=events_handler, digest=True)
    async with adevice(camera) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS) as session:
            assert session.gap is None
            camera.sockets[0].push(notify(state="1"))
            camera.sockets[0].close()
            events = [e async for e in session.notifications()]
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as again:
            assert again.gap is not None
    assert [e.topic for e in events] == ["tns1:Device/tnsaxis:IO/VirtualPort"]
    assert camera.sockets[0].received[0]["method"] == "events:configure"
    assert camera.authorization[0] is None and (camera.authorization[1] or "").startswith("Digest ")


@pytest.mark.anyio
async def test_async_request_errors_and_timeouts() -> None:
    def handler(socket: FakeSocket, message: Any) -> None:
        if message["method"] == "data-hub_v1:unsubscribe":
            socket.push({"jsonrpc": "2.0", "id": message["id"], "error": {"code": 2105, "message": "nope"}})

    camera = FakeWsCamera(handler=handler)
    async with adevice(camera) as dev:
        async with dev.connect_session(DATA_HUB, heartbeat=QUICK) as session:
            with pytest.raises(errors.ApiAccessDenied):
                await session.request("data-hub_v1:unsubscribe", {})
            with pytest.raises(errors.ReadTimeout):
                await session.request("data-hub_v1:listTopics", timeout=0.05)
            with pytest.raises(errors.ReadTimeout):
                await session.receive(timeout=0.05)


@pytest.mark.anyio
async def test_async_refusal_close_codes_and_cleanup() -> None:
    refused = FakeWsCamera(refuse=404)
    async with adevice(refused) as dev:
        with pytest.raises(errors.NotSupported):
            async with dev.connect_session(EVENTS):
                pass
    camera = FakeWsCamera()
    async with adevice(camera, max_streams=1) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK) as session:
            camera.sockets[0].close(1011)
            with pytest.raises(errors.ConnectionFailed):
                [m async for m in session]
        with pytest.raises(KeyError):  # not wrapped in an ExceptionGroup
            async with dev.connect_session(EVENTS, heartbeat=QUICK):
                raise KeyError("x")
    assert all(s.closed for s in camera.streams)


@pytest.mark.anyio
async def test_async_heartbeat_and_token() -> None:
    camera = FakeWsCamera()
    async with adevice(camera) as dev:
        async with dev.connect_session(EVENTS, heartbeat=Heartbeat(0.05, 0.1), use_token=True) as session:
            import asyncio

            camera.sockets[0].answer_pings = False
            with pytest.raises(errors.ConnectionFailed):
                await session.receive(timeout=3)
            await asyncio.sleep(0)
    assert camera.ws_requests[0].url.params["wssession"] == camera.token
