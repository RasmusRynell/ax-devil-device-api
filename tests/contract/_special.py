"""Examples of streamed replies, WebSocket sessions and RTSP URL builders (see docs/spec-format.md, "Examples").

Each kind is exercised through the generated API method, with fake transports:

- ``stream``: the request is compared like a ``cgi`` request; ``response`` is served and, when it names ``items``,
  the decoded items are compared.
- ``rtsp``: the URL the method returns is compared with ``response.url``.
- ``session``: a fake WebSocket camera accepts the handshake; its path, query and the messages sent right after it
  are compared with ``request.path``, ``request.query`` and ``request.messages``.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote

import httpx
import pytest

from ax_devil_device_api import Heartbeat
from ax_devil_device_api.device import Device

from . import _harness as h

ROOT = Path(__file__).resolve().parents[2]
CREDENTIALS = ("root", "pass")
HOST = "camera.test"


def _codegen_naming() -> Any:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return importlib.import_module("codegen.naming")


def _properties(spec: dict[str, Any], schema: dict[str, Any] | None) -> dict[str, Any]:
    resolved: dict[str, Any] = schema or {}
    if "$ref" in resolved:
        resolved = (spec.get("types") or {})[resolved["$ref"].rsplit("/", 1)[-1]] or {}
    return resolved.get("properties") or {}


def python_kwargs(spec: dict[str, Any], op_spec: dict[str, Any], params: dict[str, Any] | None) -> dict[str, Any]:
    """The example's ``params`` (wire names) as keyword arguments of the generated method."""
    naming = _codegen_naming()
    props = _properties(spec, op_spec.get("params"))
    out = {}
    for wire, value in (params or {}).items():
        if wire not in props:
            raise AssertionError(f"example params name {wire!r}, which the operation does not declare")
        out[naming.field_name(wire, (props[wire] or {}).get("x-python-name"))] = value
    return out


def api_classes(spec: dict[str, Any], ops: Any) -> tuple[Any, Any]:
    """(sync API class, async API class) of the module that defines ``ops``."""
    module = sys.modules[ops.__module__]
    name = spec["python"]["class"]
    name = name[:-3] if name.endswith("Api") and len(name) > 3 else name
    return getattr(module, f"{name}Api"), getattr(module, f"Async{name}Api")


def run_special(kind: str, spec: dict[str, Any], ops: Any, op_id: str, example: dict[str, Any]) -> None:
    if bool((example.get("x-contract") or {}).get("template")):
        pytest.skip("template examples are not run for stream, session and rtsp operations")
    {"stream": _stream, "rtsp": _rtsp, "session": _session}[kind](spec, ops, op_id, example)


# -- streamed replies ----------------------------------------------------------------


def _stream(spec: dict[str, Any], ops: Any, op_id: str, example: dict[str, Any]) -> None:
    op = getattr(ops, op_id)
    request = example.get("request") or {}
    response = example.get("response") or {}
    model, expected_args = h.build_cgi(op, request)
    decoder = getattr(op.binding.reply, "decoder", "bytes")

    def handler(sent: h.Sent) -> httpx.Response:
        content_type = response.get("content_type") or ("multipart/x-mixed-replace; boundary=b" if decoder == "mjpeg" else "application/octet-stream")
        return httpx.Response(response.get("status", 200), content=str(response.get("text", "")).encode(), headers={"content-type": content_type})

    fake = h.Fake(handler)
    with Device(HOST, credentials=CREDENTIALS, transport=httpx.MockTransport(fake)) as dev:
        stream = dev.invoke(op, model)
        with stream as opened:
            if "items" in response:
                items = [item.body.decode() if decoder == "mjpeg" else item for item in opened]
                if decoder == "bytes":
                    assert b"".join(items) == b"".join(str(i).encode() for i in response["items"])
                else:
                    assert items == response["items"]
    assert len(fake.calls) == 1, f"expected one request, got {len(fake.calls)}"
    sent = fake.calls[0]
    assert sent.method == op.binding.method and sent.path == op.binding.path
    assert {**sent.query, **(sent.form or {})} == expected_args
    h.check_sent_body(op, request, sent)


# -- RTSP URLs -----------------------------------------------------------------------


def _rtsp(spec: dict[str, Any], ops: Any, op_id: str, example: dict[str, Any]) -> None:
    op_spec = spec["operations"][op_id]
    request = example.get("request") or {}
    expected = (example.get("response") or {}).get("url")
    kwargs = python_kwargs(spec, op_spec, request.get("params"))
    options = {k: request[k] for k in ("port", "include_credentials") if k in request}

    def refuse(sent: h.Sent) -> httpx.Response | None:
        raise AssertionError("an RTSP operation must not make a request")

    sync_api, _ = api_classes(spec, ops)
    fake = h.Fake(refuse)
    with Device(HOST, credentials=CREDENTIALS, transport=httpx.MockTransport(fake)) as dev:
        url = getattr(dev.api(sync_api), op_id)(**kwargs, **options)
    assert not fake.calls
    if expected is not None:
        assert str(url) == expected


# -- WebSocket sessions --------------------------------------------------------------


def _handler(socket: Any, message: Any) -> None:
    """Acknowledges the setup requests of the events and data hub codecs."""
    if message.get("method") == "events:configure":
        socket.push({"apiVersion": "1.0", "context": message.get("context"), "method": "events:configure", "data": {}})
    elif "id" in message:
        socket.push({"jsonrpc": "2.0", "id": message["id"], "result": {}})


def _session(spec: dict[str, Any], ops: Any, op_id: str, example: dict[str, Any]) -> None:
    unit = str(ROOT / "tests" / "unit")
    if unit not in sys.path:
        sys.path.insert(0, unit)
    from ws_fake import FakeWsCamera

    op_spec = spec["operations"][op_id]
    session = op_spec["binding"]["session"]
    request = example.get("request") or {}
    kwargs = python_kwargs(spec, op_spec, request.get("params"))
    connect = dict(request.get("connect") or {})
    sync_api, _ = api_classes(spec, ops)

    camera = FakeWsCamera(handler=_handler)
    with Device(HOST, credentials=CREDENTIALS, transport=camera.transport()) as dev:
        with getattr(dev.api(sync_api), op_id)(**kwargs, **connect, heartbeat=Heartbeat(None)):
            pass
    assert len(camera.ws_requests) == 1, "expected one WebSocket handshake"
    handshake = camera.ws_requests[0]
    expected_path = request.get("path")
    if expected_path is None:
        expected_path = session["path"]
        for wire, value in (request.get("params") or {}).items():
            expected_path = expected_path.replace("{" + wire + "}", quote(str(value), safe=""))
    assert handshake.url.raw_path.split(b"?", 1)[0].decode() == expected_path
    expected_query = request.get("query")
    if expected_query is None:
        expected_query = dict(session.get("query") or {})
    got = dict(parse_qsl(handshake.url.query.decode()))
    assert got == {k: str(v) for k, v in expected_query.items()}
    if "messages" in request:
        sent = [m for m in camera.sockets[0].received]
        assert len(sent) == len(request["messages"]), f"expected {len(request['messages'])} messages after the handshake, got {len(sent)}"
        for got_message, want in zip(sent, request["messages"]):
            _assert_subset(got_message, want)


def _assert_subset(got: Any, want: Any) -> None:
    """``want`` is contained in ``got``: dicts by key (extra keys such as ``context`` or ``id`` are ignored), lists exactly."""
    if isinstance(want, dict):
        assert isinstance(got, dict), f"{got!r} is not an object"
        for key, value in want.items():
            assert key in got, f"{key!r} missing in {got!r}"
            _assert_subset(got[key], value)
    elif isinstance(want, list):
        assert isinstance(got, list) and len(got) == len(want), f"{got!r} != {want!r}"
        for g, w in zip(got, want):
            _assert_subset(g, w)
    else:
        assert got == want
