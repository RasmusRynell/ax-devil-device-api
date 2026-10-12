"""Helpers for the spec-example contract tests: request building, fake device, comparisons."""

from __future__ import annotations

import json
import re
import string
from dataclasses import dataclass, field
from typing import Any, get_origin
from urllib.parse import parse_qsl

import httpx


@dataclass
class Sent:
    method: str
    path: str
    query: dict[str, str]
    json: Any
    form: dict[str, str] | None


@dataclass
class Fake:
    """A transport that records the operation's request and answers with the documented response."""

    handler: Any
    calls: list[Sent] = field(default_factory=list)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        ctype = request.headers.get("content-type", "")
        body: Any = None
        form = None
        if request.content:
            if "json" in ctype:
                body = json.loads(request.content)
            elif "x-www-form-urlencoded" in ctype:
                form = dict(parse_qsl(request.content.decode(), keep_blank_values=True))
        sent = Sent(request.method, request.url.path, dict(request.url.params.items()), body, form)
        response = self.handler(sent)
        if response is None:
            return httpx.Response(404, text="unexpected request")
        self.calls.append(sent)
        return response


# -- request model construction ------------------------------------------------


def build_jsonrpc(op, request: dict) -> Any:
    params = request.get("params")
    field = getattr(op.binding, "params_field", None)
    if field is not None and op.params is not None:
        # Array or free-form params: the whole value is one wrapped field.
        info = op.params.model_fields[field]
        return op.params.model_validate({info.serialization_alias or field: params})
    params = params or {}
    if op.params is None:
        assert not params, f"{op.id} takes no params but example has {params}"
        return None
    return op.params.model_validate(params)


def _template_regex(template: str, multi: frozenset[str] = frozenset()) -> tuple[re.Pattern[str], list[str]]:
    """Regex for a path template. Placeholders in ``multi`` may span several segments."""
    names: list[str] = []
    out = ""
    for literal, name, _, _ in string.Formatter().parse(template):
        out += re.escape(literal)
        if name:
            names.append(name)
            out += "(.+)" if name in multi else "([^/]+)"
    return re.compile(out + "$"), names


def dca_relative(spec_root: str, binding_path: str) -> str:
    return binding_path[len(spec_root):] if binding_path.startswith(spec_root) else binding_path


def build_dca(op, request: dict, root: str) -> tuple[Any, str]:
    """Return (model, expected absolute path)."""
    template = op.binding.path
    rel = dca_relative(root, template)
    given = request.get("path")
    values: dict[str, str] = {}
    if given is None:
        path = template
    else:
        candidate = given if given.startswith(root) else root + given
        styles = dict(getattr(op.binding, "key_styles", ()) or ())
        dotted = frozenset(n for n, s in styles.items() if s == "dots_to_slashes")
        pattern, names = _template_regex(template, dotted)
        match = pattern.match(candidate)
        assert match, f"example path {given!r} does not match template {rel!r}"
        from urllib.parse import unquote

        values = {}
        for n, v in zip(names, match.groups()):
            # dots_to_slashes: the key is written as nested segments, the model holds the dotted key.
            values[n] = ".".join(unquote(s) for s in v.split("/")) if n in dotted else unquote(v)
        path = candidate
    raw_body = request.get("body")
    # {"data": <value>}: the value may be any JSON type (string, number, boolean, array, null).
    body = raw_body.get("data") if isinstance(raw_body, dict) and "data" in raw_body else {}
    if op.binding.body == "value" and op.binding.body_field:
        # Property setters: the whole {"data": value} is one field.
        from ax_devil_device_api._protocols.dca import _field_for

        name = _field_for(op.params, op.binding.body_field) if op.params else None
        field = op.params.model_fields[name] if op.params and name else None
        wire_name = (field.serialization_alias if field else None) or op.binding.body_field
        data = {**values, wire_name: body}
    else:
        data = {**values, **(body if isinstance(body, dict) else {})}
    if op.params is None:
        assert not data
        return None, path
    return op.params.model_validate(data), path


def build_cgi(op, request: dict) -> tuple[Any, dict[str, str]]:
    """Return (model, expected full argument dict including fixed ones)."""
    binding = op.binding
    fixed = dict(binding.fixed_query)
    args = dict(request.get("query") or request.get("form") or {})
    args = {str(k): ("true" if v is True else "false" if v is False else str(v)) for k, v in args.items()}
    for key, value in fixed.items():
        assert args.pop(key, value) == value, f"example changes fixed argument {key}"
    expected = {**fixed, **args}
    if op.params is None:
        return None, expected
    data: dict[str, Any] = {}
    remaining = dict(args)
    spread = None
    for arg in binding.args:
        if arg.style == "spread":
            spread = arg
            continue
        wire = arg.wire or arg.field
        if wire not in remaining:
            continue
        value = remaining.pop(wire)
        if arg.style == "csv":
            data[arg.field] = value.split(",")
        elif arg.style == "axis_bool":
            assert value in ("yes", "no"), value
            data[arg.field] = value == "yes"
        else:
            data[arg.field] = value
    if remaining:
        assert spread is not None, f"unknown arguments {sorted(remaining)}"
        data[spread.field] = remaining
    return op.params.model_validate(data), expected


# -- result checking ------------------------------------------------------------


def check_response_only(op, family: str, response: dict) -> None:
    """Validate a documented response against the result model without building a request."""
    from ax_devil_device_api._protocols.base import parse_result

    if family == "jsonrpc":
        data = response.get("data", {})
    elif family == "dca":
        body = response.get("body")
        data = body.get("data") if isinstance(body, dict) else None
    else:
        raise AssertionError(f"{family}: response-only validation is not supported")
    check_result(op, parse_result(op, data) if op.result is not None else None)


def check_result(op, result: Any) -> None:
    expected = op.result
    if expected is None:
        assert result is None
        return
    cls = get_origin(expected) or expected
    if isinstance(cls, type):
        assert isinstance(result, cls), f"{op.id}: expected {expected}, got {type(result)}"
    else:
        # Literal, Annotated and union aliases: the value must validate as the result type.
        from ax_devil_device_api._protocols.base import RESPONSE_CONTEXT, adapter

        adapter(expected).validate_python(result, context={RESPONSE_CONTEXT: True})
