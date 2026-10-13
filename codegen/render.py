"""Render an ``ApiDef`` as the source text of one API module (unformatted)."""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from typing import Any

from .build import BUILTIN_SHADOWS, SESSION_CODECS, SESSION_SETUPS
from .loader import SpecError
from .model import ApiDef, FieldDef, OpDef, TypeDef
from .naming import last_word
from .xmlreply import reply_kind

REQUEST_OPTIONS = "request_options: RequestOptions | None = None"

WRITE_SENTENCES = {
    "replace": "Replaces the whole configuration; fields left out return to their defaults.",
    "patch": "Changes only the fields given.",
}
PATCH_ENTRIES_SENTENCE = "Changes only the entries given; entries that do not exist yet may be created."


def write_sentence(op: OpDef) -> str | None:
    """Docstring sentence for ``write``. A patch whose arguments include a list of models acts per entry (upsert style)."""
    if op.write == "patch" and any(f.model_name and f.ann.startswith("list[") for f in op.args):
        return PATCH_ENTRIES_SENTENCE
    return WRITE_SENTENCES.get(op.write or "")


# -- signatures (shared with the API surface listing) --------------------------


@dataclass
class Signature:
    args: list[str]
    """Parameters after ``self``, as source text."""
    returns: str
    overload: bool = False


def _sig_type(f: FieldDef) -> str:
    """Argument type: nullable fields accept an explicit ``None``."""
    if f.nullable and f.sig != "None" and not f.sig.endswith("| None"):
        return f"{f.sig} | None"
    return f.sig


def _arg(f: FieldDef) -> str:
    return f"{f.py}: {_sig_type(f)}" if f.required else f"{f.py}: {_sig_type(f)} | MISSING = MISSING"


STREAM_ITEMS = {"mjpeg": "Part", "lines": "str", "bytes": "bytes"}
SESSION_OPTIONS = "heartbeat: Heartbeat = DEFAULT_HEARTBEAT, use_token: bool = False"


def session_setup(op: OpDef) -> str:
    assert op.session is not None
    return op.session.get("setup") or SESSION_CODECS[op.session.get("codec", "raw")]


def special_signature(op: OpDef, is_async: bool) -> Signature | None:
    """Signature of session and rtsp operations; ``None`` for calls (which may still stream)."""
    if op.kind == "session":
        options = [f"{name}: {ann}" for name, ann in SESSION_SETUPS[session_setup(op)]]
        ret = "AbstractAsyncContextManager[AsyncSession]" if is_async else "AbstractContextManager[Session]"
        return Signature([*map(_arg, op.args), *options, "*", SESSION_OPTIONS, REQUEST_OPTIONS], ret)
    if op.kind == "rtsp":
        positional = sorted((f for f in op.args if f.py in op.positional), key=lambda f: op.positional.index(f.py))
        keyword = [f for f in op.args if f.py not in op.positional]
        return Signature([*map(_arg, positional), "*", *map(_arg, keyword), "port: int | None = None", "include_credentials: bool = False"], "RtspUrl")
    return None


def signatures(op: OpDef, is_async: bool = False) -> tuple[list[Signature], Signature | None]:
    """(overloads, implementation). Plain operations have one entry and no implementation."""
    special = special_signature(op, is_async)
    if special is not None:
        return [special], None
    ret = op.result or "None"
    if op.kind == "stream":
        ret = f"{'Async' if is_async else ''}StreamResult[{STREAM_ITEMS[op.stream_decoder or 'bytes']}]"
    if op.params is None:
        return [Signature(["*", REQUEST_OPTIONS], ret)], None
    fields = op.args
    positional = [f for f in fields if f.py in op.positional]
    positional.sort(key=lambda f: op.positional.index(f.py))
    keyword = [f for f in fields if f.py not in op.positional]
    if op.overloaded:
        name = op.params.name
        first = Signature([f"request: {name}", "/", "*", REQUEST_OPTIONS], ret, overload=True)
        second = Signature([*map(_arg, positional), "/", "*", *map(_arg, keyword), REQUEST_OPTIONS], ret, overload=True)
        if positional:
            impl = Signature(["request: Any = MISSING", "/", "*args: Any", REQUEST_OPTIONS, "**kwargs: Any"], ret)
        else:
            impl = Signature([f"request: {name} | None = None", "/", "*", REQUEST_OPTIONS, "**kwargs: Any"], ret)
        return [first, second], impl
    args = [_arg(f) for f in positional] + ["*", *map(_arg, keyword), REQUEST_OPTIONS]
    return [Signature(args, ret)], None


# -- helpers ---------------------------------------------------------------------


def tup(items: list[str]) -> str:
    if not items:
        return "()"
    return f"({items[0]},)" if len(items) == 1 else f"({', '.join(items)})"


def docstring(text: str, indent: str) -> list[str]:
    text = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    if text.endswith('"'):
        text = text[:-1] + '\\"'
    lines = text.split("\n")
    if len(lines) == 1:
        return [f'{indent}"""{text}"""']
    out = [f'{indent}"""{lines[0]}']
    out += [(indent + line).rstrip() for line in lines[1:]]
    out.append(f'{indent}"""')
    return out


KIND_SENTENCES = {
    "stream": "The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.",
    "session": "Use as a context manager (``with`` / ``async with``); it yields the WebSocket session.",
    "rtsp": "Builds the URL only; no request is made.",
}


def sentence(text: str) -> str:
    return text if text.endswith((".", "!", "?", ":")) else text + "."


def op_doc(op: OpDef) -> str:
    tail = []
    if op.kind in KIND_SENTENCES:
        tail.append(KIND_SENTENCES[op.kind])
    if sentence_for_write := write_sentence(op):
        tail.append(sentence_for_write)
    tail.append(f"Access: {op.access}.")
    tail_text = " ".join(tail)
    summary = sentence(op.summary)
    if not op.description and len(summary) + len(tail_text) < 90:
        return f"{summary} {tail_text}"
    parts = [summary]
    if op.description:
        parts.append("\n".join(textwrap.wrap(op.description, 100)))
    parts.append("\n".join(textwrap.wrap(tail_text, 100)))
    return "\n\n".join(parts)


def shadow_fix(text: str, op_ids: set[str]) -> str:
    """Use ``builtins.list`` where an operation named ``list`` shadows the builtin inside ``OPS``."""
    for name in BUILTIN_SHADOWS:
        if name in op_ids:
            text = re.sub(rf"(?<![\w.\"']){name}(?![\w\"'])", f"builtins.{name}", text)
    return text


def pyname_str(value: Any) -> str:
    return repr(value)


# -- models ----------------------------------------------------------------------


def render_field(f: FieldDef) -> list[str]:
    ann = f.ann
    needs_none = (not f.required and f.default is None) or f.nullable
    if needs_none and not ann.endswith("| None") and ann != "None":
        ann += " | None"
    parts: list[str] = []
    if not f.required:
        parts.append(f"default={f.default if f.default is not None else 'None'}")
    if f.wire != f.py:
        parts += [f"validation_alias={f.wire!r}", f"serialization_alias={f.wire!r}"]
    parts += f.kwargs
    if parts and (len(parts) > 1 or not parts[0].startswith("default=")):
        value = f" = Field({', '.join(parts)})"
    elif parts:
        value = " = " + parts[0][len("default=") :]
    else:
        value = ""
    lines = [f"    {f.py}: {ann}{value}"]
    if f.doc:
        lines += docstring(f.doc, "    ")
    return lines


def render_from_current(td: TypeDef, source: TypeDef) -> list[str]:
    rt = td.round_trip
    assert rt is not None
    param = last_word(source.name)
    exclude = sorted(set(source.masked) | set(source.read_only))
    needs = []
    for f in td.fields:
        if not f.required or f.py in rt.set_values:
            continue
        src = source.by_wire(f.wire)
        if src is not None and src.required and src.py not in exclude:
            continue
        needs.append(f.py)
    exclude_text = f"exclude={{{', '.join(repr(n) for n in exclude)}}}" if exclude else ""
    lines = [
        "",
        "    @classmethod",
        f"    def from_current(cls, {param}: {source.name}) -> {td.name}:",
    ]
    intro = f"A request that rewrites ``{param}`` unchanged: copy it, edit fields, send it back."
    if rt.set_values:
        names = ", ".join(f"``{k}``" for k in rt.set_values)
        note = f"Masked and read-only fields are dropped and {names} is set, so stored secrets survive the round trip."
        intro += "\n\n" + "\n".join(textwrap.wrap(note, 100))
    lines += docstring(intro, "        ")
    lines.append(f"        data = {param}.request_data({exclude_text})")
    if needs:
        names = ", ".join(repr(n) for n in needs)
        lines += [
            f"        missing = [name for name in ({names},) if name not in data]",
            "        if missing:",
            "            raise ValueError(f\"the current value has no {', '.join(missing)} to keep\")",
        ]
    clash = [k for k in rt.set_values if source.by_py(k) is not None]
    if rt.set_values and clash:
        for k, v in rt.set_values.items():
            lines.append(f"        data[{k!r}] = {v!r}")
        lines.append("        return cls(**data)")
    elif rt.set_values:
        lines.append(f"        return cls(**data, {', '.join(f'{k}={v!r}' for k, v in rt.set_values.items())})")
    else:
        lines.append("        return cls(**data)")
    return lines


def render_type(td: TypeDef, types: dict[str, TypeDef]) -> list[str]:
    if td.kind == "alias":
        return [f"{td.name} = {td.alias_expr}"]
    lines = ["", "", f"class {td.name}(Model):"]
    body: list[str] = []
    if td.doc:
        body += docstring(td.doc, "    ")
    if td.nullable:
        names = ", ".join(repr(n) for n in td.nullable)
        body.append(f"    __nullable__: ClassVar[frozenset[str]] = frozenset({{{names}}})")
    for f in td.fields:
        body += render_field(f)
    if td.round_trip:
        body += render_from_current(td, types[td.round_trip.from_name])
    if not body:
        body = ["    pass"]
    return lines + body + [""]


# -- descriptors -----------------------------------------------------------------


def errors_code(errors: dict[Any, dict[str, Any]]) -> str:
    items = []
    for code, entry in errors.items():
        kind = f", {entry['kind']!r}" if entry.get("kind") else ""
        items.append(f"{code!r}: ErrorCode({entry['description']!r}{kind})")
    return "{" + ", ".join(items) + "}"


def discovery_code(api: ApiDef) -> str:
    items = []
    for kind, value in api.discovery:
        if kind == "api_discovery":
            items.append(f"ApiDiscovery({value!r})")
        elif kind == "dca":
            items.append(f"DcaDiscovery({value['api']!r}, {value['version']!r})")
        elif kind == "param":
            extra = f", {str(value['value'])!r}" if value.get("value") is not None else ""
            compare = value.get("compare", "==")
            if compare != "==":
                if value.get("value") is None:
                    raise SpecError(f"param discovery {value['name']!r}: compare {compare!r} needs a value")
                extra += f", {compare!r}"
            items.append(f"ParamDiscovery({value['name']!r}{extra})")
        elif kind == "acap":
            items.append(f"AcapDiscovery({value['name']!r})")
        elif kind == "service":
            items.append(f"ServiceDiscovery({value['namespace']!r})")
        else:
            raise SpecError(f"unknown discovery kind {kind!r}")
    return tup(items)


def common_binding_args(op_binding: dict[str, Any], api_binding: dict[str, Any]) -> list[str]:
    out = []
    auth = op_binding.get("auth", api_binding.get("auth"))
    timeout = op_binding.get("timeout", api_binding.get("timeout"))
    if auth and auth != "required":
        out.append(f"auth={auth!r}")
    if timeout is not None:
        out.append(f"timeout={timeout!r}")
    return out


def negotiation_code(binding: dict[str, Any]) -> str | None:
    if "negotiation" not in binding:
        return None
    neg = binding["negotiation"]
    if neg in (None, "none"):
        return "NoVersion()"
    if "fixed" in neg:
        major, minor = str(neg["fixed"]).split(".")
        return f"FixedVersion(ApiVersion({int(major)}, {int(minor)}))"
    opts = neg.get("get_supported_versions") or {}
    args = []
    if opts.get("key", "apiVersions") != "apiVersions":
        args.append(f"key={opts['key']!r}")
    if opts.get("auth"):
        args.append(f"auth={opts['auth']!r}")
    return f"GetSupportedVersions({', '.join(args)})" if args else None


SOAP_PATH = "/vapix/services"


def soap_path(binding: dict[str, Any]) -> str:
    return binding.get("path", SOAP_PATH)


def rtsp_binding_code(op: OpDef) -> str:
    assert op.rtsp is not None
    args = []
    if op.rtsp.get("path", MEDIA_PATH) != MEDIA_PATH:
        args.append(f"path={op.rtsp['path']!r}")
    if op.rtsp.get("port", RTSP_PORT) != RTSP_PORT:
        args.append(f"port={op.rtsp['port']!r}")
    query = op.rtsp.get("query") or {}
    if query:
        args.append(f"fixed_query={tup([f'({k!r}, {_query_value(v)!r})' for k, v in query.items()])}")
    return f"RtspBinding({', '.join(args)})"


def session_code(op: OpDef) -> str:
    assert op.session is not None
    s = op.session
    args = ["INFO.id", repr(s["path"])]
    query = s.get("query") or {}
    if query:
        args.append(f"query={tup([f'({k!r}, {_query_value(v)!r})' for k, v in query.items()])}")
    codec = s.get("codec", "raw")
    if codec != "raw":
        args.append(f"codec={SESSION_CODEC_CLASSES[codec]}")
    setup = session_setup(op)
    if setup != "none":
        args.append(f"setup={SESSION_SETUP_FUNCTIONS[setup]}")
    return f"SessionSpec({', '.join(args)})"


MEDIA_PATH = "/axis-media/media.amp"
RTSP_PORT = 554
SESSION_CODEC_CLASSES = {"events": "EventsCodec()", "datahub": "DataHubCodec()"}
SESSION_SETUP_FUNCTIONS = {"events": "events_setup", "datahub": "datahub_setup"}


def binding_code(api: ApiDef, op: OpDef) -> str:
    ob, ab = op.binding, api.binding
    if op.kind == "rtsp":
        return rtsp_binding_code(op)
    extra = common_binding_args(ob, ab)
    if api.family == "jsonrpc":
        if "method" not in ob:
            raise SpecError(f"{op.id}: jsonrpc operations need binding.method")
        path = repr(ob["path"]) if "path" in ob else "PATH"
        args = [repr(ob["method"]), path]
        neg = negotiation_code(ab)
        if neg:
            args.append(f"negotiation={neg}")
        if op.params_field:
            args.append(f"params_field={op.params_field!r}")
        placement = ob.get("params_placement", ab.get("params_placement"))
        if placement and placement != "params":
            args.append(f"params_placement={placement!r}")
        multipart = ob.get("multipart")
        if multipart is not None:
            parts = [f"json_part={multipart['json_part']!r}"] if multipart.get("json_part") else []
            parts.append(f"uploads={tup(upload_specs(op))}")
            args.append(f"multipart=JsonRpcMultipart({', '.join(parts)})")
        return f"JsonRpcBinding({', '.join(args + extra)})"
    if api.family == "service_json":
        args = [repr(ob["path"]) if "path" in ob else "PATH", repr(ob["operation"])]
        return f"ServiceJsonBinding({', '.join(args + extra)})"
    if api.family == "soap":
        namespace = ob.get("namespace") or ab["namespace"]
        args = [repr(ob["action"]), repr(ob["element"]), repr(namespace)]
        if op.reply_map:
            args.append(f"reply={op.reply_map}")
        if soap_path(ob) != SOAP_PATH:
            args.append("path=PATH" if "path" not in ob else f"path={ob['path']!r}")
        namespaces = {**(ab.get("namespaces") or {}), **(ob.get("namespaces") or {})}
        if namespaces:
            extra = extra + [f"namespaces={tup([f'({p!r}, {uri!r})' for p, uri in namespaces.items()])}"]
        return f"SoapBinding({', '.join(args + extra)})"
    if api.family in ("dca", "rest"):
        method = ob.get("method")
        if not method:
            raise SpecError(f"{op.id}: {api.family} operations need binding.method")
        path = ob.get("path", "")
        if path and not path.startswith("/"):
            raise SpecError(f"{op.id}: {api.family} binding.path must start with '/'")
        if path:
            escaped = path.replace("{", "{{").replace("}", "}}").replace('"', '\\"')
            path_code = f'f"{{ROOT}}{escaped}"'
        else:
            path_code = "ROOT"
        args = [repr(method), path_code]
        body = ob.get("body", "none")
        if body != "none":
            args.append(f"body={body!r}")
        if ob.get("body_field"):
            args.append(f"body_field={ob['body_field']!r}")
        if api.family == "rest":
            query = [(op.params.by_py(n) or op.params.by_wire(n)) if op.params else None for n in ob.get("query") or []]
            if query:
                args.append(f"query={tup([f'({f.py!r}, {f.wire!r})' for f in query if f])}")
            return f"RestBinding({', '.join(args + extra)})"
        styles = ob.get("key_styles") or {}
        if styles:
            args.append(f"key_styles={tup([f'({k!r}, {v!r})' for k, v in styles.items()])}")
        return f"DcaBinding({', '.join(args + extra)})"
    # cgi
    args = ["PATH" if "path" not in ob else repr(ob["path"])]
    if ob.get("method", "GET") != "GET":
        args.append(f"method={ob['method']!r}")
    if ob.get("encoding", "query") != "query":
        args.append(f"encoding={ob['encoding']!r}")
    for key, name in (("query", "fixed_query"), ("url_query", "url_query")):
        fixed = ob.get(key) or {}
        if fixed:
            args.append(f"{name}={tup([f'({k!r}, {_query_value(v)!r})' for k, v in fixed.items()])}")
    if ob.get("content_type"):
        args.append(f"content_type={ob['content_type']!r}")
    if op.params is not None:
        cgi_args = []
        for f in op.args:
            if f.py in op.key_fields or f.upload is not None or f.place == "body":
                continue
            style = f.style or ("csv" if f.sig.startswith("list[") else "spread" if f.is_mapping else None)
            parts = [repr(f.py)]
            if f.wire != f.py:
                parts.append(f"wire={f.wire!r}")
            if style and style != "plain":
                parts.append(f"style={style!r}")
            if f.place in ("query", "form"):
                parts.append(f"place={f.place!r}")
            cgi_args.append(f"CgiArg({', '.join(parts)})")
        if cgi_args:
            args.append(f"args={tup(cgi_args)}")
        body = [f for f in op.args if f.place == "body"]
        if body:
            args.append(f"body_field={body[0].py!r}")
        uploads = upload_specs(op)
        if uploads:
            args.append(f"uploads={tup(uploads)}")
    reply = reply_code(ob, op)
    if reply:
        args.append(f"reply={reply}")
    if ob.get("accept"):
        args.append(f"accept={ob['accept']!r}")
    if ob.get("stream") or op.kind == "stream":
        args.append("stream=True")
    return f"CgiBinding({', '.join(args + extra)})"


def _query_value(v: Any) -> str | None:
    """Fixed argument value as text; ``None`` is a bare key."""
    if v is None:
        return None
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def upload_specs(op: OpDef) -> list[str]:
    """``UploadSpec(...)`` sources for the operation's ``x-upload`` arguments."""
    out = []
    for f in op.args:
        if f.upload is None:
            continue
        parts = [repr(f.py)]
        for key in ("part", "filename", "content_type"):
            if f.upload.get(key):
                parts.append(f"{key}={f.upload[key]!r}")
        out.append(f"UploadSpec({', '.join(parts)})")
    return out


def reply_code(ob: dict[str, Any], op: OpDef) -> str | None:
    if "reply" not in ob:
        return None
    kind, opts = reply_kind(ob)
    if kind == "text_ok":
        return "TextOk()"
    if kind == "text":
        return "Text()"
    if kind == "json":
        return "JsonReply()"
    if kind == "stream":
        decoder = opts.get("decoder", "bytes")
        args = [repr(decoder)] if decoder != "bytes" else []
        if opts.get("encoding"):
            args.append(f"encoding={opts['encoding']!r}")
        return f"Stream({', '.join(args)})"
    if kind == "text_lines":
        return f"TextLines(skip={opts['skip']})" if opts.get("skip") else "TextLines()"
    if kind == "text_kv":
        prefix = opts.get("strip_prefix")
        return f"TextKv(strip_prefix={prefix!r})" if prefix else "TextKv()"
    if kind == "xml":
        args = []
        if opts.get("error_elements") is not None:
            args.append(f"error_elements={tup([repr(e) for e in opts['error_elements']])}")
        if op.reply_map:
            args.append(f"map={op.reply_map}")
        status = opts.get("status_error")
        if status:
            args.append(f"status_error=XmlStatusError({', '.join(f'{k}={v!r}' for k, v in status.items())})")
        return f"Xml({', '.join(args)})"
    if kind == "binary":
        args = []
        if opts.get("media_types"):
            args.append(f"media_types={tup([repr(m) for m in opts['media_types']])}")
        if opts.get("signatures"):
            args.append(f"signatures={tup([repr(bytes.fromhex(s)) for s in opts['signatures']])}")
        return f"Binary({', '.join(args)})"
    raise SpecError(f"{op.id}: unknown reply codec {kind!r}")


def render_ops(api: ApiDef) -> list[str]:
    ids = {op.id for op in api.ops}
    lines = ["class OPS:"]
    calls = [op for op in api.ops if op.kind != "session"]
    if not calls:
        lines.append("    pass")
    for op in calls:
        args = [f"INFO, {op.id!r}", binding_code(api, op)]
        if op.params:
            args.append(f"params={op.params.name}")
        if op.result:
            args.append(f"result={shadow_fix(op.result, ids)}")
        args += [f"access={op.access!r}", f"effect={op.effect!r}"]
        if op.since:
            args.append(f"since=ApiVersion({op.since[0]}, {op.since[1]})")
        if op.write:
            args.append(f"write={op.write!r}")
        if op.applicability:
            items = []
            for a in op.applicability:
                value = f", {a.value!r}" if a.value is not None else ""
                items.append(f"Applicability({a.path!r}, ApiVersion({a.since[0]}, {a.since[1]}){value})")
            args.append(f"applicability={tup(items)}")
        if op.errors:
            args.append(f"errors={errors_code(op.errors)}")
        if op.support != "docs-only":
            args.append(f"support={op.support!r}")
        lines.append(f"    {op.id} = Operation({', '.join(args)})")
    sessions = [op for op in api.ops if op.kind == "session"]
    if sessions:
        lines += ["", "", "class SESSIONS:"]
        lines += [f"    {op.id} = {session_code(op)}" for op in sessions]
    return lines


def info_code(api: ApiDef) -> list[str]:
    b = api.binding
    args = [
        f"id={api.id!r}",
        f"name={api.name!r}",
        f"family=Family.{api.family.upper()}",
    ]
    if api.family == "jsonrpc":
        if "major" not in b:
            raise SpecError("jsonrpc binding needs `major`")
        args.append(f"major={b['major']}")
        versions = []
        for v in b.get("versions") or []:
            major, minor = str(v).split(".")
            versions.append(f"ApiVersion({int(major)}, {int(minor)})")
        if versions:
            args.append(f"known_versions={tup(versions)}")
    if api.discovery:
        args.append(f"discovery={discovery_code(api)}")
    if api.docs:
        args.append(f"docs={tup([repr(d) for d in api.docs])}")
    if api.errors:
        args.append(f"errors={errors_code(api.errors)}")
    return [f"INFO = ApiInfo({', '.join(args)})"]


# -- API classes -----------------------------------------------------------------


def class_doc(api: ApiDef) -> str:
    extra = ""
    if api.family == "jsonrpc":
        extra = f", version {api.binding.get('major')}"
    elif api.family == "dca":
        for kind, value in api.discovery:
            if kind == "dca":
                extra = f", {value['version']}"
                break
    return f"{api.name} (``{api.id}``{extra})."


def _value(f: FieldDef) -> str:
    if not f.is_mapping:
        return f.py
    return f"None if {f.py} is None else dict({f.py})" if f.nullable else f"dict({f.py})"


def render_special_call(op: OpDef) -> list[str]:
    """Body of a session or rtsp method (neither does I/O in the method itself)."""
    if op.kind == "session":
        options = [name for name, _ in SESSION_SETUPS[session_setup(op)]]
        spec = f"SESSIONS.{op.id}"
        if op.args:
            spec += f".bind({{{', '.join(f'{f.wire!r}: {f.py}' for f in op.args)}}})"
        args = [spec, "request_options=request_options", "heartbeat=heartbeat", "use_token=use_token"]
        args += [f"{name}={name}" for name in options]
        return [f"        return self._device.connect_session({', '.join(args)})"]
    items = ", ".join(f'"{f.py}": {_value(f)}' for f in op.args)
    return [f"        return self._device.rtsp_url_for(OPS.{op.id}, {{{items}}}, port=port, include_credentials=include_credentials)"]


def render_call(op: OpDef, is_async: bool) -> list[str]:
    prefix = ("return " if op.result or op.kind == "stream" else "") + ("await " if is_async else "")
    if op.params is None:
        return [f"        {prefix}self._run(OPS.{op.id}, None, {{}}, request_options)"]
    if op.overloaded:
        lines: list[str] = []
        if op.positional:
            names = tup([repr(n) for n in op.positional])
            lines += [
                "        if request is MISSING:",
                "            request = None",
                f"        elif args or not isinstance(request, {op.params.name}):",
                f"            kwargs = {{**dict(zip({names}, (request, *args), strict=False)), **kwargs}}",
                "            request = None",
            ]
        return lines + [f"        {prefix}self._run(OPS.{op.id}, request, kwargs, request_options)"]
    fields = op.args
    optional_maps = [f for f in fields if f.is_mapping and not f.required]
    items = []
    for f in fields:
        if f in optional_maps:
            continue
        items.append(f'"{f.py}": {_value(f)}')
    if not optional_maps:
        return [f"        {prefix}self._run(OPS.{op.id}, None, {{{', '.join(items)}}}, request_options)"]
    lines = [f"        args: dict[str, Any] = {{{', '.join(items)}}}"]
    for f in optional_maps:
        lines += [f"        if {f.py} is not MISSING:", f'            args["{f.py}"] = {_value(f)}']
    lines.append(f"        {prefix}self._run(OPS.{op.id}, None, args, request_options)")
    return lines


def render_method(op: OpDef, is_async: bool) -> list[str]:
    # Sessions and RTSP URLs need no await: the async API returns the (async) context manager or the URL directly.
    kw = "async def" if is_async and op.kind not in ("session", "rtsp") else "def"
    overloads, impl = signatures(op, is_async)
    lines: list[str] = []

    def header(sig: Signature) -> str:
        return f"    {kw} {op.id}(self, {', '.join(sig.args)}) -> {sig.returns}"

    for sig in overloads if impl else []:
        lines += ["    @overload", header(sig) + ": ..."]
    main = impl or overloads[0]
    lines.append(header(main) + ":")
    lines += docstring(op_doc(op), "        ")
    lines += render_special_call(op) if op.kind in ("session", "rtsp") else render_call(op, is_async)
    lines.append("")
    return lines


def render_class(api: ApiDef, is_async: bool) -> list[str]:
    name = ("Async" if is_async else "") + api.class_name + "Api"
    lines = ["", f"class {name}({'AsyncApi' if is_async else 'SyncApi'}):"]
    lines += docstring(class_doc(api), "    ")
    lines += ["", "    INFO = INFO", ""]
    for op in api.ops:
        lines += render_method(op, is_async)
    return lines


# -- module ----------------------------------------------------------------------

IMPORTS = """\
from __future__ import annotations

import builtins
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._http.upload import UploadSource, UploadSpec
from .._protocols.base import AcapDiscovery, ApiDiscovery, ApiInfo, ApiVersion, Applicability, DcaDiscovery, ErrorCode, Family, Model, Operation, ParamDiscovery, ServiceDiscovery
from .._protocols.cgi import Binary, CgiArg, CgiBinding, JsonReply, Text, TextKv, TextLines, TextOk, Xml
from .._protocols.dca import DcaBinding
from .._protocols.rest import RestBinding
from .._protocols.service_json import ServiceJsonBinding
from .._protocols.soap import SoapBinding
from .._protocols.jsonrpc import FixedVersion, GetSupportedVersions, JsonRpcBinding, JsonRpcMultipart, NoVersion
from .._protocols.xmlmap import XmlField, XmlMap, XmlStatusError
from ._base import AsyncApi, SyncApi
"""

# Imported only by modules that use the feature, so type names cannot collide with them elsewhere (see build.FEATURE_RESERVED).
FEATURE_IMPORTS = {
    "stream": [
        "from .._protocols.cgi import Stream",
        "from .._runtime.driver import AsyncStreamResult, StreamResult",
        "from .._streams import Part",
    ],
    "session": [
        "from collections.abc import Sequence",
        "from contextlib import AbstractAsyncContextManager, AbstractContextManager",
        "from .._http.options import DEFAULT_HEARTBEAT, Heartbeat",
        "from .._runtime.ws import AsyncSession, Session, SessionSpec",
    ],
    "events": ["from .._runtime.ws_codecs import EventFilter, EventsCodec, events_setup"],
    "datahub": ["from .._runtime.ws_codecs import DataHubCodec, datahub_setup"],
    "rtsp": ["from ..rtsp import RtspBinding, RtspUrl"],
}


def api_features(api: ApiDef) -> set[str]:
    out: set[str] = set()
    for op in api.ops:
        if op.kind in ("stream", "rtsp"):
            out.add(op.kind)
        elif op.kind == "session":
            assert op.session is not None
            out.add("session")
            if op.session.get("codec") == "events" or session_setup(op) == "events":
                out.add("events")
            if op.session.get("codec") == "datahub" or session_setup(op) == "datahub":
                out.add("datahub")
    return out


def render_module(api: ApiDef) -> str:
    types = {t.name: t for t in api.types}
    out = [f"# GENERATED from {api.source}. Do not edit.", "# Regenerate with `uv run python -m codegen generate`."]
    summary = api.summary.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    out += [f'"""{summary}', ""]
    out += [f"Docs: {d}" for d in api.docs[:1]]
    out += ['"""', ""]
    out.append(IMPORTS + "".join(line + "\n" for f in sorted(api_features(api)) for line in FEATURE_IMPORTS[f]))
    out += ["# " + "-" * 75, "# Models", ""]
    for td in api.types:
        out += render_type(td, types)
    out += ["", "# " + "-" * 75, "# Descriptors", ""]
    if api.family in ("dca", "rest"):
        root = api.binding.get("root")
        if not root:
            raise SpecError(f"{api.family} binding needs `root`")
        out.append(f"ROOT = {root!r}")
    elif api.family == "soap":
        out.append(f"PATH = {soap_path(api.binding)!r}")
    elif api.family in ("ws", "rtsp") and "path" not in api.binding:
        out.append("# No shared path: every operation names its own endpoint.")
    else:
        if "path" not in api.binding:
            raise SpecError("binding.path is required")
        out.append(f"PATH = {api.binding['path']!r}")
    out.append("")
    out += info_code(api)
    out.append("")
    out += render_ops(api)
    out += ["", "", "# " + "-" * 75, "# API classes"]
    out += render_class(api, False)
    out += render_class(api, True)
    return "\n".join(out) + "\n"
