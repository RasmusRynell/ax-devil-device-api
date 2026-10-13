"""Device identity, discovery probes and API support checks (sans-IO).

Three probes describe what a device offers, and a fourth runs only for APIs that need it:

- classic API discovery (``apidiscovery.cgi`` ``getApiList``),
- Device Configuration discovery (``/config/discover``),
- the ``param.cgi`` ``Properties.API`` group (a property outside it is probed lazily, one ``param.cgi`` list per
  declared property, cached as ``properties:<name>``; a leading ``root.`` is stripped),
- installed ACAP applications (``applications/list.cgi``),
- the web services listed by the Entry service (``GetServices``).

Each probe either succeeds (its result is cached until ``refresh()``) or
fails (the error is reported and the probe is retried next time). A probe
failure never turns into "not supported". A property that was never queried
counts as unknown, a queried one that is absent as "no". An ``ApiError``
containing ``getting param in group`` means the property is absent ("no");
any other probe error is unknown.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .._http.types import RawBody, Request
from .._protocols.base import (
    AcapDiscovery,
    ApiDiscovery,
    ApiInfo,
    ApiVersion,
    CallFlow,
    DcaDiscovery,
    Family,
    Model,
    Operation,
    ParamDiscovery,
    ServiceDiscovery,
    http_error,
)
from .._protocols.cgi import CgiArg, CgiBinding, TextKv
from .._protocols.cgi import flow as cgi_flow
from .._protocols.jsonrpc import FixedVersion
from .._protocols.jsonrpc import flow as jsonrpc_flow
from .._protocols.soap import SoapBinding, build_envelope
from .._protocols.state import DeviceState
from ..apis import api_discovery as _api_discovery
from ..apis import basic_device_info as _basic_device_info
from ..errors import ApiError, DeviceError, ResponseFormatError

BASE_PROPERTY_GROUP = "Properties.API"
PROPERTY_SCOPE_PREFIX = "properties:"

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


class Support(str, Enum):  # noqa: UP042 (StrEnum would change str() and format())
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
    observed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

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
    applications: Mapping[str, str] | None = None
    """Installed ACAP applications: ``Name`` -> ``Version``. ``None`` if the probe failed or was not run."""
    services: Mapping[str, str] | None = None
    """Web services listed by the Entry service: namespace -> ``XAddr``. ``None`` if the probe failed or was not run."""
    property_groups: frozenset[str] = frozenset({"Properties.API"})
    """``param.cgi`` groups that were actually listed. A property outside them was never asked for."""

    @classmethod
    def from_probes(cls, values: Mapping[str, Any], errors: Mapping[str, str]) -> Capabilities:
        """Assemble from probe results keyed like ``PROBES`` (plus ``properties:<name>`` scope probes)."""
        properties = values.get("properties")
        groups = frozenset({BASE_PROPERTY_GROUP})
        extra = {k: v for k, v in values.items() if k.startswith(PROPERTY_SCOPE_PREFIX)}
        if properties is not None and extra:
            properties = dict(properties)
            for found in extra.values():
                properties.update(found)
            groups |= {k[len(PROPERTY_SCOPE_PREFIX):] for k in extra}
        return cls(
            classic_apis=values.get("classic_apis"),
            dca_apis=values.get("dca_apis"),
            properties=properties,
            property_groups=groups,
            errors=dict(errors),
            observed_at=datetime.now(UTC),
            applications=values.get("applications"),
            services=values.get("services"),
        )


# ---------------------------------------------------------------------------
# Internal operations used by the probes

_INTERNAL = ApiInfo(id="device", name="Device runtime", family=Family.JSONRPC, major=1, known_versions=(ApiVersion(1, 0),))
_PARAM_INFO = ApiInfo(id="parameter-management", name="Parameter management", family=Family.CGI)


class _ParamListRequest(Model):
    group: list[str]


# The probes reuse the generated operations (path, method, API info, error table) but read
# the raw reply: identity keeps every property the device returns, not only the modelled ones.
# API discovery is anonymous, so it neither negotiates nor demands credentials up front.
_GET_API_LIST = replace(
    _api_discovery.OPS.get_api_list,
    binding=replace(
        _api_discovery.OPS.get_api_list.binding, negotiation=FixedVersion(ApiVersion(1, 0)), auth="if_challenged"
    ),
    params=None,
    result=dict,
)
_GET_ALL_PROPERTIES = replace(_basic_device_info.OPS.get_all_properties, result=dict)
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
_APPLICATIONS_OP = Operation(_INTERNAL, "applications_list", object(), effect="read")
_ENTRY_NS = "http://www.axis.com/vapix/ws/entry"
_ENTRY_BINDING = SoapBinding(f"{_ENTRY_NS}/GetServices", "GetServices", _ENTRY_NS)
_SERVICES_OP = Operation(_INTERNAL, "entry_get_services", object(), effect="read")


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
    params = _ParamListRequest(group=[BASE_PROPERTY_GROUP])
    data = yield from cgi_flow(_LIST_PROPERTIES, params, state)
    return data


def property_scope_flow(name: str) -> Callable[[DeviceState], CallFlow[dict[str, str]]]:
    """Probe for one property (or group) outside ``Properties.API`` that an API's discovery names.

    A device without the property may answer with a ``getting param in group`` error; that is a
    definite "not there" and yields an empty result. Any other failure is raised.
    """

    def flow(state: DeviceState) -> CallFlow[dict[str, str]]:
        try:
            data = yield from cgi_flow(_LIST_PROPERTIES, _ParamListRequest(group=[name]), state)
        except ApiError as error:
            if "getting param in group" in f"{error.message} {error.details or ''}":
                return {}
            raise
        return data

    return flow


def applications_flow(state: DeviceState) -> CallFlow[dict[str, str]]:
    response = yield Request("POST", "/axis-cgi/applications/list.cgi", accept="text/xml")
    if not 200 <= response.status < 300:
        raise http_error(_APPLICATIONS_OP, response)
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as error:
        raise ResponseFormatError("applications", "list", "response is not valid XML") from error
    if root.get("result") not in (None, "ok"):
        raise ResponseFormatError("applications", "list", f"device answered result={root.get('result')!r}")
    return {
        name: app.get("Version", "")
        for app in root.iter()
        if app.tag.rpartition("}")[2] == "application" and (name := app.get("Name"))
    }


def services_flow(state: DeviceState) -> CallFlow[dict[str, str]]:
    """Entry service ``GetServices``: namespace -> ``XAddr`` of every service the device offers."""
    response = yield Request(
        "POST",
        _ENTRY_BINDING.path,
        body=RawBody(
            build_envelope(_ENTRY_BINDING, {"IncludeCapability": False}),
            f'application/soap+xml; charset=utf-8; action="{_ENTRY_BINDING.action}"',
        ),
        accept="application/soap+xml",
    )
    if not 200 <= response.status < 300:
        raise http_error(_SERVICES_OP, response)
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as error:
        raise ResponseFormatError("entry-service", "get_services", "response is not valid XML") from error
    found: dict[str, str] = {}
    for service in root.iter():
        if service.tag.rpartition("}")[2] != "Service":
            continue
        children = {c.tag.rpartition("}")[2]: (c.text or "").strip() for c in service}
        if children.get("Namespace"):
            found[children["Namespace"]] = children.get("XAddr", "")
    if not found:
        raise ResponseFormatError("entry-service", "get_services", "response lists no services")
    return found


PROBES = {
    "classic_apis": classic_apis_flow,
    "dca_apis": dca_apis_flow,
    "properties": properties_flow,
}

class _OptionalProbes(dict[str, Callable[[DeviceState], CallFlow[Any]]]):
    """``applications``, ``services``, and on demand ``properties:<name>`` (one per property outside ``Properties.API``)."""

    def __missing__(self, key: str) -> Callable[[DeviceState], CallFlow[Any]]:
        if key.startswith(PROPERTY_SCOPE_PREFIX):
            return property_scope_flow(key[len(PROPERTY_SCOPE_PREFIX):])
        raise KeyError(key)


OPTIONAL_PROBES = _OptionalProbes({"applications": applications_flow, "services": services_flow})
"""Probes that cost an extra (administrator) request and are only needed by some APIs.
``extra_probes(info)`` says which ones an API's discovery wants."""


def _normalized(name: str) -> str:
    return name.removeprefix("root.")


def _is_queried(name: str, groups: frozenset[str]) -> bool:
    name = _normalized(name)
    return any(name == g or name.startswith(g + ".") for g in groups)


def extra_probes(info: ApiInfo) -> tuple[str, ...]:
    """Names of the ``OPTIONAL_PROBES`` that ``info``'s discovery needs."""
    wanted = []
    if any(isinstance(m, AcapDiscovery) for m in info.discovery):
        wanted.append("applications")
    if any(isinstance(m, ServiceDiscovery) for m in info.discovery):
        wanted.append("services")
    for m in info.discovery:
        if isinstance(m, ParamDiscovery) and not _is_queried(m.name, frozenset({BASE_PROPERTY_GROUP})):
            wanted.append(PROPERTY_SCOPE_PREFIX + _normalized(m.name))
    return tuple(dict.fromkeys(wanted))


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
            name = _normalized(method.name)
            value = caps.properties.get(name)
            if value is not None and _param_matches(method, value):
                return SupportResult(Support.YES, f"parameter {name}={value}", observed_at=caps.observed_at)
            if value is None and not _is_queried(name, caps.property_groups):
                reason = caps.errors.get(PROPERTY_SCOPE_PREFIX + name, "probe not run")
                unknown.append(f"parameter {name} was not queried: {reason}")
        elif isinstance(method, AcapDiscovery):
            if caps.applications is None:
                unknown.append(f"installed applications probe failed: {caps.errors.get('applications', 'not run')}")
                continue
            for name, version in caps.applications.items():
                if name.casefold() == method.name.casefold():
                    return SupportResult(Support.YES, f"application {name} {version} is installed", observed_at=caps.observed_at)

        elif isinstance(method, ServiceDiscovery):
            if caps.services is None:
                unknown.append(f"entry service probe failed: {caps.errors.get('services', 'not run')}")
                continue
            if method.namespace in caps.services:
                return SupportResult(Support.YES, f"listed by the entry service as {method.namespace}", observed_at=caps.observed_at)

    if unknown:
        return SupportResult(Support.UNKNOWN, "discovery was incomplete", tuple(unknown), caps.observed_at)
    return SupportResult(Support.NO, f"{info.id} is not listed by the device's discovery", observed_at=caps.observed_at)


def _version_key(text: str) -> tuple[int, ...] | None:
    parts = text.strip().split(".")
    return tuple(int(p) for p in parts) if all(p.isdigit() for p in parts) else None


def _param_matches(method: ParamDiscovery, value: str) -> bool:
    if method.value is None:
        return True
    if method.compare == ">=":
        have, want = _version_key(value), _version_key(method.value)
        return have is not None and want is not None and have >= want
    return value == method.value


def probe_error(error: Exception) -> str:
    return f"{type(error).__name__}: {error}" if isinstance(error, DeviceError) else repr(error)
