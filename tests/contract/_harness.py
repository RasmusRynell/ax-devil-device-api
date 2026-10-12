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
    params = request.get("params") or {}
    if op.params is None:
        assert not params, f"{op.id} takes no params but example has {params}"
        return None
    return op.params.model_validate(params)


def _template_regex(template: str) -> tuple[re.Pattern[str], list[str]]:
    names: list[str] = []
    out = ""
    for literal, name, _, _ in string.Formatter().parse(template):
        out += re.escape(literal)
        if name:
            names.append(name)
            out += "([^/]+)"
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
        pattern, names = _template_regex(template)
        match = pattern.match(candidate)
        assert match, f"example path {given!r} does not match template {rel!r}"
        from urllib.parse import unquote

        values = {n: unquote(v) for n, v in zip(names, match.groups())}
        path = candidate
    body = (request.get("body") or {}).get("data") or {}
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


def check_result(op, result: Any) -> None:
    expected = op.result
    if expected is None:
        assert result is None
        return
    cls = get_origin(expected) or expected
    assert isinstance(result, cls), f"{op.id}: expected {expected}, got {type(result)}"
