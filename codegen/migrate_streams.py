"""Migration of the v1 specs that describe WebSocket sessions, HTTP streams and RTSP URLs.

``migrate_v1.main`` calls ``streaming_family`` for every v1 spec no other converter claims and
``companions`` for specs whose deferred parts become a second spec. The output uses the spec
features of the ws/rtsp/stream bindings (see docs/spec-format.md):

- ``ws``: ``binding.session`` operations (``connect``) for event streaming and Device Data Hub.
  In-session requests (``events:configure``, ``data-hub_v1:subscribe``) are not operations.
- ``cgi`` with ``reply: {stream: ...}`` operations and ``binding.rtsp`` URL operations (media.cgi,
  audio receive, RTSP query parameters) next to the plain CGI calls of the same v1 spec.
- ``rtsp``: APIs that only describe RTSP URLs.
- companions: ``heartbeat`` -> ``heartbeat-soap`` (SOAP), AAM Pro -> ``axis-audio-manager-pro-ws``,
  intercom -> ``intercom-ws`` and ``intercom-configuration``.

Everything is written as ``curated: false``; RTSP commands that must be driven (DESCRIBE, SETUP,
GET_PARAMETER, tunnelling over HTTP) and STOMP notifications are skipped with a note.
"""

from __future__ import annotations

import copy
import re

from codegen import migrate_v1 as m

MEDIA_PATH = "/axis-media/media.amp"

# Endpoint, fixed handshake query and codec of the session APIs the runtime has codecs for.
WS_SESSIONS = {
    "event-streaming-over-websocket": ("/vapix/ws-data-stream", {"sources": "events"}, "events"),
    "datahub-streaming-over-websocket": ("/vapix/ws/v1", {"apis": "data-hub"}, "datahub"),
}


def streaming_family(v1):
    """``ws``, ``rtsp`` or ``cgi`` for the streaming specs handled here, else ``None``."""
    ops = v1.get("operations") or []
    kinds = {o.get("kind") for o in ops}
    styles = v1.get("styles") or []
    if styles and styles[0] == "websocket" and "stream" in kinds:
        return "ws"
    if kinds and kinds <= {"rtsp_request", "soap_operation"} and "rtsp_request" in kinds:
        return "rtsp"
    if kinds & {"stream", "rtsp_request"} and kinds <= {"stream", "rtsp_request", "http_endpoint"}:
        return "cgi" if _cgi_ops(ops) else "rtsp"
    return None


def _cgi_ops(ops):
    return [o for o in ops if o.get("kind") == "http_endpoint" or _stream_op(o)]


# --------------------------------------------------------------------------- shared helpers


def _finish(v1, section, family, notes, access, binding, api_errors, types, ops_out, *, keep_types):
    """Header, discovery, types, operations, sources and provenance (cf. ``migrate_v1._finish_doc``)."""
    modname = (v1.get("python") or {}).get("module") or m.snake(v1["id"])
    doc = m.common_header(v1, section, family, notes, {"module": modname, "class": m.class_name(v1)})
    doc["access"] = access
    disc = _discovery(v1, notes)
    if disc:
        doc["discovery"] = disc
    requires = m.convert_requires(v1)
    if requires:
        doc["requires"] = requires
    doc["binding"] = binding
    if api_errors:
        doc["errors"] = api_errors
    if not keep_types:
        used = m.reachable_types(types, ops_out)
        dropped = sorted(set(types) - used)
        if dropped:
            notes.add("types-dropped", "types not referenced by any migrated operation: " + ", ".join(dropped))
        types = {k: v for k, v in types.items() if k in used}
    if types:
        doc["types"] = types
    doc["operations"] = ops_out
    doc["sources"] = m.convert_sources(v1)
    for key in ("param_cgi_groups", "events", "versioning", "envelope", "notes"):
        if v1.get(key):
            notes.add("dropped-section", f"v1 section {key} not carried over")
    m.check_refs(doc, notes)
    m.finalize(doc, notes)
    prov = {"completeness": (v1.get("provenance") or {}).get("completeness", "partial")}
    open_questions = list((v1.get("provenance") or {}).get("open_questions") or []) + notes.render()
    if open_questions:
        prov["open_questions"] = open_questions
    prov["migrated_from"] = "v1"
    prov["curated"] = False
    doc["provenance"] = prov
    return doc


def _discovery(v1, notes):
    entries = m.convert_discovery(v1, notes, "cgi")
    for entry in entries:
        param = entry.get("param")
        if param and re.search(r"[<>]", str(param.get("value", ""))):
            notes.add("discovery", f"{param['name']}: the documented value {param['value']!r} is a placeholder; only the property's existence is checked")
            param.pop("value")
    return entries


def _access(v1):
    level = (v1.get("auth") or {}).get("default_access_level")
    return level if level in m.ACCESS_LEVELS else "admin"


def _header(op, oid, access, effect="read"):
    out = m._op_header(op, oid, access, effect, None)
    return out


def _skip(notes, op, why):
    notes.add("op-skipped", f"{op['id']}: {why}")


# --------------------------------------------------------------------------- WebSocket sessions


def convert_ws(v1, section, ctxinfo):
    """Event streaming and Device Data Hub: one ``connect`` session operation."""
    notes = m.Notes()
    access = _access(v1)
    ops_out = {}
    used = set()
    for op in v1["operations"]:
        kind = op.get("kind")
        if kind == "stream":
            oid = m._unique_op_id(op, used)
            path, query, codec = _session_of(v1, op, notes)
            o = _header(op, oid, access)
            o["binding"] = {"session": _drop_empty({"path": path, "query": query, "codec": codec if codec != "raw" else None})}
            ops_out[oid] = o
        elif kind == "ws_message":
            _skip(notes, op, "an in-session message: sent with session.request(method, params), or a notification the codec parses (EventNotification, TopicSample)")
        elif "wssession" in op["id"] or "session_token" in op["id"]:
            _skip(notes, op, "the session token is handled by connect(use_token=True)")
        else:
            _skip(notes, op, f"kind {kind} is not a session")
    if not ops_out:
        return None, notes
    v1types = v1.get("types") or {}
    typemap = m.make_typemap(list(v1types))
    ctx = m.Ctx(notes, typemap, v1types)
    types = {typemap[n]: m.conv(m.strip_xml_hints(s), ctx) for n, s in v1types.items()}
    reserved = {"EventFilter", "Notification"} if v1["id"] in ("event-streaming-over-websocket",) else set()
    for name in sorted(set(types) & reserved):
        del types[name]
        notes.add("types-dropped", f"{name}: the runtime's EventFilter/EventNotification replace it")
    errors = m.convert_errors(v1.get("errors"), notes, scope="general")
    doc = _finish(v1, section, "ws", notes, access, {}, errors, types, ops_out, keep_types=True)
    return doc, notes


def _session_of(v1, op, notes):
    known = WS_SESSIONS.get(v1["id"])
    path = (op.get("http") or {}).get("path") or "/"
    if known:
        return known
    query = {}
    for p in op.get("params") or []:
        if p.get("in") == "query" and p.get("required") and (p.get("default") is not None or len(p.get("enum") or []) == 1):
            query[p["name"]] = p.get("default") if p.get("default") is not None else p["enum"][0]
    notes.add("session-codec", f"{op['id']}: no runtime codec for this API; the session is raw (frames pass through)")
    return path, query, "raw"


def _drop_empty(d):
    return {k: v for k, v in d.items() if v not in (None, {}, [])}


# --------------------------------------------------------------------------- RTSP URL operations


def _rtsp_path(v1, op):
    """Path of the RTSP endpoint named by the operation or the API (``/axis-media/ssm/media.amp``)."""
    for text in (op.get("name"), op.get("summary"), *(((v1.get("transport") or {}).get("base_paths")) or [])):
        match = re.search(r"rtsp://[^/\s]+(/[\w./-]*)", text or "")
        if match:
            path = match.group(1)
            if path.startswith("/axis-media/"):
                return path
    return MEDIA_PATH


def _rtsp_candidate(op):
    """The ``rtsp_query`` parameters, or ``None`` if the operation is an RTSP command rather than a URL."""
    params = [p for p in op.get("params") or [] if p.get("in") == "rtsp_query"]
    if not params or any(p["name"] == "body" or p.get("type") == "object" for p in params):
        return None
    return params


def rtsp_ops(v1, ops, ctx, notes, access, used, existing=()):
    """``(oid, v2 operation)`` pairs for the URL-carrying RTSP operations of ``ops``."""
    out = {}
    seen = []  # (path, fixed, parameter names) of the operations kept so far
    for op in ops:
        if op.get("kind") != "rtsp_request":
            continue
        params = _rtsp_candidate(op)
        if params is None:
            _skip(notes, op, "an RTSP command or session request (DESCRIBE/SETUP/GET_PARAMETER ...), not a URL; RTSP clients drive these")
            continue
        path = _rtsp_path(v1, op)
        if "axismedia" in ((v1.get("transport") or {}).get("base_paths") or [""])[0]:
            notes.add("rtsp-path", "the documented path 'axismedia/media.amp' is a typo; /axis-media/media.amp is used")
        fixed, props, required = {}, {}, []
        for p in params:
            single = p.get("enum") if len(p.get("enum") or []) == 1 else None
            if p.get("required") and (single or p.get("default") is not None):
                fixed[p["name"]] = single[0] if single else p["default"]
                continue
            schema = m.cgi_param(p, ctx, notes, op["id"])
            props[p["name"]] = schema
            if p.get("required"):
                required.append(p["name"])
        names = set(props)
        if any(path == q[0] and fixed == q[1] and names <= q[2] for q in seen):
            _skip(notes, op, "the same URL as an earlier operation (its parameters are a subset)")
            continue
        seen.append((path, fixed, names))
        oid = m._unique_op_id({"id": op["id"] if op["id"].endswith("_url") else op["id"] + "_url"}, used | set(existing))
        used.add(oid)
        o = _header(op, oid, access)
        rtsp = {}
        if path != MEDIA_PATH:
            rtsp["path"] = path
        if fixed:
            rtsp["query"] = {k: str(v) for k, v in fixed.items()}
        o["binding"] = {"rtsp": rtsp}
        if props:
            schema = {"type": "object"}
            if required:
                schema["required"] = required
            schema["properties"] = props
            o["params"] = schema
        out[oid] = o
    return out


# --------------------------------------------------------------------------- HTTP stream operations


def _stream_op(op):
    """A GET stream operation this converter can express (no request body, no tunnelling header)."""
    if op.get("kind") != "stream":
        return False
    http = op.get("http") or {}
    if (http.get("method") or "GET").upper() != "GET" or http.get("request_content_type"):
        return False
    return not any(p.get("in") in ("header", "json_body", "form", "multipart", "path") for p in op.get("params") or [])


def _decoder(op):
    response = op.get("response") or {}
    content_type = (response.get("content_type") or (op.get("http") or {}).get("response_content_type") or "").lower()
    if content_type.startswith("multipart/x-mixed-replace") and "audio" not in content_type:
        return "mjpeg"
    if response.get("format") == "text" and content_type.startswith("text/"):
        return "lines"
    return "bytes"


def convert_cgi_streams(v1, section, ctxinfo):
    """Specs with ``stream`` and ``rtsp_request`` operations: CGI calls, ``reply: stream`` operations and RTSP URLs."""
    notes = m.Notes()
    http_ops = []
    marked = {}
    for op in v1["operations"]:
        kind = op.get("kind")
        if kind == "http_endpoint":
            http_ops.append(op)
        elif kind == "stream":
            if _stream_op(op):
                clone = copy.deepcopy(op)
                clone["kind"] = "http_endpoint"
                clone["response"] = dict(clone.get("response") or {}, format="binary")
                clone["response"].pop("schema", None)
                http_ops.append(clone)
                marked[m.snake(op["id"])] = _decoder(op)
            else:
                _skip(notes, op, "a request body, tunnelling headers or a path argument; uploads and RTSP-over-HTTP are not stream replies")
    base = copy.deepcopy(v1)
    base["operations"] = http_ops
    doc, cgi_notes = (m.convert_cgi(base, section, ctxinfo) if http_ops else (None, m.Notes()))
    notes.items.extend(cgi_notes.items)
    notes.dropped.update(cgi_notes.dropped)
    access = doc["access"] if doc else _access(v1)

    v1types = {}
    ctx = m.Ctx(notes, m.make_typemap([]), v1types)
    used = set(doc["operations"]) if doc else set()
    urls = rtsp_ops(v1, v1["operations"], ctx, notes, access, used)
    if doc is None:
        if not urls:
            return None, notes
        return _rtsp_doc(v1, section, notes, access, urls), notes
    for oid, decoder in marked.items():
        o = doc["operations"].get(oid)
        if o is None:
            continue
        o["binding"]["reply"] = {"stream": {"decoder": decoder}} if decoder != "bytes" else "stream"
        o.pop("result", None)
        o.pop("examples", None)
        o["effect"] = "read"
        o.pop("write", None)
    doc["operations"].update(urls)
    doc["provenance"]["open_questions"] = [q for q in doc["provenance"].get("open_questions", []) if not q.startswith("migration:")] + notes.render()
    return doc, notes


def _rtsp_doc(v1, section, notes, access, urls):
    return _finish(v1, section, "rtsp", notes, access, {}, {}, {}, urls, keep_types=True)


def convert_rtsp(v1, section, ctxinfo):
    """APIs that are only RTSP URLs (event streams, metadata streams)."""
    notes = m.Notes()
    for op in v1["operations"]:
        if op.get("kind") == "soap_operation":
            _skip(notes, op, "a SOAP call; the Event service spec covers it")
    ctx = m.Ctx(notes, m.make_typemap([]), {})
    access = _access(v1)
    urls = rtsp_ops(v1, v1["operations"], ctx, notes, access, set())
    if not urls:
        return None, notes
    return _rtsp_doc(v1, section, notes, access, urls), notes


def convert(v1, section, ctxinfo, family):
    return {"ws": convert_ws, "cgi": convert_cgi_streams, "rtsp": convert_rtsp}[family](v1, section, ctxinfo)


# --------------------------------------------------------------------------- companion specs


def companions(loaded, ctxinfo, only=None):
    """``(section, id, doc, notes)`` for the deferred parts of specs another converter already handles."""
    out = []
    by_id = {v1["id"]: (section, v1) for section, v1 in loaded}
    for builder, source in (
        (heartbeat_soap, "heartbeat"),
        (aam_pro_ws, "axis-audio-manager-pro-api"),
        (intercom_ws, "intercom-service"),
        (intercom_configuration, "intercom-service"),
    ):
        if source in by_id:
            section, v1 = by_id[source]
            doc, notes = builder(copy.deepcopy(v1), section, ctxinfo)
            if doc is not None and (not only or source in only or doc["id"] in only):
                out.append((section, doc["id"], doc, notes))
    return out


def _rename(v1, new_id, name, module, class_name, summary=None, keep_questions=True):
    """Turn a copy of the parent's v1 spec into the companion's: own id, names and summary."""
    v1["id"] = new_id
    v1["name"] = name
    v1["python"] = {"module": module, "class_name": class_name}
    if summary:
        v1["summary"] = summary
    if not keep_questions:
        v1["provenance"] = dict(v1.get("provenance") or {}, open_questions=[])
    return v1


def heartbeat_soap(v1, section, ctxinfo):
    """The SOAP twin of the JSON Heartbeat service."""
    ops = [o for o in v1["operations"] if o.get("kind") == "soap_operation"]
    for op in ops:
        response = op.setdefault("response", {})
        if not isinstance(response.get("schema"), dict) and response.get("fields"):
            response["schema"] = {
                "type": "object",
                "properties": {f["name"]: {"type": f.get("type", "string"), "description": f.get("description", "")} for f in response["fields"]},
            }
    v1["operations"] = ops
    v1["styles"] = ["soap"]
    _rename(
        v1, "heartbeat-soap", "Heartbeat service API (SOAP)", "heartbeat_soap", "HeartbeatSoapApi",
        "Send heartbeats to a device through the SOAP twin of the Heartbeat service (see heartbeat for the JSON form).",
    )
    return m.convert_service(v1, section, ctxinfo, "soap")


def _raw_ws_op(op, oid, access, path, notes):
    o = _header(op, oid, access)
    o["binding"] = {"session": {"path": path}}
    placeholders = re.findall(r"\{(\w+)\}", path)
    if placeholders:
        o["params"] = {"type": "object", "required": placeholders, "properties": {n: {"type": "string"} for n in placeholders}}
    return o


def aam_pro_ws(v1, section, ctxinfo):
    """Binary audio WebSockets of the Audio Manager Pro server (raw sessions with a session id in the path)."""
    notes = m.Notes()
    access = _access(v1)
    used, ops_out = set(), {}
    for op in v1["operations"]:
        if op.get("kind") != "ws_message":
            continue
        path = (op.get("http") or {}).get("path", "")
        if "{" not in path:
            _skip(notes, op, "STOMP notifications over WebSocket: needs a STOMP codec (not available); the payload formats are undocumented")
            continue
        oid = m._unique_op_id(op, used)
        ops_out[oid] = _raw_ws_op(op, oid, access, path, notes)
    if not ops_out:
        return None, notes
    _rename(
        v1, "axis-audio-manager-pro-ws", "AXIS Audio Manager Pro WebSocket audio", "axis_audio_manager_pro_ws", "AxisAudioManagerProWs",
        "Send and receive binary audio of an Audio Manager Pro audio session over a WebSocket.", keep_questions=False,
    )
    v1["discovery"] = []
    notes.add("session-codec", "binary audio frames pass through unchanged (raw sessions); send bytes as binary frames")
    return _finish(v1, section, "ws", notes, access, {}, {}, {}, ops_out, keep_types=True), notes


def intercom_ws(v1, section, ctxinfo):
    """The ``/vapix/intercomws`` WebSocket (JSON-RPC and event notifications) as a raw session."""
    notes = m.Notes()
    access = _access(v1)
    used, ops_out = set(), {}
    for op in v1["operations"]:
        if op.get("kind") == "ws_message":
            oid = m._unique_op_id(op, used)
            ops_out[oid] = _raw_ws_op(op, oid, access, (op.get("http") or {}).get("path", "/vapix/intercomws"), notes)
            notes.add("session-codec", f"{oid}: Google JSON / JSON-RPC messages (axev:subscribe ...) are not decoded; send dicts, receive text and json.loads it")
    if not ops_out:
        return None, notes
    _rename(
        v1, "intercom-ws", "Intercom service WebSocket", "intercom_ws", "IntercomWs",
        "WebSocket endpoint of the Intercom service for RPC calls and event notifications.", keep_questions=False,
    )
    v1["discovery"] = [d for d in v1.get("discovery") or [] if d.get("method") != "other"]
    return _finish(v1, section, "ws", notes, access, {}, {}, {}, ops_out, keep_types=True), notes


def intercom_configuration(v1, section, ctxinfo):
    """The REST resource ``/vapix/intercom/Configuration`` (GET, POST, PUT) as three operations."""
    op = next((o for o in v1["operations"] if o["id"] == "configuration_resource"), None)
    if op is None:
        return None, m.Notes()
    ops = []
    for oid, method, summary, wanted in (
        ("get_configuration", "GET", "Get the configuration.", ("includeImageFile",)),
        ("update_configuration", "POST", "Update the configuration (UpdateConfiguration).", ("Configuration", "imageFile")),
        ("set_configuration", "PUT", "Replace the configuration (SetConfiguration).", ("Configuration", "imageFile")),
    ):
        clone = copy.deepcopy(op)
        clone.update(id=oid, name=oid, summary=summary)
        clone["http"] = dict(clone["http"], method=method)
        clone["http"].pop("alt_methods", None)
        clone["params"] = [dict(p, **({"in": "query"} if method == "GET" else {})) for p in clone["params"] if p["name"] in wanted]
        if method != "GET":
            clone["response"] = {k: v for k, v in clone["response"].items() if k != "schema"} if method == "PUT" else clone["response"]
        ops.append(clone)
    v1["operations"] = ops
    v1["styles"] = ["other"]
    v1["errors"] = []
    for o in ops:
        o["errors"] = []
    _rename(
        v1, "intercom-configuration", "Intercom configuration resource", "intercom_configuration", "IntercomConfiguration",
        "Get, update or replace the intercom configuration as a REST resource.",
    )
    v1["discovery"] = [d for d in v1.get("discovery") or [] if d.get("method") != "other"]
    return m.convert_rest(v1, section, ctxinfo)
