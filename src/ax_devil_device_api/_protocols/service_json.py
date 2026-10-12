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
from typing import Any

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
    return parse_result(op, data)


register_binding(ServiceJsonBinding, flow)
