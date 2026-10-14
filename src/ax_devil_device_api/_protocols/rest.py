"""Plain REST/JSON APIs: method + path + JSON body, bare JSON response.

Unlike Device Configuration there is no ``{"data": ...}`` envelope. Failures
are signalled by the HTTP status. A status documented in the operation's (or
API's) ``errors`` table, keyed by the integer status, becomes an ``ApiError``
carrying the response text; other failures use the generic HTTP errors
(401 -> ``AuthError``, 403, 404, 503, ...).
"""

from __future__ import annotations

import json
import string
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal
from urllib.parse import quote

from .._http.types import AuthPolicy, JsonBody, Request, Response, check_path_param
from ..errors import ResponseFormatError
from .base import CallFlow, Model, Operation, api_error, check_applicability, http_error, parse_result, register_binding
from .dca import _alias, _field_for
from .state import DeviceState

RestMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


@dataclass(frozen=True)
class RestBinding:
    """Wire binding of one REST operation.

    ``path`` is the full path template; ``{name}`` placeholders are filled from
    the params field of that Python (or wire) name and percent-encoded.
    ``query`` lists ``(field, wire_name)`` pairs sent as query arguments when set.
    ``body``: ``none`` sends no body; ``object`` sends all set params except
    path and query fields as a JSON object (``{}`` if none); ``value`` sends the
    value of the single field ``body_field`` as the whole JSON body.
    """

    method: RestMethod
    path: str
    body: Literal["none", "object", "value"] = "none"
    body_field: str | None = None
    query: tuple[tuple[str, str], ...] = ()
    auth: AuthPolicy = "required"
    timeout: float | None = None
    sensitive: bool = False
    """The ``value`` body is a secret (a masked or secret-named field): debug hooks never see it."""

    @property
    def path_params(self) -> tuple[str, ...]:
        return tuple(name for _, name, _, _ in string.Formatter().parse(self.path) if name)


def _scalar(value: Any) -> str:
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _build(op: Operation[RestBinding], params: Model | None) -> Request:
    binding = op.binding
    wire = params.to_wire() if params is not None else {}
    path_values: dict[str, str] = {}
    consumed: set[str] = set()
    for name in binding.path_params:
        field = _field_for(params, name) if params is not None else None
        value = getattr(params, field, None) if field is not None and params is not None else None
        if field is None or value is None:
            raise TypeError(f"{op.api.id}.{op.id}: missing path parameter {name!r}")
        if isinstance(value, Enum):
            value = value.value
        text = str(value)
        check_path_param(f"{op.api.id}.{op.id}", name, text)
        if text in ("", ".", ".."):
            raise ValueError(f"{op.api.id}.{op.id}: {name}={text!r} is not a valid path segment")
        path_values[name] = quote(text, safe="")
        assert params is not None
        consumed.add(_alias(params, field))
    path = binding.path.format(**path_values)

    query: list[tuple[str, str]] = []
    for field_name, wire_name in binding.query:
        if params is None or field_name not in params.model_fields_set:
            continue
        value = getattr(params, field_name)
        if value is None:
            continue
        consumed.add(_alias(params, field_name))
        values = value if isinstance(value, (list, tuple)) else [value]
        query.extend((wire_name, _scalar(v)) for v in values)

    body: JsonBody | None = None
    if binding.body == "object":
        body = JsonBody({k: v for k, v in wire.items() if k not in consumed})
    elif binding.body == "value":
        assert params is not None and binding.body_field is not None
        field = _field_for(params, binding.body_field) or binding.body_field
        body = JsonBody(wire.get(_alias(params, field)), sensitive=binding.sensitive)

    return Request(
        binding.method, path, query=tuple(query), body=body, accept="application/json", auth=binding.auth, timeout=binding.timeout
    )


def _decode(op: Operation[RestBinding], response: Response) -> Any:
    status = response.status
    if not 200 <= status < 300:
        if status not in (401, 403) and op.error_code(status) is not None:
            raise api_error(op, status, response.excerpt(), http_status=status, details=response.safe_text)
        raise http_error(op, response, documented=True)
    if not response.content.strip():
        return None
    try:
        return json.loads(response.content)
    except ValueError as error:
        raise ResponseFormatError(op.api.id, op.id, "response is not valid JSON") from error


def flow(op: Operation[RestBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    check_applicability(op, params, None)
    response = yield _build(op, params)
    data = _decode(op, response)
    if op.result is None:
        return None
    return parse_result(op, data)


register_binding(RestBinding, flow)
