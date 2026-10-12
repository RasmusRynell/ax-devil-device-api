"""Device identity, discovery probes and API support checks (sans-IO).

Three probes describe what a device offers:

- classic API discovery (``apidiscovery.cgi`` ``getApiList``),
- Device Configuration discovery (``/config/discover``),
- the ``param.cgi`` ``Properties.API`` group.

Each probe either succeeds (its result is cached until ``refresh()``) or
fails (the error is reported and the probe is retried next time). A probe
failure never turns into "not supported".
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from ..errors import DeviceError, ResponseFormatError
from .._http.types import Request
from .._protocols.base import (
    ApiDiscovery,
    ApiInfo,
    ApiVersion,
    CallFlow,
    DcaDiscovery,
    Family,
    Model,
    Operation,
    ParamDiscovery,
    http_error,
)
from .._protocols.cgi import CgiArg, CgiBinding, TextKv
from .._protocols.jsonrpc import FixedVersion, GetSupportedVersions, JsonRpcBinding
from .._protocols.jsonrpc import flow as jsonrpc_flow
from .._protocols.cgi import flow as cgi_flow
from .._protocols.state import DeviceState

# ---------------------------------------------------------------------------
# Public results


@dataclass(frozen=True)
class DeviceIdentity:
    """Who the device is, from Basic device information (``getAllProperties``)."""

    model: str | None
    """Short product name, e.g. ``AXIS Q1656``."""
    product_number: str | None
    full_name: str | None
    serial_number: str | None
    firmware_version: str | None
    hardware_id: str | None
    architecture: str | None
    properties: Mapping[str, str] = field(repr=False)
    """Every property the device returned."""


class Support(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SupportResult:
    """Answer of ``Device.supports``. Truthy only for ``Support.YES``."""

    status: Support
    reason: str
    errors: tuple[str, ...] = ()
    """Probe failures that made the answer ``UNKNOWN``."""
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __bool__(self) -> bool:
        return self.status is Support.YES


@dataclass(frozen=True)
class Capabilities:
    """Everything the discovery probes returned. ``None`` means that probe failed."""

    classic_apis: Mapping[str, str] | None
    """API id -> version, from classic API discovery."""
    dca_apis: Mapping[str, frozenset[str]] | None
    """Device Configuration API name -> path versions (``v1``, ``v2beta``)."""
    properties: Mapping[str, str] | None
    """``Properties.API.*`` parameters (``root.`` removed)."""
    errors: Mapping[str, str]
    """Probe name -> error, for probes that failed."""
    observed_at: datetime


# ---------------------------------------------------------------------------
# Internal operations used by the probes

_INTERNAL = ApiInfo(id="device", name="Device runtime", family=Family.JSONRPC, major=1, known_versions=(ApiVersion(1, 0),))
_CLASSIC_INFO = ApiInfo(id="api-discovery", name="API discovery", family=Family.JSONRPC, major=1, known_versions=(ApiVersion(1, 0),))
_BASIC_INFO = ApiInfo(id="basic-device-info", name="Basic device information", family=Family.JSONRPC, major=1, known_versions=(ApiVersion(1, 0),))
_PARAM_INFO = ApiInfo(id="parameter-management", name="Parameter management", family=Family.CGI)


class _ParamListRequest(Model):
    group: list[str]


_GET_API_LIST = Operation(
    _CLASSIC_INFO,
    "get_api_list",
    JsonRpcBinding("getApiList", "/axis-cgi/apidiscovery.cgi", negotiation=FixedVersion(ApiVersion(1, 0)), auth="if_challenged"),
    result=dict,
    effect="read",
)
_GET_ALL_PROPERTIES = Operation(
    _BASIC_INFO,
    "get_all_properties",
    JsonRpcBinding(
        "getAllProperties",
        "/axis-cgi/basicdeviceinfo.cgi",
        negotiation=GetSupportedVersions(key="apiVersions"),
    ),
    result=dict,
    effect="read",
)
_LIST_PROPERTIES = Operation(
    _PARAM_INFO,
    "list",
    CgiBinding(
        "/axis-cgi/param.cgi",
        fixed_query=(("action", "list"),),
        args=(CgiArg("group", style="csv"),),
        reply=TextKv(strip_prefix="root."),
    ),
    params=_ParamListRequest,
    result=dict[str, str],
    effect="read",
)
_DISCOVER_OP = Operation(_INTERNAL, "config_discover", object(), effect="read")


# ---------------------------------------------------------------------------
# Probe flows


def identity_flow(state: DeviceState) -> CallFlow[DeviceIdentity]:
    data = yield from jsonrpc_flow(_GET_ALL_PROPERTIES, None, state)
    props = data.get("propertyList") if isinstance(data, dict) else None
    if not isinstance(props, dict):
        raise ResponseFormatError("basic-device-info", "get_all_properties", "response has no propertyList object")
    props = {str(k): str(v) for k, v in props.items()}
    return DeviceIdentity(
        model=props.get("ProdShortName"),
        product_number=props.get("ProdNbr"),
        full_name=props.get("ProdFullName"),
        serial_number=props.get("SerialNumber"),
        firmware_version=props.get("Version"),
        hardware_id=props.get("HardwareID"),
        architecture=props.get("Architecture"),
        properties=props,
    )


def classic_apis_flow(state: DeviceState) -> CallFlow[dict[str, str]]:
    data = yield from jsonrpc_flow(_GET_API_LIST, None, state)
    entries = data.get("apiList") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise ResponseFormatError("api-discovery", "get_api_list", "response has no apiList array")
    return {
        str(entry["id"]): str(entry.get("version", ""))
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }


def dca_apis_flow(state: DeviceState) -> CallFlow[dict[str, frozenset[str]]]:
    response = yield Request("GET", "/config/discover", accept="application/json")
    if not 200 <= response.status < 300:
        raise http_error(_DISCOVER_OP, response)
    try:
        payload: Any = json.loads(response.content)
    except ValueError as error:
        raise ResponseFormatError("device", "config_discover", "response is not valid JSON") from error
    apis = payload.get("apis") if isinstance(payload, dict) else None
    if not isinstance(apis, dict):
        raise ResponseFormatError("device", "config_discover", "response has no apis object")
    return {
        str(name): frozenset(str(v) for v in versions)
        for name, versions in apis.items()
        if isinstance(versions, dict)
    }


def properties_flow(state: DeviceState) -> CallFlow[dict[str, str]]:
    params = _ParamListRequest(group=["Properties.API"])
    data = yield from cgi_flow(_LIST_PROPERTIES, params, state)
    return data


PROBES = {
    "classic_apis": classic_apis_flow,
    "dca_apis": dca_apis_flow,
    "properties": properties_flow,
}


# ---------------------------------------------------------------------------
# Support decision (pure)


def decide_support(info: ApiInfo, caps: Capabilities) -> SupportResult:
    """Answer whether ``info`` is supported, from probe results alone."""
    if not info.discovery:
        return SupportResult(Support.UNKNOWN, f"{info.id} declares no discovery method", observed_at=caps.observed_at)

    unknown: list[str] = []
    for method in info.discovery:
        if isinstance(method, ApiDiscovery):
            if caps.classic_apis is None:
                unknown.append(f"classic API discovery failed: {caps.errors.get('classic_apis')}")
                continue
            version = caps.classic_apis.get(method.id)
            if version is not None:
                if info.major is not None and not version.startswith(f"{info.major}."):
                    return SupportResult(
                        Support.NO, f"device has {method.id} version {version}, this client speaks {info.major}.x",
                        observed_at=caps.observed_at,
                    )
                return SupportResult(Support.YES, f"listed by API discovery as {method.id} {version}", observed_at=caps.observed_at)
        elif isinstance(method, DcaDiscovery):
            if caps.dca_apis is None:
                unknown.append(f"Device Configuration discovery failed: {caps.errors.get('dca_apis')}")
                continue
            if method.version in caps.dca_apis.get(method.api, frozenset()):
                return SupportResult(Support.YES, f"listed by /config/discover as {method.api} {method.version}", observed_at=caps.observed_at)
        elif isinstance(method, ParamDiscovery):
            if caps.properties is None:
                unknown.append(f"parameter probe failed: {caps.errors.get('properties')}")
                continue
            value = caps.properties.get(method.name)
            if value is not None and (method.value is None or value == method.value):
                return SupportResult(Support.YES, f"parameter {method.name}={value}", observed_at=caps.observed_at)

    if unknown:
        return SupportResult(Support.UNKNOWN, "discovery was incomplete", tuple(unknown), caps.observed_at)
    return SupportResult(Support.NO, f"{info.id} is not listed by the device's discovery", observed_at=caps.observed_at)


def probe_error(error: Exception) -> str:
    return f"{type(error).__name__}: {error}" if isinstance(error, DeviceError) else repr(error)
