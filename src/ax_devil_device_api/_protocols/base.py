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
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    Generic,
    Literal,
    Protocol,
    Self,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    PrivateAttr,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    TypeAdapter,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_serializer,
    model_validator,
)

from .._http.debug import register_secret_names
from .._http.types import Request, Response
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

_FOR_REQUEST = "ax_devil_request"
_DROP_MASKED = "ax_devil_drop_masked"

RESPONSE_CONTEXT = "ax_devil_response"
"""Validation context key set while parsing device responses (unknown fields allowed)."""

_ROUND_TRIP = "ax_devil_round_trip"
"""Context key of ``from_current``: a set collecting the enum values this client does not know (device-returned)."""
_ALLOWED_VALUES = "ax_devil_allowed_values"
"""Context key of send-time revalidation: the unknown enum values a round trip carried, which stay acceptable."""


class _Masked:
    """Stands in for a masked field's value in ``repr``."""

    def __repr__(self) -> str:
        return "'*****'"


_MASKED_REPR = _Masked()


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
    __response_required__: ClassVar[frozenset[str]] = frozenset()
    """Required read-only fields (``required`` with ``x-read-only``): the device always returns them, so a response
    without one is rejected, while a request model leaves them out (``not_sent``) and never sends them."""

    __masked__: ClassVar[frozenset[str]] = frozenset()
    """Fields the device masks in responses (``x-masked``): never copied by ``from_current`` and redacted in debug hooks."""
    __read_only__: ClassVar[frozenset[str]] = frozenset()
    """Fields only present in responses (``x-read-only``): omitted from every request, at any depth."""

    _round_trip_values: frozenset[Any] = PrivateAttr(default_factory=frozenset)
    """Unknown enum values a ``from_current`` round trip carried over from the device; they pass send-time revalidation."""

    model_config = ConfigDict(
        hide_input_in_errors=True,
        populate_by_name=True,
        extra="ignore",
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if cls.__masked__:
            wire = cls._wire_to_field()
            register_secret_names(alias for alias, name in wire.items() if name in cls.__masked__)

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
        if not isinstance(data, dict):
            return data
        if is_response(info):
            if cls.__response_required__:
                names = cls._wire_to_field()
                present = {names[key] for key in data if key in names}
                missing = sorted(cls.__response_required__ - present)
                if missing:
                    raise ValueError(f"required field(s) missing from the response: {', '.join(missing)}")
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
            context = info.context or {}
            response = bool(context.get(RESPONSE_CONTEXT))
            collector = context.get(_ROUND_TRIP)
            allowed = context.get(_ALLOWED_VALUES)
            if info.field_name is not None and (response or collector is not None or allowed is not None):
                field = cls.model_fields[info.field_name]
                annotation = Annotated[(field.annotation, *field.metadata)] if field.metadata else field.annotation
                if response:
                    coerced = _coerce_text(annotation, value)
                    if coerced is not value:
                        try:
                            return handler(coerced)
                        except ValidationError:
                            value = coerced
                if _is_new_enum_value(annotation, value):
                    new = _unknown_items(annotation, value)
                    if response:
                        return value
                    pairs = [(info.field_name, item) for item in new]
                    if not pairs:
                        raise  # no unknown enum value: some other constraint failed (for example an emptied list)
                    if collector is not None:
                        collector.update(pairs)
                        return value
                    if allowed is not None and all(pair in allowed for pair in pairs):
                        return value
            raise

    def __repr_args__(self) -> Iterable[tuple[str | None, Any]]:
        fields_set = self.model_fields_set
        masked = self.__masked__
        for name, value in super().__repr_args__():
            if name in fields_set or value is not None:
                yield name, (_MASKED_REPR if name in masked and value is not None else value)

    @model_serializer(mode="wrap")
    def _omit_unsendable(self, handler: SerializerFunctionWrapHandler, info: SerializationInfo) -> Any:
        data = handler(self)
        context = info.context
        if not isinstance(data, dict) or not isinstance(context, dict):
            return data
        drop: set[str] = set()
        if context.get(_FOR_REQUEST):
            drop |= self.__read_only__
        if context.get(_DROP_MASKED):
            drop |= self.__masked__ | self.__read_only__
        for name in drop:
            field_info = type(self).model_fields.get(name)
            data.pop(name, None)
            if field_info is not None and isinstance(field_info.serialization_alias, str):
                data.pop(field_info.serialization_alias, None)
        return data

    @classmethod
    def from_response_data(cls, data: dict[str, Any]) -> Self:
        """Build a request model from plain data a device returned (``from_current``).

        Request rules apply (unknown fields and bad values are rejected), except that enum values newer
        than the generated code are carried over, so a round trip survives a firmware upgrade. The model
        remembers them: send-time revalidation accepts exactly those values and no others.
        """
        seen: set[Any] = set()
        model = cls.model_validate(data, context={_ROUND_TRIP: seen})
        model._round_trip_values = frozenset(seen)
        return model

    def revalidated(self) -> Self:
        """A fresh, validated copy: catches edits made after construction (assignment, ``model_copy(update=...)``).

        Runs under strict request rules, so a value that construction would reject raises ``ValidationError``.
        """
        data = _plain(self)
        model = type(self).model_validate(data, context={_ALLOWED_VALUES: self._round_trip_values})
        model._round_trip_values = self._round_trip_values
        return model

    def to_wire(self) -> dict[str, Any]:
        """Serialize for sending: aliases, set fields only, read-only fields omitted at any depth."""
        return self.model_dump(mode="json", by_alias=True, exclude_unset=True, context={_FOR_REQUEST: True})

    def set_fields(self) -> dict[str, Any]:
        """The explicitly set fields as ``{attribute: value}`` (nested models kept as models)."""
        return {name: getattr(self, name) for name in self.model_fields_set}

    def request_data(self, *, exclude: Iterable[str] = ()) -> dict[str, Any]:
        """Set, non-null fields as plain data keyed by Python names, for building a request.

        Masked and read-only fields are dropped at every depth (through nested
        models and lists). Nested models become dicts, so the request model
        re-validates them under request rules. Nulls from a response mean
        "not configured" and are dropped rather than sent back.
        """
        return self.model_dump(
            mode="python",
            by_alias=False,
            exclude_unset=True,
            exclude_none=True,
            exclude=set(exclude),
            context={_DROP_MASKED: True},
        )


def _plain(value: Any) -> Any:
    """The set fields of models as plain dicts keyed by Python name (other values, such as uploads, kept as they are)."""
    if isinstance(value, BaseModel):
        return {name: _plain(getattr(value, name)) for name in value.model_fields_set}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_plain(item) for item in value)
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    return value


def not_sent() -> Any:
    """Default of a required read-only field: absent on a request model, which never sends it."""
    return None


class _Const:
    """Marks a ``Literal`` generated from ``const``: a fixed value, not an extensible enum."""

    def __repr__(self) -> str:
        return "CONST"


CONST = _Const()
"""Annotation metadata for ``const`` fields (``Annotated[Literal["x"], CONST]``). They stay strict in responses:
only enums tolerate values newer than the generated ``Literal``, so a union can still pick the right variant."""


def _literal_values(annotation: Any) -> tuple[Any, ...] | None:
    """The values of a ``Literal`` (possibly inside ``X | None``), or ``None``."""
    if get_origin(annotation) is Annotated:
        return _literal_values(get_args(annotation)[0])
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
    if get_origin(annotation) is Annotated:
        base, *metadata = get_args(annotation)
        return not any(m is CONST for m in metadata) and _is_new_enum_value(base, value)
    if get_origin(annotation) in (Union, UnionType):
        return any(_is_new_enum_value(arg, value) for arg in get_args(annotation) if arg is not type(None))
    if get_origin(annotation) is list:
        (item,) = get_args(annotation) or (Any,)
        return isinstance(value, list) and bool(value) and all(_is_new_enum_value(item, v) or _matches(item, v) for v in value)
    values = _literal_values(annotation)
    if not values or value is None:
        return False
    return type(value) in {type(v) for v in values}


def _known_values(annotation: Any) -> tuple[Any, ...]:
    """Every enum value the annotation lists (through ``Annotated``, unions and lists)."""
    if get_origin(annotation) in (Annotated, list, Union, UnionType):
        return tuple(v for arg in get_args(annotation) for v in _known_values(arg))
    return _literal_values(annotation) or ()


def _unknown_items(annotation: Any, value: Any) -> list[Any]:
    """The scalars of ``value`` (itself or its list items) that the annotation does not list."""
    known = _known_values(annotation)
    return [item for item in (value if isinstance(value, list) else [value]) if item not in known]


def _matches(annotation: Any, value: Any) -> bool:
    values = _literal_values(annotation)
    return values is not None and value in values


_INT_TEXT = re.compile(r"[+-]?\d+")


def _coerce_text(annotation: Any, value: Any) -> Any:
    """Turn text from XML or ``key=value`` replies into the integer a ``Literal[1, 2]`` field lists.

    Only strings that spell an integer, for fields that are integer enums, are
    converted (also inside lists); everything else is returned unchanged.
    """
    if isinstance(value, list):
        item = next((a for a in get_args(annotation) if get_origin(a) is list), annotation)
        (inner,) = get_args(item) or (Any,)
        return [_coerce_text(inner, v) for v in value]
    if isinstance(value, str) and _INT_TEXT.fullmatch(value.strip()):
        values = _literal_values(annotation)
        if values and any(isinstance(v, int) and not isinstance(v, bool) for v in values):
            return int(value)
    return value


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
        if _is_new_enum_value(op.result, data):  # newer firmware may add an enum value to a scalar result too
            return data
        raise ResponseFormatError(op.api.id, op.id, f"response does not match the documented shape: {error}") from error


# ---------------------------------------------------------------------------
# API and operation descriptors


class Family(str, Enum):  # noqa: UP042 (StrEnum would change str() and format())
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
    """One documented error: a code (the key of the ``errors`` map), or a message.

    An entry with ``message`` or ``message_prefix`` is matched against the message text of a
    failure reply that carries no code (``Error: account user name.``); its key in the map is
    only a label. ``message`` must equal the reply message, ``message_prefix`` must start it; both are
    case-sensitive, collapse whitespace and ignore a trailing full stop.
    """

    description: str
    kind: ErrorKind | None = None
    message: str | None = None
    message_prefix: str | None = None

    def matches_message(self, message: str) -> bool:
        text = _normalize_message(message)
        if self.message is not None and text == _normalize_message(self.message):
            return True
        return self.message_prefix is not None and text.startswith(_normalize_message(self.message_prefix))


def _normalize_message(text: str) -> str:
    return " ".join(text.split()).rstrip(".").strip()


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


@dataclass(frozen=True)
class ServiceDiscovery:
    """A web service is offered: its namespace is listed by the Entry service ``GetServices``."""

    namespace: str


Discovery = ApiDiscovery | DcaDiscovery | ParamDiscovery | AcapDiscovery | ServiceDiscovery


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

    def error_code(self, code: int | str | None, message: str | None = None) -> ErrorCode | None:
        """The documented error for ``code``; without a code (or when it is unknown), the one matching ``message``.

        An exact key wins over a range key (``"9000-9999"``); the operation's table wins over the API's.
        """
        if code is not None:
            for table in (self.errors, self.api.errors):
                entry = table.get(code)
                if entry is not None and entry.message is None and entry.message_prefix is None:
                    return entry
            number = _code_number(code)
            if number is not None:
                for table in (self.errors, self.api.errors):
                    for key, entry in table.items():
                        bounds = _RANGE_KEY.fullmatch(key.strip()) if isinstance(key, str) else None
                        if bounds is not None and int(bounds[1]) <= number <= int(bounds[2]):
                            return entry
        if message:
            for table in (self.errors, self.api.errors):
                for entry in table.values():
                    if (entry.message is not None or entry.message_prefix is not None) and entry.matches_message(message):
                        return entry
        return None


_RANGE_KEY = re.compile(r"(\d+)\s*-\s*(\d+)")


def _code_number(code: int | str) -> int | None:
    if isinstance(code, bool):
        return None
    if isinstance(code, int):
        return code
    return int(code) if code.strip().isdigit() else None


def api_error(
    op: Operation[Any], code: int | str | None, message: str, *, http_status: int | None, details: Any
) -> ApiError:
    """Build the right ``ApiError`` subclass for a documented (or unknown) code."""
    info = op.error_code(code, message)
    kind = info.kind if info else None
    if kind is None and http_status == 403:
        kind = "access_denied"
    elif kind is None and http_status == 503:
        kind = "unavailable"
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
