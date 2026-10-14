"""Device Configuration REST APIs (``/config/rest/<api>/<version>/...``).

Request body (set/add/actions): {"data": <value>}
Success:                        {"status": "success", "data": <value>}
Error:                          {"status": "error", "error": {"code": int, "message": str}}

Errors come with a real HTTP error status, but the body is inspected first so
the device's code and message are kept.
"""

from __future__ import annotations

import json
import string
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import quote

from .._http.types import AuthPolicy, JsonBody, Request, Response, check_path_param
from ..errors import ResponseFormatError
from .base import CallFlow, Model, Operation, api_error, check_applicability, http_error, parse_result, register_binding
from .state import DeviceState

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


@dataclass(frozen=True)
class DcaBinding:
    """Wire binding of one Device Configuration operation.

    ``path`` is the full path template; ``{name}`` placeholders are filled
    from the params fields of the same Python name and percent-encoded.
    ``body`` decides what goes in ``{"data": ...}``:

    - ``none``: no body.
    - ``object``: all set params except the path parameters, as an object.
    - ``value``: the value of the single field ``body_field`` (setting one property).
    """

    method: HttpMethod
    path: str
    body: Literal["none", "object", "value"] = "none"
    body_field: str | None = None
    key_styles: tuple[tuple[str, Literal["segment", "dots_to_slashes", "path"]], ...] = ()
    """Per placeholder: ``dots_to_slashes`` writes a dotted key as nested path segments
    (``com.axis.topic`` -> ``com/axis/topic``); ``path`` keeps the ``/`` of a nested path
    (``a/b`` stays two segments); the default is one encoded segment. Empty, ``.`` and ``..``
    segments are rejected in every style."""
    auth: AuthPolicy = "required"
    timeout: float | None = None
    sensitive: bool = False
    """The ``value`` body is a secret (a masked or secret-named field): debug hooks never see it."""

    @property
    def path_params(self) -> tuple[str, ...]:
        return tuple(name for _, name, _, _ in string.Formatter().parse(self.path) if name)


def _build(op: Operation[DcaBinding], params: Model | None) -> Request:
    binding = op.binding
    wire = params.to_wire() if params is not None else {}
    path_values: dict[str, str] = {}
    for name in binding.path_params:
        field = _field_for(params, name) if params is not None else None
        value = getattr(params, field, None) if field is not None else None
        if value is None:
            raise TypeError(f"{op.api.id}.{op.id}: missing path parameter {name!r}")
        text = str(value)
        style = dict(binding.key_styles).get(name)
        check_path_param(f"{op.api.id}.{op.id}", name, text, multi_segment=style == "path")
        segments = text.split(".") if style == "dots_to_slashes" else text.split("/") if style == "path" else [text]
        for segment in segments:
            if segment in ("", ".", ".."):
                # These would address a different resource after URL normalization.
                raise ValueError(f"{op.api.id}.{op.id}: {name}={text!r} is not a valid path segment")
        path_values[name] = "/".join(quote(segment, safe="") for segment in segments)
    path = binding.path.format(**path_values)

    body: JsonBody | None = None
    if binding.body == "object":
        # Actions without arguments still send an empty object: {"data": {}}.
        excluded = (
            {_alias(params, f) for f in (_field_for(params, n) for n in binding.path_params) if f is not None}
            if params is not None
            else set()
        )
        body = JsonBody({"data": {k: v for k, v in wire.items() if k not in excluded}})
    elif binding.body == "value":
        assert params is not None and binding.body_field is not None
        field = _field_for(params, binding.body_field) or binding.body_field
        body = JsonBody({"data": wire.get(_alias(params, field))}, sensitive=binding.sensitive)

    return Request(binding.method, path, body=body, accept="application/json", auth=binding.auth, timeout=binding.timeout)


def _field_for(params: Model | type[Model], placeholder: str) -> str | None:
    """The params field a path placeholder refers to, by Python name or wire name."""
    fields = (params if isinstance(params, type) else type(params)).model_fields
    if placeholder in fields:
        return placeholder
    for name, info in fields.items():
        if placeholder in (info.serialization_alias, info.validation_alias, info.alias):
            return name
    return None


def _alias(params: Model, name: str) -> str:
    info = type(params).model_fields[name]
    alias = info.serialization_alias or info.alias
    return alias if isinstance(alias, str) else name


def _decode(op: Operation[DcaBinding], response: Response) -> Any:
    payload: Any = None
    if response.content:
        try:
            payload = json.loads(response.content)
        except ValueError:
            payload = None

    if isinstance(payload, dict) and payload.get("status") == "error":
        error = payload.get("error")
        code = error.get("code") if isinstance(error, dict) else None
        message = str(error.get("message", "")) if isinstance(error, dict) else str(error)
        raise api_error(op, code, message, http_status=response.status, details=error)
    if not 200 <= response.status < 300:
        raise http_error(op, response)
    if not response.content:
        return None
    # Some documented responses omit "status" on success; a 2xx with "data" is accepted.
    if not isinstance(payload, dict) or payload.get("status", "success" if "data" in payload else None) != "success":
        raise ResponseFormatError(op.api.id, op.id, "response is not a Device Configuration success envelope")
    return payload.get("data")


def flow(op: Operation[DcaBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    check_applicability(op, params, None)
    response = yield _build(op, params)
    data = _decode(op, response)
    if op.result is None:
        return None
    return parse_result(op, data)


register_binding(DcaBinding, flow)
