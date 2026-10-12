"""WebSocket, HTTP stream and RTSP conversion of codegen/migrate_streams.py (synthetic v1 input)."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from codegen import migrate_streams as ms
from codegen import migrate_v1 as m
from codegen.build import build_api
from codegen.loader import LoadedSpec, validate

CTX = {"all_modules": set()}


def v1_spec(spec_id: str, styles: list[str], *ops: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {
        "id": spec_id, "name": spec_id.title(), "summary": "Demo.", "status": "released", "styles": styles,
        "python": {"module": spec_id.replace("-", "_"), "class_name": "DemoApi"},
        "auth": {"default_access_level": "viewer"}, "sources": [{"url": "https://example.test/doc"}],
        "operations": list(ops), **extra,
    }  # fmt: skip


def check(doc: dict[str, Any]) -> None:
    """The document is valid against the schema and builds."""
    assert validate(doc) == []
    api = build_api(LoadedSpec(Path(f"specs/apis/{doc['section']}/{doc['id']}.yaml"), copy.deepcopy(doc)))
    assert api.ops


def connect_op(**kw: Any) -> dict[str, Any]:
    return {
        "id": "connect", "name": "connect", "kind": "stream", "summary": "Open the WebSocket.",
        "http": {"method": "GET", "path": "/vapix/ws-data-stream"},
        "params": [{"name": "sources", "in": "query", "type": "string", "required": True}], **kw,
    }  # fmt: skip


def test_websocket_specs_become_session_operations() -> None:
    v1 = v1_spec(
        "event-streaming-over-websocket", ["websocket", "json_rpc_cgi"], connect_op(),
        {"id": "get_session_token", "kind": "http_endpoint", "http": {"method": "GET", "path": "/axis-cgi/wssession.cgi"}},
        {"id": "configure", "kind": "ws_message", "summary": "x", "json_rpc": {"method": "events:configure"}},
        types={"EventFilter": {"type": "object", "properties": {"topicFilter": {"type": "string"}}}},
    )  # fmt: skip
    assert ms.streaming_family(v1) == "ws" and m.classify_v1_family(v1) is None
    doc, notes = ms.convert(copy.deepcopy(v1), "network-video", CTX, "ws")
    assert doc["family"] == "ws" and doc["provenance"]["curated"] is False
    assert doc["operations"] == {
        "connect": {
            "summary": "Open the WebSocket.", "effect": "read",
            "binding": {"session": {"path": "/vapix/ws-data-stream", "query": {"sources": "events"}, "codec": "events"}},
        }
    }  # fmt: skip
    assert "types" not in doc  # the runtime's EventFilter replaces it
    assert {k for k, _ in notes.items} >= {"op-skipped", "types-dropped"}
    check(doc)


def test_unknown_websocket_api_is_a_raw_session() -> None:
    v1 = v1_spec("other-ws", ["websocket"], connect_op())
    doc, notes = ms.convert(v1, "network-video", CTX, "ws")
    assert doc["operations"]["connect"]["binding"]["session"] == {"path": "/vapix/ws-data-stream"}
    assert any(k == "session-codec" for k, _ in notes.items)
    check(doc)


def rtsp_op(op_id: str, *params: dict[str, Any], **kw: Any) -> dict[str, Any]:
    return {"id": op_id, "name": op_id, "kind": "rtsp_request", "summary": op_id, "params": list(params), **kw}


def q(name: str, **kw: Any) -> dict[str, Any]:
    return {"name": name, "in": "rtsp_query", "type": "string", "required": False, **kw}


def test_rtsp_only_spec_has_urls_with_fixed_arguments() -> None:
    v1 = v1_spec(
        "casing", ["rtsp", "other"],
        rtsp_op("stream_casing", q("event", enum=["on"], required=True), q("eventtopic", required=True, default="tns1:Device/Casing")),
        rtsp_op("stream_all", q("video", type="integer", enum=[0, 1]), q("eventtopic")),
        rtsp_op("play", q("video", type="integer", enum=[0, 1])),  # same URL as stream_all minus an argument
        rtsp_op("setup", {"name": "CSeq", "in": "header", "type": "integer"}),  # an RTSP command, not a URL
        rtsp_op("set_parameter", q("body", required=True)),
    )  # fmt: skip
    assert ms.streaming_family(v1) == "rtsp"
    doc, notes = ms.convert(v1, "network-video", CTX, "rtsp")
    ops = doc["operations"]
    assert list(ops) == ["stream_casing_url", "stream_all_url"]
    assert ops["stream_casing_url"]["binding"] == {"rtsp": {"query": {"event": "on", "eventtopic": "tns1:Device/Casing"}}}
    assert "params" not in ops["stream_casing_url"]
    assert set(ops["stream_all_url"]["params"]["properties"]) == {"video", "eventtopic"}
    skipped = [d for k, d in notes.items if k == "op-skipped"]
    assert len(skipped) == 3 and any("subset" in d for d in skipped)
    check(doc)


def test_ssm_path_is_taken_from_the_operation_name() -> None:
    v1 = v1_spec("media", ["rtsp"], rtsp_op("ssm", q("audio"), name="DESCRIBE rtsp://<servername>/axis-media/ssm/media.amp"))
    doc, _ = ms.convert(v1, "network-video", CTX, "rtsp")
    assert doc["operations"]["ssm_url"]["binding"] == {"rtsp": {"path": "/axis-media/ssm/media.amp"}}


def test_cgi_streams_mix_calls_streams_and_urls() -> None:
    v1 = v1_spec(
        "media", ["http_stream", "rtsp"],
        {"id": "get_media", "name": "get_media", "kind": "stream", "summary": "Media.", "http": {"method": "GET", "path": "/axis-cgi/media.cgi"},
         "params": [{"name": "fps", "in": "query", "type": "integer", "required": False}],
         "response": {"format": "binary", "content_type": "video/x-matroska"}},
        {"id": "get_mjpeg", "name": "get_mjpeg", "kind": "stream", "summary": "MJPEG.", "http": {"method": "GET", "path": "/axis-cgi/media.cgi"},
         "params": [], "response": {"format": "multipart", "content_type": "multipart/x-mixed-replace; boundary=x"}},
        {"id": "monitor", "name": "monitor", "kind": "stream", "summary": "Ports.", "http": {"method": "GET", "path": "/axis-cgi/media.cgi"},
         "params": [], "response": {"format": "text", "content_type": "text/plain"}},
        {"id": "transmit", "name": "transmit", "kind": "stream", "summary": "Upload.", "http": {"method": "POST", "path": "/axis-cgi/media.cgi"},
         "params": [{"name": "body", "in": "json_body", "type": "binary", "required": True}]},
        {"id": "status", "name": "status", "kind": "http_endpoint", "summary": "Status.", "http": {"method": "GET", "path": "/axis-cgi/media.cgi"},
         "params": [], "response": {"format": "text"}},
        rtsp_op("live", q("audio", type="integer", enum=[0, 1])),
    )  # fmt: skip
    assert ms.streaming_family(v1) == "cgi"
    doc, notes = ms.convert(v1, "network-video", CTX, "cgi")
    ops = doc["operations"]
    assert doc["family"] == "cgi" and doc["binding"] == {"path": "/axis-cgi/media.cgi"}
    assert ops["get_media"]["binding"]["reply"] == "stream" and "result" not in ops["get_media"]
    assert ops["get_mjpeg"]["binding"]["reply"] == {"stream": {"decoder": "mjpeg"}}
    assert ops["monitor"]["binding"]["reply"] == {"stream": {"decoder": "lines"}}
    assert "transmit" not in ops and ops["status"]["binding"]["reply"] == "text"
    assert ops["live_url"]["binding"] == {"rtsp": {}}
    check(doc)


def test_companion_specs_split_the_deferred_parts() -> None:
    heartbeat = v1_spec(
        "heartbeat", ["other", "soap"],
        {"id": "heartbeat", "name": "axhbt:Heartbeat (JSON)", "kind": "http_endpoint", "summary": "Json.",
         "http": {"method": "POST", "path": "/vapix/axhbt"}, "params": [], "response": {"format": "json"}},
        {"id": "heartbeat_soap", "name": "axhbt:Heartbeat (SOAP)", "kind": "soap_operation", "summary": "Send a heartbeat via SOAP.",
         "http": {"method": "POST", "path": "/vapix/services"}, "soap": {"operation": "Heartbeat", "input_element": "axhbt:Heartbeat"},
         "params": [{"name": "Duration", "in": "soap_body", "type": "integer", "required": True}],
         "response": {"format": "xml", "fields": [{"name": "SessionId", "type": "string"}]}},
        soap={"namespaces": {"axhbt": "http://www.axis.com/vapix/ws/Heartbeat"}},
    )  # fmt: skip
    aam = v1_spec(
        "axis-audio-manager-pro-api", ["other", "websocket"],
        {"id": "ws_recv_audio", "name": "recv", "kind": "ws_message", "summary": "Receive audio.",
         "http": {"method": "GET", "path": "/api/v1.2/audioSessions/{audioSessionId}/ws/recv"},
         "params": [{"name": "audioSessionId", "in": "path", "type": "string", "required": True}]},
        {"id": "notifications", "name": "stomp", "kind": "ws_message", "summary": "STOMP.", "http": {"method": "GET", "path": "/api/v1.2/notifications"}},
    )  # fmt: skip
    intercom = v1_spec(
        "intercom-service", ["other", "websocket"],
        {"id": "websocket", "name": "ws", "kind": "ws_message", "summary": "RPC and events.", "http": {"method": "GET", "path": "/vapix/intercomws"}},
    )  # fmt: skip
    found = {doc["id"]: doc for _, _, doc, _ in ms.companions([("network-video", heartbeat), ("audio-systems", aam), ("intercom", intercom)], CTX)}
    assert sorted(found) == ["axis-audio-manager-pro-ws", "heartbeat-soap", "intercom-ws"]
    soap = found["heartbeat-soap"]
    assert soap["family"] == "soap" and soap["python"]["module"] == "heartbeat_soap"
    assert soap["operations"]["heartbeat_soap"]["result"]["properties"] == {"SessionId": {"type": "string"}}
    ws = found["axis-audio-manager-pro-ws"]
    assert list(ws["operations"]) == ["ws_recv_audio"]
    assert ws["operations"]["ws_recv_audio"]["params"]["required"] == ["audioSessionId"]
    assert found["intercom-ws"]["operations"]["websocket"]["binding"] == {"session": {"path": "/vapix/intercomws"}}
    for doc in found.values():
        check(doc)
    assert [d["id"] for _, _, d, _ in ms.companions([("network-video", heartbeat)], CTX, only=["intercom-ws"])] == []


def test_main_writes_streaming_specs_and_never_overwrites(tmp_path: Path) -> None:
    src = tmp_path / "src" / "network-video"
    src.mkdir(parents=True)
    (src / "casing.yaml").write_text(yaml.safe_dump(v1_spec("casing", ["rtsp"], rtsp_op("stream", q("event", enum=["on"], required=True)))))
    out = tmp_path / "out"
    assert m.main(["--src", str(tmp_path / "src"), "--out", str(out)]) == 0
    written = (out / "network-video" / "casing.yaml").read_text()
    assert "family: rtsp" in written and "rtsp:" in written and "curated: false" in written
    (out / "network-video" / "casing.yaml").write_text("edited\n")
    assert m.main(["--src", str(tmp_path / "src"), "--out", str(out)]) == 0
    assert (out / "network-video" / "casing.yaml").read_text() == "edited\n"
