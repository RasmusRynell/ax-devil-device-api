#!/usr/bin/env python3
"""Migrate the v1 VAPIX spec corpus to the v2 spec format.

Usage: uv run python codegen/migrate_v1.py [--src DIR] [--out DIR] [--only ID ...]

Scope: JSON-RPC CGI (styles[0] == json_rpc_cgi), Device Configuration REST
(device_config_rest in styles) and classic CGI (styles[0] in cgi_query, cgi_xml,
cgi_form_post). Other families are skipped. The v1 corpus is
treated as data only (yaml.safe_load). Hand-curated v2 specs are never
overwritten.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import keyword
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

DEFAULT_SRC = Path("/home/sumss/Downloads/vapix_spec/vapix/spec/apis")
REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "specs" / "apis"

CURATED = {
    ("network-video", "mqtt-client"),
    ("device-configuration", "analytics-mqtt-config"),
    ("network-video", "parameter-management"),
}
CURATED_MODULES = {"mqtt_client", "analytics_mqtt", "parameter_management"}

ACCESS_LEVELS = {"anonymous", "viewer", "operator", "admin"}
SCHEMA_KEYS_SCALAR = {
    "minimum", "maximum", "minLength", "maxLength", "pattern", "default", "const", "description",
}
KEEP_EXT = {"x-nullable", "x-masked", "x-read-only", "x-python-name", "x-name", "x-style"}

# --------------------------------------------------------------------------- helpers

try:  # reuse the generator's own naming rules when available
    sys.path.insert(0, str(REPO))
    from codegen.build import RESERVED_MODULE_NAMES as _RESERVED_TYPES  # type: ignore
    from codegen.naming import NamingError as _NamingError, field_name as _field_name  # type: ignore
except Exception:  # noqa: BLE001
    _RESERVED_TYPES = frozenset()
    _NamingError = None
    _field_name = None


class Notes:
    """Collects migration notes as (kind, detail)."""

    def __init__(self):
        self.items: list[tuple[str, str]] = []
        self.dropped = collections.Counter()

    def add(self, kind, detail):
        t = (kind, detail)
        if t not in self.items:
            self.items.append(t)

    def render(self):
        out = [f"migration: {k}: {d}" for k, d in self.items]
        if self.dropped:
            kws = ", ".join(f"{k} x{n}" for k, n in sorted(self.dropped.items()))
            out.append(f"migration: dropped-keywords: {kws}")
        return out


def snake(name: str) -> str:
    s = re.sub(r"[^0-9A-Za-z]+", "_", name)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    return re.sub(r"_+", "_", s).strip("_").lower()


def pascal(name: str) -> str:
    parts = [p for p in re.split(r"[^0-9A-Za-z]+", name) if p]
    out = "".join(p[0].upper() + p[1:] for p in parts)
    if not out:
        out = "T"
    if out[0].isdigit():
        out = "T" + out
    return out


def singular(word: str) -> str:
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith(("ss", "us", "is")):
        return word
    if word.endswith("s") and len(word) > 1:
        return word[:-1]
    return word


def singular_snake(seg: str) -> str:
    s = snake(seg)
    head, sep, tail = s.rpartition("_")
    return head + sep + singular(tail)


def trim(desc, limit=220):
    if not isinstance(desc, str):
        return desc
    d = re.sub(r"\s+", " ", desc).strip()
    d = re.sub(r"\s*\(optional\)", "", d)
    d = re.sub(r"\s+([.,;])", r"\1", d)
    if len(d) <= limit:
        return d
    m = re.search(r"[.!?](\s|$)", d)
    if m and m.end() <= limit + 40:
        return d[: m.start() + 1]
    cut = d[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "..."


def short_summary(s, limit=160):
    if not isinstance(s, str):
        return s
    d = re.sub(r"\s+", " ", s).strip()
    m = re.search(r"[.!?](\s|$)", d)
    if m and m.end() <= limit:
        d = d[: m.start() + 1] if m.start() + 1 < len(d) else d
    if len(d) > limit:
        d = d[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return d


def parse_version(v):
    m = re.match(r"^\s*v?(\d+)(?:\.(\d+))?", str(v))
    if not m:
        return None
    return int(m.group(1)), int(m.group(2) or 0)


def vstr(t):
    return f"{t[0]}.{t[1]}"


def error_kind(desc: str):
    d = (desc or "").lower()
    rules = [
        ("access_denied", ("authoriz", "permission", "access")),
        ("unavailable", ("busy", "unavailable", "try again")),
        ("unsupported", ("not supported", "unsupported", "version")),
        ("not_found", ("not found", "does not exist")),
        ("invalid_argument", ("invalid", "missing", "required", "parameter", "format", "too large")),
        ("internal", ("internal", "unexpected")),
    ]
    for kind, words in rules:
        if any(w in d for w in words):
            return kind
    return None


def convert_errors(errs, notes, scope=None, skip=None):
    out = {}
    for e in errs or []:
        if scope and e.get("scope") != scope:
            continue
        code = e.get("code")
        if code is None:
            continue
        name, desc = e.get("name"), e.get("description")
        if name and desc and name != desc:
            text = f"{name.rstrip('.')}. {desc}"
        else:
            text = name or desc or ""
        text = trim(text, 200)
        entry = {"description": text}
        k = error_kind(text)
        if k:
            entry["kind"] = k
        if skip is not None and code in skip and skip[code].get("description") == text:
            continue
        out[code] = entry
    return out


# --------------------------------------------------------------------------- schema conversion


class Ctx:
    def __init__(self, notes, typemap, v1types):
        self.notes = notes
        self.typemap = typemap
        self.v1types = v1types


def map_ref(ref, ctx):
    m = re.match(r"^#/types/([^/]+)$", ref)
    if m:
        return "#/types/" + ctx.typemap.get(m.group(1), pascal(m.group(1)))
    ctx.notes.add("odd-ref", f"unsupported $ref {ref}")
    return None


def is_nullable(s):
    if not isinstance(s, dict):
        return False
    if s.get("nullable") is True or s.get("x-nullable") is True:
        return True
    if isinstance(s.get("type"), list) and "null" in s["type"]:
        return True
    for k in ("anyOf", "oneOf"):
        if any(isinstance(x, dict) and x.get("type") == "null" for x in s.get(k) or []):
            return True
    return False


def conv(s, ctx):
    """Convert a v1 JSON-schema-ish dict to the v2 subset."""
    if not isinstance(s, dict):
        return {}
    s = dict(s)
    for k in ("anyOf", "oneOf"):
        if isinstance(s.get(k), list) and any(isinstance(x, dict) and x.get("type") == "null" for x in s[k]):
            rest = [x for x in s[k] if not (isinstance(x, dict) and x.get("type") == "null")]
            s.pop(k)
            if len(rest) == 1:
                outer = {kk: vv for kk, vv in s.items()}
                s = dict(rest[0])
                s.update(outer)
            elif rest:
                s[k] = rest
    out = {}
    nullable = []

    if "x-unresolved-type" in s:
        name = s.pop("x-unresolved-type")
        if name in ctx.v1types:
            s["$ref"] = "#/types/" + name
        else:
            ctx.notes.add("unresolved-type", f"type {name} is not defined in the source")
    if "allOf" in s:
        parts = s.pop("allOf") or []
        merged = {}
        refs = [p for p in parts if isinstance(p, dict) and "$ref" in p]
        if len(parts) == 1:
            merged = dict(parts[0])
        elif len(refs) == len(parts):
            merged = dict(parts[0])
            ctx.notes.add("allof", "allOf with several $refs reduced to the first")
        else:
            props, req = {}, []
            for p in parts:
                if "$ref" in p:
                    ctx.notes.add("allof", "allOf mixing $ref and inline parts: $ref ignored")
                    continue
                props.update(p.get("properties", {}))
                req += [r for r in p.get("required", []) if isinstance(r, str)]
                for k, v in p.items():
                    if k not in ("properties", "required"):
                        merged.setdefault(k, v)
            if props:
                merged["properties"] = props
            if req:
                merged["required"] = req
        for k, v in s.items():
            merged[k] = v  # outer keys (description) win
        s = merged
    if "anyOf" in s:
        s["oneOf"] = s.pop("anyOf")
        ctx.notes.add("anyof", "anyOf converted to oneOf")

    desc = s.get("description")
    t = s.get("type")
    if isinstance(t, list):
        non_null = [x for x in t if x != "null"]
        if "null" in t:
            nullable_self = True
        t = non_null[0] if non_null else None
        if len(non_null) > 1:
            ctx.notes.add("multi-type", f"type list {non_null} reduced to {t}")
        s["type"] = t
    if t in ("any", None):
        s.pop("type", None)
        t = None
    elif t == "enum":
        vals = s.get("enum") or []
        s["type"] = "integer" if vals and all(isinstance(v, int) and not isinstance(v, bool) for v in vals) else "string"
        t = s["type"]
    elif t == "binary":
        s["type"] = "string"
        s["format"] = "binary"
        t = "string"

    if "$ref" in s:
        r = map_ref(s["$ref"], ctx)
        if r:
            out["$ref"] = r
    elif "type" in s:
        out["type"] = s["type"]
    if "enum" in s and "$ref" not in out:
        out["enum"] = s["enum"] if isinstance(s["enum"], list) else [s["enum"]]
    if "const" in s:
        out["const"] = s["const"]
    if "items" in s:
        if isinstance(s["items"], dict):
            out["items"] = conv(s["items"], ctx)
        elif isinstance(s["items"], list) and s["items"]:
            out["items"] = conv(s["items"][0], ctx)
    if "oneOf" in s and isinstance(s["oneOf"], list):
        out["oneOf"] = [conv(x, ctx) for x in s["oneOf"]]
    for k in ("minimum", "maximum", "minLength", "maxLength", "pattern", "default"):
        if k in s and "$ref" not in out:
            out[k] = s[k]
    if "default" in s and "$ref" in out:
        out["default"] = s["default"]
    if "additionalProperties" in s:
        ap = s["additionalProperties"]
        out["additionalProperties"] = conv(ap, ctx) if isinstance(ap, dict) else ap
    if isinstance(s.get("properties"), dict):
        props = {}
        for pname, psub in s["properties"].items():
            if not isinstance(psub, dict):
                psub = {}
            if is_nullable(psub):
                nullable.append(pname)
            props[pname] = conv(psub, ctx)
        out["properties"] = props
        if "type" not in out and "$ref" not in out:
            out["type"] = "object"
        req = s.get("required")
        if isinstance(req, list):
            req = [r for r in req if r in props]
            if req:
                out["required"] = req
    for k in ("x-masked", "x-read-only", "x-python-name", "x-name", "x-style"):
        if k in s:
            out[k] = s[k]
    if isinstance(s.get("x-nullable"), list):
        nullable += [n for n in s["x-nullable"] if n not in nullable]
    if nullable:
        out["x-nullable"] = nullable

    extra = []
    for k in ("minItems", "maxItems"):
        if k in s:
            extra.append(f"{k}={s[k]}")
    if s.get("format") and s["format"] != "binary":
        extra.append(f"format={s['format']}")
    if s.get("format") == "binary":
        out["format"] = "binary"
    if desc:
        d = trim(desc)
        if extra:
            d += f" ({', '.join(extra)})"
        out["description"] = d
    elif extra:
        out["description"] = ", ".join(extra)

    known = {
        "type", "enum", "const", "items", "oneOf", "minimum", "maximum", "minLength", "maxLength",
        "pattern", "default", "additionalProperties", "properties", "required", "description", "$ref",
        "nullable", "format", "minItems", "maxItems", "x-nullable", "x-gettable", "x-unresolved-type",
        "allOf", "anyOf", *KEEP_EXT,
    }
    for k in s:
        if k not in known:
            ctx.notes.dropped[k] += 1
    if "nullable" in s and s["nullable"] is True and not nullable:
        pass  # handled by the parent object
    return order_schema(out)


ORDER_OBJ = ["type", "x-name", "description", "required", "x-nullable", "x-masked", "x-read-only", "properties"]
ORDER_OTHER = [
    "$ref", "type", "x-name", "format", "enum", "const", "items", "oneOf", "minimum", "maximum",
    "minLength", "maxLength", "pattern", "default", "additionalProperties", "x-nullable", "x-python-name",
    "x-style", "description",
]


def order_schema(s):
    order = ORDER_OBJ if "properties" in s else ORDER_OTHER
    out = {k: s[k] for k in order if k in s}
    for k in s:
        if k not in out:
            out[k] = s[k]
    return out


def leaf_schema(p, ctx):
    """Schema for one flattened v1 param."""
    s = {}
    if isinstance(p.get("schema"), dict):
        s = conv(p["schema"], ctx)
    t = p.get("type")
    if "$ref" not in s and "oneOf" not in s and "type" not in s:
        if t in ("string", "integer", "number", "boolean", "array", "object"):
            s["type"] = t
        elif t == "enum":
            vals = p.get("enum") or []
            s["type"] = "integer" if vals and all(isinstance(v, int) for v in vals) else "string"
        elif t == "binary":
            s["type"] = "string"
            s["format"] = "binary"
    if p.get("enum") and "$ref" not in s:
        s["enum"] = p["enum"]
    if p.get("items") and s.get("type") == "array" and "items" not in s:
        it = p["items"]
        s["items"] = conv(it, ctx) if isinstance(it, dict) else {}
    c = p.get("constraints") or {}
    for src, dst in (("minimum", "minimum"), ("maximum", "maximum"), ("min_length", "minLength"),
                     ("max_length", "maxLength"), ("pattern", "pattern")):
        if src in c and "$ref" not in s:
            s[dst] = c[src]
    extra = []
    if "min_items" in c:
        extra.append(f"minItems={c['min_items']}")
    if "max_items" in c:
        extra.append(f"maxItems={c['max_items']}")
    if c.get("unit"):
        extra.append(f"unit={c['unit']}")
    if "default" in p and p["default"] is not None:
        s["default"] = p["default"]
    d = p.get("description") or s.get("description")
    if d:
        d = trim(d)
        ed = p.get("enum_descriptions")
        if isinstance(ed, dict) and ed:
            bits = [f"{k}: {trim(v, 80).rstrip('.')}" for k, v in ed.items()]
            d = (d + " Values: " + "; ".join(bits))
            d = trim(d, 500)
        if extra:
            d += f" ({', '.join(extra)})"
        s["description"] = d
    elif extra:
        s["description"] = ", ".join(extra)
    if p.get("nullable") is True or is_nullable(p.get("schema")):
        s["_nullable"] = True
    return order_schema(s)


def flowify_marker(obj):
    return obj


class Flow(dict):
    pass


class FlowList(list):
    pass


def flowify(obj, depth=0):
    """Mark small leaf mappings as flow style for compact, diff-friendly YAML."""
    if isinstance(obj, dict):
        new = {k: flowify(v, depth + 1) for k, v in obj.items()}
        scalar = all(
            (not isinstance(v, (dict, list))) or (isinstance(v, FlowList)) for v in new.values()
        )
        if scalar and new:
            try:
                size = len(json.dumps(obj, default=str))
            except TypeError:
                size = 999
            if size <= 100 and not any(isinstance(v, str) and "\n" in v for v in new.values()):
                return Flow(new)
        return new
    if isinstance(obj, list):
        items = [flowify(v, depth + 1) for v in obj]
        if items and all(not isinstance(v, (dict, list)) for v in items):
            try:
                size = len(json.dumps(obj, default=str))
            except TypeError:
                size = 999
            if size <= 80:
                return FlowList(items)
        return items
    return obj


class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def _repr_flow(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", dict(data), flow_style=True)


def _repr_flowlist(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", list(data), flow_style=True)


def _repr_dict(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


def _repr_str(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


Dumper.add_representer(Flow, _repr_flow)
Dumper.add_representer(FlowList, _repr_flowlist)
Dumper.add_representer(dict, _repr_dict)
Dumper.add_representer(str, _repr_str)


def dump_yaml(doc):
    # blank line between top-level sections for readability
    chunks = []
    for key, val in doc.items():
        text = yaml.dump({key: val}, Dumper=Dumper, sort_keys=False, width=110, allow_unicode=True,
                         default_flow_style=False)
        chunks.append(text)
    head_keys = ("format", "id", "name", "summary", "section", "family", "status", "python", "docs",
                 "access", "discovery", "requires")
    head = "".join(c for c, k in zip(chunks, doc) if k in head_keys)
    rest = [c for c, k in zip(chunks, doc) if k not in head_keys]
    return "\n".join([head] + rest)


# --------------------------------------------------------------------------- shared parts


def common_header(v1, section, family, notes, python_info):
    doc = {}
    doc["format"] = 2
    doc["id"] = v1["id"]
    doc["name"] = v1["name"]
    summ = short_summary(v1.get("summary") or v1["name"])
    if summ.rstrip().endswith(":"):
        summ = v1["name"]
    doc["summary"] = summ
    doc["section"] = section
    doc["family"] = family
    status = v1.get("status")
    if status not in ("released", "beta", "alpha", "deprecated"):
        notes.add("status", f"v1 status {status!r} mapped to released")
        status = "released"
    doc["status"] = status
    doc["python"] = python_info
    urls = []
    for s in v1.get("sources", []):
        if s.get("url") and s["url"] not in urls:
            urls.append(s["url"])
    doc["docs"] = urls
    lvl = (v1.get("auth") or {}).get("default_access_level")
    if lvl not in ACCESS_LEVELS:
        if lvl not in (None, "unknown"):
            notes.add("access", f"default access level {lvl!r} replaced by admin")
        lvl = "admin"
    doc["access"] = lvl
    return doc


def convert_discovery(v1, notes, family, version_hint=None):
    out = []
    for d in v1.get("discovery") or []:
        m = d.get("method")
        if m == "api_discovery" and d.get("id"):
            out.append({"api_discovery": d["id"]})
        elif m == "api_discovery":
            notes.add("discovery", "api_discovery entry without id dropped")
        elif m == "device_config_discover" and d.get("id"):
            ver = None
            if d.get("path"):
                ver = d["path"].rstrip("/").rsplit("/", 1)[-1]
            ver = ver or version_hint
            if ver:
                out.append({"dca": {"api": d["id"], "version": ver}})
            else:
                notes.add("discovery", "device_config_discover without version dropped")
        elif m == "param_property":
            prop = d.get("property") or ""
            mm = re.match(r"^([\w.\-]+)=(.*)$", prop)
            if mm and not re.search(r"[<>!]=?$", mm.group(1)):
                out.append({"param": {"name": mm.group(1), "value": mm.group(2).strip()}})
            else:
                notes.add("discovery", f"param_property {prop!r} is not a Name=value pair: dropped")
        else:
            notes.add("discovery", f"discovery method {m} dropped")
    seen, uniq = set(), []
    for d in out:
        k = json.dumps(d, sort_keys=True)
        if k not in seen:
            seen.add(k)
            uniq.append(d)
    return uniq


def convert_requires(v1):
    r = v1.get("requirements") or {}
    out = {}
    if r.get("axis_os_min"):
        out["firmware"] = str(r["axis_os_min"])
    if r.get("requires_application"):
        out["application"] = str(r["requires_application"])
    return out


def convert_sources(v1):
    out = []
    for s in v1.get("sources", []):
        e = {"url": s.get("url")}
        if s.get("sha256_md"):
            e["sha256_md"] = s["sha256_md"]
        if s.get("retrieved_at"):
            e["retrieved_at"] = str(s["retrieved_at"])
        out.append(e)
    return out


def class_name(v1, strip_config=False):
    cn = (v1.get("python") or {}).get("class_name") or pascal(v1["id"])
    if cn.endswith("Api") and len(cn) > 3:
        cn = cn[:-3]
    elif cn.endswith("Client") and len(cn) > 6:
        cn = cn[:-6]
    if strip_config and cn.endswith("Config") and len(cn) > 6:
        cn = cn[:-6]
    return cn


def convert_types(v1types, ctx, skip=()):
    out = {}
    for name, schema in v1types.items():
        if name in skip:
            continue
        out[ctx.typemap[name]] = conv(schema, ctx)
    return out


def make_typemap(names, reserved=()):
    m, used = {}, set(reserved)
    for n in names:
        p = pascal(n)
        if p in _RESERVED_TYPES:
            p += "Type"
        c = p
        i = 2
        while c in used:
            c = f"{p}{i}"
            i += 1
        used.add(c)
        m[n] = c
    return m


def _uniq(name, used):
    c, i = name, 2
    while c in used:
        c = f"{name}{i}"
        i += 1
    used.add(c)
    return c


def name_inline(s, owner, used):
    """Give nested inline objects unique x-names (<Owner><Property>[Item])."""
    if not isinstance(s, dict):
        return
    if s.get("type") == "array" and isinstance(s.get("items"), dict):
        it = s["items"]
        if "properties" in it and "$ref" not in it:
            if "x-name" not in it:
                it["x-name"] = _uniq(owner + "Item", used)
                s["items"] = order_schema(it)
            name_inline(s["items"], s["items"]["x-name"], used)
        return
    for pn, ps in (s.get("properties") or {}).items():
        if not isinstance(ps, dict):
            continue
        nm = owner + pascal(pn)
        holder, key = s["properties"], pn
        target = ps
        if ps.get("type") == "array" and isinstance(ps.get("items"), dict):
            target, holder, key, nm = ps["items"], ps, "items", nm + "Item"
        if isinstance(target, dict) and "properties" in target and "$ref" not in target:
            if "x-name" not in target:
                target["x-name"] = _uniq(nm, used)
                holder[key] = target = order_schema(target)
            name_inline(target, target["x-name"], used)


def fix_pynames(s):
    if isinstance(s, list):
        for x in s:
            fix_pynames(x)
        return
    if not isinstance(s, dict):
        return
    props = s.get("properties")
    if isinstance(props, dict):
        used = set()
        for pn, ps in props.items():
            if not isinstance(ps, dict):
                continue
            name = ps.get("x-python-name")
            if not name:
                try:
                    name = _field_name(pn) if _field_name else snake(pn)
                except Exception:  # noqa: BLE001
                    name = None
                if name is None:
                    base = snake(pn.lstrip("$")) or "value"
                    name = {"$schema": "json_schema"}.get(pn, base + "_")
                    ps["x-python-name"] = name
                elif name in used:
                    base = name
                    k = 2
                    while f"{base}_{k}" in used:
                        k += 1
                    name = f"{base}_{k}"
                    ps["x-python-name"] = name
            used.add(name)
    for v in s.values():
        fix_pynames(v)


def finalize(doc, notes):
    types = doc.get("types") or {}
    used = set(types) | set(_RESERVED_TYPES)
    for n, t in types.items():
        name_inline(t, n, used)
    for oid, o in doc["operations"].items():
        p = o.get("params")
        if isinstance(p, dict) and "$ref" not in p:
            if p.get("type", "object") != "object" or "properties" not in p:
                notes.add("params-not-object", f"{oid}: params is not an object schema (generator needs a model)")
            dflt = pascal(oid) + "Request"
            if "x-name" not in p and dflt in types:
                p["x-name"] = _uniq(dflt + "Args", used)
                o["params"] = p = order_schema(p)
            name_inline(p, p.get("x-name") or dflt, used)
        elif isinstance(p, dict) and "$ref" in p:
            tgt = types.get(p["$ref"].rsplit("/", 1)[-1])
            if not (isinstance(tgt, dict) and "properties" in tgt):
                notes.add("params-not-object", f"{oid}: params refers to a non-object type (generator needs a model)")
        r = o.get("result")
        if isinstance(r, dict) and "$ref" not in r:
            name_inline(r, pascal(oid) + "Result", used)
    fix_pynames(types)
    for o in doc["operations"].values():
        fix_pynames(o.get("params"))
        fix_pynames(o.get("result"))


def check_refs(doc, notes):
    """Replace dangling #/types refs by an empty schema."""
    types = doc.get("types") or {}

    def walk(o):
        if isinstance(o, dict):
            r = o.get("$ref")
            if isinstance(r, str) and r.startswith("#/types/") and r[8:] not in types:
                notes.add("dangling-ref", f"{r} is not defined; replaced by an untyped schema")
                o.pop("$ref")
            for v in list(o.values()):
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(doc.get("types"))
    walk(doc.get("operations"))


# --------------------------------------------------------------------------- effects

READ = ("get", "list", "read", "query", "check", "fetch", "is", "has")
ACTION = ("start", "stop", "activate", "deactivate", "restart", "reboot", "trigger", "test", "send", "move")


def infer_effect(op_id):
    """Return (effect, write, guessed)."""
    w = snake(op_id).split("_")[0]
    if w in READ:
        return "read", None, False
    if w in ("add", "create"):
        return "write", "create", False
    if w in ("remove", "delete"):
        return "write", "delete", False
    if w in ("set", "update"):
        return "write", "patch", True
    if w == "configure":
        return "write", "replace", False
    if w == "clear":
        return "write", "delete", True
    if w in ("reset", "import"):
        return "write", "replace", True
    if w in ACTION:
        return "action", None, False
    return "unknown", None, False


# --------------------------------------------------------------------------- JSON-RPC


class Node:
    def __init__(self):
        self.schema = None
        self.children = collections.OrderedDict()
        self.array = False
        self.required = False
        self.nullable = False


def node_schema(node):
    if node.schema is None:
        node.schema = {"type": "object"}
    base = dict(node.schema)
    if "$ref" in base or not node.children:
        return base
    props, req, nulls = {}, [], []
    for name, ch in node.children.items():
        props[name] = node_schema(ch)
        if ch.required:
            req.append(name)
        if ch.nullable:
            nulls.append(name)
    obj = {"type": "object"}
    if req:
        obj["required"] = req
    if nulls:
        obj["x-nullable"] = nulls
    obj["properties"] = props
    if node.array or base.get("type") == "array":
        items = obj
        out = {k: v for k, v in base.items() if k not in ("type", "items", "properties")}
        out = {"type": "array", "items": items, **{k: v for k, v in out.items() if k != "type"}}
        return order_schema(out)
    for k in ("description", "x-name"):
        if k in base:
            obj[k] = base[k]
    return order_schema(obj)


def clean_leaf(s):
    s = dict(s)
    s.pop("_nullable", None)
    return s


def build_rpc_params(plist, ctx, notes, op_id, placement_flags):
    """Returns (params_schema|None, since_fields, skipped_multipart)."""
    root = Node()
    root.schema = {"type": "object"}
    since_fields = {}
    whole = None
    array_root = False
    for p in plist:
        pin = p.get("in")
        name = p["name"]
        if pin in ("multipart", "rtsp_query"):
            notes.add("non-json-param", f"{op_id}: {pin} parameter {name} dropped")
            continue
        if name == "params":
            whole = leaf_schema(p, ctx)
            continue
        if name.startswith("params[]."):
            array_root = True
            name = name[len("params[]."):]
        elif name.startswith("params."):
            name = name[len("params."):]
        elif pin == "json_body":
            placement_flags["top_level"] = True
        segs = name.split(".")
        node = root
        for i, seg in enumerate(segs):
            is_arr = seg.endswith("[]")
            seg = seg[:-2] if is_arr else seg
            ch = node.children.get(seg)
            if ch is None:
                ch = Node()
                node.children[seg] = ch
            if is_arr:
                ch.array = True
            node = ch
        ls = leaf_schema(p, ctx)
        if ls.pop("_nullable", None):
            node.nullable = True
        if node.schema is not None and node.children and "$ref" not in ls:
            # keep description of earlier synthesized parent
            pass
        node.schema = ls
        node.required = bool(p.get("required"))
        if p.get("since"):
            pv = parse_version(p["since"])
            if pv:
                since_fields["params." + ".".join(s.rstrip("[]") for s in segs)] = vstr(pv)
    if whole is not None:
        whole.pop("_nullable", None)
        if root.children:
            notes.add("params-shape", f"{op_id}: both whole params and flattened params present")
        return whole, since_fields
    if not root.children:
        return None, since_fields
    sch = node_schema(root)
    if array_root:
        notes.add("params-array", f"{op_id}: params is an array of objects (params[].x)")
        sch = {"type": "array", "items": sch}
    return sch, since_fields


def rpc_result(op, ctx, notes):
    resp = op.get("response") or {}
    schema = resp.get("schema")
    if not isinstance(schema, dict):
        return None
    props = schema.get("properties")
    if isinstance(props, dict) and "data" in props:
        data = props["data"]
    elif "$ref" in schema or "x-unresolved-type" in schema:
        data = schema
    else:
        if props:
            notes.add("result-shape", f"{op['id']}: response schema has no data wrapper; result omitted")
        return None
    if not isinstance(data, dict) or not data:
        return None
    r = conv(data, ctx)
    if r.get("type") == "object" and not r.get("properties") and "$ref" not in r and "additionalProperties" not in r:
        return None
    if r == {"type": "object"}:
        return None
    if not r:
        return None
    return r


def parse_json_maybe(v):
    if isinstance(v, (dict, list)):
        return v
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return None
    return None


def rpc_examples(op, placement, notes):
    out = []
    for e in op.get("examples") or []:
        req = e.get("request") or {}
        resp = e.get("response") or {}
        body = req.get("body")
        if body is None:
            body = parse_json_maybe(req.get("raw"))
        rbody = resp.get("body")
        if rbody is None:
            rbody = parse_json_maybe(resp.get("raw"))
        if not isinstance(body, dict) or not isinstance(rbody, dict):
            continue
        if placement == "params":
            params = body.get("params", {})
        else:
            params = {k: v for k, v in body.items() if k not in ("apiVersion", "context", "method")}
        if "data" in rbody:
            r = {"data": rbody["data"]}
        elif "error" in rbody and isinstance(rbody["error"], dict):
            r = {"error": {k: rbody["error"][k] for k in ("code", "message") if k in rbody["error"]}}
        else:
            continue
        ex = {"title": e.get("title") or op["id"], "request": {"params": params}, "response": r}
        if e.get("source_url"):
            ex["source"] = e["source_url"]
        out.append(ex)
    return out


def convert_jsonrpc(v1, section, ctxinfo):
    notes = Notes()
    ops = v1["operations"]
    ver = v1.get("versioning") or {}

    # --- versions
    parsed = []
    for v in ver.get("api_versions") or []:
        pv = parse_version(v)
        if pv:
            parsed.append(pv)
    if not parsed:
        for op in ops:
            for e in op.get("examples") or []:
                b = (e.get("request") or {}).get("body")
                if isinstance(b, dict) and parse_version(b.get("apiVersion", "")):
                    parsed.append(parse_version(b["apiVersion"]))
        parsed = sorted(set(parsed))
        if parsed:
            notes.add("versions", "versions taken from examples (none in versioning)")
        else:
            parsed = [(1, 0)]
            notes.add("versions", "no versions documented; assumed 1.0")
    major = max(p[0] for p in parsed)
    versions = sorted({p for p in parsed if p[0] == major})
    others = sorted({p[0] for p in parsed if p[0] != major})
    if others:
        notes.add("other-majors",
                  f"API also documents major(s) {', '.join(map(str, others))}; this spec covers major {major} only. "
                  "A separate spec (module suffix _v2 for later majors) is needed for the others")
    first_version = versions[0]

    # --- ops filter
    rpc_ops, gsv = [], []
    for op in ops:
        if op.get("kind") != "json_rpc_method" or not (op.get("json_rpc") or {}).get("method"):
            notes.add("skipped-op", f"{op['id']} ({op.get('kind')}) is not a JSON-RPC method; skipped")
            continue
        if op["json_rpc"]["method"].startswith("getSupportedVersions") or op["id"] == "get_supported_versions":
            gsv.append(op)
            continue
        rpc_ops.append(op)

    # --- binding path
    paths = collections.Counter((op.get("http") or {}).get("path") for op in ops if op.get("kind") == "json_rpc_method")
    paths.pop(None, None)
    base_paths = (v1.get("transport") or {}).get("base_paths") or []
    if paths:
        top = paths.most_common()
        best = max(c for _, c in top)
        cands = [p for p, c in top if c == best]
        path = base_paths[0] if base_paths and base_paths[0] in cands else cands[0]
    elif base_paths:
        path = base_paths[0]
    else:
        path = ""
        notes.add("path-unknown", "CGI path is not documented in the source; binding.path left empty")

    # --- negotiation
    if gsv:
        key = "apiVersions"
        sch = (gsv[0].get("response") or {}).get("schema") or {}
        dprops = (((sch.get("properties") or {}).get("data") or {}).get("properties") or {})
        if dprops:
            key = next(iter(dprops))
        if len({(o.get("http") or {}).get("path") for o in gsv}) > 1:
            notes.add("negotiation", "getSupportedVersions exists on several paths; one negotiation used")
        negotiation = {"get_supported_versions": {"key": key}}
    elif ver.get("version_field") == "apiVersion":
        negotiation = {"fixed": vstr(versions[-1])}
    else:
        negotiation = None

    # --- types
    v1types = v1.get("types") or {}
    reserved = {pascal(v1["id"])}
    typemap = make_typemap(v1types.keys())
    ctx = Ctx(notes, typemap, v1types)
    types = convert_types(v1types, ctx)

    # --- operations
    flags = {"top_level": False}
    ops_out = {}
    general_errors = convert_errors(v1.get("errors"), notes, scope="general")
    default_access = (v1.get("auth") or {}).get("default_access_level")
    if default_access not in ACCESS_LEVELS:
        default_access = "admin"
    guessed, unknown = [], []
    for op in rpc_ops:
        oid = op["id"]
        if keyword.iskeyword(oid):
            notes.add("keyword", f"operation id {oid} is a Python keyword; renamed {oid}_")
            oid = oid + "_"
        o = {}
        o["summary"] = short_summary(op.get("summary") or oid)
        if op.get("description"):
            d = trim(op["description"], 400)
            if d != o["summary"]:
                o["description"] = d
        al = op.get("access_level")
        if al in ACCESS_LEVELS and al != default_access:
            o["access"] = al
        eff, wr, g = infer_effect(op["id"])
        o["effect"] = eff
        if wr:
            o["write"] = wr
        if g:
            guessed.append(f"{oid}={eff}/{wr}")
        if eff == "unknown":
            unknown.append(oid)
        sv = parse_version(op.get("since")) if op.get("since") else None
        if sv and sv != first_version:
            if sv[0] == major:
                o["since"] = vstr(sv)
        b = {"method": op["json_rpc"]["method"]}
        opath = (op.get("http") or {}).get("path")
        if opath and opath != path:
            b["path"] = opath
        o["binding"] = b
        usable = [p for p in op.get("params", [])]
        if usable and all(p.get("in") == "multipart" for p in usable):
            notes.add("multipart-op", f"{oid}: only multipart parameters; skipped (not representable)")
            continue
        sch, since_fields = build_rpc_params(usable, ctx, notes, oid, flags)
        if sch:
            o["params"] = sch
        res = rpc_result(op, ctx, notes)
        if res:
            o["result"] = res
        if since_fields:
            o["since_fields"] = since_fields
        oerrs = convert_errors(op.get("errors"), notes, skip=general_errors)
        if oerrs:
            o["errors"] = oerrs
        exs = rpc_examples(op, "params", notes)
        ops_out[oid] = (o, exs, op)
    placement = "top_level" if flags["top_level"] else "params"
    if placement == "top_level":
        # examples and param roots were built with params placement; rebuild examples
        pass
    final_ops = {}
    for oid, (o, exs, op) in ops_out.items():
        exs = rpc_examples(op, placement, notes)
        if exs:
            o["examples"] = exs
        final_ops[oid] = o
    if guessed:
        notes.add("effect-guessed", "write semantics guessed from the method name: " + ", ".join(guessed))
    if unknown:
        notes.add("effect-unknown", "effect could not be inferred from the method name: " + ", ".join(unknown))

    # --- assemble
    pyinfo = {
        "module": (v1.get("python") or {}).get("module") or snake(v1["id"]),
        "class": class_name(v1),
    }
    doc = common_header(v1, section, "jsonrpc", notes, pyinfo)
    disc = convert_discovery(v1, notes, "jsonrpc")
    if disc:
        doc["discovery"] = disc
    req = convert_requires(v1)
    if req:
        doc["requires"] = req
    binding = {"path": path, "major": major, "versions": [vstr(v) for v in versions]}
    if negotiation:
        binding["negotiation"] = negotiation
    binding["params_placement"] = placement
    doc["binding"] = binding
    if general_errors:
        doc["errors"] = general_errors
    if types:
        doc["types"] = types
    doc["operations"] = final_ops
    doc["sources"] = convert_sources(v1)
    check_refs(doc, notes)
    finalize(doc, notes)
    prov = {"completeness": (v1.get("provenance") or {}).get("completeness", "partial")}
    oq = list((v1.get("provenance") or {}).get("open_questions") or []) + notes.render()
    if oq:
        prov["open_questions"] = oq
    prov["migrated_from"] = "v1"
    prov["curated"] = False
    doc["provenance"] = prov
    return doc, notes


# --------------------------------------------------------------------------- DCA


class Ent:
    def __init__(self, raw, parent):
        self.raw = raw
        self.parent = parent
        self.name = raw["name"]
        self.kind = raw.get("type")
        self.key = raw.get("key_property")
        self.children = []
        self.chain = []  # (segment, is_collection)
        self.type_name = None
        self.props = {p["name"]: p for p in raw.get("properties") or []}
        self.ops = set(raw.get("operations") or [])
        self.attrs = raw.get("attributes") or {}


def build_entities(rest_model):
    ents = {}
    roots = []

    def walk(raw, parent, rootname):
        e = Ent(raw, parent)
        if parent is None:
            e.chain = []
        else:
            seg = raw["name"][len(rootname) + 1:] if raw["name"].startswith(rootname + ".") else raw["name"]
            # segment relative to parent
            pname = parent.name
            rel = raw["name"][len(pname) + 1:] if raw["name"].startswith(pname + ".") else seg
            e.chain = parent.chain + [(rel, raw.get("type") == "collection")]
        ents[e.name] = e
        if parent:
            parent.children.append(e)
        for c in raw.get("entities") or []:
            walk(c, e, rootname)
        return e

    for r in rest_model.get("entities") or []:
        roots.append(walk(r, None, r["name"]))
    return ents, roots


def ent_seg_names(ent, last_form):
    """Snake segments for an entity chain. last_form: 'singular' or 'plural'."""
    segs = []
    for i, (s, coll) in enumerate(ent.chain):
        last = i == len(ent.chain) - 1
        if coll and (not last or last_form == "singular"):
            segs.append(singular_snake(s))
        else:
            segs.append(snake(s))
    return segs


def prop_schema(p, ctx, notes):
    s = {}
    if isinstance(p.get("schema"), dict) and p["schema"]:
        s = conv(p["schema"], ctx)
    else:
        dt = str(p.get("datatype") or "").lower()
        m = {"boolean": "boolean", "string": "string", "integer": "integer", "number": "number",
             "float": "number", "int": "integer"}
        if dt in m:
            s = {"type": m[dt]}
        else:
            notes.add("untyped-property", f"property {p['name']} has unknown datatype {p.get('datatype')!r}")
    d = p.get("description")
    if d and "description" not in s:
        s["description"] = trim(d)
    elif d and "$ref" not in s and "description" in s:
        pass
    return order_schema(s)


def perm_flags(p):
    ops = p.get("operations")
    if not ops:
        return True, False
    return ("get" in ops), ("set" in ops)


def convert_dca(v1, section, ctxinfo):
    notes = Notes()
    rm = v1.get("rest_model")
    root_path = rm["root_path"]
    ents, roots = build_entities(rm)
    if len(roots) != 1:
        notes.add("roots", f"{len(roots)} root entities; only the first is the tree root")
    root = roots[0]
    v1types = v1.get("types") or {}

    # generated entity types in v1 -> entity
    gen_map = {}
    for tname, t in v1types.items():
        d = (t or {}).get("description") or ""
        m = re.match(r"^([\w.\-]+) entity \(", d)
        if m and m.group(1) in ents:
            gen_map[tname] = ents[m.group(1)]
    for op in v1["operations"]:
        r = op.get("rest") or {}
        if r.get("operation") in ("get", "list") and not r.get("property"):
            data = (((op.get("response") or {}).get("schema") or {}).get("properties") or {}).get("data") or {}
            ref = data.get("$ref") or (data.get("items") or {}).get("$ref")
            if ref and ref.startswith("#/types/") and r.get("entity") in ents:
                gen_map.setdefault(ref[8:], ents[r["entity"]])

    shared = [n for n in v1types if n not in gen_map]
    cls = class_name(v1, strip_config=True)
    typemap = make_typemap(shared, reserved=())
    used = set(typemap.values())

    # entity type names
    def want(e):
        if e.parent is None:
            return cls
        seg, coll = e.chain[-1]
        return pascal(singular_snake(seg) if coll else seg)

    used |= set(_RESERVED_TYPES)
    pending = list(ents.values())
    for e in pending:
        base = want(e)
        cand = base
        if cand in used and e.parent is not None:
            cand = pascal(e.parent.type_name or want(e.parent)) + base
        i = 2
        while cand in used:
            cand = f"{base}{i}"
            i += 1
        e.type_name = cand
        used.add(cand)
    for tname, e in gen_map.items():
        typemap[tname] = e.type_name

    ctx = Ctx(notes, typemap, v1types)
    types = convert_types(v1types, ctx, skip=set(gen_map))

    # entity types
    v1_add = collections.defaultdict(set)
    for op in v1["operations"]:
        r = op.get("rest") or {}
        if r.get("operation") == "add" and r.get("entity") in ents:
            for p in op.get("params") or []:
                if p.get("in") == "json_body":
                    nm = p["name"][5:] if p["name"].startswith("data.") else p["name"]
                    v1_add[r["entity"]].add(nm.split(".")[0])
    for e in ents.values():
        readable = {n: p for n, p in e.props.items() if perm_flags(p)[0]}
        add_attr = e.attrs.get("add_operation") or e.attrs.get("add") or {}
        add_names = set(add_attr.get("required") or add_attr.get("required_fields") or []) | set(
            add_attr.get("optional") or add_attr.get("optional_fields") or []) | v1_add[e.name]
        mutable = ("set" in e.ops) or ("add" in e.ops) or any(perm_flags(p)[1] for p in e.props.values())
        props, nulls, ro = {}, [], []
        for n, p in readable.items():
            props[n] = prop_schema(p, ctx, notes)
            if p.get("nullable") is True:
                nulls.append(n)
            if mutable and not perm_flags(p)[1] and n not in add_names:
                ro.append(n)
        for c in e.children:
            seg = c.chain[-1][0]
            if c.kind == "collection":
                props[seg] = {"type": "array", "items": {"$ref": "#/types/" + c.type_name}}
            else:
                props[seg] = {"$ref": "#/types/" + c.type_name}
        t = {"type": "object"}
        if e.raw.get("description") and e.parent is not None:
            t["description"] = trim(e.raw["description"])
        elif e.parent is None:
            t["description"] = "The whole API tree."
        if e.key and e.key in readable:
            t["required"] = [e.key]
        if nulls:
            t["x-nullable"] = nulls
        if ro:
            t["x-read-only"] = ro
        t["properties"] = props
        types[e.type_name] = order_schema(t)

    # operations
    entries = []  # dict(verb, ent, kind, prop, op)
    default_access = (v1.get("auth") or {}).get("default_access_level")
    if default_access not in ACCESS_LEVELS:
        default_access = "admin"
    dropped_prop_gets = 0
    for op in v1["operations"]:
        r = op.get("rest") or {}
        e = ents.get(r.get("entity"))
        if not e:
            notes.add("skipped-op", f"{op['id']}: unknown entity {r.get('entity')}")
            continue
        opn, prop = r.get("operation"), r.get("property")
        if opn == "get" and prop:
            if "get" in e.ops:
                dropped_prop_gets += 1
                continue
        entries.append({"e": e, "opn": opn, "prop": prop, "action": r.get("action"), "op": op})
    if dropped_prop_gets:
        notes.add("dropped-property-gets", f"{dropped_prop_gets} per-property GET operations dropped")

    def base_name(en, level):
        e, opn, prop = en["e"], en["opn"], en["prop"]
        is_root = e.parent is None
        item = e.kind == "collection"
        if opn == "action":
            a = snake(en["action"] or "action")
            if level == 0:
                return a
            segs = ent_seg_names(e, "singular")
            return a + "_" + "_".join(segs[-level:]) if segs else a
        if opn == "list":
            segs = ent_seg_names(e, "plural")
            return "list_" + "_".join(segs[-max(level, 1):])
        segs = ent_seg_names(e, "singular")
        sel = segs[-max(level, 1):] if segs else []
        tail = "_".join(sel)
        if opn == "get":
            if not prop and is_root:
                return "get_all"
            return "get_" + tail + (("_" + snake(prop)) if prop else "")
        if opn == "set":
            if prop:
                return "set_" + (tail + "_" if tail else "") + snake(prop)
            return "update_" + (tail if tail else "all")
        if opn in ("add", "remove"):
            return f"{opn}_{tail}"
        return f"{snake(opn or 'op')}_{tail}"

    levels = [0 if en["opn"] == "action" else 1 for en in entries]
    names = [None] * len(entries)
    for _ in range(8):
        names = [base_name(en, lv) for en, lv in zip(entries, levels)]
        cnt = collections.Counter(names)
        changed = False
        for i, n in enumerate(names):
            if cnt[n] > 1:
                maxlv = len(entries[i]["e"].chain)
                if levels[i] < maxlv:
                    levels[i] += 1
                    changed = True
        if not changed:
            break
    cnt = collections.Counter(names)
    for i, n in enumerate(names):
        if cnt[n] > 1:
            notes.add("name-collision", f"operation name {n} collides; numeric suffix added")
    seen = collections.Counter()
    final_names = []
    for n in names:
        seen[n] += 1
        final_names.append(n if seen[n] == 1 else f"{n}_{seen[n]}")
    for i, n in enumerate(final_names):
        if keyword.iskeyword(n):
            final_names[i] = n + "_"
            notes.add("keyword", f"operation id {n} is a Python keyword; renamed {n}_")

    ops_out = {}
    extra_types = {}
    unresolved_actions = []
    for en, oid in zip(entries, final_names):
        e, opn, prop, op = en["e"], en["opn"], en["prop"], en["op"]
        r = op["rest"]
        o = {}
        o["summary"] = dca_summary(e, opn, prop, en["action"], op, v1["name"])
        al = op.get("access_level")
        if al in ACCESS_LEVELS and al != default_access:
            o["access"] = al
        if opn in ("get", "list"):
            o["effect"] = "read"
        elif opn == "add":
            o["effect"], o["write"] = "write", "create"
        elif opn == "remove":
            o["effect"], o["write"] = "write", "delete"
        elif opn == "set":
            o["effect"], o["write"] = "write", "patch"
        else:
            o["effect"] = "action"
        http = op["http"]
        path = http["path"]
        rel = path[len(root_path):] if path.startswith(root_path) else path
        b = {"method": http["method"], "path": rel}
        # key params
        keys = []
        for p in op.get("params") or []:
            if p.get("in") == "path":
                keys.append(p)
        key_names = [k["name"] for k in keys]
        props_obj = {}
        required = []
        for k in keys:
            ent_key = k["name"]
            # description from the owning entity key property if resolvable
            s = leaf_schema({kk: vv for kk, vv in k.items() if kk != "description"}, ctx)
            s.pop("_nullable", None)
            kd = None
            for anc in _ancestors(e):
                if anc.key == ent_key and ent_key in anc.props:
                    kd = anc.props[ent_key].get("description")
                    break
            if kd and "$ref" not in s:
                s["description"] = trim(kd)
            props_obj[ent_key] = order_schema(s)
            required.append(ent_key)
        body_params = [p for p in (op.get("params") or []) if p.get("in") == "json_body"]
        result = None
        if opn in ("get", "list"):
            data = (((op.get("response") or {}).get("schema") or {}).get("properties") or {}).get("data")
            if isinstance(data, dict) and data:
                result = conv(data, ctx)
        elif opn == "action":
            data = (((op.get("response") or {}).get("schema") or {}).get("properties") or {}).get("data")
            if isinstance(data, dict) and data:
                result = conv(data, ctx)
                if not result or result == {"type": "object"}:
                    result = None
        body_kind = None
        if opn == "add":
            body_kind = "object"
            add_attr = e.attrs.get("add_operation") or e.attrs.get("add") or {}
            req_n = list(add_attr.get("required") or add_attr.get("required_fields") or [])
            opt_n = list(add_attr.get("optional") or add_attr.get("optional_fields") or [])
            if not req_n and not opt_n:
                names_v1 = []
                for p in body_params:
                    nm = p["name"][5:] if p["name"].startswith("data.") else p["name"]
                    nm = nm.split(".")[0]
                    if nm not in names_v1:
                        names_v1.append(nm)
                req_n = [nm for nm in names_v1 if any(
                    (q["name"] == "data." + nm and q.get("required") and not q.get("inferred")) for q in body_params)]
                opt_n = [nm for nm in names_v1 if nm not in req_n]
            fields, req_f = {}, []
            for nm in req_n + opt_n:
                p = e.props.get(nm)
                fields[nm] = prop_schema(p, ctx, notes) if p else {}
                if nm in req_n:
                    req_f.append(nm)
            props_obj.update(fields)
            required += req_f
            tname = pascal(oid) + "Request"
            while tname in types or tname in extra_types:
                tname += "Args"
            tdef = {"type": "object", "description": f"Arguments of ``{oid}``."}
            if required:
                tdef["required"] = list(required)
            tdef["properties"] = props_obj
            extra_types[tname] = order_schema(tdef)
            params = {"$ref": "#/types/" + tname}
            if not (req_n or opt_n):
                notes.add("empty-add", f"{oid}: no add fields found")
        elif opn == "set" and not prop:
            body_kind = "object"
            names_v1 = []
            for p in body_params:
                nm = p["name"][5:] if p["name"].startswith("data.") else p["name"]
                nm = nm.split(".")[0]
                if nm not in names_v1 and nm not in key_names:
                    names_v1.append(nm)
            set_attr = e.attrs.get("set_operation") or {}
            for nm in names_v1:
                p = e.props.get(nm)
                props_obj[nm] = prop_schema(p, ctx, notes) if p else {}
            sreq = [x for x in (set_attr.get("required") or []) if x in props_obj]
            required += sreq
            tname = pascal(oid) + "Request"
            while tname in types or tname in extra_types:
                tname += "Args"
            tdef = {"type": "object", "description": f"Arguments of ``{oid}``."}
            if required:
                tdef["required"] = list(required)
            tdef["properties"] = props_obj
            extra_types[tname] = order_schema(tdef)
            params = {"$ref": "#/types/" + tname}
        elif opn == "set" and prop:
            body_kind = "value"
            p = e.props.get(prop)
            if p:
                ps = prop_schema(p, ctx, notes)
            else:
                ps = leaf_schema(body_params[0], ctx) if body_params else {}
                ps.pop("_nullable", None)
            props_obj[prop] = ps
            required.append(prop)
            params = _obj(props_obj, required, e, key_names)
            b["body_field"] = prop
        elif opn == "action":
            if body_params:
                act = next((a for a in e.raw.get("actions") or [] if a.get("name") == en["action"]), None)
                inp = (act or {}).get("input") or {}
                resolved = None
                ref_name = inp.get("x-unresolved-type") if isinstance(inp, dict) else None
                if isinstance(inp, dict) and "$ref" in inp:
                    ref_name = inp["$ref"].rsplit("/", 1)[-1]
                if ref_name and ref_name in v1types:
                    resolved = v1types[ref_name]
                if isinstance(resolved, dict) and not resolved.get("properties") and resolved.get("type", "object") == "object" \
                        and "$ref" not in resolved and "allOf" not in resolved:
                    body_kind = None  # empty input object: nothing to send
                    params = _obj(props_obj, required, e, key_names) if props_obj else None
                elif isinstance(resolved, dict) and isinstance(resolved.get("properties"), dict):
                    rc = conv(resolved, ctx)
                    for nm, sch in (rc.get("properties") or {}).items():
                        props_obj[nm] = sch
                    required += list(rc.get("required") or [])
                    body_kind = "object"
                    params = _obj(props_obj, required, e, key_names)
                else:
                    unresolved_actions.append(oid)
                    props_obj["data"] = {"description": trim(body_params[0].get("description") or "Action input.")}
                    required.append("data")
                    body_kind = "value"
                    b["body_field"] = "data"
                    params = _obj(props_obj, required, e, key_names)
            elif props_obj:
                params = _obj(props_obj, required, e, key_names)
            else:
                params = None
        else:
            params = _obj(props_obj, required, e, key_names) if props_obj else None
        if body_kind:
            b["body"] = body_kind
        elif opn == "action":
            b["body"] = "none"
        if isinstance(result, dict) and "$ref" in result:
            tgt = types.get(result["$ref"].rsplit("/", 1)[-1])
            if isinstance(tgt, dict) and tgt.get("type", "object") == "object" and not tgt.get("properties") \
                    and "$ref" not in tgt and "additionalProperties" not in tgt:
                result = None
        o["binding"] = b
        if params:
            o["params"] = params
        if result:
            o["result"] = result
        oerrs = convert_errors(op.get("errors"), notes)
        if oerrs:
            o["errors"] = oerrs
        exs = dca_examples(op, root_path)
        if exs:
            o["examples"] = exs
        ops_out[oid] = o
    if unresolved_actions:
        notes.add("action-input-unresolved",
                  "action input type not defined in the source; passed as a raw value in `data`: "
                  + ", ".join(unresolved_actions))
    # x-name for key-only params
    xnames = {}
    for oid, o in ops_out.items():
        p = o.get("params")
        if isinstance(p, dict) and "properties" in p and "$ref" not in p and "x-name" not in p:
            e = next(en["e"] for en, n in zip(entries, final_names) if n == oid)
            if o["binding"].get("body") in (None, "none") and set(p["properties"]) == set(p.get("required", [])):
                nm = e.type_name + "".join(pascal(k) for k in p["properties"]) + "Request"
                sig = json.dumps(p, sort_keys=True)
                if nm not in xnames or xnames[nm] == sig:
                    xnames[nm] = sig
                    p2 = {"type": "object", "x-name": nm}
                    p2.update({k: v for k, v in p.items() if k != "type"})
                    o["params"] = order_schema(p2)
    types.update(extra_types)

    # assemble
    ver_hint = root_path.rstrip("/").rsplit("/", 1)[-1]
    modname = (v1.get("python") or {}).get("module") or snake(v1["id"])
    if modname.endswith("_config"):
        stripped = modname[: -len("_config")]
        if stripped and stripped not in ctxinfo["all_modules"] and stripped not in CURATED_MODULES:
            modname_out = stripped
        else:
            modname_out = modname
            notes.add("module-collision", f"module name {stripped} collides with another spec; kept {modname}")
    else:
        modname_out = modname
    pyinfo = {"module": modname_out, "class": cls if modname_out != modname else class_name(v1)}
    doc = common_header(v1, section, "dca", notes, pyinfo)
    disc = convert_discovery(v1, notes, "dca", ver_hint)
    if disc:
        doc["discovery"] = disc
    req = convert_requires(v1)
    if req:
        doc["requires"] = req
    doc["binding"] = {"root": root_path}
    general_errors = convert_errors(v1.get("errors"), notes)
    if general_errors:
        doc["errors"] = general_errors
    if types:
        doc["types"] = types
    doc["operations"] = ops_out
    doc["sources"] = convert_sources(v1)
    check_refs(doc, notes)
    finalize(doc, notes)
    prov = {"completeness": (v1.get("provenance") or {}).get("completeness", "partial")}
    oq = list((v1.get("provenance") or {}).get("open_questions") or []) + notes.render()
    if oq:
        prov["open_questions"] = oq
    prov["migrated_from"] = "v1"
    prov["curated"] = False
    doc["provenance"] = prov
    return doc, notes


def _words(seg):
    return snake(seg).replace("_", " ")


def dca_summary(e, opn, prop, action, op, api_name):
    segs = [s for s, _ in e.chain]
    coll = e.kind == "collection"
    last = segs[-1] if segs else None
    one = _words(singular_snake(last)) if last else api_name
    many = _words(last) if last else api_name
    if opn == "action":
        act = next((a for a in e.raw.get("actions") or [] if a.get("name") == action), None)
        d = (act or {}).get("description")
        if d:
            return short_summary(d)
        return f"Run the {_words(action)} action" + (f" on a {one}." if coll else ".")
    if opn == "get" and not prop:
        if e.parent is None:
            return f"All data of the {api_name} API."
        return f"Get one {one}." if coll else f"Get the {one} settings."
    if opn == "list":
        return f"List the {many}."
    if opn == "get":
        return f"Get the {_words(prop)} of " + (f"a {one}." if coll else f"the {one}.")
    if opn == "set" and not prop:
        return f"Update a {one}." if coll else f"Update the {one} settings."
    if opn == "set":
        return f"Set the {_words(prop)} of " + (f"a {one}." if coll else f"the {one}." if last else "the device.")
    if opn == "add":
        return f"Add a {one}."
    if opn == "remove":
        return f"Remove a {one}."
    return short_summary(op.get("summary") or opn)


def _ancestors(e):
    while e is not None:
        yield e
        e = e.parent


def _obj(props, required, e, key_names):
    o = {"type": "object"}
    if required:
        o["required"] = list(required)
    o["properties"] = props
    return order_schema(o)


def dca_examples(op, root_path):
    out = []
    for ex in op.get("examples") or []:
        req = ex.get("request") or {}
        resp = ex.get("response") or {}
        rbody = resp.get("body")
        if rbody is None and resp.get("raw") is not None:
            rbody = parse_json_maybe(resp.get("raw"))
            if rbody is None:
                continue
        body = req.get("body")
        if body is None and req.get("raw") is not None:
            body = parse_json_maybe(req["raw"])
            if body is None:
                continue
        path = req.get("path") or ""
        if path.startswith(root_path):
            path = path[len(root_path):]
        r = {"path": path}
        if body is not None:
            r["body"] = body
        rr = {}
        if resp.get("http_status") is not None:
            rr["status"] = resp["http_status"]
        if rbody is not None:
            rr["body"] = rbody
        if not rr:
            continue
        e = {"title": ex.get("title") or op["id"], "request": r, "response": rr}
        if ex.get("source_url"):
            e["source"] = ex["source_url"]
        out.append(e)
    return out


# --------------------------------------------------------------------------- driver


# --------------------------------------------------------------------------- classic CGI

CGI_STYLES = ("cgi_query", "cgi_xml", "cgi_form_post")
RAW_BODY_TYPES = ("application/xml", "text/xml", "application/json", "multipart/form-data")
READ_VERBS = READ + ("download", "capture", "show", "view", "snapshot", "status", "retrieve", "poll", "find", "search")
ACTION_VERBS = ACTION + ("format", "repair", "check_disk", "pause", "resume", "cancel", "abort", "call", "play", "save")
WRITE_PATCH_VERBS = ("enable", "disable", "apply", "set", "update", "modify", "change", "configure", "select")
ERROR_ATTR_VALUES = ("error", "failed", "fail", "failure")
ERROR_MESSAGE_ATTRS = ("errormsg", "errormessage", "description", "message", "error", "reason")
ERROR_CODE_ATTRS = ("errorcode", "code")


def _xlocal(tag):
    return tag.rsplit("}", 1)[-1]


def cgi_effect(op_id, method):
    """(effect, write) for a CGI operation id, or (None, None)."""
    words = snake(op_id).split("_")
    first = words[0]
    if first in READ_VERBS:
        return "read", None
    if first in ("add", "create", "register", "upload", "import"):
        return "write", "create"
    if first in ("remove", "delete", "clear", "unregister"):
        return "write", "delete"
    if first in WRITE_PATCH_VERBS:
        return "write", "patch"
    if first in ("reset", "restore"):
        return "write", "replace"
    if first in ACTION_VERBS or "_".join(words[:2]) in ACTION_VERBS:
        return "action", None
    if first == "export" or any(w in ("progress", "info", "whoami", "query", "until", "status", "log", "logs", "report", "csv", "json", "xml") for w in words):
        return "read", None
    if "add" in words:
        return "write", "create"
    if first in ("mount", "unmount", "lock", "unlock", "bind", "unbind", "goto", "factory", "hard", "ping", "tcp",
                 "port", "oneshot", "record", "manual", "serial", "control", "ptz", "speed", "on"):
        return "action", None
    return None, None


def split_http_raw(raw):
    """(status, body) from a raw HTTP response or a bare body."""
    status = None
    if not isinstance(raw, str):
        return None, None
    text = raw.replace("\r\n", "\n")
    m = re.match(r"^HTTP/\d(?:\.\d)?\s+(\d{3})", text)
    if m:
        status = int(m.group(1))
        _, sep, body = text.partition("\n\n")
        text = body if sep else ""
    return status, text.strip("\n")


def parse_request_raw(raw):
    """(method, path, query) from the first line of a raw request, or None."""
    if not isinstance(raw, str):
        return None
    m = re.match(r"^\s*(GET|POST)\s+(\S+)", raw)
    if not m:
        return None
    path, _, query = m.group(2).partition("?")
    return m.group(1), path, query


def parse_xml_body(text):
    if not isinstance(text, str):
        return None
    i = text.find("<")
    if i < 0:
        return None
    try:
        return ET.fromstring(text[i:])
    except ET.ParseError:
        return None


def example_pairs(op):
    """Yield (example, request-part, response status, response body) for an operation's examples."""
    for e in op.get("examples") or []:
        resp = e.get("response") or {}
        status, body = split_http_raw(resp.get("raw")) if resp.get("raw") is not None else (None, None)
        if body is None and isinstance(resp.get("body"), str):
            body = resp["body"]
        status = resp.get("http_status") or status
        yield e, e.get("request") or {}, status, body


def derive_xml_errors(op):
    """Error rules visible in the example XML: (error_elements, status_error) or (None, None)."""
    elements, status = [], None
    for _e, _req, _st, body in example_pairs(op):
        root = parse_xml_body(body)
        if root is None:
            continue
        for el in root.iter():
            name = _xlocal(el.tag)
            if (el is not root or name == "Error") and name.endswith("Error") and name not in elements:
                elements.append(name)
            attrs = {_xlocal(k): v for k, v in el.attrib.items()}
            for key in ("result", "status"):
                if key in attrs and attrs[key].lower() in ERROR_ATTR_VALUES and status is None:
                    rule = {"attribute": key, "value": attrs[key]}
                    msg = next((a for a in attrs if a.lower() in ERROR_MESSAGE_ATTRS), None)
                    code = next((a for a in attrs if a.lower() in ERROR_CODE_ATTRS), None)
                    if msg:
                        rule["message"] = msg
                    if code:
                        rule["code"] = code
                    status = rule
    return elements, status


# ---- XML alignment: where does each schema property live in the sample reply?

def _resolve(s, types):
    for _ in range(10):
        if isinstance(s, dict) and "$ref" in s:
            s = types.get(s["$ref"].rsplit("/", 1)[-1], {})
        else:
            break
    return s if isinstance(s, dict) else {}


def _kind(s, types):
    r = _resolve(s, types)
    if "properties" in r:
        return "object"
    if r.get("type") == "array" or "items" in r:
        return "array"
    if r.get("type") == "object":
        return "map"
    return "scalar"


def _find_path(el, name, ci=False, depth=3):
    """Path (list of tags) from el to the first descendant named name (BFS), or None."""
    want = name.lower() if ci else name
    level = [(el, [])]
    for _ in range(depth):
        nxt = []
        for node, path in level:
            for child in node:
                tag = _xlocal(child.tag)
                if (tag.lower() if ci else tag) == want:
                    return path + [tag], child
                nxt.append((child, path + [tag]))
        level = nxt
    return None


def align_props(obj, types, el, memo):
    """Annotate obj's properties with x-xml where they live in el. Returns (matched, unmatched names)."""
    if id(obj) in memo:
        return memo[id(obj)]
    memo[id(obj)] = (0, [], 0.0)  # recursion guard
    attrs = {_xlocal(k): v for k, v in el.attrib.items()}
    matched, unmatched, weight = 0, [], 0.0
    for name, ps in (obj.get("properties") or {}).items():
        kind = _kind(ps, types)
        hint = None
        found = False
        depth_w = 1.0
        if kind in ("scalar", "map"):
            if name in attrs:
                found = True
            else:
                ci = next((a for a in attrs if a.lower() == name.lower()), None)
                if ci is not None:
                    hint, found = {"attribute": ci}, True
                else:
                    hit = _find_path(el, name) or _find_path(el, name, ci=True)
                    if hit is not None:
                        hint, found = {"child": "/".join(hit[0])}, True
                        depth_w = 1.0 / len(hit[0])
        else:
            hit = _find_path(el, name) or _find_path(el, name, ci=True)
            if hit is not None:
                path, child = hit
                if kind == "array":
                    items = _resolve(ps.get("items") if isinstance(ps, dict) else None, types)
                    if "properties" in items:
                        align_props(items, types, child, memo)
                else:
                    align_props(_resolve(ps, types), types, child, memo)
                if "/".join(path) != name:
                    hint = {"path": "/".join(path)}
                found = True
                depth_w = 1.0 / len(path)
        if found:
            matched += 1
            weight += depth_w
            if hint:
                ps["x-xml"] = hint
        else:
            unmatched.append(name)
    memo[id(obj)] = (matched, unmatched, weight)
    return memo[id(obj)]


def xml_candidates(root, bonus_names):
    out = [(root, [], 0)]
    level = [(root, [])]
    for depth in range(1, 5):
        nxt = []
        for node, path in level:
            for child in node:
                p = path + [_xlocal(child.tag)]
                out.append((child, p, depth))
                nxt.append((child, p))
        level = nxt
    return out


def align_result(schema, types, root, bonus_names=()):
    """Align an object schema to the best element of the sample reply.

    Returns (root_path or None, matched, unmatched) on success, or None."""
    props = schema.get("properties") or {}
    if not props:
        return None
    best = None
    for el, path, depth in xml_candidates(root, bonus_names):
        trial_schema = copy.deepcopy(schema)
        trial_types = copy.deepcopy(types)
        m, un, w = align_props(trial_schema, trial_types, el, {})
        score = w + (0.5 if _xlocal(el.tag) in bonus_names else 0) - depth * 0.001
        if m and (best is None or score > best[0]):
            best = (score, el, path, m, un)
    if best is None or best[3] * 2 < len(props):
        return None
    _score, el, path, _m, _un = best
    m, un, _w = align_props(schema, types, el, {})
    return ("/".join(path) or None), m, un


# ---- parameters

def cgi_param(p, ctx, notes, op_id):
    s = leaf_schema(p, ctx)
    s.pop("_nullable", None)
    if isinstance(s.get("enum"), list) and any(isinstance(v, bool) for v in s["enum"]):
        notes.add("enum-bool", f"{op_id}.{p['name']}: enum values were parsed as booleans by YAML; mapped to 'true'/'false' strings")
        s["enum"] = ["true" if v else "false" for v in s["enum"]]
        s["type"] = "string"
    if isinstance(s.get("default"), bool) and s.get("type") == "string":
        s["default"] = "true" if s["default"] else "false"
    if s.get("type") == "boolean":
        text = " ".join(str(x) for x in (p.get("description"), p.get("constraints")) if x)
        if re.search(r"\byes\b", text, re.IGNORECASE) and re.search(r"\bno\b", text, re.IGNORECASE):
            s["x-style"] = "axis_bool"
        elif re.search(r"(?<![\w.])0(?![\w.])", text) and re.search(r"(?<![\w.])1(?![\w.])", text):
            notes.add("bool-encoding", f"{op_id}.{p['name']}: documented as 0/1; sent as true/false (check)")
    if s.get("type") == "object":
        notes.add("object-param", f"{op_id}.{p['name']}: object-valued query parameter kept as a free-form map")
    pn = p.get("python_name")
    if pn and pn != p["name"]:
        try:
            derived = _field_name(p["name"]) if _field_name else snake(p["name"])
        except Exception:  # noqa: BLE001
            derived = None
        if derived != pn and keyword.iskeyword(pn) is False and pn.isidentifier():
            s["x-python-name"] = pn
    return order_schema(s)


def cgi_unsupported(op):
    """Reason why the runtime cannot express this operation, or None."""
    http = op.get("http") or {}
    rct = (http.get("request_content_type") or "").split(";")[0].strip()
    if rct in RAW_BODY_TYPES:
        return f"request body of type {rct} is not supported by the cgi binding"
    for p in op.get("params") or []:
        if p.get("in") in ("json_body", "multipart", "path"):
            return f"parameter {p['name']!r} is sent in {p['in']}, which the cgi binding cannot express"
    if (op.get("response") or {}).get("format") == "multipart":
        return "multipart streaming reply is not supported"
    return None


def parse_query_args(q):
    """dict from a query string, or None for placeholders / repeated keys."""
    if q is None:
        return {}
    if re.search(r"[<>\[\]{}]", q):
        return None
    pairs = urllib.parse.parse_qsl(q, keep_blank_values=True)
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys):
        return None
    return dict(pairs)


def cgi_examples(op, binding_query, param_names, form, path, default_path, notes, op_id, required_names):
    out = []
    for e, req, status, body in example_pairs(op):
        if body is None:
            continue
        method_raw = parse_request_raw(req.get("raw"))
        q = req.get("query")
        if q is None and method_raw:
            q = method_raw[2]
        if method_raw and method_raw[1] != path:
            continue
        if q is None and not method_raw and req:
            if req.get("path") and req["path"].split("?")[0] != path:
                continue
        if not req:
            continue
        args = parse_query_args(q if isinstance(q, str) else None if q else "")
        if args is None:
            continue
        args = {k: v for k, v in args.items() if not (k in binding_query and str(binding_query[k]) == v)}
        if any(k not in param_names for k in args):
            continue
        if any(n not in args for n in required_names):
            continue
        if "�" in body or len(body) > 1500:
            continue
        ex = {"title": trim(e.get("title") or op_id, 120)}
        ex["request"] = {("form" if form else "query"): args}
        ex["response"] = {"status": status or 200, "text": body}
        if e.get("source_url"):
            ex["source"] = e["source_url"]
        out.append(ex)
        if len(out) >= 3:
            break
    return out


def convert_cgi(v1, section, ctxinfo):
    notes = Notes()
    v1types = v1.get("types") or {}
    cls = class_name(v1)
    typemap = make_typemap(list(v1types))
    ctx = Ctx(notes, typemap, v1types)
    types = {}
    for name, schema in v1types.items():
        types[typemap[name]] = conv(strip_xml_hints(schema), ctx)

    ops_in = v1["operations"]
    skipped_ops = []
    candidates = []
    for op in ops_in:
        kind = op.get("kind")
        if kind != "http_endpoint":
            skipped_ops.append((op["id"], f"kind {kind} is not a classic CGI call"))
            continue
        why = cgi_unsupported(op)
        if why:
            skipped_ops.append((op["id"], why))
            continue
        candidates.append(op)
    for oid, why in skipped_ops:
        notes.add("op-skipped", f"{oid}: {why}")
    if not candidates:
        return None, notes

    paths = collections.Counter((op["http"].get("path") or "").split("?")[0] for op in candidates)
    api_path = paths.most_common(1)[0][0]
    lvl = (v1.get("auth") or {}).get("default_access_level")
    api_access = lvl if lvl in ACCESS_LEVELS else "admin"

    api_errors = convert_errors(v1.get("errors"), notes, scope="api")
    ops_out = {}
    used_ids = set()
    unknown_effect = []
    extra_types = {}
    used_names = set(types) | set(_RESERVED_TYPES)
    for op in candidates:
        oid = snake(op["id"]) or "call"
        if oid[0].isdigit() or keyword.iskeyword(oid):
            oid = "op_" + oid
        base, i = oid, 2
        while oid in used_ids:
            oid = f"{base}_{i}"
            i += 1
        used_ids.add(oid)
        http = op["http"]
        resp = op.get("response") or {}
        path = (http.get("path") or "").split("?")[0]
        method = http.get("method", "GET").upper()
        fixed = {k: str(v) for k, v in (http.get("fixed_query") or {}).items()}
        if "?" in (http.get("path") or ""):
            extra = urllib.parse.parse_qsl(http["path"].split("?", 1)[1], keep_blank_values=True)
            fixed.update(extra)
        params = op.get("params") or []
        has_form = any(p.get("in") == "form" for p in params)
        form = has_form and method == "POST"
        if has_form and method != "POST":
            notes.add("form-on-get", f"{oid}: form parameters on a {method} call sent as query arguments")
        if form and any(p.get("in") == "query" for p in params):
            notes.add("mixed-encoding", f"{oid}: query and form parameters are all sent in the POST body (check)")
        binding = {}
        if path != api_path:
            binding["path"] = path
        binding["method"] = method
        if fixed:
            binding["query"] = fixed
        if form:
            binding["encoding"] = "form"

        # parameters
        props, req = {}, []
        for p in params:
            if p["name"] in props:
                continue
            props[p["name"]] = cgi_param(p, ctx, notes, oid)
            if p.get("required") is True:
                req.append(p["name"])
        o = {}
        o["summary"] = short_summary(op.get("summary") or oid)
        desc = op.get("description")
        extras = []
        if op.get("deprecated"):
            extras.append("Deprecated.")
        if op.get("since"):
            extras.append(f"Since {op['since']}.")
        if desc or extras:
            o["description"] = trim(" ".join([desc or ""] + extras).strip(), 600)
        acc = op.get("access_level")
        if acc in ACCESS_LEVELS and acc != api_access:
            o["access"] = acc
        effect, write = cgi_effect(op["id"], method)
        if effect is None:
            effect, write = "unknown", None
            unknown_effect.append(oid)
        o["effect"] = effect
        if write:
            o["write"] = write

        # reply
        fmt = resp.get("format")
        ct = (resp.get("content_type") or http.get("response_content_type") or "").split(";")[0].strip()
        bodies = [b for _e, _r, _s, b in example_pairs(op) if b]
        reply = "text"
        result = None
        rschema = resp.get("schema") if isinstance(resp.get("schema"), dict) else None
        bonus = set()
        if rschema:
            if rschema.get("x-xml-success-element"):
                bonus.add(rschema["x-xml-success-element"])
        if fmt == "xml" or (fmt is None and ct.endswith("xml")):
            reply = "xml"
            elems, status_err = derive_xml_errors(op)
            opts = {}
            if elems:
                opts["error_elements"] = sorted(set(elems) | {"GeneralError"})
            if status_err:
                opts["status_error"] = status_err
            if opts:
                reply = {"xml": opts}
            result = xml_result(op, oid, rschema, resp, ctx, types, extra_types, used_names, notes, bonus)
        elif fmt == "json" or ct == "application/json":
            reply = "json"
            if rschema:
                r = conv(strip_xml_hints(rschema), ctx)
                if r.get("type") == "object" and not r.get("properties") and "$ref" not in r and "additionalProperties" not in r:
                    r = None
                if r:
                    result = r
            else:
                notes.add("json-untyped", f"{oid}: JSON reply without schema; result is untyped")
        elif fmt == "binary" or (ct and not ct.startswith(("text/", "application/xml")) and fmt != "text_kv"):
            reply = {"binary": {"media_types": [ct]}} if ct and ct != "application/octet-stream" else "binary"
            result = {"type": "string", "format": "binary"}
        elif fmt == "text_kv":
            strip = "root." if any(re.search(r"^root\.", b, re.MULTILINE) for b in bodies) else None
            reply = {"text_kv": {"strip_prefix": strip}} if strip else "text_kv"
            result = {"type": "object", "additionalProperties": {"type": "string"}}
        elif fmt in ("text", "none", None):
            if bodies and all(b.strip() == "OK" for b in bodies):
                reply = "text_ok"
            elif fmt == "none" or (fmt is None and not resp.get("notes")):
                reply = "text"
            else:
                reply = "text"
                if effect not in ("write", "action"):
                    result = {"type": "string"}
                elif "OK" in (resp.get("notes") or ""):
                    notes.add("reply-ok", f"{oid}: notes mention OK; reply read as plain text (check)")
        else:
            notes.add("reply-format", f"{oid}: response format {fmt!r} read as text")
        if result == {"x-xml": True} and effect in ("write", "action"):
            result = None  # nothing useful to return
        binding["reply"] = reply
        o["binding"] = binding
        if props:
            pschema = {"type": "object"}
            if req:
                pschema["required"] = req
            pschema["properties"] = props
            o["params"] = pschema
        if result is not None:
            o["result"] = result
        errs = convert_errors(op.get("errors"), notes, skip=api_errors)
        if errs:
            o["errors"] = errs
        exs = cgi_examples(op, fixed, set(props), form, path, api_path, notes, oid, req)
        if exs:
            o["examples"] = exs
        ops_out[oid] = o
    if unknown_effect:
        notes.add("effect-unknown", "effect could not be inferred from the name: " + ", ".join(unknown_effect))
    types.update(extra_types)

    modname = (v1.get("python") or {}).get("module") or snake(v1["id"])
    doc = common_header(v1, section, "cgi", notes, {"module": modname, "class": cls})
    doc["access"] = api_access
    disc = convert_discovery(v1, notes, "cgi")
    if disc:
        doc["discovery"] = disc
    req_ = convert_requires(v1)
    if req_:
        doc["requires"] = req_
    doc["binding"] = {"path": api_path}
    if api_errors:
        doc["errors"] = api_errors
    used_types = reachable_types(types, ops_out)
    dropped = sorted(set(types) - used_types)
    if dropped:
        notes.add("types-dropped", "types not referenced by any migrated operation: " + ", ".join(dropped))
    types = {k: v for k, v in types.items() if k in used_types}
    if types:
        doc["types"] = types
    doc["operations"] = ops_out
    doc["sources"] = convert_sources(v1)
    for key in ("param_cgi_groups", "events", "versioning", "envelope", "notes"):
        if v1.get(key):
            notes.add("dropped-section", f"v1 section {key} not carried over")
    check_refs(doc, notes)
    finalize(doc, notes)
    prov = {"completeness": (v1.get("provenance") or {}).get("completeness", "partial")}
    oq = list((v1.get("provenance") or {}).get("open_questions") or []) + notes.render()
    if oq:
        prov["open_questions"] = oq
    prov["migrated_from"] = "v1"
    prov["curated"] = False
    doc["provenance"] = prov
    return doc, notes


def strip_xml_hints(schema):
    if isinstance(schema, dict):
        return {k: strip_xml_hints(v) for k, v in schema.items() if not k.startswith(("x-xml", "x-xsd"))}
    if isinstance(schema, list):
        return [strip_xml_hints(v) for v in schema]
    return schema


def reachable_types(types, ops_out):
    seen = set()

    def walk(o):
        if isinstance(o, dict):
            r = o.get("$ref")
            if isinstance(r, str) and r.startswith("#/types/"):
                n = r[8:]
                if n not in seen and n in types:
                    seen.add(n)
                    walk(types[n])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for o in ops_out.values():
        walk(o.get("params"))
        walk(o.get("result"))
    return seen


def xml_result(op, oid, rschema, resp, ctx, types, extra_types, used_names, notes, bonus):
    """Result schema for an XML reply: a mapped model where the sample reply allows, else the raw element."""
    raw_el = {"x-xml": True}
    schema = None
    if rschema and (rschema.get("properties") or rschema.get("$ref")):
        schema = conv(strip_xml_hints(rschema), ctx)
    elif resp.get("fields"):
        props = {}
        for f in resp["fields"]:
            if not isinstance(f, dict) or not f.get("name"):
                continue
            t = f.get("type") if f.get("type") in ("string", "integer", "number", "boolean") else "string"
            ps = {"type": t}
            if f.get("description"):
                ps["description"] = trim(f["description"])
            props[f["name"]] = ps
        if props:
            schema = {"type": "object", "properties": props}
    if schema is None:
        if (resp.get("format") == "xml"):
            hint = sorted(set(re.findall(r"types\.(\w+)", resp.get("notes") or "")))
            more = f" (the v1 notes point at type(s) {', '.join(hint)})" if hint else ""
            notes.add("xml-unmapped", f"{oid}: no response schema in v1; result is the raw XML element{more}")
        return raw_el
    sample = None
    for _e, _r, _s, body in example_pairs(op):
        root = parse_xml_body(body)
        if root is not None and not any(_xlocal(x.tag).endswith("Error") for x in root.iter() if x is not root):
            sample = root
            break
    if sample is None:
        notes.add("xml-unmapped", f"{oid}: no parseable sample reply to derive the x-xml mapping from; result is the raw XML element")
        return raw_el
    work_types = copy.deepcopy(types)
    top = _resolve(schema, work_types) if "$ref" in schema else schema
    if "properties" not in top:
        notes.add("xml-unmapped", f"{oid}: response schema is not an object; result is the raw XML element")
        return raw_el
    hit = align_result(top, work_types, sample, bonus)
    if hit is None:
        notes.add("xml-unmapped", f"{oid}: schema properties not found in the sample reply; result is the raw XML element")
        return raw_el
    root_path, matched, unmatched = hit
    if unmatched:
        notes.add("xml-partial", f"{oid}: not found in the sample reply (left as attributes of the mapped element): " + ", ".join(unmatched))
    for k in types:  # keep annotations made on shared types
        types[k] = work_types[k]
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        if root_path:
            # a shared type with a root only for this call: wrap by copying
            new = _uniq(pascal(oid) + "Result", used_names)
            copy_t = copy.deepcopy(work_types[name])
            copy_t["x-xml"] = {"root": root_path}
            extra_types[new] = copy_t
            return {"$ref": "#/types/" + new}
        return {"$ref": "#/types/" + name}
    new = _uniq(pascal(oid) + "Result", used_names)
    top = dict(top)
    if root_path:
        top["x-xml"] = {"root": root_path}
    extra_types[new] = order_schema(top) if "x-xml" not in top else top
    return {"$ref": "#/types/" + new}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    files = sorted(args.src.glob("*/*.yaml"))
    all_modules = set()
    loaded = []
    for f in files:
        v1 = yaml.safe_load(f.read_text())
        loaded.append((f.parent.name, v1))
        all_modules.add((v1.get("python") or {}).get("module") or "")
    ctxinfo = {"all_modules": all_modules}

    stats = collections.Counter()
    skipped = collections.Counter()
    kinds = collections.Counter()
    failures = []
    outputs = []
    for section, v1 in loaded:
        styles = v1.get("styles") or []
        sid = v1["id"]
        if args.only and sid not in args.only:
            continue
        if styles and styles[0] == "json_rpc_cgi":
            fam = "jsonrpc"
        elif styles and styles[0] in CGI_STYLES:
            fam = "cgi"
        elif "device_config_rest" in styles:
            fam = "dca"
        else:
            skipped[f"out-of-scope:{styles[0] if styles else None}"] += 1
            print(f"out-of-scope {sid} ({styles[0] if styles else None})", file=sys.stderr)
            continue
        if (section, sid) in CURATED:
            skipped["hand-curated"] += 1
            continue
        if fam == "dca" and not v1.get("rest_model"):
            skipped["dca-without-rest_model"] += 1
            print(f"skip {sid}: no rest_model", file=sys.stderr)
            continue
        try:
            conv_fn = {"jsonrpc": convert_jsonrpc, "dca": convert_dca, "cgi": convert_cgi}[fam]
            doc, notes = conv_fn(copy.deepcopy(v1), section, ctxinfo)
            if doc is None:
                skipped["cgi-no-expressible-operations"] += 1
                print(f"skip {sid}: " + "; ".join(d for _, d in notes.items), file=sys.stderr)
                continue
        except Exception as exc:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            failures.append((sid, repr(exc)))
            continue
        stats[fam] += 1
        for k, _ in notes.items:
            kinds[k] += 1
        if notes.dropped:
            kinds["dropped-keywords"] += 1
        outputs.append((section, sid, doc))

    for section, sid, doc in outputs:
        text = "# Migrated from the v1 corpus by codegen/migrate_v1.py; not yet curated.\n" + dump_yaml(flowify_doc(doc))
        out = args.out / section / f"{sid}.yaml"
        if args.dry_run:
            continue
        if out.exists() and "curated: true" in out.read_text():
            print(f"keep curated {out}", file=sys.stderr)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)

    print("converted:", dict(stats))
    print("skipped:", dict(skipped))
    print("failures:", failures)
    print("note kinds:")
    for k, n in kinds.most_common():
        print(f"  {k}: {n}")
    return 1 if failures else 0


def flowify_doc(doc):
    out = {}
    for k, v in doc.items():
        if k in ("types", "operations", "errors", "binding", "provenance"):
            out[k] = flowify(v)
        elif k == "discovery":
            out[k] = flowify(v)
        else:
            out[k] = v
    return out


if __name__ == "__main__":
    sys.exit(main())
