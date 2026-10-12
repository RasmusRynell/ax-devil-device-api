"""Axis service APIs spoken as JSON (``POST /vapix/<service>``).

Request:  POST <path> {"<prefix>:<Operation>": {...params}}
Success:  the bare message object (no envelope); an empty body means ``{}``
Error:    {"Fault": "env:Sender", "FaultCode": "ter:InvalidArgs",
           "FaultSubCode": "ter:Foo" | null, "FaultReason": str, "FaultMsg": str | null}

Faults normally come with HTTP 400/500, so the body is inspected before the
status. The error code is ``FaultSubCode`` when present, else ``FaultCode``
(both strings such as ``axast:DeviceNotCalibrated``).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

from ..errors import ResponseFormatError
from .._http.types import AuthPolicy, JsonBody, Request, Response
from .base import CallFlow, Model, Operation, api_error, check_applicability, http_error, parse_result, register_binding
from .state import DeviceState


@dataclass(frozen=True)
class ServiceJsonBinding:
    """Wire binding of one service operation."""

    path: str
    """Service endpoint, e.g. ``/vapix/axast``."""
    operation: str
    """Qualified operation name used as the single body key, e.g. ``axast:PerformSpeakerTest``."""
    auth: AuthPolicy = "required"
    timeout: float | None = None


def fault_of(payload: Any) -> dict[str, Any] | None:
    """The fault object if ``payload`` is a service fault, else ``None``."""
    if isinstance(payload, dict) and "Fault" in payload and ("FaultCode" in payload or "FaultSubCode" in payload):
        return payload
    return None


def _decode(op: Operation[ServiceJsonBinding], response: Response) -> Any:
    payload: Any = None
    if response.content:
        try:
            payload = json.loads(response.content)
        except ValueError:
            payload = None

    fault = fault_of(payload)
    if fault is not None:
        code = fault.get("FaultSubCode") or fault.get("FaultCode")
        message = fault.get("FaultMsg") or fault.get("FaultReason") or str(fault.get("Fault", ""))
        raise api_error(op, code, str(message), http_status=response.status, details=fault)
    if not 200 <= response.status < 300:
        raise http_error(op, response)
    if not response.content.strip():
        return {}
    if not isinstance(payload, dict):
        raise ResponseFormatError(op.api.id, op.id, "response is not a JSON object")
    return payload


def _kind_matches(tp: Any, value: Any) -> bool:
    origin = get_origin(tp) or tp
    if origin is Annotated:
        return _kind_matches(get_args(tp)[0], value)
    if origin in (Union, UnionType):
        return any(_kind_matches(a, value) for a in get_args(tp))
    if origin is Any:
        return True
    if isinstance(origin, type):
        if origin is bool:
            return isinstance(value, bool)
        if origin in (int, float):
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if issubclass(origin, Model):
            return isinstance(value, dict)
        return isinstance(value, origin)
    return True


def _normalize(tp: Any, value: Any) -> Any:
    """Adapt a response to quirks of Axis JSON services, following the declared result type.

    - A single-element list serialized as a bare scalar/object is wrapped into a list.
    - A JSON number where a string is declared becomes a string (booleans are left alone).
    Everything else is returned unchanged; validation reports real mismatches.
    """
    origin = get_origin(tp)
    if origin is Annotated:
        return _normalize(get_args(tp)[0], value)
    if origin in (Union, UnionType):
        if value is None:
            return value
        args = [a for a in get_args(tp) if a is not type(None)]
        matching = [a for a in args if _kind_matches(a, value)]
        if matching:
            return _normalize(matching[0], value)
        for arg in args:
            changed = _normalize(arg, value)
            if changed is not value:
                return changed
        return value
    if origin in (list, set, frozenset, tuple):
        inner = (get_args(tp) or (Any,))[0]
        if value is None:
            return value
        items = value if isinstance(value, list) else [value]
        return [_normalize(inner, item) for item in items]
    if origin is dict:
        args = get_args(tp)
        if isinstance(value, dict) and len(args) == 2:
            return {k: _normalize(args[1], v) for k, v in value.items()}
        return value
    if tp is str:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
        return value
    if isinstance(tp, type) and issubclass(tp, Model) and isinstance(value, dict):
        names = tp._wire_to_field()
        out: dict[str, Any] = {}
        for key, item in value.items():
            field = names.get(key) if isinstance(key, str) else None
            out[key] = _normalize(tp.model_fields[field].annotation, item) if field else item
        return out
    return value


def flow(op: Operation[ServiceJsonBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    binding = op.binding
    check_applicability(op, params, None)
    args = params.to_wire() if params is not None else {}
    response = yield Request(
        "POST",
        binding.path,
        body=JsonBody({binding.operation: args}),
        accept="application/json",
        auth=binding.auth,
        timeout=binding.timeout,
    )
    data = _decode(op, response)
    if op.result is None:
        return None
    return parse_result(op, _normalize(op.result, data))


register_binding(ServiceJsonBinding, flow)
