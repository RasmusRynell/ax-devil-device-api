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

import re
import xml.etree.ElementTree as ET
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .._http.types import RawBody, Request, loads_json
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
from .._protocols.xmlmap import parse_xml
from ..apis import api_discovery as _api_discovery
from ..apis import basic_device_info as _basic_device_info
from ..errors import ApiError, AuthError, DeviceError, PoolTimeout, ResponseFormatError, TransportError

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
    firmware: str | None = None
    """Firmware (AXIS OS) version from the device identity; ``None`` if it is not known (not fetched, or the request failed)."""
    applications_problems: tuple[str, ...] = ()
    """Entries of the applications list that had no usable name; an absent application is then unknown."""
    services_problems: tuple[str, ...] = ()
    """Entries of the entry-service list that had no namespace; an absent service is then unknown."""
    classic_versions: Mapping[str, Advertised] | None = None
    """Per classic API id: every advertised version and the malformed entries seen (``classic_apis`` shows the versions
    joined as text). ``None`` if the probe failed."""
    dca_malformed: Mapping[str, str] = field(default_factory=dict)
    """``/config/discover`` APIs listed in the wrong shape: name -> why. Their support is unknown, not absent."""

    @classmethod
    def from_probes(cls, values: Mapping[str, Any], errors: Mapping[str, str]) -> Capabilities:
        """Assemble from probe results keyed like ``PROBES`` (plus ``properties:<name>`` scope probes)."""
        properties = values.get("properties")
        groups = frozenset({BASE_PROPERTY_GROUP}) if properties is not None else frozenset()
        extra = {k: v for k, v in values.items() if k.startswith(PROPERTY_SCOPE_PREFIX)}
        if extra:
            # Each scope is merged on its own: a failed base probe must not discard a scope that worked.
            properties = dict(properties or {})
            for found in extra.values():
                properties.update(found)
            groups |= {k[len(PROPERTY_SCOPE_PREFIX):] for k in extra}
        errors = dict(errors)
        classic = values.get("classic_apis")
        dca = values.get("dca_apis")
        classic_versions: Mapping[str, Advertised] | None = None
        if isinstance(classic, ClassicListing):
            classic_versions = classic.entries
            for name, entry in classic.entries.items():
                if entry.problems:  # recorded with the probe errors; the probe itself worked
                    errors[f"classic_apis[{name}]"] = "; ".join(entry.problems)
            classic = {name: ", ".join(entry.versions) for name, entry in classic.entries.items() if entry.versions}
        malformed: Mapping[str, str] = {}
        if isinstance(dca, DcaListing):
            malformed = dict(dca.malformed)
            for name, reason in malformed.items():
                errors[f"dca_apis[{name}]"] = reason
            dca = dict(dca.apis)
        applications = values.get("applications")
        applications_problems: tuple[str, ...] = ()
        if isinstance(applications, NamedListing):
            applications_problems = applications.problems
            if applications_problems:
                errors["applications"] = "; ".join(applications_problems)
            applications = dict(applications.items)
        services = values.get("services")
        services_problems: tuple[str, ...] = ()
        if isinstance(services, NamedListing):
            services_problems = services.problems
            if services_problems:
                errors["services"] = "; ".join(services_problems)
            services = dict(services.items)
        return cls(
            applications_problems=applications_problems,
            services_problems=services_problems,
            classic_apis=classic,
            dca_apis=dca,
            classic_versions=classic_versions,
            dca_malformed=malformed,
            properties=properties,
            property_groups=groups,
            errors=errors,
            observed_at=datetime.now(UTC),
            applications=applications,
            services=services,
            firmware=values.get("firmware"),
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
    # Every key and value must be text: str() would turn null into "None" and an object into its repr, and that would be
    # cached as the firmware. A malformed answer raises and caches nothing (the previous identity stays).
    bad = [key for key, value in props.items() if not isinstance(key, str) or not isinstance(value, str)]
    if bad:
        raise ResponseFormatError(
            "basic-device-info", "get_all_properties", f"propertyList values must be text; wrong for: {', '.join(map(repr, bad))}"
        )
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


def classic_apis_flow(state: DeviceState) -> CallFlow[ClassicListing]:
    data = yield from jsonrpc_flow(_GET_API_LIST, None, state)
    entries = data.get("apiList") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise ResponseFormatError("api-discovery", "get_api_list", "response has no apiList array")
    versions: dict[str, list[str]] = {}
    problems: dict[str, list[str]] = {}
    for index, entry in enumerate(entries):
        ident = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(entry, dict) or not isinstance(ident, str) or not ident:
            problems.setdefault(f"<entry {index}>", []).append(malformed_reason("apiList", index, entry, "an object with an id"))
            continue
        version = entry.get("version")
        try:
            if not isinstance(version, str):
                raise ValueError
            ApiVersion.parse(version)  # the same major.minor rule as negotiated API versions
        except ValueError:
            problems.setdefault(ident, []).append(malformed_reason("apiList", ident, entry, "an entry with a major.minor version"))
            continue
        versions.setdefault(ident, []).append(version)  # every advertised version is kept (1.0 and 2.0)
    result = {ident: Advertised(tuple(found), tuple(problems.pop(ident, ()))) for ident, found in versions.items()}
    for ident, reasons in problems.items():
        result[ident] = Advertised((), tuple(reasons))
    return ClassicListing(result)


def malformed_reason(source: str, name: Any, value: Any, expected: str) -> str:
    """The one wording of a malformed discovery entry (the classic apiList and ``/config/discover`` share it)."""
    return f"{source} lists {name!r} as {value!r}, not {expected}"


@dataclass(frozen=True)
class Advertised:
    """The versions the classic apiList advertises for one id (it may list several: 1.0 and 2.0), and the malformed
    entries seen for that id. An id with problems is *unknown* unless a well-formed version already answers."""

    versions: tuple[str, ...]
    problems: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClassicListing:
    """What the classic API discovery probe found: per id, plus entries whose id could not be read (``<entry N>``)."""

    entries: Mapping[str, Advertised]


@dataclass(frozen=True)
class NamedListing:
    """A name -> text listing (installed applications, entry-service namespaces) and the entries that could not be read
    (no usable name). Those could have been the one asked for, so an absent name is *unknown* while any exist."""

    items: Mapping[str, str]
    problems: tuple[str, ...] = ()


@dataclass(frozen=True)
class DcaListing:
    """What ``/config/discover`` listed: the readable APIs, and the ones listed in the wrong shape (name -> reason)."""

    apis: Mapping[str, frozenset[str]]
    malformed: Mapping[str, str] = field(default_factory=dict)


def probe_is_complete(value: Any) -> bool:
    """Whether a probe result is definitive and may be cached (a result with a malformed entry is not). The one rule
    both discovery paths use."""
    if isinstance(value, ClassicListing):
        return not any(entry.problems for entry in value.entries.values())
    if isinstance(value, DcaListing):
        return not value.malformed
    if isinstance(value, NamedListing):
        return not value.problems
    return True


def dca_apis_flow(state: DeviceState) -> CallFlow[DcaListing]:
    response = yield Request("GET", "/config/discover", accept="application/json")
    if not 200 <= response.status < 300:
        raise http_error(_DISCOVER_OP, response)
    try:
        payload: Any = loads_json(response.content)
    except ValueError as error:
        raise ResponseFormatError("device", "config_discover", "response is not valid JSON") from error
    apis = payload.get("apis") if isinstance(payload, dict) else None
    if not isinstance(apis, dict):
        raise ResponseFormatError("device", "config_discover", "response has no apis object")
    return DcaListing(
        {str(name): frozenset(str(v) for v in versions) for name, versions in apis.items() if isinstance(versions, dict)},
        {
            str(name): malformed_reason("/config/discover", name, versions, "an object of versions")
            for name, versions in apis.items()
            if not isinstance(versions, dict)
        },
    )


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


def _attr(element: ET.Element, name: str) -> str:
    """Attribute value by case-insensitive name: older devices answer ``name=``/``version=``."""
    for key, value in element.attrib.items():
        if key.casefold() == name.casefold():
            return value
    return ""


def applications_flow(state: DeviceState) -> CallFlow[NamedListing]:
    response = yield Request("POST", "/axis-cgi/applications/list.cgi", accept="text/xml")
    if not 200 <= response.status < 300:
        raise http_error(_APPLICATIONS_OP, response)
    try:
        root = parse_xml(response.content)
    except ET.ParseError as error:
        raise ResponseFormatError("applications", "list", "response is not valid XML") from error
    if root.tag.rpartition("}")[2] != "reply":  # an unrelated document (a login page, <html/>) is not an empty list
        raise ResponseFormatError("applications", "list", f"expected a <reply> document, got <{root.tag.rpartition('}')[2]}>")
    if root.get("result") not in (None, "ok"):
        raise ResponseFormatError("applications", "list", f"device answered result={root.get('result')!r}")
    found: dict[str, str] = {}
    problems: list[str] = []
    for index, app in enumerate(a for a in root.iter() if a.tag.rpartition("}")[2] == "application"):
        name = _attr(app, "Name")
        if name:
            found[name] = _attr(app, "Version")
        else:
            problems.append(malformed_reason("applications/list.cgi", f"application {index}", dict(app.attrib), "an application with a Name"))
    return NamedListing(found, tuple(problems))


def services_flow(state: DeviceState) -> CallFlow[NamedListing]:
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
        root = parse_xml(response.content)
    except ET.ParseError as error:
        raise ResponseFormatError("entry-service", "get_services", "response is not valid XML") from error
    if root.tag.rpartition("}")[2] != "Envelope":  # a SOAP reply, not an unrelated document
        raise ResponseFormatError("entry-service", "get_services", f"expected a SOAP envelope, got <{root.tag.rpartition('}')[2]}>")
    found: dict[str, str] = {}
    problems: list[str] = []
    for index, service in enumerate(s for s in root.iter() if s.tag.rpartition("}")[2] == "Service"):
        children = {c.tag.rpartition("}")[2]: (c.text or "").strip() for c in service}
        if children.get("Namespace"):
            found[children["Namespace"]] = children.get("XAddr", "")
        else:
            problems.append(malformed_reason("GetServices", f"service {index}", children, "a service with a Namespace"))
    if not found and not problems:
        raise ResponseFormatError("entry-service", "get_services", "response lists no services")
    return NamedListing(found, tuple(problems))


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
    """Answer whether ``info`` is supported, from probe results alone.

    A discovery match is only a ``YES`` if the device firmware also meets the API's ``requires.firmware``;
    below it the answer is ``NO``, and with an unknown firmware it is ``UNKNOWN``.
    """
    result = _decide_discovery(info, caps)
    minimum = info.requires_firmware
    want = _firmware_key(minimum) if minimum is not None else None
    if minimum is None or want is None:
        return result  # no minimum, or one this client cannot read: not enforced
    have = _firmware_key(caps.firmware) if caps.firmware else None
    if have is not None and have < want and result.status is not Support.NO:
        # A known firmware below the minimum settles it, even when discovery failed (old firmware often lacks the endpoints).
        return SupportResult(
            Support.NO, f"device firmware {caps.firmware} is older than the {minimum} that {info.id} requires",
            observed_at=caps.observed_at,
        )
    if result.status is not Support.YES:
        return result
    if have is None:
        why = caps.errors.get("identity") or ("firmware version not known" if not caps.firmware else f"unreadable firmware {caps.firmware!r}")
        return SupportResult(
            Support.UNKNOWN, f"{info.id} needs firmware {minimum} or newer, and the device firmware is not known",
            (f"device identity: {why}",), caps.observed_at,
        )
    return result


_FIRMWARE_PART = re.compile(r"\d+")


def _firmware_key(text: str) -> tuple[int, ...] | None:
    """Leading dotted numbers of a firmware version (``11.5``, ``10.12.213``, ``9.80.1.1``); ``None`` if there are none."""
    parts: list[int] = []
    for part in text.strip().split("."):
        match = _FIRMWARE_PART.match(part)
        if match is None:
            break
        parts.append(int(match.group()))
        if match.end() != len(part):
            break
    return tuple(parts) or None


def _decide_discovery(info: ApiInfo, caps: Capabilities) -> SupportResult:
    if not info.discovery:
        return SupportResult(Support.UNKNOWN, f"{info.id} declares no discovery method", observed_at=caps.observed_at)

    unknown: list[str] = []
    for method in info.discovery:
        if isinstance(method, ApiDiscovery):
            if caps.classic_apis is None:
                unknown.append(f"classic API discovery failed: {caps.errors.get('classic_apis')}")
                continue
            listed = (caps.classic_versions or {}).get(method.id)
            if listed is None and (text := caps.classic_apis.get(method.id)):
                listed = Advertised((text,))  # a Capabilities built from plain id -> version text
            if listed is None:
                # Absent, but an entry without a readable id could have been this API: unknown, not a verdict.
                hidden = [
                    reason
                    for key, entry in (caps.classic_versions or {}).items()
                    if key.startswith("<entry ")
                    for reason in entry.problems
                ]
                if hidden:
                    unknown.extend(hidden)
                    continue
            if listed is not None:
                # Any advertised version that fits answers YES (an id may list 1.0 and 2.0).
                fitting = [v for v in listed.versions if info.major is None or v.startswith(f"{info.major}.")]
                if fitting:
                    return SupportResult(Support.YES, f"listed by API discovery as {method.id} {fitting[0]}", observed_at=caps.observed_at)
                if listed.problems:
                    unknown.extend(listed.problems)
                    continue
                if listed.versions:
                    return SupportResult(
                        Support.NO,
                        f"device has {method.id} version {', '.join(listed.versions)}, this client speaks {info.major}.x",
                        observed_at=caps.observed_at,
                    )
        elif isinstance(method, DcaDiscovery):
            if caps.dca_apis is None:
                unknown.append(f"Device Configuration discovery failed: {caps.errors.get('dca_apis')}")
                continue
            if method.version in caps.dca_apis.get(method.api, frozenset()):
                return SupportResult(Support.YES, f"listed by /config/discover as {method.api} {method.version}", observed_at=caps.observed_at)
            if method.api in caps.dca_malformed:
                unknown.append(caps.dca_malformed[method.api])
                continue
        elif isinstance(method, ParamDiscovery):
            name = _normalized(method.name)
            value = (caps.properties or {}).get(name)
            if value is not None and _param_matches(method, value):
                return SupportResult(Support.YES, f"parameter {name}={value}", observed_at=caps.observed_at)
            groups = caps.property_groups if caps.properties is not None else frozenset()
            if value is None and not _is_queried(name, groups):
                # Judge only the probe that covers this property: the base group or its own scope.
                if _is_queried(name, frozenset({BASE_PROPERTY_GROUP})):
                    reason = caps.errors.get("properties", "probe not run")
                else:
                    reason = caps.errors.get(PROPERTY_SCOPE_PREFIX + name, "probe not run")
                unknown.append(f"parameter {name} was not queried: {reason}")
        elif isinstance(method, AcapDiscovery):
            if caps.applications is None:
                unknown.append(f"installed applications probe failed: {caps.errors.get('applications', 'not run')}")
                continue
            for name, version in caps.applications.items():
                if name.casefold() == method.name.casefold():
                    return SupportResult(Support.YES, f"application {name} {version} is installed", observed_at=caps.observed_at)
            if caps.applications_problems:  # an entry without a usable name could have been this application
                unknown.extend(caps.applications_problems)

        elif isinstance(method, ServiceDiscovery):
            if caps.services is None:
                unknown.append(f"entry service probe failed: {caps.errors.get('services', 'not run')}")
                continue
            if method.namespace in caps.services:
                return SupportResult(Support.YES, f"listed by the entry service as {method.namespace}", observed_at=caps.observed_at)
            if caps.services_problems:
                unknown.extend(caps.services_problems)

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


def is_unreachable(error: BaseException) -> bool:
    """Whether a failure says the whole device is out of reach, not that one probe went wrong: credentials rejected,
    or a transport failure BEFORE anything was sent (refused, unreachable, DNS, connect timeout, TLS). A reset after the
    request was sent (``request_sent=True``) fails only that probe, and waiting for a free connection slot says
    nothing about the device."""
    if isinstance(error, AuthError):
        return True
    return isinstance(error, TransportError) and not isinstance(error, PoolTimeout) and error.request_sent is False


def skipped_probe_error(cause: str) -> str:
    """Error text of a probe that was not run because an earlier probe showed the device cannot be reached."""
    return f"not run: skipped because the device could not be reached ({cause})"


def probe_error(error: Exception) -> str:
    return f"{type(error).__name__}: {error}" if isinstance(error, DeviceError) else repr(error)
