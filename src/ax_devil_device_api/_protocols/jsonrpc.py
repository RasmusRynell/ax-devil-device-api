"""JSON-RPC-style CGI APIs.

Request:  POST <path> {"apiVersion": "M.m", "method": "...", "params": {...}}
Success:  {"apiVersion", "method", "data": {...}}
Error:    {"apiVersion", "method", "error": {"code": int, "message": str}}

Errors are usually returned with HTTP 200 but some APIs use 4xx/5xx, so the
body is always inspected before the status.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from ..errors import ApiError, NotSupported, ResponseFormatError
from .._http.types import AuthPolicy, JsonBody, Request, Response
from .base import (
    ApiVersion,
    CallFlow,
    Model,
    Operation,
    api_error,
    check_applicability,
    http_error,
    parse_result,
    register_binding,
    select_version,
)
from .state import DeviceState


VERSION_NOT_SUPPORTED = 2100
"""JSON-RPC error code for "API version not supported" in current Axis APIs."""


@dataclass(frozen=True)
class GetSupportedVersions:
    """Negotiate with ``getSupportedVersions``; versions are listed under ``data[key]``."""

    key: str = "apiVersions"
    auth: AuthPolicy = "required"


@dataclass(frozen=True)
class FixedVersion:
    """The API has no negotiation; always send this ``apiVersion``."""

    version: ApiVersion


@dataclass(frozen=True)
class NoVersion:
    """The API takes no ``apiVersion`` field at all."""


Negotiation = GetSupportedVersions | FixedVersion | NoVersion


@dataclass(frozen=True)
class JsonRpcBinding:
    """Wire binding of one JSON-RPC method."""

    method: str
    path: str
    negotiation: Negotiation = GetSupportedVersions()
    params_placement: Literal["params", "top_level"] = "params"
    """``top_level`` merges arguments into the envelope instead of ``params``."""
    params_field: str | None = None
    """For APIs whose ``params`` is an array or a free-form map: the one
    request field whose value is sent as the whole ``params``."""
    auth: AuthPolicy = "required"
    timeout: float | None = None


def _envelope(method: str, version: ApiVersion | None) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if version is not None:
        body["apiVersion"] = str(version)
    body["method"] = method
    return body


def _decode(op: Operation[Any], response: Response) -> dict[str, Any]:
    """Return the envelope of a successful response or raise the right error."""
    payload: Any = None
    if response.content:
        try:
            payload = json.loads(response.content)
        except ValueError:
            payload = None

    if isinstance(payload, dict) and "error" in payload:
        error = payload["error"]
        if isinstance(error, dict):
            code = error.get("code")
            message = str(error.get("message", ""))
        else:
            code, message = None, str(error)
        raise api_error(op, code, message, http_status=response.status, details=error)
    if response.status != 200:
        raise http_error(op, response)
    if not isinstance(payload, dict):
        raise ResponseFormatError(op.api.id, op.id, "response is not a JSON object")
    return payload


def _advertised(op: Operation[JsonRpcBinding], state: DeviceState) -> CallFlow[tuple[ApiVersion, ...]]:
    binding = op.binding
    negotiation = binding.negotiation
    assert isinstance(negotiation, GetSupportedVersions)
    cache_key = f"jsonrpc:{binding.path}"
    cached = state.advertised_versions(cache_key)
    if cached is not None:
        return cached
    token = state.versions_token(cache_key)
    response = yield Request(
        "POST",
        binding.path,
        body=JsonBody({"method": "getSupportedVersions"}),
        accept="application/json",
        auth=negotiation.auth,
        timeout=binding.timeout,
    )
    payload = _decode(op, response)
    data = payload.get("data")
    raw = data.get(negotiation.key) if isinstance(data, dict) else None
    if not isinstance(raw, list) or not all(isinstance(v, str) for v in raw):
        raise ResponseFormatError(op.api.id, op.id, f"getSupportedVersions returned no {negotiation.key} list")
    try:
        versions = tuple(ApiVersion.parse(v) for v in raw)
    except ValueError as error:
        raise ResponseFormatError(op.api.id, op.id, f"getSupportedVersions: {error}") from error
    state.set_advertised_versions(cache_key, versions, token)
    return versions


def _version(op: Operation[JsonRpcBinding], state: DeviceState) -> CallFlow[ApiVersion | None]:
    negotiation = op.binding.negotiation
    if isinstance(negotiation, NoVersion):
        return None
    if isinstance(negotiation, FixedVersion):
        return negotiation.version
    advertised = yield from _advertised(op, state)
    major = op.api.major
    if major is None:
        raise TypeError(f"{op.api.id}: JSON-RPC API with negotiation needs ApiInfo.major")
    version = select_version(advertised, major, op.api.known_versions)
    if version is None:
        offered = ", ".join(str(v) for v in advertised) or "none"
        raise NotSupported(op.api.id, op.id, f"device offers API versions {offered}, this client needs {major}.x")
    return version


def flow(op: Operation[JsonRpcBinding], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    binding = op.binding
    version = yield from _version(op, state)
    check_applicability(op, params, version)

    body = _envelope(binding.method, version)
    args = params.to_wire() if params is not None else {}
    if binding.params_field is not None:
        assert params is not None
        field = type(params).model_fields[binding.params_field]
        alias = field.serialization_alias or binding.params_field
        if alias in args:
            body["params"] = args[alias]
    elif binding.params_placement == "top_level":
        body.update(args)
    elif args:
        body["params"] = args

    response = yield Request(
        "POST",
        binding.path,
        body=JsonBody(body),
        accept="application/json",
        auth=binding.auth,
        timeout=binding.timeout,
    )
    try:
        payload = _decode(op, response)
    except (ApiError, NotSupported) as error:
        # Evidence that cached versions are stale (e.g. firmware changed):
        # the device rejected our version, or the endpoint vanished.
        if isinstance(binding.negotiation, GetSupportedVersions) and (
            response.status == 404 or (isinstance(error, ApiError) and error.code == VERSION_NOT_SUPPORTED)
        ):
            state.forget_advertised_versions(f"jsonrpc:{binding.path}")
        raise
    echoed = payload.get("method")
    if echoed is not None and echoed != binding.method:
        raise ResponseFormatError(op.api.id, op.id, f"response is for method {echoed!r}, expected {binding.method!r}")
    data = payload.get("data")
    if op.result is None:
        return None
    return parse_result(op, {} if data is None else data)


register_binding(JsonRpcBinding, flow)
