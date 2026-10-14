"""The contract harness on fixture specs: examples for SOAP, REST, streamed replies, RTSP URLs and WebSocket sessions.

These run the same code as ``tests/contract/test_examples.py`` (``run_example``) on specs generated in memory, so a
curator-written example of each kind is known to work before it is added to a real spec.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))  # tests/ -> the contract package

from contract._runner import run_example
from test_bindings import base_spec, load_module

NS = "http://www.axis.com/vapix/ws/certificates"
ACERT = "http://www.axis.com/vapix/ws/cert"


def run(spec: dict[str, Any], op_id: str, index: int = 0) -> None:
    module = load_module(spec)
    run_example(spec, module.OPS, op_id, spec["operations"][op_id]["examples"][index])


def op(binding: dict[str, Any], examples: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    return {"summary": "x", "effect": "read", "binding": binding, "examples": examples, **extra}


# -- SOAP ----------------------------------------------------------------------------

SOAP_SPEC = base_spec(
    "soap",
    {"namespace": NS, "namespaces": {"acert": ACERT}},
    {
        "create": op(
            {"action": f"{NS}/Create", "element": "Create"},
            [
                {
                    "title": "Create with prefixed names",
                    "request": {"params": {"acert:Id": "c1", "@acert:flag": True, "Subject": {"acert:CN": "me"}}},
                    "response": {"text": f'<CreateResponse xmlns="{NS}" xmlns:c="{ACERT}"><c:Id>c1</c:Id><Size>2</Size></CreateResponse>'},
                },
                {
                    "title": "Raw body wins",
                    "request": {"body": f'<Create xmlns="{NS}" xmlns:acert="{ACERT}" acert:flag="true"><acert:Id>c1</acert:Id></Create>',
                                "params": {"acert:Id": "c1", "@acert:flag": True}},
                },
                {
                    "title": "Fault",
                    "request": {"params": {"acert:Id": "dup"}},
                    "response": {"error": {"code": "ter:InvalidArgs", "message": "Duplicate"}},
                },
            ],
            effect="write",
            params={"type": "object", "required": ["acert:Id"], "properties": {
                "acert:Id": {"type": "string"}, "@acert:flag": {"type": "boolean"},
                "Subject": {"type": "object", "x-name": "CreateSubject", "properties": {"acert:CN": {"type": "string"}}}}},
            result={"$ref": "#/types/Created"},
            errors={"ter:InvalidArgs": {"description": "Bad", "kind": "invalid_argument"}},
        ),
    },
    types={"Created": {"type": "object", "required": ["acert:Id"], "properties": {"acert:Id": {"type": "string"}, "Size": {"type": "integer"}}}},
)  # fmt: skip


@pytest.mark.parametrize("index", [0, 1, 2])
def test_soap_examples_with_prefixed_names(index: int) -> None:
    run(SOAP_SPEC, "create", index)


def test_soap_example_that_differs_from_what_is_sent_fails() -> None:
    spec = {**SOAP_SPEC, "operations": {"create": {**SOAP_SPEC["operations"]["create"], "examples": [
        {"title": "wrong", "request": {"params": {"acert:Id": "c1"}}, "response": {"text": f'<CreateResponse xmlns="{NS}"><Id>c1</Id></CreateResponse>'}},
    ]}}}  # fmt: skip
    module = load_module(spec)
    wrong = {"title": "wrong", "request": {"params": {"acert:Id": "c1"}, "body": f'<Create xmlns="{NS}"><Id>c1</Id></Create>'}}
    with pytest.raises(AssertionError):
        run_example(spec, module.OPS, "create", wrong)  # the prefixed element is in another namespace than the example's


# -- REST ----------------------------------------------------------------------------

REST_SPEC = base_spec(
    "rest",
    {"root": "/vapix/things"},
    {
        "get_thing": op(
            {"method": "GET", "path": "/{id}", "query": ["detail"]},
            [
                {"title": "ok", "request": {"path": "/t1", "query": {"detail": "true"}}, "response": {"status": 200, "body": {"id": "t1", "name": "a"}}},
                {"title": "missing", "request": {"path": "/nope"}, "response": {"status": 404, "body": {"message": "no"}}},
            ],
            params={"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}, "detail": {"type": "boolean"}}},
            result={"$ref": "#/types/Thing"},
            errors={404: {"description": "Missing", "kind": "not_found"}},
        ),
        "create_thing": op(
            {"method": "POST", "body": "object"},
            [{"title": "create", "request": {"body": {"name": "n"}}, "response": {"status": 200, "body": {"id": "t2"}}}],
            effect="write", write="create",
            params={"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}},
            result={"$ref": "#/types/Thing"},
        ),
    },
    types={"Thing": {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}, "name": {"type": "string"}}}},
)  # fmt: skip


@pytest.mark.parametrize(("op_id", "index"), [("get_thing", 0), ("get_thing", 1), ("create_thing", 0)])
def test_rest_examples(op_id: str, index: int) -> None:
    run(REST_SPEC, op_id, index)


# -- streamed replies ----------------------------------------------------------------

STREAM_SPEC = base_spec(
    "cgi",
    {"path": "/axis-cgi/mjpg/video.cgi"},
    {
        "mjpeg": op(
            {"reply": {"stream": {"decoder": "mjpeg"}}},
            [{
                "title": "Two frames",
                "request": {"query": {"fps": "5"}},
                "response": {
                    "content_type": "multipart/x-mixed-replace; boundary=b",
                    "text": "--b\r\nContent-Type: image/jpeg\r\nContent-Length: 3\r\n\r\nabc\r\n--b\r\nContent-Type: image/jpeg\r\nContent-Length: 2\r\n\r\nde\r\n--b--\r\n",
                    "items": ["abc", "de"],
                },
            }],
            params={"type": "object", "properties": {"fps": {"type": "integer"}}},
        ),
        "monitor": op(
            {"path": "/axis-cgi/io/port.cgi", "query": {"monitor": "all"}, "reply": {"stream": {"decoder": "lines"}}},
            [{"title": "Ports", "request": {"query": {"monitor": "all"}}, "response": {"text": "0=active\n1=inactive\n", "items": ["0=active", "1=inactive"]}}],
        ),
        "download": op({"path": "/axis-cgi/media.cgi", "reply": "stream"}, [{"title": "Request only"}]),
    },
)  # fmt: skip


@pytest.mark.parametrize("op_id", ["mjpeg", "monitor", "download"])
def test_stream_examples(op_id: str) -> None:
    run(STREAM_SPEC, op_id)


def test_stream_example_with_wrong_items_fails() -> None:
    spec = {**STREAM_SPEC}
    module = load_module(spec)
    bad = {"request": {"query": {"monitor": "all"}}, "response": {"text": "a\n", "items": ["b"]}}
    with pytest.raises(AssertionError):
        run_example(spec, module.OPS, "monitor", bad)


# -- RTSP URLs -----------------------------------------------------------------------

RTSP_SPEC = base_spec(
    "rtsp",
    {},
    {
        "stream": op(
            {"rtsp": {"query": {"videocodec": "h264"}}},
            [
                {"title": "Live", "request": {"params": {"resolution": "1280x720", "audio": False}},
                 "response": {"url": "rtsp://camera.test:554/axis-media/media.amp?videocodec=h264&resolution=1280x720&audio=0"}},
                {"title": "Credentials and port", "request": {"params": {}, "port": 8554, "include_credentials": True},
                 "response": {"url": "rtsp://root:pass@camera.test:8554/axis-media/media.amp?videocodec=h264"}},
            ],
            params={"type": "object", "properties": {"resolution": {"type": "string"}, "audio": {"type": "boolean"}}},
        ),
    },
)  # fmt: skip


@pytest.mark.parametrize("index", [0, 1])
def test_rtsp_examples(index: int) -> None:
    run(RTSP_SPEC, "stream", index)


def test_rtsp_example_with_wrong_url_fails() -> None:
    module = load_module(RTSP_SPEC)
    with pytest.raises(AssertionError):
        run_example(RTSP_SPEC, module.OPS, "stream", {"request": {"params": {}}, "response": {"url": "rtsp://camera.test:554/other"}})


# -- sessions ------------------------------------------------------------------------

WS_SPEC = base_spec(
    "ws",
    {},
    {
        "connect": op(
            {"session": {"path": "/vapix/ws-data-stream", "query": {"sources": "events"}, "codec": "events"}},
            [{
                "title": "Filtered events",
                "request": {
                    "connect": {"event_filter_list": [{"topicFilter": "tns1:Device/tnsaxis:IO/VirtualPort"}]},
                    "messages": [{"method": "events:configure", "params": {"eventFilterList": [{"topicFilter": "tns1:Device/tnsaxis:IO/VirtualPort"}]}}],
                },
            }],
        ),
        "audio_session": op(
            {"session": {"path": "/api/v1.2/audioSessions/{audioSessionId}/ws/recv"}},
            [{"title": "One session", "request": {"params": {"audioSessionId": "a#b 1"}, "path": "/api/v1.2/audioSessions/a%23b%201/ws/recv"}},
             {"title": "Path from the binding", "request": {"params": {"audioSessionId": "s1"}}}],
            params={"type": "object", "required": ["audioSessionId"], "properties": {"audioSessionId": {"type": "string"}}},
        ),
    },
)  # fmt: skip


@pytest.mark.parametrize(("op_id", "index"), [("connect", 0), ("audio_session", 0), ("audio_session", 1)])
def test_session_examples(op_id: str, index: int) -> None:
    run(WS_SPEC, op_id, index)


def test_session_example_with_wrong_message_fails() -> None:
    module = load_module(WS_SPEC)
    bad = {"request": {"connect": {"event_filter_list": [{"topicFilter": "t"}]}, "messages": [{"method": "other"}]}}
    with pytest.raises(AssertionError):
        run_example(WS_SPEC, module.OPS, "connect", bad)


def test_contract_skip_marker_still_applies_to_special_kinds() -> None:
    module = load_module(RTSP_SPEC)
    with pytest.raises(pytest.skip.Exception):
        run_example(RTSP_SPEC, module.OPS, "stream", {"x-contract": {"skip": "needs a real device"}, "request": {"params": {}}})
