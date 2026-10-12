"""Runtime descriptors shared by every protocol family and by generated code.

Generated API modules contain only data built from these types (``ApiInfo``,
``Operation``, bindings, models) plus thin methods. All behaviour lives in the
protocol modules, which are sans-IO: a call is a generator that yields
``Request`` values and receives ``Response`` values.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Generator, Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import UnionType
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, Protocol, TypeVar, Union, get_args, get_origin

from pydantic import (
    BaseModel,
    ConfigDict,
    TypeAdapter,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_validator,
)

from ..errors import (
    ApiAccessDenied,
    ApiError,
    ApiUnavailable,
    AuthError,
    DeviceError,
    ErrorKind,
    HttpAccessDenied,
    HttpError,
    HttpUnavailable,
    NotSupported,
    ResponseFormatError,
)
from .._http.types import Request, Response

if TYPE_CHECKING:
    from .state import DeviceState

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

# ---------------------------------------------------------------------------
# Versions


@dataclass(frozen=True, order=True)
class ApiVersion:
    """A ``major.minor`` API version as used by JSON-RPC ``apiVersion``."""

    major: int
    minor: int

    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"(\d+)\.(\d+)")

    @classmethod
    def parse(cls, text: str) -> ApiVersion:
        match = cls._PATTERN.fullmatch(text.strip())
        if match is None:
            raise ValueError(f"Not a major.minor version: {text!r}")
        return cls(int(match.group(1)), int(match.group(2)))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


def select_version(advertised: Iterable[ApiVersion], major: int, known: Iterable[ApiVersion]) -> ApiVersion | None:
    """Pick the version to speak with a device.

    Devices advertise the highest minor version they support per major
    version, and minor versions are backward compatible. So the right choice
    is the lower of the device's highest minor and the highest minor the
    generated code knows about. With no known versions, use the device's.
    Returns ``None`` when the device offers nothing in this major version.
    """
    device_max = max((v for v in advertised if v.major == major), default=None)
    if device_max is None:
        return None
    known_max = max((v for v in known if v.major == major), default=None)
    if known_max is None:
        return device_max
    return min(device_max, known_max)


# ---------------------------------------------------------------------------
# Models

RESPONSE_CONTEXT = "ax_devil_response"
"""Validation context key set while parsing device responses (unknown fields allowed)."""


class Model(BaseModel):
    """Base class for generated request and response models.

    - Fields use snake_case attributes. Wire names are given as
      ``validation_alias``/``serialization_alias`` (not ``alias``) so type
      checkers see the Python names in constructors.
    - Optional fields default to ``None``. The model remembers which fields
      were set; unset fields are never sent. An explicit ``None`` is sent as
      JSON ``null`` only for fields listed in ``__nullable__``, and is rejected
      at construction for every other field.
    - Fields the device always returns are required; a response missing one
      raises ``ResponseFormatError``.
    - Parsing device responses ignores unknown fields and keeps enum values
      newer than the generated ``Literal`` (newer firmware may add both).
      Constructing a model in Python rejects unknown fields and invalid enum
      values, so typos fail loudly with a ``ValidationError``.
    """

    __nullable__: ClassVar[frozenset[str]] = frozenset()

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )

    @classmethod
    def _wire_to_field(cls) -> dict[str, str]:
        names: dict[str, str] = {}
        for name, field_info in cls.model_fields.items():
            names[name] = name
            for alias in (field_info.alias, field_info.validation_alias, field_info.serialization_alias):
                if isinstance(alias, str):
                    names[alias] = name
        return names

    @model_validator(mode="before")
    @classmethod
    def _check_request_fields(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict) or is_response(info):
            return data
        names = cls._wire_to_field()
        unknown = sorted(str(key) for key in data if key not in names)
        if unknown:
            raise ValueError(f"unexpected field(s): {', '.join(unknown)}")
        nulls = sorted(names[k] for k, v in data.items() if v is None and names[k] not in cls.__nullable__)
        if nulls:
            raise ValueError(f"field(s) cannot be null; leave them unset instead: {', '.join(nulls)}")
        return data

    @field_validator("*", mode="wrap")
    @classmethod
    def _tolerate_new_enum_values(cls, value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo) -> Any:
        try:
            return handler(value)
        except ValidationError:
            if is_response(info) and info.field_name is not None:
                annotation = cls.model_fields[info.field_name].annotation
                if _is_new_enum_value(annotation, value):
                    return value
            raise

    def __repr_args__(self) -> Iterable[tuple[str | None, Any]]:
        fields_set = self.model_fields_set
        return ((name, value) for name, value in super().__repr_args__() if name in fields_set or value is not None)

    def to_wire(self) -> dict[str, Any]:
        """Serialize for sending: aliases, set fields only, JSON-compatible values."""
        return self.model_dump(mode="json", by_alias=True, exclude_unset=True)

    def set_fields(self) -> dict[str, Any]:
        """The explicitly set fields as ``{attribute: value}`` (nested models kept as models)."""
        return {name: getattr(self, name) for name in self.model_fields_set}

    def request_data(self, *, exclude: Iterable[str] = ()) -> dict[str, Any]:
        """Set, non-null fields as plain data keyed by Python names, for building a request.

        Nested models become dicts, so the request model re-validates them
        under request rules. Nulls from a response mean "not configured" and
        are dropped rather than sent back.
        """
        return self.model_dump(mode="python", by_alias=False, exclude_unset=True, exclude_none=True, exclude=set(exclude))


def _literal_values(annotation: Any) -> tuple[Any, ...] | None:
    """The values of a ``Literal`` (possibly inside ``X | None``), or ``None``."""
    if get_origin(annotation) is Literal:
        return get_args(annotation)
    if get_origin(annotation) in (Union, UnionType):
        for arg in get_args(annotation):
            values = _literal_values(arg)
            if values is not None:
                return values
    return None


def _is_new_enum_value(annotation: Any, value: Any) -> bool:
    """Whether ``value`` is an unknown member of an enum: same primitive type, new value.

    ``list[Literal[...]]`` fields accept lists of such values. Nulls,
    objects and values of another type are still rejected.
    """
    if get_origin(annotation) in (Union, UnionType):
        return any(_is_new_enum_value(arg, value) for arg in get_args(annotation) if arg is not type(None))
    if get_origin(annotation) is list:
        (item,) = get_args(annotation) or (Any,)
        return isinstance(value, list) and all(_is_new_enum_value(item, v) or _matches(item, v) for v in value)
    values = _literal_values(annotation)
    if not values or value is None:
        return False
    return type(value) in {type(v) for v in values}


def _matches(annotation: Any, value: Any) -> bool:
    values = _literal_values(annotation)
    return values is not None and value in values


def is_response(info: ValidationInfo) -> bool:
    return bool((info.context or {}).get(RESPONSE_CONTEXT))


_adapters: dict[Any, TypeAdapter[Any]] = {}


def adapter(tp: Any) -> TypeAdapter[Any]:
    """Cached ``TypeAdapter`` for a result type."""
    found = _adapters.get(tp)
    if found is None:
        found = _adapters[tp] = TypeAdapter(tp)
    return found


def parse_result(op: Operation[Any], data: Any) -> Any:
    """Validate response data against the operation's result type."""
    if op.result is None:
        return None
    try:
        return adapter(op.result).validate_python(data, context={RESPONSE_CONTEXT: True})
    except ValidationError as error:
        raise ResponseFormatError(op.api.id, op.id, f"response does not match the documented shape: {error}") from error


# ---------------------------------------------------------------------------
# API and operation descriptors


class Family(str, Enum):
    JSONRPC = "jsonrpc"
    DCA = "dca"
    CGI = "cgi"
    PARAM = "param"
    SERVICE_JSON = "service_json"
    SOAP = "soap"
    REST = "rest"
    WS = "ws"
    RTSP = "rtsp"


Access = Literal["anonymous", "viewer", "operator", "admin", "unknown"]
Effect = Literal["read", "write", "action", "unknown"]
WriteSemantics = Literal["replace", "patch", "create", "delete"]
"""How a write changes state: ``replace`` overwrites the whole configuration
(unset fields return to defaults), ``patch`` changes only the fields sent."""
SupportStatus = Literal["verified", "docs-only", "known-broken"]


@dataclass(frozen=True)
class ErrorCode:
    """One documented error code."""

    description: str
    kind: ErrorKind | None = None


@dataclass(frozen=True)
class ApiDiscovery:
    """Listed by classic API discovery (``apidiscovery.cgi``) under ``id``."""

    id: str


@dataclass(frozen=True)
class DcaDiscovery:
    """Listed by Device Configuration discovery (``/config/discover``)."""

    api: str
    version: str


@dataclass(frozen=True)
class ParamDiscovery:
    """A ``param.cgi`` property, e.g. ``Properties.API.HTTP.Version`` == ``3``.

    ``compare`` ``">="`` accepts any value that is at least ``value``: dotted
    numbers compare component by component (``1.20`` >= ``1.9``).
    """

    name: str
    value: str | None = None
    compare: Literal["==", ">="] = "=="


@dataclass(frozen=True)
class AcapDiscovery:
    """An ACAP application is installed (``applications/list.cgi``), matched by its ``Name`` attribute."""

    name: str


Discovery = ApiDiscovery | DcaDiscovery | ParamDiscovery | AcapDiscovery


@dataclass(frozen=True)
class ApiInfo:
    """Static description of one generated API class (one major version)."""

    id: str
    name: str
    family: Family
    major: int | None = None
    known_versions: tuple[ApiVersion, ...] = ()
    discovery: tuple[Discovery, ...] = ()
    docs: tuple[str, ...] = ()
    errors: Mapping[int | str, ErrorCode] = field(default_factory=dict)
    """API-wide error codes, from the spec's general error table."""


@dataclass(frozen=True)
class Applicability:
    """Version requirement for a parameter path or an enum value.

    ``path`` is a dotted path of Python attribute names inside the params model
    (``server.alpn_protocol``). ``value`` restricts the requirement to one enum
    value of that field.
    """

    path: str
    since: ApiVersion
    value: Any = None


B = TypeVar("B")


@dataclass(frozen=True)
class Operation(Generic[B]):
    """One callable operation. ``binding`` selects and configures the protocol."""

    api: ApiInfo
    id: str
    binding: B
    params: type[Model] | None = None
    result: Any = None
    access: Access = "unknown"
    effect: Effect = "unknown"
    since: ApiVersion | None = None
    write: WriteSemantics | None = None
    applicability: tuple[Applicability, ...] = ()
    errors: Mapping[int | str, ErrorCode] = field(default_factory=dict)
    support: SupportStatus = "docs-only"

    def error_code(self, code: int | str | None) -> ErrorCode | None:
        if code is None:
            return None
        return self.errors.get(code) or self.api.errors.get(code)


def api_error(
    op: Operation[Any], code: int | str | None, message: str, *, http_status: int | None, details: Any
) -> ApiError:
    """Build the right ``ApiError`` subclass for a documented (or unknown) code."""
    info = op.error_code(code)
    kind = info.kind if info else None
    if kind is None and http_status == 403:
        kind = "access_denied"
    cls = {"access_denied": ApiAccessDenied, "unavailable": ApiUnavailable}.get(kind or "", ApiError)
    return cls(
        op.api.id,
        op.id,
        code,
        message,
        description=info.description if info else None,
        kind=kind,
        http_status=http_status,
        details=details,
    )


def http_error(op: Operation[Any], response: Response) -> DeviceError:
    """Build the error for a failure status that carried no API error envelope."""
    status = response.status
    if status == 401:
        return AuthError(f"{op.api.id}.{op.id}: the device requires authentication and no usable credentials were configured")
    if status == 403:
        return HttpAccessDenied(status, response.excerpt(), api=op.api.id, operation=op.id, detail=f"requires {op.access} access")
    if status == 503:
        return HttpUnavailable(status, response.excerpt(), api=op.api.id, operation=op.id)
    if status == 404:
        return NotSupported(op.api.id, op.id, f"{response.request.path} not found (HTTP 404)")
    return HttpError(status, response.excerpt(), api=op.api.id, operation=op.id)


def check_applicability(op: Operation[Any], params: Model | None, version: ApiVersion | None) -> None:
    """Reject operations, set fields, or enum values newer than ``version``.

    Only explicitly set fields count: an unset optional field is never sent.
    When the version is unknown (APIs without negotiation) nothing is checked.
    """
    if version is None:
        return
    if op.since is not None and version < op.since:
        raise NotSupported(op.api.id, op.id, f"requires API version {op.since}, device speaks {version}", required=str(op.since))
    if params is None:
        return
    for rule in op.applicability:
        if version >= rule.since:
            continue
        found, value = _lookup_set(params, rule.path.split("."))
        if not found:
            continue
        if rule.value is None or _contains_value(value, rule.value):
            what = f"{rule.path}={rule.value!r}" if rule.value is not None else rule.path
            raise NotSupported(
                op.api.id, op.id, f"{what} requires API version {rule.since}, device speaks {version}", required=str(rule.since)
            )


def _lookup_set(obj: Any, parts: list[str]) -> tuple[bool, Any]:
    if not parts:
        return True, obj
    if isinstance(obj, BaseModel):
        head = parts[0]
        if head not in obj.model_fields_set:
            return False, None
        return _lookup_set(getattr(obj, head), parts[1:])
    if isinstance(obj, (list, tuple)):
        hits = [_lookup_set(item, parts) for item in obj]
        values = [v for ok, v in hits if ok]
        return (bool(values), values)
    return False, None


def _contains_value(value: Any, wanted: Any) -> bool:
    if isinstance(value, list):
        return any(_contains_value(v, wanted) for v in value)
    if isinstance(value, Enum):
        value = value.value
    return value == wanted


# ---------------------------------------------------------------------------
# Call flows


CallFlow = Generator[Request, Response, T]
"""A sans-IO call: yields requests, receives responses, returns the result.

A request with ``stream=True`` must be the last one a flow yields. The flow
then receives a ``Response`` with empty ``content`` (2xx) or the full error
body (any other status), and returns either a ``StreamDecoder`` (success) or
raises.
"""


class StreamDecoder(Protocol[T_co]):
    """Incremental decoder for a streamed response body."""

    def feed(self, chunk: bytes) -> Iterable[T_co]:
        """Consume a chunk; return the items it completes."""
        ...

    def close(self) -> Iterable[T_co]:
        """End of body; return trailing items or raise if the body was truncated."""
        ...


class BytesDecoder:
    """Pass raw body chunks through unchanged."""

    def feed(self, chunk: bytes) -> Iterable[bytes]:
        return (chunk,) if chunk else ()

    def close(self) -> Iterable[bytes]:
        return ()


FlowFactory = Callable[[Operation[Any], "Model | None", "DeviceState"], CallFlow[Any]]
"""Builds the flow for one call. Registered per binding type."""

_FLOWS: dict[type, FlowFactory] = {}


def register_binding(binding_type: type, factory: FlowFactory) -> None:
    _FLOWS[binding_type] = factory


def flow_for(op: Operation[Any], params: Model | None, state: DeviceState) -> CallFlow[Any]:
    factory = _FLOWS.get(type(op.binding))
    if factory is None:
        raise TypeError(f"No protocol registered for binding {type(op.binding).__name__}")
    return factory(op, params, state)
