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

from ..errors import ResponseFormatError
from .._http.types import AuthPolicy, JsonBody, Request, Response
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
    auth: AuthPolicy = "required"
    timeout: float | None = None

    @property
    def path_params(self) -> tuple[str, ...]:
        return tuple(name for _, name, _, _ in string.Formatter().parse(self.path) if name)


def _build(op: Operation[DcaBinding], params: Model | None) -> Request:
    binding = op.binding
    wire = params.to_wire() if params is not None else {}
    path_values: dict[str, str] = {}
    for name in binding.path_params:
        value = getattr(params, name, None) if params is not None else None
        if value is None:
            raise TypeError(f"{op.api.id}.{op.id}: missing path parameter {name!r}")
        text = str(value)
        if text in ("", ".", ".."):
            # These would address a different resource after URL normalization.
            raise ValueError(f"{op.api.id}.{op.id}: {name}={text!r} is not a valid path segment")
        path_values[name] = quote(text, safe="")
    path = binding.path.format(**path_values)

    body: JsonBody | None = None
    if binding.body == "object":
        assert params is not None
        excluded = {_alias(params, name) for name in binding.path_params}
        body = JsonBody({"data": {k: v for k, v in wire.items() if k not in excluded}})
    elif binding.body == "value":
        assert params is not None and binding.body_field is not None
        body = JsonBody({"data": wire.get(_alias(params, binding.body_field))})

    return Request(binding.method, path, body=body, accept="application/json", auth=binding.auth, timeout=binding.timeout)


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
    if not isinstance(payload, dict) or payload.get("status") != "success":
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
